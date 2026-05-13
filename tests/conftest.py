"""Shared pytest fixtures."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from m6.config.logging import reset_logging_for_tests
from m6.config.settings import reset_settings_cache


@pytest.fixture(autouse=True)
def _reset_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset settings + logging between tests; redirect IO into ``tmp_path``."""
    monkeypatch.setenv("M6_ENV", "test")
    monkeypatch.setenv("M6_LOG_LEVEL", "WARNING")
    monkeypatch.setenv("M6_DB_PATH", str(tmp_path / "audit.sqlite"))
    monkeypatch.setenv("M6_FAISS_PATH", str(tmp_path / "index.faiss"))
    monkeypatch.setenv("M6_RESULTS_DIR", str(tmp_path / "results"))
    reset_settings_cache()
    reset_logging_for_tests()
    os.chdir(tmp_path)
