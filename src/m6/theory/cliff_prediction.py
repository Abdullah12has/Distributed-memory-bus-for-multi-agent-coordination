"""Coordination Cliff Theorem — prediction, sharpness analysis, and validation.

Theorem 1 (Coordination Cliff Bound):
  Consider a coordination task where a compressor C with per-token retention
  probability q(r) at compression ratio r is applied to each fragment ONCE
  before the planner reads them. Let theta be the minimum fraction of
  task-relevant tokens required for coordination success. Then:

    (i)   P(success | r) <= p0 * q(r)
    (ii)  A coordination cliff exists at r* where q(r*) = theta
    (iii) r* depends only on C (through q) and the task (through theta),
          NOT on planner model capacity.

  Note: if compression is applied across N sequential passes (e.g.,
  iterative summarization), the bound tightens to q(r)^N. In our
  experiments, N=1 (single compression pass before coordination).

Theorem 2 (Cliff Sharpness via Concentration):
  Under assumption A1 (memoryless compressor), the number of surviving
  task-relevant tokens X ~ Binomial(M, q(r)), where M is the total number
  of task-relevant tokens. By the Hoeffding-Chernoff bound:

    If q(r) > theta:  P(X/M < theta) <= exp(-2M(q(r) - theta)^2)
    If q(r) < theta:  P(X/M >= theta) <= exp(-2M(theta - q(r))^2)

  As M -> infinity, P(success) converges to a step function at q(r) = theta.
  The transition width in q-space scales as O(1/sqrt(M)), explaining why
  the coordination cliff is SHARP (a phase transition), not gradual.

Corollary 1 (Ceiling-Cliff Separation):
  Model capacity m determines baseline success p0(m), while cliff position
  r* is determined solely by compressor C and task threshold theta.
  When p0(m) < theta, no cliff is detectable (floor effect).
  When p0(m) >= theta, r* is invariant to m.

  Evidence: H5 family-c shows all model sizes (1.5B, 3.8B, 8B) cliff at
  the same ratio (~8x with LLMLingua-2), matching the deterministic solver.
  H5 family-a: 1.5B/3.8B have p0 < theta (baseline ~3-17%), so no cliff
  is detectable — this is a floor effect, not counter-evidence.

Corollary 2 (Information Density Scaling):
  For tasks with information density d (fraction of tokens that are
  task-critical), theta ~ d. Dense quantitative tasks (d ~ 0.5) cliff
  early; distributed qualitative tasks (d ~ 0.1) cliff late or show
  gradual degradation rather than a sharp phase transition.

  Evidence: C1 family-a (numeric aggregation, theta=0.48) cliffs at 2.5x;
  family-c (tree traversal, theta=0.38) cliffs at 6.7x; MultiHopRAG
  (multi-hop QA, theta~0.08) shows gradual decline with tau~11.3x.

This module implements:
  - predicted_tau(): compute r* from a token-recall curve
  - q_required(): compute the minimum token recall for coordination
  - chernoff_success_probability(): P(success) with finite-M sharpness
  - chernoff_success_curve(): full curve with M-dependent sharpness
  - cliff_sharpness(): transition width as a function of M
  - derive_theta(): empirically derive theta from sweep data
  - validate_prediction(): compare predicted vs empirical cliff positions
  - validate_model_independence(): test Corollary 1 on H5 data
  - estimate_task_theta(): derive theta from any coord_success curve
  - validate_task_theta(): test Corollary 2 across tasks

Usage:
    from m6.theory.cliff_prediction import predicted_tau, validate_prediction

    # From H1/H2 sweep data
    token_recall_curve = [(1.0, 1.0), (2.0, 0.52), (4.0, 0.11), ...]
    tau_star = predicted_tau(token_recall_curve, n_compression_passes=1, theta=0.5)
"""

from __future__ import annotations

from typing import Any

import numpy as np


def q_required(theta: float, n_compression_passes: int = 1) -> float:
    """Minimum token recall to maintain coordination success.

    From Theorem 1(ii): q* = theta^(1/N) where N is the number of
    compression passes. For N=1 (our default), q* = theta.

    Args:
        theta: Minimum fraction of task-relevant tokens needed for success.
        n_compression_passes: Number of times compression is applied.
            Default 1 (single pass before coordination, matching our setup).

    Returns:
        q*: the minimum token recall.
    """
    if n_compression_passes <= 0:
        raise ValueError("n_compression_passes must be positive")
    if not 0 < theta <= 1:
        raise ValueError("theta must be in (0, 1]")
    return theta ** (1.0 / n_compression_passes)


def predicted_tau(
    token_recall_curve: list[tuple[float, float]],
    n_compression_passes: int = 1,
    theta: float = 0.5,
) -> float:
    """Predict the cliff position from a measured token-recall curve.

    Finds the compression ratio r* where q(r)^N first drops below theta.
    For N=1 (default, matching our single-pass setup), this is simply
    where q(r) < theta.

    Args:
        token_recall_curve: List of (ratio, token_recall) pairs, sorted by ratio.
        n_compression_passes: Number of compression passes (default 1).
        theta: Fraction of source information the planner needs to succeed.

    Returns:
        Predicted tau* (compression ratio at the cliff).
        Returns float("inf") if the cliff is outside the measured range.
    """
    q_min = q_required(theta, n_compression_passes)
    curve = sorted(token_recall_curve, key=lambda x: x[0])

    for i, (ratio, q) in enumerate(curve):
        if q < q_min:
            # Interpolate between this point and the previous one
            if i == 0:
                return ratio
            prev_ratio, prev_q = curve[i - 1]
            # Linear interpolation: find r where q(r) = q_min
            if abs(prev_q - q) < 1e-9:
                return ratio
            frac = (prev_q - q_min) / (prev_q - q)
            return prev_ratio + frac * (ratio - prev_ratio)

    return float("inf")


def derive_theta(
    sweep_csv_path: str,
    success_threshold: float = 0.5,
    compressors: list[str] | None = None,
    family: str = "a",
    recall_column: str = "token_recall",
) -> dict[str, Any]:
    """Empirically derive theta from the H1/H2 sweep data.

    For each compressor, finds the recall value at the ratio where
    coord_success first drops below ``success_threshold``. Theta is the
    average of these critical recall values.

    Args:
        recall_column: Which recall metric to use. Default "token_recall"
            (generic word overlap). Use "critical_token_recall" for
            task-specific tokens when that column is available.

    Returns:
        Dict with per-compressor theta estimates and the mean.
    """
    import pandas as pd

    df = pd.read_csv(sweep_csv_path)
    if compressors is None:
        compressors = sorted(df["compressor"].unique())

    # Fall back to token_recall if requested column doesn't exist
    col = recall_column if recall_column in df.columns else "token_recall"

    per_comp: dict[str, float] = {}
    for comp in compressors:
        sub = df[(df["compressor"] == comp) & (df["family"] == family)]
        agg = sub.groupby("ratio")[["coord_success", col]].mean().reset_index()
        agg = agg.sort_values("ratio")
        # Find the first ratio where coord_success drops below threshold
        for _, row in agg.iterrows():
            if row["coord_success"] < success_threshold and row["ratio"] > 1.0:
                per_comp[comp] = float(row[col])
                break
        else:
            # No cliff found — use the recall at max ratio
            if not agg.empty:
                per_comp[comp] = float(agg.iloc[-1][col])

    thetas = list(per_comp.values())
    mean_theta = float(np.mean(thetas)) if thetas else 0.5

    return {
        "per_compressor": per_comp,
        "mean_theta": mean_theta,
        "family": family,
        "success_threshold": success_threshold,
        "recall_column": col,
        "note": "Empirically derived from H1/H2 sweep. Use mean_theta as theta parameter.",
    }


def chernoff_success_probability(
    q: float,
    theta: float,
    m: int,
    n_compression_passes: int = 1,
) -> float:
    """Coordination success probability via Chernoff bound.

    Under the memoryless compressor assumption, the number of surviving
    task-relevant tokens follows Binomial(M, q^N). The Chernoff bound
    gives the probability that the surviving fraction exceeds theta:

        If q^N > theta:  P(X/M >= theta) >= 1 - exp(-2M(q^N - theta)^2)
        If q^N < theta:  P(X/M >= theta) <= exp(-2M(theta - q^N)^2)
        If q^N = theta:  P(X/M >= theta) ~ 0.5

    The key insight: for large M, the transition sharpens into a step
    function at q^N = theta. This explains WHY the cliff is sharp.
    """
    qn = q ** n_compression_passes
    gap = qn - theta
    exponent = 2.0 * m * gap * gap

    if gap > 0:
        # Above cliff: success probability approaches 1
        return 1.0 - np.exp(-exponent)
    elif gap < 0:
        # Below cliff: success probability approaches 0
        return np.exp(-exponent)
    else:
        return 0.5


def chernoff_success_curve(
    token_recall_curve: list[tuple[float, float]],
    theta: float,
    m: int,
    n_compression_passes: int = 1,
    p0: float = 1.0,
) -> list[tuple[float, float]]:
    """Predict coordination success at each ratio using Chernoff bound.

    Unlike the hard-threshold version, this produces a smooth but steep
    transition whose sharpness depends on M (number of task-relevant tokens).
    Larger M = sharper cliff.
    """
    result = []
    for ratio, q in sorted(token_recall_curve, key=lambda x: x[0]):
        prob = chernoff_success_probability(q, theta, m, n_compression_passes)
        result.append((ratio, p0 * prob))
    return result


def cliff_sharpness(m: int, theta: float = 0.5) -> float:
    """Quantify cliff sharpness: the ratio-range over which success drops from 90% to 10%.

    For a Binomial(M, q) model with threshold theta, the transition width
    (in q-space) scales as O(1/sqrt(M)). Larger M = narrower transition.

    Returns the approximate transition width in q-space.
    """
    if m <= 0:
        return float("inf")
    # From Chernoff: P drops from 0.9 to 0.1 over delta_q where
    # exp(-2M*delta_q^2) = 0.1, so delta_q = sqrt(ln(10)/(2M))
    return float(np.sqrt(np.log(10) / (2 * m)))


def survival_probability(q: float, n_compression_passes: int = 1) -> float:
    """Probability that task-relevant information survives compression.

    From Theorem 1(i): P(survive) = q^N where N is compression passes.
    For N=1 (default): P(survive) = q.
    """
    return q ** n_compression_passes


def predicted_success_curve(
    token_recall_curve: list[tuple[float, float]],
    n_compression_passes: int,
    theta: float,
    p0: float = 1.0,
) -> list[tuple[float, float]]:
    """Predict coordination success at each ratio from Theorem 1.

    Returns a list of (ratio, predicted_success) pairs where:
        predicted_success = p0 if q(r)^N >= theta, else 0.

    For a smooth version (not binary), use predicted_success_smooth().
    """
    q_min = q_required(theta, n_compression_passes)
    result = []
    for ratio, q in sorted(token_recall_curve, key=lambda x: x[0]):
        if q >= q_min:
            result.append((ratio, p0))
        else:
            result.append((ratio, 0.0))
    return result


def predicted_success_smooth(
    token_recall_curve: list[tuple[float, float]],
    n_compression_passes: int,
    theta: float,
    p0: float = 1.0,
    steepness: float = 20.0,
) -> list[tuple[float, float]]:
    """Smooth predicted coordination success using a logistic transition.

    Instead of a hard threshold at q^N = theta, uses:
        P(success) = p0 / (1 + exp(-steepness * (q^N - theta)))

    This produces a smooth S-curve that matches the empirical cliff shape
    better than the hard threshold while remaining theory-grounded.
    """
    result = []
    for ratio, q in sorted(token_recall_curve, key=lambda x: x[0]):
        qn = q ** n_compression_passes
        prob = p0 / (1.0 + np.exp(-steepness * (qn - theta)))
        result.append((ratio, float(prob)))
    return result


def validate_prediction(
    token_recall_curve: list[tuple[float, float]],
    empirical_tau: float,
    n_compression_passes: int,
    theta: float,
) -> dict[str, Any]:
    """Compare predicted vs empirical cliff position.

    Returns a dict with:
        predicted_tau: from the theorem
        empirical_tau: from piecewise/logistic fit
        abs_error: |predicted - empirical|
        rel_error_pct: relative error as percentage
        q_min: required per-round token recall
        match: True if within 25% relative error
    """
    pred_tau = predicted_tau(token_recall_curve, n_compression_passes, theta)
    q_min = q_required(theta, n_compression_passes)

    if np.isinf(pred_tau) or np.isnan(empirical_tau):
        return {
            "predicted_tau": pred_tau,
            "empirical_tau": empirical_tau,
            "abs_error": float("nan"),
            "rel_error_pct": float("nan"),
            "q_min": q_min,
            "n_compression_passes": n_compression_passes,
            "theta": theta,
            "match": False,
        }

    abs_err = abs(pred_tau - empirical_tau)
    rel_err = abs_err / max(abs(empirical_tau), 1e-9) * 100

    return {
        "predicted_tau": pred_tau,
        "empirical_tau": empirical_tau,
        "abs_error": abs_err,
        "rel_error_pct": rel_err,
        "q_min": q_min,
        "n_compression_passes": n_compression_passes,
        "theta": theta,
        "match": rel_err <= 25.0,
    }


def extract_token_recall_curve(
    sweep_csv_path: str,
    compressor: str = "lingua2",
    family: str = "a",
) -> list[tuple[float, float]]:
    """Extract the token-recall curve from an H1/H2 sweep CSV.

    Reads the sweep_results.csv, filters to the given compressor and family,
    and returns (ratio, mean_token_recall) pairs.
    """
    import pandas as pd

    df = pd.read_csv(sweep_csv_path)
    sub = df[(df["compressor"] == compressor) & (df["family"] == family)]
    agg = sub.groupby("ratio")["token_recall"].mean().reset_index()
    return [(float(r), float(q)) for r, q in zip(agg["ratio"], agg["token_recall"])]


def extract_empirical_tau(
    sweep_csv_path: str,
    compressor: str = "lingua2",
    family: str = "a",
) -> float:
    """Extract the empirical tau from an H1/H2 sweep CSV using logistic fit."""
    import pandas as pd

    from m6.experiments.run_h1_h2 import fit_piecewise

    df = pd.read_csv(sweep_csv_path)
    sub = df[(df["compressor"] == compressor) & (df["family"] == family)]
    agg = sub.groupby("ratio")["coord_success"].mean().reset_index()
    fit = fit_piecewise(agg["ratio"].to_numpy(), agg["coord_success"].to_numpy())
    # Prefer logistic tau if available
    return fit.get("logistic_tau", fit["tau"])


def full_validation(
    sweep_csv_path: str,
    n_compression_passes: int = 1,
    theta: float = 0.5,
    compressors: list[str] | None = None,
    families: list[str] | None = None,
) -> dict[str, Any]:
    """Run full predicted-vs-empirical validation across compressors and families.

    Returns a nested dict: {compressor: {family: validation_result}}.
    """
    if compressors is None:
        compressors = ["lingua2", "phi3-extractive", "filter"]
    if families is None:
        families = ["a", "b", "c"]

    results: dict[str, Any] = {}
    for comp in compressors:
        results[comp] = {}
        for fam in families:
            try:
                curve = extract_token_recall_curve(sweep_csv_path, comp, fam)
                emp_tau = extract_empirical_tau(sweep_csv_path, comp, fam)
                results[comp][fam] = validate_prediction(curve, emp_tau, n_compression_passes, theta)
            except Exception as e:
                results[comp][fam] = {"error": str(e)}

    # Summary
    all_validations = [
        v for comp_results in results.values()
        for v in comp_results.values()
        if isinstance(v, dict) and "match" in v
    ]
    n_match = sum(1 for v in all_validations if v["match"])
    results["_summary"] = {
        "n_validated": len(all_validations),
        "n_match": n_match,
        "match_rate": n_match / max(len(all_validations), 1),
        "n_compression_passes": n_compression_passes,
        "theta": theta,
    }
    return results


def cross_validate_theta(
    sweep_csv_path: str,
    families: list[str] | None = None,
    compressors: list[str] | None = None,
    n_compression_passes: int = 1,
    recall_column: str = "token_recall",
) -> dict[str, Any]:
    """Leave-one-family-out cross-validation for theta.

    For each held-out family:
      1. Derive theta from the other families
      2. Predict tau on the held-out family
      3. Compare to empirical tau

    This addresses the circularity critique: theta is never derived and
    validated on the same data.

    Returns dict with per-family results and overall match rate.
    """
    if families is None:
        families = ["a", "b", "c"]

    results: dict[str, Any] = {}
    for held_out in families:
        train_families = [f for f in families if f != held_out]

        # Derive theta from training families
        train_thetas = []
        for train_fam in train_families:
            dt = derive_theta(
                sweep_csv_path,
                family=train_fam,
                compressors=compressors,
                recall_column=recall_column,
            )
            train_thetas.append(dt["mean_theta"])
        theta_cv = float(np.mean(train_thetas)) if train_thetas else 0.5

        # Validate on held-out family
        val_results = {}
        comps = compressors or ["lingua2", "phi3-extractive", "filter"]
        for comp in comps:
            try:
                curve = extract_token_recall_curve(sweep_csv_path, comp, held_out)
                emp_tau = extract_empirical_tau(sweep_csv_path, comp, held_out)
                val_results[comp] = validate_prediction(
                    curve, emp_tau, n_compression_passes, theta_cv
                )
            except Exception as e:
                val_results[comp] = {"error": str(e)}

        results[held_out] = {
            "theta_cv": theta_cv,
            "train_families": train_families,
            "validations": val_results,
        }

    # Summary
    all_vals = [
        v
        for fam_result in results.values()
        for v in fam_result["validations"].values()
        if isinstance(v, dict) and "match" in v
    ]
    n_match = sum(1 for v in all_vals if v["match"])
    results["_summary"] = {
        "n_validated": len(all_vals),
        "n_match": n_match,
        "match_rate": n_match / max(len(all_vals), 1),
    }
    return results


def theta_sensitivity(
    sweep_csv_path: str,
    theta_values: list[float] | None = None,
    compressors: list[str] | None = None,
    families: list[str] | None = None,
    n_compression_passes: int = 1,
) -> dict[str, Any]:
    """Sensitivity analysis: predicted tau across a range of theta values.

    For each (theta, compressor, family), computes predicted_tau and compares
    to empirical_tau. Shows how robust the cliff prediction is to theta choice.

    Returns dict with per-theta validation results.
    """
    if theta_values is None:
        theta_values = [0.3, 0.4, 0.5, 0.6, 0.7]
    if compressors is None:
        compressors = ["lingua2", "phi3-extractive", "filter"]
    if families is None:
        families = ["a", "b", "c"]

    results: dict[str, Any] = {}
    for theta in theta_values:
        theta_key = f"theta={theta:.1f}"
        validation = full_validation(
            sweep_csv_path,
            n_compression_passes=n_compression_passes,
            theta=theta,
            compressors=compressors,
            families=families,
        )
        results[theta_key] = validation

    # Per-family theta derivation
    per_family_theta = {}
    for fam in families:
        dt = derive_theta(sweep_csv_path, family=fam, compressors=compressors)
        per_family_theta[fam] = dt["mean_theta"]
    results["per_family_theta"] = per_family_theta

    return results


# ============================================================================
# Corollary 1: Model-Independence Validation (H5)
# ============================================================================

def validate_model_independence(
    h5_csv_path: str,
    baseline_threshold: float = 0.5,
    tau_tolerance_pct: float = 50.0,
    h1h2_csv_path: str | None = None,
) -> dict[str, Any]:
    """Test Corollary 1: cliff position is model-independent.

    For each family where at least 2 models have baseline >= baseline_threshold,
    fit piecewise cliffs and check that tau spread is within tau_tolerance_pct.

    Optionally compares H5 taus to H1/H2 deterministic solver taus (different
    solver architecture, same compressor) for cross-architecture validation.

    Args:
        h5_csv_path: Path to H5 results CSV (planner_model, ratio, family, coord_success).
        baseline_threshold: Minimum baseline coord_success to include a model.
        tau_tolerance_pct: Maximum allowed spread in tau across models (%).
        h1h2_csv_path: Optional H1/H2 sweep CSV for cross-architecture comparison.

    Returns:
        Dict with per-family results and overall verdict.
    """
    import pandas as pd

    from m6.experiments.run_h5 import fit_piecewise

    df = pd.read_csv(h5_csv_path)
    families = sorted(df["family"].unique())
    models = sorted(df["planner_model"].unique())

    per_family: dict[str, Any] = {}
    n_testable = 0
    n_invariant = 0

    for fam in families:
        fam_df = df[df["family"] == fam]

        # Check baselines
        baselines: dict[str, float] = {}
        taus: dict[str, float] = {}
        for model in models:
            sub = fam_df[fam_df["planner_model"] == model]
            baseline = float(sub[sub["ratio"] == 1.0]["coord_success"].mean()) if not sub[sub["ratio"] == 1.0].empty else 0.0
            baselines[model] = baseline

            if baseline >= baseline_threshold:
                agg = sub.groupby("ratio")["coord_success"].mean().reset_index()
                agg = agg.sort_values("ratio")
                fit = fit_piecewise(agg["ratio"].to_numpy(), agg["coord_success"].to_numpy())
                tau = fit.get("logistic_tau", fit.get("tau", float("nan")))
                taus[model] = tau

        valid_taus = {m: t for m, t in taus.items() if not np.isnan(t)}

        if len(valid_taus) >= 2:
            n_testable += 1
            tau_vals = list(valid_taus.values())
            tau_mean = np.mean(tau_vals)
            tau_spread = (max(tau_vals) - min(tau_vals)) / max(abs(tau_mean), 1e-9) * 100
            is_invariant = tau_spread <= tau_tolerance_pct

            if is_invariant:
                n_invariant += 1

            per_family[fam] = {
                "baselines": baselines,
                "taus": taus,
                "valid_taus": valid_taus,
                "tau_mean": float(tau_mean),
                "tau_spread_pct": float(tau_spread),
                "is_invariant": is_invariant,
                "n_models_tested": len(valid_taus),
                "floor_effect_models": [m for m, b in baselines.items() if b < baseline_threshold],
            }
        else:
            per_family[fam] = {
                "baselines": baselines,
                "taus": taus,
                "valid_taus": valid_taus,
                "skipped": True,
                "reason": f"<2 models with baseline >= {baseline_threshold}",
                "floor_effect_models": [m for m, b in baselines.items() if b < baseline_threshold],
            }

    # Cross-architecture comparison with H1/H2 if available
    cross_arch: dict[str, Any] = {}
    if h1h2_csv_path:
        h12_df = pd.read_csv(h1h2_csv_path)
        # Get lingua2 (same compressor as H5) tau per family from deterministic solver
        for fam in families:
            sub = h12_df[(h12_df["compressor"] == "lingua2") & (h12_df["family"] == fam)]
            if sub.empty:
                continue
            agg = sub.groupby("ratio")["coord_success"].mean().reset_index()
            fit = fit_piecewise(agg["ratio"].to_numpy(), agg["coord_success"].to_numpy())
            det_tau = fit.get("logistic_tau", fit.get("tau", float("nan")))
            h5_tau = per_family.get(fam, {}).get("tau_mean", float("nan"))
            if not np.isnan(det_tau) and not np.isnan(h5_tau):
                diff_pct = abs(det_tau - h5_tau) / max(abs(det_tau), 1e-9) * 100
                cross_arch[fam] = {
                    "deterministic_tau": float(det_tau),
                    "h5_mean_tau": float(h5_tau),
                    "diff_pct": float(diff_pct),
                    "match": diff_pct <= tau_tolerance_pct,
                }

    supported = n_invariant >= 1 and n_testable >= 1
    return {
        "per_family": per_family,
        "cross_architecture": cross_arch,
        "n_testable_families": n_testable,
        "n_invariant_families": n_invariant,
        "corollary1_supported": supported,
        "baseline_threshold": baseline_threshold,
        "tau_tolerance_pct": tau_tolerance_pct,
    }


# ============================================================================
# Corollary 2: Task-Dependent Theta
# ============================================================================

def estimate_task_theta(
    results_csv_path: str,
    success_col: str = "coord_success",
    ratio_col: str = "ratio",
    success_threshold: float = 0.5,
    recall_col: str | None = None,
) -> dict[str, Any]:
    """Estimate theta for any task from its coord_success vs ratio curve.

    If recall_col is available, theta = token_recall at the cliff ratio.
    Otherwise, estimate from the success curve shape: theta ~ ratio at which
    success drops below success_threshold, mapped through the compressor's
    typical q(r) curve.

    Args:
        results_csv_path: CSV with at least ratio and coord_success columns.
        success_col: Column name for coordination success.
        ratio_col: Column name for compression ratio.
        success_threshold: Threshold for defining the cliff.
        recall_col: Optional token_recall column for direct theta estimation.

    Returns:
        Dict with estimated theta and supporting data.
    """
    import pandas as pd

    df = pd.read_csv(results_csv_path)
    agg = df.groupby(ratio_col)[success_col].mean().reset_index()
    agg = agg.sort_values(ratio_col)

    # Find cliff ratio (first ratio where success < threshold)
    baseline = float(agg[agg[ratio_col] == 1.0][success_col].mean()) if not agg[agg[ratio_col] == 1.0].empty else float(agg.iloc[0][success_col])
    cliff_ratio = float("nan")
    for _, row in agg.iterrows():
        if row[ratio_col] > 1.0 and row[success_col] < success_threshold * baseline:
            cliff_ratio = float(row[ratio_col])
            break

    # If recall column available, get theta directly
    theta_from_recall = float("nan")
    if recall_col and recall_col in df.columns:
        recall_agg = df.groupby(ratio_col)[recall_col].mean().reset_index()
        recall_agg = recall_agg.sort_values(ratio_col)
        if not np.isnan(cliff_ratio):
            closest = recall_agg.iloc[(recall_agg[ratio_col] - cliff_ratio).abs().argsort()[:1]]
            theta_from_recall = float(closest[recall_col].iloc[0])

    # Estimate theta from success curve shape
    # Use the AUC-normalized metric: tasks where success decays slowly have low theta
    ratios = agg[ratio_col].to_numpy()
    success = agg[success_col].to_numpy()
    if len(ratios) >= 2 and baseline > 0:
        # Normalized AUC: area under (success/baseline) vs ratio
        norm_success = np.clip(success / baseline, 0, 1)
        auc = float(np.trapz(norm_success, ratios) / (ratios[-1] - ratios[0]))
        # Map AUC to theta estimate: low AUC = high theta (info-dense), high AUC = low theta
        theta_from_curve = float(1.0 - auc)
    else:
        auc = float("nan")
        theta_from_curve = float("nan")

    # Best estimate: prefer recall-based, fall back to curve-based
    theta_est = theta_from_recall if not np.isnan(theta_from_recall) else theta_from_curve

    return {
        "theta_estimate": theta_est,
        "theta_from_recall": theta_from_recall,
        "theta_from_curve": theta_from_curve,
        "cliff_ratio": cliff_ratio,
        "baseline": baseline,
        "normalized_auc": auc if not np.isnan(auc) else None,
        "n_ratios": len(ratios),
    }


def validate_task_theta(
    task_results: dict[str, str],
    h1h2_csv_path: str | None = None,
) -> dict[str, Any]:
    """Test Corollary 2: theta varies with task information density.

    Takes results from multiple tasks and shows that theta correlates with
    task structure (dense quantitative vs distributed qualitative).

    Args:
        task_results: Dict mapping task name to results CSV path.
            e.g. {"c1-family-a": "results/h1_h2_final/sweep_results.csv", ...}
        h1h2_csv_path: Optional path for per-family theta derivation.

    Returns:
        Dict with per-task theta estimates and correlation analysis.
    """
    per_task: dict[str, Any] = {}

    # Get per-family thetas from H1/H2 if available
    if h1h2_csv_path:
        for fam in ["a", "b", "c"]:
            key = f"c1-family-{fam}"
            try:
                dt = derive_theta(h1h2_csv_path, family=fam)
                per_task[key] = {
                    "theta": dt["mean_theta"],
                    "source": "derive_theta",
                    "per_compressor": dt["per_compressor"],
                }
            except Exception as e:
                per_task[key] = {"error": str(e)}

    # Estimate theta for each additional task
    for task_name, csv_path in task_results.items():
        if task_name.startswith("c1-family-"):
            continue  # Already handled above
        try:
            est = estimate_task_theta(csv_path)
            per_task[task_name] = {
                "theta": est["theta_estimate"],
                "theta_from_recall": est["theta_from_recall"],
                "theta_from_curve": est["theta_from_curve"],
                "cliff_ratio": est["cliff_ratio"],
                "baseline": est["baseline"],
                "source": "estimate_task_theta",
            }
        except Exception as e:
            per_task[task_name] = {"error": str(e)}

    # Correlation: do tasks with higher theta cliff earlier?
    valid = [(v["theta"], v.get("cliff_ratio", float("nan")))
             for v in per_task.values()
             if isinstance(v, dict) and "theta" in v
             and not np.isnan(v.get("theta", float("nan")))]

    correlation = float("nan")
    if len(valid) >= 3:
        thetas_arr = np.array([t for t, _ in valid])
        # Higher theta should mean earlier cliff (lower cliff_ratio)
        # But cliff_ratio may be NaN for some tasks
        cliffs = [c for _, c in valid if not np.isnan(c)]
        thetas_for_corr = [t for t, c in valid if not np.isnan(c)]
        if len(cliffs) >= 3:
            from scipy import stats
            rho, p = stats.spearmanr(thetas_for_corr, cliffs)
            correlation = float(rho)

    return {
        "per_task": per_task,
        "theta_cliff_correlation": correlation,
        "n_tasks": len(per_task),
        "corollary2_note": "Higher theta (denser information) should correlate with earlier cliff (lower ratio).",
    }


def full_validation_per_family(
    sweep_csv_path: str,
    n_compression_passes: int = 1,
    compressors: list[str] | None = None,
    families: list[str] | None = None,
) -> dict[str, Any]:
    """Run validation using per-family theta instead of global theta.

    This should produce better predictions than full_validation() with a
    single global theta, since theta is task-specific (Corollary 2).
    """
    if compressors is None:
        compressors = ["lingua2", "phi3-extractive", "filter"]
    if families is None:
        families = ["a", "b", "c"]

    # Derive per-family theta
    per_family_theta: dict[str, float] = {}
    for fam in families:
        dt = derive_theta(sweep_csv_path, family=fam, compressors=compressors)
        per_family_theta[fam] = dt["mean_theta"]

    results: dict[str, Any] = {}
    for comp in compressors:
        results[comp] = {}
        for fam in families:
            theta_f = per_family_theta[fam]
            try:
                curve = extract_token_recall_curve(sweep_csv_path, comp, fam)
                emp_tau = extract_empirical_tau(sweep_csv_path, comp, fam)
                results[comp][fam] = validate_prediction(curve, emp_tau, n_compression_passes, theta_f)
            except Exception as e:
                results[comp][fam] = {"error": str(e)}

    # Summary
    all_validations = [
        v for comp_results in results.values()
        for v in comp_results.values()
        if isinstance(v, dict) and "match" in v
    ]
    n_match = sum(1 for v in all_validations if v["match"])
    results["_summary"] = {
        "n_validated": len(all_validations),
        "n_match": n_match,
        "match_rate": n_match / max(len(all_validations), 1),
        "n_compression_passes": n_compression_passes,
        "per_family_theta": per_family_theta,
    }
    return results
