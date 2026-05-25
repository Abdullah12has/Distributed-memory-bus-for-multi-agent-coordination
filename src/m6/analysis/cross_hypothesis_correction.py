#!/usr/bin/env python3
"""Cross-hypothesis Holm-Bonferroni correction.

Plan-v3 §5.4 specifies Holm correction within families {H1,H2,H5}, {H3}, {H4}.
Each experiment runner corrects only within itself. This script collects all
p-values across hypotheses and applies joint correction.

Usage:
    python -m m6.analysis.cross_hypothesis_correction \\
        --h1h2 results/h1_h2/verdicts.json \\
        --h5 results/h5/verdicts.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from m6.experiments.run_h1_h2 import holm_correction


def collect_pvalues(
    h1h2_verdicts: dict | None = None,
    h5_verdicts: dict | None = None,
) -> list[tuple[str, str, float]]:
    """Collect all p-values from H1, H2, H5 for joint correction.

    Returns list of (hypothesis, label, p_value) tuples.
    """
    pvals: list[tuple[str, str, float]] = []

    # H1: one p-value per compressor
    if h1h2_verdicts and "h1" in h1h2_verdicts:
        h1 = h1h2_verdicts["h1"]
        for comp, result in h1.items():
            if isinstance(result, dict) and "p" in result:
                pvals.append(("H1", f"rho_{comp}", float(result["p"])))

    # H2: one p-value per (compressor, family) cell
    if h1h2_verdicts and "h2" in h1h2_verdicts:
        h2 = h1h2_verdicts["h2"]
        for cell in h2.get("cells", []):
            p = cell.get("test_p")
            if p is not None:
                label = f"{cell['compressor']}/{cell['family']}"
                pvals.append(("H2", label, float(p)))

    # H5: currently uses piecewise fit, no per-family p-value
    # (H5 verdict is based on monotonicity + gap, not statistical tests)
    # Include if H5 adds statistical tests in the future.

    return pvals


def apply_cross_correction(
    pvals: list[tuple[str, str, float]],
) -> list[tuple[str, str, float, float]]:
    """Apply Holm-Bonferroni to the joint {H1, H2, H5} family.

    Returns list of (hypothesis, label, raw_p, adjusted_p) tuples.
    """
    if not pvals:
        return []
    raw = [p for _, _, p in pvals]
    adjusted = holm_correction(raw)
    return [
        (hyp, label, raw_p, adj_p)
        for (hyp, label, raw_p), adj_p in zip(pvals, adjusted)
    ]


def main():
    parser = argparse.ArgumentParser(description="Cross-hypothesis Holm correction")
    parser.add_argument("--h1h2", type=str, default=None, help="H1/H2 verdicts.json")
    parser.add_argument("--h5", type=str, default=None, help="H5 verdicts.json")
    parser.add_argument("--out", type=str, default="results/cross_correction.json")
    args = parser.parse_args()

    h1h2 = json.loads(Path(args.h1h2).read_text()) if args.h1h2 else None
    h5 = json.loads(Path(args.h5).read_text()) if args.h5 else None

    pvals = collect_pvalues(h1h2, h5)
    corrected = apply_cross_correction(pvals)

    print("=" * 60)
    print("Cross-Hypothesis Holm-Bonferroni Correction")
    print(f"Family: {{H1, H2, H5}} — {len(pvals)} tests")
    print("=" * 60)

    any_changed = False
    for hyp, label, raw, adj in corrected:
        changed = (raw < 0.05) != (adj < 0.05)
        marker = " *** CHANGED" if changed else ""
        if changed:
            any_changed = True
        print(f"  {hyp} {label:30s} raw={raw:.6f}  adj={adj:.6f}{marker}")

    if not any_changed:
        print("\nNo verdicts changed by cross-hypothesis correction.")
    else:
        print("\nWARNING: Some verdicts changed — update the paper!")

    result = {
        "tests": [
            {"hypothesis": h, "label": l, "p_raw": r, "p_adjusted": a}
            for h, l, r, a in corrected
        ],
        "n_tests": len(corrected),
        "any_verdict_changed": any_changed,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
