"""parse_sub_task_assignments tests.

Pins the regression for the AutoGen-path empty-assignment bug: the previous
orchestrator hard-coded ``sub_task_assignments={}``, which silently failed
the family-(b) success check on every workload.
"""

from __future__ import annotations

from m6.agents.orchestrator import parse_sub_task_assignments
from m6.benchmark.schemas import SubTask, TagDistribution, Workload, WorkloadFamily
from m6.memory_bus.schemas import Classification, Fragment, TagVector


def _toy_workload() -> Workload:
    sub_tasks = tuple(
        SubTask(
            sub_task_id=f"toy/sub-{i}",
            description=f"sub {i}",
            expected_solver=f"worker-{i}",
            expected_answer=f"sub-{i}=worker-{i}",
        )
        for i in range(3)
    )
    return Workload(
        workload_id="toy",
        family=WorkloadFamily.CONSTRAINT_SATISFACTION,
        seed=0,
        tag_distribution=TagDistribution.UNIFORM,
        fragments=(
            Fragment(
                fragment_id="toy/f",
                text="spec",
                tags=TagVector(acl_mask=0, classification=Classification.PUBLIC),
            ),
        ),
        sub_tasks=sub_tasks,
        initial_prompt="assign sub-0..2 to worker-0..2",
        n_agents=3,
        expected_answer="sub-0=worker-0;sub-1=worker-1;sub-2=worker-2",
    )


def test_inline_equals_form() -> None:
    msgs = [
        {
            "source": "planner",
            "content": "Assignments: sub-0=worker-2, sub-1=worker-0, sub-2=worker-1",
        }
    ]
    out = parse_sub_task_assignments(msgs, _toy_workload())
    assert out == {
        "toy/sub-0": "worker-2",
        "toy/sub-1": "worker-0",
        "toy/sub-2": "worker-1",
    }


def test_arrow_form() -> None:
    msgs = [{"source": "planner", "content": "ASSIGN sub-0 -> worker-2\nASSIGN sub-1 to worker-0"}]
    out = parse_sub_task_assignments(msgs, _toy_workload())
    assert out["toy/sub-0"] == "worker-2"
    assert out["toy/sub-1"] == "worker-0"


def test_worker_first_form() -> None:
    msgs = [{"source": "planner", "content": "worker-2: sub-0\nworker-0: sub-1"}]
    out = parse_sub_task_assignments(msgs, _toy_workload())
    assert out["toy/sub-0"] == "worker-2"
    assert out["toy/sub-1"] == "worker-0"


def test_later_assignment_wins() -> None:
    msgs = [
        {"source": "planner", "content": "sub-0=worker-0"},
        {"source": "planner", "content": "sub-0=worker-2"},  # revision
    ]
    out = parse_sub_task_assignments(msgs, _toy_workload())
    assert out["toy/sub-0"] == "worker-2"


def test_unknown_sub_task_id_dropped() -> None:
    msgs = [{"source": "planner", "content": "sub-99=worker-1"}]
    out = parse_sub_task_assignments(msgs, _toy_workload())
    assert out == {}


def test_canonical_id_resolution() -> None:
    """Planner emits short id ('sub-0'); resolver maps to canonical ('toy/sub-0')."""
    msgs = [{"source": "planner", "content": "sub-0=worker-1"}]
    out = parse_sub_task_assignments(msgs, _toy_workload())
    assert "toy/sub-0" in out
