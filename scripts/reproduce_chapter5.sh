#!/usr/bin/env bash
# Reproduce the Chapter 5 headline figure (coordination cliff).
# Runs H1 and H2 in sequence; writes results/h{1,2}/<run_id>/results.csv.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "→ Regenerating C1 benchmark..."
.venv/bin/python -m m6.benchmark.cli generate \
  --config configs/benchmark/c1-v0.1.yaml \
  --out data/processed/c1-v0.1

for h in h1 h2; do
  echo "→ Running ${h}..."
  .venv/bin/python -m m6.experiments.cli run \
    --hypothesis "$h" \
    --config "configs/experiments/${h}.yaml"
done

echo "✓ Chapter 5 reproduction complete. See results/h{1,2}/."
