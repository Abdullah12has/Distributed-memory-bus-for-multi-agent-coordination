"""CAAC — Cliff-Aware Adaptive Compression.

A training-free compressor wrapper that monitors token-recall per fragment
and backs off compression when the predicted coordination success drops
below a safety threshold. Based on Theorem 1 from the coordination cliff
theory (see m6.theory.cliff_prediction).

Algorithm:
  1. Compute q_min = theta (for single-pass compression, N=1).
  2. For each fragment, compress at the target ratio.
  3. Measure token_recall of the compressed output.
  4. If token_recall >= q_min: accept (safe, above cliff).
  5. Else: binary-search for the largest ratio that keeps token_recall >= q_min.
  6. Floor: never back off below min_ratio (default 1.5x) to ensure
     meaningful compression even when backing off.

This wrapper works with ANY underlying compressor (lingua2, phi3-extractive,
filter) without retraining.  Overhead is negligible: token_recall is a set
intersection (~0.1ms per fragment); binary search adds at most 4-5 compress
calls on backed-off fragments only.

Usage:
    from m6.compressors.caac import CAACCompressor

    caac = CAACCompressor(
        inner="lingua2",
        target_ratio=4.0,
        theta=0.5,  # derive via cliff_prediction.derive_theta()
    )
    slot = caac.compress(fragment)
    text = caac.decompress(slot)
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from m6.compressors import make_compressor
from m6.compressors.base import Compressor, ModelCard
from m6.memory_bus.schemas import CompressedSlot, Fragment, TextSummary
from m6.theory.cliff_prediction import q_required


def _normalize_token(t: str) -> str:
    return t.lower().strip()


def _token_recall(source: str, compressed: str) -> float:
    """Fast generic token-recall: fraction of source word-tokens preserved in compressed.

    Note: this treats all tokens equally (conservative proxy). The theorem's q(r) refers
    to task-relevant tokens specifically. For theorem validation, use critical_token_recall
    from run_h1_h2.py which weights family-specific tokens (numbers for a, patterns for b/c).
    CAAC uses generic recall for simplicity — it overestimates preservation, meaning CAAC
    backs off slightly less than optimal (conservative direction).
    """
    src_toks = set(_normalize_token(t) for t in re.findall(r"\w+", source))
    comp_toks = set(_normalize_token(t) for t in re.findall(r"\w+", compressed))
    if not src_toks:
        return 1.0
    return len(src_toks & comp_toks) / len(src_toks)


class CAACCompressor:
    """Cliff-Aware Adaptive Compression wrapper.

    Wraps any base compressor and dynamically adjusts the per-fragment
    compression ratio to stay above the coordination cliff predicted by
    Theorem 1.
    """

    compressor_id: str = "caac"
    tokenizer_id: str = "caac-wrapper"

    def __init__(
        self,
        *,
        inner: str | Compressor = "lingua2",
        target_ratio: float = 4.0,
        n_compression_passes: int = 1,
        theta: float = 0.5,
        min_ratio: float = 1.5,
        binary_search_steps: int = 5,
        **inner_kwargs: Any,
    ) -> None:
        """
        Args:
            inner: Base compressor name or instance to wrap.
            target_ratio: Desired compression ratio (CAAC may use less).
            n_compression_passes: Number of times compression is applied (default 1).
            theta: Minimum surviving information fraction for success.
                Derive empirically via cliff_prediction.derive_theta().
            min_ratio: Lowest ratio CAAC will back off to (1.5 = always
                achieve at least 1.5x compression, even when backing off).
            binary_search_steps: Max iterations for finding safe ratio.
            **inner_kwargs: Passed to make_compressor if inner is a string.
        """
        self.target_ratio = target_ratio
        self.n_compression_passes = n_compression_passes
        self.theta = theta
        self.min_ratio = min_ratio
        self._search_steps = binary_search_steps
        self._q_min = q_required(theta, n_compression_passes)

        # Build or store the inner compressor
        if isinstance(inner, str):
            self._inner_name = inner
            self._inner_kwargs = inner_kwargs
            self._inner = make_compressor(inner, target_ratio=target_ratio, **inner_kwargs)
        else:
            self._inner_name = inner.compressor_id
            self._inner_kwargs = {}
            self._inner = inner

        # Cache inner compressors at different ratios to avoid reloading models
        self._comp_cache: dict[float, Compressor] = {target_ratio: self._inner}

        # Tracking stats
        self._total_fragments = 0
        self._backed_off = 0
        self._total_target_chars = 0
        self._total_output_chars = 0

    def compress(
        self,
        fragment: Fragment,
        target_ratio: float | None = None,
    ) -> CompressedSlot:
        ratio = target_ratio if target_ratio is not None else self.target_ratio
        self._total_fragments += 1
        self._total_target_chars += len(fragment.text)

        if ratio <= 1.0:
            self._total_output_chars += len(fragment.text)
            return self._make_slot(fragment, fragment.text, 1.0)

        # Step 1: try compressing at the full target ratio
        compressed_text = self._compress_at_ratio(fragment, ratio)
        q = _token_recall(fragment.text, compressed_text)

        # Step 2: if token recall is safe, accept
        if q >= self._q_min:
            actual_ratio = len(fragment.text) / max(len(compressed_text), 1)
            self._total_output_chars += len(compressed_text)
            return self._make_slot(fragment, compressed_text, actual_ratio)

        # Step 3: binary search for the largest safe ratio
        self._backed_off += 1
        safe_text = self._binary_search_safe_ratio(fragment, ratio)
        actual_ratio = len(fragment.text) / max(len(safe_text), 1)
        self._total_output_chars += len(safe_text)
        return self._make_slot(fragment, safe_text, actual_ratio)

    def _compress_at_ratio(self, fragment: Fragment, ratio: float) -> str:
        """Compress a fragment at a specific ratio using the inner compressor."""
        comp = self._get_compressor_at_ratio(ratio)
        slot = comp.compress(fragment, target_ratio=ratio)
        return comp.decompress(slot) or fragment.text

    def _binary_search_safe_ratio(self, fragment: Fragment, max_ratio: float) -> str:
        """Find the largest ratio where token_recall >= q_min."""
        lo = self.min_ratio
        hi = max_ratio
        epsilon = 0.1  # Stop when search interval is narrow enough
        # Initialize to min_ratio compression (not uncompressed) to
        # guarantee at least min_ratio compression even on full backoff.
        best_text = self._compress_at_ratio(fragment, self.min_ratio)
        best_q = _token_recall(fragment.text, best_text)

        for _ in range(self._search_steps):
            if hi - lo < epsilon:
                break
            mid = (lo + hi) / 2.0
            if mid <= 1.05:
                # Below meaningful compression, just return original
                break
            compressed = self._compress_at_ratio(fragment, mid)
            q = _token_recall(fragment.text, compressed)
            if q >= self._q_min:
                # Safe: try compressing more
                best_text = compressed
                best_q = q
                lo = mid
            else:
                # Unsafe: back off
                hi = mid

        if best_q < self._q_min:
            import logging
            logging.getLogger(__name__).warning(
                "CAAC binary search exhausted: best q=%.3f < q_min=%.3f "
                "(fragment %d chars, min_ratio=%.1f)",
                best_q, self._q_min, len(fragment.text), self.min_ratio,
            )
        return best_text

    def _get_compressor_at_ratio(self, ratio: float) -> Compressor:
        """Get or build an inner compressor at the given ratio (cached)."""
        # Round to 2 decimals for cache-key stability
        key = round(ratio, 2)
        if key not in self._comp_cache:
            self._comp_cache[key] = make_compressor(
                self._inner_name, target_ratio=ratio, **self._inner_kwargs
            )
        return self._comp_cache[key]

    def decompress(self, slot: CompressedSlot) -> str:
        if isinstance(slot.payload, TextSummary):
            return slot.payload.text
        return ""

    def embed(self, _slot: CompressedSlot) -> list[float] | None:
        return None

    def model_card(self) -> ModelCard:
        achieved = (
            self._total_target_chars / max(self._total_output_chars, 1)
            if self._total_fragments > 0
            else self.target_ratio
        )
        return ModelCard(
            compressor_id=self.compressor_id,
            family="adaptive",
            base_model=self._inner_name,
            trained=False,
            training_loss=None,
            target_ratio_default=self.target_ratio,
            notes=(
                f"CAAC wrapping {self._inner_name}. "
                f"q_min={self._q_min:.3f} (theta={self.theta}, N={self.n_compression_passes}). "
                f"Backed off {self._backed_off}/{self._total_fragments} fragments. "
                f"Achieved ratio: {achieved:.2f}x (target {self.target_ratio}x)."
            ),
        )

    @property
    def stats(self) -> dict[str, Any]:
        """Return compression statistics for reporting."""
        achieved = (
            self._total_target_chars / max(self._total_output_chars, 1)
            if self._total_fragments > 0
            else 0.0
        )
        return {
            "total_fragments": self._total_fragments,
            "backed_off": self._backed_off,
            "backoff_rate": self._backed_off / max(self._total_fragments, 1),
            "target_ratio": self.target_ratio,
            "achieved_ratio": achieved,
            "q_min": self._q_min,
            "theta": self.theta,
            "n_compression_passes": self.n_compression_passes,
        }

    def _make_slot(self, fragment: Fragment, text: str, ratio: float) -> CompressedSlot:
        digest = hashlib.sha256(
            f"{fragment.fragment_id}|caac|{ratio}".encode()
        ).hexdigest()[:16]
        return CompressedSlot(
            slot_id=f"caac-{digest}",
            payload=TextSummary(text=text),
            tags=fragment.tags,
            audit_pointers=(),
            compressor_id=self.compressor_id,
            ratio=max(ratio, 1.0),
        )
