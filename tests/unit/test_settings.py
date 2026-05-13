"""Settings + logging tests."""

from __future__ import annotations

import pytest

from m6.config.settings import M6Settings, get_settings, reset_settings_cache


def test_defaults_load() -> None:
    """A bare settings object resolves all defaults without errors."""
    s = M6Settings()
    assert s.env == "test"
    assert 1024 <= s.port <= 65535
    assert s.default_compressor in {"icae", "icae-tag", "lingua2", "filter", "none"}


def test_seeds_parsing_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("M6_DEFAULT_SEEDS", "1,3,5,7")
    reset_settings_cache()
    s = get_settings()
    assert s.default_seeds == (1, 3, 5, 7)


def test_ratio_bounds() -> None:
    with pytest.raises(ValueError, match="must be in"):
        M6Settings(default_ratio=64.0)
