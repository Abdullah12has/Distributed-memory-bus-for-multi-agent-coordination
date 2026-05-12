"""Storage layer protocols and reference implementations.

Three Protocols, three concrete classes. Swap-in instructions live in
``docs/adr/ADR-002-storage-stack.md``.
"""

from m6.memory_bus.storage.protocols import AuditLog, Scratchpad, VectorStore
from m6.memory_bus.storage.scratchpad import InMemoryScratchpad
from m6.memory_bus.storage.sqlite_audit import SQLiteAuditLog
from m6.memory_bus.storage.vector_store import FaissVectorStore

__all__ = [
    "AuditLog",
    "FaissVectorStore",
    "InMemoryScratchpad",
    "SQLiteAuditLog",
    "Scratchpad",
    "VectorStore",
]
