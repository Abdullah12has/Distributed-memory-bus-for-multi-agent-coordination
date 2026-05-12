"""TTL'd in-memory scratchpad.

Hot path: ``get`` / ``put`` must be O(1) and lock-free where possible. We accept
a global lock for ``expire`` because expiry is amortised — it runs at most
every ``ttl/4`` seconds.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict

from m6.config.logging import get_logger
from m6.memory_bus.schemas import CompressedSlot, SlotId

log = get_logger(__name__)


class InMemoryScratchpad:
    """LRU + TTL scratchpad.

    ``put`` evicts the oldest entry when ``len > max_size``. ``get`` refreshes
    LRU position. ``expire`` walks the head of the OrderedDict and drops entries
    whose age exceeds ``ttl_seconds``.
    """

    def __init__(self, *, ttl_seconds: int, max_size: int = 100_000) -> None:
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._lock = threading.RLock()
        self._store: OrderedDict[SlotId, tuple[CompressedSlot, float]] = OrderedDict()

    def get(self, slot_id: SlotId) -> CompressedSlot | None:
        now = time.time()
        with self._lock:
            entry = self._store.get(slot_id)
            if entry is None:
                return None
            slot, t = entry
            if now - t > self._ttl:
                # Lazy expiry: drop on read past TTL.
                del self._store[slot_id]
                return None
            self._store.move_to_end(slot_id)
            return slot

    def put(self, slot: CompressedSlot) -> None:
        now = time.time()
        with self._lock:
            self._store[slot.slot_id] = (slot, now)
            self._store.move_to_end(slot.slot_id)
            while len(self._store) > self._max_size:
                evicted_id, _ = self._store.popitem(last=False)
                log.info("scratchpad.evicted", slot_id=evicted_id, reason="lru")

    def expire(self) -> int:
        """Drop expired entries; return count removed."""
        now = time.time()
        removed = 0
        with self._lock:
            # Walk from the head (oldest) until we find one not yet expired.
            for slot_id in list(self._store.keys()):
                _, t = self._store[slot_id]
                if now - t > self._ttl:
                    del self._store[slot_id]
                    removed += 1
                else:
                    break
        if removed:
            log.info("scratchpad.expired", removed=removed)
        return removed

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)
