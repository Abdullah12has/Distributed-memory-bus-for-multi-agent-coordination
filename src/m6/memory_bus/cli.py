"""CLI entry-point ``m6-bus`` — thin wrapper around uvicorn."""

from __future__ import annotations

import sys

import uvicorn

from m6.config.settings import get_settings


def main(argv: list[str] | None = None) -> int:
    """Run the memory bus FastAPI service."""
    _ = argv  # currently unused; argparse hooks land in M5 polish.
    settings = get_settings()
    uvicorn.run(
        "m6.memory_bus.api:app",
        host=settings.host,
        port=settings.port,
        workers=1,
        log_config=None,
        access_log=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
