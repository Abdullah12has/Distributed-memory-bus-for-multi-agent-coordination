"""Business logic for the memory bus.

The service is intentionally thin: it composes compressor + storage + policy +
audit log into the read/write/audit operations. The FastAPI app in
:mod:`m6.memory_bus.api` is a thin shell around the service.

Reference: ``docs/ARCHITECTURE.md`` §2 (data flow) and ``docs/TECHNICAL_REFERENCE.md``
§3 (data model).
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import OrderedDict
from typing import Protocol

from m6.config.logging import get_logger
from m6.memory_bus.policy import Principal, enforce
from m6.memory_bus.schemas import (
    AuditRow,
    CompressedSlot,
    EventType,
    Fragment,
    SlotId,
    WriteResponse,
)
from m6.memory_bus.storage.protocols import AuditLog, Scratchpad, VectorStore

log = get_logger(__name__)

# Cap the number of distinct (subject, slot_id) pairs we keep for read-miss
# deduplication. Adversarial readers cannot exceed this regardless of request
# rate. The TTL window is 60 s — within that window, repeat misses for the same
# (subject, slot_id) collapse to one audit row.
_READ_MISS_DEDUPE_CAP = 4096
_READ_MISS_DEDUPE_TTL_S = 60.0


class CompressorAPI(Protocol):
    """Service-facing slice of the :class:`m6.compressors.base.Compressor`.

    We re-declare the minimal protocol here so the memory_bus subpackage does
    not import the compressors subpackage (and pull in PyTorch/MLX at import
    time). The compressors implement this larger protocol naturally.
    """

    compressor_id: str

    def compress(
        self,
        fragment: Fragment,
        target_ratio: float | None = None,
    ) -> CompressedSlot: ...

    def embed(self, slot: CompressedSlot) -> list[float] | None:
        """Return an indexable embedding for the slot, or None if not applicable."""


class MemoryBusService:
    """The memory bus service. Stateless beyond the storage handles."""

    def __init__(
        self,
        *,
        audit: AuditLog,
        scratchpad: Scratchpad,
        vector_store: VectorStore,
        compressor: CompressorAPI,
    ) -> None:
        self.audit = audit
        self.scratchpad = scratchpad
        self.vector_store = vector_store
        self.compressor = compressor
        # Per-(subject, slot_id) dedupe window for read-misses so a noisy reader
        # cannot append unbounded ERROR rows to the audit log.
        self._read_miss_seen: OrderedDict[tuple[str, str], float] = OrderedDict()
        self._read_miss_lock = threading.Lock()
        # Per-(subject, fragment_id) dedupe for *denied writes*. Without this,
        # an attacker hammering /v1/write with un-grantable tags could grow the
        # audit log unboundedly — each denied write would otherwise generate a
        # new ``deny-<uuid>`` slot_id and a fresh audit row.
        self._write_deny_seen: OrderedDict[tuple[str, str], float] = OrderedDict()
        self._write_deny_lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # write
    # ------------------------------------------------------------------ #
    def write(
        self,
        principal: Principal,
        fragment: Fragment,
        target_ratio: float | None = None,
    ) -> WriteResponse:
        """Compress, persist, and audit. Returns the slot_id and chain tip."""
        t0 = time.perf_counter()

        # Policy: the WRITER must satisfy the fragment's tags. Reading the
        # write side of policy is symmetric to reading-back.
        if not enforce(principal, fragment.tags):
            if self._should_log_write_deny(principal.subject, fragment.fragment_id):
                row = self.audit.append(
                    slot_id=_provisional_slot_id(),
                    event_type=EventType.DENY,
                    result="DENIED",
                    payload_bytes=fragment.text.encode("utf-8"),
                    requester_acl=principal.acl_mask,
                    requester_classification=int(principal.classification),
                )
                log.info(
                    "bus.write_denied",
                    subject=principal.subject,
                    fragment_id=fragment.fragment_id,
                    audit_rowid=row.rowid,
                )
            raise PolicyDenied(f"Write denied for subject={principal.subject}")

        # Compress, then store, then audit. Order matters: the audit row's
        # payload_hash includes the slot_id, so the slot must exist first.
        slot = self.compressor.compress(fragment, target_ratio=target_ratio)
        self.scratchpad.put(slot)

        embedding = self.compressor.embed(slot)
        if embedding is not None:
            import numpy as np

            self.vector_store.add(slot.slot_id, np.asarray(embedding, dtype="float32"))

        payload_bytes = f"WRITE|{slot.slot_id}|{slot.compressor_id}|{slot.ratio}|{fragment.fragment_id}".encode()
        row = self.audit.append(
            slot_id=slot.slot_id,
            event_type=EventType.WRITE,
            result="OK",
            payload_bytes=payload_bytes,
            requester_acl=principal.acl_mask,
            requester_classification=int(principal.classification),
        )
        log.info(
            "bus.write_ok",
            subject=principal.subject,
            slot_id=slot.slot_id,
            audit_rowid=row.rowid,
            wallclock_ms=int((time.perf_counter() - t0) * 1000),
        )
        return WriteResponse(
            slot_id=slot.slot_id, chain_hash=row.chain_hash.hex(), audit_rowid=row.rowid
        )

    # ------------------------------------------------------------------ #
    # read
    # ------------------------------------------------------------------ #
    def read(self, principal: Principal, slot_id: SlotId) -> tuple[CompressedSlot, AuditRow]:
        """Read a slot. Append READ/DENY to the audit log.

        Read-misses are deduplicated per ``(subject, slot_id)`` within a
        60-second window so a noisy reader cannot inflate the audit log; the
        first miss in a window always audits, subsequent ones short-circuit
        with a synthetic :class:`SlotNotFound`.
        """
        slot = self.scratchpad.get(slot_id)
        if slot is None:
            # No rehydration from FAISS yet — the embedding is lossy and we do
            # not want to silently substitute a near-neighbour. Future work
            # (D7) will use the audit log's payload to rehydrate.
            if not self._should_log_read_miss(principal.subject, slot_id):
                raise SlotNotFound(f"Slot {slot_id} not in scratchpad (deduped)")
            payload_bytes = f"READ|MISS|{slot_id}".encode()
            row = self.audit.append(
                slot_id=slot_id,
                event_type=EventType.READ,
                result="ERROR",
                payload_bytes=payload_bytes,
                requester_acl=principal.acl_mask,
                requester_classification=int(principal.classification),
            )
            raise SlotNotFound(f"Slot {slot_id} not in scratchpad (audit rowid={row.rowid})")

        if not enforce(principal, slot.tags):
            payload_bytes = f"DENY|READ|{slot_id}".encode()
            row = self.audit.append(
                slot_id=slot_id,
                event_type=EventType.DENY,
                result="DENIED",
                payload_bytes=payload_bytes,
                requester_acl=principal.acl_mask,
                requester_classification=int(principal.classification),
            )
            log.info(
                "bus.read_denied",
                subject=principal.subject,
                slot_id=slot_id,
                audit_rowid=row.rowid,
            )
            raise PolicyDenied(f"Read denied for subject={principal.subject}")

        payload_bytes = f"READ|OK|{slot_id}".encode()
        row = self.audit.append(
            slot_id=slot_id,
            event_type=EventType.READ,
            result="OK",
            payload_bytes=payload_bytes,
            requester_acl=principal.acl_mask,
            requester_classification=int(principal.classification),
        )
        log.info("bus.read_ok", subject=principal.subject, slot_id=slot_id, audit_rowid=row.rowid)
        return slot, row

    # ------------------------------------------------------------------ #
    # audit
    # ------------------------------------------------------------------ #
    def audit_history(self, slot_id: SlotId) -> list[AuditRow]:
        return self.audit.history(slot_id)

    def chain_tip(self) -> bytes | None:
        return self.audit.chain_tip()

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _should_log_read_miss(self, subject: str, slot_id: str) -> bool:
        """Per-(subject, slot_id) dedupe: True iff this miss should be audited.

        First miss in the TTL window → True (and we record the timestamp).
        Subsequent misses within the window → False.
        After the cap is hit, the oldest entry is evicted FIFO.
        """
        return _dedupe_check(
            (subject, slot_id),
            self._read_miss_seen,
            self._read_miss_lock,
            ttl_s=_READ_MISS_DEDUPE_TTL_S,
            cap=_READ_MISS_DEDUPE_CAP,
        )

    def _should_log_write_deny(self, subject: str, fragment_id: str) -> bool:
        """Same dedupe shape, applied to denied writes."""
        return _dedupe_check(
            (subject, fragment_id),
            self._write_deny_seen,
            self._write_deny_lock,
            ttl_s=_READ_MISS_DEDUPE_TTL_S,
            cap=_READ_MISS_DEDUPE_CAP,
        )


# --------------------------------------------------------------------------- #
# Exceptions translated to HTTP at the API layer.
# --------------------------------------------------------------------------- #


class PolicyDenied(Exception):
    """Raised when an ACL check fails."""


class SlotNotFound(Exception):
    """Raised when a slot_id is not in the scratchpad."""


def _provisional_slot_id() -> str:
    """For audit rows that record a denied write (no real slot exists)."""
    return f"deny-{uuid.uuid4().hex[:16]}"


def _dedupe_check(
    key: tuple[str, str],
    seen: OrderedDict[tuple[str, str], float],
    lock: threading.Lock,
    *,
    ttl_s: float,
    cap: int,
) -> bool:
    """Generic sliding-window dedupe.

    Returns True iff ``key`` should be acted on (first time, or outside the TTL
    window). Updates ``seen`` in place; evicts oldest entries FIFO once size
    exceeds ``cap``.
    """
    now = time.time()
    with lock:
        ts = seen.get(key)
        if ts is not None and now - ts < ttl_s:
            seen.move_to_end(key)
            return False
        seen[key] = now
        seen.move_to_end(key)
        while len(seen) > cap:
            seen.popitem(last=False)
        return True
