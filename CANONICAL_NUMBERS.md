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

> **Discrepancy:** the brief quoted "filter -0.82, phi3 +0.32, lingua2 +0.03,
> truncation +0.05". None of those match `h1_h2_v2/verdicts.json` (the canonical
> file) nor `h1_h2_finegrid/verdicts.json` (filter -0.100, lingua2 +0.311,
> truncation +0.551; phi3 absent). The brief's values were not found in any
> on-disk H1 verdict file. **Using the canonical v2 file values above.**

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
> - Brief said "n=30 re-run tau~2.79 0.5-crossing"; the `frontier_qwen72b_e2`
>   file reports `frontier_tau=7.235` (CI does not contain synth). No 2.79 value
>   appears in that file. **Using the file value 7.235** and flagging that the
>   e2 re-run did NOT validate (synth reference there is 12.153).
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

> **Discrepancy:** brief said P1−P2 "3.2pp/2.0pp" (matches: 3.24/2.02) but quoted
> per-pipeline EUR means of "P1 3.0e-5 / P2 2.9e-5 / P3 3.1e-5". The on-disk
> column is `eur_per_query` (not `eur_cost`, which does not exist) and its means
> are **~1.7e-4**, an order of magnitude larger. **Using the file values.**

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

> **Discrepancy:** brief said "deterministic family-a cliff ~1.1". No τ value of
> ~1.1 appears in `h1_h2_finegrid/verdicts.json`; the family-a logistic τ* is
> **2.5** (piecewise τ ≈ 13.4). **Using the file value 2.5.** If the brief's 1.1
> refers to a different artifact (e.g. a deterministic-solver sweep CSV not
> surfaced in this verdicts JSON), it could not be located on disk.
