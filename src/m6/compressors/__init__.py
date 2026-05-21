"""Compressor framework (C2 + C4).

Public surface:

* :class:`Compressor` — the protocol every variant conforms to.
* :class:`CompressedSlot` — the wire-level result type (re-exported from
  ``m6.memory_bus.schemas`` for convenience).
* :func:`make_compressor` — registry-backed factory.

Concrete variants live in submodules:

* :mod:`m6.compressors.lingua2` — LLMLingua-2 hard-prompt baseline.
* :mod:`m6.compressors.filter`  — instruction-aware filter heuristic.
* :mod:`m6.compressors.icae`    — ICAE-style soft-prompt (the C2 trainable arm).
* :mod:`m6.compressors.tag_preserving` — ICAE + per-slot TagHead (C4).

ADR: ``docs/adr/ADR-001-compressor-architecture.md``.
"""

from __future__ import annotations

from typing import Any

from m6.compressors.base import Compressor, ModelCard
from m6.memory_bus.schemas import CompressedSlot

__all__ = ["CompressedSlot", "Compressor", "ModelCard", "make_compressor"]


def make_compressor(name: str, **kwargs: Any) -> Compressor:
    """Build a compressor by name. Lazy imports so the bus can boot without
    PyTorch/MLX installed (the ``none`` variant is in this very file).
    """
    name = name.lower()
    if name in {"none", "identity"}:
        return _IdentityCompressor()
    if name == "lingua2":
        from m6.compressors.lingua2 import LLMLingua2Compressor

        return LLMLingua2Compressor(**kwargs)
    if name == "filter":
        from m6.compressors.filter import InstructionAwareFilter

        return InstructionAwareFilter(**kwargs)
    if name in {"phi3-extractive", "phi3_extractive", "phi3"}:
        from m6.compressors.phi3_extractive import Phi3ExtractiveCompressor

        return Phi3ExtractiveCompressor(**kwargs)
    msg = f"Unknown compressor: {name!r}. Available: none, lingua2, filter, phi3-extractive"
    raise ValueError(msg)


# --------------------------------------------------------------------------- #
# Identity compressor — the no-compression control condition required by every
# experiment (plan risk register).
# --------------------------------------------------------------------------- #
class _IdentityCompressor:
    """``compressor=none``: returns the source text verbatim as a TextSummary.

    Required by the per-experiment "no-compression control condition" mitigation
    for the AutoGen-runtime-bug risk (plan §7).
    """

    compressor_id: str = "none"
    tokenizer_id: str = "identity"
    target_ratio: float = 1.0

    def compress(
        self,
        fragment: Any,
        target_ratio: float | None = None,  # noqa: ARG002
    ) -> CompressedSlot:
        from m6.memory_bus.schemas import TextSummary
        from m6.utils.io import make_run_id

        return CompressedSlot(
            slot_id=make_run_id("slot"),
            payload=TextSummary(text=fragment.text),
            tags=fragment.tags,
            audit_pointers=(),
            compressor_id=self.compressor_id,
            ratio=1.0,
        )

    def decompress(self, slot: CompressedSlot) -> str:
        from m6.memory_bus.schemas import TextSummary

        if isinstance(slot.payload, TextSummary):
            return slot.payload.text
        return ""

    def embed(self, _slot: CompressedSlot) -> list[float] | None:
        return None

    def model_card(self) -> ModelCard:
        return ModelCard(
            compressor_id=self.compressor_id,
            family="identity",
            base_model=None,
            trained=False,
            training_loss=None,
            target_ratio_default=1.0,
            notes="Identity / no-compression control condition.",
        )
