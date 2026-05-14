"""Coordination metrics (plan §5.2).

Pure functions of the :class:`WorkloadTrace` and the underlying :class:`Workload`.
"""

from __future__ import annotations

from dataclasses import dataclass

from m6.benchmark.schemas import Workload, WorkloadTrace
from m6.config.logging import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class CoordinationMetrics:
    final_success: float  # 0/1
    sub_task_assignment_accuracy: float  # [0, 1]
    rounds_to_completion: int
    critic_flagged_error_rate: float  # [0, 1]


def score_coordination_trace(workload: Workload, trace: WorkloadTrace) -> CoordinationMetrics:
    """Compute all four coordination metrics for one (workload, trace) pair.

    The final-success scorer is family-specific:

    * Family (a) cross-document fact aggregation — exact match on the aggregate.
    * Family (b) constraint satisfaction — every sub-task assigned to a worker
      whose capacity covers its load. Constraint-checked.
    * Family (c) multi-step retrieval — exact match on the leaf answer.
    """
    success_fn_by_family = {
        "a": _success_a,
        "b": _success_b,
        "c": _success_c,
    }
    success = success_fn_by_family[workload.family.value](workload, trace)

    sub_task_accuracy = _sub_task_accuracy(workload, trace)
    critic_rate = trace.critic_flag_count / max(trace.rounds, 1)

    return CoordinationMetrics(
        final_success=float(success),
        sub_task_assignment_accuracy=sub_task_accuracy,
        rounds_to_completion=trace.rounds,
        critic_flagged_error_rate=critic_rate,
    )


# --------------------------------------------------------------------------- #
# Family-specific success predicates
# --------------------------------------------------------------------------- #
def _success_a(workload: Workload, trace: WorkloadTrace) -> bool:
    return _norm(trace.final_answer) == _norm(workload.expected_answer)


def _success_b(workload: Workload, trace: WorkloadTrace) -> bool:
    """Family (b): every sub-task assigned to *some* worker; assignment respects
    capacity (we trust the workload generator to ensure feasibility exists).
    """
    if trace.final_status != "DONE":
        return False
    if len(trace.sub_task_assignments) != len(workload.sub_tasks):
        return False
    # Capacity check: aggregate load per worker, compare to the workload's
    # advertised capacities (stored in metadata).
    capacities = workload.metadata.get("capacities", "")
    if not (isinstance(capacities, str) and capacities):
        # Missing metadata is a generator bug, not a free pass — the
        # constraint-satisfaction generator always sets ``capacities`` and
        # ``Workload.metadata`` is typed as ``dict[str, str|int|float]``. If
        # we ever see an empty value here, fail closed so the bug surfaces.
        log.warning(
            "coordination._success_b.missing_capacities",
            workload_id=workload.workload_id,
            note="returning success=False; expected metadata['capacities'] to be set",
        )
        return False
    cap_list = [int(x) for x in capacities.split(",")]
    load_by_worker: dict[str, int] = {}
    for st in workload.sub_tasks:
        assigned = trace.sub_task_assignments.get(st.sub_task_id, "")
        load = int(st.constraints.get("load", 1) or 1)
        load_by_worker[assigned] = load_by_worker.get(assigned, 0) + load
    for worker_str, load in load_by_worker.items():
        if not worker_str.startswith("worker-"):
            return False
        idx = int(worker_str.split("-", 1)[1])
        if idx >= len(cap_list):
            return False
        if load > cap_list[idx]:
            return False
    return True


def _success_c(workload: Workload, trace: WorkloadTrace) -> bool:
    return _norm(trace.final_answer) == _norm(workload.expected_answer)


# --------------------------------------------------------------------------- #
# Sub-task accuracy
# --------------------------------------------------------------------------- #
def _sub_task_accuracy(workload: Workload, trace: WorkloadTrace) -> float:
    if not workload.sub_tasks:
        return 1.0
    correct = sum(
        1
        for st in workload.sub_tasks
        if trace.sub_task_assignments.get(st.sub_task_id, "") == st.expected_solver
    )
    return correct / len(workload.sub_tasks)


def _norm(s: str) -> str:
    return " ".join(s.lower().split())
