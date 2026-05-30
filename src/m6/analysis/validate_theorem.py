#!/usr/bin/env python3
"""Validate Theorem 1 (compounding-error model) against empirical data.

Reads H1/H2 sweep CSV, extracts token_recall curves, computes predicted
tau from Theorem 1, and compares to empirical cliff positions. Generates
the predicted-vs-empirical comparison that is the key theory-validation
figure for the NeurIPS paper.

Usage:
    python -m m6.analysis.validate_theorem --csv results/h1_h2/sweep_results.csv
    python -m m6.analysis.validate_theorem --csv results/h1_h2/sweep_results.csv --plot
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from m6.theory.cliff_prediction import (
    cross_validate_theta,
    extract_token_recall_curve,
    full_validation,
    full_validation_per_family,
    predicted_success_smooth,
    predicted_tau,
    q_required,
)


def run_validation(
    csv_path: str,
    n_compression_passes: int = 1,
    theta: float = 0.5,
    compressors: list[str] | None = None,
    families: list[str] | None = None,
) -> dict:
    """Run full Theorem 1 validation on H1/H2 sweep data."""
    results = full_validation(
        csv_path,
        n_compression_passes=n_compression_passes,
        theta=theta,
        compressors=compressors,
        families=families,
    )
    return results


def print_validation(results: dict) -> None:
    """Pretty-print validation results, including the rel-error distribution."""
    summary = results.get("_summary", {})
    q_min = q_required(summary.get("theta", 0.5), summary.get("n_compression_passes", 1))
    print(f"Compounding-error model parameters: N={summary.get('n_compression_passes')}, theta={summary.get('theta')}, q_min={q_min:.4f}")
    print()

    rel_errors: list[float] = []
    n_cells = 0
    n_match_25 = 0
    n_match_50 = 0
    for comp, fam_results in results.items():
        if comp.startswith("_"):
            continue
        print(f"  Compressor: {comp}")
        for fam, val in fam_results.items():
            if "error" in val:
                print(f"    Family {fam}: ERROR — {val['error']}")
                continue
            pred = val.get("predicted_tau", float("nan"))
            emp = val.get("empirical_tau", float("nan"))
            err = val.get("rel_error_pct", float("nan"))
            match = val.get("match", False)
            marker = "MATCH" if match else "MISS"
            pred_str = f"{pred:.2f}" if not np.isinf(pred) and not np.isnan(pred) else "N/A"
            emp_str = f"{emp:.2f}" if not np.isnan(emp) else "N/A"
            err_str = f"{err:.1f}%" if not np.isnan(err) else "N/A"
            print(f"    Family {fam}: predicted={pred_str}, empirical={emp_str}, error={err_str} [{marker}]")
            n_cells += 1
            if not np.isnan(err) and not np.isinf(err):
                rel_errors.append(float(err))
                if err <= 25.0:
                    n_match_25 += 1
                if err <= 50.0:
                    n_match_50 += 1
            # NaN/Inf cells count as MISS in both denominators (consistent
            # with the original thesis prose convention)
        print()

    # Report both ±25% and ±50% over the *same* denominator (total cells
    # attempted, including NaN/Inf cells which count as MISS).
    rate_25 = n_match_25 / max(n_cells, 1)
    rate_50 = n_match_50 / max(n_cells, 1)
    print(f"Summary: {n_match_25}/{n_cells} matches at ±25% ({rate_25:.0%})")
    print(f"         {n_match_50}/{n_cells} matches at ±50% ({rate_50:.0%})")
    if rel_errors:
        errs = np.array(rel_errors)
        n_finite = len(errs)
        print(
            f"Relative-error distribution (n={n_finite} cells with finite rel_error): "
            f"median={np.median(errs):.1f}%, "
            f"IQR=[{np.percentile(errs, 25):.1f}, {np.percentile(errs, 75):.1f}]%, "
            f"max={errs.max():.1f}%"
        )


def generate_plot(csv_path: str, out_dir: str, n_compression_passes: int = 1, theta: float = 0.5) -> None:
    """Generate the predicted-vs-empirical figure."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    df = pd.read_csv(csv_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    q_min = q_required(theta, n_compression_passes)
    compressors = sorted(df["compressor"].unique())

    # Focus on family-a (sharpest cliff)
    fam_a = df[df["family"] == "a"]
    if fam_a.empty:
        print("No family-a data found")
        return

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    # Left: token recall curves + q_min
    ax1 = axes[0]
    colors = {"lingua2": "#1b9e77", "phi3-extractive": "#d95f02", "filter": "#7570b3", "truncation": "#e7298a"}
    for comp in compressors:
        sub = fam_a[fam_a["compressor"] == comp]
        tr = sub.groupby("ratio")["token_recall"].mean().reset_index()
        color = colors.get(comp, "#333333")
        ax1.plot(tr["ratio"], tr["token_recall"], "o-", color=color, label=comp, markersize=4)
    ax1.axhline(q_min, ls="--", color="red", alpha=0.7, label=f"$q_{{min}}$ = {q_min:.3f}")
    ax1.set_xlabel("Compression Ratio")
    ax1.set_ylabel("Token Recall $q(r)$")
    ax1.set_title("Token Retention vs Compression")
    ax1.legend(fontsize=8)
    ax1.set_ylim(-0.05, 1.05)

    # Right: empirical vs predicted coordination success
    ax2 = axes[1]
    for comp in compressors:
        sub = fam_a[fam_a["compressor"] == comp]
        # Empirical
        agg = sub.groupby("ratio")["coord_success"].mean().reset_index()
        color = colors.get(comp, "#333333")
        ax2.plot(agg["ratio"], agg["coord_success"], "o-", color=color, label=f"{comp} (emp)", markersize=4)
        # Predicted
        tr = sub.groupby("ratio")["token_recall"].mean().reset_index()
        curve = list(zip(tr["ratio"].tolist(), tr["token_recall"].tolist()))
        if curve:
            predicted = predicted_success_smooth(curve, n_compression_passes, theta, p0=1.0, steepness=25.0)
            pr = [r for r, _ in predicted]
            ps = [s for _, s in predicted]
            ax2.plot(pr, ps, "x--", color=color, alpha=0.5, markersize=5)

    # Add predicted tau vertical line for lingua2
    try:
        tr_curve = extract_token_recall_curve(csv_path, "lingua2", "a")
        pred_tau = predicted_tau(tr_curve, n_compression_passes, theta)
        if not np.isinf(pred_tau):
            ax2.axvline(pred_tau, ls=":", color="red", alpha=0.6, label=f"Predicted $\\tau^*$={pred_tau:.1f}")
    except Exception:
        pass

    ax2.set_xlabel("Compression Ratio")
    ax2.set_ylabel("Coordination Success")
    ax2.set_title("Predicted vs Empirical (Theorem 1)")
    ax2.legend(fontsize=7)
    ax2.set_ylim(-0.05, 1.05)

    fig.tight_layout()
    fig.savefig(out / "theorem1_validation.pdf", dpi=300, bbox_inches="tight")
    fig.savefig(out / "theorem1_validation.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved figures to {out}/theorem1_validation.{{pdf,png}}")


def main():
    parser = argparse.ArgumentParser(description="Validate the compounding-error model against empirical data")
    parser.add_argument("--csv", type=str, required=True, help="H1/H2 sweep_results.csv path")
    parser.add_argument("--n-compression-passes", type=int, default=1, help="Number of compression passes")
    parser.add_argument("--theta", type=float, default=0.5, help="Success threshold (global in-sample only)")
    parser.add_argument("--recall-column", type=str, default="critical_token_recall",
                        help="Column name for per-family theta derivation (default: critical_token_recall)")
    parser.add_argument(
        "--validation-mode",
        type=str,
        choices=["loo", "in-sample", "all"],
        default="loo",
        help=(
            "Which validation to treat as the headline. 'loo' (default, recommended): "
            "leave-one-family-out cross-validation of theta_q; not-in-sample. "
            "'in-sample': full_validation + full_validation_per_family (theta derived "
            "and tested on the same sweep — sanity check only). 'all': run all three."
        ),
    )
    parser.add_argument("--plot", action="store_true", help="Generate validation figure")
    parser.add_argument("--out", type=str, default="figures", help="Output dir for plots/JSON")
    args = parser.parse_args()

    print("=" * 60)
    print("Compounding-Error Model Validation")
    print(f"Validation mode: {args.validation_mode}")
    print("=" * 60)
    print()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.validation_mode in ("loo", "all"):
        print("--- Leave-one-family-out cross-validation (headline) ---")
        try:
            loo_results = cross_validate_theta(
                args.csv,
                n_compression_passes=args.n_compression_passes,
                recall_column=args.recall_column,
            )
            with open(out_dir / "theorem1_validation_loo.json", "w") as f:
                json.dump(loo_results, f, indent=2, default=str)
            loo_summary = loo_results.get("_summary", {})
            n_match = loo_summary.get("n_match", 0)
            n_total = loo_summary.get("n_validated", 0)
            print(
                f"LOO-CV summary: {n_match}/{n_total} matches at ±25%; "
                f"theta_q derived on n-1 families, predicted tau on the held-out family."
            )
            per_family_theta = loo_summary.get("per_family_theta_loo", {})
            if per_family_theta:
                print(f"Per-family LOO theta_q: {per_family_theta}")
            print(f"LOO results saved to {out_dir / 'theorem1_validation_loo.json'}")
        except Exception as e:
            print(f"  [skip] LOO-CV failed: {e}")
        print()

    if args.validation_mode in ("in-sample", "all"):
        print("--- Global theta in-sample validation (sanity check) ---")
        results = run_validation(args.csv, n_compression_passes=args.n_compression_passes, theta=args.theta)
        print_validation(results)
        with open(out_dir / "theorem1_validation.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nGlobal in-sample results saved to {out_dir / 'theorem1_validation.json'}")

        print()
        print("--- Per-family in-sample validation ---")
        try:
            pf_results = full_validation_per_family(
                args.csv,
                n_compression_passes=args.n_compression_passes,
                recall_column=args.recall_column,
            )
            print_validation(pf_results)
            pf_summary = pf_results.get("_summary", {})
            per_family_theta = pf_summary.get("per_family_theta", {})
            print(f"\nPer-family thetas: {per_family_theta}")
            with open(out_dir / "theorem1_validation_per_family.json", "w") as f:
                json.dump(pf_results, f, indent=2, default=str)
            print(f"Per-family in-sample results saved to {out_dir / 'theorem1_validation_per_family.json'}")
        except Exception as e:
            print(f"  [skip] per-family in-sample validation failed: {e}")

    if args.plot:
        generate_plot(args.csv, args.out, n_compression_passes=args.n_compression_passes, theta=args.theta)


if __name__ == "__main__":
    main()
