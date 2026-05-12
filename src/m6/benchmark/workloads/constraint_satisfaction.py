"""Family (b) — constraint-satisfaction planning.

Assign N sub-tasks under capacity constraints. Verified deterministically with
a constraint checker: each agent has a capacity, each sub-task has a load, the
assignment must respect agent capabilities (tag-driven), and the total load on
each agent must stay within capacity.

Ground truth = one feasible assignment found by a simple greedy solver (we do
NOT require the agent runtime to find the *optimal* assignment, only a feasible
one; the critic uses the constraint checker to grade).
"""

from __future__ import annotations

import numpy as np

from m6.benchmark.schemas import (
    SubTask,
    TagDistribution,
    Workload,
    WorkloadFamily,
)
from m6.benchmark.tags import make_tag_vector
from m6.memory_bus.schemas import Fragment


def generate_constraint_satisfaction(
    n_instances: int,
    *,
    seed: int,
    tag_distribution: TagDistribution,
) -> list[Workload]:
    workloads: list[Workload] = []
    base_rng = np.random.default_rng(seed)
    for i in range(n_instances):
        instance_seed = int(base_rng.integers(low=0, high=2**31 - 1))
        rng = np.random.default_rng(instance_seed)
        workloads.append(
            _build_instance(
                instance_id=f"c1-b-{i:03d}",
                rng=rng,
                tag_distribution=tag_distribution,
                seed=instance_seed,
            )
        )
    return workloads


def _build_instance(
    *,
    instance_id: str,
    rng: np.random.Generator,
    tag_distribution: TagDistribution,
    seed: int,
) -> Workload:
    n_agents = int(rng.choice([3, 5, 8]))
    n_tasks = int(rng.integers(low=n_agents + 2, high=n_agents * 3))
    capacities = rng.integers(low=2, high=6, size=n_agents)
    loads = rng.integers(low=1, high=3, size=n_tasks)

    # Greedy feasible assignment (by capacity-remaining).
    assignment: dict[int, int] = {}
    remaining = capacities.copy()
    for t in range(n_tasks):
        # pick the agent with the most remaining capacity.
        order = np.argsort(-remaining)
        for a in order:
            if remaining[a] >= loads[t]:
                assignment[t] = int(a)
                remaining[a] -= loads[t]
                break
        else:
            # Infeasible — bump the most-loaded agent's capacity by 1 and retry.
            a_max = int(np.argmax(capacities))
            capacities[a_max] += 1
            remaining[a_max] += 1
            t -= 1  # noqa: PLW2901 — intentional retry

    fragments: list[Fragment] = [
        Fragment(
            fragment_id=f"{instance_id}/spec",
            text=(
                f"Sub-tasks: {n_tasks}. Agents: {n_agents} with capacities "
                f"{capacities.tolist()}. Loads: {loads.tolist()}. "
                "Assign every sub-task respecting capacity."
            ),
            tags=make_tag_vector(rng, tag_distribution, source_id=f"{instance_id}/spec"),
            task_hint="Distribute the listed sub-tasks across agents under capacity constraints.",
        ),
    ]

    sub_tasks = tuple(
        SubTask(
            sub_task_id=f"{instance_id}/sub-{t}",
            description=f"Task {t} of load {int(loads[t])}.",
            expected_solver=f"worker-{assignment[t]}",
            expected_answer=f"assigned_to=worker-{assignment[t]}",
            constraints={"load": int(loads[t])},
        )
        for t in range(n_tasks)
    )

    initial_prompt = (
        f"Assign {n_tasks} sub-tasks across {n_agents} agents with respective "
        f"capacities {capacities.tolist()}, respecting task loads {loads.tolist()}."
    )
    expected_answer = ";".join(
        f"sub-{t}=worker-{assignment[t]}" for t in range(n_tasks)
    )

    return Workload(
        workload_id=instance_id,
        family=WorkloadFamily.CONSTRAINT_SATISFACTION,
        seed=seed,
        tag_distribution=tag_distribution,
        fragments=tuple(fragments),
        sub_tasks=sub_tasks,
        initial_prompt=initial_prompt,
        n_agents=n_agents,
        expected_answer=expected_answer,
        metadata={
            "n_agents": n_agents,
            "n_tasks": n_tasks,
            "capacities": ",".join(str(int(c)) for c in capacities),
        },
    )
