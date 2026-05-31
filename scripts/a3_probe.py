#!/usr/bin/env python3
"""E7: Independent A3 probe — break the cliff/A3 circularity.

The compounding-error model's assumption A3 (threshold success) is, in
the manuscript, justified by the sharp empirical cliff of section 4.3 —
and that cliff is in turn *explained* by A3. The justification is
circular (acknowledged in section 5.3). This script breaks the
circularity with a direct probe: it varies the surviving fraction of
task-critical tokens **by hand-curated deletion, not via a compressor**,
then measures whether an LLM planner's coordination success follows the
threshold-sigmoid shape A3 predicts.

Why an LLM planner (not the regex solver): the regex solver fails the
instant a needed token is deleted, so it would re-prove the tautology.
A non-trivial planner (Llama-3.1-8B) *could* in principle compensate;
whatever shape its success-vs-recall curve takes is therefore a genuine
A3 test rather than a restatement of token recall.

Critical-token definitions match m6.metrics.critical_token_recall:
  family-a: multi-digit numbers  \b\d{2,}\b
  family-b: all numbers          \d+
  family-c: chain refs           (?:entry \d+|FINAL-\d+)

For each workload we collect every critical-token *occurrence* across
its fragments, delete a controlled fraction k/M uniformly at random
(several masking seeds), reconstruct the fragment texts with the deleted
occurrences replaced by a neutral placeholder, and run the planner. The
retained recall is measured directly as (M - n_deleted)/M.

Output: results/a3_probe/results.csv  +  verdict.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from m6.benchmark.generator import load as load_benchmark
from m6.experiments.run_h5 import ollama_planner_solve

CRIT_PATTERNS = {
    "a": re.compile(r"\b\d{2,}\b"),
    "b": re.compile(r"\d+"),
    "c": re.compile(r"(?:entry \d+|FINAL-\d+)", re.IGNORECASE),
}
PLACEHOLDER = "[?]"


def critical_spans(text: str, family: str) -> list[tuple[int, int]]:
    """Return (start, end) spans of every critical-token occurrence."""
    pat = CRIT_PATTERNS.get(family, CRIT_PATTERNS["c"])
    return [m.span() for m in pat.finditer(text)]


def delete_occurrences(text: str, spans_to_delete: set[tuple[int, int]]) -> str:
    """Rebuild text with the given critical spans replaced by PLACEHOLDER."""
    if not spans_to_delete:
        return text
    out = []
    last = 0
    for start, end in sorted(spans_to_delete):
        out.append(text[last:start])
        out.append(PLACEHOLDER)
        last = end
    out.append(text[last:])
    return "".join(out)


def make_deleted_fragments(
    workload, family: str, k_frac: float, rng: np.random.Generator
) -> tuple[dict[str, str], float]:
    """Delete k_frac of all critical-token occurrences across fragments.

    Returns (fragment_id -> modified_text, retained_recall).
    """
    # Global list of (fragment_id, span) occurrences.
    occ: list[tuple[str, tuple[int, int]]] = []
    for frag in workload.fragments:
        for span in critical_spans(frag.text, family):
            occ.append((frag.fragment_id, span))
    total = len(occ)
    if total == 0:
        return {f.fragment_id: f.text for f in workload.fragments}, 1.0

    n_delete = int(round(k_frac * total))
    chosen_idx = set(rng.choice(total, size=n_delete, replace=False).tolist()) if n_delete else set()

    per_frag_del: dict[str, set[tuple[int, int]]] = {}
    for i, (fid, span) in enumerate(occ):
        if i in chosen_idx:
            per_frag_del.setdefault(fid, set()).add(span)

    texts = {}
    for frag in workload.fragments:
        texts[frag.fragment_id] = delete_occurrences(
            frag.text, per_frag_del.get(frag.fragment_id, set())
        )
    retained = (total - n_delete) / total
    return texts, retained


def fit_logistic(recall: np.ndarray, success: np.ndarray) -> dict:
    """Fit success = L / (1 + exp(-k*(recall - r0))). Returns params + sharpness."""
    from scipy.optimize import curve_fit

    def f(x, L, k, r0):
        return L / (1.0 + np.exp(-k * (x - r0)))

    try:
        popt, _ = curve_fit(
            f, recall, success, p0=[1.0, 10.0, 0.5],
            bounds=([0.0, 0.0, 0.0], [1.0, 200.0, 1.0]), maxfev=20000,
        )
        L, k, r0 = popt
        preds = f(recall, *popt)
        rmse = float(np.sqrt(np.mean((preds - success) ** 2)))
        return {"L": float(L), "k": float(k), "r0": float(r0), "rmse": rmse}
    except Exception as e:  # noqa: BLE001
        return {"L": float("nan"), "k": float("nan"), "r0": float("nan"),
                "rmse": float("nan"), "error": str(e)}


def main() -> None:
    ap = argparse.ArgumentParser(description="E7 independent A3 probe")
    ap.add_argument("--families", type=str, default="a")
    ap.add_argument("--model", type=str, default="llama3.1:8b")
    ap.add_argument("--n-workloads", type=int, default=20)
    ap.add_argument("--fracs", type=str, default="0,0.15,0.3,0.45,0.6,0.75,0.9,1.0")
    ap.add_argument("--mask-seeds", type=str, default="0,1,2")
    ap.add_argument("--planner-seed", type=int, default=0)
    ap.add_argument("--benchmark", type=str, default="data/processed/c1-v0.1")
    ap.add_argument("--out", type=str, default="results/a3_probe")
    args = ap.parse_args()

    families = args.families.split(",")
    fracs = [float(x) for x in args.fracs.split(",")]
    mask_seeds = [int(x) for x in args.mask_seeds.split(",")]

    all_w = load_benchmark(args.benchmark)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for fam in families:
        ws = [w for w in all_w if w.family.value == fam][: args.n_workloads]
        total_calls = len(ws) * len(fracs) * len(mask_seeds)
        done = 0
        print(f"family-{fam}: {len(ws)} workloads x {len(fracs)} fracs x "
              f"{len(mask_seeds)} mask-seeds = {total_calls} planner calls")
        for w in ws:
            for k_frac in fracs:
                for ms in mask_seeds:
                    rng = np.random.default_rng(hash((w.workload_id, k_frac, ms)) % (2**32))
                    texts, retained = make_deleted_fragments(w, fam, k_frac, rng)
                    res = ollama_planner_solve(args.model, w, texts, seed=args.planner_seed)
                    rows.append({
                        "family": fam,
                        "workload_id": w.workload_id,
                        "model": args.model,
                        "k_frac_deleted": k_frac,
                        "mask_seed": ms,
                        "retained_recall": retained,
                        "coord_success": res["coord_success"],
                        "f1": res["f1"],
                    })
                    done += 1
                    if done % 10 == 0 or done == total_calls:
                        print(f"  [{done}/{total_calls}]", flush=True)
        pd.DataFrame(rows).to_csv(out_dir / "results.csv", index=False)

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "results.csv", index=False)

    # Verdict: per-family success-vs-retained-recall curve + logistic sharpness.
    verdict = {}
    for fam in families:
        sub = df[df["family"] == fam]
        # Aggregate success at each retained-recall level (mean over workloads+mask-seeds).
        agg = sub.groupby("retained_recall")["coord_success"].mean().reset_index()
        recall = agg["retained_recall"].to_numpy(dtype=float)
        success = agg["coord_success"].to_numpy(dtype=float)
        fit = fit_logistic(recall, success)
        # Sharpness diagnostic: width of the recall band over which success
        # goes 0.2 -> 0.8 (smaller = sharper = more threshold-like).
        order = np.argsort(recall)
        r_sorted, s_sorted = recall[order], success[order]
        def _cross(level):
            for i in range(1, len(s_sorted)):
                if (s_sorted[i - 1] - level) * (s_sorted[i] - level) <= 0 and s_sorted[i] != s_sorted[i - 1]:
                    t = (level - s_sorted[i - 1]) / (s_sorted[i] - s_sorted[i - 1])
                    return float(r_sorted[i - 1] + t * (r_sorted[i] - r_sorted[i - 1]))
            return float("nan")
        r20, r80 = _cross(0.2), _cross(0.8)
        transition_width = abs(r80 - r20) if not (np.isnan(r20) or np.isnan(r80)) else float("nan")
        verdict[fam] = {
            "logistic": fit,
            "transition_recall_band_0.2_0.8": transition_width,
            "curve": {f"{r:.3f}": float(s) for r, s in zip(agg["retained_recall"], agg["coord_success"])},
            "interpretation": (
                "THRESHOLD-LIKE (A3 supported directly)" if (not np.isnan(transition_width) and transition_width <= 0.25)
                else "GRADED (A3 is first-order; graded-success refinement indicated)"
                if not np.isnan(transition_width) else "INCONCLUSIVE"
            ),
        }
    (out_dir / "verdict.json").write_text(json.dumps(verdict, indent=2))
    print("\n=== A3 PROBE VERDICT ===")
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
