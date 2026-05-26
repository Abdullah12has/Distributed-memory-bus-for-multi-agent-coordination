# Thesis Knowledge Map: What You Have, What's New, What to Read, What Remains

## Context

You're about to write your M6 thesis and want a clear picture of:
1. What the NeurIPS upgrade plan added beyond the original thesis
2. What plan-v3 covers and its implementation status
3. What you need to know before writing
4. What papers to read

This is a **knowledge document**, not a code change plan.

---

## Part 1: What NeurIPS Added (Beyond the Original Thesis)

The NeurIPS plan (`neurIPS.md`) transforms the thesis from "we measured something interesting" into **theory + method + experiments**. Three new contributions were added:

### 1A. Formal Theory — Coordination Cliff Theorem
- **File**: `src/m6/theory/cliff_prediction.py` (325 lines)
- **What**: Theorem 1 proves P(success | r) <= p0 * q(r)^N, predicting WHERE the cliff occurs
- **Key insight**: cliff position depends on compressor + task complexity, NOT model size
- **Functions**: `predicted_tau()`, `q_required()`, `derive_theta()`, `validate_prediction()`
- **Status**: CODE COMPLETE. LaTeX proof (`paper/sections/theorem.tex`) NOT YET WRITTEN.

### 1B. CAAC Algorithm — Cliff-Aware Adaptive Compression
- **File**: `src/m6/compressors/caac.py` (250 lines)
- **What**: Wrapper that dynamically backs off per-fragment to stay above the cliff
- **How**: Compresses at target ratio → measures token_recall → if below theta, binary-search for safe ratio
- **Hyperparams**: theta=0.5, min_ratio=1.5, n_compression_passes=1
- **Status**: CODE COMPLETE. Experiment runner `run_caac.py` COMPLETE. GPU run PENDING (in production queue).

### 1C. Broader Validation
- **Frontier validation** (`run_frontier.py`, 424 lines): GPT-4o-mini cliff sweep via OpenAI API
  - Status: CODE COMPLETE. Needs API key + ~$20. NOT YET RUN.
- **Figure generation** (`src/m6/figures/generate.py`, 475 lines): 6 publication figures
  - Status: CODE COMPLETE. Needs experiment results to generate.

### What NeurIPS adds that the thesis alone doesn't need:
- The formal theorem (thesis could just report empirical cliff)
- CAAC algorithm (thesis could just report fixed-ratio results)
- Frontier model validation (thesis can rely on local models)
- 9-page paper format (thesis is full-length)

**But**: all three strengthen the thesis significantly. The theorem gives you a "why", CAAC gives you a "so what", and frontier validation pre-empts the "only small models" criticism.

---

## Part 2: Plan-v3 Status — What's Implemented

### Core Infrastructure (ALL COMPLETE)
| Component | File(s) | Status |
|-----------|---------|--------|
| C1 Benchmark (150 instances, 3 families) | `data/processed/c1-v0.1/` | DONE |
| LLMLingua-2 compressor | `src/m6/compressors/lingua2.py` | DONE |
| Phi-3-Mini extractive | `src/m6/compressors/phi3_extractive.py` | DONE |
| Instruction-aware filter | `src/m6/compressors/filter.py` | DONE |
| Identity (control) | `src/m6/compressors/__init__.py` | DONE |
| Truncation baseline | `src/m6/compressors/truncation.py` | DONE |
| CAAC wrapper | `src/m6/compressors/caac.py` | DONE |
| Memory bus (FastAPI+SQLite+FAISS) | `src/m6/memory_bus/` | DONE |
| Orchestrator (deterministic + AutoGen) | `src/m6/agents/orchestrator.py` | DONE |
| Coordination metrics | `src/m6/evaluation/metrics/coordination.py` | DONE |

### Experiment Runners (ALL COMPLETE)
| Runner | File | Status |
|--------|------|--------|
| H1/H2 sweep | `run_h1_h2.py` | DONE |
| H3 RAG pipeline | `run_h3.py` | DONE |
| H4 disclosure | `run_h4.py` | DONE |
| H5 model scaling | `run_h5.py` | DONE |
| H6 MultiHopRAG | `run_h6.py` | DONE |
| CAAC experiment | `run_caac.py` | DONE |
| Frontier validation | `run_frontier.py` | DONE |

### Production Runs (IN PROGRESS)
| Experiment | Results Dir | Status |
|------------|-------------|--------|
| H1/H2 final (19,500 rows) | `results/h1_h2_final/` | DONE |
| H3 final (900 rows) | `results/h3_final/` | DONE |
| H4 final (756 rows) | `results/h4_final/` | DONE |
| H5 final (9,000 rows) | `results/h5_final/` | IN PROGRESS (~78%) |
| H6 final | `results/h6_final/` | QUEUED (after H5) |
| CAAC final | `results/caac_final/` | QUEUED (after H6) |
| Frontier (GPT-4o-mini) | — | NOT STARTED (needs API key) |

### Hypothesis Verdicts (Current)
| H | Verdict | Key Numbers |
|---|---------|-------------|
| H1 | **SUPPORTED** | All 3 compressors rho < 0.6, CIs exclude 0.6 |
| H2 | **SUPPORTED** | 8/9 cells significant, logistic tau ~2.5x |
| H3 | **NOT SUPPORTED** | P1 > P2 both regimes, no sign-flip. P3 dominates. |
| H4 | **SUPPORTED** | lingua2 -50pp, filter -43.7pp, phi3 -19.4pp |
| H5 | **NOT SUPPORTED** | Cliff position model-invariant (interesting finding) |
| H6 | **PENDING** | Code ready, GPU run queued |

---

## Part 3: What You Need to Know Before Writing

### 3A. Critical Design Truths (Honesty Points)

These MUST be correctly framed in the thesis:

1. **Single-pass compression (N=1)**: Fragments compressed ONCE before solver reads them. The theorem uses N=1. The q^N formula supports multi-pass but experiments only do single-pass.

2. **No actual multi-agent coordination in experiments**: The deterministic solver is a regex parser. The H5 planner is a single LLM call. Frame as "task solvability under compression," not multi-round agent communication. The AutoGen backend EXISTS but wasn't used for production.

3. **Family-b is unsolvable by LLMs ≤8B**: Small models can't do constraint-satisfaction planning even without compression. Near-zero baseline means compression effects can't be measured. This is a genuine capability gap (insight #33).

4. **Phi-3 compression ceiling ~2.5x**: phi3-extractive can't actually compress beyond ~2.5x regardless of target. Results above 3x target are duplicates of ~2.5x behavior. Report by ACHIEVED ratio, not target (insight #31).

5. **The "2x cliff"**: The biggest coord_success drop is consistently between 1.0x and 2.0x. Logistic tau of 2.5x confirms this. Even modest compression destroys coordination-critical structure.

### 3B. Chapter Mapping

| Chapter | Content | Hypotheses | Key Figures |
|---------|---------|------------|-------------|
| Ch1-2 | Intro + Related Work | — | Architecture diagram |
| Ch3 | System Design (memory bus) | — | System architecture |
| Ch4 | C1 Benchmark | — | Family examples |
| **Ch5** | Compression Effects on Coordination | H1 + H2 + H5 | Cliff curve, decorrelation scatter, model overlay |
| **Ch6** | RAG Pipeline Placement & Cost | H3 | Pipeline comparison bars |
| **Ch7** | Inference Disclosure & Transfer | H4 + H6 | Disclosure bar chart, transfer curve |
| Ch8 | Discussion + Limitations | — | — |

### 3C. Terminology to Use Consistently

| Wrong | Right | Why |
|-------|-------|-----|
| "QA accuracy" | "information preservation" / "qa_f1" | It's token-level F1, not answer accuracy |
| "inference disclosure" | "protected-fact recovery rate" | Not differential privacy |
| "multi-agent coordination rounds" | "task solvability under compression" | Experiments are single-pass |
| "H3 falsifies LongLLMLingua" | "compress-first preserves content quality" | Don't overclaim |
| "H5 failed" | "cliff position is model-invariant" | Frame as discovery |

### 3D. Thesis-Text Actions (No Code Needed)

From the deep review (2026-05-25), these need addressing in writing only:
- Rename H1 to "information preservation vs coordination"
- Reframe H3 narrative around compress-first advantage
- Acknowledge H5 Phi-3 confound (0% at ratio=1.0 for some families)
- Note H3 cost model uses target ratio, not achieved
- Explicitly state experiments measure task solvability, not multi-agent communication
- Family-A limitation: all 50 workloads are "sum 8 numbers"
- Family-B limitation: capacity inflation ensures feasibility for deterministic solver but LLMs can't handle it

---

## Part 4: Papers to Read Before Writing

### Tier 1: MUST-READ (Read These First, In This Order)

| # | Paper | Why | Time |
|---|-------|-----|------|
| 1 | **LLMLingua-2** (Pan et al., ACL 2024) | Your primary compressor. Understand the token-classification approach — your thesis measures what happens when it drops the wrong tokens. | 2h |
| 2 | **AutoGen** (Wu et al., ICLR 2024 Workshop) | Your orchestrator pattern. Understand planner-worker-critic conversation flow for the compounding-error model. | 2h |
| 3 | **RAG Original** (Lewis et al., NeurIPS 2020) | Pipeline foundation for H3. You need to explain why pipeline ordering matters. | 1.5h |
| 4 | **Lost in the Middle** (Liu et al., TACL 2024) | Explains why moderate compression can help (LLMs ignore middle context). Precedent for "surprising measurement" papers. | 1.5h |
| 5 | **LongLLMLingua** (Jiang et al., ACL 2024) | Your H3 foil. Your finding that P1 > P2 contradicts their retrieve-first design. | 1.5h |
| 6 | **Efron & Tibshirani Ch.16** (1993) | Your bootstrap p-value method. Must understand the recentered-null construction. | 1h |
| 7 | **Saleh et al. CSUR** (ACM 2025) | Your research group's survey. Positions your memory bus in broader context. | 1h |

### Tier 2: SHOULD-READ (Context and Comparisons)

| Paper | Why |
|-------|-----|
| **Generative Agents** (Park et al., UIST 2023) | Memory architecture lineage — your memory bus descends from this |
| **MemGPT** (Packer et al., 2023) | Closest context-management approach — they page, you compress |
| **RECOMP** (Xu et al., ICLR 2024) | Compare your phi3-extractive against their trained extractive |
| **Selective Context** (Li et al., EMNLP 2023) | Predecessor to LLMLingua, similar to your filter.py approach |
| **MetaGPT** (Hong et al., ICLR 2024) | Multi-agent with shared message pool — you fill the "what if compressed?" gap |
| **MultiHopRAG** (Tang & Yang, EMNLP 2024) | Your H6 benchmark — must understand scoring if you report H6 |
| **Holm** (1979) | Your multiple-comparison correction. Short paper, 6 pages. |

### Tier 3: NICE-TO-HAVE (Broadens Framing)

ICAE, Gist Tokens, CAMEL, Reflexion, RAPTOR, GraphRAG, Self-RAG, HippoRAG, HotpotQA, AgentBench, LongBench, RULER

### You Already Have

All 100 papers are downloaded with markdown summaries in `papers_neurips_iclr/` (10 categories). Full BibTeX in `thesis_latex/citations.bib`.

---

## Part 5: What Remains (Ordered by Priority)

### P0: Must Complete Before Submission

1. **Wait for production run to finish** (~5-6h remaining: H5 completion, H6, CAAC)
2. **Generate figures** from final results (`python -m m6.figures.generate`)
3. **Write Ch5** (H1+H2+H5: cliff existence, decorrelation, model-invariance)
4. **Write Ch6** (H3: RAG pipeline placement, compress-first advantage)
5. **Write Ch7** (H4+H6: disclosure reduction, transfer validation)
6. **Write Ch8** (Discussion, limitations, future work — honest framing)
7. **Read Tier 1 papers** (10.5h total reading)

### P1: Strongly Recommended

8. **Run frontier validation** (GPT-4o-mini, ~$20, needs OPENAI_API_KEY)
9. **Write NeurIPS paper draft** (9 pages, reuses thesis content)
10. **Read Tier 2 papers** (~7h reading)
11. **CAAC ablations** (theta sensitivity, if time permits)

### P2: If Time Permits

12. HotpotQA cliff sweep
13. Selective Context as 4th compressor
14. GPT-4o spot check
15. Docker reproducibility package

---

## Verification

This plan is read-only knowledge — no code changes needed. To verify current state:
- Check production run: `ssh gpu "tail -20 ~/production_run.log"`
- Check completed results: `ssh gpu "ls results/*_final/"`
- Generate figures once runs complete: `python -m m6.figures.generate`
