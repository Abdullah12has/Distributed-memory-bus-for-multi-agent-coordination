"""Family (a) — cross-document fact aggregation.

Vignette-7-style: 8 source documents, planner asks "what is X across all
sources?", workers retrieve, critic checks consistency. Per
``use-case-university-ai-service-economy.pdf`` §3.7 (Period-end project
reporting): "8 parallel specialised agents + 80% cloud-payload reduction".

We synthesise fake-but-internally-consistent source documents so the
ground-truth answer is deterministic given the seed.
"""

from __future__ import annotations

import numpy as np

from m6.benchmark.schemas import (
    ProtectedFact,
    SubTask,
    TagDistribution,
    Workload,
    WorkloadFamily,
)
from m6.benchmark.tags import make_tag_vector
from m6.memory_bus.schemas import Classification, Fragment

# Vignette 7 institutional systems (use-case-university-ai-service-economy.pdf p. 2).
_DEFAULT_SYSTEMS = (
    "publication_db",
    "contract_db",
    "moodle",
    "patio",
    "peppi",
    "crm",
    "tatu_sap",
    "sap_travel",
)

_TEMPLATE = (
    "[{system}] Project {project_id} — period {period}.\n"
    "Recorded hours: {hours}. Approved budget: EUR {budget}.\n"
    "Notes: {notes}.\n"
)
_NOTE_BANK = (
    "Travel costs charged separately under WBS-{wbs}.",
    "Two researchers on parental leave for half the period.",
    "ERDF reporting deadline {deadline}; HE deadline two weeks later.",
    "Material costs settled in advance per contract clause {clause}.",
    "Three publications submitted; one accepted.",
)


def generate_fact_aggregation(
    n_instances: int,
    *,
    seed: int,
    tag_distribution: TagDistribution,
    systems: tuple[str, ...] = _DEFAULT_SYSTEMS,
) -> list[Workload]:
    """Generate ``n_instances`` workloads."""
    workloads: list[Workload] = []
    base_rng = np.random.default_rng(seed)
    for i in range(n_instances):
        instance_seed = int(base_rng.integers(low=0, high=2**31 - 1))
        rng = np.random.default_rng(instance_seed)
        workloads.append(
            _build_instance(
                instance_id=f"c1-a-{i:03d}",
                rng=rng,
                tag_distribution=tag_distribution,
                systems=systems,
                seed=instance_seed,
            )
        )
    return workloads


def _build_instance(
    *,
    instance_id: str,
    rng: np.random.Generator,
    tag_distribution: TagDistribution,
    systems: tuple[str, ...],
    seed: int,
) -> Workload:
    project_id = f"P-{int(rng.integers(low=1000, high=9999))}"
    period = f"2025-Q{int(rng.integers(low=1, high=5))}"

    # Per-system facts. The ground-truth aggregate is sum-of-hours and
    # sum-of-budget. The critic checks this against the planner's answer.
    per_system_hours = {s: int(rng.integers(low=10, high=200)) for s in systems}
    per_system_budget = {s: int(rng.integers(low=1_000, high=50_000)) for s in systems}
    total_hours = sum(per_system_hours.values())
    total_budget = sum(per_system_budget.values())

    fragments: list[Fragment] = []
    protected_facts: list[ProtectedFact] = []
    for s in systems:
        text = _TEMPLATE.format(
            system=s,
            project_id=project_id,
            period=period,
            hours=per_system_hours[s],
            budget=per_system_budget[s],
            notes=str(rng.choice(_NOTE_BANK)).format(
                wbs=int(rng.integers(low=100, high=999)),
                deadline=f"2026-0{int(rng.integers(low=1, high=10))}-15",
                clause=f"§{int(rng.integers(low=2, high=20))}.{int(rng.integers(low=1, high=10))}",
            ),
        )
        tag = make_tag_vector(rng, tag_distribution, source_id=f"{instance_id}/{s}")
        frag = Fragment(
            fragment_id=f"{instance_id}/{s}",
            text=text,
            tags=tag,
            task_hint=f"Aggregate hours and budget across all systems for {project_id}.",
        )
        fragments.append(frag)

        # Build a protected-fact entry if the fragment is confidential+.
        # Questions are balanced: one "yes" (threshold below actual) and
        # one "no" (threshold above actual) so priors-only baseline can't
        # score 100% by always guessing the same answer.
        if int(tag.classification) >= int(Classification.CONFIDENTIAL):
            budget_val = per_system_budget[s]
            hours_val = per_system_hours[s]
            protected_facts.append(
                ProtectedFact(
                    fragment_id=frag.fragment_id,
                    fact=f"{s}.budget={budget_val}",
                    yesno_questions=(
                        f"Did {s} for project {project_id} record at least {hours_val - 5} hours?",
                        f"Did {s} for project {project_id} exceed EUR {budget_val + 5000} in budget?",
                    ),
                    answers=("yes", "no"),
                )
            )

    sub_tasks = tuple(
        SubTask(
            sub_task_id=f"{instance_id}/sub-{j}",
            description=f"Extract recorded hours and budget for project {project_id} from {s}.",
            expected_solver=f"worker-{j % 8}",
            expected_answer=f"hours={per_system_hours[s]};budget={per_system_budget[s]}",
        )
        for j, s in enumerate(systems)
    )

    initial_prompt = (
        f"Aggregate the period-end report for project {project_id} across the following "
        f"systems: {', '.join(systems)}. Report total hours and total budget."
    )
    expected_answer = f"hours={total_hours};budget={total_budget}"

    return Workload(
        workload_id=instance_id,
        family=WorkloadFamily.CROSS_DOC_FACT_AGGREGATION,
        seed=seed,
        tag_distribution=tag_distribution,
        fragments=tuple(fragments),
        sub_tasks=sub_tasks,
        initial_prompt=initial_prompt,
        n_agents=8,
        expected_answer=expected_answer,
        protected_facts=tuple(protected_facts),
        metadata={
            "project_id": project_id,
            "period": period,
            "systems": ",".join(systems),
            "total_hours": total_hours,
            "total_budget": total_budget,
        },
    )
