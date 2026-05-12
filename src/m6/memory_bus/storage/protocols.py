"""Storage protocols.

Why protocols and not abstract base classes? The bus and the experiments mock
storage in unit tests by passing simple dataclasses; with `Protocol`, the mock
doesn't need to inherit from anything.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np

from m6.memory_bus.schemas import AuditRow, CompressedSlot, SlotId


@runtime_checkable
class AuditLog(Protocol):
    """Append-only audit log with tamper-evident hash chain.

    Implementations MUST refuse any UPDATE or DELETE. The chain hash is computed
    as ``SHA-256(prev_hash ‖ payload_hash)`` so a corrupted middle row breaks
    every downstream row.
    """

    def append(
        self,
        slot_id: SlotId,
        event_type: str,
        result: str,
        payload_bytes: bytes,
        requester_acl: int | None = None,
        requester_classification: int | None = None,
    ) -> AuditRow: ...

    def get(self, rowid: int) -> AuditRow | None: ...

    def history(self, slot_id: SlotId) -> list[AuditRow]: ...

    def chain_tip(self) -> bytes | None:
        """SHA-256 of the most recent row's chain_hash, or None if empty."""

    def verify(self) -> bool:
        """Walk the chain end-to-end, return True iff every link is intact."""

    def close(self) -> None: ...


@runtime_checkable
class Scratchpad(Protocol):
    """Active in-process slot store. Ephemeral. TTL'd."""

    def get(self, slot_id: SlotId) -> CompressedSlot | None: ...

    def put(self, slot: CompressedSlot) -> None: ...

    def expire(self) -> int:
        """Drop expired entries; return the number removed."""

    def __len__(self) -> int: ...


@runtime_checkable
class VectorStore(Protocol):
    """FAISS-CPU today, Qdrant tomorrow. Cosine, top-k."""

    dim: int

    def add(self, slot_id: SlotId, embedding: np.ndarray) -> None: ...

    def search(self, query: np.ndarray, k: int) -> list[tuple[SlotId, float]]: ...

    def save(self) -> None: ...

    def reload(self) -> None: ...

    def __len__(self) -> int: ...
