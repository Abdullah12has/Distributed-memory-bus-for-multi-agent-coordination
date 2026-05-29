#!/usr/bin/env python3
"""CAAC vs fixed-ratio baselines — Pareto frontier experiment.

Compares Cliff-Aware Adaptive Compression (CAAC) against fixed-ratio
compression at matched target ratios. Shows that CAAC Pareto-dominates
by maintaining coordination success while achieving meaningful compression.

The key figure: achieved_ratio (x-axis) vs coord_success (y-axis).
Fixed compressors trace a cliff curve; CAAC traces a higher curve.

Run:
    python -m m6.experiments.run_caac
    python -m m6.experiments.run_caac --smoke
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from m6.agents.orchestrator import AgentConfig, PlannerWorkerCritic
from m6.benchmark.generator import load as load_benchmark
from m6.benchmark.schemas import Workload, WorkloadTrace
from m6.compressors import make_compressor
from m6.compressors.cache import CompressionCache, make_cached_compressor
from m6.compressors.caac import CAACCompressor, _token_recall
from m6.experiments.run_h1_h2 import score_coordination
from m6.theory.cliff_prediction import derive_theta


# ============================================================================
# Config
# ============================================================================
@dataclass
class CAACConfig:
    benchmark_path: str = "data/processed/c1-v0.1"
    inner_compressors: list[str] | None = None
    target_ratios: list[float] | None = None
    seeds: list[int] | None = None
    families: list[str] | None = None
    n_workloads: int | None = None
    n_compression_passes: int = 1
    theta: float = 0.5  # global fallback when prior_sweep_csv is None
    prior_sweep_csv: str | None = "results/h1_h2_v2/sweep_results.csv"
    recall_column: str = "critical_token_recall"
    out_dir: str = "results/caac"
    cache_path: str | None = None

    def __post_init__(self):
        if self.inner_compressors is None:
            self.inner_compressors = ["lingua2", "filter"]
        if self.target_ratios is None:
            self.target_ratios = [1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0]
        if self.seeds is None:
            self.seeds = [0, 1, 2]
        if self.families is None:
            self.families = ["a", "b", "c"]

    @classmethod
    def smoke(cls) -> CAACConfig:
        return cls(
            inner_compressors=["filter"],
            target_ratios=[1.0, 4.0, 8.0],
            seeds=[0],
            families=["a"],
            n_workloads=3,
            out_dir="results/caac_smoke",
            prior_sweep_csv=None,  # smoke uses global theta
        )


# ============================================================================
# Multi-agent coordination (reuse deterministic solver)
# ============================================================================
def _run_coordination(workload: Workload, compressor: Any, seed: int) -> WorkloadTrace:
    import asyncio
    orchestrator = PlannerWorkerCritic(
        cfg=AgentConfig(backend="determ"),
        compressor=compressor,
    )
    return asyncio.run(orchestrator.run(workload, seed=seed))


# ============================================================================
# Main sweep
# ============================================================================
def _derive_per_family_thetas(cfg: CAACConfig) -> dict[str, float]:
    """Derive per-family theta_q from the prior sweep.

    Per ADR-007: CAAC's q_min is family-adaptive. With
    ``prior_sweep_csv`` set, we call ``derive_theta(family=...,
    recall_column=cfg.recall_column)`` for each family and use the
    "mean" theta across compressors as the per-family value.

    Falls back to ``cfg.theta`` for any family where derivation fails
    (e.g., no cliff found in the sweep) or when ``prior_sweep_csv``
    is None.
    """
    out: dict[str, float] = {}
    if cfg.prior_sweep_csv is None:
        for fam in cfg.families:
            out[fam] = cfg.theta
        print(f"  Per-family theta (global fallback): {out}")
        return out
    for fam in cfg.families:
        try:
            res = derive_theta(
                cfg.prior_sweep_csv,
                family=fam,
                recall_column=cfg.recall_column,
            )
            theta_val = float(res.get("mean_theta", cfg.theta))
            if not (0.0 < theta_val < 1.0):
                print(f"  WARN: derived theta for family={fam} out of (0,1): {theta_val}; using global {cfg.theta}")
                theta_val = cfg.theta
            out[fam] = theta_val
        except Exception as e:
            print(f"  WARN: derive_theta failed for family={fam}: {e}; using global {cfg.theta}")
            out[fam] = cfg.theta
    print(f"  Per-family theta (from {cfg.prior_sweep_csv}, col={cfg.recall_column}): {out}")
    return out


def run_caac_experiment(cfg: CAACConfig) -> pd.DataFrame:
    print(f"Loading benchmark from {cfg.benchmark_path}...")
    all_workloads = load_benchmark(cfg.benchmark_path)
    family_set = set(cfg.families)
    workloads = [w for w in all_workloads if w.family.value in family_set]
    if cfg.n_workloads:
        # Take n_workloads per family
        filtered = []
        for fam in sorted(family_set):
            fam_ws = [w for w in workloads if w.family.value == fam]
            filtered.extend(fam_ws[: cfg.n_workloads])
        workloads = filtered
    print(f"  {len(workloads)} workloads loaded")

    per_family_theta = _derive_per_family_thetas(cfg)

    # Load precomputed cache if provided (used for fixed baselines only;
    # CAAC's adaptive binary search needs live compressor access)
    ext_cache: CompressionCache | None = None
    if cfg.cache_path:
        ext_cache = CompressionCache.load(cfg.cache_path)

    rows: list[dict[str, Any]] = []
    done = 0
    t_start = time.time()

    # Pool: one inner compressor instance per name, reused across all target
    # ratios. Every supported compressor accepts ``target_ratio`` per-call in
    # its ``.compress()`` method, so we never need a separate instance per
    # ratio. Without pooling, the original loop loaded a fresh LLMLingua-2
    # model (~2 GiB GPU) for each of 8 target ratios per inner — across two
    # inners plus CAAC wrappers that's ~24 model copies = OOM on a 32 GiB
    # GPU. The CAAC wrapper itself now also caches a single shared instance
    # (see CAACCompressor._get_compressor_at_ratio).
    inner_pool: dict[str, Any] = {}

    for inner_name in cfg.inner_compressors:
        if inner_name not in inner_pool:
            inner_pool[inner_name] = make_compressor(inner_name)
        live_inner = inner_pool[inner_name]

        for target_ratio in cfg.target_ratios:
            # --- Fixed baseline ---
            print(f"\n  Fixed {inner_name} @ {target_ratio}x...")
            if target_ratio == 1.0:
                fixed_comp = make_compressor("identity")
                fixed_target = None  # identity ignores ratio
            elif ext_cache is not None:
                fixed_comp = make_cached_compressor(inner_name, ext_cache, target_ratio=target_ratio)
                fixed_target = None  # cached compressor encodes ratio in its key
            else:
                fixed_comp = live_inner  # pooled — pass target_ratio per call
                fixed_target = target_ratio

            for w in workloads:
                # Compress fragments and measure achieved ratio
                compressed_parts = []
                total_src, total_comp = 0, 0
                for frag in w.fragments:
                    fh = frag.model_copy(update={"task_hint": w.initial_prompt})
                    if fixed_target is None:
                        slot = fixed_comp.compress(fh)
                    else:
                        slot = fixed_comp.compress(fh, target_ratio=fixed_target)
                    text = fixed_comp.decompress(slot) or frag.text
                    compressed_parts.append(text)
                    total_src += len(frag.text)
                    total_comp += len(text)
                achieved_ratio = total_src / max(total_comp, 1)

                # Token recall
                avg_q = np.mean([
                    _token_recall(f.text, c)
                    for f, c in zip(w.fragments, compressed_parts)
                ])

                for seed in cfg.seeds:
                    trace = _run_coordination(w, fixed_comp, seed)
                    coord = score_coordination(w, trace)
                    rows.append({
                        "method": f"fixed-{inner_name}",
                        "inner_compressor": inner_name,
                        "target_ratio": target_ratio,
                        "achieved_ratio": achieved_ratio,
                        "family": w.family.value,
                        "workload_id": w.workload_id,
                        "seed": seed,
                        "coord_success": coord["coord_success"],
                        "token_recall": float(avg_q),
                        "is_caac": False,
                    })
                    done += 1

            # --- CAAC ---
            if target_ratio <= 1.0:
                continue  # No point wrapping identity
            print(f"  CAAC({inner_name}) @ target {target_ratio}x...")
            # One CAAC instance per family — each uses its own derived
            # theta_q AND its own family-specific CTR safety check (per
            # ADR-007). The inner compressor is the pooled live_inner,
            # so memory cost is constant per family.
            caacs_by_family: dict[str, CAACCompressor] = {}
            for fam in cfg.families:
                caacs_by_family[fam] = CAACCompressor(
                    inner=live_inner,
                    target_ratio=target_ratio,
                    n_compression_passes=cfg.n_compression_passes,
                    theta=per_family_theta[fam],
                    family=fam,
                )

            for w in workloads:
                fam = w.family.value
                caac = caacs_by_family.get(fam)
                if caac is None:
                    continue  # workload's family not in cfg.families
                compressed_parts = []
                total_src, total_comp = 0, 0
                for frag in w.fragments:
                    fh = frag.model_copy(update={"task_hint": w.initial_prompt})
                    slot = caac.compress(fh)
                    text = caac.decompress(slot) or frag.text
                    compressed_parts.append(text)
                    total_src += len(frag.text)
                    total_comp += len(text)
                achieved_ratio = total_src / max(total_comp, 1)

                avg_q = np.mean([
                    _token_recall(f.text, c)
                    for f, c in zip(w.fragments, compressed_parts)
                ])

                for seed in cfg.seeds:
                    trace = _run_coordination(w, caac, seed)
                    coord = score_coordination(w, trace)
                    rows.append({
                        "method": f"caac-{inner_name}",
                        "inner_compressor": inner_name,
                        "target_ratio": target_ratio,
                        "achieved_ratio": achieved_ratio,
                        "family": fam,
                        "workload_id": w.workload_id,
                        "seed": seed,
                        "coord_success": coord["coord_success"],
                        "token_recall": float(avg_q),
                        "is_caac": True,
                        "theta_q": per_family_theta[fam],
                    })
                    done += 1

            if done % 50 == 0:
                elapsed = time.time() - t_start
                print(f"    [{done} cells] {elapsed:.0f}s elapsed")
                sys.stdout.flush()

    return pd.DataFrame(rows)


# ============================================================================
# Verdict / summary
# ============================================================================
def _compute_pair_metrics(fixed: pd.DataFrame, caac: pd.DataFrame, eps: float = 1e-6) -> dict | None:
    """Compute the per-cell (fixed, caac) comparison block.

    Returns None when either input is empty.
    """
    if fixed.empty or caac.empty:
        return None
    fixed_cs = float(fixed["coord_success"].mean())
    caac_cs = float(caac["coord_success"].mean())
    fixed_ar = float(fixed["achieved_ratio"].mean())
    caac_ar = float(caac["achieved_ratio"].mean())
    no_worse_coord = caac_cs >= fixed_cs - eps
    no_worse_ratio = caac_ar >= fixed_ar - eps
    better_coord = caac_cs > fixed_cs + eps
    better_ratio = caac_ar > fixed_ar + eps
    strict = no_worse_coord and no_worse_ratio and (better_coord or better_ratio)
    weak = caac_cs >= fixed_cs - eps
    return {
        "fixed_coord": fixed_cs,
        "caac_coord": caac_cs,
        "fixed_achieved_ratio": fixed_ar,
        "caac_achieved_ratio": caac_ar,
        "coord_improvement_pp": (caac_cs - fixed_cs) * 100,
        "compression_sacrifice": fixed_ar - caac_ar,
        "caac_dominates_strict": strict,
        "caac_dominates_weak": weak,
        "caac_dominates": strict,
    }


def compute_caac_summary(df: pd.DataFrame) -> dict:
    """Compute Pareto dominance summary aggregated across families.

    Two criteria reported per (inner_compressor, target_ratio):
      * caac_dominates_strict: strict Pareto — CAAC is no worse on both
        (coord, compression) AND strictly better on at least one.
      * caac_dominates_weak: legacy — CAAC coord >= fixed coord
        (counts ties; ignores compression sacrifice).

    The strict rate is the load-bearing one for ADR-007's
    operating-point framing — expected to be ~0/N. The weak rate
    survives only for back-compat readers.
    """
    summary: dict[str, Any] = {}
    for inner in df["inner_compressor"].unique():
        sub = df[df["inner_compressor"] == inner]
        per_ratio = {}
        for ratio in sorted(sub["target_ratio"].unique()):
            if ratio <= 1.0:
                continue
            fixed = sub[(sub["target_ratio"] == ratio) & (~sub["is_caac"])]
            caac = sub[(sub["target_ratio"] == ratio) & (sub["is_caac"])]
            pair = _compute_pair_metrics(fixed, caac)
            if pair is not None:
                per_ratio[str(ratio)] = pair
        n_strict = sum(1 for v in per_ratio.values() if v["caac_dominates_strict"])
        n_weak = sum(1 for v in per_ratio.values() if v["caac_dominates_weak"])
        summary[inner] = {
            "per_ratio": per_ratio,
            "n_dominated_strict": n_strict,
            "n_dominated_weak": n_weak,
            "n_total": len(per_ratio),
            "dominance_rate_strict": n_strict / max(len(per_ratio), 1),
            "dominance_rate_weak": n_weak / max(len(per_ratio), 1),
            "n_dominated": n_strict,
            "dominance_rate": n_strict / max(len(per_ratio), 1),
        }
    return summary


def compute_caac_summary_per_family(df: pd.DataFrame) -> dict:
    """Per-family Pareto-dominance breakdown.

    Surfaces the operating-point texture that the across-family summary
    blurs. For ADR-007 / Q5 the per-family report is the one that goes
    into Ch8: family-c (CAAC's strongest family per the ablation in
    insights §54) vs family-a (where CAAC pancakes to min_ratio).
    """
    summary: dict[str, Any] = {}
    for inner in df["inner_compressor"].unique():
        sub_i = df[df["inner_compressor"] == inner]
        per_family: dict[str, Any] = {}
        for fam in sorted(sub_i["family"].unique()):
            sub = sub_i[sub_i["family"] == fam]
            per_ratio = {}
            for ratio in sorted(sub["target_ratio"].unique()):
                if ratio <= 1.0:
                    continue
                fixed = sub[(sub["target_ratio"] == ratio) & (~sub["is_caac"])]
                caac = sub[(sub["target_ratio"] == ratio) & (sub["is_caac"])]
                pair = _compute_pair_metrics(fixed, caac)
                if pair is not None:
                    per_ratio[str(ratio)] = pair
            n_strict = sum(1 for v in per_ratio.values() if v["caac_dominates_strict"])
            n_weak = sum(1 for v in per_ratio.values() if v["caac_dominates_weak"])
            theta_q = None
            caac_theta = sub[sub["is_caac"]].get("theta_q")
            if caac_theta is not None and not caac_theta.empty:
                theta_q = float(caac_theta.iloc[0])
            per_family[fam] = {
                "theta_q": theta_q,
                "per_ratio": per_ratio,
                "n_dominated_strict": n_strict,
                "n_dominated_weak": n_weak,
                "n_total": len(per_ratio),
                "dominance_rate_strict": n_strict / max(len(per_ratio), 1),
                "dominance_rate_weak": n_weak / max(len(per_ratio), 1),
            }
        summary[inner] = per_family
    return summary


def compute_caac_verdict(
    summary: dict,
    cliff_ratio: float = 4.0,
    operating_point_threshold_pp: float = 15.0,
) -> dict:
    """Verdict for the CAAC hypothesis under two criteria.

    Two verdicts are reported side-by-side:

    1. **Strict-Pareto** (the literal claim "CAAC dominates fixed"):
       PASS iff any inner compressor has >= 50% of cliff-region ratios
       (target >= cliff_ratio) where CAAC is no-worse on BOTH coord AND
       achieved compression ratio AND strictly better on at least one.
       This is almost always NOT SUPPORTED because CAAC by construction
       trades compression for coordination: at high target ratios it backs
       off, so its achieved ratio is below the fixed baseline.

    2. **Operating-point** (the honest empirical claim "CAAC is a useful
       safety-bounded compressor"): PASS iff any inner compressor has, at
       the HIGHEST target ratio tested, a coord_improvement >=
       operating_point_threshold_pp. This captures the real value prop:
       *at the cliff, where fixed compression collapses to 0%, CAAC's
       graceful backoff retains coordination.*

    The overall ``verdict`` is the strict-Pareto verdict (preserves the
    pre-registered criterion). The operating-point verdict is reported
    alongside as ``operating_point_verdict``.
    """
    per_compressor: dict[str, Any] = {}
    overall_strict_pass = False
    overall_op_pass = False

    for inner, data in summary.items():
        ratios_sorted = sorted(
            data["per_ratio"].items(), key=lambda kv: float(kv[0])
        )
        cliff_cells = [v for r, v in ratios_sorted if float(r) >= cliff_ratio]
        n_cliff = len(cliff_cells)
        n_strict_cliff = sum(1 for v in cliff_cells if v["caac_dominates_strict"])
        rate_strict_cliff = n_strict_cliff / max(n_cliff, 1)

        best = max(
            data["per_ratio"].items(),
            key=lambda kv: kv[1]["coord_improvement_pp"],
            default=(None, None),
        )

        # Operating point: the highest target ratio tested. At this ratio,
        # fixed compression typically collapses (coord -> 0); the question
        # is whether CAAC's backoff keeps coord nontrivial.
        max_ratio_cell = ratios_sorted[-1][1] if ratios_sorted else None
        max_ratio_imp_pp = (max_ratio_cell["coord_improvement_pp"]
                            if max_ratio_cell is not None else 0.0)
        op_passes = (max_ratio_cell is not None
                     and max_ratio_imp_pp >= operating_point_threshold_pp)

        per_compressor[inner] = {
            "n_cliff_ratios": n_cliff,
            "n_strict_cliff": n_strict_cliff,
            "strict_dominance_rate_cliff": rate_strict_cliff,
            "strict_dominance_rate_all": data["dominance_rate_strict"],
            "weak_dominance_rate_all": data["dominance_rate_weak"],
            "best_improvement_ratio": float(best[0]) if best[0] is not None else None,
            "best_improvement_pp": (best[1]["coord_improvement_pp"]
                                   if best[1] is not None else None),
            "max_target_ratio": (float(ratios_sorted[-1][0])
                                 if ratios_sorted else None),
            "max_ratio_coord_improvement_pp": max_ratio_imp_pp,
            "passes_strict_pareto": rate_strict_cliff >= 0.5,
            "passes_operating_point": op_passes,
            "passes": rate_strict_cliff >= 0.5,  # back-compat alias = strict
        }
        if per_compressor[inner]["passes_strict_pareto"]:
            overall_strict_pass = True
        if op_passes:
            overall_op_pass = True

    return {
        "criterion_strict_pareto": (
            f"CAAC achieves strict Pareto improvement (no worse on coord AND "
            f"on achieved ratio AND strictly better on at least one) at >= 50% "
            f"of cliff-region ratios (target_ratio >= {cliff_ratio}) for at "
            f"least one inner compressor."
        ),
        "criterion_operating_point": (
            f"CAAC retains coord_improvement >= {operating_point_threshold_pp}pp "
            f"at the highest target ratio (the operating-point where fixed "
            f"compression collapses), for at least one inner compressor."
        ),
        "cliff_ratio": cliff_ratio,
        "operating_point_threshold_pp": operating_point_threshold_pp,
        "per_compressor": per_compressor,
        "verdict": "SUPPORTED" if overall_strict_pass else "NOT SUPPORTED",
        "operating_point_verdict": "SUPPORTED" if overall_op_pass else "NOT SUPPORTED",
        "narrative": (
            "CAAC is a *safety-bounded* compressor: when given a target ratio "
            "the inner compressor cannot survive, CAAC backs off rather than "
            "collapsing. Under strict Pareto (no worse on either axis) it does "
            "not dominate fixed-ratio compression, by construction — CAAC "
            "trades compression for coordination. Its empirical value is "
            "graceful degradation at high target ratios: where fixed coord "
            "collapses to 0%, CAAC retains a meaningful fraction. Avoid "
            "describing CAAC as 'dominant' or 'Pareto-optimal' in the writeup; "
            "describe it as 'knows when to stop'."
        ),
    }


# ============================================================================
# Entry point
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="CAAC vs fixed-ratio baselines")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--out", type=str, default=None)
    parser.add_argument("--cache", type=str, default=None, help="Path to precomputed compression cache JSON (fixed baselines only)")
    parser.add_argument("--theta", type=float, default=None, help="CAAC theta (min surviving info fraction)")
    parser.add_argument("--n-passes", type=int, default=None, help="Number of compression passes (N)")
    args = parser.parse_args()

    cfg = CAACConfig.smoke() if args.smoke else CAACConfig()
    if args.out:
        cfg.out_dir = args.out
    if args.cache:
        cfg.cache_path = args.cache
    if args.theta is not None:
        cfg.theta = args.theta
    if args.n_passes is not None:
        cfg.n_compression_passes = args.n_passes

    print("=" * 60)
    print("CAAC: Cliff-Aware Adaptive Compression")
    print("=" * 60)
    print(f"Inner compressors: {cfg.inner_compressors}")
    print(f"Target ratios: {cfg.target_ratios}")
    print(f"Families: {cfg.families}")
    print(f"N_rounds: {cfg.n_compression_passes}, theta: {cfg.theta}")
    print(f"Output: {cfg.out_dir}")
    print()

    df = run_caac_experiment(cfg)

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "results.csv", index=False)
    print(f"\nSaved {len(df)} rows to {out_dir / 'results.csv'}")

    summary = compute_caac_summary(df)

    print("\n" + "=" * 60)
    print("CAAC SUMMARY")
    print("=" * 60)
    for inner, data in summary.items():
        print(f"\n  Inner: {inner}")
        print(f"  Strict-Pareto dominance: {data['n_dominated_strict']}/{data['n_total']} ratios "
              f"(rate={data['dominance_rate_strict']:.0%})")
        print(f"  Weak (coord>=) dominance: {data['n_dominated_weak']}/{data['n_total']} ratios "
              f"(rate={data['dominance_rate_weak']:.0%})")
        for ratio, v in data["per_ratio"].items():
            marker = ">>>" if v["caac_dominates_strict"] else ("~~~" if v["caac_dominates_weak"] else "   ")
            print(
                f"    {marker} {ratio}x: fixed={v['fixed_coord']:.0%} caac={v['caac_coord']:.0%} "
                f"(+{v['coord_improvement_pp']:.0f}pp) "
                f"achieved={v['caac_achieved_ratio']:.1f}x vs {v['fixed_achieved_ratio']:.1f}x"
            )

    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nSummary saved to {out_dir / 'summary.json'}")

    per_family_summary = compute_caac_summary_per_family(df)
    with open(out_dir / "summary_per_family.json", "w") as f:
        json.dump(per_family_summary, f, indent=2, default=str)
    print(f"Per-family summary saved to {out_dir / 'summary_per_family.json'}")

    verdict = compute_caac_verdict(summary)
    with open(out_dir / "verdicts.json", "w") as f:
        json.dump(verdict, f, indent=2, default=str)
    print(f"\nStrict-Pareto verdict:    {verdict['verdict']}  (saved to {out_dir / 'verdicts.json'})")
    print(f"Operating-point verdict:  {verdict['operating_point_verdict']}")
    for inner, pc in verdict["per_compressor"].items():
        strict_marker = "PASS" if pc["passes_strict_pareto"] else "FAIL"
        op_marker = "PASS" if pc["passes_operating_point"] else "FAIL"
        print(f"  {inner}:")
        print(f"    [{strict_marker}] strict cliff dominance "
              f"{pc['n_strict_cliff']}/{pc['n_cliff_ratios']} "
              f"({pc['strict_dominance_rate_cliff']:.0%})")
        print(f"    [{op_marker}] operating-point: +{pc['max_ratio_coord_improvement_pp']:.1f}pp coord "
              f"at target={pc['max_target_ratio']}x")


if __name__ == "__main__":
    main()
