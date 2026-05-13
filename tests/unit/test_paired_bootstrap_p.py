"""Paired-bootstrap p-value sanity — pin code-review fix #6 (recentred null)."""

from __future__ import annotations

import numpy as np

from m6.evaluation.statistics import paired_bootstrap_diff


def test_zero_diff_high_p() -> None:
    """If diff is identically zero, recentring gives |c| ≥ 0 for all bootstrap
    means ⇒ p = 1.0 (capped at 1.0).
    """
    a = np.zeros(100)
    b = np.zeros(100)
    res = paired_bootstrap_diff(a, b)
    assert res.p_value == 1.0


def test_constant_diff_low_p() -> None:
    """Constant non-zero diff: all bootstrap means equal the observed mean,
    centred bootstrap is identically zero, |0| ≥ |observed| is False ⇒ p hits
    the 1/n_resamples floor.
    """
    a = np.ones(50)
    b = np.zeros(50)
    res = paired_bootstrap_diff(a, b, n_resamples=2_000)
    assert res.statistic == 1.0
    assert (res.p_value or 1.0) <= 1.0 / 2_000 + 1e-9


def test_noisy_positive_diff_below_005() -> None:
    """Small but consistent positive effect: p should clear 0.05."""
    rng = np.random.default_rng(0)
    a = rng.normal(loc=0.5, scale=1.0, size=400)
    b = rng.normal(loc=0.0, scale=1.0, size=400)
    res = paired_bootstrap_diff(a, b)
    assert (res.p_value or 1.0) < 0.05
    assert res.ci_low > 0
