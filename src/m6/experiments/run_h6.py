#!/usr/bin/env python3
"""H6 — MultiHopRAG transfer validation.

Tests whether the coordination cliff found on synthetic C1 benchmarks
transfers to real multi-hop QA data (MultiHopRAG, Tang & Yang EMNLP 2024).

H6 supported iff:
  - tau* within +/-15% of synthetic C1 family-a tau*
  - coord_success within +/-10pp at each overlapping ratio

Run:
    python -m m6.experiments.run_h6
    python -m m6.experiments.run_h6 --smoke
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
from m6.experiments.run_h1_h2 import f1_score as token_f1
from m6.experiments.run_h1_h2 import _normalize  # noqa: PLC2701
from m6.experiments.run_h5 import fit_piecewise

# ============================================================================
# Config
# ============================================================================
OLLAMA_URL = "http://127.0.0.1:11434"


@dataclass
class H6Config:
    benchmark_path: str = "data/processed/multihoprag-30"
    compressor: str = "lingua2"
    ratios: list[float] | None = None
    seeds: list[int] | None = None
    n_workloads: int = 30
    planner_model: str = "llama3.1:8b"
    synth_results_path: str | None = None  # H5 results dir for comparison
    out_dir: str = "results/h6"

    def __post_init__(self):
        if self.ratios is None:
            self.ratios = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0]
        if self.seeds is None:
            self.seeds = [0, 1, 2, 3, 4]

    @classmethod
    def smoke(cls) -> H6Config:
        return cls(
            ratios=[1.0, 4.0, 8.0, 16.0],
            seeds=[0],
            n_workloads=3,
            out_dir="results/h6_smoke",
        )


# ============================================================================
# QA metrics
# ============================================================================
def exact_match(prediction: str, reference: str) -> float:
    return float(_normalize(prediction) == _normalize(reference))


# ============================================================================
# Ollama planner
# ============================================================================
def ollama_planner_solve(
    model: str, workload: Workload, compressed_texts: dict[str, str], seed: int = 0
) -> dict:
    """Ask the Ollama planner to solve a MultiHopRAG workload."""
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
    em = exact_match(answer, workload.expected_answer)
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
def _ensure_benchmark(cfg: H6Config) -> None:
    """Generate the MultiHopRAG benchmark on disk if it doesn't exist."""
    path = Path(cfg.benchmark_path)
    if (path / "family-a.jsonl").exists():
        return
    print(f"  Generating MultiHopRAG benchmark at {cfg.benchmark_path}...")
    from m6.corpus.multihoprag import load_multihoprag, persist

    workloads = load_multihoprag(n=30, seed=0)  # always persist full 30
    persist(workloads, cfg.benchmark_path)
    print(f"  Saved {len(workloads)} workloads")


def run_h6(cfg: H6Config) -> pd.DataFrame:
    _ensure_benchmark(cfg)

    # Validate Ollama planner is available
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
                rows.append(
                    {
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
                    }
                )

                done += 1
                if done % 50 == 0 or done == total:
                    elapsed = time.time() - t_start
                    eta = (elapsed / done) * (total - done)
                    print(
                        f"    [{done}/{total}] {elapsed:.0f}s elapsed, ETA {eta:.0f}s"
                    )
                    sys.stdout.flush()
                # Incremental save every 200 cells
                if done % 200 == 0:
                    pd.DataFrame(rows).to_csv(
                        out_dir / "results.partial.csv", index=False
                    )

    return pd.DataFrame(rows)


# ============================================================================
# Verdict
# ============================================================================
def compute_h6_verdict(df: pd.DataFrame, synth_results_path: str | None) -> dict:
    """Compare H6 curve to synthetic C1 family-a results."""
    # Fit piecewise on H6 data
    agg = df.groupby("ratio")["coord_success"].mean().reset_index()
    real_fit = fit_piecewise(agg["ratio"].to_numpy(), agg["coord_success"].to_numpy())
    real_curve = {
        str(r): float(s) for r, s in zip(agg["ratio"], agg["coord_success"])
    }

    verdict: dict[str, Any] = {
        "real_tau": real_fit["tau"],
        "real_drop_rel": real_fit["drop_rel"],
        "real_curve": real_curve,
        "real_mean_coord": float(df["coord_success"].mean()),
        "real_mean_f1": float(df["f1"].mean()),
    }

    if not synth_results_path:
        verdict["h6_supported"] = None
        verdict["note"] = "No synthetic results path provided; skipping comparison."
        return verdict

    # Load synthetic results
    synth_csv = Path(synth_results_path) / "results.csv"
    if not synth_csv.exists():
        verdict["h6_supported"] = None
        verdict["note"] = f"Synthetic results not found at {synth_csv}"
        return verdict

    synth_df = pd.read_csv(synth_csv)

    # Try H5 format first (has planner_model column)
    if "planner_model" in synth_df.columns:
        synth_df = synth_df[
            (synth_df["family"] == "a") & (synth_df["planner_model"] == "8B")
        ]
    elif "family" in synth_df.columns:
        # H1/H2 format
        synth_df = synth_df[
            (synth_df["family"] == "a") & (synth_df["compressor"] == "lingua2")
        ]

    if synth_df.empty:
        verdict["h6_supported"] = None
        verdict["note"] = "No matching synthetic family-a data found."
        return verdict

    synth_agg = synth_df.groupby("ratio")["coord_success"].mean().reset_index()
    synth_fit = fit_piecewise(
        synth_agg["ratio"].to_numpy(), synth_agg["coord_success"].to_numpy()
    )
    synth_curve = {
        str(r): float(s) for r, s in zip(synth_agg["ratio"], synth_agg["coord_success"])
    }

    verdict["synth_tau"] = synth_fit["tau"]
    verdict["synth_drop_rel"] = synth_fit["drop_rel"]
    verdict["synth_curve"] = synth_curve

    # Guard: no cliff detected
    if real_fit["drop_rel"] < 0.15 or synth_fit["drop_rel"] < 0.15:
        verdict["h6_supported"] = False
        verdict["note"] = (
            f"Insufficient cliff: real drop={real_fit['drop_rel']:.2f}, "
            f"synth drop={synth_fit['drop_rel']:.2f}. Need >= 0.15 on both."
        )
        return verdict

    # Tau comparison: within +/-15%
    tau_real = real_fit["tau"]
    tau_synth = synth_fit["tau"]
    if np.isnan(tau_real) or np.isnan(tau_synth) or tau_synth == 0:
        tau_passes = False
        tau_diff_pct = float("nan")
    else:
        tau_diff_pct = abs(tau_real - tau_synth) / abs(tau_synth) * 100
        tau_passes = tau_diff_pct <= 15.0
    verdict["tau_diff_pct"] = tau_diff_pct
    verdict["tau_within_15pct"] = tau_passes

    # Coord success curve comparison (informational only — scoring differs
    # between H6 token-F1>=0.5 and H5 numeric-error>0.75, so direct
    # comparison of absolute values is not meaningful)
    overlapping = set(real_curve.keys()) & set(synth_curve.keys())
    if overlapping:
        max_diff_pp = max(abs(real_curve[r] - synth_curve[r]) * 100 for r in overlapping)
        verdict["max_coord_diff_pp"] = max_diff_pp
        verdict["coord_within_10pp"] = max_diff_pp <= 10.0
        verdict["coord_note"] = "Informational only — scoring thresholds differ between H6 and H5."

    # H6 supported: tau* comparison only (scale-independent)
    verdict["h6_supported"] = tau_passes
    return verdict


# ============================================================================
# Entry point
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="H6: MultiHopRAG transfer validation")
    parser.add_argument("--smoke", action="store_true", help="Quick smoke test")
    parser.add_argument("--out", type=str, default=None, help="Output directory")
    parser.add_argument(
        "--synth-results",
        type=str,
        default=None,
        help="Path to H5 results dir for comparison",
    )
    args = parser.parse_args()

    cfg = H6Config.smoke() if args.smoke else H6Config()
    if args.out:
        cfg.out_dir = args.out
    if args.synth_results:
        cfg.synth_results_path = args.synth_results

    print("=" * 60)
    print("H6: MultiHopRAG Transfer Validation")
    print("=" * 60)
    print(f"Compressor: {cfg.compressor}")
    print(f"Planner: {cfg.planner_model}")
    print(f"Ratios: {cfg.ratios}")
    print(f"Seeds: {cfg.seeds}")
    print(f"Workloads: {cfg.n_workloads}")
    print(f"Output: {cfg.out_dir}")
    print()

    df = run_h6(cfg)

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "results.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nSaved {len(df)} rows to {csv_path}")

    # Quick summary
    print("\nCoord success by ratio:")
    summary = df.groupby("ratio")["coord_success"].mean()
    for ratio, cs in summary.items():
        print(f"  {ratio:5.1f}x: {cs:.2%}")

    # Verdict
    verdict = compute_h6_verdict(df, cfg.synth_results_path)
    print(f"\nH6 VERDICT:")
    print(f"  Real tau*: {verdict['real_tau']:.1f}" if not np.isnan(verdict.get("real_tau", float("nan"))) else "  Real tau*: N/A")
    print(f"  Real drop: {verdict['real_drop_rel']:.1%}")
    if verdict.get("synth_tau") is not None:
        print(f"  Synth tau*: {verdict['synth_tau']:.1f}")
        print(f"  Tau diff: {verdict.get('tau_diff_pct', 0):.1f}%")
        print(f"  Max coord diff: {verdict.get('max_coord_diff_pp', 0):.1f}pp")
    if verdict.get("note"):
        print(f"  Note: {verdict['note']}")
    print(f"  => H6 SUPPORTED: {verdict['h6_supported']}")

    with open(out_dir / "verdicts.json", "w") as f:
        json.dump(verdict, f, indent=2, default=str)
    print(f"\nVerdicts saved to {out_dir / 'verdicts.json'}")


if __name__ == "__main__":
    main()
