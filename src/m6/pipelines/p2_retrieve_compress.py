"""P2 — retrieve→compress.

The classical LongLLMLingua setup. The corpus is indexed in full; the
compressor runs as a post-retrieval node-processor over the top-k results
before they are handed to the synthesiser.

Reference: ``docs/TECHNICAL_REFERENCE.md`` §7.2.
"""

from __future__ import annotations

from dataclasses import dataclass

from m6.compressors.base import Compressor
from m6.memory_bus.schemas import Fragment, TextSummary
from m6.pipelines.retriever import InMemoryRetriever, RetrievedDoc, Retriever


@dataclass
class Pipeline2:
    """retrieve→compress."""

    compressor: Compressor
    retriever: Retriever | None = None
    target_ratio: float = 4.0

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
            slot = self.compressor.compress(
                d.fragment.model_copy(update={"task_hint": q}),
                target_ratio=self.target_ratio,
            )
            if isinstance(slot.payload, TextSummary):
                compressed_text = slot.payload.text
            else:
                compressed_text = self.compressor.decompress(slot) or d.fragment.text
            out.append(
                RetrievedDoc(
                    fragment=d.fragment.model_copy(update={"text": compressed_text}),
                    score=d.score,
                )
            )
        return out
