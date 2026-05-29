"""Shared recall metrics for compression evaluation.

Two recall metrics are used across the m6 codebase:

- :func:`token_recall` — generic word-overlap recall between a source
  fragment and its compressed form. Treats all tokens equally.

- :func:`critical_token_recall` (CTR) — family-specific recall measuring
  the fraction of *task-critical* tokens preserved. Tighter and more
  task-relevant than generic recall. Different families use different
  critical-token definitions:

    - **family-a** (cross-document fact aggregation): multi-digit numbers
      — the values being summed. Single digits excluded as noise.
    - **family-b** (constraint-satisfaction planning): all numbers
      (capacities, loads, agent/task counts).
    - **family-c** (multi-step retrieval): "Entry X" / "FINAL-XXXX" chain
      references the solver must follow.

The CTR function was originally defined in
``m6.experiments.run_h1_h2:137``; this module is the canonical location
since 2026-05-29 (per ADR-007). ``run_h1_h2`` re-exports it for
backwards compatibility.
"""

from __future__ import annotations

import re
import string


def _normalize(s: str) -> str:
    """Canonical normalization for word-set comparison.

    Matches the implementation that originated in
    ``m6.experiments.run_h1_h2``: lowercase, strip punctuation,
    remove articles (a/an/the), and collapse whitespace.
    """
    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def token_recall(source: str, compressed: str, gold_answer: str = "") -> float:
    """Fraction of source tokens preserved in compressed text.

    Used by the compounding-error model: q = token_recall; surviving
    info after N rounds ~ q^N. Measures how many of the *source*
    tokens survive compression, not gold-answer tokens (which may be
    aggregated and not appear in any single fragment).

    The ``gold_answer`` parameter is accepted for back-compat with the
    original signature but not used.
    """
    del gold_answer  # back-compat parameter; intentionally unused
    target_tokens = set(_normalize(source).split())
    comp_tokens = set(_normalize(compressed).split())
    if not target_tokens:
        return 1.0
    return len(target_tokens & comp_tokens) / len(target_tokens)


def critical_token_recall(source: str, compressed: str, family: str) -> float:
    """Fraction of task-critical tokens preserved in compressed text.

    Unlike :func:`token_recall` which counts all words, this focuses on
    the tokens that actually determine coordination success.

    Args:
        source: Uncompressed source fragment text.
        compressed: Compressed output text.
        family: C1 task family. One of ``{"a", "b", "c"}``. Other values
            are treated as family-c by default (chain-reference style).

    Returns:
        Float in [0, 1] giving the preserved-critical-token fraction,
        or ``float("nan")`` when the source has no critical tokens
        (caller must handle NaN — typical pattern is to fall back to
        :func:`token_recall`).
    """
    if family == "a":
        critical = set(re.findall(r"\b\d{2,}\b", source))
    elif family == "b":
        critical = set(re.findall(r"\d+", source))
    else:
        critical = set(re.findall(r"(?:entry \d+|FINAL-\d+)", source, re.IGNORECASE))
    if not critical:
        return float("nan")
    critical = {c.lower() for c in critical}
    compressed_lower = compressed.lower()
    preserved = 0
    for c in critical:
        if re.fullmatch(r"\d+", c):
            if re.search(r"(?<!\d)" + re.escape(c) + r"(?!\d)", compressed_lower):
                preserved += 1
        else:
            pattern = r"\b" + re.escape(c) + r"\b"
            if re.search(pattern, compressed_lower):
                preserved += 1
    return preserved / len(critical)
