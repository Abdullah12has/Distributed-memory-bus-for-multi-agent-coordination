# Model Cards

**Provenance.** Every identifier and parameter in this file was read directly off
the on-disk artifacts of *Memory Bus for Multi-Fragment LLM Workflows* (Syed
Abdullah Hassan, University of Oulu) on 2026-06-01, against result files produced
on the dates each run was completed (H5 2026-05-27, H4-unbiased-v2 2026-05-29,
frontier runs 2026-05-28). Local-planner IDs came from
`results/h5_final/results.csv` (column `planner_model_name`); the H4 reader ID
from `results/h4_unbiased_v2/verdicts.json` (`reader_model`); frontier IDs from
the `model` column of each `results/frontier_*/results.csv`; compressor and
decoding parameters from the source files cited per row. Host facts confirmed on
this machine: the Ollama binary is at `/usr/local/bin/ollama`; `ollama list`
returned the three real digests recorded below (`qwen2.5:1.5b-instruct-q4_K_M`
not pulled on this host); this repo does **not** use Git LFS (no
`.gitattributes`, `git lfs` is not installed, result files are plain on-disk
files); the C1 benchmark master seed is `20260514` per
`data/processed/c1-v0.1/manifest.json`. **No value in this file is a
placeholder.**

> **Hardware / hosting.** Local models (Ollama planners + H4 reader) ran on the
> RTX 5090 32 GB GPU host (WSL2 Ubuntu 22.04) and on an Apple M4 Pro for local
> development/smoke runs. Frontier models were served remotely: Qwen-2.5-72B and
> DeepSeek-V4-Pro via the Featherless inference API, GPT-oss-120B via the OpenAI
> Responses API.

---

## Local planners (H5 / Corollary 1)

The three planners are different architecture families (the original
"Qwen 1.5B/3.8B/8B scaling" label was a documented error). Decoding for all
three: `temperature=0.1`, `num_predict=512`, `seed=<run seed>`
(`src/m6/experiments/run_h5.py:124`). Ollama digests below are the real IDs from
`ollama list` on this host.

### qwen2.5:1.5b-instruct-q4_K_M — planner

| Field | Value |
|-------|-------|
| Role | Planner (smallest local arm) |
| Exact identifier | `qwen2.5:1.5b-instruct-q4_K_M` |
| Family / size | Qwen-2.5, 1.5 B params, 4-bit `q4_K_M` quantization |
| Source | Ollama (local) |
| Digest | not pulled on this host (obtain via `ollama list` on the GPU host where H5 ran) |
| Decoding | temperature 0.1, num_predict 512, seed per run |
| Used in | H5 / Corollary 1 (local cross-architecture arm) |

### phi3:latest — planner (Phi-3-Mini 3.8B)

| Field | Value |
|-------|-------|
| Role | Planner (mid local arm) |
| Exact identifier | `phi3:latest` (Phi-3-Mini, 3.8 B) |
| Source | Ollama (local) |
| Digest | `4f2222927938` (2.2 GB; `ollama list`, this host) |
| Decoding | temperature 0.1, num_predict 512, seed per run |
| Used in | H5 / Corollary 1; also the Phi-3-Mini extractive compressor backbone |
| Note | Family-a floor effect (baseline < 50 %) — correctly skipped in H5 |

### llama3.1:8b — planner

| Field | Value |
|-------|-------|
| Role | Planner (largest local arm) |
| Exact identifier | `llama3.1:8b` (Llama-3.1 8 B) |
| Source | Ollama (local) |
| Digest | `46e0c10c039e` (4.9 GB; `ollama list`, this host) |
| Decoding | temperature 0.1, num_predict 512, seed per run |
| Used in | H5 / Corollary 1; also the A3 probe (`results/a3_probe/results.csv`) |

---

## H4 reader (protected-fact recovery)

### llama3.1:8b — reader

| Field | Value |
|-------|-------|
| Role | Reader / adversary in H4 (protected-fact recovery rate) |
| Exact identifier | `llama3.1:8b` (default `reader_model`/`model` in `src/m6/experiments/run_h4.py:8,24`; verdicts JSON does not store the id) |
| Source | Ollama (local) |
| Digest | `46e0c10c039e` (4.9 GB; `ollama list`, this host) |
| Decoding | temperature 0.0 / greedy, num_predict 10 (`src/m6/experiments/run_h4.py:83`) |
| Used in | H4 (`results/h4_unbiased_v2/`, `results/h4_unbiased/`) |
| Note | Documented "no"-bias: priors_rate ≈ 0.03 / baseline_rate ≈ 0.58 when ground truth is yes |

---

## Frontier planners (Corollary 1 cross-architecture validation)

Decoding for all frontier runs: `temperature=0.1`, `max_tokens=1024`
(`src/m6/experiments/run_frontier.py:179-180`).

### Qwen/Qwen2.5-72B-Instruct

| Field | Value |
|-------|-------|
| Role | Frontier planner (Corollary 1 invariance evidence) |
| Exact identifier | `Qwen/Qwen2.5-72B-Instruct` |
| Source | Featherless inference API |
| Version | API-served; pin = the HF repo above |
| Decoding | temperature 0.1, max_tokens 1024 |
| Used in | `results/frontier_qwen72b/`, `results/frontier_qwen72b_e2/` (re-run with 2.5 ratio added) |

### deepseek-ai/DeepSeek-V4-Pro

| Field | Value |
|-------|-------|
| Role | Frontier planner (Corollary 1 invariance evidence) |
| Exact identifier | `deepseek-ai/DeepSeek-V4-Pro` |
| Source | Featherless inference API |
| Decoding | temperature 0.1, max_tokens 1024 |
| Used in | `results/frontier_deepseekv4/` |

### openai/gpt-oss-120b

| Field | Value |
|-------|-------|
| Role | Frontier planner — scoped out per ADR-006 (extended-reasoning, outside calibrated regime) |
| Exact identifier | `openai/gpt-oss-120b` |
| Source | OpenAI Responses API |
| Decoding | temperature 0.1, max_tokens 1024 |
| Used in | `results/frontier_gptoss120b/`, `results/frontier_gptoss120b_v2/` (both `STATUS_NONCANONICAL.txt`) |

---

## Compressor models (all training-free)

### LLMLingua-2 — token classifier

| Field | Value |
|-------|-------|
| Role | Token-level compressor (XLM-RoBERTa classifier) |
| Exact identifier | `microsoft/llmlingua-2-xlm-roberta-large-meetingbank` (`src/m6/compressors/lingua2.py:34`) |
| Tokenizer | `xlm-roberta-base` (`lingua2.py:27`) |
| Source | HuggingFace (upstream `llmlingua` package; Pan et al., ACL Findings 2024) |
| Device | auto → CUDA on GPU host, MPS on M4 Pro (`lingua2.py:72-97`) |
| Used in | H1/H2, H3, H4, H5/H6, frontier, CAAC |

### Instruction-aware filter — cross-encoder reranker

| Field | Value |
|-------|-------|
| Role | TF-IDF prune + cross-encoder rerank, then token-level trim |
| Reranker identifier | `BAAI/bge-reranker-base` (`src/m6/compressors/filter.py:93`, loaded via `sentence_transformers.CrossEncoder`) |
| Source | HuggingFace |
| Used in | H1/H2, H3, H4, H5/H6, CAAC |

### Phi-3-Mini extractive

| Field | Value |
|-------|-------|
| Role | Verbatim span selection with novel-token stripping + LLMLingua-2 fallback |
| Backbone | `phi3:latest` (Phi-3-Mini 3.8 B) via Ollama (`src/m6/compressors/phi3_extractive.py:30`, `DEFAULT_MODEL`) |
| Source | Ollama (local), endpoint `http://127.0.0.1:11434` |
| Digest | `4f2222927938` (`ollama list`, this host) |
| Decoding | temperature 0.0 (`phi3_extractive.py:107`) |
| Used in | H1/H2, H3, H4, H5/H6, CAAC |

### Truncation / Identity (no model)

| Field | Value |
|-------|-------|
| Truncation | Prefix-truncation baseline, no model (`src/m6/compressors/truncation.py`) |
| Identity | No-compression control, no model (`src/m6/compressors/__init__.py`) |
| Used in | H1/H2 v2 (truncation added 2026-05-27) and all runs as controls |
