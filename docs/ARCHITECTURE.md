# Architecture

This document is the canonical system view for the `m6-thesis` codebase. It is short on purpose — the long-form discussion lives in [`TECHNICAL_REFERENCE.md` §2 and §6](TECHNICAL_REFERENCE.md). Read this first; that second.

## 1. Layered topology

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                          ACCESS LAYER (FastAPI)                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  POST /v1/write    POST /v1/subscribe    GET /v1/read    GET /v1/audit  │ │
│  │     │                  │                     │              │           │ │
│  │  PolicyMiddleware ─────┴────┐         StructLogMiddleware  │           │ │
│  │     │                       │           OtelMiddleware     │           │ │
│  └─────┼───────────────────────┼─────────────────────────────────────────┘ │
│        ▼                       ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                     MemoryBusService (business logic)                  │ │
│  │  compress(...) → store(...) → audit(...) → publish_event(...)          │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
                         │              │              │
                         ▼              ▼              ▼
┌──────────────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐
│   COMPRESSION LAYER      │  │  STORAGE LAYER   │  │  AGENT RUNTIME (AutoGen) │
│                          │  │                  │  │                          │
│  Compressor (Protocol)   │  │  AuditLog (sqlite)│  │  Planner ─► Workers ─►   │
│   ├─ lingua2             │  │  Scratchpad (dict)│  │     ◄───── Critic        │
│   ├─ filter              │  │  VectorStore (faiss)│ │                          │
│   ├─ icae                │  │                  │  │  bridge → memory_bus     │
│   └─ icae-tag (C4)       │  │  CostLedger      │  │                          │
└──────────────────────────┘  └──────────────────┘  └──────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        INFERENCE BACKEND (Protocol)                          │
│          mlx_backend │ ollama_backend │ openai_backend                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

Every arrow is a typed Python interface defined as a `typing.Protocol` in the importer's module.

## 2. Data flow for one `POST /v1/write`

1. Client sends `{fragment, tags, task_hint}` with bearer token.
2. `PolicyMiddleware` resolves the requester's ACL bitmask from the token claims and inserts it into the request scope.
3. `MemoryBusService.write(...)` calls the active `Compressor.compress(...)`.
4. The returned `CompressedSlot` is appended to the audit log (with `event_type=WRITE`) and indexed in FAISS.
5. The audit log's append trigger computes `chain_hash = SHA-256(prev_hash ‖ payload_hash)` and refuses any later `UPDATE` or `DELETE`.
6. The cost ledger gets a row if a paid backend was invoked.
7. The response includes `slot_id`, `chain_hash`, and a backpointer for `GET /v1/audit/{slot_id}`.

## 3. Data flow for one `GET /v1/read/{slot_id}`

1. `PolicyMiddleware` resolves requester ACL.
2. `MemoryBusService.read(...)`:
   * Fetch slot from the scratchpad or rehydrate from FAISS.
   * Check `requester.acl ⊇ slot.tags.acl_mask` and `requester.classification ≥ slot.tags.classification`. Deny otherwise — and append a `DENY` row to the audit log so the deny event is itself auditable.
   * Append `READ` to the audit log.
3. The response is the `CompressedSlot`, with the audit row id.

## 4. Component → file map

| Capability | File |
|------------|------|
| App factory | `src/m6/memory_bus/api.py::create_app` |
| Schemas | `src/m6/memory_bus/schemas.py` |
| Service | `src/m6/memory_bus/service.py::MemoryBusService` |
| Policy middleware | `src/m6/memory_bus/policy.py` |
| SQLite audit log | `src/m6/memory_bus/storage/sqlite_audit.py` |
| FAISS vector store | `src/m6/memory_bus/storage/vector_store.py` |
| Scratchpad | `src/m6/memory_bus/storage/scratchpad.py` |
| CompressedSlot dataclass | `src/m6/memory_bus/slot.py` |
| Compressor protocol | `src/m6/compressors/base.py` |
| LLMLingua-2 | `src/m6/compressors/lingua2.py` |
| ICAE | `src/m6/compressors/icae.py` |
| Filter | `src/m6/compressors/filter.py` |
| Tag-preserving | `src/m6/compressors/tag_preserving.py` |
| Dual-objective trainer | `src/m6/compressors/training/train_icae.py` |
| InfoNCE primitive | `src/m6/compressors/training/loss.py` |
| Benchmark generator | `src/m6/benchmark/generator.py` |
| Workload families | `src/m6/benchmark/workloads/{fact_aggregation,constraint_satisfaction,multi_step_retrieval}.py` |
| Coordination metrics | `src/m6/evaluation/metrics/coordination.py` |
| Statistical protocol | `src/m6/evaluation/statistics.py` |
| Cliff fitter | `src/m6/evaluation/cliff_fitting.py` |
| RAG P1/P2/P3 | `src/m6/pipelines/{p1_compress_retrieve,p2_retrieve_compress,p3_joint}.py` |
| Cost model | `src/m6/pipelines/cost_model.py` |
| Agent orchestration | `src/m6/agents/orchestrator.py` |
| Inference backends | `src/m6/inference/{mlx,ollama,api}_backend.py` |
| Experiment runners | `src/m6/experiments/h{1..4}_*.py` |
| CLI | `src/m6/cli.py` |

## 5. Configuration sources of truth

```
configs/
├── benchmark/
│   └── c1-v0.1.yaml             # canonical C1 v0.1 generator config
├── training/
│   ├── icae-7b.yaml             # default ICAE training (dual-objective)
│   └── icae-7b-tags.yaml        # C4 variant
├── experiments/
│   ├── h1.yaml
│   ├── h2.yaml
│   ├── h3.yaml
│   └── h4.yaml
└── models/
    ├── llama-3.1-8b-instruct.yaml
    └── qwen2.5-14b-instruct.yaml
```

Resolved config = environment variables (`.env`) **overridden by** the YAML chosen at the CLI **overridden by** explicit `--<key>=<value>` arguments. The resolution happens in `m6.config.settings.resolve(...)` and produces a frozen `pydantic.BaseModel`.

## 6. Telemetry

* **Structured logs** (`structlog` JSON to stdout) — every API call and every backend call.
* **OTel traces** via `OTEL_EXPORTER_OTLP_ENDPOINT`. Optional; disabled by default.
* **Cost ledger** (`cost_ledger` SQLite table) — every paid call.
* **Audit log** (`audit_log` SQLite table) — every state transition.

## 7. Deployment

| Mode | How | Used for |
|------|-----|----------|
| Native dev | `make bus-dev` | Iteration. |
| Docker compose | `make docker-up` | Repro of the deliverable. |
| HuggingFace Hub release | trainer side; loaded at startup | Compressor artefacts. |
| GitHub release tag | `vX.Y.Z` | Full repro of every chapter figure. |

## 8. Future work

The storage layer protocols (audit log, vector store, scratchpad) are designed to be replaceable. Any conforming implementation can be swapped in without changes to the access or compression layers.
