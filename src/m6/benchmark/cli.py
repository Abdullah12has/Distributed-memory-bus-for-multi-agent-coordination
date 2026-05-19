"""``m6-benchmark`` CLI."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from m6.benchmark.generator import BenchmarkConfig, generate, load
from m6.config.logging import configure_logging, get_logger

app = typer.Typer(add_completion=False, help="C1 benchmark generation + validation.")
log = get_logger(__name__)


@app.command()  # type: ignore[misc]
def generate_cmd(
    config: Path = typer.Option(..., "--config", "-c", help="Path to YAML config."),
    out: Path | None = typer.Option(None, "--out", "-o", help="Override output dir."),
) -> None:
    """Generate the C1 benchmark from ``config``."""
    configure_logging()
    cfg = BenchmarkConfig.from_yaml(config)
    if out is not None:
        cfg = type(cfg)(**{**cfg.__dict__, "out_dir": str(out)})
    out_dir = generate(cfg)
    typer.echo(f"✓ wrote {out_dir}")


@app.command()  # type: ignore[misc]
def validate(
    path: Path = typer.Option(..., "--path", "-p", help="Path to a generated benchmark dir."),
) -> None:
    """Re-load every workload and validate the schema. Exits non-zero on error."""
    configure_logging()
    try:
        workloads = load(path)
    except Exception as e:
        log.error("benchmark.validate_failed", error=str(e))
        raise typer.Exit(code=1) from e
    log.info("benchmark.validate_ok", total=len(workloads))
    typer.echo(f"✓ {len(workloads)} workloads validated")


def main(argv: list[str] | None = None) -> int:
    app(argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
