#!/usr/bin/env bash
# Month-1 stop-the-line calibration: reproduce LLMLingua-2 on NarrativeQA + HotpotQA.
#
# Plan §4.1: NarrativeQA F1 within 2 pp of reported, HotpotQA within 3 pp.
# Failure to meet these → stop and tell Lauri before proceeding.
#
# Outputs (idempotent):
#   results/sanity/llamacpp_baseline.json     consumed by LlamaCppBackend at 70B startup
#   results/baselines/lingua2-narrativeqa.csv per-example F1 on the calibration sample
#   results/baselines/lingua2-hotpotqa.csv    same for HotpotQA
#
# Backends are configurable per-config; the script only requires an API key
# when the chosen config actually uses a paid backend. To run fully locally
# (no API key), use `configs/experiments/baselines-local.yaml` or pass
# --config to point at any config whose qa_backend / sanity_backend are
# "mlx" / "ollama" / "llamacpp" / "echo".
#
# Exit codes:
#   0  ⇒ every dataset passed its tolerance; safe to proceed to ICAE training
#   1  ⇒ at least one dataset failed; stop and tell Lauri
#   2  ⇒ the script itself failed (missing config, missing API key, etc.)
#
# Usage:
#   ./scripts/reproduce_baselines.sh                       # default config (openai)
#   ./scripts/reproduce_baselines.sh --config configs/experiments/baselines-local.yaml
#   ./scripts/reproduce_baselines.sh --skip-calibration    # only refresh the sanity JSON
#   ./scripts/reproduce_baselines.sh --skip-sanity         # only run dataset calibration

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# ---- argv: separate out --config from the rest -----------------------------
CONFIG="configs/experiments/baselines.yaml"
PASSTHROUGH=()
while [ $# -gt 0 ]; do
  case "$1" in
    --config)
      CONFIG="$2"; shift 2 ;;
    --config=*)
      CONFIG="${1#--config=}"; shift ;;
    *)
      PASSTHROUGH+=("$1"); shift ;;
  esac
done

VENV_PY="$ROOT/.venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
  echo "[!] No venv at .venv/. Run \`make install-dev\` first." >&2
  exit 2
fi

if [ ! -f "$CONFIG" ]; then
  echo "[!] Missing config at $CONFIG." >&2
  exit 2
fi

# ---- read which backends the config actually uses --------------------------
# We use the project's Python rather than yq so we don't add a new tool dep.
read -r QA_BACKEND SANITY_BACKEND < <("$VENV_PY" - <<PY
import sys, yaml
cfg = yaml.safe_load(open("$CONFIG"))
print(cfg.get("qa_backend", "openai"), cfg.get("sanity_backend", "openai"))
PY
)

# Load .env so OPENAI_API_KEY / ANTHROPIC_API_KEY are visible if defined.
if [ -f .env ]; then
  set -o allexport
  # shellcheck disable=SC1091
  . ./.env
  set +o allexport
fi

# ---- only require API keys for the backends actually selected --------------
needs_openai=false
needs_anthropic=false
for b in "$QA_BACKEND" "$SANITY_BACKEND"; do
  case "$b" in
    openai)   needs_openai=true ;;
    anthropic) needs_anthropic=true ;;
  esac
done

if [ "$needs_openai" = true ] && [ -z "${OPENAI_API_KEY:-}" ]; then
  cat >&2 <<MSG
[!] $CONFIG uses qa_backend or sanity_backend = "openai" but OPENAI_API_KEY is unset.
[!] Two options to proceed without an OpenAI key:
[!]   1. ./scripts/reproduce_baselines.sh --config configs/experiments/baselines-local.yaml
[!]      (uses Ollama by default — no API key required)
[!]   2. Edit $CONFIG and switch the backends to "mlx" or "ollama".
MSG
  exit 2
fi
if [ "$needs_anthropic" = true ] && [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "[!] $CONFIG uses Anthropic but ANTHROPIC_API_KEY is unset." >&2
  exit 2
fi

mkdir -p results/sanity results/baselines

echo "→ Reproducing LLMLingua-2 baselines (config: $CONFIG)"
echo "  qa_backend=$QA_BACKEND   sanity_backend=$SANITY_BACKEND"
"$VENV_PY" -m m6.experiments.baselines --config "$CONFIG" ${PASSTHROUGH[@]+"${PASSTHROUGH[@]}"}
status=$?

if [ "$status" -eq 0 ]; then
  echo "✓ baselines reproduced (within tolerance). Sanity JSON:"
  if [ -f results/sanity/llamacpp_baseline.json ]; then
    cat results/sanity/llamacpp_baseline.json
  fi
else
  echo "✗ baselines FAILED. See results/baselines/*.csv for the per-example breakdown."
  echo "  Plan §4.1 says: stop and tell Lauri before proceeding to ICAE training."
fi

exit "$status"
