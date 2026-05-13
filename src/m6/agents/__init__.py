"""Agent runtime.

AutoGen v0.4 pinned (see ``docs/adr/ADR-004-agent-runtime.md``). The
orchestrator translates a :class:`m6.benchmark.schemas.Workload` into a
planner-worker-critic loop and emits a :class:`WorkloadTrace`.

Public surface:

* :class:`PlannerWorkerCritic` — the orchestrator.
* :class:`AgentConfig` — runtime configuration.

A minimal **deterministic fallback runner** is provided so the experiment
harness can exercise its plumbing without AutoGen installed.
"""

from m6.agents.orchestrator import AgentConfig, PlannerWorkerCritic

__all__ = ["AgentConfig", "PlannerWorkerCritic"]
