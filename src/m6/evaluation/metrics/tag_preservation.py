"""Tag-preservation metric for H5.

Defined in ``docs/HYPOTHESIS_IMPLEMENTATION_PLAN.md`` (H5):

A fragment's tag is "preserved" iff:
* ``acl_recovered ⊇ acl_true``  *OR*
* ``popcount(acl_recovered ∩ acl_true) / popcount(acl_true) ≥ 0.9``
* AND ``class_recovered ≥ class_true`` (lattice ordering).
"""

from __future__ import annotations

from dataclasses import dataclass

from m6.memory_bus.schemas import TagVector


@dataclass(frozen=True)
class PreservationCounts:
    n_total: int
    n_preserved: int
    n_acl_preserved: int
    n_class_preserved: int

    @property
    def rate(self) -> float:
        return 0.0 if self.n_total == 0 else self.n_preserved / self.n_total

    @property
    def acl_rate(self) -> float:
        return 0.0 if self.n_total == 0 else self.n_acl_preserved / self.n_total

    @property
    def class_rate(self) -> float:
        return 0.0 if self.n_total == 0 else self.n_class_preserved / self.n_total


def preservation_rate(
    true_tags: list[TagVector],
    recovered_tags: list[TagVector],
    *,
    acl_overlap_threshold: float = 0.9,
) -> PreservationCounts:
    """Return the H5 preservation rates.

    Args:
        true_tags: ground-truth tags from the source fragment.
        recovered_tags: tags recovered from the compressed slot.
        acl_overlap_threshold: fraction of true ACL bits that must be in the
            recovered ACL bits. Default 0.9 per plan §3 H5.
    """
    if len(true_tags) != len(recovered_tags):
        msg = f"length mismatch: {len(true_tags)} vs {len(recovered_tags)}"
        raise ValueError(msg)

    n_preserved = n_acl = n_class = 0
    for t, r in zip(true_tags, recovered_tags, strict=True):
        acl_pres = _acl_preserved(t.acl_mask, r.acl_mask, acl_overlap_threshold)
        cls_pres = int(r.classification) >= int(t.classification)
        if acl_pres:
            n_acl += 1
        if cls_pres:
            n_class += 1
        if acl_pres and cls_pres:
            n_preserved += 1
    return PreservationCounts(
        n_total=len(true_tags),
        n_preserved=n_preserved,
        n_acl_preserved=n_acl,
        n_class_preserved=n_class,
    )


def _acl_preserved(true_acl: int, rec_acl: int, threshold: float) -> bool:
    if true_acl == 0:
        # Vacuously preserved when there are no true bits to preserve.
        return True
    if (rec_acl & true_acl) == true_acl:
        return True
    intersect_popcount = bin(rec_acl & true_acl).count("1")
    true_popcount = bin(true_acl).count("1")
    return intersect_popcount / true_popcount >= threshold
