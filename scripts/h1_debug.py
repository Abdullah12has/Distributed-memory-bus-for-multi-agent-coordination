import csv, collections
ratios = collections.defaultdict(set)
wls = collections.defaultdict(set)
sample = []
with open("results/h1_h2_v2/results.csv") as f:
    for i, row in enumerate(csv.DictReader(f)):
        if row["metric"] in ("qa_f1", "coord_success"):
            ratios[(row["compressor"], row["metric"])].add(row["ratio"])
            wls[(row["compressor"], row["metric"])].add(row["workload_id"])
        if i < 3:
            sample.append(row)
lines = []
for s in sample:
    lines.append(str({k: s[k] for k in ["compressor","ratio","workload_family","workload_id","metric","value"]}))
for k in sorted(ratios):
    lines.append(f"{k}: ratios={sorted(ratios[k])[:12]} nwl={len(wls[k])} egwl={sorted(wls[k])[:2]}")
open("/tmp/dbg.txt","w").write("\n".join(lines)+"\n")
print("ok")
