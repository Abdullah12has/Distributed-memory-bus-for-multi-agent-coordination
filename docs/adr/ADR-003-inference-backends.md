# ADR-003: Inference backends per model size

**Status:** Accepted
**Date:** 2026-05-12
**Deciders:** Syed Abdullah Hassan, Lauri Lovén

## Context

The thesis evaluates four model sizes — **7B, 13B, 34B-int4, 70B-int4** (plan §2.2). One M4 Pro 48 GB is the compute envelope (plan §1). No backend serves all four sizes well:

* **MLX-LM** is native to Apple Silicon and fastest at fp16, but stops being practical above 13B at fp16 because of memory.
* **llama.cpp** with GGUF Q4\_K\_M is the only realistic path for 34B and 70B on 48 GB.
* **Ollama** wraps `llama.cpp` with an HTTP API and great DX, but adds a process boundary.
* **External APIs** are the only path for GPT-4o-mini (H6 judge, C3 cost arm) and Claude (cross-check, cost arm).

## Decision

A unified `InferenceBackend` Protocol with five concrete backends, selected per-experiment:

| Backend | Models | Use cases |
|---------|--------|-----------|
| `MlxBackend` | Llama-3.1-8B-Instruct (fp16), Qwen2.5-14B-Instruct (fp16) | 7B/13B inference; training (via PEFT). |
| `LlamaCppBackend` | Qwen2.5-32B-Instruct Q4\_K\_M, Llama-3.1-70B-Instruct Q4\_K\_M | 34B/70B inference. |
| `OllamaBackend` | Any Ollama tag | Dev convenience; quick iteration. |
| `OpenAIBackend` | `gpt-4o-mini` | H6 judge, C3 cost arm, LLM-as-judge. |
| `AnthropicBackend` | `claude-haiku-4-5`, `claude-sonnet-4-6` | Cost arm; cross-check on 10% sample. |

All five implement `complete()` and `embed()` (where applicable) and write to the cost ledger on every call.

**70B sanity check.** `LlamaCppBackend.__init__` runs a 5-prompt NarrativeQA mini-eval and **refuses to serve traffic** if F1 drops by more than 5 pp from a recorded baseline. Mitigation for plan-risk-register row 4 ("70B int4 on M4 Pro produces broken output that contaminates results"). The result is logged and propagates to `results/.../70b/`.

## Options considered

### Option A — Single backend (e.g. Ollama for everything)

Pros: simple. Cons: cannot fine-tune via PEFT; LoRA training requires MLX or PyTorch.

### Option B — Per-task backends with no unifying Protocol

Pros: zero abstraction overhead. Cons: experiment runners would need to know about each backend's API; cost ledger logic would be duplicated.

### Option C — Unified Protocol, per-size concrete *(chosen)*

Pros: Experiment runners write `backend = make_backend(model_size)` and stop caring. Cost ledger logic centralised. 70B sanity check encoded once.

## Trade-off analysis

The cost of the Protocol is a thin shim; the cost of *not* having it is duplicated retry / cost-tracking / sanity-check logic across five places.

## Consequences

**Easier.**
* `m6.experiments.cli run --backend=auto` picks the right backend by model size.
* Mocking inference in unit tests (use a dummy backend).
* Adding a CUDA backend for the doctoral phase.

**Harder.**
* Tracking GPU memory pressure when MLX and `llama.cpp` are both loaded — solved by lazy-init: backends load model weights only on first `complete()`.

## Action items

1. [x] Define `InferenceBackend` Protocol.
2. [x] Implement `MlxBackend`, `LlamaCppBackend`, `OllamaBackend`, `OpenAIBackend`, `AnthropicBackend`.
3. [x] Add the 70B NarrativeQA mini-eval to `LlamaCppBackend` startup.
4. [x] Wire the cost ledger writes.
5. [ ] Document model-card hashes for each model file under `docs/model_cards/`.
