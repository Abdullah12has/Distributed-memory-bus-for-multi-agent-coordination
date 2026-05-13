"""Backend factory."""

from __future__ import annotations

from typing import Any

from m6.inference.base import InferenceBackend


def make_backend(name: str, **kwargs: Any) -> InferenceBackend:
    """Build a backend by name. Lazy imports per ADR-003."""
    name = name.lower()
    if name == "mlx":
        from m6.inference.mlx_backend import MlxBackend

        return MlxBackend(**kwargs)
    if name == "llamacpp":
        from m6.inference.llamacpp_backend import LlamaCppBackend

        return LlamaCppBackend(**kwargs)
    if name == "ollama":
        from m6.inference.ollama_backend import OllamaBackend

        return OllamaBackend(**kwargs)
    if name == "openai":
        from m6.inference.api_backend import OpenAIBackend

        return OpenAIBackend(**kwargs)
    if name == "anthropic":
        from m6.inference.api_backend import AnthropicBackend

        return AnthropicBackend(**kwargs)
    if name == "echo":
        # Deterministic mock used in unit tests.
        from m6.inference.api_backend import EchoBackend

        return EchoBackend(**kwargs)
    msg = f"Unknown inference backend: {name!r}"
    raise ValueError(msg)
