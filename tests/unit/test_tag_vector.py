"""Tag vector semantics: union, classification ordering, ACL membership."""

from __future__ import annotations

import pytest

from m6.memory_bus.schemas import Classification, TagVector


def test_union_preserves_max_classification() -> None:
    a = TagVector(acl_mask=0b1100, classification=Classification.INTERNAL)
    b = TagVector(acl_mask=0b0011, classification=Classification.SECRET)
    out = TagVector.union([a, b])
    assert out.acl_mask == 0b1111
    assert out.classification is Classification.SECRET


def test_grants_to_acl_subset_required() -> None:
    tag = TagVector(acl_mask=0b1100, classification=Classification.PUBLIC)
    # requester missing bit 3 (= 0b0100) is denied.
    assert tag.grants_to(0b1000, Classification.SECRET) is False
    # requester with all bits passes.
    assert tag.grants_to(0b1100, Classification.PUBLIC) is True


def test_grants_to_classification_ordering() -> None:
    tag = TagVector(acl_mask=0, classification=Classification.CONFIDENTIAL)
    assert tag.grants_to(0, Classification.CONFIDENTIAL) is True
    assert tag.grants_to(0, Classification.RESTRICTED) is True
    assert tag.grants_to(0, Classification.INTERNAL) is False


def test_acl_overflow_rejected() -> None:
    with pytest.raises(ValueError, match="uint64"):
        TagVector(acl_mask=2**64)
