#!/usr/bin/env bash
# Reproduce Chapter 7 headline figures (tag preservation).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
.venv/bin/python -m m6.experiments.cli run --hypothesis h4 --config configs/experiments/h4.yaml
echo "✓ Chapter 7 reproduction complete."
