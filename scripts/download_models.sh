#!/usr/bin/env bash
# Download a model into the HF cache. Used by `make models-pull-*`.
# Usage: ./scripts/download_models.sh <hf-or-ollama-tag>
set -euo pipefail
TAG="${1:?missing model tag}"
HF_HOME="${HF_HOME:-./data/hf-cache}"
mkdir -p "$HF_HOME"

case "$TAG" in
  llama-3.1-8b-instruct)
    .venv/bin/python -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='meta-llama/Llama-3.1-8B-Instruct', cache_dir='${HF_HOME}')
"
    ollama pull llama3.1:8b-instruct-q4_K_M || true
    ;;
  qwen2.5-14b-instruct)
    .venv/bin/python -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='Qwen/Qwen2.5-14B-Instruct', cache_dir='${HF_HOME}')
"
    ;;
  qwen2.5-32b-instruct-q4_k_m)
    .venv/bin/python -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='Qwen/Qwen2.5-32B-Instruct-GGUF', cache_dir='${HF_HOME}',
  allow_patterns=['*Q4_K_M*'])
"
    ;;
  llama-3.1-70b-instruct-q4_k_m)
    .venv/bin/python -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='bartowski/Meta-Llama-3.1-70B-Instruct-GGUF', cache_dir='${HF_HOME}',
  allow_patterns=['*Q4_K_M*'])
"
    ;;
  *)
    echo "Unknown tag: $TAG" >&2
    exit 1
    ;;
esac

echo "✓ pulled $TAG"
