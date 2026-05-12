"""Benchmark data model.

A workload is a self-contained planner-worker-critic task. Three families per
``docs/TECHNICAL_REFERENCE.md`` §6.1; the same Pydantic schema captures all
three with a discriminator field.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from m6.memory_bus.schemas import Fragment, TagVector


class WorkloadFamily(str, Enum):
    CROSS_DOC_FACT_AGGREGATION = "a"
    CONSTRAINT_SATISFACTION = "b"
    MULTI_STEP_RETRIEVAL = "c"


class SubTask(BaseModel):
    """One unit of work assigned by the planner to a worker."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    sub_task_id: str
    description: str
    expected_solver: str          # e.g. "worker-2" or "any-with-tool=retrieve"
    expected_answer: str          # ground truth used by the critic
    constraints: dict[str, str | int | float] = Field(default_factory=dict)


class TagDistribution(str, Enum):
    UNIFORM = "uniform"
    SKEWED = "skewed"
    HIERARCHICAL = "hierarchical"


class ProtectedFact(BaseModel):
    """Used by H6 — a fact-recovery target for the held-out reader."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    fragment_id: str
    fact: str
    yesno_questions: tuple[str, ...]
    answers: tuple[Literal["yes", "no"], ...]


class Workload(BaseModel):
    """Self-contained workload instance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workload_id: str
    family: WorkloadFamily
    seed: int                                # generation seed (not the experiment seed)
    tag_distribution: TagDistribution
    fragments: tuple[Fragment, ...]
    sub_tasks: tuple[SubTask, ...]
    initial_prompt: str
    n_agents: int
    expected_answer: str                     # planner's final-answer ground truth
    protected_facts: tuple[ProtectedFact, ...] = Field(default_factory=tuple)
    metadata: dict[str, str | int | float] = Field(default_factory=dict)


class WorkloadManifest(BaseModel):
    """Top-level manifest for the C1 release.

    Written to ``data/processed/c1-v0.1/manifest.json``. Carries the resolved
    config, the seed, and counts per family for reproducibility checks.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: str
    generated_at: str
    config_hash: str
    families: dict[str, int]
    total: int
    notes: str = ""


class WorkloadTrace(BaseModel):
    """One agent-runtime trace from the planner-worker-critic loop.

    Persisted to ``traces/`` for replay; consumed by the coordination-metric
    scorers in :mod:`m6.evaluation.metrics.coordination`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    trace_id: str
    workload_id: str
    compressor_id: str
    ratio: float
    seed: int
    rounds: int
    final_status: Literal["DONE", "REVISE", "ERROR"]
    final_answer: str
    sub_task_assignments: dict[str, str]
    critic_flag_count: int
    wallclock_ms: int
    expected: TagVector | None = None     # not used by scorers; for forensics
