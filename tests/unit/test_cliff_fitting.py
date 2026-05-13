"""Piecewise-linear cliff fitter."""

from __future__ import annotations

import numpy as np

from m6.evaluation.cliff_fitting import fit_piecewise


def test_recovers_known_cliff() -> None:
    """Fitting a synthetic cliff at τ=5 should recover τ within ±1.0."""
    rng = np.random.default_rng(0)
    ratios = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0])

    def f(r: float) -> float:
        return 0.95 - 0.01 * (r - 5) if r <= 5 else 0.95 - 0.10 * (r - 5)

    success = np.array([f(r) for r in ratios]) + rng.normal(0, 0.005, len(ratios))
    fit = fit_piecewise(ratios, success, seed=0)
    assert abs(fit.tau - 5.0) <= 1.0
    assert fit.slope_right <= fit.slope_left + 1e-3
    assert fit.drop_rel > 0.0


def test_smooth_curve_has_low_drop() -> None:
    """A smoothly-decreasing curve should produce a small drop_rel."""
    ratios = np.array([1.0, 2.0, 4.0, 8.0, 16.0])
    success = np.array([0.9, 0.85, 0.78, 0.7, 0.62])
    fit = fit_piecewise(ratios, success, seed=0)
    assert fit.drop_rel < 0.3
