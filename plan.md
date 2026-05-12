# MASTER THESIS M6

# Distributed Memory Bus for Multi-Agent Campus Systems

*Context Compression, Coordination Quality, and Policy-Aware Sharing*

**Implementation Plan**

**Syed Abdullah Hassan**
University of Oulu · Faculty of ITEE · CSE Research Unit
Future Computing Group

Academic supervisor: Lauri Lovén
Industry: TalentAdore (Asim Nadeem, Oskari Valkama)

*May 2026*

---

## 1. Thesis Statement

This thesis designs, implements, and evaluates a distributed memory bus with a context-compression layer for multi-agent institutional systems. It contributes (i) a multi-agent coordination benchmark, (ii) an empirical characterization of how context compression affects multi-agent coordination quality across model sizes 7B–70B, (iii) a catalogue of three RAG + compression pipeline architectures evaluated under matched conditions, and (iv) a tag-preserving compressor variant integrated with a reference memory-bus implementation that exposes the integration interfaces the FCG platform requires.

The work is grounded in three motivations: (a) FCG objectives O4 (agentic memory), O5 (multi-agent coordination), and O9 (semantic interconnect); (b) TalentAdore's industry need for cost-aware context management at production scale, where token costs dominate operating expenses; and (c) doctoral track D7 (Federated Knowledge Orchestration), for which this thesis provides the institutional-scale memory-bus substrate.

**The deliverable is the thesis manuscript and the reference implementation.** All effort is directed at producing a defensible thesis on time. External publications are not in scope and are not part of the work plan; if anything follows from the thesis, it does so after submission and is decided then.

**Compute envelope.** All training and evaluation runs on a single M4 Pro 48 GB workstation with MLX, llama.cpp, and Ollama. Inference scales to 70B at int4 quantization (slow but feasible); fine-tuning is 7B-primary with 13B at low LoRA rank as the upper limit. This is the only compute available and the plan is designed around it — there are no contingent paths on external clusters. The 70B evaluation arm is delivered as a single-point characterization at the suspected coordination cliff identified at 13B/34B, not a full ratio sweep, because that is what M4 Pro wallclock realistically supports.

**Out of scope.** Production-grade governance enforcement (the tag-preserving compressor is a research prototype with measured properties, not a compliance tool); cross-tokenizer or cross-model-family compressed exchange; a live production deployment on the FCG platform (the integration interface is delivered as a reference implementation that the FCG team can adopt). These are explicitly doctoral-phase work.

---

## 2. Four Contributions

The contributions correspond to the four research questions in the accepted proposal and form the chapter sequence of the thesis.

### 2.1 C1 — A multi-agent coordination benchmark for context compression

A reproducible synthetic benchmark inspired by Vignette 7 (period-end reporting across eight university systems): a planner agent, N worker agents, and a critic, exchanging compressed state through a shared scratchpad. Configurable workload difficulty, agent count, source-document characteristics, and tag distributions. Coordination-quality metrics that go beyond per-turn correctness: planner-replan count, sub-task-assignment accuracy, rounds-to-completion, critic-flagged error rate, and a summary-level inference disclosure metric for the policy story. Released alongside the thesis with documentation and seed configurations.

### 2.2 C2 — Empirical characterization of compression effects on multi-agent coordination at model-size scale

Three established compressors evaluated on C1 across compression ratios 1×–16× and model sizes {7B, 13B, 34B-int4, 70B-int4}: LLMLingua-2 (hard-prompt baseline, no training), an instruction-aware filtering variant (heuristic, no training), and an ICAE-style soft-prompt compressor that is the trainable arm.

**ICAE-style training spec.** The soft-prompt compressor is fine-tuned with a joint dual-objective loss following Ge et al. 2024 (ICAE) and Chevalier et al. 2023 (AutoCompressor): **L = L_reconstruction + λ · L_contrastive**. The reconstruction term is the standard token-level language-modelling loss over the source fragment given the compressed memory slots (encoder LoRA-adapted Llama-3.1-8B-Instruct, frozen decoder). The contrastive term is an InfoNCE loss over (positive, negative) source-fragment pairs sampled from the institutional corpus: positives are fragments from the same source document or planner-worker-critic dialogue trace; negatives are fragments from unrelated documents in the same batch. The contrastive weight λ is searched on a validation split.

The central finding is the existence and shape of a "coordination cliff": a compression-ratio threshold τ* beyond which coordination success degrades sharply, even when single-agent QA accuracy degrades smoothly. Central correlation analysis: how well does single-agent QA accuracy predict multi-agent coordination success? Model-size analysis: does τ* shift, sharpen, or disappear at larger scales? This is the headline empirical result of the thesis.

### 2.3 C3 — Joint RAG + compression pipeline catalogue

Three pipeline architectures implemented end-to-end on FAISS + LlamaIndex: P1 (compress→retrieve, pre-compress corpus then retrieve compressed chunks), P2 (retrieve→compress, retrieve full docs then post-retrieve compression — the "classical" LongLLMLingua setup), and P3 (joint, conditional compression based on retrieval relevance scores). Each pipeline benchmarked under matched retrieval quality. Cost model in €/query under TalentAdore's actual production pricing for GPT-4o-mini and Claude Haiku 4.5, plus amortised local inference cost on M4 Pro.

### 2.4 C4 — Tag-preserving compressor variant and reference memory-bus integration

Modification of the ICAE-style compressor that adds a per-slot tag-prediction head emitting an inherited per-fragment provenance/ACL vector. Evaluated on (i) tag-preservation rate at ratios 2×, 4×, 8×; (ii) accuracy delta vs. the unmodified version on C1; (iii) summary-level inference disclosure: when a held-out reader views compressed summaries with no quoted source text, can it reconstruct protected source content above chance?

Delivered with a reference memory-bus integration that exposes the read/write/subscribe API, policy-enforcement middleware, and audit-log format that the FCG platform team can adopt without rewriting the compression layer.

The four contributions form a sequence: build the testbed (C1), use it to make a measurement the field has not made and to characterise across model scale (C2), embed compression into the RAG pipelines institutional agents actually use (C3), then probe what happens when compression carries metadata and package the result as integration-ready infrastructure (C4). Each contribution maps to a thesis chapter (Ch 4, Ch 5, Ch 6, Ch 7 respectively).

---

## 3. Eight Hypotheses

Each hypothesis is grounded in a specific measurable comparison with an explicit falsifiable claim. All eight are thesis hypotheses; falsification of any of them is itself a thesis-worthy result and is reported as such in the relevant chapter.

| ID | Hypothesis | Falsifiable claim / effect size |
|----|------------|---------------------------------|
| H1 | Single-agent QA accuracy under compression is a poor predictor of multi-agent coordination success. | Spearman ρ between single-agent QA accuracy delta and multi-agent coordination success delta across matched compression ratios is below 0.6 on at least two of the three compressors at 7B. |
| H2 | A coordination cliff τ* exists and is task-dependent. | For each (compressor, workload) cell at 7B, there is a compression ratio τ* such that coordination success at ratios > τ* falls by ≥30% relative to ratios < τ*. τ* varies by workload but not by compressor family, within ±20%. |
| H3 | Training distribution matters: ICAE-style compressor fine-tuned on planner-worker-critic dialogue traces outperforms the same compressor fine-tuned on monolithic QA at matched single-agent QA accuracy. | Higher coordination success on C1 at matched single-agent QA. Small training set (~5K traces), same hyperparameters, same compute. |
| H4 | RAG pipeline placement matters: P1 (compress→retrieve) and P2 (retrieve→compress) dominate in different regimes. | P1 dominates P2 on storage-bounded settings (FAISS index size capped); P2 dominates P1 on accuracy-bounded settings (retrieval recall capped). P3 (joint) closes the gap on a combined accuracy×€ score. Effect size ≥ 5pp F1. |
| H5 | Tag-preservation head preserves provenance tags at rate ≥85% at 4× compression with accuracy degradation ≤5pp. | Specific numbers are the falsification targets. If preservation drops to 60% or accuracy by 15pp, the hypothesis is falsified and that itself is reported as a chapter finding. |
| H6 | Summary-level inference disclosure is measurable and the tag-preserving compressor reduces it. | A held-out reader (gpt-4o-mini) recovers protected facts from compressed summaries at rate substantially above the priors-only chance baseline when the tag-preserving compressor is NOT used (showing the metric measures something real), and at lower rate when it IS used at matched compression ratio. |
| H7 | The coordination cliff τ* shifts toward higher compression ratios as model size grows. | Measured across {7B, 13B, 34B-int4, 70B-int4}, τ* increases monotonically with model size on at least 2 of 3 workload families. 70B is single-point characterization at the suspected τ* identified at 13B/34B; 7B and 13B are full sweeps; 34B-int4 is a focused partial sweep. |
| H8 | Findings on synthetic Vignette-7 transfer to real M0/M1/M2 traces. | On a subset of multi-agent workflows reconstructed from real M0/M1/M2 traces, the qualitative shape of the coordination-vs-compression curve matches synthetic results within ±15% on τ* and ±10pp on coordination success. Gated on M0/M1/M2 readiness. |

Narrative arc: (H1) standard metrics are incomplete → (H2) coordination cliff exists → (H3) training distribution matters → (H4) RAG pipeline placement matters → (H5, H6) governance metadata can ride along and is measurable → (H7) the cliff scales with model size → (H8) the synthetic benchmark transfers to real deployment.

**Chapter mapping.** H1, H2 → Chapter 5 (baseline characterization). H3 → Chapter 5 ablation section. H4 → Chapter 6 (RAG pipelines). H5, H6 → Chapter 7 (tag-preserving extension). H7 → Chapter 8 (model-size scaling). H8 → Chapter 9 (real-trace transfer).

---

## 4. Implementation Plan (10 Months)

### 4.1 Phase 1 — Foundation (Months 0–1)

#### Month 0 (Weeks 1–2) — Onboarding

- **Read (must-read tier):** Onboarding doc; AI Service Markets Trilogy Papers 1–2; FCG architecture documents; MemIndex (Saleh 2025, ACM TAAS); Wang et al. In-Context Former (EMNLP 2024); Fei et al. semantic compression (ACL 2024); Rae et al. Compressive Transformers (2019); Guo et al. dynamic context compression for RAG (2025); Haseeb 2025 Context Engineering for Multi-Agent LLM Code Assistants; Yu et al. MemAgent.
- **Should-read tier:** Paper 3; Saleh et al. message brokers survey (ACM CSUR 2025); Campus use case Vignette 7; Financial analysis; Lovén 6G Continuum.
- **Stack:** Python 3.11, MLX for training and 7B/13B inference (Apple Silicon native), llama.cpp + GGUF for int4 inference at 34B/70B, Ollama for developer-experience inference, HF Transformers + PEFT (LoRA) for fine-tuning workflows, FAISS-CPU, LlamaIndex, AutoGen for agent runtime, SQLite for audit log, FastAPI for the reference memory-bus interface.
- **Repo:** single GitHub repo `m6-thesis` with subdirectories `benchmark/`, `compressors/`, `pipelines/`, `memory-bus/`, `experiments/`, `thesis/`.
- **Meetings:** weekly with Lauri (30 min), weekly with TalentAdore (Asim/Oskari, 30 min), bi-weekly with Faisal Khan (M1) and Vu Truong (M2) to track agent-readiness for the real-trace arm.
- **Scope sign-off with Lauri (60 min, before any code is written).** Confirm in writing (filed at `docs/scope-signoff.md`): (a) the FCG-integration deliverable is a reference implementation — a FastAPI service exposing the memory-bus API with documented contracts and a single-machine deployment, not a live production integration on the FCG agentic platform; (b) real M0/M1/M2 traces (H8) are evaluated as a parallel arm gated on M0/M1/M2 connector readiness, with the synthetic Vignette-7 benchmark carrying the thesis evaluation regardless. If Lauri pushes back on either, the scope conversation happens before coding starts, not at Month 7.

#### Month 1 (Weeks 3–4) — Literature review and baselines

- Write the related-work chapter (Chapter 3) draft, ~20 pages, covering compression, multi-agent memory, RAG, long-context benchmarks, privacy-aware retrieval, and the FCG / distributed-AI niche.
- Reproduce three baseline compressors on M4 Pro with Llama-3.1-8B-Instruct: LLMLingua-2 (XLM-RoBERTa based, runs on MPS), ICAE (port CUDA dependencies if needed; time-box porting to 2 weeks), and a simple instruction-aware filter. Targets: NarrativeQA F1 within 2pp of reported numbers, HotpotQA F1 within 3pp.
- Validate the ICAE-style dual-objective training pipeline (reconstruction + InfoNCE contrastive) end-to-end on a tiny synthetic corpus (≤1K samples, 100 steps). If MLX lacks an InfoNCE-friendly batch contrastive primitive, fall back to a manual cosine-similarity InfoNCE implementation in PyTorch (MPS). One-week time-box.
- Stand up the no-compression scaffold: a single-process Python harness running AutoGen-based planner-worker-critic loop with SQLite-logged state, FastAPI exposed for the future integration story.
- Curate the institutional corpus subset (no PII): publications from M0 (coordinate with Mohammad), redacted contract excerpts from M1 (coordinate with Faisal), Moodle/Patio materials from M2 (coordinate with Vu). Target ~50 MB.
- **Sanity check:** does the planner-worker-critic loop produce non-trivial coordination patterns at 7B? Run on a known simple coordination task. If nothing interesting happens at 7B, scope-down C1's difficulty before locking the design.
- **Deliverable:** `baselines-reproduced.csv`; Chapter 3 (related work) draft; integration-API skeleton; `scope-signoff.md` filed.

### 4.2 Phase 2 — Benchmark and Baseline Measurement (Months 2–3)

#### Month 2 — Build C1

- Synthetic workload generator with configurable parameters: source documents (10–200), agents (3–8), sub-task complexity (1–4 levels), tag distribution (uniform, skewed, hierarchical), source-document length (500–5000 tokens).
- Three workload families: (a) cross-document fact aggregation (Vignette-7-style); (b) constraint-satisfaction planning (assign sub-tasks under capacity constraints); (c) multi-step retrieval (chain queries across heterogeneous source families). ~50 instances per family, 150 total.
- Coordination-quality metrics implemented as scoring functions over AutoGen trace logs: final task success, sub-task-assignment accuracy, rounds-to-completion, critic-flagged error rate, summary-level inference disclosure proxy.
- Tag generation: synthetic ACL bitmasks (uint64) and classification levels (5 tiers) attached to source fragments. Distribution parameters configurable so H5–H6 can be tested at different governance-stringency levels.
- Begin Chapter 4 (benchmark) draft: design rationale, workload family definitions, metric definitions.
- **Deliverable:** C1 benchmark v0.1, reproducible from a single command; Chapter 4 outline + design rationale section drafted.

#### Month 3 — Baseline characterization (H1, H2) and ICAE training

- Run all three baseline compressors at ratios {1, 2, 4, 8, 16} on C1 with 5 seeds per cell. 7B-primary, 13B on subsample for H2 sanity.
- **ICAE-style trainable compressor produced this month.** Train with L = L_reconstruction + λ · L_contrastive (per §2.2). LoRA via MLX, rank 16, batch 4, gradient accumulation 8. λ swept in {0.1, 0.3, 1.0} on validation; ablation reported. Training corpus: institutional subset from Month 1 (~50 MB) plus a subsampled BookCorpus chunk for breadth. Wallclock target: ≤3 days on M4 Pro.
- Compute coordination metrics and matched single-agent QA metrics. Test H1.
- Search for τ* in each (compressor, workload) cell using piecewise-linear cliff fitting. Test H2.
- **Deliverable:** `coordination-baselines-7b.csv` + `coordination-baselines-13b.csv`; ICAE-style compressor checkpoint + model card; preliminary plots — the headline figure for thesis Chapter 5.

### 4.3 Phase 3 — RAG Pipelines and Mid-Thesis Consolidation (Months 4–5)

#### Month 4 — RAG pipelines (H4) and training-distribution experiment (H3)

- C3 implementation: P1, P2, P3 built on FAISS + LlamaIndex. P3 uses LlamaIndex's post-processor hooks with a relevance-score-conditional router. All three integrated with the C1 workload families.
- Benchmark P1/P2/P3 on C1 family (a) (cross-document fact aggregation) and on NarrativeQA/HotpotQA for external comparability. Storage-bounded and accuracy-bounded settings configured explicitly.
- Cost model fitted to TalentAdore production pricing for GPT-4o-mini / Claude Haiku 4.5, plus amortised M4 Pro inference cost (electricity + wallclock). €/workflow is the headline cost metric.
- Training-distribution experiment: construct ~5K planner-worker-critic dialogue traces (synthetic or scraped from AutoGen/MetaGPT demos). Fine-tune the ICAE-style compressor on (a) QA baseline and (b) multi-agent dialogue. Same hyperparameters, same dual-objective loss, same compute. Evaluate both on C1. Test H3.
- Test H4 with the P1/P2/P3 results.
- **Deliverable:** `rag-pipeline-results.csv`; `training-data-ablation.csv`.

#### Month 5 — Mid-thesis consolidation and review

- Consolidate Months 2–4 results into thesis chapter drafts: Chapter 4 (benchmark, full draft), Chapter 5 (baseline characterization, including H1/H2/H3 results), Chapter 6 (RAG pipelines, including H4 results).
- **Mid-thesis review with Lauri (formal, ~90 min).** Present chapter drafts and the headline figures. Goal: lock the empirical story for the first half of the thesis and surface any methodological concerns before Months 6–7.
- Address Lauri's mid-thesis feedback: re-run any ablations he requests, tighten figures, revise chapter prose.
- Revise Chapter 3 (related work) to reflect what was actually used and what 2026 papers appeared during Months 2–4.
- Tighten the C1 benchmark release: model card, dataset card, reproducibility script polished to a state where an external reader can run a single command and reproduce the Chapter 5 headline figure.
- **Deliverable:** Chapters 3–6 in reviewable draft state; mid-thesis review meeting completed; ablation reruns merged; C1 benchmark v1.0 release-ready.

### 4.4 Phase 4 — Tag-Preserving Extension and Scaling (Months 6–7)

#### Month 6 — Build C4 (H5, H6)

- Add per-slot tag-prediction head to the ICAE-style compressor. Joint reconstruction + contrastive + tag-prediction loss with tunable weights.
- Sweep tag-loss weight to find the configuration that meets H5 (≥85% preservation at 4×). LoRA via MLX; if memory tight, use rank-8 at 7B.
- Implement summary-level inference disclosure measurement: given compressed summaries without quoted source text, query gpt-4o-mini via API with structured prompts asking to recover protected facts. Compare disclosure rates between tag-preserving and baseline compressors. Test H5, H6.
- Document the integration interface: FastAPI service exposing `write(fragment, tags) → slot_id`, `read(slot_id, requester_acl) → compressed_or_403`, `subscribe(query, ttl)`, `audit(slot_id) → provenance_chain`.
- Begin Chapter 7 (tag-preserving extension) draft.
- **Deliverable:** tag-preserving compressor checkpoint + model card; `inference-disclosure-results.csv`; integration-API documentation; Chapter 7 outline.

#### Month 7 — Model-size scaling (H7) and real-trace arm (H8)

- **Model-size scaling:** repeat the H2 coordination-cliff experiments at {13B, 34B-int4, 70B-int4}. 13B fp16 is comfortable on M4 Pro. 34B int4 (~5–10 tok/s) supports a focused partial sweep around the suspected τ* identified at 13B. 70B int4 (~3–5 tok/s) supports a single-point characterization at the suspected τ* — explicitly methodologically disclosed in Chapter 8.
- Sanity-check 70B int4 on known-answer NarrativeQA samples before running C1 to confirm output quality. If degraded, document and exclude from headline claims.
- **Real-trace arm:** with Faisal and Vu, identify 2–3 multi-system workflows reconstructable from actual M0/M1/M2 traces. If agents aren't ready, this arm is documented as in-progress per `scope-signoff.md` and the synthetic benchmark carries the thesis evaluation. Test H8 on whatever subset is available.
- Draft Chapters 7 (tag-preserving extension, complete), 8 (model-size scaling), 9 (real-trace arm).
- **Deliverable:** `model-size-scaling.csv`; `real-trace-arm-status.md`; thesis Chapters 7–9 drafted.

### 4.5 Phase 5 — Stretch Goals (Month 8)

Pick at most TWO based on Lauri's input at end of Month 7. Each is included in the thesis as a chapter section, not as a separate publication.

- **S1 — Calibration study.** Fit piecewise-linear cliff on ≤100 instances; predict τ* on held-out workflows with MAE ≤ 1.5× ratio units. Adds a practical-deployability section to Chapter 8.
- **S2 — Adversarial robustness ablation.** SecurityLingua-style red-team prompts targeting the compressor; measure tag-preservation under attack. Anchors the C4 governance claims in Chapter 7.
- **S3 — Haseeb 2025 baseline comparison.** Implement the multi-agent context-engineering approach from Haseeb 2025 on C1; compare against C2 compressors. Strengthens Chapter 5.
- **S4 — TalentAdore production trace replication.** With Asim/Oskari, run C1 evaluation on an NDA-cleared TalentAdore production trace. Strengthens the industry-relevance arm in Chapter 6.
- **S5 — Compression × market mechanism.** Feed compression ratio into Paper 1's polymatroid simulation harness; report welfare under compression. Cleanest doctoral bridge to D3; appears as a discussion section in Chapter 10.

### 4.6 Phase 6 — Thesis Writing (Months 9–10)

- **Month 9 — draft consolidation.** Chapters 1–6 to Lauri Week 1, 7–10 Week 3. Re-run headline figures with 5 fresh seeds; report mean and bootstrap CI. Final benchmark sweep on contested cells. Discussion chapter (10) drafted with explicit framing of contributions, limitations, and the doctoral bridge to D7.
- **Month 10 — final revision and submission.** Incorporate Lauri's and TalentAdore's comments. No new experiments. Reproducibility package: Docker compose for the memory bus + benchmark, HuggingFace hub release for the tag-preserving compressor, GitHub release tag for everything, model cards, data cards, README with one-command reproduction of every headline figure. Submit thesis.

---

## 5. Evaluation Strategy

### 5.1 Benchmark suite

| Use | Benchmark | Why |
|-----|-----------|-----|
| Compressor calibration / sanity | NarrativeQA, HotpotQA | Compressors must hit reported numbers ±2–3pp |
| External long-context comparator | LongBench v2 (subsample) | Compressors not broken in standard settings |
| QA vs. coordination correlation (H1) | C1 + matched single-agent QA derived from same sources | Matched tasks make the correlation meaningful |
| Coordination cliff τ* (H2) | C1 | The benchmark is the contribution |
| Training-distribution (H3) | C1 | Same |
| RAG pipeline placement (H4) | C1 family (a) + NarrativeQA + HotpotQA | C1 for multi-agent; standard for external comparability |
| Tag preservation (H5) | C1 with synthetic tags | Real ACL data not available |
| Inference disclosure (H6) | C1 + held-out reader LLM | Tests metric has empirical content |
| Model-size scaling (H7) | C1 family (a), 4 model sizes | Compute-bounded; family (a) most discriminative |
| Real-trace transfer (H8) | M0/M1/M2 reconstructed workflows | Gated on connector readiness |
| Agent-task motivation | GAIA Level 1 | Motivates multi-agent framing |
| Agent-task external comparability | AgentBench (selected envs: OS, DB, LTP) | External comparability; not on critical path |

### 5.2 Metrics

- **Quality:** F1, EM, ROUGE-L, BERTScore on QA subtasks. LLM-as-judge (gpt-4o-mini) with Claude Sonnet 4.6 cross-check on 10% sample.
- **Fidelity:** hallucination rate via DeepEval and RAGAS; manual annotation on 100 random examples per condition.
- **Coordination:** final task success, sub-task-assignment accuracy, rounds-to-completion, critic-flagged error rate.
- **Compression:** input/output token ratio; total tokens per workflow.
- **Cost (€/workflow):** TalentAdore production prices for GPT-4o-mini / Claude Haiku 4.5; amortised M4 Pro inference cost (electricity + wallclock). Carries the TalentAdore industry-relevance story.
- **Latency:** p50/p95 ms/query, separately for compression step and end-to-end.
- **Tag preservation:** fraction of compressed slots whose recovered tags match the union of source-fragment tags.
- **Inference disclosure:** held-out reader LLM's protected-fact recall rate when shown compressed summaries with no quoted source text.

### 5.3 Statistical protocol

- 5 seeds per condition; bootstrap CI alongside means.
- Paired bootstrap for compressor-vs-compressor comparisons on matched instances.
- Wilcoxon signed-rank for the cliff-detection (H2) test.
- Holm correction within each hypothesis family. Families: {H1, H2, H3}, {H4}, {H5, H6}, {H7}, {H8}.
- Effect sizes (Cliff's δ for ordinal, Cohen's d for continuous) alongside p-values.

### 5.4 Compute budget on M4 Pro 48 GB

| Experiment | Approach | Wallclock |
|------------|----------|-----------|
| NarrativeQA / HotpotQA baseline reproduction at 7B | MLX or PyTorch MPS, full evaluation | 1–2 days |
| C1 baseline at 7B: 3 compressors × 5 ratios × 5 seeds × 150 workflows | MLX inference; AutoGen orchestration | 5–10 days |
| ICAE-style compressor training, reconstruction + InfoNCE, 7B LoRA | MLX, rank 16 | ≤3 days |
| C1 characterization at 13B fp16 inference | MLX-LM | 10–20 days |
| 13B LoRA fine-tuning at rank 8 (stretch) | MLX with aggressive memory management | Tight; test feasibility early |
| 34B int4: focused partial sweep at suspected τ* | llama.cpp + GGUF | 3–5 days for subset |
| 70B int4: single-point characterization at suspected τ* | llama.cpp + GGUF, ~3–5 tok/s | 7–14 days for the single point |
| Adversarial-robustness sweep (S2, if selected) | 7B only | 1 week |
| AgentBench selected envs (OS, DB, LTP) at 7B | Off-the-shelf AgentBench harness | 1 week |
| Real-trace arm | Blocked by M0/M1/M2 readiness, not compute | — |

Total compute across Months 0–10 fits comfortably within a single workstation if the 13B / 34B / 70B inference passes are scheduled overnight and on weekends. The plan does not depend on external compute.

---

## 6. Technical Architecture

### 6.1 System view

Three-layer memory bus. The MSc delivers a single-machine reference implementation; the FCG platform team adopts the integration interface.

- **Storage layer.** SQLite for the audit log (append-only via trigger); in-memory dict for the active scratchpad; FAISS-CPU for compressed-slot retrieval. Architecture designed so that Redis Cluster + Postgres can swap in at the doctoral phase without changing the integration API.
- **Compression layer.** Pluggable Compressor interface: `compress(fragment, task_hint, tags) → CompressedSlot`. CompressedSlot carries (a) the slot tensor or text summary, (b) the inherited tag vector, (c) a backpointer to audit-log entries. Three compressor variants ship: V1 dense-embedding, V2 ICAE-style with dual-objective training, V3 instruction-aware filter. The tag-preserving variant (C4) is V2 with an added tag head.
- **Access layer.** FastAPI service exposing write, read, subscribe, audit. Policy-enforcement middleware checks the requester's ACL bitmask against the entry's bitmask on every read; logs every access. This is the API the FCG team adopts.

### 6.2 Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Compressor training | MLX with PEFT (LoRA); PyTorch (MPS) fallback | MLX is native to Apple Silicon; MPS fallback covers ops MLX lacks |
| Inference (≤13B fp16) | Ollama or MLX-LM | Ollama for DX; MLX-LM for controllability |
| Inference (34B/70B int4) | llama.cpp with GGUF quantized models | The practical option at 48 GB |
| Agent runtime | AutoGen | Mature; clean scratchpad integration |
| Vector store | FAISS-CPU | M4 Pro CPU headroom is sufficient |
| RAG orchestration | LlamaIndex | Post-processor hooks needed for P3 |
| Audit log | SQLite | One file, ACID, zero ops overhead |
| Integration interface | FastAPI | Language-agnostic HTTP contract for the FCG team |
| Evaluation harness | Custom Python + RAGAS + DeepEval | Hallucination, faithfulness, custom coordination metrics |
| External-API arm (cost analysis) | GPT-4o-mini, Claude Haiku 4.5 | TalentAdore production prices |

### 6.3 What the doctoral phase (D7) takes over

- Fully distributed memory bus (Redis Cluster + NATS + Postgres triggers + OpenTelemetry).
- Cross-tokenizer / cross-model-family compressed exchange across heterogeneous LLM backends.
- Cryptographic commitment infrastructure tied to AI Service Markets Trilogy Papers 2 and 3.
- Federated memory bus across institutions.
- Live production deployment with M0–M5 production agents at institutional scale.

---

## 7. Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| ICAE baseline has CUDA-only dependencies that don't port to MPS/MLX cleanly | High — Month 1 slips | Medium-high | Have AutoCompressor or from-scratch soft-prompt variant ready as backup; time-box porting to 2 weeks |
| MLX lacks InfoNCE-friendly batch contrastive primitive for the dual-objective training | Medium — Month 3 slips | Medium | Manual cosine-similarity InfoNCE in PyTorch (MPS); tested on tiny synthetic corpus in Month 1 |
| 13B fine-tuning at usable rank doesn't fit in 48 GB | Medium — H7 weakens but does not break | Medium | 7B-only fine-tuning is the primary path. 13B LoRA at rank 8 is the upper limit. If 13B fine-tuning fails, fine-tuning results are 7B-only and H7 is tested via inference scaling rather than training scaling |
| 70B int4 on M4 Pro produces broken output that contaminates results | High — invalidates 70B claims | Medium | Sanity-check 70B int4 on known-answer tasks before running C1. If degraded, document and exclude from headline claims; H7 then rests on 7B/13B/34B |
| Coordination cliff τ* doesn't exist — H2 falsified | Medium — thesis story changes | Medium | Falsification is a thesis-worthy result; Chapter 5 reports the negative finding and discusses why standard metrics correlate better than expected |
| H3 (training distribution) fails | Medium | Medium | Report the negative result; add a small follow-up on prompt-engineering instead of fine-tuning as a Chapter 5 ablation |
| Tag-preservation head training is unstable on MLX | Medium — C4 weakens | Low-medium | Start with low tag-loss weight; synthetic-regression-only baseline as the floor |
| M0/M1/M2 agents not ready by Month 7 | Medium — H8 untested | Medium | Synthetic benchmark carries the thesis. H8 is stretch validation; documented as deferred to D7 if not run, per scope-signoff.md |
| AutoGen runtime bugs confound coordination measurements | High — invalidates results | Medium | No-compression-control condition in every experiment; pin AutoGen version |
| A new paper publishes C2's exact result during the thesis window | Medium — novelty erodes | Medium-high | Weekly arxiv-sanity / Google Scholar alerts on "multi-agent compression," "context compression coordination," "coordination cliff." If a near-miss appears, accelerate submission and reframe Chapter 1 to emphasize the unique aspects: cross-system institutional framing, model-size scaling story, the policy-aware extension |
| TalentAdore expects deliverables conflicting with the thesis | Medium | Low-medium | Pre-negotiate Month 0. Their primary interest is the cost-analysis arm (€/workflow) in C3 and §5.2 |
| Scope expansion after Month 0 | High | Medium | scope-signoff.md filed in Month 0 documents the agreed boundaries. Additions are negotiated as explicit trade-offs against existing scope |
| Schedule slips push submission past the 10-month window | High — degree timeline at risk | Medium | Mid-thesis review in Month 5 is the early warning signal. If two or more chapters are not in reviewable state by end of Month 5, drop stretch goals (Month 8) entirely and reallocate to writing |

---

## 8. Bridge to Doctoral Research (D7)

The MSc gives the doctoral phase four concrete starting points:

- **Working benchmark (C1)** extensible to real-system traces, cross-institutional federation, and richer adversarial governance scenarios.
- **Empirical baseline (C2)** for coordination effects of compression across model scales. D7 tests whether the effects survive cross-tokenizer exchange, federation boundaries, and larger institutional settings.
- **RAG pipeline catalogue (C3)** as scaffolding for cross-institutional retrieval under bandwidth and privacy budgets.
- **Tag-preserving compressor and reference memory-bus integration (C4)** that the doctoral phase scales up into the full distributed memory bus with cryptographic commitment infrastructure.

Doctoral sub-questions the MSc cannot answer but its scaffolding makes tractable:

- How does τ* shift under federation latency?
- Do tag-preservation rates survive federated aggregation?
- What governance properties does cryptographic commitment add over per-slot tags?
- Can C1 be extended into a cross-institutional benchmark suite, and what governance constraints differ from single-institution settings?

The thesis's final chapter (Discussion) names these explicitly to make the MSc → PhD bridge clean.

---

## 9. Key References

### 9.1 Context compression and memory

- Jiang et al. LLMLingua. EMNLP 2023.
- Jiang et al. LongLLMLingua. ACL 2024.
- Pan et al. LLMLingua-2. ACL Findings 2024.
- Mu et al. Learning to Compress Prompts with Gist Tokens. NeurIPS 2023.
- Chevalier et al. AutoCompressor. EMNLP 2023. *Basis for the dual reconstruction + contrastive training spec.*
- Ge et al. In-context Autoencoder (ICAE). ICLR 2024. *Basis for the soft-prompt architecture used in C2 and C4.*
- Wang et al. In-Context Former (ICF). EMNLP 2024.
- Fei et al. Semantic compression. ACL 2024.
- Rae et al. Compressive Transformers. ICLR 2020.
- Guo et al. Dynamic context compression for RAG. 2025.
- Cheng et al. xRAG. arXiv 2405.13792, 2024.
- Li, Liu, Su, Collier. Prompt Compression for LLMs: A Survey. NAACL 2025.

### 9.2 Multi-agent systems, agentic memory, and context engineering

- Wu et al. AutoGen. 2023.
- Hong et al. MetaGPT. ICLR 2024.
- Li et al. CAMEL. 2023.
- Shinn et al. Reflexion. NeurIPS 2023.
- Packer et al. MemGPT / Letta. 2023.
- Xu et al. A-MEM. NeurIPS 2025.
- Chhikara et al. Mem0: Scalable Long-Term Memory. arXiv 2504.19413, 2025.
- Rasmussen et al. Zep. arXiv 2501.13956, 2025.
- Zhang et al. AgentPrune. arXiv 2410.02506, 2024.
- Wang et al. AgentDropout. arXiv 2503.18891, 2025.
- Park et al. Collaborative Memory: Dynamic Access Control. arXiv 2505.18279, 2025.
- Ye et al. KVCOMM. NeurIPS 2025.
- Haseeb. Context Engineering for Multi-Agent LLM Code Assistants. arXiv 2508.08322, 2025.
- Yu et al. MemAgent. arXiv 2507.02259, 2025.
- Anthropic. *How we built our multi-agent research system.* Anthropic engineering blog, June 2025. *Industry precedent for orchestrator-worker multi-agent coordination; their finding that token usage explains 80% of performance variance is the closest published analog to the coordination-cliff hypothesis (H2).*
- Rajasekaran, Dixon, Ryan, Hadfield et al. *Effective context engineering for AI agents.* Anthropic Applied AI engineering blog, 2025. *Names compaction, tool-result clearing, memory, and just-in-time retrieval as the four primitives; the JITR pattern is the contemporary alternative to embedding-based RAG that the C3 pipeline catalogue is benchmarked against.*
- Anthropic. *Managing context on the Claude Developer Platform: context editing and the memory tool.* Anthropic news, October 2025. *Reports 84% token reduction on a 100-turn web-search evaluation via context editing; directly relevant to the compression-ratio metrics in §5.2.*

### 9.3 RAG, long-context, and benchmarks

- Lewis et al. RAG. NeurIPS 2020.
- Sarthi et al. RAPTOR. ICLR 2024.
- Edge et al. GraphRAG. 2024.
- Gutiérrez et al. HippoRAG / HippoRAG 2. NeurIPS 2024 / ICML 2025.
- Asai et al. Self-RAG. ICLR 2024.
- Hsieh et al. RULER. 2024.
- Bai et al. LongBench / LongBench v2. 2024–2025.
- Yen et al. HELMET. ICLR 2025.
- Liu et al. Lost in the Middle. TACL 2024.
- Mialon et al. GAIA. 2023.
- Liu et al. AgentBench. ICLR 2024.
- Anthropic. *Contextual Retrieval.* Anthropic news, September 2024. *Pre-processing comparator for the C3 pipeline catalogue: prepends Claude-generated chunk-level context to each document chunk before embedding. Reported retrieval improvements across codebases, fiction, arXiv papers, and science papers; cost ~$1.02 per million document tokens with prompt caching.*

### 9.4 Privacy-aware retrieval and adversarial robustness

- Zhou et al. Privacy-Aware RAG. arXiv 2503.15548, 2025.
- Bassit & Boddeti. SecureRAG. 2025.
- Zhao. FRAG. 2024.
- Addison et al. C-FedRAG. 2024.
- Li et al. SecurityLingua. CoLM 2025.

### 9.5 FCG programme and internal references

- Paper 1 — Real-Time AI Service Economy. Lovén, IEEE TSC, under review.
- Paper 2 — Trustworthy Marketplace Architecture. Lovén, IEEE TSC, in preparation.
- Paper 3 — Collusion, Learning, and Dynamic Credibility. Lovén, IEEE TSC.
- Paper 4 — Epistemic Incentives. Lovén, IEEE TSC supplementary.
- Saleh et al. MemIndex: Agentic Event-based Distributed Memory Management. ACM TAAS, 2025. *Baseline architecture extended by this thesis.*
- Saleh et al. Towards Message Brokers for Generative AI. ACM Computing Surveys, 2025.
- Lovén et al. Large Language Models in the 6G-Enabled Computing Continuum. 6G Research Visions, 2025.
- Kokkonen, Pirttikangas, Lovén. Autonomy and Intelligence in the Computing Continuum. arXiv 2205.01423, 2022.
- Sheikhi, Kostakos, Lovén. Cognitive SOC. IEEE BigData 2025.
- Campus use case (FCG internal): Vignette 7 — period-end reporting across eight systems.
- Financial analysis (FCG internal): 5-year projections, token-cost dominance.
- FCG system / software / integrator architecture documents.
- NIST AI Risk Management Framework 1.0. 2023.

---

*End of document.*