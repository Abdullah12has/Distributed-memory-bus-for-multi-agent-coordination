#!/usr/bin/env python3
"""Generate unified compression quality table across all hypotheses.

One table, all compressors as rows, key metrics as columns. Gives reviewers
a single-glance comparison.

Usage:
    python -m m6.analysis.unified_table \\
        --h1h2 results/h1_h2/sweep_results.csv \\
        --h4 results/h4/results.csv \\
        --h3 results/h3/results.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def build_unified_table(
    h1h2_csv: str | None = None,
    h4_csv: str | None = None,
    h3_csv: str | None = None,
    ratio: float = 4.0,
) -> pd.DataFrame:
    """Build the unified compressor comparison table at a given ratio."""
    rows = []

    compressor_set: set[str] = set()

    # H1/H2 data: token_recall, qa_f1, coord_success at the target ratio
    h1h2_data: dict[str, dict] = {}
    if h1h2_csv and Path(h1h2_csv).exists():
        df = pd.read_csv(h1h2_csv)
        for comp, sub in df[df["ratio"] == ratio].groupby("compressor"):
            compressor_set.add(str(comp))
            h1h2_data[str(comp)] = {
                "token_recall": float(sub["token_recall"].mean()),
                "qa_f1": float(sub["qa_f1"].mean()),
                "coord_success": float(sub["coord_success"].mean()),
            }

    # H4 data: disclosure rate at compressed condition
    h4_data: dict[str, float] = {}
    if h4_csv and Path(h4_csv).exists():
        df = pd.read_csv(h4_csv)
        if "has_error" in df.columns:
            df = df[~df["has_error"]]
        for comp, sub in df.groupby("compressor"):
            compressor_set.add(str(comp))
            h4_data[str(comp)] = float(sub["compressed_correct"].mean())

    # H3 data: P1 F1 at the target ratio
    h3_data: dict[str, float] = {}
    if h3_csv and Path(h3_csv).exists():
        df = pd.read_csv(h3_csv)
        p1 = df[(df["pipeline"] == "P1") & (df["ratio"] == ratio)]
        for comp, sub in p1.groupby("compressor"):
            compressor_set.add(str(comp))
            h3_data[str(comp)] = float(sub["f1"].mean())

    for comp in sorted(compressor_set):
        row = {"compressor": comp}
        if comp in h1h2_data:
            row.update(h1h2_data[comp])
        if comp in h4_data:
            row["disclosure_rate"] = h4_data[comp]
        if comp in h3_data:
            row["p1_f1"] = h3_data[comp]
        rows.append(row)

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Unified compression quality table")
    parser.add_argument("--h1h2", type=str, default=None)
    parser.add_argument("--h4", type=str, default=None)
    parser.add_argument("--h3", type=str, default=None)
    parser.add_argument("--ratio", type=float, default=4.0)
    parser.add_argument("--out", type=str, default="results/unified_table.csv")
    args = parser.parse_args()

    table = build_unified_table(args.h1h2, args.h4, args.h3, ratio=args.ratio)

    if table.empty:
        print("No data found. Provide at least one CSV with --h1h2, --h4, or --h3.")
        return

    print(f"\nUnified Compressor Quality Table @ {args.ratio}x compression:")
    print("=" * 80)
    print(table.to_string(index=False, float_format="%.3f"))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out, index=False)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
