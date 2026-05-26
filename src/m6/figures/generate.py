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
    n_compression_passes, theta = 1, 0.5
    q_min = q_required(theta, n_compression_passes)
    predicted = predicted_success_smooth(tr_curve, n_compression_passes, theta, p0=1.0)

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
# Novelty figures (neurips_novelty_plan.md Ideas 2 & 3)
# ============================================================================
def fig_pareto_privacy_coordination(h1h2_csv: str, h4_csv: str, out: Path) -> None:
    """Privacy-coordination Pareto frontier (Idea 2).

    Each compressor is a point: x = coord_success at ratio=4x,
    y = disclosure reduction (baseline - compressed recovery rate).
    Shows the tradeoff: aggressive compression improves privacy but hurts coordination.
    """
    df1 = pd.read_csv(h1h2_csv)
    df4 = pd.read_csv(h4_csv)
    if df1.empty or df4.empty:
        print("  [skip] pareto: empty data")
        return
    if "has_error" in df4.columns:
        df4 = df4[~df4["has_error"]]

    fig, ax = plt.subplots(figsize=(6, 5))

    compressors = sorted(set(df1["compressor"].unique()) & set(df4["compressor"].unique()))

    for comp in compressors:
        # Coord success at multiple ratios
        c1 = df1[df1["compressor"] == comp]
        # Disclosure reduction from H4
        c4 = df4[df4["compressor"] == comp]
        baseline_rate = float(c4["baseline_correct"].mean())
        compressed_rate = float(c4["compressed_correct"].mean())
        disclosure_reduction = baseline_rate - compressed_rate

        # Plot points at ratios 2x, 4x, 8x
        for ratio in [2.0, 4.0, 8.0]:
            sub = c1[c1["ratio"] == ratio]
            if sub.empty:
                continue
            coord = float(sub["coord_success"].mean())
            color = COLORS.get(comp, "#333333")
            marker = "o" if ratio == 4.0 else ("^" if ratio == 2.0 else "s")
            size = 100 if ratio == 4.0 else 60
            ax.scatter(coord, disclosure_reduction, c=color, marker=marker,
                       s=size, zorder=5, edgecolors="white", linewidths=0.5)

        # Label at ratio=4x
        sub4 = c1[c1["ratio"] == 4.0]
        if not sub4.empty:
            coord4 = float(sub4["coord_success"].mean())
            ax.annotate(comp, (coord4, disclosure_reduction),
                        textcoords="offset points", xytext=(8, 4),
                        fontsize=8, color=COLORS.get(comp, "#333333"))

    ax.set_xlabel("Coordination Success")
    ax.set_ylabel("Disclosure Reduction (pp)")
    ax.set_title("Privacy–Coordination Tradeoff")
    ax.set_xlim(-0.05, 1.05)
    # Set y-axis from data range with margin
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(min(-0.05, ymin - 0.05), max(0.6, ymax + 0.1))
    # Ideal corner annotation relative to actual axis
    ax.annotate("ideal\n(high coord,\nhigh privacy)",
                xy=(0.95, ax.get_ylim()[1] * 0.85), fontsize=7, color="gray",
                ha="center", style="italic")

    # Legend for marker shapes
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="^", color="gray", linestyle="None", markersize=6, label="2x"),
        Line2D([0], [0], marker="o", color="gray", linestyle="None", markersize=8, label="4x"),
        Line2D([0], [0], marker="s", color="gray", linestyle="None", markersize=6, label="8x"),
    ]
    ax.legend(handles=legend_elements, title="Ratio", loc="upper left", fontsize=8)

    fig.savefig(out / "pareto_privacy_coordination.pdf")
    fig.savefig(out / "pareto_privacy_coordination.png")
    plt.close(fig)
    print(f"  pareto: {out / 'pareto_privacy_coordination.pdf'}")


def fig_compressor_fingerprints(h1h2_csv: str, out: Path, ctr_csv: str | None = None) -> None:
    """Compressor fingerprints — q(r) curves per compressor (Idea 3).

    Shows token_recall curves (solid) and critical_token_recall curves (dashed)
    for each compressor, averaged across families. Annotates predicted tau*
    from the theorem at theta=0.5.
    """
    df = pd.read_csv(h1h2_csv)
    if df.empty:
        print("  [skip] fingerprints: empty data")
        return

    # Load critical token recall if available
    ctr_df = None
    if ctr_csv and Path(ctr_csv).exists():
        ctr_df = pd.read_csv(ctr_csv)

    from m6.theory.cliff_prediction import predicted_tau

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    families = ["a", "b", "c"]
    family_labels = {"a": "Family A (Aggregation)", "b": "Family B (Constraints)", "c": "Family C (Chain)"}
    theta = 0.5

    for idx, fam in enumerate(families):
        ax = axes[idx]
        ax.set_title(family_labels[fam], fontsize=11)

        for comp in sorted(df["compressor"].unique()):
            color = COLORS.get(comp, "#333333")
            sub = df[(df["compressor"] == comp) & (df["family"] == fam)]
            if sub.empty:
                continue
            tr = sub.groupby("ratio")["token_recall"].mean().sort_index()
            ax.plot(tr.index, tr.values, "o-", color=color, label=comp,
                    markersize=4, linewidth=1.5)

            # Predicted tau
            curve = list(zip(tr.index.tolist(), tr.values.tolist()))
            tau = predicted_tau(curve, n_compression_passes=1, theta=theta)
            if np.isfinite(tau) and tau <= 16:
                ax.axvline(tau, color=color, linestyle=":", alpha=0.4, linewidth=1)

            # Critical token recall (dashed)
            if ctr_df is not None:
                csub = ctr_df[(ctr_df["compressor"] == comp) & (ctr_df["family"] == fam)]
                if not csub.empty:
                    ctr_agg = csub.groupby("ratio")["critical_token_recall"].mean().dropna().sort_index()
                    if not ctr_agg.empty:
                        ax.plot(ctr_agg.index, ctr_agg.values, "x--", color=color,
                                markersize=4, linewidth=1, alpha=0.6)

        # Theta line
        ax.axhline(theta, color="red", linestyle="--", alpha=0.3, linewidth=1)
        ax.text(15.5, theta + 0.02, f"θ={theta}", color="red", fontsize=7, alpha=0.5, ha="right")

        ax.set_xlabel("Compression Ratio")
        if idx == 0:
            ax.set_ylabel("Token Recall q(r)")
        ax.set_xlim(0.5, 16.5)
        ax.set_ylim(-0.05, 1.05)

    # Single legend for all subplots
    handles, labels = axes[0].get_legend_handles_labels()
    # Add dashed line to legend if CTR exists
    if ctr_df is not None:
        from matplotlib.lines import Line2D
        handles.append(Line2D([0], [0], linestyle="--", color="gray", marker="x", markersize=4, label="critical recall"))
        labels.append("critical recall")
    fig.legend(handles, labels, loc="upper center", ncol=len(handles),
               bbox_to_anchor=(0.5, 1.02), fontsize=8)

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(out / "compressor_fingerprints.pdf")
    fig.savefig(out / "compressor_fingerprints.png")
    plt.close(fig)
    print(f"  fingerprints: {out / 'compressor_fingerprints.pdf'}")


# ============================================================================
# Additional figures (publication_guide.md + experiment_plan.md)
# ============================================================================
def fig_h1_scatter(h1h2_csv: str, out: Path) -> None:
    """H1 scatter: delta_qa vs delta_coord, colored by compressor."""
    df = pd.read_csv(h1h2_csv)
    if df.empty:
        print("  [skip] h1_scatter: empty")
        return

    families = sorted(df["family"].unique())
    compressors = sorted(df["compressor"].unique())
    fig, axes = plt.subplots(1, len(families), figsize=(4.5 * len(families), 4), sharey=True)
    if len(families) == 1:
        axes = [axes]

    for ax, fam in zip(axes, families):
        fam_df = df[df["family"] == fam]
        for comp in compressors:
            sub = fam_df[fam_df["compressor"] == comp]
            agg = sub.groupby(["workload_id", "ratio"]).agg(
                qa_f1=("qa_f1", "first"),
                coord_success=("coord_success", "mean"),
            ).reset_index()
            ref = agg[agg["ratio"] == 1.0][["workload_id", "qa_f1", "coord_success"]]
            ref = ref.rename(columns={"qa_f1": "qa_ref", "coord_success": "coord_ref"})
            merged = agg.merge(ref, on="workload_id", how="left")
            merged = merged[merged["ratio"] != 1.0].dropna()
            if merged.empty:
                continue
            dqa = merged["qa_f1"] - merged["qa_ref"]
            dcoord = merged["coord_success"] - merged["coord_ref"]
            color = COLORS.get(comp, "#333333")
            ax.scatter(dqa, dcoord, c=color, label=comp, alpha=0.5, s=15)
        ax.set_xlabel(r"$\Delta$ Info Preservation")
        ax.set_title(f"Family {fam.upper()}")
        ax.axhline(0, ls=":", color="gray", alpha=0.3)
        ax.axvline(0, ls=":", color="gray", alpha=0.3)
        if fam == families[0]:
            ax.set_ylabel(r"$\Delta$ Coordination Success")
            ax.legend(fontsize=7)

    fig.suptitle("H1: Information Preservation vs Coordination (decorrelated)", fontsize=12)
    fig.tight_layout()
    fig.savefig(out / "h1_scatter.pdf")
    fig.savefig(out / "h1_scatter.png")
    plt.close(fig)
    print(f"  h1_scatter: {out / 'h1_scatter.pdf'}")


def fig_h5_model_overlay(h5_csv: str, out: Path) -> None:
    """H5 model-size overlay: 4 models on family-a, showing ceiling not cliff."""
    df = pd.read_csv(h5_csv)
    fam_a = df[df["family"] == "a"]
    if fam_a.empty:
        print("  [skip] h5_overlay: no family-a")
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    models = sorted(fam_a["planner_model"].unique(), key=lambda m: float(m.replace("B", "")))
    for model in models:
        sub = fam_a[fam_a["planner_model"] == model]
        agg = sub.groupby("ratio")["coord_success"].mean().reset_index()
        color = COLORS.get(model, "#333333")
        ax.plot(agg["ratio"], agg["coord_success"], "o-", color=color, label=model, markersize=5)

    ax.set_xlabel("Compression Ratio")
    ax.set_ylabel("Coordination Success")
    ax.set_title("Model Size Affects Ceiling, Not Cliff Position")
    ax.legend(title="Planner")
    ax.set_ylim(-0.05, 1.05)
    ax.annotate("Same cliff position\n(all models ~3-4x)",
                xy=(3.5, 0.15), fontsize=9, color="red", ha="center",
                arrowprops=dict(arrowstyle="->", color="red"),
                xytext=(6, 0.4))
    fig.savefig(out / "h5_model_overlay.pdf")
    fig.savefig(out / "h5_model_overlay.png")
    plt.close(fig)
    print(f"  h5_overlay: {out / 'h5_model_overlay.pdf'}")


def fig_scaling_auc(h5_csv: str, out: Path) -> None:
    """Scaling: AUC bar chart + cliff position comparison (Idea 7).

    Shows that AUC (coordination quality) scales with model size,
    but cliff position (tau*) does NOT.
    """
    df = pd.read_csv(h5_csv)
    if df.empty:
        print("  [skip] scaling_auc: empty")
        return

    models = sorted(df["planner_model"].unique(), key=lambda m: float(m.replace("B", "")))
    families = [f for f in ["a", "c"] if f in df["family"].unique()]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    # Left: AUC per model per family
    ax = axes[0]
    x = np.arange(len(models))
    n_fam = len(families)
    width = 0.7 / max(n_fam, 1)
    offsets = np.linspace(-width * (n_fam - 1) / 2, width * (n_fam - 1) / 2, n_fam) if n_fam > 1 else [0.0]
    for offset, fam in zip(offsets, families):
        aucs = []
        for m in models:
            sub = df[(df["planner_model"] == m) & (df["family"] == fam)]
            agg = sub.groupby("ratio")["coord_success"].mean().sort_index()
            if len(agg) >= 2:
                aucs.append(float(np.trapz(agg.values, agg.index)))
            else:
                aucs.append(0.0)
        ax.bar(x + offset, aucs, width, label=f"Family {fam.upper()}", alpha=0.85)
    ax.set_xlabel("Planner Model")
    ax.set_ylabel("AUC (Coordination Quality)")
    ax.set_title("Ceiling Scales with Model Size")
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()

    # Right: cliff curves overlaid (family-a)
    ax = axes[1]
    fam_a = df[df["family"] == "a"]
    if not fam_a.empty:
        for m in models:
            sub = fam_a[fam_a["planner_model"] == m]
            agg = sub.groupby("ratio")["coord_success"].mean().sort_index()
            color = COLORS.get(m, "#333333")
            ax.plot(agg.index, agg.values, "o-", color=color, label=m, markersize=5)
        ax.axhline(0.5, ls="--", color="red", alpha=0.3)
        ax.text(14, 0.53, "θ=0.5", color="red", fontsize=8, alpha=0.5)
    ax.set_xlabel("Compression Ratio")
    ax.set_ylabel("Coordination Success")
    ax.set_title("Cliff Position Is Model-Invariant")
    ax.legend(title="Planner")
    ax.set_ylim(-0.05, 1.05)

    fig.tight_layout()
    fig.savefig(out / "scaling_auc.pdf")
    fig.savefig(out / "scaling_auc.png")
    plt.close(fig)
    print(f"  scaling_auc: {out / 'scaling_auc.pdf'}")


def fig_caac_ablation(caac_csv: str, out: Path) -> None:
    """CAAC ablation: coord_success vs target_ratio for fixed vs CAAC."""
    df = pd.read_csv(caac_csv)
    if df.empty:
        print("  [skip] caac_ablation: empty")
        return

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Left: coord success comparison
    ax = axes[0]
    for inner in sorted(df["inner_compressor"].unique()):
        sub = df[df["inner_compressor"] == inner]
        fixed = sub[~sub["is_caac"]].groupby("target_ratio")["coord_success"].mean()
        caac = sub[sub["is_caac"]].groupby("target_ratio")["coord_success"].mean()
        ax.plot(fixed.index, fixed.values, "o--", color=COLORS["fixed"], alpha=0.6, label=f"Fixed {inner}")
        if not caac.empty:
            ax.plot(caac.index, caac.values, "s-", color=COLORS["caac"], label=f"CAAC({inner})")
    ax.set_xlabel("Target Compression Ratio")
    ax.set_ylabel("Coordination Success")
    ax.set_title("CAAC vs Fixed: Coordination")
    ax.legend(fontsize=8)
    ax.set_ylim(-0.05, 1.05)

    # Right: achieved ratio comparison
    ax = axes[1]
    for inner in sorted(df["inner_compressor"].unique()):
        sub = df[df["inner_compressor"] == inner]
        fixed = sub[~sub["is_caac"]].groupby("target_ratio")["achieved_ratio"].mean()
        caac = sub[sub["is_caac"]].groupby("target_ratio")["achieved_ratio"].mean()
        ax.plot(fixed.index, fixed.values, "o--", color=COLORS["fixed"], alpha=0.6, label=f"Fixed {inner}")
        if not caac.empty:
            ax.plot(caac.index, caac.values, "s-", color=COLORS["caac"], label=f"CAAC({inner})")
    ax.plot([1, 16], [1, 16], ":", color="gray", alpha=0.3, label="Target=Achieved")
    ax.set_xlabel("Target Compression Ratio")
    ax.set_ylabel("Achieved Compression Ratio")
    ax.set_title("CAAC vs Fixed: Achieved Ratio")
    ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(out / "caac_ablation.pdf")
    fig.savefig(out / "caac_ablation.png")
    plt.close(fig)
    print(f"  caac_ablation: {out / 'caac_ablation.pdf'}")


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
        fig_h5_model_overlay(h5, out)
        fig_scaling_auc(h5, out)
    if h1h2:
        fig2_cliff_families(h1h2, out)
        fig3_predicted_vs_empirical(h1h2, out)
        fig_h1_scatter(h1h2, out)
        ctr_csv = _find("critical_token_recall_fixed.csv")
        fig_compressor_fingerprints(h1h2, out, ctr_csv=ctr_csv)
    if h1h2 and h4:
        fig_pareto_privacy_coordination(h1h2, h4, out)
    if caac:
        fig4_caac_pareto(caac, out)
        fig_caac_ablation(caac, out)
    if h4:
        fig5_privacy_quality(h4, out)
    if frontier:
        fig6_frontier(frontier, args.local or (h5 if h5 else None), out)

    print(f"\nAll figures saved to {out}/")


if __name__ == "__main__":
    main()
