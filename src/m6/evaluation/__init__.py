"""Evaluation harness.

Subpackages:

* :mod:`m6.evaluation.metrics` — QA, coordination, hallucination, compression,
  cost, latency, tag preservation, inference disclosure.
* :mod:`m6.evaluation.statistics` — bootstrap CI, paired bootstrap, Wilcoxon,
  Holm correction, effect sizes.
* :mod:`m6.evaluation.cliff_fitting` — piecewise-linear cliff fitter (H2/H7).
"""

from m6.evaluation.cliff_fitting import CliffFit, fit_piecewise
from m6.evaluation.statistics import (
    BootstrapResult,
    LongDF,
    bootstrap_mean_ci,
    holm_correction,
    mann_whitney_u,
    paired_bootstrap_diff,
    wilcoxon_signed_rank,
)

__all__ = [
    "BootstrapResult",
    "CliffFit",
    "LongDF",
    "bootstrap_mean_ci",
    "fit_piecewise",
    "holm_correction",
    "mann_whitney_u",
    "paired_bootstrap_diff",
    "wilcoxon_signed_rank",
]
