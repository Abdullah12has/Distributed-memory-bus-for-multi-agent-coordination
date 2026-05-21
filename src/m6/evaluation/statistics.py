"""Statistical protocol (plan §5.3).

* Bootstrap CI (10 000 resamples).
* Paired bootstrap for compressor-vs-compressor.
* Mann-Whitney U for the cliff-detection (H2) test (independent samples).
* Holm correction within each hypothesis family.
* Effect sizes — Cliff's δ for ordinal, Cohen's d for continuous.

Every test returns a :class:`BootstrapResult` so the experiment runners can
serialise verdicts uniformly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy import stats

# --------------------------------------------------------------------------- #
# Canonical long-format dataframe schema (used by experiment runners).
# --------------------------------------------------------------------------- #
LONG_COLUMNS = (
    "experiment_id",
    "hypothesis",
    "compressor",
    "ratio",
    "actual_ratio",
    "pipeline",
    "model",
    "model_size",
    "workload_family",
    "workload_id",
    "seed",
    "metric",
    "value",
    "wallclock_ms",
    "eur_cost",
    "run_id",
    "git_sha",
    "config_hash",
    "created_at",
    "invalid",
    "invalid_reason",
)


class LongDF:
    """Tiny convenience wrapper for the long-format results dataframe.

    Kept lightweight on purpose; pandas methods are exposed via ``.df``.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        missing = set(LONG_COLUMNS) - set(df.columns)
        if missing:
            msg = f"Missing required columns: {sorted(missing)}"
            raise ValueError(msg)
        self.df = df

    @classmethod
    def empty(cls) -> LongDF:
        return cls(pd.DataFrame(columns=list(LONG_COLUMNS)))

    @classmethod
    def from_rows(cls, rows: list[dict[str, object]]) -> LongDF:
        df = pd.DataFrame(rows, columns=list(LONG_COLUMNS))
        return cls(df)

    def to_csv(self, path: str) -> None:
        self.df.to_csv(path, index=False)


# --------------------------------------------------------------------------- #
# Bootstrap CI
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class BootstrapResult:
    """Output of every statistical test in this module."""

    statistic: float
    p_value: float | None
    ci_low: float
    ci_high: float
    effect_size: float | None
    method: str
    n: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def bootstrap_mean_ci(
    values: NDArray[np.float64],
    *,
    n_resamples: int = 10_000,
    confidence: float = 0.95,
    seed: int = 0,
) -> BootstrapResult:
    """Empirical bootstrap CI of the mean. Two-sided."""
    values = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(seed)
    means = np.empty(n_resamples, dtype=np.float64)
    n = len(values)
    if n == 0:
        return BootstrapResult(0.0, None, 0.0, 0.0, None, "bootstrap_mean", 0)
    for i in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        means[i] = values[idx].mean()
    alpha = 1.0 - confidence
    return BootstrapResult(
        statistic=float(values.mean()),
        p_value=None,
        ci_low=float(np.quantile(means, alpha / 2)),
        ci_high=float(np.quantile(means, 1 - alpha / 2)),
        effect_size=None,
        method="bootstrap_mean",
        n=n,
    )


def paired_bootstrap_diff(
    a: NDArray[np.float64],
    b: NDArray[np.float64],
    *,
    n_resamples: int = 10_000,
    confidence: float = 0.95,
    seed: int = 0,
) -> BootstrapResult:
    """Paired bootstrap on differences (a − b). Plan §5.3.

    Reports:
    * **statistic**       — observed mean difference.
    * **ci_low / ci_high** — percentile bootstrap CI of the mean difference.
    * **p_value**         — two-sided percentile-bootstrap p-value for H0:
      mean(a − b) = 0. Computed by re-centring the bootstrap distribution
      (subtract the observed mean) and taking the fraction of recentred means
      whose absolute value meets or exceeds the observed absolute mean — this
      is the standard percentile-bootstrap test for a mean against a null of
      zero, and is what reviewers expect over the tail-doubling shortcut.

    For a more rigorous (non-symmetric) two-sided test use a sign-flip
    permutation test; the percentile-bootstrap shape here is the version cited
    in Efron & Tibshirani (1993) §16.4.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.shape != b.shape:
        msg = f"paired: shape mismatch {a.shape} vs {b.shape}"
        raise ValueError(msg)
    n = len(a)
    if n == 0:
        return BootstrapResult(0.0, 1.0, 0.0, 0.0, 0.0, "paired_bootstrap_diff", 0)

    diff = a - b
    observed = float(diff.mean())

    rng = np.random.default_rng(seed)
    means = np.empty(n_resamples, dtype=np.float64)
    for i in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        means[i] = diff[idx].mean()

    # Recentre the bootstrap distribution so its mean is zero — this is the
    # bootstrap analogue of "the null hypothesis is true".
    centred = means - means.mean()
    abs_observed = abs(observed)
    # Two-sided test: fraction of recentred means at least as extreme as
    # observed, in absolute value.
    p = float(np.mean(np.abs(centred) >= abs_observed))
    # Clip to [1/n_resamples, 1.0] so a vanishing p doesn't underflow to 0.
    p = max(p, 1.0 / n_resamples)

    alpha = 1.0 - confidence
    return BootstrapResult(
        statistic=observed,
        p_value=p,
        ci_low=float(np.quantile(means, alpha / 2)),
        ci_high=float(np.quantile(means, 1 - alpha / 2)),
        effect_size=cohens_d(a, b),
        method="paired_bootstrap_diff",
        n=n,
    )


def wilcoxon_signed_rank(
    a: NDArray[np.float64],
    b: NDArray[np.float64],
    *,
    alternative: Literal["two-sided", "less", "greater"] = "two-sided",
) -> BootstrapResult:
    """Wrapper around ``scipy.stats.wilcoxon`` returning a :class:`BootstrapResult`.

    Use this for **paired** observations (same workload+seed, different
    compressor/ratio). For independent samples use :func:`mann_whitney_u`.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.shape != b.shape:
        msg = (
            f"wilcoxon_signed_rank requires paired samples of equal length; "
            f"got {a.shape} vs {b.shape}. Use mann_whitney_u for independent samples."
        )
        raise ValueError(msg)
    diff = a - b
    # Drop zero-diff pairs to make wilcoxon happy (zero_method='wilcox').
    nonzero = diff[diff != 0]
    if nonzero.size == 0:
        return BootstrapResult(0.0, 1.0, 0.0, 0.0, 0.0, "wilcoxon", 0)
    res = stats.wilcoxon(a, b, alternative=alternative, zero_method="wilcox")
    return BootstrapResult(
        statistic=float(res.statistic),
        p_value=float(res.pvalue),
        ci_low=float("nan"),
        ci_high=float("nan"),
        effect_size=cliffs_delta(a, b),
        method="wilcoxon",
        n=int(nonzero.size),
    )


def mann_whitney_u(
    a: NDArray[np.float64],
    b: NDArray[np.float64],
    *,
    alternative: Literal["two-sided", "less", "greater"] = "two-sided",
) -> BootstrapResult:
    """Mann-Whitney U rank-sum test for two **independent** samples.

    Used for the cliff-detection test in H2: success values at ``r < τ`` vs
    ``r ≥ τ`` are independent observations drawn across different workload
    instances / seeds, so a paired test is inappropriate.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.size == 0 or b.size == 0:
        return BootstrapResult(0.0, 1.0, 0.0, 0.0, 0.0, "mann_whitney_u", 0)
    res = stats.mannwhitneyu(a, b, alternative=alternative)
    return BootstrapResult(
        statistic=float(res.statistic),
        p_value=float(res.pvalue),
        ci_low=float("nan"),
        ci_high=float("nan"),
        effect_size=cliffs_delta(a, b),
        method="mann_whitney_u",
        n=int(a.size + b.size),
    )


# --------------------------------------------------------------------------- #
# Multiple-comparison correction
# --------------------------------------------------------------------------- #
def holm_correction(p_values: list[float], alpha: float = 0.05) -> list[float]:
    """Holm-Bonferroni adjusted p-values.

    Returns adjusted p-values in the input order. Reject H0_i ⟺ adj_p_i ≤ alpha.
    """
    _ = alpha  # kept in signature for documentation; not used in adjustment math.
    n = len(p_values)
    if n == 0:
        return []
    order = sorted(range(n), key=lambda i: p_values[i])
    adj: list[float] = [0.0] * n
    running = 0.0
    for rank, idx in enumerate(order):
        candidate = (n - rank) * p_values[idx]
        running = max(running, candidate)
        adj[idx] = min(running, 1.0)
    return adj


# --------------------------------------------------------------------------- #
# Effect sizes
# --------------------------------------------------------------------------- #
def cohens_d(a: NDArray[np.float64], b: NDArray[np.float64]) -> float:
    """Cohen's d for paired samples (mean diff / pooled SD)."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    diff = a - b
    sd = float(np.std(diff, ddof=1)) if diff.size > 1 else 1.0
    if sd == 0:
        return 0.0
    return float(diff.mean()) / sd


def cliffs_delta(a: NDArray[np.float64], b: NDArray[np.float64]) -> float:
    """Cliff's δ — ordinal effect size in [-1, 1]."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    # Vectorised: for each (a_i, b_j) pair, compute sign(a_i - b_j) and average.
    diffs = a[:, None] - b[None, :]
    n_total = diffs.size
    if n_total == 0:
        return 0.0
    return float(((diffs > 0).sum() - (diffs < 0).sum()) / n_total)


def spearman_rho(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    *,
    n_bootstrap: int = 10_000,
    seed: int = 0,
) -> BootstrapResult:
    """Spearman's ρ with bootstrap CI (H1)."""
    rho, p = stats.spearmanr(x, y)
    rng = np.random.default_rng(seed)
    n = len(x)
    rhos = np.empty(n_bootstrap, dtype=np.float64)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        rhos[i], _ = stats.spearmanr(x[idx], y[idx])
    # Filter NaN values from bootstrap (constant resamples produce NaN rho).
    rhos_clean = rhos[~np.isnan(rhos)]
    if rhos_clean.size > 0:
        ci_low = float(np.quantile(rhos_clean, 0.025))
        ci_high = float(np.quantile(rhos_clean, 0.975))
    else:
        ci_low = float("nan")
        ci_high = float("nan")
    return BootstrapResult(
        statistic=float(rho) if not np.isnan(rho) else 0.0,
        p_value=float(p) if not np.isnan(p) else 1.0,
        ci_low=ci_low,
        ci_high=ci_high,
        effect_size=None,
        method="spearman_rho",
        n=n,
    )
