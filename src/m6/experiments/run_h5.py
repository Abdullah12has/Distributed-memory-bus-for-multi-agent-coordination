#!/usr/bin/env python3
"""H5 — Model-size scaling: does tau* shift upward with larger planner LLMs?

Tests 3 planner sizes (1.5B / 3.8B / 8B) with LLMLingua-2 as fixed compressor.
The deterministic orchestrator is replaced with a direct Ollama planner call
so the LLM quality actually affects the coordination outcome.

H5 supported iff:
  tau*_8B >= tau*_3.8B >= tau*_1.5B on >= 2/3 families,
  with largest-vs-smallest gap >= 1.5 ratio units.

Run:
    python -m m6.experiments.run_h5
    python -m m6.experiments.run_h5 --smoke
"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter
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

# ============================================================================
# Config
# ============================================================================
OLLAMA_URL = "http://127.0.0.1:11434"

PLANNER_MODELS = {
    "1.5B": "qwen2.5:1.5b-instruct-q4_K_M",
    "3.8B": "phi3:latest",
    "8B": "llama3.1:8b",
}


@dataclass
class H5Config:
    benchmark_path: str = "data/processed/c1-v0.1"
    compressor: str = "lingua2"  # fixed compressor
    ratios: list[float] | None = None
    seeds: list[int] | None = None
    families: list[str] | None = None  # plan-v3: family (a) only for H5
    n_workloads: int = 30  # plan-v3 §2: 30 of the 50 family-(a) instances
    out_dir: str = "results/h5"
    planner_models: dict[str, str] | None = None

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
def ollama_planner_solve(model: str, workload: Workload, compressed_texts: dict[str, str], seed: int = 0) -> dict:
    """Ask the Ollama planner to solve the workload given compressed fragments."""
    fragments_text = "\n\n".join(f"[{fid}] {text}" for fid, text in compressed_texts.items())
    prompt = f"""You are a planner in a multi-agent system. Your task:

{workload.initial_prompt}

Available information:
{fragments_text}

Instructions:
1. Read all fragments carefully.
2. Provide your final answer on a line starting with "ANSWER: ".
3. For each sub-task, assign it to a worker: "sub-X = worker-Y"

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
    except Exception:
        response = ""

    # Extract answer
    answer = ""
    for line in response.split("\n"):
        if line.strip().upper().startswith("ANSWER:"):
            answer = line.split(":", 1)[1].strip()
            break
    if not answer:
        answer = response[:200]

    # Extract assignments
    assignments = {}
    for match in re.finditer(r"(sub-\d+)\s*=\s*(worker-\d+)", response, re.IGNORECASE):
        assignments[match.group(1)] = match.group(2).lower()

    # Score
    expected_norm = " ".join(workload.expected_answer.lower().split())
    answer_norm = " ".join(answer.lower().split())
    success = float(expected_norm == answer_norm)

    # F1 as softer metric
    p_tok = _normalize(answer).split()
    r_tok = _normalize(workload.expected_answer).split()
    if p_tok and r_tok:
        common = Counter(p_tok) & Counter(r_tok)
        num_same = sum(common.values())
        if num_same > 0:
            prec = num_same / len(p_tok)
            rec = num_same / len(r_tok)
            f1 = 2 * prec * rec / (prec + rec)
        else:
            f1 = 0.0
    else:
        f1 = 0.0

    # Use F1 > 0.5 as a softer success criterion for coordination
    coord_success = float(f1 > 0.5)

    # Subtask accuracy
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


def _normalize(s: str) -> str:
    import string

    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


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

    bounds = [
        (float(x.min()), float(x.max())),
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
    workloads = load_benchmark(cfg.benchmark_path)
    family_set = set(cfg.families)
    workloads = [w for w in workloads if w.family.value in family_set]
    workloads = workloads[: cfg.n_workloads]
    print(f"  {len(workloads)} workloads loaded")

    rows: list[dict[str, Any]] = []
    comp_cache: dict[float, Any] = {}
    total = len(cfg.planner_models) * len(cfg.ratios) * len(workloads) * len(cfg.seeds)
    done = 0
    t_start = time.time()

    for model_label, model_name in cfg.planner_models.items():
        print(f"\n  Planner: {model_label} ({model_name})")
        for ratio in cfg.ratios:
            if ratio not in comp_cache:
                comp_cache[ratio] = make_compressor(cfg.compressor, target_ratio=ratio)
            comp = comp_cache[ratio]

            for w in workloads:
                # Compress fragments
                compressed_texts = {}
                for frag in w.fragments:
                    slot = comp.compress(frag)
                    text = comp.decompress(slot) or frag.text
                    compressed_texts[frag.fragment_id] = text

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

    return pd.DataFrame(rows)


def compute_h5_verdict(df: pd.DataFrame) -> dict:
    """Check if tau* shifts upward with model size."""
    taus = {}  # {(model, family): tau}
    for (model, family), sub in df.groupby(["planner_model", "family"]):
        agg = sub.groupby("ratio")["coord_success"].mean().reset_index()
        fit = fit_piecewise(agg["ratio"].to_numpy(), agg["coord_success"].to_numpy())
        taus[(model, family)] = fit["tau"]

    # Check monotonicity per family
    model_sizes = sorted(df["planner_model"].unique(), key=lambda m: float(m.replace("B", "")))
    families = sorted(df["family"].unique())

    monotonic_families = 0
    per_family = {}
    for fam in families:
        fam_taus = [taus.get((m, fam), float("nan")) for m in model_sizes]
        is_monotonic = all(
            fam_taus[i] <= fam_taus[i + 1]
            for i in range(len(fam_taus) - 1)
            if not np.isnan(fam_taus[i]) and not np.isnan(fam_taus[i + 1])
        )
        gap = fam_taus[-1] - fam_taus[0] if len(fam_taus) >= 2 else 0
        per_family[fam] = {
            "taus": dict(zip(model_sizes, fam_taus, strict=False)),
            "monotonic": is_monotonic,
            "gap": gap,
        }
        if is_monotonic:
            monotonic_families += 1

    # H5: monotonic on >= 2/3 families AND gap >= 1.5
    max_gap = max((d["gap"] for d in per_family.values()), default=0)
    return {
        "per_family": per_family,
        "monotonic_families": monotonic_families,
        "max_gap": max_gap,
        "h5_supported": monotonic_families >= 2 and max_gap >= 1.5,
    }


def main():
    parser = argparse.ArgumentParser(description="H5: Model-size scaling")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()

    cfg = H5Config.smoke() if args.smoke else H5Config()
    if args.out:
        cfg.out_dir = args.out

    print("=" * 60)
    print("H5: Model-Size Scaling")
    print("=" * 60)

    df = run_h5(cfg)
    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "results.csv", index=False)
    print(f"\nSaved {len(df)} rows to {out_dir / 'results.csv'}")

    verdict = compute_h5_verdict(df)
    print("\nH5 VERDICT:")
    for fam, data in verdict["per_family"].items():
        print(
            f"  Family {fam}: taus={data['taus']} monotonic={data['monotonic']} gap={data['gap']:.1f}"
        )
    print(
        f"  => H5 SUPPORTED: {verdict['h5_supported']} ({verdict['monotonic_families']}/3 monotonic, gap={verdict['max_gap']:.1f})"
    )

    with open(out_dir / "verdicts.json", "w") as f:
        json.dump(verdict, f, indent=2, default=str)


if __name__ == "__main__":
    main()
