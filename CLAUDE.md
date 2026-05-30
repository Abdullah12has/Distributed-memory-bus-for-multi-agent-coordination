# M6 Thesis — Distributed Memory Bus for Multi-Agent Coordination

Master's thesis by Syed Abdullah Hassan, University of Oulu.
Context compression + coordination quality + policy-aware sharing.

## IMPORTANT: Insight Logging Rule

**Every new insight, finding, bug, fix, or decision MUST be appended to `insights.txt`** in the project root. This includes:
- Experiment results and their interpretation
- Bugs found and how they were fixed
- Design decisions and their rationale
- Performance observations
- Hypothesis verdict changes

Format: numbered section with heading, date, and clear description. See existing entries in `insights.txt` for style.

---

## Project Structure

| Path | Purpose |
|------|---------|
| `src/m6/` | Main package (pip-installable as `m6`) |
| `configs/experiments/h{1-6}.yaml` | Experiment configs |
| `results/` | Local results (auto-created) |
| `data/processed/c1-v0.1/` | C1 benchmark (150 instances, 3 families) |
| `plan-v3.md` | Active plan (v1 and v2 are dead) |
| `docs/TECHNICAL_REFERENCE_V3.md` | Technical spec |
| `insights.txt` | Running log of all findings and decisions |
| `CONTEXT.md` | Domain glossary (θ_q vs θ_info, τ*, q(r), N, calibrated regime, etc.) |
| `docs/adr/ADR-006-008` | Load-bearing decisions from 2026-05-29 grilling reconciliation |

## Compressors (all training-free)

1. **LLMLingua-2** (`lingua2.py`) — token-level XLM-RoBERTa classifier
2. **Phi-3-Mini extractive** (`phi3_extractive.py`) — verbatim span selection via Ollama, with novel-token stripping + LLMLingua-2 fallback
3. **Instruction-aware filter** (`filter.py`) — TF-IDF + cross-encoder reranker
4. **Truncation** (`truncation.py`) — prefix-truncation baseline (added 2026-05-27 for h1_h2_v2)
5. **Identity** (`__init__.py`) — no-compression control
6. **CAAC** (`caac.py`) — wrapper, not a fifth family; per ADR-007 reframed as operating-point selection (not Pareto dominance)

## Experiment Scripts (v3, self-contained)

```bash
# Smoke tests (local)
python -m m6.experiments.run_h1_h2 --smoke
python -m m6.experiments.run_h3 --smoke
python -m m6.experiments.run_h4 --smoke
python -m m6.experiments.run_h5 --smoke
python -m m6.experiments.run_h6 --smoke

# Full runs (on GPU server: ssh gpu)
python -m m6.experiments.run_h1_h2
python -m m6.experiments.run_h3
python -m m6.experiments.run_h4
python -m m6.experiments.run_h5
python -m m6.experiments.run_h6 --synth-results results/h5_full
```

## GPU Server

- Access: `ssh gpu` (Tailscale 100.70.160.59, WSL2 Ubuntu 22.04)
- Hardware: RTX 5090 32GB, Python 3.12, CUDA, Ollama
- Venv: `~/Distributed-memory-bus-for-multi-agent-coordination/.venv/`
- Must use `.venv/bin/python3` (system python is 3.10)
- `OLLAMA_NUM_PARALLEL=4` set in `~/.bashrc`
- nvidia-smi at `/usr/lib/wsl/lib/nvidia-smi`

## Hypotheses & Current Verdicts

### H1: QA vs Coordination Decorrelation
- **Criterion**: Spearman rho < 0.6, CI excluding 0.6, on >= 2/3 compressors
- **Status: SUPPORTED** (h1_h2_v3_quick2, 2026-05-24)
  - filter: rho=-0.287 [-0.331, -0.240]
  - lingua2: rho=0.256 [0.211, 0.298]
  - phi3-extractive: rho=0.284 [0.230, 0.336]
  - All 3/3 below 0.6 with CIs excluding 0.6

### H2: Coordination Cliff
- **Criterion**: Cliff >= 30% drop + Mann-Whitney p < 0.05 on >= 7/9 cells
- **Status: SUPPORTED** (h1_h2_v3_quick2, 2026-05-24, 8/9 cells significant)
  - Only failure: filter/c (tau=N/A, no cliff detected)
  - All tau* cluster near 15.9-16.0 (piecewise fit boundary bias — real drops but tau position unreliable)

### H3: RAG Pipeline Placement
- **Criterion**: P1/P2 sign-flip between storage/accuracy regimes, 5pp effect
- **Status: NOT SUPPORTED** (P1 > P2 in both regimes, no sign-flip; P3 dominates)
- Narrative: compress-first (P1) consistently better; challenges LongLLMLingua assumption

### H4: Inference Disclosure
- **Criterion**: baseline > priors AND compressed < baseline
- **Status: SUPPORTED** (re-validated 2026-05-29 on unbiased benchmark in `results/h4_unbiased/`)
  - Signal: +29pp (p=0.0001) for all 3 compressors (baseline 0.78 vs priors 0.50)
  - Reduction: filter -21pp, lingua2 -19pp (both p=0.0001); phi3 -7.5pp (p=0.027, borderline)
  - Key insight: compression aggressiveness correlates with disclosure gap. Aggressive token-level compressors (filter, lingua2) reduce disclosure substantially; extractive copying (phi3) preserves enough surface tokens that the leak persists.
- **Note (2026-05-29) — original `h4_final` had a question-template surface-pattern bias**: every "at least X" question had ground truth YES, every "exceed X" question had ground truth NO. A surface-pattern reader could score 100% from the verb alone. Reader (llama3.1:8b) didn't exploit this in practice (priors stayed near 0.50) but the DATA WAS biased, inflating baseline to 0.97. Benchmark generator was fixed (`fact_aggregation.py:119-156`) to use a single comparator phrasing ("at least N") with parity-based threshold sign — so the YES/NO answer is now decoupled from question wording. Fragments unchanged (cache stays valid).
- **Reader's "no" bias caveat**: llama3.1:8b under-predicts YES — when ground truth is yes, priors_rate ≈ 0.03, baseline_rate ≈ 0.58. When ground truth is no, both ≈ 1.00. The pooled priors of 0.50 reflects balanced ground-truth distribution, not reader competence. The thesis should note: H4 measures *"compression preserves enough to flip a no-biased reader to confident yes"* — asymmetric but still a valid leakage signal.

### H5: Model-Size Scaling
- **Original criterion**: tau* monotonic across 1.5B/3.8B/8B on >= 2/3 families, gap >= 1.5
- **Original status: NOT SUPPORTED** (confirmed across 5 diagnostic configs, 2026-05-24)
- **Reframed as Corollary 1 (Ceiling-Cliff Separation): SUPPORTED** (2026-05-27)
  - Family-c: all 3 models (1.5B/3.8B/8B) cliff at tau_mean=4.1, spread=24% — model-invariant
  - Family-a: 1.5B (17%) and 3.8B (3%) have floor effect (baseline < 50%) — correctly skipped
  - Family-b: all models below threshold — correctly skipped
  - **Key finding**: model size affects ceiling p0, not cliff position r*
  - Validates compounding-error model part (iii) **within the calibrated regime** per ADR-006: r* depends on compressor + task, not planner capacity. Extended-reasoning planners (e.g., GPT-oss 120B) are scoped out of this claim.

### H6: MultiHopRAG Transfer
- **Original criterion**: tau* within +/-15% of C1 family-a, coord_success within +/-10pp
- **Original status: NOT SUPPORTED** (h6_final, 2026-05-27, tau 320% different)
  - MultiHopRAG tau=11.3x vs C1 family-a tau=2.7x
  - MultiHopRAG baseline=34.7% (task much harder than C1)
- **Reframed as Corollary 2 (Information Density Scaling): SUPPORTED** (2026-05-27, confirmed 2026-05-29)
  - MultiHopRAG **θ_info**=0.484 (distributed QA, low info density)
  - C1 family-a **θ_info**=0.967 (dense numeric, high info density) — earlier value 0.881 was from a different computation; current canonical AUC-based value is 0.967 per `hotpotqa_sweep/verdicts.json`
  - HotpotQA θ_info=0.373 (most distributed)
  - Gap (MHR vs C1-a) = 0.48; gap (HotpotQA vs C1-a) = 0.59 — both well above 0.1 threshold
  - **Key finding**: θ_info scales with task information density — dense tasks cliff early, distributed tasks degrade gradually
  - **Important — θ_info ≠ θ_q.** θ_info (AUC-based, per-task, used here for Corollary 2) is distinct from θ_q (recall-threshold, per-family, used in the cliff equation q(r*) = θ_q). The CTR end-to-end switch for CAAC + cliff prediction does NOT affect Corollary 2. See CONTEXT.md.
  - **Thesis-only positioning** per ADR-006 / Q11: Corollary 2 lives in thesis Ch7; dropped from NeurIPS-track positioning.

## Completed Experiment Runs (GPU Server)

| Run | Directory | Date | Status | Notes |
|-----|-----------|------|--------|-------|
| H1/H2 final | `h1_h2_final` | 2026-05-26 | Done | 3 compressors, 10 ratios, H1+H2 SUPPORTED |
| H3 final | `h3_final` | 2026-05-26 | Done | 3 compressors, H3 not supported |
| H4 final | `h4_final` | 2026-05-26 | Done | H4 supported, 3 compressors |
| H5 final | `h5_final` | 2026-05-27 | Done | 9000 rows, Corollary 1 SUPPORTED |
| H6 final | `h6_final` | 2026-05-27 | Done | **1500 rows** (was misreported as 1524), Corollary 2 SUPPORTED |
| H1/H2 v2 | `h1_h2_v2` | 2026-05-27 | **Done** (27000 rows; 4 compressors incl truncation) |
| Frontier smoke | `frontier_smoke` | 2026-05-27 | Done | Featherless API test |
| Frontier Qwen 72B | `frontier_qwen72b` | 2026-05-28 | Done | 180 rows, τ_diff 0.8% from synth — VALIDATES |
| Frontier DeepSeek V4 Pro | `frontier_deepseekv4` | 2026-05-28 | Done | 180 rows, CI [1.76, 7.14] contains synth — VALIDATES |
| Frontier GPT-oss 120B (v1, v2) | `frontier_gptoss120b{,_v2}` | 2026-05-28 | **Scoped out per ADR-006** | Extended-reasoning planner, outside calibrated regime. Retained on disk with `STATUS_NONCANONICAL.txt`. |
| HotpotQA sweep | `hotpotqa_sweep` | 2026-05-28 | Done | 750 rows, τ=2.69, θ_info=0.373, Corollary 2 second external benchmark |
| CAAC | `caac` | 2026-05-28 | Done; **rerun pending** with CTR + per-family θ_q wiring per ADR-007 | 13500 rows; strict_pareto = 0/7 (expected per operating-point framing); §54 ablation confirms safety-floor character |

## Key Bugs Fixed

1. **qa_f1 always zero**: was comparing compressed fragments against aggregated answer; fixed to measure information preservation
2. **phi3 100% fallback**: verifier too strict, now salvages at >= 50% extractive fraction (commit 63bf8ee)
3. **H4 question bias**: all ground-truth answers were "no"; fixed to balanced yes/no
4. **H3 F1 metric**: was comparing retrieved text vs aggregated answer; fixed to fragment-level content F1
5. **H5 family-b agent/worker mismatch**: LLMs output `agent-X`, scoring expected `worker-X`; now accepts both (commit f6b942b)
6. **H5 family-b exact-match scoring**: replaced with feasibility checker — any valid bin-packing scores 1.0 (commit 9d006f7)
7. **H5 vacuous monotonicity**: all-NaN families no longer pass `all()` on empty iterator (commit 0da542b)
8. **H2/H5 tau boundary bias**: tau constrained to interior 10% margin, prevents parking at x.max (commit 0da542b)
9. **H4 missing Holm correction**: added Holm-Bonferroni across all 2N tests (commit 0da542b)
10. **H3 P1=P2 cost model**: P1 now uses compressed corpus tokens for retrieval cost (commit 0da542b)
11. **Smoke tests missing phi3**: added phi3-extractive to H1/H2, H3, H4 smoke configs (commit 0da542b)
12. **H1 task_hint mismatch**: QA and coord paths used different hints; now both use initial_prompt (commit 237d509)
13. **H1 CI inflation**: qa_f1 duplicated across seeds inflating N; now averages coord_success across seeds first (commit 237d509)
14. **H1 NaN CI acceptance**: NaN ci_high no longer counts as supported (commit 237d509)
15. **H4 silent "no" on exception**: now returns "error" + warning log (commit 237d509)
16. **H2 Mann-Whitney → Wilcoxon**: paired test (same workloads in both groups violates independence) (commit 59f5b63)
17. **H2 logistic fit added**: compounding-error model predicts smooth curve; both piecewise+logistic now fitted (commit 59f5b63)
18. **H5 max_gap non-monotonic**: gap now only from monotonic families (commit 59f5b63)
19. **H4 error tracking**: has_error column added, filtered before verdict (commit 59f5b63)
20. **H3 bootstrap inflation**: now averages per workload before bootstrapping (commit 59f5b63)
21. **H6 verdict tau-only**: coord curve comparison informational only (incompatible scoring) (commit 59f5b63)
22. **H5 task_hint missing**: pre-compression now passes w.initial_prompt (commit 59f5b63)
23. **n_workloads per family**: was total (only family-a loaded); now per-family so all families represented (commit 8b9bed6)
24. **Theorem N=3 mismatch**: claimed q^3 compounding but code compresses once; fixed to N=1 default, q_min=theta
25. **CAAC trivial backoff**: min_ratio was 1.0 (backs off to no compression); changed to 1.5
26. **CAAC hardcoded theta**: was 0.65 with no derivation; added `derive_theta()`, default now 0.5
27. **rounds field fake**: was `len(sub_tasks)` not actual rounds; set to 1 (truthful)
28. **Filter non-determinism**: stopword dropping depended on iteration order; words now as explicit list
29. **Missing critical_token_recall**: added family-specific metric (numbers for a, patterns for b, FINAL for c)
30. **Missing achieved_ratio**: added actual compression ratio column to H1/H2 CSV

## Critical Framing Notes (from deep review 2026-05-25, reconciled 2026-05-29)

### Naming: "compounding-error model", not "Theorem 1" (per ADR-008)
Thesis manuscript uses plan-v3's terminology: **compounding-error model**.
The formal LaTeX proof in `paper/sections/theorem.tex` is dropped — Ch5
uses the derivation paragraph from plan-v3 §3 instead. Codebase
identifiers (`theorem_validation.json`, `validate_theorem.py`, etc.)
are NOT renamed for back-compat; CONTEXT.md documents the mapping.

### N=1 (FIXED)
The compounding-error model originally claimed N=3 rounds of compression (q^N),
but the code only compresses once (N=1). Fixed: model now uses N=1 by default,
q_min = θ_q directly. The q^N formulation is still available for multi-pass
scenarios but is explicitly documented as not matching our experiments.

### Evaluation Honesty
- **Deterministic solver (H1/H2)**: Information-extraction pipeline (regex parser),
  NOT a multi-agent system. Isolates compression effects from LLM noise.
- **Ollama planner (H5/H6)**: Single LLM call with all fragments, NOT multi-round
  agent coordination. Measures coordination-task solvability under compression.
- **rounds field**: Set to 1 (truthful: one compression pass + one solve pass).
  Previously was set to len(sub_tasks), which was misleading.
- The AutoGen backend EXISTS in the code (orchestrator.py:179+) but was not used
  for production experiments due to high variance masking compression effects.

### CAAC Constraints (updated 2026-05-29 per ADR-007)
- min_ratio changed from 1.0 to 1.5 — CAAC must achieve at least 1.5x compression
- theta changed from hardcoded 0.65 to empirically derivable via `derive_theta()`
- Default theta=0.5, default n_compression_passes=1
- **Active sprint**: wire `cfg.theta = derive_theta(family, recall_column="critical_token_recall")` per-family; CAAC's internal q-check switches from generic token_recall to critical_token_recall. Rerun on GPU (~7h).
- **Framing**: CAAC reframed as theorem-grounded **operating-point selection** (not Pareto dominance). Strict-Pareto rate = 0/7 is the EXPECTED and CORRECT result, not a contribution-killer. CAAC trades compression for predictable coordination above q_min; fixed-ratio trades coord for compression. They populate complementary regions of the (coord, achieved_ratio) frontier. See ADR-007 + insights §54.

## Thesis-Text Actions (no code, must address in writing)

- **Rename H1**: "information preservation vs coordination" (not "QA accuracy")
- **Reframe H3**: "compress-first preserves content quality" (don't claim to falsify LongLLMLingua)
- **H5 Phi-3 confound**: acknowledge in discussion (0% at ratio=1.0)
- **H4 terminology**: use "protected-fact recovery rate" not "inference disclosure"
- **H3 cost**: note uses target ratio, not achieved
- **Evaluation scope**: explicitly state experiments measure task solvability, not multi-agent communication
- **Family-A limitation**: all 50 workloads are "sum 8 numbers" — zero variability in reasoning type. Acknowledge in limitations.
- **Family-B limitation**: capacity generator inflates capacity to ensure feasibility. Tasks are trivially solvable for the deterministic solver but still hard for LLM planners (constraint tracking).

## Chapter Mapping

- **Ch5**: H1 + H2 + H5 (compounding-error model + cliff measurement + Corollary 1)
- **Ch6**: H3 (RAG pipelines + cost) — verdict NOT SUPPORTED, honestly framed per Q12
- **Ch7**: H4 + H6 (protected-fact recovery + Corollary 2 + memory bus)
- **Ch8**: Discussion + CAAC demonstration (~3 pages per ADR-007) + limitations + future work

## Theory: Corollaries (added 2026-05-27, reconciled 2026-05-29)

### Corollary 1 (Ceiling-Cliff Separation)
Planner capacity m determines baseline success p0(m), while cliff position r*
is determined solely by compressor C and task threshold θ_q **within the
calibrated regime** (per ADR-006). When p0(m) < θ_q, no cliff is detectable
(floor effect). When p0(m) >= θ_q AND the planner does not recover from
sub-threshold information via extended reasoning, r* is invariant to m.
- Implemented: `validate_model_independence()` in cliff_prediction.py
- Validated: Family-c, all 3 local models (1.5B/3.8B/8B), τ spread=24%
- Validated at frontier: Qwen 72B (τ_diff 0.8%), DeepSeek V4 Pro (CI contains synth)
- Calibrated-regime exception: GPT-oss 120B scoped out per ADR-006

### Corollary 2 (Information Density Scaling)
**θ_info** ~ d (fraction of task-critical tokens). Dense quantitative tasks
(d ~ 0.5) cliff early; distributed qualitative tasks (d ~ 0.1) cliff late.
- Implemented: `estimate_task_theta()`, `validate_task_theta()` in cliff_prediction.py
- Validated: C1-a θ_info=0.967 > MHR θ_info=0.484 > HotpotQA θ_info=0.373
- **θ_info ≠ θ_q** — see CONTEXT.md. Different quantities, different methods.
- Thesis-only positioning per Q11; not load-bearing for any external venue.

### Per-family θ_q validation (compounding-error model)
- `full_validation_per_family()` IS called (audit was wrong on this)
- Match rate: 33% strict per-family with CTR (4/12); 58% at 25% tolerance (7/12)
- Position in thesis: "first-order model with bootstrap-CI uncertainty band" per Q7 D — predicted-τ* band overlaid with empirical-τ* replaces audit-flagged broken predicted_vs_empirical figure
- Bootstrap-CI machinery is the active-sprint rigor lift (Task 3, ~2h)

## Compression Cache (added 2026-05-27)

Precomputed compression cache separates compression from evaluation:
- `src/m6/compressors/cache.py` — CompressionCache + CachedCompressor
- `src/m6/experiments/precompute_cache.py` — run once on GPU
- All runners accept `--cache <path>` to skip compression
- H1/H2, H3, frontier can run fully locally with cache

## Remaining Work (Thesis, ~1 week sprint per Q13)

Tracked as harness tasks 1–9 (see TaskList). Punch list:

1. **[DONE]** Reconcile CLAUDE.md and insights.txt with audit-confirmed status
2. **[PENDING]** Wire derive_theta + CTR into CAAC and rerun sweep (~7h GPU + 3h)
3. **[PENDING]** Compute bootstrap CI on θ_q and generate predicted-τ* band figure (~2h)
4. **[PENDING]** Audit hygiene cleanup — _find() fix, partial.csv deletion, frontier seed plumbing, STATUS_NONCANONICAL markers (~2h)
5. **[DONE]** Write Ch5 (compounding-error model + cliff + Corollary 1)
6. **[DONE]** Write Ch6 (H3 NOT SUPPORTED honestly — compress-first dominance)
7. **[DONE]** Write Ch7 (H4 unbiased + Corollary 2 + memory bus integration)
8. **[DONE]** Write Ch8 (Discussion + CAAC operating-point demonstration + limitations + future work)
9. **[IN PROGRESS]** Final polish, reproducibility check, submit

### Manuscript status (2026-05-30)

First full draft compiled in `thesis_latex/` from the Oulu ITEE
template (`dithesis.cls`). Output: 72 pages A4, ~950 KB, copied
to `thesis.pdf` in the project root. Manuscript title per ADR-009
is *Distributed Memory Bus for Multi-Fragment LLM Workflows:
Context Compression, the Coordination Cliff, and Privacy*; the
codebase project name remains *Multi-Agent Coordination* (this
file's header) for back-compat with existing artefacts.

All verdict-table numbers refreshed against the canonical results
JSON on disk (`h1_h2_v2`, `h4_unbiased`, `h5_final`, `h3_final`,
`frontier_qwen72b`, `frontier_deepseekv4`, `hotpotqa_sweep`).
See insights.txt §65 for the per-chapter status, per-table
number-refresh notes, and the outstanding user-side items
(Finnish translation review, region-plot regeneration for
`caac_pareto`, predicted-τ* band figure for
`predicted_vs_empirical`).

## NeurIPS / ICLR — DEFERRED per Q13 (thesis-only scope)

NeurIPS 2026 main, NeurIPS 2026 D&B, NeurIPS workshop, and ICLR 2027 are
all skipped for this sprint. The codebase retains CAAC, the frontier
runners, theta-validation machinery, and the compounding-error model
implementation; the original `neurIPS.md` is preserved unedited as a
future-work bookmark.

Reasons:
- Audit revealed sufficient fragility (CTR rerun + bootstrap CI + proof
  writing all required) that the May 2026 NeurIPS deadline was hostile
  even if open.
- Thesis (~1 week) is the only deliverable; ICLR 2027 path can be
  revived later via the ADR-006/007/008 bookmarks.
- See ADR-008 "Revisit when" condition.

Items intentionally NOT done in this sprint:
- Theorem 1 formal LaTeX proof (downgraded to model derivation, ADR-008)
- GPT-4o-mini frontier spot check (declined, Q9)
- Selective Context as 4th compressor (Q9 declined; thesis has 4 incl. truncation)
- HotpotQA was claimed open; audit-stale — DONE since 2026-05-28
- CAAC theta/N sensitivity ablations — DONE (§54 in insights, informative null)
