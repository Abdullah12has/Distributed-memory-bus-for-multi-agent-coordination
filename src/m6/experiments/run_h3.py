#!/usr/bin/env python3
"""H3 — RAG pipeline placement: P1 vs P2 vs P3.

P1 dominates on storage-bounded (high compression), P2 on accuracy-bounded
(low compression). P3 closes the gap. Effect >= 5pp F1.

Run:
    python -m m6.experiments.run_h3
    python -m m6.experiments.run_h3 --smoke
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from m6.benchmark.generator import load as load_benchmark
from m6.benchmark.schemas import WorkloadFamily
from m6.compressors import make_compressor
from m6.pipelines import Pipeline1, Pipeline2, Pipeline3
from m6.pipelines.cost_model import eur_for_call


# ============================================================================
# Config
# ============================================================================
@dataclass
class H3Config:
    benchmark_path: str = "data/processed/c1-v0.1"
    compressors: list[str] | None = None
    ratio_storage: float = 8.0  # high compression for storage-bounded
    ratio_accuracy: float = 2.0  # low compression for accuracy-bounded
    n_workloads: int | None = None
    out_dir: str = "results/h3"

    def __post_init__(self):
        if self.compressors is None:
            self.compressors = ["lingua2", "phi3-extractive", "filter"]

    @classmethod
    def smoke(cls) -> H3Config:
        return cls(compressors=["lingua2", "phi3-extractive", "filter"], n_workloads=3, out_dir="results/h3_smoke")


# ============================================================================
# QA metric (inline)
# ============================================================================
def _normalize(s: str) -> str:
    import re
    import string

    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def f1_score(prediction: str, reference: str) -> float:
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


# ============================================================================
# Statistics (inline)
# ============================================================================
def paired_bootstrap_diff(a: np.ndarray, b: np.ndarray, n_boot: int = 10000) -> dict:
    diff = a - b
    observed = float(diff.mean())
    rng = np.random.default_rng(42)
    n = len(diff)
    means = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        means[i] = diff[idx].mean()
    centred = means - means.mean()
    p = float(np.mean(np.abs(centred) >= abs(observed)))
    p = max(p, 1.0 / n_boot)
    return {
        "diff_pp": observed * 100,
        "ci_low_pp": float(np.quantile(means, 0.025)) * 100,
        "ci_high_pp": float(np.quantile(means, 0.975)) * 100,
        "p_value": p,
    }


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
# Main
# ============================================================================
def run_h3(cfg: H3Config) -> pd.DataFrame:
    print(f"Loading benchmark from {cfg.benchmark_path}...")
    workloads = [
        w
        for w in load_benchmark(cfg.benchmark_path)
        if w.family is WorkloadFamily.CROSS_DOC_FACT_AGGREGATION
    ]
    if cfg.n_workloads:
        workloads = workloads[: cfg.n_workloads]
    print(f"  {len(workloads)} family-(a) workloads loaded")

    regime_ratios = {
        "storage_bounded": cfg.ratio_storage,
        "accuracy_bounded": cfg.ratio_accuracy,
    }
    rows: list[dict[str, Any]] = []

    for comp_name in cfg.compressors:
        for regime, ratio in regime_ratios.items():
            print(f"  {comp_name} / {regime} (ratio={ratio}x)...")
            comp = make_compressor(comp_name, target_ratio=ratio)
            pipelines = {
                "P1": Pipeline1(comp, target_ratio=ratio),
                "P2": Pipeline2(comp, target_ratio=ratio),
                "P3": Pipeline3(comp, target_ratio=ratio),
            }
            for w in workloads:
                corpus = list(w.fragments)
                source_ids = {f.fragment_id for f in w.fragments}
                for p_name, pipe in pipelines.items():
                    pipe.build(corpus)
                    hits = pipe.query(w.initial_prompt, k=5)
                    # Retrieval recall: fraction of source fragments retrieved
                    retrieved_ids = {h.fragment.fragment_id for h in hits}
                    retrieval_recall = len(retrieved_ids & source_ids) / max(len(source_ids), 1)
                    # Per-fragment content F1: how much source text survives
                    frag_f1s = []
                    for h in hits:
                        orig = next((f for f in w.fragments if f.fragment_id == h.fragment.fragment_id), None)
                        if orig:
                            frag_f1s.append(f1_score(h.fragment.text, orig.text))
                    content_f1 = sum(frag_f1s) / len(frag_f1s) if frag_f1s else 0.0
                    # Cost model: estimate tokens actually processed per pipeline
                    corpus_tokens = sum(len(f.text) // 4 for f in corpus)
                    retrieved_tokens = sum(len(h.fragment.text) // 4 for h in hits)
                    compressed_corpus_tokens = int(corpus_tokens / max(ratio, 1.0))
                    if p_name == "P1":
                        # compress full corpus → retrieve from compressed
                        # Cost = compress(full) + retrieve(compressed)
                        input_tokens = corpus_tokens + compressed_corpus_tokens
                    elif p_name == "P2":
                        # retrieve from full corpus → compress top-k only
                        # Cost = retrieve(full) + compress(top-k)
                        input_tokens = corpus_tokens + retrieved_tokens
                    else:  # P3
                        # retrieve full → conditionally compress subset
                        input_tokens = corpus_tokens + int(retrieved_tokens * 0.7)
                    eur = eur_for_call("local-ollama", input_tokens, 200)
                    rows.append(
                        {
                            "compressor": comp_name,
                            "regime": regime,
                            "ratio": ratio,
                            "pipeline": p_name,
                            "workload_id": w.workload_id,
                            "f1": content_f1,
                            "retrieval_recall": retrieval_recall,
                            "eur_per_query": eur,
                            "f1_over_eur": content_f1 / max(eur, 1e-9),
                        }
                    )

    return pd.DataFrame(rows)


def compute_h3_verdict(df: pd.DataFrame) -> dict:
    per_regime = {}
    p_values = []

    for regime in ("storage_bounded", "accuracy_bounded"):
        r = df[df["regime"] == regime]
        if r.empty:
            continue
        # Paired P1 vs P2 on workload_id
        p1 = r[r["pipeline"] == "P1"][["workload_id", "compressor", "f1"]].rename(
            columns={"f1": "f1_p1"}
        )
        p2 = r[r["pipeline"] == "P2"][["workload_id", "compressor", "f1"]].rename(
            columns={"f1": "f1_p2"}
        )
        paired = p1.merge(p2, on=["workload_id", "compressor"])
        if paired.empty:
            continue
        a = paired["f1_p1"].to_numpy(dtype=np.float64)
        b = paired["f1_p2"].to_numpy(dtype=np.float64)
        boot = paired_bootstrap_diff(a, b)
        p_values.append(boot["p_value"])

        # P3 ranking
        ranking = {}
        for pname in ("P1", "P2", "P3"):
            f1_vals = r[r["pipeline"] == pname]["f1"].to_numpy(dtype=np.float64)
            eur_vals = r[r["pipeline"] == pname]["eur_per_query"].to_numpy(dtype=np.float64)
            if f1_vals.size > 0:
                ranking[pname] = float(f1_vals.mean() / max(eur_vals.mean(), 1e-9))
        leader = max(ranking, key=lambda k: ranking[k]) if ranking else None

        per_regime[regime] = {
            "p1_vs_p2_diff_pp": boot["diff_pp"],
            "p1_vs_p2_ci_pp": [boot["ci_low_pp"], boot["ci_high_pp"]],
            "p1_vs_p2_p": boot["p_value"],
            "ranking": ranking,
            "leader": leader,
        }

    # Holm correct
    adjusted = holm_correction(p_values) if p_values else []
    for (regime, data), adj in zip(per_regime.items(), adjusted, strict=False):
        data["p_holm"] = adj

    # Verdict
    supported = False
    if len(per_regime) == 2:
        sb = per_regime.get("storage_bounded", {})
        ab = per_regime.get("accuracy_bounded", {})
        sign_flip = (sb.get("p1_vs_p2_diff_pp", 0) * ab.get("p1_vs_p2_diff_pp", 0)) < 0
        effect = (
            abs(sb.get("p1_vs_p2_diff_pp", 0)) >= 5.0 and abs(ab.get("p1_vs_p2_diff_pp", 0)) >= 5.0
        )
        p3_wins = sb.get("leader") == "P3" and ab.get("leader") == "P3"
        sig = all(d.get("p_holm", 1.0) < 0.05 for d in per_regime.values())
        supported = sign_flip and effect and p3_wins and sig

    return {"regimes": per_regime, "h3_supported": supported}


def main():
    parser = argparse.ArgumentParser(description="H3: RAG pipeline placement")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()

    cfg = H3Config.smoke() if args.smoke else H3Config()
    if args.out:
        cfg.out_dir = args.out

    print("=" * 60)
    print("H3: RAG Pipeline Placement")
    print("=" * 60)

    df = run_h3(cfg)
    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "results.csv", index=False)
    print(f"\nSaved {len(df)} rows to {out_dir / 'results.csv'}")

    verdict = compute_h3_verdict(df)
    print("\nH3 VERDICT:")
    for regime, data in verdict["regimes"].items():
        print(
            f"  {regime}: P1-P2 diff = {data['p1_vs_p2_diff_pp']:.1f}pp, leader = {data['leader']}"
        )
    print(f"  => H3 SUPPORTED: {verdict['h3_supported']}")

    with open(out_dir / "verdicts.json", "w") as f:
        json.dump(verdict, f, indent=2, default=str)


if __name__ == "__main__":
    main()
