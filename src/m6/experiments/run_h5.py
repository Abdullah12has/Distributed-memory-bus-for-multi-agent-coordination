#!/usr/bin/env python3
"""H5 — Model-size scaling: does tau* shift upward with larger planner LLMs?

Tests 4 planner sizes (1.5B / 3.8B / 8B / 14B) with LLMLingua-2 as fixed
compressor. The deterministic orchestrator is replaced with a direct Ollama
planner call so the LLM quality actually affects the coordination outcome.

H5 supported iff:
  tau* monotonically non-decreasing across model sizes on >= 2/3 families,
  with largest-vs-smallest gap >= 1.5 ratio units.

Run:
    python -m m6.experiments.run_h5
    python -m m6.experiments.run_h5 --smoke
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import numpy as np
import pandas as pd
from scipy import optimize

from m6.benchmark.generator import load as load_benchmark
from m6.benchmark.schemas import Workload
from m6.compressors import make_compressor
from m6.compressors.cache import CompressionCache, make_cached_compressor

# ============================================================================
# Config
# ============================================================================
OLLAMA_URL = "http://127.0.0.1:11434"

PLANNER_MODELS = {
    "1.5B": "qwen2.5:1.5b-instruct-q4_K_M",
    "3.8B": "phi3:latest",
    "8B": "llama3.1:8b",
    "14B": "qwen2.5:14b",
}


@dataclass
class H5Config:
    benchmark_path: str = "data/processed/c1-v0.1"
    compressor: str = "lingua2"  # fixed compressor
    ratios: list[float] | None = None
    seeds: list[int] | None = None
    families: list[str] | None = None  # plan-v3: family (a) only for H5
    n_workloads: int = 20  # per family (20 × 3 families = 60 total)
    out_dir: str = "results/h5"
    planner_models: dict[str, str] | None = None
    cache_path: str | None = None

    def __post_init__(self):
        if self.ratios is None:
            self.ratios = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0]
        if self.seeds is None:
            self.seeds = [0, 1, 2, 3, 4]
        if self.families is None:
            self.families = ["a", "b", "c"]
        if self.planner_models is None:
            self.planner_models = PLANNER_MODELS.copy()

    @classmethod
    def smoke(cls) -> H5Config:
        return cls(
            ratios=[1.0, 4.0, 8.0, 16.0],
            seeds=[0],
            families=["a"],
            n_workloads=3,
            planner_models={"8B": "llama3.1:8b"},
            out_dir="results/h5_smoke",
        )


# ============================================================================
# Ollama planner
# ============================================================================
def _format_hint(workload: Workload) -> str:
    """Return a family-specific format instruction for the ANSWER line."""
    fam = workload.family.value
    if fam == "a":
        return 'Use exactly this format: "ANSWER: hours=<total_hours>;budget=<total_budget>" (integers only, no currency symbols).'
    elif fam == "b":
        return 'Use exactly this format: "ANSWER: sub-0=worker-X;sub-1=worker-Y;..." listing every sub-task assignment. Use "worker-0", "worker-1", etc. as agent names.'
    else:  # family c
        return 'Use exactly this format: "ANSWER: FINAL-<number>" with the leaf value.'


def ollama_planner_solve(model: str, workload: Workload, compressed_texts: dict[str, str], seed: int = 0) -> dict:
    """Ask the Ollama planner to solve the workload given compressed fragments."""
    fragments_text = "\n\n".join(f"[{fid}] {text}" for fid, text in compressed_texts.items())
    format_hint = _format_hint(workload)
    prompt = f"""You are a planner in a multi-agent system. Your task:

{workload.initial_prompt}

Available information:
{fragments_text}

Instructions:
1. Read all fragments carefully.
2. Provide your final answer on a SINGLE line starting with "ANSWER: ".
{format_hint}

Your response:"""

    try:
        resp = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 512, "temperature": 0.1, "seed": seed},
            },
            timeout=120.0,
        )
        resp.raise_for_status()
        response = resp.json().get("response", "")
    except Exception as e:
        print(f"  [warn] planner exception ({model}): {e}", file=sys.stderr)
        response = ""

    # Extract answer (take last ANSWER: line — LLMs sometimes draft then revise)
    answer = ""
    for line in response.split("\n"):
        if line.strip().upper().startswith("ANSWER:"):
            answer = line.split(":", 1)[1].strip()
    if not answer:
        answer = response[:200]

    # Extract assignments from the answer line (single source of truth)
    # Accept both "worker-X" and "agent-X" (LLMs often say "agent" since fragments use that word)
    assignments = {}
    for match in re.finditer(r"(sub-\d+)\s*=\s*(?:worker|agent)-(\d+)", answer, re.IGNORECASE):
        assignments[match.group(1)] = f"worker-{match.group(2)}"

    # Score using family-aware method
    coord_success, f1 = _score_answer(workload, answer)

    # Subtask accuracy (uses same assignments extracted from answer line)
    subtask_acc = 0.0
    if workload.sub_tasks:
        correct = sum(
            1
            for st in workload.sub_tasks
            if assignments.get(st.sub_task_id.split("/")[-1], "") == st.expected_solver
        )
        subtask_acc = correct / len(workload.sub_tasks)

    return {
        "answer": answer,
        "coord_success": coord_success,
        "f1": f1,
        "subtask_acc": subtask_acc,
        "raw_response": response[:500],
    }


def _score_answer(workload: Workload, answer: str) -> tuple[float, float]:
    """Score answer with family-aware logic. Returns (coord_success, f1)."""
    expected = workload.expected_answer
    fam = workload.family.value

    if fam == "a":
        return _score_family_a(expected, answer)
    elif fam == "b":
        return _score_family_b(workload, answer)
    else:
        return _score_family_c(expected, answer)


def _score_family_a(expected: str, answer: str) -> tuple[float, float]:
    """Family a: extract hours and budget numbers, score by relative error."""
    def _extract_nums(s: str) -> dict[str, int | None]:
        nums: dict[str, int | None] = {"hours": None, "budget": None}
        # Match "hours=X", "hours: X", "hours X", "total hours: X", etc.
        m = re.search(r"hours\s*[=:]?\s*(\d[\d,]*)", s, re.IGNORECASE)
        if m:
            nums["hours"] = int(m.group(1).replace(",", ""))
        m = re.search(r"budget\s*[=:]?\s*(?:EUR\s*)?(\d[\d,]*)", s, re.IGNORECASE)
        if m:
            nums["budget"] = int(m.group(1).replace(",", ""))
        return nums

    exp_nums = _extract_nums(expected)
    ans_nums = _extract_nums(answer)

    scores = []
    for key in ["hours", "budget"]:
        ev = exp_nums.get(key)
        av = ans_nums.get(key)
        if ev is not None and av is not None and ev > 0:
            rel_err = abs(ev - av) / ev
            scores.append(max(0.0, 1.0 - rel_err))
        elif ev is not None and av is None:
            scores.append(0.0)

    if not scores:
        return 0.0, 0.0
    f1 = sum(scores) / len(scores)
    # Require both values within 25% error (f1 > 0.75) for coordination success
    coord_success = float(f1 > 0.75)
    return coord_success, f1


def _score_family_b(workload: "Workload", answer: str) -> tuple[float, float]:
    """Family b: check assignment feasibility (all tasks assigned, capacities respected)."""
    # Parse capacities from metadata
    cap_str = workload.metadata.get("capacities", "")
    if not cap_str:
        return 0.0, 0.0
    capacities = [int(x) for x in str(cap_str).split(",")]
    n_agents = len(capacities)

    # Parse loads from sub_tasks
    loads = {}
    for st in workload.sub_tasks:
        sub_id = st.sub_task_id.split("/")[-1]  # "c1-b-000/sub-0" -> "sub-0"
        loads[sub_id] = int(st.constraints.get("load", 1) or 1)

    # Parse assignments from answer (accept both worker-X and agent-X)
    ans_map = {}
    for m in re.finditer(r"(sub-\d+)\s*=\s*(?:worker|agent)-(\d+)", answer, re.IGNORECASE):
        ans_map[m.group(1).lower()] = int(m.group(2))

    # Check: all tasks assigned?
    n_tasks = len(loads)
    assigned = sum(1 for sub_id in loads if sub_id in ans_map)
    if assigned == 0:
        return 0.0, 0.0

    # Check feasibility: no agent exceeds capacity
    agent_load = [0] * n_agents
    feasible = True
    for sub_id, agent_idx in ans_map.items():
        if sub_id not in loads:
            continue
        if agent_idx < 0 or agent_idx >= n_agents:
            feasible = False
            break
        agent_load[agent_idx] += loads[sub_id]
        if agent_load[agent_idx] > capacities[agent_idx]:
            feasible = False
            break

    # f1 = task coverage (fraction assigned); coord_success = all assigned AND feasible
    f1 = assigned / n_tasks
    coord_success = float(feasible and assigned == n_tasks)
    return coord_success, f1


def _score_family_c(expected: str, answer: str) -> tuple[float, float]:
    """Family c: extract FINAL-XXXX and compare."""
    exp_m = re.search(r"FINAL-(\d+)", expected, re.IGNORECASE)
    ans_m = re.search(r"FINAL-(\d+)", answer, re.IGNORECASE)
    if exp_m and ans_m and exp_m.group(1) == ans_m.group(1):
        return 1.0, 1.0
    return 0.0, 0.0


# ============================================================================
# Cliff fitting (inline)
# ============================================================================
def fit_piecewise(ratios: np.ndarray, success: np.ndarray) -> dict:
    x = np.asarray(ratios, dtype=np.float64)
    y = np.asarray(success, dtype=np.float64)
    if len(x) < 4 or float(np.ptp(y)) < 1e-6:
        return {"tau": float("nan"), "drop_rel": 0.0}
    y_range = float(max(np.max(y) - np.min(y), 1e-6))

    def _obj(params):
        tau, sl, sd, intercept = params
        sr = sl - max(sd, 0.0)
        preds = np.where(x <= tau, intercept + sl * (x - tau), intercept + sr * (x - tau))
        return float(np.mean((preds - y) ** 2))

    x_margin = (x.max() - x.min()) * 0.1
    bounds = [
        (float(x.min() + x_margin), float(x.max() - x_margin)),
        (-2 / y_range, 2 / y_range),
        (0.0, 4 / y_range),
        (float(y.min() - 1), float(y.max() + 1)),
    ]
    result = optimize.differential_evolution(_obj, bounds=bounds, seed=0, maxiter=3000)
    tau, sl, sd, intercept = result.x
    sr = sl - max(sd, 0.0)
    left_eval = float(intercept + sl * (x.min() - tau))
    right_eval = float(intercept + sr * (x.max() - tau))
    drop_rel = (left_eval - right_eval) / max(abs(left_eval), 1e-6)
    return {"tau": float(tau), "drop_rel": float(drop_rel)}


# ============================================================================
# Main
# ============================================================================
def run_h5(cfg: H5Config) -> pd.DataFrame:
    print(f"Loading benchmark from {cfg.benchmark_path}...")
    all_workloads = load_benchmark(cfg.benchmark_path)
    family_set = set(cfg.families)
    # Sample n_workloads per family so all families are represented
    workloads = []
    for fam in sorted(family_set):
        fam_ws = [w for w in all_workloads if w.family.value == fam]
        workloads.extend(fam_ws[: cfg.n_workloads])
    print(f"  {len(workloads)} workloads loaded ({cfg.n_workloads} per family)")

    # Validate Ollama models are available before starting long sweep
    print("  Checking Ollama model availability...")
    for label, model_name in cfg.planner_models.items():
        try:
            resp = httpx.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": model_name, "prompt": "test", "stream": False,
                      "options": {"num_predict": 1}},
                timeout=30.0,
            )
            resp.raise_for_status()
            print(f"    {label} ({model_name}): OK")
        except Exception as e:
            print(f"    {label} ({model_name}): FAILED — {e}", file=sys.stderr)
            raise RuntimeError(
                f"Ollama model {model_name!r} not available. "
                f"Pull it with: ollama pull {model_name}"
            ) from e

    # Load precomputed cache if provided
    ext_cache: CompressionCache | None = None
    if cfg.cache_path:
        ext_cache = CompressionCache.load(cfg.cache_path)

    rows: list[dict[str, Any]] = []
    comp_cache: dict[float, Any] = {}
    # Cache compressed text per (ratio, fragment_id) — compression is
    # deterministic (temp=0), so reuse across planner models and seeds.
    compressed_cache: dict[tuple[float, str], str] = {}
    total = len(cfg.planner_models) * len(cfg.ratios) * len(workloads) * len(cfg.seeds)
    done = 0
    t_start = time.time()

    # Pre-compress all fragments for all ratios (compressor is fixed in H5).
    # This avoids redundant Ollama calls when iterating over planner models.
    print(f"  Pre-compressing fragments for {len(cfg.ratios)} ratios...")
    for ratio in cfg.ratios:
        if ratio not in comp_cache:
            comp_cache[ratio] = make_compressor(cfg.compressor, target_ratio=ratio)
        comp = comp_cache[ratio]
        for w in workloads:
            for frag in w.fragments:
                cache_key = (ratio, frag.fragment_id)
                if cache_key not in compressed_cache:
                    # Try precomputed cache first
                    if ext_cache is not None:
                        cached = ext_cache.lookup(cfg.compressor, ratio, frag.fragment_id, w.initial_prompt)
                        if cached is not None:
                            compressed_cache[cache_key] = cached
                            continue
                    frag_with_hint = frag.model_copy(update={"task_hint": w.initial_prompt})
                    slot = comp.compress(frag_with_hint)
                    compressed_cache[cache_key] = comp.decompress(slot) or frag.text
    print(f"  Cached {len(compressed_cache)} compressed fragments")

    for model_label, model_name in cfg.planner_models.items():
        print(f"\n  Planner: {model_label} ({model_name})")
        for ratio in cfg.ratios:
            for w in workloads:
                # Look up cached compressed fragments
                compressed_texts = {
                    frag.fragment_id: compressed_cache[(ratio, frag.fragment_id)]
                    for frag in w.fragments
                }

                for seed in cfg.seeds:
                    result = ollama_planner_solve(model_name, w, compressed_texts, seed=seed)
                    rows.append(
                        {
                            "planner_model": model_label,
                            "planner_model_name": model_name,
                            "compressor": cfg.compressor,
                            "ratio": ratio,
                            "family": w.family.value,
                            "workload_id": w.workload_id,
                            "seed": seed,
                            "coord_success": result["coord_success"],
                            "f1": result["f1"],
                            "subtask_acc": result["subtask_acc"],
                        }
                    )
                    done += 1
                    if done % 50 == 0:
                        elapsed = time.time() - t_start
                        eta = (elapsed / done) * (total - done)
                        print(f"    [{done}/{total}] {elapsed:.0f}s elapsed, ETA {eta:.0f}s")
                        sys.stdout.flush()
                    # Incremental save every 200 cells
                    if done % 200 == 0:
                        out_dir = Path(cfg.out_dir)
                        out_dir.mkdir(parents=True, exist_ok=True)
                        pd.DataFrame(rows).to_csv(out_dir / "results.partial.csv", index=False)

    return pd.DataFrame(rows)


def _compute_auc(ratios: np.ndarray, success: np.ndarray) -> float:
    """Area under the coord_success vs ratio curve (normalized to [0,1]).

    AUC is a more robust model-quality metric than tau* because it is
    well-defined even for gradual declines and does not suffer from
    boundary bias. Higher AUC = model degrades more slowly with compression.
    """
    x = np.asarray(ratios, dtype=np.float64)
    y = np.asarray(success, dtype=np.float64)
    if len(x) < 2:
        return 0.0
    order = np.argsort(x)
    x, y = x[order], y[order]
    raw_auc = float(np.trapz(y, x))
    # Normalize by the range so AUC is in [0, 1]
    span = float(x.max() - x.min())
    return raw_auc / span if span > 0 else 0.0


def compute_h5_verdict(df: pd.DataFrame) -> dict:
    """Check if tau* shifts upward with model size."""
    taus = {}  # {(model, family): tau}
    aucs = {}  # {(model, family): auc}
    for (model, family), sub in df.groupby(["planner_model", "family"]):
        agg = sub.groupby("ratio")["coord_success"].mean().reset_index()
        fit = fit_piecewise(agg["ratio"].to_numpy(), agg["coord_success"].to_numpy())
        taus[(model, family)] = fit["tau"]
        aucs[(model, family)] = _compute_auc(agg["ratio"].to_numpy(), agg["coord_success"].to_numpy())

    # Check monotonicity per family
    model_sizes = sorted(df["planner_model"].unique(), key=lambda m: float(m.replace("B", "")))
    families = sorted(df["family"].unique())

    monotonic_families = 0
    per_family = {}
    for fam in families:
        fam_taus = [taus.get((m, fam), float("nan")) for m in model_sizes]
        fam_aucs = [aucs.get((m, fam), 0.0) for m in model_sizes]
        # Need at least 2 non-NaN taus to assess monotonicity
        valid_pairs = [
            (fam_taus[i], fam_taus[i + 1])
            for i in range(len(fam_taus) - 1)
            if not np.isnan(fam_taus[i]) and not np.isnan(fam_taus[i + 1])
        ]
        is_monotonic = len(valid_pairs) >= 1 and all(a <= b for a, b in valid_pairs)
        non_nan = [t for t in fam_taus if not np.isnan(t)]
        gap = non_nan[-1] - non_nan[0] if len(non_nan) >= 2 else 0.0
        # AUC monotonicity: is AUC monotonically increasing with model size?
        auc_monotonic = all(fam_aucs[i] <= fam_aucs[i + 1] for i in range(len(fam_aucs) - 1))
        per_family[fam] = {
            "taus": dict(zip(model_sizes, fam_taus, strict=False)),
            "aucs": dict(zip(model_sizes, fam_aucs, strict=False)),
            "monotonic": is_monotonic,
            "auc_monotonic": auc_monotonic,
            "gap": gap,
        }
        if is_monotonic:
            monotonic_families += 1

    # H5: monotonic on >= 2/3 families AND gap >= 1.5
    max_gap = max((d["gap"] for d in per_family.values() if d["monotonic"]), default=0.0)
    return {
        "per_family": per_family,
        "monotonic_families": monotonic_families,
        "max_gap": max_gap,
        "h5_supported": monotonic_families >= 2 and max_gap >= 1.5,
    }


def compute_h5_model_independence_verdict(df: pd.DataFrame, baseline_threshold: float = 0.5) -> dict:
    """Corollary 1: cliff position is model-independent when baseline > threshold.

    For each family where at least 2 models have baseline >= baseline_threshold,
    check that tau spread across models is small. This reframes H5 from
    "does tau increase with model size?" to "is tau invariant to model size?"

    Note: cliff_prediction.validate_model_independence() provides a CSV-based version
    of this same analysis for post-hoc validation. This in-memory version is used
    during the experiment run.
    """
    model_sizes = sorted(df["planner_model"].unique(), key=lambda m: float(m.replace("B", "")))
    families = sorted(df["family"].unique())

    per_family: dict[str, Any] = {}
    n_testable = 0
    n_invariant = 0

    for fam in families:
        fam_df = df[df["family"] == fam]
        baselines: dict[str, float] = {}
        taus: dict[str, float] = {}

        for model in model_sizes:
            sub = fam_df[fam_df["planner_model"] == model]
            bl_sub = sub[sub["ratio"] == 1.0]
            baseline = float(bl_sub["coord_success"].mean()) if not bl_sub.empty else 0.0
            baselines[model] = baseline

            if baseline >= baseline_threshold:
                agg = sub.groupby("ratio")["coord_success"].mean().reset_index()
                fit = fit_piecewise(agg["ratio"].to_numpy(), agg["coord_success"].to_numpy())
                taus[model] = fit.get("logistic_tau", fit.get("tau", float("nan")))

        valid_taus = {m: t for m, t in taus.items() if not np.isnan(t)}
        floor_models = [m for m, b in baselines.items() if b < baseline_threshold]

        if len(valid_taus) >= 2:
            n_testable += 1
            tau_vals = list(valid_taus.values())
            tau_mean = float(np.mean(tau_vals))
            tau_spread = (max(tau_vals) - min(tau_vals)) / max(abs(tau_mean), 1e-9) * 100
            is_invariant = tau_spread <= 50.0

            if is_invariant:
                n_invariant += 1

            per_family[fam] = {
                "baselines": baselines,
                "taus": valid_taus,
                "tau_mean": tau_mean,
                "tau_spread_pct": float(tau_spread),
                "is_invariant": is_invariant,
                "floor_effect_models": floor_models,
            }
        else:
            per_family[fam] = {
                "baselines": baselines,
                "taus": valid_taus,
                "skipped": True,
                "reason": f"<2 models with baseline >= {baseline_threshold}",
                "floor_effect_models": floor_models,
            }

    supported = n_invariant >= 1 and n_testable >= 1
    return {
        "per_family": per_family,
        "n_testable_families": n_testable,
        "n_invariant_families": n_invariant,
        "corollary1_supported": supported,
        "baseline_threshold": baseline_threshold,
        "framing": "Cliff position is model-independent (Corollary 1). "
                   "Model size affects ceiling p0, not cliff position r*.",
        "limitation": f"Validated on {n_testable}/{len(per_family)} families "
                      f"(others have floor effects: baseline < {baseline_threshold}). "
                      "Tau spread tolerance is 50%. Stronger evidence would require "
                      "more families with sufficient baseline performance.",
    }


def main():
    parser = argparse.ArgumentParser(description="H5: Model-size scaling")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--out", type=str, default=None)
    parser.add_argument("--cache", type=str, default=None, help="Path to precomputed compression cache JSON")
    args = parser.parse_args()

    cfg = H5Config.smoke() if args.smoke else H5Config()
    if args.out:
        cfg.out_dir = args.out
    if args.cache:
        cfg.cache_path = args.cache

    print("=" * 60)
    print("H5: Model-Size Scaling")
    print("=" * 60)

    df = run_h5(cfg)
    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "results.csv", index=False)
    print(f"\nSaved {len(df)} rows to {out_dir / 'results.csv'}")

    verdict = compute_h5_verdict(df)
    print("\nH5 VERDICT (original — tau monotonicity):")
    for fam, data in verdict["per_family"].items():
        print(
            f"  Family {fam}: taus={data['taus']} monotonic={data['monotonic']} gap={data['gap']:.1f}"
        )
    print(
        f"  => H5 SUPPORTED: {verdict['h5_supported']} ({verdict['monotonic_families']}/3 monotonic, gap={verdict['max_gap']:.1f})"
    )

    # Corollary 1: model-independence verdict
    mi_verdict = compute_h5_model_independence_verdict(df)
    print("\nH5 VERDICT (reframed — Corollary 1: model-independence):")
    for fam, data in mi_verdict["per_family"].items():
        if data.get("skipped"):
            print(f"  Family {fam}: SKIPPED — {data['reason']} (floor: {data['floor_effect_models']})")
        else:
            print(
                f"  Family {fam}: tau_mean={data['tau_mean']:.1f} spread={data['tau_spread_pct']:.0f}% "
                f"invariant={data['is_invariant']} (floor: {data['floor_effect_models']})"
            )
    print(
        f"  => COROLLARY 1 SUPPORTED: {mi_verdict['corollary1_supported']} "
        f"({mi_verdict['n_invariant_families']}/{mi_verdict['n_testable_families']} invariant families)"
    )

    verdict["model_independence"] = mi_verdict
    with open(out_dir / "verdicts.json", "w") as f:
        json.dump(verdict, f, indent=2, default=str)


if __name__ == "__main__":
    main()
