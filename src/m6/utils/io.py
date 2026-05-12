"""I/O primitives shared by every subsystem.

Atomic write, JSONL streaming, run-id generation, content hashing.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@contextmanager
def atomic_write(path: Path | str, mode: str = "w", encoding: str = "utf-8") -> Iterator[Any]:
    """Write to ``path`` atomically.

    Opens a temp file in the same directory, writes, fsyncs, and renames. The
    rename is atomic on the same filesystem. Both text and binary modes
    supported.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(
        mode=mode,
        encoding=encoding if "b" not in mode else None,
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    )
    try:
        yield tmp
        tmp.flush()
        os.fsync(tmp.fileno())
    except Exception:
        tmp.close()
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
        raise
    else:
        tmp.close()
        os.replace(tmp.name, path)


def write_jsonl(path: Path | str, rows: list[dict[str, Any]]) -> int:
    """Append-write a list of dicts as JSONL. Returns rows written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, default=_json_default) + "\n")
            n += 1
    return n


def read_jsonl(path: Path | str) -> list[dict[str, Any]]:
    """Read a JSONL file into a list of dicts. Skips empty lines."""
    path = Path(path)
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            out.append(json.loads(line))
    return out


def hash_text(text: str) -> str:
    """SHA-256 of ``text`` in UTF-8, lowercase hex."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_dict(d: dict[str, Any]) -> str:
    """Stable SHA-256 of a dict: JSON-serialised with sorted keys."""
    canonical = json.dumps(d, sort_keys=True, default=_json_default, ensure_ascii=False)
    return hash_text(canonical)


def make_run_id(prefix: str = "run") -> str:
    """Generate a sortable run id: ``<prefix>-YYYYmmdd-HHMMSS-<uuid8>``."""
    now = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{now}-{uuid.uuid4().hex[:8]}"


def _json_default(o: Any) -> Any:
    """Default JSON serializer for non-stdlib types."""
    if isinstance(o, Path):
        return str(o)
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    if hasattr(o, "isoformat"):
        return o.isoformat()
    if hasattr(o, "model_dump"):
        return o.model_dump()
    if hasattr(o, "__dict__"):
        return o.__dict__
    msg = f"Unserialisable: {type(o).__name__}"
    raise TypeError(msg)
