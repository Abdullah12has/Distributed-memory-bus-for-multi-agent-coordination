#!/usr/bin/env bash
# Run CAAC ablations, HotpotQA sweep, and GPT-oss retest on GPU server.
# Usage: tmux new -s ablations './scripts/run_ablations.sh'
set -euo pipefail
cd "$(dirname "$0")/.."

PY=".venv/bin/python3"
CACHE="results/compression_cache.json"
SYNTH="results/h1_h2_final"

echo "=============================================="
echo "Starting experiment batch: $(date)"
echo "=============================================="

# ------------------------------------------------------------------
# 1. HotpotQA cliff sweep (~2h)
# ------------------------------------------------------------------
echo ""
echo "[1/10] HotpotQA cliff sweep"
$PY -m m6.experiments.run_hotpotqa \
    --out results/hotpotqa_sweep \
    --synth-results "$SYNTH"

# ------------------------------------------------------------------
# 2. GPT-oss 120B retest (frontier, ~30min)
# ------------------------------------------------------------------
echo ""
echo "[2/10] GPT-oss 120B frontier retest"
$PY -m m6.experiments.run_frontier \
    --model openai/gpt-oss-120b \
    --out results/frontier_gptoss120b_v2 \
    --synth-results "$SYNTH" \
    --cache "$CACHE"

# ------------------------------------------------------------------
# 3. CAAC theta ablation (skip 0.5 — already have it in results/caac)
# ------------------------------------------------------------------
echo ""
echo "[3/10] CAAC theta=0.6"
$PY -m m6.experiments.run_caac --theta 0.6 --out results/caac_theta_0.6 --cache "$CACHE"

echo ""
echo "[4/10] CAAC theta=0.7"
$PY -m m6.experiments.run_caac --theta 0.7 --out results/caac_theta_0.7 --cache "$CACHE"

echo ""
echo "[5/10] CAAC theta=0.8"
$PY -m m6.experiments.run_caac --theta 0.8 --out results/caac_theta_0.8 --cache "$CACHE"

# ------------------------------------------------------------------
# 4. CAAC N ablation (skip N=1 — already have it in results/caac)
# ------------------------------------------------------------------
echo ""
echo "[6/10] CAAC N=2"
$PY -m m6.experiments.run_caac --n-passes 2 --out results/caac_N_2 --cache "$CACHE"

echo ""
echo "[7/10] CAAC N=3"
$PY -m m6.experiments.run_caac --n-passes 3 --out results/caac_N_3 --cache "$CACHE"

echo ""
echo "[8/10] CAAC N=4"
$PY -m m6.experiments.run_caac --n-passes 4 --out results/caac_N_4 --cache "$CACHE"

echo ""
echo "[9/10] CAAC N=5"
$PY -m m6.experiments.run_caac --n-passes 5 --out results/caac_N_5 --cache "$CACHE"

# ------------------------------------------------------------------
# Done
# ------------------------------------------------------------------
echo ""
echo "=============================================="
echo "All experiments complete: $(date)"
echo "=============================================="
echo ""
echo "Results:"
echo "  - HotpotQA:    results/hotpotqa_sweep/"
echo "  - GPT-oss v2:  results/frontier_gptoss120b_v2/"
echo "  - CAAC theta:  results/caac_theta_{0.6,0.7,0.8}/"
echo "  - CAAC N:      results/caac_N_{2,3,4,5}/"
