"""Retriever protocol + a FAISS-backed reference implementation.

We do not depend on LlamaIndex at this level — pipelines own that integration.
The retriever surface is intentionally small so it composes easily with all
three pipeline styles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np

from m6.memory_bus.schemas import Fragment, TagVector


@dataclass(frozen=True)
class RetrievedDoc:
    """One retrieved document with the retriever's similarity score."""

    fragment: Fragment
    score: float


class Retriever(Protocol):
    """Anything that can rank ``Fragment``s by relevance to a query."""

    def index(self, fragments: list[Fragment]) -> None: ...
    def search(self, query: str, k: int) -> list[RetrievedDoc]: ...


class InMemoryRetriever:
    """Reference :class:`Retriever`. Uses a sentence-transformers embedder.

    Falls back to deterministic-hash embeddings if sentence-transformers is
    missing. The pipelines' headline experiments always use the real embedder;
    the hash fallback exists so unit tests pass on CI.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-large-en-v1.5",
        *,
        dim: int = 1024,
    ) -> None:
        self.model_name = model_name
        self.dim = dim
        self._embedder: Any | None = None
        try:
            from sentence_transformers import SentenceTransformer

            self._embedder = SentenceTransformer(model_name)
            # Read the actual dim back from the model so the user can override.
            self.dim = self._embedder.get_sentence_embedding_dimension() or dim
        except ImportError:  # pragma: no cover — fallback path
            self._embedder = None

        self._fragments: list[Fragment] = []
        self._embeddings: np.ndarray | None = None

    def index(self, fragments: list[Fragment]) -> None:
        self._fragments = list(fragments)
        texts = [f.text for f in fragments]
        embs = self._embed_batch(texts)
        self._embeddings = embs

    def search(self, query: str, k: int) -> list[RetrievedDoc]:
        if self._embeddings is None or not self._fragments:
            return []
        q = self._embed_batch([query])[0]
        sims = self._embeddings @ q
        idxs = np.argsort(-sims)[:k]
        return [
            RetrievedDoc(fragment=self._fragments[int(i)], score=float(sims[int(i)]))
            for i in idxs
        ]

    # ------------------------------------------------------------------ #
    # Embedding
    # ------------------------------------------------------------------ #
    def _embed_batch(self, texts: list[str]) -> np.ndarray:
        if self._embedder is not None:
            arr = self._embedder.encode(texts, normalize_embeddings=True)
            return np.asarray(arr, dtype=np.float32)
        # Hash fallback — deterministic, dimension matches.
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            seed = abs(hash(t)) % (2**32)
            rng = np.random.default_rng(seed)
            v = rng.standard_normal(self.dim).astype(np.float32)
            v /= np.linalg.norm(v) + 1e-12
            out[i] = v
        return out


def apply_acl_filter(
    docs: list[RetrievedDoc], *, requester_acl: int, requester_classification: int
) -> list[RetrievedDoc]:
    """Drop docs whose tags the requester cannot satisfy.

    The pipelines call this *after* retrieval so the retriever stays
    policy-agnostic; the bus's policy middleware is the canonical enforcer.
    """
    out: list[RetrievedDoc] = []
    for d in docs:
        t: TagVector = d.fragment.tags
        if t.grants_to(requester_acl, t.classification.__class__(requester_classification)):
            out.append(d)
    return out
