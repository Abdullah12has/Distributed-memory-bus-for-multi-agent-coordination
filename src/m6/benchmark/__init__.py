"""C1 benchmark.

Three workload families × ~50 instances = 150 total.
Single-command regeneration via :func:`m6.benchmark.generator.generate` or
``make bench-generate``.

Reference: ``docs/TECHNICAL_REFERENCE.md`` §6 and ``configs/benchmark/c1-v0.1.yaml``.
"""

from m6.benchmark.generator import BenchmarkConfig, generate
from m6.benchmark.schemas import Workload, WorkloadFamily

__all__ = ["BenchmarkConfig", "Workload", "WorkloadFamily", "generate"]
