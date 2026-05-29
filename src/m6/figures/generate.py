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


def fig3_predicted_vs_empirical(h1h2_csv: str, out: Path, family: str = "c",
                                 compressor: str = "lingua2") -> None:
    """Figure 3: Theorem 1 validation — predicted vs empirical cliff.

    Default uses family-c × lingua2 because that's the regime where the curves
    actually differ in informative ways: empirical declines gradually
    (1.0 → 0.92 → 0.76 → 0.30 over r=4-8) while Theorem 1 predicts the cliff
    at r≈3.5 (too conservative). Family-a was the original choice but its
    empirical curve drops 1.0→0 in a single step (r=1→2), so both the
    empirical and predicted curves collapse onto the same step function and
    you can't see whether the theorem is right or wrong.
    """
    from m6.theory.cliff_prediction import (
        predicted_success_smooth,
        extract_token_recall_curve,
        q_required,
    )

    df = pd.read_csv(h1h2_csv)
    sub = df[(df["family"] == family) & (df["compressor"] == compressor)]
    if sub.empty:
        print(f"  [skip] fig3: no {compressor}/family-{family} data")
        return

    # Empirical curve
    agg = sub.groupby("ratio")["coord_success"].mean().reset_index()

    # Token recall curve
    tr_agg = sub.groupby("ratio")["token_recall"].mean().reset_index()
    tr_curve = list(zip(tr_agg["ratio"].tolist(), tr_agg["token_recall"].tolist()))

    # Predicted curve
    n_compression_passes, theta = 1, 0.5
    q_min = q_required(theta, n_compression_passes)
    predicted = predicted_success_smooth(tr_curve, n_compression_passes, theta, p0=1.0)

    family_labels = {"a": "Numeric Aggregation",
                     "b": "Constraint Planning",
                     "c": "Multi-Step Retrieval"}
    fam_lbl = family_labels.get(family, family)
    suptitle = f"Theorem 1 Validation — Family {family.upper()}: {fam_lbl} ({compressor})"

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Left: token recall + q_min threshold
    ax1.plot(tr_agg["ratio"], tr_agg["token_recall"], "s-", color="#1b9e77",
             label="Token Recall q(r)", markersize=5, linewidth=1.8)
    ax1.axhline(q_min, ls="--", color="red", alpha=0.7,
                label=f"q_min = {q_min:.2f}")
    # Shade the region where q < q_min (theorem predicts failure)
    tr_sorted = tr_agg.sort_values("ratio")
    ax1.fill_between(tr_sorted["ratio"], 0, q_min,
                     where=(tr_sorted["token_recall"] < q_min),
                     alpha=0.08, color="red", label="theorem: failure region")
    ax1.set_xlabel("Compression Ratio")
    ax1.set_ylabel("Token Recall q(r)")
    ax1.set_title("(a) Token Retention")
    ax1.legend(fontsize=8, loc="upper right")
    ax1.set_ylim(-0.05, 1.05)
    ax1.grid(True, alpha=0.2, linewidth=0.5)

    # Right: empirical vs predicted coordination success
    ax2.plot(agg["ratio"], agg["coord_success"], "o-", color="#7570b3",
             label="Empirical", markersize=6, linewidth=1.8)
    pred_r = [r for r, _ in predicted]
    pred_s = [s for _, s in predicted]
    ax2.plot(pred_r, pred_s, "x--", color="#d95f02",
             label="Predicted (Theorem 1)", markersize=7, linewidth=1.8)
    ax2.set_xlabel("Compression Ratio")
    ax2.set_ylabel("Coordination Success")
    ax2.set_title("(b) Predicted vs Empirical Cliff")
    ax2.legend(fontsize=9, loc="upper right")
    ax2.set_ylim(-0.05, 1.05)
    ax2.grid(True, alpha=0.2, linewidth=0.5)

    # Annotate the gap between theory and reality
    # find largest |empirical - predicted| gap
    pred_dict = dict(predicted)
    gaps = [(r, agg.loc[agg["ratio"] == r, "coord_success"].values[0] - pred_dict.get(r, 0))
            for r in agg["ratio"] if r in pred_dict]
    if gaps:
        rmax, gmax = max(gaps, key=lambda x: abs(x[1]))
        if abs(gmax) > 0.15:
            emp_y = agg.loc[agg["ratio"] == rmax, "coord_success"].values[0]
            # Place callout below the empirical point when it's near the top of
            # the axes (avoids overflowing ylim=1.05 and colliding with the
            # suptitle when bbox_inches="tight" expands the bounding box).
            x_max = agg["ratio"].max()
            text_x = min(rmax + 2.5, x_max - 0.5)
            if emp_y > 0.7:
                text_y = max(emp_y - 0.25, 0.20)
            else:
                text_y = min(emp_y + 0.15, 0.95)
            ax2.annotate(
                f"Theorem 1\nconservative\n(Δ={gmax:+.2f})" if gmax > 0
                else f"Theorem 1\noptimistic\n(Δ={gmax:+.2f})",
                xy=(rmax, emp_y),
                xytext=(text_x, text_y),
                fontsize=8, color="#444", ha="left",
                arrowprops=dict(arrowstyle="->", color="#777", lw=1),
            )

    fig.suptitle(suptitle, fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(out / "predicted_vs_empirical.pdf")
    fig.savefig(out / "predicted_vs_empirical.png")
    plt.close(fig)
    print(f"  fig3: {out / 'predicted_vs_empirical.pdf'}")


def fig4_caac_pareto(caac_csv: str, out: Path) -> None:
    """Figure 4: CAAC vs fixed-ratio operating regions, per family.

    Per ADR-007, CAAC is reframed as operating-point selection rather
    than Pareto dominance. The figure is a 3-panel per-family layout
    where each panel shows the (achieved_ratio, coord_success) trace
    of fixed-ratio compression (which traces a cliff curve) and CAAC's
    cluster (which tends to pack near min_ratio when q_min is tight,
    or extend along the high-coord shelf when CAAC successfully
    selects an operating point).

    Distinct colors per inner compressor (the audit flagged legend
    confusion in the prior figure where both "Fixed filter" and "Fixed
    lingua2" rendered in the same red).
    """
    df = pd.read_csv(caac_csv)
    if df.empty:
        print("  [skip] fig4: empty CAAC data")
        return

    families = sorted(df["family"].unique()) if "family" in df.columns else ["all"]
    # Map of per-family theta_q (load from caac CSV if present)
    fam_theta: dict[str, float | None] = {}
    if "theta_q" in df.columns:
        for fam in families:
            sub = df[(df["family"] == fam) & df["theta_q"].notna()]
            fam_theta[fam] = float(sub["theta_q"].iloc[0]) if not sub.empty else None
    inners = sorted(df["inner_compressor"].unique())

    # Distinct color per inner; CAAC vs fixed distinguished by marker
    palette = {
        "lingua2": "#1f77b4",   # blue
        "filter": "#d62728",    # red
        "phi3-extractive": "#2ca02c",  # green
        "truncation": "#9467bd",  # purple
    }

    n_panels = len(families)
    fig, axes = plt.subplots(1, n_panels, figsize=(4.2 * n_panels, 3.6),
                             sharey=True, squeeze=False)
    axes = axes[0]

    for ax_i, fam in enumerate(families):
        ax = axes[ax_i]
        sub_f = df[df["family"] == fam] if "family" in df.columns else df
        for inner in inners:
            color = palette.get(inner, "#444444")
            si = sub_f[sub_f["inner_compressor"] == inner]
            fixed = si[~si["is_caac"]]
            if not fixed.empty:
                fagg = fixed.groupby("target_ratio").agg(
                    coord=("coord_success", "mean"),
                    ratio=("achieved_ratio", "mean"),
                ).reset_index().sort_values("target_ratio")
                ax.plot(fagg["ratio"], fagg["coord"], "o-",
                        color=color, alpha=0.55, markersize=5,
                        label=f"Fixed {inner}")
            caac = si[si["is_caac"]]
            if not caac.empty:
                cagg = caac.groupby("target_ratio").agg(
                    coord=("coord_success", "mean"),
                    ratio=("achieved_ratio", "mean"),
                ).reset_index().sort_values("target_ratio")
                ax.plot(cagg["ratio"], cagg["coord"], "s",
                        color=color, markersize=8, markeredgecolor="black",
                        markeredgewidth=0.8,
                        label=f"CAAC({inner})")

        # Annotate per-family theta_q (the q_min CAAC enforces)
        theta = fam_theta.get(fam)
        if theta is not None:
            ax.text(0.98, 0.02, f"θ_q = {theta:.2f}",
                    transform=ax.transAxes, ha="right", va="bottom",
                    fontsize=9, alpha=0.85,
                    bbox={"facecolor": "white", "edgecolor": "gray",
                          "boxstyle": "round,pad=0.3", "alpha": 0.8})
        ax.set_xlabel("Achieved Compression Ratio")
        if ax_i == 0:
            ax.set_ylabel("Coordination Success")
        ax.set_title(f"Family {fam.upper()}")
        ax.set_ylim(-0.05, 1.08)
        ax.grid(alpha=0.25)

    # Single shared legend below the figure
    handles, labels = axes[0].get_legend_handles_labels()
    # Dedupe while preserving order
    seen: dict[str, Any] = {}
    for h, l in zip(handles, labels):
        if l not in seen:
            seen[l] = h
    fig.legend(seen.values(), list(seen.keys()),
               loc="lower center", ncol=min(len(seen), 4),
               bbox_to_anchor=(0.5, -0.04), fontsize=9, frameon=False)

    fig.suptitle("CAAC operating points vs fixed-ratio cliff curves (per family)",
                 fontsize=11, y=0.99)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(out / "caac_pareto.pdf", bbox_inches="tight")
    fig.savefig(out / "caac_pareto.png", bbox_inches="tight", dpi=160)
    plt.close(fig)
    print(f"  fig4: {out / 'caac_pareto.pdf'} (per-family operating-point layout)")


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
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylim(0, 1.12)
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
    short_name = model_name.split("/")[-1] if "/" in model_name else model_name
    ax.plot(agg["ratio"], agg["coord_success"], "o-", color=COLORS.get("GPT-4o-mini", "#e6ab02"),
            label=short_name, markersize=6)

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
    if len(models) >= 2 and fam_a.groupby("planner_model")["coord_success"].mean().max() > 0.1:
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
                aucs.append(float(np.trapezoid(agg.values, agg.index)))
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
# New figures: B1-B6 (thesis-specific)
# ============================================================================
def fig_hotpotqa_cliff(hotpotqa_csv: str, h1h2_csv: str | None, out: Path) -> None:
    """B1: HotpotQA cliff curve, overlaid with C1 family-a for comparison."""
    df = pd.read_csv(hotpotqa_csv)
    if df.empty:
        print("  [skip] hotpotqa_cliff: empty")
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    agg = df.groupby("ratio")["coord_success"].agg(["mean", "std", "count"]).reset_index()
    sem = agg["std"] / np.sqrt(agg["count"].clip(1))
    ax.plot(agg["ratio"], agg["mean"], "o-", color="#e7298a", label="HotpotQA", markersize=6)
    ax.fill_between(agg["ratio"], (agg["mean"] - 1.96 * sem).clip(0),
                     (agg["mean"] + 1.96 * sem).clip(0, 1), alpha=0.2, color="#e7298a")

    # Overlay C1 family-a if available
    if h1h2_csv and Path(h1h2_csv).exists():
        c1 = pd.read_csv(h1h2_csv)
        c1a = c1[(c1["family"] == "a") & (c1["compressor"] == "lingua2")]
        if not c1a.empty:
            c1agg = c1a.groupby("ratio")["coord_success"].mean().reset_index()
            ax.plot(c1agg["ratio"], c1agg["coord_success"], "s--", color="#1b9e77",
                    label="C1 Family-A", markersize=5, alpha=0.7)

    ax.set_xlabel("Compression Ratio")
    ax.set_ylabel("Coordination Success")
    ax.set_title("HotpotQA vs C1: Coordination Cliff Comparison")
    ax.legend()
    ax.set_ylim(-0.05, 1.05)
    fig.savefig(out / "hotpotqa_cliff.pdf")
    fig.savefig(out / "hotpotqa_cliff.png")
    plt.close(fig)
    print(f"  hotpotqa_cliff: {out / 'hotpotqa_cliff.pdf'}")


def fig_theta_density(out: Path) -> None:
    """B2: Theta estimates across tasks — Corollary 2 visualization."""
    import json

    # Collect theta estimates from verdict files
    tasks = []
    for vfile in sorted(Path("results").rglob("verdicts.json")):
        try:
            v = json.loads(vfile.read_text())
            if "theta_estimate" in v:
                name = v.get("dataset", vfile.parent.name)
                tasks.append({"task": name, "theta": v["theta_estimate"],
                              "baseline": v.get("baseline_coord", float("nan"))})
            # Pick up C1 family-A theta carried alongside other verdicts (e.g.
            # in hotpotqa_sweep/verdicts.json) so the bar chart compares
            # against the C1 reference even when no C1 verdict.json carries it.
            if "c1_family_a_theta" in v:
                tasks.append({"task": "C1-A", "theta": v["c1_family_a_theta"],
                              "baseline": float("nan")})
            if "task_theta" in v and isinstance(v["task_theta"], dict):
                tt = v["task_theta"]
                if "theta_estimate" in tt:
                    tasks.append({"task": tt.get("task", "unknown"), "theta": tt["theta_estimate"],
                                  "baseline": tt.get("baseline", float("nan"))})
                for fam, t in tt.get("c1_thetas", {}).items():
                    tasks.append({"task": f"C1-{fam}", "theta": t, "baseline": float("nan")})
        except Exception:
            continue

    if not tasks:
        print("  [skip] theta_density: no verdict files with theta")
        return

    # Deduplicate by task name, keep last; capitalize names
    seen = {}
    for t in tasks:
        # Capitalize task names for display
        name = t["task"]
        if name == name.lower() and "-" not in name:
            name = name.replace("_", " ").title()
        t["task"] = name
        seen[t["task"]] = t
    tasks = sorted(seen.values(), key=lambda t: t["theta"], reverse=True)

    fig, ax = plt.subplots(figsize=(7, 4))
    names = [t["task"] for t in tasks]
    thetas = [t["theta"] for t in tasks]
    colors = ["#d95f02" if "C1" in n else "#7570b3" for n in names]
    bars = ax.barh(range(len(names)), thetas, color=colors, alpha=0.85, edgecolor="white")
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.set_xlabel(r"$\theta$ (Information Density Estimate)")
    ax.set_title("Task Information Density (Corollary 2)")
    ax.set_xlim(0, 1.05)
    ax.axvline(0.5, ls=":", color="gray", alpha=0.3)
    ax.invert_yaxis()

    # Annotation
    ax.annotate("Dense tasks\n(cliff early)", xy=(0.9, 0.3), fontsize=8,
                color="#d95f02", ha="center", style="italic",
                xycoords="axes fraction")
    ax.annotate("Distributed tasks\n(cliff late)", xy=(0.3, 0.8), fontsize=8,
                color="#7570b3", ha="center", style="italic",
                xycoords="axes fraction")

    fig.tight_layout()
    fig.savefig(out / "theta_density.pdf")
    fig.savefig(out / "theta_density.png")
    plt.close(fig)
    print(f"  theta_density: {out / 'theta_density.pdf'}")


def fig_caac_theta_sensitivity(out: Path) -> None:
    """B3: CAAC coordination success across theta values."""
    import json

    # Collect from caac_theta_* and caac/ directories
    summaries = {}
    for d in sorted(Path("results").glob("caac*")):
        sfile = d / "summary.json"
        if not sfile.exists():
            continue
        name = d.name
        # Extract theta from dir name or default
        if "theta" in name:
            try:
                theta = float(name.split("theta_")[1])
            except (IndexError, ValueError):
                continue
        elif name == "caac":
            theta = 0.5  # default
        else:
            continue
        try:
            summary = json.loads(sfile.read_text())
            summaries[theta] = summary
        except Exception:
            continue

    if len(summaries) < 2:
        print(f"  [skip] caac_theta: only {len(summaries)} theta values found")
        return

    fig, ax = plt.subplots(figsize=(7, 4.5))
    theta_colors = {0.5: "#1b9e77", 0.6: "#d95f02", 0.7: "#7570b3", 0.8: "#e7298a"}

    for theta in sorted(summaries):
        summary = summaries[theta]
        # Use first inner compressor
        inner = next(iter(summary))
        ratios = []
        coords = []
        for r_str, data in summary[inner]["per_ratio"].items():
            ratios.append(float(r_str))
            coords.append(data["caac_coord"])
        if ratios:
            color = theta_colors.get(theta, "#333333")
            ax.plot(ratios, coords, "o-", color=color, label=f"θ={theta}", markersize=5)

    # Also plot fixed baseline from theta=0.5
    if 0.5 in summaries:
        s = summaries[0.5]
        inner = next(iter(s))
        ratios_f, coords_f = [], []
        for r_str, data in s[inner]["per_ratio"].items():
            ratios_f.append(float(r_str))
            coords_f.append(data["fixed_coord"])
        if ratios_f:
            ax.plot(ratios_f, coords_f, "x--", color="#d62728", label="Fixed (no CAAC)",
                    markersize=5, alpha=0.6)

    ax.set_xlabel("Target Compression Ratio")
    ax.set_ylabel("Coordination Success")
    ax.set_title("CAAC Sensitivity to θ Threshold")
    ax.legend()
    ax.set_ylim(-0.05, 1.05)
    fig.tight_layout()
    fig.savefig(out / "caac_theta_sensitivity.pdf")
    fig.savefig(out / "caac_theta_sensitivity.png")
    plt.close(fig)
    print(f"  caac_theta: {out / 'caac_theta_sensitivity.pdf'}")


def fig_caac_n_sensitivity(out: Path) -> None:
    """B4: CAAC coordination success across N (compression passes) values."""
    import json

    summaries = {}
    for d in sorted(Path("results").glob("caac*")):
        sfile = d / "summary.json"
        if not sfile.exists():
            continue
        name = d.name
        if name.startswith("caac_N_"):
            try:
                n_val = int(name.split("N_")[1])
            except (IndexError, ValueError):
                continue
        elif name == "caac":
            n_val = 1
        else:
            continue
        try:
            summaries[n_val] = json.loads(sfile.read_text())
        except Exception:
            continue

    if len(summaries) < 2:
        print(f"  [skip] caac_n: only {len(summaries)} N values found")
        return

    fig, ax = plt.subplots(figsize=(7, 4.5))
    n_colors = {1: "#1b9e77", 2: "#d95f02", 3: "#7570b3", 4: "#e7298a", 5: "#e6ab02"}

    for n_val in sorted(summaries):
        summary = summaries[n_val]
        inner = next(iter(summary))
        ratios, coords = [], []
        for r_str, data in summary[inner]["per_ratio"].items():
            ratios.append(float(r_str))
            coords.append(data["caac_coord"])
        if ratios:
            color = n_colors.get(n_val, "#333333")
            ax.plot(ratios, coords, "o-", color=color, label=f"N={n_val}", markersize=5)

    ax.set_xlabel("Target Compression Ratio")
    ax.set_ylabel("Coordination Success")
    ax.set_title("CAAC Sensitivity to N (Compression Passes)")
    ax.legend()
    ax.set_ylim(-0.05, 1.05)
    fig.tight_layout()
    fig.savefig(out / "caac_n_sensitivity.pdf")
    fig.savefig(out / "caac_n_sensitivity.png")
    plt.close(fig)
    print(f"  caac_n: {out / 'caac_n_sensitivity.pdf'}")


def fig_frontier_multi(out: Path) -> None:
    """B5: All frontier models overlaid on same axes."""
    frontier_dirs = sorted(Path("results").glob("frontier_*"))
    if not frontier_dirs:
        print("  [skip] frontier_multi: no frontier dirs")
        return

    fig, ax = plt.subplots(figsize=(7, 4.5))
    model_colors = ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#e6ab02"]
    color_idx = 0

    for d in frontier_dirs:
        csv = d / "results.csv"
        if not csv.exists() or "smoke" in d.name:
            continue
        df = pd.read_csv(csv)
        if df.empty:
            continue
        model = df["model"].iloc[0]
        # Skip duplicate versions (use v2 if exists)
        agg = df.groupby("ratio")["coord_success"].mean().reset_index()
        color = model_colors[color_idx % len(model_colors)]
        # Shorten model name for legend
        short_name = model.split("/")[-1] if "/" in model else model
        ax.plot(agg["ratio"], agg["coord_success"], "o-", color=color,
                label=short_name, markersize=5)
        color_idx += 1

    # Overlay local 8B if H5 exists
    h5_hits = sorted(Path("results").rglob("h5*/results.csv"))
    if h5_hits:
        h5 = pd.read_csv(h5_hits[-1])
        h5a = h5[(h5["family"] == "a") & (h5["planner_model"] == "8B")]
        if not h5a.empty:
            agg = h5a.groupby("ratio")["coord_success"].mean().reset_index()
            ax.plot(agg["ratio"], agg["coord_success"], "s--", color="#666666",
                    label="Llama-3.1-8B (local)", markersize=4, alpha=0.6)

    ax.set_xlabel("Compression Ratio")
    ax.set_ylabel("Coordination Success")
    ax.set_title("Frontier Model Cliff Comparison")
    ax.legend(fontsize=8)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.15, linewidth=0.5)
    fig.tight_layout()
    fig.savefig(out / "frontier_multi.pdf")
    fig.savefig(out / "frontier_multi.png")
    plt.close(fig)
    print(f"  frontier_multi: {out / 'frontier_multi.pdf'}")


def fig_h3_pipelines(h3_csv: str, out: Path) -> None:
    """B6: H3 RAG pipeline comparison — grouped bar chart."""
    df = pd.read_csv(h3_csv)
    if df.empty or "pipeline" not in df.columns:
        print("  [skip] h3_pipelines: empty or no pipeline column")
        return

    # Use f1 as the metric (H3 doesn't have coord_success)
    metric = "coord_success" if "coord_success" in df.columns else "f1"

    # Detect regime values: may be "storage_bounded"/"accuracy_bounded" or "storage"/"accuracy"
    if "regime" in df.columns:
        regimes = sorted(df["regime"].unique())
    else:
        regimes = ["all"]

    fig, axes = plt.subplots(1, len(regimes), figsize=(5 * len(regimes), 4.5), squeeze=False)
    axes = axes[0]
    pipeline_colors = {"P1": "#1b9e77", "P2": "#d95f02", "P3": "#7570b3"}

    for idx, regime in enumerate(regimes):
        ax = axes[idx]
        sub = df[df["regime"] == regime] if regime != "all" else df
        if sub.empty:
            continue

        compressors = sorted(sub["compressor"].unique())
        pipelines = sorted(sub["pipeline"].unique())
        x = np.arange(len(compressors))
        width = 0.7 / max(len(pipelines), 1)
        offsets = np.linspace(-width * (len(pipelines) - 1) / 2,
                               width * (len(pipelines) - 1) / 2, len(pipelines))

        for offset, pipe in zip(offsets, pipelines):
            vals = [float(sub[(sub["compressor"] == c) & (sub["pipeline"] == pipe)][metric].mean())
                    for c in compressors]
            color = pipeline_colors.get(pipe, "#333333")
            ax.bar(x + offset, vals, width, label=pipe, color=color, alpha=0.85)

        ax.set_xlabel("Compressor")
        ax.set_ylabel("Content F1" if metric == "f1" else "Coordination Success")
        # Clean up regime name for title
        regime_label = regime.replace("_bounded", "").replace("_", " ").title()
        ax.set_title(f"Pipeline Comparison ({regime_label} Regime)")
        ax.set_xticks(x)
        ax.set_xticklabels(compressors, rotation=15)
        ax.set_ylim(0, max(0.3, sub[metric].max() * 1.15) if not sub[metric].isna().all() else 1.05)
        if idx == 0:
            ax.legend()

    fig.tight_layout()
    fig.savefig(out / "h3_pipelines.pdf")
    fig.savefig(out / "h3_pipelines.png")
    plt.close(fig)
    print(f"  h3_pipelines: {out / 'h3_pipelines.pdf'}")


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

    # Auto-discover results if not specified.
    #
    # Resolution order:
    #   1. Match in a parent dir whose name contains "_final" (e.g. h5_final/).
    #   2. Match outside obvious dev/smoke dirs (smoke, micro, diag, quick, etc.).
    #   3. Alphabetical-last match.
    #
    # For ambiguous globs (e.g. "caac*/results.csv" where both caac/ and
    # caac_theta_X/ exist), pass an explicit path via the CLI (--caac, --frontier, ...).
    _SKIP_TOKENS = ("smoke", "micro", "diag", "quick", "short",
                    "bt_", "sanity", "cache_test", "deep_")

    def _find(pattern: str) -> str | None:
        hits = sorted(Path("results").rglob(pattern))
        if not hits:
            return None
        final = [h for h in hits if "_final" in h.parent.name]
        if final:
            return str(final[-1])
        good = [h for h in hits if not any(t in h.parent.name for t in _SKIP_TOKENS)]
        return str((good or hits)[-1])

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

    # New thesis figures (B1-B6)
    hotpotqa = _find("hotpotqa*/results.csv")
    h3 = _find("h3*/results.csv")
    if hotpotqa:
        fig_hotpotqa_cliff(hotpotqa, h1h2, out)
    fig_theta_density(out)
    fig_caac_theta_sensitivity(out)
    fig_caac_n_sensitivity(out)
    fig_frontier_multi(out)
    if h3:
        fig_h3_pipelines(h3, out)

    print(f"\nAll figures saved to {out}/")


if __name__ == "__main__":
    main()
