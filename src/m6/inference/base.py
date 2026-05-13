"""Backend protocol and shared dataclasses.

Every concrete backend implements :class:`InferenceBackend`. The :class:`Completion`
record is what flows from ``complete()`` and is the row written to the cost
ledger.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import numpy as np


@dataclass(frozen=True)
class Completion:
    """One completion result. Includes cost so the ledger writes are trivial."""

    text: str
    input_tokens: int
    output_tokens: int
    wallclock_ms: int
    eur_cost: float
    finish_reason: str = "stop"
    raw: dict[str, object] = field(default_factory=dict)


@runtime_checkable
class InferenceBackend(Protocol):
    backend_id: str
    model_id: str

    async def complete(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        stop: list[str] | None = None,
        request_id: str | None = None,
    ) -> Completion: ...

    async def embed(self, text: str) -> np.ndarray: ...

    def cost_eur(self, input_tokens: int, output_tokens: int) -> float: ...
