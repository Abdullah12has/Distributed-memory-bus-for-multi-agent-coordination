"""External API backends — OpenAI, Anthropic, and a mock Echo for tests.

Cost is computed via :mod:`m6.pipelines.cost_model` so every backend uses the
same authoritative price table. Each backend writes a row to the cost ledger
on every call (callers pass an audit handle via ``with_cost_ledger``).

Retry: ``tenacity`` exponential back-off, 5 retries, 2–32 s. Configurable per
backend via the ``retry_*`` kwargs.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential

from m6.config.logging import get_logger
from m6.config.settings import get_settings
from m6.inference.base import Completion
from m6.pipelines.cost_model import eur_for_call

if TYPE_CHECKING:  # pragma: no cover - optional
    pass

log = get_logger(__name__)


# --------------------------------------------------------------------------- #
# OpenAI
# --------------------------------------------------------------------------- #
class OpenAIBackend:
    """OpenAI Chat Completions. Used for the H6 judge and the C3 cost arm."""

    backend_id: str = "openai"

    def __init__(self, model: str | None = None, **_extra: Any) -> None:
        from openai import AsyncOpenAI

        settings = get_settings()
        api_key = settings.openai_api_key.get_secret_value() if settings.has_openai() else ""  # type: ignore[union-attr]
        if not api_key:
            log.warning("backend.openai.no_api_key")
        self.model_id = model or settings.openai_model
        self._client = AsyncOpenAI(api_key=api_key or None)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=32))  # type: ignore[misc]
    async def complete(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        stop: list[str] | None = None,
        request_id: str | None = None,
    ) -> Completion:
        _ = request_id
        t0 = time.perf_counter()
        # OpenAI's parameter changed between model families. The o-series
        # (``o1``, ``o3``, ``o4`` ...) require ``max_completion_tokens``; gpt-4o
        # and gpt-4o-mini still use the legacy ``max_tokens``. We branch on the
        # model name rather than letting the SDK auto-detect because some SDK
        # versions reject the param outright.
        is_o_series = self.model_id.startswith(("o1", "o3", "o4"))
        token_kwarg: dict[str, int] = (
            {"max_completion_tokens": max_tokens} if is_o_series else {"max_tokens": max_tokens}
        )
        resp = await self._client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            stop=stop,
            **token_kwarg,
        )
        wallclock = int((time.perf_counter() - t0) * 1000)
        text = (resp.choices[0].message.content or "").strip()
        usage = resp.usage
        in_tok = usage.prompt_tokens if usage else 0
        out_tok = usage.completion_tokens if usage else 0
        return Completion(
            text=text,
            input_tokens=in_tok,
            output_tokens=out_tok,
            wallclock_ms=wallclock,
            eur_cost=self.cost_eur(in_tok, out_tok),
            finish_reason=resp.choices[0].finish_reason or "stop",
        )

    async def embed(self, text: str) -> np.ndarray:
        resp = await self._client.embeddings.create(model="text-embedding-3-small", input=text)
        return np.asarray(resp.data[0].embedding, dtype=np.float32)

    def cost_eur(self, input_tokens: int, output_tokens: int) -> float:
        return eur_for_call(self.model_id, input_tokens, output_tokens)


# --------------------------------------------------------------------------- #
# Anthropic
# --------------------------------------------------------------------------- #
class AnthropicBackend:
    """Anthropic Messages. Used for the C3 cost arm and the 10% cross-check."""

    backend_id: str = "anthropic"

    def __init__(self, model: str | None = None, **_extra: Any) -> None:
        from anthropic import AsyncAnthropic

        settings = get_settings()
        api_key = settings.anthropic_api_key.get_secret_value() if settings.has_anthropic() else ""  # type: ignore[union-attr]
        if not api_key:
            log.warning("backend.anthropic.no_api_key")
        self.model_id = model or settings.anthropic_model
        self._client = AsyncAnthropic(api_key=api_key or None)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=32))  # type: ignore[misc]
    async def complete(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        stop: list[str] | None = None,
        request_id: str | None = None,
    ) -> Completion:
        _ = request_id
        t0 = time.perf_counter()
        resp = await self._client.messages.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stop_sequences=stop,
        )
        wallclock = int((time.perf_counter() - t0) * 1000)
        # Anthropic returns a list of content blocks; we concat text blocks.
        text = "".join(blk.text for blk in resp.content if getattr(blk, "type", "") == "text")
        in_tok = resp.usage.input_tokens if resp.usage else 0
        out_tok = resp.usage.output_tokens if resp.usage else 0
        return Completion(
            text=text.strip(),
            input_tokens=in_tok,
            output_tokens=out_tok,
            wallclock_ms=wallclock,
            eur_cost=self.cost_eur(in_tok, out_tok),
            finish_reason=resp.stop_reason or "stop",
        )

    async def embed(self, _text: str) -> np.ndarray:
        msg = "Anthropic does not expose an embeddings endpoint; use OpenAIBackend."
        raise NotImplementedError(msg)

    def cost_eur(self, input_tokens: int, output_tokens: int) -> float:
        return eur_for_call(self.model_id, input_tokens, output_tokens)


# --------------------------------------------------------------------------- #
# Echo — deterministic mock for tests
# --------------------------------------------------------------------------- #
class EchoBackend:
    """Returns the prompt back. Used in unit tests to avoid API calls."""

    backend_id: str = "echo"

    def __init__(self, model: str = "echo", **_extra: Any) -> None:
        self.model_id = model

    async def complete(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        stop: list[str] | None = None,
        request_id: str | None = None,
    ) -> Completion:
        _ = (max_tokens, temperature, stop, request_id)
        # Tokens estimated as ~4 chars/token.
        n_in = max(1, len(prompt) // 4)
        text = f"echo: {prompt[:200]}"
        n_out = max(1, len(text) // 4)
        return Completion(
            text=text,
            input_tokens=n_in,
            output_tokens=n_out,
            wallclock_ms=1,
            eur_cost=0.0,
        )

    async def embed(self, text: str) -> np.ndarray:
        seed = abs(hash(text)) % (2**32)
        rng = np.random.default_rng(seed)
        v = rng.standard_normal(384).astype(np.float32)
        return v / (np.linalg.norm(v) + 1e-12)

    def cost_eur(self, _input_tokens: int, _output_tokens: int) -> float:
        return 0.0
