"""P1 — compress→retrieve.

Storage-bounded regime. The corpus is compressed *before* it is indexed; the
FAISS index stores the compressed chunks. Retrieval and synthesis operate on
the compressed text.

Reference: ``docs/TECHNICAL_REFERENCE.md`` §7.1.
"""

from __future__ import annotations

from dataclasses import dataclass

from m6.compressors.base import Compressor
from m6.memory_bus.schemas import Fragment, TextSummary
from m6.pipelines.retriever import InMemoryRetriever, RetrievedDoc, Retriever


@dataclass
class Pipeline1:
    """compress→retrieve.

    Constructor accepts a :class:`Compressor` and an optional :class:`Retriever`
    (default :class:`InMemoryRetriever`). The :meth:`build` step compresses the
    corpus and indexes the compressed text.
    """

    compressor: Compressor
    retriever: Retriever | None = None
    target_ratio: float = 4.0

    def __post_init__(self) -> None:
        if self.retriever is None:
            self.retriever = InMemoryRetriever()
        self._built = False

    # ------------------------------------------------------------------ #
    # API
    # ------------------------------------------------------------------ #
    def build(self, corpus: list[Fragment]) -> None:
        compressed = [
            self._compress_to_fragment(f, target_ratio=self.target_ratio) for f in corpus
        ]
        assert self.retriever is not None
        self.retriever.index(compressed)
        self._built = True

    def query(self, q: str, k: int = 10) -> list[RetrievedDoc]:
        if not self._built:
            msg = "Call build(corpus) before query()."
            raise RuntimeError(msg)
        assert self.retriever is not None
        return self.retriever.search(q, k=k)

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _compress_to_fragment(self, f: Fragment, *, target_ratio: float) -> Fragment:
        slot = self.compressor.compress(f, target_ratio=target_ratio)
        # We can only index *text*; soft-prompt slots cannot live in this
        # pipeline. Pipelines that want to index soft slots use the memory bus.
        if isinstance(slot.payload, TextSummary):
            text = slot.payload.text
        else:
            # Use a best-effort textual reconstruction; for ICAE this is
            # currently empty — flag explicitly so experiment runners can
            # decide whether to skip P1 for soft-prompt compressors.
            text = self.compressor.decompress(slot) or f.text[: int(len(f.text) / target_ratio)]
        return f.model_copy(update={"text": text})
