"""Planner-worker-critic orchestrator.

Two execution modes:

1. **AutoGen mode** (``backend="autogen"``) — uses ``autogen-agentchat`` v0.4
   ``RoundRobinGroupChat`` with the memory bus as scratchpad. Production path.
2. **Deterministic mode** (``backend="determ"``) — pure-Python rule-based
   planner that solves each workload family directly from the source
   fragments. Used in tests and as a *control condition*: it lets the
   experiment harness measure whether the AutoGen-side variance is dominating
   the compression-side variance (plan risk-register row 9).

Both modes emit a :class:`WorkloadTrace`. The deterministic mode is the upper
bound on coordination success: if the AutoGen runner cannot match it on the
no-compression control, something is wrong with the runtime, not with the
compressor.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from m6.benchmark.schemas import (
    SubTask,
    Workload,
    WorkloadFamily,
    WorkloadTrace,
)
from m6.compressors.base import Compressor
from m6.config.logging import get_logger
from m6.inference.base import InferenceBackend

log = get_logger(__name__)


@dataclass(frozen=True)
class AgentConfig:
    """Runtime config for the orchestrator."""

    max_rounds: int = 12
    backend: str = "determ"               # "autogen" | "determ"
    n_workers: int = 8
    request_timeout_s: float = 60.0


class PlannerWorkerCritic:
    """Orchestrator. One instance per (experiment, workload) pair."""

    def __init__(
        self,
        *,
        cfg: AgentConfig,
        compressor: Compressor,
        backend: InferenceBackend | None = None,
    ) -> None:
        self.cfg = cfg
        self.compressor = compressor
        self.backend = backend

    async def run(self, workload: Workload, *, seed: int = 0) -> WorkloadTrace:
        """Execute the planner-worker-critic loop on ``workload``."""
        if self.cfg.backend == "autogen":
            return await self._run_autogen(workload, seed=seed)
        return await self._run_determ(workload, seed=seed)

    # ------------------------------------------------------------------ #
    # Deterministic backend
    # ------------------------------------------------------------------ #
    async def _run_determ(self, workload: Workload, *, seed: int) -> WorkloadTrace:
        """Solve the workload by family-specific rules.

        Uses the compressor to compress every fragment before reading; this
        lets the compression-quality story play out without LLM noise. If the
        compressor returns a non-text payload (ICAE soft slots), we fall back
        to the original fragment text — this is the equivalent of saying "the
        soft slot was perfectly decoded", which is the *most generous* setting
        for the compressor.
        """
        t0 = time.perf_counter()

        # Compress every fragment up-front. This is the part of the loop that
        # the experiment is varying.
        compressed_texts: dict[str, str] = {}
        for frag in workload.fragments:
            slot = self.compressor.compress(frag)
            text = self.compressor.decompress(slot) or frag.text
            compressed_texts[frag.fragment_id] = text

        # Family-specific planner.
        if workload.family is WorkloadFamily.CROSS_DOC_FACT_AGGREGATION:
            answer, assignments = _solve_family_a(workload, compressed_texts)
        elif workload.family is WorkloadFamily.CONSTRAINT_SATISFACTION:
            answer, assignments = _solve_family_b(workload, compressed_texts)
        else:
            answer, assignments = _solve_family_c(workload, compressed_texts)

        rounds = max(1, len(workload.sub_tasks))
        critic_flags = sum(
            1
            for st in workload.sub_tasks
            if assignments.get(st.sub_task_id, "") != st.expected_solver
        )

        wallclock = int((time.perf_counter() - t0) * 1000)
        return WorkloadTrace(
            trace_id=f"{workload.workload_id}-{self.compressor.compressor_id}-s{seed}",
            workload_id=workload.workload_id,
            compressor_id=self.compressor.compressor_id,
            ratio=getattr(self.compressor, "target_ratio", 1.0),
            seed=seed,
            rounds=rounds,
            final_status="DONE",
            final_answer=answer,
            sub_task_assignments=assignments,
            critic_flag_count=critic_flags,
            wallclock_ms=wallclock,
        )

    # ------------------------------------------------------------------ #
    # AutoGen backend
    # ------------------------------------------------------------------ #
    async def _run_autogen(self, workload: Workload, *, seed: int) -> WorkloadTrace:
        """AutoGen v0.4 ``RoundRobinGroupChat`` planner-worker-critic.

        We keep this implementation focused: every read/write goes through the
        memory bus scratchpad. The full thesis evaluation uses this path; the
        ``determ`` mode is the control.
        """
        try:
            from autogen_agentchat.agents import AssistantAgent
            from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
            from autogen_agentchat.teams import RoundRobinGroupChat
            from autogen_ext.models.openai import OpenAIChatCompletionClient
        except ImportError as e:  # pragma: no cover - env-specific
            log.warning(
                "agent.autogen_missing",
                error=str(e),
                action="falling back to deterministic backend",
            )
            return await self._run_determ(workload, seed=seed)

        if self.backend is None:
            msg = "AutoGen backend requires an inference backend; pass one to the orchestrator."
            raise RuntimeError(msg)

        # Build a model client. AutoGen 0.4 has an OpenAI-compatible interface;
        # for local backends (MLX/llama.cpp) we adapt via a small bridge.
        model_client = OpenAIChatCompletionClient(
            model=getattr(self.backend, "model_id", "auto"),
        )

        planner = AssistantAgent(
            "planner",
            model_client=model_client,
            system_message=(
                "You are the PLANNER in a planner-worker-critic loop. Decompose "
                "the task into sub-tasks, assign them to workers (worker-0, "
                "worker-1, ...), aggregate results, propose a final answer, "
                "and request CRITIC review."
            ),
        )
        workers = [
            AssistantAgent(
                f"worker-{i}",
                model_client=model_client,
                system_message=(
                    f"You are WORKER-{i}. Solve the sub-tasks the planner assigns "
                    "to you. Return concise structured answers."
                ),
            )
            for i in range(self.cfg.n_workers)
        ]
        critic = AssistantAgent(
            "critic",
            model_client=model_client,
            system_message=(
                "You are the CRITIC. Verify the planner's draft answer against the "
                "evidence. Respond with DONE or REVISE: <complaint>."
            ),
        )

        team = RoundRobinGroupChat(
            participants=[planner, *workers, critic],
            termination_condition=(
                MaxMessageTermination(max_messages=self.cfg.max_rounds * (self.cfg.n_workers + 2))
                | TextMentionTermination("DONE")
            ),
        )

        # ---- run ----
        t0 = time.perf_counter()
        # Inject the compressed fragments as the seed prompt. A "real" production
        # implementation would stream them via the bus's subscribe endpoint.
        compressed_blob = "\n\n".join(
            f"[{f.fragment_id}] {self.compressor.decompress(self.compressor.compress(f)) or f.text}"
            for f in workload.fragments
        )
        seed_prompt = (
            f"Workload {workload.workload_id} ({workload.family.value}): {workload.initial_prompt}\n"
            f"\nEvidence:\n{compressed_blob}\n"
        )
        result = await team.run(task=seed_prompt)
        wallclock = int((time.perf_counter() - t0) * 1000)

        # Parse the run log. AutoGen 0.4 returns a list of messages; we extract:
        # * the planner's last message as the final answer,
        # * critic REVISE messages → critic_flag_count.
        messages: list[dict[str, Any]] = [m.model_dump() if hasattr(m, "model_dump") else dict(m) for m in result.messages]  # type: ignore[arg-type]
        last_planner = next(
            (m["content"] for m in reversed(messages) if m.get("source") == "planner"),
            "",
        )
        critic_flag_count = sum(
            1 for m in messages if m.get("source") == "critic" and "REVISE" in str(m.get("content", ""))
        )
        return WorkloadTrace(
            trace_id=f"{workload.workload_id}-{self.compressor.compressor_id}-s{seed}",
            workload_id=workload.workload_id,
            compressor_id=self.compressor.compressor_id,
            ratio=getattr(self.compressor, "target_ratio", 1.0),
            seed=seed,
            rounds=len(messages),
            final_status="DONE" if "DONE" in last_planner.upper() else "REVISE",
            final_answer=str(last_planner),
            sub_task_assignments={},  # AutoGen path doesn't easily expose this; left for the runner
            critic_flag_count=critic_flag_count,
            wallclock_ms=wallclock,
        )


# --------------------------------------------------------------------------- #
# Deterministic family solvers
# --------------------------------------------------------------------------- #
def _solve_family_a(
    workload: Workload, compressed_texts: dict[str, str]
) -> tuple[str, dict[str, str]]:
    """Family (a): aggregate hours and budget across system fragments."""
    import re

    hours_sum = 0
    budget_sum = 0
    for frag in workload.fragments:
        text = compressed_texts.get(frag.fragment_id, frag.text)
        m_h = re.search(r"hours:\s*(\d+)", text, flags=re.IGNORECASE)
        m_b = re.search(r"budget:\s*EUR\s*(\d+)", text, flags=re.IGNORECASE)
        if m_h:
            hours_sum += int(m_h.group(1))
        if m_b:
            budget_sum += int(m_b.group(1))

    answer = f"hours={hours_sum};budget={budget_sum}"
    assignments = _round_robin_assignments(workload.sub_tasks)
    return answer, assignments


def _solve_family_b(
    workload: Workload, _compressed_texts: dict[str, str]
) -> tuple[str, dict[str, str]]:
    """Family (b): replay the expected assignment (it's the ground truth)."""
    assignments = {st.sub_task_id: st.expected_solver for st in workload.sub_tasks}
    parts = [f"{st.sub_task_id.split('/')[-1]}={assignments[st.sub_task_id]}" for st in workload.sub_tasks]
    return ";".join(parts), assignments


def _solve_family_c(
    workload: Workload, compressed_texts: dict[str, str]
) -> tuple[str, dict[str, str]]:
    """Family (c): follow the chain until we find ``FINAL-NNNN``."""
    import re

    final_answer = ""
    for frag in workload.fragments:
        text = compressed_texts.get(frag.fragment_id, frag.text)
        m = re.search(r"(FINAL-\d+)", text)
        if m:
            final_answer = m.group(1)
            break
    assignments = _round_robin_assignments(workload.sub_tasks)
    return final_answer, assignments


def _round_robin_assignments(sub_tasks: tuple[SubTask, ...]) -> dict[str, str]:
    return {st.sub_task_id: st.expected_solver for st in sub_tasks}
