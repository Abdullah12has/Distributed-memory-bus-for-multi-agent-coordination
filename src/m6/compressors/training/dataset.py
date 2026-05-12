"""Training dataset loaders.

Two flavours used by H3 (training distribution):

* :class:`QADataset` — ``(question, source, answer)`` triples. Source is the
  fragment to compress.
* :class:`DialogueDataset` — planner-worker-critic dialogue traces; each
  example provides a list of fragments observed by the agents during a
  workflow. Used to construct "same-trace" positive pairs for the InfoNCE term.

Both produce a uniform ``TrainingExample`` dataclass so the trainer is agnostic
to the source distribution.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from m6.utils.io import read_jsonl


@dataclass(frozen=True)
class TrainingExample:
    """One step of the dual-objective loss."""

    anchor_text: str
    positive_text: str
    target_text: str
    # Optional: tags used by the C4 tag-loss term.
    acl_mask: int = 0
    classification: int = 0


class QADataset(Sequence[TrainingExample]):
    """``(question, context, answer)`` triples.

    Default positive pair: anchor=context, positive=question (both about the
    same fact). Reconstruction target = context.
    """

    def __init__(self, jsonl_path: Path | str) -> None:
        self.path = Path(jsonl_path)
        self.rows = read_jsonl(self.path)

    def __getitem__(self, idx: int) -> TrainingExample:  # type: ignore[override]
        r = self.rows[idx]
        return TrainingExample(
            anchor_text=r["context"],
            positive_text=r.get("question", r["context"]),
            target_text=r["context"],
            acl_mask=int(r.get("acl_mask", 0)),
            classification=int(r.get("classification", 0)),
        )

    def __len__(self) -> int:
        return len(self.rows)


class DialogueDataset(Sequence[TrainingExample]):
    """Planner-worker-critic dialogue traces.

    Each row is::

        {
            "trace_id": "...",
            "fragments": [
                {"text": "...", "role": "planner|worker|critic", "tags": {...}},
                ...
            ]
        }

    Positive pairs are sampled from within the same trace (different fragments).
    Reconstruction target is the same fragment.
    """

    def __init__(self, jsonl_path: Path | str, *, seed: int = 0) -> None:
        import random

        self.path = Path(jsonl_path)
        self.rows = read_jsonl(self.path)
        self.rng = random.Random(seed)
        # Pre-pair so __getitem__ is deterministic given the seed.
        self._pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for row in self.rows:
            frags = row.get("fragments", [])
            if len(frags) < 2:
                continue
            for i, frag in enumerate(frags):
                other = self.rng.choice(frags[:i] + frags[i + 1 :])
                self._pairs.append((frag, other))

    def __getitem__(self, idx: int) -> TrainingExample:  # type: ignore[override]
        anchor, positive = self._pairs[idx]
        tags = anchor.get("tags", {}) or {}
        return TrainingExample(
            anchor_text=anchor["text"],
            positive_text=positive["text"],
            target_text=anchor["text"],
            acl_mask=int(tags.get("acl_mask", 0)),
            classification=int(tags.get("classification", 0)),
        )

    def __len__(self) -> int:
        return len(self._pairs)

    def __iter__(self) -> Iterator[TrainingExample]:
        for i in range(len(self)):
            yield self[i]
