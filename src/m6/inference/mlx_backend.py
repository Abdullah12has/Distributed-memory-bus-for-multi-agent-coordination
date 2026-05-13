"""MLX-LM backend for Apple Silicon.

Loads at construction; warm enough for sub-second next-token latency on M4 Pro
for ≤13B fp16 models.

Imports are deferred so the test environment (Linux CI) does not try to install
MLX. ``MlxBackend.__init__`` raises a clear error if MLX is missing.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

import numpy as np

from m6.config.logging import get_logger
from m6.inference.base import Completion
from m6.pipelines.cost_model import eur_for_call

if TYPE_CHECKING:  # pragma: no cover
    pass

log = get_logger(__name__)


class MlxBackend:
    """MLX-LM backend for 7B/13B inference."""

    backend_id: str = "mlx"

    def __init__(
        self,
        *,
        model: str = "mlx-community/Llama-3.1-8B-Instruct-4bit",
        adapter_path: str | None = None,
        embedder_model: str = "BAAI/bge-large-en-v1.5",
        **_extra: Any,
    ) -> None:
        try:
            from mlx_lm import load  # type: ignore[import-not-found]
        except ImportError as e:  # pragma: no cover - env-specific
            msg = "mlx-lm is not installed. Run `pip install m6-thesis[mlx]`."
            raise RuntimeError(msg) from e

        self.model_id = model
        self.adapter_path = adapter_path
        self.embedder_model = embedder_model
        self._embedder: Any | None = None
        log.info("backend.mlx.loading", model=model, adapter_path=adapter_path)
        self._model, self._tokenizer = load(model, adapter_path=adapter_path)
        log.info("backend.mlx.loaded", model=model)

    async def complete(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        stop: list[str] | None = None,
        request_id: str | None = None,
    ) -> Completion:
        _ = (request_id, stop)
        from mlx_lm import generate  # type: ignore[import-not-found]

        t0 = time.perf_counter()
        text = generate(
            self._model,
            self._tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            temp=temperature,
            verbose=False,
        )
        wallclock = int((time.perf_counter() - t0) * 1000)
        in_tok = len(self._tokenizer.encode(prompt))
        out_tok = len(self._tokenizer.encode(text)) - in_tok
        return Completion(
            text=text,
            input_tokens=in_tok,
            output_tokens=max(out_tok, 0),
            wallclock_ms=wallclock,
            eur_cost=self.cost_eur(in_tok, max(out_tok, 0)),
        )

    async def embed(self, text: str) -> np.ndarray:
        """Return a sentence embedding for ``text``.

        MLX-LM models return *logits*, not hidden states, from their forward
        pass — mean-pooling logits is not a meaningful embedding. We delegate
        to ``sentence-transformers`` (configurable via the ``embedder_model``
        kwarg at construction); this is also what the RAG pipelines use for
        retrieval so the embedding spaces stay consistent.

        Callers who want raw model hidden states should attach a forward hook
        on the underlying model directly; that path is left for D7 because the
        current thesis evaluation never needs LLM-generated embeddings on the
        critical path.
        """
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._embedder = SentenceTransformer(self.embedder_model)
            except ImportError as e:  # pragma: no cover - env-specific
                msg = (
                    "MlxBackend.embed requires sentence-transformers. "
                    "Either `pip install m6-thesis[torch]` or pass "
                    "`embedder=` to the backend constructor."
                )
                raise RuntimeError(msg) from e
        arr = self._embedder.encode(text, normalize_embeddings=True)
        return np.asarray(arr, dtype=np.float32)

    def cost_eur(self, input_tokens: int, output_tokens: int) -> float:
        return eur_for_call("local-mlx", input_tokens, output_tokens)
