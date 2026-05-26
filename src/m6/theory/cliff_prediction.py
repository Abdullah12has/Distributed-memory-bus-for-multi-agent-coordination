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

This module implements:
  - predicted_tau(): compute r* from a token-recall curve
  - q_required(): compute the minimum token recall for coordination
  - chernoff_success_probability(): P(success) with finite-M sharpness
  - chernoff_success_curve(): full curve with M-dependent sharpness
  - cliff_sharpness(): transition width as a function of M
  - derive_theta(): empirically derive theta from sweep data
  - validate_prediction(): compare predicted vs empirical cliff positions

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
