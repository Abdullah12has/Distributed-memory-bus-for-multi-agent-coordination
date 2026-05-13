"""SQLite audit log: append-only enforcement + tamper detection."""

from __future__ import annotations

from pathlib import Path

import pytest

from m6.memory_bus.storage.sqlite_audit import GENESIS_HASH, SQLiteAuditLog


@pytest.fixture()
def audit(tmp_path: Path) -> SQLiteAuditLog:
    return SQLiteAuditLog(tmp_path / "audit.sqlite")


def test_append_and_verify(audit: SQLiteAuditLog) -> None:
    rows = []
    for i in range(5):
        r = audit.append(
            slot_id=f"slot-{i:04d}",
            event_type="WRITE",
            result="OK",
            payload_bytes=f"payload-{i}".encode(),
            requester_acl=0,
            requester_classification=0,
        )
        rows.append(r)
    assert audit.verify() is True
    assert audit.chain_tip() == rows[-1].chain_hash
    assert rows[0].prev_hash == GENESIS_HASH


def test_update_rejected(audit: SQLiteAuditLog) -> None:
    audit.append(slot_id="s-0001", event_type="WRITE", result="OK", payload_bytes=b"x")
    with pytest.raises(Exception, match="append-only"):
        audit._conn.execute("UPDATE audit_log SET result = 'DENIED' WHERE rowid = 1")  # type: ignore[attr-defined]


def test_delete_rejected(audit: SQLiteAuditLog) -> None:
    audit.append(slot_id="s-0001", event_type="WRITE", result="OK", payload_bytes=b"x")
    with pytest.raises(Exception, match="append-only"):
        audit._conn.execute("DELETE FROM audit_log WHERE rowid = 1")  # type: ignore[attr-defined]


def test_corrupted_chain_fails_verify(tmp_path: Path) -> None:
    """Given a corrupted chain (simulated by dropping the trigger and
    overwriting a payload_hash), ``verify()`` reports failure.

    Note: this test confirms the *chain-walker* detects corruption, not that
    the SQL trigger blocks UPDATEs — that's covered by
    :func:`test_update_rejected`.
    """
    db = tmp_path / "audit.sqlite"
    audit = SQLiteAuditLog(db)
    for i in range(3):
        audit.append(slot_id=f"s-{i}", event_type="WRITE", result="OK", payload_bytes=b"x")
    # Bypass the trigger to *simulate* a file-level tamper. In a real attack
    # the attacker would edit the SQLite file directly; the trigger only
    # protects against in-process tampering.
    audit._conn.execute("DROP TRIGGER audit_log_no_update")  # type: ignore[attr-defined]
    audit._conn.execute(  # type: ignore[attr-defined]
        "UPDATE audit_log SET payload_hash = X'00' WHERE rowid = 2"
    )
    assert audit.verify() is False
