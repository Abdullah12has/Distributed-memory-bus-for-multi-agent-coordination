"""Instruction-aware filter — heuristic baseline.

Two stages (``docs/TECHNICAL_REFERENCE.md`` §5.4):

1. Sentence-level filter: TF-IDF prune + cross-encoder rerank, keep top-k.
2. Token-level trim: drop stop-words and ≤2-char tokens until the target ratio.

Deterministic given ``(task_hint, fragment, target_ratio)``. No training.
Used as a floor baseline that ICAE must beat by ≥3 pp F1 to justify training.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from m6.compressors.base import ModelCard
from m6.config.logging import get_logger
from m6.memory_bus.schemas import CompressedSlot, Fragment, TextSummary

log = get_logger(__name__)


# A minimal English stop-word list; we deliberately keep it small so this stays
# pure-Python and dependency-free at runtime.
_STOPWORDS = frozenset(
    [
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "have",
        "he",
        "her",
        "him",
        "his",
        "i",
        "if",
        "in",
        "is",
        "it",
        "its",
        "just",
        "my",
        "no",
        "not",
        "of",
        "on",
        "or",
        "so",
        "that",
        "the",
        "their",
        "them",
        "they",
        "this",
        "to",
        "was",
        "we",
        "what",
        "when",
        "where",
        "which",
        "who",
        "will",
        "with",
        "you",
        "your",
    ]
)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_TOKEN_RE = re.compile(r"\w+|[^\w\s]")


class InstructionAwareFilter:
    """Pure-Python heuristic filter."""

    compressor_id: str = "filter"
    tokenizer_id: str = "whitespace+punct"

    def __init__(
        self,
        *,
        target_ratio: float = 4.0,
        rerank_model: str = "BAAI/bge-reranker-base",
        use_reranker: bool = True,
        **_extra: Any,
    ) -> None:
        self.target_ratio = target_ratio
        self.use_reranker = use_reranker
        self._reranker: Any | None = None
        if use_reranker:
            try:
                from sentence_transformers import CrossEncoder

                self._reranker = CrossEncoder(rerank_model, max_length=512)
            except ImportError:  # pragma: no cover — graceful degradation
                log.warning("compressor.filter.no_reranker", reason="sentence-transformers missing")
                self.use_reranker = False
        log.info(
            "compressor.filter.init",
            target_ratio=target_ratio,
            use_reranker=self.use_reranker,
        )

    # ------------------------------------------------------------------ #
    # Compressor protocol
    # ------------------------------------------------------------------ #
    def compress(
        self,
        fragment: Fragment,
        target_ratio: float | None = None,
    ) -> CompressedSlot:
        ratio = target_ratio if target_ratio is not None else self.target_ratio
        compressed = self._filter(fragment.text, fragment.task_hint or "", ratio)
        slot_id = "filter-" + _digest(f"{fragment.fragment_id}|{ratio}|{compressed}")[:16]
        return CompressedSlot(
            slot_id=slot_id,
            payload=TextSummary(text=compressed),
            tags=fragment.tags,
            compressor_id=self.compressor_id,
            ratio=ratio,
        )

    def decompress(self, slot: CompressedSlot) -> str:
        if isinstance(slot.payload, TextSummary):
            return slot.payload.text
        return ""

    def embed(self, _slot: CompressedSlot) -> list[float] | None:
        return None

    def embed_text(self, _text: str) -> list[float] | None:
        return None

    def model_card(self) -> ModelCard:
        return ModelCard(
            compressor_id=self.compressor_id,
            family="filter",
            base_model="BAAI/bge-reranker-base" if self.use_reranker else None,
            trained=False,
            training_loss=None,
            target_ratio_default=self.target_ratio,
            notes="Heuristic 2-stage filter. Floor baseline; ICAE must beat by ≥3pp F1.",
        )

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _filter(self, text: str, task_hint: str, target_ratio: float) -> str:
        # Stage 1: sentence-level. Rank by reranker score (if available),
        # otherwise by lexical overlap with the task hint.
        sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]
        if not sentences:
            return text

        if self.use_reranker and self._reranker is not None and task_hint:
            scores = self._reranker.predict(
                [(task_hint, s) for s in sentences], convert_to_numpy=True
            )
            ranked = sorted(
                zip(sentences, scores, strict=True), key=lambda x: float(x[1]), reverse=True
            )
            sentences_ranked = [s for s, _ in ranked]
        else:
            hint_tokens = {t.lower() for t in _TOKEN_RE.findall(task_hint)}
            sentences_ranked = sorted(
                sentences,
                key=lambda s: -sum(1 for t in _TOKEN_RE.findall(s) if t.lower() in hint_tokens),
            )

        target_chars = int(len(text) / target_ratio)
        keep: list[str] = []
        running = 0
        for s in sentences_ranked:
            if running + len(s) > target_chars and keep:
                break
            keep.append(s)
            running += len(s)

        # Restore original order for readability — important for downstream
        # LLMs that rely on discourse structure.
        order = {s: i for i, s in enumerate(sentences)}
        keep = sorted(keep, key=lambda s: order.get(s, 0))

        # Stage 2: token-level trim to hit ratio.
        # Use whitespace splitting to preserve punctuation attached to words
        # (e.g., "hours:" stays as "hours:", not "hours :").
        joined = " ".join(keep)
        if target_ratio <= 1.0:
            return joined
        words = joined.split()
        source_words = text.split()
        target_word_count = max(int(len(source_words) / target_ratio), 1)
        kept_words: list[str] = []
        for word in words:
            word_lower = word.lower().strip(".,;:!?()[]{}\"'")
            if word_lower in _STOPWORDS or (word_lower.isalpha() and len(word_lower) <= 2):
                continue
            kept_words.append(word)
            if len(kept_words) >= target_word_count:
                break
        # If we over-pruned (very small fragments), fall back to the sentence
        # selection without token-level trim.
        if len(kept_words) < max(target_word_count // 2, 8):
            return joined
        return " ".join(kept_words)


def _digest(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
