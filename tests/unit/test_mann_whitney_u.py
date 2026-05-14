"""Mann-Whitney U test used by H2 — pin regression in code-review issue #2."""

from __future__ import annotations

import numpy as np
import pytest

from m6.evaluation.statistics import mann_whitney_u, wilcoxon_signed_rank


def test_independent_samples_clear_separation() -> None:
    """Two well-separated independent samples → low p, large positive effect."""
    rng = np.random.default_rng(0)
    a = rng.normal(loc=1.0, scale=0.1, size=50)
    b = rng.normal(loc=0.0, scale=0.1, size=80)  # different N!
    res = mann_whitney_u(a, b, alternative="greater")
    assert (res.p_value or 1.0) < 0.001
    assert res.effect_size is not None
    assert res.effect_size > 0.8
    assert res.method == "mann_whitney_u"


def test_unequal_lengths_supported() -> None:
    """Unlike wilcoxon, mann_whitney_u accepts unequal-length inputs."""
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0, 7.0, 8.0])
    res = mann_whitney_u(a, b)
    assert res.p_value is not None
    assert res.n == 8


def test_wilcoxon_rejects_unequal_lengths() -> None:
    """The paired test should refuse mismatched shapes after the fix."""
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0])
    with pytest.raises(ValueError, match="paired samples of equal length"):
        wilcoxon_signed_rank(a, b)
