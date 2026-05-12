"""Top-level C1 benchmark generator.

One YAML config in, one directory of JSONL out. Reproducible from a single
command (``make bench-generate``).

The directory layout is::

    data/processed/c1-v0.1/
    ├── manifest.json
    ├── family-a.jsonl      # cross-document fact aggregation
    ├── family-b.jsonl      # constraint-satisfaction planning
    └── family-c.jsonl      # multi-step retrieval
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from m6.benchmark.schemas import (
    TagDistribution,
    Workload,
    WorkloadFamily,
    WorkloadManifest,
)
from m6.benchmark.workloads import (
    generate_constraint_satisfaction,
    generate_fact_aggregation,
    generate_multi_step_retrieval,
)
from m6.config.logging import get_logger
from m6.utils.io import atomic_write, hash_dict, write_jsonl

log = get_logger(__name__)


@dataclass(frozen=True)
class BenchmarkConfig:
    """Resolved benchmark-generation config. Mirrors ``configs/benchmark/c1-v0.1.yaml``."""

    version: str = "c1-v0.1"
    seed: int = 0
    n_per_family: int = 50
    families: tuple[str, ...] = ("a", "b", "c")
    tag_distribution: str = "skewed"           # uniform | skewed | hierarchical
    out_dir: str = "data/processed/c1-v0.1"

    @classmethod
    def from_yaml(cls, path: Path | str) -> BenchmarkConfig:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


def generate(cfg: BenchmarkConfig) -> Path:
    """Generate the benchmark on disk. Returns the output directory."""
    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tag_dist = TagDistribution(cfg.tag_distribution)
    families_counts: dict[str, int] = {}

    for f in cfg.families:
        family = WorkloadFamily(f)
        path = out_dir / f"family-{family.value}.jsonl"
        # Truncate; the writer is append-only by default.
        path.write_text("", encoding="utf-8")

        workloads = _generate_family(family, cfg.n_per_family, cfg.seed, tag_dist)
        n = write_jsonl(path, [_dump_workload(w) for w in workloads])
        families_counts[family.value] = n
        log.info("benchmark.family_written", family=family.value, n=n, path=str(path))

    manifest = WorkloadManifest(
        version=cfg.version,
        generated_at=datetime.now(timezone.utc).isoformat(),
        config_hash=hash_dict(dataclasses.asdict(cfg)),
        families=families_counts,
        total=sum(families_counts.values()),
        notes=(
            "C1 benchmark v0.1 — three workload families per plan §4.2. "
            "Vignette-7 inspired (use-case-university-ai-service-economy.pdf §3.7)."
        ),
    )
    with atomic_write(out_dir / "manifest.json", mode="w") as fh:
        json.dump(manifest.model_dump(), fh, indent=2, sort_keys=True)
    log.info(
        "benchmark.manifest_written",
        path=str(out_dir / "manifest.json"),
        total=manifest.total,
    )
    return out_dir


def _generate_family(
    family: WorkloadFamily,
    n: int,
    seed: int,
    tag_dist: TagDistribution,
) -> Iterable[Workload]:
    # Family seeds are derived so each family is reproducible independently.
    family_seed = seed * 7919 + ord(family.value)
    if family is WorkloadFamily.CROSS_DOC_FACT_AGGREGATION:
        return generate_fact_aggregation(n, seed=family_seed, tag_distribution=tag_dist)
    if family is WorkloadFamily.CONSTRAINT_SATISFACTION:
        return generate_constraint_satisfaction(n, seed=family_seed, tag_distribution=tag_dist)
    if family is WorkloadFamily.MULTI_STEP_RETRIEVAL:
        return generate_multi_step_retrieval(n, seed=family_seed, tag_distribution=tag_dist)
    msg = f"Unknown family: {family}"  # pragma: no cover - exhaustive enum
    raise ValueError(msg)


def _dump_workload(w: Workload) -> dict[str, object]:
    return w.model_dump(mode="json")


def load(path: Path | str) -> list[Workload]:
    """Load every workload from a previously-generated benchmark directory."""
    out: list[Workload] = []
    path = Path(path)
    for fjson in sorted(path.glob("family-*.jsonl")):
        for line in fjson.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            out.append(Workload.model_validate_json(line))
    return out
