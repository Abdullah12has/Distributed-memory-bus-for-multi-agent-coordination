"""Short run — all 7 experiments end-to-end in ~10 min."""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd

t0 = time.time()
results = {}

def elapsed():
    return f"{time.time()-t0:.0f}s"

# === H1/H2 ===
print(f"[{elapsed()}] H1/H2...", flush=True)
from m6.experiments.run_h1_h2 import SweepConfig, run_sweep, compute_h1_verdict, compute_h2_verdict
df = run_sweep(SweepConfig(
    compressors=["lingua2", "filter"], ratios=[1.0, 4.0, 8.0, 16.0],
    seeds=[0], families=["a", "b", "c"], n_workloads=5,
    out_dir="results/short_h1_h2",
))
v1 = compute_h1_verdict(df)
v2 = compute_h2_verdict(df)
results["h1"] = v1.get("h1_supported")
results["h2"] = f"{v2['h2_supported']} ({v2['n_significant_cliffs']}/{v2['total_cells']})"
print(f"[{elapsed()}] H1={results['h1']} H2={results['h2']}", flush=True)

# === H3 ===
print(f"[{elapsed()}] H3...", flush=True)
from m6.experiments.run_h3 import H3Config, run_h3, compute_h3_verdict
df3 = run_h3(H3Config(compressors=["lingua2", "filter"], n_workloads=5, out_dir="results/short_h3"))
v3 = compute_h3_verdict(df3)
results["h3"] = v3["h3_supported"]
print(f"[{elapsed()}] H3={results['h3']}", flush=True)

# === H4 ===
print(f"[{elapsed()}] H4...", flush=True)
from m6.experiments.run_h4 import H4Config, run_h4, compute_h4_verdict
df4 = run_h4(H4Config(compressors=["lingua2", "phi3-extractive"], n_workloads=5, out_dir="results/short_h4"))
v4 = compute_h4_verdict(df4)
results["h4"] = v4["h4_supported"]
err = int(df4["has_error"].sum()) if "has_error" in df4.columns else "?"
print(f"[{elapsed()}] H4={results['h4']} errors={err}", flush=True)

# === H5 ===
print(f"[{elapsed()}] H5...", flush=True)
from m6.experiments.run_h5 import H5Config, run_h5, compute_h5_verdict
df5 = run_h5(H5Config(
    ratios=[1.0, 4.0, 8.0, 16.0], seeds=[0], families=["a", "c"], n_workloads=3,
    planner_models={"1.5B": "qwen2.5:1.5b-instruct-q4_K_M", "8B": "llama3.1:8b"},
    out_dir="results/short_h5",
))
v5 = compute_h5_verdict(df5)
results["h5"] = v5["h5_supported"]
print(f"[{elapsed()}] H5={results['h5']}", flush=True)

# === H6 ===
print(f"[{elapsed()}] H6...", flush=True)
from m6.experiments.run_h6 import H6Config, run_h6, compute_h6_verdict
df6 = run_h6(H6Config(ratios=[1.0, 4.0, 8.0, 16.0], seeds=[0], n_workloads=3,
                      synth_results_path="results/short_h5", out_dir="results/short_h6"))
v6 = compute_h6_verdict(df6, "results/short_h5")
results["h6"] = v6["h6_supported"]
print(f"[{elapsed()}] H6={results['h6']}", flush=True)

# === CAAC ===
print(f"[{elapsed()}] CAAC...", flush=True)
from m6.experiments.run_caac import CAACConfig, run_caac_experiment
dfc = run_caac_experiment(CAACConfig.smoke())
if not dfc.empty and "is_caac" in dfc.columns:
    fixed_c = dfc[~dfc["is_caac"]]["coord_success"].mean()
    caac_c = dfc[dfc["is_caac"]]["coord_success"].mean()
    results["caac"] = f"fixed={fixed_c:.2f} caac={caac_c:.2f}"
else:
    results["caac"] = "empty"
print(f"[{elapsed()}] CAAC={results['caac']}", flush=True)

# === Theory ===
print(f"[{elapsed()}] Theory...", flush=True)
from m6.theory.cliff_prediction import predicted_tau, q_required
fam_a = df[(df["family"] == "a") & (df["compressor"] == "lingua2")]
if not fam_a.empty:
    tr = fam_a.groupby("ratio")["token_recall"].mean()
    tr_curve = list(zip(tr.index.tolist(), tr.values.tolist()))
    tau = predicted_tau(tr_curve, n_compression_passes=1, theta=0.5)
    results["theory_tau"] = f"{tau:.1f}"
else:
    results["theory_tau"] = "N/A"
print(f"[{elapsed()}] Theory tau={results['theory_tau']}", flush=True)

# === Summary ===
total = time.time() - t0
print(f"\n{'='*60}")
print(f"ALL DONE in {total:.0f}s ({total/60:.1f} min)")
print(f"{'='*60}")
for k, v in results.items():
    print(f"  {k}: {v}")
