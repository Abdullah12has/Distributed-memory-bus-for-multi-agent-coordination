#!/usr/bin/env python3
"""Regenerate broken figures with explicit *_final/ CSV paths.

The auto-discovery in src/m6/figures/generate.py uses
`sorted(Path('results').rglob(pattern))[-1]`, which picks
*alphabetically last* matches like `h5_smoke`, `h1_h2_v3_quick2`,
`caac_smoke`, `frontier_smoke2`, etc., instead of the `_final/` runs.

This script bypasses that by passing explicit CSV paths.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from m6.figures import generate as G  # noqa: E402

OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# Canonical results paths per insights §55 (post-audit reconciliation):
# - H1/H2 use h1_h2_v2 (4 compressors incl truncation, 27k rows)
# - H4 uses h4_unbiased (question-template bias fix landed 2026-05-29)
# - Other final dirs unchanged.
H1H2 = str(ROOT / "results/h1_h2_v2/sweep_results.csv")
H3   = str(ROOT / "results/h3_final/results.csv")
H4   = str(ROOT / "results/h4_unbiased/results.csv")
H5   = str(ROOT / "results/h5_final/results.csv")
H6   = str(ROOT / "results/h6_final/results.csv")
CAAC = str(ROOT / "results/caac/results.csv")
FRONT = str(ROOT / "results/frontier_qwen72b/results.csv")
# CTR file: h1_h2_v2 carries the critical_token_recall column inline; no
# separate fix file is needed.
CTR  = str(ROOT / "results/h1_h2_final/critical_token_recall_fixed.csv")

print("Regenerating with explicit final CSVs...")
print(f"  H1/H2:    {H1H2}")
print(f"  H3:       {H3}")
print(f"  H4:       {H4}")
print(f"  H5:       {H5}")
print(f"  H6:       {H6}")
print(f"  CAAC:     {CAAC}")
print(f"  Frontier: {FRONT}")
print()

# ---- H5 figures (cliff_hero, h5_overlay, scaling_auc) ----
G.fig1_cliff_hero(H5, OUT)
G.fig_h5_model_overlay(H5, OUT)
G.fig_scaling_auc(H5, OUT)

# ---- H1/H2 figures (cliff_families, h1_scatter, fingerprints) ----
G.fig2_cliff_families(H1H2, OUT)
G.fig_h1_scatter(H1H2, OUT)
G.fig_compressor_fingerprints(H1H2, OUT, ctr_csv=CTR)

# ---- predicted_vs_empirical is owned by scripts/bootstrap_theta_q.py ----
# (Per insights §57 / Q7 D / ADR-008, the figure is a bootstrap-CI band
# overlay derived from per-family θ_q resampling. The generator in
# m6.figures.generate.fig3_predicted_vs_empirical is preserved for legacy
# use but does NOT produce the canonical band figure.)
import subprocess
print("  predicted_vs_empirical: delegating to scripts/bootstrap_theta_q.py …")
subprocess.run([sys.executable, str(ROOT / "scripts/bootstrap_theta_q.py")],
               check=True, cwd=str(ROOT))

# ---- H1/H2 x H4 (pareto privacy/coord) ----
G.fig_pareto_privacy_coordination(H1H2, H4, OUT)

# ---- CAAC ----
G.fig4_caac_pareto(CAAC, OUT)
G.fig_caac_ablation(CAAC, OUT)

# ---- H4 (privacy quality) ----
G.fig5_privacy_quality(H4, OUT)

# ---- Frontier validation (uses H5 family-a 8B as local overlay) ----
G.fig6_frontier(FRONT, H5, OUT)

# ---- H3 RAG pipelines ----
G.fig_h3_pipelines(H3, OUT)

# ---- Frontier multi (uses rglob — needs cwd at project root) ----
import os
os.chdir(ROOT)
G.fig_frontier_multi(OUT)

# ---- Theta density (also uses rglob) ----
G.fig_theta_density(OUT)

# ---- HotpotQA cliff is left untouched (used different CSV path) ----
print("\nDONE. Regenerated figures are in figures/. Originals are in figures/old/")
