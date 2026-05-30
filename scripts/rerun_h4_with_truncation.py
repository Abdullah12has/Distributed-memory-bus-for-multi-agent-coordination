#!/usr/bin/env python3
"""Rerun H4 with all four compressors including truncation.

Senior-reviewer audit (2026-05-30) flagged truncation's absence from the
canonical h4_unbiased run as a construct-validity gap: without truncation
as a destruction-only baseline, the disclosure metric can't separately test
'privacy gain > utility loss'. This script reruns H4 with truncation
included so the manuscript can report the four-compressor result.

Output: results/h4_unbiased_v2/{results.csv, verdicts.json}
"""
from __future__ import annotations

import json
from pathlib import Path

from m6.experiments.run_h4 import H4Config, compute_h4_verdict, run_h4

OUT_DIR = "results/h4_unbiased_v2"


def main() -> None:
    cfg = H4Config(
        compressors=["lingua2", "phi3-extractive", "filter", "truncation"],
        out_dir=OUT_DIR,
    )

    print("=" * 60)
    print("H4 rerun with truncation included")
    print(f"Compressors: {cfg.compressors}")
    print(f"Output: {OUT_DIR}")
    print("=" * 60)

    df = run_h4(cfg)
    out_path = Path(cfg.out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    if not df.empty:
        df.to_csv(out_path / "results.csv", index=False)
        print(f"\nSaved {len(df)} rows to {out_path / 'results.csv'}")

    verdict = compute_h4_verdict(df)
    print("\nH4 v2 VERDICT (4 compressors):")
    for comp, data in verdict.get("per_compressor", {}).items():
        print(
            f"  {comp}: priors={data['priors_rate']:.3f} "
            f"baseline={data['baseline_rate']:.3f} "
            f"compressed={data['compressed_rate']:.3f}"
        )
        print(
            f"    signal: {'YES' if data['signal_significant'] else 'no'} | "
            f"reduction: {'YES' if data['reduction_significant'] else 'no'}"
        )
    print(f"  => H4 SUPPORTED: {verdict['h4_supported']}")

    with open(out_path / "verdicts.json", "w") as f:
        json.dump(verdict, f, indent=2, default=str)
    print(f"Verdicts saved to {out_path / 'verdicts.json'}")


if __name__ == "__main__":
    main()
