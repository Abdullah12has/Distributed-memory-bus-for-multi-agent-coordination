"""Inference backends.

Unified protocol + per-backend implementations. Use :func:`make_backend` to
build a backend by name. See ``docs/adr/ADR-003-inference-backends.md``.
"""

from m6.inference.base import Completion, InferenceBackend
from m6.inference.factory import make_backend

__all__ = ["Completion", "InferenceBackend", "make_backend"]
