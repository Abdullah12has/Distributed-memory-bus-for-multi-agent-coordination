"""Piecewise-linear cliff fitter for H2.

Fits a two-piece linear function with a free breakpoint τ. Constraint: the
right piece's slope is ≤ the left piece's slope (the "cliff" can only go down).
``scipy.optimize.differential_evolution`` is used for robustness against the
non-convex objective surface.

Returns a :class:`CliffFit` with the breakpoint τ, the two slopes, the
intercept, the RMSE, and the relative drop between left and right means.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy import optimize


@dataclass(frozen=True)
class CliffFit:
    tau: float
    slope_left: float
    slope_right: float
    intercept: float
    rmse: float
    drop_rel: float
    n: int


def _piecewise(
    x: NDArray[np.float64],
    tau: float,
    slope_left: float,
    slope_right: float,
    intercept: float,
) -> NDArray[np.float64]:
    """Two linear pieces meeting at ``tau``. Continuous by construction."""
    out = np.where(
        x <= tau,
        intercept + slope_left * (x - tau),
        intercept + slope_right * (x - tau),
    )
    return out.astype(np.float64)


def fit_piecewise(
    ratios: NDArray[np.float64],
    success: NDArray[np.float64],
    *,
    bounds: tuple[float, float] = (1.0, 16.0),
    n_restart: int = 16,
    seed: int = 0,
) -> CliffFit:
    """Fit piecewise-linear curve and return :class:`CliffFit`.

    Constraint: ``slope_right ≤ slope_left`` (the cliff drops). Enforced by
    parameterising on slope_left and a non-positive delta.
    """
    x = np.asarray(ratios, dtype=np.float64)
    y = np.asarray(success, dtype=np.float64)
    n = len(x)
    if n < 4:
        msg = f"Need ≥4 points for piecewise fit, got {n}"
        raise ValueError(msg)

    y_range = float(max(np.max(y) - np.min(y), 1e-6))

    def _objective(params: NDArray[np.float64]) -> float:
        tau, slope_left, slope_drop, intercept = params
        slope_right = slope_left - max(slope_drop, 0.0)
        preds = _piecewise(x, tau, slope_left, slope_right, intercept)
        return float(np.mean((preds - y) ** 2))

    param_bounds = [
        bounds,  # tau
        (-2.0 / y_range, 2.0 / y_range),  # slope_left  (per ratio-unit)
        (0.0, 4.0 / y_range),  # slope_drop  ≥ 0
        (float(y.min() - 1.0), float(y.max() + 1.0)),  # intercept
    ]

    result = optimize.differential_evolution(
        _objective,
        bounds=param_bounds,
        seed=seed,
        maxiter=300 * n_restart,
        tol=1e-6,
        polish=True,
        popsize=15,
        init="sobol",
    )
    tau, slope_left, slope_drop, intercept = result.x
    slope_right = slope_left - max(slope_drop, 0.0)
    preds = _piecewise(x, tau, slope_left, slope_right, intercept)
    rmse = float(np.sqrt(np.mean((preds - y) ** 2)))
    left_mean = float(y[x <= tau].mean()) if (x <= tau).any() else 0.0
    right_mean = float(y[x > tau].mean()) if (x > tau).any() else left_mean
    drop_rel = (left_mean - right_mean) / max(left_mean, 1e-6)

    return CliffFit(
        tau=float(tau),
        slope_left=float(slope_left),
        slope_right=float(slope_right),
        intercept=float(intercept),
        rmse=rmse,
        drop_rel=float(drop_rel),
        n=n,
    )
