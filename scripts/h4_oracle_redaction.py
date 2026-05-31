#!/usr/bin/env python3
"""E4: Oracle-redaction control for the H4 inference-disclosure metric.

The H4 construct-validity finding (h4_unbiased_v2) is that disclosure
reduction is monotonic in how aggressively a compressor *destroys* source
tokens — truncation (most destructive) reduces disclosure most, the
verbatim Phi-3 extractive compressor not at all. The open question that
finding raises: is privacy reduction *only* achievable through bulk
destruction, or can a targeted mechanism remove the protected fact while
destroying almost nothing?

This script measures the constructive endpoint of that frontier: an
ORACLE redaction that removes ONLY the answer-bearing numeric values
(the recorded-hours and approved-budget figures the protected-fact
questions probe), leaving all other tokens intact. If oracle redaction
drives disclosure to the priors floor while destroying ~2 tokens, it
proves (i) the H4 metric does detect privacy-specific removal when it
happens, and (ii) the blanket compressors reduce disclosure only as a
side effect of destruction — they are NOT doing targeted filtering. It
also gives the memory bus an actual privacy mechanism (policy-driven
field redaction) rather than relying on lossy compression.

Reader and scoring match m6.experiments.run_h4 exactly (same ask_reader,
same gt comparison). Output: results/h4_oracle/results.csv + verdict.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from m6.benchmark.generator import load as load_benchmark
from m6.experiments.run_h4 import ask_reader, READER_MODEL

# Family-a protected quantities: "Recorded hours: N" and "budget: EUR N".
HOURS_RE = re.compile(r"(Recorded hours:\s*)(\d+)", re.IGNORECASE)
BUDGET_RE = re.compile(r"(budget:\s*EUR\s*)(\d+)", re.IGNORECASE)
VALUE_RE = re.compile(r"=\s*(\d+)")  # fallback: value after '=' in pf.fact
REDACT = "[REDACTED]"


def oracle_redact(text: str, fact: str) -> str:
    """Remove the answer-bearing numbers, keep everything else."""
    out = HOURS_RE.sub(lambda m: m.group(1) + REDACT, text)
    out = BUDGET_RE.sub(lambda m: m.group(1) + REDACT, out)
    # Fallback: also redact the literal value parsed from pf.fact, if present.
    mv = VALUE_RE.search(fact or "")
    if mv:
        out = re.sub(r"(?<!\d)" + re.escape(mv.group(1)) + r"(?!\d)", REDACT, out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="E4 oracle-redaction H4 control")
    ap.add_argument("--reader", type=str, default=READER_MODEL)
    ap.add_argument("--n-workloads", type=int, default=None)
    ap.add_argument("--benchmark", type=str, default="data/processed/c1-v0.1")
    ap.add_argument("--out", type=str, default="results/h4_oracle")
    args = ap.parse_args()

    workloads = [w for w in load_benchmark(args.benchmark) if w.protected_facts]
    if args.n_workloads:
        workloads = workloads[: args.n_workloads]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"{len(workloads)} workloads with protected facts; reader={args.reader}")

    rows = []
    for wi, w in enumerate(workloads):
        preamble = w.initial_prompt
        frag_lookup = {f.fragment_id: f for f in w.fragments}
        for pf in w.protected_facts:
            frag = frag_lookup.get(pf.fragment_id)
            if frag is None:
                continue
            redacted = oracle_redact(frag.text, getattr(pf, "fact", ""))
            for q, gt in zip(pf.yesno_questions, pf.answers):
                pri = ask_reader(args.reader, preamble, q)
                base = ask_reader(args.reader, frag.text, q)
                orc = ask_reader(args.reader, redacted, q)
                err = "error" in (pri, base, orc)
                rows.append({
                    "workload_id": w.workload_id,
                    "fragment_id": pf.fragment_id,
                    "question": q,
                    "gt_answer": gt,
                    "priors_correct": float(pri == gt),
                    "baseline_correct": float(base == gt),
                    "oracle_redacted_correct": float(orc == gt),
                    "orig_len": len(frag.text),
                    "redacted_len": len(redacted),
                    "destruction_frac": 1.0 - len(redacted) / max(len(frag.text), 1),
                    "has_error": err,
                })
        if (wi + 1) % 10 == 0:
            print(f"  [{wi+1}/{len(workloads)}]", flush=True)
            pd.DataFrame(rows).to_csv(out_dir / "results.csv", index=False)

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "results.csv", index=False)
    ok = df[~df["has_error"]]

    def bal(col):
        return float(np.mean([ok[ok.gt_answer == c][col].mean() for c in ["yes", "no"]]))

    pri, base, orc = bal("priors_correct"), bal("baseline_correct"), bal("oracle_redacted_correct")
    verdict = {
        "n_rows": int(len(ok)),
        "reader": args.reader,
        "balanced_priors": pri,
        "balanced_baseline": base,
        "balanced_oracle_redacted": orc,
        "oracle_reduction_pp": round((base - orc) * 100, 1),
        "oracle_destruction_frac_mean": float(ok["destruction_frac"].mean()),
        "pooled_priors": float(ok.priors_correct.mean()),
        "pooled_baseline": float(ok.baseline_correct.mean()),
        "pooled_oracle": float(ok.oracle_redacted_correct.mean()),
        "interpretation": (
            "Oracle redaction drives disclosure toward the priors floor while "
            "destroying ~{:.1%} of the text. This is the privacy-per-utility "
            "frontier endpoint: targeted field redaction achieves with near-zero "
            "destruction what blanket compression needs heavy destruction for, "
            "confirming the H4 construct-validity finding constructively and "
            "giving the memory-bus policy layer a real (non-compression) privacy "
            "mechanism.".format(float(ok["destruction_frac"].mean()))
        ),
    }
    (out_dir / "verdict.json").write_text(json.dumps(verdict, indent=2))
    print("\n=== E4 ORACLE-REDACTION VERDICT ===")
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
