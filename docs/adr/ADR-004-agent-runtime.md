# ADR-004: Agent runtime — AutoGen v0.4 pinned

**Status:** Accepted
**Date:** 2026-05-12
**Deciders:** Syed Abdullah Hassan, Lauri Lovén

## Context

The thesis needs a planner-worker-critic loop with scratchpad-style state sharing (plan §6.2). Several options exist:
* **AutoGen** (Microsoft) — popular, mature, breaking-change rewrite in v0.4 (Oct 2024).
* **MetaGPT** — strong SOP framing, less ergonomic for ad-hoc topologies.
* **CAMEL** — role-playing dialogue, not really an orchestration framework.
* **LangGraph** — graph-based, very flexible, slower to develop with.
* **Custom** — write the loop ourselves on top of `asyncio`.

External constraint: the plan explicitly names AutoGen as the agent runtime (plan §6.2). It also flags ("**pin AutoGen version**", plan risk register) the risk of runtime bugs confounding coordination measurements.

## Decision

* **AutoGen 0.4.x** pinned in `requirements.txt`. The v0.4 rewrite is required because:
  * It is the actively supported track; v0.2 receives only bug fixes.
  * The async event-driven core matches our SSE-based subscribe API.
  * `Team` / `RoundRobinGroupChat` primitives map cleanly to planner-worker-critic.
* Every experiment includes a **`compressor=none` control condition**. If the control condition's variance is comparable to the treatment's variance, the experiment is flagged `invalid` (mitigation for the AutoGen-runtime-bug risk).
* The scratchpad is **the memory bus** — agents do not get a private scratchpad. Every write goes through `POST /v1/write` so the compressor is on the critical path.

## Options considered

### Option A — Custom asyncio loop

Pros: zero dependency drift. Cons: re-invents AutoGen and exposes us to subtle ordering bugs the thesis is not about.

### Option B — LangGraph

Pros: graph-based, very flexible. Cons: heavier dependency tree (LangChain), and the team has no LangGraph experience.

### Option C — AutoGen 0.4.x *(chosen)*

Pros: matches the plan. Mature. Pinning is the documented mitigation. Cons: v0.4 breaking change is large; some tutorials still reference v0.2 patterns.

### Option D — AutoGen 0.2.x

Pros: most tutorials work. Cons: unsupported track; will rot.

## Trade-off analysis

The plan names AutoGen; deviating would require renegotiating scope with Lauri. The risk of runtime bugs is mitigated by (a) version pinning, (b) the no-compression control, and (c) explicit invariant checks in the trace scorers.

## Consequences

**Easier.**
* Planner-worker-critic via `RoundRobinGroupChat`.
* Async tool calls.

**Harder.**
* Upgrading AutoGen mid-thesis — we won't.
* Sharing state between agents that AutoGen does not natively support — solved by the memory-bus scratchpad.

## Action items

1. [x] Pin `autogen-agentchat`, `autogen-core`, `autogen-ext[openai]` to `>=0.4,<0.5`.
2. [x] Implement `m6.agents.orchestrator.PlannerWorkerCritic` on top of `RoundRobinGroupChat`.
3. [x] Implement the scratchpad bridge that routes writes/reads through the memory bus.
4. [x] Add the control-condition variance check to every experiment runner.
