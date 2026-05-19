"""LLMLingua-2 hard-prompt baseline.

Thin adapter around the upstream :mod:`llmlingua` Python package
(Pan et al., ACL Findings 2024). XLM-RoBERTa-based token classifier, runs
natively on MPS.

Calibration target (plan §4.1): NarrativeQA F1 within 2 pp, HotpotQA F1 within
3 pp. Failure to hit this is a Month-1 stop-the-line event.
"""

from __future__ import annotations

import hashlib
from typing import Any

from m6.compressors.base import ModelCard
from m6.config.logging import get_logger
from m6.memory_bus.schemas import CompressedSlot, Fragment, TextSummary

log = get_logger(__name__)


class LLMLingua2Compressor:
    """Wraps :class:`llmlingua.PromptCompressor` in the project's Protocol."""

    compressor_id: str = "lingua2"
    tokenizer_id: str = "xlm-roberta-base"

    DEFAULT_FORCE_TOKENS: tuple[str, ...] = ("\n", ".", "!", "?")

    def __init__(
        self,
        *,
        model_name: str = "microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
        target_ratio: float = 4.0,
        device: str = "auto",
        force_tokens: tuple[str, ...] | None = None,
        **_extra: Any,
    ) -> None:
        from llmlingua import PromptCompressor  # type: ignore[import-not-found]

        self.model_name = model_name
        self.target_ratio = target_ratio
        # Resolve "auto" ourselves rather than letting llmlingua/transformers
        # default to "cuda" — on Apple Silicon they'll crash with
        # "Torch not compiled with CUDA enabled" because the cpu-only torch
        # wheel is installed. Preference order: explicit > CUDA > MPS > CPU.
        resolved_device = self._resolve_device(device)
        self.device = resolved_device
        kwargs: dict[str, Any] = {
            "model_name": model_name,
            "use_llmlingua2": True,
            "device_map": resolved_device,
        }
        self._inner = PromptCompressor(**kwargs)
        log.info("compressor.lingua2.device", requested=device, resolved=resolved_device)

        # Validate force_tokens against the wrapped tokenizer's vocab. The
        # default ("\n", ".", "!", "?") are not guaranteed to be in every
        # XLM-RoBERTa variant's vocab; passing an unknown force-token to
        # llmlingua silently degrades compression. Drop missing ones, warn.
        requested = tuple(force_tokens or self.DEFAULT_FORCE_TOKENS)
        self._force_tokens = self._filter_force_tokens(requested)
        log.info(
            "compressor.lingua2.init",
            model=model_name,
            target_ratio=target_ratio,
            force_tokens=self._force_tokens,
            dropped=tuple(set(requested) - set(self._force_tokens)),
        )

    @staticmethod
    def _resolve_device(requested: str) -> str:
        """Map ``device="auto"`` to a concrete device that PyTorch can actually use.

        The default behaviour of ``transformers`` and ``llmlingua`` is to pick
        ``cuda`` when ``device_map`` is unset, which crashes on Apple Silicon
        builds of PyTorch (no CUDA compiled in). We resolve explicitly:

        * If the caller passed anything other than ``"auto"``, use it as-is.
        * Else prefer CUDA if available, then MPS, else CPU.
        """
        if requested != "auto":
            return requested
        try:
            import torch

            if torch.cuda.is_available():
                return "cuda"
            if (
                getattr(torch.backends, "mps", None) is not None
                and torch.backends.mps.is_available()
            ):
                return "mps"
        except ImportError:  # pragma: no cover - torch is a hard dep
            pass
        return "cpu"

    def _filter_force_tokens(self, requested: tuple[str, ...]) -> tuple[str, ...]:
        """Return only those force-tokens present in the wrapped tokenizer's vocab.

        We try the upstream object's ``tokenizer`` attribute first (the standard
        ``llmlingua`` field name); fall back to returning the request unchanged
        if the attribute is missing — better to over-include than to silently
        drop everything.
        """
        tok = getattr(self._inner, "tokenizer", None)
        if tok is None or not hasattr(tok, "get_vocab"):
            return requested
        vocab = tok.get_vocab()
        return tuple(t for t in requested if t in vocab)

    def compress(
        self,
        fragment: Fragment,
        target_ratio: float | None = None,
    ) -> CompressedSlot:
        ratio = target_ratio if target_ratio is not None else self.target_ratio
        # llmlingua expects the *retention* rate (∈ [0, 1]), not the compression ratio.
        rate = max(min(1.0 / ratio, 1.0), 0.05)
        out = self._inner.compress_prompt(
            fragment.text,
            instruction=fragment.task_hint or "",
            question=fragment.task_hint or "",
            rate=rate,
            force_tokens=list(self._force_tokens),
        )
        compressed_text: str = out["compressed_prompt"]
        slot_id = _digest(f"{fragment.fragment_id}|{ratio}|{compressed_text}")
        return CompressedSlot(
            slot_id=f"lingua2-{slot_id[:16]}",
            payload=TextSummary(text=compressed_text),
            tags=fragment.tags,
            compressor_id=self.compressor_id,
            ratio=ratio,
        )

    def decompress(self, slot: CompressedSlot) -> str:
        if isinstance(slot.payload, TextSummary):
            return slot.payload.text
        return ""

    def embed(self, slot: CompressedSlot) -> list[float] | None:  # noqa: ARG002
        # LLMLingua-2 is a token filter; we have no native embedding for the
        # output. The bus's vector store path is therefore unused for this
        # compressor — RAG pipelines re-embed the compressed text via a
        # dedicated embedder.
        return None

    def embed_text(self, text: str) -> list[float] | None:  # noqa: ARG002
        return None

    def model_card(self) -> ModelCard:
        return ModelCard(
            compressor_id=self.compressor_id,
            family="hard-prompt",
            base_model=self.model_name,
            trained=False,
            training_loss=None,
            target_ratio_default=self.target_ratio,
            notes=(
                "LLMLingua-2 (Pan et al., ACL Findings 2024). Token-level "
                "classifier; XLM-RoBERTa-based. Calibration target: "
                "NarrativeQA ±2pp, HotpotQA ±3pp per plan §4.1."
            ),
        )


def _digest(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
