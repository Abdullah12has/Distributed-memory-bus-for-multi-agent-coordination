# Data Cards

**Provenance.** Every count, seed, and θ_info value in this file was read directly
off the on-disk artifacts of *Memory Bus for Multi-Fragment LLM Workflows* on
2026-06-01, against files produced on each run's completion date. C1 instance
counts were obtained by counting non-empty lines of
`data/processed/c1-v0.1/family-{a,b,c}.jsonl` (50 each, 150 total) and
cross-checked against `data/processed/c1-v0.1/manifest.json`; the C1 master seed
is `20260514` (same for all three families) per that manifest. MultiHopRAG and
HotpotQA usage counts were obtained by counting data rows of
`results/h6_final/results.csv` (1500) and `results/hotpotqa_sweep/results.csv`
(750); θ_info values from `results/corollary2_theta_info.json`. This repo does
**not** use Git LFS — all data and result files are plain on-disk files (no
`.gitattributes`, `git lfs` not installed). **No value in this file is a
placeholder.**

---

## C1 benchmark (`c1-v0.1`)

| Field | Value |
|-------|-------|
| Name | C1 synthetic coordination benchmark, version `c1-v0.1` |
| Location | `data/processed/c1-v0.1/` (`family-a.jsonl`, `family-b.jsonl`, `family-c.jsonl`, `manifest.json`) |
| Source | Synthetic, generated in-repo for this thesis |
| License | In-repo synthetic (repo license applies) |
| Total instances | 150 (verified: 50 + 50 + 50 from the three `.jsonl` files) |
| Master seed | `20260514` (all three families; `manifest.json`) |
| Family a | `cross_document_fact_aggregation`, 50 instances, seed 20260514 — dense numeric, high info density (θ_info 0.967) |
| Family b | `constraint_satisfaction_planning`, 50 instances, seed 20260514 — bin-packing / constraint tracking |
| Family c | `multi_step_retrieval`, 50 instances, seed 20260514 — multi-step retrieval (FINAL-token tracking) |
| ACL / tag distribution | Synthetic access-control labels and tags carried on each fragment (used by the policy-aware / H4 protected-fact path) |
| Consumed by | H1, H2, H3, H4, H5, CAAC, A3 probe, fine-grid, frontier (families a/c) |

File sizes on disk: `family-a.jsonl` 323,279 B; `family-b.jsonl` 137,233 B;
`family-c.jsonl` 120,539 B; `manifest.json` 399 B.

---

## MultiHopRAG (H6 / Corollary 2)

| Field | Value |
|-------|-------|
| Name | MultiHopRAG |
| Source / citation | Tang & Yang, *MultiHop-RAG: Benchmarking Retrieval-Augmented Generation for Multi-Hop Queries*, Findings of EMNLP 2024 |
| License | (verify license — MultiHopRAG repo; not confirmed on this host) |
| Role | External transfer benchmark (distributed QA, low info density) |
| θ_info | 0.484 (`results/corollary2_theta_info.json`, key `MultiHopRAG.theta_info`; baseline 0.347, τ 3.0) |
| Rows used | 1500 data rows in `results/h6_final/results.csv` (counted) |
| Consumed by | H6 (original NOT SUPPORTED) → Corollary 2 (SUPPORTED) |

---

## HotpotQA (Corollary 2)

| Field | Value |
|-------|-------|
| Name | HotpotQA |
| Source / citation | Yang et al., *HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering*, EMNLP 2018 |
| License | CC BY-SA 4.0 |
| Role | Second external benchmark for Corollary 2 (most distributed) |
| θ_info | 0.373 (`results/corollary2_theta_info.json`, key `HotpotQA.theta_info`; baseline 0.593, τ NaN) |
| Rows used | 750 data rows in `results/hotpotqa_sweep/results.csv` (counted) |
| Consumed by | Corollary 2 (Information Density Scaling) |

---

## θ_info ordering (Corollary 2 headline)

C1-a 0.967 > MultiHopRAG 0.484 > HotpotQA 0.373 — dense tasks cliff early,
distributed tasks degrade gradually. Ground truth: `results/corollary2_theta_info.json`.
θ_info (AUC-based, per-task) ≠ θ_q (recall-threshold, per-family); see CONTEXT.md.
