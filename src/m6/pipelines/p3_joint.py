"""P3 — joint, conditional compression on retrieval relevance.

The router uses the retriever's similarity score to decide whether to compress.
Hybrid of P1 and P2: high-relevance hits stay verbatim, mid-relevance hits are
compressed, low-relevance hits are dropped.

Reference: ``docs/TECHNICAL_REFERENCE.md`` §7.3. Direct structural analogue of
Guo et al. *Dynamic context compression for RAG* (2025).
"""

from __future__ import annotations

from dataclasses import dataclass

from m6.compressors.base import Compressor
from m6.memory_bus.schemas import Fragment, TextSummary
from m6.pipelines.retriever import InMemoryRetriever, RetrievedDoc, Retriever


@dataclass
class Pipeline3:
    """Joint retrieve+compress with score-conditional routing."""

    compressor: Compressor
    retriever: Retriever | None = None
    target_ratio: float = 4.0
    theta_high: float = 0.75
    theta_low: float = 0.45

    def __post_init__(self) -> None:
        if self.retriever is None:
            self.retriever = InMemoryRetriever()
        self._built = False

    def build(self, corpus: list[Fragment]) -> None:
        assert self.retriever is not None
        self.retriever.index(corpus)
        self._built = True

    def query(self, q: str, k: int = 10) -> list[RetrievedDoc]:
        if not self._built:
            msg = "Call build(corpus) before query()."
            raise RuntimeError(msg)
        assert self.retriever is not None
        raw = self.retriever.search(q, k=k)
        out: list[RetrievedDoc] = []
        for d in raw:
            if d.score >= self.theta_high:
                # Verbatim
                out.append(d)
            elif d.score >= self.theta_low:
                # Compress
                slot = self.compressor.compress(
                    d.fragment.model_copy(update={"task_hint": q}),
                    target_ratio=self.target_ratio,
                )
                text = (
                    slot.payload.text
                    if isinstance(slot.payload, TextSummary)
                    else self.compressor.decompress(slot) or d.fragment.text
                )
                out.append(
                    RetrievedDoc(
                        fragment=d.fragment.model_copy(update={"text": text}),
                        score=d.score,
                    )
                )
            else:
                # Drop
                continue
        return out
