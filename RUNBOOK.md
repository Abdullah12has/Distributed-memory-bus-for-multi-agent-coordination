# Experiment Runbook

> **Today:** Month 0 of the 10-month plan (May 2026). The headline experiments
> (H1–H7) cannot run yet — they need a trained ICAE checkpoint, and `make
> train-icae` takes ~3 days on the M4 Pro 48 GB. This runbook is the exact
> ordered sequence to get from a fresh clone to "headline figures in the bag".
>
> All commands run on **your M4 Pro 48 GB workstation**, not on the remote
> sandbox. The sandbox is Linux aarch64 and cannot use MLX, llama.cpp on Apple
> Silicon, or Apple's MPS backend. Don't try to run any of this remotely.
>
> Wallclock estimates are from `plan.md` §5.4 and assume the workstation is
> idle.

---

## 0. One-time prerequisites (≈30 minutes)

```bash
# Clone (skip if you're already here)
git clone <repo> m6-thesis && cd m6-thesis

# Python 3.11 (3.10 lacks StrEnum which we use)
brew install python@3.11

# Set up the project venv and install all deps (MLX, PEFT, AutoGen, FAISS, ...)
make install-dev

# Verify the install
make check                          # ruff + mypy + unit tests
```

If `make check` is green, proceed.

```bash
# Copy and edit the env file. Only the API keys are sensitive.
cp .env.example .env
# Then edit .env and fill in OPENAI_API_KEY (for H6) and ANTHROPIC_API_KEY
# (for the C3 cost arm and the Sonnet-4.6 cross-check).
```

---

## 1. Model artefacts (≈1 hour, mostly network)

```bash
# Llama-3.1-8B-Instruct in MLX format (the 7B path). ~16 GB download.
make models-pull-7b

# Optional, can defer until Month 7:
# make models-pull-13b    # Qwen2.5-14B-Instruct
# make models-pull-34b    # Qwen2.5-32B Q4_K_M (≈18 GB)
# make models-pull-70b    # Llama-3.1-70B Q4_K_M (≈40 GB)
```

---

## 2. C1 benchmark v0.1 (≈2 minutes)

```bash
# Generates 150 workloads across families a/b/c.
make bench-generate
# Output: data/processed/c1-v0.1/{manifest.json, family-a.jsonl, family-b.jsonl, family-c.jsonl}

make bench-validate
# Schema check: every workload's pydantic model parses cleanly.
```

This is the artefact published alongside the thesis (plan §2.1). Tag the git
revision now so the headline figures are reproducible against this exact
benchmark version.

---

## 3. Reproduce the LLMLingua-2 baseline (Month 1 stop-the-line, ≈1–2 days)

```bash
# NarrativeQA F1 must be within 2 pp of reported; HotpotQA within 3 pp.
# If either fails by more than that, stop and tell Lauri before proceeding.
./scripts/reproduce_baselines.sh             # ⚠️ this script is a stub; see below
```

> **NOTE:** `scripts/reproduce_baselines.sh` is not yet written. The
> minimum work is: write a script that runs LLMLingua-2 on NarrativeQA and
> HotpotQA test splits, records F1, and refuses to proceed if the targets
> aren't met. This is the **next manual task** before any training.

---

## 4. Train the ICAE compressor (≈3 days)

```bash
# Headline ICAE: 7B encoder + frozen 7B decoder, LoRA rank 16, dual-objective.
make train-icae                              # configs/training/icae-7b.yaml
# Output: checkpoints/icae-7b/final/

# The two follow-up checkpoints can train in parallel if you have the patience
# to swap models — they share the same base, so on the M4 Pro it's serial.
make train-icae-tags                         # C4 variant, ≈3 days
make train-dialogue                          # H3 ablation, ≈3 days
```

Two of these (H3 dialogue and C4 tag-head) are required for the H3, H5, and H6
headline experiments. Total Month 1–3 wallclock: ≈9–10 days of training.

**Strict-mode reminder.** The headline configs
(`configs/experiments/h{1,2,3,5,6,7}.yaml`) all set
`require_trained_compressors: true`. If you want to do a quick stub-mode smoke
test before the training finishes, set it to `false` for the smoke run only.
Production headline figures **must** use trained weights — anything else is a
methodological flaw the supervisor will catch.

---

## 5. Headline experiments (in order)

### Chapter 5 figures: coordination cliff (≈10–15 days)

```bash
# H1: Spearman ρ(Δ_qa, Δ_coord) < 0.6 on ≥2 of 3 compressors
make exp-h1                                  # ≈2 days

# H2: piecewise-linear cliff fit + Mann-Whitney U
make exp-h2                                  # ≈5–10 days; the headline run

# H3: matched single-agent QA, dialogue vs QA training
make exp-h3                                  # ≈2 days

# Headline figure for Ch. 5:
make reproduce-ch5
```

After this completes, paste the `verdicts.json` from each `results/h{N}/.../`
into the `% RESULTS:` placeholders in `thesis_latex/Chapters/summary.tex` and
`thesis_latex/Chapters/experiments.tex`.

### Chapter 6 figure: RAG pipelines (≈3 days)

```bash
make exp-h4                                  # P1 / P2 / P3 × storage/accuracy regimes
make reproduce-ch6
```

The verdict computation is now in-code; the CSV at `results/h4/.../results.csv`
plus `verdicts.json` will tell you whether the H4 falsifiable claim is
supported.

### Chapter 7 figures: tag preservation + inference disclosure (≈2 days)

```bash
make exp-h5                                  # tag preservation rate ≥85% at 4×
make exp-h6                                  # gpt-4o-mini reader (≈EUR 30 in API)
make reproduce-ch7
```

The H6 runner now refuses to start if your workload-families list doesn't
include at least one family that emits protected facts (a or c).

### Chapter 8 figure: model-size scaling (≈3 weeks)

```bash
# 7B is already done (it's the H2 baseline).
# 13B fp16:
#   edit configs/experiments/h7.yaml: model_size: "13b", backend: "mlx"
make exp-h7                                  # ≈10–20 days

# 34B int4 (focused partial sweep):
#   edit h7.yaml: model_size: "34b-int4", backend: "llamacpp"
#   set ratios to {τ_13B - 2, τ_13B, τ_13B + 2, 1, 16}
make exp-h7                                  # ≈3–5 days

# 70B int4 SINGLE POINT (~3-5 t/s; the slowest arm):
#   edit h7.yaml: model_size: "70b-int4", ratios: [τ_34B]
#   ⚠️ the LlamaCppBackend sanity check refuses to start without
#      results/sanity/llamacpp_baseline.json — populate it from Month 1
#      baseline reproduction first.
make exp-h7                                  # ≈7–14 days

make reproduce-ch8
```

### Chapter 9 figure: real-trace transfer (gated)

```bash
# Edit docs/agent_readiness.yaml when Mohammad / Faisal / Vu say their
# connectors are ready. H8 will short-circuit cleanly with a
# "documented-as-deferred" verdict otherwise.
make exp-h8
```

---

## 6. Drafting the manuscript

```bash
cd thesis_latex
latexmk -pdf -bibtex main.tex
```

For each chapter with `% RESULTS:` placeholders, paste the verdict + the
headline figure path.

Manifest of placeholders:

```
Chapters/experiments.tex:   % RESULTS:   (one per hypothesis)
Chapters/summary.tex:        % RESULTS:   (one paragraph per H1..H8 + closing)
```

---

## 7. Stretch goals (Month 8, optional)

`plan.md` §4.5 lists S1–S5. Pick at most two with Lauri at end of Month 7.

```bash
# S1: calibration-study script (not yet written)
# S2: SecurityLingua red-team sweep (not yet written)
# S3: Haseeb 2025 baseline (not yet written)
# S4: TalentAdore production-trace replication (NDA-gated)
# S5: Compression × Paper 1 polymatroid simulation (FCG team owns)
```

---

## 8. Submission (Month 10)

```bash
# Reproducibility package
git tag v1.0
git push origin v1.0

# HuggingFace upload of the tag-preserving compressor
huggingface-cli upload-folder checkpoints/icae-7b-tags/final \
    --repo-id <org>/m6-icae-tag-v1

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
| `H5Runner refuses to start: 0 of N workloads carry protected_facts` | `workload_families` set to `["b"]` only — family (b) has no protected facts | Add `"a"` or `"c"` to `workload_families` in the YAML |
| `RuntimeError: require_trained_compressors=true but 'icae' is in stub mode` | No trained checkpoint at the configured path | Train via `make train-icae`, or flip the flag to `false` for stub-mode smoke runs |
| `LlamaCppBackend RuntimeError: Sanity baseline missing` | `results/sanity/llamacpp_baseline.json` not populated | Run the Month 1 baseline reproduction; record the resulting F1 |
| `Sanity check failed: F1 dropped by Xpp from baseline` (70B int4) | int4 quantisation degraded the model below the threshold | The thesis explicitly documents this risk (plan §7 row 4); exclude 70B from headline claims |
| AutoGen runner produces 0 sub-task assignments | Planner's output doesn't match any of the three regex patterns | Inspect a trace; if the planner uses a new format, extend `_ASSIGN_PATTERNS` in `m6.agents.orchestrator` and re-test |
