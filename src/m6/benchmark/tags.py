"""Synthetic ACL tag generators.

Three distributions match ``TECHNICAL_REFERENCE.md`` §3.2:

* uniform — each capability bit set independently with p=0.5.
* skewed — exponential family; a handful of bits dominate (typical real ACL).
* hierarchical — bits clustered by classification level so high-classification
  fragments carry a strict superset of low-classification bits.

Each generator is a deterministic function of ``(rng, classification_level)``;
unit-tested for reproducibility.
"""

from __future__ import annotations

import numpy as np

from m6.benchmark.schemas import TagDistribution
from m6.memory_bus.schemas import Classification, TagVector


def sample_acl(
    rng: np.random.Generator,
    distribution: TagDistribution,
    classification: Classification,
) -> int:
    """Return a uint64 ACL mask."""
    if distribution is TagDistribution.UNIFORM:
        bits = rng.integers(0, 2, size=64).astype(np.uint64)
    elif distribution is TagDistribution.SKEWED:
        # Exponential frequencies: bit i set with probability exp(-i/8) clipped.
        probs = np.exp(-np.arange(64) / 8.0)
        probs = np.clip(probs, 0.0, 1.0)
        bits = (rng.random(size=64) < probs).astype(np.uint64)
    elif distribution is TagDistribution.HIERARCHICAL:
        # Top 16 bits gated by classification; the higher the level, the more bits.
        bits = np.zeros(64, dtype=np.uint64)
        low_n = 48                              # always-on pool
        bits[:low_n] = (rng.random(size=low_n) < 0.4).astype(np.uint64)
        high_n = (16 * int(classification)) // 4  # 0 / 4 / 8 / 12 / 16 bits
        if high_n > 0:
            bits[low_n : low_n + high_n] = 1
    else:  # pragma: no cover — exhaustive enum
        msg = f"Unknown tag distribution: {distribution}"
        raise ValueError(msg)

    return _bits_to_uint64(bits)


def sample_classification(
    rng: np.random.Generator,
    *,
    pmf: tuple[float, float, float, float, float] = (0.4, 0.3, 0.15, 0.1, 0.05),
) -> Classification:
    """Sample from the 5-tier lattice.

    Default PMF is skewed toward PUBLIC / INTERNAL (mirroring typical campus
    document distributions; ``use-case-university-ai-service-economy.pdf`` p. 9
    notes that period-end reports mix CONFIDENTIAL data with PUBLIC summaries).
    """
    if abs(sum(pmf) - 1.0) > 1e-6:
        msg = f"PMF must sum to 1.0, got {sum(pmf)}"
        raise ValueError(msg)
    return Classification(int(rng.choice(5, p=list(pmf))))


def make_tag_vector(
    rng: np.random.Generator,
    distribution: TagDistribution,
    source_id: str,
) -> TagVector:
    clazz = sample_classification(rng)
    acl = sample_acl(rng, distribution, clazz)
    return TagVector(
        acl_mask=acl,
        classification=clazz,
        source_ids=(source_id,),
    )


def _bits_to_uint64(bits: np.ndarray) -> int:
    if bits.shape != (64,):
        msg = f"Expected shape (64,), got {bits.shape}"
        raise ValueError(msg)
    out = 0
    for i in range(64):
        if int(bits[i]):
            out |= 1 << i
    return out
