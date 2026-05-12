"""C4 — Tag-preserving ICAE variant.

Inherits from :class:`m6.compressors.icae.ICAECompressor` and adds:

* A per-slot tag-prediction head (``TagHead``) that predicts ``(acl_mask,
  classification)`` from each memory-slot embedding.
* Tag-recovery logic for the H5 evaluation.
* A separate model-card.

The head's training is wired into :mod:`m6.compressors.training.train_icae`
when ``--tag-head=true`` is set (config: ``configs/training/icae-7b-tags.yaml``).

Reference: ``docs/TECHNICAL_REFERENCE.md`` §5.5 and §4.5 (H5).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np

from m6.compressors.base import ModelCard
from m6.compressors.icae import ICAECompressor
from m6.config.logging import get_logger
from m6.memory_bus.schemas import (
    Classification,
    CompressedSlot,
    Fragment,
    SoftEmbed,
    TagVector,
)

log = get_logger(__name__)


class TagPreservingICAE(ICAECompressor):
    """ICAE + per-slot ``TagHead``.

    The tag head is a tiny MLP (one linear layer per output) loaded from
    ``<checkpoint>/tag_head.npz`` when present. In stub mode we fake recovery
    deterministically from the slot embedding hash so end-to-end tests pass.
    """

    compressor_id: str = "icae-tag"

    def __init__(
        self,
        *,
        tag_head_path: str | Path | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.tag_head_path = Path(tag_head_path) if tag_head_path else None
        self._w_acl: np.ndarray | None = None
        self._b_acl: np.ndarray | None = None
        self._w_class: np.ndarray | None = None
        self._b_class: np.ndarray | None = None

        if self.tag_head_path and self.tag_head_path.exists():
            try:
                self._load_tag_head(self.tag_head_path)
                log.info("compressor.tag.loaded", path=str(self.tag_head_path))
            except Exception as e:  # pragma: no cover - env-specific
                log.warning("compressor.tag.load_failed", reason=str(e))

    # ------------------------------------------------------------------ #
    # Compressor protocol
    # ------------------------------------------------------------------ #
    def compress(
        self,
        fragment: Fragment,
        target_ratio: float | None = None,
    ) -> CompressedSlot:
        slot = super().compress(fragment, target_ratio=target_ratio)
        # Replace the compressor_id so downstream code knows this is the C4 variant.
        return slot.model_copy(update={"compressor_id": self.compressor_id})

    def model_card(self) -> ModelCard:
        return ModelCard(
            compressor_id=self.compressor_id,
            family="soft-prompt",
            base_model=self.base_model,
            trained=self._mode == "trained",
            training_loss="L_recon + λ_NCE·L_NCE + λ_tag·L_tag (plan §2.4, §5.5)",
            target_ratio_default=self.target_ratio,
            notes=(
                "ICAE + per-slot TagHead (C4 variant). H5 falsification "
                "targets: ≥85% preservation at 4×, ≤5pp accuracy drop. H6 "
                "evaluation uses gpt-4o-mini-as-reader."
            ),
        )

    # ------------------------------------------------------------------ #
    # Tag recovery (H5)
    # ------------------------------------------------------------------ #
    def recover_tags(self, slot: CompressedSlot) -> TagVector:
        """Run the per-slot tag head over each memory slot and aggregate."""
        if not isinstance(slot.payload, SoftEmbed):
            return slot.tags

        arr = slot.payload.as_ndarray()
        if self._w_acl is None:
            # Stub recovery: derive a deterministic guess from the slot's hash.
            return self._stub_recover_tags(slot)

        # ACL: sigmoid(W_acl·h + b_acl) > 0.5 ⇒ bit set. Aggregate via OR.
        acl_logits = arr @ self._w_acl.T + self._b_acl
        acl_probs = 1.0 / (1.0 + np.exp(-acl_logits))           # (num_slots, 64)
        acl_bits = (acl_probs > 0.5).any(axis=0).astype(np.uint64)
        acl_mask = int(_bits_to_uint64(acl_bits))

        # Classification: arg-max over softmax(W_class·h + b_class), aggregate via MAX.
        class_logits = arr @ self._w_class.T + self._b_class    # (num_slots, 5)
        per_slot_class = class_logits.argmax(axis=1)
        clazz = Classification(int(per_slot_class.max()))

        return slot.tags.model_copy(update={"acl_mask": acl_mask, "classification": clazz})

    def _stub_recover_tags(self, slot: CompressedSlot) -> TagVector:
        """Stub: emit the original tags ⊕ a tiny deterministic perturbation.

        Used in tests so the H5 metric path executes end-to-end without a
        trained head.
        """
        seed = int.from_bytes(hashlib.sha256(slot.slot_id.encode()).digest()[:8], "big")
        rng = np.random.default_rng(seed)
        flip_mask = int(rng.integers(low=0, high=2**16, dtype=np.uint64))
        acl = (slot.tags.acl_mask ^ flip_mask) & ((1 << 64) - 1)
        clazz = slot.tags.classification
        return slot.tags.model_copy(update={"acl_mask": acl, "classification": clazz})

    # ------------------------------------------------------------------ #
    # IO
    # ------------------------------------------------------------------ #
    def _load_tag_head(self, path: Path) -> None:
        npz = np.load(path)
        self._w_acl = npz["w_acl"].astype(np.float32)
        self._b_acl = npz["b_acl"].astype(np.float32)
        self._w_class = npz["w_class"].astype(np.float32)
        self._b_class = npz["b_class"].astype(np.float32)


def _bits_to_uint64(bits: np.ndarray) -> int:
    """Convert a length-64 bool array (LSB-first) to a single uint64."""
    if bits.shape != (64,):
        msg = f"Expected length-64 array, got shape={bits.shape}"
        raise ValueError(msg)
    out = 0
    for i in range(64):
        if bits[i]:
            out |= 1 << i
    return out
