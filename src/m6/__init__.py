"""m6-thesis — Distributed Memory Bus for Multi-Agent Campus Systems.

The package's top-level surface is intentionally small. Each subpackage owns its
public API; ``m6.cli`` aggregates them into a Typer-based command-line entry
point.

Public re-exports here are limited to the items most code outside the package
imports:

* :class:`m6.config.settings.M6Settings` — resolved runtime configuration.
* :class:`m6.memory_bus.schemas.Fragment`, :class:`CompressedSlot`,
  :class:`TagVector` — the wire-level types.

Anything else is reached through its module path so that import order stays
predictable and circular imports stay impossible.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("m6-thesis")
except PackageNotFoundError:  # pragma: no cover - happens before `pip install -e .`
    __version__ = "0.0.0+unbuilt"

__all__ = ["__version__"]
