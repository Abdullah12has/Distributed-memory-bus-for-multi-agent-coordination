# Canonical Numbers Registry

**Provenance.** Every number below was read directly off the on-disk result
JSON/CSV of *The Coordination Cliff: How Context Compression Breaks Multi-Fragment LLM Workflows* on 2026-06-01, against
files produced on each run's completion date (H1/H2-v2 2026-05-27,
H4-unbiased-v2 2026-05-29, H5 2026-05-27, frontier 2026-05-28, CAAC 2026-05-29,
A3/bus/finegrid 2026-05-31). Host facts confirmed: the Ollama binary is at
`/usr/local/bin/ollama` with real digests (`phi3:latest` = `4f2222927938`,
`llama3.1:8b` = `46e0c10c039e`; `qwen2.5:1.5b-instruct-q4_K_M` not pulled on
this host); this repo does **not** use Git LFS (no `.gitattributes`, `git lfs`
not installed — all result files are plain on-disk files); the C1 master seed is
`20260514` (`data/processed/c1-v0.1/manifest.json`). Each value is the figure
read from the cited file with the exact JSON key/extraction noted. Where the
figure differs from the number quoted in the originating task brief, the
discrepancy is flagged and the **file value is used** (the file is ground
truth). **No value in this file is a placeholder.**

> **2026-06-04 reconciliation pass.** Three earlier "discrepancy" notes (H1
> workload-level ρ, the frontier Qwen-72B τ, and the fine-grid family-a "~1.1"
> cliff) were **false alarms** — they were written by inspecting only the
> `verdicts.json` files and never running the workload-level collapse or the
> 0.5×p0-crossing the manuscript actually reports. All three manuscript figures
> were re-derived directly on the GPU and **match**; the notes below are
> corrected accordingly. The one real change: the frontier claim was re-anchored
> from `frontier_qwen72b_e2` (broken logistic fit on its extended grid) onto the
> validated n=10 `frontier_qwen72b` run.

> **Important — two H1/H2 datasets exist.** `results/h1_h2_v2/` is the canonical
> 4-compressor run cited by the manuscript verdict tables;
> `results/h1_h2_finegrid/` is a 2026-05-31 dense-ratio re-run with 3
> compressors. They give different ρ and τ values. This registry quotes the
> **v2** file as canonical and notes the finegrid value where relevant.

---

## H1 — Information preservation vs coordination (Spearman ρ)

Source: `results/h1_h2_v2/verdicts.json`, key `h1.<compressor>.rho` (with CI
`ci_low`/`ci_high`, `n`).

| Compressor | ρ | 95% CI | n | supported |
|---|---|---|---|---|
| filter | **-0.5927** | [-0.6405, -0.5416] | 1350 | true |
| lingua2 | **+0.3810** | [0.3445, 0.4178] | 1350 | true |
| phi3-extractive | **+0.1930** | [0.1311, 0.2521] | 750 | true |
| truncation | **+0.3837** | [0.3491, 0.4179] | 1350 | true |

`h1.h1_supported=true`, all four below the 0.6 threshold.

> **Two H1 statistics, both correct (resolved 2026-06-04 by recomputation on
> the GPU).** `verdicts.json` stores the **pooled** Spearman rho over all
> (workload x ratio) delta-pairs (n=1350/750): filter -0.593, lingua2 +0.381,
> phi3 +0.193, truncation +0.384 (the table above). The manuscript's
> `tab:h1_rho` *also* reports a **workload-level** rho (n=150): for each
> compressor, collapse the 1350 delta-pairs to one mean (delta_qa, delta_coord)
> per workload, then Spearman over the 150 workloads. That column is **not**
> stored in `verdicts.json` (the verdict pipeline `run_h1_h2.py:_verdict_h1`
> only emits the pooled rho), but it **reproduces exactly** from
> `h1_h2_v2/sweep_results.csv`: filter **-0.818** (CI[-0.854,-0.762]), lingua2
> **+0.026** (CI[-0.128,+0.177]), phi3 **+0.315** (CI[+0.181,+0.442]),
> truncation **+0.051** (CI[-0.097,+0.197]) -- matching the manuscript and the
> abstract's "[-0.82,+0.32]" range. The pooled->workload drop (lingua2
> +0.381->+0.026; truncation +0.384->+0.051) is the pseudo-replication effect
> H1 reports, and it is real. **An earlier note here calling these values
> "not on disk" was a false alarm: it inspected only `verdicts.json` and never
> ran the workload-level collapse.** Both columns are canonical.

## H2 — Coordination cliff

Source: `results/h1_h2_v2/verdicts.json`, `h2`.

| Field | Value | Key |
|---|---|---|
| Significant cells | **11 / 12** | `h2.n_significant_cliffs=11`, `h2.total_cells=12` |
| Only non-significant cell | filter / family-c (τ null, drop 0.0, n_pairs 0) | `h2.cells[2]` |
| τ* (model_selected, logistic) | most cells 2.5; lingua2/c 6.696; phi3/b 4.865; truncation/c 4.950 | `h2.cells[*].tau` (after logistic selection) |
| τ spread (family-c) | 106.25 % (>20 %) | `h2.tau_spread.c.spread_pct` |
| Verdict | `h2.h2_supported=true` | — |

(Brief's "11/12 cells significant" matches the file exactly. Note the headline
τ* values reported in `cells[*].tau` are mostly the logistic 2.5; the raw
piecewise τ values are much larger — both are stored.)

## Compounding-error model (per-family τ* match rate)

| Field | Value | Source / key |
|---|---|---|
| In-sample match (±25 %) | **33.3 % = 4/12** | `results/h1_h2_v2/theorem1_validation_per_family.json` `_summary.match_rate=0.3333`, `n_match=4` |
| Leave-one-out match | **25 % = 3/12** | `results/h1_h2_v2/theorem1_validation_loo.json` `_summary.match_rate=0.25`, `n_match=3` |
| LOO match at ±50 % | 75 % = 9/12 | `theorem1_validation_loo.json` `_summary.match_rate_50pct=0.75` |
| Per-family θ_q (in-sample) | a 0.6324, b 0.8376, c 0.5896 | `theorem1_validation_per_family.json` `_summary.per_family_theta` |
| Recall column | `critical_token_recall` | `theorem1_validation_loo.json` `_summary.recall_column` |

(Both 33 % in-sample and 25 % LOO match the brief.)

---

## Corollary 1 — Ceiling-Cliff Separation

| Field | Value | Source / key |
|---|---|---|
| Local τ spread (family-c) | **23.91 %** (>20 % bar, `is_invariant=false`) | `results/h5_final/model_independence_20pct.json` `per_family.c.tau_spread_pct`; per-model τ 1.5B 3.694 / 3.8B 4.681 / 8B 4.012; `tau_mean=4.129` |
| Qwen-72B τ (n_boot=500) | **2.677**, CI [1.917, 7.231], diff **0.83 %** from synth 2.700, CI contains synth | `results/frontier_qwen72b/verdicts.json` `frontier_tau`, `frontier_tau_ci`, `comparison.tau_diff_pct=0.83`, `tau_ci_contains_synth=true` |
| Qwen-72B re-run (e2, +2.5 ratio) | τ **7.235**, CI [1.773, 7.277], diff 40.46 %, CI does **not** contain synth (12.153) | `results/frontier_qwen72b_e2/verdicts.json` `frontier_tau`, `comparison` |
| DeepSeek-V4-Pro τ | **2.155**, CI [1.764, 7.140], diff 20.18 %, CI contains synth | `results/frontier_deepseekv4/verdicts.json` `frontier_tau`, `comparison.tau_diff_pct=20.18` |
| TOST equivalence (Qwen, ±20 %) | **NOT equivalent**; frac_boot_in_band 0.22 | `results/tost_corollary1.json` `frontier_qwen72b.tost_vs_synth.equivalent_pm20=false` |
| TOST equivalence (DeepSeek, ±20 %) | **NOT equivalent**; frac_boot_in_band 0.06 | `results/tost_deepseek.json` `tost_vs_synth.equivalent_pm20=false` |

> **Notes / discrepancies vs brief:**
> - Brief said Qwen-72B CI [1.92, 7.23] and DeepSeek τ 2.155 — both match.
> - **Frontier anchor = the n=10 `frontier_qwen72b` run** (τ=2.677, diff 0.83 %,
>   CI contains synth, `theorem_validated=true`) — clean and file-backed. The
>   manuscript (§4.5 / §4.6.2 / §4.6.5) was re-anchored onto it on 2026-06-04.
>   The `frontier_qwen72b_e2` re-run's stored `frontier_tau=7.235` and
>   `synth_tau=12.153` are a **broken logistic fit on its extended ratio grid**:
>   its curve {1:1.0, 2:0.8, 2.5:0.68, 3:0.373, 4:0.133, 6:0.0} 0.5-crosses at
>   **~2.79** (verified on GPU), so a fitted midpoint of 7.235 is degenerate —
>   the curve is consistent with no-shift even though the parametric fit failed.
>   e2 is now cited only as a robustness re-run by 0.5-crossing (~2.79), not as
>   the load-bearing cell. The "2.79" the manuscript quotes IS the verified e2
>   0.5-crossing, not the broken stored `frontier_tau`.
> - Brief framed TOST as the headline against ±10 %; the on-disk TOST uses a
>   **±20 %** equivalence band (`method` string) and both reject equivalence.
> - CI-overlap supports invariance for the original runs; TOST does not
>   establish equivalence. `h5_final/model_independence_20pct.json` itself
>   reports `corollary1_supported=false` at the strict 20 % local bar — the
>   binary verdict rests on the frontier CI-overlap evidence per ADR-006.

## Corollary 2 — Information Density Scaling

Source: `results/corollary2_theta_info.json` (`<task>.theta_info`).

| Task | θ_info | Aux | Key |
|---|---|---|---|
| C1 family-a | **0.967** | baseline 1.0, τ 2.0 | `C1_family_a.theta_info` |
| MultiHopRAG | **0.484** | baseline 0.347, τ 3.0 | `MultiHopRAG.theta_info` |
| HotpotQA | **0.373** | baseline 0.593, τ NaN | `HotpotQA.theta_info` |

(All three match the brief.)

> **Family-c θ_info ≈ 0.62 (cited in `implementation.tex` §3.5) is reproducible
> but not stored in this JSON.** The JSON holds only the three *cross-benchmark*
> tasks of the Corollary 2 comparison (family-a vs MultiHopRAG vs HotpotQA);
> family-c is an internal C1 density anchor, not part of that comparison.
> θ_info is `1 − normalized-AUC` of the per-task lingua2 coordination curve;
> recomputed on the GPU from `h1_h2_v2/sweep_results.csv` it gives **family-a
> 1−0.033 = 0.967** (matching the stored value, confirming the method) and
> **family-c 1−0.383 = 0.617 ≈ 0.62** (matching the prose). So the 0.62 is a
> correct, method-consistent number, not an untraceable one; it is simply not
> persisted because family-c is outside the three-benchmark Corollary 2 set.

---

## H3 — RAG pipeline placement (NOT SUPPORTED)

| Field | Value | Source |
|---|---|---|
| P1−P2 (storage-bounded) | **3.24 pp**, CI [1.84, 4.72], p=0.0001, leader P3 | `results/h3_final/verdicts.json` `regimes.storage_bounded.p1_vs_p2_diff_pp` |
| P1−P2 (accuracy-bounded) | **2.02 pp**, CI [1.15, 2.85], p=0.0001, leader P3 | `results/h3_final/verdicts.json` `regimes.accuracy_bounded.p1_vs_p2_diff_pp` |
| Verdict | no sign-flip, P3 dominates, `h3_supported=false` | `results/h3_final/verdicts.json` |
| EUR/query mean P1 | **1.70e-04** (n=300) | `results/h3_eprice/results.csv`, mean of `eur_per_query` where `pipeline=P1` |
| EUR/query mean P2 | **1.63e-04** (n=300) | `results/h3_eprice/results.csv`, `pipeline=P2` |
| EUR/query mean P3 | **1.68e-04** (n=300) | `results/h3_eprice/results.csv`, `pipeline=P3` |

> **Settled (2026-06-04). `tab:h3` is now column-attributed across two runs.**
> The two H3 runs give different per-query EUR because `h3_eprice` is the
> *cost-instrumented re-run*: `h3_final` eur_per_query ≈ 3e-5 (storage P1 2.72e-5
> / P2 2.82e-5 / P3 3.07e-5; accuracy 3.29 / 3.00 / 3.10e-5; spread 9.8–12.8%),
> while `h3_eprice` eur_per_query ≈ 1.7e-4 (storage 1.67 / 1.61 / 1.67e-4;
> accuracy 1.74 / 1.66 / 1.68e-4; spread **4.1–4.9%**). The manuscript's appendix
> text quotes the **4.1–4.9%** spread, i.e. the `h3_eprice` figure — so the
> table's EUR column is taken from `h3_eprice` (matching the text) while **F1 and
> achieved-ratio stay from `h3_final`** (where the P1−P2 verdict 3.24/2.02 pp and
> its BCa CIs are computed). The caption attributes each column to its run. The
> table originally carried `h3_final` EUR (~3e-5), which contradicted its own
> "4.1–4.9%" text; corrected 2026-06-04. No conclusion depends on the EUR
> magnitude (the thesis makes **no cost-parity / Pareto claim**).

## H4 — Protected-fact recovery (per-compressor reduction)

Source: `results/h4_unbiased_v2/verdicts.json`. baseline_rate 0.7821, priors_rate
0.4964 (signal gap 0.2857, p=0.0001 all). Reader `llama3.1:8b`.

| Compressor | Reduction | p | Key |
|---|---|---|---|
| truncation | **-24.6 pp** | 0.0001 (sig) | `per_compressor.truncation.reduction_test.diff=0.2464` |
| filter | **-20.4 pp** | 0.0001 (sig) | `per_compressor.filter.reduction_test.diff=0.2036` |
| lingua2 | **-18.9 pp** | 0.0001 (sig) | `per_compressor.lingua2.reduction_test.diff=0.1893` |
| phi3-extractive | **-0.4 pp** | **0.9082** (not sig) | `per_compressor.phi3-extractive.reduction_test.diff=0.0036, p=0.9082` |

`h4_supported=true`. (All four values match the brief exactly.)

---

## CAAC — operating-point selection

Source: `results/caac/verdicts.json` (per_compressor for lingua2, filter).

| Field | Value | Key |
|---|---|---|
| Strict-Pareto (cliff ratios) | **0** for both lingua2 and filter (expected per ADR-007) | `per_compressor.*.n_strict_cliff=0`, `passes_strict_pareto=false` |
| Weak dominance (all ratios) | rate **1.0** (both compressors) | `per_compressor.*.weak_dominance_rate_all=1.0` |
| Operating-point pass | filter passes (16.7 pp at max ratio), lingua2 fails (2.67 pp) | `per_compressor.*.passes_operating_point` |
| Verdict | strict NOT SUPPORTED; operating-point SUPPORTED | `verdict`, `operating_point_verdict` |
| Config | cliff_ratio 4.0, op threshold 15.0 pp | `cliff_ratio`, `operating_point_threshold_pp` |

> **Discrepancy:** brief said "strict-Pareto 0/7, weak dominance 14/14, plateaus
> 33%/50%". The `results/caac/verdicts.json` file is keyed per inner compressor
> (lingua2, filter), reporting strict_cliff=0 (matches "0") and
> weak_dominance_rate_all=1.0 (i.e. fully weakly dominant — consistent with
> "14/14"). The "0/7" config count and "33%/50% plateau" figures are not stored
> as such in this verdicts file; the strict-Pareto = 0 and full weak dominance
> are confirmed. **Using the file's per-compressor values.**

## A3 probe (cliff shape)

Source: `results/a3_probe/verdict.json` (`<fam>.logistic`).

| Field | Value | Key |
|---|---|---|
| Dense (a): k_slope | **15.107** | `a.logistic.k` |
| Dense (a): r0_midpoint | **0.8420** | `a.logistic.r0` |
| Dense (a): interpretation | THRESHOLD-LIKE | `a.interpretation` |
| Distributed (c): k_slope | **5.864** | `c.logistic.k` |
| Distributed (c): r0 | 0.5377; interpretation GRADED | `c.logistic.r0`, `c.interpretation` |

(File contains families a and c only — no family-b. Brief's "dense k~15 r0~0.84,
distributed k~5.9" matches a and c.)

## Memory-bus microbenchmark

Sources: `results/bus_bench/bench.json` (macOS arm64 / M-series, py3.11),
`results/bus_bench/bench_gpu.json` (Linux WSL2 x86_64, py3.12). n=5000,
warmup=500.

| Field | bench.json (M) | bench_gpu.json (WSL2) | Key |
|---|---|---|---|
| Write throughput | **18189.6 ops/s** | 5752.9 ops/s | `write_end_to_end.throughput_ops_s` |
| Read throughput | 19857.9 ops/s | 6394.9 ops/s | `read_end_to_end.throughput_ops_s` |
| Policy-enforce throughput | 5.19e6 ops/s | 6.72e6 ops/s | `policy_enforce.throughput_ops_s` |
| Audit verify per-row | **1.678 µs** | **2.19 µs** | `audit_verify.verify_per_row_us` |

> **Discrepancy:** brief said "write ~16–18k ops/s" — the **bench.json** write
> figure 18189.6 matches; the **GPU** write is much lower (5752.9 ops/s, WSL2
> SQLite). Brief's "verify ~1.6–2.2 µs/row" matches the **audit-chain
> verify_per_row_us** (1.678 / 2.19), not a write-row latency.

## Fine-grid cliff (deterministic)

Source: `results/h1_h2_finegrid/verdicts.json`.

| Field | Value | Key |
|---|---|---|
| Family-a τ* (model_selected) | **2.5** (logistic) for filter/lingua2/truncation | `h2.cells[*].tau` where family=a |
| Family-a piecewise τ | 13.42 (filter) / 7.32 (lingua2) / 13.62 (truncation) | `h2.cells[*].piecewise_tau` |
| Significant cells | 8 / 9 | `h2.n_significant_cliffs=8`, `h2.total_cells=9` |

> **Resolved (2026-06-04, recomputed on GPU).** The manuscript's "deterministic
> family-a cliff ~1.1" is the **0.5×p0-crossing of the deterministic-solver
> coordination curve on the fine grid**, NOT the logistic τ*. Computed from
> `h1_h2_finegrid/sweep_results.csv`: lingua2 crosses at **1.12** (curve
> 1.0→0.0 between r=1 and r=1.25), filter at **1.73**, truncation at **1.84** —
> matching the manuscript's "≈1.1 / ≈1.7 / ≈1.85". The logistic fit reported in
> `verdicts.json` (τ*=2.5, piecewise ≈13.4) is a *different statistic* on the
> same curve, biased upward by the coarse low-end spacing; the manuscript
> deliberately quotes the 0.5-crossing to argue the true solver cliff sits well
> below the logistic 2.5. Both are correct; the earlier "not on disk" note only
> checked `verdicts.json` and missed the CSV-derived crossing.
