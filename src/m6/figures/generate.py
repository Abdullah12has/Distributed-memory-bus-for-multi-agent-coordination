#!/usr/bin/env python3
"""Generate all paper figures from experiment results.

Produces 6 figures for the NeurIPS submission:
  1. cliff_hero.pdf       — Coordination cliff across model sizes (Figure 1)
  2. cliff_families.pdf   — Cliff shape by task family (Figure 2)
  3. predicted_vs_empirical.pdf — Theorem 1 validation (Figure 3)
  4. caac_pareto.pdf       — CAAC vs fixed-ratio Pareto frontier (Figure 4)
  5. privacy_quality.pdf   — Privacy-quality tradeoff (Figure 5)
  6. frontier_validation.pdf — Frontier model cliff (Figure 6)

Usage:
    python -m m6.figures.generate --results-dir results/ --out figures/
    python -m m6.figures.generate --h1h2 results/h1_h2/sweep_results.csv --out figures/
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Consistent style
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "legend.fontsize": 9,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
})

COLORS = {
    "1.5B": "#1b9e77",
    "3.8B": "#d95f02",
    "8B": "#7570b3",
    "14B": "#e7298a",
    "GPT-4o-mini": "#e6ab02",
    "lingua2": "#1b9e77",
    "phi3-extractive": "#d95f02",
    "filter": "#7570b3",
    "fixed": "#d62728",
    "caac": "#2ca02c",
}


def fig1_cliff_hero(h5_csv: str, out: Path) -> None:
    """Figure 1: Coordination cliff across model sizes for family-a."""
    df = pd.read_csv(h5_csv)
    df = df[df["family"] == "a"]
    if df.empty:
        print("  [skip] fig1: no family-a data in H5 results")
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    for model in sorted(df["planner_model"].unique(), key=lambda m: float(m.replace("B", ""))):
        sub = df[df["planner_model"] == model]
        agg = sub.groupby("ratio")["coord_success"].agg(["mean", "std"]).reset_index()
        color = COLORS.get(model, "#333333")
        ax.plot(agg["ratio"], agg["mean"], "o-", color=color, label=model, markersize=4)
        ax.fill_between(
            agg["ratio"],
            (agg["mean"] - agg["std"]).clip(0),
            (agg["mean"] + agg["std"]).clip(0, 1),
            alpha=0.15, color=color,
        )

    ax.set_xlabel("Compression Ratio")
    ax.set_ylabel("Coordination Success")
    ax.set_title("Coordination Cliff — Family A (Numeric Aggregation)")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(title="Planner Size")
    ax.axhline(0.5, ls=":", color="gray", alpha=0.5)
    fig.savefig(out / "cliff_hero.pdf")
    fig.savefig(out / "cliff_hero.png")
    plt.close(fig)
    print(f"  fig1: {out / 'cliff_hero.pdf'}")


def fig2_cliff_families(h1h2_csv: str, out: Path) -> None:
    """Figure 2: Cliff shape comparison across 3 task families."""
    df = pd.read_csv(h1h2_csv)
    if df.empty:
        print("  [skip] fig2: empty H1/H2 data")
        return

    families = sorted(df["family"].unique())
    fig, axes = plt.subplots(1, len(families), figsize=(4 * len(families), 3.5), sharey=True)
    if len(families) == 1:
        axes = [axes]

    family_labels = {"a": "Numeric Aggregation", "b": "Constraint Planning", "c": "Multi-Step Retrieval"}

    for ax, fam in zip(axes, families):
        sub = df[df["family"] == fam]
        for comp in sorted(sub["compressor"].unique()):
            csub = sub[sub["compressor"] == comp]
            agg = csub.groupby("ratio")["coord_success"].mean().reset_index()
            color = COLORS.get(comp, "#333333")
            ax.plot(agg["ratio"], agg["coord_success"], "o-", color=color, label=comp, markersize=3)
        ax.set_xlabel("Compression Ratio")
        ax.set_title(f"Family {fam.upper()}: {family_labels.get(fam, fam)}")
        ax.set_ylim(-0.05, 1.05)
        if fam == families[0]:
            ax.set_ylabel("Coordination Success")
            ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(out / "cliff_families.pdf")
    fig.savefig(out / "cliff_families.png")
    plt.close(fig)
    print(f"  fig2: {out / 'cliff_families.pdf'}")


def fig3_predicted_vs_empirical(h1h2_csv: str, out: Path) -> None:
    """Figure 3: Theorem 1 validation — predicted vs empirical cliff."""
    from m6.theory.cliff_prediction import (
        predicted_success_smooth,
        extract_token_recall_curve,
        q_required,
    )

    df = pd.read_csv(h1h2_csv)
    fam_a = df[(df["family"] == "a") & (df["compressor"] == "lingua2")]
    if fam_a.empty:
        print("  [skip] fig3: no lingua2/family-a data")
        return

    # Empirical curve
    agg = fam_a.groupby("ratio")["coord_success"].mean().reset_index()

    # Token recall curve
    tr_agg = fam_a.groupby("ratio")["token_recall"].mean().reset_index()
    tr_curve = list(zip(tr_agg["ratio"].tolist(), tr_agg["token_recall"].tolist()))

    # Predicted curve
    n_rounds, theta = 3, 0.65
    q_min = q_required(theta, n_rounds)
    predicted = predicted_success_smooth(tr_curve, n_rounds, theta, p0=1.0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Left: token recall + q_min threshold
    ax1.plot(tr_agg["ratio"], tr_agg["token_recall"], "s-", color="#1b9e77", label="Token Recall q(r)")
    ax1.axhline(q_min, ls="--", color="red", alpha=0.7, label=f"q_min = {q_min:.3f}")
    ax1.set_xlabel("Compression Ratio")
    ax1.set_ylabel("Token Recall q(r)")
    ax1.set_title("Token Retention Curve")
    ax1.legend()
    ax1.set_ylim(-0.05, 1.05)

    # Right: empirical vs predicted coordination success
    ax2.plot(agg["ratio"], agg["coord_success"], "o-", color="#7570b3", label="Empirical", markersize=5)
    pred_r = [r for r, _ in predicted]
    pred_s = [s for _, s in predicted]
    ax2.plot(pred_r, pred_s, "x--", color="#d95f02", label="Predicted (Theorem 1)", markersize=6)
    ax2.set_xlabel("Compression Ratio")
    ax2.set_ylabel("Coordination Success")
    ax2.set_title("Predicted vs Empirical Cliff")
    ax2.legend()
    ax2.set_ylim(-0.05, 1.05)

    fig.tight_layout()
    fig.savefig(out / "predicted_vs_empirical.pdf")
    fig.savefig(out / "predicted_vs_empirical.png")
    plt.close(fig)
    print(f"  fig3: {out / 'predicted_vs_empirical.pdf'}")


def fig4_caac_pareto(caac_csv: str, out: Path) -> None:
    """Figure 4: CAAC vs fixed-ratio Pareto frontier."""
    df = pd.read_csv(caac_csv)
    if df.empty:
        print("  [skip] fig4: empty CAAC data")
        return

    fig, ax = plt.subplots(figsize=(6, 4))

    for inner in sorted(df["inner_compressor"].unique()):
        sub = df[df["inner_compressor"] == inner]
        # Fixed
        fixed = sub[~sub["is_caac"]]
        fagg = fixed.groupby("target_ratio").agg(
            coord=("coord_success", "mean"),
            ratio=("achieved_ratio", "mean"),
        ).reset_index()
        ax.plot(fagg["ratio"], fagg["coord"], "o-", color=COLORS["fixed"],
                label=f"Fixed {inner}", markersize=5, alpha=0.7)

        # CAAC
        caac = sub[sub["is_caac"]]
        if not caac.empty:
            cagg = caac.groupby("target_ratio").agg(
                coord=("coord_success", "mean"),
                ratio=("achieved_ratio", "mean"),
            ).reset_index()
            ax.plot(cagg["ratio"], cagg["coord"], "s-", color=COLORS["caac"],
                    label=f"CAAC({inner})", markersize=6)

    ax.set_xlabel("Achieved Compression Ratio")
    ax.set_ylabel("Coordination Success")
    ax.set_title("CAAC vs Fixed-Ratio Compression")
    ax.legend()
    ax.set_ylim(-0.05, 1.05)
    fig.savefig(out / "caac_pareto.pdf")
    fig.savefig(out / "caac_pareto.png")
    plt.close(fig)
    print(f"  fig4: {out / 'caac_pareto.pdf'}")


def fig5_privacy_quality(h4_csv: str, out: Path) -> None:
    """Figure 5: Privacy-quality tradeoff across compressors."""
    df = pd.read_csv(h4_csv)
    if df.empty or "has_error" not in df.columns:
        # Try without error filtering
        pass
    else:
        df = df[~df["has_error"]]

    if df.empty:
        print("  [skip] fig5: empty H4 data")
        return

    fig, ax = plt.subplots(figsize=(6, 4))

    compressors = sorted(df["compressor"].unique())
    x = np.arange(len(compressors))
    width = 0.25

    for i, (label, col) in enumerate([
        ("Priors Only", "priors_correct"),
        ("Baseline (1x)", "baseline_correct"),
        ("Compressed (4x)", "compressed_correct"),
    ]):
        vals = [float(df[df["compressor"] == c][col].mean()) for c in compressors]
        bars = ax.bar(x + (i - 1) * width, vals, width, label=label, alpha=0.85)

    ax.set_xlabel("Compressor")
    ax.set_ylabel("Protected-Fact Recovery Rate")
    ax.set_title("Compression and Information Disclosure")
    ax.set_xticks(x)
    ax.set_xticklabels(compressors, rotation=15)
    ax.legend()
    ax.set_ylim(0, 1.05)
    fig.savefig(out / "privacy_quality.pdf")
    fig.savefig(out / "privacy_quality.png")
    plt.close(fig)
    print(f"  fig5: {out / 'privacy_quality.pdf'}")


def fig6_frontier(frontier_csv: str, local_csv: str | None, out: Path) -> None:
    """Figure 6: Frontier model vs local model cliff comparison."""
    df = pd.read_csv(frontier_csv)
    if df.empty:
        print("  [skip] fig6: empty frontier data")
        return

    fig, ax = plt.subplots(figsize=(6, 4))

    # Frontier
    agg = df.groupby("ratio")["coord_success"].mean().reset_index()
    model_name = df["model"].iloc[0]
    ax.plot(agg["ratio"], agg["coord_success"], "o-", color=COLORS.get("GPT-4o-mini", "#e6ab02"),
            label=model_name, markersize=6)

    # Local (if available)
    if local_csv and Path(local_csv).exists():
        ldf = pd.read_csv(local_csv)
        if "planner_model" in ldf.columns:
            ldf = ldf[(ldf["family"] == "a") & (ldf["planner_model"] == "8B")]
        elif "family" in ldf.columns:
            ldf = ldf[(ldf["family"] == "a") & (ldf["compressor"] == "lingua2")]
        if not ldf.empty:
            lagg = ldf.groupby("ratio")["coord_success"].mean().reset_index()
            ax.plot(lagg["ratio"], lagg["coord_success"], "s--", color=COLORS["8B"],
                    label="Llama-3.1-8B (local)", markersize=5, alpha=0.7)

    ax.set_xlabel("Compression Ratio")
    ax.set_ylabel("Coordination Success")
    ax.set_title("Frontier vs Local: Coordination Cliff")
    ax.legend()
    ax.set_ylim(-0.05, 1.05)
    fig.savefig(out / "frontier_validation.pdf")
    fig.savefig(out / "frontier_validation.png")
    plt.close(fig)
    print(f"  fig6: {out / 'frontier_validation.pdf'}")


# ============================================================================
# Entry point
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="Generate paper figures")
    parser.add_argument("--out", type=str, default="figures", help="Output directory")
    parser.add_argument("--h1h2", type=str, default=None, help="H1/H2 sweep CSV")
    parser.add_argument("--h4", type=str, default=None, help="H4 results CSV")
    parser.add_argument("--h5", type=str, default=None, help="H5 results CSV")
    parser.add_argument("--caac", type=str, default=None, help="CAAC results CSV")
    parser.add_argument("--frontier", type=str, default=None, help="Frontier results CSV")
    parser.add_argument("--local", type=str, default=None, help="Local model CSV for fig6 comparison")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Generating Paper Figures")
    print("=" * 60)

    # Auto-discover results if not specified
    def _find(pattern: str) -> str | None:
        hits = sorted(Path("results").rglob(pattern))
        return str(hits[-1]) if hits else None

    h1h2 = args.h1h2 or _find("sweep_results.csv")
    h4 = args.h4 or _find("h4*/results.csv")
    h5 = args.h5 or _find("h5*/results.csv")
    caac = args.caac or _find("caac*/results.csv")
    frontier = args.frontier or _find("frontier*/results.csv")

    if h5:
        fig1_cliff_hero(h5, out)
    if h1h2:
        fig2_cliff_families(h1h2, out)
        fig3_predicted_vs_empirical(h1h2, out)
    if caac:
        fig4_caac_pareto(caac, out)
    if h4:
        fig5_privacy_quality(h4, out)
    if frontier:
        fig6_frontier(frontier, args.local or (h5 if h5 else None), out)

    print(f"\nAll figures saved to {out}/")


if __name__ == "__main__":
    main()
