"""Tag preservation metric."""

from __future__ import annotations

from m6.evaluation.metrics.tag_preservation import preservation_rate
from m6.memory_bus.schemas import Classification, TagVector


def test_perfect_preservation() -> None:
    a = TagVector(acl_mask=0b1010, classification=Classification.INTERNAL)
    out = preservation_rate([a], [a])
    assert out.rate == 1.0


def test_acl_superset_acceptable() -> None:
    truth = TagVector(acl_mask=0b1010, classification=Classification.INTERNAL)
    recovered = TagVector(acl_mask=0b1111, classification=Classification.INTERNAL)
    out = preservation_rate([truth], [recovered])
    assert out.rate == 1.0


def test_class_below_truth_breaks_preservation() -> None:
    truth = TagVector(acl_mask=0, classification=Classification.CONFIDENTIAL)
    rec = TagVector(acl_mask=0, classification=Classification.INTERNAL)
    out = preservation_rate([truth], [rec])
    assert out.rate == 0.0
    assert out.class_rate == 0.0


def test_partial_acl_overlap_above_threshold() -> None:
    truth = TagVector(acl_mask=0b1111_1111_1111, classification=Classification.PUBLIC)  # 12 bits
    rec_high = TagVector(acl_mask=0b1111_1111_1110, classification=Classification.PUBLIC)  # 11 of 12
    out = preservation_rate([truth], [rec_high])
    # 11/12 ≈ 0.917 ≥ 0.9 ⇒ preserved.
    assert out.rate == 1.0
