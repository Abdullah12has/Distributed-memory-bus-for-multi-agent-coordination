"""Configuration layer.

Two responsibilities:

1. :mod:`m6.config.settings` — Pydantic-settings backed environment + CLI
   resolution. Single source of truth for runtime configuration.
2. :mod:`m6.config.logging` — ``structlog`` setup. Imported once at process
   startup by :func:`m6.config.logging.configure_logging`.
"""

from m6.config.logging import configure_logging
from m6.config.settings import M6Settings, get_settings

__all__ = ["M6Settings", "configure_logging", "get_settings"]
