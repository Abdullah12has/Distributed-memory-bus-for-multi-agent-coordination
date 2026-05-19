# Technical Reference -- m6-thesis

> **Audience.** This document is the canonical engineering reference for the code in `src/m6/`. It maps every claim in `plan.md` to a concrete code module, a paper, and a falsifiable measurement. Anyone writing or reviewing code should read this *before* opening the source tree.
>
> **Status.** Living document. Pinned at commit-time to the `plan.md` revision dated **May 2026**. Every section header carries the back-pointers it is grounded in.
>
> **Authoring conventions.**
> 1. Every empirical claim must point to a *single* paper, a *single* internal reference, or a *single* measurement that the codebase produces and that lives in `results/`.
> 2. Where the plan and a paper disagree, the **plan wins** and the disagreement is footnoted.
> 3. Wallclocks are stated for the **M4 Pro 48 GB single-machine envelope** (plan S1, S5.4). Any external-cluster aside is marked *non-critical-path*.

---

## Table of contents

1. [Scope, goals, and non-goals](#1-scope-goals-and-non-goals)
2. [System architecture -- three-layer memory bus](#2-system-architecture--three-layer-memory-bus)
3. [Data model](#3-data-model)
4. [The four hypotheses -- implementation specification](#4-the-four-hypotheses--implementation-specification)
5. [Compressor framework (C2 + C4)](#5-compressor-framework-c2--c4)
6. [Benchmark (C1)](#6-benchmark-c1)
7. [RAG pipeline catalogue (C3)](#7-rag-pipeline-catalogue-c3)
8. [Inference backends](#8-inference-backends)
9. [Agent runtime](#9-agent-runtime)
10. [Evaluation and statistics](#10-evaluation-and-statistics)
11. [Results layout and reproducibility](#11-results-layout-and-reproducibility)
12. [Grounding sources -- what each cited paper actually says](#12-grounding-sources--what-each-cited-paper-actually-says)
13. [Risks, kill-switches, and time-boxes](#13-risks-kill-switches-and-time-boxes)
14. [Glossary](#14-glossary)

---

## 1. Scope, goals, and non-goals

### 1.1 Thesis statement (verbatim from `plan.md` S1)

> *"This thesis designs, implements, and evaluates a distributed memory bus with a context-compression layer for multi-agent institutional systems. It contributes (i) a multi-agent coordination benchmark, (ii) an empirical characterization of how context compression affects multi-agent coordination quality, (iii) a catalogue of three RAG + compression pipeline architectures evaluated under matched conditions, and (iv) a tag-preserving compressor variant integrated with a reference memory-bus implementation that exposes the integration interfaces the FCG platform requires."*

### 1.2 In scope

| Contribution | What the code must produce | Plan refs |
|--------------|---------------------------|-----------|
| **C1** -- multi-agent coordination benchmark | Reproducible synthetic Vignette-7-style benchmark with three workload families, 150 instances, coordination-quality metrics, synthetic ACL tags. Single-command regeneration. | S2.1, S4.2 |
| **C2** -- empirical compression characterisation | Three compressors x five ratios x five seeds on C1, with paired-bootstrap CI. Headline output: existence/shape of the coordination cliff t\*. | S2.2, S4.3, S4.4 |
| **C3** -- RAG + compression pipeline catalogue | Three pipelines (P1 compress-then-retrieve, P2 retrieve-then-compress, P3 joint) on FAISS + LlamaIndex, benchmarked under matched retrieval quality with a EUR/query cost model fit to **GPT-4o-mini** and **Claude Haiku 4.5** prices plus amortised local cost. | S2.3, S4.3 |
| **C4** -- tag-preserving compressor + reference memory-bus integration | ICAE variant with per-slot tag-prediction head; FastAPI service exposing `write` / `read` / `subscribe` / `audit`; policy-enforcement middleware; SQLite audit log. | S2.4, S4.4, S6 |

### 1.3 Explicitly out of scope (plan S1, S6.3)

* Production-grade governance enforcement. The tag-preserving compressor is a **research prototype with measured properties**, not a compliance tool.
* Cross-tokenizer or cross-model-family compressed exchange.
* Live production deployment on the FCG platform -- the deliverable is a reference FastAPI service.

### 1.4 Compute envelope

| Workload | Path | Notes |
|----------|------|-------|
| 7B / 13B fp16 inference | MLX-LM on M4 Pro | Apple-Silicon-native; primary path. |
| 7B LoRA fine-tuning | MLX + PEFT, rank 16, batch 4, accum 8 | <=3 days wallclock (plan S4.3). |
| 13B LoRA fine-tuning | MLX rank 8, *if memory allows* | Time-boxed, stretch (plan risk 3). |
| External API arm | OpenAI + Anthropic clients | Cost-tracked per call. |

Everything else (eval, agent orchestration, FAISS) is CPU-bound on the same host.

---

## 2. System architecture -- three-layer memory bus

### 2.1 Layers (plan S6.1)

```
+-----------------------------------------------------------------+
| ACCESS LAYER  -- FastAPI service                                  |
|  POST   /v1/write   (fragment, tags) -> slot_id                   |
|  GET    /v1/read/{slot_id}?requester_acl=... -> CompressedSlot|403|
|  POST   /v1/subscribe (query, ttl)  -> SSE stream                 |
|  GET    /v1/audit/{slot_id}         -> provenance chain            |
|  + ACL middleware, structured logging, OTel hooks                 |
+-----------------------------------------------------------------+
| COMPRESSION LAYER  -- pluggable Compressor interface              |
|  compress(fragment, task_hint, tags) -> CompressedSlot             |
|  Variants:                                                        |
|   V1  dense-embedding   (cheap baseline, no training)             |
|   V2  ICAE-style soft-prompt    (dual-objective trained)          |
|   V3  instruction-aware filter  (heuristic, no training)          |
|   V4  V2 + per-slot tag-prediction head    (C4)                   |
+-----------------------------------------------------------------+
| STORAGE LAYER                                                     |
|  SQLite (audit log, append-only via trigger)                      |
|  in-memory dict (active scratchpad, TTL)                          |
|  FAISS-CPU (compressed-slot retrieval)                            |
+-----------------------------------------------------------------+
```

### 2.2 Component -> module map

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

### 2.3 Architecture grounding -- what we kept, what we changed

The three-layer split is **lifted directly from MemIndex (Saleh et al., ACM TAAS 2025)**, which is the architecture the thesis explicitly extends ("baseline architecture extended by this thesis", plan S9.5). Two material differences:

1. **Compression is a first-class layer**, not an optimisation. MemIndex treats memory entries as opaque; we make every read pass through a `Compressor.compress(...)` call so the experimental knob is a parameter of the system, not a downstream consumer.
2. **Per-slot tags are part of the data model**, not metadata attached out-of-band. The provenance/ACL bitmask is inherited and is itself a target of measurement (C4).

The bus-vs-broker terminology is grounded in the **Saleh et al. *Message Brokers for GenAI* survey (ACM CSUR 2025)**. The survey's reference GenAI-agent model -- perception (sensors, tools, broker) + brain (memory, sub-goal decomposition, chain-of-thought, self-critic) + actuation (Fig. 3, p. 14) -- is the topology the planner-worker-critic loop instantiates. We adopt **at-least-once semantics with acknowledgments and a durable persistent log** (Saleh CSUR p. 12), which here is the SQLite audit log; the in-memory scratchpad is ephemeral and is allowed to lose state on crash because the audit log is the source of truth.

### 2.4 Boundary with the FCG platform stack

The thesis ships a **single FastAPI service**. The FCG software architecture specifies a dual messaging topology for the full platform. The thesis's reference implementation collapses these into **SQLite + an in-memory dict + an HTTP API**, on the grounds that:

* The compute envelope is one machine. Adding distributed messaging on the same M4 Pro adds operational complexity without adding empirical signal.
* The compression-layer API is protocol-based and designed for extensibility. Whether the wire is HTTP or a pub/sub transport is a deployment-time decision decoupled from the compressor and evaluation contracts.

What is *preserved* from the FCG stack:

* Event types are recreated as Pydantic models in `m6.memory_bus.schemas` (`SliceRegistered`, `BidSubmitted`, `EpochResult`, `TranscriptCommit`, `AuditSignal` -- see S3.4).
* The audit-log table schema mirrors the FCG audit transcript table (columns: `epoch_id`, `bids_hash`, `alloc_hash`, `payments_hash`, `prev_hash`, `chain_hash`).
* The transcript hash chain `H_t = SHA-256(epoch_id || bids_hash || alloc_hash || payments_hash || H_{t-1})` is implemented in `m6.memory_bus.storage.sqlite_audit.chain_hash(...)` and tested with a tamper-detection unit test.

### 2.5 Future work

The repo is structured so several natural extensions are drop-in replacements rather than rewrites:

1. **Storage swap.** `m6.memory_bus.storage` exposes three protocols -- `AuditLog`, `Scratchpad`, `VectorStore`. SQLite/in-memory-dict/FAISS today; alternative backends can implement the same protocols.
2. **Cross-tokenizer compressed exchange.** Out of scope (plan S1). The compressor interface carries a `tokenizer_id` field so a future tokeniser adapter can be layered in.
3. **Live FCG deployment.** The FastAPI service is the contract. Production deployment is a separate engineering effort.

---

## 3. Data model

### 3.1 Core types (Pydantic)

```python
# src/m6/memory_bus/schemas.py
class TagVector(BaseModel):
    """
    Provenance + ACL metadata that travels with every fragment and slot.
    ACL bitmask is uint64 -- 64 named capabilities. Classification levels are a
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
* `TextSummary` -- a string (LLMLingua-2 hard-prompt; instruction-aware filter; xRAG-style stub).
* `SoftEmbed` -- a `numpy.ndarray` of shape `(num_slots, d_model)` (ICAE).
* `TokenIds` -- a list of token ids in the encoder's vocabulary (AutoCompressor-style).

### 3.2 Tag semantics

Tags are **synthetic** (plan S4.2). The thesis does not use real ACL data. The bitmask is a uint64 with two distributions tested:
* **uniform** -- each capability bit set independently with probability 0.5.
* **skewed** -- exponential family so a handful of bits dominate, modelling typical real ACL distributions (most fragments are "low" classification).
* **hierarchical** -- bits clustered by classification level, so high-classification fragments carry a strict superset of low-classification bits.

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
| `chain_hash` | BLOB(32) | SHA-256(prev_hash || payload_hash) |
| `created_at` | TEXT NOT NULL | ISO-8601 UTC |

The chain hash mirrors the FCG audit transcript table, collapsing auction-specific fields into a single `payload_hash` since the thesis bus does not run an auction.

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

### 3.5 Cost model accounting

Every external API call writes a row to `cost_ledger`:

| Column | Type |
|--------|------|
| `experiment_id` | TEXT |
| `provider` | TEXT -- `openai` / `anthropic` / `local-mlx` |
| `model` | TEXT |
| `input_tokens` | INTEGER |
| `output_tokens` | INTEGER |
| `eur_cost` | REAL |
| `wallclock_ms` | INTEGER |
| `created_at` | TEXT |

Pricing constants live in `m6.pipelines.cost_model.PRICING`. The frontier-cloud-pricing baseline (USD 3 / 1M input, USD 15 / 1M output, approximately EUR 2.76 / EUR 13.80) is grounded in the FCG financial analysis. The local-inference amortised cost (EUR 0.05/1M tokens for on-prem) is from the same source.

---

## 4. The four hypotheses -- implementation specification

Each hypothesis section answers **(a) what does the code need to compute, (b) what paper grounds it, (c) which module owns it, (d) what's the falsification target, (e) what's the statistical test.**

### 4.1 H1 -- QA accuracy is a poor predictor of coordination success

**Falsifiable claim (plan S3, H1):** Spearman rho between single-agent QA accuracy delta and multi-agent coordination success delta across matched compression ratios is **below 0.6 on at least two of the three compressors at 7B.**

**What the code computes.** For each `(compressor c, ratio r, workload w, seed s)` cell:
1. Run the single-agent QA derivative of the workload -- the same source documents, but with a single agent answering the planner's seed question. Record F1 / EM.
2. Run the full planner-worker-critic loop with the same `(c, r, w, s)`. Record final task success, sub-task-assignment accuracy, rounds-to-completion.
3. Compute `delta_qa = qa_at_r - qa_at_r=1` and `delta_coord = coord_at_r - coord_at_r=1`.
4. Across the union of cells per compressor, compute Spearman rho between `delta_qa` and `delta_coord`.

**Module.** `m6.experiments.h1_qa_vs_coordination`.

**Grounding papers.**
* **Anthropic, *How we built our multi-agent research system* (June 2025)** -- the published industry analogue that motivates H1: their finding that *token usage explains 80% of performance variance* (plan S9.2). H1 asks whether the standard single-agent QA metric is still informative under coordination.
* **Liu et al. *Lost in the Middle* (TACL 2024)** -- the canonical counter-example: single-agent F1 looks fine while the model misses the middle. We use it as a single-agent calibration anchor.

**Statistical test.** Spearman rho with 95% bootstrap CI (10K resamples). Failure to reject `rho >= 0.6` is *thesis-worthy* per plan S3 ("falsification of any of them is itself a thesis-worthy result").

### 4.2 H2 -- A coordination cliff t* exists and is task-dependent

**Falsifiable claim:** For each `(compressor, workload)` cell at 7B, there is a compression ratio t* such that coordination success at `r > t*` falls by **>=30%** relative to `r < t*`. t* varies by workload but **not by compressor family within +/-20%**.

**What the code computes.**
1. Fit a piecewise-linear function `f(r; a, b, t)` to the (compression ratio -> coordination success) curve per cell. Two linear pieces meeting at t; fitted by minimising MSE with `scipy.optimize.differential_evolution` on `t in [1, 16]`.
2. The "cliff" is defined as the breakpoint t where the slope of the right piece exceeds the slope of the left piece by a threshold and the relative drop on the right exceeds 30%.
3. Sanity-tested by **Wilcoxon signed-rank** comparing `coord(r < t*)` vs `coord(r >= t*)` across seeds (plan S5.3).

**Module.** `m6.evaluation.cliff_fitting.fit_piecewise(...)` + `m6.experiments.h2_coordination_cliff`.

**Grounding papers.**
* **Rae et al. *Compressive Transformers* (ICLR 2020)** -- establishes that compressed memory has a degradation curve, but reports smooth monotonic decay. H2 asks whether *multi-agent coordination* breaks this monotonicity.
* **Jiang et al. *LongLLMLingua* (ACL 2024)** -- reports continuous accuracy-vs-ratio curves on single-agent QA. We replicate their methodology, then re-instrument on C1.
* **Pan et al. *LLMLingua-2* (ACL Findings 2024)** -- the same, with task-agnostic data distillation.
* **Anthropic, *How we built our multi-agent research system* (June 2025)** -- the 80%-token-variance finding is the closest published analogue.

### 4.3 H3 -- RAG pipeline placement matters

**Falsifiable claim:**
* P1 (compress-then-retrieve) dominates P2 (retrieve-then-compress) **on storage-bounded settings** (FAISS index size capped).
* P2 dominates P1 **on accuracy-bounded settings** (retrieval recall capped).
* P3 (joint) closes the gap on a **combined accuracy x EUR score**.
* Effect size >= **5 pp F1** on C1 family (a).

**What the code computes.** For each `(pipeline P, budget mode B)`:
* `B = storage-bounded` -- FAISS index size capped at 100 MB. Both P1 (small compressed chunks) and P2 (full chunks) compete under that ceiling.
* `B = accuracy-bounded` -- retrieval recall@10 capped at 0.85. Adjust the embedding granularity until both reach that recall.
* P3 picks at retrieval time: chunks with `score > theta` go straight in; chunks with `score < theta` are compressed first. theta swept.
* Headline metric: F1 on the workload + EUR/query (see `m6.pipelines.cost_model`).

**Module.** `m6.pipelines.{p1,p2,p3}_*` + `m6.experiments.h3_rag_placement`.

**Grounding papers.**
* **Lewis et al. *RAG* (NeurIPS 2020)** -- the baseline architecture.
* **Sarthi et al. *RAPTOR* (ICLR 2024)** -- hierarchical summarisation; informs the P1 pre-compression layout.
* **Edge et al. *GraphRAG* (2024)** -- graph-summary RAG; not directly compared but informs P3's relevance-routing logic.
* **Gutierrez et al. *HippoRAG / HippoRAG 2* (NeurIPS 2024 / ICML 2025)** -- memory-organisation-as-graph; we cite it in the discussion of why P3 looks the way it does.
* **Asai et al. *Self-RAG* (ICLR 2024)** -- reflection-token gating; structurally similar to P3's score-conditional routing.
* **Cheng et al. *xRAG* (arXiv 2405.13792, 2024)** -- extreme-compression-aware RAG; the compress-step in P1 follows xRAG's hard-prompt approach.
* **Guo et al. *Dynamic context compression for RAG* (2025)** -- the closest published analogue to P3.
* **Anthropic, *Contextual Retrieval* (Sep 2024)** -- chunk-level context prepending; used as a baseline pre-processor for P1.
* **Anthropic, *Managing context on the Claude Developer Platform: context editing and the memory tool* (Oct 2025)** -- reports a **84% token reduction on a 100-turn web-search evaluation** via context editing (plan S9.2). This is the closest production analogue to what P3 does.

### 4.4 H4 -- Tag preservation >= 85% at 4x with <=5 pp accuracy drop

**Falsifiable claim:** The tag-preserving compressor preserves provenance tags **at rate >=85% at 4x compression** with accuracy degradation **<=5 pp** relative to the non-tag-preserving baseline.

**What the code computes.**
1. Add a per-slot tag-prediction head on top of the ICAE soft-prompt slots. Head: small MLP from the slot embedding -> (acl_logit, classification_logit). Loss: BCE-with-logits for the 64-bit ACL, cross-entropy for the 5-tier classification.
2. Joint loss: `L = L_recon + lambda_NCE * L_NCE + lambda_tag * L_tag`. lambda_tag swept in `{0.1, 0.3, 1.0, 3.0}`.
3. **Tag preservation rate.** Recover tags from each compressed slot via the head; compare to the **union of source-fragment tags** (a fragment's tag is preserved iff *at least one* of its bits or its classification level is recovered).
4. **Accuracy delta.** Same C1 evaluation as the H2 baseline, head added but not used for reading.

**Module.** `m6.compressors.tag_preserving` + `m6.evaluation.metrics.tag_preservation` + `m6.experiments.h4_tag_preservation`.

**Grounding papers.**
* **Ge et al. *ICAE* (ICLR 2024)** -- the soft-prompt architecture H4 modifies.
* **Chevalier et al. *AutoCompressor* (EMNLP 2023)** -- provides the reconstruction loss formulation and shows that LoRA adapters suffice for the encoder side.
* **Mu et al. *Gist Tokens* (NeurIPS 2023)** -- alternate per-slot summary mechanism; cited in the discussion as a baseline.
* **Park et al. *Collaborative Memory: Dynamic Access Control* (arXiv 2505.18279, 2025)** -- the published precedent for ACL-aware memory in multi-agent systems.
* **Zhou et al. *Privacy-Aware RAG* (arXiv 2503.15548, 2025)** -- privacy-preserving retrieval, structurally analogous.

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
| `icae` | soft-prompt | **yes** | `L_recon + lambda_NCE * L_NCE` | The C2 trainable arm. |
| `icae-tag` | soft-prompt | **yes** | `L_recon + lambda_NCE * L_NCE + lambda_tag * L_tag` | C4. |

### 5.2 ICAE training spec (plan S2.2, S4.2)

> *"The soft-prompt compressor is fine-tuned with a joint dual-objective loss following Ge et al. 2024 (ICAE) and Chevalier et al. 2023 (AutoCompressor): **L = L\_reconstruction + lambda * L\_contrastive**."* -- plan S2.2 (verbatim).

**Architecture.**
* Encoder: **Llama-3.1-8B-Instruct**, LoRA-adapted (rank 16, alpha=32, dropout=0.05, target modules `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`).
* Decoder: same backbone, **frozen** (no LoRA). This is the AutoCompressor pattern; cuts trainable parameters by ~50% and matches Ge et al. ICAE.
* Memory slots: `M` learnable [MEM] tokens prepended to the encoder input. Default `M = 128` for a 4x target ratio on 512-token fragments.

**Loss.**
* `L_recon` -- token-level cross-entropy of the source fragment given the [MEM] slots, computed on the **frozen decoder**.
* `L_NCE` -- InfoNCE over pairs in the batch:
  * **Positives.** (fragment_a, fragment_b) drawn from the same source document.
  * **Negatives.** Other fragments in the same batch (in-batch negatives).
  * Similarity = mean-pooled [MEM] embedding cosine.
  * Temperature `tau` = 0.07 (standard SimCLR).
* `lambda` swept in `{0.1, 0.3, 1.0}` on a validation split (plan S4.3).
* C4 adds `lambda_tag * L_tag` with `L_tag = BCE(acl_pred, acl_true) + CE(class_pred, class_true)`.

**Optimiser.** AdamW, `lr = 3e-4`, `weight_decay = 0.0`, `betas = (0.9, 0.95)`, cosine schedule with 200-step linear warmup. Gradient accumulation 8. Batch 4. Sequence length 512 (fragment) + 128 (memory).

**MLX path.**
* Encoder LoRA via `mlx_lm.lora`.
* InfoNCE primitive: MLX 0.21 does **not** ship a batch contrastive op. We implement it manually as `mlx.nn.losses.cross_entropy(logits, labels)` over a `(B, B)` similarity matrix. Tested on a 1K synthetic corpus (plan S4.1 -- "If MLX lacks an InfoNCE-friendly batch contrastive primitive, fall back to a manual cosine-similarity InfoNCE...")
* PyTorch-MPS fallback if any MLX op is missing: `torch.nn.functional.cross_entropy` on the same matrix.

**Compute budget.** <=3 days wallclock for 7B at rank 16, ~5K traces, ~50 MB corpus. 13B at rank 8 is the upper limit (plan S4.3 risk register).

### 5.3 LLMLingua-2 wrapper

Thin adapter around the upstream `llmlingua` Python package (Pan et al. ACL Findings 2024). XLM-RoBERTa-based, runs natively on MPS. Single config: target ratio. **Validation target:** NarrativeQA F1 within **2 pp** of reported numbers; HotpotQA F1 within **3 pp** (plan S4.1). Failure to hit those is a Month-1 stop-the-line event.

### 5.4 Instruction-aware filter

Simple heuristic baseline. Two stages:
1. **Sentence-level filter.** TF-IDF + a small cross-encoder reranker (`BAAI/bge-reranker-base`) selects the top-k sentences whose relevance score w.r.t. `task_hint` exceeds theta.
2. **Token-level trim.** Drop stop-words and <=2-character tokens until the target ratio is hit.

Deterministic given `(task_hint, fragment, target_ratio)`. No training. Useful as a *floor* baseline that the trained ICAE variant must beat by >=3 pp F1 to justify its training cost.

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

### 6.1 Workload families (plan S4.2)

| Family | Code | Source | Skeleton |
|--------|------|--------|----------|
| (a) cross-document fact aggregation | `cross_doc_fact_aggregation` | 10-200 source docs | Vignette-7 style: planner asks "what is X across all sources?", workers retrieve, critic checks consistency. |
| (b) constraint-satisfaction planning | `constraint_satisfaction` | 3-8 capacity-bounded agents | Assign N sub-tasks under capacity constraints; verified with a constraint-checker. |
| (c) multi-step retrieval | `multi_step_retrieval` | heterogeneous source families | Chain queries: result of step k feeds step k+1; up to 4 levels. |

**Instance count.** ~50 per family, **150 total** (plan S4.2).

**Configuration knobs (per family).**
* Number of source documents: 10 / 50 / 200.
* Number of agents: 3 / 5 / 8.
* Sub-task complexity level: 1 / 2 / 3 / 4.
* Tag distribution: uniform / skewed / hierarchical.
* Source document length: 500 / 1500 / 5000 tokens.

### 6.2 Coordination-quality metrics (plan S5.2)

* **Final task success** -- boolean: did the planner declare DONE with a critic-approved result?
* **Sub-task-assignment accuracy** -- fraction of sub-tasks assigned to the agent the workload's ground-truth solver function expected.
* **Rounds-to-completion** -- number of planner-worker-critic cycles before DONE.
* **Critic-flagged error rate** -- fraction of rounds where the critic returned `STATUS=REVISE`.

These are all computed by **scoring functions over AutoGen trace logs** (plan S4.2). Code lives in `m6.evaluation.metrics.coordination`. The scoring functions are pure functions of the trace; they do not call the model.

### 6.3 Corpus

Curated institutional subset, **PII-redacted**, ~50 MB (plan S4.1):
* Publications from M0 (coordination with Mohammad Abaeiani).
* Redacted contract excerpts from M1 (coordination with Faisal Khan).
* Moodle/Patio materials from M2 (coordination with Vu Truong).
* Padded with a sub-sampled BookCorpus chunk for breadth, only on the training side. Evaluation always uses the institutional subset.

Loader: `m6.corpus.loader.InstitutionalCorpus`. PII redaction: `m6.corpus.pii_redaction` runs an off-the-shelf NER (`en_core_web_lg`) plus a hand-curated phone-number / email regex over every loaded document. **Redaction is mandatory.** The loader refuses to return a document that has not passed the redaction stage.

---

## 7. RAG pipeline catalogue (C3)

### 7.1 P1 -- compress-then-retrieve

```
   +---------------+    +----------------+    +---------------+    +-------+
   | Source docs   | -> | Compress (any) | -> | Embed + index | -> | FAISS |
   +---------------+    +----------------+    +---------------+    +-------+
                                                                       |
            +-----------+    +--------------------------+              |
   Query -> | Retriever | -> | Synthesiser (LLM)        |  <-----------+
            +-----------+    +--------------------------+
```
* Compression is **upstream** of indexing. The FAISS index stores compressed embeddings (or compressed text re-embedded).
* Storage advantage. Quality risk: information that is compressed away is forever gone.

**Implementation.** `m6.pipelines.p1_compress_retrieve.Pipeline1`. Uses LlamaIndex's `IngestionPipeline` with the compressor as a custom `TransformComponent`.

### 7.2 P2 -- retrieve-then-compress (the classical LongLLMLingua setup)

```
   Query ->  Retriever (full docs)  ->  Compress retrieved set  ->  Synthesiser
```
* Compression is **post-retrieval**. The FAISS index stores full chunks.
* Accuracy advantage on raw retrieval; cost advantage at inference; storage cost stays high.

**Implementation.** `m6.pipelines.p2_retrieve_compress.Pipeline2`. Uses LlamaIndex's `NodePostprocessor` interface; the postprocessor calls the compressor.

### 7.3 P3 -- joint, conditional compression

```
   Query ->  Retriever  ->  for each retrieved chunk:
                              if score > theta_high:   keep verbatim
                              elif theta_low < score:  compress
                              else:                    discard
                          ->  Synthesiser
```
* Hybrid. The router uses the retriever's relevance score to decide whether to compress.
* Two thresholds. Swept; default `theta_high = 0.75, theta_low = 0.45` (cosine on `BAAI/bge-large-en-v1.5`).

**Implementation.** `m6.pipelines.p3_joint.Pipeline3` -- also a `NodePostprocessor`, but with a per-node branch.

**Grounding.** This is the structural analogue of **Guo et al. *Dynamic context compression for RAG* (2025)** (plan S9.1). The `theta`-based routing is what makes P3 distinct from P2.

### 7.4 Cost model

```python
# src/m6/pipelines/cost_model.py
@dataclass(frozen=True)
class PricePerMillion:
    input_eur:  float
    output_eur: float

PRICING: dict[str, PricePerMillion] = {
    "gpt-4o-mini":             PricePerMillion(0.138, 0.552),   # USD 0.15 / 0.60 -> EUR
    "claude-haiku-4-5":        PricePerMillion(0.92,  4.60),    # USD 1.00 / 5.00 -> EUR
    "frontier-sonnet-tier":    PricePerMillion(2.76,  13.80),   # FCG financial analysis
    "local-mlx":               PricePerMillion(0.05,  0.05),    # on-prem amortised
}
```

* The **frontier-sonnet-tier** number is grounded in the FCG financial analysis (*"USD 3 / 1M input tokens, USD 15 / 1M output tokens, approximately EUR 2.76 / EUR 13.80"*).
* The **local-amortised** number (EUR 0.05/1M tokens) is from the same source.
* The **GPT-4o-mini** and **Claude Haiku 4.5** prices reflect TalentAdore production pricing as of May 2026. Constants live in one place; experiments do not hard-code prices. **Update procedure:** on each pricing change, edit `PRICING`, rerun `make exp-h3`.

The headline cost metric is **EUR/workflow** (plan S5.2).

---

## 8. Inference backends

| Backend | Module | Models served | Notes |
|---------|--------|---------------|-------|
| MLX-LM | `m6.inference.mlx_backend` | 7B fp16, 13B fp16 | Native to Apple Silicon; primary path. |
| Ollama | `m6.inference.ollama_backend` | DX / quick iteration | Wraps a localhost HTTP endpoint. |
| OpenAI | `m6.inference.api_backend.OpenAIBackend` | `gpt-4o-mini` | Used as the C3 cost arm and LLM-as-judge. |
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

The `Completion` carries `text`, `input_tokens`, `output_tokens`, `wallclock_ms`, `eur_cost`. Every call appends to `cost_ledger` (S3.5).

**Retry policy.** `tenacity` exponential back-off, `5` retries, `2 -> 32 s`. **Rate-limit policy.** Token-bucket per provider, configurable via env.

---

## 9. Agent runtime

### 9.1 Why AutoGen v0.4

AutoGen is the most mature multi-agent framework with scratchpad-style state sharing (plan S6.2). The **v0.4 rewrite is a breaking API change** (released October 2024); we pin to v0.4.x because:
* The async event-driven core matches our SSE-based subscribe API.
* The `Team` / `RoundRobinGroupChat` primitives are a clean planner-worker-critic skeleton.
* The single-process harness from plan S4.1 is a thin shim over `RoundRobinGroupChat`.

### 9.2 Planner-worker-critic topology

```
   +---------+        +----------+        +--------+
   | Planner | >>>>>> | Worker_i | >>>>>> | Critic |
   +---------+        +----------+        +--------+
        ^                                       |
        +------------- REVISE / DONE <----------+
```

* **Planner** decomposes the workload into sub-tasks, assigns them, and tracks completion.
* **Workers** each carry a tool (retrieve, compute, write-to-scratchpad). They never talk to each other directly -- communication is mediated by the planner.
* **Critic** receives the planner's draft answer and either `DONE`s it or returns `REVISE` with a structured complaint that re-enters the loop.

This is the **Saleh CSUR p. 14 GenAI-agent reference architecture** (perception + brain + actuation) instantiated as three actors. It is also the **Hong et al. *MetaGPT* SOP** pattern adapted to a single workflow.

### 9.3 Scratchpad bridge

The shared scratchpad is the **memory bus**. Every agent's writes to the scratchpad go through `POST /v1/write`. Reads go through `GET /v1/read`. This is what makes the memory bus the *experimental subject* rather than a hidden detail. With compression on, every write goes through the active `Compressor`; with compression off, the compressor is a no-op identity transform.

### 9.4 No-compression control

Every experiment runs a `compressor=none` control condition (plan risk register: "*AutoGen runtime bugs confound coordination measurements ... no-compression-control condition in every experiment; pin AutoGen version*"). If the control condition's variance dominates the signal-of-interest's variance, the experiment is *invalid* and is flagged in the results CSV.

---

## 10. Evaluation and statistics

### 10.1 Metrics (plan S5.2)

| Family | Metric | Module |
|--------|--------|--------|
| Quality | F1, EM, ROUGE-L, BERTScore | `m6.evaluation.metrics.qa` |
| Coordination | success, sub-task-acc, rounds, critic-flagged | `m6.evaluation.metrics.coordination` |
| Hallucination | DeepEval `Faithfulness`, RAGAS `faithfulness`, manual annotation on 100 random | `m6.evaluation.metrics.hallucination` |
| Compression | input/output token ratio, total tokens per workflow | `m6.evaluation.metrics.compression` |
| Cost | EUR/workflow via the cost ledger | `m6.evaluation.metrics.cost` |
| Latency | p50 / p95 ms/query, per-stage and end-to-end | `m6.evaluation.metrics.latency` |
| Tag preservation | fraction of slots whose recovered tags are a superset of source tags | `m6.evaluation.metrics.tag_preservation` |

### 10.2 LLM-as-judge

* **Judge.** `gpt-4o-mini` (cheap, deterministic with `temperature=0`).
* **Cross-check.** `claude-sonnet-4-6` on a **10% sample** (plan S5.2). If judge-vs-cross-check agreement drops below 0.85 (Cohen's kappa), the judge is recalibrated.
* **Anti-bias.** The judge sees a position-randomised pair, never which compressor produced which answer.

### 10.3 Statistical protocol (plan S5.3)

* **5 seeds per condition.**
* **Bootstrap CI** alongside means (10 000 resamples; `scipy.stats.bootstrap`).
* **Paired bootstrap** for compressor-vs-compressor comparisons on matched instances.
* **Mann-Whitney U** for the cliff-detection (H2) test.
* **Holm correction** within each hypothesis family. Families: `{H1, H2}`, `{H3}`, `{H4}`.
* **Effect sizes** -- Cliff's delta for ordinal outcomes, Cohen's d for continuous. Always reported alongside p-values.

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

Two linear pieces meeting at `t`. Minimised by `scipy.optimize.differential_evolution`; `t` is unique because we constrain the right-piece slope <= left-piece slope.

`CliffFit` exposes `tau, slope_left, slope_right, intercept, rmse, drop_rel`. H2 calls it directly.

---

## 11. Results layout and reproducibility

### 11.1 Filesystem

```
results/
+-- h1/
|   +-- 7b/<run_id>/qa_vs_coord.csv
|   +-- 7b/<run_id>/spearman.json
|   +-- 7b/<run_id>/manifest.yaml
+-- h2/
|   +-- 7b/<run_id>/cliff_per_cell.csv
|   +-- 7b/<run_id>/mann_whitney.json
|   +-- 13b/...
+-- h3/
+-- h4/
```

Each `<run_id>` is `YYYYmmdd-HHMMSS-<git_sha>-<config_hash>`. The `manifest.yaml` carries the full resolved config, the `m6.__version__`, the Python version, the platform, and the hash of every input file used.

### 11.2 Reproduce-a-figure protocol

Every figure has a `make reproduce-ch<N>` target. The target:
1. Reads `configs/experiments/<hypothesis>.yaml`.
2. Re-derives the run_id from the resolved config hash.
3. Skips work that has already been done (idempotent).
4. Writes a CSV to `results/<hypothesis>/.../`.
5. Renders the figure with `m6.evaluation.plot.figure_for(hypothesis)`.

### 11.3 Final reproducibility package (plan S4.6 Month 10)

* Docker compose (`docker/docker-compose.yml`) brings up the memory bus + benchmark.
* HuggingFace hub release for the tag-preserving compressor.
* GitHub release tag for everything.
* Model cards (compressor-side) and data cards (benchmark-side) live in `docs/model_cards/` and `docs/data_cards/`.
* `README.md` carries one-command reproduction.

---

## 12. Grounding sources -- what each cited paper actually says

Concise factual summary of the papers the codebase rests on.

### 12.1 Compression and memory

| Paper | What it actually says | Where we use it |
|-------|----------------------|-----------------|
| **Jiang et al. *LLMLingua* (EMNLP 2023)** | Coarse-to-fine prompt compression using a small LM (BERT/GPT-2) to predict and drop low-utility tokens. Ratios up to 20x with <=1 pp drop on GSM8K. | Baseline reference; not directly run because superseded by LLMLingua-2. |
| **Jiang et al. *LongLLMLingua* (ACL 2024)** | Same idea, applied to long contexts; introduces question-aware coarse-to-fine. | Reference for the **P2 retrieve-then-compress** classical setup (S7.2). |
| **Pan et al. *LLMLingua-2* (ACL Findings 2024)** | Task-agnostic data distillation; XLM-RoBERTa token classifier; faster, multilingual. | **The `lingua2` compressor.** Calibration on NarrativeQA/HotpotQA. |
| **Mu et al. *Gist Tokens* (NeurIPS 2023)** | Learn special "gist" tokens that compress prefix prompts via attention-mask training. | Architectural cousin to ICAE; cited in discussion. |
| **Chevalier et al. *AutoCompressor* (EMNLP 2023)** | Reconstruction loss with summary vectors; LoRA-adapted; frozen decoder. | **Basis for our dual loss.** Plan S2.2 lists it as the basis. |
| **Ge et al. *ICAE* (ICLR 2024)** | Soft-prompt encoder LoRA-adapted, frozen decoder, reconstruction objective; 4x compression with minor drop on NaturalQuestions. | **Basis for the soft-prompt architecture.** Plan S2.2 lists it as the basis. |
| **Wang et al. *ICF / In-Context Former* (EMNLP 2024)** | Cross-attention compression, no reconstruction loss; faster training. | Discussion-only. |
| **Fei et al. *Semantic compression* (ACL 2024)** | Semantic-unit-level (not token-level) compression. | Discussion-only. |
| **Rae et al. *Compressive Transformers* (ICLR 2020)** | Compressed memory in transformer attention; smooth monotonic degradation. | H2 counter-example anchor. |
| **Guo et al. *Dynamic context compression for RAG* (2025)** | Relevance-conditional compression for RAG. | **Direct analogue of P3.** |
| **Cheng et al. *xRAG* (2024)** | Extreme-compression-aware RAG; hard-prompt style. | P1's compress-step. |
| **Li, Liu, Su, Collier. *Prompt Compression: A Survey* (NAACL 2025)** | Taxonomy + evaluation framework for prompt compression. | Used for terminology consistency. |

### 12.2 Multi-agent systems and memory

| Paper | What it actually says | Where we use it |
|-------|----------------------|-----------------|
| **Wu et al. *AutoGen* (2023)** | Multi-agent conversation framework with role-based agents and tool use. | **Agent runtime -- v0.4 pinned.** |
| **Hong et al. *MetaGPT* (ICLR 2024)** | SOP-based multi-agent collaboration; structured artifact passing. | Planner-worker-critic SOP. |
| **Li et al. *CAMEL* (2023)** | Role-playing dialogue for autonomous agents. | Dialogue trace diversity. |
| **Shinn et al. *Reflexion* (NeurIPS 2023)** | Self-reflection / verbal reinforcement for sequential decision-making. | Critic's REVISE loop. |
| **Packer et al. *MemGPT / Letta* (2023)** | OS-like memory hierarchy for LLMs with paged virtual context. | Reference for the scratchpad-vs-archive split. |
| **Xu et al. *A-MEM* (NeurIPS 2025)** | Agent memory with Zettelkasten-style linking. | Discussion. |
| **Chhikara et al. *Mem0* (arXiv 2504.19413, 2025)** | Scalable long-term memory with embedding + extraction. | Industry comparator. |
| **Rasmussen et al. *Zep* (arXiv 2501.13956, 2025)** | Temporal knowledge graph memory. | Discussion. |
| **Zhang et al. *AgentPrune* (arXiv 2410.02506, 2024)** | Sparsify agent communication graph; reduce cost. | Discussion of P3 alternatives. |
| **Wang et al. *AgentDropout* (arXiv 2503.18891, 2025)** | Randomly drop agents during training. | Robustness sub-claim in Chapter 5. |
| **Park et al. *Collaborative Memory: Dynamic Access Control* (arXiv 2505.18279, 2025)** | ACL-aware shared memory; per-fragment provenance. | **C4 tag-preserving design ancestor.** |
| **Ye et al. *KVCOMM* (NeurIPS 2025)** | KV-cache compression for communication-efficient multi-agent inference. | Discussion. |
| **Haseeb. *Context Engineering for Multi-Agent LLM Code Assistants* (arXiv 2508.08322, 2025)** | Training-distribution mismatch causes coordination breakdown. | Discussion. |
| **Yu et al. *MemAgent* (arXiv 2507.02259, 2025)** | Memory-augmented agent with retrieval over its own past actions. | Discussion. |
| **Anthropic, *How we built our multi-agent research system* (June 2025)** | Orchestrator-worker topology; **token usage explains 80% of performance variance**. | **H1/H2 motivation, the closest published analogue to the coordination cliff.** Plan S9.2 verbatim. |
| **Rajasekaran et al. *Effective context engineering for AI agents* (Anthropic, 2025)** | Names **compaction, tool-result clearing, memory, just-in-time retrieval** as the four primitives. | **C3 P3 design grounding.** |
| **Anthropic, *Managing context on the Claude Developer Platform* (Oct 2025)** | **84% token reduction on a 100-turn web-search evaluation via context editing.** | Compression-ratio metric calibration. Plan S9.2 verbatim. |

### 12.3 RAG, long-context, benchmarks

| Paper | What it actually says | Where we use it |
|-------|----------------------|-----------------|
| **Lewis et al. *RAG* (NeurIPS 2020)** | The original retrieval-augmented generation. | P1/P2/P3 ancestor. |
| **Sarthi et al. *RAPTOR* (ICLR 2024)** | Recursive abstractive summarisation; hierarchical index. | P1 informant. |
| **Edge et al. *GraphRAG* (2024)** | Graph-summarised retrieval. | P3 routing-logic informant. |
| **Gutierrez et al. *HippoRAG / HippoRAG 2* (NeurIPS 2024 / ICML 2025)** | Memory-organisation-as-graph. | Discussion of why P3 looks the way it does. |
| **Asai et al. *Self-RAG* (ICLR 2024)** | Reflection tokens gate retrieval. | P3 gating analogue. |
| **Bai et al. *LongBench / v2* (2024-2025)** | Long-context QA benchmark. | External calibration. |
| **Liu et al. *Lost in the Middle* (TACL 2024)** | Position bias on long contexts. | H1 anchor. |
| **Mialon et al. *GAIA* (2023)** | Multi-step agent benchmark Level 1-3. | Motivates multi-agent framing; Level 1 used as a sanity check (plan S5.1). |
| **Liu et al. *AgentBench* (ICLR 2024)** | Multi-environment agent benchmark. | Selected envs (OS, DB, LTP) on critical path; rest non-critical. |
| **Anthropic, *Contextual Retrieval* (Sep 2024)** | Prepend chunk-level Claude-generated context before embedding; **~$1.02 / 1M document tokens with prompt caching**. | **P1 pre-processor baseline.** Plan S9.3 verbatim. |

### 12.4 Privacy-aware retrieval

| Paper | Where we use it |
|-------|-----------------|
| **Zhou et al. *Privacy-Aware RAG* (2025)** | Threat model anchor for tag-preservation design. |
| **Bassit & Boddeti. *SecureRAG* (2025)** | Threat model reference. |
| **Li et al. *SecurityLingua* (CoLM 2025)** | Adversarial-robustness reference. |

### 12.5 Internal FCG documents

The following internal FCG documents informed the architecture and cost model. They are referenced by title; see the thesis bibliography for full citations.

* **Saleh et al. *Towards Message Brokers for Generative AI* (ACM CSUR 2025)** -- Survey of traditional and modern brokers with a five-direction research agenda. The **GenAI agent reference architecture (Fig. 3, p. 14)** -- perception/brain/actuation -- is the topology our planner-worker-critic loop instantiates. Defines the at-least-once delivery semantics adopted by the audit log.

* **FCG integrator architecture** -- Specifies seven integrator subsystems. Defines the cross-market hash chain pattern the thesis bus inherits for its audit chain (S3.3). The thesis bus inherits the audit-chain pattern but **not** the auction subsystems.

* **FCG software architecture** -- Translates the integrator into a buildable stack. Defines the dual messaging topology and the transcript hash chain `H_t = SHA-256(epoch_id || bids_hash || alloc_hash || payments_hash || H_{t-1})` that the thesis bus implements in simplified form (S3.3).

* **FCG financial analysis** -- Five-year financial projection for the University of Oulu. Provides the frontier cloud pricing (USD 3 / 1M input, USD 15 / 1M output) and the on-premises marginal cost (EUR 0.05/1M tokens) that ground the cost model in S7.4.

* **FCG use-case document** -- Narrative companion listing the institutional system inventory and eight vignettes. The focal Vignette 3.7 (period-end project reporting) shapes the C1 family (a) workload generator.

---

## 13. Risks, kill-switches, and time-boxes

The plan's risk register (S7) is the source of truth. Engineering-relevant kill-switches are encoded in the codebase so they fire automatically:

| Risk | Code-level kill-switch |
|------|------------------------|
| ICAE port to MLX/MPS slips | `m6.compressors.training.train_icae` time-boxed to **14 days** -- after which it emits a stop-the-line event and the experiment falls back to AutoCompressor. |
| MLX lacks InfoNCE primitive | Detected at startup by `m6.compressors.training.loss._probe_mlx_nce`; falls back to PyTorch-MPS. |
| 13B fine-tuning OOMs at rank 8 | Trainer catches OOM, halves the rank, retries once, then declares 7B-only. |
| H2 falsified (no cliff) | `m6.experiments.h2_coordination_cliff` reports the negative finding via `result.falsified = True`; the chapter writer renders the "no cliff" version of the figure. |
| AutoGen runtime bugs confound metrics | Every experiment includes a `compressor=none` control condition. If `var(control) >= var(treatment)`, the experiment is flagged `invalid` in `manifest.yaml`. |
| A new paper publishes C2's exact result | Out-of-band; we keep an arXiv alert running, not encoded here. |

Time-boxes are enforced. They are not advisory.

---

## 14. Glossary

* **ACL bitmask** -- `uint64` capability vector attached to a fragment or slot. Bit `i` represents capability `i`.
* **Classification tier** -- 0..4 lattice: PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED < SECRET.
* **C1 / C2 / C3 / C4** -- the four contributions (plan S2).
* **Coordination cliff t\*** -- the compression ratio above which coordination success drops by >=30% (plan S3 H2).
* **Compressor variant V1/V2/V3** -- dense-embedding / ICAE-style / instruction-aware filter (plan S6.1).
* **Dual-objective loss** -- `L_recon + lambda * L_NCE` (plan S2.2).
* **FCG** -- Future Computing Group at the CSE Research Unit, University of Oulu.
* **InfoNCE** -- Information Noise-Contrastive Estimation loss; the L\_NCE term.
* **ICAE** -- In-Context Autoencoder (Ge et al. ICLR 2024).
* **LoRA** -- Low-Rank Adaptation; PEFT-style fine-tuning.
* **MPS** -- Apple Metal Performance Shaders -- the PyTorch backend on Apple Silicon.
* **MLX** -- Apple's native ML framework for Apple Silicon.
* **MemIndex** -- Saleh et al. ACM TAAS 2025 baseline architecture this thesis extends.
* **Memory slot** -- one of `M` learnable `[MEM]` token positions in the ICAE encoder. The compressed representation.
* **Plan / `plan.md`** -- the implementation plan; ground truth for scope and schedule.
* **Scratchpad** -- the in-memory dict in the storage layer; the agents' shared working surface.
* **Slot** -- abbreviation of `CompressedSlot` (S3.1).
* **Tag head** -- the per-slot MLP that predicts `(acl_mask, classification)` in the C4 variant (S5.5).
* **t\*** -- the coordination cliff threshold from H2.
* **Vignette 7 (a.k.a. 3.7)** -- period-end project reporting across eight university systems; the canonical workload C1 family (a) is built around.

---

*End of document.*
