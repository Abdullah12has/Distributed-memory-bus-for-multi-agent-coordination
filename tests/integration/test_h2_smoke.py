"""Smoke test: generate a tiny benchmark, run H2 with the identity compressor,
verify the runner writes a CSV.

This is the integration-level proof that the full pipeline (benchmark →
orchestrator → cliff fit → CSV) plumbs together without errors.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from m6.benchmark.generator import BenchmarkConfig, generate
from m6.experiments.base import ExperimentConfig
from m6.experiments.h2_coordination_cliff import H2Runner


@pytest.mark.integration()
def test_h2_smoke(tmp_path: Path) -> None:
    bench_cfg = BenchmarkConfig(
        version="c1-smoke",
        seed=0, n_per_family=2, families=("a",), tag_distribution="uniform",
        out_dir=str(tmp_path / "bench"),
    )
    generate(bench_cfg)

    cfg = ExperimentConfig(
        hypothesis="h2",
        benchmark_path=str(tmp_path / "bench"),
        compressors=("none",),
        ratios=(1.0, 2.0, 4.0, 8.0),
        seeds=(0, 1),
        workload_families=("a",),
        out_dir=str(tmp_path / "results"),
    )
    runner = H2Runner(cfg)
    result = runner.run_sync()
    assert (result.out_dir / "results.csv").exists()
    df = pd.read_csv(result.out_dir / "results.csv")
    assert not df.empty
    assert {"compressor", "ratio", "value"}.issubset(df.columns)
