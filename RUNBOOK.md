# Experiment Runbook

> **Today:** Month 0 of the 10-month plan (May 2026). The headline experiments
> (H1-H4) cannot run yet -- they need a trained ICAE checkpoint, and `make
> train-icae` takes ~3 days on the M4 Pro 48 GB. This runbook is the exact
> ordered sequence to get from a fresh clone to "headline figures in the bag".
>
> **Default path = fully local. No API key required for any headline figure.**
> Every default config uses Ollama (for inference) or MLX (for training).
> Opt-in OpenAI variants exist under `configs/experiments/*-openai.yaml` for
> users who want to add the paid cost-comparison arm to Chapter 6.
>
> All commands run on **your M4 Pro 48 GB workstation**. The sandbox is Linux
> aarch64 and cannot use MLX or Apple's MPS backend.
>
> Wallclock estimates are from `plan.md` section 5.4 and assume the workstation is
> idle.

---

## Current State (as of 2026-05-15)

| Asset | Status |
|-------|--------|
| C1 benchmark v0.1 (3 families, 150 instances) | Generated at `data/processed/c1-v0.1/` |
| LLMLingua-2 baseline calibration | Done: `results/baselines/lingua2-{narrativeqa,hotpotqa}.csv` |
| Sanity baseline JSON | Done: `results/sanity/llamacpp_baseline.json` |
| Ollama model (llama3.1:8b) | Pulled: `llama3.1:8b-instruct-q4_K_M` |
| ICAE compressor checkpoint | NOT TRAINED -- stub mode |
| Tag-preserving ICAE checkpoint (C4) | NOT TRAINED -- stub mode |
| H1 experiment results | NOT RUN |
| H2 experiment results | NOT RUN |
| H3 experiment results | NOT RUN |
| H4 experiment results | NOT RUN |
| Thesis chapters 1-4 | Drafted (intro, related work, implementation, benchmark) |
| Thesis chapters 5-7 | Placeholder results only |

---

## 0. One-time prerequisites (~30 minutes)

```bash
cd /Users/abdullah/Desktop/oulu-work/code/Distributed-memory-bus-for-multi-agent-coordination
make install-dev
cp .env.example .env
make check                          # ruff + mypy + unit tests
```

```bash
# Install Ollama if not already present
brew install ollama
ollama serve &                       # background daemon
```

```bash
# HuggingFace login (Llama-3.1 weights are gated behind a Meta license)
huggingface-cli login
```

---

## 1. Model artefacts (~1 hour, mostly network)

```bash
make models-pull-7b

# Pre-warm compressor and retriever models:
.venv/bin/python -c "
from llmlingua import PromptCompressor
PromptCompressor(
    model_name='microsoft/llmlingua-2-xlm-roberta-large-meetingbank',
    use_llmlingua2=True,
)
from sentence_transformers import SentenceTransformer
SentenceTransformer('BAAI/bge-large-en-v1.5')
SentenceTransformer('BAAI/bge-reranker-base')
"

# Optional, defer until H2 13B arm:
# make models-pull-13b    # Qwen2.5-14B-Instruct
```

---

## 2. C1 benchmark v0.1 (~2 minutes)

```bash
make bench-generate
make bench-validate
```

Output: `data/processed/c1-v0.1/{manifest.json, family-a.jsonl, family-b.jsonl, family-c.jsonl}`

---

## 3. Reproduce the LLMLingua-2 baseline (Month 1 stop-the-line, ~2-3 hours)

```bash
make baselines-smoke       # 2-minute smoke test
make baselines             # full run (~2-3h, local Ollama)
```

**Verify:** `results/baselines/lingua2-narrativeqa.csv` and `lingua2-hotpotqa.csv` show F1 within calibration targets (NarrativeQA within 2pp, HotpotQA within 3pp).

If either falls outside tolerance, stop and tell Lauri before ICAE training.

---

## 4. Train the ICAE compressor (~6 days total)

### 4a. Base ICAE (~3 days)

```bash
make train-icae                              # configs/training/icae-7b.yaml
```

- Encoder: Llama-3.1-8B-Instruct, LoRA rank 16
- Loss: L_recon + lambda * L_NCE
- Lambda sweep: {0.1, 0.3, 1.0}

**Verify:** `checkpoints/icae-7b/` contains adapter weights + `model_card.json`.

### 4b. Tag-preserving ICAE (C4, ~3 days)

```bash
make train-icae-tags                         # C4 variant
```

- Additional loss: + lambda_tag * L_tag
- Lambda_tag sweep: {0.1, 0.3, 1.0, 3.0}

**Verify:** `checkpoints/icae-7b-tags/` contains weights + tag head + `model_card.json`.

**Strict-mode reminder.** The headline configs set `require_trained_compressors: true`. For quick stub-mode smoke tests, flip to `false` temporarily.

---

## 5. Headline experiments (in order)

### Chapter 5: Coordination cliff (~7-12 days)

```bash
make exp-h1                                  # ~2 days
make exp-h2                                  # ~5-10 days (+ ~3 days for 13B arm)
make reproduce-ch5
```

**H1 verifies:** Spearman rho < 0.6 on >=2 of 3 compressors.
**H2 verifies:** Piecewise-linear cliff with >=30% drop, Mann-Whitney p < 0.05.

### Chapter 6: RAG pipelines (~3 days)

```bash
make exp-h3                                  # P1/P2/P3, storage vs accuracy bounded
make reproduce-ch6
```

**H3 verifies:** P1 vs P2 sign-flip across regimes, >=5pp F1 effect, P3 leads combined score.

### Chapter 7: Tag preservation (~1 day)

```bash
make exp-h4                                  # preservation rate >=85% at 4x
make reproduce-ch7
```

**H4 verifies:** preservation >= 0.85 at 4x AND accuracy delta CI lower bound >= -5pp.

---

## 6. Dependency graph

```
Steps 0-3 (env setup, benchmark, baselines)
  |
  v
4a (train ICAE, ~3d) -------> 4b (train ICAE-tag, ~3d)
  |                              |
  v                              v
H1 (~2d) -> H2 (~8-13d)        H4 (~1d)
               |
               v
             H3 (~3d)
               |
               v
        Generate figures (D1)
               |
               v
        Write thesis (F1-F2)
```

### Estimated total wallclock

| Phase | Wallclock |
|-------|-----------|
| 0-3: Setup + baselines | 1 day |
| 4: Training | 6 days (4a + 4b sequential) |
| 5: Experiments | 14-20 days |
| Figures | <1 day |
| **Total critical path** | **~20-28 days** |

B2/C4 can run in parallel with C1/C2 after B1 completes.

---

## 7. Optional: Cost-comparison arm

Only if you want real EUR/workflow numbers with API pricing:

```bash
# Edit .env:
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

make baselines-openai      # ~EUR 1 total
```

---

## 8. Stretch goals (Month 8, pick at most 2 with Lauri)

- **S1:** Calibration study (predict tau* on held-out workflows)
- **S2:** SecurityLingua adversarial sweep on tag preservation
- **S3:** Haseeb 2025 context-engineering baseline on C1
- **S4:** TalentAdore production trace replication (NDA-gated)

---

## 9. Submission (Month 10)

```bash
git tag v1.0
git push origin v1.0

# Final docker compose smoke
make docker-up
curl http://localhost:8080/healthz

# Final thesis PDF
cd thesis_latex && latexmk -pdf -bibtex main.tex
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `RuntimeError: require_trained_compressors=true but 'icae' is in stub mode` | No trained checkpoint | Train via `make train-icae`, or set `require_trained_compressors: false` for smoke runs |
| AutoGen runner produces 0 sub-task assignments | Planner output doesn't match regex patterns | Inspect trace; extend `_ASSIGN_PATTERNS` in `m6.agents.orchestrator` |
| `pip install` fails with MLX errors on Linux | MLX is Apple-Silicon-only | Use `pip install -e ".[torch,rag,external,eval,dev]"` (no `mlx` extra) |
| `make baselines` exits non-zero | F1 outside tolerance | Check `results/baselines/*.csv`; stop and tell Lauri |
| HuggingFace "Cannot access gated repo" | Haven't accepted Meta license | Visit HF model page, click "Request access", then `huggingface-cli login` |
