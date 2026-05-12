"""FAISS-CPU vector store.

FAISS does not store id → string mappings natively; we maintain a parallel
``ids: list[SlotId]`` and use FAISS's internal int64 ids as positional indices.

Choice of index: ``IndexHNSWFlat`` with M=32 — small enough to fit on CPU for
the C1-scale workload (~7.5K slots, plan §4.2) and recall@10 is typically
> 0.95 at this scale.

For larger D7 deployments, swap to ``IndexIVFFlat`` with explicit training; the
:class:`VectorStore` Protocol is unchanged.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

import faiss  # type: ignore[import-not-found]
import numpy as np

from m6.config.logging import get_logger
from m6.memory_bus.schemas import SlotId

log = get_logger(__name__)


class FaissVectorStore:
    """Cosine-similarity HNSW index over compressed-slot embeddings."""

    def __init__(self, path: Path | str, dim: int = 768, *, hnsw_m: int = 32) -> None:
        self.path = Path(path)
        self.dim = dim
        self._lock = threading.RLock()
        # We store unit-normalised vectors and use L2; recall is identical to
        # cosine on the unit sphere, and FAISS's flat indices support it.
        self._index = faiss.IndexHNSWFlat(dim, hnsw_m, faiss.METRIC_L2)
        self._index.hnsw.efConstruction = 200
        self._index.hnsw.efSearch = 128
        self._ids: list[SlotId] = []

        if self.path.exists():
            self.reload()

    # ------------------------------------------------------------------ #
    # Protocol surface
    # ------------------------------------------------------------------ #
    def add(self, slot_id: SlotId, embedding: np.ndarray) -> None:
        vec = _normalise(embedding.astype(np.float32, copy=False))
        if vec.shape[-1] != self.dim:
            msg = f"Embedding dim {vec.shape[-1]} ≠ index dim {self.dim}"
            raise ValueError(msg)
        with self._lock:
            self._index.add(vec.reshape(1, -1))
            self._ids.append(slot_id)

    def search(self, query: np.ndarray, k: int) -> list[tuple[SlotId, float]]:
        q = _normalise(query.astype(np.float32, copy=False)).reshape(1, -1)
        if q.shape[-1] != self.dim:
            msg = f"Query dim {q.shape[-1]} ≠ index dim {self.dim}"
            raise ValueError(msg)
        with self._lock:
            if len(self._ids) == 0:
                return []
            distances, indices = self._index.search(q, min(k, len(self._ids)))
            ids = self._ids  # local copy for safety outside the lock
        results: list[tuple[SlotId, float]] = []
        for dist, idx in zip(distances[0], indices[0], strict=True):
            if idx < 0:
                continue
            # Convert squared-L2 on unit vectors to cosine similarity:
            # ‖a − b‖² = 2 − 2·cos(θ)  ⇒  cos = 1 − dist/2.
            sim = float(1.0 - dist / 2.0)
            results.append((ids[idx], sim))
        return results

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            faiss.write_index(self._index, str(self.path))
            (self.path.with_suffix(".ids.json")).write_text(json.dumps(self._ids), encoding="utf-8")
        log.info("vector_store.saved", path=str(self.path), n=len(self._ids))

    def reload(self) -> None:
        with self._lock:
            if not self.path.exists():
                return
            self._index = faiss.read_index(str(self.path))
            ids_path = self.path.with_suffix(".ids.json")
            self._ids = (
                json.loads(ids_path.read_text(encoding="utf-8")) if ids_path.exists() else []
            )
        log.info("vector_store.reloaded", path=str(self.path), n=len(self._ids))

    def __len__(self) -> int:
        with self._lock:
            return len(self._ids)


def _normalise(v: np.ndarray) -> np.ndarray:
    """L2-normalise; safe against zero vectors."""
    norm = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(norm == 0, 1.0, norm)
