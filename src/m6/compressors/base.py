"""Compressor protocol and shared dataclasses.

The protocol is intentionally small — four methods. Concrete subclasses are
free to grow private internals. The :class:`ModelCard` dataclass is the lookup
that experiment runners persist into ``manifest.yaml``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from m6.memory_bus.schemas import CompressedSlot, Fragment


@dataclass(frozen=True)
class ModelCard:
    """The structured model-card persisted with every checkpoint.

    Mirror of the canonical fields requested by the HuggingFace hub model-card
    template; sufficient for reproducibility per plan §4.6 Month 10.
    """

    compressor_id: str
    family: str                          # "hard-prompt" / "soft-prompt" / "filter" / "identity"
    base_model: str | None               # e.g. "meta-llama/Llama-3.1-8B-Instruct"
    trained: bool
    training_loss: str | None            # e.g. "L_recon + 0.3*L_NCE"
    target_ratio_default: float
    notes: str = ""
    git_sha: str | None = None
    config_hash: str | None = None


@runtime_checkable
class Compressor(Protocol):
    """The contract every compressor implements.

    See :func:`m6.compressors.make_compressor` for the registry-backed factory
    and ``docs/TECHNICAL_REFERENCE.md`` §5 for the architectural rationale.
    """

    compressor_id: str
    tokenizer_id: str
    target_ratio: float

    def compress(
        self,
        fragment: Fragment,
        target_ratio: float | None = None,
    ) -> CompressedSlot:
        """Compress ``fragment``. ``target_ratio=None`` ⇒ use ``self.target_ratio``."""

    def decompress(self, slot: CompressedSlot) -> str:
        """Return a best-effort text reconstruction. For embedding-only slots
        this MAY return the empty string.
        """

    def embed(self, slot: CompressedSlot) -> list[float] | None:
        """Return an embedding suitable for FAISS indexing, or None."""

    def model_card(self) -> ModelCard: ...
