"""SQLite-backed audit log with tamper-evident hash chain.

Schema and trigger mirror ``software-architecture.pdf`` §3.5 ``audit_transcript``
with the bid/alloc/payments columns collapsed into a single ``payload_hash``
(the thesis bus does not run an auction). Detailed rationale in
``docs/adr/ADR-002-storage-stack.md``.

Concurrency: SQLite in WAL mode allows multiple readers + one writer. The bus
runs with ``--workers 1`` so write contention is bounded by the agent runtime.
"""

from __future__ import annotations

import hashlib
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from m6.config.logging import get_logger
from m6.memory_bus.schemas import AuditRow, SlotId

log = get_logger(__name__)

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA temp_store = MEMORY;

CREATE TABLE IF NOT EXISTS audit_log (
    rowid                    INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_id                  TEXT NOT NULL,
    event_type               TEXT NOT NULL CHECK (event_type IN
        ('WRITE','READ','SUBSCRIBE','DENY','COMPRESS','EVICT')),
    requester_acl            INTEGER,
    requester_classification INTEGER,
    result                   TEXT NOT NULL CHECK (result IN ('OK','DENIED','ERROR')),
    prev_hash                BLOB NOT NULL,
    payload_hash             BLOB NOT NULL,
    chain_hash               BLOB NOT NULL,
    created_at               TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_audit_slot_id ON audit_log(slot_id);
CREATE INDEX IF NOT EXISTS ix_audit_created_at ON audit_log(created_at);

-- Append-only enforcement: refuse UPDATEs and DELETEs.
CREATE TRIGGER IF NOT EXISTS audit_log_no_update
BEFORE UPDATE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'audit_log is append-only: UPDATE rejected');
END;

CREATE TRIGGER IF NOT EXISTS audit_log_no_delete
BEFORE DELETE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'audit_log is append-only: DELETE rejected');
END;

-- Cost ledger lives in the same database for transactional consistency.
CREATE TABLE IF NOT EXISTS cost_ledger (
    rowid          INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id  TEXT,
    provider       TEXT NOT NULL,
    model          TEXT NOT NULL,
    input_tokens   INTEGER NOT NULL,
    output_tokens  INTEGER NOT NULL,
    eur_cost       REAL NOT NULL,
    wallclock_ms   INTEGER NOT NULL,
    created_at     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_cost_experiment ON cost_ledger(experiment_id);
"""

# Genesis hash for an empty chain: 32 zero bytes. Same convention as Bitcoin's
# coinbase parent, kept here for the same reason — gives `verify()` a starting
# point.
GENESIS_HASH = b"\x00" * 32


class SQLiteAuditLog:
    """Reference :class:`AuditLog` implementation.

    Thread-safe via a single per-instance ``RLock``; bus-internal callers are
    expected to be cooperative.

    See ``docs/TECHNICAL_REFERENCE.md`` §3.3 for the column definitions and the
    chain-hash formula.
    """

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        # ``check_same_thread=False`` because FastAPI handlers can run in
        # different worker threads under uvloop; we serialize on ``self._lock``.
        self._conn = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA_SQL)
        log.info("audit.opened", path=str(self.path))

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def append(
        self,
        slot_id: SlotId,
        event_type: str,
        result: str,
        payload_bytes: bytes,
        requester_acl: int | None = None,
        requester_classification: int | None = None,
    ) -> AuditRow:
        """Append one row. The chain_hash is computed inside the lock so it
        never races with another writer.
        """
        payload_hash = hashlib.sha256(payload_bytes).digest()
        with self._lock:
            prev = self.chain_tip() or GENESIS_HASH
            chain_hash = hashlib.sha256(prev + payload_hash).digest()
            cur = self._conn.execute(
                "INSERT INTO audit_log "
                "(slot_id, event_type, requester_acl, requester_classification, "
                " result, prev_hash, payload_hash, chain_hash, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    slot_id,
                    event_type,
                    requester_acl,
                    requester_classification,
                    result,
                    prev,
                    payload_hash,
                    chain_hash,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            rowid = cur.lastrowid
        if rowid is None:  # pragma: no cover — defensive
            msg = "SQLite returned no rowid after INSERT"
            raise RuntimeError(msg)
        row = self.get(rowid)
        if row is None:  # pragma: no cover — defensive
            msg = f"Could not fetch just-inserted rowid={rowid}"
            raise RuntimeError(msg)
        return row

    def get(self, rowid: int) -> AuditRow | None:
        with self._lock:
            r = self._conn.execute("SELECT * FROM audit_log WHERE rowid = ?", (rowid,)).fetchone()
        if r is None:
            return None
        return _row_to_audit(r)

    def history(self, slot_id: SlotId) -> list[AuditRow]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM audit_log WHERE slot_id = ? ORDER BY rowid ASC",
                (slot_id,),
            ).fetchall()
        return [_row_to_audit(r) for r in rows]

    def chain_tip(self) -> bytes | None:
        with self._lock:
            r = self._conn.execute(
                "SELECT chain_hash FROM audit_log ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
        return None if r is None else bytes(r["chain_hash"])

    def verify(self) -> bool:
        """Walk every row, recompute chain_hash, compare to the stored value."""
        with self._lock:
            rows = self._conn.execute(
                "SELECT prev_hash, payload_hash, chain_hash "
                "FROM audit_log ORDER BY rowid ASC"
            ).fetchall()
        prev = GENESIS_HASH
        for i, r in enumerate(rows):
            stored_prev = bytes(r["prev_hash"])
            if stored_prev != prev:
                log.warning("audit.chain_broken", rowid=i + 1, reason="prev_hash_mismatch")
                return False
            recomputed = hashlib.sha256(prev + bytes(r["payload_hash"])).digest()
            if recomputed != bytes(r["chain_hash"]):
                log.warning("audit.chain_broken", rowid=i + 1, reason="chain_hash_mismatch")
                return False
            prev = recomputed
        return True

    def close(self) -> None:
        with self._lock:
            self._conn.close()
        log.info("audit.closed", path=str(self.path))

    # Context manager support for tests.
    def __enter__(self) -> SQLiteAuditLog:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    # ------------------------------------------------------------------ #
    # Cost ledger helpers (lives in the same DB; sharing the lock is cheap)
    # ------------------------------------------------------------------ #
    def append_cost(
        self,
        *,
        experiment_id: str | None,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        eur_cost: float,
        wallclock_ms: int,
    ) -> int:
        """Append one row to the cost ledger."""
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO cost_ledger "
                "(experiment_id, provider, model, input_tokens, output_tokens, "
                " eur_cost, wallclock_ms, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    experiment_id,
                    provider,
                    model,
                    input_tokens,
                    output_tokens,
                    eur_cost,
                    wallclock_ms,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        return int(cur.lastrowid or 0)


def _row_to_audit(r: sqlite3.Row) -> AuditRow:
    return AuditRow(
        rowid=r["rowid"],
        slot_id=r["slot_id"],
        event_type=r["event_type"],
        requester_acl=r["requester_acl"],
        requester_classification=r["requester_classification"],
        result=r["result"],
        prev_hash=bytes(r["prev_hash"]),
        payload_hash=bytes(r["payload_hash"]),
        chain_hash=bytes(r["chain_hash"]),
        created_at=datetime.fromisoformat(r["created_at"]),
    )
