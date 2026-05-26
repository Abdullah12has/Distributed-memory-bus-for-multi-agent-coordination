"""Recompute critical_token_recall with the fixed metric and re-validate theorem."""
import json, re, time, math
import pandas as pd
import numpy as np

t0 = time.time()

from m6.memory_bus.schemas import Fragment
from m6.compressors import make_compressor as build_compressor
from m6.theory.cliff_prediction import predicted_tau
from m6.experiments.run_h1_h2 import critical_token_recall as critical_token_recall_fixed


# Load workloads
workloads_by_fam = {}
for fam in ["a", "b", "c"]:
    wls = []
    with open(f"data/processed/c1-v0.1/family-{fam}.jsonl") as f:
        for line in f:
            wls.append(json.loads(line))
    workloads_by_fam[fam] = wls[:10]
    n_frags = sum(len(w["fragments"]) for w in wls[:10])
    print(f"Family {fam}: {len(wls[:10])} workloads, {n_frags} fragments")

ratios = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0]
phi3_ratios = [1.0, 2.0, 4.0, 8.0, 12.0, 16.0]
compressor_names = ["lingua2", "filter"]  # phi3 excluded: Ollama too slow while H5 running

rows = []
for comp_name in compressor_names:
    comp_ratios = phi3_ratios if comp_name == "phi3-extractive" else ratios
    for ratio in comp_ratios:
        comp = build_compressor(comp_name, target_ratio=ratio)
        for fam in ["a", "b", "c"]:
            for wl in workloads_by_fam[fam]:
                # Use workload-level initial_prompt as task_hint (matches main sweep)
                hint = wl.get("initial_prompt", "")
                for frag_d in wl["fragments"]:
                    frag = Fragment(
                        fragment_id=frag_d["fragment_id"],
                        text=frag_d["text"],
                        tags=frag_d.get("tags", {}),
                        task_hint=hint,
                    )
                    if ratio == 1.0:
                        ct = frag.text
                    else:
                        slot = comp.compress(frag)
                        ct = comp.decompress(slot) or frag.text

                    ctr = critical_token_recall_fixed(frag.text, ct, fam)
                    rows.append({
                        "compressor": comp_name,
                        "ratio": ratio,
                        "family": fam,
                        "critical_token_recall": ctr,
                    })

        elapsed = time.time() - t0
        print(f"  {comp_name} @ {ratio}x done ({elapsed:.0f}s)", flush=True)

df = pd.DataFrame(rows)
df.to_csv("results/h1_h2_final/critical_token_recall_fixed.csv", index=False)
print(f"\nDone in {time.time()-t0:.0f}s, {len(df)} rows")

# Print curves
print("\n" + "=" * 70)
print("CRITICAL TOKEN RECALL CURVES (FIXED)")
print("=" * 70)
for comp in compressor_names:
    for fam in ["a", "b", "c"]:
        sub = df[(df.compressor == comp) & (df.family == fam)]
        if sub.empty:
            continue
        agg = sub.groupby("ratio")["critical_token_recall"].mean()
        vals = ", ".join(f"{r:.0f}x:{v:.3f}" for r, v in zip(agg.index, agg.values))
        print(f"{comp}/{fam}: {vals}")
    print()

# Theorem validation
print("=" * 70)
print("THEOREM VALIDATION — CRITICAL_TOKEN_RECALL vs TOKEN_RECALL")
print("=" * 70)

df_full = pd.read_csv("results/h1_h2_final/sweep_results.csv")

print(f"\n{'comp':<20s} {'fam':<6s} {'metric':<10s} {'observed':>10s} {'predicted':>10s} {'error':>8s} {'match':>6s}")
print("-" * 72)

for comp in compressor_names:
    for fam in ["a", "b", "c"]:
        cs = df_full[(df_full.compressor == comp) & (df_full.family == fam)]
        if cs.empty:
            continue
        agg_cs = cs.groupby("ratio")["coord_success"].mean().sort_index()

        # Find observed cliff midpoint
        prev_r, prev_cs = None, None
        cliff_mid = None
        for r, v in agg_cs.items():
            if prev_r is not None and prev_cs >= 0.5 and v < 0.5:
                frac = (prev_cs - 0.5) / (prev_cs - v) if prev_cs != v else 0.5
                cliff_mid = prev_r + frac * (r - prev_r)
                break
            if v >= 0.5:
                prev_r, prev_cs = r, v

        if cliff_mid is None:
            if agg_cs.iloc[0] < 0.5:
                cliff_mid = 1.0
            elif agg_cs.iloc[-1] >= 0.5:
                print(f"{comp:<20s} {fam:<6s} {'—':<10s} {'NO CLIFF':>10s}")
                continue

        theta = 0.5

        # token_recall prediction
        tr = cs.groupby("ratio")["token_recall"].mean()
        curve_tr = list(zip(tr.index.tolist(), tr.values.tolist()))
        pred_tr = predicted_tau(curve_tr, n_compression_passes=1, theta=theta)
        err_tr = abs(pred_tr - cliff_mid) if pred_tr != float("inf") else float("nan")
        match_tr = err_tr <= 1.0 if not math.isnan(err_tr) else False

        # critical_token_recall prediction
        ctr_sub = df[(df.compressor == comp) & (df.family == fam)]
        valid = ctr_sub.groupby("ratio")["critical_token_recall"].mean().dropna()
        if len(valid) >= 2:
            curve_ctr = list(zip(valid.index.tolist(), valid.values.tolist()))
            pred_ctr = predicted_tau(curve_ctr, n_compression_passes=1, theta=theta)
            err_ctr = abs(pred_ctr - cliff_mid) if pred_ctr != float("inf") else float("nan")
            match_ctr = err_ctr <= 1.0 if not math.isnan(err_ctr) else False
        else:
            pred_ctr = float("nan")
            err_ctr = float("nan")
            match_ctr = False

        def fmt(v):
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                return "inf" if math.isinf(v) else "NaN"
            return f"{v:.2f}"

        print(f"{comp:<20s} {fam:<6s} {'tok_rec':<10s} {fmt(cliff_mid):>10s} {fmt(pred_tr):>10s} {fmt(err_tr):>8s} {'YES' if match_tr else 'no':>6s}")
        print(f"{'':<20s} {'':<6s} {'crit_rec':<10s} {fmt(cliff_mid):>10s} {fmt(pred_ctr):>10s} {fmt(err_ctr):>8s} {'YES' if match_ctr else 'no':>6s}")

# Summary
print("\n" + "=" * 70)
print("COMPARISON: token_recall vs critical_token_recall curves")
print("=" * 70)
for comp in ["lingua2", "filter"]:
    for fam in ["a", "b", "c"]:
        tr = df_full[(df_full.compressor == comp) & (df_full.family == fam)]
        ctr = df[(df.compressor == comp) & (df.family == fam)]
        if tr.empty or ctr.empty:
            continue
        tr_agg = tr.groupby("ratio")["token_recall"].mean()
        ctr_agg = ctr.groupby("ratio")["critical_token_recall"].mean()
        print(f"\n{comp}/{fam}:")
        print(f"  {'ratio':>6s}  {'tok_recall':>10s}  {'crit_recall':>11s}  {'gap':>6s}")
        for r in sorted(set(tr_agg.index) & set(ctr_agg.index)):
            t = tr_agg.get(r, float("nan"))
            c = ctr_agg.get(r, float("nan"))
            g = t - c if not (math.isnan(t) or math.isnan(c)) else float("nan")
            print(f"  {r:6.0f}x  {t:10.3f}  {c:11.3f}  {g:6.3f}")
