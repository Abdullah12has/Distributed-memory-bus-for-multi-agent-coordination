"""Deep diagnostic — 20 min pass to find nuances, anomalies, bugs."""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

t0 = time.time()
print("=" * 70)
print("DEEP DIAGNOSTIC — 20 min pass")
print("=" * 70, flush=True)

# =====================================================================
# 1. H1/H2: 3 compressors + truncation, all 3 families, 10 wl/fam
#    Tests: logistic vs piecewise, Wilcoxon, seed averaging, per-family
# =====================================================================
print("\n" + "=" * 60)
print("1. H1/H2 (4 compressors, 6 ratios, 2 seeds, 10 wl/fam)")
print("=" * 60, flush=True)

from m6.experiments.run_h1_h2 import (
    SweepConfig, run_sweep, compute_h1_verdict, compute_h2_verdict,
)

cfg1 = SweepConfig(
    compressors=["lingua2", "phi3-extractive", "filter", "truncation"],
    ratios=[1.0, 2.0, 4.0, 8.0, 12.0, 16.0],
    compressor_ratios={"phi3-extractive": [1.0, 4.0, 8.0]},
    seeds=[0, 1],
    families=["a", "b", "c"],
    n_workloads=10,
    out_dir="results/deep_h1_h2",
)
df1 = run_sweep(cfg1)
Path("results/deep_h1_h2").mkdir(parents=True, exist_ok=True)
df1.to_csv("results/deep_h1_h2/sweep_results.csv", index=False)

# Sanity checks
print("\n--- SANITY CHECKS ---")
print(f"Families: {sorted(df1['family'].unique())}")
print(f"Workloads per family: {df1.groupby('family')['workload_id'].nunique().to_dict()}")
print(f"qa_f1 at ratio=1.0 by family:")
print(df1[df1["ratio"] == 1.0].groupby("family")["qa_f1"].mean())
print(f"\ncoord_success at ratio=1.0 by family x compressor:")
print(df1[df1["ratio"] == 1.0].groupby(["family", "compressor"])["coord_success"].mean().unstack("compressor"))

# Check truncation vs lingua2 — truncation should be worse
print("\n--- TRUNCATION vs LINGUA2 ---")
for fam in sorted(df1["family"].unique()):
    for metric in ["qa_f1", "coord_success"]:
        trunc = df1[(df1["compressor"] == "truncation") & (df1["family"] == fam)].groupby("ratio")[metric].mean()
        lingua = df1[(df1["compressor"] == "lingua2") & (df1["family"] == fam)].groupby("ratio")[metric].mean()
        # Compare at ratio=4
        t4 = trunc.get(4.0, float("nan"))
        l4 = lingua.get(4.0, float("nan"))
        winner = "lingua2" if l4 > t4 else ("truncation" if t4 > l4 else "tie")
        print(f"  {fam}/{metric}@4x: trunc={t4:.3f} lingua={l4:.3f} winner={winner}")

# H1 verdict
v1 = compute_h1_verdict(df1)
print("\n--- H1 VERDICT ---")
for comp in sorted(v1.keys()):
    if isinstance(v1[comp], dict) and "rho" in v1[comp]:
        d = v1[comp]
        ci_lo = f"{d.get('ci_low', 0):.3f}" if isinstance(d.get("ci_low"), float) and not np.isnan(d.get("ci_low", 0)) else "NaN"
        ci_hi = f"{d.get('ci_high', 0):.3f}" if isinstance(d.get("ci_high"), float) and not np.isnan(d.get("ci_high", 0)) else "NaN"
        print(f"  {comp}: rho={d['rho']:.3f} [{ci_lo}, {ci_hi}] n={d.get('n')} supported={d.get('supported')}")
        if d.get("cliffs_delta") is not None:
            print(f"    cliffs_delta={d['cliffs_delta']:.3f} cohens_d={d.get('cohens_d', 0):.3f}")
print(f"  => H1 SUPPORTED: {v1.get('h1_supported')} ({v1.get('n_below_threshold')}/4)")

# H2 verdict
v2 = compute_h2_verdict(df1)
print("\n--- H2 VERDICT ---")
for c in v2["cells"]:
    tau_s = f"{c['tau']:.1f}" if c["tau"] is not None else "N/A"
    model = c.get("model_selected", "?")
    log_tau = c.get("logistic_tau")
    log_tau_s = f"{log_tau:.1f}" if log_tau is not None and not np.isnan(log_tau) else "N/A"
    log_rmse = c.get("logistic_rmse")
    pw_rmse = c.get("rmse")
    print(f"  {c['compressor']}/{c['family']}: pw_tau={tau_s} log_tau={log_tau_s} model={model} pairs={c.get('n_pairs', 0)} p_holm={c.get('test_p_holm', 'N/A')}")
    if pw_rmse is not None and log_rmse is not None:
        print(f"    pw_rmse={pw_rmse:.4f} log_rmse={log_rmse:.4f}")
print(f"  => H2 SUPPORTED: {v2['h2_supported']} ({v2['n_significant_cliffs']}/{v2['total_cells']})")

# Check: any anomalies in the data?
print("\n--- ANOMALY CHECK ---")
# 1. token_recall should decrease with ratio
for comp in sorted(df1["compressor"].unique()):
    tr = df1[df1["compressor"] == comp].groupby("ratio")["token_recall"].mean()
    monotonic = all(tr.iloc[i] >= tr.iloc[i+1] - 0.01 for i in range(len(tr)-1))
    print(f"  {comp} token_recall monotonic: {monotonic} (1x={tr.iloc[0]:.3f} -> 16x={tr.iloc[-1]:.3f})")

# 2. qa_f1 should be ~1.0 at ratio=1.0
for comp in sorted(df1["compressor"].unique()):
    q1 = df1[(df1["compressor"] == comp) & (df1["ratio"] == 1.0)]["qa_f1"].mean()
    ok = q1 > 0.95
    print(f"  {comp} qa_f1@1x: {q1:.4f} {'OK' if ok else 'PROBLEM!'}")

# 3. coord_success should be 1.0 at ratio=1.0 for family-a
for comp in sorted(df1["compressor"].unique()):
    c1 = df1[(df1["compressor"] == comp) & (df1["ratio"] == 1.0) & (df1["family"] == "a")]["coord_success"].mean()
    print(f"  {comp} coord@1x/a: {c1:.2f}")

with open("results/deep_h1_h2/verdicts.json", "w") as f:
    json.dump({"h1": v1, "h2": v2}, f, indent=2, default=str)

print(f"\nH1/H2 done in {time.time()-t0:.0f}s", flush=True)

# =====================================================================
# 2. H4: All 3 compressors, 10 workloads — test Holm + error tracking
# =====================================================================
print("\n" + "=" * 60)
print("2. H4 (3 compressors, 10 workloads)")
print("=" * 60, flush=True)
t2 = time.time()

from m6.experiments.run_h4 import H4Config, run_h4, compute_h4_verdict

cfg4 = H4Config(
    compressors=["lingua2", "phi3-extractive", "filter"],
    n_workloads=10,
    out_dir="results/deep_h4",
)
df4 = run_h4(cfg4)
Path("results/deep_h4").mkdir(parents=True, exist_ok=True)
df4.to_csv("results/deep_h4/results.csv", index=False)

v4 = compute_h4_verdict(df4)
print("\n--- H4 VERDICT ---")
for comp, data in v4.get("per_compressor", {}).items():
    sig_p = data["signal_test"].get("p_holm", data["signal_test"]["p"])
    red_p = data["reduction_test"].get("p_holm", data["reduction_test"]["p"])
    print(f"  {comp}: priors={data['priors_rate']:.2f} base={data['baseline_rate']:.2f} comp={data['compressed_rate']:.2f}")
    print(f"    signal p_holm={sig_p:.4f} reduction p_holm={red_p:.4f}")
    print(f"    signal_sig={data['signal_significant']} reduction_sig={data['reduction_significant']}")
print(f"  => H4 SUPPORTED: {v4['h4_supported']}")

n_err = int(df4["has_error"].sum()) if "has_error" in df4.columns else "?"
print(f"  Errors: {n_err}/{len(df4)}")

# Anomaly: check priors balance (should be ~50% with balanced yes/no)
if not df4.empty:
    priors_rate = df4["priors_correct"].mean()
    print(f"  Priors rate: {priors_rate:.2f} (should be ~0.50 for balanced questions)")

with open("results/deep_h4/verdicts.json", "w") as f:
    json.dump(v4, f, indent=2, default=str)

print(f"\nH4 done in {time.time()-t2:.0f}s", flush=True)

# =====================================================================
# 3. CAAC smoke — verify it runs and produces sensible results
# =====================================================================
print("\n" + "=" * 60)
print("3. CAAC smoke")
print("=" * 60, flush=True)
t3 = time.time()

from m6.experiments.run_caac import CAACConfig, run_caac_experiment

cfg_c = CAACConfig.smoke()
df_c = run_caac_experiment(cfg_c)
if not df_c.empty:
    Path("results/deep_caac").mkdir(parents=True, exist_ok=True)
    df_c.to_csv("results/deep_caac/results.csv", index=False)

    print("\n--- CAAC RESULTS ---")
    print(f"  Rows: {len(df_c)}")
    # Compare fixed vs CAAC
    if "is_caac" in df_c.columns:
        fixed = df_c[~df_c["is_caac"]]
        caac = df_c[df_c["is_caac"]]
        print(f"  Fixed coord: {fixed['coord_success'].mean():.2f} (n={len(fixed)})")
        print(f"  CAAC coord:  {caac['coord_success'].mean():.2f} (n={len(caac)})")
        # CAAC should have higher coord at high ratios
        for r in sorted(df_c["target_ratio"].unique()):
            fc = fixed[fixed["target_ratio"] == r]["coord_success"].mean() if not fixed[fixed["target_ratio"] == r].empty else float("nan")
            cc = caac[caac["target_ratio"] == r]["coord_success"].mean() if not caac[caac["target_ratio"] == r].empty else float("nan")
            print(f"    ratio={r}: fixed={fc:.2f} caac={cc:.2f}")
    else:
        print("  WARNING: is_caac column missing")
else:
    print("  CAAC returned empty DataFrame!")

print(f"\nCAAC done in {time.time()-t3:.0f}s", flush=True)

# =====================================================================
# 4. Theory validation — predicted vs empirical tau
# =====================================================================
print("\n" + "=" * 60)
print("4. Theory validation")
print("=" * 60, flush=True)

from m6.theory.cliff_prediction import predicted_tau, q_required, predicted_success_smooth

# Use H1/H2 data
fam_a = df1[(df1["family"] == "a") & (df1["compressor"] == "lingua2")]
if not fam_a.empty:
    tr_agg = fam_a.groupby("ratio")["token_recall"].mean()
    tr_curve = list(zip(tr_agg.index.tolist(), tr_agg.values.tolist()))
    cs_agg = fam_a.groupby("ratio")["coord_success"].mean()

    n_compression_passes, theta = 1, 0.5
    q_min = q_required(theta, n_compression_passes)
    tau_pred = predicted_tau(tr_curve, n_compression_passes, theta)
    pred_curve = predicted_success_smooth(tr_curve, n_compression_passes, theta, p0=1.0)

    print(f"  q_required(theta={theta}, N={n_compression_passes}) = {q_min:.4f}")
    print(f"  predicted tau* = {tau_pred:.1f}")
    print(f"\n  Empirical vs Predicted:")
    for r in sorted(cs_agg.index):
        emp = cs_agg[r]
        pred_val = next((s for pr, s in pred_curve if abs(pr - r) < 0.01), float("nan"))
        print(f"    ratio={r:.0f}: empirical={emp:.2f} predicted={pred_val:.2f}")
else:
    print("  No lingua2/family-a data for theory validation")

# =====================================================================
# SUMMARY
# =====================================================================
total = time.time() - t0
print("\n" + "=" * 70)
print(f"DEEP DIAGNOSTIC COMPLETE — {total:.0f}s ({total/60:.1f} min)")
print("=" * 70)
print(f"  H1: {v1.get('h1_supported')} ({v1.get('n_below_threshold')}/4 compressors)")
print(f"  H2: {v2['h2_supported']} ({v2['n_significant_cliffs']}/{v2['total_cells']} cells)")
print(f"  H4: {v4['h4_supported']}")
print(f"  CAAC: {'OK' if not df_c.empty else 'EMPTY'}")
print(f"  Theory: tau_pred={tau_pred:.1f}" if not fam_a.empty else "  Theory: N/A")
