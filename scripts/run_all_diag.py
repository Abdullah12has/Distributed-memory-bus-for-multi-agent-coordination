"""Run all experiments with diagnostic configs to stress-test fixes."""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

print("=" * 70)
print("FULL DIAGNOSTIC SWEEP - All hypotheses, all fixes")
print("=" * 70)
t0 = time.time()

# =====================================================================
# 1. H1/H2: Test Wilcoxon, logistic fit, seed averaging, NaN CI guard
# =====================================================================
print("\n" + "=" * 60)
print("TEST 1: H1/H2 (3 compressors, 5 ratios, 2 seeds, 15 workloads)")
print("=" * 60, flush=True)

from m6.experiments.run_h1_h2 import (
    SweepConfig,
    run_sweep,
    compute_h1_verdict,
    compute_h2_verdict,
)

cfg1 = SweepConfig(
    compressors=["lingua2", "phi3-extractive", "filter"],
    ratios=[1.0, 2.0, 4.0, 8.0, 16.0],
    compressor_ratios={"phi3-extractive": [1.0, 4.0, 8.0]},
    seeds=[0, 1],
    families=["a", "b", "c"],
    n_workloads=15,
    out_dir="results/diag_h1_h2",
)
df1 = run_sweep(cfg1)
Path("results/diag_h1_h2").mkdir(parents=True, exist_ok=True)
df1.to_csv("results/diag_h1_h2/sweep_results.csv", index=False)

v1 = compute_h1_verdict(df1)
print("\nH1 VERDICT:")
for comp in ["lingua2", "phi3-extractive", "filter"]:
    if comp in v1 and isinstance(v1[comp], dict) and "rho" in v1[comp]:
        d = v1[comp]
        ci_lo = d.get("ci_low", "?")
        ci_hi = d.get("ci_high", "?")
        ci_lo_s = f"{ci_lo:.3f}" if isinstance(ci_lo, float) else str(ci_lo)
        ci_hi_s = f"{ci_hi:.3f}" if isinstance(ci_hi, float) else str(ci_hi)
        print(f"  {comp}: rho={d['rho']:.3f} [{ci_lo_s}, {ci_hi_s}] supported={d.get('supported')}")
print(f"  => H1 SUPPORTED: {v1.get('h1_supported')}")

v2 = compute_h2_verdict(df1)
print("\nH2 VERDICT:")
for c in v2["cells"]:
    tau_s = f"{c['tau']:.1f}" if c["tau"] is not None else "N/A"
    p_s = c.get("test_p_holm", "N/A")
    model = c.get("model_selected", "?")
    log_tau = c.get("logistic_tau", "?")
    print(f"  {c['compressor']}/{c['family']}: tau={tau_s} drop={c['drop_rel']:.1%} p_holm={p_s} model={model} log_tau={log_tau}")
print(f"  => H2 SUPPORTED: {v2['h2_supported']} ({v2['n_significant_cliffs']}/{v2['total_cells']})")

print("\nSANITY: qa_f1 at ratio=1.0:")
print(df1[df1["ratio"] == 1.0].groupby("family")["qa_f1"].mean())

with open("results/diag_h1_h2/verdicts.json", "w") as f:
    json.dump({"h1": v1, "h2": v2}, f, indent=2, default=str)

print(f"\nH1/H2 done in {time.time()-t0:.0f}s", flush=True)

# =====================================================================
# 2. H3: Test per-workload bootstrap and corrected cost model
# =====================================================================
print("\n" + "=" * 60)
print("TEST 2: H3 (3 compressors, 10 workloads)")
print("=" * 60, flush=True)
t2 = time.time()

from m6.experiments.run_h3 import H3Config, run_h3, compute_h3_verdict

cfg3 = H3Config(
    compressors=["lingua2", "phi3-extractive", "filter"],
    n_workloads=10,
    out_dir="results/diag_h3",
)
df3 = run_h3(cfg3)
Path("results/diag_h3").mkdir(parents=True, exist_ok=True)
df3.to_csv("results/diag_h3/results.csv", index=False)

v3 = compute_h3_verdict(df3)
print("\nH3 VERDICT:")
for regime, data in v3["regimes"].items():
    diff = data["p1_vs_p2_diff_pp"]
    p = data["p1_vs_p2_p"]
    leader = data["leader"]
    print(f"  {regime}: P1-P2 diff={diff:.1f}pp p={p:.4f} leader={leader}")
print(f"  => H3 SUPPORTED: {v3['h3_supported']}")

print("\nCOST MODEL CHECK (P1 vs P2 should differ):")
for regime in ["storage_bounded", "accuracy_bounded"]:
    r = df3[df3["regime"] == regime]
    for p in ["P1", "P2", "P3"]:
        eur = r[r["pipeline"] == p]["eur_per_query"].mean()
        f1_val = r[r["pipeline"] == p]["f1"].mean()
        print(f"  {regime}/{p}: EUR={eur:.6f} F1={f1_val:.3f}")

with open("results/diag_h3/verdicts.json", "w") as f:
    json.dump(v3, f, indent=2, default=str)

print(f"\nH3 done in {time.time()-t2:.0f}s", flush=True)

# =====================================================================
# 3. H4: Test Holm correction and error tracking
# =====================================================================
print("\n" + "=" * 60)
print("TEST 3: H4 (2 compressors, 5 workloads)")
print("=" * 60, flush=True)
t3 = time.time()

from m6.experiments.run_h4 import H4Config, run_h4, compute_h4_verdict

cfg4 = H4Config(
    compressors=["lingua2", "phi3-extractive"],
    n_workloads=5,
    out_dir="results/diag_h4",
)
df4 = run_h4(cfg4)
Path("results/diag_h4").mkdir(parents=True, exist_ok=True)
df4.to_csv("results/diag_h4/results.csv", index=False)

v4 = compute_h4_verdict(df4)
print("\nH4 VERDICT:")
for comp, data in v4.get("per_compressor", {}).items():
    sig_p = data["signal_test"].get("p_holm", data["signal_test"]["p"])
    red_p = data["reduction_test"].get("p_holm", data["reduction_test"]["p"])
    print(f"  {comp}: priors={data['priors_rate']:.2f} base={data['baseline_rate']:.2f} comp={data['compressed_rate']:.2f}")
    print(f"    signal p_holm={sig_p:.4f} sig={data['signal_significant']} | reduction p_holm={red_p:.4f} sig={data['reduction_significant']}")
print(f"  => H4 SUPPORTED: {v4['h4_supported']}")

if "has_error" in df4.columns:
    n_err = int(df4["has_error"].sum())
    print(f"\nERROR TRACKING: {n_err}/{len(df4)} rows had errors")
else:
    print("\nERROR TRACKING: has_error column missing!")

with open("results/diag_h4/verdicts.json", "w") as f:
    json.dump(v4, f, indent=2, default=str)

print(f"\nH4 done in {time.time()-t3:.0f}s", flush=True)

# =====================================================================
# 4. H5: Test monotonicity fix, max_gap fix, task_hint
# =====================================================================
print("\n" + "=" * 60)
print("TEST 4: H5 (3 models, families a+c, 4 ratios, 1 seed, 5 wl)")
print("=" * 60, flush=True)
t4 = time.time()

from m6.experiments.run_h5 import H5Config, run_h5, compute_h5_verdict

cfg5 = H5Config(
    ratios=[1.0, 4.0, 8.0, 16.0],
    seeds=[0],
    families=["a", "c"],
    n_workloads=5,
    planner_models={
        "1.5B": "qwen2.5:1.5b-instruct-q4_K_M",
        "3.8B": "phi3:latest",
        "8B": "llama3.1:8b",
    },
    out_dir="results/diag_h5",
)
df5 = run_h5(cfg5)
Path("results/diag_h5").mkdir(parents=True, exist_ok=True)
df5.to_csv("results/diag_h5/results.csv", index=False)

v5 = compute_h5_verdict(df5)
print("\nH5 VERDICT:")
for fam, data in v5["per_family"].items():
    taus = data["taus"]
    mono = data["monotonic"]
    gap = data["gap"]
    print(f"  Family {fam}: taus={taus} monotonic={mono} gap={gap:.1f}")
mf = v5["monotonic_families"]
mg = v5["max_gap"]
print(f"  => H5 SUPPORTED: {v5['h5_supported']} ({mf} monotonic, gap={mg:.1f})")
print(f"\nMAX_GAP CHECK: {mg:.1f} (should only include monotonic families)")

with open("results/diag_h5/verdicts.json", "w") as f:
    json.dump(v5, f, indent=2, default=str)

print(f"\nH5 done in {time.time()-t4:.0f}s", flush=True)

# =====================================================================
# 5. H6: Smoke with synth comparison
# =====================================================================
print("\n" + "=" * 60)
print("TEST 5: H6 smoke (3 workloads, 4 ratios)")
print("=" * 60, flush=True)
t5 = time.time()

from m6.experiments.run_h6 import H6Config, run_h6, compute_h6_verdict

cfg6 = H6Config(
    ratios=[1.0, 4.0, 8.0, 16.0],
    seeds=[0],
    n_workloads=3,
    out_dir="results/diag_h6",
)
df6 = run_h6(cfg6)
Path("results/diag_h6").mkdir(parents=True, exist_ok=True)
df6.to_csv("results/diag_h6/results.csv", index=False)

synth_path = None
for p in ["results/h5_full", "results/diag_h5"]:
    if (Path(p) / "results.csv").exists():
        synth_path = p
        break

v6 = compute_h6_verdict(df6, synth_path)
print("\nH6 VERDICT:")
rt = v6.get("real_tau", float("nan"))
print(f"  Real tau*: {rt:.1f}" if not np.isnan(rt) else "  Real tau*: N/A")
print(f"  Real drop: {v6.get('real_drop_rel', 0):.1%}")
if synth_path:
    st = v6.get("synth_tau", float("nan"))
    print(f"  Synth tau*: {st:.1f}" if not np.isnan(st) else "  Synth tau*: N/A")
    td = v6.get("tau_diff_pct", float("nan"))
    print(f"  Tau diff: {td:.1f}%" if not np.isnan(td) else "  Tau diff: N/A")
if v6.get("note"):
    print(f"  Note: {v6['note']}")
print(f"  => H6 SUPPORTED: {v6['h6_supported']}")

with open("results/diag_h6/verdicts.json", "w") as f:
    json.dump(v6, f, indent=2, default=str)

print(f"\nH6 done in {time.time()-t5:.0f}s", flush=True)

# =====================================================================
# SUMMARY
# =====================================================================
total = time.time() - t0
print("\n" + "=" * 70)
print(f"ALL TESTS COMPLETE - {total:.0f}s total")
print("=" * 70)
print(f"  H1: {v1.get('h1_supported')}")
print(f"  H2: {v2['h2_supported']} ({v2['n_significant_cliffs']}/{v2['total_cells']})")
print(f"  H3: {v3['h3_supported']}")
print(f"  H4: {v4['h4_supported']}")
print(f"  H5: {v5['h5_supported']}")
print(f"  H6: {v6['h6_supported']}")
