# Hypothesis Implementation Plan

Per-hypothesis cookbook: **(a)** the precise computation, **(b)** the input/output schema, **(c)** the configuration knobs, **(d)** the test that decides "supported / falsified", **(e)** the wallclock budget on the M4 Pro 48 GB. Read this beside `TECHNICAL_REFERENCE.md` §4 — the reference defines the *why*, this document defines the *how* and the *order*.

> All cells below use the column names of the canonical results long-format dataframe defined in `m6.evaluation.statistics.LongDF`. Field reference at the bottom of this document.

---

## Index — when to run what

```
                     ┌──────── month 0 sanity ───────┐
                     │                                │
   ┌─────────────────┼───── month 2 ────┐             │
   │                 │                  │             │
H1 ────────► H2 ────────► H7 (model-size scaling)
                 │                  ▲
                 │                  │
                 └─►  H3 (training distribution ablation)
                     │
                     └─►  H4 (RAG pipelines)
                          │
                          └─►  H5 (tag preservation)
                               │
                               └─►  H6 (inference disclosure)
                                    │
                                    └─►  H8 (real-trace transfer)  [gated]
```

The dependency graph is **strict for evaluation** but **not** for code authorship — you can write all the runners in parallel; you just cannot *run* them out of order without invalidating the comparison.

---

## H1 — Single-agent QA is a poor predictor of multi-agent coordination

**Runner.** `m6.experiments.h1_qa_vs_coordination`.

**Inputs.**
* C1 benchmark `data/processed/c1-v0.1/`.
* Trained ICAE checkpoint `checkpoints/icae-7b/`.
* Backend `mlx@llama-3.1-8b-instruct`.

**Pipeline.**
1. For each `(compressor c ∈ {lingua2, filter, icae}, ratio r ∈ {1, 2, 4, 8, 16}, workload w ∈ C1, seed s ∈ {0..4})`:
   * Build a **single-agent QA derivative** of the workload — same source documents, the planner's seed question only, no workers and no critic. Record F1, EM, ROUGE-L.
   * Run the **full planner-worker-critic loop** with the same `(c, r, w, s)`. Record `success`, `subtask_acc`, `rounds`, `critic_flagged_rate`.
2. Compute `Δ_qa = qa(r) − qa(1)` and `Δ_coord = coord(r) − coord(1)` per workload.
3. Per compressor `c`, compute **Spearman ρ** between `Δ_qa` and `Δ_coord` across the (workload × ratio × seed) Cartesian product, paired bootstrap CI (10 000 resamples).

**Knobs.** `configs/experiments/h1.yaml`.

**Decision.** **Supported** ⟺ Spearman ρ < 0.6 for **≥ 2 of the 3 compressors** at 7B.

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
| `delta_qa` | float | `qa_f1(r) − qa_f1(1)` |
| `delta_coord` | float | `coord_success(r) − coord_success(1)` |

Plus `spearman.json` with `{compressor → {rho, p_value, ci_low, ci_high}}`.

**Wallclock.** ~2 days (3 compressors × 5 ratios × 5 seeds × 150 workflows × 2 modes = 22 500 runs at ~6 s/run on 7B fp16).

---

## H2 — A coordination cliff τ* exists and is task-dependent

**Runner.** `m6.experiments.h2_coordination_cliff`.

**Inputs.** Same as H1 plus 13B fp16 backend on a sub-sample of 30 workloads.

**Pipeline.**
1. For each `(c, w, s)`: sweep `r ∈ {1, 2, 3, 4, 5, 6, 8, 10, 12, 16}` (denser around the suspected cliff).
2. Average across seeds → `(r, coord_success)` curve.
3. **Fit `m6.evaluation.cliff_fitting.fit_piecewise(...)`** → `(τ, slope_left, slope_right, drop_rel)`.
4. **Mann-Whitney U** `coord(r < τ)` vs `coord(r ≥ τ)`. These two samples are **independent** — they are drawn across different `(workload, seed, ratio)` cells, not paired — so the signed-rank test is inappropriate; a rank-sum test is the right one.
5. Across `c ∈ compressors`, compare τ within each `w`. Effect size = `max_τ − min_τ` as a fraction of mean.

**Decision.**
* Cliff at cell `(c, w)` ⟺ `drop_rel ≥ 0.30` **and** Wilcoxon p < 0.05 (Holm-adjusted within the {H1, H2, H3} family).
* "varies by workload but not by compressor within ±20%" ⟺ for each w, `(max_τ − min_τ)/mean_τ ≤ 0.20`.

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
| `wilcoxon_W` | float |
| `wilcoxon_p` | float |
| `wilcoxon_p_holm` | float |

**Wallclock.** ~5–10 days for 7B + ~3 days for the 13B sub-sample.

---

## H3 — Training distribution: dialogue traces beat QA at matched single-agent accuracy

**Runner.** `m6.experiments.h3_training_distribution`.

**Inputs.**
* Two ICAE checkpoints: `checkpoints/icae-7b-qa/` and `checkpoints/icae-7b-dialogue/`. Both trained with identical optimiser + LoRA config + total step count.
* ~5K dialogue traces generated by `m6.benchmark.dialogue_traces.synthesize(n=5000, ...)` with `compressor=none`.

**Pipeline.**
1. For each checkpoint, evaluate single-agent QA across ratios `r ∈ {1..16}`. Build a `r → qa_f1` curve.
2. Find operating ratios `(r_qa, r_dia)` such that `|qa(r_qa) − qa(r_dia)| ≤ 0.01` (1 pp).
3. At the matched operating point, run **C1 family (a)** with both checkpoints, 5 seeds each.
4. Test `coord_dialogue > coord_qa` with paired bootstrap on matched instances.

**Decision.** Paired-bootstrap p < 0.05 (Holm-adjusted within {H1, H2, H3}).

**Output.** `results/h3/7b/<run_id>/matched_accuracy.csv` + `verdict.json`.

**Wallclock.** ~2 days for two trainings (each ≤ 3 d) parallelisable + ~1 day for the matched evaluation. Trainings happen during Month 4 in parallel with H4.

---

## H4 — RAG pipeline placement matters

**Runner.** `m6.experiments.h4_rag_placement`.

**Inputs.**
* C1 family (a) workloads (cross-document fact aggregation) + NarrativeQA + HotpotQA for external comparability.
* Three pipelines: `P1`, `P2`, `P3` from `m6.pipelines.*`.

**Pipeline.**
1. Build two budget configurations.
   * **Storage-bounded.** FAISS index size capped at 100 MB. Both P1 and P2 tune chunking until index size ≤ 100 MB.
   * **Accuracy-bounded.** Retrieval recall@10 capped at 0.85. Both P1 and P2 tune retrieval until R@10 ≤ 0.85.
2. For each `(pipeline, budget, ratio ∈ {2, 4, 8}, seed)`: run the workload, record `f1`, `eur_per_query`, `latency_p50_ms`, `latency_p95_ms`.
3. P3 swept on `(θ_high, θ_low) ∈ {(.75,.45), (.7,.5), (.8,.4)}`.

**Decision.**
* P1 vs P2 effect size ≥ **5 pp F1** with paired-bootstrap CI excluding 0 in *both* budget modes (sign flips per the H4 claim).
* P3 wins on the combined `f1 / eur_per_query` ranking with Holm-adjusted p < 0.05.

**Output.** `results/h4/<run_id>/rag_pipeline_results.csv`:

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

## H5 — Tag preservation ≥ 85% at 4× with ≤ 5 pp accuracy drop

**Runner.** `m6.experiments.h5_tag_preservation`.

**Inputs.**
* `checkpoints/icae-7b/` (baseline) and `checkpoints/icae-7b-tags/` (C4 variant).
* C1 instances with synthetic tags from each of the three tag distributions (uniform / skewed / hierarchical).

**Pipeline.**
1. For each tag distribution, ratio `r ∈ {2, 4, 8}`, seed: compress every fragment in C1 with the C4 variant.
2. Recover tags via the `TagHead`. A fragment's tag is "preserved" iff:
   * `acl_recovered ⊇ acl_true` *OR* `popcount(acl_recovered ∩ acl_true) / popcount(acl_true) ≥ 0.9`.
   * `class_recovered ≥ class_true` (lattice ordering).
3. Tag preservation rate = #preserved / #fragments.
4. Accuracy delta: re-run C1 with both checkpoints, paired bootstrap on `success`.

**Decision.**
* **Supported** ⟺ preservation rate ≥ 0.85 at `r=4` **and** accuracy delta ≥ −0.05.

**Output.** `results/h5/<run_id>/tag_preservation.csv`:

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

## H6 — Summary-level inference disclosure

**Runner.** `m6.experiments.h6_inference_disclosure`.

**Inputs.**
* C1 fragments with `classification ≥ CONFIDENTIAL` + a hand-curated list of (fragment_id → list[ProtectedFact]) mappings stored in `data/processed/c1-v0.1/protected_facts.jsonl`.
* `gpt-4o-mini` API key.

**Pipeline.**
1. **Priors-only baseline.** Reader sees only the workload preamble (no compressed summary). Asks the same yes/no protected-fact questions. Record recall = `true_positive_rate`.
2. **Baseline compressor.** Compress fragments with `icae` (no tag head). Show reader the summary only. Record recall.
3. **C4 compressor.** Same with `icae-tag`. Record recall.

**Decision.**
* Metric measures something real ⟺ `recall(baseline) > recall(priors_only)` with paired bootstrap p < 0.05 (Holm within {H5, H6}).
* C4 reduces disclosure ⟺ `recall(c4) < recall(baseline)` at matched ratio, paired bootstrap p < 0.05.

**Output.** `results/h6/<run_id>/inference_disclosure.csv`:

| Column | Type |
|--------|------|
| `condition` | str (`priors_only`/`baseline`/`c4`) |
| `ratio` | float \| null |
| `seed` | int |
| `recall_protected` | float |
| `false_positive_rate` | float |
| `judge_model` | str |
| `cost_eur` | float |

**Wallclock.** ~1 day; cost ~ EUR 30 in OpenAI API.

---

## H7 — Cliff τ* shifts with model size

**Runner.** `m6.experiments.h7_model_size_scaling`.

**Inputs.**
* MLX-LM 7B + 13B; `llama.cpp` 34B-int4 + 70B-int4.

**Pipeline.**
1. **7B** — full sweep already in H2.
2. **13B** — full sweep on family (a) cross-document fact aggregation (the most discriminative; plan §5.4). 30-workload sub-sample.
3. **34B-int4** — focused sweep at `r ∈ {τ_13B − 2, τ_13B, τ_13B + 2}` plus a coarse sanity at `r ∈ {1, 16}`. 15 workloads.
4. **70B-int4** — **single point** at `r = τ_34B` with 5 seeds, 10 workloads. **Pre-run NarrativeQA sanity check** (§8 backend startup) — abort if F1 drop > 5 pp.

**Decision.** Monotonically non-decreasing τ across `{7B, 13B, 34B-int4, 70B-int4}` on **≥ 2 of 3 workload families**. (70B is single-point on family (a) only; the H7 evaluation extends to families (b)/(c) at 7B/13B only.)

**Output.** `results/h7/<run_id>/model_size_scaling.csv`:

| Column | Type |
|--------|------|
| `model_size` | str (`7b`/`13b`/`34b-int4`/`70b-int4`) |
| `workload_family` | str |
| `ratio` | float |
| `seed` | int |
| `coord_success` | float |
| `qa_f1` | float |
| `tokens_per_second` | float |
| `narrativeqa_sanity_f1` | float \| null |
| `tau_fit` | float \| null |

**Wallclock.** ~3 weeks (driven by 70B int4 wallclock at 3–5 tok/s).

---

## H8 — Real M0/M1/M2 trace transfer

**Runner.** `m6.experiments.h8_real_trace_transfer`.

**Pre-condition.** `docs/agent_readiness.yaml` reports at least one of `{m0, m1, m2}` as `ready=true`. Otherwise the runner short-circuits and writes `documented-as-deferred` per `scope-signoff.md`.

**Inputs.** Real trace files exported by Mohammad / Faisal / Vu. Loader at `m6.corpus.loader.RealTraceLoader`.

**Pipeline.**
1. Reconstruct 2–3 cross-system workflows from the traces into `Workload` instances.
2. Run the H2 procedure on these workflows.
3. Compare τ\* and coordination-success curves to the synthetic results.

**Decision.** Match within ±15% on τ\* and ±10 pp on coordination success.

**Output.** `results/h8/<run_id>/real_vs_synth.csv` + `manifest.yaml` with the agent_readiness snapshot.

**Wallclock.** Gated on connector readiness, not compute.

---

## Long-format dataframe field reference

`m6.evaluation.statistics.LongDF` is the canonical wide schema across all experiments. Every results CSV is a projection of this. Columns:

| Column | Type | Notes |
|--------|------|-------|
| `experiment_id` | str | e.g. `h2-20260315-abc1234-cfg5678` |
| `hypothesis` | str | `h1`..`h8` |
| `compressor` | str | `lingua2` / `filter` / `icae` / `icae-tag` / `none` |
| `ratio` | float | nominal compression ratio (input/output tokens) |
| `actual_ratio` | float | measured; for sanity |
| `pipeline` | str | `none` / `P1` / `P2` / `P3` |
| `model` | str | e.g. `llama-3.1-8b-instruct` |
| `model_size` | str | `7b` / `13b` / `34b-int4` / `70b-int4` |
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
