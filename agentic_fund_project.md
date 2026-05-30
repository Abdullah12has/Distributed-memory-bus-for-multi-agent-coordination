# Fund Platform — Architecture Handoff for the Thesis Agent

> **Document purpose.** This is a one-shot, self-contained reference for an LLM agent that is writing the Master's thesis *"Distributed Memory Bus for Multi-Fragment LLM Workflows: Context Compression, the Coordination Cliff, and Privacy."* The thesis builds a research-grade memory bus with FAISS, ACL tags, hash-chained audit log, and a protected-fact privacy metric, evaluated against a synthetic multi-fragment benchmark. The Fund Platform — described here — is a production multi-agent investment platform that has *independently* converged on many of the same architectural abstractions (compaction, three-tier memory, three-stage rails, atomic-write append-only audit log, typed event stream, schema-as-truth, file-based planner/worker handoff). Several thesis-load-bearing pieces are *missing* from this codebase (no FAISS, no ACL tags, no hash-chained log, no protected-fact reader) — that gap is the thesis's contribution story and is documented explicitly in §14.
>
> Read §0–§2 in order. After that, sections are independently consumable; jump to the one the chapter you're writing needs. Code excerpts are quoted verbatim with `path:line_start-line_end` headers so you do not need to fetch source files to write.

---

## §0 — Reading guide

### Audience and scope

You (the thesis agent) already have:

- The thesis draft (`draft1.md` covering Chs 3–8 in pass 1).
- The thesis terminology locked in `CONTEXT.md`.
- The ADR decisions for the thesis pipeline (ADR-006 calibrated regime, ADR-007 CAAC framing, ADR-008 model name, ADR-009 multi-fragment scope).

This document gives you what you don't have: concrete architectural grounding in a real multi-agent production system that ships the abstractions your thesis defines. Use it to:

1. **Ground Ch 3 §3.1** ("Architecture") by citing the Fund Platform as the production-grade pattern your bus generalises.
2. **Ground Ch 7 §7.5** ("The memory bus and the H4 channel") by citing the three-stage rails as the privacy-infrastructure pattern your protected-fact metric extends.
3. **Ground Ch 8 §8.5 / §8.6** ("Limitations" / "Future work") by citing the gaps in this codebase as concrete integration targets for the thesis's design.

The document is *not*:

- A user manual for the Fund Platform. (Operators read `README.md` and `docs/architecture/IMPLEMENTATION_DOC.md`.)
- A defence of the Fund Platform's design choices. (Those are anchored in ADR-0001 through ADR-0015 in `docs/architecture/adr/`.)
- An exhaustive description. (15 packages, 345 tests, 58 endpoints; this doc covers ~10 components.)

### Terminology mapping (preview — full version in Appendix B)

| Fund Platform term | Thesis term | Notes |
|---|---|---|
| `Compactor` | compressor | Single naive strategy (summarise middle); thesis catalogue has four. |
| `compaction_threshold_tokens` | θ_q (operationalised) | Per-agent context-budget knob analogous to the per-family success threshold. |
| `CompactionEvent { tokens_before, tokens_after }` | q(r) measurement | On-the-wire compression-ratio sample. |
| `ArchivalMemory` | `Fragment` | Field-by-field comparison in §5. |
| `GuardrailsEngine.check_retrieval` | retrieval-time ACL filter slot | Where the thesis's CONFIDENTIAL-tag check would live. |
| `_write_validated_json` | audit-log write primitive | Atomic temp+rename + JSON Schema validation + quarantine. |
| `file_sync_log` table | append-only audit log | Has `content_hash` field but no chain (thesis adds the SHA-256 chain). |
| `BAAI/bge-large-en-v1.5` retrieval | (thesis only) | The Fund Platform has *no* retrieval/vector code; this is a gap, not a parallel. |

### How this document is organised

| § | Section |
|---|---|
| 0 | Reading guide (you are here) |
| 1 | System overview |
| 2 | Architectural parallels at a glance |
| 3 | Agent SDK and the per-turn agent loop |
| 4 | Compaction subsystem (deep dive) |
| 5 | Three-tier memory subsystem |
| 6 | Event taxonomy and observability |
| 7 | Guardrails (rails) and privacy infrastructure |
| 8 | File-based audit log and atomic-write protocol |
| 9 | Per-agent YAML configuration model |
| 10 | Tracker and Cluster Manager — multi-fragment parallels |
| 11 | Orchestration: Temporal workflows |
| 12 | LinkML schema-as-source-of-truth |
| 13 | Production `data/` directory layout |
| 14 | What's *missing* — the thesis's contribution surface |
| 15 | What NOT to import into the thesis |
| 16 | Suggested insertion points by thesis chapter |
| A | File index |
| B | Glossary |

---

## §1 — System overview

The Fund Platform is a multi-agent AI investment fund analysis system. Five autonomous agents (Gate, Analyst, Tracker, Chinese Quant, Cluster Manager) analyse companies, score them, track week-over-week changes, and surface investment ideas to a human Operator through a Palantir-style canvas UI. Strategy C1 ("High Net Cash") is the first cluster; five more are planned. Agents communicate exclusively through files on disk; every state mutation is auditable end-to-end.

```
┌──────────────────────────────────────────────────────────────────────┐
│  Operator Canvas (Next.js)                            :8006          │
│  - WebSocket connection to /ws/events for live event stream          │
│  - REST API for trigger, approval, browse                            │
└──────────────┬───────────────────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────────────────┐
│  Platform API (FastAPI)                              :8005           │
│  - 58 endpoints across 6 routers                                     │
│  - ConnectionManager fan-out via /ws/events                          │
│  - /api/events/broadcast receives agent events                       │
└──────┬──────────────────────────────────────────────────┬────────────┘
       │ trigger workflow                                  │ broadcast event
       │                                                   │
┌──────▼───────────────────────────────┐  ┌────────────────▼───────────┐
│  Temporal Orchestrator               │  │ Postgres (mirror)          │
│  - 5 workflows, 1 activity each      │  │ - hello_summaries          │
│  - RetryPolicy(max_attempts=2)       │  │ - file_sync_log            │
│  - Activities run agent.run_blocking │  └────────────────▲───────────┘
└──────┬───────────────────────────────┘                   │
       │ launches Agent.run() loop                          │ upsert
       │                                                    │
┌──────▼─────────────────────────────────┐    ┌─────────────┴──────────┐
│  Agent SDK                             │    │ FileSync               │
│  - Agent.run() turn loop               │    │ - watchdog Observer    │
│  - Compactor (Haiku summariser)        │    │ - validator (jsonschema) │
│  - GuardrailsEngine (3-stage rails)    │    │ - quarantine on fail   │
│  - MemoryStore (core/recall/archival)  │    │ - mirror to Postgres   │
└──────┬─────────────────────────────────┘    └─────────────▲──────────┘
       │ tool calls via MCP protocol                         │ watch
       │                                                     │
┌──────▼────────────────────────┐                  ┌─────────┴────────┐
│  MCP servers                  │                  │ data/             │
│  - filesystem (atomic R/W)    │─── writes ──────►│  universe/{tkr}/  │
│  - yahoo-finance              │                  │  cluster_1/state/ │
│  - edgar                      │                  │  _quarantine/     │
│  - e2b-sandbox (-I subprocess)│                  │  _backups/        │
│  - web-search (SearXNG)       │                  └───────────────────┘
└───────────────────────────────┘
```

**Key invariants:**

1. **Files in `data/` are the source of truth** (ADR-0003, ADR-0008). Postgres is a derived, read-only mirror. If the bus is wiped, agents rebuild from disk.
2. **Every external capability is wrapped as an MCP server** (ADR-0007). Tools never reach the network directly from agent code.
3. **All LLM calls go through LiteLLM** (ADR-0005). No direct Anthropic/OpenAI SDK calls in app code.
4. **LinkML is the single source of truth for data shapes** (ADR-0004). Pydantic, JSON Schema, SQL DDL, GraphQL, TS types are generated.
5. **Agents communicate only through files.** No in-process IPC; no shared memory. This makes the system fully auditable.

**Out of scope for this document:** the UI/Canvas implementation, the LLM gateway internals, the SearXNG and EDGAR adapters, the Quant agent's statistical specifics, the cost analytics, the operator approval queue.

---

## §2 — Architectural parallels at a glance

| Fund Platform component | Thesis concept | Where in the thesis | This doc § |
|---|---|---|---|
| `Compactor` (single naive summariser) | compression layer (4 strategies + CAAC) | Ch 3 §3.2, Ch 5 §5.1 | §4 |
| `Agent.run()` per-turn loop with inline compaction | planner/worker shape | Ch 3 §3.1 architecture diagram | §3 |
| `MemoryStore` three-tier (core/recall/archival) | memory bus fragment layer | Ch 3 §3.1 architecture, Ch 8 §8.6 integration target | §5 |
| `ArchivalMemory.embedding: list[float] \| None` (unused) | `Fragment.embedding` + FAISS index | Ch 3 §3.1, Ch 8 §8.6 | §5, §14 |
| `GuardrailsEngine` three-stage rails | input/output/retrieval rails for ACL/privacy | Ch 7 §7.5 privacy infrastructure | §7 |
| Built-in PII regexes (SSN/CC/IBAN) | shallow-filter baseline for the protected-fact attack | Ch 7 §7.1 (potential baseline comparison) | §7 |
| `_write_validated_json` atomic write | audit-log write primitive | Ch 3 §3.1 bus implementation | §8 |
| `file_sync_log` append-only table | append-only audit log | Ch 3 §3.1 audit log | §8 |
| `file_sync_log.content_hash` field (TODO, unpopulated) | SHA-256 hash chain | Ch 3 §3.1 (the chain is the thesis's contribution over this) | §8, §14 |
| `CompactionEvent { tokens_before, tokens_after }` | q(r) on-the-wire measurement | Ch 3 §3.5 instrumentation, Ch 5 §5.5 q(r) sampling | §6 |
| Typed `AgentEvent` taxonomy | experiment-harness event schema | Ch 3 §3.5 reproducibility | §6 |
| Per-agent YAML `compaction_threshold_tokens` | θ_q (operational analogue) | Ch 5 §5.4 calibrated regime | §9 |
| Tracker activity (append-only weekly log) | per-fragment audit-log entries | Ch 3 §3.1 audit log shape | §10 |
| Cluster Manager activity (reads ~10 fragments) | planner-over-fragments | Ch 3 §3.4 single-call planner setup | §10 |
| Temporal workflows + activities | durable planner/worker boundary | Ch 8 §8.6 multi-round future work | §11 |
| LinkML schemas → 5 artifact targets | single-source-of-truth data model | Ch 3 §3.1 data shapes | §12 |
| `e2b-sandbox` `_run_python` (`-I` isolated subprocess) | held-out protected-fact reader pattern | Ch 7 §7.1, Ch 8 §8.3 reader engineering | §7 |
| `data/universe/{TICKER}/` per-ticker folder | per-source fragment grouping | Ch 4 C1 benchmark fragment structure | §13 |

---

## §3 — Agent SDK and the per-turn agent loop

The Agent SDK at `packages/agent-sdk/src/agent_sdk/` is the LLM-bearing engine every activity uses. The relevant headline classes:

| File | Lines | Purpose |
|---|---|---|
| `agent.py` | 520 | `Agent` + `AgentConfig`. The per-turn loop. |
| `compactor.py` | 132 | `Compactor`. Threshold-triggered summariser. See §4. |
| `memory.py` | 112 | `MemoryStore` + `ArchivalMemory`. See §5. |
| `rails/engine.py` | 162 | `GuardrailsEngine`. See §7. |
| `events.py` | 107 | Typed event hierarchy. See §6. |
| `registry.py` | 90 | `ToolRegistry` with `fnmatch` filtering. |
| `llm.py` | 285 | `LiteLLMClient` chokepoint, retry+fallback. |

### `AgentConfig` — the per-agent budget and policy model

`packages/agent-sdk/src/agent_sdk/agent.py:48-83`:

| Field | Type | Default | Meaning |
|---|---|---|---|
| `name` | str | — | Agent identity |
| `role` | str | — | Role used in system prompt |
| `model` | str | — | Primary LLM (LiteLLM model string) |
| `fallback_model` | str \| None | None | Used if primary exhausts retries |
| `max_turns` | int | 50 | Max iterations before `MaxTurnsExceeded` |
| `budget_tokens` | int | 200_000 | Token budget for the whole run |
| `budget_usd` | float | 5.0 | USD cost budget |
| `compaction_threshold_tokens` | int | 60_000 | **The per-agent θ_q analogue** — context size that triggers compaction |
| `permission_mode` | str | "default" | One of `default`, `plan`, `bypass`, `acceptedit` |
| `allowed_tools` | list[str] | [] | fnmatch patterns for tool whitelisting |
| `permissions_override` | dict[str, str] | {} | Per-tool permission overrides |
| `can_spawn_subagents` | bool | False | Enable sub-agent spawning |
| `max_subagent_depth` | int | 0 | Max nesting depth |
| `allowed_subagent_types` | list[str] | [] | Whitelisted subagent type names |

### `Agent.run()` — the per-turn loop

The loop is a Python async generator. Per turn it (1) checks input rail, (2) decides whether to compact, (3) calls the LLM, (4) checks output rail, (5) enforces budget, (6) dispatches tool calls (parallel for safe tools, serial for unsafe), (7) re-injects tool results. The relevant block (`packages/agent-sdk/src/agent_sdk/agent.py:144-180`) is:

```python
        # Input guardrails: check task content before LLM call
        if self._guardrails and messages:
            task_text = " ".join(m.content for m in messages if m.content)
            rail_result = self._guardrails.check_input(task_text)
            if not rail_result.passed:
                logger.error(
                    "agent.input_rail_blocked",
                    rail=rail_result.rail_name,
                    violation=rail_result.violation,
                )
                raise RuntimeError(f"Input guardrail blocked: {rail_result.violation}")

        # Fix #5: single filter() call builds both tool map and LLM definitions
        matched_tools = self._tool_registry.filter(self._config.allowed_tools)
        tools = {t.name: t for t in matched_tools}
        tool_defs = self._build_tool_definitions_from(matched_tools)

        turn = 0
        last_response: LLMResponse | None = None
        all_artifacts: list[str] = []

        while turn < self._config.max_turns:
            turn += 1

            # Compaction check (spec §5.1)
            if self._compactor:
                est_tokens = self._compactor.estimate_tokens(messages)
                if est_tokens > self._config.compaction_threshold_tokens:
                    tokens_before = est_tokens
                    messages = await self._compactor.compact(messages)
                    tokens_after = self._compactor.estimate_tokens(messages)
                    yield CompactionEvent(
                        agent_run_id=ctx.agent_run_id,
                        turn=turn,
                        tokens_before=tokens_before,
                        tokens_after=tokens_after,
                    )
```

The next block (`agent.py:182-207`) is the LLM call wrapped in output guardrails + budget:

```python
            # LLM call
            response = await self._llm.complete(
                model=self._config.model,
                messages=messages,
                tools=tool_defs if tool_defs else None,
                fallback_model=self._config.fallback_model,
                metadata=self._llm_metadata(ctx, turn),
            )
            last_response = response

            # Output guardrails: check LLM response text
            if self._guardrails and response.content:
                rail_result = self._guardrails.check_output(response.content)
                if not rail_result.passed:
                    logger.warning(
                        "agent.output_rail_violation",
                        rail=rail_result.rail_name,
                        violation=rail_result.violation,
                        turn=turn,
                    )

            ctx.budget.add(
                tokens=response.usage.total_tokens,
                cost_usd=response.cost_usd,
            )
            ctx.budget.check_or_raise()
```

Note that output-rail violations are **logged but not raised**. This is the conservative "warn don't block" stance the rails take by default (dev mode); see §7 for the `RailConfig.enforce` toggle.

### Tool dispatch — the planner/worker shape

`agent.py:367-434` is the dispatcher. The relevant invariants:

1. **Permission gating is always serial** (rate-limited LLM-driven approval flow).
2. **Tools split into safe (`is_concurrency_safe=True`) and unsafe.**
3. **Safe tools run in parallel** via `asyncio.gather(..., return_exceptions=True)`.
4. **Unsafe tools run sequentially.**

```python
        # 2. Split safe/unsafe
        safe = [c for c in permitted if tools[c.name].is_concurrency_safe]
        unsafe = [c for c in permitted if not tools[c.name].is_concurrency_safe]

        # 3. Run safe in parallel
        # Fix #7: use return_exceptions=True to handle CancelledError gracefully
        if safe:
            safe_results = await asyncio.gather(
                *[self._invoke_tool(c, tools[c.name], ctx) for c in safe],
                return_exceptions=True,
            )
            for tc, res in zip(safe, safe_results, strict=True):
                if isinstance(res, BaseException):
                    results[tc.id] = ToolResult(success=False, error=str(res))
                else:
                    results[tc.id] = res

        # 4. Run unsafe sequentially
        for tc in unsafe:
            results[tc.id] = await self._invoke_tool(tc, tools[tc.name], ctx) 
```

**Thesis parallel.** This is the closest analogue in any real codebase to your thesis's *single LLM call with all compressed fragments visible* setup (per ADR-009). The Fund Platform's planner/worker shape lives inside one process, not across LangGraph nodes — but the in-loop compaction step (`agent.py:169-180`) is *exactly* the engineering pattern your bus design assumes: a per-turn token-budget check that triggers compression before the next LLM call. Quote `CompactionEvent`'s `tokens_before` / `tokens_after` (`events.py:76-80`) in Ch 3 §3.5 as evidence that q(r) is already a logged quantity in production multi-agent systems.

---

## §4 — Compaction subsystem (deep dive)

`packages/agent-sdk/src/agent_sdk/compactor.py` (132 lines) is the closest direct parallel to the thesis's compression layer in the entire Fund Platform codebase.

### The strategy

One strategy: *preserve system + recent N, summarise the middle, replace the middle with a `[Previous conversation summary]` user-role message*. The summariser is a cheap Haiku call. The threshold is per-agent (`AgentConfig.compaction_threshold_tokens`). Token estimation is `chars // 4` (`compactor.py:45`).

### The compaction prompt (verbatim)

`packages/agent-sdk/src/agent_sdk/compactor.py:21-24`:

```python
_COMPACTION_PROMPT = """Summarize the following conversation history into a concise summary.
Preserve all key facts, tool call results, decisions made, and important data.
Do NOT lose any specific numbers, scores, file paths, or ticker information.
Output only the summary, no preamble."""
```

This is the prompt-engineered "critical-token-retention" surrogate the production system uses. Note the explicit instruction to preserve numbers, scores, file paths, and tickers — exactly the regex classes your C1 family-a critical-token taxonomy targets (multi-digit numbers, see Ch 4 §4.2).

### The `compact()` method (verbatim)

`packages/agent-sdk/src/agent_sdk/compactor.py:52-121`:

```python
    async def compact(self, messages: list[Message]) -> list[Message]:
        """Compact the message list by summarizing the middle section.

        Preserves:
        - First message (system prompt)
        - Last ``preserve_recent`` messages (recent context)

        Replaces everything in between with a single summary message.

        Returns:
            New message list with compacted history.

        Raises:
            CompactionFailed: If the summarization LLM call fails.
        """
        if len(messages) <= self._preserve_recent + 1:
            return messages

        # Split: system | middle | recent
        system = messages[0] if messages[0].role == "system" else None
        if system:
            middle = messages[1 : -self._preserve_recent]
            recent = messages[-self._preserve_recent :]
        else:
            middle = messages[: -self._preserve_recent]
            recent = messages[-self._preserve_recent :]

        if not middle:
            return messages

        tokens_before = self.estimate_tokens(messages)

        # Build the text to summarize
        middle_text = self._format_messages_for_summary(middle)

        try:
            response = await self._llm.complete(
                model=self._model,
                messages=[
                    Message(role="system", content=_COMPACTION_PROMPT),
                    Message(role="user", content=middle_text),
                ],
            )
            summary_text = response.content
        except Exception as e:
            raise CompactionFailed(f"Compaction LLM call failed: {e}") from e

        # Build compacted message list
        summary_message = Message(
            role="user",
            content=f"[Previous conversation summary]\n{summary_text}",
        )

        result: list[Message] = []
        if system:
            result.append(system)
        result.append(summary_message)
        result.extend(recent)

        tokens_after = self.estimate_tokens(result)
        logger.info(
            "compactor.compacted",
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            messages_before=len(messages),
            messages_after=len(result),
            middle_messages_summarized=len(middle),
        )

        return result
```

### `Compactor` configuration

| Field | Type | Default | Meaning |
|---|---|---|---|
| `llm` | LiteLLMClient | (required) | LLM client for summarisation |
| `model` | str | `"fund/claude-haiku-4-5"` | Cheap model for the summary call |
| `preserve_recent` | int | 4 | Number of recent messages preserved verbatim |

### What this compactor is *not*

- **Not token-level.** Unlike LLMLingua-2, the Fund Platform Compactor operates on whole messages, not tokens.
- **Not learned.** A pre-trained summariser is *used* (Haiku) but no special compression model is trained.
- **Not adaptive per fragment.** Unlike CAAC, the compactor applies a uniform policy regardless of which messages carry critical information.
- **Not benchmarked.** The Fund Platform measures `tokens_before` / `tokens_after` (via `CompactionEvent`) but no coordination-success rubric exists in this codebase to compare against.

### Thesis parallel

Compactor sits where your `Compressor` protocol sits — between the agent loop and the LLM call. Compactor's signature `compact(messages) -> messages` is a coarser version of your `compress(fragment, target_ratio) -> CompressedSlot`. The `CompactionEvent { tokens_before, tokens_after }` is the production-system instance of your q(r) on-the-wire measurement.

**Where this lands in the thesis:**

- **Ch 3 §3.2 (compressor catalogue table).** Add a row in the *Production baselines* category that cites Compactor as the dominant production strategy (cheap LLM, threshold-triggered, system+recent preservation). The thesis's four training-free compressors are evaluated against this default.
- **Ch 3 §3.5 (reproducibility).** Adopt `CompactionEvent`'s field schema (`tokens_before`, `tokens_after`, `event_id`, `agent_run_id`, `turn`) as the experiment-harness logging contract.
- **Ch 8 §8.6 (future work).** "A natural deployment story for this thesis is replacing the production Haiku-summariser Compactor with a thresholded LLMLingua-2 wrapper that respects the per-family cliff τ\*. The `compaction_threshold_tokens` knob (`AgentConfig` in `packages/agent-sdk/src/agent_sdk/agent.py:63`) is the per-agent θ_q that CAAC would consume."

---

## §5 — Three-tier memory subsystem

`packages/agent-sdk/src/agent_sdk/memory.py` (112 lines) defines a three-tier memory model: **core** (KV block in system prompt), **recall** (recent message window), **archival** (long-term, designed for vector search). The archival tier is the closest in-codebase analogue to your `Fragment` record.

### The `ArchivalMemory` shape

`packages/agent-sdk/src/agent_sdk/memory.py:30-41`:

```python
class ArchivalMemory(BaseModel):
    """A single archival memory entry."""

    memory_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    key: str
    value: str
    source_run_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(UTC) + timedelta(days=90))
    embedding: list[float] | None = None
```

### Field-by-field comparison to the thesis `Fragment`

| Thesis `Fragment` field | `ArchivalMemory` equivalent | Notes |
|---|---|---|
| `slot_id` | `memory_id` | Both UUID, both client-generated. |
| `payload.text` | `value` | Direct equivalent. |
| `tags` (provenance + ACL) | `agent_id`, `source_run_id` | Provenance is rich; **ACL is missing entirely** — no `classification: PUBLIC|INTERNAL|CONFIDENTIAL` field. |
| `embedding` | `embedding: list[float] \| None` | Field present; **unused in production retrieval path**. |
| `key` (lookup) | `key` | Both string-keyed; thesis bus also supports content-addressed retrieval via FAISS. |
| `created_at` | `created_at` | Direct equivalent. |
| `expires_at` | `expires_at` | Direct equivalent (90-day default in Fund Platform; thesis bus uses TTL/LRU on the scratchpad). |

### The substring-search admission

`packages/agent-sdk/src/agent_sdk/memory.py:68-87`:

```python
    async def search_archival(
        self,
        agent_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[ArchivalMemory]:
        """Search archival memory by naive substring match.

        Production would use pgvector cosine similarity.
        """
        memories = self._archival.get(agent_id, [])
        now = datetime.now(UTC)
        # Filter expired and match by substring
        results: list[ArchivalMemory] = []
        for mem in memories:
            if mem.expires_at < now:
                continue
            if query.lower() in mem.key.lower() or query.lower() in mem.value.lower():
                results.append(mem)
        return results[:top_k]
```

The `"Production would use pgvector cosine similarity"` docstring is the explicit acknowledgement that the embedded vector field exists but the substring-matcher is a test-grade placeholder. **The thesis's FAISS-backed retrieval is the missing half of this memory bus.**

### `MemoryConfig` shape

`packages/agent-sdk/src/agent_sdk/memory.py:20-28`:

| Field | Type | Default | Meaning |
|---|---|---|---|
| `core_block_size_tokens` | int | 2_000 | Max tokens for core block in system prompt |
| `archival_enabled` | bool | True | Enable long-term memory |
| `recall_window_messages` | int | 30 | Size of recent message window |
| `archival_top_k` | int | 5 | Number of archival results per search |
| `archival_expiry_days` | int | 90 | Default expiry for archival memories |

### Thesis parallel

The Fund Platform's archival tier has the *shape* of your bus's fragment record but is *missing the retrieval engine and the ACL tags*. Your bus generalises by (a) adding FAISS as the production-grade retriever, (b) introducing classification tags as first-class fragment fields, and (c) wiring an instruction-aware compressor between the writer and the index.

**Where this lands in the thesis:**

- **Ch 3 §3.1.** Cite the `ArchivalMemory` shape as evidence that production multi-agent platforms converge on a recognisable fragment record but defer the retrieval layer (per the `Production would use pgvector` comment). Frame your bus as the *complete* version of this pattern: same fields plus the ACL tag, plus the FAISS index, plus the SHA-256 chain.
- **Ch 8 §8.6 (future work / integration target).** "The Fund Platform memory schema (`packages/agent-sdk/src/agent_sdk/memory.py`) is one field-addition away from this thesis's bus — adding `classification: ClassificationTag` to `ArchivalMemory` and wiring `search_archival` to a FAISS index instead of substring matching converts the Fund Platform's stub retrieval surface into a deployment of this design."

---

## §6 — Event taxonomy and observability

`packages/agent-sdk/src/agent_sdk/events.py` (107 lines) defines a typed event hierarchy. The events are JSON-serialisable Pydantic models, emitted by `Agent.run()` and broadcast to live operators via WebSocket.

### Base event

`packages/agent-sdk/src/agent_sdk/events.py:26-33`:

```python
class AgentEvent(BaseModel):
    """Base class for all agent events."""

    event_id: str = Field(default_factory=_event_id)
    timestamp: datetime = Field(default_factory=_now)
    agent_run_id: str
    turn: int
```

Every event carries a UUID, a timestamp, the run that produced it, and the turn within that run.

### Event subtypes

| Event | Fields | Line |
|---|---|---|
| `LLMCallEvent` | `model`, `prompt_tokens`, `completion_tokens`, `cost_usd`, `stop_reason`, `tool_use_blocks` | 35–43 |
| `ToolCallEvent` | `tool_name`, `args`, `result`, `permission_mode_applied` | 46 |
| `ApprovalRequiredEvent` | `tool_name`, `args`, `reasoning`, `estimated_cost_usd` | 55 |
| `SubagentSpawnedEvent` | `subagent_type`, `subagent_run_id`, `brief_summary`, `budget_allocated_usd` | 67 |
| **`CompactionEvent`** | **`tokens_before`, `tokens_after`** | **76–80** |
| `MemoryExtractedEvent` | `memories_written` | 83 |
| `DoneEvent` | `result: AgentResult` | 103 |

### The compression-ratio measurement

`packages/agent-sdk/src/agent_sdk/events.py:76-80`:

```python
class CompactionEvent(AgentEvent):
    """Emitted when context compaction occurs."""

    tokens_before: int
    tokens_after: int
```

This is the on-the-wire compression-ratio measurement: `ratio = tokens_after / tokens_before` per event. Combined with `event_id`, `timestamp`, `agent_run_id`, `turn`, every compression event in the system is uniquely identifiable, ordered, and bound to its run context.

### `LLMCallEvent` — what the cost/usage row looks like

`packages/agent-sdk/src/agent_sdk/events.py:35-43`:

```python
class LLMCallEvent(AgentEvent):
    """Emitted after each LLM call completes."""

    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    stop_reason: str
    tool_use_blocks: list[dict[str, Any]] = Field(default_factory=list)
```

Fired per turn (`agent.py:209-218`). Captures the model invoked (after potential fallback), token usage, cost, stop reason, and the serialised tool-use blocks.

### How events reach the operator

The flow is: agent emits event → activity passes `on_event=broadcast_event` callback → `broadcast_event` POSTs to Platform API `/api/events/broadcast` → ConnectionManager fan-outs to all active WebSocket clients on `/ws/events`.

`apps/orchestrator/src/orchestrator/event_broadcaster.py` (full file, 53 lines):

```python
"""Broadcast agent events to the Platform API WebSocket.

During agent runs, the worker calls this to POST events to
``/api/events/broadcast`` so the canvas UI receives live updates.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
import structlog

from agent_sdk.events import AgentEvent

logger = structlog.get_logger(__name__)

_API_URL = os.environ.get("PLATFORM_API_URL", "http://localhost:8005")

# Reuse a single client to avoid creating a new TCP connection per event
_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=5.0)
    return _client


async def broadcast_event(event: AgentEvent) -> None:
    """POST an agent event to the Platform API for WebSocket broadcast."""
    url = f"{_API_URL}/api/events/broadcast"
    payload: dict[str, Any] = {
        "event_type": type(event).__name__,
        **event.model_dump(mode="json"),
    }
    try:
        client = _get_client()
        resp = await client.post(url, json=payload)
        if resp.status_code != 200:
            logger.warning(
                "event_broadcast.failed",
                status=resp.status_code,
                event_type=payload["event_type"],
            )
    except httpx.ConnectError:
        # Platform API not running — silently skip
        pass
    except Exception as exc:
        logger.debug("event_broadcast.error", error=str(exc))
```

The broadcaster is a single async function with a singleton httpx client (TCP-reuse optimisation), fire-and-forget semantics, and silent failure if the Platform API is unreachable. This is important: **events are not persisted by the broadcaster**. Persistence happens only on the FileSync mirror side (see §8).

### Platform API receive surface

The `/api/events/broadcast` POST endpoint, `apps/platform-api/src/platform_api/routers/workflows.py:101-106`:

```python
@router.post("/api/events/broadcast")
async def broadcast_event(event: dict[str, Any]) -> dict[str, str]:
    """Broadcast an event to all connected WebSocket clients."""
    if _ws_manager:
        await _ws_manager.broadcast(event)
    return {"status": "broadcasted"}
```

The `ConnectionManager` in `apps/platform-api/src/platform_api/app.py:55-82`:

```python
class ConnectionManager:
    """Manages active WebSocket connections for live event streaming."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)
        logger.info("ws.client_connected", total=len(self._connections))

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.remove(websocket)
        logger.info("ws.client_disconnected", total=len(self._connections))

    async def broadcast(self, message: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for connection in self._connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for conn in dead:
            self._connections.remove(conn)
            logger.info("ws.dead_connection_removed", total=len(self._connections))
```

### Thesis parallel

The Fund Platform event taxonomy is the production analogue of your experiment-harness instrumentation. Three observations the thesis can lean on:

1. **`CompactionEvent` already carries `tokens_before` / `tokens_after`.** Quote this verbatim in Ch 3 §3.5 as evidence that q(r) is a logged quantity in real systems, not a research-only metric.
2. **Events are *not* persisted in the broadcast path.** Only the file-write side (FileSync) writes a durable record. This is a *gap* your bus's append-only audit log fills explicitly.
3. **Event schema is typed and stable across runs** — your experiment CSVs can adopt this schema (UUID `event_id`, ISO timestamp, `agent_run_id`, `turn`) without reinventing.

**Where this lands in the thesis:**

- **Ch 3 §3.5 (reproducibility).** "The event taxonomy our experiment logger conforms to (`packages/agent-sdk/src/agent_sdk/events.py`) is the production-grade pattern; we extend it with per-event `compressor_id`, `target_ratio`, `achieved_ratio` fields to make the q(r) sample point complete."

---

## §7 — Guardrails (rails) and privacy infrastructure

`packages/agent-sdk/src/agent_sdk/rails/engine.py` (162 lines) implements a three-stage rails engine: **input** (before LLM), **output** (after LLM), **retrieval** (before injecting external data). It is, line for line, the production engineering pattern your Ch 7 privacy story needs.

### The three checkpoints

`packages/agent-sdk/src/agent_sdk/rails/engine.py:85-120`:

```python
    def check_input(self, content: str) -> RailResult:
        """Check input content before it reaches the LLM."""
        if self._config.check_prompt_injection:
            result = self._check_prompt_injection(content, "input")
            if not result.passed:
                return self._handle_violation(result)

        if self._config.check_pii:
            result = self._check_pii(content, "input")
            if not result.passed:
                return self._handle_violation(result)

        return RailResult(passed=True, stage="input")

    def check_output(self, content: str) -> RailResult:
        """Check LLM output before tool dispatch."""
        if self._config.check_pii:
            result = self._check_pii(content, "output")
            if not result.passed:
                return self._handle_violation(result)

        return RailResult(passed=True, stage="output")

    def check_retrieval(self, content: str) -> RailResult:
        """Check externally-retrieved content before context injection."""
        if self._config.check_prompt_injection:
            result = self._check_prompt_injection(content, "retrieval")
            if not result.passed:
                return self._handle_violation(result)

        if self._config.check_pii:
            result = self._check_pii(content, "retrieval")
            if not result.passed:
                return self._handle_violation(result)

        return RailResult(passed=True, stage="retrieval")
```

The **retrieval-stage** check is the hook the thesis's CONFIDENTIAL-tag ACL filter slots into. Every fragment retrieved from external storage (or, in the thesis's case, every slot returned from the FAISS retriever) passes through `check_retrieval` before injection into the LLM's prompt.

### The dev/prod enforce toggle

`packages/agent-sdk/src/agent_sdk/rails/engine.py:144-161`:

```python
    def _handle_violation(self, result: RailResult) -> RailResult:
        if self._config.enforce:
            logger.error(
                "guardrails.violation_blocked",
                rail=result.rail_name,
                stage=result.stage,
                violation=result.violation,
            )
            return result
        else:
            logger.info(
                "guardrails.violation_logged",
                rail=result.rail_name,
                stage=result.stage,
                violation=result.violation,
                enforce=False,
            )
            return RailResult(passed=True, rail_name=result.rail_name, stage=result.stage)
```

`enforce=False` (dev mode) logs the violation but returns `passed=True`, allowing the run to continue. `enforce=True` (prod) returns `passed=False`, which the agent loop treats as a hard block (input stage) or a warning (output stage).

### PII regexes (verbatim)

`packages/agent-sdk/src/agent_sdk/rails/engine.py:64-68`:

```python
_PII_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "SSN"),
    (r"\b\d{16}\b", "credit_card"),
    (r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}[A-Z0-9]{0,16}\b", "IBAN"),
]
```

Three regex patterns: US SSN, 16-digit credit card, EU IBAN format.

### Prompt-injection blocklist (verbatim)

`packages/agent-sdk/src/agent_sdk/rails/engine.py:51-60`:

```python
    blocked_patterns: list[str] = field(
        default_factory=lambda: [
            r"ignore previous instructions",
            r"ignore all previous",
            r"disregard your instructions",
            r"you are now",
            r"act as if you",
            r"pretend to be",
        ]
    )
```

### `RailConfig` shape

| Field | Type | Default | Meaning |
|---|---|---|---|
| `enforce` | bool | False | Dev (log only) vs prod (block) |
| `check_pii` | bool | True | Enable PII detection |
| `check_prompt_injection` | bool | True | Enable jailbreak blocklist |
| `check_off_topic` | bool | True | Reserved (unused in implementation) |
| `check_numerical_hallucination` | bool | True | Reserved (unused) |
| `allowed_topics` | list[str] | (defaults) | Whitelist of allowed topics |
| `blocked_patterns` | list[str] | (the 6 above) | Prompt-injection regex patterns |

### The held-out subprocess pattern (`e2b` sandbox)

A related engineering pattern lives in the e2b sandbox MCP. `packages/mcp-servers/e2b-sandbox/src/mcp_server_e2b/server.py:28-75`:

```python
def _run_python(
    code: str,
    timeout_s: int = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """Execute Python code in a subprocess with timeout."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
        script_path = f.name

    try:
        # Strip secrets from subprocess environment (security: ADR-0013)
        tmp = tempfile.gettempdir()
        safe_env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", tmp)}
        result = subprocess.run(  # noqa: S603 — script_path is a temp file we wrote
            [sys.executable, "-I", script_path],  # -I: isolated mode, no site-packages
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=tempfile.gettempdir(),
            env=safe_env,
        )

        stdout = result.stdout[:_MAX_OUTPUT_BYTES]
        stderr = result.stderr[:_MAX_OUTPUT_BYTES]

        return {
            "exit_code": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "truncated": len(result.stdout) > _MAX_OUTPUT_BYTES
            or len(result.stderr) > _MAX_OUTPUT_BYTES,
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Execution timed out after {timeout_s}s",
            "truncated": False,
        }
    except Exception as e:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "truncated": False,
        }
    finally:
        Path(script_path).unlink(missing_ok=True)
```

Constants: `_DEFAULT_TIMEOUT_S = 30`, `_MAX_OUTPUT_BYTES = 50_000`. This is the engineering pattern for a **held-out hermetic subprocess** — strip secrets from env, run with `-I` (no site-packages), cap output, enforce timeout. Your thesis's protected-fact-recovery reader (Llama-3.1-8B in a sandboxed process) wants exactly this pattern; the e2b sandbox is a working reference implementation.

### Thesis parallel

Three direct uses for Ch 7 (privacy chapter) and Ch 8 (limitations / future work):

1. **`check_retrieval` is the slot for your ACL filter.** Quote the three-stage rail structure verbatim and frame your bus's CONFIDENTIAL-tag check as a specialisation of `check_retrieval`.
2. **The PII regexes are a "shallow-filter baseline".** Your held-out Llama-3.1-8B reader can attack both the unfiltered baseline and the PII-regex-filtered baseline; the *gap* between these two is the empirical signal that compression-aware ACL is needed (regexes don't cover protected facts).
3. **The e2b `-I` subprocess pattern is the engineering substrate for your reader.** Cite `_run_python` (line numbers above) in Ch 7 §7.1 footnote when describing the reader's hermetic-execution context. Production-grade hardening (Firecracker microVMs) is noted in ADR-0013.

**Where this lands in the thesis:**

- **Ch 7 §7.5 (memory bus and the H4 channel).** "Production multi-agent platforms (e.g., the Fund Platform's `GuardrailsEngine` at `packages/agent-sdk/src/agent_sdk/rails/engine.py`) implement a three-stage rail check (input / output / retrieval). The bus described in this thesis specialises the retrieval stage by introducing classification tags on fragments and an ACL filter that drops or downgrades sub-PII protected facts that the shallow regex baselines (SSN / credit card / IBAN) cannot detect."
- **Ch 8 §8.6 (future work).** "An enforcement layer for the bus (compressor switching on protected-fact-recovery threshold breach) is the natural extension; the `GuardrailsEngine.enforce` toggle (`rails/engine.py:144`) is the dev/prod policy switch that pattern would adopt."

---

## §8 — File-based audit log and atomic-write protocol

The Fund Platform's "files are source of truth" decision (ADR-0003, ADR-0008) makes the file system the durability and audit-evidence substrate. The implementation has three load-bearing pieces: (1) the **atomic write** primitive in the filesystem MCP, (2) the **FileSync watcher** that validates and mirrors writes, (3) the **append-only `file_sync_log`** table.

### The write-flow diagram

```
                  Agent calls filesystem.write_*  tool
                                │
                                ▼
                _write_validated_json (filesystem MCP server)
                                │
            ┌───────────────────┴───────────────────┐
            │                                       │
            ▼                                       ▼
   ┌────────────────┐                    ┌──────────────────────┐
   │ Schema invalid │                    │   Schema valid       │
   │ (LinkML/JSON   │                    │                      │
   │  Schema fail)  │                    │ tempfile.mkstemp     │
   └────────┬───────┘                    │ (in target folder)   │
            │                            │   ▼                  │
            ▼                            │ write payload to tmp │
   ┌────────────────┐                    │   ▼                  │
   │  copy to       │                    │ os.replace(tmp,      │
   │  data/         │                    │   target.json)       │
   │  _quarantine/  │                    │  ← atomic            │
   │  with _invalid │                    └──────────┬───────────┘
   │  suffix        │                               │
   └────────────────┘                               │
                                                    ▼
                                        FileSync watcher
                                          (watchdog Observer)
                                                    │
                                       ┌────────────┴────────────┐
                                       │                         │
                                       ▼                         ▼
                          ┌──────────────────────┐  ┌────────────────────────┐
                          │ validator.py runs    │  │ db.py records          │
                          │  jsonschema validate │  │  file_sync_log row     │
                          │  (LinkML-generated   │  │  (valid, error,        │
                          │   schemas)           │  │   content_hash[TODO])  │
                          └──────────┬───────────┘  └────────────────────────┘
                                     │
                          ┌──────────┴───────────┐
                          │                      │
                          ▼                      ▼
                ┌────────────────┐    ┌──────────────────────┐
                │ Valid:         │    │ Invalid:             │
                │ upsert to      │    │ copy to              │
                │ hello_summaries│    │ data/_quarantine/    │
                │ (Postgres)     │    │ with _invalid suffix │
                └────────────────┘    └──────────────────────┘
```

### The atomic-write primitive

`packages/mcp-servers/filesystem/src/mcp_server_filesystem/server.py:124-189`:

```python
def _write_validated_json(
    ticker: str,
    data: dict[str, Any],
    tool_name: str,
    quarantine_dir: Path | None = None,
) -> dict[str, Any]:
    """Write a schema-validated JSON file with atomic write (ADR-0003).

    Generic writer used by write_hello_summary, write_analyst_record, etc.
    """
    if tool_name not in _WRITE_SCHEMAS:
        return {"error": f"Unknown write tool: {tool_name}"}

    schema_file, class_name, output_filename = _WRITE_SCHEMAS[tool_name]
    data_dir = _get_data_dir()
    folder = _safe_ticker_path(data_dir, ticker)
    quarantine = quarantine_dir or (data_dir / "_quarantine")

    if folder is None:
        return {"error": f"Invalid ticker path: {ticker!r}"}

    if not folder.is_dir():
        return {"error": f"Ticker folder {ticker!r} not found"}

    # Validate
    error = _validate_against_schema(data, schema_file, class_name)
    if error:
        quarantine.mkdir(parents=True, exist_ok=True)
        invalid_name = output_filename.replace(".json", "_invalid.json")
        quarantine_path = quarantine / f"{ticker}_{invalid_name}"
        quarantine_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        logger.warning(
            "filesystem.schema_validation_failed",
            ticker=ticker,
            tool=tool_name,
            error=error,
            quarantine_path=str(quarantine_path),
        )
        return {
            "error": f"Schema validation failed: {error}",
            "quarantine_path": str(quarantine_path),
        }

    # Atomic write
    target = folder / output_filename
    content = json.dumps(data, indent=2, default=str)

    fd, tmp_path = tempfile.mkstemp(dir=str(folder), prefix=f".{output_filename}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, target)
    except Exception:
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
        raise

    logger.info(
        "filesystem.file_written",
        ticker=ticker,
        tool=tool_name,
        path=str(target),
        size_bytes=len(content),
    )

    return {"path": str(target), "size_bytes": len(content), "ticker": ticker}
```

Four invariants:

1. **Validate before write.** Schema-invalid data is *never* placed in the canonical location.
2. **Quarantine instead of discard.** Invalid writes are preserved in `data/_quarantine/` with an `_invalid` suffix and a logged warning. Operator can post-hoc inspect.
3. **Temp file in the same directory as the target.** Required for atomic rename to be cross-filesystem-safe.
4. **`os.replace(tmp, target)` is the atomicity.** On POSIX, `os.replace` is atomic; the file either exists in its old state or its new state, never partial.

### The FileSync state machine

`apps/file-sync/src/file_sync/handler.py` (137 lines, the full handler):

```python
class SyncHandler:
    """Processes file change events from the data/ directory."""

    def __init__(
        self,
        *,
        data_dir: Path,
        quarantine_dir: Path,
        validator: FileValidator,
        db_conn: DbConnection | None = None,
    ) -> None:
        self._data_dir = data_dir
        self._quarantine_dir = quarantine_dir
        self._validator = validator
        self._db_conn = db_conn

    def handle_file_event(self, file_path: Path) -> dict[str, Any]:
        """Process a single file change event.

        Returns a status dict with keys: path, valid, action, error.
        """
        if not file_path.exists():
            return {"path": str(file_path), "valid": False, "action": "skipped", "error": "gone"}

        if file_path.suffix != ".json":
            return {"path": str(file_path), "valid": True, "action": "skipped", "error": None}

        # Skip temp files from atomic writes
        if file_path.name.startswith("."):
            return {"path": str(file_path), "valid": True, "action": "skipped", "error": None}

        ticker = self._extract_ticker(file_path)
        valid, error = self._validator.validate_file(file_path)

        if not valid:
            self._quarantine(file_path, ticker)
            self._log_sync_event(file_path, ticker, valid=False, error_message=error)
            logger.warning(
                "file_sync.validation_failed",
                path=str(file_path),
                error=error,
            )
            return {"path": str(file_path), "valid": False, "action": "quarantined", "error": error}

        # Replicate to Postgres
        self._replicate(file_path, ticker)
        self._log_sync_event(file_path, ticker, valid=True)

        logger.info("file_sync.replicated", path=str(file_path), ticker=ticker)
        return {"path": str(file_path), "valid": True, "action": "replicated", "error": None}

    def scan_directory(self) -> list[dict[str, Any]]:
        """Full reconciliation scan of the data/ directory.

        Processes every JSON file, validating and replicating each.
        Used at startup and for nightly reconciliation (ADR-0008).
        """
        results: list[dict[str, Any]] = []
        for json_file in sorted(self._data_dir.rglob("*.json")):
            if json_file.name.startswith("."):
                continue
            result = self.handle_file_event(json_file)
            results.append(result)
        return results
```

Note `scan_directory()` — a full *reconciliation pass*. This is the engineering equivalent of "nightly bus integrity check": at startup or scheduled, walk every JSON file and re-validate. Any drift between disk and Postgres is corrected.

### The append-only audit log

`apps/file-sync/src/file_sync/db.py:24-36`:

```python
_CREATE_SYNC_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS file_sync_log (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    ticker TEXT,
    synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid BOOLEAN NOT NULL,
    error_message TEXT,
    content_hash TEXT,
    size_bytes INTEGER
);
"""
```

Field-by-field:

| Field | Meaning |
|---|---|
| `id` | Auto-increment PK |
| `file_path` | Absolute path on disk |
| `file_name` | Basename (e.g. `analyst_record.json`) |
| `ticker` | Extracted from path (e.g. `TEST_GB`) |
| `synced_at` | Timestamp of replication event |
| `valid` | Boolean (true if passed validation) |
| `error_message` | Validation error if invalid |
| **`content_hash`** | **TEXT field — defined but not currently populated** |
| `size_bytes` | File size in bytes |

The `content_hash` column is the most thesis-relevant field. It is *defined* but *not yet computed*: the schema acknowledges the need for content tamper-evidence, but the production implementation has not wired the SHA-256 calculation. This is the engineering gap your thesis's SHA-256 hash chain fills explicitly (ADR-0005-equivalent in the thesis).

### Schema-driven validation in FileSync

`apps/file-sync/src/file_sync/validator.py` uses the LinkML-generated JSON Schemas to validate. The filename → schema mapping:

```python
_FILE_SCHEMA_MAP: dict[str, tuple[str, str]] = {
    "hello_summary.json": ("hello", "HelloSummary"),
    "analyst_record.json": ("analyst_record", "AnalystRecord"),
    "tracker_weekly_history.json": ("tracker", "TrackerWeeklyHistory"),
    "ranking.json": ("cluster_state", "Ranking"),
}
```

Each entry says: when validating a file matching this filename pattern, load schema `{schema_name}.json` from `packages/ontology/src/generated/json_schema/`, validate against class `{class_name}`. The schemas themselves are LinkML-generated (see §12).

### Thesis parallel

The Fund Platform's audit-log infrastructure is **almost** the thesis's bus audit log:

| Thesis bus audit log | Fund Platform | Gap |
|---|---|---|
| Per-event entry | `file_sync_log` row | — |
| Validate-before-commit | `_write_validated_json` + jsonschema | — |
| Quarantine on validation fail | `data/_quarantine/` | — |
| Atomic temp+rename writes | `tempfile.mkstemp` + `os.replace` | — |
| **SHA-256 content hash per row** | `content_hash` field exists but unpopulated | **Thesis adds the calculation** |
| **Hash chain `hash_self = SHA-256(slot_id \|\| op \|\| t \|\| hash_prev)`** | not implemented | **Thesis adds the chain** |
| Per-fragment ACL tag | no ACL field anywhere | **Thesis adds `classification`** |

**Where this lands in the thesis:**

- **Ch 3 §3.1 (bus implementation).** "Production multi-agent platforms achieve tamper-evidence through atomic writes + validation quarantine + append-only mirror, but stop short of cryptographic chaining (cf. the Fund Platform's `file_sync_log` schema in `apps/file-sync/src/file_sync/db.py:24-36`, which defines a `content_hash` column but does not yet populate it). Our bus extends this pattern with (a) populated SHA-256 hashes per row and (b) a hash-chained `hash_prev` field that makes any post-hoc mutation detectable. This refinement is the engineering substance of contribution C1 (audit log)."

---

## §9 — Per-agent YAML configuration model

The Fund Platform's five C1 agents (`Analyst`, `Tracker`, `Gate`, `Cluster Manager`, `Chinese Quant`) share a unified YAML config schema. Each config file is at `agents/{agent-name}/config.yaml`.

### Comparison across all five

| Field | Analyst | Tracker | Gate | CM | Quant |
|---|---|---|---|---|---|
| `name` | c1-analyst | c1-tracker | c1-gate-agent | c1-cluster-manager | c1-chinese-quant |
| `role` | analyst | tracker | gate_agent | cluster_manager | chinese_quant |
| `cluster_id` | C1 | C1 | null | C1 | C1 |
| `model` | fund/claude-opus-4 | fund/claude-haiku-4-5 | fund/claude-sonnet-4-5 | fund/claude-opus-4 | fund/claude-sonnet-4-5 |
| `fallback_model` | claude-sonnet-4-5 | claude-sonnet-4-5 | — | claude-sonnet-4-5 | — |
| `max_turns` | 50 | 30 | 30 | 50 | 40 |
| `budget_tokens` | 200_000 | 50_000 | 50_000 | 300_000 | 100_000 |
| `budget_usd` | $5.00 | $2.00 | $1.00 | $8.00 | $3.00 |
| **`compaction_threshold_tokens`** | **60_000** | **30_000** | **30_000** | **80_000** | **50_000** |
| `permission_mode` | default | bypass | default | default | bypass |
| `can_spawn_subagents` | true | true | false | true | false |
| `max_subagent_depth` | 1 | 1 | 0 | 1 | 0 |

The CM has the largest token budget (300K) and the highest compaction threshold (80K), reflecting its multi-fragment-aggregation role (see §10). Gate has the smallest budget; it's a fast triage step. Tracker uses Haiku (cheapest model) because it runs weekly across the whole universe.

### Tools by agent (extract — full lists in source)

| Agent | Read tools | Write tools | External tools |
|---|---|---|---|
| Analyst | `filesystem.read_*` | `write_analyst_record`, `write_deep_dive_report` | web_search, yahoo_finance, edgar, e2b.run_python |
| Tracker | `filesystem.read_*` | `append_tracker_history`, `write_tracker_event_log` | yahoo_finance, web_search, edgar.search_filings |
| Gate | `filesystem.read_*` | `write_cluster_inbox`, `write_universe_ledger`, `write_decision_log` | yahoo_finance.get_quote/financials, web_search, edgar.search_filings |
| CM | `filesystem.read_*` | `write_ranking`, `write_cm_decision_log`, `write_reanalysis_ticket`, `write_submission`, `write_dormancy_log`, `write_unmanaged_buckets`, `write_tracker_universe`, `write_tracker_event_log`, `write_quant_dataset` | web_search |
| Quant | `filesystem.read_*` | `write_quant_dataset`, `write_quant_report`, `write_per_measure_track_record` | e2b.run_python |

### Full config — the C1 Analyst

`agents/c1-analyst/config.yaml` (verbatim):

```yaml
# C1 Analyst agent configuration — per Implementation Doc §7.2.
# Runs a 5-stage analysis pipeline for a single ticker.

name: c1-analyst
role: analyst
cluster_id: C1
version: 1

model: fund/claude-opus-4
fallback_model: fund/claude-sonnet-4-5
max_turns: 50
budget_tokens: 200000
budget_usd: 5.00
compaction_threshold_tokens: 60000
permission_mode: default

allowed_tools:
  - filesystem.read_*
  - filesystem.write_analyst_record
  - filesystem.write_deep_dive_report
  - web_search.*
  - yahoo_finance.*
  - edgar.*
  - e2b.run_python

permissions_override:
  filesystem.read_*: bypass
  web_search.*: bypass
  yahoo_finance.*: bypass
  edgar.*: bypass
  e2b.run_python: default
  filesystem.write_analyst_record: default
  filesystem.write_deep_dive_report: default

can_spawn_subagents: true
max_subagent_depth: 1
allowed_subagent_types:
  - research_subagent
```

The `permissions_override` block is the per-tool policy switch. Reads and external data fetches are bypassed (no operator approval); writes and code execution require approval (`default` mode).

### Thesis parallel

The Fund Platform's per-agent YAML is the closest production analogue to the thesis's per-family θ_q. Specifically:

- **`compaction_threshold_tokens`** is the per-agent context-budget knob. Map it 1:1 to your per-family θ_q. The CM's higher value (80K) reflects its higher multi-fragment-aggregation tolerance; the Tracker's lower value (30K) reflects its tighter operating budget. This is the kind of per-fragment-family parameter the thesis's compounding-error model assumes can be measured and set.
- **`permissions_override`** dict is the per-tool ACL analogue. The `bypass` / `default` / `plan` modes are the production engineering shape of the policy layer your bus's ACL enforcement would extend.

**Where this lands in the thesis:**

- **Ch 5 §5.4 (calibrated regime).** "The operational analogue of θ_q in production multi-agent platforms is a per-agent context-budget knob (e.g., Fund Platform's `AgentConfig.compaction_threshold_tokens`, `packages/agent-sdk/src/agent_sdk/agent.py:63`); the thesis's contribution is to derive θ_q empirically from a coordination-success rubric rather than set it by operator intuition."

---

## §10 — Tracker and Cluster Manager: the in-codebase multi-fragment parallels

Two activities in the Fund Platform are the closest engineering proxies to the thesis's multi-fragment workflow setup.

### The Tracker — append-only weekly audit log

`apps/orchestrator/src/orchestrator/activities/tracker_activity.py` runs once per week per ticker. Each run:

1. Reads the ticker folder (`filesystem.read_ticker_folder`).
2. Pulls the latest price snapshot (`yahoo_finance.get_quote`).
3. Computes week-over-week and 4-week trailing deltas against the prior `tracker_weekly_history.json`.
4. **Appends** a new row to `tracker_weekly_history.json` via `filesystem.append_tracker_history`.
5. If any threshold trips (price drop > X%, IRR regression, dormancy threshold reached), **appends** to `tracker_event_log.json` via `filesystem.write_tracker_event_log`.

The Tracker's system prompt (`agents/c1-tracker/prompts/system.md`) makes the append-only invariant explicit:

```markdown
## Rules
- Use Haiku for routine tracking; escalate to Sonnet only for anomaly investigation
- Never modify analyst_record.json — that belongs to the Analyst
- Append-only to tracker_weekly_history.json (never overwrite existing rows)
- Flag missing price data rather than skipping silently
```

This is the production system's invariant: tracker history is *never revised*, only appended. Each row is a full snapshot of the ticker's state at that week (prices, scores, valuation, coverage ratios). The trail is the *audit log of weekly state* for each ticker.

### The Cluster Manager — planner-over-fragments

`apps/orchestrator/src/orchestrator/activities/cm_activity.py` runs once per month per cluster. Each run:

1. Reads the entire cluster's universe of analyses. For each active ticker:
   - `tracker_universe.json` (current roster)
   - `analyst_record.json` (per-ticker scores, conviction, valuation)
   - `tracker_weekly_history.json` (price/coverage drift)
   - `tracker_event_log.json` (anomaly flags from Tracker)
   - `quant_dataset.json` / `quant_report.json` (Chinese Quant signals)
   - cluster_1/inbox/ (Gate's pending tickers)
   - cluster_1/reanalysis_queue/ (prior reanalysis state)
2. **Aggregates across all of these fragments** to produce a single Ranking, a CM decision log, and 4 derived state files.

The CM's system prompt:

```markdown
## Rules
- Submissions are high-stakes — use plan mode, present full rationale
- Never modify analyst_record.json directly — create reanalysis tickets instead
- Log every decision with reasoning to cm_decision_log.json
- Rankings must be reproducible from the underlying data
```

The CM writes six state files per run (via these tool calls):

- `filesystem.write_ranking` → `cluster_1/state/ranking.json` (composite scores, conviction buckets)
- `filesystem.write_cm_decision_log` → `cluster_1/state/cm_decision_log.json` (triage decisions with reasoning)
- `filesystem.write_reanalysis_ticket` → entries in `cluster_1/reanalysis_queue/`
- `filesystem.write_submission` → `cluster_1/submissions/` (plan-mode upward submissions)
- `filesystem.write_dormancy_log` → `cluster_1/state/dormancy_log.json`
- `filesystem.write_tracker_universe` → `cluster_1/state/tracker_universe.json` (synced roster)

### ASCII shape of the CM's multi-fragment read

```
            ┌──────────────────────────────────────────────────┐
            │                Cluster Manager                   │
            │           (run_cluster_manager_agent)            │
            └─────────────────────────┬────────────────────────┘
                                      │ reads N fragments per active ticker
       ┌──────────────────┬──────────┴──────────┬────────────────┬─────────────────┐
       │                  │                     │                │                 │
       ▼                  ▼                     ▼                ▼                 ▼
 universe/AAPL/    universe/AAPL/      universe/AAPL/    cluster_1/quant/   cluster_1/
 analyst_record    tracker_weekly_     tracker_event_   quant_dataset.json  inbox/
 .json             history.json        log.json                            *.json
   ▲                  ▲                                      ▲                  ▲
   │                  │                                      │                  │
 Analyst           Tracker              Tracker          Chinese Quant       Gate
 wrote it          appended             appended         wrote it            wrote it

 ... × every active ticker (typically 8–30 per cluster) ...
                                      │
                                      ▼
                          ┌─────────────────────────────────────────┐
                          │   CM aggregates information across      │
                          │   ~10 fragments per ticker × N tickers  │
                          │   (= ~80-300 fragments per CM run)      │
                          └─────────────────┬───────────────────────┘
                                            │ writes 6 derived state files
       ┌────────────┬───────────────────────┼────────────────────────┬──────────────┐
       │            │                       │                        │              │
       ▼            ▼                       ▼                        ▼              ▼
   ranking.json    cm_decision_         reanalysis_                submission/    dormancy_
                   log.json             queue/*.json               *.json         log.json
```

### Thesis parallel

The Cluster Manager activity is the closest engineering parallel in any real multi-agent system to your thesis's *planner-over-fragments single-LLM-call* setup. Specifically:

- **The planner reads many fragments by reference.** Same shape as your bus.
- **The planner emits a structured aggregate decision.** Same shape as your coordination answer (ranking + decision log).
- **The decision is logged with reasoning.** Same shape as your audit log.
- **Multi-fragment reasoning is the load-bearing task.** No single fragment contains the answer; the planner must integrate across all of them.

Differences:

- **No compression** between the file read and the LLM call. The CM reads raw JSON; if it overflows context, the in-loop Compactor triggers reactively. There is no per-fragment compression policy.
- **No ACL filter.** Every active ticker's fragments are read uniformly; no tag-based filtering.
- **No round structure.** The CM is a single LLM-bearing activity; no multi-agent round-trip.

**Where this lands in the thesis:**

- **Ch 3 §3.4 (evaluation methodology).** Cite the CM activity as the production analogue of the single-call planner the thesis evaluates: real multi-agent platforms do not, in practice, run round-after-round agent dialogue; they run a planner that reads structured per-fragment state and produces a structured aggregate. Strengthens the ADR-009 framing that single-call evaluation is not a research compromise but a faithful model of production reality.
- **Ch 8 §8.6 (future work).** Concrete deployment story: "the CM activity (`apps/orchestrator/src/orchestrator/activities/cm_activity.py`) is one engineering pass away from being a deployment of the thesis's memory bus — replace its `filesystem.read_*` calls with the bus's `/v1/retrieve` endpoint, configure per-family θ_q on the bus, and the cliff measurement methodology transfers directly to production cluster management."

---

## §11 — Orchestration: Temporal workflows

The Fund Platform uses Temporal for durable workflow scheduling. All five agent invocations are Temporal workflows, each wrapping a single activity that runs the agent loop.

### Workflow shape table

| Workflow | Activity | `start_to_close_timeout` | `RetryPolicy` |
|---|---|---|---|
| `AnalystWorkflow` | `run_analyst_agent` | 15 min | `max_attempts=2` |
| `TrackerWorkflow` | `run_tracker_agent` | 10 min | `max_attempts=2` |
| `ClusterManagerWorkflow` | `run_cluster_manager_agent` | 20 min | `max_attempts=2` |
| `GateAgentWorkflow` | `run_gate_agent` | 5 min | `max_attempts=2` |
| `ChineseQuantWorkflow` | `run_quant_agent` | 30 min | `max_attempts=2` |

All workflows are minimal (~25-45 lines): they declare a single activity, wrap it with retry semantics, and log the invocation.

### Activity flow (representative — Analyst)

`apps/orchestrator/src/orchestrator/activities/analyst_activity.py:44-101`:

```python
@activity.defn
async def run_analyst_agent(input: HelloInput) -> HelloResult:
    """Run the C1 Analyst against a ticker folder."""
    activity.logger.info("analyst_activity.starting ticker=%s", input.ticker)

    config = _load_analyst_config()

    llm = LiteLLMClient(base_url=os.environ.get("LITELLM_URL", "http://localhost:8008"), api_key="sk-local")

    registry = ToolRegistry()
    await _register_analyst_tools(registry)

    permission_system = PermissionSystem(permissions_override=config.permissions_override)
    prompt_loader = PromptLoader(str(_PROMPTS_DIR))

    run_id = str(uuid.uuid4())
    ctx = ToolContext(
        agent_id=config.name,
        agent_run_id=run_id,
        workflow_id=activity.info().workflow_id,
        budget=BudgetTracker(max_tokens=config.budget_tokens, max_usd=config.budget_usd),
        permission_mode=config.permission_mode,
        cluster_id=config.cluster_id,
    )

    from agent_sdk.rails import GuardrailsEngine, RailConfig

    agent = Agent(
        config=config,
        llm=llm,
        permission_system=permission_system,
        tool_registry=registry,
        prompt_loader=prompt_loader,
        guardrails=GuardrailsEngine(RailConfig(enforce=False)),
    )

    try:
        from orchestrator.event_broadcaster import broadcast_event

        result = await agent.run_blocking(
            task={"ticker": input.ticker, "nation": input.nation},
            ctx=ctx,
            on_event=broadcast_event,
        )
        return HelloResult(
            status=result.status,
            summary=result.summary,
            artifacts=result.artifacts,
            tokens_used=result.tokens_used,
            cost_usd=result.cost_usd,
        )
    except Exception as e:
        from agent_sdk.errors import RETRYABLE_ERRORS

        activity.logger.error("analyst_activity.failed ticker=%s error=%s", input.ticker, str(e))
        if isinstance(e, tuple(RETRYABLE_ERRORS)):
            raise
        return HelloResult(status="failed", error=str(e))
```

### Replay safety — why files cross workflow boundaries

Temporal workflows must be deterministic; on replay (after a worker restart) Temporal re-runs the workflow code and expects the same activity calls in the same order. **Activities, by contrast, can do non-deterministic work**: they are checkpointed, and replayed activities return cached results.

The Fund Platform takes a strict reading of this: all side effects (file writes, LLM calls, network broadcasts) happen inside activities; workflows only orchestrate. Concretely:

- **Configs load on every activity execution** (`analyst_activity.py:49`). If config were stored in workflow input, replay would require the same config snapshot.
- **Tool registries build fresh per activity** (`tracker_activity.py:46-60`). Registrations are deterministic function calls, not dynamic code.
- **The event broadcaster is imported at runtime, not workflow definition** (`analyst_activity.py:81`). If the broadcaster changes between original execution and replay, the activity uses the current version without a determinism check failure.
- **Atomic writes are idempotent.** If an activity replays and writes the same file again, the temp file from the first attempt is gone; the second write succeeds.

**The upshot:** state crosses activity boundaries via *files*, not via in-memory passing or workflow-input arguments. This is what the thesis's planner/worker design also assumes when it says "every endpoint returns by reference and the bus is the integration substrate" (Ch 3 §3.4).

### Schedules (cron-based triggers)

`apps/orchestrator/src/orchestrator/schedules.py` declares three cron schedules:

- **Tracker:** Friday 22:00 UTC (post-US-close), weekly
- **Cluster Manager:** First Monday 09:00 UTC, monthly
- **Chinese Quant:** 1st of month 06:00 UTC, monthly
- **Gate:** Reactive only (no schedule); triggered by CSV upload event

### Thesis parallel

The Temporal layer is the durability substrate for everything else; it is *outside* the thesis's central claim but is the engineering pattern the thesis's multi-round future work needs.

**Where this lands in the thesis:**

- **Ch 8 §8.6 (future work — multi-round multi-agent evaluation).** "The Fund Platform's Temporal orchestrator (`apps/orchestrator/src/orchestrator/workflows/*.py`) is a worked example of file-mediated planner/worker handoff with deterministic replay. Re-running H1/H2 on a multi-round backend with the bus as the cross-round state substrate is a natural extension; the Fund Platform shows the engineering pattern (single activity per agent invocation; all state through files) is workable at production scale."

---

## §12 — LinkML schema-as-source-of-truth

`packages/ontology/src/schemas/` holds 8 LinkML YAML schemas. The `make gen-schemas` build pipeline compiles each to five artifact types:

```
packages/ontology/src/generated/
├── graphql/      # 11 .graphql files
├── json_schema/  # 11 .json files (consumed by validator.py — §8)
├── pydantic/     # 13 Python modules (consumed by agents at runtime)
├── sql/          # 4 SQL DDL dialects
└── (TypeScript types generated under apps/web/)
```

### The eight schemas

| Schema | Lines | Tree-root classes | Purpose |
|---|---|---|---|
| `common.yaml` | 222 | (none) | Types (`TickerString`, `EurAmount`, `IsoDate`), enums (`ConvictionBucket`, `EvidenceSourceType`), reusable slots (`EvidenceSource`, `Flag`) |
| `analyst_record.yaml` | 239 | `AnalystRecord` | C1 Analyst's per-ticker analysis; scores, valuation, evidence, calibrated conviction |
| `security.yaml` | 107 | `Security`, `FinancialsSnapshot` | Company identity + financial statement snapshot |
| `quant.yaml` | 472 | `QuantDataset`, `QuantMonthlyReport`, `PerMeasureTrackRecord`, `CompositeState`, `GraduationLog` | Chinese Quant's research outputs |
| `tracker.yaml` | 249 | `TrackerWeeklyHistory`, `TrackerEventLog`, `TrackerUniverse` | Tracker's weekly snapshots + event log |
| `cluster_state.yaml` | 354 | `Ranking`, `CmDecisionLog`, `Submission`, `ReanalysisTicket`, `DormancyLog` | Cluster Manager's state files |
| `gate.yaml` | 259 | `GateInboxRecord`, `UniverseLedger`, `GateDecisionLog`, `GateStats` | Gate's inbox + universe ledger |
| `hello.yaml` | 50 | `HelloSummary` | Vertical slice test (Phase 0) |

### Excerpt — `common.yaml` types and enums

`packages/ontology/src/schemas/common.yaml` (verbatim, partial):

```yaml
types:
  EurAmount:
    uri: xsd:decimal
    base: float
    description: Amount denominated in EUR
    minimum_value: -1.0e18
    maximum_value: 1.0e18

  TickerString:
    uri: xsd:string
    base: str
    description: Exchange ticker symbol, uppercase letters/numbers/dot
    pattern: "^[A-Z0-9.]{1,12}$"

  IsoDate:
    uri: xsd:date
    base: str
    description: ISO 8601 date

enums:
  ConvictionBucket:
    description: Analyst's calibrated conviction level for a name
    permissible_values:
      exceptional:
        description: Highest conviction; target IRR probability >= 0.65
      strong:
        description: High conviction; target IRR probability 0.50-0.65
      decent:
        description: Moderate conviction; target IRR probability 0.30-0.50
      marginal:
        description: Low conviction; target IRR probability < 0.30
```

### Excerpt — `analyst_record.yaml` composition

`packages/ontology/src/schemas/analyst_record.yaml` (verbatim, partial):

```yaml
classes:
  AnalystRecord:
    description: Structured Analyst output for a single ticker on a single analysis date
    tree_root: true
    attributes:
      _schema_version:
        range: string
        required: true
      ticker:
        range: TickerString
        required: true
      nation:
        range: CountryCode
        required: true
      analyst_record_date:
        range: IsoDate
        required: true
      financials_snapshot:
        range: FinancialsSnapshot
        required: true
        inlined: true
      scores:
        range: Score
        multivalued: true
        inlined_as_list: true
        required: true
      consistency_check:
        range: ConsistencyCheck
        required: true
        inlined: true
      calibrated_conviction:
        range: CalibratedConviction
        required: true
        inlined: true
```

Note the `imports: [linkml:types, common, security]` at the file head; LinkML resolves cross-schema references through this import graph.

### Thesis parallel

LinkML gives the Fund Platform a property that the thesis's bus design needs: **one source for the data model, generated to every downstream consumer.** The thesis's `Fragment`, `CompressedSlot`, `Tag`, `AuditLogEntry` types can be expressed in LinkML the same way, generating the FastAPI request/response bodies, the FAISS metadata schema, and the protected-fact reader's input contract from one source. The methodology is transferable without claiming the schemas themselves are.

**Where this lands in the thesis:**

- **Ch 3 §3.1 (data model section).** "The bus's `Fragment` and `CompressedSlot` types are expressed in LinkML (cf. `packages/ontology/src/schemas/` in the Fund Platform reference implementation), generating the FastAPI bodies, the FAISS metadata schema, and the protected-fact reader's input contract from one source. This is a defensible single-source-of-truth claim that future readers can verify by inspecting the generated artefacts under `packages/ontology/src/generated/`."

---

## §13 — Production `data/` directory layout

`data/` is the source of truth. Postgres is a derived mirror. Wiping Postgres and re-running FileSync `scan_directory()` rebuilds the mirror from disk.

### Top-level tree

```
data/
├── _backups/                          ← timestamped snapshots from `make backup`
├── _quarantine/                       ← invalid writes preserved with `_invalid` suffix
├── gate/                              ← Gate Agent ephemeral state
│   ├── universe_ledger.json           ← rolling cache of all tickers seen
│   ├── decision_log.json              ← append-only Gate decisions
│   └── gate_stats.json                ← rolling counters
├── universe/                          ← per-ticker folders, one per (ticker, nation)
│   ├── AAPL/
│   ├── SNW_PL/                        ← Polish ticker — uses underscore convention
│   ├── KIST/
│   ├── TEST_GB/                       ← Hello-agent seeded test data
│   ├── AAA/
│   └── ...
└── cluster_1/                         ← C1 cluster state machine
    ├── inbox/                         ← Gate writes here; Analyst consumes
    ├── state/                         ← Cluster Manager's outputs
    ├── quant/
    │   ├── datasets/                  ← Chinese Quant datasets (D_1m, D_3m, D_12m)
    │   └── prior_reports/             ← monthly reports archive
    ├── reanalysis_queue/              ← CM-issued tickets for Analyst
    ├── scratch/                       ← ephemeral working state
    └── submissions/                   ← upward submissions to Strategy Lead
```

### One ticker's folder (AAPL)

```
universe/AAPL/
├── manifest.json                    ← ticker metadata (_schema_version, name, sector, currency)
├── profile.txt                      ← company description (cached from external source)
├── quote.json                       ← last price snapshot
├── financials.json                  ← balance sheet + income statement
├── analyst_record.json              ← AnalystRecord (Analyst-written, atomic)
├── tracker_weekly_history.json      ← TrackerWeeklyHistory (Tracker-appended)
├── tracker_event_log.json           ← TrackerEventLog (Tracker-appended)
└── deep_dive_report.md              ← optional long-form analysis
```

### One cluster's state directory

```
cluster_1/state/
├── ranking.json                     ← Ranking (CM, atomic, overwritten monthly)
├── cm_decision_log.json             ← CmDecisionLog (CM, append-only)
├── dormancy_log.json                ← DormancyLog (CM, append-only)
├── unmanaged_buckets.json           ← UnmanagedBuckets (CM, atomic)
└── tracker_universe.json            ← TrackerUniverse (CM-written, Tracker-consumed)
```

### File-by-agent ownership

| File | Written by | Mode | Schema |
|---|---|---|---|
| `universe/{TKR}/analyst_record.json` | Analyst | atomic | `AnalystRecord` |
| `universe/{TKR}/deep_dive_report.md` | Analyst | atomic | (markdown) |
| `universe/{TKR}/tracker_weekly_history.json` | Tracker | append | `TrackerWeeklyHistory` |
| `universe/{TKR}/tracker_event_log.json` | Tracker | append | `TrackerEventLog` |
| `cluster_1/inbox/{TKR}_{date}.json` | Gate | atomic | `GateInboxRecord` |
| `gate/universe_ledger.json` | Gate | atomic | `UniverseLedger` |
| `gate/decision_log.json` | Gate | append | `GateDecisionLog` |
| `cluster_1/state/ranking.json` | CM | atomic | `Ranking` |
| `cluster_1/state/cm_decision_log.json` | CM | append | `CmDecisionLog` |
| `cluster_1/state/dormancy_log.json` | CM | append | `DormancyLog` |
| `cluster_1/reanalysis_queue/{TKR}_{date}.json` | CM | atomic | `ReanalysisTicket` |
| `cluster_1/submissions/{TKR}_{date}.json` | CM | atomic | `Submission` |
| `cluster_1/quant/datasets/D_{horizon}.json` | Quant | atomic | `QuantDataset` |
| `cluster_1/quant/prior_reports/{YYYY-MM}.json` | Quant | atomic | `QuantMonthlyReport` |

### Thesis parallel

The per-ticker folder shape is the closest engineering analogue to your thesis's fragment-grouped multi-source workload. Each ticker = workload; each file in the folder = fragment from a distinct source (Analyst record, Tracker snapshot, financials, profile, deep dive). The CM activity (§10) reads many such per-ticker folders to produce a single ranking — directly parallel to your planner-over-fragments setup.

**Where this lands in the thesis:**

- **Ch 4 §4.1 (C1 benchmark design motivation).** "The fragment-grouping structure of C1's synthetic workloads mirrors the per-ticker folder shape that production multi-agent platforms use (cf. `data/universe/{TICKER}/` in the Fund Platform): one workload, multiple distinct-source fragments. This is a structural choice with engineering precedent, not a research-only convenience."

---

## §14 — What's *missing* from the codebase that the thesis adds

This section is the **contribution-fuel framing**: every gap below is a concrete piece of architectural substance the thesis adds *over* the production baseline.

### 1. No FAISS / no embedding / no retrieval layer

Grep across `packages/`, `apps/`, `agents/` for `FAISS`, `pgvector`, `embedding`, `vector`, `RAG` returns **zero production-code hits**. The `ArchivalMemory.embedding` field exists but is `None` in every code path; `search_archival` does substring matching.

**The thesis adds:**
- `BAAI/bge-large-en-v1.5` embedder
- FAISS-CPU index
- `POST /v1/retrieve` similarity-query endpoint
- The retrieve→compress / compress→retrieve / joint-routing pipeline placement question (Ch 6)

### 2. No ACL tags on fragments

No field on `ArchivalMemory`, no field on any LinkML class, no field on `Fragment` in the codebase carries a `classification: PUBLIC | INTERNAL | CONFIDENTIAL` tag. The closest analogue is the per-tool `permissions_override` dict, but that gates *tool invocation*, not *fragment retrieval*.

**The thesis adds:**
- A first-class `tags: ClassificationTag` field on every fragment
- Retrieval-time ACL filtering via `GuardrailsEngine.check_retrieval`-equivalent
- The protected-fact-question-set instrumentation per CONFIDENTIAL fragment

### 3. Audit log has no hash chain

`file_sync_log.content_hash` is a defined `TEXT` column but is *never populated*. The append-only property is asserted by `INSERT`-only writes, not by cryptographic chaining.

**The thesis adds:**
- SHA-256 per row, populated synchronously with insert
- Hash chain field `hash_self = SHA-256(slot_id || op || t || hash_prev)`
- The threat model: tamper-evidence under local-file-write access (research-grade, per ADR-005 of the thesis)

### 4. No protected-fact reader / no H4 instrumentation

There is no held-out Llama-3.1-8B (or equivalent) attached to the bus for measuring information leakage from compressed fragments. The closest analogue is the e2b sandbox `_run_python` — a hermetic subprocess for code execution, *not* for adversarial reading.

**The thesis adds:**
- The held-out reader (Llama-3.1-8B) as a sandboxed subprocess on the same engineering substrate
- The yes/no-question-set methodology for protected-fact recovery
- The unbiased benchmark fix (Ch 7 §7.2) — a methodological contribution

### 5. No coordination-success rubric

The Fund Platform measures `tokens_before` / `tokens_after` per compaction event, but there is no scoring of *whether the post-compaction agent run succeeded at its task*. Success is implicit (operator reads the output and decides).

**The thesis adds:**
- The three-family C1 coordination scorer (numeric sum ± 25%; bin-packing feasibility; FINAL-NNNN exact match)
- The trace-only scoring property (no LLM in the loop on the scoring side)
- The coordination-cliff measurement methodology

### 6. No compression operating-point selection

The Compactor compresses to a fixed shape (preserve N, summarise the rest). There is no per-fragment compression ratio decision, no safety bound check, no fallback if a fragment is over-compressed.

**The thesis adds:**
- CAAC (Cliff-Aware Adaptive Compression) wrapping any base compressor
- Per-fragment critical-token-recall check
- Binary-search to the safe operating point bounded by `min_ratio`

### 7. No multi-strategy compressor catalogue

The Fund Platform uses one compaction strategy. The thesis evaluates four (LLMLingua-2, Phi-3-Mini extractive, instruction-aware filter, truncation) plus CAAC.

**The thesis adds:**
- The pluggable `Compressor` protocol with `compress(fragment, target_ratio) -> CompressedSlot`
- Empirical comparison across compressors on the same benchmark
- The decorrelation finding (Ch 5 §5.2): QA-F1 ≠ coordination success

### Summary framing

The Fund Platform is *the production-grade baseline architecture* the thesis builds on. The thesis's contribution is the *measurement framework and the missing engineering substance*:

| Layer | Fund Platform | Thesis adds |
|---|---|---|
| Memory bus shape | Three-tier with embed field | FAISS-backed retrieval; ACL tag field |
| Audit log | Atomic write + quarantine + append-only mirror | SHA-256 hash chain; per-row content hash population |
| Privacy infrastructure | Three-stage rails + PII regexes | Protected-fact-recovery metric; CONFIDENTIAL-tag retrieval filter |
| Compression layer | One naive summariser | Four compressors + CAAC; cliff measurement; θ_q bootstrap |
| Coordination | Implicit (operator scored) | Three-family rubric; trace-only scoring; coordination cliff |
| Multi-fragment workflow | Per-ticker folder + CM aggregation | Same shape, controlled benchmark, quantified compression effect |

This framing turns the codebase into **prior art that motivates the thesis's contributions** rather than **a competing system the thesis must distinguish itself from.**

---

## §15 — What NOT to import into the thesis

Components the thesis should *not* try to pull in, with reasons:

1. **Temporal/LangGraph orchestration details.** The thesis's evaluation uses single LLM calls (ADR-009); durable orchestration is a scope mismatch with Ch 3 §3.4. *Brief* mention in Ch 8 §8.6 multi-round future work is enough.
2. **MCP tool protocol internals.** Interesting engineering, orthogonal to the thesis's central question (compression × coordination). One sentence of Ch 2 prior art is sufficient.
3. **Chinese Quant agent specifics.** Statistical research methodology with fund-specific semantics; not transferable to a memory-bus thesis.
4. **Canvas UI / Next.js frontend.** Operator UX; entirely out of scope.
5. **LiteLLM gateway internals.** A routing chokepoint; the thesis already uses it but does not need to describe it. One footnote in Ch 3 §3.3 is enough (you already have this — "Inference backend").
6. **Per-cluster strategy specifics (C1 "High Net Cash").** Domain-specific scoring rubric; not transferable.
7. **The Operator approval flow.** Production governance pattern; not a research contribution surface.
8. **Cost analytics (`/api/cost/*` endpoints).** Operational dashboard concern.

Net: focus on §3 (agent loop), §4 (compaction), §5 (memory tiers), §6 (events), §7 (rails), §8 (audit log), §9 (per-agent config), §10 (CM as multi-fragment planner), §12 (LinkML methodology). Skip the rest.

---

## §16 — Suggested insertion points by thesis chapter

These are draft paragraphs the thesis agent can lift into the manuscript with minimal editing. Each cites the Fund Platform as background grounding, not as a competing system. Cite-anchors use the exact `path:lines` format the thesis agent already uses.

### For Ch 3 §3.1 (after the existing architectural overview)

> Production multi-agent platforms (e.g., the Fund Platform reference implementation at `packages/agent-sdk/src/agent_sdk/`) independently converge on a recognisable shape: a typed event stream emitted from a per-turn agent loop (`agent.py:144-289`), threshold-triggered context compaction inline with the LLM call (`compactor.py:52-121`), atomic-write file storage with validate-or-quarantine (`packages/mcp-servers/filesystem/src/mcp_server_filesystem/server.py:124-189`), a three-stage rail check at input / output / retrieval (`rails/engine.py:85-120`), and a per-agent YAML config that exposes a `compaction_threshold_tokens` budget knob (`agent.py:63`) — the operational analogue of this thesis's per-family θ_q. The memory bus described in this chapter generalises this pattern by (a) making the compressor pluggable, (b) introducing FAISS-backed semantic retrieval where production systems explicitly defer (cf. the `# Production would use pgvector cosine similarity` admission in `memory.py:74-76`), (c) adding classification tags as a first-class fragment field where production systems have no equivalent, and (d) populating SHA-256 content hashes per audit-log row and chaining them, where production systems define the column but leave it unpopulated (cf. `file_sync_log.content_hash` in `apps/file-sync/src/file_sync/db.py:24-36`). Each contribution maps onto a concrete gap rather than reinventing an existing abstraction.

### For Ch 3 §3.5 (after the existing reproducibility note)

> The instrumentation contract the experimental harness conforms to is the typed `AgentEvent` taxonomy used by production multi-agent platforms (cf. `packages/agent-sdk/src/agent_sdk/events.py`). Every event carries `event_id`, `timestamp`, `agent_run_id`, `turn`; the `CompactionEvent` subtype additionally carries `tokens_before` and `tokens_after` (`events.py:76-80`), the production-system instance of this thesis's q(r) on-the-wire measurement. Extending this schema with `compressor_id`, `target_ratio`, and `achieved_ratio` fields completes the experiment-harness logging contract used to produce `results/h1_h2_v2/sweep_results.csv` and downstream `verdicts.json` files.

### For Ch 7 §7.5 (after the existing "memory bus exposes the protected-fact channel" paragraph)

> Three-stage rails (input / output / retrieval) are now the standard defensive pattern for production multi-agent platforms (cf. `packages/agent-sdk/src/agent_sdk/rails/engine.py:85-120`). The retrieval stage is the slot at which this thesis's CONFIDENTIAL-tag ACL check applies: every fragment returned from the bus's FAISS retriever passes through `check_retrieval` before injection into the LLM's context. The bus's specialisation over the production baseline is that the check is *content-aware* — it consults the per-fragment classification tag (the protected-fact channel above), not only the regex-based PII filters that the production engine ships with (SSN / credit card / IBAN, `engine.py:64-68`). The dev/prod enforcement toggle (`engine.py:144-161`) is the operational switch operators use to ramp from log-only to block-on-violation.

### For Ch 8 §8.5 (after the LongLLMLingua comparison)

> A second prior-art reference point worth surfacing: production multi-agent platforms (e.g., the Fund Platform) ship a single threshold-triggered summarising compactor as the default (`packages/agent-sdk/src/agent_sdk/compactor.py:52-121`), with a hardcoded prompt that instructs the summariser to preserve numbers, scores, file paths, and tickers (`compactor.py:21-24`). This is, in effect, the production-system attempt at critical-token preservation through prompt engineering rather than through a measurement-anchored cliff bound. The four training-free compressors evaluated in this thesis are positioned as drop-in replacements for this default, with CAAC providing the missing operating-point selection that prompt engineering cannot supply.

### For Ch 8 §8.6 (additions to the future-work list)

> **Bus integration target.** The Fund Platform's `ArchivalMemory` schema (`packages/agent-sdk/src/agent_sdk/memory.py:30-41`) and `search_archival` placeholder (`memory.py:68-87`) are one field-addition and one engine swap away from being a deployment of this thesis's bus: add `classification: ClassificationTag` and wire `search_archival` to a FAISS index. The `compaction_threshold_tokens` knob (`agent.py:63`) becomes the per-agent θ_q. The `_write_validated_json` primitive (`mcp_server_filesystem/server.py:124-189`) and the `file_sync_log` table (`apps/file-sync/src/file_sync/db.py:24-36`) become the audit-log substrate once the `content_hash` column is populated and the SHA-256 chain is added. Demonstrating this integration end-to-end on a production multi-agent platform would extend the thesis's empirical claims to a real-deployment context.
>
> **Multi-round multi-agent evaluation on Temporal-style durable workflows.** The Fund Platform's Temporal orchestrator (`apps/orchestrator/src/orchestrator/workflows/*.py`, five workflows) is a worked example of file-mediated planner/worker handoff with deterministic replay semantics. Re-running H1/H2 on a multi-round backend (per-round LLM call, state crossing rounds via the bus) would test whether the coordination cliff appears in genuinely multi-agent settings; the Fund Platform shows that file-mediated state-handoff is workable at production scale.

---

## Appendix A — File index

Load-bearing files referenced in this document, with one-line descriptions:

### Agent SDK
- `packages/agent-sdk/src/agent_sdk/agent.py` (520 lines) — `Agent` + `AgentConfig`; per-turn loop; tool dispatch with parallel/serial split.
- `packages/agent-sdk/src/agent_sdk/compactor.py` (132 lines) — `Compactor.compact()` summarise-the-middle implementation; `_COMPACTION_PROMPT`.
- `packages/agent-sdk/src/agent_sdk/memory.py` (112 lines) — `MemoryStore`, `MemoryConfig`, `ArchivalMemory` (closest in-codebase analogue to thesis `Fragment`).
- `packages/agent-sdk/src/agent_sdk/rails/engine.py` (162 lines) — `GuardrailsEngine` three-stage rails; PII regexes; dev/prod toggle.
- `packages/agent-sdk/src/agent_sdk/events.py` (107 lines) — typed `AgentEvent` hierarchy; `CompactionEvent { tokens_before, tokens_after }`.
- `packages/agent-sdk/src/agent_sdk/registry.py` (90 lines) — `ToolRegistry.filter()` with fnmatch wildcards.
- `packages/agent-sdk/src/agent_sdk/llm.py` (285 lines) — `LiteLLMClient` chokepoint, retry + fallback.

### Orchestrator and activities
- `apps/orchestrator/src/orchestrator/workflows/{analyst,tracker,cm,gate,quant}_workflow.py` — five minimal Temporal workflows wrapping single activities.
- `apps/orchestrator/src/orchestrator/activities/analyst_activity.py` (~101 lines) — Analyst agent activity; full flow shown in §11.
- `apps/orchestrator/src/orchestrator/activities/tracker_activity.py` — Tracker activity; append-only writes.
- `apps/orchestrator/src/orchestrator/activities/cm_activity.py` — Cluster Manager activity; multi-fragment aggregation.
- `apps/orchestrator/src/orchestrator/activities/gate_activity.py` — Gate Agent activity.
- `apps/orchestrator/src/orchestrator/activities/quant_activity.py` — Chinese Quant activity.
- `apps/orchestrator/src/orchestrator/activities/tool_adapters.py` (~330 lines) — `_make_tool_class()` factory; atomic write block.
- `apps/orchestrator/src/orchestrator/event_broadcaster.py` (53 lines) — full file quoted in §6.
- `apps/orchestrator/src/orchestrator/schedules.py` — cron schedules (Tracker weekly, CM monthly, Quant monthly).

### File-sync (audit log)
- `apps/file-sync/src/file_sync/handler.py` (137 lines) — `SyncHandler.handle_file_event` + `scan_directory`.
- `apps/file-sync/src/file_sync/validator.py` (97 lines) — `FileValidator` using LinkML-generated JSON Schemas.
- `apps/file-sync/src/file_sync/db.py` (128 lines) — `file_sync_log` schema; `content_hash` column (TODO).
- `apps/file-sync/src/file_sync/watcher.py` (75 lines) — watchdog Observer + dispatch.

### Platform API (event surface)
- `apps/platform-api/src/platform_api/app.py` — `ConnectionManager` (lines 55-82); `/ws/events` (lines 85-94).
- `apps/platform-api/src/platform_api/routers/workflows.py` — `/api/events/broadcast` (lines 101-106); approval handler (lines 88-98).

### MCP servers
- `packages/mcp-servers/filesystem/src/mcp_server_filesystem/server.py` — `_write_validated_json` (lines 124-189).
- `packages/mcp-servers/e2b-sandbox/src/mcp_server_e2b/server.py` — `_run_python` (lines 28-75).
- `packages/mcp-servers/yahoo-finance/`, `packages/mcp-servers/edgar/`, `packages/mcp-servers/web-search/` — additional MCP servers (not deep-read).

### Ontology
- `packages/ontology/src/schemas/common.yaml` (222 lines) — types + enums + reusable slots.
- `packages/ontology/src/schemas/analyst_record.yaml` (239 lines) — `AnalystRecord` + scoring composition.
- `packages/ontology/src/schemas/security.yaml` (107 lines) — `Security` + `FinancialsSnapshot`.
- `packages/ontology/src/schemas/quant.yaml` (472 lines) — Quant outputs.
- `packages/ontology/src/schemas/tracker.yaml` (249 lines) — Tracker history + event log.
- `packages/ontology/src/schemas/cluster_state.yaml` (354 lines) — CM state files.
- `packages/ontology/src/schemas/gate.yaml` (259 lines) — Gate inbox + ledger.
- `packages/ontology/src/schemas/hello.yaml` (50 lines) — vertical slice (Phase 0).
- `packages/ontology/src/generated/{pydantic,json_schema,sql,graphql}/` — generated artifacts.

### Agent configs
- `agents/c1-analyst/config.yaml` (39 lines) — full config shown in §9.
- `agents/c1-tracker/config.yaml` (~36 lines) — Tracker; Haiku model; append-only writes.
- `agents/c1-gate-agent/config.yaml` (~36 lines) — Gate; smallest budget; no subagents.
- `agents/c1-cluster-manager/config.yaml` (~37 lines) — CM; largest budget; can spawn cross-cluster subagents.
- `agents/c1-chinese-quant/config.yaml` (~31 lines) — Quant; e2b code-execution-heavy.
- `agents/c1-tracker/prompts/system.md` — append-only invariant declaration.
- `agents/c1-cluster-manager/prompts/system.md` — multi-fragment aggregation invariant.

### Data layout
- `data/_backups/`, `data/_quarantine/`, `data/gate/`, `data/universe/{TKR}/`, `data/cluster_1/{inbox,state,quant,reanalysis_queue,scratch,submissions}/` — see §13 tree.

### ADRs (referenced for context)
- ADR-0003 — files as source of truth
- ADR-0004 — LinkML as schema source of truth
- ADR-0005 — LiteLLM gateway
- ADR-0006 — Temporal + LangGraph layered
- ADR-0007 — MCP tool protocol
- ADR-0008 — Postgres as derived mirror
- ADR-0011 — observability stack (Langfuse + OTel + structlog)
- ADR-0012 — GuardrailsEngine and rail mode
- ADR-0013 — E2B + Firecracker sandboxing
- ADR-0015 — JWT auth (v1) + OIDC scaffolding

---

## Appendix B — Glossary

Codebase term ↔ thesis term mapping. When the thesis agent reads a Fund Platform identifier, this table tells it the corresponding thesis concept.

| Fund Platform | Thesis | Notes |
|---|---|---|
| `Agent.run()` | planner+worker loop | One per-process loop; thesis's planner/worker can be one or multiple processes. |
| `AgentConfig` | per-fragment-family policy record | Maps roughly to your family-level config. |
| `AgentConfig.compaction_threshold_tokens` | θ_q (per-family threshold) | The Fund Platform sets this by operator intuition; the thesis derives it empirically. |
| `AgentConfig.allowed_tools` | per-fragment-family tool ACL | fnmatch wildcards. |
| `AgentConfig.permissions_override` | per-tool policy override | Bypass / default / plan modes. |
| `Compactor` | compressor (single, naive) | One strategy: preserve system+recent, summarise the middle. Cf. thesis's four. |
| `Compactor.compact(messages)` | `Compressor.compress(fragment, target_ratio)` | Coarser unit (messages vs fragments), single strategy vs four. |
| `_COMPACTION_PROMPT` | prompt-engineered critical-token-retention bias | The production system tries to preserve numbers + tickers via prompt; the thesis measures this directly. |
| `compaction_threshold_tokens` (knob) | per-family θ_q | See above. |
| `MemoryStore` (three tiers) | memory bus | Core / recall / archival ≈ system prompt block / recent window / vector store. |
| `MemoryConfig` | bus configuration | The closest analogue. |
| `ArchivalMemory` | `Fragment` | Field-by-field comparison in §5. |
| `ArchivalMemory.embedding` | `Fragment.embedding` | Field exists but unused in production; thesis adds FAISS. |
| `ArchivalMemory.key` | `Fragment.tag` (provenance key) | String-keyed lookup. |
| `MemoryStore.search_archival()` | `POST /v1/retrieve` | Substring matcher; thesis uses FAISS. |
| `MemoryStore.write_archival()` | `POST /v1/write` | Append to archival tier. |
| `GuardrailsEngine` | privacy / ACL enforcement layer | Three checkpoints. |
| `GuardrailsEngine.check_input` | input rail | Before LLM call. |
| `GuardrailsEngine.check_output` | output rail | After LLM call. |
| `GuardrailsEngine.check_retrieval` | **ACL filter slot** | Where the thesis's CONFIDENTIAL-tag check goes. |
| `RailConfig.enforce` | dev/prod policy switch | False = log only; true = block. |
| `_PII_PATTERNS` | shallow-filter baseline | SSN / credit card / IBAN regexes. |
| `blocked_patterns` | prompt-injection blocklist | "ignore previous instructions" style. |
| `_write_validated_json` | audit-log write primitive | Validate → atomic temp+rename → quarantine on fail. |
| `tempfile.mkstemp` + `os.replace` | atomic write protocol | POSIX atomicity. |
| `data/_quarantine/` | quarantine destination | Invalid writes preserved with `_invalid` suffix. |
| `file_sync_log` (table) | append-only audit log | INSERT-only; per-event row. |
| `file_sync_log.content_hash` | **per-row hash (TODO)** | Column defined, not populated. Thesis adds SHA-256 computation. |
| `FileSync.scan_directory()` | nightly bus integrity check | Full reconciliation pass. |
| `AgentEvent` | bus event (base) | event_id, timestamp, agent_run_id, turn. |
| `CompactionEvent { tokens_before, tokens_after }` | **q(r) on-the-wire measurement** | `ratio = tokens_after / tokens_before`. |
| `LLMCallEvent` | per-LLM-call observability row | Used by experiment harness. |
| `event_broadcaster.broadcast_event` | event fanout to operators | Best-effort POST. |
| `ConnectionManager` (Platform API) | WebSocket fan-out | Live operator subscription. |
| `Temporal workflow` | durable planner/worker boundary | Workflows hold no in-memory state across replay. |
| `RetryPolicy(maximum_attempts=2)` | activity-level retry semantics | Uniform across all five workflows. |
| `LinkML` (schema layer) | single-source-of-truth data model | Generates Pydantic + JSON Schema + SQL + GraphQL + TS. |
| `make gen-schemas` | LinkML build pipeline | Run after schema edits. |
| `universe/{TICKER}/` | per-workload fragment grouping | One folder = one ticker = one workload. |
| `cluster_1/state/ranking.json` | planner output | CM-written, atomic. |
| `cluster_1/state/cm_decision_log.json` | planner decision audit log | CM-written, append-only. |
| Tracker activity | append-only weekly state log | Closest engineering analogue to thesis's bus log. |
| Cluster Manager activity | planner over multi-fragment input | Reads ~10 files per ticker × N tickers; writes 6 derived state files. |
| `_run_python` (e2b sandbox) | held-out hermetic subprocess pattern | Engineering substrate for the protected-fact reader. |

---

*End of THESIS_HANDOFF.md*
