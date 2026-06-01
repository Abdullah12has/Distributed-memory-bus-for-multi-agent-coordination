#!/usr/bin/env python3
"""Frontier model cliff sweep — validates coordination cliff on large models.

Tests whether the coordination cliff discovered on local models (1.5B-14B)
also appears on frontier-class models via an OpenAI-compatible API. This
validates Theorem 1(iii): cliff position depends on the compressor, not the model.

Supports any OpenAI-compatible endpoint (OpenAI, Featherless, Together, etc.)
via OPENAI_BASE_URL and OPENAI_API_KEY environment variables.

Default: Featherless API with Qwen2.5-72B-Instruct.

Run:
    FEATHERLESS_API_KEY=xxx python -m m6.experiments.run_frontier
    FEATHERLESS_API_KEY=xxx python -m m6.experiments.run_frontier --smoke
    FEATHERLESS_API_KEY=xxx python -m m6.experiments.run_frontier --model meta-llama/Llama-3.3-70B-Instruct
    OPENAI_API_KEY=xxx OPENAI_BASE_URL=https://api.openai.com/v1 python -m m6.experiments.run_frontier --model gpt-4o-mini
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from m6.benchmark.generator import load as load_benchmark
from m6.benchmark.schemas import Workload
from m6.compressors import make_compressor
from m6.compressors.cache import CompressionCache, make_cached_compressor
from m6.experiments.run_h5 import (
    _score_family_a,
    _score_family_b,
    _score_family_c,
    fit_piecewise,
)


# ============================================================================
# Config
# ============================================================================
@dataclass
class FrontierConfig:
    benchmark_path: str = "data/processed/c1-v0.1"
    compressor: str = "lingua2"
    model: str = "Qwen/Qwen2.5-72B-Instruct"
    api_base: str | None = None  # auto-detect from env
    api_key: str | None = None   # auto-detect from env
    ratios: list[float] | None = None
    seeds: list[int] | None = None
    families: list[str] | None = None
    n_workloads: int = 10
    synth_results_path: str | None = None
    out_dir: str = "results/frontier"
    cache_path: str | None = None
    priors: bool = False  # E3: add a fragments-blanked PRIORS condition (ratio sentinel 999.0)
    request_delay: float = 0.4  # inter-call pacing (s) to stay under Featherless rate limit

    def __post_init__(self):
        if self.ratios is None:
            self.ratios = [1.0, 2.0, 3.0, 4.0, 6.0, 8.0]
        if self.seeds is None:
            self.seeds = [0, 1, 2]
        if self.families is None:
            self.families = ["a"]

    @classmethod
    def smoke(cls) -> FrontierConfig:
        return cls(
            ratios=[1.0, 4.0],
            seeds=[0],
            n_workloads=2,
            out_dir="results/frontier_smoke",
        )


# ============================================================================
# OpenAI planner
# ============================================================================
def _format_hint(workload: Workload) -> str:
    fam = workload.family.value
    if fam == "a":
        return 'Use exactly this format: "ANSWER: hours=<total_hours>;budget=<total_budget>" (integers only, no currency symbols).'
    elif fam == "b":
        return 'Use exactly this format: "ANSWER: sub-0=worker-X;sub-1=worker-Y;..." listing every sub-task assignment.'
    else:
        return 'Use exactly this format: "ANSWER: FINAL-<number>" with the leaf value.'


def _resolve_api_config(
    api_base: str | None = None, api_key: str | None = None
) -> tuple[str, str]:
    """Resolve API base URL and key from args or environment.

    Priority: explicit args > FEATHERLESS_ env > OPENAI_ env.
    Default: Featherless API.
    """
    base = api_base
    key = api_key
    if not base:
        base = os.environ.get(
            "OPENAI_BASE_URL",
            os.environ.get("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"),
        )
    if not key:
        key = os.environ.get("OPENAI_API_KEY", "") or os.environ.get("FEATHERLESS_API_KEY", "")
    # Strip trailing /chat/completions if user included it
    base = base.rstrip("/")
    if base.endswith("/chat/completions"):
        base = base.rsplit("/chat/completions", 1)[0]
    if not key:
        raise RuntimeError(
            "No API key found. Set FEATHERLESS_API_KEY or OPENAI_API_KEY."
        )
    return base, key


def openai_planner_solve(
    model: str,
    workload: Workload,
    compressed_texts: dict[str, str],
    seed: int = 0,
    api_key: str | None = None,
    api_base: str | None = None,
) -> dict:
    """Ask a model to solve the workload via any OpenAI-compatible API."""
    import httpx

    base, key = _resolve_api_config(api_base, api_key)

    fragments_text = "\n\n".join(
        f"[{fid}] {text}" for fid, text in compressed_texts.items()
    )
    format_hint = _format_hint(workload)
    user_msg = f"""You are a planner in a multi-agent system. Your task:

{workload.initial_prompt}

Available information:
{fragments_text}

Instructions:
1. Read all fragments carefully.
2. Provide your final answer on a SINGLE line starting with "ANSWER: ".
{format_hint}

Your response:"""

    # Retry with exponential backoff on 429 (rate limit) and 5xx. Featherless
    # throttles aggressively under concurrent load, and an un-retried 429
    # returns an empty response that scores as coord_success=0 — silently
    # corrupting the cliff curve. Backoff makes each cell robust.
    import time as _time
    response = ""
    input_tokens = output_tokens = 0
    max_attempts = 6
    for attempt in range(max_attempts):
        try:
            resp = httpx.post(
                f"{base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a precise assistant. Always respond with exactly one line starting with ANSWER: in the requested format. Do not explain your reasoning."},
                        {"role": "user", "content": user_msg},
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.1,
                    "seed": seed,
                },
                timeout=180.0,
            )
            if resp.status_code == 429 or resp.status_code >= 500:
                wait = 2 ** attempt
                if attempt < max_attempts - 1:
                    print(f"  [retry] {resp.status_code} attempt {attempt+1}/{max_attempts}, "
                          f"sleeping {wait}s", file=sys.stderr)
                    _time.sleep(wait)
                    continue
            resp.raise_for_status()
            data = resp.json()
            response = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            break
        except Exception as e:  # noqa: BLE001
            wait = 2 ** attempt
            if attempt < max_attempts - 1:
                print(f"  [retry] exception attempt {attempt+1}/{max_attempts} "
                      f"({type(e).__name__}), sleeping {wait}s", file=sys.stderr)
                _time.sleep(wait)
                continue
            print(f"  [warn] API exception after {max_attempts} attempts ({base}): {e}",
                  file=sys.stderr)
            response = ""
            input_tokens = output_tokens = 0

    # Extract answer
    answer = ""
    for line in response.split("\n"):
        if line.strip().upper().startswith("ANSWER:"):
            answer = line.split(":", 1)[1].strip()
            break
    if not answer:
        answer = response[:200]

    # Score
    coord_success, f1 = _score_answer(workload, answer)

    return {
        "answer": answer,
        "coord_success": coord_success,
        "f1": f1,
        "raw_response": response[:500],
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


def _score_answer(workload: Workload, answer: str) -> tuple[float, float]:
    fam = workload.family.value
    if fam == "a":
        return _score_family_a(workload.expected_answer, answer)
    elif fam == "b":
        return _score_family_b(workload, answer)
    return _score_family_c(workload.expected_answer, answer)


# ============================================================================
# Main
# ============================================================================
def run_frontier(cfg: FrontierConfig) -> pd.DataFrame:
    print(f"Loading benchmark from {cfg.benchmark_path}...")
    all_workloads = load_benchmark(cfg.benchmark_path)
    family_set = set(cfg.families)
    workloads = []
    for fam in sorted(family_set):
        fam_ws = [w for w in all_workloads if w.family.value == fam]
        workloads.extend(fam_ws[: cfg.n_workloads])
    print(f"  {len(workloads)} workloads loaded")

    # Load precomputed cache if provided
    ext_cache: CompressionCache | None = None
    if cfg.cache_path:
        ext_cache = CompressionCache.load(cfg.cache_path)

    # Pre-compress
    comp_cache: dict[float, Any] = {}
    compressed_cache: dict[tuple[float, str], str] = {}
    print(f"  Pre-compressing for {len(cfg.ratios)} ratios...")
    for ratio in cfg.ratios:
        for w in workloads:
            for frag in w.fragments:
                key = (ratio, frag.fragment_id)
                if key not in compressed_cache:
                    # Try precomputed cache first.
                    if ext_cache is not None:
                        cached = ext_cache.lookup(cfg.compressor, ratio, frag.fragment_id, w.initial_prompt)
                        if cached is not None:
                            compressed_cache[key] = cached
                            continue
                    # Cache miss — instantiate the compressor LAZILY (this is what
                    # loads LLMLingua onto the GPU). With a complete cache no model
                    # is ever loaded, so the frontier arm is pure-API and does not
                    # contend for GPU memory with other jobs.
                    if ratio not in comp_cache:
                        comp_cache[ratio] = make_compressor(cfg.compressor, target_ratio=ratio)
                    comp = comp_cache[ratio]
                    fh = frag.model_copy(update={"task_hint": w.initial_prompt})
                    slot = comp.compress(fh)
                    compressed_cache[key] = comp.decompress(slot) or frag.text
    print(f"  Cached {len(compressed_cache)} fragments")

    rows: list[dict[str, Any]] = []
    total = len(cfg.ratios) * len(workloads) * len(cfg.seeds)
    done = 0
    t_start = time.time()
    total_cost = 0.0

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Warm-up: Featherless throttles the first burst of a cold connection, which
    # otherwise wipes out whichever ratio is processed first (observed: ratio 1.0
    # lost 79% of calls to empty responses while every later ratio was clean).
    # Fire throwaway calls until several succeed in a row before the real sweep.
    if workloads:
        warm_w = workloads[0]
        warm_texts = {f.fragment_id: f.text for f in warm_w.fragments}
        ok_streak = 0
        for i in range(40):
            r = openai_planner_solve(cfg.model, warm_w, warm_texts, seed=0,
                                     api_key=cfg.api_key, api_base=cfg.api_base)
            time.sleep(cfg.request_delay)
            ok_streak = ok_streak + 1 if r.get("input_tokens", 0) > 0 else 0
            if ok_streak >= 5:
                break
        print(f"  Warm-up done ({i+1} calls, streak {ok_streak})")

    for ratio in cfg.ratios:
        for w in workloads:
            compressed_texts = {
                frag.fragment_id: compressed_cache[(ratio, frag.fragment_id)]
                for frag in w.fragments
            }
            for seed in cfg.seeds:
                result = openai_planner_solve(
                    cfg.model, w, compressed_texts, seed=seed,
                    api_key=cfg.api_key, api_base=cfg.api_base,
                )
                # Self-rate-limit: Featherless throttles a sustained single
                # stream at the account level (~a few req/s). A small fixed
                # delay keeps us under the limit so 429 backoff never triggers,
                # which is far faster end-to-end than retrying after throttling.
                time.sleep(cfg.request_delay)

                # Estimate cost
                from m6.pipelines.cost_model import PRICING
                price = PRICING.get(cfg.model)
                if price:
                    call_cost = (
                        result["input_tokens"] / 1e6 * price.input_eur
                        + result["output_tokens"] / 1e6 * price.output_eur
                    )
                    total_cost += call_cost

                rows.append({
                    "model": cfg.model,
                    "compressor": cfg.compressor,
                    "ratio": ratio,
                    "family": w.family.value,
                    "workload_id": w.workload_id,
                    "seed": seed,
                    "coord_success": result["coord_success"],
                    "f1": result["f1"],
                    "input_tokens": result["input_tokens"],
                    "output_tokens": result["output_tokens"],
                })
                done += 1
                if done % 10 == 0 or done == total:
                    elapsed = time.time() - t_start
                    eta = (elapsed / done) * (total - done) if done > 0 else 0
                    print(
                        f"    [{done}/{total}] {elapsed:.0f}s, ETA {eta:.0f}s, "
                        f"cost EUR {total_cost:.4f}"
                    )
                    sys.stdout.flush()

                # Incremental save
                if done % 50 == 0:
                    pd.DataFrame(rows).to_csv(out_dir / "results.partial.csv", index=False)

    # E3: PRIORS condition — blank every fragment so the planner answers from
    # the prompt alone. Recorded at ratio sentinel 999.0. Comparing the
    # planner's accuracy at high compression (q->0) against this priors-only
    # rate is the operational test of the calibrated regime's second condition
    # (section 4.4.3): a planner is OUT of regime if its q->0 accuracy exceeds
    # priors + slack, i.e. it recovers sub-threshold information by reasoning.
    if cfg.priors:
        print("  PRIORS condition (all fragments blanked)...")
        for w in workloads:
            blanked = {frag.fragment_id: "[redacted]" for frag in w.fragments}
            for seed in cfg.seeds:
                result = openai_planner_solve(
                    cfg.model, w, blanked, seed=seed,
                    api_key=cfg.api_key, api_base=cfg.api_base,
                )
                rows.append({
                    "model": cfg.model,
                    "compressor": cfg.compressor,
                    "ratio": 999.0,
                    "family": w.family.value,
                    "workload_id": w.workload_id,
                    "seed": seed,
                    "coord_success": result["coord_success"],
                    "f1": result["f1"],
                    "input_tokens": result["input_tokens"],
                    "output_tokens": result["output_tokens"],
                })

    return pd.DataFrame(rows)


def _compute_api_cost(df: pd.DataFrame) -> float:
    """Compute total API cost using model-specific pricing."""
    if df.empty:
        return 0.0
    from m6.pipelines.cost_model import PRICING
    model = df["model"].iloc[0]
    price = PRICING.get(model)
    if not price:
        return 0.0
    return float(
        df["input_tokens"].sum() / 1e6 * price.input_eur
        + df["output_tokens"].sum() / 1e6 * price.output_eur
    )


def _bootstrap_tau(
    df: pd.DataFrame,
    n_boot: int = 500,
    seed: int = 0,
) -> dict:
    """Bootstrap a CI on tau by resampling workloads.

    Why workloads (not individual rows): workloads are the natural unit of
    independent variability — each is a distinct task instance. Resampling
    rows (workload × ratio × seed) would underestimate variance because
    rows from the same workload are correlated. Resampling seeds alone
    (3 seeds) gives too few independent draws.

    Returns dict with tau_ci, tau_median, n_boot_valid (number of
    bootstrap samples where fit_piecewise produced a finite tau).
    """
    if df.empty or "workload_id" not in df.columns:
        return {"tau_median": float("nan"), "tau_ci_low": float("nan"),
                "tau_ci_high": float("nan"), "n_boot_valid": 0}

    workloads = df["workload_id"].unique()
    rng = np.random.default_rng(seed)
    taus: list[float] = []
    for _ in range(n_boot):
        sampled = rng.choice(workloads, size=len(workloads), replace=True)
        sub = pd.concat([df[df["workload_id"] == w] for w in sampled])
        agg = sub.groupby("ratio")["coord_success"].mean().reset_index()
        if len(agg) < 3:
            continue
        try:
            fit = fit_piecewise(agg["ratio"].to_numpy(),
                                agg["coord_success"].to_numpy())
            t = fit.get("tau", float("nan"))
            if not np.isnan(t) and np.isfinite(t):
                taus.append(float(t))
        except Exception:
            continue

    if not taus:
        return {"tau_median": float("nan"), "tau_ci_low": float("nan"),
                "tau_ci_high": float("nan"), "n_boot_valid": 0}
    arr = np.array(taus)
    return {
        "tau_median": float(np.median(arr)),
        "tau_ci_low": float(np.percentile(arr, 2.5)),
        "tau_ci_high": float(np.percentile(arr, 97.5)),
        "n_boot_valid": len(taus),
    }


def compute_frontier_verdict(
    df: pd.DataFrame, synth_results_path: str | None
) -> dict:
    """Compare frontier cliff to local model cliff.

    Reports both the point estimate of tau (from pooled ratio-means) and
    a bootstrap CI (resampling workloads). The CI catches the fragility
    flagged in the audit: with n=10 workloads × 6 ratios × 3 seeds, a
    single workload's outcome can shift tau by 3× — the CI quantifies
    this.
    """
    # Drop failed API calls (empty response -> input_tokens==0). A throttled or
    # errored call is MISSING DATA, not a coordination failure; counting it as
    # coord_success=0 silently corrupts the cliff curve (e.g. a cold-start
    # throttle that only hits the first ratio processed). Also separate the
    # PRIORS condition (ratio sentinel 999) from the cliff fit.
    if "input_tokens" in df.columns:
        df = df[df["input_tokens"] > 0].copy()
    priors_df = df[df["ratio"] >= 999.0]
    df = df[df["ratio"] < 999.0]
    agg = df.groupby("ratio")["coord_success"].mean().reset_index()
    frontier_fit = fit_piecewise(
        agg["ratio"].to_numpy(), agg["coord_success"].to_numpy()
    )
    frontier_curve = {
        str(r): float(s) for r, s in zip(agg["ratio"], agg["coord_success"])
    }

    tau_boot = _bootstrap_tau(df)

    verdict: dict[str, Any] = {
        "model": df["model"].iloc[0] if not df.empty else "unknown",
        "frontier_tau": frontier_fit["tau"],
        "frontier_tau_ci": [tau_boot["tau_ci_low"], tau_boot["tau_ci_high"]],
        "frontier_tau_median_boot": tau_boot["tau_median"],
        "frontier_tau_boot_n": tau_boot["n_boot_valid"],
        "frontier_drop_rel": frontier_fit["drop_rel"],
        "frontier_curve": frontier_curve,
        "frontier_baseline_coord": float(
            df[df["ratio"] == 1.0]["coord_success"].mean()
        ) if not df[df["ratio"] == 1.0].empty else float("nan"),
        "priors_coord": float(priors_df["coord_success"].mean()) if not priors_df.empty else None,
        "high_ratio_coord": float(df[df["ratio"] == df["ratio"].max()]["coord_success"].mean()) if not df.empty else float("nan"),
        "total_api_cost_eur": _compute_api_cost(df),
    }

    if not synth_results_path:
        verdict["comparison"] = None
        verdict["note"] = "No synthetic results for comparison."
        return verdict

    synth_csv = Path(synth_results_path) / "results.csv"
    if not synth_csv.exists():
        # Try sweep_results.csv (H1/H2 format)
        synth_csv = Path(synth_results_path) / "sweep_results.csv"
    if not synth_csv.exists():
        verdict["comparison"] = None
        verdict["note"] = f"Synthetic results not found at {synth_results_path}"
        return verdict

    synth_df = pd.read_csv(synth_csv)
    # Filter to family-a, 8B model (or lingua2 compressor for H1/H2)
    if "planner_model" in synth_df.columns:
        synth_df = synth_df[
            (synth_df["family"] == "a") & (synth_df["planner_model"] == "8B")
        ]
    elif "family" in synth_df.columns:
        synth_df = synth_df[
            (synth_df["family"] == "a") & (synth_df["compressor"] == "lingua2")
        ]

    if synth_df.empty:
        verdict["comparison"] = None
        verdict["note"] = "No matching synthetic family-a data."
        return verdict

    synth_agg = synth_df.groupby("ratio")["coord_success"].mean().reset_index()
    synth_fit = fit_piecewise(
        synth_agg["ratio"].to_numpy(), synth_agg["coord_success"].to_numpy()
    )

    tau_f = frontier_fit["tau"]
    tau_s = synth_fit["tau"]

    if np.isnan(tau_f) or np.isnan(tau_s) or tau_s == 0:
        tau_diff_pct = float("nan")
        tau_match_point = False
        tau_ci_contains_synth = False
    else:
        tau_diff_pct = abs(tau_f - tau_s) / abs(tau_s) * 100
        tau_match_point = tau_diff_pct <= 25.0  # 25% tolerance, point estimate
        # CI-based match: does the bootstrap CI on frontier tau contain
        # synth_tau? This is more robust than the point-estimate diff,
        # since with n=10 workloads a single outcome can flip tau by 3×.
        ci_lo = tau_boot["tau_ci_low"]
        ci_hi = tau_boot["tau_ci_high"]
        if np.isnan(ci_lo) or np.isnan(ci_hi):
            tau_ci_contains_synth = False
        else:
            tau_ci_contains_synth = bool(ci_lo <= tau_s <= ci_hi)

    verdict["comparison"] = {
        "synth_tau": synth_fit["tau"],
        "synth_drop_rel": synth_fit["drop_rel"],
        "tau_diff_pct": tau_diff_pct,
        "tau_match_point": tau_match_point,
        "tau_ci_contains_synth": tau_ci_contains_synth,
        "tau_match": tau_match_point,  # back-compat alias
        "theorem_validated": tau_ci_contains_synth,  # now uses CI, not point
        "note": (
            "Theorem 1(iii) validated: bootstrap CI on frontier tau contains synth tau."
            if tau_ci_contains_synth
            else (
                "Cliff position differs even after accounting for bootstrap uncertainty. "
                "Point estimate within 25% but CI excludes synth tau — possible cherry-pick "
                "from limited workload count."
                if tau_match_point
                else "Cliff position differs — may indicate model-dependent theta"
            )
        ),
    }

    return verdict


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv not installed — rely on env vars being set

    parser = argparse.ArgumentParser(description="Frontier model cliff sweep")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--out", type=str, default=None)
    parser.add_argument("--model", type=str, default=None,
                        help="Model name (default: Qwen/Qwen2.5-72B-Instruct)")
    parser.add_argument("--api-base", type=str, default=None,
                        help="API base URL (default: auto-detect from env)")
    parser.add_argument("--synth-results", type=str, default=None)
    parser.add_argument("--cache", type=str, default=None, help="Path to precomputed compression cache JSON")
    parser.add_argument("--n-workloads", type=int, default=None,
                        help="Workloads per family (default 10). E2 powered sweep uses 40.")
    parser.add_argument("--seeds", type=str, default=None,
                        help="Comma-separated planner seeds (default 0,1,2). E2 uses 0,1,2,3,4.")
    parser.add_argument("--ratios", type=str, default=None,
                        help="Comma-separated compression ratios (default 1,2,3,4,6,8).")
    parser.add_argument("--delay", type=float, default=None,
                        help="Inter-call pacing in seconds (default 0.4; use 1.0-1.5 for throttled models).")
    parser.add_argument("--priors", action="store_true",
                        help="E3: also run a PRIORS condition (fragments blanked) to measure "
                             "q->0 recovery vs priors-only baseline for the calibrated-regime test.")
    args = parser.parse_args()

    cfg = FrontierConfig.smoke() if args.smoke else FrontierConfig()
    if args.out:
        cfg.out_dir = args.out
    if args.model:
        cfg.model = args.model
    if args.api_base:
        cfg.api_base = args.api_base
    if args.synth_results:
        cfg.synth_results_path = args.synth_results
    if args.cache:
        cfg.cache_path = args.cache
    if args.n_workloads:
        cfg.n_workloads = args.n_workloads
    if args.seeds:
        cfg.seeds = [int(s) for s in args.seeds.split(",")]
    if args.ratios:
        cfg.ratios = [float(r) for r in args.ratios.split(",")]
    cfg.priors = bool(args.priors)
    if args.delay is not None:
        cfg.request_delay = args.delay

    # Validate API key is available
    try:
        base, _ = _resolve_api_config(cfg.api_base, cfg.api_key)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print("=" * 60)
    print("Frontier Model Cliff Sweep")
    print("=" * 60)
    print(f"Model: {cfg.model}")
    print(f"API: {base}")
    print(f"Compressor: {cfg.compressor}")
    print(f"Ratios: {cfg.ratios}")
    print(f"Seeds: {cfg.seeds}")
    print(f"Workloads: {cfg.n_workloads}")
    print(f"Output: {cfg.out_dir}")
    print()

    df = run_frontier(cfg)
    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "results.csv", index=False)
    print(f"\nSaved {len(df)} rows to {out_dir / 'results.csv'}")

    # Summary
    print("\nCoord success by ratio:")
    for ratio, cs in df.groupby("ratio")["coord_success"].mean().items():
        print(f"  {ratio:5.1f}x: {cs:.2%}")

    verdict = compute_frontier_verdict(df, cfg.synth_results_path)
    print(f"\nFrontier tau*: {verdict['frontier_tau']:.1f}" if not np.isnan(verdict.get("frontier_tau", float("nan"))) else "\nFrontier tau*: N/A")
    print(f"Drop: {verdict['frontier_drop_rel']:.1%}")
    print(f"API cost: EUR {verdict.get('total_api_cost_eur', 0):.4f}")

    if verdict.get("comparison"):
        comp = verdict["comparison"]
        print(f"Synth tau*: {comp['synth_tau']:.1f}")
        print(f"Tau diff: {comp['tau_diff_pct']:.1f}%")
        print(f"Theorem validated: {comp['theorem_validated']}")

    with open(out_dir / "verdicts.json", "w") as f:
        json.dump(verdict, f, indent=2, default=str)
    print(f"\nVerdicts saved to {out_dir / 'verdicts.json'}")


if __name__ == "__main__":
    main()
