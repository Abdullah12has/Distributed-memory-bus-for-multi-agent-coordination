"""Workload family generators."""

from m6.benchmark.workloads.constraint_satisfaction import generate_constraint_satisfaction
from m6.benchmark.workloads.fact_aggregation import generate_fact_aggregation
from m6.benchmark.workloads.multi_step_retrieval import generate_multi_step_retrieval

__all__ = [
    "generate_constraint_satisfaction",
    "generate_fact_aggregation",
    "generate_multi_step_retrieval",
]
