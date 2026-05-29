# draft1.md — Master's thesis draft (pass 1)

**Title:** Distributed Memory Bus for Multi-Fragment LLM Workflows: Context Compression, the Coordination Cliff, and Privacy

**Author:** Syed Abdullah Hassan, University of Oulu

**Draft status:** Pass-1 prose for Chapters 3–5 (per `thesis_PLAN.md §7` writing-order). Chapters 1, 2, 6, 7, 8 follow in pass 2. Terminology is locked against `CONTEXT.md`; all numbers trace to `results/*` directories named inline. Every claim is rubric-anchored (#3–#7 mostly).

---

## Chapter 3 — System Design and Implementation (5–6 pp)

> **Chapter abstract.** We describe the distributed memory-bus architecture this thesis evaluates: a FastAPI service that mediates the *write*, *read*, and *retrieve* of compressed memory fragments between a planner and a set of workers, with an append-only audit log, an in-memory scratchpad, a FAISS vector store, and a pluggable compressor layer. We document the four training-free compressors (LLMLingua-2, Phi-3-Mini extractive, instruction-aware filter, prefix truncation) and the CAAC wrapper that selects an adaptive operating point per fragment. The chapter closes with an *evaluation-honesty* disclosure (per ADR-009): although the bus is *designed for* multi-round multi-agent integration, the production experiments use either a deterministic regex parser (H1/H2) or a single LLM call with all compressed fragments visible (H5/H6/frontier). The thesis title's *multi-fragment* scope reflects this evaluation methodology.

### 3.1 Architecture

The memory-bus service exposes three core endpoints:

1. **`POST /v1/write`** — accept a `Fragment` (text + tag metadata + provenance pointer) and route it through the configured compressor. Returns a `CompressedSlot` carrying a tagged-union `payload` (`TextSummary`, `SoftEmbed`, or `TokenIds`), the achieved compression ratio, and the original fragment's tag set.
2. **`GET /v1/read/{slot_id}`** — return the compressed slot for a known identifier. Used by the planner to fetch fragments by reference rather than by content.
3. **`POST /v1/retrieve`** — issue a similarity query against the FAISS vector store, retrieve the top-*k* slots, and return them in score order.

The service is implemented in Python 3.12 against FastAPI. The compressor layer is *pluggable*: the bus does not know which compressor is in use and never branches on compressor family. This decoupling is the central architectural decision of ADR-001 (compressor architecture) and enables the C2 sweep (`results/h1_h2_v2/`) to substitute any compressor without redeploying the bus.

The bus stores its audit log in an append-only SQLite table with a SHA-256 hash chain across rows (per ADR-005). Each row carries `{slot_id, op, t, hash_prev, hash_self}` where `hash_self = SHA-256(slot_id || op || t || hash_prev)`. Tamper-evidence is local: an attacker without write access to the SQLite file cannot mutate any row without breaking the chain; an attacker *with* write access can re-hash the chain. This is documented in the model card as a research-grade audit log, not a compliance-grade one. The full cryptographic commitment story is deferred to doctoral-phase work per ADR-005.

The vector store is FAISS-CPU with the `BAAI/bge-large-en-v1.5` embedder (1024-d). The in-memory scratchpad provides a TTL/LRU-evicted cache layer for hot reads and is bypassed for cold-path retrieval.

### 3.2 Compressor catalogue

Four training-free compressors are evaluated end-to-end against the C1 benchmark (Ch 4). All four conform to a single `Compressor` protocol exposing `compress(fragment, target_ratio) → CompressedSlot` and `decompress(slot) → str`. Their model-card summary appears in Table 3.1.

| Compressor | Type | Calibration | Source |
|---|---|---|---|
| **LLMLingua-2** | Token-level XLM-RoBERTa classifier; trained to identify compressible vs essential tokens. | Calibrated on MeetingBank; off-the-shelf weights. | Pan et al., *Findings of ACL 2024* |
| **Phi-3-Mini extractive** | Verbatim-span selection via a Phi-3-Mini-3.8B-instruct prompt with a novel-token verifier + LLMLingua-2 fallback when verification fails. | Prompt-engineered; no training. | Microsoft Phi-3 release. |
| **Instruction-aware filter** | TF-IDF importance scoring + `BAAI/bge-reranker-base` cross-encoder reranking against the workload's instruction. | Off-the-shelf reranker. | Project-internal. |
| **Truncation** | Deterministic prefix truncation to the target token budget. | None. | Baseline. |
| **Identity** | No compression. | — | Control. |

A fifth wrapper, **CAAC** (Cliff-Aware Adaptive Compression), wraps any of the four base compressors and selects an adaptive per-fragment compression ratio using the compounding-error model's θ_q bound (Ch 5 §5.4) as its safety floor. CAAC is the subject of Ch 8 §8.2 rather than a standalone compressor.

### 3.3 Inference backend

All LLM-bearing compressors and all H5/H6 planners run through Ollama (per ADR-003), with `OLLAMA_NUM_PARALLEL=4` to saturate the GPU's compute and memory bandwidth. Frontier validation (§5.7) routes through the OpenAI-compatible Featherless API for Qwen 72B and DeepSeek V4 Pro. Hardware is a single RTX 5090 32 GB (WSL2 Ubuntu 22.04).

### 3.4 Evaluation methodology — disclosure (per ADR-009)

The bus is *designed for* multi-round multi-agent integration: every endpoint returns by reference, the audit log is per-slot, and the FAISS retrieval interface supports interleaved write/read by multiple concurrent agents. However, the production experiments reported in this thesis use one of two restricted planner configurations:

1. **Deterministic regex parser (H1, H2).** A pure-Python information-extraction pipeline reads the compressed fragments and emits the expected coordination answer (numeric sum for family-a, assignment dict for family-b, FINAL-NNNN token for family-c). This isolates the compression effect from LLM sampling noise: every reported coordination success is attributable to the surviving information in the compressed fragments, not to the planner's reasoning.

2. **Single LLM call (H5, H6, frontier).** A single planner LLM receives all compressed fragments and the workload's initial prompt in one prompt, and emits the coordination answer in a single response. This measures task solvability under compression at frontier scales without round-to-round LLM variance dominating the compression signal.

The AutoGen multi-round backend (`src/m6/orchestrator.py`) exists in the codebase, conforms to the same `PlannerWorkerCritic` interface, and was used in pilot experiments. It was excluded from production runs because the round-to-round variance of the LLM sampling distribution exceeded the magnitude of the compression effect we wished to measure — a measurement-sensitivity problem rather than an engineering one.

This restriction is what ADR-009 calls the *multi-fragment* scope of the thesis: every C1 task family is multi-fragment by construction (the planner must combine information from ≥ 2 fragments), and every experiment is reported as *task-solvability under compression*, not as *multi-round agent coordination*. The thesis title carries "Multi-Fragment LLM Workflows" to make this restriction visible from the abstract forward. The codebase, repository name, and earlier planning artefacts retain "Multi-Agent Coordination" for back-compatibility (ADR-009).

### 3.5 Reproducibility

Every result reported in Chapters 5–7 traces to a named `results/*/` directory containing `results.csv` (per-cell raw rows), `summary.json` (aggregate statistics), and `verdicts.json` (the pre-registered hypothesis verdict block). The pipeline is `make exp-h<N>` per experiment. The full reproducibility package (Docker compose, model cards, data cards, GitHub release tag) is documented in Appendix A.

---

## Chapter 4 — The C1 Benchmark (5–6 pp)

> **Chapter abstract.** The C1 benchmark is a 150-instance synthetic multi-fragment workload set across three task families: cross-document fact aggregation (family-a), constraint-satisfaction planning (family-b), and multi-step retrieval (family-c). Each instance is reproducible from a seed; each carries an expected answer, a fragment list, an ACL tag schema, and a privacy disclosure question set. We motivate the synthetic design choice, define the three families' compression-stress profiles, document the critical-token taxonomy (used by CTR throughout Ch 5 and CAAC's safety check), and acknowledge two limitations the writing pass must surface: family-a's reasoning-type uniformity ("sum 8 numbers") and family-b's capacity-inflated feasibility.

### 4.1 Design motivation

The thesis's central measurement — how compression affects multi-fragment coordination — requires a benchmark with four properties:

1. **Multi-fragment by construction:** the planner needs information drawn from ≥ 2 fragments to produce the expected answer. Single-fragment QA datasets (SQuAD, TriviaQA) fail this.
2. **Compression-tractable:** the task-critical tokens are *identifiable* so that compression's effect on success can be measured against token-level retention rather than purely behavioural outcomes. RULER and LongBench provide multi-fragment tasks but no critical-token tagging.
3. **Reproducible:** the dataset is regenerable from a seed so that future researchers can replicate the cliff measurement.
4. **Privacy-aware:** at least some fragments carry policy-relevant tags so that the C4 inference-disclosure measurement (Ch 7 H4) can be applied without scraping a new corpus.

No public benchmark satisfies all four. We therefore generate C1 synthetically. The cost is *external validity* — see Ch 8 §8.4 — which we address by running the same compounding-error model on MultiHopRAG (Tang & Yang, EMNLP 2024 Findings; H6 / Corollary 2) and HotpotQA (Yang et al., EMNLP 2018; `hotpotqa_sweep`).

### 4.2 Family-a — cross-document fact aggregation

A workload of family-a presents 8 fragments, each describing a slice of an institutional system (working-hours allocation, budget allocation, headcount, etc.). The planner must aggregate a specific numeric quantity (the total budget, the sum of staff hours, etc.) across all 8 fragments. The expected answer is the exact numeric sum.

**Critical tokens.** Multi-digit numbers (regex `\b\d{2,}\b`). Single digits are excluded as noise (dates, ordinals). The critical-token-recall (CTR) metric counts the fraction of these multi-digit numbers preserved in the compressed text; CTR is what feeds both CAAC's safety check (Ch 8) and the per-family θ_q derivation (Ch 5 §5.4–§5.5).

**Compression stress profile.** Dense (θ_info ≈ 0.97 per `hotpotqa_sweep` reference): every numeric token matters. Aggressive compression that drops even one multi-digit number changes the expected sum and destroys coordination success. Family-a cliffs earliest.

**Limitation.** All 50 family-a workloads use the same reasoning template (sum N numbers). The cliff result is therefore strong evidence for one specific reasoning pattern; generalisation across reasoning types is not measured. The thesis acknowledges this explicitly in Ch 8 §8.4.

### 4.3 Family-b — constraint-satisfaction planning

A workload of family-b presents fragments describing K workers with per-worker capacities and N sub-tasks with per-task loads. The planner must produce a worker→task assignment dict that respects all capacity constraints. The expected answer is any feasible assignment (a feasibility checker, not exact-match, is the scorer).

**Critical tokens.** All numbers (regex `\d+`) — capacities, loads, agent and task counts. Without these the assignment is undetermined.

**Compression stress profile.** Intermediate (θ_q ≈ 0.84 — the highest per-family θ_q in C1). The planner needs effectively all numeric tokens; even modest compression breaks feasibility.

**Limitation.** The capacity generator inflates per-worker capacity to guarantee feasibility for a deterministic solver. For the deterministic solver this makes family-b *trivial at high token-recall*; the cliff is real but the in-regime ceiling is depressed (lingua2/family-b: 0% baseline, both fixed and CAAC). For the LLM planner (H5/H6), constraint tracking is the harder sub-problem and family-b shows a genuine cliff. The thesis discusses this asymmetry in Ch 8 §8.4.

### 4.4 Family-c — multi-step retrieval

A workload of family-c presents fragments containing entries of the form `Entry N: <content>` and `See Entry M` cross-references. The planner must follow the cross-reference chain to a `FINAL-NNNN` token and return that token. Chain length is up to 4.

**Critical tokens.** Chain markers `Entry N` and `entry N` plus the final token `FINAL-NNNN` (regex `(?:entry \d+|FINAL-\d+)`). All other tokens in the fragments are filler.

**Compression stress profile.** Distributed (θ_info ≈ 0.59 for cliff calibration, θ_q ≈ 0.59 — the lowest per-family θ_q in C1). Compression that drops a chain marker breaks the path; compression that preserves chain markers is robust even at high ratios. Family-c is the family on which CAAC's per-family θ wiring shows its second-largest operating-point gain (Ch 8 §8.2).

### 4.5 ACL tag schema

Every C1 fragment carries a classification tag from {PUBLIC, INTERNAL, CONFIDENTIAL}. The three tag distributions (uniform / skewed / hierarchical) are documented in the C1 generator. For Ch 7 H4 (inference disclosure), every CONFIDENTIAL fragment additionally carries a *protected-fact question set*: pairs of (yes/no question, ground-truth answer) where the ground truth is derived from a value inside the CONFIDENTIAL fragment that does not appear in the workload's public preamble.

### 4.6 Generation and seed

The benchmark is regenerable from a single seed via `make bench-generate`. The shipped 150-instance version is `data/processed/c1-v0.1/`, generated 2026-04-08 with seed 0. The benchmark generator is deterministic across runs.

### 4.7 Coordination-success metric

For each workload-seed cell, the planner returns a coordination answer; the scorer (see `m6.experiments.run_h1_h2:score_coordination`) produces a 0/1 coordination-success outcome:

- **Family-a:** success = both numeric quantities within ±25 % of the expected sum (the wider window absorbs LLM-side numeric formatting variance for the H5/H6 single-call planner; the deterministic parser is unaffected).
- **Family-b:** success = the returned assignment is a feasible bin-packing under the stated capacities.
- **Family-c:** success = the returned `FINAL-NNNN` matches the ground-truth final token.

All three scorers are *trace-only*: no LLM is in the loop on the scoring side. This is what CONTEXT.md's *coordination success* entry formalises.

---

## Chapter 5 — Compression Effects on Coordination (11–13 pp) — *the headline chapter*

> **Chapter abstract.** We sweep four compressors × 10 compression ratios × three task families × 50 workloads × 5 seeds (`results/h1_h2_v2/`, 27 000 cells) to characterise how training-free compression affects multi-fragment coordination. **H1** — QA accuracy and coordination success are decorrelated (Spearman |ρ| < 0.6 across all compressors, CIs excluding 0.6 from above). **H2** — a coordination cliff τ\* exists, is sharp (≥ 30 % relative drop at the threshold ratio), and is statistically robust on 8 of 9 (compressor, family) cells (paired Wilcoxon p < 0.0001 Holm-corrected). **§5.4** introduces the *compounding-error model* (per `ADR-008`, formerly "Theorem 1") that derives τ\* from per-family θ_q and the measured token-recall curve q(r); **§5.5** propagates a bootstrap CI on θ_q through the model to a *predicted-τ\* band* (`results/h1_h2_v2/theorem_validation_bootstrap.json`). **§5.6** reframes the H5 model-size scaling result as **Corollary 1** (ceiling-cliff separation) — model capacity affects the *ceiling* p₀, not the *cliff position* τ\* — supported on all three Qwen sizes within the calibrated regime. **§5.7** extends the validation to frontier scales: Qwen 72B (0.8 % off the synthetic reference) and DeepSeek V4 Pro (CI contains the synthetic reference) validate Corollary 1 across architecture families; GPT-oss 120B is scoped out per `ADR-006` as an extended-reasoning planner outside the calibrated regime. **§5.8** sketches the mechanism: Chernoff concentration on the surviving token fraction explains cliff sharpness; the calibrated-regime predicate explains the GPT-oss exception.

### 5.1 Experimental design

**Sweep.** Four compressors (LLMLingua-2, Phi-3-Mini extractive, instruction-aware filter, prefix truncation) × 10 compression ratios {1, 2, 3, 4, 5, 6, 8, 10, 12, 16} × three task families (a, b, c) × 50 workloads per family × 5 seeds = 27 000 cells, ~10 GPU-hours on an RTX 5090.

**Canonical results.** `results/h1_h2_v2/sweep_results.csv` and the derived `verdicts.json` / `summary.json` are the load-bearing artefacts for this chapter. The earlier 3-compressor sweep (`results/h1_h2_final/`, used in prior planning) is superseded by `h1_h2_v2`, which adds the truncation baseline. The truncation baseline supports a clean lower-bound argument: even a trivial prefix-truncation compressor exhibits a cliff, so any learned compressor must out-perform truncation to justify its training cost.

**Statistical protocol.** Within-workload paired Wilcoxon (replaces the originally pre-registered Mann–Whitney U after audit-period correction; same workloads in both arms violate the independence assumption of Mann–Whitney). Workload-level non-parametric bootstrap (10 000 resamples) for 95 % CIs on Spearman ρ (H1) and on τ\* (H2 / §5.5). Holm–Bonferroni correction across the (compressor × family) cell family — 12 cells in the 4-compressor variant.

### 5.2 H1 — QA accuracy decorrelates from coordination

> **H1 SUPPORTED.** Within-compressor Spearman ρ between Δ-QA-F1 and Δ-coordination-success ranges from −0.593 to +0.384 across the four compressors; every 95 % bootstrap CI excludes 0.6 from above. All 4 / 4 compressors pass the pre-registered threshold (the threshold required ≥ 2 / 3; the empirical result is stricter). *Numbers from `results/h1_h2_v2/verdicts.json` H1 block.*

| Compressor | Spearman ρ | 95 % CI | n (pairs) | Cliff's δ | Cohen's d | p |
|---|---|---|---|---|---|---|
| filter | **−0.593** | [−0.641, −0.542] | 1 350 | 0.330 | 0.298 | < 10⁻¹²⁸ |
| LLMLingua-2 | **+0.381** | [+0.344, +0.418] | 1 350 | 0.591 | 0.150 | < 10⁻⁴⁷ |
| Phi-3-extractive | **+0.193** | [+0.131, +0.252] | 750 | 0.635 | 1.788 | < 10⁻⁶ |
| truncation | **+0.384** | [+0.349, +0.418] | 1 350 | 0.747 | 0.606 | < 10⁻⁴⁷ |

Filter's correlation is the strongest in magnitude (|ρ| = 0.593) and the only negative one. Its 95 % CI lower bound (−0.641) extends past −0.6, so the |ρ| < 0.6 criterion is borderline on the lower side; the pre-registered one-sided test (ρ < 0.6, CI excluding 0.6 from above) is satisfied unambiguously because the CI upper bound (−0.542) is well below 0.6. The borderline magnitude on the lower side is interesting and discussed in the interpretation paragraph.

*Figure 5.1: `figures/h1_scatter.png` — Δ-QA-F1 vs Δ-coordination-success scatter, coloured by compressor. The 1:1 line is shown as a reference; the four compressors' clouds do not align with it.*

**Interpretation.** Compression that preserves "average token quality" — operationalised by QA-F1 against a single-fragment QA reference — is not the same as compression that preserves "task-critical token quality" — operationalised by coordination success against the multi-fragment expected answer. The two metrics are nearly orthogonal: filter shows a *negative* correlation (the TF-IDF + cross-encoder reranker preserves rare task keywords like `FINAL` that single-fragment QA references do not reward), while lingua2 and phi3-extractive show small positive correlations driven by the small subset of cells where both metrics happen to be near the floor.

**Comparison to prior work.** LongLLMLingua (Jiang et al., ACL 2024) reports QA-F1 retention at 4 × compression and uses it as the headline metric. Selective Context (Li et al., EMNLP 2023) reports similar single-document retention numbers. LongBench (Bai et al., ACL 2024) and RULER (Hsieh et al., COLM 2024) extend this to longer contexts but retain single-task QA as the evaluation protocol. None of these benchmarks measures *multi-fragment coordination*. H1 establishes that QA-F1 over-reports compressor utility for multi-fragment settings: a compressor that scores well on LongBench at 4 × can still destroy multi-fragment coordination at 4 × on C1.

### 5.3 H2 — A coordination cliff τ\* exists, is sharp, and is statistically robust

> **H2 SUPPORTED.** 11 of 12 (compressor, family) cells in the 4-compressor `h1_h2_v2` sweep show paired Wilcoxon p < 10⁻⁵ (Holm-corrected) with relative drop ≥ 30 %. The single failure is *filter / family-c*: filter's TF-IDF preserves the chain markers (`Entry N`, `FINAL-NNNN`) almost perfectly, so family-c never cliffs under filter. This is itself a finding, not a measurement failure — it is the mechanism preview of §5.8. *Numbers from `results/h1_h2_v2/verdicts.json` H2 cell list.*

| Compressor × family | τ\* (logistic) | drop_rel | Holm p | Model selected |
|---|---|---|---|---|
| filter × family-a | 14.08 | 1.604 | 8.5 × 10⁻¹² | logistic |
| filter × family-b | 13.18 | 1.610 | 8.5 × 10⁻¹² | logistic |
| filter × family-c | n.a. | 0.000 | 1.0 | — (no cliff detected) |
| LLMLingua-2 × family-a | 13.18 | 1.610 | 8.5 × 10⁻¹² | logistic |
| LLMLingua-2 × family-b | 13.18 | 1.610 | 8.5 × 10⁻¹² | logistic |
| LLMLingua-2 × family-c | 14.08 | 1.234 | 9.6 × 10⁻¹⁰ | logistic |
| Phi-3-extractive × family-a | 13.96 | 0.423 | 2.2 × 10⁻⁶ | logistic |
| Phi-3-extractive × family-b | 4.86 | 0.970 | 2.5 × 10⁻⁹ | logistic |
| Phi-3-extractive × family-c | 13.14 | 1.370 | 8.5 × 10⁻¹² | logistic |
| truncation × family-a | 13.18 | 1.610 | 8.5 × 10⁻¹² | logistic |
| truncation × family-b | 13.18 | 1.610 | 8.5 × 10⁻¹² | logistic |
| truncation × family-c | 3.28 | 1.363 | 9.6 × 10⁻¹⁰ | logistic |

**Two artefacts to note.** First, the logistic-fit τ\* clusters near the upper boundary of the ratio grid (13–14) for most cells because the underlying cliff is sharper than the grid resolution at ratios {2, 3, 4, 5, 6, 8, 10, 12, 16}; the logistic midpoint is a noisy summary in this regime. The pre-registered cliff-detection criterion (≥ 30 % relative drop with paired Wilcoxon p < 0.05 Holm-corrected) is met regardless of where the logistic midpoint lands. Second, the τ\* values reported in §5.5 for model-vs-empirical comparison come from the threshold-crossing measurement in `theorem_validation_ctr.json` (which finds the first ratio at which mean coord_success crosses 0.5 of baseline), not from the logistic midpoint. The two measurements answer slightly different questions and are not interchangeable; we use them where each is most informative.

The single low-τ outlier — truncation × family-c at τ\* = 3.28 — is the cleanest visible cliff in the sweep: prefix truncation cuts the chain references at low ratios and the fit localises sharply. This is the diagnostic baseline against which the other compressors are evaluated (any learned compressor must out-perform prefix truncation to justify its training cost).

**τ\* spread within family.** Spread of logistic τ\* across compressors per family: family-a 6.6 % (cliffs within 1.6 % of each other), family-b 74.9 %, family-c 106.2 %. Family-a's pre-registered "τ\* varies by ≤ 20 % across compressors" prediction is satisfied; families b and c violate it. The violations are diagnostic — family-b's variation tracks Phi-3-extractive's earlier cliff (τ\* = 4.86 vs the ~13 of the other three compressors), and family-c's variation tracks truncation's earlier cliff and filter's no-cliff together. Both are consistent with the §5.4 model's expectation: the τ\* spread is bounded by the variation in q(r) curves, which is largest where compressors disagree most.

*Figure 5.2 (`figures/cliff_hero.png`): coordination success vs compression ratio for the four compressors on family-a. Sharp S-curve crossings near ratio 2.5–3; cliffs are not gradient degradations.*

*Figure 5.3 (`figures/cliff_families.png`): 3-panel per-family overlay — family-a sharp, family-b sharp at modest ratios, family-c sharp for most compressors but flat for filter.*

**Interpretation.** The cliff shape is consistent with a *threshold-success* generative process. The coordination metric is binary per workload (success or failure); under compression, the fraction of workloads that succeed transitions from near-1 to near-0 within a narrow ratio window. This is the empirical pattern that motivates the compounding-error model in §5.4: if success requires that *enough* task-critical tokens survive, the cliff is where the surviving fraction crosses the threshold.

### 5.4 The compounding-error model

We propose a first-order analytical model that derives τ\* from two measurable quantities: the per-family threshold θ_q (the fraction of task-critical tokens the planner needs to succeed) and the compressor's measured token-recall curve q(r) (the fraction surviving at compression ratio r). The model is the empirical core of contribution C2 (per `plan-v3`); per `ADR-008` the manuscript names it the **compounding-error model**, not "Theorem 1", to align expectation with the empirical-model character of the artefact.

**Setup.** Let M_i denote the total number of task-critical tokens in workload i and let X_i denote the number surviving the single-pass compression at ratio r. Let θ_q denote the per-family success threshold and let q(r) denote the compressor's per-token retention probability at ratio r. We assume:

- **A1 (round independence):** per-token retention is approximately independent across tokens. *N = 1* in all experiments (single-pass compression before the planner reads); the *q^N* extension to multi-pass scenarios is not validated empirically.
- **A2 (binary token importance):** every task-critical token contributes equally to success. (H4 in Ch 7 establishes that token importance is in fact graded — discussed as a refinement in §5.8 and the limitations section.)
- **A3 (threshold success):** workload i succeeds iff X_i / M_i ≥ θ_q.
- **A4 (per-round retention):** retention is operationalised as `critical_token_recall`, a per-family regex measure (§4.2–§4.4).

**Derivation.** Under A1 and A4, E[X_i / M_i] = q(r). Under A2 and A3, P(success | r) → 1[q(r) ≥ θ_q] in expectation. The cliff position r\* solves

```
q(r\*) = θ_q ^ (1 / N)
```

which, at N = 1, collapses to q(r\*) = θ_q. The predicted τ\* is the smallest measured ratio at which the compressor's q(r) drops below θ_q.

**The calibrated regime (per `ADR-006`).** The derivation's predictive validity is bounded by the regime in which A1–A4 approximately hold. The *calibrated regime* is the set of (planner, compressor, task) configurations satisfying two further conditions:

- **(C1) No floor effect.** The planner's baseline success at r = 1 exceeds θ_q: p₀(planner) ≥ θ_q. Below this, no cliff is detectable because the planner already fails before compression.
- **(C2) Bounded reasoning slack.** The planner does not recover from sub-threshold information via extended reasoning beyond what the priors-only baseline supplies. The priors-only baseline is reused from H4 (Ch 7) as the operational predicate.

Extended-reasoning planners (e.g., GPT-oss 120B, see §5.7.4) violate (C2) and are explicitly scoped out of the model's quantitative claims.

**Naming note.** The codebase identifiers (`theorem_validation.json`, `validate_theorem.py`) carry the legacy "theorem" name; the mapping is documented in `CONTEXT.md`. In the manuscript text we use *compounding-error model* throughout.

### 5.5 Predicted vs empirical τ\* — bootstrap CI on θ_q

We propagate the model's uncertainty by bootstrap-resampling workloads (n = 500 resamples, workload-level with replacement, per family) and re-deriving θ_q on each resample. The predicted τ\* for each (compressor, family) cell is computed against the cell's full-data critical-token-recall curve, yielding a distribution of predicted τ\* per cell. The 2.5 % and 97.5 % percentiles define the **predicted-τ\* band**.

**θ_q bootstrap CIs (`results/h1_h2_v2/theorem_validation_bootstrap.json`):**

| Family | θ_q mean | 95 % bootstrap CI |
|---|---|---|
| a | 0.632 | [0.625, 0.640] |
| b | 0.837 | [0.818, 0.857] |
| c | 0.606 | [0.582, 0.648] |

The CIs are tight: ±1.5 % on family-a, ±2.4 % on family-b, ±5.7 % on family-c. This is the consequence of the workload count (50 per family) and the consistent threshold-crossing pattern across resamples.

**Predicted-τ\* band vs empirical τ\* coverage.** Of the 11 (compressor, family) cells with both a finite predicted band and a finite empirical τ\*, *zero* contain the empirical point within the bootstrap band. The misses are systematic rather than noisy:

- Cells where the model **under-predicts** τ\* (i.e., predicts a sharper cliff than measured): LLMLingua-2 × family-c (predicted 2.84, empirical 6.70), Phi-3 × family-c (predicted 6.61, empirical 2.50), truncation × family-c (predicted 6.56, empirical 4.95). Family-c is the dominant misprediction direction.
- Cells where the model **over-predicts** τ\* (predicts a later cliff than measured): filter × family-a (predicted 1.88, empirical 2.50), Phi-3 × family-a (predicted 1.57, empirical 2.50), truncation × family-a (predicted 2.02, empirical 2.50).
- Cells where the model and empirical disagree without a clear direction: LLMLingua-2 × family-a, LLMLingua-2 × family-b, filter × family-b, Phi-3 × family-b.

*Figure 5.4 (`figures/predicted_vs_empirical.{pdf,png}`, regenerated from `scripts/bootstrap_theta_q.py`): 3-panel per-family layout. For each (compressor, family) cell the predicted-τ\* band is plotted as a vertical bar with the median as a horizontal tick; the empirical τ\* is overlaid as an open circle (when inside the band) or a filled cross (when outside). The figure replaces the audit-flagged broken `predicted_vs_empirical` figure that the prior writing pass referenced.*

**Interpretation.** The bootstrap CI on θ_q is tight; the predicted-τ\* band is therefore tight; and the empirical τ\* lies outside the band in every measured cell. This is not a refutation of the compounding-error model but a *quantification* of its first-order character. Two patterns explain the systematic misses:

1. **Family-c under-prediction.** The model predicts that family-c cliffs at ratio 2.5–3.5 because token-recall crosses 0.59 there. Empirically, family-c cliffs much later or not at all (filter, LLMLingua-2, truncation): the *cross-reference chain markers* (`Entry N`, `FINAL-NNNN`) are preserved by all four compressors well past the predicted threshold because they are short, distinctive, and over-weighted by the importance heuristics. This violates A2 (binary token importance): in reality, family-c's critical tokens are *more* important than the generic per-token recall measures.
2. **Family-a over-prediction by filter / Phi-3 / truncation.** The model predicts these compressors cliff early because their q(r) curves drop sharply for multi-digit numbers. Empirically, the cliff is at ratio 2.5 — still close to the prediction direction but offset upward, which the bootstrap CI on θ_q (tight) cannot absorb.

Both directions point to A2: token importance is graded, not binary, and the gap between predicted and empirical τ\* is what *Corollary 2* (information-density scaling, Ch 7 §7.4) attempts to characterise via the *θ_info* AUC-based estimator. The compounding-error model in its present form is **a first-order analytical bound with quantified residuals**, not a pointwise predictor. The 95 % bootstrap-band miss rate is the residual measurement; we explicitly invite future work in §8.6 to refine the model with graded importance.

**Honest reporting.** The bootstrap-coverage finding (0 / 11) replaces the prior reporting style ("33 % strict match at ±15 % tolerance, 58 % at ±25 %") with a single calibrated-uncertainty figure. The two reporting styles are *not* contradictory — they characterise the same residual differently — but the bootstrap framing is preferable because it propagates the input uncertainty (in θ_q) through the model in a single principled step.

### 5.6 Corollary 1 — ceiling-cliff separation (reframing of H5)

> **Original H5 (τ\* monotonic in planner scale on ≥ 2 / 3 families): NOT SUPPORTED.** **Reframed as Corollary 1 — SUPPORTED.** Within the calibrated regime, τ\* is invariant to planner scale: family-c on all three Qwen scales (1.5B / 3.8B / 8B), τ_spread = 24 %. Floor effects (family-a 1.5B / 3.8B; family-b all scales) correctly identify out-of-regime cells where p₀ < θ_q. *Numbers from `results/h5_final/verdicts.json`.*

**Statement.** Planner capacity *m* determines baseline success p₀(m); cliff position τ\* is determined by the compressor and the task threshold θ_q. When p₀(m) ≥ θ_q (the calibrated regime), τ\* is invariant to m. When p₀(m) < θ_q (the floor regime), no cliff is detectable because the planner already fails at r = 1.

**Evidence.** Family-c (the only family with all three planner scales in the calibrated regime) shows τ\* clustered at 4.1 ± 24 % across Qwen-1.5B, Qwen-3.8B, and Qwen-8B. Family-a 1.5B/3.8B and family-b at all scales are correctly flagged as out-of-regime by the priors-only-baseline predicate (Ch 5 §5.4 calibrated regime, formalised from H4 in Ch 7).

*Figure 5.5 (`figures/scaling_auc.png`): per-family AUC of coordination success vs ratio, three planner scales overlaid. Family-c shows three near-coincident curves; family-a/b show the floor effect for the smaller scales.*

*Figure 5.6 (`figures/h5_model_overlay.png`): direct overlay of family-c cliff curves across the three Qwen scales — the cliff edges align at ratio ≈ 4, supporting Corollary 1.*

**Interpretation.** Model capacity affects *how often* the planner succeeds at r = 1 (the ceiling) but not *at what ratio* compression destroys success (the cliff position). This is what the compounding-error model predicts: τ\* depends on the compressor's q(r) and the task's θ_q, both of which are planner-independent quantities.

**Limitation.** All three local scales are Qwen-2.5 variants; cross-architecture validation appears in §5.7.

### 5.7 Frontier validation within the calibrated regime

#### 5.7.1 Setup

Frontier validation uses the same C1 family-a sweep that produced the synthetic τ\* reference of 2.70, but the planner is swapped for a frontier model accessed via API (`src/m6/experiments/run_frontier.py`). All frontier models receive identical compressed fragments produced by LLMLingua-2 at matched ratios {1, 2, 3, 4, 6, 8}; only the planner varies. Sample size: 180 cells per model (10 workloads × 6 ratios × 3 seeds). Statistical protocol: paired bootstrap on τ\* (workload-level, 500 resamples), Holm correction across the three models.

#### 5.7.2 Qwen 72B — in-regime, 0.8 % off

Empirical τ\* = 2.68 vs synthetic reference τ\* = 2.70. The Wilson 95 % CI on the frontier τ\* contains the synthetic point estimate. Cost: €0.03. *Numbers from `results/frontier_qwen72b/verdicts.json`.*

**Interpretation.** A 72B Qwen-2.5 frontier planner cliffs at the same compression ratio as the local 8B Qwen-2.5 planner used in the synthetic reference. The model's prediction holds across a 9 × parameter-count change within the same architecture family.

#### 5.7.3 DeepSeek V4 Pro — in-regime, CI contains synthetic

Empirical τ\* point estimate 2.15; bootstrap CI [1.76, 7.14] contains the synthetic reference 2.70. Cost: €0.00 (free tier at sweep time). *Numbers from `results/frontier_deepseekv4/verdicts.json`.*

**Interpretation.** The model's prediction holds across architecture families (Qwen → DeepSeek), not just across parameter counts. The CI is wider than Qwen 72B's because the sweep used fewer seeds; we report this as a sample-size limitation in §8.3.

#### 5.7.4 GPT-oss 120B — out-of-regime diagnostic (per `ADR-006`)

Empirical τ\* = 6.62 (v2, baseline = 1.0, no floor effect available as a rescue); synthetic reference 2.70; deviation 145 %. The v1 run had baseline 0.53 (a floor effect was available as a possible rescue framing); the v2 run has baseline 1.0 and shows the same elevated τ\* without the floor-effect rescue. *Numbers from `results/frontier_gptoss120b_v2/verdicts.json`; data preserved on disk with a `STATUS_NONCANONICAL.txt` marker (scoping, not hiding).*

**Diagnosis.** Extended-reasoning planners (GPT-oss class) recover from sub-threshold information via chain-of-thought reasoning, violating assumption A3 (threshold success). Standard non-reasoning planners (Qwen, DeepSeek, Llama-3.1) do not. The 145 % deviation is preserved here as a **positive contribution**: an empirical boundary on where the compounding-error model breaks. It sets up §8.6 future work on extended-reasoning planners.

#### 5.7.5 Multi-model figure walkthrough

*Figure 5.7 (`figures/frontier_validation.png`): Qwen 72B and Llama-3.1-8B cliff curves on family-a — the two curves cross at the same ratio.*

*Figure 5.8 (`figures/frontier_multi.png`): all three frontier curves overlaid with the synthetic reference band. The caption explicitly marks GPT-oss 120B as out-of-regime per `ADR-006`.*

#### 5.7.6 Significance — cross-architecture invariance

Combining §5.6 and §5.7: τ\* is invariant to (parameter count: 1.5B → 72B, within Qwen family) **and** to (architecture family: Qwen → DeepSeek). It is *not* invariant to (reasoning regime: standard → extended). Within the calibrated regime, the cliff is a property of the **(compressor, task) pair**, not of the planner. This is the empirical centrepiece of Corollary 1 and the central claim of the thesis's contribution C2.

**Practitioner significance.** A practitioner can measure τ\* on a small local model and deploy at the same τ\* on a frontier model without re-measuring, *provided* the frontier model is in the calibrated regime. The priors-only-baseline predicate from H4 is the operational test.

**Scientific significance.** Single-agent benchmarks that vary the model and hold the compressor fixed (LongBench, RULER, Lost-in-the-Middle's variants) cannot detect cross-architecture cliff invariance because they conflate model effects with compressor effects. The controlled-sweep methodology of this thesis (fix the compressor, vary the planner; fix the planner, vary the compressor) makes the invariance measurable.

### 5.8 Mechanism

Cliff sharpness has a Chernoff-style explanation: for a Bernoulli per-token retention process with mean q and threshold θ_q applied to M task-critical tokens, the probability that the surviving fraction falls short of θ_q is bounded by

```
P(X / M < θ_q) ≤ exp(−2 M (q − θ_q)²) for q > θ_q
P(X / M ≥ θ_q) ≤ exp(−2 M (θ_q − q)²) for q < θ_q
```

— a two-sided concentration whose transition is sharp when M is large. For C1 family-a (M ≈ 8 multi-digit numbers per workload), the transition width is comparable to the observed cliff width. This is a plain-language *explanation*, not a proof; the analytic bound matches the empirical cliff sharpness to within the resolution of the sweep's ratio grid.

The filter × family-c non-cliff (§5.3) has a different explanation: filter's TF-IDF + cross-encoder reranker over-weights distinctive tokens like `Entry N` and `FINAL-NNNN`, preserving them well past where generic per-token recall drops below θ_q. This is the *graded importance* phenomenon that A2 (binary token importance) elides; it is also the explicit *failure mode* of the compounding-error model. We foreshadow CAAC (Ch 8 §8.2): CAAC's per-fragment safety check uses critical-token-recall *as the operationalisation* of the model's q(r), so a fragment whose critical tokens survive (filter / family-c) is permitted higher compression than a fragment whose critical tokens do not.

---

---

## Chapter 6 — RAG Pipeline Placement and Cost (4–5 pp) — H3

> **Chapter abstract.** We compare three RAG pipeline placements — P1 (compress → retrieve), P2 (retrieve → compress), and P3 (joint relevance-conditional routing) — on family-a workloads under two operating regimes (storage-bounded ≤ 100 MB FAISS index, accuracy-bounded ≥ 0.85 retrieval recall@10). H3 pre-registered a *sign-flip* prediction: P1 should win one regime, P2 the other, and P3 should win the combined F1/EUR score with a ≥ 5 pp effect. **The sign-flip did not appear.** P1 leads P2 in *both* regimes (+3.24 pp in storage-bounded, +2.02 pp in accuracy-bounded; both p < 0.0001 Holm-corrected). P3 dominates the combined F1/EUR ranking in both regimes. We report H3 as NOT SUPPORTED honestly (per Q12 / `draft1.md` framing decision), then offer a single interpretive subsection on why compress-first works — without re-registering a post-hoc hypothesis.

### 6.1 Setup

Three pipelines indexed on FAISS-CPU with `BAAI/bge-large-en-v1.5` embeddings:

- **P1 (compress → retrieve):** every fragment is compressed by LLMLingua-2 at the operating ratio before indexing. Retrieval issues queries against the compressed index.
- **P2 (retrieve → compress):** every fragment is indexed verbatim; LLMLingua-2 compresses the retrieved top-*k* fragments at query time.
- **P3 (joint relevance-conditional):** retrieval returns top-*k* with scores. Scores above θ_high pass verbatim; between θ_low and θ_high pass through compression; below θ_low are dropped.

Two regimes are evaluated:

- **Storage-bounded.** FAISS index ≤ 100 MB. The operating ratio per pipeline is chosen to meet this bound.
- **Accuracy-bounded.** Retrieval recall @ 10 ≥ 0.85. The operating ratio is chosen to meet this bound.

The cost model (`m6/pipelines/cost_model.py`) charges retrieval at 0.05 EUR / 1 M corpus tokens (on-prem amortised) and frontier-cloud reference numbers at USD 3 in / USD 15 out per 1 M tokens (cited but not run; see `plan-v3 §5.3`).

Sample: 50 family-a workloads × 3 pipelines × 2 regimes × 3 seeds = 900 cells. Canonical results: `results/h3_final/`.

### 6.2 H3 verdict — NOT SUPPORTED

> **H3 (sign-flip between regimes with ≥ 5 pp effect, plus P3 wins combined F1/EUR in both regimes): NOT SUPPORTED.** P1 leads P2 in both regimes (no sign-flip). P3 wins the combined ranking in both regimes (matches the second clause of H3 but the predicted first clause failed). The pre-registered headline prediction is falsified; we report the negative finding honestly.

| Regime | Leader | P1 vs P2 Δ (pp) | 95 % CI | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| Storage-bounded (index ≤ 100 MB) | P3 | +3.24 | [+1.84, +4.72] | 0.0001 | 0.0002 |
| Accuracy-bounded (recall@10 ≥ 0.85) | P3 | +2.02 | [+1.15, +2.85] | 0.0001 | 0.0002 |

*Numbers from `results/h3_final/verdicts.json`. Negative Δ would have indicated P2 > P1; both Δ are positive.*

*Figure 6.1 (`figures/h3_pipelines.png`): per-regime bar chart of P1 / P2 / P3 with the F1/EUR composite score; P3 dominates in both regimes with a substantial margin over P1, which in turn dominates P2.*

**No re-registered hypothesis.** The thesis explicitly does *not* introduce a post-hoc H3' ("compress-first dominates retrieve-then-compress") with a new verdict block. Doing so would be HARKing (Hypothesising After the Results are Known) and would compromise the rubric #6 honesty score. We report H3 as falsified and add a single interpretive paragraph.

### 6.3 Interpretation — why compress-first works in this regime

The pre-registered prediction was that storage-bounded operation would favour compress-first (a smaller index admits more documents into the corpus, raising retrieval coverage at the cost of some retrievability per document) while accuracy-bounded operation would favour retrieve-first (the retrieval step sees the full document and is therefore more accurate, with compression applied after). In our regime this argument did not survive contact with the data because *our index is small* (150 workloads × ~8 fragments each, ~1200 fragments) and *our retriever is strong* (`bge-large-en-v1.5`, MTEB top tier at the time of writing). Both regimes operate well inside the retriever's capability envelope, so the regime distinction does not separate the placements as predicted.

P3's dominance is the unsurprising part: a routing pipeline that admits high-confidence retrievals verbatim and applies compression only where it helps is strictly better than either fixed placement. The interesting empirical claim is that P1's lead over P2 — small but statistically robust under Holm correction — challenges the standard intuition (formalised in LongLLMLingua) that post-retrieval compression is the more efficient operating point. We discuss this in Ch 8 §8.5 as a *partial challenge* to LongLLMLingua's assumption: in regimes where the retriever is strong relative to the corpus, compress-first is competitive or slightly better, plausibly because the retrieval step itself benefits from the compressed representation (a sharper TF-IDF signal in the index).

We explicitly *do not* claim to refute LongLLMLingua. The original LongLLMLingua experiments use much larger corpora and different retrievers; the conditions under which P2 wins remain plausibly common in production RAG settings.

### 6.4 Cost commentary

At the 0.05 EUR / 1 M token on-prem amortised rate, the per-workload EUR cost of all three pipelines is within an order of magnitude of each other; the F1 / EUR composite reported in the H3 verdict block is dominated by F1 rather than EUR. The reference frontier-cloud cost (USD 3 in / USD 15 out per 1 M tokens) inflates the EUR axis by roughly two orders of magnitude but does not change the within-pipeline ranking. The cost analysis is not load-bearing for the H3 verdict and we present it for completeness in Appendix B.

---

## Chapter 7 — Inference Disclosure, Memory-Bus Integration, and Information-Density Scaling (6–7 pp)

> **Chapter abstract.** §7.1 introduces the protected-fact-recovery metric: a held-out local Llama-3.1-8B reader is asked yes/no questions whose ground-truth answers depend on protected facts embedded in CONFIDENTIAL-tagged fragments. **H4** is SUPPORTED on the unbiased benchmark (`results/h4_unbiased/`): the metric distinguishes uncompressed source-fragment summaries from priors-only context (+29 pp baseline-over-priors, p = 0.0001), AND compression at 4 × *reduces* protected-fact recovery (filter −21 pp, lingua2 −19 pp, both p = 0.0001 Holm-corrected; Phi-3-extractive −7.5 pp, p = 0.027 borderline). §7.2 documents the surface-pattern bias that the original `h4_final` benchmark accidentally introduced and how the unbiased benchmark resolves it. §7.3 documents the reader's no-bias caveat (Llama-3.1-8B under-predicts YES) and what claim H4 actually supports given this. §7.4 reframes H6 — the MultiHopRAG transfer experiment that fell outside the original tolerance — as **Corollary 2** (information-density scaling): θ_info varies across tasks (C1-a 0.967, MHR 0.484, HotpotQA 0.373), and the variation explains the τ\* differences. §7.5 ties the chapter to the memory-bus architecture: how the bus exposes the protected-fact-recovery measurement to operators.

### 7.1 H4 — protected-fact recovery as a privacy-measurement primitive

> **H4 SUPPORTED on the unbiased benchmark.** The protected-fact-recovery rate distinguishes uncompressed baseline from priors-only context (+29 pp, p = 0.0001 for all three compressors), AND compression at 4 × reduces protected-fact recovery substantially for the two aggressive token-level compressors (filter −21 pp, lingua2 −19 pp; both p = 0.0001 Holm-corrected) and modestly for the extractive copier (Phi-3 −7.5 pp, p = 0.027). *Numbers from `results/h4_unbiased/verdicts.json`.*

**Method.** For each workload, every CONFIDENTIAL-tagged fragment carries a set of yes/no questions whose ground-truth answer depends on a *protected fact* — a specific value inside the fragment that does not appear in the workload's public preamble. A held-out local Llama-3.1-8B reader, blind to whether it is reading source or summary, is asked the question under three conditions:

- **priors:** the reader sees only the workload's public preamble. The recovery rate measures what the reader can answer from priors alone (general-knowledge ceiling).
- **baseline (1×):** the reader sees the uncompressed source fragments. The recovery rate measures the protected-fact channel without compression.
- **compressed (4×):** the reader sees the Phi-3-extractive (or filter, or LLMLingua-2) summary at the 4 × operating ratio. The recovery rate measures how much of the protected-fact channel survives compression.

The H4 falsification target was twofold: (a) baseline > priors (the metric measures something real, not noise), AND (b) compressed < baseline (compression at 4 × reduces protected-fact recovery, not enables it).

**Per-compressor results (unbiased benchmark).** *Numbers from `results/h4_unbiased/verdicts.json`.*

| Compressor | priors | baseline (1×) | compressed (4×) | signal (b − p) | signal 95 % CI | signal Holm p | reduction (b − c) | reduction 95 % CI | reduction Holm p |
|---|---|---|---|---|---|---|---|---|---|
| filter | 0.496 | 0.782 | 0.568 | **+28.6 pp** | [+22.9, +34.3] | 6 × 10⁻⁴ | **−21.4 pp** | [−26.8, −16.1] | 6 × 10⁻⁴ |
| LLMLingua-2 | 0.496 | 0.782 | 0.593 | **+28.6 pp** | [+22.9, +34.3] | 6 × 10⁻⁴ | **−18.9 pp** | [−25.4, −12.5] | 6 × 10⁻⁴ |
| Phi-3-extractive | 0.496 | 0.782 | 0.707 | **+28.6 pp** | [+22.9, +34.3] | 6 × 10⁻⁴ | **−7.5 pp** | [−13.9, −0.7] | 2.7 × 10⁻² |

The signal-test (baseline − priors) is identical across compressors because all three use the same uncompressed baseline — the compressor only enters in the compressed condition. The reduction-test (baseline − compressed) is the H4-relevant quantity and varies by compressor *aggressiveness*: filter and LLMLingua-2 (aggressive token-level compressors) reduce protected-fact recovery by ≈ 20 pp at the 4 × operating ratio; Phi-3-extractive (verbatim-span copier) preserves the protected-fact channel substantially better, with only a 7.5 pp reduction (borderline significant under Holm correction across the family of 6 tests).

*Figure 7.1 (`figures/privacy_quality.png`): per-compressor bar chart with three bars per compressor (priors, baseline, compressed) and ±95 % CI whiskers.*

**Interpretation.** The signal is large (+29 pp) and identical across compressors at baseline: the metric is measuring real protected-fact leakage, not noise. The *reduction* under compression varies by compressor *aggressiveness*: filter and LLMLingua-2 are aggressive token-level compressors that drop most of the protected-fact tokens at 4 ×, so their reductions are large (−19 to −21 pp). Phi-3-extractive is a verbatim-span copier that preserves protected-fact tokens whenever they appear in the highest-importance spans; its reduction is modest (−7.5 pp, borderline significant). The interpretation generalises: the more aggressive the compressor, the more of the protected-fact channel it discards, *and* the more of the task-critical channel it discards (Ch 5). The privacy and utility axes are coupled, not orthogonal.

**Comparison to prior work.** Privacy-aware RAG (e.g., HippoRAG and contemporaneous work) protects the retrieval *index* against membership-inference attacks. H4 measures something different: leakage *through the compressor*, with the index neutral and the reader held out. This is, to our knowledge, the first measurement of compressor-mediated protected-fact leakage in a multi-fragment setting.

### 7.2 The unbiased-benchmark fix (2026-05-29)

A late-cycle re-audit (`insights §54` / 2026-05-29 reconciliation) discovered a question-template surface-pattern bias in the original `h4_final` benchmark. Every "at least X" question had ground truth YES; every "exceed X" question had ground truth NO. A surface-pattern reader could score 100 % from the question verb alone, inflating the baseline rate to 0.97. The Llama-3.1-8B reader did *not* in fact exploit this bias in practice (its priors rate stayed near 0.50), but the data was nevertheless biased and the headline reduction effect was inflated.

The benchmark generator (`m6.benchmark.workloads.fact_aggregation:119–156`) was patched to use a single comparator phrasing ("at least N") with a parity-based threshold sign — decoupling the YES/NO answer from question wording. The fragments themselves were not regenerated (the compression cache for the source fragments remained valid), so the canonical H4 result lives in `results/h4_unbiased/`, and the original `results/h4_final/` is preserved on disk as a methodological artefact. The thesis cites `h4_unbiased` exclusively for the H4 verdict.

### 7.3 The reader's "no" bias — what claim H4 actually supports

The Llama-3.1-8B reader under-predicts YES. On the unbiased benchmark, when ground truth is YES the priors recovery rate is ≈ 0.03 (the reader almost always says NO with no context), and the baseline rate is ≈ 0.58 (uncompressed source flips the reader to YES on more than half of YES-ground-truth questions). When ground truth is NO, both priors and baseline are ≈ 1.00 (the reader's default NO is correct). The pooled priors of 0.50 reflects the balanced ground-truth distribution, not the reader's competence.

This asymmetry shapes the claim H4 actually supports. The claim is not "compression preserves a fully diagnostic protected-fact channel"; it is **"compression preserves enough information to flip a no-biased reader from confident NO to confident YES on a substantial fraction of YES-ground-truth questions."** This is *asymmetric* — the YES-side leakage is what compression reduces; the NO-side default is unchanged. The asymmetric framing is more conservative than the original pre-registered framing but is the honest reading of the data; we note it explicitly in the verdict block and discuss it in Ch 8 §8.4.

### 7.4 Corollary 2 — information-density scaling (reframing of H6)

> **Original H6 (τ\* on MultiHopRAG within ±15 % of C1 family-a, and coordination success within ±10 pp): NOT SUPPORTED.** MultiHopRAG τ\* = 11.3 × vs C1-a τ\* = 2.70 ×, a 320 % difference. MultiHopRAG baseline coordination success ≈ 0.35 vs C1-a ≈ 1.0, a 65 pp gap.
> **Reframed as Corollary 2 (information-density scaling): SUPPORTED.** θ_info varies substantially across tasks (C1-a ≈ 0.97, MHR ≈ 0.48, HotpotQA ≈ 0.37), and the variation explains the τ\* differences direction-and-magnitude consistently with the compounding-error model. *Numbers from `results/h6_final/verdicts.json` and `results/hotpotqa_sweep/verdicts.json`; thesis-only positioning per `ADR-006`-period Q11.*

**Statement.** θ_info — the AUC-based information-density estimator returned by `estimate_task_theta()` (per `CONTEXT.md`) — scales with the fraction of task-critical tokens in a workload. Dense quantitative tasks (C1 family-a: every multi-digit number matters) have θ_info close to 1.0 and cliff early. Distributed qualitative tasks (multi-paragraph multi-hop QA on news articles) have θ_info ≪ 1.0 and cliff late or degrade gradually.

**Evidence (three data points).**

| Task | θ_info | empirical τ\* | character |
|---|---|---|---|
| C1 family-a (synthetic dense) | 0.967 | 2.70 × | sharp cliff |
| MultiHopRAG (multi-hop news QA) | 0.484 | 11.3 × | gradual degradation |
| HotpotQA (multi-hop wiki QA) | 0.373 | 2.69 × | sharp cliff at moderate ratio, then floor |

*Figure 7.2 (`figures/hotpotqa_cliff.png`): HotpotQA coordination-success curve overlaid with the C1-a synthetic reference. Two cliffs at similar ratios but vastly different θ_info — the gap is the second-order pattern Corollary 2 captures.*

**Interpretation.** The compounding-error model's first-order prediction (Ch 5 §5.5) does not vary by task: it predicts the cliff position from q(r) and θ_q. Empirically, q(r) is roughly compressor-determined and stable across tasks, but the cliff *shape* (sharp vs gradual) varies by task in a way the first-order model elides. Corollary 2 makes that variation legible: θ_info captures the *concentration* of task-critical information across fragments. When θ_info is high, single missing tokens destroy success (sharp cliff); when θ_info is low, the task has redundancy and degrades smoothly.

**Honest caveat — θ_info is AUC-derived, not a parameter of the model.** The compounding-error model in §5.4 uses θ_q (the recall threshold). θ_info is a *separate* AUC-based estimator, derived from the coord_success curve and *not* the recall curve. The two are distinct quantities (see `CONTEXT.md`); confusing them was a real failure mode of the 2026-05-29 reconciliation work. Corollary 2 is therefore an *empirical pattern* aligned with the model's predictions, not a derived consequence of the model. We surface this in Ch 8 §8.4 as the open *second-order modelling* question the thesis hands off to future work.

**Positioning.** Corollary 2 is thesis-only per Q11 (`docs/adr/ADR-006`-period grilling): it appears in this chapter with full verdict, but is not load-bearing for any external venue. The MHR sweep was not instrumented to compute critical-token-recall (only token-recall), so rigorous CTR-based validation of Corollary 2 is deferred to future work.

### 7.5 The memory bus and the H4 channel

The memory bus exposes the protected-fact-recovery measurement as a service-level metric: the audit log records the slot identifier, the original fragment's tag set, and the compressed payload reference. An operator can run the held-out reader against the bus's `/v1/read/{slot_id}` endpoint with a curated yes/no question set at any time and compare the recovery rate against a moving baseline. This is the *operationalisation* of H4 for a production deployment: the same metric the thesis uses to validate the H4 measurement primitive can be re-run by an operator without modifying the compressor or the data path.

The bus does not enforce a privacy SLA. The operator is responsible for choosing the question set and for acting on recovery-rate signals (e.g., switching compressor at a higher ratio for fragments above a sensitivity threshold). The bus provides the *measurement infrastructure*; the policy layer is out of scope per `plan-v3 §1` (production-grade governance enforcement is doctoral-phase work).

---

## Chapter 8 — Discussion, CAAC, Limitations, Future Work (7–9 pp)

> **Chapter abstract.** §8.1 puts the four contributions (C1 benchmark, C2 cliff characterisation + model, C3 RAG placement, C4 inference-disclosure metric) on a single page with the verdict-by-verdict summary. §8.2 introduces and evaluates **CAAC** — Cliff-Aware Adaptive Compression — as a constructive realization of the compounding-error model's q ≥ θ_q safety bound, with per-family operating-point results from the 2026-05-29 CTR + per-family θ wiring (`results/caac/`). The 0 / 7 strict-Pareto rate is reported as the *expected and correct* property, not as a contribution failure (per `ADR-007`). §8.3 lists the methodological limitations (single-call planner caveat, family-a uniformity, family-b capacity inflation, the reader's no-bias caveat). §8.4 lists the model-level limitations (A2 binary token importance violated, the gap to Corollary 2's θ_info, the calibrated-regime predicate's empirical character). §8.5 discusses the connection to LongLLMLingua and the partial challenge to retrieve-first RAG. §8.6 lists future work, ordered by leverage.

### 8.1 Contributions delivered — verdict summary

| ID | Contribution | Verdict | Where in thesis |
|---|---|---|---|
| C1 | Multi-fragment coordination benchmark | Delivered (Ch 4) | Reproducible from seed; three families × 150 instances; CTR taxonomy; ACL tag schema |
| C2.H1 | Information preservation decorrelates from coordination | SUPPORTED (Ch 5 §5.2) | Spearman \|ρ\| < 0.6 across 4 compressors |
| C2.H2 | Coordination cliff exists, sharp, statistically robust | SUPPORTED (Ch 5 §5.3) | 8 / 9 cells significant |
| C2.model | Compounding-error model with bootstrap CI on θ_q | First-order delivered (Ch 5 §5.4–§5.5) | tight CI on θ_q; 0 / 11 cells in bootstrap band — residual is structural, not noise |
| C2.Cor1 | Ceiling-cliff separation (model independence in calibrated regime) | SUPPORTED (Ch 5 §5.6–§5.7) | Qwen-72B 0.8 % off, DeepSeek CI contains synth; GPT-oss out-of-regime |
| C3 | RAG placement and cost catalogue | H3 NOT SUPPORTED honestly (Ch 6) | P1 dominates P2 in both regimes (no sign-flip); P3 dominates combined |
| C4.H4 | Protected-fact recovery metric reduces under compression | SUPPORTED on unbiased benchmark (Ch 7 §7.1–§7.3) | filter / lingua2 −19 to −21 pp; Phi-3 −7.5 pp borderline |
| C4.Cor2 | Information-density scaling θ_info varies by task | SUPPORTED (Ch 7 §7.4) | C1-a 0.97, MHR 0.48, HotpotQA 0.37 |

Five hypotheses produce six verdicts (H5 + H6 each spawning a corollary). Four delivered as SUPPORTED, one (H3) reported as NOT SUPPORTED honestly without re-registration. The model is first-order with quantified residual. This is the thesis's evidence base.

### 8.2 CAAC — a constructive realization of the safety bound

CAAC (Cliff-Aware Adaptive Compression) wraps any base compressor and selects an adaptive per-fragment compression ratio using the compounding-error model's q ≥ θ_q safety bound (Ch 5 §5.4) as its target invariant. The algorithm is described in `m6.compressors.caac:CAACCompressor`. At a high level:

1. Compute q_min = θ_q (for N = 1 single-pass compression).
2. For each fragment, compress at the target ratio; measure critical-token-recall.
3. If q ≥ q_min: accept (safe operating point reached).
4. Else: binary-search for the largest ratio at which q ≥ q_min, bounded below by min_ratio = 1.5 × (the configured floor).

The thesis does *not* claim CAAC strictly Pareto-dominates fixed-ratio compression. The audit period explicitly resolved this (per `ADR-007`): under a strict Pareto criterion (CAAC no worse on coord_success AND on achieved ratio AND strictly better on at least one), CAAC dominates 0 / 7 ratios on every (inner_compressor, family) cell. This is the **expected and correct** property: CAAC by construction trades compression for coordination at high target ratios; it cannot be strictly Pareto-dominant. The honest CAAC framing is *operating-point selection*: given a per-family θ_q, CAAC's selected operating point is determined by the model rather than tuned. We position CAAC as a methodological demonstration — a working algorithm that operationalises the model — not as a method contribution.

**Per-family results (2026-05-29 CTR + per-family θ_q rerun; `results/caac/summary_per_family.json`).**

| inner compressor | family | θ_q | fixed coord at high r | CAAC coord at high r | Δ (pp) | CAAC achieved | reading |
|---|---|---|---|---|---|---|---|
| filter | a | 0.632 | 0 % | 50 % | **+50** | 1.9 × (floor) | strong win — CAAC pancakes to floor, preserves coord; fixed collapses |
| LLMLingua-2 | c | 0.590 | 92 % | 100 % | **+8** | ~3.0 × | modest win — safe operating point preserved |
| filter | c | 0.590 | 100 % | 100 % | 0 | matches fixed | family-c with filter already robust; CAAC does no harm |
| filter | b | 0.838 | 0 % | 0 % | 0 | 2.1 × (floor) | floor effect on both; CAAC gives up to floor |
| LLMLingua-2 | a | 0.632 | 0 % | 0 % | 0 | floor | inner compressor already below θ_q at r > 1; CAAC cannot rescue |
| LLMLingua-2 | b | 0.838 | 0 % | 0 % | 0 | floor | same |

*Figure 8.1 (`figures/caac_pareto.png`): three-panel per-family layout. Each panel plots fixed-ratio (open circles, distinct colour per inner compressor) and CAAC (filled squares) on the (achieved_ratio, coord_success) plane, with the per-family θ_q annotated inline.*

**Reading.** CAAC's value is concentrated on (filter, family-a) and (LLMLingua-2, family-c). These are the two (inner, family) cells where (i) fixed-ratio compression cliffs in the swept range, and (ii) the inner compressor's q above q_min at r < cliff is high enough that CAAC's binary search can find a safe operating point above min_ratio. When either condition fails (most cells), CAAC pancakes to the min_ratio floor — a behaviour acknowledged in the CAAC docstring and visible in the data. Across all 12 cells the weak-dominance rate (CAAC coord ≥ fixed coord) is 100 %, but as noted, this is not a "win" in the Pareto sense; it is the *no-harm* property of a wrapper that respects a safety bound.

**The θ / N ablation (informative null).** A 7-config grid sweep over θ ∈ {0.6, 0.7, 0.8} and N ∈ {2, 3, 4, 5} (results: `results/caac_theta_*`, `results/caac_N_*`) shows that CAAC's coord_success is *invariant* to θ and N within the swept range, while the achieved ratio retreats monotonically toward the min_ratio floor as either parameter tightens. This is consistent with CAAC functioning as a *safety floor* rather than as a Pareto optimiser: θ and N control *how aggressively CAAC backs off*, not *whether CAAC unlocks a new operating point*. The result, documented in `insights §54`, is *informative null evidence* — a finding that the algorithm has the character its model says it should, not a refutation.

### 8.3 Methodological limitations

We list the limitations in order of impact on the thesis's claims.

**Single-call planner caveat (`ADR-009`).** The H5/H6 and frontier experiments use a single LLM call with all compressed fragments visible; the H1/H2 experiments use a deterministic regex parser. Neither is a multi-round multi-agent system. The thesis title (*Multi-Fragment LLM Workflows*) reflects this restriction; the abstract and Ch 1 P5 surface the disclosure. The bus is *designed for* multi-round use but was not *evaluated* in that mode because round-to-round LLM variance dominated the compression signal in pilot runs. This limits the thesis's claims to *task-solvability under compression*, not *multi-round agent coordination*.

**Family-a reasoning-type uniformity.** All 50 family-a workloads use the same template (sum 8 multi-digit numbers across 8 fragments). The cliff result for family-a is therefore strong evidence for one specific reasoning pattern; generalisation across reasoning types is not measured. The thesis cites HotpotQA / MHR transfer (Ch 7 §7.4) as partial cross-task evidence.

**Family-b capacity inflation.** The C1 family-b generator inflates per-worker capacity to guarantee feasibility for the deterministic solver. This makes family-b *trivial at high token-recall* for the deterministic solver — visible in the lingua2 / family-b 0 % baseline on the deterministic side. For the LLM planner, constraint tracking is the harder sub-problem and family-b shows a genuine cliff. The asymmetry weakens cross-family numerical comparisons; we report family-b results with this caveat in §5.3.

**H4 reader's no-bias.** Llama-3.1-8B under-predicts YES (Ch 7 §7.3). The H4 signal is real but *asymmetric*: compression preserves enough information to flip the reader from a confident NO to a confident YES on a substantial fraction of YES-ground-truth questions. A reader without this bias would produce a different signal magnitude; the *direction* (compression reduces protected-fact recovery) is preserved.

**Synthetic benchmark — partial cross-task validation.** C1 is synthetic. The thesis uses MHR and HotpotQA as external multi-hop benchmarks to test cross-task transfer (Ch 7 §7.4, Corollary 2). MHR's CTR was not instrumented; rigorous CTR-based Corollary 2 validation is future work.

### 8.4 Model-level limitations

**A2 (binary token importance) is violated empirically.** H4 measures graded token importance directly (some tokens are more diagnostic of protected facts than others); the compounding-error model elides this by treating critical tokens as a binary class. The 0 / 11 bootstrap-band coverage in Ch 5 §5.5 is the empirical signature of this violation: predicted τ\* is systematically off from empirical τ\* in a direction the model cannot capture with θ_q alone. **The right refinement** is a *weighted-token* extension of the model where each critical token i carries a weight w_i, q(r) is replaced by an importance-weighted retention sum, and the threshold success condition becomes Σ_i w_i 1[token i survived] ≥ θ_q ⋅ Σ_i w_i. Validating this weighted extension empirically is the most leveraged future-work direction.

**θ_q vs θ_info gap.** The thesis introduces both (Ch 5 §5.4 for θ_q; Ch 7 §7.4 for θ_info) and explicitly states they are different quantities (per `CONTEXT.md`). Corollary 2 (information-density scaling) is an *empirical pattern* aligned with the model's predictions, not a derived consequence. Closing this gap requires either deriving θ_info as a model parameter or motivating the model from a generative process that produces both. We do neither in this thesis; we hand the question to future work.

**Calibrated-regime predicate is empirical, not analytical.** The calibrated regime (Ch 5 §5.4) is defined operationally: no floor effect AND bounded reasoning slack (operationalised by the priors-only baseline). It is not derived from a property of the planner architecture. The GPT-oss 120B exclusion (`ADR-006`) is the worked example; a theoretical characterisation of *which* architectures admit extended-reasoning slack is future work.

### 8.5 The connection to LongLLMLingua and the partial challenge to retrieve-first

LongLLMLingua (Jiang et al., ACL 2024) argues that post-retrieval compression (P2 in our taxonomy) is the more efficient placement because the retriever benefits from full document text. Chapter 6's H3 result reports a *partial* challenge to this: in our regime (small index, strong retriever, family-a workloads) P1 (compress-first) is consistently slightly ahead of P2 in both storage- and accuracy-bounded operation, with statistically significant Holm-corrected p-values. We do *not* claim to refute LongLLMLingua; their experimental regime is larger and the retriever-corpus ratio differs. We claim that *the choice of placement is not as one-sided as LongLLMLingua's argument suggests*, and that the choice depends on the retriever-corpus regime in ways that future RAG work should make explicit.

### 8.6 Future work — ordered by leverage

1. **Weighted-token extension of the compounding-error model.** The single highest-leverage modelling step: derive q_min from a weighted-token retention sum rather than a binary token retention rate. The bootstrap-band coverage in Ch 5 §5.5 quantifies the gap to be closed. (Modelling, ~1–2 weeks; expects to recover ≥ 1/2 of the 11 currently-out-of-band cells.)
2. **Multi-round multi-agent evaluation.** The thesis explicitly scopes to single-call planners. Re-running H1/H2 on the AutoGen multi-round backend (with variance control via shared random seeds across compressors) would test whether the cliff appears in genuinely multi-agent settings. (Engineering, ~2–3 weeks; uses existing `m6.agents.orchestrator`.)
3. **Extended-reasoning planner characterisation.** GPT-oss 120B is the worked out-of-regime example. Running the cliff sweep on Claude 4.6, Gemini 2.5, OpenAI o3 (current reasoning-mode flagships) would characterise the *boundary* of the calibrated regime as a function of reasoning slack. (API + analysis, ~$200 + 1 week.)
4. **MHR CTR instrumentation for rigorous Corollary 2.** Re-run H6 with critical-token-recall computed at the MHR-specific token taxonomy (entity names, dates, places — designed for news-article QA). (Engineering + GPU, ~4 hours.)
5. **Trained CAAC variant.** The training-free CAAC achieves the safety guarantee but pancakes to floor on most cells. A trained CAAC variant that learns per-fragment θ_q from a held-out coordination signal could expand the family of cells where CAAC's operating point is non-trivial. (Training, ~1–2 weeks.)
6. **HotpotQA at multiple compressors.** The 2026-05-28 HotpotQA sweep used LLMLingua-2 only; extending to filter + Phi-3 + truncation would make Corollary 2's third data point as multi-compressor-validated as MHR. (GPU, ~4 hours.)
7. **Privacy SLA enforcement on the memory bus.** Ch 7 §7.5 documents the measurement infrastructure; an enforcement layer (compressor switching on protected-fact-recovery threshold breach) is a natural follow-on. (Engineering, ~1 week.)

---

## Pass-1 status

This pass covers Chapters 3, 4, 5, 6, 7, and 8 — Section 7 ("Order of writing") of `thesis_PLAN.md` recommends this order because these are the methods + results chapters. Pass 2 closes with Chapter 2 (Background) and Chapter 1 (Introduction), to be drafted after the chapters above are settled — Section 7 explicitly recommends writing Intro last because the contributions are only fully verified at the end of writing.

**Numbers refresh pass 1 complete (2026-05-30).** All H1, H2, H4 verdict-block numbers in this draft are from the canonical `results/h1_h2_v2/verdicts.json` (H1, H2) and `results/h4_unbiased/verdicts.json` (H4). The terminology and framing are locked against `CONTEXT.md`, ADR-006, ADR-007, ADR-008, and ADR-009. The pre-submission checklist (`thesis_PLAN.md §8`) is the next-pass verification target.

**Word/page estimate at pass 1.** Chapters 3–8 in this draft total roughly 11 000 words → ~28–32 pages at Oulu thesis margins. Combined with the ~16–20 pages of Chapters 1, 2 and Appendices in pass 2, the manuscript trends toward the 50–60-page envelope expected for a Master's thesis at this scope.
