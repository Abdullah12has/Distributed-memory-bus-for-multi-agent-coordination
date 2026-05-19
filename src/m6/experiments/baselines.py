"""Month-1 baseline reproduction.

Two artefacts are produced here, both required before the headline runs:

1. **LLMLingua-2 calibration CSVs** at ``results/baselines/lingua2-{dataset}.csv``.
   Plan §4.1 calls for NarrativeQA F1 within 2 pp of reported and HotpotQA F1
   within 3 pp of reported. Targets are configurable so the user can paste in
   the exact numbers from Pan et al. (ACL Findings 2024) Table 2.

2. **Llama.cpp sanity baseline JSON** at ``results/sanity/llamacpp_baseline.json``.
   The :class:`m6.inference.llamacpp_backend.LlamaCppBackend` refuses to start
   at the 70B int4 size unless this file exists; it carries the 7B reference
   F1 over the same five-prompt mini-eval that the backend re-runs at
   startup, so a degraded 70B run is detected before any C1 traffic flows.

The module is intentionally CPU-and-API-friendly: the QA-model side defaults
to ``gpt-4o-mini`` (so it works without local MLX), and the sanity baseline
uses MLX when available and falls back to the same API model with a recorded
note.

Cost envelope (rough, at 0.138 EUR / 1M input + 0.552 EUR / 1M output for
gpt-4o-mini at TalentAdore pricing):

* ~200 NarrativeQA queries × ~3 KB input = ~600 KB ≈ EUR 0.10
* ~200 HotpotQA queries × ~3 KB input  = ~600 KB ≈ EUR 0.10
* Total budget: < EUR 1.

The script is idempotent: re-running overwrites the CSV. Run
``scripts/reproduce_baselines.sh`` (the driver), not this module directly,
unless you want fine-grained control over the calibration subset size.
"""

from __future__ import annotations

import argparse
import asyncio
import dataclasses
import json
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from m6.config.logging import configure_logging, get_logger
from m6.evaluation.metrics.qa import f1_score
from m6.inference import make_backend
from m6.inference.base import InferenceBackend
from m6.utils.io import atomic_write
from m6.utils.seed import seed_all

log = get_logger(__name__)


# --------------------------------------------------------------------------- #
# Config + targets
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class DatasetSpec:
    """One calibration dataset: how to load, which split, sample size, target."""

    name: str
    hf_repo: str
    hf_config: str | None
    split: str
    n_samples: int
    target_f1: float  # the published-paper F1 to compare against
    tolerance_pp: float  # absolute percentage-point tolerance
    text_key: str  # which dataset field is the context to compress
    question_key: str  # which field is the question
    answer_key: str  # which field is the gold answer


@dataclass(frozen=True)
class BaselineConfig:
    """Top-level reproduction config; loaded from configs/experiments/baselines.yaml."""

    datasets: tuple[DatasetSpec, ...]
    compression_ratio: float = 4.0
    qa_backend: str = "ollama"  # local-default; "openai" is opt-in
    qa_model: str = "llama3.1:8b-instruct-q4_K_M"
    seed: int = 0

    # 7B sanity baseline (for the 70B startup check).
    sanity_backend: str = "ollama"  # local-default
    sanity_model: str = "llama3.1:8b-instruct-q4_K_M"
    sanity_out_path: str = "results/sanity/llamacpp_baseline.json"

    # Output directory for the per-dataset CSVs.
    out_dir: str = "results/baselines"

    @classmethod
    def from_yaml(cls, path: Path | str) -> BaselineConfig:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        ds_list: list[DatasetSpec] = []
        for d in data.get("datasets", []):
            ds_list.append(DatasetSpec(**d))
        scalar_keys = {f.name for f in dataclasses.fields(cls)} - {"datasets"}
        scalars = {k: v for k, v in data.items() if k in scalar_keys}
        return cls(datasets=tuple(ds_list), **scalars)


# --------------------------------------------------------------------------- #
# Calibration record
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class CalibrationResult:
    dataset: str
    n_samples: int
    target_f1: float
    tolerance_pp: float
    observed_f1: float
    drop_pp: float
    pass_fail: str  # "PASS" | "FAIL"
    eur_cost: float
    wallclock_s: float


# --------------------------------------------------------------------------- #
# Sanity prompt-set (must match LlamaCppBackend's _SANITY_PROMPTS verbatim)
# --------------------------------------------------------------------------- #
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
        "Passage: Water boils at 100 degrees Celsius at sea level.\n"
        "Question: At what temperature does water boil at sea level?\nAnswer:",
        "100 degrees Celsius",
    ),
    (
        "Passage: The Moon orbits the Earth.\nQuestion: What does the Moon orbit?\nAnswer:",
        "the Earth",
    ),
]


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Month-1 baseline reproduction (LLMLingua-2 + sanity baseline)."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML config (e.g. configs/experiments/baselines.yaml).",
    )
    parser.add_argument(
        "--skip-calibration",
        action="store_true",
        help="Skip the LLMLingua-2 calibration (only produce sanity baseline JSON).",
    )
    parser.add_argument(
        "--skip-sanity",
        action="store_true",
        help="Skip producing the sanity baseline JSON (only run calibration).",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help=(
            "Fast end-to-end sanity run: limits each dataset to 2 examples and "
            "disables the tolerance gate, so the script always exits 0 if the "
            "pipeline is wired correctly. Use this before the 2–3h full run to "
            "verify Ollama / LLMLingua-2 device / dataset extraction all work."
        ),
    )
    args = parser.parse_args(argv)

    configure_logging()
    cfg = BaselineConfig.from_yaml(args.config)
    if args.smoke:
        cfg = _apply_smoke_overrides(cfg)
        log.warning(
            "baselines.smoke_mode",
            note=(
                "--smoke is ON: 2 examples/dataset, tolerance gate disabled, "
                "every observed F1 is reported but no exit-1 failure on miss."
            ),
        )
    seed_all(cfg.seed)

    overall_ok = True

    if not args.skip_calibration:
        try:
            results = asyncio.run(_run_calibration(cfg))
            if not args.smoke:
                overall_ok = overall_ok and all(r.pass_fail == "PASS" for r in results)
            else:
                # In smoke mode, just log the F1s — never fail the run.
                for r in results:
                    log.info(
                        "baselines.smoke.dataset_done",
                        dataset=r.dataset,
                        observed_f1=r.observed_f1,
                        n_samples=r.n_samples,
                        eur_cost=r.eur_cost,
                    )
        except Exception:
            log.exception("baselines.calibration_failed")
            overall_ok = False

    if not args.skip_sanity:
        try:
            asyncio.run(_record_sanity_baseline(cfg))
        except Exception:
            log.exception("baselines.sanity_failed")
            overall_ok = False

    if overall_ok:
        log.info("baselines.done", status="PASS", smoke=args.smoke)
        return 0
    log.error(
        "baselines.done",
        status="FAIL",
        action=(
            "Stop and tell Lauri before proceeding to ICAE training. "
            "See results/baselines/*.csv for per-dataset details."
        ),
    )
    return 1


# --------------------------------------------------------------------------- #
# Calibration loop
# --------------------------------------------------------------------------- #
async def _run_calibration(cfg: BaselineConfig) -> list[CalibrationResult]:
    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    backend = make_backend(cfg.qa_backend, model=cfg.qa_model)
    compressor = _make_lingua2(target_ratio=cfg.compression_ratio)

    results: list[CalibrationResult] = []
    for ds in cfg.datasets:
        log.info("baselines.dataset.start", dataset=ds.name, n=ds.n_samples)
        samples = _load_dataset(ds)
        result = await _calibrate_one(
            ds,
            samples=samples,
            compressor=compressor,
            backend=backend,
            ratio=cfg.compression_ratio,
            out_dir=out_dir,
        )
        results.append(result)
        log.info(
            "baselines.dataset.done",
            dataset=ds.name,
            observed_f1=result.observed_f1,
            target_f1=result.target_f1,
            drop_pp=result.drop_pp,
            pass_fail=result.pass_fail,
        )
    return results


async def _calibrate_one(
    ds: DatasetSpec,
    *,
    samples: list[dict[str, Any]],
    compressor: Any,
    backend: InferenceBackend,
    ratio: float,
    out_dir: Path,
) -> CalibrationResult:
    """Run LLMLingua-2 compression + QA on one dataset, return pass/fail."""
    from m6.memory_bus.schemas import Classification, Fragment, TagVector

    rows: list[dict[str, Any]] = []
    t_start = time.perf_counter()
    total_cost = 0.0

    for i, ex in enumerate(samples):
        try:
            context = _extract_text(ex, ds.text_key)
            question = _extract_text(ex, ds.question_key)
        except (KeyError, TypeError, AttributeError) as e:
            log.warning("baselines.skip_malformed_row", idx=i, dataset=ds.name, error=str(e))
            continue
        gold_raw = _resolve_path(ex, ds.answer_key)
        gold = _normalize_gold(gold_raw)
        if not gold or not context or not question:
            continue
        # Truncate to Fragment's pydantic limit (200K chars) with a comfortable
        # margin; LLMLingua-2's effective window is ~4K tokens anyway, and
        # full NarrativeQA books run to ~500K chars.
        if len(context) > 100_000:
            context = context[:100_000]

        # Compress with LLMLingua-2 at the target ratio.
        frag = Fragment(
            fragment_id=f"{ds.name}-{i:05d}",
            text=context,
            tags=TagVector(acl_mask=0, classification=Classification.PUBLIC),
            task_hint=question,
        )
        slot = compressor.compress(frag, target_ratio=ratio)
        compressed_text = compressor.decompress(slot) or context

        # Ask the QA model.
        prompt = (
            "Answer the question using ONLY the provided context. Give the "
            "shortest correct answer (a single token, name, or noun phrase).\n\n"
            f"Context:\n{compressed_text}\n\nQuestion: {question}\nAnswer:"
        )
        completion = await backend.complete(prompt, max_tokens=64, temperature=0.0)
        pred = completion.text.strip()

        f1 = f1_score(pred, gold)
        rows.append(
            {
                "dataset": ds.name,
                "idx": i,
                "ratio": ratio,
                "f1": f1,
                "pred": pred[:240],
                "gold": gold[:240],
                "eur_cost": completion.eur_cost,
            }
        )
        total_cost += completion.eur_cost

    wallclock_s = time.perf_counter() - t_start
    df = pd.DataFrame(rows)
    csv_path = out_dir / f"lingua2-{ds.name}.csv"
    df.to_csv(csv_path, index=False)
    log.info("baselines.calibration.written", path=str(csv_path), n_rows=len(df))

    observed_f1 = float(df["f1"].mean()) if not df.empty else 0.0
    drop_pp = (ds.target_f1 - observed_f1) * 100.0
    pass_fail = "PASS" if abs(drop_pp) <= ds.tolerance_pp else "FAIL"

    return CalibrationResult(
        dataset=ds.name,
        n_samples=len(df),
        target_f1=ds.target_f1,
        tolerance_pp=ds.tolerance_pp,
        observed_f1=observed_f1,
        drop_pp=drop_pp,
        pass_fail=pass_fail,
        eur_cost=total_cost,
        wallclock_s=wallclock_s,
    )


# --------------------------------------------------------------------------- #
# Sanity baseline
# --------------------------------------------------------------------------- #
async def _record_sanity_baseline(cfg: BaselineConfig) -> None:
    """Run the 5 SANITY_PROMPTS through the reference backend and record F1.

    The resulting JSON is consumed by LlamaCppBackend at 70B startup; the
    backend refuses to serve traffic if its observed F1 on the same prompt set
    is more than 5 pp below ``ref_f1``.
    """
    backend = make_backend(cfg.sanity_backend, model=cfg.sanity_model)
    f1s: list[float] = []
    for prompt, expected in _SANITY_PROMPTS:
        completion = await backend.complete(prompt, max_tokens=64, temperature=0.0)
        f1s.append(f1_score(completion.text, expected))
    import statistics

    ref_f1 = float(statistics.mean(f1s)) if f1s else 0.0
    payload = {
        "ref_model": cfg.sanity_model,
        "ref_backend": cfg.sanity_backend,
        "ref_f1": ref_f1,
        "n_prompts": len(_SANITY_PROMPTS),
        "recorded_at": datetime.now(UTC).isoformat(),
        "per_prompt_f1": f1s,
        "note": (
            "F1 over the m6.inference.llamacpp_backend._SANITY_PROMPTS mini-eval. "
            "LlamaCppBackend refuses to serve at 70B int4 if observed F1 is more "
            "than 5 pp below this number."
        ),
    }
    out_path = Path(cfg.sanity_out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with atomic_write(out_path, mode="w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
    log.info("baselines.sanity.written", path=str(out_path), ref_f1=ref_f1)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _make_lingua2(target_ratio: float) -> Any:
    """Build the LLMLingua-2 compressor with a clean error if the package is missing."""
    try:
        from m6.compressors.lingua2 import LLMLingua2Compressor

        return LLMLingua2Compressor(target_ratio=target_ratio)
    except ImportError as e:
        msg = (
            "llmlingua is not installed. Run `pip install m6-thesis[torch]` "
            "before invoking the baseline reproduction."
        )
        raise RuntimeError(msg) from e


def _load_dataset(ds: DatasetSpec) -> list[dict[str, Any]]:
    """Load the first ``n_samples`` examples from a HuggingFace dataset.

    For NarrativeQA / HotpotQA the gold-answer field is sometimes a list of
    strings; we flatten to the longest gold answer.
    """
    try:
        from datasets import load_dataset
    except ImportError as e:
        msg = (
            "The `datasets` package is not installed. "
            "Run `pip install m6-thesis[torch]` before reproduction."
        )
        raise RuntimeError(msg) from e

    log.info("baselines.dataset.loading", dataset=ds.name, repo=ds.hf_repo, split=ds.split)
    if ds.hf_config:
        d = load_dataset(ds.hf_repo, ds.hf_config, split=ds.split, streaming=True)
    else:
        d = load_dataset(ds.hf_repo, split=ds.split, streaming=True)

    out: list[dict[str, Any]] = []
    for row in d:
        out.append(row)
        if len(out) >= ds.n_samples:
            break
    return out


def _apply_smoke_overrides(cfg: BaselineConfig) -> BaselineConfig:
    """Return a copy of ``cfg`` with every dataset's n_samples clamped to 2
    and the tolerance opened wide so the run can never fail.

    Used by ``--smoke``. Keeps everything else identical so the run still
    exercises the LLMLingua-2 device, the dataset extraction path, the
    Ollama backend, and the sanity-baseline write.
    """
    new_datasets = tuple(
        dataclasses.replace(d, n_samples=2, tolerance_pp=100.0) for d in cfg.datasets
    )
    return dataclasses.replace(cfg, datasets=new_datasets)


def _resolve_path(row: Any, path: str) -> Any:
    """Walk a dotted path through nested dicts.

    ``_resolve_path(row, "document.summary.text")`` returns
    ``row["document"]["summary"]["text"]``. Used to drill into the nested
    schemas of NarrativeQA and HotpotQA.
    """
    cur: Any = row
    for part in path.split("."):
        cur = cur[part] if isinstance(cur, dict) else getattr(cur, part)
    return cur


def _extract_text(row: Any, key: str) -> str:
    """Extract the *text* field from a dataset row.

    Handles three shapes:

    * **Dotted path** (default): ``"document.summary.text"`` for NarrativeQA,
      ``"question.text"`` for NarrativeQA questions.
    * **Plain key** for simple-string fields (``"question"`` in HotpotQA).
    * **Special sentinel ``__hotpot_context__``** for HotpotQA's
      ``{title: [...], sentences: [[...]]}`` shape — concatenated into one
      readable passage.
    """
    if key == "__hotpot_context__":
        return _flatten_hotpot_context(row.get("context", {}))
    value = _resolve_path(row, key)
    if isinstance(value, str):
        return value
    # NarrativeQA's `answers` field is sometimes routed here by mistake;
    # flatten to the first textual answer rather than stringify the dict.
    if isinstance(value, list) and value and isinstance(value[0], dict) and "text" in value[0]:
        return str(value[0]["text"])
    return str(value)


def _flatten_hotpot_context(context: dict[str, Any]) -> str:
    """Flatten HotpotQA's `context = {title: [...], sentences: [[...], [...]]}`
    into a single readable passage of the form::

        [<title-0>] <s0> <s1> ...
        [<title-1>] <s0> <s1> ...
    """
    titles = context.get("title", []) or []
    sentences = context.get("sentences", []) or []
    if not titles or not sentences:
        return ""
    blocks: list[str] = []
    for title, sents in zip(titles, sentences, strict=False):
        block = f"[{title}] " + " ".join(s for s in sents if isinstance(s, str))
        blocks.append(block)
    return "\n".join(blocks)


def _normalize_gold(gold: Any) -> str:
    """Flatten gold-answer field to a single string."""
    if isinstance(gold, str):
        return gold
    if isinstance(gold, list):
        if not gold:
            return ""
        first = gold[0]
        if isinstance(first, dict):
            # NarrativeQA shape: list[{"text": "...", "tokens": [...]}]
            return str(first.get("text", first.get("tokens", "")))
        if isinstance(first, str):
            return str(max(gold, key=len))
        return str(first)
    if isinstance(gold, dict):
        # HotpotQA shape: {"answer": "..."} or {"text": [...], "answer_start": [...]}
        if "answer" in gold:
            return str(gold["answer"])
        if "text" in gold:
            text = gold["text"]
            return str(text[0]) if isinstance(text, list) and text else str(text)
    return str(gold)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
