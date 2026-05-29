#!/usr/bin/env python3
"""HotpotQA cliff sweep — second external benchmark validation.

Tests whether the coordination cliff transfers to HotpotQA multi-hop QA data.
Mirrors run_h6.py but uses HotpotQA instead of MultiHopRAG. Also computes
Corollary 2 theta estimate for information density comparison.

Run:
    python -m m6.experiments.run_hotpotqa
    python -m m6.experiments.run_hotpotqa --smoke
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import numpy as np
import pandas as pd

from m6.benchmark.generator import load as load_benchmark
from m6.benchmark.schemas import Workload
from m6.compressors import make_compressor
from m6.compressors.cache import CompressionCache
from m6.experiments.run_h1_h2 import f1_score as token_f1
from m6.experiments.run_h1_h2 import _normalize  # noqa: PLC2701
from m6.experiments.run_h5 import fit_piecewise

# ============================================================================
# Config
# ============================================================================
OLLAMA_URL = "http://127.0.0.1:11434"


@dataclass
class HotpotQAConfig:
    benchmark_path: str = "data/processed/hotpotqa-50"
    compressor: str = "lingua2"
    ratios: list[float] | None = None
    seeds: list[int] | None = None
    n_workloads: int = 50
    planner_model: str = "llama3.1:8b"
    synth_results_path: str | None = None
    out_dir: str = "results/hotpotqa_sweep"
    cache_path: str | None = None

    def __post_init__(self):
        if self.ratios is None:
            self.ratios = [1.0, 2.0, 4.0, 8.0, 16.0]
        if self.seeds is None:
            self.seeds = [0, 1, 2]

    @classmethod
    def smoke(cls) -> HotpotQAConfig:
        return cls(
            ratios=[1.0, 4.0],
            seeds=[0],
            n_workloads=3,
            out_dir="results/hotpotqa_smoke",
        )


# ============================================================================
# Ollama planner (reuse H6 pattern)
# ============================================================================
def ollama_planner_solve(
    model: str, workload: Workload, compressed_texts: dict[str, str], seed: int = 0
) -> dict:
    """Ask the Ollama planner to solve a HotpotQA workload."""
    fragments_text = "\n\n".join(
        f"[{fid}] {text}" for fid, text in compressed_texts.items()
    )
    prompt = f"""You are a planner in a multi-agent system. Your task:

{workload.initial_prompt}

Available information:
{fragments_text}

Instructions:
1. Read all fragments carefully.
2. Provide your final answer on a SINGLE line starting with "ANSWER: ".
Keep the answer brief (a few words).

Your response:"""

    try:
        resp = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 256, "temperature": 0.1, "seed": seed},
            },
            timeout=120.0,
        )
        resp.raise_for_status()
        response = resp.json().get("response", "")
    except Exception as e:
        print(f"  [warn] planner exception: {e}", file=sys.stderr)
        response = ""

    # Extract answer
    answer = ""
    for line in response.split("\n"):
        if line.strip().upper().startswith("ANSWER:"):
            answer = line.split(":", 1)[1].strip()
            break
    if not answer:
        answer = response[:200]

    f1 = token_f1(answer, workload.expected_answer)
    em = float(_normalize(answer) == _normalize(workload.expected_answer))
    coord_success = float(f1 >= 0.5)

    return {
        "answer": answer,
        "coord_success": coord_success,
        "f1": f1,
        "exact_match": em,
        "raw_response": response[:500],
    }


# ============================================================================
# Main sweep
# ============================================================================
def _ensure_benchmark(cfg: HotpotQAConfig) -> None:
    """Generate the HotpotQA benchmark on disk if it doesn't exist."""
    path = Path(cfg.benchmark_path)
    if (path / "family-a.jsonl").exists():
        return
    print(f"  Generating HotpotQA benchmark at {cfg.benchmark_path}...")
    from m6.corpus.hotpotqa import load_hotpotqa, persist

    workloads = load_hotpotqa(n=50, seed=0)
    persist(workloads, cfg.benchmark_path)
    print(f"  Saved {len(workloads)} workloads")


def run_hotpotqa(cfg: HotpotQAConfig) -> pd.DataFrame:
    _ensure_benchmark(cfg)

    # Validate Ollama planner
    try:
        resp = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": cfg.planner_model, "prompt": "test", "stream": False,
                  "options": {"num_predict": 1}},
            timeout=30.0,
        )
        resp.raise_for_status()
        print(f"  Planner {cfg.planner_model}: OK")
    except Exception as e:
        raise RuntimeError(
            f"Ollama model {cfg.planner_model!r} not available. "
            f"Pull it with: ollama pull {cfg.planner_model}"
        ) from e

    print(f"Loading benchmark from {cfg.benchmark_path}...")
    workloads = load_benchmark(cfg.benchmark_path)
    if cfg.n_workloads and len(workloads) > cfg.n_workloads:
        workloads = workloads[: cfg.n_workloads]
    print(f"  {len(workloads)} workloads loaded")

    # Load precomputed cache if provided
    ext_cache: CompressionCache | None = None
    if cfg.cache_path:
        ext_cache = CompressionCache.load(cfg.cache_path)

    # Pre-compress all fragments
    comp_cache: dict[float, Any] = {}
    compressed_cache: dict[tuple[float, str], str] = {}

    print(f"  Pre-compressing fragments for {len(cfg.ratios)} ratios...")
    for ratio in cfg.ratios:
        if ratio not in comp_cache:
            comp_cache[ratio] = make_compressor(cfg.compressor, target_ratio=ratio)
        comp = comp_cache[ratio]
        for w in workloads:
            for frag in w.fragments:
                cache_key = (ratio, frag.fragment_id)
                if cache_key not in compressed_cache:
                    if ext_cache is not None:
                        cached = ext_cache.lookup(cfg.compressor, ratio, frag.fragment_id, None)
                        if cached is not None:
                            compressed_cache[cache_key] = cached
                            continue
                    slot = comp.compress(frag)
                    compressed_cache[cache_key] = comp.decompress(slot) or frag.text
    print(f"  Cached {len(compressed_cache)} compressed fragments")

    rows: list[dict[str, Any]] = []
    total = len(cfg.ratios) * len(workloads) * len(cfg.seeds)
    done = 0
    t_start = time.time()

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for ratio in cfg.ratios:
        for w in workloads:
            compressed_texts = {
                frag.fragment_id: compressed_cache[(ratio, frag.fragment_id)]
                for frag in w.fragments
            }
            for seed in cfg.seeds:
                result = ollama_planner_solve(
                    cfg.planner_model, w, compressed_texts, seed=seed
                )
                rows.append({
                    "compressor": cfg.compressor,
                    "ratio": ratio,
                    "workload_id": w.workload_id,
                    "seed": seed,
                    "coord_success": result["coord_success"],
                    "f1": result["f1"],
                    "exact_match": result["exact_match"],
                    "answer": result["answer"][:200],
                    "expected_answer": w.expected_answer,
                    "n_evidence": len(w.fragments),
                })

                done += 1
                if done % 50 == 0 or done == total:
                    elapsed = time.time() - t_start
                    eta = (elapsed / done) * (total - done)
                    print(
                        f"    [{done}/{total}] {elapsed:.0f}s elapsed, ETA {eta:.0f}s"
                    )
                    sys.stdout.flush()
                if done % 200 == 0:
                    pd.DataFrame(rows).to_csv(
                        out_dir / "results.partial.csv", index=False
                    )

    return pd.DataFrame(rows)


# ============================================================================
# Verdict
# ============================================================================
def compute_verdict(df: pd.DataFrame, synth_results_path: str | None) -> dict:
    """Compute cliff position and Corollary 2 theta estimate."""
    agg = df.groupby("ratio")["coord_success"].mean().reset_index()
    curve_fit = fit_piecewise(agg["ratio"].to_numpy(), agg["coord_success"].to_numpy())
    curve = {str(r): float(s) for r, s in zip(agg["ratio"], agg["coord_success"])}

    baseline = float(df[df["ratio"] == 1.0]["coord_success"].mean()) if not df[df["ratio"] == 1.0].empty else float("nan")

    verdict: dict[str, Any] = {
        "dataset": "hotpotqa",
        "tau": curve_fit["tau"],
        "drop_rel": curve_fit["drop_rel"],
        "curve": curve,
        "baseline_coord": baseline,
        "mean_f1": float(df["f1"].mean()),
        "mean_em": float(df["exact_match"].mean()),
        "n_workloads": df["workload_id"].nunique(),
    }

    # Estimate theta (Corollary 2)
    ratios = agg["ratio"].to_numpy()
    success = agg["coord_success"].to_numpy()
    if len(ratios) >= 2 and baseline > 0:
        norm_success = np.clip(success / baseline, 0, 1)
        span = float(ratios[-1] - ratios[0])
        auc = float(getattr(np, "trapezoid", np.trapz)(norm_success, ratios) / span) if span > 0 else 0.0
        theta = 1.0 - auc
    else:
        auc = float("nan")
        theta = float("nan")

    verdict["normalized_auc"] = auc
    verdict["theta_estimate"] = theta

    # Compare with C1 if synth results available
    if synth_results_path:
        synth_csv = Path(synth_results_path) / "results.csv"
        if not synth_csv.exists():
            synth_csv = Path(synth_results_path) / "sweep_results.csv"
        if synth_csv.exists():
            synth_df = pd.read_csv(synth_csv)
            if "planner_model" in synth_df.columns:
                synth_df = synth_df[synth_df["planner_model"] == "8B"]
            elif "compressor" in synth_df.columns:
                synth_df = synth_df[synth_df["compressor"] == "lingua2"]

            # Compute C1 family-a theta
            fam_a = synth_df[synth_df["family"] == "a"] if "family" in synth_df.columns else synth_df
            if not fam_a.empty:
                fa_agg = fam_a.groupby("ratio")["coord_success"].mean().reset_index().sort_values("ratio")
                fa_ratios = fa_agg["ratio"].to_numpy()
                fa_success = fa_agg["coord_success"].to_numpy()
                fa_baseline = float(fa_success[0]) if len(fa_success) > 0 else 0.0
                if len(fa_ratios) >= 2 and fa_baseline > 0:
                    fa_norm = np.clip(fa_success / fa_baseline, 0, 1)
                    fa_span = float(fa_ratios[-1] - fa_ratios[0])
                    fa_auc = float(getattr(np, "trapezoid", np.trapz)(fa_norm, fa_ratios) / fa_span) if fa_span > 0 else 0.0
                    c1a_theta = 1.0 - fa_auc
                    verdict["c1_family_a_theta"] = c1a_theta
                    verdict["theta_gap"] = abs(c1a_theta - theta)
                    verdict["corollary2_supported"] = verdict["theta_gap"] >= 0.1

                # Synth tau for comparison
                synth_fit = fit_piecewise(fa_ratios, fa_success)
                verdict["synth_tau"] = synth_fit["tau"]
                verdict["tau_diff_pct"] = (
                    abs(curve_fit["tau"] - synth_fit["tau"]) / abs(synth_fit["tau"]) * 100
                    if synth_fit["tau"] != 0 and not np.isnan(synth_fit["tau"])
                    else float("nan")
                )

    return verdict


# ============================================================================
# Entry point
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="HotpotQA cliff sweep")
    parser.add_argument("--smoke", action="store_true", help="Quick smoke test")
    parser.add_argument("--out", type=str, default=None, help="Output directory")
    parser.add_argument("--synth-results", type=str, default=None,
                        help="Path to H1/H2 or H5 results dir for comparison")
    parser.add_argument("--cache", type=str, default=None,
                        help="Path to precomputed compression cache JSON")
    args = parser.parse_args()

    cfg = HotpotQAConfig.smoke() if args.smoke else HotpotQAConfig()
    if args.out:
        cfg.out_dir = args.out
    if args.synth_results:
        cfg.synth_results_path = args.synth_results
    if args.cache:
        cfg.cache_path = args.cache

    print("=" * 60)
    print("HotpotQA Cliff Sweep")
    print("=" * 60)
    print(f"Compressor: {cfg.compressor}")
    print(f"Planner: {cfg.planner_model}")
    print(f"Ratios: {cfg.ratios}")
    print(f"Seeds: {cfg.seeds}")
    print(f"Workloads: {cfg.n_workloads}")
    print(f"Output: {cfg.out_dir}")
    print()

    df = run_hotpotqa(cfg)

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "results.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nSaved {len(df)} rows to {csv_path}")

    # Summary
    print("\nCoord success by ratio:")
    for ratio, cs in df.groupby("ratio")["coord_success"].mean().items():
        print(f"  {ratio:5.1f}x: {cs:.2%}")

    print(f"\nMean F1: {df['f1'].mean():.3f}")
    print(f"Mean EM: {df['exact_match'].mean():.3f}")

    # Verdict
    verdict = compute_verdict(df, cfg.synth_results_path)
    print(f"\nHotpotQA tau*: {verdict['tau']:.1f}" if not np.isnan(verdict.get("tau", float("nan"))) else "\nHotpotQA tau*: N/A")
    print(f"Drop: {verdict['drop_rel']:.1%}")
    print(f"Theta estimate: {verdict['theta_estimate']:.3f}")

    if verdict.get("c1_family_a_theta") is not None:
        print(f"C1 family-a theta: {verdict['c1_family_a_theta']:.3f}")
        print(f"Theta gap: {verdict['theta_gap']:.3f}")
        print(f"Corollary 2 supported: {verdict.get('corollary2_supported', 'N/A')}")

    if verdict.get("synth_tau") is not None:
        print(f"Synth tau: {verdict['synth_tau']:.1f}")
        print(f"Tau diff: {verdict.get('tau_diff_pct', 0):.1f}%")

    with open(out_dir / "verdicts.json", "w") as f:
        json.dump(verdict, f, indent=2, default=str)
    print(f"\nVerdicts saved to {out_dir / 'verdicts.json'}")


if __name__ == "__main__":
    main()
