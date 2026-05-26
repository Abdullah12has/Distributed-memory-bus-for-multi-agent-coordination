"""Production run — all hypotheses sequentially on GPU.

Estimated: ~12-14 hours total.
  H1/H2: ~6h (3 compressors, 10 ratios, 5 seeds, 50 wl/fam)
  H3:    ~30 min (3 compressors, 50 workloads)
  H4:    ~2h (3 compressors, 50 workloads)
  H5:    ~3h (3 models, 10 ratios, 5 seeds, 20 wl/fam)
  H6:    ~65 min (30 workloads, 10 ratios, 5 seeds)
  CAAC:  ~1h (2 inner compressors, 6 ratios)
"""
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

t0 = time.time()

def log(msg):
    elapsed = time.time() - t0
    h, m = divmod(int(elapsed), 3600)
    m, s = divmod(m, 60)
    print(f"[{h:02d}:{m:02d}:{s:02d}] {msg}", flush=True)

log("=" * 60)
log("PRODUCTION RUN — All hypotheses")
log(f"Started: {datetime.now(UTC).isoformat()}")
log("=" * 60)

verdicts = {}

# =====================================================================
# H1/H2: Full sweep
# =====================================================================
log("H1/H2: 4 compressors, 10 ratios, 5 seeds, 50 wl/fam, 3 families")
from m6.experiments.run_h1_h2 import SweepConfig, run_sweep, compute_h1_verdict, compute_h2_verdict

cfg = SweepConfig(
    compressors=["lingua2", "phi3-extractive", "filter", "truncation"],
    ratios=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0],
    compressor_ratios={"phi3-extractive": [1.0, 2.0, 4.0, 8.0, 12.0, 16.0]},
    seeds=[0, 1, 2, 3, 4],
    families=["a", "b", "c"],
    n_workloads=50,
    out_dir="results/h1_h2_final",
)
df1 = run_sweep(cfg)
out = Path("results/h1_h2_final")
out.mkdir(parents=True, exist_ok=True)
df1.to_csv(out / "sweep_results.csv", index=False)

v1 = compute_h1_verdict(df1)
v2 = compute_h2_verdict(df1)
verdicts["h1"] = v1.get("h1_supported")
verdicts["h2"] = f"{v2['h2_supported']} ({v2['n_significant_cliffs']}/{v2['total_cells']})"
with open(out / "verdicts.json", "w") as f:
    json.dump({"h1": v1, "h2": v2}, f, indent=2, default=str)
log(f"H1/H2 done: H1={verdicts['h1']} H2={verdicts['h2']}")

# =====================================================================
# H3: RAG pipeline
# =====================================================================
log("H3: 3 compressors, 50 workloads")
from m6.experiments.run_h3 import H3Config, run_h3, compute_h3_verdict

cfg3 = H3Config(
    compressors=["lingua2", "phi3-extractive", "filter"],
    n_workloads=50,
    out_dir="results/h3_final",
)
df3 = run_h3(cfg3)
out3 = Path("results/h3_final")
out3.mkdir(parents=True, exist_ok=True)
df3.to_csv(out3 / "results.csv", index=False)
v3 = compute_h3_verdict(df3)
verdicts["h3"] = v3["h3_supported"]
with open(out3 / "verdicts.json", "w") as f:
    json.dump(v3, f, indent=2, default=str)
log(f"H3 done: {verdicts['h3']}")

# =====================================================================
# H4: Inference disclosure
# =====================================================================
log("H4: 3 compressors, 50 workloads")
from m6.experiments.run_h4 import H4Config, run_h4, compute_h4_verdict

cfg4 = H4Config(
    compressors=["lingua2", "phi3-extractive", "filter"],
    n_workloads=50,
    out_dir="results/h4_final",
)
df4 = run_h4(cfg4)
out4 = Path("results/h4_final")
out4.mkdir(parents=True, exist_ok=True)
df4.to_csv(out4 / "results.csv", index=False)
v4 = compute_h4_verdict(df4)
verdicts["h4"] = v4["h4_supported"]
with open(out4 / "verdicts.json", "w") as f:
    json.dump(v4, f, indent=2, default=str)
log(f"H4 done: {verdicts['h4']}")

# =====================================================================
# H5: Model-size scaling
# =====================================================================
log("H5: 3 models, 10 ratios, 5 seeds, 20 wl/fam, families a+c")
from m6.experiments.run_h5 import H5Config, run_h5, compute_h5_verdict

cfg5 = H5Config(
    ratios=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0],
    seeds=[0, 1, 2, 3, 4],
    families=["a", "c"],  # family-b excluded: LLMs ≤8B can't do constraint-satisfaction (see insight #33)
    n_workloads=20,
    planner_models={
        "1.5B": "qwen2.5:1.5b-instruct-q4_K_M",
        "3.8B": "phi3:latest",
        "8B": "llama3.1:8b",
    },
    out_dir="results/h5_final",
)
df5 = run_h5(cfg5)
out5 = Path("results/h5_final")
out5.mkdir(parents=True, exist_ok=True)
df5.to_csv(out5 / "results.csv", index=False)
v5 = compute_h5_verdict(df5)
verdicts["h5"] = v5["h5_supported"]
with open(out5 / "verdicts.json", "w") as f:
    json.dump(v5, f, indent=2, default=str)
log(f"H5 done: {verdicts['h5']}")

# =====================================================================
# H6: MultiHopRAG transfer
# =====================================================================
log("H6: 30 workloads, 10 ratios, 5 seeds")
from m6.experiments.run_h6 import H6Config, run_h6, compute_h6_verdict

cfg6 = H6Config(
    ratios=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0],
    seeds=[0, 1, 2, 3, 4],
    n_workloads=30,
    synth_results_path="results/h5_final",
    out_dir="results/h6_final",
)
df6 = run_h6(cfg6)
out6 = Path("results/h6_final")
out6.mkdir(parents=True, exist_ok=True)
df6.to_csv(out6 / "results.csv", index=False)
v6 = compute_h6_verdict(df6, cfg6.synth_results_path)
verdicts["h6"] = v6["h6_supported"]
with open(out6 / "verdicts.json", "w") as f:
    json.dump(v6, f, indent=2, default=str)
log(f"H6 done: {verdicts['h6']}")

# =====================================================================
# CAAC: Adaptive compression
# =====================================================================
log("CAAC: lingua2+filter, 6 ratios, 20 wl, 2 seeds")
from m6.experiments.run_caac import CAACConfig, run_caac_experiment, compute_caac_summary

cfg_c = CAACConfig(
    inner_compressors=["lingua2", "filter"],
    target_ratios=[1.0, 2.0, 4.0, 6.0, 8.0, 16.0],
    seeds=[0, 1],
    families=["a", "c"],
    n_workloads=20,
    out_dir="results/caac_final",
)
dfc = run_caac_experiment(cfg_c)
outc = Path("results/caac_final")
outc.mkdir(parents=True, exist_ok=True)
dfc.to_csv(outc / "results.csv", index=False)
vc = compute_caac_summary(dfc)
with open(outc / "summary.json", "w") as f:
    json.dump(vc, f, indent=2, default=str)
if not dfc.empty and "is_caac" in dfc.columns:
    fc = dfc[~dfc["is_caac"]]["coord_success"].mean()
    cc = dfc[dfc["is_caac"]]["coord_success"].mean()
    verdicts["caac"] = f"fixed={fc:.2f} caac={cc:.2f}"
else:
    verdicts["caac"] = "empty"
log(f"CAAC done: {verdicts['caac']}")

# =====================================================================
# Theory validation
# =====================================================================
log("Theory validation")
from m6.theory.cliff_prediction import predicted_tau, q_required, derive_theta

theta_result = derive_theta("results/h1_h2_final/sweep_results.csv")
theta = theta_result["mean_theta"]
log(f"  Derived theta={theta:.3f}")

fam_a = df1[(df1["family"] == "a") & (df1["compressor"] == "lingua2")]
if not fam_a.empty:
    tr = fam_a.groupby("ratio")["token_recall"].mean()
    tr_curve = list(zip(tr.index.tolist(), tr.values.tolist()))
    tau = predicted_tau(tr_curve, n_compression_passes=1, theta=theta)
    verdicts["theory_tau"] = f"{tau:.1f}"
    log(f"  Predicted tau={tau:.1f}")
else:
    verdicts["theory_tau"] = "N/A"

# =====================================================================
# SUMMARY
# =====================================================================
total = time.time() - t0
h, m = divmod(int(total), 3600)
m, s = divmod(m, 60)

log("")
log("=" * 60)
log(f"ALL DONE — {h:02d}:{m:02d}:{s:02d}")
log("=" * 60)
for k, v in verdicts.items():
    log(f"  {k}: {v}")

# Save final summary
with open("results/production_summary.json", "w") as f:
    json.dump({
        "verdicts": verdicts,
        "total_seconds": total,
        "completed_at": datetime.now(UTC).isoformat(),
    }, f, indent=2, default=str)
log(f"Summary saved to results/production_summary.json")
