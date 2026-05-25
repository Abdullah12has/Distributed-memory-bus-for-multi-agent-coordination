"""Coordination Cliff Theorem — prediction and validation.

Theorem 1 (Coordination Cliff Bound):
  Consider a multi-agent system with N sequential information-extraction
  rounds, where each round applies a compressor C with per-token retention
  probability q(r) at compression ratio r. Let theta be the minimum fraction
  of task-relevant tokens required for coordination success. Then:

    (i)   P(success | r) <= p0 * q(r)^N
    (ii)  A coordination cliff exists at r* where q(r*) = theta^(1/N)
    (iii) r* depends only on C (through q) and the task (through N, theta),
          NOT on planner model capacity.

This module implements:
  - predicted_tau(): compute r* from a token-recall curve
  - q_required(): compute the minimum per-round token recall
  - validate_prediction(): compare predicted vs empirical cliff positions
  - plot_prediction(): generate the predicted-vs-empirical figure

Usage:
    from m6.theory.cliff_prediction import predicted_tau, validate_prediction

    # From H1/H2 sweep data
    token_recall_curve = [(1.0, 1.0), (2.0, 0.52), (4.0, 0.11), ...]
    tau_star = predicted_tau(token_recall_curve, n_rounds=3, theta=0.65)
"""

from __future__ import annotations

from typing import Any

import numpy as np


def q_required(theta: float, n_rounds: int) -> float:
    """Minimum per-round token recall to maintain coordination success.

    From Theorem 1(ii): q* = theta^(1/N).

    Args:
        theta: Minimum fraction of task-relevant tokens needed for success.
        n_rounds: Number of planner-worker-critic rounds.

    Returns:
        q*: the minimum per-round token recall.
    """
    if n_rounds <= 0:
        raise ValueError("n_rounds must be positive")
    if not 0 < theta <= 1:
        raise ValueError("theta must be in (0, 1]")
    return theta ** (1.0 / n_rounds)


def predicted_tau(
    token_recall_curve: list[tuple[float, float]],
    n_rounds: int,
    theta: float,
) -> float:
    """Predict the cliff position from a measured token-recall curve.

    Finds the compression ratio r* where q(r)^N first drops below theta,
    i.e., where q(r) < theta^(1/N). Uses linear interpolation between
    measured points for precision.

    Args:
        token_recall_curve: List of (ratio, token_recall) pairs, sorted by ratio.
        n_rounds: Typical rounds-to-completion (e.g., 3 for family-a).
        theta: Fraction of source information the planner needs to succeed.

    Returns:
        Predicted tau* (compression ratio at the cliff).
        Returns float("inf") if the cliff is outside the measured range.
    """
    q_min = q_required(theta, n_rounds)
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


def survival_probability(q: float, n_rounds: int) -> float:
    """Probability that task-relevant information survives N rounds.

    From Theorem 1(i): P(survive) = q^N.
    """
    return q ** n_rounds


def predicted_success_curve(
    token_recall_curve: list[tuple[float, float]],
    n_rounds: int,
    theta: float,
    p0: float = 1.0,
) -> list[tuple[float, float]]:
    """Predict coordination success at each ratio from Theorem 1.

    Returns a list of (ratio, predicted_success) pairs where:
        predicted_success = p0 if q(r)^N >= theta, else 0.

    For a smooth version (not binary), use predicted_success_smooth().
    """
    q_min = q_required(theta, n_rounds)
    result = []
    for ratio, q in sorted(token_recall_curve, key=lambda x: x[0]):
        if q >= q_min:
            result.append((ratio, p0))
        else:
            result.append((ratio, 0.0))
    return result


def predicted_success_smooth(
    token_recall_curve: list[tuple[float, float]],
    n_rounds: int,
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
        qn = q ** n_rounds
        prob = p0 / (1.0 + np.exp(-steepness * (qn - theta)))
        result.append((ratio, float(prob)))
    return result


def validate_prediction(
    token_recall_curve: list[tuple[float, float]],
    empirical_tau: float,
    n_rounds: int,
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
    pred_tau = predicted_tau(token_recall_curve, n_rounds, theta)
    q_min = q_required(theta, n_rounds)

    if np.isinf(pred_tau) or np.isnan(empirical_tau):
        return {
            "predicted_tau": pred_tau,
            "empirical_tau": empirical_tau,
            "abs_error": float("nan"),
            "rel_error_pct": float("nan"),
            "q_min": q_min,
            "n_rounds": n_rounds,
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
        "n_rounds": n_rounds,
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
    n_rounds: int = 3,
    theta: float = 0.65,
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
                results[comp][fam] = validate_prediction(curve, emp_tau, n_rounds, theta)
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
        "n_rounds": n_rounds,
        "theta": theta,
    }
    return results
