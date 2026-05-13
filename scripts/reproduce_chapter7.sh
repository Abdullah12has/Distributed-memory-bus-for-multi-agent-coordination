#!/usr/bin/env bash
# Reproduce Chapter 7 headline figures (tag preservation + inference disclosure).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
.venv/bin/python -m m6.experiments.cli run --hypothesis h5 --config configs/experiments/h5.yaml
.venv/bin/python -m m6.experiments.cli run --hypothesis h6 --config configs/experiments/h6.yaml
echo "✓ Chapter 7 reproduction complete."
