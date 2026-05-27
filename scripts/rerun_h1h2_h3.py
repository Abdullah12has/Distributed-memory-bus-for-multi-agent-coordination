"""Re-run H1/H2 (with truncation + fixed critical_token_recall) and H3 (with fixed cost model).

Queue after the current production run finishes:
    nohup .venv/bin/python3 scripts/rerun_h1h2_h3.py > ~/rerun.log 2>&1 &

Estimated: ~9 hours total
  H1/H2: ~8h (4 compressors incl truncation, 10 ratios, 5 seeds, 50 wl/fam)
  H3:    ~30 min (3 compressors, 50 workloads, fixed gpt-4o-mini pricing)
"""
import json
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
log("RE-RUN: H1/H2 (truncation + fixed CTR) + H3 (fixed cost)")
log(f"Started: {datetime.now(UTC).isoformat()}")
log("=" * 60)

# =====================================================================
# H1/H2: 4 compressors including truncation
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
    out_dir="results/h1_h2_v2",
)
df1 = run_sweep(cfg)
out = Path("results/h1_h2_v2")
out.mkdir(parents=True, exist_ok=True)
df1.to_csv(out / "sweep_results.csv", index=False)

v1 = compute_h1_verdict(df1)
v2 = compute_h2_verdict(df1)
with open(out / "verdicts.json", "w") as f:
    json.dump({"h1": v1, "h2": v2}, f, indent=2, default=str)
log(f"H1/H2 done: H1={v1.get('h1_supported')} H2={v2['h2_supported']} ({v2['n_significant_cliffs']}/{v2['total_cells']})")

# =====================================================================
# H3: Fixed cost model (gpt-4o-mini pricing)
# =====================================================================
log("H3: 3 compressors, 50 workloads, gpt-4o-mini cost model")
from m6.experiments.run_h3 import H3Config, run_h3, compute_h3_verdict

cfg3 = H3Config(
    compressors=["lingua2", "phi3-extractive", "filter"],
    n_workloads=50,
    out_dir="results/h3_v2",
)
df3 = run_h3(cfg3)
out3 = Path("results/h3_v2")
out3.mkdir(parents=True, exist_ok=True)
df3.to_csv(out3 / "results.csv", index=False)
v3 = compute_h3_verdict(df3)
with open(out3 / "verdicts.json", "w") as f:
    json.dump(v3, f, indent=2, default=str)
log(f"H3 done: {v3['h3_supported']}")

# =====================================================================
# Theory validation with new data
# =====================================================================
log("Theory validation on new H1/H2 data")
from m6.theory.cliff_prediction import full_validation, derive_theta

theta_result = derive_theta(str(out / "sweep_results.csv"))
theta = theta_result["mean_theta"]
log(f"  Derived theta={theta:.3f}")

results = full_validation(str(out / "sweep_results.csv"), n_compression_passes=1, theta=theta)
with open(out / "theorem_validation.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
s = results["_summary"]
log(f"  Theorem validation: {s['n_match']}/{s['n_validated']} matched")

# =====================================================================
# Summary
# =====================================================================
total = time.time() - t0
h, m = divmod(int(total), 3600)
m, s = divmod(m, 60)
log("")
log("=" * 60)
log(f"RE-RUN DONE — {h:02d}:{m:02d}:{s:02d}")
log("=" * 60)
log(f"  H1/H2: results/h1_h2_v2/sweep_results.csv ({len(df1)} rows)")
log(f"  H3:    results/h3_v2/results.csv ({len(df3)} rows)")
