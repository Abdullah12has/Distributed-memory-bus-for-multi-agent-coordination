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

## Compressors (all training-free)

1. **LLMLingua-2** (`lingua2.py`) — token-level XLM-RoBERTa classifier
2. **Phi-3-Mini extractive** (`phi3_extractive.py`) — verbatim span selection via Ollama, with novel-token stripping + LLMLingua-2 fallback
3. **Instruction-aware filter** (`filter.py`) — TF-IDF + cross-encoder reranker
4. **Identity** (`__init__.py`) — no-compression control

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
- **Status: SUPPORTED**
  - Signal: +5pp (p=0.001) for all 3 compressors
  - Reduction: lingua2 -14.3pp (p=0.0001), phi3 -3.2pp (p=0.006), filter NS
  - Key insight: compression aggressiveness correlates with disclosure gap

### H5: Model-Size Scaling
- **Criterion**: tau* monotonic across 1.5B/3.8B/8B on >= 2/3 families, gap >= 1.5
- **Status: NOT SUPPORTED** (confirmed across 5 diagnostic configs, 2026-05-24)
  - Family-a: 8B cliff at 3x, all models cliff at same ratio. Gap negligible.
  - Family-c: gradual decline, no model-size dependence. Non-monotonic tau*.
  - Family-b: 0% everywhere due to agent/worker naming bug in scoring
  - 14B (Qwen2.5) tested: same cliff position as 8B, confirming cliff is compressor-driven
- Narrative: "model size affects ceiling, not cliff position" — more interesting than support

### H6: MultiHopRAG Transfer (Optional)
- **Criterion**: tau* within +/-15% of C1 family-a, coord_success within +/-10pp
- **Status: PENDING** — implementation ready, needs GPU run
- Runner: `python -m m6.experiments.run_h6 --synth-results results/h5_full`
- Data: 30 MultiHopRAG examples reformulated as C1 family-a workloads
- Wallclock: ~65 min on GPU

## Completed Experiment Runs (GPU Server)

| Run | Directory | Date | Status | Notes |
|-----|-----------|------|--------|-------|
| H3 full | `h3_full` | 2026-05-24 | Done | 900 rows, H3 not supported |
| H4 full | `h4_v2` | 2026-05-22 | Done | H4 supported, 3 compressors |
| H5 full | `h5_full` | 2026-05-24 | Done | 9000 rows, H5 not supported |
| H1/H2 full | `h1_h2_full` | 2026-05-21 | Done | phi3=lingua2 fallback bug |
| H1/H2 v2 | `h1_h2_v2` | 2026-05-24 | Done | intermediate fix attempt |
| H1/H2 rerun | `h1_h2_v3_quick2` | 2026-05-24 | Done | phi3 fix + qa_f1 fix confirmed. H1+H2 SUPPORTED |
| H3 quick | `quick_h3` | 2026-05-24 | Done | smoke test validation |
| H4 quick | `quick_h4` | 2026-05-24 | Done | smoke test validation |
| H5 quick | `quick_h5` | 2026-05-24 | Done | smoke test validation |
| H5 diagnostic | `h5_diagnostic` | 2026-05-24 | Done | 3 models x 3 families x 4 ratios x 2 seeds x 10 wl |
| H5 diag1 cliff | `h5_diag1_cliff` | 2026-05-24 | Done | Family-a, 8 ratios, cliff shape |
| H5 diag2 famc | `h5_diag2_famc` | 2026-05-24 | Done | Family-c, 8 ratios, non-monotonic investigation |
| H5 diag4 14B | `h5_diag4_14b` | 2026-05-24 | Done | 4 models incl 14B, family-a |
| H5 diag5 combined | `h5_diag5_combined` | 2026-05-24 | Done | A+C, 3 models, 6 ratios |

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

## Critical Framing Notes (from deep review, 2026-05-25)

### Theorem-Implementation Mismatch (FIXED)
The compounding-error model originally claimed N=3 rounds of compression (q^N),
but the code only compresses once (N=1). Fixed: theorem now uses N=1 by default,
q_min = theta directly. The q^N formulation is still available for multi-pass
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

### CAAC Constraints
- min_ratio changed from 1.0 to 1.5 — CAAC must achieve at least 1.5x compression
- theta changed from hardcoded 0.65 to empirically derivable via `derive_theta()`
- Default theta=0.5, default n_compression_passes=1

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

- **Ch5**: H1 + H2 + H5 (coordination cliff + scaling)
- **Ch6**: H3 (RAG pipelines + cost)
- **Ch7**: H4 + H6 (inference disclosure + memory bus + transfer validation)

## Remaining Work (Thesis)

- Full production runs with all fixes applied
- H6 MultiHopRAG transfer validation (implementation ready, needs GPU run ~65min)
- Thesis writing: Ch5, Ch6, Ch7 results sections
- Figures: cliff curves, model-size bar charts, pipeline comparison

## NeurIPS Upgrade Plan (see neurIPS.md for full details)

### Implementation Checklist (P0 — Must-Have)

- [ ] **THEORY**: Theorem 1 proof (coordination cliff bound) — `paper/sections/theorem.tex`
- [x] **THEORY**: `src/m6/theory/cliff_prediction.py` — predicted_tau() + comparison plot (DONE)
- [x] **ALGORITHM**: `src/m6/compressors/caac.py` — Cliff-Aware Adaptive Compression wrapper (DONE)
- [x] **ALGORITHM**: `src/m6/experiments/run_caac.py` — CAAC vs fixed-ratio experiments (DONE, smoke verified)
- [x] **EXPERIMENT**: `src/m6/experiments/run_frontier.py` — GPT-4o-mini cliff sweep via OpenAI (DONE, needs API key)
- [ ] **EXPERIMENT**: Run H6 MultiHopRAG on GPU (~65 min)
- [ ] **EXPERIMENT**: Run frontier validation (~$20 API cost)
- [ ] **EXPERIMENT**: Run CAAC vs baselines on C1 (~4h GPU)
- [ ] **EXPERIMENT**: Run full H1/H2 with 10 ratios + all fixes (~6h GPU)
- [x] **FIGURES**: `src/m6/figures/generate.py` — 6 figure generators (DONE, auto-discovers CSVs)
- [ ] **PAPER**: NeurIPS 9-page paper draft

### Implementation Checklist (P1 — Should-Have)

- [ ] HotpotQA cliff sweep (50 questions, ~2h GPU)
- [ ] CAAC ablation: theta sensitivity {0.5, 0.6, 0.7, 0.8}
- [ ] CAAC ablation: N sensitivity {1, 2, 3, 4, 5}
- [ ] Per-fragment backing-off analysis
- [ ] Selective Context as 4th compressor (~80 lines)
- [ ] GPT-4o spot check at ratios {1, 4} (~$15)
- [ ] Appendix with full result tables
- [ ] Docker compose for reproducibility
