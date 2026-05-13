"""Benchmark generator: deterministic counts, schema-valid."""

from __future__ import annotations

from pathlib import Path

from m6.benchmark.generator import BenchmarkConfig, generate, load


def test_generates_expected_counts(tmp_path: Path) -> None:
    cfg = BenchmarkConfig(
        version="c1-test",
        seed=0,
        n_per_family=3,
        families=("a", "b", "c"),
        tag_distribution="uniform",
        out_dir=str(tmp_path / "bench"),
    )
    out_dir = generate(cfg)
    wls = load(out_dir)
    assert len(wls) == 9
    families = {w.family.value for w in wls}
    assert families == {"a", "b", "c"}


def test_deterministic_under_same_seed(tmp_path: Path) -> None:
    cfg1 = BenchmarkConfig(seed=42, n_per_family=2, out_dir=str(tmp_path / "b1"))
    cfg2 = BenchmarkConfig(seed=42, n_per_family=2, out_dir=str(tmp_path / "b2"))
    generate(cfg1)
    generate(cfg2)
    a = sorted([w.expected_answer for w in load(tmp_path / "b1")])
    b = sorted([w.expected_answer for w in load(tmp_path / "b2")])
    assert a == b
