"""Experiment runners — one per hypothesis (H1..H8).

Each runner reads a YAML config, executes the protocol described in
``docs/HYPOTHESIS_IMPLEMENTATION_PLAN.md``, and writes the canonical long-format
CSV under ``results/h{N}/<run_id>/``.

Shared infrastructure lives in :mod:`m6.experiments.base`.
"""

from m6.experiments.base import ExperimentConfig, ExperimentResult, ExperimentRunner

__all__ = ["ExperimentConfig", "ExperimentResult", "ExperimentRunner"]
