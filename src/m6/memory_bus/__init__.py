"""Memory bus reference implementation.

Three pieces:

* :mod:`m6.memory_bus.api` — FastAPI app factory.
* :mod:`m6.memory_bus.service` — business logic (compress → store → audit).
* :mod:`m6.memory_bus.storage` — three storage protocols: audit log,
  scratchpad, vector store. SQLite + in-memory dict + FAISS-CPU today; Postgres
  + Redis + Qdrant tomorrow.

The architectural rationale lives in ``docs/adr/ADR-002-storage-stack.md`` and
``docs/TECHNICAL_REFERENCE.md`` §2.
"""

from m6.memory_bus.schemas import (
    AuditRow,
    CompressedSlot,
    Fragment,
    ReadResponse,
    SlotPayload,
    SubscribeRequest,
    TagVector,
    WriteRequest,
    WriteResponse,
)
from m6.memory_bus.service import MemoryBusService

__all__ = [
    "AuditRow",
    "CompressedSlot",
    "Fragment",
    "MemoryBusService",
    "ReadResponse",
    "SlotPayload",
    "SubscribeRequest",
    "TagVector",
    "WriteRequest",
    "WriteResponse",
]
