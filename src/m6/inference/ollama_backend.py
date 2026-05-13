"""Ollama backend — wraps a localhost HTTP endpoint.

Used for developer iteration. Production experiments use MLX or llama.cpp
directly so the cost ledger is unambiguous about which device served traffic.
"""

from __future__ import annotations

import time
from typing import Any

import httpx
import numpy as np

from m6.config.logging import get_logger
from m6.inference.base import Completion
from m6.pipelines.cost_model import eur_for_call

log = get_logger(__name__)


class OllamaBackend:
    """Ollama HTTP client."""

    backend_id: str = "ollama"

    def __init__(
        self,
        *,
        model: str = "llama3.1:8b-instruct-q4_K_M",
        base_url: str = "http://127.0.0.1:11434",
        **_extra: Any,
    ) -> None:
        self.model_id = model
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)

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
        body: dict[str, Any] = {
            "model": self.model_id,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if stop:
            body["options"]["stop"] = stop
        r = await self._client.post("/api/generate", json=body)
        r.raise_for_status()
        out = r.json()
        wallclock = int((time.perf_counter() - t0) * 1000)
        text = out.get("response", "").strip()
        in_tok = int(out.get("prompt_eval_count", 0))
        out_tok = int(out.get("eval_count", 0))
        return Completion(
            text=text,
            input_tokens=in_tok,
            output_tokens=out_tok,
            wallclock_ms=wallclock,
            eur_cost=self.cost_eur(in_tok, out_tok),
        )

    async def embed(self, text: str) -> np.ndarray:
        r = await self._client.post("/api/embeddings", json={"model": self.model_id, "prompt": text})
        r.raise_for_status()
        return np.asarray(r.json()["embedding"], dtype=np.float32)

    def cost_eur(self, input_tokens: int, output_tokens: int) -> float:
        return eur_for_call("local-ollama", input_tokens, output_tokens)

    async def aclose(self) -> None:
        await self._client.aclose()
