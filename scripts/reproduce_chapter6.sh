#!/usr/bin/env bash
# Reproduce Chapter 6 headline figure (RAG pipelines + cost analysis).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
.venv/bin/python -m m6.experiments.cli run --hypothesis h4 --config configs/experiments/h4.yaml
echo "✓ Chapter 6 reproduction complete."
