"""Cost model — pricing table sanity."""

from __future__ import annotations

import math

import pytest

from m6.pipelines.cost_model import PRICING, eur_for_call, register_price


def test_unknown_model_raises() -> None:
    with pytest.raises(KeyError):
        eur_for_call("nope", 1, 1)


def test_zero_tokens_zero_cost() -> None:
    assert eur_for_call("gpt-4o-mini", 0, 0) == 0.0


def test_one_million_tokens_matches_table() -> None:
    p = PRICING["gpt-4o-mini"]
    cost = eur_for_call("gpt-4o-mini", 1_000_000, 0)
    assert math.isclose(cost, p.input_eur, rel_tol=1e-9)


def test_register_price_overrides() -> None:
    register_price("custom-model", input_eur=1.0, output_eur=2.0)
    assert eur_for_call("custom-model", 1_000_000, 1_000_000) == 3.0
