"""QA metrics — F1, EM, ROUGE-L (BERTScore handled by ``evaluate``).

The F1 implementation matches the SQuAD reference token-overlap F1 so external
comparators (NarrativeQA, HotpotQA) reproduce.
"""

from __future__ import annotations

import re
import string
from collections import Counter


def _normalize(s: str) -> str:
    """SQuAD-style normalisation."""
    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = " ".join(s.split())
    return s


def em_score(prediction: str, reference: str) -> float:
    """Exact-match score, ∈ {0, 1}."""
    return float(_normalize(prediction) == _normalize(reference))


def f1_score(prediction: str, reference: str) -> float:
    """Token-overlap F1, ∈ [0, 1]."""
    p_tokens = _normalize(prediction).split()
    r_tokens = _normalize(reference).split()
    if not p_tokens or not r_tokens:
        return float(p_tokens == r_tokens)
    common = Counter(p_tokens) & Counter(r_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(p_tokens)
    recall = num_same / len(r_tokens)
    return 2 * precision * recall / (precision + recall)


def rouge_l(prediction: str, reference: str) -> float:
    """ROUGE-L (longest common subsequence) F1."""
    p_tokens = _normalize(prediction).split()
    r_tokens = _normalize(reference).split()
    if not p_tokens or not r_tokens:
        return float(p_tokens == r_tokens)
    lcs = _lcs_length(p_tokens, r_tokens)
    if lcs == 0:
        return 0.0
    precision = lcs / len(p_tokens)
    recall = lcs / len(r_tokens)
    return 2 * precision * recall / (precision + recall)


def _lcs_length(a: list[str], b: list[str]) -> int:
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return 0
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]
