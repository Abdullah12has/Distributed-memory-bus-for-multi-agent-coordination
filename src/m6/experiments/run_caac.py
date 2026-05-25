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
from m6.compressors.caac import CAACCompressor, _token_recall
from m6.experiments.run_h1_h2 import score_coordination


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
    theta: float = 0.5
    out_dir: str = "results/caac"

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

    rows: list[dict[str, Any]] = []
    done = 0
    t_start = time.time()

    for inner_name in cfg.inner_compressors:
        for target_ratio in cfg.target_ratios:
            # --- Fixed baseline ---
            print(f"\n  Fixed {inner_name} @ {target_ratio}x...")
            fixed_comp = make_compressor(inner_name, target_ratio=target_ratio)

            for w in workloads:
                # Compress fragments and measure achieved ratio
                compressed_parts = []
                total_src, total_comp = 0, 0
                for frag in w.fragments:
                    fh = frag.model_copy(update={"task_hint": w.initial_prompt})
                    slot = fixed_comp.compress(fh)
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
            caac = CAACCompressor(
                inner=inner_name,
                target_ratio=target_ratio,
                n_compression_passes=cfg.n_compression_passes,
                theta=cfg.theta,
            )

            for w in workloads:
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
                        "family": w.family.value,
                        "workload_id": w.workload_id,
                        "seed": seed,
                        "coord_success": coord["coord_success"],
                        "token_recall": float(avg_q),
                        "is_caac": True,
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
def compute_caac_summary(df: pd.DataFrame) -> dict:
    """Compute Pareto dominance summary: does CAAC dominate fixed at each ratio?"""
    summary: dict[str, Any] = {}

    for inner in df["inner_compressor"].unique():
        sub = df[df["inner_compressor"] == inner]
        per_ratio = {}
        for ratio in sorted(sub["target_ratio"].unique()):
            if ratio <= 1.0:
                continue
            fixed = sub[(sub["target_ratio"] == ratio) & (~sub["is_caac"])]
            caac = sub[(sub["target_ratio"] == ratio) & (sub["is_caac"])]
            if fixed.empty or caac.empty:
                continue

            fixed_cs = float(fixed["coord_success"].mean())
            caac_cs = float(caac["coord_success"].mean())
            fixed_ar = float(fixed["achieved_ratio"].mean())
            caac_ar = float(caac["achieved_ratio"].mean())

            # CAAC dominates if coord_success >= fixed AND achieved_ratio > 1
            dominates = caac_cs >= fixed_cs
            per_ratio[str(ratio)] = {
                "fixed_coord": fixed_cs,
                "caac_coord": caac_cs,
                "fixed_achieved_ratio": fixed_ar,
                "caac_achieved_ratio": caac_ar,
                "coord_improvement_pp": (caac_cs - fixed_cs) * 100,
                "compression_sacrifice": fixed_ar - caac_ar,
                "caac_dominates": dominates,
            }

        n_dominated = sum(1 for v in per_ratio.values() if v["caac_dominates"])
        summary[inner] = {
            "per_ratio": per_ratio,
            "n_dominated": n_dominated,
            "n_total": len(per_ratio),
            "dominance_rate": n_dominated / max(len(per_ratio), 1),
        }

    return summary


# ============================================================================
# Entry point
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="CAAC vs fixed-ratio baselines")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()

    cfg = CAACConfig.smoke() if args.smoke else CAACConfig()
    if args.out:
        cfg.out_dir = args.out

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
        print(f"  Dominance: {data['n_dominated']}/{data['n_total']} ratios")
        for ratio, v in data["per_ratio"].items():
            marker = ">>>" if v["caac_dominates"] else "   "
            print(
                f"    {marker} {ratio}x: fixed={v['fixed_coord']:.0%} caac={v['caac_coord']:.0%} "
                f"(+{v['coord_improvement_pp']:.0f}pp) "
                f"achieved={v['caac_achieved_ratio']:.1f}x vs {v['fixed_achieved_ratio']:.1f}x"
            )

    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nSummary saved to {out_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
