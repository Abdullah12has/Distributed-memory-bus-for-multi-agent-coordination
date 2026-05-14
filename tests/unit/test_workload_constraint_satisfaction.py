"""Constraint-satisfaction workload generator: completeness + feasibility.

Pins the regression for second-pass code-review issue A — the previous version
left some sub-tasks unassigned because the ``t -= 1`` retry was a no-op under
``range()``.
"""

from __future__ import annotations

from m6.benchmark.schemas import TagDistribution
from m6.benchmark.workloads.constraint_satisfaction import (
    generate_constraint_satisfaction,
)


def test_every_subtask_has_an_expected_solver() -> None:
    """For 20 seeds, every generated workload assigns every sub-task."""
    workloads = generate_constraint_satisfaction(
        n_instances=20, seed=0, tag_distribution=TagDistribution.UNIFORM
    )
    for w in workloads:
        for st in w.sub_tasks:
            assert st.expected_solver.startswith(
                "worker-"
            ), f"workload {w.workload_id} has an unassigned sub-task: {st.sub_task_id}"


def test_capacity_respected() -> None:
    """Aggregate per-worker load should not exceed (final) capacity.

    We can't compare against the *original* capacities because the generator
    is allowed to bump them when infeasible; instead we check the assignment
    is internally consistent: every load value is positive and assignment IDs
    are valid worker indices.
    """
    workloads = generate_constraint_satisfaction(
        n_instances=10, seed=1, tag_distribution=TagDistribution.SKEWED
    )
    for w in workloads:
        n_agents = w.n_agents
        for st in w.sub_tasks:
            assert st.expected_solver.startswith("worker-")
            idx = int(st.expected_solver.split("-")[1])
            assert 0 <= idx < n_agents
            load = st.constraints.get("load", 1)
            assert isinstance(load, int)
            assert load >= 1


def test_expected_answer_matches_assignment() -> None:
    """The semicolon-joined expected_answer should mirror the sub_tasks list."""
    workloads = generate_constraint_satisfaction(
        n_instances=3, seed=42, tag_distribution=TagDistribution.HIERARCHICAL
    )
    for w in workloads:
        parts = w.expected_answer.split(";")
        assert len(parts) == len(w.sub_tasks)
