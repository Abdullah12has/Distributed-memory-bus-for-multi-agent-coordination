"""Identity (no-compression) compressor."""

from __future__ import annotations

from m6.compressors import make_compressor
from m6.memory_bus.schemas import Fragment, TagVector


def test_identity_roundtrip() -> None:
    c = make_compressor("none")
    f = Fragment(
        fragment_id="f-0001",
        text="hello world",
        tags=TagVector(acl_mask=0),
    )
    slot = c.compress(f)
    assert slot.ratio == 1.0
    assert c.decompress(slot) == "hello world"
    assert slot.tags == f.tags
