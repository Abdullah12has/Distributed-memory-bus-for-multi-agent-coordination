"""Pin the baseline-reproduction regression on nested dataset schemas.

NarrativeQA's ``document`` and ``question`` fields are nested dicts; HotpotQA's
``context`` is ``{title: [...], sentences: [[...]]}``. The original code
stringified the whole dict, which (a) produced garbage text, and (b) blew past
Fragment's 200-K-char limit when the dict's repr was long. These tests pin the
extractor against both shapes.
"""

from __future__ import annotations

import pytest

from m6.experiments.baselines import _extract_text, _flatten_hotpot_context, _resolve_path


def test_resolve_path_walks_nested_dict() -> None:
    row = {"document": {"summary": {"text": "hello"}}}
    assert _resolve_path(row, "document.summary.text") == "hello"


def test_resolve_path_raises_on_missing_key() -> None:
    with pytest.raises(KeyError):
        _resolve_path({"a": {"b": 1}}, "a.c")


def test_extract_text_narrativeqa_shape() -> None:
    row = {
        "document": {"summary": {"text": "Once upon a time..."}, "text": "FULL BOOK"},
        "question": {"text": "Who?", "tokens": ["Who", "?"]},
    }
    assert _extract_text(row, "document.summary.text") == "Once upon a time..."
    assert _extract_text(row, "question.text") == "Who?"


def test_extract_text_hotpotqa_sentinel() -> None:
    row = {
        "context": {
            "title": ["Topic A", "Topic B"],
            "sentences": [
                ["A1.", "A2."],
                ["B1.", "B2.", "B3."],
            ],
        }
    }
    out = _extract_text(row, "__hotpot_context__")
    assert "[Topic A]" in out
    assert "[Topic B]" in out
    assert "A1." in out
    assert "B3." in out


def test_extract_text_plain_string_passthrough() -> None:
    row = {"question": "What is 2+2?"}
    assert _extract_text(row, "question") == "What is 2+2?"


def test_flatten_hotpot_context_empty_safe() -> None:
    assert _flatten_hotpot_context({}) == ""
    assert _flatten_hotpot_context({"title": [], "sentences": []}) == ""
