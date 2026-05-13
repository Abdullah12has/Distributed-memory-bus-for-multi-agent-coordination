"""Top-level CLI: ``m6 <subcommand>``.

Aggregates the bus + benchmark + experiment subcommands behind a single Typer
app. The other CLI entry points (``m6-bus``, ``m6-benchmark``, ``m6-experiment``)
remain as direct shortcuts.
"""

from __future__ import annotations

import sys

import typer

from m6 import __version__
from m6.benchmark.cli import app as benchmark_app
from m6.experiments.cli import app as experiment_app
from m6.memory_bus.cli import main as bus_main

app = typer.Typer(add_completion=False, help="m6-thesis CLI")
app.add_typer(benchmark_app, name="benchmark", help="C1 benchmark commands.")
app.add_typer(experiment_app, name="experiment", help="H1..H8 runner commands.")


@app.command()
def bus() -> None:
    """Run the memory bus FastAPI service."""
    bus_main()


@app.command()
def version() -> None:
    """Print the installed m6 version."""
    typer.echo(f"m6-thesis {__version__}")


def main(argv: list[str] | None = None) -> int:
    app(argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
