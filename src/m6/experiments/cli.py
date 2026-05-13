"""``m6-experiment`` CLI."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from m6.config.logging import configure_logging
from m6.experiments.base import configure_runner

app = typer.Typer(add_completion=False, help="Experiment runners (H1–H8).")


@app.command()
def run(
    hypothesis: str = typer.Option(..., "--hypothesis", "-h", help="h1..h8"),
    config: Path = typer.Option(..., "--config", "-c", help="YAML config path"),
) -> None:
    """Run one hypothesis end-to-end. Writes to ``results/<h>/<run_id>/``."""
    configure_logging()
    runner = configure_runner(hypothesis, config)
    runner.run_sync()


def main(argv: list[str] | None = None) -> int:
    app(argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
