"""Phi-3-Mini extractive compressor (training-free).

Uses Phi-3-Mini-3.8B via Ollama to select verbatim spans from the source text.
The prompt explicitly forbids paraphrasing or novel token generation. A post-hoc
verifier checks every output: each token must appear in the source.

Retry strategy (per TECHNICAL_REFERENCE_V3 §2):
  1. First attempt with standard extractive prompt.
  2. On verifier failure: retry with stricter prompt.
  3. On second failure: fall back to LLMLingua-2 at the same ratio.

Usage:
    comp = Phi3ExtractiveCompressor(target_ratio=4.0)
    slot = comp.compress(fragment)
    text = comp.decompress(slot)  # the selected spans
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

import httpx

from m6.compressors.base import ModelCard
from m6.memory_bus.schemas import CompressedSlot, Fragment, TextSummary

OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "phi3:latest"

# Frozen prompt per TECHNICAL_REFERENCE_V3 §2.
EXTRACTIVE_PROMPT = """You are a passage selector, NOT a writer. Your job is to select the minimal set of contiguous spans from the PASSAGE that a downstream reader would need to answer the QUESTION.

RULES:
  1. Output ONLY tokens that appear verbatim in the PASSAGE.
  2. Do NOT summarise, paraphrase, infer, or add new tokens.
  3. Separate selected spans with a single newline.
  4. Target output length: at most {target_tokens} tokens.
  5. If unsure whether a span is relevant, include it.

PASSAGE:
{passage}

QUESTION (task hint):
{task_hint}

SELECTED SPANS:"""

STRICT_RETRY_PROMPT = """Repeat the source spans verbatim. DO NOT alter casing or punctuation. Select spans from the PASSAGE that answer the QUESTION. Output at most {target_tokens} tokens.

PASSAGE:
{passage}

QUESTION:
{task_hint}

VERBATIM SPANS:"""


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _normalise_token(t: str) -> str:
    return t.lower().strip()


def verify_extractive(
    source: str, output: str, max_violation_rate: float = 0.05
) -> tuple[bool, float]:
    """Return (passed, fraction_extractive).

    A token is extractive if it appears in the source. Per TECHNICAL_REFERENCE_V3 §2.
    """
    src_tokens = set(_normalise_token(t) for t in re.findall(r"\w+", source))
    out_tokens = [_normalise_token(t) for t in re.findall(r"\w+", output) if t]
    if not out_tokens:
        return True, 1.0
    n_extractive = sum(1 for t in out_tokens if t in src_tokens)
    fraction = n_extractive / len(out_tokens)
    return fraction >= (1.0 - max_violation_rate), fraction


def _call_ollama(url: str, model: str, prompt: str, max_tokens: int) -> str:
    resp = httpx.post(
        f"{url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max(max_tokens, 32), "temperature": 0.0},
        },
        timeout=120.0,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


class Phi3ExtractiveCompressor:
    """Extractive compressor using Phi-3-Mini via Ollama.

    Every output token must appear in the source. On verifier failure:
    retry with stricter prompt, then fall back to LLMLingua-2.
    """

    compressor_id: str = "phi3-extractive"
    tokenizer_id: str = "phi3"

    def __init__(
        self,
        *,
        target_ratio: float = 4.0,
        ollama_model: str = DEFAULT_MODEL,
        ollama_url: str = OLLAMA_URL,
        verify_extractive: bool = True,
        max_violation_rate: float = 0.05,
        max_input_tokens: int = 4096,
        **_extra: Any,
    ) -> None:
        self.target_ratio = target_ratio
        self.model = ollama_model
        self._url = ollama_url
        self._verify = verify_extractive
        self._max_violation = max_violation_rate
        self._max_input = max_input_tokens
        self._verify_failures = 0
        self._fallback_count = 0
        self._total_calls = 0
        self._lingua2_fallback: Any = None

    def compress(
        self,
        fragment: Fragment,
        target_ratio: float | None = None,
    ) -> CompressedSlot:
        ratio = target_ratio or self.target_ratio
        if ratio <= 1.0:
            return self._make_slot(fragment, fragment.text, 1.0)

        source = fragment.text
        source_tokens = _estimate_tokens(source)
        target_tokens = max(10, int(source_tokens / ratio))
        task_hint = getattr(fragment, "task_hint", "") or "Preserve all factual claims."

        # Attempt 1: standard extractive prompt
        output = self._try_extract(source, task_hint, target_tokens, EXTRACTIVE_PROMPT)

        # Attempt 2: stricter prompt on verifier failure
        if output is None:
            self._verify_failures += 1
            output = self._try_extract(source, task_hint, target_tokens, STRICT_RETRY_PROMPT)

        # Attempt 3: fall back to LLMLingua-2
        if output is None:
            self._verify_failures += 1
            self._fallback_count += 1
            output = self._lingua2_compress(fragment, ratio)

        actual_ratio = len(source) / max(len(output), 1)
        return self._make_slot(fragment, output, actual_ratio)

    def _try_extract(
        self, source: str, task_hint: str, target_tokens: int, prompt_template: str
    ) -> str | None:
        try:
            prompt = prompt_template.format(
                target_tokens=target_tokens,
                passage=source[: self._max_input * 4],
                task_hint=task_hint,
            )
            raw = _call_ollama(self._url, self.model, prompt, max_tokens=target_tokens + 50)
            self._total_calls += 1

            if not self._verify:
                return raw

            passed, fraction = verify_extractive(source, raw, self._max_violation)
            if passed:
                return raw
            return None
        except Exception:
            return None

    def _lingua2_compress(self, fragment: Fragment, ratio: float) -> str:
        """Fall back to LLMLingua-2 at the same ratio."""
        if self._lingua2_fallback is None:
            try:
                from m6.compressors.lingua2 import LLMLingua2Compressor

                self._lingua2_fallback = LLMLingua2Compressor(target_ratio=ratio)
            except Exception:
                # Last resort: truncation
                target_len = max(10, int(len(fragment.text) / ratio))
                return fragment.text[:target_len]
        slot = self._lingua2_fallback.compress(fragment, target_ratio=ratio)
        return self._lingua2_fallback.decompress(slot) or fragment.text[:100]

    def decompress(self, slot: CompressedSlot) -> str:
        if isinstance(slot.payload, TextSummary):
            return slot.payload.text
        return ""

    def embed(self, _slot: CompressedSlot) -> list[float] | None:
        return None

    def model_card(self) -> ModelCard:
        return ModelCard(
            compressor_id=self.compressor_id,
            family="hard-prompt",
            base_model=self.model,
            trained=False,
            training_loss=None,
            target_ratio_default=self.target_ratio,
            notes=(
                f"Extractive Phi-3-Mini via Ollama. "
                f"Verify failures: {self._verify_failures}, "
                f"LLMLingua-2 fallbacks: {self._fallback_count}/{self._total_calls}"
            ),
        )

    def _make_slot(self, fragment: Fragment, text: str, ratio: float) -> CompressedSlot:
        digest = hashlib.sha256(f"{fragment.fragment_id}|{ratio}".encode()).hexdigest()[:16]
        return CompressedSlot(
            slot_id=f"phi3-{digest}",
            payload=TextSummary(text=text),
            tags=fragment.tags,
            audit_pointers=(),
            compressor_id=self.compressor_id,
            ratio=ratio,
        )
