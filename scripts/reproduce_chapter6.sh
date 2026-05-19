#!/usr/bin/env bash
# Reproduce Chapter 6 headline figure (RAG pipelines + cost analysis).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
.venv/bin/python -m m6.experiments.cli run --hypothesis h3 --config configs/experiments/h3.yaml
echo "✓ Chapter 6 reproduction complete."
