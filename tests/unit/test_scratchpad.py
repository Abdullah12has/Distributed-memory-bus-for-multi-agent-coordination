"""Scratchpad TTL + LRU."""

from __future__ import annotations

import time

from m6.memory_bus.schemas import CompressedSlot, TagVector, TextSummary
from m6.memory_bus.storage.scratchpad import InMemoryScratchpad


def _make_slot(i: int) -> CompressedSlot:
    return CompressedSlot(
        slot_id=f"slot-{i:08d}",
        payload=TextSummary(text=f"hello-{i}"),
        tags=TagVector(acl_mask=0),
        compressor_id="none",
        ratio=1.0,
    )


def test_put_get_roundtrip() -> None:
    s = InMemoryScratchpad(ttl_seconds=60, max_size=128)
    slot = _make_slot(1)
    s.put(slot)
    got = s.get(slot.slot_id)
    assert got is not None
    assert got.slot_id == slot.slot_id


def test_lru_eviction() -> None:
    s = InMemoryScratchpad(ttl_seconds=60, max_size=2)
    s.put(_make_slot(1))
    s.put(_make_slot(2))
    s.put(_make_slot(3))
    assert len(s) == 2
    assert s.get("slot-00000001") is None


def test_ttl_expiry() -> None:
    s = InMemoryScratchpad(ttl_seconds=0, max_size=10)
    s.put(_make_slot(1))
    time.sleep(0.01)
    assert s.get("slot-00000001") is None
