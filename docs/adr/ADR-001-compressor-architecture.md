# ADR-001: Compressor architecture — pluggable interface with three families

**Status:** Accepted
**Date:** 2026-05-12
**Deciders:** Syed Abdullah Hassan (author), Lauri Lovén (academic supervisor), Asim Nadeem & Oskari Valkama (TalentAdore)

## Context

The thesis evaluates context compression for multi-agent coordination across a parameter space the size of `compressors × ratios × workloads × seeds × model_sizes`. The compressor is the most-iterated component: we train a new one for C4 (H5), train a second variant for H3 (training distribution), and need to compare against two off-the-shelf baselines on every experiment. Coupling the bus to a specific compressor would force a re-deploy on every change and make the C2 ratio sweep impractical.

External constraints:
* The M4 Pro 48 GB single-machine envelope rules out training anything larger than 13B at rank 8 (plan §4.3 risk register).
* MLX is the native fast path; PyTorch-MPS is the fallback for ops MLX lacks (plan §4.1).
* The plan explicitly names three compressor families (plan §2.2): LLMLingua-2, ICAE-style, instruction-aware filter.
* The C4 tag-preserving variant must be a *modification* of the ICAE soft-prompt compressor (plan §2.4), not a fork.

## Decision

Implement a **`Compressor` Protocol** that all variants conform to, with **four concrete classes** living under `src/m6/compressors/`:

```
Compressor (Protocol)
├── LLMLingua2Compressor    (hard-prompt; no training)
├── InstructionAwareFilter  (heuristic; no training)
├── ICAECompressor          (soft-prompt; trained on L_recon + λ·L_NCE)
└── TagPreservingICAE       (ICAE + per-slot TagHead; C4)
```

* `TagPreservingICAE` inherits from `ICAECompressor` and *adds* the `TagHead`, the joint loss term, and the recovery logic. Code reuse is achieved by composition (the tag head is a separate `nn.Module`), not by branching on a flag.
* All four return the same `CompressedSlot` type with a tagged-union `payload` field (`TextSummary | SoftEmbed | TokenIds`). Storage and access layers never branch on compressor family.

## Options considered

### Option A — One concrete `Compressor` class with a `family` flag

| Dimension | Assessment |
|-----------|------------|
| Complexity | High — every method branches on `self.family`. |
| Cost | Low up-front, high over time. |
| Scalability | Bad — adding C4 requires touching every method. |
| Team familiarity | High. |

**Pros.** Fewer files; less indirection.
**Cons.** Couples evaluation logic to compressor internals. Test surface explodes.

### Option B — Pluggable `Protocol` with one class per variant *(chosen)*

| Dimension | Assessment |
|-----------|------------|
| Complexity | Medium — clean separation of concerns. |
| Cost | One-time investment in the protocol + a base class. |
| Scalability | Excellent — new variants are new files; tests are per-class. |
| Team familiarity | Medium — Protocol is in standard library. |

**Pros.** Strict separation of trained / untrained / heuristic. C4 inherits from ICAE cleanly. Storage and access layers stay compressor-agnostic.
**Cons.** Slightly more boilerplate.

### Option C — Adopt LangChain's `Runnable` interface and call upstream `llmlingua` directly

| Dimension | Assessment |
|-----------|------------|
| Complexity | Low for the LLMLingua path. |
| Cost | Adds LangChain to the dependency tree. |
| Scalability | Bad — ICAE and the tag head are not natural LangChain runnables. |
| Team familiarity | High. |

**Pros.** Instant LLMLingua wrapper.
**Cons.** Forces a heavy dependency on a stack the thesis does not otherwise use. Locks the C4 variant into a programming model that does not fit a soft-prompt encoder.

## Trade-off analysis

Option B trades a small one-time boilerplate cost for permanent decoupling between compressor implementations and everything downstream. The C4 variant (the thesis's headline contribution) is materially easier under Option B because it inherits from `ICAECompressor`. Option C was rejected because LangChain has no natural fit for a soft-prompt encoder; the wrapper boilerplate would re-emerge inside the Runnable, just hidden behind LangChain conventions.

## Consequences

**Easier.**
* Swapping compressors at experiment runtime via `--compressor=icae-tag`.
* Mocking the compressor in unit tests; the memory bus is testable without any model weights.
* Adding a new compressor family for D7 (e.g. KVCOMM-style cache compression).

**Harder.**
* Performance optimisations that span compressor + access layer (none anticipated at thesis scale).
* Sharing tokenisation state across families — handled by exposing `tokenizer_id` on the protocol.

**Revisit when.**
* The doctoral phase wants cross-tokenizer compressed exchange. The Protocol's `tokenizer_id` field is the seam.

## Action items

1. [x] Define `Compressor` Protocol + `CompressedSlot` dataclass.
2. [x] Implement `LLMLingua2Compressor`.
3. [x] Implement `InstructionAwareFilter`.
4. [x] Implement `ICAECompressor` (encoder LoRA + frozen decoder).
5. [x] Implement `TagPreservingICAE` (subclass of `ICAECompressor`).
6. [ ] Run NarrativeQA + HotpotQA calibration to confirm LLMLingua-2 within 2–3 pp of reported.
