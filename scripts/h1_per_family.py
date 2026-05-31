import csv, collections, statistics
import scipy.stats as ss

# wide format: compressor,ratio,family,workload_id,seed,qa_f1,qa_em,coord_success,...
rows = []
comps = set()
with open("results/h1_h2_v2/sweep_results.csv") as f:
    for r in csv.DictReader(f):
        try:
            rows.append({
                "comp": r["compressor"], "fam": r["family"], "wl": r["workload_id"],
                "ratio": float(r["ratio"]), "qa": float(r["qa_f1"]),
                "co": float(r["coord_success"]),
            })
            comps.add(r["compressor"])
        except Exception:
            continue

# mean over seeds per (comp,wl,ratio)
agg = collections.defaultdict(lambda: collections.defaultdict(list))
fam_of = {}
for d in rows:
    k = (d["comp"], d["wl"], d["ratio"])
    agg[k]["qa"].append(d["qa"]); agg[k]["co"].append(d["co"])
    fam_of[d["wl"]] = d["fam"]
mean = {k: (statistics.mean(v["qa"]), statistics.mean(v["co"])) for k, v in agg.items()}

def calc(comp, fam=None, wl_level=False):
    wls = set(k[1] for k in mean if k[0] == comp and (fam is None or fam_of[k[1]] == fam))
    ratios = sorted(set(k[2] for k in mean if k[0] == comp))
    if not ratios:
        return ("no-data", 0)
    base = min(ratios); xs = []; ys = []
    for wl in wls:
        dq = []; dc = []
        for r in ratios:
            if r == base:
                continue
            kb = (comp, wl, base); kr = (comp, wl, r)
            if kb in mean and kr in mean:
                dq.append(mean[kr][0] - mean[kb][0])
                dc.append(mean[kr][1] - mean[kb][1])
        if wl_level:
            if dq:
                xs.append(statistics.mean(dq)); ys.append(statistics.mean(dc))
        else:
            xs += dq; ys += dc
    n = len(xs)
    if n < 3 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return ("flat/NA", n)
    res = ss.spearmanr(xs, ys)
    return (round(float(res.statistic), 3), f"{float(res.pvalue):.1e}", n)

out = ["ALL COMPRESSORS: " + str(sorted(comps))]
for c in sorted(comps):
    if c == "identity":
        continue
    out.append("")
    out.append(f"{c}: pooled={calc(c)} | wl-level={calc(c, wl_level=True)}")
    for fam in ["a", "b", "c"]:
        out.append(f"    fam-{fam}: pooled={calc(c, fam)} | wl-level={calc(c, fam, True)}")
text = "\n".join(out)
print(text)
open("/tmp/h1_result.txt", "w").write(text + "\n")
