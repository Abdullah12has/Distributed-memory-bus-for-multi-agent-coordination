#!/usr/bin/env python3
"""H4 — Summary-level inference disclosure.

Measures whether compression reduces leakage of protected facts.
A held-out Ollama reader tries to recover protected facts under three conditions:
  1. priors-only (no fragments)
  2. baseline (uncompressed, ratio=1)
  3. compressed (ratio=4)

H4 supported iff:
  - baseline > priors (metric measures something real)
  - compressed < baseline (compression reduces disclosure)
  - Both with paired-bootstrap p < 0.05

Run:
    python -m m6.experiments.run_h4
    python -m m6.experiments.run_h4 --smoke
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import numpy as np
import pandas as pd

from m6.benchmark.generator import load as load_benchmark
from m6.compressors import make_compressor

# ============================================================================
# Config
# ============================================================================
OLLAMA_URL = "http://127.0.0.1:11434"
READER_MODEL = "llama3.1:8b"


@dataclass
class H4Config:
    benchmark_path: str = "data/processed/c1-v0.1"
    compressors: list[str] | None = None
    ratio: float = 4.0
    n_workloads: int | None = None
    out_dir: str = "results/h4"
    reader_model: str = READER_MODEL

    def __post_init__(self):
        if self.compressors is None:
            self.compressors = ["lingua2", "phi3-extractive", "filter"]

    @classmethod
    def smoke(cls) -> H4Config:
        return cls(compressors=["lingua2", "phi3-extractive"], n_workloads=3, out_dir="results/h4_smoke")


# ============================================================================
# Ollama reader
# ============================================================================
def ask_reader(model: str, context: str, question: str) -> str:
    """Ask the reader model a yes/no question given context. Returns 'yes' or 'no'."""
    prompt = f"""Based ONLY on the following context, answer the question with exactly "yes" or "no".

Context:
{context}

Question: {question}

Answer (yes/no):"""

    try:
        resp = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 10, "temperature": 0.0},
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        answer = resp.json().get("response", "").strip().lower()
        if "yes" in answer:
            return "yes"
        return "no"
    except Exception as e:
        import sys
        print(f"  [warn] reader exception: {e}", file=sys.stderr)
        return "error"


# ============================================================================
# Statistics (inline)
# ============================================================================
from m6.experiments.run_h1_h2 import holm_correction as _holm_correction


def paired_bootstrap(a: np.ndarray, b: np.ndarray, n_boot: int = 10000) -> dict:
    diff = a - b
    observed = float(diff.mean())
    rng = np.random.default_rng(42)
    n = len(diff)
    if n == 0:
        return {"diff": 0.0, "ci_low": 0.0, "ci_high": 0.0, "p": 1.0}
    means = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        means[i] = diff[idx].mean()
    centred = means - means.mean()
    p = float(np.mean(np.abs(centred) >= abs(observed)))
    p = max(p, 1.0 / n_boot)
    return {
        "diff": observed,
        "ci_low": float(np.quantile(means, 0.025)),
        "ci_high": float(np.quantile(means, 0.975)),
        "p": p,
    }


# ============================================================================
# Main
# ============================================================================
def run_h4(cfg: H4Config) -> pd.DataFrame:
    print(f"Loading benchmark from {cfg.benchmark_path}...")
    workloads = load_benchmark(cfg.benchmark_path)
    # Only use workloads that have protected facts
    workloads = [w for w in workloads if w.protected_facts]
    if cfg.n_workloads:
        workloads = workloads[: cfg.n_workloads]
    print(f"  {len(workloads)} workloads with protected facts")

    if not workloads:
        print("  WARNING: No workloads have protected facts. Generating dummy results.")
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []

    # Cache compressors (avoid reloading LLMLingua-2 / Phi-3 per question)
    comp_cache: dict[str, Any] = {}
    for comp_name in cfg.compressors:
        print(f"  Loading compressor: {comp_name}...")
        comp_cache[comp_name] = make_compressor(comp_name, target_ratio=cfg.ratio)

    for w in workloads:
        preamble = w.initial_prompt  # public info only
        frag_lookup = {f.fragment_id: f for f in w.fragments}

        for pf in w.protected_facts:
            frag_obj = frag_lookup.get(pf.fragment_id)
            frag_text = frag_obj.text if frag_obj else ""

            for q, gt_answer in zip(pf.yesno_questions, pf.answers, strict=False):
                # Condition 1: priors only
                priors_answer = ask_reader(cfg.reader_model, preamble, q)
                priors_correct = float(priors_answer == gt_answer)

                # Condition 2: baseline (uncompressed)
                baseline_answer = ask_reader(cfg.reader_model, frag_text, q)
                baseline_correct = float(baseline_answer == gt_answer)

                # Condition 3: compressed at 4x (per plan-v3, test all compressors)
                if frag_obj is None:
                    continue
                for comp_name in cfg.compressors:
                    comp = comp_cache[comp_name]
                    slot = comp.compress(frag_obj)
                    compressed_text = comp.decompress(slot) or ""
                    comp_answer = ask_reader(cfg.reader_model, compressed_text, q)
                    comp_correct = float(comp_answer == gt_answer)

                    rows.append({
                        "workload_id": w.workload_id,
                        "fragment_id": pf.fragment_id,
                        "question": q,
                        "gt_answer": gt_answer,
                        "compressor": comp_name,
                        "ratio": cfg.ratio,
                        "priors_correct": priors_correct,
                        "baseline_correct": baseline_correct,
                        "compressed_correct": comp_correct,
                        "compressed_text_len": len(compressed_text),
                        "original_text_len": len(frag_text),
                    })

        print(f"  {w.workload_id}: {len(w.protected_facts)} protected facts processed")

    return pd.DataFrame(rows)


def compute_h4_verdict(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"h4_supported": False, "note": "no protected facts found"}

    # Aggregate per compressor — collect all p-values for Holm correction
    per_comp = {}
    all_p_values = []  # (compressor, test_type, p_value)
    for comp, sub in df.groupby("compressor"):
        priors = sub["priors_correct"].to_numpy(dtype=np.float64)
        baseline = sub["baseline_correct"].to_numpy(dtype=np.float64)
        compressed = sub["compressed_correct"].to_numpy(dtype=np.float64)

        # Test 1: baseline > priors (metric is real)
        test_signal = paired_bootstrap(baseline, priors)
        # Test 2: compressed < baseline (compression helps privacy)
        test_reduction = paired_bootstrap(baseline, compressed)

        per_comp[comp] = {
            "priors_rate": float(priors.mean()),
            "baseline_rate": float(baseline.mean()),
            "compressed_rate": float(compressed.mean()),
            "signal_test": test_signal,
            "reduction_test": test_reduction,
        }
        all_p_values.append((comp, "signal", test_signal["p"]))
        all_p_values.append((comp, "reduction", test_reduction["p"]))

    # Holm-Bonferroni correction across all tests
    raw_ps = [p for _, _, p in all_p_values]
    adjusted = _holm_correction(raw_ps)
    for (comp, test_type, _), p_adj in zip(all_p_values, adjusted):
        per_comp[comp][f"{test_type}_test"]["p_holm"] = p_adj

    # Apply significance using Holm-corrected p-values
    for comp, d in per_comp.items():
        d["signal_significant"] = d["signal_test"]["p_holm"] < 0.05 and d["signal_test"]["diff"] > 0
        d["reduction_significant"] = d["reduction_test"]["p_holm"] < 0.05 and d["reduction_test"]["diff"] > 0

    # H4 supported: at least one compressor shows both signal AND reduction
    any_supported = any(
        d["signal_significant"] and d["reduction_significant"] for d in per_comp.values()
    )
    return {"per_compressor": per_comp, "h4_supported": any_supported}


def main():
    parser = argparse.ArgumentParser(description="H4: Inference disclosure")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()

    cfg = H4Config.smoke() if args.smoke else H4Config()
    if args.out:
        cfg.out_dir = args.out

    print("=" * 60)
    print("H4: Summary-Level Inference Disclosure")
    print("=" * 60)

    df = run_h4(cfg)
    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not df.empty:
        df.to_csv(out_dir / "results.csv", index=False)
        print(f"\nSaved {len(df)} rows to {out_dir / 'results.csv'}")

    verdict = compute_h4_verdict(df)
    print("\nH4 VERDICT:")
    for comp, data in verdict.get("per_compressor", {}).items():
        print(
            f"  {comp}: priors={data['priors_rate']:.2f} baseline={data['baseline_rate']:.2f} compressed={data['compressed_rate']:.2f}"
        )
        print(
            f"    signal: {'YES' if data['signal_significant'] else 'no'} | reduction: {'YES' if data['reduction_significant'] else 'no'}"
        )
    print(f"  => H4 SUPPORTED: {verdict['h4_supported']}")

    with open(out_dir / "verdicts.json", "w") as f:
        json.dump(verdict, f, indent=2, default=str)


if __name__ == "__main__":
    main()
