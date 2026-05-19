# Hypothesis Implementation Plan

Per-hypothesis cookbook: **(a)** the precise computation, **(b)** the input/output schema, **(c)** the configuration knobs, **(d)** the test that decides "supported / falsified", **(e)** the wallclock budget on the M4 Pro 48 GB. Read this beside `TECHNICAL_REFERENCE.md` S4 -- the reference defines the *why*, this document defines the *how* and the *order*.

> All cells below use the column names of the canonical results long-format dataframe defined in `m6.evaluation.statistics.LongDF`. Field reference at the bottom of this document.

---

## Index -- when to run what

```
H1 --------> H2 (coordination cliff)
                |
                +---> H3 (RAG pipeline placement)
                       |
                       +---> H4 (tag preservation)
```

The dependency graph is **strict for evaluation** but **not** for code authorship -- you can write all the runners in parallel; you just cannot *run* them out of order without invalidating the comparison.

---

## H1 -- Single-agent QA is a poor predictor of multi-agent coordination

**Runner.** `m6.experiments.h1_qa_vs_coordination`.

**Inputs.**
* C1 benchmark `data/processed/c1-v0.1/`.
* Trained ICAE checkpoint `checkpoints/icae-7b/`.
* Backend `mlx@llama-3.1-8b-instruct`.

**Pipeline.**
1. For each `(compressor c in {lingua2, filter, icae}, ratio r in {1, 2, 4, 8, 16}, workload w in C1, seed s in {0..4})`:
   * Build a **single-agent QA derivative** of the workload -- same source documents, the planner's seed question only, no workers and no critic. Record F1, EM, ROUGE-L.
   * Run the **full planner-worker-critic loop** with the same `(c, r, w, s)`. Record `success`, `subtask_acc`, `rounds`, `critic_flagged_rate`.
2. Compute `delta_qa = qa(r) - qa(1)` and `delta_coord = coord(r) - coord(1)` per workload.
3. Per compressor `c`, compute **Spearman rho** between `delta_qa` and `delta_coord` across the (workload x ratio x seed) Cartesian product, paired bootstrap CI (10 000 resamples).

**Knobs.** `configs/experiments/h1.yaml`.

**Decision.** **Supported** iff Spearman rho < 0.6 for **>= 2 of the 3 compressors** at 7B.

**Output schema.** `results/h1/7b/<run_id>/qa_vs_coord.csv`:

| Column | Type | Meaning |
|--------|------|---------|
| `compressor` | str | `lingua2` \| `filter` \| `icae` |
| `ratio` | float | 1 / 2 / 4 / 8 / 16 |
| `workload_family` | str | a / b / c |
| `workload_id` | str | `c1-{family}-{n:03d}` |
| `seed` | int | 0..4 |
| `qa_f1` | float | single-agent F1 |
| `qa_em` | float | single-agent EM |
| `coord_success` | int | 0/1 |
| `coord_subtask_acc` | float | [0, 1] |
| `coord_rounds` | int | rounds to DONE |
| `coord_critic_flagged_rate` | float | [0, 1] |
| `delta_qa` | float | `qa_f1(r) - qa_f1(1)` |
| `delta_coord` | float | `coord_success(r) - coord_success(1)` |

Plus `spearman.json` with `{compressor -> {rho, p_value, ci_low, ci_high}}`.

**Wallclock.** ~2 days (3 compressors x 5 ratios x 5 seeds x 150 workflows x 2 modes = 22 500 runs at ~6 s/run on 7B fp16).

---

## H2 -- A coordination cliff tau* exists and is task-dependent

**Runner.** `m6.experiments.h2_coordination_cliff`.

**Inputs.** Same as H1 (C1 benchmark, ICAE checkpoint, 7B backend).

**Pipeline.**
1. For each `(c, w, s)`: sweep `r in {1, 2, 3, 4, 5, 6, 8, 10, 12, 16}` (denser around the suspected cliff).
2. Average across seeds -> `(r, coord_success)` curve.
3. **Fit `m6.evaluation.cliff_fitting.fit_piecewise(...)`** -> `(tau, slope_left, slope_right, drop_rel)`.
4. **Mann-Whitney U** `coord(r < tau)` vs `coord(r >= tau)`. These two samples are **independent** -- they are drawn across different `(workload, seed, ratio)` cells, not paired -- so the signed-rank test is inappropriate; a rank-sum test is the right one.
5. Across `c in compressors`, compare tau within each `w`. Effect size = `max_tau - min_tau` as a fraction of mean.

**Decision.**
* Cliff at cell `(c, w)` iff `drop_rel >= 0.30` **and** Mann-Whitney p < 0.05 (Holm-adjusted within the {H1, H2} family).
* "varies by workload but not by compressor within +/-20%" iff for each w, `(max_tau - min_tau)/mean_tau <= 0.20`.

**Output.** `results/h2/7b/<run_id>/cliff_per_cell.csv`:

| Column | Type |
|--------|------|
| `compressor` | str |
| `workload_family` | str |
| `tau` | float |
| `slope_left` | float |
| `slope_right` | float |
| `drop_rel` | float |
| `rmse` | float |
| `mann_whitney_U` | float |
| `mann_whitney_p` | float |
| `mann_whitney_p_holm` | float |

**Wallclock.** ~5--10 days for the full 7B sweep.

---

## H3 -- RAG pipeline placement matters

**Runner.** `m6.experiments.h3_rag_placement`.

**Inputs.**
* C1 family (a) workloads (cross-document fact aggregation) + NarrativeQA + HotpotQA for external comparability.
* Three pipelines: `P1`, `P2`, `P3` from `m6.pipelines.*`.

**Pipeline.**
1. Build two budget configurations.
   * **Storage-bounded.** FAISS index size capped at 100 MB. Both P1 and P2 tune chunking until index size <= 100 MB.
   * **Accuracy-bounded.** Retrieval recall@10 capped at 0.85. Both P1 and P2 tune retrieval until R@10 <= 0.85.
2. For each `(pipeline, budget, ratio in {2, 4, 8}, seed)`: run the workload, record `f1`, `eur_per_query`, `latency_p50_ms`, `latency_p95_ms`.
3. P3 swept on `(theta_high, theta_low) in {(.75,.45), (.7,.5), (.8,.4)}`.

**Decision.**
* P1 vs P2 effect size >= **5 pp F1** with paired-bootstrap CI excluding 0 in *both* budget modes (sign flips per the H3 claim).
* P3 wins on the combined `f1 / eur_per_query` ranking with Holm-adjusted p < 0.05.

**Output.** `results/h3/<run_id>/rag_pipeline_results.csv`:

| Column | Type |
|--------|------|
| `pipeline` | str (`P1`/`P2`/`P3`) |
| `budget_mode` | str |
| `ratio` | float |
| `seed` | int |
| `f1` | float |
| `eur_per_query` | float |
| `latency_p50_ms` | float |
| `latency_p95_ms` | float |
| `theta_high` | float \| null |
| `theta_low` | float \| null |
| `faiss_index_mb` | float |
| `recall_at_10` | float |

**Wallclock.** ~3 days.

---

## H4 -- Tag preservation >= 85% at 4x with <= 5 pp accuracy drop

**Runner.** `m6.experiments.h4_tag_preservation`.

**Inputs.**
* `checkpoints/icae-7b/` (baseline) and `checkpoints/icae-7b-tags/` (C4 variant).
* C1 instances with synthetic tags from each of the three tag distributions (uniform / skewed / hierarchical).

**Pipeline.**
1. For each tag distribution, ratio `r in {2, 4, 8}`, seed: compress every fragment in C1 with the C4 variant.
2. Recover tags via the `TagHead`. A fragment's tag is "preserved" iff:
   * `acl_recovered >= acl_true` *OR* `popcount(acl_recovered & acl_true) / popcount(acl_true) >= 0.9`.
   * `class_recovered >= class_true` (lattice ordering).
3. Tag preservation rate = #preserved / #fragments.
4. Accuracy delta: re-run C1 with both checkpoints, paired bootstrap on `success`.

**Decision.**
* **Supported** iff preservation rate >= 0.85 at `r=4` **and** accuracy delta >= -0.05.

**Output.** `results/h4/<run_id>/tag_preservation.csv`:

| Column | Type |
|--------|------|
| `tag_distribution` | str |
| `ratio` | float |
| `seed` | int |
| `preservation_rate_acl` | float |
| `preservation_rate_class` | float |
| `preservation_rate_combined` | float |
| `coord_success_baseline` | float |
| `coord_success_c4` | float |
| `delta_pp` | float |

**Wallclock.** ~1 day.

---

## Long-format dataframe field reference

`m6.evaluation.statistics.LongDF` is the canonical wide schema across all experiments. Every results CSV is a projection of this. Columns:

| Column | Type | Notes |
|--------|------|-------|
| `experiment_id` | str | e.g. `h2-20260315-abc1234-cfg5678` |
| `hypothesis` | str | `h1`..`h4` |
| `compressor` | str | `lingua2` / `filter` / `icae` / `icae-tag` / `none` |
| `ratio` | float | nominal compression ratio (input/output tokens) |
| `actual_ratio` | float | measured; for sanity |
| `pipeline` | str | `none` / `P1` / `P2` / `P3` |
| `model` | str | e.g. `llama-3.1-8b-instruct` |
| `model_size` | str | `7b` |
| `workload_family` | str | `a` / `b` / `c` |
| `workload_id` | str |  |
| `seed` | int |  |
| `metric` | str | `f1` / `em` / `coord_success` / `tag_preservation` / ... |
| `value` | float |  |
| `wallclock_ms` | int |  |
| `eur_cost` | float |  |
| `run_id` | str |  |
| `git_sha` | str |  |
| `config_hash` | str |  |
| `created_at` | str | ISO-8601 UTC |
| `invalid` | bool | True if control-condition variance dominates |
| `invalid_reason` | str \| null |  |
