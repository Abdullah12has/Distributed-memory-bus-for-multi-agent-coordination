"""Battle test H1/H2 with 4 different configs."""
import time
import numpy as np
import pandas as pd
from m6.experiments.run_h1_h2 import SweepConfig, run_sweep, compute_h1_verdict, compute_h2_verdict

t0 = time.time()

# A: Fine-grained ratios around cliff (1-5x)
print("=== A: Fine ratios 1-5x, 3 families, 15 wl ===", flush=True)
dfA = run_sweep(SweepConfig(
    compressors=["lingua2", "filter"], ratios=[1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0],
    seeds=[0, 1], families=["a", "b", "c"], n_workloads=15,
    out_dir="results/bt_h12_fine",
))
v2A = compute_h2_verdict(dfA)
print(f"  H2={v2A['h2_supported']} ({v2A['n_significant_cliffs']}/{v2A['total_cells']})")
for c in v2A["cells"]:
    if c["tau"] is not None:
        lt = c.get("logistic_tau")
        lt_s = f"{lt:.2f}" if lt and not np.isnan(lt) else "N/A"
        print(f"    {c['compressor']}/{c['family']}: log_tau={lt_s} model={c.get('model_selected','?')} drop={c['drop_rel']:.0%}")
print("  Coord curve (lingua2):")
print(dfA[dfA["compressor"] == "lingua2"].groupby(["family", "ratio"])["coord_success"].mean().unstack("family").to_string())
print(f"  [{time.time()-t0:.0f}s]", flush=True)

# B: Extreme compression (8-16x) on family-c
print("\n=== B: Extreme ratios, family-c, 20 wl ===", flush=True)
dfB = run_sweep(SweepConfig(
    compressors=["lingua2", "filter"], ratios=[1.0, 8.0, 10.0, 12.0, 14.0, 16.0],
    seeds=[0, 1], families=["c"], n_workloads=20,
    out_dir="results/bt_h12_extreme",
))
print("  Coord (family-c):")
print(dfB.groupby(["compressor", "ratio"])["coord_success"].mean().unstack("compressor").to_string())
print("  qa_f1 (family-c):")
print(dfB.groupby(["compressor", "ratio"])["qa_f1"].mean().unstack("compressor").to_string())
print(f"  [{time.time()-t0:.0f}s]", flush=True)

# C: Truncation vs lingua2 cliff position
print("\n=== C: Truncation vs lingua2, family-a, 20 wl ===", flush=True)
dfC = run_sweep(SweepConfig(
    compressors=["lingua2", "truncation"], ratios=[1.0, 2.0, 3.0, 4.0, 6.0, 8.0],
    seeds=[0, 1], families=["a"], n_workloads=20,
    out_dir="results/bt_h12_trunc",
))
v2C = compute_h2_verdict(dfC)
for c in v2C["cells"]:
    if c["tau"] is not None:
        lt = c.get("logistic_tau")
        lt_s = f"{lt:.2f}" if lt and not np.isnan(lt) else "N/A"
        print(f"    {c['compressor']}: log_tau={lt_s} drop={c['drop_rel']:.0%}")
print("  token_recall:")
print(dfC.groupby(["compressor", "ratio"])["token_recall"].mean().unstack("compressor").to_string())
print("  coord_success:")
print(dfC.groupby(["compressor", "ratio"])["coord_success"].mean().unstack("compressor").to_string())
print(f"  [{time.time()-t0:.0f}s]", flush=True)

# D: Full power test — 20 wl/fam, Wilcoxon needs pairs
print("\n=== D: Power test, 20 wl/fam, 3 families ===", flush=True)
dfD = run_sweep(SweepConfig(
    compressors=["lingua2", "filter"], ratios=[1.0, 2.0, 4.0, 8.0, 16.0],
    seeds=[0, 1], families=["a", "b", "c"], n_workloads=20,
    out_dir="results/bt_h12_power",
))
v1D = compute_h1_verdict(dfD)
v2D = compute_h2_verdict(dfD)
print(f"  H1={v1D.get('h1_supported')}")
for comp in ["lingua2", "filter"]:
    d = v1D.get(comp, {})
    if isinstance(d, dict) and "rho" in d:
        ci_lo = d.get("ci_low", float("nan"))
        ci_hi = d.get("ci_high", float("nan"))
        print(f"    {comp}: rho={d['rho']:.3f} [{ci_lo:.3f}, {ci_hi:.3f}] n={d.get('n')}")
print(f"  H2={v2D['h2_supported']} ({v2D['n_significant_cliffs']}/{v2D['total_cells']})")
for c in v2D["cells"]:
    p = c.get("test_p_holm")
    p_s = f"{p:.4f}" if p is not None else "N/A"
    lt = c.get("logistic_tau")
    lt_s = f"{lt:.1f}" if lt and not np.isnan(lt) else "N/A"
    print(f"    {c['compressor']}/{c['family']}: log_tau={lt_s} pairs={c.get('n_pairs',0)} p_holm={p_s}")
print(f"  [{time.time()-t0:.0f}s]", flush=True)

print(f"\nH1/H2 battle test done in {time.time()-t0:.0f}s")
