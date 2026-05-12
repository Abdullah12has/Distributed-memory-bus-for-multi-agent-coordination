# Technical Reference — m6-thesis

> **Audience.** This document is the canonical engineering reference for the code in `src/m6/`. It maps every claim in `plan.md` to a concrete code module, a paper, and a falsifiable measurement. Anyone writing or reviewing code should read this *before* opening the source tree.
>
> **Status.** Living document. Pinned at commit-time to the `plan.md` revision dated **May 2026**. Every section header carries the back-pointers it is grounded in.
>
> **Authoring conventions.**
> 1. Every empirical claim must point to a *single* paper, a *single* page in one of the bundled internal PDFs, or a *single* measurement that the codebase produces and that lives in `results/`.
> 2. Where the plan and a paper disagree, the **plan wins** and the disagreement is footnoted.
> 3. Wallclocks are stated for the **M4 Pro 48 GB single-machine envelope** (plan §1, §5.4). Any external-cluster aside is marked *non-critical-path*.

---

## Table of contents

1. [Scope, goals, and non-goals](#1-scope-goals-and-non-goals)
2. [System architecture — three-layer memory bus](#2-system-architecture--three-layer-memory-bus)
3. [Data model](#3-data-model)
4. [The eight hypotheses — implementation specification](#4-the-eight-hypotheses--implementation-specification)
5. [Compressor framework (C2 + C4)](#5-compressor-framework-c2--c4)
6. [Benchmark (C1)](#6-benchmark-c1)
7. [RAG pipeline catalogue (C3)](#7-rag-pipeline-catalogue-c3)
8. [Inference backends](#8-inference-backends)
9. [Agent runtime](#9-agent-runtime)
10. [Evaluation and statistics](#10-evaluation-and-statistics)
11. [Results layout and reproducibility](#11-results-layout-and-reproducibility)
12. [Grounding sources — what each cited paper actually says](#12-grounding-sources--what-each-cited-paper-actually-says)
13. [Risks, kill-switches, and time-boxes](#13-risks-kill-switches-and-time-boxes)
14. [Glossary](#14-glossary)

---

## 1. Scope, goals, and non-goals

### 1.1 Thesis statement (verbatim from `plan.md` §1)

> *"This thesis designs, implements, and evaluates a distributed memory bus with a context-compression layer for multi-agent institutional systems. It contributes (i) a multi-agent coordination benchmark, (ii) an empirical characterization of how context compression affects multi-agent coordination quality across model sizes 7B–70B, (iii) a catalogue of three RAG + compression pipeline architectures evaluated under matched conditions, and (iv) a tag-preserving compressor variant integrated with a reference memory-bus implementation that exposes the integration interfaces the FCG platform requires."*

### 1.2 In scope

| Contribution | What the code must produce | Plan refs |
|--------------|---------------------------|-----------|
| **C1** — multi-agent coordination benchmark | Reproducible synthetic Vignette-7-style benchmark with three workload families, 150 instances, coordination-quality metrics, synthetic ACL tags. Single-command regeneration. | §2.1, §4.2 |
| **C2** — empirical compression characterisation | Three compressors × five ratios × five seeds × four model sizes on C1, with paired-bootstrap CI. Headline output: existence/shape/scaling of the coordination cliff τ\*. | §2.2, §4.3, §4.4 |
| **C3** — RAG + compression pipeline catalogue | Three pipelines (P1 compress→retrieve, P2 retrieve→compress, P3 joint) on FAISS + LlamaIndex, benchmarked under matched retrieval quality with a €/query cost model fit to **GPT-4o-mini** and **Claude Haiku 4.5** prices plus amortised local cost. | §2.3, §4.3 |
| **C4** — tag-preserving compressor + reference memory-bus integration | ICAE variant with per-slot tag-prediction head; FastAPI service exposing `write` / `read` / `subscribe` / `audit`; policy-enforcement middleware; SQLite audit log. | §2.4, §4.4, §6 |

### 1.3 Explicitly out of scope (plan §1, §6.3)

* Production-grade governance enforcement. The tag-preserving compressor is a **research prototype with measured properties**, not a compliance tool.
* Cross-tokenizer or cross-model-family compressed exchange.
* Live production deployment on the FCG platform — the deliverable is a reference FastAPI service.
* Fully distributed memory bus with Redis Cluster + NATS + OpenTelemetry. The repo *is structured so this can be swapped in later* (see §2.5), but D7 owns that work.

### 1.4 Compute envelope

| Workload | Path | Notes |
|----------|------|-------|
| 7B / 13B fp16 inference | MLX-LM on M4 Pro | Apple-Silicon-native; primary path. |
| 7B LoRA fine-tuning | MLX + PEFT, rank 16, batch 4, accum 8 | ≤3 days wallclock (plan §4.3). |
| 13B LoRA fine-tuning | MLX rank 8, *if memory allows* | Time-boxed, stretch (plan risk 3). |
| 34B int4 inference | llama.cpp + GGUF (Q4\_K\_M) | ~5–10 tok/s; focused partial sweep only. |
| 70B int4 inference | llama.cpp + GGUF (Q4\_K\_M) | ~3–5 tok/s; **single-point characterisation**, not full sweep. |
| External API arm | OpenAI + Anthropic clients | Cost-tracked per call. |

Everything else (eval, agent orchestration, FAISS) is CPU-bound on the same host.

---

## 2. System architecture — three-layer memory bus

### 2.1 Layers (plan §6.1)

```
┌──────────────────────────────────────────────────────────────────┐
│ ACCESS LAYER  ── FastAPI service                                 │
│  POST   /v1/write   (fragment, tags) → slot_id                   │
│  GET    /v1/read/{slot_id}?requester_acl=… → CompressedSlot|403  │
│  POST   /v1/subscribe (query, ttl)  → SSE stream                 │
│  GET    /v1/audit/{slot_id}         → provenance chain           │
│  + ACL middleware, structured logging, OTel hooks                │
├──────────────────────────────────────────────────────────────────┤
│ COMPRESSION LAYER  ── pluggable Compressor interface             │
│  compress(fragment, task_hint, tags) → CompressedSlot            │
│  Variants:                                                       │
│   V1  dense-embedding   (cheap baseline, no training)            │
│   V2  ICAE-style soft-prompt    (dual-objective trained)         │
│   V3  instruction-aware filter  (heuristic, no training)         │
│   V4  V2 + per-slot tag-prediction head    (C4)                  │
├──────────────────────────────────────────────────────────────────┤
│ STORAGE LAYER                                                    │
│  SQLite (audit log, append-only via trigger)                     │
│  in-memory dict (active scratchpad, TTL)                         │
│  FAISS-CPU (compressed-slot retrieval)                           │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Component → module map

| Layer | Component | Code module |
|-------|-----------|-------------|
| Access | FastAPI app | `m6.memory_bus.api` |
| Access | Policy middleware | `m6.memory_bus.policy` |
| Access | Pydantic schemas | `m6.memory_bus.schemas` |
| Compression | Compressor base class | `m6.compressors.base` |
| Compression | LLMLingua-2 wrapper | `m6.compressors.lingua2` |
| Compression | ICAE soft-prompt | `m6.compressors.icae` |
| Compression | Instruction-aware filter | `m6.compressors.filter` |
| Compression | Tag-preserving variant | `m6.compressors.tag_preserving` |
| Compression | Training (joint loss) | `m6.compressors.training.train_icae` |
| Storage | SQLite audit log | `m6.memory_bus.storage.sqlite_audit` |
| Storage | Scratchpad | `m6.memory_bus.storage.scratchpad` |
| Storage | FAISS vector store | `m6.memory_bus.storage.vector_store` |

### 2.3 Architecture grounding — what we kept, what we changed

The three-layer split is **lifted directly from MemIndex (Saleh et al., ACM TAAS 2025)**, which is the architecture the thesis explicitly extends ("baseline architecture extended by this thesis", plan §9.5). Two material differences:

1. **Compression is a first-class layer**, not an optimisation. MemIndex treats memory entries as opaque; we make every read pass through a `Compressor.compress(...)` call so the experimental knob is a parameter of the system, not a downstream consumer.
2. **Per-slot tags are part of the data model**, not metadata attached out-of-band. The provenance/ACL bitmask is inherited and is itself a target of measurement (C4).

The bus-vs-broker terminology is grounded in the **Saleh et al. *Message Brokers for GenAI* survey (ACM CSUR 2025)**. The survey's reference GenAI-agent model — perception (sensors, tools, broker) + brain (memory, sub-goal decomposition, chain-of-thought, self-critic) + actuation (Fig. 3, p. 14) — is the topology the planner-worker-critic loop instantiates. We adopt **at-least-once semantics with acknowledgments and a durable persistent log** (Saleh CSUR p. 12), which here is the SQLite audit log; the in-memory scratchpad is ephemeral and is allowed to lose state on crash because the audit log is the source of truth.

### 2.4 Boundary with the FCG platform stack

The thesis ships a **single FastAPI service**. The FCG software architecture (`software-architecture.pdf` §2) specifies a dual messaging topology — NATS (1–5 ms ephemeral) for the real-time path and Kafka (5–50 ms durable, the source of truth and audit trail) for the persistent path. The thesis's reference implementation collapses these into **SQLite + an in-memory dict + an HTTP API**, on the grounds that:

* The compute envelope is one machine. NATS + Kafka on the same M4 Pro adds operational complexity without adding empirical signal.
* The FCG architecture document explicitly contemplates a 150–200 ms synchronous-path latency budget (`software-architecture.pdf` p. 10); SQLite + FastAPI sit comfortably under that on a single host.
* The compression-layer API is what FCG adopts. Whether the wire is NATS / Kafka / HTTP is a layer-2 decision the doctoral phase makes (plan §6.3).

What is *preserved* from the FCG stack so D7 can swap things in:

* Event types from `software-architecture.pdf` §4 are recreated as Pydantic models in `m6.memory_bus.schemas` (`SliceRegistered`, `BidSubmitted`, `EpochResult`, `TranscriptCommit`, `AuditSignal` — see §3.4).
* The audit-log table schema mirrors the `audit_transcript` table from `software-architecture.pdf` §3.5 (columns: `epoch_id`, `bids_hash`, `alloc_hash`, `payments_hash`, `prev_hash`, `chain_hash`).
* The transcript hash chain `H_t = SHA-256(epoch_id || bids_hash || alloc_hash || payments_hash || H_{t-1})` is implemented in `m6.memory_bus.storage.sqlite_audit.chain_hash(...)` and tested with a tamper-detection unit test.

### 2.5 What D7 (the doctoral phase) takes over

`plan.md` §6.3 names five doctoral-phase items. The repo is structured so these are drop-in replacements, not rewrites:

1. **Storage swap.** `m6.memory_bus.storage` exposes three protocols — `AuditLog`, `Scratchpad`, `VectorStore`. SQLite/in-memory-dict/FAISS today; Postgres/Redis Cluster/Qdrant tomorrow.
2. **Cross-tokenizer compressed exchange.** Out of scope (plan §1). The compressor interface carries a `tokenizer_id` field so D7 can layer in a tokeniser adapter.
3. **Cryptographic commitment infrastructure.** The hash-chain entry point exists; the `software-architecture.pdf` Bayesian type-tracker (`L_t = ρ·L_{t-1} + log(Pr(z_t|strategic)/Pr(z_t|honest))`) is mentioned in `docs/adr/ADR-005-future-cryptographic-commit.md` as the doctoral-phase upgrade.
4. **Federated memory bus.** The bus is single-host. D7 federates.
5. **Live FCG deployment.** The FastAPI service is the contract. The deployment is D7's.

---

## 3. Data model

### 3.1 Core types (Pydantic)

```python
# src/m6/memory_bus/schemas.py
class TagVector(BaseModel):
    """
    Provenance + ACL metadata that travels with every fragment and slot.
    ACL bitmask is uint64 — 64 named capabilities. Classification levels are a
    5-tier lattice (PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED < SECRET).
    """
    acl_mask:        int             # uint64 capability bitmask
    classification:  Literal[0, 1, 2, 3, 4]   # 0=PUBLIC, 4=SECRET
    source_ids:      tuple[str, ...]          # provenance back-pointers
    issued_at:       datetime
    inherited_from:  tuple[str, ...] = ()     # parent slot_ids if any

class Fragment(BaseModel):
    fragment_id: str
    text:        str
    tags:        TagVector

class CompressedSlot(BaseModel):
    slot_id:        str
    payload:        SlotPayload   # tagged union: TextSummary | SoftEmbed | TokenIds
    tags:           TagVector
    audit_pointers: tuple[str, ...]      # rowids in the SQLite audit log
    compressor_id:  str
    ratio:          float
    created_at:     datetime
```

`SlotPayload` is a tagged union because the three compressor families produce different representations:
* `TextSummary` — a string (LLMLingua-2 hard-prompt; instruction-aware filter; xRAG-style stub).
* `SoftEmbed` — a `numpy.ndarray` of shape `(num_slots, d_model)` (ICAE).
* `TokenIds` — a list of token ids in the encoder's vocabulary (AutoCompressor and the H3 dialogue-trained variant).

### 3.2 Tag semantics

Tags are **synthetic** (plan §4.2). The thesis does not use real ACL data. The bitmask is a uint64 with two distributions tested:
* **uniform** — each capability bit set independently with probability 0.5.
* **skewed** — exponential family so a handful of bits dominate, modelling typical real ACL distributions (most fragments are "low" classification).
* **hierarchical** — bits clustered by classification level, so high-classification fragments carry a strict superset of low-classification bits.

The classification tier is a 5-tier lattice. Lifted from the **NIST AI RMF 1.0 (2023)** lattice + the **Park et al. *Collaborative Memory* (arXiv 2505.18279, 2025)** dynamic-access-control framing.

### 3.3 The audit log

| Column | Type | Notes |
|--------|------|-------|
| `rowid` | INTEGER PK auto | append-only |
| `slot_id` | TEXT NOT NULL |  |
| `event_type` | TEXT CHECK in (`WRITE`, `READ`, `SUBSCRIBE`, `DENY`, `COMPRESS`, `EVICT`) |  |
| `requester_acl` | INTEGER | uint64 stored as int64 |
| `result` | TEXT CHECK in (`OK`, `DENIED`, `ERROR`) |  |
| `prev_hash` | BLOB(32) | SHA-256 of the previous row's `chain_hash` |
| `payload_hash` | BLOB(32) | SHA-256 of the event payload |
| `chain_hash` | BLOB(32) | SHA-256(prev_hash ‖ payload_hash) |
| `created_at` | TEXT NOT NULL | ISO-8601 UTC |

The chain hash mirrors the `audit_transcript` table from `software-architecture.pdf` §3.5 verbatim modulo the column names (we collapse `bids_hash`, `alloc_hash`, `payments_hash` into a single `payload_hash` because the thesis bus does not run an auction).

**Append-only enforcement.** A SQL trigger raises on any `UPDATE` or `DELETE` of `audit_log`. Implementation lives in `m6.memory_bus.storage.sqlite_audit.SCHEMA_SQL`.

### 3.4 Event types and Pydantic mirrors

| Event | Schema | When emitted |
|-------|--------|--------------|
| `SlotWritten` | `(slot_id, tags, compressor_id, ratio)` | every `POST /v1/write` |
| `SlotRead` | `(slot_id, requester_acl, granted)` | every `GET /v1/read` |
| `SubscriptionOpened` | `(subscription_id, query_hash, ttl_s)` | every `POST /v1/subscribe` |
| `PolicyDenied` | `(slot_id, requester_acl, reason)` | denied reads or denied writes |
| `AuditChainCommit` | `(rowid, chain_hash)` | every `WRITE`/`READ`/`DENY` |
| `CompressorChanged` | `(compressor_id, ratio, model_card_hash)` | model swap |

These match (without trying to re-implement) the event-sourcing taxonomy in `software-architecture.pdf` §4. The doctoral phase substitutes Kafka topics with the same names.

### 3.5 Cost model accounting

Every external API call writes a row to `cost_ledger`:

| Column | Type |
|--------|------|
| `experiment_id` | TEXT |
| `provider` | TEXT — `openai` / `anthropic` / `local-mlx` / `local-llamacpp` |
| `model` | TEXT |
| `input_tokens` | INTEGER |
| `output_tokens` | INTEGER |
| `eur_cost` | REAL |
| `wallclock_ms` | INTEGER |
| `created_at` | TEXT |

Pricing constants live in `m6.pipelines.cost_model.PRICING`. The frontier-cloud-pricing baseline (`USD 3 / 1M input, USD 15 / 1M output ≈ EUR 2.76 / EUR 13.80`) is grounded in `financial-analysis-university-ai-service-economy.pdf` §6, p. 10. The local-inference amortised cost (EUR 0.05/1M tokens for ConfidentialMind-style on-prem) is from the same page.

---

## 4. The eight hypotheses — implementation specification

Each hypothesis section answers **(a) what does the code need to compute, (b) what paper grounds it, (c) which module owns it, (d) what's the falsification target, (e) what's the statistical test.**

### 4.1 H1 — QA accuracy is a poor predictor of coordination success

**Falsifiable claim (plan §3, H1):** Spearman ρ between single-agent QA accuracy delta and multi-agent coordination success delta across matched compression ratios is **below 0.6 on at least two of the three compressors at 7B.**

**What the code computes.** For each `(compressor c, ratio r, workload w, seed s)` cell:
1. Run the single-agent QA derivative of the workload — the same source documents, but with a single agent answering the planner's seed question. Record F1 / EM.
2. Run the full planner-worker-critic loop with the same `(c, r, w, s)`. Record final task success, sub-task-assignment accuracy, rounds-to-completion.
3. Compute `Δ_qa = qa_at_r − qa_at_r=1` and `Δ_coord = coord_at_r − coord_at_r=1`.
4. Across the union of cells per compressor, compute Spearman ρ between `Δ_qa` and `Δ_coord`.

**Module.** `m6.experiments.h1_qa_vs_coordination`.

**Grounding papers.**
* **Anthropic, *How we built our multi-agent research system* (June 2025)** — the published industry analogue that motivates H1: their finding that *token usage explains 80% of performance variance* (plan §9.2). H1 asks whether the standard single-agent QA metric is still informative under coordination.
* **Liu et al. *Lost in the Middle* (TACL 2024)** — the canonical counter-example: single-agent F1 looks fine while the model misses the middle. We use it as a single-agent calibration anchor.

**Statistical test.** Spearman ρ with 95% bootstrap CI (10K resamples). Failure to reject `ρ ≥ 0.6` is *thesis-worthy* per plan §3 ("falsification of any of them is itself a thesis-worthy result").

### 4.2 H2 — A coordination cliff τ* exists and is task-dependent

**Falsifiable claim:** For each `(compressor, workload)` cell at 7B, there is a compression ratio τ* such that coordination success at `r > τ*` falls by **≥30%** relative to `r < τ*`. τ* varies by workload but **not by compressor family within ±20%**.

**What the code computes.**
1. Fit a piecewise-linear function `f(r; a, b, τ)` to the (compression ratio → coordination success) curve per cell. Two linear pieces meeting at τ; fitted by minimising MSE with `scipy.optimize.differential_evolution` on `τ ∈ [1, 16]`.
2. The "cliff" is defined as the breakpoint τ where the slope of the right piece exceeds the slope of the left piece by a threshold and the relative drop on the right exceeds 30%.
3. Sanity-tested by **Wilcoxon signed-rank** comparing `coord(r < τ*)` vs `coord(r ≥ τ*)` across seeds (plan §5.3).

**Module.** `m6.evaluation.cliff_fitting.fit_piecewise(...)` + `m6.experiments.h2_coordination_cliff`.

**Grounding papers.**
* **Rae et al. *Compressive Transformers* (ICLR 2020)** — establishes that compressed memory has a degradation curve, but reports smooth monotonic decay. H2 asks whether *multi-agent coordination* breaks this monotonicity.
* **Jiang et al. *LongLLMLingua* (ACL 2024)** — reports continuous accuracy-vs-ratio curves on single-agent QA. We replicate their methodology, then re-instrument on C1.
* **Pan et al. *LLMLingua-2* (ACL Findings 2024)** — the same, with task-agnostic data distillation.
* **Anthropic, *How we built our multi-agent research system* (June 2025)** — the 80%-token-variance finding is the closest published analogue.

### 4.3 H3 — Training distribution matters: dialogue traces beat QA at matched accuracy

**Falsifiable claim:** Same compressor, same hyperparameters, same dual-objective loss; trained on dialogue traces vs on monolithic QA. Compares them on C1 at **matched single-agent QA accuracy**. The dialogue-trained variant has higher coordination success.

**What the code computes.**
1. Construct ~5K planner-worker-critic dialogue traces. Source: synthetic — generated by the C1 generator with no compression so the traces are clean. Cross-check on a small sample from public AutoGen / MetaGPT demos (verbatim is unrelated; we use them for structural diversity).
2. Fine-tune the ICAE-style compressor on (a) QA pairs and (b) dialogue traces. Same hyperparameters, same compute budget.
3. Find the operating-ratio pair `(r_a, r_b)` such that **single-agent QA accuracy is matched ±1 pp** between (a) and (b).
4. At that matched operating point, run C1 and report `(coord_b − coord_a)`. Positive at p < 0.05 (paired bootstrap) → H3 supported.

**Module.** `m6.experiments.h3_training_distribution` + `m6.compressors.training.dataset.DialogueDataset`.

**Grounding papers.**
* **Wu et al. *AutoGen* (2023)** — provides the trace shape: planner-as-orchestrator and tool-using workers.
* **Hong et al. *MetaGPT* (ICLR 2024)** — provides the SOP (standardised operating procedure) framing for sub-task assignment.
* **Haseeb. *Context Engineering for Multi-Agent LLM Code Assistants* (arXiv 2508.08322, 2025)** — explicitly names training-distribution mismatch as a cause of coordination breakdown.

### 4.4 H4 — RAG pipeline placement matters

**Falsifiable claim:**
* P1 (compress→retrieve) dominates P2 (retrieve→compress) **on storage-bounded settings** (FAISS index size capped).
* P2 dominates P1 **on accuracy-bounded settings** (retrieval recall capped).
* P3 (joint) closes the gap on a **combined accuracy × € score**.
* Effect size ≥ **5 pp F1** on C1 family (a).

**What the code computes.** For each `(pipeline P, budget mode B)`:
* `B = storage-bounded` — FAISS index size capped at 100 MB. Both P1 (small compressed chunks) and P2 (full chunks) compete under that ceiling.
* `B = accuracy-bounded` — retrieval recall@10 capped at 0.85. Adjust the embedding granularity until both reach that recall.
* P3 picks at retrieval time: chunks with `score > θ` go straight in; chunks with `score < θ` are compressed first. θ swept.
* Headline metric: F1 on the workload + €/query (see `m6.pipelines.cost_model`).

**Module.** `m6.pipelines.{p1,p2,p3}_*` + `m6.experiments.h4_rag_placement`.

**Grounding papers.**
* **Lewis et al. *RAG* (NeurIPS 2020)** — the baseline architecture.
* **Sarthi et al. *RAPTOR* (ICLR 2024)** — hierarchical summarisation; informs the P1 pre-compression layout.
* **Edge et al. *GraphRAG* (2024)** — graph-summary RAG; not directly compared but informs P3's relevance-routing logic.
* **Gutiérrez et al. *HippoRAG / HippoRAG 2* (NeurIPS 2024 / ICML 2025)** — memory-organisation-as-graph; we cite it in the discussion of why P3 looks the way it does.
* **Asai et al. *Self-RAG* (ICLR 2024)** — reflection-token gating; structurally similar to P3's score-conditional routing.
* **Cheng et al. *xRAG* (arXiv 2405.13792, 2024)** — extreme-compression-aware RAG; the compress-step in P1 follows xRAG's hard-prompt approach.
* **Guo et al. *Dynamic context compression for RAG* (2025)** — the closest published analogue to P3.
* **Anthropic, *Contextual Retrieval* (Sep 2024)** — chunk-level context prepending; used as a baseline pre-processor for P1.
* **Anthropic, *Managing context on the Claude Developer Platform: context editing and the memory tool* (Oct 2025)** — reports a **84% token reduction on a 100-turn web-search evaluation** via context editing (plan §9.2). This is the closest production analogue to what P3 does.

### 4.5 H5 — Tag preservation ≥ 85% at 4× with ≤5 pp accuracy drop

**Falsifiable claim:** The tag-preserving compressor preserves provenance tags **at rate ≥85% at 4× compression** with accuracy degradation **≤5 pp** relative to the non-tag-preserving baseline.

**What the code computes.**
1. Add a per-slot tag-prediction head on top of the ICAE soft-prompt slots. Head: small MLP from the slot embedding → (acl_logit, classification_logit). Loss: BCE-with-logits for the 64-bit ACL, cross-entropy for the 5-tier classification.
2. Joint loss: `L = L_recon + λ_NCE · L_NCE + λ_tag · L_tag`. λ_tag swept in `{0.1, 0.3, 1.0, 3.0}`.
3. **Tag preservation rate.** Recover tags from each compressed slot via the head; compare to the **union of source-fragment tags** (a fragment's tag is preserved iff *at least one* of its bits or its classification level is recovered).
4. **Accuracy delta.** Same C1 evaluation as the H2 baseline, head added but not used for reading.

**Module.** `m6.compressors.tag_preserving` + `m6.evaluation.metrics.tag_preservation` + `m6.experiments.h5_tag_preservation`.

**Grounding papers.**
* **Ge et al. *ICAE* (ICLR 2024)** — the soft-prompt architecture H5 modifies.
* **Chevalier et al. *AutoCompressor* (EMNLP 2023)** — provides the reconstruction loss formulation and shows that LoRA adapters suffice for the encoder side.
* **Mu et al. *Gist Tokens* (NeurIPS 2023)** — alternate per-slot summary mechanism; cited in the discussion as a baseline.
* **Park et al. *Collaborative Memory: Dynamic Access Control* (arXiv 2505.18279, 2025)** — the published precedent for ACL-aware memory in multi-agent systems.
* **Zhou et al. *Privacy-Aware RAG* (arXiv 2503.15548, 2025)** — privacy-preserving retrieval, structurally analogous.

### 4.6 H6 — Summary-level inference disclosure is measurable and the tag-preserving compressor reduces it

**Falsifiable claim:** A held-out reader (gpt-4o-mini) recovers protected facts from compressed summaries at a rate **substantially above** the priors-only chance baseline when the tag-preserving compressor is **not used** (showing the metric measures something real), and at a **lower** rate when it **is** used at matched compression ratio.

**What the code computes.**
1. Pick a held-out set of `(source_fragment, protected_fact)` pairs. Protected facts are factoids drawn from fragments with classification level ≥ `CONFIDENTIAL`. Same fragments are used to build the "priors-only" baseline by giving the reader only the workload's public preamble.
2. Compress each fragment with **(a)** baseline ICAE, **(b)** the tag-preserving variant, at matched ratio.
3. Show the reader only the **compressed summary, with no quoted source text**. The reader is gpt-4o-mini with a structured prompt asking it to produce yes/no answers to (protected\_fact)-themed questions.
4. Disclosure rate = (true-positive recovery rate). Compare priors-only / baseline / tag-preserving at the same ratio.

**Module.** `m6.experiments.h6_inference_disclosure` + `m6.evaluation.metrics.inference_disclosure`.

**Grounding papers.**
* **Li et al. *SecurityLingua* (CoLM 2025)** — adversarial-prompt construction for compression security; the stretch goal S2 reuses this.
* **Bassit & Boddeti. *SecureRAG* (2025)** — privacy-preserving RAG; informs the threat model.
* **Zhao. *FRAG* (2024)** and **Addison et al. *C-FedRAG* (2024)** — federated privacy-aware RAG; informs the metric design for the doctoral phase.

### 4.7 H7 — The cliff τ* shifts with model size

**Falsifiable claim:** Across `{7B, 13B, 34B-int4, 70B-int4}`, τ* increases monotonically with model size on **at least 2 of 3 workload families**. 7B and 13B are full sweeps; 34B-int4 is focused partial; 70B-int4 is **single-point characterisation** at the τ* identified at 13B/34B.

**What the code computes.** Same machinery as H2, but iterated across `INFERENCE_BACKEND × MODEL_SIZE`:
* 7B/13B → MLX-LM at fp16.
* 34B → `llama.cpp` GGUF Q4\_K\_M. Focused partial sweep at `r ∈ {2, 4, 6, 8, 10}` centred on the 13B-suspected τ*.
* 70B → `llama.cpp` GGUF Q4\_K\_M. **One ratio**, at the suspected τ*, with 5 seeds. Sanity-checked first by running NarrativeQA on the 70B int4 build and verifying F1 is within 5 pp of the reported number.

**Module.** `m6.experiments.h7_model_size_scaling` + `m6.inference.{mlx_backend, llamacpp_backend}`.

**Grounding papers.**
* **Hsieh et al. *RULER* (2024)** — establishes that long-context performance scales non-monotonically with model size in some tasks; we adopt their score-by-effective-context framing for the 70B sanity check.
* **Yen et al. *HELMET* (ICLR 2025)** — long-context capability benchmark; calibration anchor for the 13B/34B/70B sweep.
* **Rajasekaran et al. *Effective context engineering for AI agents* (Anthropic, 2025)** — names compaction, tool-result clearing, memory, and just-in-time retrieval as the four primitives. The 70B single-point is justified by the plan-§4.4 model-size argument and grounded against this taxonomy.

### 4.8 H8 — Findings transfer to real M0/M1/M2 traces

**Falsifiable claim:** On a subset of multi-agent workflows reconstructed from real M0/M1/M2 traces, the qualitative shape of the coordination-vs-compression curve matches synthetic results **within ±15% on τ*** and **±10 pp on coordination success**. **Gated on M0/M1/M2 readiness** — if the agents are not delivered, H8 is documented-as-deferred per `docs/scope-signoff.md`.

**What the code computes.**
1. With Faisal Khan (M1, Contract DB agent) and Vu Truong (M2, Moodle/Patio platform comparison harness), identify 2–3 cross-system workflows that can be reconstructed from real traces.
2. Reformulate each as a `Workload` instance loadable by C1's runner.
3. Run the H2 procedure on these workflows. Compare τ* and coordination-success curves to synthetic.

**Module.** `m6.experiments.h8_real_trace_transfer` + `m6.corpus.loader.RealTraceLoader`.

**Grounding papers.**
* **Saleh et al. *MemIndex* (ACM TAAS 2025)** — the institutional memory architecture; the workflow shapes mirror MemIndex's event timeline.
* **`use-case-university-ai-service-economy.pdf` §3.7** — *Period-end project reporting* (Vignette 3.7) is the canonical real-trace workflow. The PDF describes a Phase-2 cost of **EUR 2.15** per report achieved via **8 parallel specialised agents + 80% cloud-payload reduction** (p. 9). This is the design target our C1 family (a) — cross-document fact aggregation — models.

---

## 5. Compressor framework (C2 + C4)

### 5.1 The `Compressor` interface

```python
# src/m6/compressors/base.py
class Compressor(Protocol):
    compressor_id: str
    tokenizer_id:  str
    target_ratio:  float

    def compress(
        self,
        fragment: Fragment,
        task_hint: str | None = None,
        tags:      TagVector | None = None,
    ) -> CompressedSlot: ...

    def decompress(self, slot: CompressedSlot) -> str:
        """Return text reconstruction (best-effort; not all variants support exact recovery)."""

    def model_card(self) -> ModelCard: ...
```

Four concrete implementations:

| ID | Family | Trained? | Loss | Notes |
|----|--------|----------|------|-------|
| `lingua2` | hard-prompt | no | n/a | LLMLingua-2 token-level filter; XLM-RoBERTa-based. |
| `filter` | hard-prompt | no | n/a | Instruction-aware filter: heuristic + cross-encoder rerank. |
| `icae` | soft-prompt | **yes** | `L_recon + λ_NCE · L_NCE` | The C2 trainable arm. |
| `icae-tag` | soft-prompt | **yes** | `L_recon + λ_NCE · L_NCE + λ_tag · L_tag` | C4. |

### 5.2 ICAE training spec (plan §2.2, §4.2)

> *"The soft-prompt compressor is fine-tuned with a joint dual-objective loss following Ge et al. 2024 (ICAE) and Chevalier et al. 2023 (AutoCompressor): **L = L\_reconstruction + λ · L\_contrastive**."* — plan §2.2 (verbatim).

**Architecture.**
* Encoder: **Llama-3.1-8B-Instruct**, LoRA-adapted (rank 16, α=32, dropout=0.05, target modules `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`).
* Decoder: same backbone, **frozen** (no LoRA). This is the AutoCompressor pattern; cuts trainable parameters by ~50% and matches Ge et al. ICAE.
* Memory slots: `M` learnable [MEM] tokens prepended to the encoder input. Default `M = 128` for a 4× target ratio on 512-token fragments.

**Loss.**
* `L_recon` — token-level cross-entropy of the source fragment given the [MEM] slots, computed on the **frozen decoder**.
* `L_NCE` — InfoNCE over pairs in the batch:
  * **Positives.** (fragment_a, fragment_b) drawn from (i) the same source document, or (ii) the same planner-worker-critic dialogue trace (H3 dialogue variant).
  * **Negatives.** Other fragments in the same batch (in-batch negatives).
  * Similarity = mean-pooled [MEM] embedding cosine.
  * Temperature `τ` = 0.07 (standard SimCLR).
* `λ` swept in `{0.1, 0.3, 1.0}` on a validation split (plan §4.3).
* C4 adds `λ_tag · L_tag` with `L_tag = BCE(acl_pred, acl_true) + CE(class_pred, class_true)`.

**Optimiser.** AdamW, `lr = 3e-4`, `weight_decay = 0.0`, `betas = (0.9, 0.95)`, cosine schedule with 200-step linear warmup. Gradient accumulation 8. Batch 4. Sequence length 512 (fragment) + 128 (memory).

**MLX path.**
* Encoder LoRA via `mlx_lm.lora`.
* InfoNCE primitive: MLX 0.21 does **not** ship a batch contrastive op. We implement it manually as `mlx.nn.losses.cross_entropy(logits, labels)` over a `(B, B)` similarity matrix. Tested on a 1K synthetic corpus (plan §4.1 — "If MLX lacks an InfoNCE-friendly batch contrastive primitive, fall back to a manual cosine-similarity InfoNCE…")
* PyTorch-MPS fallback if any MLX op is missing: `torch.nn.functional.cross_entropy` on the same matrix.

**Compute budget.** ≤ 3 days wallclock for 7B at rank 16, ~5K traces, ~50 MB corpus. 13B at rank 8 is the upper limit (plan §4.3 risk register).

### 5.3 LLMLingua-2 wrapper

Thin adapter around the upstream `llmlingua` Python package (Pan et al. ACL Findings 2024). XLM-RoBERTa-based, runs natively on MPS. Single config: target ratio. **Validation target:** NarrativeQA F1 within **2 pp** of reported numbers; HotpotQA F1 within **3 pp** (plan §4.1). Failure to hit those is a Month-1 stop-the-line event.

### 5.4 Instruction-aware filter

Simple heuristic baseline. Two stages:
1. **Sentence-level filter.** TF-IDF + a small cross-encoder reranker (`BAAI/bge-reranker-base`) selects the top-k sentences whose relevance score w.r.t. `task_hint` exceeds θ.
2. **Token-level trim.** Drop stop-words and ≤2-character tokens until the target ratio is hit.

Deterministic given `(task_hint, fragment, target_ratio)`. No training. Useful as a *floor* baseline that the trained ICAE variant must beat by ≥3 pp F1 to justify its training cost.

### 5.5 Tag-preserving variant (C4)

Adds a `TagHead` module on top of the ICAE encoder.

```python
class TagHead(nn.Module):
    def __init__(self, d_model: int):
        self.acl_head:   nn.Linear = nn.Linear(d_model, 64)        # 64-bit ACL
        self.class_head: nn.Linear = nn.Linear(d_model, 5)         # 5-tier classification

    def forward(self, slot_embed: Tensor) -> tuple[Tensor, Tensor]:
        return self.acl_head(slot_embed), self.class_head(slot_embed)
```

**Tag loss.**
```
L_tag = BCE_with_logits(acl_pred, acl_true) + CE(class_pred, class_true)
```
**Aggregation rule for the source fragment's tag.** Slots inherit the **union** of their constituent fragments' ACL bits and the **maximum** of their classification levels (lattice-respecting aggregation).

---

## 6. Benchmark (C1)

### 6.1 Workload families (plan §4.2)

| Family | Code | Source | Skeleton |
|--------|------|--------|----------|
| (a) cross-document fact aggregation | `cross_doc_fact_aggregation` | 10–200 source docs | Vignette-7 style: planner asks "what is X across all sources?", workers retrieve, critic checks consistency. |
| (b) constraint-satisfaction planning | `constraint_satisfaction` | 3–8 capacity-bounded agents | Assign N sub-tasks under capacity constraints; verified with a constraint-checker. |
| (c) multi-step retrieval | `multi_step_retrieval` | heterogeneous source families | Chain queries: result of step k feeds step k+1; up to 4 levels. |

**Instance count.** ~50 per family, **150 total** (plan §4.2).

**Configuration knobs (per family).**
* Number of source documents: 10 / 50 / 200.
* Number of agents: 3 / 5 / 8.
* Sub-task complexity level: 1 / 2 / 3 / 4.
* Tag distribution: uniform / skewed / hierarchical.
* Source document length: 500 / 1500 / 5000 tokens.

### 6.2 Coordination-quality metrics (plan §5.2)

* **Final task success** — boolean: did the planner declare DONE with a critic-approved result?
* **Sub-task-assignment accuracy** — fraction of sub-tasks assigned to the agent the workload's ground-truth solver function expected.
* **Rounds-to-completion** — number of planner-worker-critic cycles before DONE.
* **Critic-flagged error rate** — fraction of rounds where the critic returned `STATUS=REVISE`.
* **Summary-level inference disclosure proxy** — gpt-4o-mini-as-reader from H6.

These are all computed by **scoring functions over AutoGen trace logs** (plan §4.2). Code lives in `m6.evaluation.metrics.coordination`. The scoring functions are pure functions of the trace; they do not call the model.

### 6.3 Corpus

Curated institutional subset, **PII-redacted**, ~50 MB (plan §4.1):
* Publications from M0 (coordination with Mohammad Abaeiani).
* Redacted contract excerpts from M1 (coordination with Faisal Khan).
* Moodle/Patio materials from M2 (coordination with Vu Truong).
* Padded with a sub-sampled BookCorpus chunk for breadth, only on the training side. Evaluation always uses the institutional subset.

Loader: `m6.corpus.loader.InstitutionalCorpus`. PII redaction: `m6.corpus.pii_redaction` runs an off-the-shelf NER (`en_core_web_lg`) plus a hand-curated phone-number / email regex over every loaded document. **Redaction is mandatory.** The loader refuses to return a document that has not passed the redaction stage.

---

## 7. RAG pipeline catalogue (C3)

### 7.1 P1 — compress→retrieve

```
   ┌──────────────┐    ┌─────────────────┐    ┌───────────────┐    ┌────────┐
   │ Source docs  │ →  │ Compress (any)  │ →  │ Embed + index │ →  │ FAISS  │
   └──────────────┘    └─────────────────┘    └───────────────┘    └────────┘
                                                                       │
            ┌──────────┐    ┌──────────────────────────┐               │
   Query → │ Retriever │ → │ Synthesiser (LLM)         │  ←────────────┘
            └──────────┘    └──────────────────────────┘
```
* Compression is **upstream** of indexing. The FAISS index stores compressed embeddings (or compressed text re-embedded).
* Storage advantage. Quality risk: information that is compressed away is forever gone.

**Implementation.** `m6.pipelines.p1_compress_retrieve.Pipeline1`. Uses LlamaIndex's `IngestionPipeline` with the compressor as a custom `TransformComponent`.

### 7.2 P2 — retrieve→compress (the classical LongLLMLingua setup)

```
   Query →  Retriever (full docs)  →  Compress retrieved set  →  Synthesiser
```
* Compression is **post-retrieval**. The FAISS index stores full chunks.
* Accuracy advantage on raw retrieval; cost advantage at inference; storage cost stays high.

**Implementation.** `m6.pipelines.p2_retrieve_compress.Pipeline2`. Uses LlamaIndex's `NodePostprocessor` interface; the postprocessor calls the compressor.

### 7.3 P3 — joint, conditional compression

```
   Query →  Retriever  →  for each retrieved chunk:
                              if score > θ_high:   keep verbatim
                              elif θ_low < score:  compress
                              else:                discard
                          →  Synthesiser
```
* Hybrid. The router uses the retriever's relevance score to decide whether to compress.
* Two thresholds. Swept; default `θ_high = 0.75, θ_low = 0.45` (cosine on `BAAI/bge-large-en-v1.5`).

**Implementation.** `m6.pipelines.p3_joint.Pipeline3` — also a `NodePostprocessor`, but with a per-node branch.

**Grounding.** This is the structural analogue of **Guo et al. *Dynamic context compression for RAG* (2025)** (plan §9.1). The `θ`-based routing is what makes P3 distinct from P2.

### 7.4 Cost model

```python
# src/m6/pipelines/cost_model.py
@dataclass(frozen=True)
class PricePerMillion:
    input_eur:  float
    output_eur: float

PRICING: dict[str, PricePerMillion] = {
    "gpt-4o-mini":             PricePerMillion(0.138, 0.552),   # USD 0.15 / 0.60 → EUR
    "claude-haiku-4-5":        PricePerMillion(0.92,  4.60),    # USD 1.00 / 5.00 → EUR
    "frontier-sonnet-tier":    PricePerMillion(2.76,  13.80),   # financial-analysis §6
    "local-mlx":               PricePerMillion(0.05,  0.05),    # on-prem amortised
    "local-llamacpp-int4":     PricePerMillion(0.05,  0.05),    # same
}
```

* The **frontier-sonnet-tier** number is grounded verbatim against `financial-analysis-university-ai-service-economy.pdf` p. 10 (*"USD 3 / 1M input tokens, USD 15 / 1M output tokens ≈ EUR 2.76 / EUR 13.80"*).
* The **local-amortised** number (EUR 0.05/1M tokens) is from the same page.
* The **GPT-4o-mini** and **Claude Haiku 4.5** prices reflect TalentAdore production pricing as of May 2026. Constants live in one place; experiments do not hard-code prices. **Update procedure:** on each pricing change, edit `PRICING`, rerun `make exp-h4`.

The headline cost metric is **€/workflow** (plan §5.2). The corollary metric carried for the industry-relevance narrative is **EUR 2.15 per period-end report** — the Phase-2 target from `use-case-university-ai-service-economy.pdf` Vignette 3.7.

---

## 8. Inference backends

| Backend | Module | Models served | Notes |
|---------|--------|---------------|-------|
| MLX-LM | `m6.inference.mlx_backend` | 7B fp16, 13B fp16 | Native to Apple Silicon; primary path. |
| llama.cpp + GGUF | `m6.inference.llamacpp_backend` | 34B Q4\_K\_M, 70B Q4\_K\_M | The only feasible 70B path on 48 GB. |
| Ollama | `m6.inference.ollama_backend` | DX / quick iteration | Wraps a localhost HTTP endpoint. |
| OpenAI | `m6.inference.api_backend.OpenAIBackend` | `gpt-4o-mini` | Used as the H6 judge and the C3 cost arm. |
| Anthropic | `m6.inference.api_backend.AnthropicBackend` | `claude-haiku-4-5`, `claude-sonnet-4-6` | Cross-check + cost arm. |

All backends implement the same `InferenceBackend` Protocol:

```python
class InferenceBackend(Protocol):
    backend_id: str
    model_id:   str

    async def complete(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        stop: list[str] | None = None,
        request_id: str | None = None,
    ) -> Completion: ...

    async def embed(self, text: str) -> np.ndarray: ...

    def cost_eur(self, input_tokens: int, output_tokens: int) -> float: ...
```

The `Completion` carries `text`, `input_tokens`, `output_tokens`, `wallclock_ms`, `eur_cost`. Every call appends to `cost_ledger` (§3.5).

**Retry policy.** `tenacity` exponential back-off, `5` retries, `2 → 32 s`. **Rate-limit policy.** Token-bucket per provider, configurable via env. **70B sanity.** Backend startup runs a 5-prompt NarrativeQA mini-eval and refuses to serve traffic if F1 drops by more than 5 pp from a recorded baseline.

---

## 9. Agent runtime

### 9.1 Why AutoGen v0.4

AutoGen is the most mature multi-agent framework with scratchpad-style state sharing (plan §6.2). The **v0.4 rewrite is a breaking API change** (released October 2024); we pin to v0.4.x because:
* The async event-driven core matches our SSE-based subscribe API.
* The `Team` / `RoundRobinGroupChat` primitives are a clean planner-worker-critic skeleton.
* The single-process harness from plan §4.1 is a thin shim over `RoundRobinGroupChat`.

### 9.2 Planner-worker-critic topology

```
   ┌─────────┐        ┌──────────┐        ┌────────┐
   │ Planner │ →→→→→→ │ Worker_i │ →→→→→→ │ Critic │
   └─────────┘        └──────────┘        └────────┘
        ▲                                       │
        └───────────── REVISE / DONE ←──────────┘
```

* **Planner** decomposes the workload into sub-tasks, assigns them, and tracks completion.
* **Workers** each carry a tool (retrieve, compute, write-to-scratchpad). They never talk to each other directly — communication is mediated by the planner.
* **Critic** receives the planner's draft answer and either `DONE`s it or returns `REVISE` with a structured complaint that re-enters the loop.

This is the **Saleh CSUR p. 14 GenAI-agent reference architecture** (perception + brain + actuation) instantiated as three actors. It is also the **Hong et al. *MetaGPT* SOP** pattern adapted to a single workflow.

### 9.3 Scratchpad bridge

The shared scratchpad is the **memory bus**. Every agent's writes to the scratchpad go through `POST /v1/write`. Reads go through `GET /v1/read`. This is what makes the memory bus the *experimental subject* rather than a hidden detail. With compression on, every write goes through the active `Compressor`; with compression off, the compressor is a no-op identity transform.

### 9.4 No-compression control

Every experiment runs a `compressor=none` control condition (plan risk register: "*AutoGen runtime bugs confound coordination measurements ... no-compression-control condition in every experiment; pin AutoGen version*"). If the control condition's variance dominates the signal-of-interest's variance, the experiment is *invalid* and is flagged in the results CSV.

---

## 10. Evaluation and statistics

### 10.1 Metrics (plan §5.2)

| Family | Metric | Module |
|--------|--------|--------|
| Quality | F1, EM, ROUGE-L, BERTScore | `m6.evaluation.metrics.qa` |
| Coordination | success, sub-task-acc, rounds, critic-flagged | `m6.evaluation.metrics.coordination` |
| Hallucination | DeepEval `Faithfulness`, RAGAS `faithfulness`, manual annotation on 100 random | `m6.evaluation.metrics.hallucination` |
| Compression | input/output token ratio, total tokens per workflow | `m6.evaluation.metrics.compression` |
| Cost | EUR/workflow via the cost ledger | `m6.evaluation.metrics.cost` |
| Latency | p50 / p95 ms/query, per-stage and end-to-end | `m6.evaluation.metrics.latency` |
| Tag preservation | fraction of slots whose recovered tags ⊇ source tags | `m6.evaluation.metrics.tag_preservation` |
| Inference disclosure | gpt-4o-mini-as-reader recall on protected facts | `m6.evaluation.metrics.inference_disclosure` |

### 10.2 LLM-as-judge

* **Judge.** `gpt-4o-mini` (cheap, deterministic with `temperature=0`).
* **Cross-check.** `claude-sonnet-4-6` on a **10% sample** (plan §5.2). If judge-vs-cross-check agreement drops below 0.85 (Cohen's κ), the judge is recalibrated.
* **Anti-bias.** The judge sees a position-randomised pair, never which compressor produced which answer.

### 10.3 Statistical protocol (plan §5.3)

* **5 seeds per condition.**
* **Bootstrap CI** alongside means (10 000 resamples; `scipy.stats.bootstrap`).
* **Paired bootstrap** for compressor-vs-compressor comparisons on matched instances.
* **Wilcoxon signed-rank** for the cliff-detection (H2) test.
* **Holm correction** within each hypothesis family. Families: `{H1, H2, H3}`, `{H4}`, `{H5, H6}`, `{H7}`, `{H8}`.
* **Effect sizes** — Cliff's δ for ordinal outcomes, Cohen's d for continuous. Always reported alongside p-values.

Tests live in `m6.evaluation.statistics`. Each test takes a long-format `pandas.DataFrame` and returns a `TestResult` dataclass with `(statistic, p_value, ci_low, ci_high, effect_size)`. Plotting helpers in `m6.evaluation.plot` use these directly.

### 10.4 Piecewise-linear cliff fitter

```python
def fit_piecewise(
    ratios: NDArray[np.float64],          # shape (N,), monotonic
    success: NDArray[np.float64],         # shape (N,), in [0, 1]
    *,
    bounds: tuple[float, float] = (1.0, 16.0),
    n_restart: int = 16,
) -> CliffFit: ...
```

Two linear pieces meeting at `τ`. Minimised by `scipy.optimize.differential_evolution`; `τ` is unique because we constrain the right-piece slope ≤ left-piece slope.

`CliffFit` exposes `tau, slope_left, slope_right, intercept, rmse, drop_rel`. H2 calls it directly; S1 (calibration study, plan §4.5) reuses it to predict τ\* on held-out workflows with MAE target ≤ 1.5 ratio units.

---

## 11. Results layout and reproducibility

### 11.1 Filesystem

```
results/
├── h1/
│   ├── 7b/<run_id>/qa_vs_coord.csv
│   ├── 7b/<run_id>/spearman.json
│   └── 7b/<run_id>/manifest.yaml
├── h2/
│   ├── 7b/<run_id>/cliff_per_cell.csv
│   ├── 7b/<run_id>/wilcoxon.json
│   └── 13b/...
├── h3/
├── h4/
├── h5/
├── h6/
├── h7/
└── h8/
```

Each `<run_id>` is `YYYYmmdd-HHMMSS-<git_sha>-<config_hash>`. The `manifest.yaml` carries the full resolved config, the `m6.__version__`, the Python version, the platform, and the hash of every input file used.

### 11.2 Reproduce-a-figure protocol

Every figure has a `make reproduce-ch<N>` target. The target:
1. Reads `configs/experiments/<hypothesis>.yaml`.
2. Re-derives the run_id from the resolved config hash.
3. Skips work that has already been done (idempotent).
4. Writes a CSV to `results/<hypothesis>/.../`.
5. Renders the figure with `m6.evaluation.plot.figure_for(hypothesis)`.

### 11.3 Final reproducibility package (plan §4.6 Month 10)

* Docker compose (`docker/docker-compose.yml`) brings up the memory bus + benchmark.
* HuggingFace hub release for the tag-preserving compressor.
* GitHub release tag for everything.
* Model cards (compressor-side) and data cards (benchmark-side) live in `docs/model_cards/` and `docs/data_cards/`.
* `README.md` carries one-command reproduction.

---

## 12. Grounding sources — what each cited paper actually says

Concise factual summary of the papers and internal documents the codebase rests on. Quotes are verbatim. Page numbers refer to the bundled PDFs.

### 12.1 Compression and memory

| Paper | What it actually says | Where we use it |
|-------|----------------------|-----------------|
| **Jiang et al. *LLMLingua* (EMNLP 2023)** | Coarse-to-fine prompt compression using a small LM (BERT/GPT-2) to predict and drop low-utility tokens. Ratios up to 20× with ≤1 pp drop on GSM8K. | Baseline reference; not directly run because superseded by LLMLingua-2. |
| **Jiang et al. *LongLLMLingua* (ACL 2024)** | Same idea, applied to long contexts; introduces question-aware coarse-to-fine. | Reference for the **P2 retrieve→compress** classical setup (§7.2). |
| **Pan et al. *LLMLingua-2* (ACL Findings 2024)** | Task-agnostic data distillation; XLM-RoBERTa token classifier; faster, multilingual. | **The `lingua2` compressor.** Calibration on NarrativeQA/HotpotQA. |
| **Mu et al. *Gist Tokens* (NeurIPS 2023)** | Learn special "gist" tokens that compress prefix prompts via attention-mask training. | Architectural cousin to ICAE; cited in discussion. |
| **Chevalier et al. *AutoCompressor* (EMNLP 2023)** | Reconstruction loss with summary vectors; LoRA-adapted; frozen decoder. | **Basis for our dual loss.** Plan §2.2 lists it as the basis. |
| **Ge et al. *ICAE* (ICLR 2024)** | Soft-prompt encoder LoRA-adapted, frozen decoder, reconstruction objective; 4× compression with minor drop on NaturalQuestions. | **Basis for the soft-prompt architecture.** Plan §2.2 lists it as the basis. |
| **Wang et al. *ICF / In-Context Former* (EMNLP 2024)** | Cross-attention compression, no reconstruction loss; faster training. | Discussion-only. |
| **Fei et al. *Semantic compression* (ACL 2024)** | Semantic-unit-level (not token-level) compression. | Discussion-only. |
| **Rae et al. *Compressive Transformers* (ICLR 2020)** | Compressed memory in transformer attention; smooth monotonic degradation. | H2 counter-example anchor. |
| **Guo et al. *Dynamic context compression for RAG* (2025)** | Relevance-conditional compression for RAG. | **Direct analogue of P3.** |
| **Cheng et al. *xRAG* (2024)** | Extreme-compression-aware RAG; hard-prompt style. | P1's compress-step. |
| **Li, Liu, Su, Collier. *Prompt Compression: A Survey* (NAACL 2025)** | Taxonomy + evaluation framework for prompt compression. | Used for terminology consistency. |

### 12.2 Multi-agent systems and memory

| Paper | What it actually says | Where we use it |
|-------|----------------------|-----------------|
| **Wu et al. *AutoGen* (2023)** | Multi-agent conversation framework with role-based agents and tool use. | **Agent runtime — v0.4 pinned.** |
| **Hong et al. *MetaGPT* (ICLR 2024)** | SOP-based multi-agent collaboration; structured artifact passing. | Planner-worker-critic SOP. |
| **Li et al. *CAMEL* (2023)** | Role-playing dialogue for autonomous agents. | H3 dialogue trace diversity. |
| **Shinn et al. *Reflexion* (NeurIPS 2023)** | Self-reflection / verbal reinforcement for sequential decision-making. | Critic's REVISE loop. |
| **Packer et al. *MemGPT / Letta* (2023)** | OS-like memory hierarchy for LLMs with paged virtual context. | Reference for the scratchpad-vs-archive split. |
| **Xu et al. *A-MEM* (NeurIPS 2025)** | Agent memory with Zettelkasten-style linking. | Discussion. |
| **Chhikara et al. *Mem0* (arXiv 2504.19413, 2025)** | Scalable long-term memory with embedding + extraction. | Industry comparator. |
| **Rasmussen et al. *Zep* (arXiv 2501.13956, 2025)** | Temporal knowledge graph memory. | Discussion. |
| **Zhang et al. *AgentPrune* (arXiv 2410.02506, 2024)** | Sparsify agent communication graph; reduce cost. | Discussion of P3 alternatives. |
| **Wang et al. *AgentDropout* (arXiv 2503.18891, 2025)** | Randomly drop agents during training. | Robustness sub-claim in Chapter 5. |
| **Park et al. *Collaborative Memory: Dynamic Access Control* (arXiv 2505.18279, 2025)** | ACL-aware shared memory; per-fragment provenance. | **C4 tag-preserving design ancestor.** |
| **Ye et al. *KVCOMM* (NeurIPS 2025)** | KV-cache compression for communication-efficient multi-agent inference. | Discussion. |
| **Haseeb. *Context Engineering for Multi-Agent LLM Code Assistants* (arXiv 2508.08322, 2025)** | Training-distribution mismatch causes coordination breakdown. | **H3 motivation; S3 stretch goal baseline.** |
| **Yu et al. *MemAgent* (arXiv 2507.02259, 2025)** | Memory-augmented agent with retrieval over its own past actions. | Discussion. |
| **Anthropic, *How we built our multi-agent research system* (June 2025)** | Orchestrator-worker topology; **token usage explains 80% of performance variance**. | **H1/H2 motivation, the closest published analogue to the coordination cliff.** Plan §9.2 verbatim. |
| **Rajasekaran et al. *Effective context engineering for AI agents* (Anthropic, 2025)** | Names **compaction, tool-result clearing, memory, just-in-time retrieval** as the four primitives. | **C3 P3 design grounding.** |
| **Anthropic, *Managing context on the Claude Developer Platform* (Oct 2025)** | **84% token reduction on a 100-turn web-search evaluation via context editing.** | Compression-ratio metric calibration. Plan §9.2 verbatim. |

### 12.3 RAG, long-context, benchmarks

| Paper | What it actually says | Where we use it |
|-------|----------------------|-----------------|
| **Lewis et al. *RAG* (NeurIPS 2020)** | The original retrieval-augmented generation. | P1/P2/P3 ancestor. |
| **Sarthi et al. *RAPTOR* (ICLR 2024)** | Recursive abstractive summarisation; hierarchical index. | P1 informant. |
| **Edge et al. *GraphRAG* (2024)** | Graph-summarised retrieval. | P3 routing-logic informant. |
| **Gutiérrez et al. *HippoRAG / HippoRAG 2* (NeurIPS 2024 / ICML 2025)** | Memory-organisation-as-graph. | Discussion of why P3 looks the way it does. |
| **Asai et al. *Self-RAG* (ICLR 2024)** | Reflection tokens gate retrieval. | P3 gating analogue. |
| **Hsieh et al. *RULER* (2024)** | Long-context capabilities benchmark; effective-context measure. | H7 70B sanity-check anchor. |
| **Bai et al. *LongBench / v2* (2024–2025)** | Long-context QA benchmark. | External calibration. |
| **Yen et al. *HELMET* (ICLR 2025)** | Long-context capability suite. | External calibration for H7. |
| **Liu et al. *Lost in the Middle* (TACL 2024)** | Position bias on long contexts. | H1 anchor. |
| **Mialon et al. *GAIA* (2023)** | Multi-step agent benchmark Level 1–3. | Motivates multi-agent framing; Level 1 used as a sanity check (plan §5.1). |
| **Liu et al. *AgentBench* (ICLR 2024)** | Multi-environment agent benchmark. | Selected envs (OS, DB, LTP) on critical path; rest non-critical. |
| **Anthropic, *Contextual Retrieval* (Sep 2024)** | Prepend chunk-level Claude-generated context before embedding; reported improvements across codebases, fiction, arXiv, science papers; **~$1.02 / 1M document tokens with prompt caching**. | **P1 pre-processor baseline.** Plan §9.3 verbatim. |

### 12.4 Privacy-aware retrieval and adversarial robustness

| Paper | Where we use it |
|-------|-----------------|
| **Zhou et al. *Privacy-Aware RAG* (2025)** | Threat model anchor for H6. |
| **Bassit & Boddeti. *SecureRAG* (2025)** | Threat model anchor for H6. |
| **Zhao. *FRAG* (2024)** | Federated extension target for D7. |
| **Addison et al. *C-FedRAG* (2024)** | Federated extension target for D7. |
| **Li et al. *SecurityLingua* (CoLM 2025)** | **S2 stretch goal** adversarial-robustness sweep. |

### 12.5 Internal FCG documents

These are bundled in the workspace and grounded with **page-cited** facts.

**`Saleh2025_MessageBrokers_GenAI.pdf`** — Saleh, Morabito, Dustdar, Tarkoma, Pirttikangas, Lovén. *Towards Message Brokers for Generative AI* (ACM CSUR 58(1), Sep 2025, doi:10.1145/3742891). Survey of traditional and modern brokers (Kafka, RocketMQ, Mosquitto, ZeroMQ, NiFi, NATS, NSQ, VerneMQ, KubeMQ, IBM MQ, Amazon SQS, Pub/Sub, Kinesis, Azure Service Bus, Solace) with explicit capacity numbers (Pub/Sub 10 MB, Storage Queue 64 KB, Kinesis 1 MB / 1 MB/s read / 20 consumers per stream — p. 9), and a five-direction research agenda. The **GenAI agent reference architecture (Fig. 3, p. 14)** — perception/brain/actuation — is the topology our planner-worker-critic loop instantiates.
*Verbatim, p. 12:* "Reliable delivery mechanisms have also evolved from minimal guarantees like 'at-most-once' delivery to robust mechanisms 'at-least-once' delivery through acknowledgments, retries, and persistent queues, as exemplified by NATS, Azure Service Bus, and Azure Storage Queue."

**`integrator-architecture.pdf`** — Internal FCG document (16 pp). Specifies seven integrator subsystems with explicit responsibilities (Sub-DAG Manager, Slice Constructor, Mechanism Executor, Resource Procurer, Commitment & Audit Interface, Governance Interface, Revenue & Accounting; pp. 3–7). Defines the **cross-market hash chain** `H_j = Hash(bids_j, alloc_j, payments_j, {H_k : k ∈ adj(j)})` (p. 6). Lists 11 ranked challenges with severity, of which **transcript integrity** and **recursive credibility of audit infrastructure** are flagged CRITICAL.
The thesis bus inherits the audit-chain pattern (§3.3 above) but **not** the auction subsystems.

**`software-architecture.pdf`** — Internal FCG document (21 pp). Translates the integrator into a buildable stack. Two messaging fabrics: **NATS (real-time, 1–5 ms)** and **Kafka (durable, 5–50 ms — source of truth and audit trail)** (§2). Languages: **Rust for the Matching Engine + max-flow library, Go for backend services, TypeScript + Python + Rust-WASM for the Agent SDK, React for dashboards.** Transcript hash chain `H_t = SHA-256(epoch_id ‖ bids_hash ‖ alloc_hash ‖ payments_hash ‖ H_{t-1})` (§3.5). The thesis bus implements an analogue of this hash chain (§3.3 above) but collapses the auction-specific fields into a single `payload_hash`.
*Verbatim, p. 17 (Decision 6):* "The ascending auction requires sub-10ms broadcast of price announcements. NATS provides this. But NATS messages are ephemeral. The audit trail requires durable, ordered, replayable event storage, which is Kafka's strength."

**`system-architecture.pdf`** — Internal FCG document (14 pp). Three-layer hybrid topology — Agent Layer → Level-1 Slice Marketplace → Level-2 Local Marketplaces. **Internal-scheduling efficiency factor 0.75 (SP) / 0.85 (entangled)** (§3). Four-table inter-component signal flow (§4). 11 high-level challenges (§6) including the **privacy–audit–latency triangle** which is the structural motivation for C4 (tag-preserving compression).

**`financial-analysis-university-ai-service-economy.pdf`** — Internal FCG document (15 pp). Five-year financial projection for the University of Oulu (28 500 nominal population). **Per-user monthly compute (Normal, p. 10):** Research-active **EUR 20→11/mo**, Administrative **11→6**, Teaching **7→4**, Students **1.50→0.85**. **Frontier cloud pricing (p. 10):** USD 3 / 1M input, USD 15 / 1M output ≈ **EUR 2.76 / EUR 13.80 per 1M tokens**. **On-premises ConfidentialMind marginal cost: EUR 0.05/1M tokens**. **Internal hourly cost EUR 25/h** (derived). **Time-reduction blended 67%** (= 0.60·0.85 + 0.40·0.40). **Investment table (p. 6):** total 5-yr EUR 3.027M. **Phase 1→2 cost reduction ~45%** (35% routing + 10% competitive pricing). **GPU utilisation lift 30–40%→70–80%**. **Normal-scenario Year-5 BCR 3.5:1**, NPV(3%) **EUR 6.9M**. These numbers ground the cost model in §7.4.

**`use-case-university-ai-service-economy.pdf`** — Internal FCG document (14 pp). Narrative companion. Lists the **institutional system inventory**: Publication DB, Contract DB, Moodle, Patio, Peppi, CRM, Office 365/Teams, Tatu (SAP), SAP Travel, SAP CATS. Three Phase-1 infrastructure tiers: laptop **Phi-4 Mini 3.8B**, on-prem ConfidentialMind 70–80B model, cloud platform (MS Copilot / Azure). Eight vignettes with per-phase time + cost; the focal **Vignette 3.7 — Period-end project reporting** reports a **Phase-2 cost of EUR 2.15 per report** via **8 parallel specialised agents + 80% cloud-payload reduction** (p. 9). The C1 family (a) workload generator emulates this shape.
*Verbatim, p. 12:* "A neutral exchange earns per-unit fees on volume. Its revenue is maximized by making the best routing decision regardless of provider. This neutrality is not a design preference but a structural constraint."

---

## 13. Risks, kill-switches, and time-boxes

The plan's risk register (§7) is the source of truth. Engineering-relevant kill-switches are encoded in the codebase so they fire automatically:

| Risk | Code-level kill-switch |
|------|------------------------|
| ICAE port to MLX/MPS slips | `m6.compressors.training.train_icae` time-boxed to **14 days** — after which it emits a stop-the-line event and the experiment falls back to AutoCompressor. |
| MLX lacks InfoNCE primitive | Detected at startup by `m6.compressors.training.loss._probe_mlx_nce`; falls back to PyTorch-MPS. |
| 13B fine-tuning OOMs at rank 8 | Trainer catches OOM, halves the rank, retries once, then declares 7B-only. |
| 70B int4 produces broken output | `m6.inference.llamacpp_backend` runs a NarrativeQA mini-eval at startup; refuses to serve traffic if F1 drops by **> 5 pp**. |
| H2 falsified (no cliff) | `m6.experiments.h2_coordination_cliff` reports the negative finding via `result.falsified = True`; the chapter writer renders the "no cliff" version of the figure. |
| AutoGen runtime bugs confound metrics | Every experiment includes a `compressor=none` control condition. If `var(control) ≥ var(treatment)`, the experiment is flagged `invalid` in `manifest.yaml`. |
| M0/M1/M2 agents not ready by Month 7 | H8 runner reads `docs/agent_readiness.yaml`; if all three flags are `false`, it short-circuits and writes a `documented-as-deferred` marker per `scope-signoff.md`. |
| A new paper publishes C2's exact result | Out-of-band; we keep an arXiv alert running, not encoded here. |

Time-boxes are enforced. They are not advisory.

---

## 14. Glossary

* **ACL bitmask** — `uint64` capability vector attached to a fragment or slot. Bit `i` represents capability `i`.
* **Classification tier** — 0..4 lattice: PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED < SECRET.
* **C1 / C2 / C3 / C4** — the four contributions (plan §2).
* **Coordination cliff τ\*** — the compression ratio above which coordination success drops by ≥30% (plan §3 H2).
* **Compressor variant V1/V2/V3** — dense-embedding / ICAE-style / instruction-aware filter (plan §6.1).
* **Dual-objective loss** — `L_recon + λ · L_NCE` (plan §2.2).
* **FCG** — Future Computing Group at the CSE Research Unit, University of Oulu.
* **GGUF** — `llama.cpp`'s quantised model file format. `Q4_K_M` is the 4-bit mixed-precision quantisation we use for 34B/70B.
* **InfoNCE** — Information Noise-Contrastive Estimation loss; the L\_NCE term.
* **ICAE** — In-Context Autoencoder (Ge et al. ICLR 2024).
* **LoRA** — Low-Rank Adaptation; PEFT-style fine-tuning.
* **MPS** — Apple Metal Performance Shaders — the PyTorch backend on Apple Silicon.
* **MLX** — Apple's native ML framework for Apple Silicon.
* **MemIndex** — Saleh et al. ACM TAAS 2025 baseline architecture this thesis extends.
* **Memory slot** — one of `M` learnable `[MEM]` token positions in the ICAE encoder. The compressed representation.
* **Period-end reporting** — the focal Vignette 3.7 workflow; the canonical real-trace target for H8.
* **Plan / `plan.md`** — the implementation plan; ground truth for scope and schedule.
* **Scratchpad** — the in-memory dict in the storage layer; the agents' shared working surface.
* **Slot** — abbreviation of `CompressedSlot` (§3.1).
* **Tag head** — the per-slot MLP that predicts `(acl_mask, classification)` in the C4 variant (§5.5).
* **τ\*** — the coordination cliff threshold from H2 / H7.
* **Vignette 7 (a.k.a. 3.7)** — period-end project reporting across eight university systems; the canonical workload C1 family (a) is built around.

---

*End of document.*
