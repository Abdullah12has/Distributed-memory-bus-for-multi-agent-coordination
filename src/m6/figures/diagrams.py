#!/usr/bin/env python3
"""Generate conceptual/architecture diagrams for the thesis.

Produces 6 diagrams using matplotlib patches and arrows:
  C1. architecture_overview.pdf  — System architecture
  C2. caac_flowchart.pdf         — CAAC algorithm flowchart
  C3. cliff_mechanism.pdf        — Coordination cliff mechanism
  C4. corollary_visual.pdf       — Corollary 1 & 2 illustration
  C5. rag_pipelines.pdf          — RAG pipeline placements (P1/P2/P3)
  C6. compressor_overview.pdf    — Compressor comparison

Usage:
    python -m m6.figures.diagrams --out figures/
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Consistent style
plt.rcParams.update({
    "font.size": 10,
    "font.family": "sans-serif",
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})

# Color palette
C_PRIMARY = "#2c3e50"
C_ACCENT1 = "#1b9e77"
C_ACCENT2 = "#d95f02"
C_ACCENT3 = "#7570b3"
C_ACCENT4 = "#e7298a"
C_LIGHT = "#ecf0f1"
C_MID = "#bdc3c7"
C_RED = "#e74c3c"
C_GREEN = "#27ae60"
C_BLUE = "#3498db"


def _box(ax, x, y, w, h, text, color=C_LIGHT, edge=C_PRIMARY, fontsize=9,
         bold=False, alpha=1.0):
    """Draw a rounded box with centered text."""
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle="round,pad=0.1", facecolor=color,
                          edgecolor=edge, linewidth=1.2, alpha=alpha)
    ax.add_patch(box)
    weight = "bold" if bold else "normal"
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            fontweight=weight, color=C_PRIMARY)
    return box


def _arrow(ax, x1, y1, x2, y2, color=C_PRIMARY, style="->", lw=1.2):
    """Draw an arrow between two points."""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw))


def _arrow_label(ax, x1, y1, x2, y2, label, color=C_PRIMARY, fontsize=7):
    """Draw an arrow with a label at the midpoint."""
    _arrow(ax, x1, y1, x2, y2, color=color)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(mx + 0.15, my, label, fontsize=fontsize, color=color, ha="left", va="center")


# ============================================================================
# C1: System Architecture Overview
# ============================================================================
def c1_architecture_overview(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("System Architecture: Distributed Memory Bus", fontsize=13,
                 fontweight="bold", pad=15)

    # Data sources (left)
    _box(ax, 1.3, 5.5, 2.2, 0.7, "Data Sources\n(Fragments)", color="#d5e8d4", bold=True)
    for i, label in enumerate(["Agent A", "Agent B", "Agent C"]):
        _box(ax, 1.3, 4.3 - i * 0.8, 1.6, 0.55, label, color="#dae8fc", fontsize=8)

    # Memory Bus (center)
    bus = FancyBboxPatch((3.2, 1.8), 3.6, 3.7, boxstyle="round,pad=0.15",
                          facecolor="#fff2cc", edgecolor=C_ACCENT2, linewidth=2)
    ax.add_patch(bus)
    ax.text(5.0, 5.2, "Memory Bus", ha="center", va="center", fontsize=12,
            fontweight="bold", color=C_ACCENT2)

    # Bus internals
    _box(ax, 5.0, 4.3, 2.8, 0.55, "Compressor (LLMLingua-2 / CAAC)", color="#ffe6cc", fontsize=8)
    _box(ax, 5.0, 3.5, 2.8, 0.55, "Tag Vector (ACL + Provenance)", color="#ffe6cc", fontsize=8)
    _box(ax, 5.0, 2.7, 2.8, 0.55, "Compressed Slots", color="#ffe6cc", fontsize=8)
    _box(ax, 5.0, 2.0, 2.8, 0.45, "Audit Chain (append-only)", color="#ffe6cc", fontsize=7)

    # Planner-Worker-Critic (right)
    _box(ax, 8.5, 5.0, 2.4, 0.65, "Planner", color="#e1d5e7", bold=True)
    _box(ax, 8.5, 3.8, 2.4, 0.65, "Workers (1..N)", color="#e1d5e7", bold=True)
    _box(ax, 8.5, 2.6, 2.4, 0.65, "Critic", color="#e1d5e7", bold=True)

    # Output
    _box(ax, 8.5, 1.2, 2.4, 0.65, "Coordination\nOutput", color="#d5e8d4", bold=True)

    # Arrows: sources → bus
    for i in range(3):
        _arrow(ax, 2.1, 4.3 - i * 0.8, 3.3, 3.5)
    _arrow(ax, 2.4, 5.5, 3.3, 4.3)

    # Arrows: bus → agents
    _arrow(ax, 7.0, 4.3, 7.3, 5.0)
    _arrow(ax, 7.0, 3.5, 7.3, 3.8)

    # Arrows: planner → workers → critic → output
    _arrow(ax, 8.5, 4.65, 8.5, 4.15)
    _arrow(ax, 8.5, 3.45, 8.5, 2.95)
    _arrow(ax, 8.5, 2.25, 8.5, 1.55)

    # Labels
    ax.text(3.0, 5.0, "write", fontsize=8, color=C_ACCENT2, style="italic",
            fontweight="bold", ha="center")
    ax.text(7.15, 4.65, "read\n(compressed)", fontsize=8, color=C_ACCENT3, style="italic",
            fontweight="bold", ha="center")

    fig.savefig(out / "architecture_overview.pdf")
    fig.savefig(out / "architecture_overview.png")
    plt.close(fig)
    print(f"  C1: {out / 'architecture_overview.pdf'}")


# ============================================================================
# C2: CAAC Algorithm Flowchart
# ============================================================================
def c2_caac_flowchart(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 8))
    ax.set_xlim(-0.3, 7.3)
    ax.set_ylim(0, 8.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("CAAC: Cliff-Aware Adaptive Compression", fontsize=13,
                 fontweight="bold", pad=15)

    # Start (wider box to fit full label without cropping)
    _box(ax, 3.5, 7.8, 3.6, 0.55, "Input: fragment, target_ratio, θ", color="#d5e8d4", bold=True)

    # Step 1
    _arrow(ax, 3.5, 7.5, 3.5, 7.1)
    _box(ax, 3.5, 6.8, 3.0, 0.55, "Compress at target_ratio", color="#dae8fc")

    # Step 2
    _arrow(ax, 3.5, 6.5, 3.5, 6.1)
    _box(ax, 3.5, 5.8, 3.0, 0.55, "Measure token_recall q", color="#dae8fc")

    # Decision
    _arrow(ax, 3.5, 5.5, 3.5, 5.0)
    diamond = plt.Polygon([[3.5, 5.0], [5.0, 4.3], [3.5, 3.6], [2.0, 4.3]],
                           facecolor="#fff2cc", edgecolor=C_PRIMARY, linewidth=1.2)
    ax.add_patch(diamond)
    ax.text(3.5, 4.3, "q ≥ θ ?", ha="center", va="center", fontsize=10, fontweight="bold")

    # Yes branch (right)
    ax.annotate("", xy=(6.0, 4.3), xytext=(5.0, 4.3),
                arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.5))
    ax.text(5.3, 4.5, "Yes", fontsize=9, color=C_GREEN, fontweight="bold")
    _box(ax, 6.0, 4.3, 1.4, 0.55, "Accept\n(safe)", color="#d5e8d4", fontsize=9)

    # No branch (down)
    ax.annotate("", xy=(3.5, 3.0), xytext=(3.5, 3.6),
                arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.5))
    ax.text(3.7, 3.35, "No", fontsize=9, color=C_RED, fontweight="bold")

    # Binary search
    _box(ax, 3.5, 2.7, 3.2, 0.55, "Binary search: find max ratio\nwhere q ≥ θ", color="#f8cecc")

    # Min ratio check
    _arrow(ax, 3.5, 2.4, 3.5, 1.9)
    _box(ax, 3.5, 1.6, 3.2, 0.55, "Floor: ratio ≥ min_ratio (1.5×)", color="#f8cecc", fontsize=8)

    # Output
    _arrow(ax, 3.5, 1.3, 3.5, 0.8)
    _arrow(ax, 6.0, 3.7, 6.0, 0.5)  # Yes path down
    _arrow(ax, 6.0, 0.5, 4.7, 0.5)  # Yes path left to output
    _box(ax, 3.5, 0.5, 3.8, 0.7, "Output: compressed text +\nachieved_ratio", color="#d5e8d4", bold=True)

    fig.savefig(out / "caac_flowchart.pdf")
    fig.savefig(out / "caac_flowchart.png")
    plt.close(fig)
    print(f"  C2: {out / 'caac_flowchart.pdf'}")


# ============================================================================
# C3: Coordination Cliff Mechanism
# ============================================================================
def c3_cliff_mechanism(out: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Left: Token recall curve
    r = np.linspace(1, 16, 200)
    q = np.clip(1.0 / (1 + 0.15 * (r - 1) ** 1.3), 0, 1)
    theta = 0.5
    r_star = r[np.argmin(np.abs(q - theta))]

    ax1.plot(r, q, "-", color=C_ACCENT1, linewidth=2.5, label="Token recall q(r)")
    ax1.axhline(theta, ls="--", color=C_RED, alpha=0.7, linewidth=1.5, label=f"θ = {theta}")
    ax1.axvline(r_star, ls=":", color=C_PRIMARY, alpha=0.5, linewidth=1)
    ax1.fill_between(r, theta, q, where=(q >= theta), color=C_ACCENT1, alpha=0.1)
    ax1.fill_between(r, 0, q, where=(q < theta), color=C_RED, alpha=0.08)
    ax1.text(r_star / 2, theta + 0.15, "Sufficient\ninformation", fontsize=8,
             color=C_ACCENT1, ha="center", style="italic")
    ax1.text(r_star + 2, theta / 2, "Critical\ninfo lost", fontsize=8,
             color=C_RED, ha="center", style="italic")
    ax1.annotate(f"r* ≈ {r_star:.1f}", xy=(r_star, theta), xytext=(r_star + 2.5, theta + 0.2),
                 fontsize=9, arrowprops=dict(arrowstyle="->", color=C_PRIMARY),
                 fontweight="bold")
    ax1.set_xlabel("Compression Ratio r")
    ax1.set_ylabel("Token Recall q(r)")
    ax1.set_title("(a) Information Retention", fontweight="bold")
    ax1.set_ylim(-0.05, 1.05)
    ax1.set_xlim(0.5, 16.5)
    ax1.legend(fontsize=8)

    # Right: Coordination success (sharp cliff)
    p0 = 1.0
    # Chernoff-style: sharp transition around r*
    success = p0 / (1 + np.exp(3.0 * (r - r_star)))
    ax2.plot(r, success, "-", color=C_ACCENT3, linewidth=2.5, label="P(success | r)")
    ax2.axvline(r_star, ls=":", color=C_PRIMARY, alpha=0.5, linewidth=1)
    ax2.fill_between(r, 0, success, where=(r <= r_star), color=C_ACCENT3, alpha=0.1)
    ax2.fill_between(r, 0, success, where=(r > r_star), color=C_RED, alpha=0.08)
    ax2.annotate("Coordination\ncliff", xy=(r_star, 0.5), xytext=(r_star + 3, 0.7),
                 fontsize=10, fontweight="bold", color=C_RED,
                 arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.5))
    ax2.set_xlabel("Compression Ratio r")
    ax2.set_ylabel("Coordination Success")
    ax2.set_title("(b) Coordination Outcome", fontweight="bold")
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_xlim(0.5, 16.5)
    ax2.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(out / "cliff_mechanism.pdf")
    fig.savefig(out / "cliff_mechanism.png")
    plt.close(fig)
    print(f"  C3: {out / 'cliff_mechanism.pdf'}")


# ============================================================================
# C4: Corollary Illustrations
# ============================================================================
def c4_corollary_visual(out: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    r = np.linspace(1, 16, 200)

    # Corollary 1: same r*, different p0
    r_star = 4.0
    for p0, label, color in [(1.0, "8B (p₀=1.0)", C_ACCENT1),
                              (0.6, "3.8B (p₀=0.6)", C_ACCENT2),
                              (0.25, "1.5B (p₀=0.25)", C_ACCENT4)]:
        success = p0 / (1 + np.exp(3.0 * (r - r_star)))
        ax1.plot(r, success, "-", color=color, linewidth=2, label=label)
    ax1.axvline(r_star, ls=":", color=C_PRIMARY, alpha=0.5, linewidth=1.5)
    ax1.annotate("Same r*\n(model-invariant)", xy=(r_star, 0.1), fontsize=9,
                 fontweight="bold", color=C_PRIMARY, ha="center")
    ax1.axhline(0.5, ls="--", color="gray", alpha=0.3)
    ax1.text(14, 0.53, "θ", color="gray", fontsize=9)
    ax1.set_xlabel("Compression Ratio r")
    ax1.set_ylabel("Coordination Success")
    ax1.set_title("(a) Corollary 1: Ceiling-Cliff Separation", fontweight="bold")
    ax1.set_ylim(-0.05, 1.05)
    ax1.set_xlim(0.5, 16.5)
    ax1.legend(fontsize=8)

    # Corollary 2: different theta → different r*
    p0 = 1.0
    for r_s, theta, label, color in [
        (3.0, 0.88, "C1-A (dense, θ=0.88)", C_ACCENT2),
        (7.0, 0.48, "MultiHopRAG (θ=0.48)", C_ACCENT3),
        (10.0, 0.37, "HotpotQA (θ=0.37)", C_ACCENT4),
    ]:
        success = p0 / (1 + np.exp(3.0 * (r - r_s)))
        ax2.plot(r, success, "-", color=color, linewidth=2, label=label)
        ax2.axvline(r_s, ls=":", color=color, alpha=0.4, linewidth=1)

    ax2.annotate("Dense tasks\ncliff early", xy=(3.0, 0.15), fontsize=8,
                 color=C_ACCENT2, ha="center", style="italic")
    ax2.annotate("Distributed tasks\ncliff late", xy=(10, 0.15), fontsize=8,
                 color=C_ACCENT4, ha="center", style="italic")
    ax2.set_xlabel("Compression Ratio r")
    ax2.set_ylabel("Coordination Success")
    ax2.set_title("(b) Corollary 2: Information Density Scaling", fontweight="bold")
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_xlim(0.5, 16.5)
    ax2.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(out / "corollary_visual.pdf")
    fig.savefig(out / "corollary_visual.png")
    plt.close(fig)
    print(f"  C4: {out / 'corollary_visual.pdf'}")


# ============================================================================
# C5: RAG Pipeline Placements
# ============================================================================
def c5_rag_pipelines(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 5.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("RAG Pipeline Placements (H3)", fontsize=13, fontweight="bold", pad=15)

    pipelines = [
        ("P1: Compress → Retrieve → Solve", 4.5,
         [("Corpus", "#dae8fc"), ("Compress", "#f8cecc"), ("Retrieve", "#fff2cc"),
          ("Solve", "#d5e8d4")]),
        ("P2: Retrieve → Compress → Solve", 2.8,
         [("Corpus", "#dae8fc"), ("Retrieve", "#fff2cc"), ("Compress", "#f8cecc"),
          ("Solve", "#d5e8d4")]),
        ("P3: Retrieve → Solve → Compress", 1.1,
         [("Corpus", "#dae8fc"), ("Retrieve", "#fff2cc"), ("Solve", "#d5e8d4"),
          ("Compress", "#f8cecc")]),
    ]

    for label, y, steps in pipelines:
        ax.text(0.3, y + 0.15, label, fontsize=10, fontweight="bold", color=C_PRIMARY, va="center")
        for i, (sname, scolor) in enumerate(steps):
            x = 1.5 + i * 2.2
            _box(ax, x, y - 0.4, 1.6, 0.55, sname, color=scolor, fontsize=9)
            if i < len(steps) - 1:
                _arrow(ax, x + 0.85, y - 0.4, x + 1.25, y - 0.4)

    # Annotations — mark P1 as best (placed right of the Solve box)
    ax.text(10.6, 4.1, "Best for\ncoordination", fontsize=9, color=C_GREEN,
            ha="center", va="center", style="italic", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#d5e8d4", edgecolor=C_GREEN,
                      alpha=0.85, linewidth=1))
    ax.annotate("", xy=(9.05, 4.1), xytext=(10.0, 4.1),
                arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.5))

    fig.savefig(out / "rag_pipelines.pdf")
    fig.savefig(out / "rag_pipelines.png")
    plt.close(fig)
    print(f"  C5: {out / 'rag_pipelines.pdf'}")


# ============================================================================
# C6: Compressor Comparison Overview
# ============================================================================
def c6_compressor_overview(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 7.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Compressor Overview", fontsize=14, fontweight="bold", pad=15)

    compressors = [
        ("LLMLingua-2", "Token-level classifier (XLM-RoBERTa)", "#1b9e77",
         "Scores each token independently;\nkeeps highest-scoring tokens",
         "'The total budget is $5000 for 8 workers'\n→ 'total budget $5000 8 workers'"),
        ("Phi-3 Extractive", "LLM span selection (Ollama)", "#d95f02",
         "Selects verbatim spans via\ninstruction-following LLM",
         "'The total budget is $5000 for 8 workers'\n→ 'budget is $5000 for 8 workers'"),
        ("Filter", "TF-IDF + Cross-Encoder reranker", "#7570b3",
         "Ranks sentences by relevance\nto task instruction",
         "[sent₁, sent₂, sent₃]\n→ [most relevant sentence]"),
        ("Truncation", "Simple prefix cut (baseline)", "#999999",
         "Keeps first N tokens;\nnaive length-based baseline",
         "'The total budget is $5000 for 8 workers'\n→ 'The total budget is'"),
    ]

    for i, (name, method, color, desc, example) in enumerate(compressors):
        y = 6.8 - i * 1.8
        # Name box (wider)
        _box(ax, 1.5, y, 2.4, 0.8, name, color=color + "33", edge=color, bold=True, fontsize=11)
        # Method label
        ax.text(3.2, y + 0.55, method, fontsize=8, color="#666666", va="center", style="italic")
        # Arrow
        _arrow(ax, 2.75, y - 0.4, 3.8, y - 0.4, color=color, lw=1.5)
        # Description
        ax.text(4.0, y - 0.4, desc, fontsize=9, color=C_PRIMARY, va="center")
        # Example (right side, bigger)
        ax.text(7.0, y - 0.1, example, fontsize=8, color="#444444", va="center",
                family="monospace", bbox=dict(boxstyle="round,pad=0.4",
                facecolor="#f5f5f5", edgecolor="#cccccc", linewidth=0.8))

    fig.savefig(out / "compressor_overview.pdf")
    fig.savefig(out / "compressor_overview.png")
    plt.close(fig)
    print(f"  C6: {out / 'compressor_overview.pdf'}")


# ============================================================================
# Entry point
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="Generate conceptual diagrams")
    parser.add_argument("--out", type=str, default="figures", help="Output directory")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Generating Conceptual Diagrams")
    print("=" * 60)

    c1_architecture_overview(out)
    c2_caac_flowchart(out)
    c3_cliff_mechanism(out)
    c4_corollary_visual(out)
    c5_rag_pipelines(out)
    c6_compressor_overview(out)

    print(f"\nAll diagrams saved to {out}/")


if __name__ == "__main__":
    main()
