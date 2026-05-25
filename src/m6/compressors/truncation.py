"""Truncation baseline — naive first-N-tokens compression.

The simplest possible compression strategy: keep the first N tokens
(by whitespace splitting) and discard the rest. Included as a mandatory
lower-bound baseline; every NeurIPS/ICLR compression paper tests against
truncation to show that intelligent token selection (LLMLingua-2, Selective
Context, etc.) outperforms naive prefix retention.

Usage:
    comp = TruncationCompressor(target_ratio=4.0)
    slot = comp.compress(fragment)
"""

from __future__ import annotations

import hashlib
from typing import Any

from m6.compressors.base import ModelCard
from m6.memory_bus.schemas import CompressedSlot, Fragment, TextSummary


class TruncationCompressor:
    """Keep the first 1/ratio fraction of tokens. No intelligence."""

    compressor_id: str = "truncation"
    tokenizer_id: str = "whitespace"

    def __init__(self, *, target_ratio: float = 4.0, **_extra: Any) -> None:
        self.target_ratio = target_ratio

    def compress(
        self, fragment: Fragment, target_ratio: float | None = None
    ) -> CompressedSlot:
        ratio = target_ratio if target_ratio is not None else self.target_ratio
        tokens = fragment.text.split()
        keep = max(1, int(len(tokens) / max(ratio, 1.0)))
        text = " ".join(tokens[:keep])
        actual_ratio = len(fragment.text) / max(len(text), 1)
        digest = hashlib.sha256(f"{fragment.fragment_id}|trunc|{ratio}".encode()).hexdigest()[:16]
        return CompressedSlot(
            slot_id=f"trunc-{digest}",
            payload=TextSummary(text=text),
            tags=fragment.tags,
            audit_pointers=(),
            compressor_id=self.compressor_id,
            ratio=max(actual_ratio, 1.0),
        )

    def decompress(self, slot: CompressedSlot) -> str:
        if isinstance(slot.payload, TextSummary):
            return slot.payload.text
        return ""

    def embed(self, _slot: CompressedSlot) -> list[float] | None:
        return None

    def model_card(self) -> ModelCard:
        return ModelCard(
            compressor_id=self.compressor_id,
            family="baseline",
            base_model=None,
            trained=False,
            training_loss=None,
            target_ratio_default=self.target_ratio,
            notes="Truncation baseline: keep first N tokens. Lower bound for intelligent compression.",
        )
