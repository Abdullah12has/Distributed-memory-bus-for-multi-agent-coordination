# MASTER THESIS M6

# Distributed Memory Bus for Multi-Agent Campus Systems

*Context Compression, Coordination Quality, and Policy-Aware Sharing*

**Implementation Plan**

**Syed Abdullah Hassan**
University of Oulu, Faculty of ITEE, CSE Research Unit
Future Computing Group

Academic supervisor: Lauri Loven
Industry: TalentAdore (Asim Nadeem, Oskari Valkama)

*May 2026*

---

## 1. Thesis Statement

This thesis designs, implements, and evaluates a distributed memory bus with a context-compression layer for multi-agent institutional systems. It contributes (i) a multi-agent coordination benchmark, (ii) an empirical characterisation of how context compression affects multi-agent coordination quality at 7B with a secondary 13B sanity arm, (iii) a catalogue of three RAG + compression pipeline architectures evaluated under matched conditions, and (iv) a tag-preserving compressor variant integrated with a reference memory-bus implementation.

The work is grounded in two motivations: (a) FCG objectives O4 (agentic memory), O5 (multi-agent coordination), and O9 (semantic interconnect); and (b) TalentAdore's industry need for cost-aware context management at production scale, where token costs dominate operating expenses.

**The deliverable is the thesis manuscript and the reference implementation.** All effort is directed at producing a defensible thesis on time.

**Compute envelope.** All training and evaluation runs on a single M4 Pro 48 GB workstation with MLX, llama.cpp, and Ollama. Fine-tuning is 7B-primary. The primary evaluation is at 7B with a secondary 13B inference arm for the coordination-cliff sanity check. This is the only compute available and the plan is designed around it.

**Out of scope.** Production-grade governance enforcement (the tag-preserving compressor is a research prototype with measured properties, not a compliance tool); cross-tokenizer or cross-model-family compressed exchange; a live production deployment on the FCG platform (the integration interface is delivered as a reference implementation that the FCG team can adopt).

---

## 2. Four Contributions

### 2.1 C1 -- A multi-agent coordination benchmark for context compression

A reproducible synthetic benchmark inspired by Vignette 7 (period-end reporting across eight university systems): a planner agent, N worker agents, and a critic, exchanging compressed state through a shared scratchpad. Configurable workload difficulty, agent count, source-document characteristics, and tag distributions. Coordination-quality metrics that go beyond per-turn correctness: planner-replan count, sub-task-assignment accuracy, rounds-to-completion, and critic-flagged error rate. Released alongside the thesis with documentation and seed configurations.

### 2.2 C2 -- Empirical characterisation of compression effects on multi-agent coordination

Three established compressors evaluated on C1 across compression ratios 1x-16x at 7B (with a secondary 13B sanity arm): LLMLingua-2 (hard-prompt baseline, no training), an instruction-aware filtering variant (heuristic, no training), and an ICAE-style soft-prompt compressor that is the trainable arm.

**ICAE-style training spec.** The soft-prompt compressor is fine-tuned with a joint dual-objective loss following Ge et al. 2024 (ICAE) and Chevalier et al. 2023 (AutoCompressor): **L = L_reconstruction + lambda * L_contrastive**. The reconstruction term is the standard token-level language-modelling loss over the source fragment given the compressed memory slots (encoder LoRA-adapted Llama-3.1-8B-Instruct, frozen decoder). The contrastive term is an InfoNCE loss over (positive, negative) source-fragment pairs sampled from the institutional corpus.

The central finding is the existence and shape of a "coordination cliff": a compression-ratio threshold tau* beyond which coordination success degrades sharply, even when single-agent QA accuracy degrades smoothly. Central correlation analysis: how well does single-agent QA accuracy predict multi-agent coordination success? A secondary 13B arm checks whether tau* shifts with model size.

### 2.3 C3 -- Joint RAG + compression pipeline catalogue

Three pipeline architectures implemented end-to-end on FAISS + LlamaIndex: P1 (compress-then-retrieve), P2 (retrieve-then-compress, the "classical" LongLLMLingua setup), and P3 (joint, conditional compression based on retrieval relevance scores). Each pipeline benchmarked under matched retrieval quality. Cost model in EUR/query under TalentAdore's actual production pricing for GPT-4o-mini and Claude Haiku 4.5, plus amortised local inference cost on M4 Pro.

### 2.4 C4 -- Tag-preserving compressor variant and reference memory-bus integration

Modification of the ICAE-style compressor that adds a per-slot tag-prediction head emitting an inherited per-fragment provenance/ACL vector. Evaluated on (i) tag-preservation rate at ratios 2x, 4x, 8x; (ii) accuracy delta vs. the unmodified version on C1.

Delivered with a reference memory-bus integration that exposes the read/write/subscribe API, policy-enforcement middleware, and audit-log format.

The four contributions form a sequence: build the testbed (C1), use it to make a measurement the field has not made (C2), embed compression into the RAG pipelines institutional agents actually use (C3), then probe what happens when compression carries metadata and package the result as integration-ready infrastructure (C4). Each contribution maps to a thesis chapter (Ch 4, Ch 5, Ch 6, Ch 7 respectively).

---

## 3. Four Hypotheses

Each hypothesis is grounded in a specific measurable comparison with an explicit falsifiable claim. All four are thesis hypotheses; falsification of any of them is itself a thesis-worthy result and is reported as such in the relevant chapter.

| ID | Hypothesis | Falsifiable claim / effect size |
|----|------------|---------------------------------|
| H1 | Single-agent QA accuracy under compression is a poor predictor of multi-agent coordination success. | Spearman rho between single-agent QA accuracy delta and multi-agent coordination success delta across matched compression ratios is below 0.6 on at least two of the three compressors at 7B. |
| H2 | A coordination cliff tau* exists and is task-dependent. | For each (compressor, workload) cell at 7B, there is a compression ratio tau* such that coordination success at ratios > tau* falls by >=30% relative to ratios < tau*. tau* varies by workload but not by compressor family, within +/-20%. A secondary 13B arm checks whether tau* shifts with model size. |
| H3 | RAG pipeline placement matters: P1 (compress-then-retrieve) and P2 (retrieve-then-compress) dominate in different regimes. | P1 dominates P2 on storage-bounded settings (FAISS index size capped); P2 dominates P1 on accuracy-bounded settings (retrieval recall capped). P3 (joint) closes the gap on a combined accuracy x EUR score. Effect size >= 5pp F1. |
| H4 | Tag-preservation head preserves provenance tags at rate >=85% at 4x compression with accuracy degradation <=5pp. | Specific numbers are the falsification targets. If preservation drops to 60% or accuracy by 15pp, the hypothesis is falsified and that itself is reported as a chapter finding. |

Narrative arc: (H1) standard metrics are incomplete -> (H2) coordination cliff exists -> (H3) RAG pipeline placement matters -> (H4) governance metadata can ride along compression.

**Chapter mapping.** H1, H2 -> Chapter 5 (baseline characterisation). H3 -> Chapter 6 (RAG pipelines). H4 -> Chapter 7 (tag-preserving extension).

---

## 4. Implementation Plan (10 Months)

### 4.1 Phase 1 -- Foundation (Months 0-1)

#### Month 0 (Weeks 1-2) -- Onboarding

- **Read (must-read tier):** Onboarding doc; AI Service Markets Trilogy Papers 1-2; FCG architecture documents; MemIndex (Saleh 2025, ACM TAAS); Wang et al. In-Context Former (EMNLP 2024); Fei et al. semantic compression (ACL 2024); Rae et al. Compressive Transformers (2019); Guo et al. dynamic context compression for RAG (2025); Haseeb 2025 Context Engineering for Multi-Agent LLM Code Assistants; Yu et al. MemAgent.
- **Should-read tier:** Paper 3; Saleh et al. message brokers survey (ACM CSUR 2025); Campus use case Vignette 7; Financial analysis.
- **Stack:** Python 3.11, MLX for training and 7B/13B inference (Apple Silicon native), llama.cpp + GGUF for quantised inference, Ollama for developer-experience inference, HF Transformers + PEFT (LoRA) for fine-tuning workflows, FAISS-CPU, LlamaIndex, AutoGen for agent runtime, SQLite for audit log, FastAPI for the reference memory-bus interface.
- **Repo:** single GitHub repo `m6-thesis` with subdirectories `benchmark/`, `compressors/`, `pipelines/`, `memory-bus/`, `experiments/`, `thesis/`.
- **Meetings:** weekly with Lauri (30 min), weekly with TalentAdore (Asim/Oskari, 30 min).
- **Scope sign-off with Lauri (60 min, before any code is written).** Confirm in writing (filed at `docs/scope-signoff.md`): (a) the FCG-integration deliverable is a reference implementation; (b) the synthetic Vignette-7 benchmark carries the thesis evaluation.

#### Month 1 (Weeks 3-4) -- Literature review and baselines

- Write the related-work chapter (Chapter 3) draft, ~20 pages.
- Reproduce three baseline compressors on M4 Pro with Llama-3.1-8B-Instruct: LLMLingua-2 (XLM-RoBERTa based, runs on MPS), ICAE (port CUDA dependencies if needed; time-box porting to 2 weeks), and a simple instruction-aware filter. Targets: NarrativeQA F1 within 2pp of reported numbers, HotpotQA F1 within 3pp.
- Validate the ICAE-style dual-objective training pipeline end-to-end on a tiny synthetic corpus (<=1K samples, 100 steps).
- Stand up the no-compression scaffold: a single-process Python harness running AutoGen-based planner-worker-critic loop with SQLite-logged state, FastAPI exposed for the integration story.
- **Deliverable:** `baselines-reproduced.csv`; Chapter 3 (related work) draft; integration-API skeleton; `scope-signoff.md` filed.

### 4.2 Phase 2 -- Benchmark and Baseline Measurement (Months 2-3)

#### Month 2 -- Build C1

- Synthetic workload generator with configurable parameters: source documents (10-200), agents (3-8), sub-task complexity (1-4 levels), tag distribution (uniform, skewed, hierarchical), source-document length (500-5000 tokens).
- Three workload families: (a) cross-document fact aggregation (Vignette-7-style); (b) constraint-satisfaction planning; (c) multi-step retrieval. ~50 instances per family, 150 total.
- Coordination-quality metrics implemented as scoring functions over trace logs: final task success, sub-task-assignment accuracy, rounds-to-completion, critic-flagged error rate.
- Tag generation: synthetic ACL bitmasks (uint64) and classification levels (5 tiers) attached to source fragments.
- Begin Chapter 4 (benchmark) draft.
- **Deliverable:** C1 benchmark v0.1; Chapter 4 outline + design rationale section drafted.

#### Month 3 -- Baseline characterisation (H1, H2) and ICAE training

- Run all three baseline compressors at ratios {1, 2, 4, 8, 16} on C1 with 5 seeds per cell. 7B-primary, 13B on subsample for H2 sanity.
- **ICAE-style trainable compressor produced this month.** Train with L = L_reconstruction + lambda * L_contrastive. LoRA via MLX, rank 16, batch 4, gradient accumulation 8. Lambda swept in {0.1, 0.3, 1.0} on validation. Wallclock target: <=3 days on M4 Pro.
- Compute coordination metrics and matched single-agent QA metrics. Test H1.
- Search for tau* in each (compressor, workload) cell using piecewise-linear cliff fitting. Test H2.
- **Deliverable:** `coordination-baselines-7b.csv` + `coordination-baselines-13b.csv`; ICAE-style compressor checkpoint; preliminary plots for Chapter 5.

### 4.3 Phase 3 -- RAG Pipelines and Mid-Thesis Consolidation (Months 4-5)

#### Month 4 -- RAG pipelines (H3)

- C3 implementation: P1, P2, P3 built on FAISS + LlamaIndex. P3 uses LlamaIndex's post-processor hooks with a relevance-score-conditional router. All three integrated with the C1 workload families.
- Benchmark P1/P2/P3 on C1 family (a) and on NarrativeQA/HotpotQA for external comparability. Storage-bounded and accuracy-bounded settings configured explicitly.
- Cost model fitted to TalentAdore production pricing for GPT-4o-mini / Claude Haiku 4.5, plus amortised M4 Pro inference cost. EUR/workflow is the headline cost metric.
- Test H3 with the P1/P2/P3 results.
- **Deliverable:** `rag-pipeline-results.csv`.

#### Month 5 -- Mid-thesis consolidation and review

- Consolidate Months 2-4 results into thesis chapter drafts: Chapter 4 (benchmark, full draft), Chapter 5 (baseline characterisation, including H1/H2 results), Chapter 6 (RAG pipelines, including H3 results).
- **Mid-thesis review with Lauri (formal, ~90 min).** Present chapter drafts and the headline figures. Goal: lock the empirical story for the first half of the thesis.
- Address Lauri's mid-thesis feedback.
- Tighten the C1 benchmark release: model card, dataset card, reproducibility script polished.
- **Deliverable:** Chapters 3-6 in reviewable draft state; mid-thesis review meeting completed; C1 benchmark v1.0 release-ready.

### 4.4 Phase 4 -- Tag-Preserving Extension (Months 6-7)

#### Month 6 -- Build C4 (H4)

- Add per-slot tag-prediction head to the ICAE-style compressor. Joint reconstruction + contrastive + tag-prediction loss with tunable weights.
- Sweep tag-loss weight to find the configuration that meets H4 (>=85% preservation at 4x). LoRA via MLX; if memory tight, use rank-8 at 7B.
- Test H4.
- Document the integration interface: FastAPI service exposing `write(fragment, tags) -> slot_id`, `read(slot_id, requester_acl) -> compressed_or_403`, `subscribe(query, ttl)`, `audit(slot_id) -> provenance_chain`.
- Begin Chapter 7 (tag-preserving extension) draft.
- **Deliverable:** tag-preserving compressor checkpoint; integration-API documentation; Chapter 7 outline.

#### Month 7 -- Chapter drafting and consolidation

- Draft Chapter 7 (tag-preserving extension, complete).
- Consolidate all chapters (5-7) with headline figures.
- **Deliverable:** Chapters 5-7 in reviewable draft state.

### 4.5 Phase 5 -- Stretch Goals (Month 8)

Pick at most TWO based on Lauri's input at end of Month 7. Each is included in the thesis as a chapter section.

- **S1 -- Calibration study.** Fit piecewise-linear cliff on <=100 instances; predict tau* on held-out workflows with MAE <= 1.5x ratio units. Adds a practical-deployability section to Chapter 5.
- **S2 -- Adversarial robustness ablation.** SecurityLingua-style red-team prompts targeting the compressor; measure tag-preservation under attack. Anchors the C4 governance claims in Chapter 7.
- **S3 -- Haseeb 2025 baseline comparison.** Implement the multi-agent context-engineering approach from Haseeb 2025 on C1; compare against C2 compressors. Strengthens Chapter 5.
- **S4 -- TalentAdore production trace replication.** With Asim/Oskari, run C1 evaluation on an NDA-cleared TalentAdore production trace. Strengthens the industry-relevance arm in Chapter 6.

### 4.6 Phase 6 -- Thesis Writing (Months 9-10)

- **Month 9 -- draft consolidation.** Chapters 1-7 to Lauri Week 1, Discussion chapter Week 3. Re-run headline figures with 5 fresh seeds; report mean and bootstrap CI. Discussion chapter drafted with explicit framing of contributions and limitations.
- **Month 10 -- final revision and submission.** Incorporate Lauri's and TalentAdore's comments. No new experiments. Reproducibility package: Docker compose for the memory bus + benchmark, GitHub release tag for everything, model cards, data cards, README with one-command reproduction of every headline figure. Submit thesis.

---

## 5. Evaluation Strategy

### 5.1 Benchmark suite

| Use | Benchmark | Why |
|-----|-----------|-----|
| Compressor calibration / sanity | NarrativeQA, HotpotQA | Compressors must hit reported numbers +/-2-3pp |
| QA vs. coordination correlation (H1) | C1 + matched single-agent QA derived from same sources | Matched tasks make the correlation meaningful |
| Coordination cliff tau* (H2) | C1 | The benchmark is the contribution |
| RAG pipeline placement (H3) | C1 family (a) + NarrativeQA + HotpotQA | C1 for multi-agent; standard for external comparability |
| Tag preservation (H4) | C1 with synthetic tags | Real ACL data not available |

### 5.2 Metrics

- **Quality:** F1, EM, ROUGE-L, BERTScore on QA subtasks. LLM-as-judge (local Llama-3.1-8B via Ollama) with opt-in GPT-4o-mini cross-check on 10% sample.
- **Coordination:** final task success, sub-task-assignment accuracy, rounds-to-completion, critic-flagged error rate.
- **Compression:** input/output token ratio; total tokens per workflow.
- **Cost (EUR/workflow):** TalentAdore production prices for GPT-4o-mini / Claude Haiku 4.5; amortised M4 Pro inference cost.
- **Latency:** p50/p95 ms/query, separately for compression step and end-to-end.
- **Tag preservation:** fraction of compressed slots whose recovered tags match the union of source-fragment tags.

### 5.3 Statistical protocol

- 5 seeds per condition; bootstrap CI alongside means.
- Paired bootstrap for compressor-vs-compressor comparisons on matched instances.
- Mann-Whitney U for the cliff-detection (H2) test.
- Holm correction within each hypothesis family. Families: {H1, H2}, {H3}, {H4}.
- Effect sizes (Cliff's delta for ordinal, Cohen's d for continuous) alongside p-values.

### 5.4 Compute budget on M4 Pro 48 GB

| Experiment | Approach | Wallclock |
|------------|----------|-----------|
| NarrativeQA / HotpotQA baseline reproduction at 7B | MLX or PyTorch MPS | 1-2 days |
| C1 baseline at 7B: 3 compressors x 5 ratios x 5 seeds x 150 workflows | MLX inference; AutoGen orchestration | 5-10 days |
| ICAE-style compressor training, reconstruction + InfoNCE, 7B LoRA | MLX, rank 16 | <=3 days |
| H2 secondary arm: 13B fp16 on 30-workload subsample | MLX-LM | 3-5 days |
| Tag-preserving ICAE training (C4) | MLX, rank 16 | <=3 days |
| RAG pipeline benchmark (H3) | MLX inference + FAISS | 3 days |
| Tag preservation sweep (H4) | MLX inference | 1 day |

Total compute fits comfortably within a single workstation.

---

## 6. Technical Architecture

### 6.1 System view

Three-layer memory bus. The MSc delivers a single-machine reference implementation.

- **Storage layer.** SQLite for the audit log (append-only via trigger); in-memory dict for the active scratchpad; FAISS-CPU for compressed-slot retrieval.
- **Compression layer.** Pluggable Compressor interface: `compress(fragment, task_hint, tags) -> CompressedSlot`. CompressedSlot carries (a) the slot tensor or text summary, (b) the inherited tag vector, (c) a backpointer to audit-log entries. Three compressor variants ship: V1 dense-embedding (LLMLingua-2), V2 ICAE-style with dual-objective training, V3 instruction-aware filter. The tag-preserving variant (C4) is V2 with an added tag head.
- **Access layer.** FastAPI service exposing write, read, subscribe, audit. Policy-enforcement middleware checks the requester's ACL bitmask against the entry's bitmask on every read; logs every access.

### 6.2 Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Compressor training | MLX with PEFT (LoRA); PyTorch (MPS) fallback | MLX is native to Apple Silicon; MPS fallback covers ops MLX lacks |
| Inference (<=13B fp16) | Ollama or MLX-LM | Ollama for DX; MLX-LM for controllability |
| Agent runtime | AutoGen | Mature; clean scratchpad integration |
| Vector store | FAISS-CPU | M4 Pro CPU headroom is sufficient |
| RAG orchestration | LlamaIndex | Post-processor hooks needed for P3 |
| Audit log | SQLite | One file, ACID, zero ops overhead |
| Integration interface | FastAPI | Language-agnostic HTTP contract |
| Evaluation harness | Custom Python + RAGAS + DeepEval | Hallucination, faithfulness, custom coordination metrics |
| External-API arm (cost analysis) | GPT-4o-mini, Claude Haiku 4.5 | TalentAdore production prices |

---

## 7. Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| ICAE baseline has CUDA-only dependencies that don't port to MPS/MLX cleanly | High -- Month 1 slips | Medium-high | Have AutoCompressor or from-scratch soft-prompt variant ready as backup; time-box porting to 2 weeks |
| MLX lacks InfoNCE-friendly batch contrastive primitive for the dual-objective training | Medium -- Month 3 slips | Medium | Manual cosine-similarity InfoNCE in PyTorch (MPS); tested on tiny synthetic corpus in Month 1 |
| Coordination cliff tau* doesn't exist -- H2 falsified | Medium -- thesis story changes | Medium | Falsification is a thesis-worthy result; Chapter 5 reports the negative finding |
| Tag-preservation head training is unstable on MLX | Medium -- C4 weakens | Low-medium | Start with low tag-loss weight; synthetic-regression-only baseline as the floor |
| AutoGen runtime bugs confound coordination measurements | High -- invalidates results | Medium | No-compression-control condition in every experiment; pin AutoGen version |
| TalentAdore expects deliverables conflicting with the thesis | Medium | Low-medium | Pre-negotiate Month 0. Their primary interest is the cost-analysis arm (EUR/workflow) in C3 |
| Scope expansion after Month 0 | High | Medium | scope-signoff.md filed in Month 0 documents the agreed boundaries |
| Schedule slips push submission past the 10-month window | High | Medium | Mid-thesis review in Month 5 is the early warning. If two or more chapters are not reviewable by end of Month 5, drop stretch goals (Month 8) entirely |

---

## 8. Key References

### 8.1 Context compression and memory

- Jiang et al. LLMLingua. EMNLP 2023.
- Jiang et al. LongLLMLingua. ACL 2024.
- Pan et al. LLMLingua-2. ACL Findings 2024.
- Mu et al. Learning to Compress Prompts with Gist Tokens. NeurIPS 2023.
- Chevalier et al. AutoCompressor. EMNLP 2023.
- Ge et al. In-context Autoencoder (ICAE). ICLR 2024.
- Wang et al. In-Context Former (ICF). EMNLP 2024.
- Fei et al. Semantic compression. ACL 2024.
- Rae et al. Compressive Transformers. ICLR 2020.
- Guo et al. Dynamic context compression for RAG. 2025.
- Cheng et al. xRAG. arXiv 2405.13792, 2024.
- Li, Liu, Su, Collier. Prompt Compression for LLMs: A Survey. NAACL 2025.

### 8.2 Multi-agent systems, agentic memory, and context engineering

- Wu et al. AutoGen. 2023.
- Hong et al. MetaGPT. ICLR 2024.
- Li et al. CAMEL. 2023.
- Shinn et al. Reflexion. NeurIPS 2023.
- Packer et al. MemGPT / Letta. 2023.
- Xu et al. A-MEM. NeurIPS 2025.
- Chhikara et al. Mem0. arXiv 2504.19413, 2025.
- Rasmussen et al. Zep. arXiv 2501.13956, 2025.
- Zhang et al. AgentPrune. arXiv 2410.02506, 2024.
- Wang et al. AgentDropout. arXiv 2503.18891, 2025.
- Park et al. Collaborative Memory: Dynamic Access Control. arXiv 2505.18279, 2025.
- Ye et al. KVCOMM. NeurIPS 2025.
- Haseeb. Context Engineering for Multi-Agent LLM Code Assistants. arXiv 2508.08322, 2025.
- Yu et al. MemAgent. arXiv 2507.02259, 2025.
- Anthropic. How we built our multi-agent research system. June 2025.
- Rajasekaran, Dixon, Ryan, Hadfield et al. Effective context engineering for AI agents. Anthropic, 2025.
- Anthropic. Managing context on the Claude Developer Platform. October 2025.

### 8.3 RAG, long-context, and benchmarks

- Lewis et al. RAG. NeurIPS 2020.
- Sarthi et al. RAPTOR. ICLR 2024.
- Edge et al. GraphRAG. 2024.
- Gutierrez et al. HippoRAG / HippoRAG 2. NeurIPS 2024 / ICML 2025.
- Asai et al. Self-RAG. ICLR 2024.
- Hsieh et al. RULER. 2024.
- Bai et al. LongBench / LongBench v2. 2024-2025.
- Yen et al. HELMET. ICLR 2025.
- Liu et al. Lost in the Middle. TACL 2024.
- Mialon et al. GAIA. 2023.
- Liu et al. AgentBench. ICLR 2024.
- Anthropic. Contextual Retrieval. September 2024.

### 8.4 Privacy-aware retrieval

- Zhou et al. Privacy-Aware RAG. arXiv 2503.15548, 2025.
- Bassit & Boddeti. SecureRAG. 2025.
- Li et al. SecurityLingua. CoLM 2025.

### 8.5 FCG programme and internal references

- Paper 1 -- Real-Time AI Service Economy. Loven, IEEE TSC.
- Saleh et al. MemIndex: Agentic Event-based Distributed Memory Management. ACM TAAS, 2025.
- Saleh et al. Towards Message Brokers for Generative AI. ACM Computing Surveys, 2025.
- Campus use case (FCG internal): Vignette 7.
- Financial analysis (FCG internal).
- NIST AI Risk Management Framework 1.0. 2023.

---

*End of document.*
