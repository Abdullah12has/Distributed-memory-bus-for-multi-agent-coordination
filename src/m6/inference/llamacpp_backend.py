"""llama.cpp + GGUF backend for 34B / 70B int4.

Plan §5.4 wallclock: 34B ~5–10 tok/s, 70B ~3–5 tok/s. The 70B mini-eval
sanity-check is the kill-switch from ``docs/adr/ADR-003-inference-backends.md``.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from m6.config.logging import get_logger
from m6.evaluation.metrics.qa import f1_score
from m6.inference.base import Completion
from m6.pipelines.cost_model import eur_for_call

log = get_logger(__name__)


# Sanity-baseline file. Populated by ``make baselines-record`` once Month 1's
# reproduction run lands. Until then, the 7B baseline F1 on the mini-set is
# *unknown*, and starting a 34B/70B backend without it would compare against a
# placeholder — exactly the failure mode plan §7 risk-register row 4 warns
# against. We therefore refuse to start until the file exists.
SANITY_BASELINE_PATH = Path("results/sanity/llamacpp_baseline.json")
SANITY_F1_DROP_THRESHOLD_PP = 5.0  # plan risk-register row 4
_SANITY_PROMPTS: list[tuple[str, str]] = [
    (
        "Read the passage and answer the question.\n\n"
        "Passage: Alice has three apples. Bob takes one. Carol takes one.\n"
        "Question: How many apples does Alice have left?\nAnswer:",
        "one",
    ),
    (
        "Passage: The capital of France is Paris.\nQuestion: What is the capital of France?\nAnswer:",
        "Paris",
    ),
    (
        "Passage: A square has four equal sides.\nQuestion: How many sides does a square have?\nAnswer:",
        "four",
    ),
    (
        "Passage: Water boils at 100 degrees Celsius at sea level.\nQuestion: At what temperature does water boil at sea level?\nAnswer:",
        "100 degrees Celsius",
    ),
    (
        "Passage: The Moon orbits the Earth.\nQuestion: What does the Moon orbit?\nAnswer:",
        "the Earth",
    ),
]


class LlamaCppBackend:
    """llama.cpp via the ``llama-cpp-python`` Python bindings."""

    backend_id: str = "llamacpp"

    def __init__(
        self,
        *,
        model_path: str,
        n_ctx: int = 8192,
        n_threads: int | None = None,
        sanity_check: bool = True,
        **_extra: Any,
    ) -> None:
        try:
            from llama_cpp import Llama
        except ImportError as e:  # pragma: no cover - env-specific
            msg = "llama-cpp-python is not installed. Run `pip install m6-thesis[inference]`."
            raise RuntimeError(msg) from e

        self.model_id = model_path
        log.info("backend.llamacpp.loading", model_path=model_path, n_ctx=n_ctx)
        self._llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=False,
        )
        log.info("backend.llamacpp.loaded", model_path=model_path)

        if sanity_check:
            self._run_sanity_check()

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

        def _run() -> dict[str, Any]:
            return self._llm.create_completion(  # type: ignore[no-any-return]
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop,
            )

        t0 = time.perf_counter()
        out = await asyncio.get_event_loop().run_in_executor(None, _run)
        wallclock = int((time.perf_counter() - t0) * 1000)
        text = out["choices"][0]["text"]
        usage = out.get("usage", {})
        in_tok = int(usage.get("prompt_tokens", 0))
        out_tok = int(usage.get("completion_tokens", 0))
        return Completion(
            text=text.strip(),
            input_tokens=in_tok,
            output_tokens=out_tok,
            wallclock_ms=wallclock,
            eur_cost=self.cost_eur(in_tok, out_tok),
            finish_reason=out["choices"][0].get("finish_reason", "stop"),
        )

    async def embed(self, _text: str) -> np.ndarray:
        msg = "Use a dedicated embedder for vector search; llama.cpp embeddings are slow."
        raise NotImplementedError(msg)

    def cost_eur(self, input_tokens: int, output_tokens: int) -> float:
        return eur_for_call("local-llamacpp-int4", input_tokens, output_tokens)

    # ------------------------------------------------------------------ #
    # Sanity check (plan risk-register row 4)
    # ------------------------------------------------------------------ #
    def _run_sanity_check(self) -> None:
        """Run the NarrativeQA-shaped mini-eval; refuse to serve traffic if F1
        drops by more than ``SANITY_F1_DROP_THRESHOLD_PP`` percentage points
        from the recorded baseline.

        If no baseline file exists yet, we refuse to start the backend rather
        than compare against a hard-coded placeholder — see ``ADR-003`` and
        ``plan.md`` §7 risk-register row 4.
        """
        baseline = _load_baseline()
        if baseline is None:
            msg = (
                f"Sanity baseline missing at {SANITY_BASELINE_PATH}. "
                f"Run `make baselines-record` (Month 1 task per plan §4.1) to "
                f"populate the 7B/13B reference F1 on the mini-eval set. "
                f"Refusing to start the llama.cpp backend without a baseline "
                f"to compare against — see ADR-003."
            )
            raise RuntimeError(msg)

        log.info("backend.llamacpp.sanity_check.start", n=len(_SANITY_PROMPTS), baseline=baseline)
        f1s: list[float] = []
        for prompt, expected in _SANITY_PROMPTS:
            out = self._llm.create_completion(prompt=prompt, max_tokens=64, temperature=0.0)
            text = out["choices"][0]["text"].strip()
            f1s.append(f1_score(text, expected))
        observed = float(np.mean(f1s))
        ref_f1 = float(baseline.get("ref_f1", 0.0))
        drop_pp = (ref_f1 - observed) * 100.0
        log.info(
            "backend.llamacpp.sanity_check.result",
            observed_f1=observed, baseline_f1=ref_f1, drop_pp=drop_pp,
        )
        if drop_pp > SANITY_F1_DROP_THRESHOLD_PP:
            msg = (
                f"Sanity check failed: F1 dropped by {drop_pp:.2f}pp from baseline "
                f"{ref_f1:.3f}. Refusing to serve traffic. See ADR-003."
            )
            raise RuntimeError(msg)


def _load_baseline() -> dict[str, Any] | None:
    """Load the sanity-baseline JSON if present.

    Expected schema::

        {
            "ref_model": "llama-3.1-8b-instruct",
            "ref_backend": "mlx",
            "ref_f1": 0.41,
            "recorded_at": "2026-06-01T12:00:00Z",
            "n_prompts": 5
        }
    """
    if not SANITY_BASELINE_PATH.exists():
        return None
    try:
        return json.loads(SANITY_BASELINE_PATH.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    except (OSError, json.JSONDecodeError) as e:
        log.warning("backend.llamacpp.baseline_load_failed", error=str(e))
        return None
