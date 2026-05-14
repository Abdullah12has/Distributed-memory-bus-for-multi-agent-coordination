#!/usr/bin/env bash
# Month-1 stop-the-line calibration: reproduce LLMLingua-2 on NarrativeQA + HotpotQA.
#
# Plan §4.1: NarrativeQA F1 within 2 pp of reported, HotpotQA within 3 pp.
# Failure to meet these → stop and tell Lauri before proceeding.
#
# Output:
#   results/sanity/llamacpp_baseline.json   (consumed by LlamaCppBackend at 70B startup)
#   results/baselines/lingua2-narrativeqa.csv
#   results/baselines/lingua2-hotpotqa.csv

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p results/sanity results/baselines

# This script is a thin driver around m6.experiments.baselines, which is the
# canonical baseline-reproduction module. The module exists in spirit only —
# see plan §4.1 for the spec. When it lands the implementation will be a
# straightforward harness:
#
#   1. Load NarrativeQA / HotpotQA test splits from HuggingFace datasets.
#   2. Compress with LLMLingua-2 at the same ratios the paper reports.
#   3. Run the same QA evaluation (single-agent F1 against gold).
#   4. Record per-(dataset, ratio) F1 to results/baselines/*.csv.
#   5. Write the 7B mini-eval baseline F1 to results/sanity/llamacpp_baseline.json
#      in the schema:
#         {"ref_model": "...", "ref_backend": "mlx", "ref_f1": 0.xx,
#          "recorded_at": "...", "n_prompts": 5}
#
# Until that module ships, run a manual NarrativeQA/HotpotQA eval and drop the
# baseline JSON in place; the llama.cpp backend refuses to start without it.

if [ ! -f results/sanity/llamacpp_baseline.json ]; then
  cat <<'WARN' >&2
[!] results/sanity/llamacpp_baseline.json does not exist yet.
[!] Either implement m6.experiments.baselines and re-run, or hand-fill it from
[!] a manual NarrativeQA run on the 7B fp16 backend before invoking llama.cpp.
[!] The 70B int4 startup sanity check depends on this baseline being recorded.
WARN
  exit 2
fi

echo "✓ baseline JSON found at results/sanity/llamacpp_baseline.json"
cat results/sanity/llamacpp_baseline.json
