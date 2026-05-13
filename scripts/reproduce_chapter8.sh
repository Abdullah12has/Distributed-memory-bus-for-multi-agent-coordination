#!/usr/bin/env bash
# Reproduce Chapter 8 headline figure (model-size scaling).
# Note: 34B and 70B take days; configure via configs/experiments/h7-*.yaml.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
for cfg in configs/experiments/h7.yaml; do
  .venv/bin/python -m m6.experiments.cli run --hypothesis h7 --config "$cfg"
done
echo "✓ Chapter 8 reproduction complete (size=7b)."
echo "   For 13B/34B/70B sweeps, edit model_size in configs/experiments/h7.yaml or use the size-suffix configs."
