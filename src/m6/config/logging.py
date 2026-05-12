"""Structured logging via ``structlog``.

We standardise on JSON in production / containers and a human-readable console
renderer in dev. The ``configure_logging`` function is idempotent so tests can
re-call it freely.

The first call writes a process-startup banner (env, version, pid) so log
streams are self-identifying. Subsequent calls re-use the cached configuration.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from m6 import __version__
from m6.config.settings import LogFormat, LogLevel, M6Settings

_CONFIGURED = False


def configure_logging(settings: M6Settings | None = None) -> None:
    """Configure stdlib + structlog. Safe to call multiple times.

    Args:
        settings: Resolved settings; if ``None`` we resolve from env.
    """
    global _CONFIGURED  # noqa: PLW0603 — guarded one-shot.
    if _CONFIGURED:
        return
    _CONFIGURED = True

    if settings is None:
        from m6.config.settings import get_settings  # local to avoid cycles

        settings = get_settings()

    level = logging.getLevelName(settings.log_level)
    logging.basicConfig(
        level=level,
        format="%(message)s",
        stream=sys.stdout,
        force=True,
    )

    # Quiet the noisiest third-party loggers.
    for noisy in ("httpx", "httpcore", "urllib3", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        _add_service_context,
    ]

    renderer: Processor
    if settings.log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(
            colors=sys.stdout.isatty(),
            exception_formatter=structlog.dev.plain_traceback,
        )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log = structlog.get_logger(__name__)
    log.info(
        "m6.startup",
        version=__version__,
        env=settings.env,
        log_level=settings.log_level,
        log_format=settings.log_format,
        pid=os.getpid(),
    )


def _add_service_context(_logger: Any, _method: str, event: EventDict) -> EventDict:
    """Add the service name to every log line — useful in multi-process setups."""
    event.setdefault("service", "m6")
    return event


def reset_logging_for_tests() -> None:
    """Test helper: undo :func:`configure_logging` so the next call re-fires.

    We do NOT promise this restores the *previous* configuration — only that a
    subsequent :func:`configure_logging` will run from scratch.
    """
    global _CONFIGURED  # noqa: PLW0603
    _CONFIGURED = False
    structlog.reset_defaults()


# Re-export so call sites can `from m6.config.logging import get_logger`.
get_logger = structlog.get_logger

__all__ = ["LogFormat", "LogLevel", "configure_logging", "get_logger", "reset_logging_for_tests"]
