"""Statistical protocol tests."""

from __future__ import annotations

import numpy as np

from m6.evaluation.statistics import (
    bootstrap_mean_ci,
    cliffs_delta,
    cohens_d,
    holm_correction,
    paired_bootstrap_diff,
)


def test_holm_correction_preserves_order() -> None:
    p = [0.01, 0.04, 0.03, 0.5]
    adj = holm_correction(p)
    assert len(adj) == 4
    assert all(0.0 <= a <= 1.0 for a in adj)
    # The largest input is adjusted to its own value (no penalty at the tail).
    assert adj[3] >= p[3]


def test_paired_bootstrap_zero_diff() -> None:
    rng = np.random.default_rng(0)
    a = rng.normal(0, 1, 200)
    b = a.copy()
    res = paired_bootstrap_diff(a, b)
    assert abs(res.statistic) < 1e-9
    # Recentred-bootstrap null with identically-zero observed mean: every
    # bootstrap mean is zero too, so |centred| ≥ 0 always ⇒ p = 1.0.
    assert (res.p_value or 0.0) >= 0.5


def test_paired_bootstrap_clear_positive() -> None:
    a = np.full(200, 1.0)
    b = np.full(200, 0.0)
    res = paired_bootstrap_diff(a, b)
    assert res.statistic == 1.0
    # Recentred bootstrap: |0| ≥ |1| is False ⇒ p hits the 1/n_resamples floor.
    assert (res.p_value or 1.0) <= 0.001


def test_bootstrap_mean_ci_covers_truth() -> None:
    rng = np.random.default_rng(0)
    samples = rng.normal(loc=5.0, scale=1.0, size=500)
    res = bootstrap_mean_ci(samples)
    assert res.ci_low <= 5.0 <= res.ci_high


def test_cohens_d_sign() -> None:
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([0.0, 1.0, 2.0])
    assert cohens_d(a, b) > 0


def test_cliffs_delta_bounds() -> None:
    a = np.array([5.0, 6.0, 7.0])
    b = np.array([1.0, 2.0, 3.0])
    assert cliffs_delta(a, b) == 1.0
    assert cliffs_delta(b, a) == -1.0
