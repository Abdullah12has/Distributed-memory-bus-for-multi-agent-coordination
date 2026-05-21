"""Shared experiment-runner infrastructure.

Every concrete hypothesis runner subclasses :class:`ExperimentRunner`. The base
class provides:

* YAML-config resolution into an :class:`ExperimentConfig`.
* Run-id generation, manifest writing.
* Long-format CSV emission.
* Bookkeeping for the no-compression control condition (plan §7 risk
  mitigation) — runner subclasses must opt out explicitly if they don't want it.

Subclasses implement :meth:`run` and return an :class:`ExperimentResult`.
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import platform
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from m6 import __version__
from m6.agents.orchestrator import AgentConfig, PlannerWorkerCritic
from m6.benchmark.generator import load as load_benchmark
from m6.benchmark.schemas import Workload
from m6.compressors import make_compressor
from m6.config.logging import get_logger
from m6.evaluation.metrics.coordination import score_coordination_trace
from m6.evaluation.statistics import LONG_COLUMNS
from m6.utils.io import atomic_write, hash_dict, make_run_id
from m6.utils.seed import seed_all

log = get_logger(__name__)


@dataclass(frozen=True)
class ExperimentConfig:
    """Common config every hypothesis runner accepts.

    Subclasses subclass this with extra fields.
    """

    hypothesis: str  # "h1".."h4"
    benchmark_path: str = "data/processed/c1-v0.1"
    compressors: tuple[str, ...] = ("lingua2", "filter", "icae")
    ratios: tuple[float, ...] = (1.0, 2.0, 4.0, 8.0, 16.0)
    seeds: tuple[int, ...] = (0, 1, 2, 3, 4)
    workload_families: tuple[str, ...] = ("a",)
    model_size: str = "7b"
    backend: str = "echo"  # for tests; production uses "mlx" etc.
    out_dir: str = "results"
    n_workloads: int | None = None
    include_no_compression_control: bool = True
    # Strict mode: refuse to run if any ICAE-family compressor is in stub mode.
    # Set this true for headline runs that must rest on trained weights.
    require_trained_compressors: bool = False
    notes: str = ""

    @classmethod
    def from_yaml(cls, path: Path | str) -> ExperimentConfig:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class ExperimentResult:
    """The output of one :meth:`ExperimentRunner.run` call."""

    run_id: str
    out_dir: Path
    df: pd.DataFrame
    verdicts: dict[str, Any] = field(default_factory=dict)


class ExperimentRunner(ABC):
    """Abstract base for all H1..H4 runners.

    Concrete subclasses override :meth:`run` and optionally :meth:`prepare`.
    """

    HYPOTHESIS: str = ""  # subclasses override

    def __init__(self, cfg: ExperimentConfig) -> None:
        self.cfg = cfg
        self.run_id = make_run_id(prefix=self.HYPOTHESIS or "exp")
        self.out_dir = Path(cfg.out_dir) / self.HYPOTHESIS / cfg.model_size / self.run_id
        self.out_dir.mkdir(parents=True, exist_ok=True)
        # Per-(name, ratio) compressor cache. Trained ICAE/PEFT instances load
        # model weights in __init__; without this cache every inner-loop call
        # would re-load. Keyed on the ratio because some compressors close over
        # their target_ratio at construction.
        self._compressor_cache: dict[tuple[str, float], Any] = {}
        self._write_manifest()

    # ------------------------------------------------------------------ #
    # API
    # ------------------------------------------------------------------ #
    @abstractmethod
    async def run(self) -> ExperimentResult: ...

    def run_sync(self) -> ExperimentResult:
        return asyncio.run(self.run())

    # ------------------------------------------------------------------ #
    # Helpers shared by every runner
    # ------------------------------------------------------------------ #
    def load_workloads(self) -> list[Workload]:
        wls = load_benchmark(self.cfg.benchmark_path)
        family_filter = set(self.cfg.workload_families)
        wls = [w for w in wls if w.family.value in family_filter]
        if self.cfg.n_workloads:
            wls = wls[: self.cfg.n_workloads]
        return wls

    def emit_row(self, **fields: Any) -> dict[str, Any]:
        """Build a long-format row with sensible defaults for the canonical schema."""
        defaults: dict[str, Any] = {
            "experiment_id": self.run_id,
            "hypothesis": self.HYPOTHESIS,
            "compressor": "none",
            "ratio": 1.0,
            "actual_ratio": 1.0,
            "pipeline": "none",
            "model": "unknown",
            "model_size": self.cfg.model_size,
            "workload_family": "a",
            "workload_id": "?",
            "seed": 0,
            "metric": "coord_success",
            "value": 0.0,
            "wallclock_ms": 0,
            "eur_cost": 0.0,
            "run_id": self.run_id,
            "git_sha": _git_sha(),
            "config_hash": hash_dict(dataclasses.asdict(self.cfg)),
            "created_at": datetime.now(UTC).isoformat(),
            "invalid": False,
            "invalid_reason": None,
        }
        defaults.update(fields)
        return {k: defaults[k] for k in LONG_COLUMNS}

    def write_results(self, df: pd.DataFrame, *, verdicts: dict[str, Any] | None = None) -> None:
        csv_path = self.out_dir / "results.csv"
        df.to_csv(csv_path, index=False)
        if verdicts:
            with atomic_write(self.out_dir / "verdicts.json", mode="w") as fh:
                json.dump(verdicts, fh, indent=2, sort_keys=True, default=str)
        log.info("experiment.results_written", path=str(csv_path), n_rows=len(df))

    def _get_compressor(self, compressor_name: str, ratio: float) -> Any:
        """Return a (cached) compressor instance for the given name and ratio."""
        key = (compressor_name, float(ratio))
        comp = self._compressor_cache.get(key)
        if comp is None:
            comp = make_compressor(compressor_name, target_ratio=ratio)
            if self.cfg.require_trained_compressors and compressor_name in {"icae", "icae-tag"}:
                is_trained = getattr(comp, "is_trained", lambda: False)()
                if not is_trained:
                    msg = (
                        f"require_trained_compressors=true but {compressor_name!r} "
                        f"is in stub mode. Train via `make train-icae` or set "
                        f"require_trained_compressors=false."
                    )
                    raise RuntimeError(msg)
            self._compressor_cache[key] = comp
        return comp

    async def score_workload_with_compressor(
        self,
        workload: Workload,
        compressor_name: str,
        ratio: float,
        *,
        seed: int,
    ) -> dict[str, Any]:
        """Run one (workload, compressor, ratio, seed) cell. Used by H1/H2.

        The compressor is cached on ``self._compressor_cache`` so a trained
        ICAE/PEFT instance is constructed once per ``(name, ratio)`` pair, not
        once per workload-seed call (which for H2 would be ~22 500 reloads).
        """
        comp = self._get_compressor(compressor_name, ratio)
        orchestrator = PlannerWorkerCritic(
            cfg=AgentConfig(backend="determ"),
            compressor=comp,
        )
        trace = await orchestrator.run(workload, seed=seed)
        metrics = score_coordination_trace(workload, trace)
        return {
            "trace": trace,
            "coord_success": metrics.final_success,
            "subtask_acc": metrics.sub_task_assignment_accuracy,
            "rounds": metrics.rounds_to_completion,
            "critic_flagged_rate": metrics.critic_flagged_error_rate,
        }

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _write_manifest(self) -> None:
        manifest = {
            "run_id": self.run_id,
            "hypothesis": self.HYPOTHESIS,
            "version": __version__,
            "platform": platform.platform(),
            "python": platform.python_version(),
            "config": dataclasses.asdict(self.cfg),
            "config_hash": hash_dict(dataclasses.asdict(self.cfg)),
            "started_at": datetime.now(UTC).isoformat(),
        }
        with atomic_write(self.out_dir / "manifest.yaml", mode="w") as fh:
            yaml.safe_dump(manifest, fh, sort_keys=True)


def _git_sha() -> str:
    """Best-effort git SHA. ``unknown`` if not in a git checkout."""
    try:
        import subprocess

        out = subprocess.run(
            ["git", "rev-parse", "--short=10", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return out.stdout.strip()
    except Exception:  # pragma: no cover
        return "unknown"


def configure_runner(hypothesis: str, config_path: Path | str) -> ExperimentRunner:
    """Build the right :class:`ExperimentRunner` subclass by hypothesis name."""
    cfg = ExperimentConfig.from_yaml(config_path)
    if cfg.hypothesis != hypothesis:
        log.warning(
            "experiment.config_hypothesis_mismatch", expected=hypothesis, in_config=cfg.hypothesis
        )

    from m6.experiments.h1_qa_vs_coordination import H1Runner
    from m6.experiments.h2_coordination_cliff import H2Runner
    from m6.experiments.h3_rag_placement import H3Runner
    from m6.experiments.h4_tag_preservation import H4Runner

    runners: dict[str, type[ExperimentRunner]] = {
        "h1": H1Runner,
        "h2": H2Runner,
        "h3": H3Runner,
        "h4": H4Runner,
    }
    cls = runners[hypothesis.lower()]
    seed_all(cfg.seeds[0] if cfg.seeds else 0)
    return cls(cfg)
