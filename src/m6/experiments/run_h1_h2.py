#!/usr/bin/env python3
"""H1 + H2 — Coordination cliff sweep.

H1: Spearman rho(delta_qa, delta_coord) < 0.6 on >= 2 of 3 compressors.
H2: Piecewise-linear cliff with >= 30% drop, Mann-Whitney p < 0.05 on >= 7/9 cells.

Both hypotheses share the same data sweep. H1 metrics are extracted in post.

Run:
    python -m m6.experiments.run_h1_h2
    python -m m6.experiments.run_h1_h2 --smoke   # quick smoke test
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import optimize, stats

from m6.agents.orchestrator import AgentConfig, PlannerWorkerCritic
from m6.benchmark.generator import load as load_benchmark
from m6.benchmark.schemas import Workload, WorkloadTrace
from m6.compressors import make_compressor


# ============================================================================
# Config
# ============================================================================
@dataclass
class SweepConfig:
    benchmark_path: str = "data/processed/c1-v0.1"
    compressors: list[str] | None = None
    ratios: list[float] | None = None
    # Per-compressor ratio overrides: phi3-extractive uses fewer ratios
    # to keep runtime manageable (~12s/fragment vs ~0.01s for lingua2).
    compressor_ratios: dict[str, list[float]] | None = None
    seeds: list[int] | None = None
    families: list[str] | None = None
    n_workloads: int | None = None  # None = all
    out_dir: str = "results/h1_h2"

    def __post_init__(self):
        if self.compressors is None:
            self.compressors = ["lingua2", "phi3-extractive", "filter"]
        if self.ratios is None:
            self.ratios = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0]
        if self.compressor_ratios is None:
            self.compressor_ratios = {
                "phi3-extractive": [1.0, 4.0, 8.0, 12.0, 16.0],
            }
        if self.seeds is None:
            self.seeds = [0, 1, 2, 3, 4]
        if self.families is None:
            self.families = ["a", "b", "c"]

    def ratios_for(self, compressor: str) -> list[float]:
        """Return ratios for a given compressor (fewer for slow ones)."""
        if self.compressor_ratios and compressor in self.compressor_ratios:
            return self.compressor_ratios[compressor]
        return self.ratios

    @classmethod
    def smoke(cls) -> SweepConfig:
        return cls(
            compressors=["lingua2", "phi3-extractive", "filter"],
            ratios=[1.0, 4.0, 8.0, 16.0],
            compressor_ratios={"phi3-extractive": [1.0, 4.0]},
            seeds=[0],
            families=["a"],
            n_workloads=3,
            out_dir="results/h1_h2_smoke",
        )


# ============================================================================
# QA metrics (inline — avoids deep import chains)
# ============================================================================
def _normalize(s: str) -> str:
    import re
    import string

    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def f1_score(prediction: str, reference: str) -> float:
    from collections import Counter

    p_tokens = _normalize(prediction).split()
    r_tokens = _normalize(reference).split()
    if not p_tokens or not r_tokens:
        return float(p_tokens == r_tokens)
    common = Counter(p_tokens) & Counter(r_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(p_tokens)
    recall = num_same / len(r_tokens)
    return 2 * precision * recall / (precision + recall)


def em_score(prediction: str, reference: str) -> float:
    return float(_normalize(prediction) == _normalize(reference))


def token_recall(source: str, compressed: str, gold_answer: str = "") -> float:
    """Fraction of source tokens preserved in compressed text.

    Used by the compounding-error model in Chapter 5: q = token_recall;
    surviving info after N rounds ~ q^N.

    Measures how many of the *source* tokens survive compression, not
    gold-answer tokens (which may be aggregated and not appear in any
    single fragment).
    """
    target_tokens = set(_normalize(source).split())
    comp_tokens = set(_normalize(compressed).split())
    if not target_tokens:
        return 1.0
    return len(target_tokens & comp_tokens) / len(target_tokens)


# ============================================================================
# Coordination metrics (inline)
# ============================================================================
def score_coordination(workload: Workload, trace: WorkloadTrace) -> dict[str, float]:
    """Compute coordination metrics. Returns dict with final_success, subtask_acc, etc."""
    family = workload.family.value
    if family == "a":
        # Use numeric scoring: success if both hours and budget within 25% error
        f1 = _score_family_a(workload.expected_answer, trace.final_answer)
        success = float(f1 > 0.75)
    elif family == "b":
        success = _success_b(workload, trace)
    else:
        success = float(_norm(trace.final_answer) == _norm(workload.expected_answer))

    subtask_acc = 1.0
    if workload.sub_tasks:
        correct = sum(
            1
            for st in workload.sub_tasks
            if trace.sub_task_assignments.get(st.sub_task_id, "") == st.expected_solver
        )
        subtask_acc = correct / len(workload.sub_tasks)

    critic_rate = trace.critic_flag_count / max(trace.rounds, 1)
    return {
        "coord_success": success,
        "subtask_acc": subtask_acc,
        "rounds": trace.rounds,
        "critic_rate": critic_rate,
    }


def _norm(s: str) -> str:
    return " ".join(s.lower().split())


def _success_b(workload: Workload, trace: WorkloadTrace) -> float:
    if trace.final_status != "DONE":
        return 0.0
    if len(trace.sub_task_assignments) != len(workload.sub_tasks):
        return 0.0
    capacities = workload.metadata.get("capacities", "")
    if not (isinstance(capacities, str) and capacities):
        return 0.0
    cap_list = [int(x) for x in capacities.split(",")]
    load_by_worker: dict[str, int] = {}
    for st in workload.sub_tasks:
        assigned = trace.sub_task_assignments.get(st.sub_task_id, "")
        load = int(st.constraints.get("load", 1) or 1)
        load_by_worker[assigned] = load_by_worker.get(assigned, 0) + load
    for worker_str, load_val in load_by_worker.items():
        if not worker_str.startswith("worker-"):
            return 0.0
        idx = int(worker_str.split("-", 1)[1])
        if idx >= len(cap_list) or load_val > cap_list[idx]:
            return 0.0
    return 1.0


# ============================================================================
# Family-aware answer scoring (matches H5's _score_answer logic)
# ============================================================================
def _score_family_a(expected: str, answer: str) -> float:
    """Extract hours and budget numbers, score by relative error."""
    import re as _re

    def _extract_nums(s: str) -> dict[str, int | None]:
        nums: dict[str, int | None] = {"hours": None, "budget": None}
        m = _re.search(r"hours\s*[=:]?\s*(\d[\d,]*)", s, _re.IGNORECASE)
        if m:
            nums["hours"] = int(m.group(1).replace(",", ""))
        m = _re.search(r"budget\s*[=:]?\s*(?:EUR\s*)?(\d[\d,]*)", s, _re.IGNORECASE)
        if m:
            nums["budget"] = int(m.group(1).replace(",", ""))
        return nums

    exp_nums = _extract_nums(expected)
    ans_nums = _extract_nums(answer)
    scores = []
    for key in ["hours", "budget"]:
        ev, av = exp_nums.get(key), ans_nums.get(key)
        if ev is not None and av is not None and ev > 0:
            scores.append(max(0.0, 1.0 - abs(ev - av) / ev))
        elif ev is not None and av is None:
            scores.append(0.0)
    return sum(scores) / len(scores) if scores else 0.0


def _score_family_b(expected: str, answer: str) -> float:
    """Compare sub-task assignments."""
    def _parse(s: str) -> dict[str, str]:
        return {m.group(1).lower(): m.group(2).lower()
                for m in re.finditer(r"(sub-\d+)\s*=\s*(worker-\d+)", s, re.IGNORECASE)}
    exp_map, ans_map = _parse(expected), _parse(answer)
    if not exp_map:
        return 0.0
    return sum(1 for k, v in exp_map.items() if ans_map.get(k) == v) / len(exp_map)


def _score_family_c(expected: str, answer: str) -> float:
    """Extract FINAL-XXXX and compare."""
    exp_m = re.search(r"FINAL-(\d+)", expected, re.IGNORECASE)
    ans_m = re.search(r"FINAL-(\d+)", answer, re.IGNORECASE)
    if exp_m and ans_m and exp_m.group(1) == ans_m.group(1):
        return 1.0
    return 0.0


def _score_answer(workload: Workload, answer: str) -> float:
    """Score answer using family-aware logic."""
    fam = workload.family.value
    if fam == "a":
        return _score_family_a(workload.expected_answer, answer)
    elif fam == "b":
        return _score_family_b(workload.expected_answer, answer)
    return _score_family_c(workload.expected_answer, answer)


# ============================================================================
# Single-agent QA (compress + concatenate, NO orchestrator)
# ============================================================================
def single_agent_qa(
    workload: Workload, compressor: Any, *, _precomputed: list[str] | None = None
) -> float:
    """Information-preservation metric (column: qa_f1): token F1 of compressed
    text vs original source text.

    NOTE: Despite the column name "qa_f1", this is NOT QA accuracy against
    gold answers. It measures how much source content survives compression
    (token recall/precision). This is deliberately different from coord_success
    (family-specific deterministic solver, binary) so that H1 can test whether
    information preservation and coordination success degrade at different
    rates under compression.

    If ``_precomputed`` is provided, skips compression (already cached).
    """
    if _precomputed is not None:
        parts = _precomputed
    else:
        parts = []
        for frag in workload.fragments:
            frag_with_hint = frag.model_copy(update={"task_hint": workload.initial_prompt})
            slot = compressor.compress(frag_with_hint)
            text = compressor.decompress(slot) or frag.text
            parts.append(text)
    synthesized = " ".join(parts)
    source_text = " ".join(frag.text for frag in workload.fragments)
    return f1_score(synthesized, source_text)


# ============================================================================
# Multi-agent coordination (full planner-worker-critic)
# ============================================================================
def run_multi_agent(workload: Workload, compressor: Any, seed: int) -> WorkloadTrace:
    """Run the deterministic planner-worker-critic on compressed fragments."""
    import asyncio

    orchestrator = PlannerWorkerCritic(
        cfg=AgentConfig(backend="determ"),
        compressor=compressor,
    )
    return asyncio.run(orchestrator.run(workload, seed=seed))


# ============================================================================
# Statistics (inline — bootstrap Spearman, cliff fitting, Mann-Whitney)
# ============================================================================
def spearman_with_ci(x: np.ndarray, y: np.ndarray, n_boot: int = 10000) -> dict:
    rho, p = stats.spearmanr(x, y)
    rng = np.random.default_rng(42)
    n = len(x)
    rhos = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        r, _ = stats.spearmanr(x[idx], y[idx])
        rhos[i] = r
    rhos_clean = rhos[~np.isnan(rhos)]
    ci_lo = float(np.quantile(rhos_clean, 0.025)) if len(rhos_clean) > 0 else float("nan")
    ci_hi = float(np.quantile(rhos_clean, 0.975)) if len(rhos_clean) > 0 else float("nan")
    return {
        "rho": float(rho) if not np.isnan(rho) else 0.0,
        "p": float(p) if not np.isnan(p) else 1.0,
        "ci_low": ci_lo,
        "ci_high": ci_hi,
        "n": n,
    }


def fit_piecewise(ratios: np.ndarray, success: np.ndarray) -> dict:
    """Fit two-piece linear model with breakpoint tau."""
    x = np.asarray(ratios, dtype=np.float64)
    y = np.asarray(success, dtype=np.float64)
    n = len(x)
    if n < 4:
        return {"tau": float("nan"), "drop_rel": 0.0, "rmse": float("nan")}

    # If no variation in y, no cliff to detect
    if float(np.ptp(y)) < 1e-6:
        return {"tau": float("nan"), "drop_rel": 0.0, "rmse": float("nan")}
    y_range = float(np.ptp(y))

    def _objective(params):
        tau, sl, sd, intercept = params
        sr = sl - max(sd, 0.0)
        preds = np.where(x <= tau, intercept + sl * (x - tau), intercept + sr * (x - tau))
        return float(np.mean((preds - y) ** 2))

    # Constrain tau to interior: need data points on both sides of the breakpoint
    x_margin = (x.max() - x.min()) * 0.1  # 10% margin from edges
    bounds = [
        (float(x.min() + x_margin), float(x.max() - x_margin)),
        (-2.0 / y_range, 2.0 / y_range),
        (0.0, 4.0 / y_range),
        (float(y.min() - 1.0), float(y.max() + 1.0)),
    ]
    result = optimize.differential_evolution(
        _objective, bounds=bounds, seed=0, maxiter=3000, tol=1e-6, polish=True
    )
    tau, sl, sd, intercept = result.x
    sr = sl - max(sd, 0.0)
    preds = np.where(x <= tau, intercept + sl * (x - tau), intercept + sr * (x - tau))
    rmse = float(np.sqrt(np.mean((preds - y) ** 2)))

    left_eval = float(intercept + sl * (x.min() - tau))
    right_eval = float(intercept + sr * (x.max() - tau))
    drop_rel = (left_eval - right_eval) / max(abs(left_eval), 1e-6)

    # Also fit logistic model for comparison: y = L / (1 + exp(k*(x - tau_l)))
    logistic_fit = _fit_logistic(x, y)

    return {
        "tau": float(tau),
        "slope_left": float(sl),
        "slope_right": float(sr),
        "intercept": float(intercept),
        "drop_rel": float(drop_rel),
        "rmse": rmse,
        "logistic_tau": logistic_fit["tau"],
        "logistic_rmse": logistic_fit["rmse"],
        "model_selected": "logistic" if logistic_fit["rmse"] < rmse else "piecewise",
    }


def _fit_logistic(x: np.ndarray, y: np.ndarray) -> dict:
    """Fit logistic cliff: y = floor + (ceil - floor) / (1 + exp(k*(x - tau)))."""
    if len(x) < 4 or float(np.ptp(y)) < 1e-6:
        return {"tau": float("nan"), "rmse": float("nan")}

    def _obj(params):
        tau, k, ceil_val, floor_val = params
        preds = floor_val + (ceil_val - floor_val) / (1.0 + np.exp(k * (x - tau)))
        return float(np.mean((preds - y) ** 2))

    x_margin = (x.max() - x.min()) * 0.1
    bounds = [
        (float(x.min() + x_margin), float(x.max() - x_margin)),  # tau
        (0.01, 10.0),    # k (steepness, positive = decreasing)
        (0.0, 1.5),      # ceil
        (-0.5, 1.0),     # floor
    ]
    result = optimize.differential_evolution(_obj, bounds=bounds, seed=0, maxiter=3000)
    tau, k, ceil_val, floor_val = result.x
    preds = floor_val + (ceil_val - floor_val) / (1.0 + np.exp(k * (x - tau)))
    rmse = float(np.sqrt(np.mean((preds - y) ** 2)))
    return {"tau": float(tau), "k": float(k), "rmse": rmse}


def holm_correction(p_values: list[float]) -> list[float]:
    n = len(p_values)
    if n == 0:
        return []
    order = sorted(range(n), key=lambda i: p_values[i])
    adj = [0.0] * n
    running = 0.0
    for rank, idx in enumerate(order):
        candidate = (n - rank) * p_values[idx]
        running = max(running, candidate)
        adj[idx] = min(running, 1.0)
    return adj


# ============================================================================
# Main sweep
# ============================================================================
def run_sweep(cfg: SweepConfig) -> pd.DataFrame:
    """Run the full H1+H2 sweep. Returns a long-format DataFrame."""
    print(f"Loading benchmark from {cfg.benchmark_path}...")
    workloads = load_benchmark(cfg.benchmark_path)
    family_set = set(cfg.families)
    workloads = [w for w in workloads if w.family.value in family_set]
    if cfg.n_workloads:
        workloads = workloads[: cfg.n_workloads]
    print(f"  {len(workloads)} workloads loaded")

    total_cells = sum(
        len(cfg.ratios_for(c)) * len(workloads) * len(cfg.seeds)
        for c in cfg.compressors
    )
    print(f"  Total cells: {total_cells}")

    rows: list[dict[str, Any]] = []
    compressor_cache: dict[tuple[str, float], Any] = {}
    # Cache compressed text per (compressor, ratio, fragment_id) — avoids
    # redundant Ollama calls across seeds and between qa/coord/token_recall.
    # At temp=0 same input always produces same output.
    compressed_text_cache: dict[tuple[str, float, str], str] = {}
    done = 0
    t_start = time.time()

    # Incremental save path — write partial results every 500 cells
    # so progress survives crashes.
    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    partial_csv = out_dir / "sweep_results.partial.csv"

    def _compress_fragment(comp: Any, comp_name: str, ratio: float, frag: Any, hint: str = "") -> str:
        cache_key = (comp_name, ratio, frag.fragment_id)
        if cache_key not in compressed_text_cache:
            frag_with_hint = frag.model_copy(update={"task_hint": hint})
            slot = comp.compress(frag_with_hint)
            compressed_text_cache[cache_key] = comp.decompress(slot) or frag.text
        return compressed_text_cache[cache_key]

    for comp_name in cfg.compressors:
        for ratio in cfg.ratios_for(comp_name):
            key = (comp_name, ratio)
            if key not in compressor_cache:
                print(f"  Building compressor {comp_name} @ {ratio}x...")
                compressor_cache[key] = make_compressor(comp_name, target_ratio=ratio)
            comp = compressor_cache[key]

            for w in workloads:
                # Compress all fragments once (cached across seeds)
                compressed_parts = [
                    _compress_fragment(comp, comp_name, ratio, frag, hint=w.initial_prompt)
                    for frag in w.fragments
                ]

                # Single-agent QA (same for all seeds — deterministic)
                qa_f1 = single_agent_qa(w, comp, _precomputed=compressed_parts)
                qa_em = em_score(
                    " ".join(compressed_parts),
                    w.expected_answer,
                )

                # Token recall for compounding-error model (per tech ref §9)
                tr = 0.0
                for frag, ct in zip(w.fragments, compressed_parts, strict=False):
                    tr += token_recall(frag.text, ct)
                avg_token_recall = tr / max(len(w.fragments), 1)

                for seed in cfg.seeds:
                    # Multi-agent coordination
                    trace = run_multi_agent(w, comp, seed)
                    coord = score_coordination(w, trace)

                    rows.append(
                        {
                            "compressor": comp_name,
                            "ratio": ratio,
                            "family": w.family.value,
                            "workload_id": w.workload_id,
                            "seed": seed,
                            "qa_f1": qa_f1,
                            "qa_em": qa_em,
                            "coord_success": coord["coord_success"],
                            "subtask_acc": coord["subtask_acc"],
                            "rounds": coord["rounds"],
                            "critic_rate": coord["critic_rate"],
                            "token_recall": avg_token_recall,
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                    )

                    done += 1
                    if done % 100 == 0 or done == total_cells:
                        elapsed = time.time() - t_start
                        eta = (elapsed / done) * (total_cells - done) if done > 0 else 0
                        print(f"  [{done}/{total_cells}] {elapsed:.0f}s elapsed, ETA {eta:.0f}s")
                        sys.stdout.flush()
                    # Incremental save every 500 cells
                    if done % 500 == 0:
                        pd.DataFrame(rows).to_csv(partial_csv, index=False)

    df = pd.DataFrame(rows)
    # Remove partial file now that we have the full result
    partial_csv.unlink(missing_ok=True)
    return df


# ============================================================================
# H1 Verdict
# ============================================================================
def compute_h1_verdict(df: pd.DataFrame) -> dict:
    """Spearman rho(delta_qa, delta_coord) < 0.6 on >= 2/3 compressors.

    Per plan-v3: 95% bootstrap CI must exclude 0.6 from above (ci_high < 0.6).
    """
    verdicts = {}
    n_below = 0
    for comp, sub in df.groupby("compressor"):
        # Average coord_success across seeds to avoid inflating N
        # (qa_f1 is seed-invariant, so duplicates would tighten CI artificially)
        agg = sub.groupby(["workload_id", "ratio"]).agg(
            qa_f1=("qa_f1", "first"),  # same across seeds
            coord_success=("coord_success", "mean"),  # average across seeds
        ).reset_index()

        # Get reference (ratio=1) values per workload
        ref = agg[agg["ratio"] == 1.0][["workload_id", "qa_f1", "coord_success"]]
        ref = ref.rename(columns={"qa_f1": "qa_ref", "coord_success": "coord_ref"})
        merged = agg.merge(ref, on=["workload_id"], how="left")
        merged = merged[merged["ratio"] != 1.0].dropna(
            subset=["qa_f1", "coord_success", "qa_ref", "coord_ref"]
        )

        if merged.empty:
            verdicts[comp] = {"note": "no non-baseline rows"}
            continue

        delta_qa = (merged["qa_f1"] - merged["qa_ref"]).to_numpy()
        delta_coord = (merged["coord_success"] - merged["coord_ref"]).to_numpy()
        result = spearman_with_ci(delta_qa, delta_coord)
        # Plan-v3 criterion: rho < 0.6 AND 95% CI upper bound < 0.6
        # NaN CI means insufficient data — do not count as supported
        supported = result["rho"] < 0.6 and not np.isnan(result["ci_high"]) and result["ci_high"] < 0.6
        result["supported"] = supported
        verdicts[comp] = result
        if supported:
            n_below += 1

    verdicts["h1_supported"] = n_below >= 2
    verdicts["n_below_threshold"] = n_below
    return verdicts


# ============================================================================
# H2 Verdict
# ============================================================================
def compute_h2_verdict(df: pd.DataFrame) -> dict:
    """Piecewise cliff fit + paired Wilcoxon signed-rank on 9 (compressor, family) cells."""
    cells = []
    tested_indices = []
    p_values = []

    for (comp, family), sub in df.groupby(["compressor", "family"]):
        agg = sub.groupby("ratio")["coord_success"].mean().reset_index()
        ratios_arr = agg["ratio"].to_numpy()
        success_arr = agg["coord_success"].to_numpy()

        if len(ratios_arr) < 4 or float(np.ptp(success_arr)) < 1e-6:
            cells.append(
                {
                    "compressor": comp,
                    "family": family,
                    "tau": None,
                    "drop_rel": 0.0,
                    "test_p": None,
                    "test_p_holm": None,
                    "n_pairs": 0,
                }
            )
            continue

        fit = fit_piecewise(ratios_arr, success_arr)

        # Paired test: for each workload, compare mean coord_success
        # below vs above tau (same workload in both groups → paired design)
        below_by_wl = sub[sub["ratio"] < fit["tau"]].groupby("workload_id")["coord_success"].mean()
        above_by_wl = sub[sub["ratio"] >= fit["tau"]].groupby("workload_id")["coord_success"].mean()
        paired = pd.DataFrame({"below": below_by_wl, "above": above_by_wl}).dropna()

        test_p = None
        n_pairs = len(paired)
        if n_pairs >= 10 and not np.allclose(paired["below"], paired["above"]):
            _, test_p = stats.wilcoxon(
                paired["below"], paired["above"], alternative="greater"
            )
            tested_indices.append(len(cells))
            p_values.append(test_p)

        cells.append(
            {
                "compressor": comp,
                "family": family,
                "tau": fit["tau"],
                "drop_rel": fit["drop_rel"],
                "rmse": fit["rmse"],
                "test_p": test_p,
                "test_p_holm": None,
                "n_pairs": n_pairs,
            }
        )

    # Holm correction
    adjusted = holm_correction(p_values) if p_values else []
    for cell_idx, adj in zip(tested_indices, adjusted, strict=False):
        cells[cell_idx]["test_p_holm"] = adj

    # Verdict: >= 7/9 cells with drop >= 30% AND significant
    n_significant_cliffs = 0
    for c in cells:
        if c["drop_rel"] is not None and c["drop_rel"] >= 0.30:
            p_holm = c.get("test_p_holm")
            if p_holm is not None and p_holm < 0.05:
                n_significant_cliffs += 1

    # Tau consistency check
    tau_spread = {}
    df_cells = pd.DataFrame(cells)
    if not df_cells.empty and "tau" in df_cells.columns:
        for family, fam_sub in df_cells.dropna(subset=["tau"]).groupby("family"):
            taus = fam_sub["tau"].to_numpy(dtype=float)
            if len(taus) > 1:
                spread = (taus.max() - taus.min()) / max(taus.mean(), 1e-6)
                tau_spread[family] = {
                    "spread_pct": float(spread * 100),
                    "within_20pct": spread <= 0.20,
                }

    return {
        "cells": cells,
        "n_significant_cliffs": n_significant_cliffs,
        "total_cells": len(cells),
        "h2_supported": n_significant_cliffs >= 7,
        "tau_spread": tau_spread,
    }


# ============================================================================
# Entry point
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="H1+H2: Coordination cliff sweep")
    parser.add_argument("--smoke", action="store_true", help="Quick smoke test")
    parser.add_argument("--out", type=str, default=None, help="Output directory")
    parser.add_argument(
        "--compressors", type=str, default=None, help="Comma-separated compressor names"
    )
    parser.add_argument("--ratios", type=str, default=None, help="Comma-separated ratios")
    parser.add_argument(
        "--families", type=str, default=None, help="Comma-separated families (a,b,c)"
    )
    parser.add_argument("--seeds", type=str, default=None, help="Comma-separated seeds")
    parser.add_argument("--n-workloads", type=int, default=None, help="Max workloads per family")
    args = parser.parse_args()

    if args.smoke:
        cfg = SweepConfig.smoke()
    else:
        cfg = SweepConfig()

    if args.out:
        cfg.out_dir = args.out
    if args.compressors:
        cfg.compressors = args.compressors.split(",")
    if args.ratios:
        cfg.ratios = [float(r) for r in args.ratios.split(",")]
    if args.families:
        cfg.families = args.families.split(",")
    if args.seeds:
        cfg.seeds = [int(s) for s in args.seeds.split(",")]
    if args.n_workloads:
        cfg.n_workloads = args.n_workloads

    print("=" * 60)
    print("H1+H2 Coordination Cliff Sweep")
    print("=" * 60)
    print(f"Compressors: {cfg.compressors}")
    print(f"Ratios: {cfg.ratios}")
    print(f"Families: {cfg.families}")
    print(f"Seeds: {cfg.seeds}")
    print(f"Output: {cfg.out_dir}")
    print()

    # Run sweep
    df = run_sweep(cfg)

    # Save raw data
    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "sweep_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nSaved {len(df)} rows to {csv_path}")

    # Compute verdicts
    print("\n" + "=" * 60)
    print("H1 VERDICT: QA vs Coordination Correlation")
    print("=" * 60)
    h1 = compute_h1_verdict(df)
    for comp, result in h1.items():
        if comp in ("h1_supported", "n_below_threshold"):
            continue
        if isinstance(result, dict) and "rho" in result:
            print(
                f"  {comp}: rho={result['rho']:.3f} [{result['ci_low']:.3f}, {result['ci_high']:.3f}] p={result['p']:.4f} n={result['n']}"
            )
    print(
        f"  => H1 SUPPORTED: {h1['h1_supported']} ({h1['n_below_threshold']}/3 compressors below 0.6)"
    )

    print("\n" + "=" * 60)
    print("H2 VERDICT: Coordination Cliff")
    print("=" * 60)
    h2 = compute_h2_verdict(df)
    for cell in h2["cells"]:
        tau_str = f"{cell['tau']:.1f}" if cell["tau"] else "N/A"
        p_str = f"{cell['test_p_holm']:.4f}" if cell["test_p_holm"] is not None else "N/A"
        print(
            f"  {cell['compressor']}/{cell['family']}: tau={tau_str} drop={cell['drop_rel']:.1%} p_holm={p_str}"
        )
    print(
        f"  => H2 SUPPORTED: {h2['h2_supported']} ({h2['n_significant_cliffs']}/{h2['total_cells']} cells)"
    )

    # Save verdicts
    verdicts = {
        "h1": h1,
        "h2": h2,
        "config": cfg.__dict__,
        "generated_at": datetime.now(UTC).isoformat(),
    }
    with open(out_dir / "verdicts.json", "w") as f:
        json.dump(verdicts, f, indent=2, default=str)
    print(f"\nVerdicts saved to {out_dir / 'verdicts.json'}")


if __name__ == "__main__":
    main()
