# Reproducibility — Master's thesis evidence base

This document is the canonical reproducibility scaffold for the manuscript
*Distributed Memory Bus for Multi-Fragment LLM Workflows: Context
Compression, the Coordination Cliff, and Privacy* (see `draft1.md` for the
draft). Every claim in the manuscript traces to a named `results/*/`
directory; every figure regenerates from a single command.

This file complements thesis Appendix A and is the artefact used during
the Task 9 pre-submission polish to verify that every result is
reconstructable from the codebase.

---

## 1. Compute envelope

- **Local development:** Apple M4 Pro 48 GB (macOS, Python 3.11).
- **GPU compute:** RTX 5090 32 GB on WSL2 Ubuntu 22.04 (`ssh gpu`,
  Python 3.12, CUDA, Ollama). `OLLAMA_NUM_PARALLEL=4`.
- **Cloud API:** Featherless OpenAI-compatible endpoint for Qwen 72B and
  DeepSeek V4 Pro frontier runs (cost < €1 total).
- **End-to-end wallclock:** ~30 hours total, dominated by H1/H2 (~10 h GPU)
  and H5 (~6 h GPU).

## 2. Canonical results directories

The pre-submission terminology pass (Task 9) verifies that the manuscript
text never cites a *smoke*, *micro*, *quick*, *diag*, *v3_quick*, or
*bt_* directory. Canonical sources:

| Hypothesis / claim | Canonical results dir | Notes |
|---|---|---|
| H1, H2 | `results/h1_h2_v2/` | 4 compressors incl. truncation, 27 000 rows |
| H3 | `results/h3_final/` | 3 pipelines × 2 regimes, 900 cells |
| H4 | `results/h4_unbiased/` | post-bias-fix (2026-05-29); supersedes `h4_final/` |
| H5 / Corollary 1 | `results/h5_final/` | 3 planner scales × 3 families |
| H6 / Corollary 2 | `results/h6_final/` + `results/hotpotqa_sweep/` | MHR + HotpotQA external benchmarks |
| Frontier Qwen 72B | `results/frontier_qwen72b/` | in-regime, τ\* 0.8 % off |
| Frontier DeepSeek V4 Pro | `results/frontier_deepseekv4/` | in-regime, CI contains synth |
| Frontier GPT-oss 120B (out-of-regime) | `results/frontier_gptoss120b/`, `_v2/` | each carries `STATUS_NONCANONICAL.txt` per ADR-006 |
| CAAC (Ch 8 demonstration) | `results/caac/` | post-2026-05-29 CTR + per-family θ_q rerun |
| CAAC θ/N ablation (informative null) | `results/caac_theta_{0.6,0.7,0.8}/`, `results/caac_N_{2,3,4,5}/` | insights §54 |
| Bootstrap CI on θ_q | `results/h1_h2_v2/theorem_validation_bootstrap.json` | scripts/bootstrap_theta_q.py |

## 3. Regeneration commands

### 3.1 Benchmark

```bash
make bench-generate     # ~5 min CPU; produces data/processed/c1-v0.1/
make bench-validate     # schema + invariant sanity check
```

### 3.2 Per-experiment regeneration (GPU server)

All experiments self-contained — invoke directly on the GPU server:

```bash
ssh gpu
cd ~/Distributed-memory-bus-for-multi-agent-coordination
source .venv/bin/activate

# Coordination cliff (H1, H2) — Ch 5 §5.2–5.3
python -m m6.experiments.run_h1_h2        # ~10 h, writes results/h1_h2_v2/

# RAG pipeline placement (H3) — Ch 6
python -m m6.experiments.run_h3           # ~3 h, writes results/h3_final/

# Protected-fact recovery (H4) — Ch 7 §7.1
python -m m6.experiments.run_h4           # ~3 h, writes results/h4_unbiased/

# Model-size scaling (Corollary 1) — Ch 5 §5.6
python -m m6.experiments.run_h5           # ~6 h, writes results/h5_final/

# Transfer to MHR (Corollary 2) — Ch 7 §7.4
python -m m6.experiments.run_h6 --synth-results results/h5_full   # ~2 h

# HotpotQA second external benchmark (Corollary 2) — Ch 7 §7.4
python -m m6.experiments.run_hotpotqa     # ~2 h, writes results/hotpotqa_sweep/

# CAAC operating-point selector (Ch 8 §8.2)
python -m m6.experiments.run_caac         # ~15 min (post-2026-05-29 pooled-inner)
```

### 3.3 Per-experiment regeneration (frontier API)

Requires `FEATHERLESS_API_KEY` or `OPENAI_API_KEY` env vars:

```bash
# Qwen 72B
python -m m6.experiments.run_frontier --provider featherless \
    --model qwen2.5-72b-instruct
    # ~2 h, writes results/frontier_qwen72b/, cost ≈ €0.03

# DeepSeek V4 Pro
python -m m6.experiments.run_frontier --provider featherless \
    --model deepseek-v4-pro
    # ~2 h, writes results/frontier_deepseekv4/, cost ≈ €0.00 (free tier at sweep time)
```

### 3.4 Analysis (local, CPU-only)

```bash
# Bootstrap CI on per-family θ_q + new predicted-τ* band figure
python scripts/bootstrap_theta_q.py
    # ~5 min CPU, writes results/h1_h2_v2/theorem_validation_bootstrap.json
    # and figures/predicted_vs_empirical.{png,pdf}
```

### 3.5 Regenerate all figures from canonical CSVs

```bash
python scripts/regen_figures.py
    # ~5 min CPU; rebuilds all data-driven figures from canonical CSVs
    # (post-2026-05-30 update: paths now point at h1_h2_v2 and h4_unbiased;
    # predicted_vs_empirical delegates to scripts/bootstrap_theta_q.py)
```

## 4. Pre-submission verification checklist (Task 9)

Each box mechanical-verifiable from a clean clone:

- [ ] `make install-dev` succeeds in a fresh venv.
- [ ] `make bench-generate && make bench-validate` produces
      `data/processed/c1-v0.1/` matching the shipped manifest.
- [ ] `python scripts/regen_figures.py` succeeds from a clean state and
      every figure in `figures/` post-dates 2026-05-30.
- [ ] `python scripts/bootstrap_theta_q.py` succeeds and produces
      `results/h1_h2_v2/theorem_validation_bootstrap.json` with
      `coverage.n_total == 11` and `coverage.n_in_band == 0` (per
      insights §57).
- [ ] Every `STATUS_NONCANONICAL.txt` present in `results/frontier_gptoss120b/`
      and `results/frontier_gptoss120b_v2/`.
- [ ] No stale `*.partial.csv` next to `results.csv` in any results dir.
- [ ] `caac/summary.json` carries the strict-Pareto criterion (legacy weak
      file deleted).
- [ ] `caac/summary_per_family.json` present and exhibits filter/family-a
      +50 pp and lingua2/family-c +8 pp per insights §56.
- [ ] `make typecheck` and `make lint` pass on `src/`.
- [ ] All referenced ADRs present: `docs/adr/ADR-001.md` through
      `ADR-009.md`.

## 5. Model cards

| Model | Source | Use in this thesis | Quantisation |
|---|---|---|---|
| Qwen-2.5-1.5B-Instruct | Alibaba | H5 small planner | q4_K_M (Ollama) |
| Qwen-2.5-3.8B-Instruct | Alibaba | H5 mid planner | q4_K_M (Ollama) |
| Qwen-2.5-8B-Instruct | Alibaba | H5 large planner / default | q4_K_M (Ollama) |
| Qwen-2.5-72B-Instruct | Alibaba | Frontier validation §5.7.2 | FP16 (Featherless API) |
| Phi-3-Mini-3.8B-Instruct | Microsoft | Extractive compressor | q4_K_M (Ollama) |
| Llama-3.1-8B-Instruct | Meta | H4 held-out reader; planner backstop | q4_K_M (Ollama) |
| DeepSeek-V4-Pro | DeepSeek | Frontier validation §5.7.3 | provider-supplied (Featherless API) |
| LLMLingua-2-XLM-RoBERTa-Large-MeetingBank | Microsoft | LLMLingua-2 compressor | FP16 (HF) |
| BAAI/bge-large-en-v1.5 | BAAI | FAISS embedder | FP16 (HF) |
| BAAI/bge-reranker-base | BAAI | Instruction-aware filter reranker | FP16 (HF) |

Total disk footprint: ~11 GB for local models. Frontier models accessed
via API only.

## 6. Data cards

| Dataset | Source | Licence | Used in |
|---|---|---|---|
| C1 v0.1 | this thesis (synthetic, seeded) | CC-BY (released with codebase) | Ch 4, all H-* on C1 |
| MultiHopRAG | Tang & Yang, EMNLP 2024 Findings | permissive academic | Ch 7 §7.4 (Corollary 2) |
| HotpotQA | Yang et al., EMNLP 2018 | CC-BY-SA 4.0 | Ch 7 §7.4 (Corollary 2) |

## 7. Audit trail

The manuscript's empirical claims trace back through the following
artefacts. Listed in dependency order so a verifier can walk forward
from raw inputs to manuscript verdicts:

1. **Raw benchmark.** `data/processed/c1-v0.1/` from `make bench-generate`,
   deterministic from seed `0`.
2. **Raw sweep outputs.** `results/{h1_h2_v2,h3_final,h4_unbiased,h5_final,
   h6_final,hotpotqa_sweep,frontier_qwen72b,frontier_deepseekv4,caac}/results.csv`
   (or `sweep_results.csv` for `h1_h2_v2`).
3. **Per-experiment verdicts.** `verdicts.json` in each results dir,
   produced by the experiment script's `compute_*_verdict()` function.
4. **Per-experiment summaries.** `summary.json` and `summary_per_family.json`
   (where applicable).
5. **Cross-experiment analysis.** `results/h1_h2_v2/theorem_validation_ctr.json`
   (per-family validation; produced by
   `m6.analysis.validate_theorem.full_validation_per_family`) and
   `results/h1_h2_v2/theorem_validation_bootstrap.json` (Q7 D bootstrap
   CI; produced by `scripts/bootstrap_theta_q.py`).
6. **Figures.** Regenerated via `scripts/regen_figures.py` and
   `scripts/bootstrap_theta_q.py` from items (2)–(5).
7. **Manuscript.** `draft1.md` (this thesis draft, Markdown source for
   LaTeX wiring); every result paragraph cites the relevant `results/*/`
   directory.

## 8. ADR audit trail

The load-bearing decisions made during the audit-period reconciliation
(2026-05-28 to 2026-05-30) are recorded as:

- **ADR-006** — GPT-oss 120B scoped out of the frontier-validation set;
  calibrated-regime predicate formalised.
- **ADR-007** — CAAC reframed as operating-point selection (not Pareto
  dominance); strict-Pareto rate of 0/7 reported as expected and correct.
- **ADR-008** — *Compounding-error model*, not "Theorem 1" — terminology
  alignment for the empirical-model character of the artefact.
- **ADR-009** — Thesis title scoped to *Multi-Fragment LLM Workflows*;
  evaluation-methodology disclosure promoted to abstract and Ch 1.

Each ADR's "Revisit when" clause documents the conditions under which
the decision may be revisited (e.g., NeurIPS or ICLR re-targeting).
