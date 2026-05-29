#!/usr/bin/env bash
# Resume CAAC ablations from step 3 (steps 1-2 already done).
set -euo pipefail
cd "$(dirname "$0")/.."

PY=".venv/bin/python3"
CACHE="results/compression_cache.json"

echo "[3/10] CAAC theta=0.6"
$PY -m m6.experiments.run_caac --theta 0.6 --out results/caac_theta_0.6 --cache "$CACHE"

echo "[4/10] CAAC theta=0.7"
$PY -m m6.experiments.run_caac --theta 0.7 --out results/caac_theta_0.7 --cache "$CACHE"

echo "[5/10] CAAC theta=0.8"
$PY -m m6.experiments.run_caac --theta 0.8 --out results/caac_theta_0.8 --cache "$CACHE"

echo "[6/10] CAAC N=2"
$PY -m m6.experiments.run_caac --n-passes 2 --out results/caac_N_2 --cache "$CACHE"

echo "[7/10] CAAC N=3"
$PY -m m6.experiments.run_caac --n-passes 3 --out results/caac_N_3 --cache "$CACHE"

echo "[8/10] CAAC N=4"
$PY -m m6.experiments.run_caac --n-passes 4 --out results/caac_N_4 --cache "$CACHE"

echo "[9/10] CAAC N=5"
$PY -m m6.experiments.run_caac --n-passes 5 --out results/caac_N_5 --cache "$CACHE"

echo "All ablations complete: $(date)"
