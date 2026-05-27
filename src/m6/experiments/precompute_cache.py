#!/usr/bin/env python3
"""Precompute compression cache for all experiments.

Runs all compressors at all ratios on all benchmark fragments, saving
compressed texts to a JSON cache file. Run once on GPU, then use
--cache everywhere.

Usage:
    # Full (all compressors, all ratios — ~30-60 min on GPU)
    python -m m6.experiments.precompute_cache

    # Smoke test (2 ratios, 3 workloads)
    python -m m6.experiments.precompute_cache --smoke

    # Custom
    python -m m6.experiments.precompute_cache --compressors lingua2,filter --ratios 1,2,4,8
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from m6.benchmark.generator import load as load_benchmark
from m6.compressors import make_compressor
from m6.compressors.cache import CompressionCache


# Union of all ratios used across experiments
ALL_RATIOS = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0]

# Compressors that actually do work (skip identity — trivial)
ALL_COMPRESSORS = ["lingua2", "phi3-extractive", "filter", "truncation"]


@dataclass
class PrecomputeConfig:
    benchmark_path: str = "data/processed/c1-v0.1"
    compressors: list[str] = field(default_factory=lambda: list(ALL_COMPRESSORS))
    ratios: list[float] = field(default_factory=lambda: list(ALL_RATIOS))
    families: list[str] = field(default_factory=lambda: ["a", "b", "c"])
    n_workloads: int | None = None  # None = all
    out_path: str = "results/compression_cache.json"

    @classmethod
    def smoke(cls) -> PrecomputeConfig:
        return cls(
            compressors=["lingua2", "filter", "truncation"],
            ratios=[1.0, 4.0],
            n_workloads=3,
            out_path="results/compression_cache_smoke.json",
        )


def precompute(cfg: PrecomputeConfig) -> CompressionCache:
    print("Loading benchmark...")
    all_workloads = load_benchmark(cfg.benchmark_path)
    family_set = set(cfg.families)

    # Select workloads per family
    by_fam: dict[str, list] = {}
    for w in all_workloads:
        if w.family.value in family_set:
            by_fam.setdefault(w.family.value, []).append(w)

    workloads = []
    for fam in sorted(by_fam):
        ws = by_fam[fam]
        if cfg.n_workloads:
            ws = ws[: cfg.n_workloads]
        workloads.extend(ws)

    # Collect unique fragments and their associated task_hints
    # We need two hint variants per fragment:
    #   1. hint="" — for H3-P1, H4, H6 (no task_hint set)
    #   2. hint=workload.initial_prompt — for H1/H2, H3-P2/P3, H5, frontier, CAAC
    fragment_hints: dict[str, set[str]] = {}  # fragment_id -> set of hints
    fragment_texts: dict[str, str] = {}  # fragment_id -> original text
    fragment_tags: dict[str, any] = {}  # fragment_id -> tags

    for w in workloads:
        for frag in w.fragments:
            fid = frag.fragment_id
            fragment_texts[fid] = frag.text
            fragment_tags[fid] = frag.tags
            if fid not in fragment_hints:
                fragment_hints[fid] = set()
            fragment_hints[fid].add("")  # no-hint variant
            fragment_hints[fid].add(w.initial_prompt)  # with-hint variant

    n_fragments = len(fragment_texts)
    n_hint_pairs = sum(len(hints) for hints in fragment_hints.values())
    total = len(cfg.compressors) * len(cfg.ratios) * n_hint_pairs
    print(f"  {len(workloads)} workloads, {n_fragments} unique fragments")
    print(f"  {len(cfg.compressors)} compressors x {len(cfg.ratios)} ratios x {n_hint_pairs} (frag, hint) pairs")
    print(f"  Total compressions: {total}")

    cache = CompressionCache()
    cache.set_meta(
        benchmark=cfg.benchmark_path,
        compressors=cfg.compressors,
        ratios=cfg.ratios,
        n_fragments=n_fragments,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    done = 0
    t_start = time.time()

    for comp_name in cfg.compressors:
        for ratio in cfg.ratios:
            print(f"\n  {comp_name} @ {ratio}x...")
            comp = make_compressor(comp_name, target_ratio=ratio)

            for fid in sorted(fragment_texts):
                text = fragment_texts[fid]
                tags = fragment_tags[fid]

                for hint in sorted(fragment_hints[fid]):
                    # Build a Fragment with the appropriate task_hint
                    from m6.memory_bus.schemas import Fragment
                    frag = Fragment(
                        fragment_id=fid,
                        text=text,
                        tags=tags,
                        task_hint=hint if hint else None,
                    )

                    try:
                        slot = comp.compress(frag, target_ratio=ratio)
                        compressed_text = comp.decompress(slot) or text
                    except Exception as e:
                        print(f"    [warn] {comp_name}/{ratio}/{fid}: {e}")
                        compressed_text = text  # fallback to original

                    cache.store(comp_name, ratio, fid, hint if hint else None, compressed_text)
                    done += 1

                    if done % 200 == 0 or done == total:
                        elapsed = time.time() - t_start
                        rate = done / elapsed if elapsed > 0 else 0
                        eta = (total - done) / rate if rate > 0 else 0
                        print(
                            f"    [{done}/{total}] {elapsed:.0f}s elapsed, "
                            f"{rate:.1f} comp/s, ETA {eta:.0f}s"
                        )

    return cache


def main():
    parser = argparse.ArgumentParser(description="Precompute compression cache")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--out", type=str, default=None)
    parser.add_argument("--compressors", type=str, default=None,
                        help="Comma-separated compressor names")
    parser.add_argument("--ratios", type=str, default=None,
                        help="Comma-separated ratios")
    parser.add_argument("--families", type=str, default=None,
                        help="Comma-separated family letters (default: a,b,c)")
    parser.add_argument("--n-workloads", type=int, default=None,
                        help="Workloads per family (default: all)")
    args = parser.parse_args()

    cfg = PrecomputeConfig.smoke() if args.smoke else PrecomputeConfig()
    if args.out:
        cfg.out_path = args.out
    if args.compressors:
        cfg.compressors = [c.strip() for c in args.compressors.split(",")]
    if args.ratios:
        cfg.ratios = [float(r) for r in args.ratios.split(",")]
    if args.families:
        cfg.families = [f.strip() for f in args.families.split(",")]
    if args.n_workloads is not None:
        cfg.n_workloads = args.n_workloads

    print("=" * 60)
    print("Precompute Compression Cache")
    print("=" * 60)
    print(f"Benchmark: {cfg.benchmark_path}")
    print(f"Compressors: {cfg.compressors}")
    print(f"Ratios: {cfg.ratios}")
    print(f"Families: {cfg.families}")
    print(f"Output: {cfg.out_path}")
    print()

    cache = precompute(cfg)
    cache.save(cfg.out_path)
    print("\nDone!")


if __name__ == "__main__":
    main()
