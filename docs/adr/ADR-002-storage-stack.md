# ADR-002: Storage stack — SQLite + in-memory dict + FAISS-CPU

**Status:** Accepted
**Date:** 2026-05-12
**Deciders:** Syed Abdullah Hassan, Lauri Lovén

## Context

The memory bus has three storage workloads:
1. **Append-only audit log.** Every state transition must be recorded immutably with a verifiable hash chain. Modelled after `software-architecture.pdf` §3.5's `audit_transcript` table.
2. **Active scratchpad.** Hot, ephemeral, ms-scale read/write. AutoGen agents thrash on this.
3. **Compressed-slot retrieval.** Vector search by semantic similarity for the RAG pipelines (C3).

External constraints:
* One M4 Pro 48 GB. No external cluster (plan §1).
* The FCG platform team will adopt the **integration interface**, not the storage stack (plan §6.3). Storage choice is reversible.
* The audit log must support a tamper-evident hash chain.

## Decision

Three storage subsystems, one technology each, behind three `Protocol`s in `src/m6/memory_bus/storage/`:

| Workload | Technology | Module |
|----------|------------|--------|
| Audit log | **SQLite** (WAL mode, `journal_mode=WAL`, `synchronous=NORMAL`) | `sqlite_audit.py` |
| Scratchpad | **In-memory `dict` with TTL** + thread-safe lock | `scratchpad.py` |
| Vector store | **FAISS-CPU** (`IndexHNSWFlat` with cosine, M=32, efSearch=128) | `vector_store.py` |

Each is wrapped in a Protocol:
* `AuditLog.append(event) -> AuditRow`, `read(slot_id) -> list[AuditRow]`, `chain_hash() -> bytes`.
* `Scratchpad.get(slot_id) -> Slot | None`, `put(slot)`, `expire()`.
* `VectorStore.add(slot_id, embedding)`, `search(query, k) -> list[Hit]`, `save(path)`, `load(path)`.

`MemoryBusService` depends on the Protocols, never on the concrete classes.

## Options considered

### Option A — Postgres + Redis + Qdrant up-front

| Dimension | Assessment |
|-----------|------------|
| Complexity | High (3 daemons + migrations). |
| Cost | Hours of devops; no signal for the thesis. |
| Scalability | Excellent. |
| Team familiarity | Medium. |

**Pros.** Production-ready. Matches `software-architecture.pdf` Phase 1.
**Cons.** No empirical signal for the thesis. Adds operational burden Lauri does not want at M0.

### Option B — SQLite + dict + FAISS *(chosen)*

| Dimension | Assessment |
|-----------|------------|
| Complexity | Low (zero daemons). |
| Cost | Trivial. |
| Scalability | Capped at ~10⁵ slots; sufficient for C1 (150 workflows × ~50 slots each = ~7.5K). |
| Team familiarity | High. |

**Pros.** No ops. Reproducible from a single file. ACID via SQLite. Hash chain implementable in SQL. FAISS is the de facto vector store in the LlamaIndex ecosystem we already depend on.
**Cons.** Single-host only. Concurrent writers must serialize on the SQLite write lock — fine for a single FastAPI worker.

### Option C — DuckDB + Chroma

| Dimension | Assessment |
|-----------|------------|
| Complexity | Medium. |
| Cost | Low. |
| Scalability | Better than SQLite for analytics; vector side is fine. |
| Team familiarity | Lower. |

**Pros.** DuckDB is excellent for the analytics we run on results CSVs.
**Cons.** DuckDB is not append-only; the hash-chain trigger is awkward. Chroma adds a second persistence boundary.

## Trade-off analysis

Option B sacrifices the doctoral-phase scaling story for a clean thesis-phase deliverable. The seam at the `Protocol` boundary means **swapping in Postgres + Redis Cluster + Qdrant is a 1–2 day rewrite of three files**, not an architectural change.

The hash-chain mechanism (mirroring `software-architecture.pdf` §3.5) is implementable in SQLite via an `INSTEAD OF UPDATE`/`DELETE` trigger and a `BEFORE INSERT` trigger that computes `chain_hash = SHA-256(prev_hash ‖ payload_hash)`. This is tested in `tests/unit/memory_bus/test_audit_chain.py::test_tamper_detection`.

## Consequences

**Easier.**
* Single-file backups (`audit.sqlite`, `index.faiss`).
* Trivial reproducibility — ship the files with the GitHub release tag.
* Tests do not need fixtures.

**Harder.**
* Multi-host. **D7's problem.**
* Concurrent writes from many FastAPI workers — work around by running with `--workers 1` and pushing parallelism into the agent runtime.

**Revisit when.**
* SQLite write throughput becomes the bottleneck (we are nowhere near this).
* Multiple FastAPI workers are needed (they are not for the single-machine reference impl).

## Action items

1. [x] Implement `SQLiteAuditLog` with the hash-chain trigger.
2. [x] Implement `InMemoryScratchpad` with TTL.
3. [x] Implement `FaissVectorStore` with cosine HNSW.
4. [x] Write unit test for tamper detection.
5. [ ] Write `BENCHMARKS.md` measuring write throughput for the thesis-scale workload (~7.5K slots).
