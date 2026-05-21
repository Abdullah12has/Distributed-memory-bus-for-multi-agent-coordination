"""ICAE-style soft-prompt compressor (C2 trainable arm).

Architecture (``docs/TECHNICAL_REFERENCE.md`` §5.2):

* Encoder: ``Llama-3.1-8B-Instruct``, LoRA-adapted.
* Decoder: same backbone, **frozen**.
* Memory slots: ``M`` learnable ``[MEM]`` tokens prepended to the encoder
  input. Default ``M = 128`` ⇒ ~4× ratio on 512-token fragments.
* Loss: ``L_recon + λ · L_NCE`` (plan §2.2).

This module deliberately ships in **two modes**:

1. **Trained mode** — when ``checkpoint_path`` exists and PyTorch+PEFT are
   installed, real LoRA adapters are loaded and used for compression.
2. **Inference-stub mode** — when no checkpoint exists, the compressor emits
   a deterministic embedding derived from a stable hash of the fragment. This
   lets the *system* be exercised end-to-end (bus, scratchpad, vector store,
   experiment runners) before the trainer has produced weights, and prevents
   ``import m6.compressors.icae`` from failing on a fresh checkout.

The training script lives in :mod:`m6.compressors.training.train_icae`.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from m6.compressors.base import ModelCard
from m6.config.logging import get_logger
from m6.memory_bus.schemas import CompressedSlot, Fragment, SoftEmbed

if TYPE_CHECKING:  # pragma: no cover - optional imports
    from peft import PeftModel
    from transformers import AutoTokenizer

log = get_logger(__name__)

DEFAULT_BASE_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
DEFAULT_NUM_SLOTS = 128
DEFAULT_D_MODEL = 4096  # Llama-3.1-8B hidden size
DEFAULT_TARGET_RATIO = 4.0


class ICAECompressor:
    """ICAE-style soft-prompt compressor.

    Falls back to a deterministic-hash stub when no checkpoint is configured;
    this keeps integration tests fast and the bus runnable on a fresh clone.
    """

    compressor_id: str = "icae"
    tokenizer_id: str = "llama-3.1"

    def __init__(
        self,
        *,
        base_model: str = DEFAULT_BASE_MODEL,
        checkpoint_path: str | os.PathLike[str] | None = None,
        target_ratio: float = DEFAULT_TARGET_RATIO,
        num_slots: int = DEFAULT_NUM_SLOTS,
        d_model: int = DEFAULT_D_MODEL,
        max_input_tokens: int = 2048,
        device: str | None = None,
        **_extra: Any,
    ) -> None:
        self.base_model = base_model
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else None
        self.target_ratio = target_ratio
        self.num_slots = num_slots
        self.d_model = d_model
        self.max_input_tokens = max_input_tokens
        self.device = device
        self._encoder: PeftModel | None = None
        self._tokenizer: AutoTokenizer | None = None

        self._mode: str = "stub"
        if self.checkpoint_path is not None and self.checkpoint_path.exists():
            try:
                self._lazy_load_torch()
                self._mode = "trained"
                log.info(
                    "compressor.icae.init",
                    mode=self._mode,
                    base_model=base_model,
                    checkpoint=str(self.checkpoint_path),
                )
            except Exception as e:  # pragma: no cover - environment-specific
                log.warning(
                    "compressor.icae.fallback_stub",
                    reason=str(e),
                    checkpoint=str(self.checkpoint_path),
                    action=(
                        "ICAE will produce deterministic-hash embeddings, NOT "
                        "real compressed representations. Train via "
                        "`make train-icae` before relying on these results."
                    ),
                )
                self._mode = "stub"
        else:
            # Stub mode is a development convenience but is easy to miss when
            # an experiment relies on a trained checkpoint. Surface it at
            # WARNING level with the resolution path.
            log.warning(
                "compressor.icae.stub_mode_active",
                base_model=base_model,
                checkpoint=str(self.checkpoint_path) if self.checkpoint_path else None,
                action=(
                    "ICAE will produce deterministic-hash embeddings, NOT "
                    "real compressed representations. Set `checkpoint_path` "
                    "to a trained adapter, or train via `make train-icae` "
                    "(plan §4.3, ~3 days on M4 Pro)."
                ),
            )

    def is_trained(self) -> bool:
        """True iff a real LoRA checkpoint is loaded; False if stub-mode."""
        return self._mode == "trained"

    # ------------------------------------------------------------------ #
    # Compressor protocol
    # ------------------------------------------------------------------ #
    def compress(
        self,
        fragment: Fragment,
        target_ratio: float | None = None,
    ) -> CompressedSlot:
        ratio = target_ratio if target_ratio is not None else self.target_ratio
        num_slots = max(int(self.num_slots / max(ratio / self.target_ratio, 1.0)), 4)

        if self._mode == "trained":
            arr = self._encode_trained(fragment.text, num_slots)
        else:
            arr = self._encode_stub(fragment.text, num_slots)

        payload = SoftEmbed.from_ndarray(arr)
        slot_id = "icae-" + _digest(f"{fragment.fragment_id}|{ratio}|{num_slots}")[:16]
        return CompressedSlot(
            slot_id=slot_id,
            payload=payload,
            tags=fragment.tags,
            compressor_id=self.compressor_id,
            ratio=ratio,
        )

    def decompress(self, _slot: CompressedSlot) -> str:
        # Soft-prompt compressors do not roundtrip to text deterministically.
        # The trained mode could synthesise an approximate reconstruction via
        # the frozen decoder; we leave that to evaluation code that wants it.
        return ""

    def embed(self, slot: CompressedSlot) -> list[float] | None:
        """Mean-pool the slot embeddings into a single 1D vector for FAISS."""
        if not isinstance(slot.payload, SoftEmbed):
            return None
        arr = slot.payload.as_ndarray()
        return arr.mean(axis=0).astype(np.float32).tolist()  # type: ignore[no-any-return]

    def embed_text(self, text: str) -> list[float] | None:
        """Embed a free-form query string for ``/v1/subscribe`` searches."""
        arr = (
            self._encode_stub(text, self.num_slots)
            if self._mode == "stub"
            else self._encode_trained(text, self.num_slots)
        )
        return arr.mean(axis=0).astype(np.float32).tolist()  # type: ignore[no-any-return]

    def model_card(self) -> ModelCard:
        return ModelCard(
            compressor_id=self.compressor_id,
            family="soft-prompt",
            base_model=self.base_model,
            trained=self._mode == "trained",
            training_loss="L_recon + λ·L_NCE (plan §2.2)",
            target_ratio_default=self.target_ratio,
            notes=(
                "ICAE-style soft-prompt (Ge et al. ICLR 2024). LoRA-adapted "
                "encoder, frozen decoder. Dual-objective trainer in "
                "m6.compressors.training.train_icae. Stub-mode when no "
                "checkpoint is loaded — useful for end-to-end tests."
            ),
        )

    # ------------------------------------------------------------------ #
    # Backends
    # ------------------------------------------------------------------ #
    def _encode_stub(self, text: str, num_slots: int) -> np.ndarray:
        """Deterministic-hash stub. Same input ⇒ same vectors.

        Used in two situations:
        * Local dev before any checkpoint is trained.
        * CI, so tests don't need GPU.
        Embeddings are sampled from N(0, 1) with a seed derived from
        SHA-256(``text``) so they are reproducible.
        """
        seed = int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")
        rng = np.random.default_rng(seed)
        return rng.standard_normal((num_slots, self.d_model)).astype(np.float32)

    def _encode_trained(self, text: str, num_slots: int) -> np.ndarray:
        """Real ICAE forward pass — encoder produces ``num_slots`` memory embeddings.

        Only invoked when a checkpoint was loaded in ``__init__``.
        """
        assert self._encoder is not None
        assert self._tokenizer is not None
        import torch

        with torch.inference_mode():
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_input_tokens,
                add_special_tokens=True,
            )
            inputs = {k: v.to(self._encoder.device) for k, v in inputs.items()}
            # The trainer side adds learned [MEM] tokens at the *end* of the input
            # (a common ICAE convention). Their hidden states are the memory.
            # When we run inference, we replicate that by appending ``num_slots``
            # MEM-token positions and slicing them off.
            mem_token_id = self._tokenizer.convert_tokens_to_ids("[MEM]")
            if mem_token_id == self._tokenizer.unk_token_id:
                # Fallback for tokenizers without an explicit MEM token: use
                # the BOS token as the placeholder; the LoRA adapter is what
                # gives these positions their compressing behaviour.
                mem_token_id = self._tokenizer.bos_token_id
            mem_ids = torch.full(
                (1, num_slots),
                int(mem_token_id),
                dtype=inputs["input_ids"].dtype,
                device=inputs["input_ids"].device,
            )
            input_ids = torch.cat([inputs["input_ids"], mem_ids], dim=1)
            attention_mask = torch.cat([inputs["attention_mask"], torch.ones_like(mem_ids)], dim=1)
            out = self._encoder(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True,
                return_dict=True,
            )
            # Last hidden layer, last `num_slots` positions are the compressed memory.
            hidden = out.hidden_states[-1][0, -num_slots:, :]
            return hidden.detach().to(torch.float32).cpu().numpy()

    def _lazy_load_torch(self) -> None:  # pragma: no cover — environment-specific
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer

        log.info("compressor.icae.loading_checkpoint", path=str(self.checkpoint_path))
        self._tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token
        # The training script adds a [MEM] special token; we must do the same
        # before loading the checkpoint so the embedding matrix shapes match.
        if "[MEM]" not in self._tokenizer.get_vocab():
            self._tokenizer.add_special_tokens({"additional_special_tokens": ["[MEM]"]})
        device_map = self.device or (
            "cuda"
            if torch.cuda.is_available()
            else "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )
        base = AutoModelForCausalLM.from_pretrained(
            self.base_model, torch_dtype=torch.float16, device_map=device_map
        )
        base.resize_token_embeddings(len(self._tokenizer))
        self._encoder = PeftModel.from_pretrained(base, str(self.checkpoint_path))
        self._encoder.eval()


def _digest(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
