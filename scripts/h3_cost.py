import csv, collections, statistics

rows = collections.defaultdict(lambda: collections.defaultdict(list))
metrics = set()
with open("results/h3_final/results.csv") as f:
    for r in csv.DictReader(f):
        pipe = r["pipeline"]
        m = r["metric"]
        metrics.add(m)
        try:
            v = float(r["value"])
        except Exception:
            continue
        # regime encoded in experiment_id or task_hint? group by pipeline+config_hash
        key = (pipe, r.get("config_hash", "")[:8])
        rows[key][m].append(v)

print("METRICS:", sorted(metrics))
print()
# Aggregate by pipeline+config
for key in sorted(rows):
    d = rows[key]
    summ = {m: round(statistics.mean(v), 5) for m, v in d.items() if v}
    print(key, summ)
