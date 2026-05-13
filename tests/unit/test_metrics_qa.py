"""QA metrics."""

from __future__ import annotations

from m6.evaluation.metrics.qa import em_score, f1_score, rouge_l


def test_em_normalisation() -> None:
    assert em_score("The Eiffel tower.", "the eiffel tower") == 1.0
    assert em_score("Eiffel", "the eiffel tower") == 0.0


def test_f1_partial_overlap() -> None:
    f1 = f1_score("the eiffel tower", "eiffel tower in paris")
    assert 0.4 < f1 < 0.7


def test_rouge_l_identical() -> None:
    assert rouge_l("hello world", "hello world") == 1.0


def test_rouge_l_disjoint() -> None:
    assert rouge_l("abc def", "xyz qrs") == 0.0
