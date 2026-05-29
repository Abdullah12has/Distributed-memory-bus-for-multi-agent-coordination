"""Compression cache — precomputed compressed texts for all experiments.

The cache stores compressed text keyed by (compressor, ratio, fragment_id,
task_hint_hash). A CachedCompressor wrapper implements the Compressor protocol
so experiments can use the cache transparently via make_compressor().

Usage:
    # Precompute (on GPU):
    python -m m6.experiments.precompute_cache

    # Use in any experiment:
    python -m m6.experiments.run_h1_h2 --cache results/compression_cache.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from m6.memory_bus.schemas import CompressedSlot, Fragment, TextSummary, TagVector


def _hint_key(task_hint: str | None) -> str:
    """Short hash of task_hint for cache key. Empty string for None/empty."""
    h = task_hint or ""
    if not h:
        return ""
    return hashlib.md5(h.encode()).hexdigest()[:12]


class CompressionCache:
    """Flat dict cache: key = 'compressor|ratio|fragment_id|hint_hash'."""

    def __init__(self) -> None:
        self._entries: dict[str, str] = {}
        self._meta: dict[str, Any] = {}

    @staticmethod
    def _key(compressor: str, ratio: float, fragment_id: str, task_hint: str | None = None) -> str:
        return f"{compressor}|{ratio}|{fragment_id}|{_hint_key(task_hint)}"

    def store(
        self,
        compressor: str,
        ratio: float,
        fragment_id: str,
        task_hint: str | None,
        compressed_text: str,
    ) -> None:
        self._entries[self._key(compressor, ratio, fragment_id, task_hint)] = compressed_text

    def lookup(
        self,
        compressor: str,
        ratio: float,
        fragment_id: str,
        task_hint: str | None = None,
    ) -> str | None:
        # Try exact key first, then fall back to no-hint variant
        result = self._entries.get(self._key(compressor, ratio, fragment_id, task_hint))
        if result is None and task_hint:
            result = self._entries.get(self._key(compressor, ratio, fragment_id, None))
        return result

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"meta": self._meta, "entries": self._entries}
        with open(path, "w") as f:
            json.dump(data, f)
        size_mb = path.stat().st_size / 1024 / 1024
        print(f"Cache saved: {path} ({len(self._entries)} entries, {size_mb:.1f} MB)")

    @classmethod
    def load(cls, path: str | Path) -> CompressionCache:
        path = Path(path)
        with open(path) as f:
            data = json.load(f)
        cache = cls()
        cache._meta = data.get("meta", {})
        cache._entries = data.get("entries", {})
        print(f"Cache loaded: {path} ({len(cache._entries)} entries)", file=sys.stderr)
        return cache

    def __len__(self) -> int:
        return len(self._entries)

    def set_meta(self, **kwargs: Any) -> None:
        self._meta.update(kwargs)


class CachedCompressor:
    """Compressor protocol wrapper that reads from a CompressionCache.

    Drop-in replacement for any compressor. Experiments pass --cache and
    get this instead of the real compressor. Raises KeyError on cache miss.
    """

    def __init__(self, compressor_id: str, target_ratio: float, cache: CompressionCache) -> None:
        self.compressor_id = compressor_id
        self.tokenizer_id = "cached"
        self.target_ratio = target_ratio
        self._cache = cache
        self._misses = 0

    def compress(
        self,
        fragment: Fragment,
        target_ratio: float | None = None,
    ) -> CompressedSlot:
        ratio = target_ratio if target_ratio is not None else self.target_ratio
        hint = fragment.task_hint
        text = self._cache.lookup(self.compressor_id, ratio, fragment.fragment_id, hint)
        if text is None:
            self._misses += 1
            if self._misses <= 3:
                key = CompressionCache._key(self.compressor_id, ratio, fragment.fragment_id, hint)
                print(f"  [cache miss] {key}", file=sys.stderr)
            raise KeyError(
                f"Cache miss: {self.compressor_id}|{ratio:.2f}|{fragment.fragment_id}|{_hint_key(hint)}"
            )
        slot_id = f"cached-{fragment.fragment_id[:40]}-{ratio:.0f}"
        return CompressedSlot(
            slot_id=slot_id,
            payload=TextSummary(text=text),
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


def make_cached_compressor(
    name: str, cache: CompressionCache, **kwargs: Any
) -> CachedCompressor:
    """Factory that mirrors make_compressor() but returns a CachedCompressor."""
    target_ratio = kwargs.get("target_ratio", 1.0)
    # Normalize name to match cache keys
    name = name.lower()
    if name in {"phi3-extractive", "phi3_extractive", "phi3"}:
        name = "phi3-extractive"
    elif name in {"none", "identity"}:
        name = "none"
    elif name in {"truncation", "trunc", "truncate"}:
        name = "truncation"
    return CachedCompressor(name, target_ratio, cache)
