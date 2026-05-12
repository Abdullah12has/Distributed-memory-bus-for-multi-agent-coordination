"""Business logic for the memory bus.

The service is intentionally thin: it composes compressor + storage + policy +
audit log into the read/write/audit operations. The FastAPI app in
:mod:`m6.memory_bus.api` is a thin shell around the service.

Reference: ``docs/ARCHITECTURE.md`` §2 (data flow) and ``docs/TECHNICAL_REFERENCE.md``
§3 (data model).
"""

from __future__ import annotations

import time
import uuid
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

    def embed(self, slot: CompressedSlot) -> "list[float] | None":
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

        payload_bytes = (
            f"WRITE|{slot.slot_id}|{slot.compressor_id}|{slot.ratio}|{fragment.fragment_id}".encode()
        )
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
        """Read a slot. Append READ/DENY to the audit log."""
        slot = self.scratchpad.get(slot_id)
        if slot is None:
            # No rehydration from FAISS yet — the embedding is lossy and we do
            # not want to silently substitute a near-neighbour. Future work
            # (D7) will use the audit log's payload to rehydrate.
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
