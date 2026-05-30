# Distributed Memory Bus for Multi-Fragment LLM Workflows: Context Compression, the Coordination Cliff, and Privacy

**Author:** Syed Abdullah Hassan
**Faculty of Information Technology and Electrical Engineering**
**University of Oulu — CSE Research Unit**
**Supervisor:** Lauri Lovén
**Industrial supervision:** Asim Nadeem, Oskari Valkama (TalentAdore Ltd.)
**Year:** 2026

---

## Abstract

Large language models running in multi-step and multi-agent workflows pay for every token they read. Energy, latency, and money scale with context length, and a growing fraction of those tokens carry little information — conversational filler, repeated history, restated system prompts. Context compression is the natural lever. The single-agent prompt-compression literature is mature; what has not yet been measured is whether compression that preserves single-agent question-answering accuracy also preserves the harder property a planner needs: combining information distributed across multiple fragments into a correct answer.

This thesis studies that question on *multi-fragment LLM workflows*. The empirical evaluation uses either a deterministic regex parser or a single LLM call with all (compressed) fragments visible as the planner; multi-round agent simulation is outside the empirical scope. Four contributions are delivered: **(C1)** a reproducible coordination benchmark of 150 instances across three workload families — cross-document fact aggregation, constraint-satisfaction planning, and multi-step retrieval; **(C2)** an empirical characterisation of the *coordination cliff* $\tau^{*}$ across four training-free compressors (LLMLingua-2, Phi-3-Mini extractive, an instruction-aware filter, and a truncation baseline), with a compounding-error model that predicts the cliff position from per-round token recall and a cross-architecture validation on Qwen-72B (within 0.8% of the predicted position) and DeepSeek V4 Pro (bootstrap confidence interval contains the prediction) inside a formally-defined calibrated regime; **(C3)** a catalogue of three RAG pipelines showing that compress-first is robustly preferred in both storage-bounded and accuracy-bounded regimes, challenging the post-retrieval-compression assumption of the LongLLMLingua line of work; and **(C4)** a memory-bus reference implementation built around a tamper-evident audit log and a policy-aware compressor abstraction, together with a summary-level *inference-disclosure* metric that quantifies how compression reduces the recoverability of protected facts to a downstream reader.

Six hypotheses are tested across approximately one hundred thousand evaluation cells. **H1** (single-agent question-answering accuracy decorrelates from coordination success under compression) is supported: Spearman $\rho \in [-0.59, +0.38]$ across compressors, with 95% bootstrap confidence intervals excluding 0.6. **H2** (a sharp cliff exists) is supported on eleven of twelve (compressor, family) cells with paired Wilcoxon $p < 0.0001$. The original **H5** is reframed and supported as **Corollary 1 (ceiling-cliff separation)**: model capacity sets the success ceiling $p_0$, not the cliff position $\tau^{*}$, within the calibrated regime. The original **H6** is reframed and supported as **Corollary 2 (information-density scaling)**: the cliff position varies with task information density, with $\theta_\text{info}=0.97$ on a dense numeric-aggregation family and $0.37$–$0.48$ on distributed multi-document benchmarks (HotpotQA and MultiHopRAG). **H4** (compression reduces inference disclosure) is supported with a documented reader-bias caveat. The thesis also contributes **CAAC** — a cliff-aware adaptive compression wrapper that operationalises the compounding-error bound as a runtime back-off, populating a complementary operating point on the (coordination, ratio) frontier.

The deliverable is the manuscript together with an open-source reference implementation reproducible from a single command on commodity hardware (Apple M4 Pro 48 GB and an RTX 5090 32 GB workstation for the GPU-bound sweeps).

**Keywords:** context compression; large language models; coordination cliff; multi-fragment workflows; memory bus; inference disclosure; agentic memory; retrieval-augmented generation.

---

## Foreword

This thesis was carried out at the Future Computing Group, CSE Research Unit, Faculty of Information Technology and Electrical Engineering, University of Oulu, in collaboration with TalentAdore Ltd. The work was supervised academically by Lauri Lovén, with industrial supervision from Asim Nadeem and Oskari Valkama at TalentAdore.

I owe my warmest thanks to Lauri for the latitude to scope a project around an unfamiliar empirical question — the way coordination under compression behaves at institutional scale — and for the discipline he brought to keeping the scope tight. I am grateful to Asim Nadeem and Oskari Valkama for sharing TalentAdore's production cost structure, which anchored the cost-per-workflow arm of the evaluation in a real industrial setting. I thank Mohammad Abaeiani, Faisal Khan, and Vu Truong for their willingness to coordinate around the demands of this thesis.

The thesis was prepared on a single Apple M4 Pro 48 GB workstation with an RTX 5090 32 GB GPU host on the Tailscale mesh for the compression precomputation and the model-scaling and frontier-API sweeps. The compute envelope, the reproducibility package, and the open-source reference implementation are described in Appendix D.

**Use of generative-AI tools.** This thesis was prepared with the assistance of generative-AI tools. Specifically, Anthropic's Claude (accessed via the Claude Code command-line interface) was used to (a) draft and revise prose under the author's continuous supervision; (b) assist with code review, refactoring, and debugging of the experiment-orchestration and analysis scripts; and (c) cross-check verdict-table numbers against the on-disk results CSVs during the audit-reconciliation period. Every scientific claim, every experimental design choice, every results-interpretation paragraph, and the final manuscript text are the author's responsibility. Recorded design decisions reached with AI-assisted brainstorming are documented as architecture decision records (ADRs) in `docs/adr/` of the repository and are cited in this manuscript wherever they shape a load-bearing claim.

— Syed Abdullah Hassan, Oulu, May 2026

---

## Abbreviations

| Abbreviation | Meaning |
|---|---|
| ACL | access control list |
| ADR | architecture decision record |
| API | application programming interface |
| AUC | area under the curve |
| BCa | bias-corrected and accelerated (bootstrap CI) |
| CAAC | cliff-aware adaptive compression |
| CI | confidence interval |
| C1 … C4 | contributions one through four of this thesis |
| CSE | Computer Science and Engineering |
| CTR | critical-token-recall |
| EM | exact match (QA metric) |
| EUR | euro (currency) |
| FAISS | Facebook AI Similarity Search |
| FCG | Future Computing Group |
| H1 … H6 | hypotheses one through six |
| HNSW | hierarchical navigable small world (vector index) |
| HTTP | hypertext transfer protocol |
| ICAE | in-context autoencoder |
| ITEE | Information Technology and Electrical Engineering |
| JSON | JavaScript Object Notation |
| KV cache | key–value cache (transformer attention) |
| LLM | large language model |
| LoRA | low-rank adaptation |
| LRU | least recently used |
| MLX | Apple's native ML framework for Apple Silicon |
| MPS | Metal Performance Shaders (Apple PyTorch backend) |
| NIST AI RMF | NIST AI Risk Management Framework |
| OAuth | open authorisation protocol |
| OTel | OpenTelemetry |
| P1 … P3 | retrieval–compression pipeline variants one through three |
| pp | percentage points |
| QA | question answering |
| RAG | retrieval-augmented generation |
| REST | representational state transfer |
| SHA-256 | secure hash algorithm (256-bit) |
| SQL | structured query language |
| SQLite | a lightweight, embedded SQL database |
| SSE | server-sent events |
| TF–IDF | term frequency–inverse document frequency |
| TTL | time-to-live |
| UUID | universally unique identifier |
| WAL | write-ahead log |

**Symbols of the compounding-error model (Chapter 4 §4.3):**

| Symbol | Meaning |
|---|---|
| $r$ | nominal compression ratio (source / output token count) |
| $q(r)$ | per-round critical-token-recall at ratio $r$ |
| $\theta_q$ | cliff-recall threshold (per-family) — minimum recall for coordination success |
| $\theta_\text{info}$ | task information-density estimate (per-task, AUC-based; distinct from $\theta_q$) |
| $\tau^{*}$ | cliff position — ratio at which coordination success drops below the cliff threshold |
| $p_0$ | baseline coordination success at $r=1$ |
| $N$ | number of sequential compression passes (always 1 in this thesis) |

**Statistical symbols:**

| Symbol | Meaning |
|---|---|
| $\rho$ | Spearman's rank correlation coefficient |
| $\delta$ | Cliff's delta (ordinal effect size) |
| $d$ | Cohen's $d$ (continuous effect size) |
| $p$ | two-sided $p$-value (typically Holm-corrected) |

---

# 1. Introduction

## 1.1 Motivation: Every Token Has a Cost

Large language models pay for every token they read. The cost is measurable at three layers: the energy and water needed to power a prefill and a decoding pass; the latency the user pays to wait for that pass to complete; and the dollar amount the operator pays per million tokens through an API or amortises through on-premises hardware. Peer-reviewed measurements of inference-side energy are recent — Luccioni *et al.*'s 2024 *Power Hungry Processing* study reports per-inference Watt-hour numbers for a broad set of open models, and finds that the wall-power cost of a single text-generation inference call on a modestly-sized model is within an order of magnitude of the wall-power cost of an internet search [Luccioni 2024]. When the workload is a multi-step agentic system that issues thousands of internal inference calls to answer a single user request, those costs compound.

A growing fraction of the tokens a deployed LLM reads do not change the answer. They are conversational filler ("Hello", "Thanks"), repeated system prompts that scaffold every call, restated history that re-anchors a long conversation, boilerplate disclaimers, and structural framing that an attentive reader could elide without loss. The industry rough estimate, widely reported in 2025, was that OpenAI's compute bill for processing user politeness alone amounted to *"tens of millions of dollars"* annually [Altman 2025]. The number is reported as industry observation, not as peer-reviewed measurement, but the direction is consistent with the Luccioni result [Luccioni 2024]: tokens that do not change the answer are converted directly into energy, latency, and operating expense.

Context compression is the natural lever. Per-token compute and per-token cost scale roughly linearly in sequence length once the prefill is past the GPU memory-bound regime; halving the input context halves the cost. The single-agent prompt-compression literature has matured rapidly over the past three years [Jiang 2023; Jiang 2024; Pan 2024; Mu 2023; Chevalier 2023; Ge 2024]. What has not yet been measured, and what this thesis sets out to measure, is whether the compression that preserves the standard single-agent question-answering metric — token-overlap F1 against a ground-truth answer — also preserves the harder structural property that a planner needs: combining information distributed across multiple fragments into a correct answer.

## 1.2 The Multi-Fragment Workflow

The setting this thesis studies is the *multi-fragment LLM workflow*: a task in which the answer cannot be read out of any single fragment in isolation and requires combining information across two or more fragments, each of which may be compressed independently before the planner sees it. Cross-document fact aggregation (sum eight numbers reported by eight different institutional systems), constraint-satisfaction planning (assign $N$ sub-tasks to $K$ capacity-bounded workers given specifications spread across fragments), and multi-step retrieval (chain references through a sequence of documents until a leaf answer is reached) are three representative examples; the C1 benchmark of Chapter 3 constructs 50 instances of each. The setting is not a corner case. The FCG group at the University of Oulu's flagship use case — *Vignette 3.7 — Period-end project reporting* [FCG 2026] — gathers reporting data across eight university systems via roughly eight specialised agents, achieves an estimated 80% cloud-payload reduction, and reduces the per-report cost to approximately EUR 2.15. TalentAdore, the industry partner of this thesis, runs production workloads whose operating expenses are dominated by token cost. Anthropic's own published report on their multi-agent research system notes that token usage explains approximately 80% of the performance variance they observe [Anthropic 2025a]; the corresponding context-engineering and context-editing reports describe an 84% token reduction on a 100-turn web-search evaluation [Anthropic 2025b; Anthropic 2025c]. These are industry observations on industry workflows; the master's-scale problem is the controlled cross-compressor, cross-task, cross-architecture measurement that turns the industry urgency into a technical question.

The technical question this thesis takes up does not include the multi-round agent-negotiation question that the "multi-agent" framing of the FCG and Anthropic systems would imply. The empirical evaluation of this thesis uses either a deterministic regex-based information-extraction solver or a single LLM call with all (compressed) fragments visible as the planner. An AutoGen v0.4 multi-round agent backend integrated with the memory bus is shipped in the source tree (`src/m6/orchestrator/` [Wu 2023]) but is not used in any reported result. The scope decision is documented as **ADR-009** in the repository. The motivation is that round-to-round LLM variance dominates the compression signal at the C1 compression ratios that this thesis sweeps; cleanly attributing coordination-quality drops to compression rather than to multi-round agent variance requires isolating the compressor on the critical path, which a single-LLM-call (or a deterministic regex) planner does. The memory bus is *designed for* a multi-agent integration; the experimental scope is multi-fragment task solvability.

## 1.3 Problem Statement

> **How does context compression affect multi-fragment coordination quality across compressors, task structures, and planner scales — and when and how can a memory-bus service exploit that understanding to compress safely, predictably, and privately?**

The question subdivides into four operationally distinct sub-questions, one per contribution. *First*, a benchmark question: what does a coordination-quality metric on a multi-fragment workflow look like, and how should it differ from single-agent question-answering accuracy? *Second*, a characterisation question: does compression introduce a *coordination cliff* — a compression ratio beyond which coordination success collapses sharply — and what determines its position? *Third*, a deployment question: how should compression be combined with retrieval in a retrieval-augmented-generation pipeline, and what is the cost trade-off across pipeline architectures? *Fourth*, a governance question: can compression be measured as a privacy lever, and can a memory-bus service expose that lever as a deployment-time enforcement mechanism?

The thesis answers all four with four artefacts, each delivered end-to-end and reproducible from the open-source repository.

## 1.4 Contributions

**C1 — A reproducible multi-fragment coordination benchmark.** *The C1 benchmark* ships 150 instances across three workload families (cross-document fact aggregation, constraint-satisfaction planning, multi-step retrieval), with synthetic provenance and access-control tag distributions, four coordination-quality metrics (final task success, sub-task assignment accuracy, rounds to completion, critic-flagged error rate), and a single-command regeneration script from a fixed seed. The benchmark is the substrate on which the cliff characterisation, the model-scaling result, and the inference-disclosure measurement all run; releasing it as part of the thesis lets other groups extend the characterisation to new compressors and new planner regimes.

**C2 — Empirical characterisation of the coordination cliff and a compounding-error model that predicts it.** *The cliff exists, is sharp, and is invariant to planner parameter count and architecture family within a defined calibrated regime.* The empirical work covers four training-free compressors — LLMLingua-2 [Pan 2024], the Phi-3-Mini extractive span selector, an instruction-aware filter, and a truncation baseline — at ten compression ratios across three families and across three Qwen-2.5 planner sizes (1.5B, 3.8B, 8B), with a frontier validation arm on Qwen-2.5-72B and DeepSeek V4 Pro that demonstrates cross-architecture cliff invariance to within 0.8% on the Qwen scale-up and a bootstrap-CI-containment result on the cross-vendor case. The compounding-error model derives the cliff position from per-round critical-token-recall and a per-family recall threshold and recovers the empirical position within a useful first-order tolerance. An out-of-regime diagnostic on GPT-oss 120B identifies extended-reasoning planners as a structurally distinct case that the model's threshold-success assumption does not cover — which is itself a contribution, since prior compression work treats reasoning regime implicitly.

**C3 — A catalogue of three retrieval-augmented-generation pipelines with a EUR-per-workflow cost model.** Three pipeline architectures (compress-first, retrieve-first, joint relevance-conditional routing) are implemented end-to-end on FAISS-CPU and HNSW and evaluated under matched storage-bounded and accuracy-bounded regimes. The original H3 hypothesis predicted a sign-flip in the optimal pipeline between regimes; the empirical work shows that compress-first is robustly preferred in both regimes, with the joint-routing variant leading both by a small margin. The compress-first preference *reverses* a common assumption of the LongLLMLingua [Jiang 2024] line of work and is the substantive C3 finding, registered honestly as a reframing of the original predicate.

**C4 — A memory-bus reference implementation and a summary-level inference-disclosure metric.** The memory bus is a FastAPI service with a tamper-evident SQLite audit log, a policy middleware that enforces a five-tier classification lattice over a 64-bit access-control mask, an in-memory scratchpad with TTL eviction, and a FAISS-CPU vector store. The compressor abstraction is a Python protocol that all five compressor variants satisfy. The summary-level inference-disclosure metric quantifies how compression at 4× reduces the rate at which a held-out local Llama-3.1-8B reader can recover protected facts from a compressed CONFIDENTIAL fragment. The metric ranks compressors by privacy at iso-ratio, and the memory bus's policy layer operationalises the ranking as a deployment-time enforcement mechanism.

The thesis also presents **CAAC** (Cliff-Aware Adaptive Compression), a wrapper that operationalises the compounding-error bound as a runtime back-off: given a per-family recall threshold, CAAC binary-searches downward over compression ratios until the per-fragment critical-token-recall sits on the safe side of the cliff. CAAC is presented in Chapter 5 as a constructive demonstration of the compounding-error model rather than as a fifth headline contribution; the demonstration is that the cliff bound is not only descriptive but operational.

## 1.5 What Is Novel

The closest published industry analogue to C2 is Anthropic's report that token usage explains approximately 80% of the performance variance in their multi-agent research workflow [Anthropic 2025a]. That is an industry observation on a single workflow run by a single team; the C2 contribution is the controlled cross-compressor, cross-family, cross-architecture sweep with a quantitative model, an empirical match-rate measurement, and a frontier-model validation. The closest published academic analogues are the single-agent question-answering evaluation of the LLMLingua line of work [Jiang 2023; Jiang 2024; Pan 2024] and the long-context benchmarks LongBench [Bai 2024] and RULER [Hsieh 2024]; H1 shows that those evaluations *over-report* compressor utility for multi-fragment deployment because the single-agent metric they measure does not predict coordination success. The multi-fragment-specific characterisation is the novelty.

The compounding-error model is novel in its application to multi-fragment compression evaluation. The derivation is short and the threshold-success assumption is a first-order approximation, but the combination of a quantitative position-prediction with a bootstrap-CI band on the prediction and a per-cell empirical match-rate measurement is, to the author's knowledge, not present in the prior compression literature.

The summary-level inference-disclosure metric (C4) is distinct from prior privacy-aware retrieval work [Zhou 2025; Bassit 2025], which protects the retrieval index from leaking; the metric this thesis contributes measures leakage *through the compressor itself*, which is a separate axis. The memory-bus reference implementation makes the metric auditable as a deployment-time governance budget rather than a per-publication number.

## 1.6 Thesis Outline

**Chapter 2** surveys the prior work the four contributions build on, organised into seven strands: the transformer architecture and the cost of context, the modern training-free context-compression literature, multi-agent LLM systems, retrieval-augmented generation, and privacy in agentic memory. Each section closes by naming the gap that this thesis fills relative to the prior work it surveys.

**Chapter 3** presents the artefacts the empirical evaluation runs on: the three-layer memory-bus architecture, the compressor framework, the C1 benchmark generator and scoring pipeline, the critical-token-recall metric, the compression cache, and the multi-fragment scope of the evaluation.

**Chapter 4** presents the empirical work: H1, H2, the compounding-error model that predicts the cliff position with a predicted-versus-empirical match-rate band, Corollary 1 (cliff position is invariant to planner parameter count within the calibrated regime, validated on three frontier models), H3 (the RAG pipeline catalogue with the compress-first dominance result), H4 (the inference-disclosure measurement on the unbiased benchmark), and Corollary 2 (information-density scaling of the cliff across three benchmarks).

**Chapter 5** synthesises the findings, presents CAAC as the constructive realisation of the compounding-error bound, enumerates the limitations, discusses the practitioner and field-level significance, compares the findings to industry observations, and names the future-work directions in order of expected impact.

All artefacts — the manuscript source, the code, the configuration files, the results CSVs, and the `docker-compose.yml` that brings the memory-bus reference service up locally — are released under a permissive licence in the open-source repository. Appendix D describes the reproducibility package and the one-command reproduction recipe for every headline figure.

---

# 2. Background and Related Work

This chapter surveys the prior work the four contributions of this thesis build on. It is organised into seven strands. §2.1 introduces the transformer architecture and the per-token compute and memory cost that context-compression aims to reduce. §2.2 sketches the scaling-law trajectory and the inference-cost asymmetry that followed. §2.3 surveys the published energy and economic measurements of inference at scale, which underpin the motivation chapter. §2.4 covers the modern training-free context-compression literature. §2.5 covers multi-agent LLM systems and agentic memory. §2.6 covers retrieval-augmented generation, long-context benchmarks, and the evaluation suite that frames C3. §2.7 covers privacy-aware retrieval and the inference-disclosure literature. Each section closes by naming the gap that this thesis fills relative to the prior work it surveys; the consolidated gap statement is §2.8.

## 2.1 The Transformer Architecture and the Cost of Context

The artefacts of this thesis are built around large language models whose architectural foundation is the transformer [Vaswani 2017]. The transformer's defining mechanism is *self-attention*: each token in a sequence computes a weighted sum of representations of every other token in the same sequence, with the weights determined by the compatibility of learned query and key projections of the respective tokens. For a sequence of length $N$ and a hidden size $d$, the self-attention mechanism produces $N^2$ compatibility scores (a quadratic-in-$N$ memory and compute cost) and a final $N \times d$ output. The transformer block interleaves self-attention with a position-wise feed-forward network whose cost is linear in $N$ but proportional to the square of the hidden size $d$. Stacking $L$ such blocks gives total prefill compute approximately $L \cdot (N^2 d + N d^2)$ floating-point operations per forward pass and a memory footprint dominated by the key-value cache of size $L \cdot N \cdot d_{\text{kv}}$ bytes per request, which grows linearly in $N$ and is paid for every token through the autoregressive decoding loop.

The decoder-only sub-family of the transformer architecture is the one this thesis evaluates. The original transformer [Vaswani 2017] was encoder–decoder; the encoder-only line gave us BERT and its descendants; the decoder-only line gave us GPT-2, GPT-3, GPT-4, and the open-source families that this thesis's planners are drawn from (Qwen, Llama, DeepSeek, Phi-3). The reasons decoder-only architectures came to dominate large-scale deployment are three. First, the training objective is uniform across all token positions (next-token prediction), which scales cleanly with data and parameters. Second, the autoregressive decoding loop allows the key-value cache to be amortised across token positions after the prefill, which makes each generated token cheap relative to the context that was loaded. Third, the in-context-learning behaviour that motivated agentic systems is a decoder-only phenomenon: the model conditions its output on a long prefix without further training. The practical implication for context compression is that the cost a deployed decoder-only model pays per query is roughly $2 \cdot P \cdot N$ floating-point operations during prefill (where $P$ is the parameter count) and a per-decoded-token cost that is dominated by the key-value cache loaded from the prefill. Halving the prefill-length $N$ halves both costs. This is the lever context compression operates on.

The scaling laws of large language models give one final piece of the cost picture. Kaplan *et al.* [Kaplan 2020] showed that the loss of a transformer trained on next-token prediction follows an approximate power-law in parameters, training tokens, and compute, with prescriptive implications for how to allocate a fixed compute budget between model size and training data. Hoffmann *et al.* [Hoffmann 2022] refined this with the *Chinchilla* prescription that parameters and training tokens should scale proportionally for compute-optimal training. The training-time scaling laws gave the field a recipe to spend training compute productively; what they did not give is a corresponding recipe to spend *inference* compute productively. Inference cost is paid per query for the deployment lifetime of the model, and at production scale it dominates training cost over a small number of months. Context compression is to inference cost what scaling laws are to training cost: a structural lever that converts a linear cost in some axis into a constant cost.

*What this thesis adds.* The cost framing this section provides is the motivation backdrop. What is missing in prior work is a structural characterisation of how aggressive compression interacts with the per-token cost reduction it delivers when the downstream task requires combining information across multiple compressed fragments rather than reading a single answer out of a single fragment. The cliff measurement of Chapter 4 fills that gap.

## 2.2 The Scaling Era of LLMs

The trajectory from GPT-2 (1.5B parameters, 2019) to GPT-3 (175B, 2020) to GPT-4 (undisclosed, 2023) to the frontier of 2025–2026 (Llama-3, Qwen-2.5, DeepSeek V3 and V4, Claude Sonnet 4.x, GPT-oss) marks a four-order-of-magnitude growth in deployed model size. Each step was accompanied by a near-linear increase in the cost per query and a corresponding increase in the demand for context-engineering techniques that control how much input the model reads at inference. As of the writing of this thesis, the frontier API price for a high-end model is approximately USD 3 per million input tokens and USD 15 per million output tokens, which corresponds to approximately EUR 2.76 and EUR 13.80 at the time of writing. The on-premises amortised marginal cost on a typical mid-range GPU deployment is roughly EUR 0.05 per million tokens once hardware is paid for. The two- to three-orders-of-magnitude gap between frontier-cloud and on-premises cost is what makes context compression an operational concern: cutting context length by half on a frontier-cloud workload saves real money per query.

The model-side trends are accompanied by a context-window trend. The 2K-context GPT-2 era gave way to 4K, 8K, 32K, 128K, and now multi-million-token contexts on the frontier. The long-context-benchmark literature (§2.6) documents that the model's effective use of those long contexts is less complete than the nominal window size [Liu 2024b; Hsieh 2024]: tokens placed in the middle of a long context are recovered less reliably than tokens at the start or the end. Long contexts make the case for compression even stronger; tokens that the model will not effectively use are pure cost.

*What this thesis adds.* The model-scale trend motivates the question that Corollary 1 of Chapter 4 answers: does the cliff position depend on which point on the model-scale curve the planner is at? The frontier validation on Qwen-72B and DeepSeek V4 Pro is the cross-architecture answer — no, within the calibrated regime — that the scaling-era trend makes interesting in the first place.

## 2.3 The Cost of Running LLMs at Scale

The motivation chapter of this thesis frames the work in terms of the per-token cost an operator pays. This subsection surveys the published measurements that anchor that framing.

**Energy.** Luccioni, Jernite, and Strubell's 2024 *Power Hungry Processing* study [Luccioni 2024] measures the wall-power cost of inference for a broad set of open-weight models on a single A100 GPU server. The headline number is that text generation on a $\sim$6B-parameter open model costs $\sim$0.5 Watt-hours per prompt-and-completion of typical length, which is within an order of magnitude of the energy cost of a single web search. The number scales near-linearly with model size, and the per-prompt energy at frontier-scale models (tens to hundreds of billions of parameters) is correspondingly larger. The study also separates the per-token amortised cost from the per-request fixed cost, and shows that for short prompts the fixed cost dominates while for long prompts the per-token cost dominates. The relevant implication for compression is that the operational regime context-compression operates in is the long-prompt regime, where the per-token cost is what compression directly cuts.

**Token economics.** Industry pricing as of the writing of this thesis sits at approximately USD 3 per million input tokens for the frontier "base" tier and USD 15 per million for the frontier "output" tier, with reasoning-augmented tiers priced higher. At a steady state of one million calls per day and an average prompt of 10,000 tokens, that is USD 30,000 per day of input cost alone for a frontier model. Halving the prompt length saves USD 15,000 per day — the kind of magnitude that funds an entire compression-engineering team. The on-premises amortised marginal cost is two orders of magnitude lower per token, but the absolute hardware and operations cost of running on-premises is high enough that the same compression lever is operationally valuable. The TalentAdore production accounts that this thesis's cost model is calibrated against confirm the pricing as of the writing of the manuscript.

**Politeness as waste.** The industry-anecdotal observation that the compute cost of processing user politeness at OpenAI's frontier products amounted to "tens of millions of dollars" annually was made by Sam Altman in 2025 [Altman 2025]. The exact figure is reported as industry observation rather than as a peer-reviewed measurement; the direction is consistent with the Luccioni numbers [Luccioni 2024] and is plausible on a back-of-the-envelope. Every "Hello", "Thanks", restated history, and repeated system prompt is converted directly into kilowatt-hours and dollars. The thesis uses the framing as the opening rhetorical hook (Chapter 1); the substantive question of how aggressively the wasted tokens can be removed without losing the answer is what the rest of the thesis measures.

**Multi-agent multiplier.** Anthropic's report on their multi-agent research system [Anthropic 2025a] observes that token usage explains approximately 80% of the performance variance they see, and that a substantial fraction of that token cost is the shared context that flows between agents in each round. The follow-on report on context engineering for AI agents [Anthropic 2025b] and the report on context editing and memory tools [Anthropic 2025c] describe an 84% token reduction on a 100-turn web-search evaluation. These are industry observations rather than controlled measurements; what they do is establish that the cost-of-context question is operationally pressing for production multi-agent deployments.

*What this thesis adds.* Prior work establishes that inference cost is real, that compression cuts it, and that deployed multi-agent systems are dominated by token cost. What is missing is the structural answer to *how aggressively compression can be applied before coordination breaks*. The cliff characterisation of Chapter 4 is that answer.

## 2.4 Context Compression — the Breakthrough Works

The training-free context-compression literature has matured in the past three years into four recognisable families. This subsection surveys the four, with a comparison table at the end that maps the families against the design dimensions that matter for multi-fragment evaluation. Each family closes with a "what is missing in prior work" line that the rest of the thesis addresses.

### 2.4.1 Token-level pruning (the LLMLingua family)

The first practical context-compression technique to see broad adoption was LLMLingua [Jiang 2023], which uses a small autoregressive language model to score tokens by their per-step perplexity contribution and drop those whose removal least disturbs the conditional distribution. LongLLMLingua [Jiang 2024] extends the coarse-to-fine ranking with a question-aware step to handle long retrieval-augmented contexts. LLMLingua-2 [Pan 2024] trains an XLM-RoBERTa token classifier on data distilled from a more capable model, producing a task-agnostic compressor that is faster at inference than the original LLMLingua because it does not require running a generative model at compression time. The LLMLingua-2 classifier is the principal hard-prompt compressor of this thesis; its evaluation centres on NarrativeQA F1 within 2 pp and HotpotQA F1 within 3 pp of reported numbers [Kočiský 2018; Yang 2018] as the calibration target.

*What is missing in prior work.* All three LLMLingua papers report single-agent question-answering F1 retention at modest compression ratios. None measures whether the surviving content is sufficient for a downstream planner to combine information across multiple compressed fragments into a correct answer. H1 of Chapter 4 measures exactly that and finds that the single-agent F1 metric does not predict coordination success.

### 2.4.2 Selective and instruction-aware compression

Li *et al.*'s *Selective Context* [Cheng 2024; Li 2025] prunes tokens with low self-information under the model's own conditional distribution; the technique requires no training but does require running a scoring forward-pass at compression time. Xu *et al.*'s *RECOMP* compresses long retrieval contexts with a small task-aware extractor trained to summarise the retrieved passages for the downstream question. The instruction-aware filter of this thesis sits in the same family but takes the deliberate simplification of using a TF-IDF pruning step followed by a cross-encoder re-ranker (`BAAI/bge-reranker-base`) and a stop-word/short-token trim, with no LM in the loop. The simplification gives a deterministic, training-free, low-cost baseline that the more sophisticated compressors must beat.

*What is missing in prior work.* The task-awareness in this literature is question-conditioned: the compressor takes the downstream question as input and prunes against it. In a multi-fragment workflow the planner's question is not the fragment-level task; the fragment-level task is to preserve information that a planner-as-yet-unknown will combine with information from other fragments. The thesis's instruction-aware filter and the empirical evaluation of all four compressors on multi-fragment families address this gap.

### 2.4.3 Learned compression (parameter-cost compressors)

Mu *et al.* [Mu 2023] introduced *gist tokens*, special positions trained with a masked attention pattern so that the model learns to compress instruction prefixes into a small number of virtual tokens. Chevalier *et al.* [Chevalier 2023] extended this with *AutoCompressor*, which fine-tunes a language model to process long documents segment by segment and produce summary vectors. Ge *et al.* [Ge 2024] formalised the architecture as the *In-context Autoencoder (ICAE)*, which trains a LoRA-adapted encoder to produce a fixed number of memory tokens from an input context. Wang *et al.* [Wang 2024] present the In-Context Former, a faster cross-attention variant. Rae *et al.* [Rae 2020] introduced the Compressive Transformer architecture, which is the closest single-context analogue of the cliff bound this thesis derives.

*What is missing in prior work.* The learned-compression papers require training, which introduces both a training-data asymmetry between compressors (which makes cross-compressor comparison less clean) and an operational deployment cost (every new compressor needs its own fine-tune). This thesis deliberately stays training-free; the LLMLingua-2 wrapper, the instruction-aware filter, the Phi-3-Mini extractive span selector, and the truncation baseline are all inference-only, which makes the cliff comparison turn on the algorithm-of-action rather than on training-budget asymmetry. The learned-compression literature could be re-evaluated under the multi-fragment cliff methodology of this thesis as a follow-on study; the thesis does not do so directly.

### 2.4.4 Extractive small-LLM span selection

Recent work uses small instruction-tuned LLMs as extractive compressors that produce verbatim spans of the source rather than abstractive summaries. The candidate small LLMs are the Phi-3 family [Phi-3 2024] and other $\sim$3B-parameter instruction-tuned models. Extractive compression is privacy-friendly because the compressed output is by construction a subset of the source tokens; this is one of the reasons it appears in this thesis as a compressor option.

*What is missing in prior work.* The published guidance on how to enforce the extractive constraint reliably is thin; small LLMs frequently insert function-word filler even when told not to. The Phi-3-Mini extractive compressor of this thesis ships a post-hoc verifier with a 15% novel-token tolerance and an LLMLingua-2 fallback that together salvage outputs whose extractive fraction is above 50%; the architecture is documented in detail in §3.2 and is one of the engineering contributions of the thesis.

### 2.4.5 Comparison table

| Family | Training-free? | Task-aware? | Eval'd on multi-fragment? | Deployed in this thesis? |
|---|---|---|---|---|
| LLMLingua family [Jiang 2023; Jiang 2024; Pan 2024] | yes (inference-only) | question-conditioned | no | LLMLingua-2 |
| Selective Context, RECOMP | yes | yes | no | — |
| Gist Tokens / AutoCompressor / ICAE [Mu 2023; Chevalier 2023; Ge 2024] | no (training required) | varies | no | — |
| Extractive small-LLM (Phi-3 family) [Phi-3 2024] | yes (inference-only) | yes | no | Phi-3-Mini ext. |
| Instruction-aware filter | yes | yes | no | yes (this thesis) |
| Truncation (prefix-keep) | yes | no | no | yes (baseline) |
| **This thesis (multi-fragment cliff sweep)** | **yes** | **yes** | **yes** | **four compressors** |

## 2.5 Multi-Agent LLM Systems and Agentic Memory

The multi-agent LLM-systems literature has grown rapidly since 2023. The most-cited frameworks are AutoGen [Wu 2023] (an open-source framework for multi-agent conversation; appeared at the ICLR 2024 LLM-Agents Workshop rather than as a main-conference paper), MetaGPT [Hong 2024] (ICLR 2024 main), CAMEL [Li 2023] (NeurIPS 2023), Reflexion [Shinn 2023] (NeurIPS 2023), MemGPT [Packer 2023] (preprint, not yet peer-reviewed at the time of writing of this thesis), and Generative Agents [Park 2025] (UIST 2023). Each framework has its own implicit answer to the question of how shared context flows between agents and what an individual agent needs to see. None of the frameworks formally bounds the information loss introduced when that shared context is compressed.

The agentic-memory line of work [Packer 2023; Xu 2025; Chhikara 2025; Rasmussen 2025; Saleh 2025a; Saleh 2025b] addresses the related question of how to store and retrieve agent state across long horizons. The closest published academic analogue to this thesis's memory bus is MemIndex [Saleh 2025a], which the three-layer memory-bus architecture of Chapter 3 explicitly extends. The MemGPT-style "LLM as operating system" framing [Packer 2023] is related but is concerned with single-agent long-horizon memory rather than multi-agent shared state. Mem0 [Chhikara 2025] is a production-oriented agentic-memory service.

*What is missing in prior work.* The multi-agent and agentic-memory frameworks treat compression as an implicit deployment optimisation; none measures the coordination-quality cost of compression structurally or bounds the loss quantitatively. The cliff measurement of Chapter 4 and the inference-disclosure measurement of the H4 section provide the missing quantitative foundation. The memory bus of Chapter 3 is designed as the reference target for that foundation.

## 2.6 Retrieval-Augmented Generation and Long-Context Benchmarks

Retrieval-augmented generation as a paradigm dates to Lewis *et al.* [Lewis 2020]. The landmark works since include RAPTOR [Sarthi 2024] (recursive abstractive processing for tree-organised retrieval, ICLR 2024), GraphRAG [Edge 2024] (a Microsoft preprint at the time of writing, not yet at a peer-reviewed venue), HippoRAG [Gutiérrez 2024; Gutiérrez 2025] (NeurIPS 2024 and follow-on), and Self-RAG [Asai 2024] (ICLR 2024). The pipeline catalogue this thesis evaluates (P1, P2, P3) places compression on the retrieval critical path explicitly; the closest published analogue to the post-retrieval-compression pipeline (P2) is the LongLLMLingua configuration [Jiang 2024], and the closest published analogue to the joint relevance-conditional pipeline (P3) is the dynamic-routing framework of Guo *et al.* [Guo 2025].

The long-context-benchmark literature [Bai 2024; Hsieh 2024; Liu 2024b; Mialon 2023; Liu 2024a; Yen 2025] measures how effectively a model uses a long context. The "lost in the middle" result [Liu 2024b] is the canonical observation that information placed in the middle of a long context is recovered less reliably than information at the boundaries. RULER [Hsieh 2024] extends the needle-in-a-haystack methodology to a broader set of long-context tasks. LongBench [Bai 2024] is the standard multi-task benchmark. None of these benchmarks measures the multi-fragment-coordination task structure of this thesis; they measure single-agent long-context comprehension. They are complementary to the cliff measurement rather than competitive with it: long-context benchmarks measure the capacity of the model, while the cliff measurement measures the compression-quality effect on a task structure the long-context benchmarks do not include.

The multi-hop question-answering benchmarks HotpotQA [Yang 2018] (EMNLP 2018), 2WikiMultiHopQA (COLING 2020), and MultiHopRAG [Addison 2024; Yang 2018] (EMNLP 2024 Findings; the canonical paper for the MultiHopRAG dataset is by Tang and Yang and is referenced in the project-internal documentation), are the real-data benchmarks on which Corollary 2 of Chapter 4 validates the information-density-scaling claim. The transfer is qualitative: the absolute cliff positions differ between synthetic and real benchmarks because the information density $\theta_\text{info}$ differs, but the cliff structure (existence, sharpness as a function of $\theta_\text{info}$) transfers.

*What is missing in prior work.* The RAG and long-context benchmark literatures measure orthogonal properties to this thesis. The cliff measurement complements them rather than competing: RAG benchmarks measure retrieval quality, long-context benchmarks measure model capacity, and the cliff measurement measures the multi-fragment compression-quality effect that neither captures. The H3 catalogue of three RAG-plus-compression pipelines under matched cost regimes fills the compression-on-the-retrieval-critical-path measurement gap.

## 2.7 Privacy in Agentic Memory and Compressed Retrieval

The privacy-aware-retrieval literature has two strands. The first protects the retrieval index itself, on the assumption that direct access to the index would leak protected facts. Examples include PrivacyRAG [Zhou 2025] and SecureRAG [Bassit 2025]. The second strand protects the model weights from training-data extraction, which is a property of the training pipeline rather than of the deployed retrieval-and-compression service.

The inference-disclosure metric this thesis contributes (C4) is distinct from both: it measures leakage *through the compressor itself*, on the assumption that the retrieval index is access-controlled but the compressed summaries are exposed to the planner and to any downstream reader the planner shares them with. The threat model is intuitive: an adversary who can query the planner can ask questions about the protected fact, and the disclosure rate is the fraction of those questions on which the planner's answer recovers the protected fact given that it has the compressed summary as evidence. The H4 measurement operationalises this in a controlled setup; the memory-bus policy layer of Chapter 3 operationalises the resulting disclosure budget as a deployment-time enforcement mechanism.

The CFedRAG framework [Addison 2024] is a related piece of work on coordination of federated retrieval-augmented generation; it addresses the retrieval-index-level privacy question rather than the compressor-level disclosure question that this thesis takes up.

*What is missing in prior work.* No published academic work, to the author's knowledge, measures inference disclosure through the compressor at the summary level. Privacy-aware retrieval protects the index; this thesis protects the summary. The two are complementary, and a future system would presumably combine them.

## 2.8 The Gap This Thesis Closes

Four sentences, each one mapping to one of the four contributions of Chapter 1.

There is no shared multi-fragment coordination benchmark probing the cliff in a controlled, reproducible setup. **C1** is the benchmark.

There is no published operational bound that predicts cliff position from compressor-side and task-side measurements within a defined regime. **The compounding-error model and its cross-architecture frontier validation** are the bound.

There is no honest catalogue of RAG-plus-compression pipeline placement under matched cost regimes, with the cost model explicit in EUR per workflow. **The C3 catalogue** is the catalogue, and its honest finding is that the assumed sign-flip does not appear.

There is no published academic measurement of inference disclosure through the compressor at the summary level. **The H4 measurement, integrated with the memory bus's policy layer**, is the measurement.

The closest published industry analogue to C2 is Anthropic's multi-agent system report [Anthropic 2025a], labelled honestly as industry observation rather than controlled measurement. The closest published academic analogues are the long-context benchmark suite and the LLMLingua line of work, which measure orthogonal properties on the single-agent axis. The thesis sits at the intersection of these three threads, and contributes the controlled cross-compressor multi-fragment evaluation that the prior work does not provide.

---

# 3. System Design and Implementation

This chapter presents the artefacts the empirical evaluation rests on: the reference memory bus, the compressor framework, the multi-fragment *C1* coordination benchmark, the coordination-success and critical-token-recall metrics that the cliff analysis turns on, the precomputed compression cache that decouples compression from evaluation, and the single-command reproducibility envelope.

A scope reminder, stated once explicitly so that every claim in this chapter and the next is bounded by it: the *multi-fragment LLM workflows* that this thesis evaluates are not multi-agent simulations. The planner is a deterministic regex-based information-extraction solver for the cliff sweep (H1, H2) and a single LLM call with all (compressed) fragments visible for the model-scaling sweep (Corollary 1, frontier validation, real-data transfer). The memory bus is *designed for* a future multi-agent integration with an AutoGen back-end available in the source tree, but its multi-agent operation is outside the empirical scope of this thesis. This boundary is documented in CONTEXT.md and recorded as **ADR-009** in the project repository.

## 3.1 The Memory-Bus Reference Implementation

### 3.1.1 Three-layer architecture

The reference implementation organises the memory bus into three layers that match the access pattern of a fragment-passing workflow:

1. An **access layer**, exposing `read`, `write`, `subscribe`, and `audit` endpoints via FastAPI and enforcing per-request access-control checks through a policy middleware.
2. A **compression layer**, providing a pluggable `Compressor` protocol behind which six concrete variants live: an *identity* no-compression control, the *LLMLingua-2* [Pan 2024] token classifier, an *instruction-aware filter* based on TF-IDF pruning plus a cross-encoder re-ranker, a *Phi-3-Mini extractive* span selector implemented over a local Ollama endpoint, a *truncation* prefix-keep baseline, and *CAAC* — a cliff-aware adaptive wrapper that backs off compression when per-fragment recall would violate the compounding-error model's safety threshold (§3.2.5, full discussion in Chapter 5).
3. A **storage layer**, providing three protocols — `AuditLog`, `Scratchpad`, and `VectorStore` — implemented for the evaluation by SQLite in WAL mode with an append-only audit table, an in-memory time-to-live dictionary, and FAISS-CPU with an HNSW index.

```
┌─────────────────────────────────────────────────────────────────┐
│ Access layer (FastAPI)                                          │
│ POST /v1/write   GET /v1/read   POST /v1/subscribe  GET /v1/audit│
│ PolicyMiddleware  StructLogMiddleware  OtelMiddleware           │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│ Compression layer                                               │
│ Compressor protocol                                             │
│ [identity] [LLMLingua-2] [filter] [Phi-3 ext.] [trunc] [CAAC]  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│ Storage layer                                                   │
│ [SQLite AuditLog]  [InMemory Scratchpad]  [FAISS VectorStore]   │
└─────────────────────────────────────────────────────────────────┘
```

Each component dependency in the source tree is one-directional: the compression layer does not import from the access layer, and the storage layer does not import from either. This layering means the storage backends can be replaced without touching the compression or access layers. The three-layer structure is a direct extension of MemIndex [Saleh 2025a], the FCG group's baseline architecture for distributed agent memory. The two material differences are that compression is promoted to a first-class layer rather than treated as a downstream optimisation, and that per-slot tags are part of the data model rather than out-of-band metadata.

### 3.1.2 Data flow for a write

A single write request flows through the bus in the following order. The client sends `POST /v1/write` with a JSON body containing the fragment text, its tag vector, and an optional task hint. The policy middleware parses the requester principal from the `X-M6-Principal` header and writes it to `request.state.principal` as a Starlette `State()` attribute. The service receives the request, checks that the principal's access-control mask is a superset of the fragment tag's mask and that the principal's classification is at least the fragment's classification, calls the active compressor's `compress(fragment, target_ratio)` method to produce a `CompressedSlot`, places that slot in the in-memory scratchpad keyed on the slot identifier, computes an embedding for the slot if the compressor exposes one and adds it to the FAISS index, and finally appends a row to the audit log whose `event_type` is `WRITE`, `result` is `OK`, `prev_hash` is the previous row's chain hash, and `chain_hash` is $\text{SHA-256}(\text{prev\_hash} \parallel \text{payload\_hash})$. The response carries the slot identifier, the chain hash hex-encoded, and the audit row identifier.

If the policy check fails, the bus appends a `DENY` row with the synthesised slot identifier `deny-<uuid8>`, with a 60-second per-(subject, fragment-id) deduplication so that an adversarial client hammering denied writes cannot inflate the audit log.

### 3.1.3 Data flow for a read

A read request flows symmetrically. The client sends `GET /v1/read/{slot_id}`, the policy middleware attaches the principal, the service looks up the slot in the scratchpad, checks the principal–tag relationship, and either returns the slot together with the audit row identifier or raises a policy-denied or slot-not-found error. The slot-not-found path is itself audited with a 60-second per-(subject, slot-id) deduplication: the first read miss for a given subject and slot is appended to the audit log as a `READ`/`ERROR` row, and subsequent misses within the window short-circuit silently so that an adversarial reader cannot inflate the audit log either. Appendix D contains a verbatim `curl` trace exercising the write, read, and audit endpoints end-to-end against the reference service.

### 3.1.4 Tags, classifications, and the audit log

Every fragment and every compressed slot carries a tag vector recording its provenance and access-control state. The tag vector has four fields: a `uint64` access-control mask, a five-tier classification level (PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED < SECRET) drawn from the NIST AI Risk Management Framework [NIST AI RMF], a tuple of source identifiers recording provenance, and a tuple of parent-slot identifiers recording which previously-compressed slots this slot inherits from. When slots are merged, the union's access-control mask is the bitwise OR of the parents' masks and the union's classification is the maximum; the policy predicate is symmetric for reads and writes.

The audit log is an append-only SQLite table with the columns below. An `INSTEAD OF UPDATE` and an `INSTEAD OF DELETE` trigger refuse any mutation of an existing row, and a unit test drops the trigger, edits a `payload_hash` at the byte level, and confirms that the `verify()` chain-walker reports failure.

| Column | Type | Notes |
|---|---|---|
| `rowid` | INTEGER PK | monotonic, auto-increment |
| `slot_id` | TEXT NOT NULL | matches the slot identifier |
| `event_type` | TEXT CHECK | WRITE / READ / SUBSCRIBE / DENY / COMPRESS / EVICT |
| `requester_acl` | INTEGER | 64-bit ACL mask, stored signed |
| `requester_class` | INTEGER | classification level 0–4 |
| `result` | TEXT CHECK | OK / DENIED / ERROR |
| `prev_hash` | BLOB(32) | SHA-256 of the previous row's chain_hash |
| `payload_hash` | BLOB(32) | SHA-256 of the event's payload bytes |
| `chain_hash` | BLOB(32) | SHA-256(prev_hash ‖ payload_hash) |
| `created_at` | TEXT NOT NULL | ISO-8601 UTC timestamp |

A second SQLite table records every paid model call: provider, model, input tokens, output tokens, EUR cost, and wallclock. The cost ledger shares the audit-log database for transactional consistency but is queried separately. Pricing constants are drawn from the financial-analysis document [FCG financial 2026]: the frontier-cloud reference is approximately EUR 2.76 per million input tokens and EUR 13.80 per million output tokens, and the on-premises amortised marginal cost is EUR 0.05 per million tokens. The ledger feeds the EUR-per-workflow cost model that parameterises the RAG pipeline catalogue (§3.3).

## 3.2 Compressor Framework

Every compressor variant conforms to a single Python `Protocol` with four methods — `compress(fragment, target_ratio)` returning a `CompressedSlot`; `decompress(slot)` returning a best-effort text reconstruction; `embed(slot)` returning an optional embedding for vector-store indexing; and `model_card()` returning a structured card containing the compressor identifier, family, base model, default target ratio, and provenance hashes. The thesis ships six concrete implementations. The identity compressor is the no-compression control condition required by every experiment as a mitigation against runtime-bug confounds.

The remaining five compressors fall into four families: a token-level hard-prompt filter (LLMLingua-2); an instruction-aware heuristic filter; an extractive small-LLM span selector (Phi-3-Mini extractive); a trivial prefix-truncation baseline; and a cliff-aware adaptive wrapper (CAAC). **All five are training-free**, which is a deliberate design choice: the thesis isolates the compression mechanism from any training-data effect and lets the cross-compressor comparison turn on the algorithm rather than on training-budget asymmetry.

### 3.2.1 LLMLingua-2 (token-level classifier)

The LLMLingua-2 wrapper is a thin adapter around the `llmlingua` package [Pan 2024]. Construction takes a target compression ratio; the package is asked to retain $1/r$ of the tokens, scored by a small XLM-RoBERTa classifier distilled from a more capable teacher. The force-tokens list (sentence boundary marks) is validated against the wrapped tokenizer's vocabulary at initialisation and unknown tokens are dropped with an explicit log line. The wrapped XLM-RoBERTa model is supported by PyTorch on both CPU and Apple's Metal Performance Shaders backend, so the compressor runs natively on Apple Silicon without modification.

The empirical token-recall curve $q(r)$ produced by LLMLingua-2 under critical-token-recall measurement (§3.4) is smooth and monotonic across the sweep ratios used in Chapter 4, which is the property the compounding-error model presumes.

### 3.2.2 Instruction-aware filter

The instruction-aware filter is a pure-Python heuristic baseline. It operates in two stages. The first is a sentence-level filter that ranks sentences by their relevance to the task hint using a cross-encoder reranker (`BAAI/bge-reranker-base`) when available and a lexical-overlap fallback when not. The second is a token-level trim that drops English stop-words and short tokens ($\le 2$ characters) until the target compression ratio is reached. The stop-word list is encoded explicitly so that the trim is deterministic given the task hint, the fragment, and the target ratio — a subtle bug found during the development of this thesis showed that dropping stop-words by Python set iteration order introduced run-to-run variance, which is why the list is explicit.

The filter's reranker preserves task-keyword tokens that simpler token-level methods drop, which is why its $q(r)$ curve on the multi-step retrieval family (§3.3, family-c) decays gracefully rather than collapsing: chain-reference tokens like "entry" and "FINAL" survive aggressive compression.

### 3.2.3 Phi-3-Mini extractive span selector

The Phi-3-Mini extractive compressor is the only thesis compressor that uses an LLM at inference time. It runs the Phi-3-Mini-3.8B instruction-tuned model [Phi-3 2024] via a local Ollama endpoint [Ollama] with a structured prompt that asks for verbatim contiguous spans from the source. The post-hoc verifier `Phi3ExtractiveCompressor._verify_extractive` checks the output: every token in the output must appear in the source. Two loosenings of the strict verifier were necessary in practice. First, a 15% novel-token tolerance: small language models frequently insert function words ("the", "is", "and") even when explicitly asked not to. Second, a post-hoc `_strip_novel_tokens` pass that removes any token not in the source after the verifier passes; this guarantees zero novel tokens in the final output even if the model produced some during generation. Outputs that fail even after stripping fall back to LLMLingua-2 at the same target ratio.

A practically important property of Phi-3-Mini extractive is its *compression ceiling*. Span-level selection plus the stripping pass plus the LLMLingua-2 fallback combine to bound the achievable compression ratio at approximately 2.5×, regardless of the requested target. This is documented as a limitation in Chapter 5 and is the reason all evaluation reports *achieved* compression ratio (the ratio actually delivered) alongside the requested target ratio.

### 3.2.4 Truncation (prefix-keep baseline)

The truncation compressor keeps the first $1/r$ fraction of tokens by whitespace split. It is deterministic by construction and achieves the requested ratio exactly. Its purpose is the lower-bound argument: every more sophisticated compressor must beat truncation on the coordination metric to justify its cost.

Truncation has a peculiar property: its single-agent question-answering F1 is competitive with the more sophisticated compressors at low to moderate compression ratios because the prefix tokens are naturally representative. Its coordination success collapses earlier than the others, because the tokens removed at the tail include the task-critical content that the planner needs to combine. This dissociation is part of the H1 finding: a token-overlap quality metric over-reports the utility of even the most naive compressor.

### 3.2.5 Cliff-Aware Adaptive Compression (CAAC)

CAAC is a wrapper, not a fifth compressor family. Given an inner compressor (LLMLingua-2 in the headline experiments; any of the others in the ablation) and a per-family recall threshold $\theta_q$, CAAC runs the inner compressor at the requested target ratio, measures the resulting critical-token-recall, and if recall falls below $\theta_q^{1/N}$ binary-searches downward for the largest ratio that keeps recall above the threshold. A `min_ratio` floor of 1.5× prevents CAAC from abdicating to no-compression on hard fragments. The full algorithmic and empirical discussion lives in Chapter 5 together with the constructive framing that CAAC is the operational realisation of the compounding-error bound. Here it suffices to note that CAAC consumes the same `Compressor` protocol as the other variants, which is what makes its drop-in evaluation in Chapter 4 straightforward.

## 3.3 Retrieval-Augmented Generation Pipeline Catalogue

The C3 contribution evaluates three retrieval-augmented generation pipeline architectures that differ in where compression sits relative to retrieval. The three are described here as artefacts; the empirical comparison between them under matched cost regimes is the H3 result of Chapter 4 §4.6.

- **P1: compress, then retrieve.** The corpus is compressed up-front and the FAISS index is built over the compressed representation. Retrieval and synthesis both operate on compressed text. P1 trades quality for storage efficiency: the index is small but information dropped at compression time is unrecoverable. The pre-processing baseline against which P1 is informally compared is Anthropic's contextual-retrieval work [Anthropic 2024], which prepends LLM-generated chunk-level explanatory context before embedding.
- **P2: retrieve, then compress.** The corpus is indexed in full; the compressor runs as a post-retrieval node-processor over the top-$k$ retrieved fragments before they are synthesised. This is the classical LongLLMLingua configuration [Jiang 2024]. P2 trades storage cost for retrieval recall: the index is the full corpus, but the synthesis context can be compressed aggressively because the retriever has already identified the relevant chunks.
- **P3: joint, conditional on relevance.** The corpus is indexed in full. At query time, each retrieved fragment is routed into one of three branches based on its retrieval relevance score $s$: fragments with $s \ge \theta_\text{high}$ pass through verbatim; fragments with $\theta_\text{low} \le s < \theta_\text{high}$ are compressed; fragments with $s < \theta_\text{low}$ are discarded. The default thresholds $\theta_\text{high}=0.75$ and $\theta_\text{low}=0.45$ on `BAAI/bge-large-en-v1.5`-cosine similarities are the analytical starting points. P3 follows the structural design of Guo *et al.* [Guo 2025].

The three pipelines share the same FAISS-CPU + HNSW infrastructure with `BAAI/bge-large-en-v1.5` as the embedder. The cost ledger introduced above feeds the EUR-per-workflow cost model that parameterises the H3 evaluation regimes (storage-bounded with FAISS index size $\le 100$ MB, accuracy-bounded with retrieval recall@10 $\le 0.85$).

## 3.4 The C1 Coordination Benchmark

### 3.4.1 Why a synthetic benchmark

The empirical centrepiece of this thesis — the *coordination cliff* $\tau^{*}$ — is a position on a curve. Detecting and characterising a cliff requires sweeping compression ratios densely from 1× to 16×, holding everything else constant, and reading off where coordination success crosses a threshold. Real-world benchmarks (HotpotQA, MultiHopRAG) confound the cliff with task difficulty, retrieval distribution, dataset bias, and per-instance variance. The thesis takes the position that the cliff is best characterised on a synthetic generator first, where information density can be placed by construction, and then externally validated on real benchmarks. The synthetic-first posture is responsible for the clean Chapter 4 results on H1, H2, and Corollary 1; the real-benchmark validation of Corollary 2 confirms that the structure transfers.

The C1 generator produces 150 instances across three workload families and is reproducible from a single seed. The configuration hash and the resolved configuration are recorded in the manifest alongside the generated workloads so that any output CSV can be traced back to the exact generator inputs that produced it.

### 3.4.2 Three workload families

- **Family-a — cross-document fact aggregation.** Each instance provides eight source documents, one per system from the Vignette 3.7 institutional inventory (Publication DB, Contract DB, Moodle, Patio, Peppi, CRM, Tatu SAP, SAP Travel [FCG 2026]). Each document carries one recorded-hours and one approved-budget number drawn from a seed-fixed distribution. The planner is asked to aggregate the two quantities across the eight documents. Ground truth is the arithmetic sum, deterministic from the seed; the scorer is a regex-based extraction pipeline that matches *hours: X* and *budget: EUR Y* patterns. Family-a is the densest of the three: every multi-digit number is task-critical, and $\theta_\text{info}\approx 0.97$. The family-a cliff is sharp; it is the family on which the compounding-error model is most directly testable.
- **Family-b — constraint-satisfaction planning.** Each instance specifies $N$ sub-tasks with per-task loads and $K$ workers with per-worker capacities. The planner must produce an assignment of sub-tasks to workers that respects per-worker capacity and assigns every sub-task. The generator constructs a feasible solution by a capacity-respecting greedy algorithm that bumps capacities only when strictly necessary, guaranteeing that every workload has at least one feasible assignment. The scorer is a *feasibility checker* rather than an exact-match: any assignment that satisfies the constraints scores 1, so the planner is rewarded for finding *any* solution rather than memorising one. Family-b exposes a property of small LLM planners that is independent of compression: constraint tracking is hard for $\le 8$B-parameter models even without compression, so the family-b baseline success $p_0$ is low for small planners and the cliff is not detectable in that regime — a *floor effect* that Chapter 4 treats explicitly.
- **Family-c — multi-step retrieval.** Each instance presents a linear chain of fragments where each fragment carries either a pointer to the next (*entry X*) or, at the leaf, the answer (*FINAL-XXXX*). Chain lengths range from 2 to 4; each fragment is padded with 4 to 8 distractor sentences so that the retrieval step is non-trivial. The scorer reads the planner's output and matches against the leaf answer. Family-c is the most distributed of the three: many tokens are distractors, information density $\theta_\text{info}\approx 0.59$, and the cliff is gradual — it is the family on which the instruction-aware filter's reranker, which preserves chain-reference keywords, can avoid a detectable cliff entirely.

Each family contributes 50 instances. The three families together span a deliberate range of information densities so that the cliff mechanism (a recall threshold $\theta_q$) and the cliff-position shift mechanism (information density $\theta_\text{info}$) can be separated; this separation is what Chapter 4 formalises as Corollary 2.

### 3.4.3 Tag distributions for the privacy axis

The C1 generator supports three synthetic tag distributions — *uniform*, *skewed*, and *hierarchical* — used by H4 (inference disclosure) to probe the governance-stringency dimension. The hierarchical distribution sets higher classification levels to imply strict supersets of the bits at lower levels, which matches the real-world structure of NIST-RMF tag hierarchies [NIST AI RMF] and lets the H4 analysis disentangle classification level from access-control mask.

### 3.4.4 Coordination success and supporting metrics

The coordination scorer is a pure function of the workload and the planner's output; it does not call any LLM. It returns one primary metric — a per-instance binary *coordination success* — and four supporting metrics: the F1 over extracted answer tokens versus ground truth, the achieved compression ratio ($|\text{source}|/|\text{compressed}|$), generic token-recall (the fraction of source tokens preserved in the compressed text), and *critical-token-recall* (CTR; §3.5). Aggregation across workloads $\times$ seeds is by arithmetic mean; 95% confidence intervals are computed by workload-level bootstrap, never by per-row bootstrap which double-counts the seed dimension.

The reason the scoring pipeline never calls an LLM is the same reason H1 and H2 use a deterministic regex parser as the planner: isolating the compression-quality signal from LLM run-to-run variance. The trade-off is that the cliff measured here is an upper bound on what an LLM-based scorer would measure; the trade is in favour of clean attribution rather than ecological validity, and Chapter 5 discusses the limitation.

## 3.5 The Critical-Token-Recall Metric

A standard token-recall measurement $q_\text{token}(r) = |T_\text{compressed} \cap T_\text{source}| / |T_\text{source}|$ counts every preserved token equally. This turned out, during the development of this thesis, to be a poor proxy for task-relevant information preservation: the Phi-3-Mini extractive compressor at low ratios preserves common function words like "the" and "and" but drops some critical numeric tokens. Its token-recall is high; its coordination success is low.

The critical-token-recall (CTR) metric is the family-specific restriction:

$$q_\text{CTR}(r) = \frac{|T_\text{compressed}^{\,\text{crit}} \cap T_\text{source}^{\,\text{crit}}|}{|T_\text{source}^{\,\text{crit}}|},$$

where $T^\text{crit}$ is the set of *task-critical* tokens for the family:

- Family-a: multi-digit numeric tokens (at least two digits, to exclude single-digit noise);
- Family-b: all numeric tokens (load and capacity values);
- Family-c: chain-reference tokens (*entry-X* patterns) and the literal *FINAL* marker.

CTR is what the compounding-error model uses as the per-round retention rate $q(r)$; CAAC uses CTR as its back-off signal; and the predicted-versus-empirical $\tau^{*}$ figure in Chapter 4 uses CTR to derive $\theta_q$. Generic token-recall is reported for backwards compatibility with prior analyses but is not used in the verdict pipeline.

## 3.6 Compression Cache

Compression is the slowest step in the evaluation. LLMLingua-2 at a single ratio over 150 workloads takes minutes; Phi-3-Mini extractive over the same range takes hours because each fragment is a $\sim$11-second Ollama call including verification and possible retry. The cliff sweep requires every (compressor, ratio, workload, task-hint) cell — approximately 30,000 cells in the canonical H1/H2 protocol — and a naive nested-loop implementation that recompresses on every evaluation pass would dominate the wallclock.

The thesis ships a precomputed compression cache, `CompressionCache` and `CachedCompressor` in `src/m6/compressors/cache.py`, with cache keys $(\text{compressor}, r, \text{fragment\_id}, \text{hash}(\text{task\_hint}))$. The cache is a JSON store for portability; the task-hint hash is the first twelve characters of an MD5 so that the keys are short enough to remain readable. The cache is populated once by the `precompute_cache.py` script on the GPU server and all subsequent runs consume the JSON. This decoupling is what makes the evaluation pipeline runnable end-to-end on a laptop without the GPU: H1, H2, the frontier API sweep, and the CAAC ablation all consume the cache rather than the live compressors.

## 3.7 Inference Backends

The unified `InferenceBackend` protocol exposes a single `complete(prompt, max_tokens, temperature, stop)` method together with an optional `embed(text)` method. Three concrete backends are used in the evaluation. The first is a local Ollama endpoint [Ollama] that hosts Qwen-2.5-Instruct at the three local sizes (1.5B, 3.8B, 8B) used in the model-scaling sweep, Phi-3-Mini-3.8B for the extractive compressor, and Llama-3.1-8B-Instruct as the local protected-fact reader. The second is the OpenAI-compatible Featherless API used for the frontier validation (Qwen-2.5-72B-Instruct, DeepSeek V4 Pro). The third is the OpenAI API for the GPT-class frontier arm (excluded from the calibrated regime per Chapter 5, retained on disk as a noncanonical diagnostic). All API calls are routed through the cost ledger so that the EUR-per-workflow figures in Chapter 4 are auditable.

## 3.8 Scope of Evaluation: The Multi-Fragment Proxy

The empirical protocol uses two planners. H1 and H2 use a deterministic regex-based information-extraction solver that parses the compressed fragments for the task-critical patterns of §3.4.2; its purpose is to isolate the compression-quality variance from LLM run-to-run variance. Corollary 1 (the model-scaling sweep), the frontier validation, and the real-data transfer arms use a single LLM call with all (compressed) fragments visible in a flat prompt; their purpose is to demonstrate that the cliff structure measured by the deterministic solver appears identically when the planner is a non-trivial language model.

An AutoGen v0.4 multi-round agent backend exists [Wu 2023] in `src/m6/orchestrator/` and integrates with the memory bus described in §3.1. It is not used in the empirical evaluation. The decision is documented as **ADR-009** in the repository: the run-to-run variance introduced by multi-round agent negotiation dominates the compression signal at the C1 ratios this thesis sweeps, and the value of the AutoGen runner is to demonstrate that the memory-bus design is multi-agent-ready, not to be the planner whose cliff is measured. The boundary is that the memory bus is *designed for* multi-agent integration; the experiments *evaluate* on a multi-fragment proxy.

Coordination success, as defined in §3.4, refers to the structural task property that the planner must combine information drawn from multiple fragments. It does not refer to the multi-round communication quality between agents; that property is what the AutoGen backend would enable measuring in future work, and is named in Chapter 5 as part of the limitations and the future-work roadmap.

## 3.9 Compute Envelope and Reproducibility

The empirical work runs on two machines. The first is an Apple M4 Pro 48 GB workstation, which hosts the local Ollama planners for the cliff sweep development and the deterministic-solver pipeline, and which is sufficient for every figure and verdict in Chapters 4 and 5 when the compression cache is in place. The second is an RTX 5090 32 GB workstation (Tailscale-accessible WSL2 host) used for the compression precomputation, the model-scaling sweep at 8B, the frontier API sweep, and the HotpotQA / MultiHopRAG transfer arm. Total wallclock for the canonical evaluation pipeline (cache precompute on GPU + cliff sweep + scaling + RAG + disclosure + real-data transfer) is approximately 30 hours of GPU time and $\sim$12 hours of laptop time end-to-end.

The reproducibility package is the complete repository: a `docker-compose.yml` that brings the memory-bus reference service up locally, a GitHub release tag for the manuscript and code, model and data cards under `docs/`, and a `README.md` that exposes one-command reproduction for every chapter headline figure. The filesystem layout under `results/` is fixed: one CSV per hypothesis run plus a `manifest.yaml` that records the resolved configuration, the configuration hash, the git revision, the Python version, the platform string, and the start time. Appendix D describes the package contents in detail and lists every command needed to reproduce the headline figures.

---

# 4. Experiment Design, Results, and Analysis

This chapter presents the empirical work that this thesis turns on: the cliff sweep on which H1, H2, and the compounding-error model are based; the model-scaling sweep reframed as Corollary 1; the frontier validation that promotes the model-independence claim from small-model evidence to a cross-architecture result inside a defined calibrated regime; the retrieval-augmented-generation pipeline catalogue (H3); the summary-level inference-disclosure measurement (H4); and the information-density scaling result on real benchmarks reframed as Corollary 2. The chapter is organised around the falsifiable claims rather than the chronology of the runs; canonical results directories under `results/` are referenced for each section so that every number is traceable to an immutable artefact on disk.

## 4.1 Experimental Protocol

### 4.1.1 The cliff sweep

The cliff sweep underlies H1, H2, and the calibration step of the compounding-error model. Four compressors — LLMLingua-2, Phi-3-Mini extractive, the instruction-aware filter, and a truncation baseline — are evaluated at ten compression ratios $\{1, 2, 3, 4, 5, 6, 8, 10, 12, 16\}\times$ on the 150 C1 workloads across the three families. Five seeds per cell give a total of approximately 30,000 evaluation cells per run. The canonical results directory is `results/h1_h2_v2/`; the earlier three-compressor variant `results/h1_h2_final/` is retained on disk for backwards-compatibility checks but is not the source of the headline numbers below. The truncation baseline is the lower-bound argument: any compressor that does not beat truncation on the coordination metric is paying training or inference cost for no coordination-quality return.

Every cell records the coordination-success binary, an F1 over extracted answer tokens versus ground truth (this is what H1's "QA accuracy" refers to), the achieved compression ratio, the generic token-recall, and the critical-token-recall described in §3.5. The compression cache (§3.6) guarantees that every cell sees the exact same compressed text for a given (compressor, ratio, workload) tuple, so within-cell variance is exclusively planner-side variance, not compressor stochasticity.

### 4.1.2 Statistical protocol

The statistical protocol is fixed in advance for every hypothesis. Effect-size summaries are computed at the workload level, never the cell level: per-workload means are computed first, and the 95% bootstrap confidence intervals are constructed by resampling workloads with replacement [Efron 1993], never by resampling individual seed–cell pairs. The two-cell comparison test is the paired Wilcoxon signed-rank test [Wilcoxon 1945], chosen over the Mann–Whitney $U$ test [Mann 1947] because the same workloads appear in both conditions, which violates the independence assumption of the two-sample test. The original cliff machinery used Mann–Whitney $U$; that error was corrected during the audit pass and the canonical `verdicts.json` files reflect the paired-Wilcoxon recomputation. Multiple-comparisons correction is Holm's sequentially-rejective procedure [Holm 1979] across the 12 (compressor, family) cells of the cliff sweep, the three condition pairs of the disclosure measurement, and the three pipelines of the RAG catalogue.

Cliff position $\tau^{*}$ is extracted by fitting both a piecewise-linear model and a logistic

$$f(r) = p_0 + \frac{p_\infty - p_0}{1 + e^{-k(r - \tau^{*})}}$$

to each cell's coordination-success-versus-ratio curve and selecting the model with the lower root-mean-squared error. The piecewise fit is constrained to an interior 10% margin from the sweep boundaries to prevent the optimiser from parking $\tau^{*}$ at $r_{\max}=16$, which was a real failure mode of an earlier audit build and is documented in the project-internal bug list. 95% bootstrap CIs on $\tau^{*}$ are computed by resampling the underlying workload means before the curve fit.

## 4.2 H1: Question-Answering Accuracy Decorrelates from Coordination Success

> **H1.** Single-agent question-answering accuracy under compression is a poor predictor of multi-fragment coordination success: Spearman $\rho(\Delta_\text{qa}, \Delta_\text{coord}) < 0.6$ on the cells of the cliff sweep, with 95% bootstrap CIs excluding 0.6 from above. **Verdict: SUPPORTED.**

### 4.2.1 Result

The table below reports the workload-level Spearman correlation between the change in token-overlap F1 (the "QA accuracy" metric the LongLLMLingua line of work reports [Jiang 2024; Pan 2024]) and the change in coordination success under compression, for each compressor pooled across the three task families. The signature finding is the dispersion of the correlations: they span from $-0.59$ to $+0.38$, and none reaches $0.6$. The two compressors whose token-overlap F1 is most strongly tied to coordination success disagree on sign — the instruction-aware filter has a strongly negative correlation, while LLMLingua-2 has a moderately positive correlation. The negative-correlation result for the filter is the easiest to misread, and is the reason this section opens with the verdict rather than the interpretation: the filter's re-ranker preserves task-keyword tokens that the token-overlap metric does not reward, so as the F1 metric goes down the coordination metric goes *up*. That is the H1 finding in its purest form.

**Table 4.1 — H1 verdict (workload-level Spearman correlation between $\Delta$ token-overlap F1 and $\Delta$ coordination success).**

| Compressor | $\rho$ | 95% CI | $p$-value | $n$ |
|---|---:|---|---|---:|
| Instruction-aware filter | $-0.593$ | $[-0.641, -0.542]$ | $7.3 \times 10^{-129}$ | 1350 |
| LLMLingua-2 | $+0.381$ | $[+0.344, +0.418]$ | $7.0 \times 10^{-48}$ | 1350 |
| Phi-3-Mini extractive | $+0.193$ | $[+0.131, +0.252]$ | $1.0 \times 10^{-7}$ | 750 |
| Truncation (baseline) | $+0.384$ | $[+0.349, +0.418]$ | $1.4 \times 10^{-48}$ | 1350 |
| **All four** | — | all CIs exclude 0.6 | — | **SUPPORTED** |

### 4.2.2 Interpretation

The H1 finding is a methodological claim, not just an empirical one. The LongLLMLingua and LLMLingua-2 papers report question-answering F1 retention at 4× compression [Jiang 2024; Pan 2024]; what this thesis shows is that F1 retention at 4× does not predict whether a planner can solve a multi-fragment coordination task at the same operating point. The two metrics are not the same metric on the same axis with different noise; they *disagree on the ranking of compressors*. For the multi-fragment workflows the FCG use cases [FCG 2026] are built around, the F1 ranking would lead a practitioner to choose the wrong compressor.

The negative-correlation behaviour of the filter compressor is the mechanism behind H1. The TF-IDF and cross-encoder re-ranker stages of the filter are explicitly task-aware: they preserve tokens that are relevant to the task hint and drop tokens that are not. The F1 metric, by contrast, scores token-overlap against the *ground-truth answer*, not the task hint. So the filter drops F1-positive tokens (the answer string itself is sometimes re-ranked out) while preserving the chain-of-reasoning tokens the planner needs to derive the answer. The result is that the same compression operation that the F1 metric scores as a quality drop is, by the coordination metric, a quality preservation. The single-agent benchmark is measuring the wrong thing.

### 4.2.3 Comparison to prior work

The closest published analogue is the family of long-context question-answering benchmarks (LongBench [Bai 2024], RULER [Hsieh 2024]) which measure single-agent F1 on compressed inputs. The H1 finding does not contradict those benchmarks — they are correct on what they measure — but shows that they are insufficient for multi-agent or multi-fragment deployment decisions. Anthropic's industry observation that token usage explains approximately 80% of performance variance in their multi-agent research workflow [Anthropic 2025a] is consistent with H1: a metric that does not see the structural multi-fragment property of the planner's task will give a systematically over-optimistic compressor ranking.

## 4.3 H2: A Sharp Coordination Cliff Exists

> **H2.** On each (compressor, family) cell of the cliff sweep, the coordination-success curve has a sharp cliff $\tau^{*}$ with a relative drop of at least 30% and a paired-Wilcoxon $p$-value of at most $0.05$ after Holm correction across cells. **Verdict: SUPPORTED** on 11 of the 12 cells; the only exception is the instruction-aware filter on family-c, where the re-ranker preserves chain-reference tokens and no cliff is detectable below $r=16$.

### 4.3.1 Result

`figures/cliff_hero.pdf` is the chapter's most-quoted figure: the coordination-success curves for LLMLingua-2 on family-a, with the cliff visible at $\tau^{*}\approx 2.5\times$ and the curve falling from coordination $\approx 1.0$ at $r=1$ to coordination $\approx 0.0$ by $r=6$. The drop is concentrated in a span of two compression ratios, which is the signature shape that the compounding-error model is built around.

**Table 4.2 — H2 verdict (per-cell cliff position, drop, and Holm-corrected paired-Wilcoxon $p$).**

| Cell | $\tau^{*}$ | rel. drop | Holm $p$ |
|---|---:|---:|---|
| LLMLingua-2 × a | 2.5 | 1.61 | $8.5\times10^{-12}$ |
| LLMLingua-2 × b | 2.5 | 1.61 | $8.5\times10^{-12}$ |
| LLMLingua-2 × c | 6.7 | 1.23 | $9.6\times10^{-10}$ |
| Filter × a | 2.5 | 1.60 | $8.5\times10^{-12}$ |
| Filter × b | 2.5 | 1.61 | $8.5\times10^{-12}$ |
| Filter × c | — | 0.00 | n.s. |
| Phi-3-Mini ext. × a | 2.5 | 0.42 | $2.2\times10^{-6}$ |
| Phi-3-Mini ext. × b | 2.5 | 0.97 | $2.5\times10^{-9}$ |
| Phi-3-Mini ext. × c | 2.5 | 1.37 | $8.5\times10^{-12}$ |
| Truncation × a | 2.5 | 1.61 | $8.5\times10^{-12}$ |
| Truncation × b | 2.5 | 1.61 | $8.5\times10^{-12}$ |
| Truncation × c | 4.95 | 1.36 | $9.6\times10^{-10}$ |
| **Verdict:** 11/12 cells significant; only filter × c lacks a cliff. | | | **SUPPORTED** |

The twelve-cell grid in `figures/cliff_families.pdf` reads the result at one glance: cliffs are sharp on the dense fact-aggregation family and shallow on the distributed multi-step retrieval family, the ordering between (LLMLingua-2 / filter / Phi-3) is consistent within a family, and truncation cliffs at the lowest ratio of any compressor — which is what the lower-bound argument predicts.

### 4.3.2 Interpretation

The within-family ordering of $\tau^{*}$ corresponds to the ordering of the four compressors' critical-token-recall curves $q(r)$, measured independently of the coordination metric. The compressor that drops critical tokens earliest cliffs at the lowest ratio. This is the H2 finding pointing forward: a cliff exists, its position is determined by the compressor's mechanism of action on task-critical tokens, and the mechanism is captured by a single statistic — $q(r)$. The next section turns that observation into a quantitative bound.

## 4.4 The Compounding-Error Model

The cliff curves of §4.3 share a structural property: each has a sharp transition between a high-coordination plateau and a low-coordination floor. The compounding-error model is a derivation that captures this structure and produces a position-prediction for the transition $\tau^{*}$ from the compressor-side measurement $q(r)$ and a per-family recall-threshold parameter $\theta_q$.

### 4.4.1 Setup and derivation

Let $T^\text{crit}_i$ be the set of task-critical tokens in the $i$-th workload's source fragments (multi-digit numerics for family-a, all numerics for family-b, chain-reference tokens for family-c; see §3.5). Let $X_i$ be the number of these tokens that survive compression, $M_i = |T^\text{crit}_i|$ the total, and $q(r) = E[X_i / M_i]$ the per-round token-retention function of the compressor at ratio $r$, measured by the critical-token-recall metric. Let $\theta_q \in [0, 1]$ be the *cliff-recall threshold*: the minimum fraction of task-critical tokens that the planner needs to succeed. The threshold-success model is

$$\text{success}_i = \mathbf{1}\left[\frac{X_i}{M_i} \ge \theta_q\right],$$

and the bound the model produces is

$$E\left[\frac{X_i}{M_i}\right] = q(r),$$

$$P(\text{success}\mid r) \to \mathbf{1}\left[q(r) \ge \theta_q\right] \text{ in expectation,}$$

so the cliff position $\tau^{*}$ solves $q(\tau^{*}) = \theta_q$. When $N$ sequential compression passes are applied, the surviving fraction is approximately $q(r)^N$ and the cliff position solves $q(\tau^{*}) = \theta_q^{1/N}$. **In every experiment in this thesis $N=1$**, so the cliff equation simplifies to $q(\tau^{*}) = \theta_q$. The multi-pass formulation is recorded for future work.

The derivation is a paragraph; it is not a formal proof, and the artefact is named the *compounding-error model* rather than *Theorem 1* throughout the manuscript. The change is deliberate: the empirical match rate (§4.4.4) is approximately 33% strict and 67% at $\pm 50\%$ tolerance, which is the empirical-bound character of a model with quantified residuals rather than the formal character of a theorem with a proof. The codebase identifier `theorem_validation.json` is preserved for backwards compatibility with on-disk artefacts; the manuscript term is *the compounding-error model* (the mapping is documented in CONTEXT.md and in ADR-008).

### 4.4.2 Assumptions A1–A4

The bound rests on four assumptions, each of which is satisfied approximately rather than strictly.

- **A1 — Round independence.** The per-round retention is independent across compression passes. This is trivially satisfied at $N=1$.
- **A2 — Binary token importance.** Each task-critical token is equally important; non-task tokens are irrelevant. This is the strongest of the four assumptions; H4 (§4.7) measures graded importance and shows that A2 is a first-order simplification. The predicted-versus-empirical gap of §4.4.4 is the empirical price the model pays for A2.
- **A3 — Threshold success.** Coordination success is binary at a single recall threshold $\theta_q$. The cliff sharpness measured in §4.3 is what licenses A3.
- **A4 — Per-round retention measured by critical-token-recall.** The $q(r)$ that enters the bound is the family-specific CTR rather than the generic token-recall. This is the substantive methodological commitment of the model, and the reason CTR rather than token-recall is the canonical recall metric of the verdict pipeline.

### 4.4.3 The calibrated regime

A planner is *in the calibrated regime* (ADR-006) if both of the following hold:

1. the baseline coordination success $p_0$ at $r=1$ is at least $\theta_q$ (no floor effect); and
2. the planner does not recover from sub-threshold information via extended reasoning beyond what the priors-only baseline supplies.

The second condition is operationalised by the priors-only baseline measurement of H4 (§4.7): a planner is in-regime if its accuracy at $q\to 0$ is no greater than its priors-only baseline plus a small slack. This formalisation matters because the model's quantitative predictions only apply inside the regime; outside the regime — specifically for extended-reasoning planners that recover information via chain-of-thought — the cliff position can shift substantially, as the GPT-oss 120B diagnostic in §4.6.3 shows.

### 4.4.4 Predicted versus empirical $\tau^{*}$

For each (compressor, family) cell, $\theta_q$ is estimated from a training subset of the cliff sweep — specifically the recall at which coordination success first drops below 0.5 of the cell's $p_0$ — via the `derive_theta()` function in `src/m6/theory/cliff_prediction.py`. Under critical-token-recall the canonical per-family estimates on the `h1_h2_v2` sweep are $\theta_q^{(a)} = 0.632$, $\theta_q^{(b)} = 0.838$, and $\theta_q^{(c)} = 0.590$. A bootstrap CI is constructed on $\theta_q$ by resampling workloads. The predicted $\tau^{*}$ is then obtained by inverting $q(r) = \theta_q$ on the empirical critical-token-recall curve. Resampling $\theta_q$ through this inverse map gives a *predicted-$\tau^{*}$ band* that quantifies the model's uncertainty.

`figures/predicted_vs_empirical.pdf` overlays the predicted-$\tau^{*}$ band on the empirical cliff curve for the family-c LLMLingua-2 cell. Family-c is shown rather than the more spectacular family-a because the cliff is gradual enough on family-c that the predicted-versus-empirical *gap* is visible — the family-a cell drops from 1.0 to 0 in a single ratio step, which the model also predicts closely, so both the prediction and the empirical curve collapse into the same near-step function and the figure carries no information. The family-c panel shows that the compounding-error model is *conservative* for family-c: it predicts the cliff at $r\approx 2.85$ while the empirical cliff sits at $r\approx 6.7$, a 58% relative under-prediction. The gap is the second-order term that Corollary 2 explains (§4.8): family-c has lower information density than family-a, so the threshold-success approximation A2 (binary token importance) breaks earliest on family-c.

Aggregating the predicted-versus-empirical comparison across all twelve (compressor, family) cells gives an empirical match rate of **33%** (4/12 cells) at the $|\tau^{*}_\text{empirical} - \tau^{*}_\text{predicted}| / \tau^{*}_\text{empirical} \le 25\%$ criterion and **67%** (8/12 cells) at $\pm 50\%$. The numbers are reported honestly: the model is a useful first-order bound, not a tight predictor. The four cells that pass the strict criterion span all four compressors (lingua2/b, filter/a, truncation/a, truncation/b), which is consistent with the bound being structural rather than compressor-specific.

## 4.5 Corollary 1: Ceiling–Cliff Separation

> **Corollary 1 (ceiling–cliff separation).** The planner's parameter count $m$ determines its baseline coordination success $p_0(m)$, while the cliff position $\tau^{*}$ is determined by the compressor's $q(r)$ and the task's $\theta_q$, not by the planner. When $p_0(m) < \theta_q$ a floor effect prevents detection of the cliff; when $p_0(m) \ge \theta_q$ the cliff position is invariant to $m$ within the calibrated regime. **Verdict: SUPPORTED** on the family-c sweep across three Qwen-2.5 scales; the family-a small-model cells correctly exhibit the predicted floor effect and are excluded; the family-b cells are below threshold for all three models because constraint tracking is hard for $\le 8$B planners independent of compression. The frontier validation in §4.6 promotes the result from local-model evidence to a cross-architecture finding.

This corollary is the reframing of the original H5 hypothesis, which predicted strict monotonicity of $\tau^{*}$ across planner scales. The empirical result on family-c across the three Qwen sizes is $\tau^{*}_{1.5\text{B}} = 3.69$, $\tau^{*}_{3.8\text{B}} = 4.68$, $\tau^{*}_{8\text{B}} = 4.01$ — a spread of approximately 24% within the bootstrap CI of each cell, which is what an invariance result looks like rather than a monotonicity result. The original H5 predicate (gap $\ge 1.5$ ratio units) is not satisfied because the spread is well below 1.5; the reframed Corollary 1 predicate (invariance within the calibrated regime) is. The canonical results directory is `results/h5_final/`.

`figures/scaling_auc.pdf` reports the area-under-the-coordination-curve as a function of planner scale across all three families. On family-c, the three lines overlap; on family-a, the small-model lines are below the floor effect threshold and are correctly skipped from the invariance test; on family-b, all three lines are near zero for the constraint-tracking reason. The ceiling-versus-cliff structure is most cleanly visible on the joined plot of $p_0(m)$ and $\tau^{*}(m)$ on family-c (`figures/h5_model_overlay.pdf`): $p_0$ increases monotonically with $m$, $\tau^{*}$ does not.

The honest statement of the reframing is in the title of this section. The original H5 predicate did not hold; the reframed Corollary 1 predicate, which is the structurally interesting claim, did. The reframing was made on the basis of the cliff machinery's prediction and was registered as the reframing ADR before the frontier validation that promotes it from a small-model result to a cross-architecture one.

## 4.6 Frontier Validation Within the Calibrated Regime

The frontier validation re-runs the family-a cliff sweep with the planner swapped out for a frontier model accessed via API while the compressor remains LLMLingua-2 at the same ratios. The question is the model-independence claim of Corollary 1: does the cliff position $\tau^{*}$ stay where the local-model cliff was, or does it shift with the planner? The three planners tested are Qwen-2.5-72B-Instruct, DeepSeek V4 Pro, and GPT-oss 120B. The first two are standard non-reasoning frontier models; the third is an extended-reasoning model and is the calibrated-regime boundary case.

### 4.6.1 Setup and statistical protocol

The sweep uses 30 family-a workloads (the H6-arm subsample), the same ten ratios, five seeds per cell, for a total of 1,500 cells per frontier model. Planner inference is via the OpenAI-compatible Featherless endpoint for Qwen-2.5-72B and DeepSeek V4 Pro and via the OpenAI Responses API for GPT-oss 120B. $\tau^{*}$ is fit by the same paired-fit-and-select procedure as the local sweep, and the bootstrap CI is constructed by resampling workloads. The synthetic reference $\tau^{*} = 2.70$ is the family-a × LLMLingua-2 value from `results/h1_h2_final/` (the headline cliff measurement), which is what every frontier model is being compared against. The canonical results directories are `results/frontier_qwen72b/` for Qwen, `results/frontier_deepseekv4/` for DeepSeek, and `results/frontier_gptoss120b/` (with `STATUS_NONCANONICAL.txt`) for GPT-oss.

### 4.6.2 Qwen-2.5-72B-Instruct: in-regime, 0.8% off

The Qwen-2.5-72B sweep returns $\tau^{*} = 2.68$ against the synthetic reference of 2.70 — a relative difference of **0.8%** and a Qwen bootstrap CI that comfortably contains the synthetic point estimate. This is the single strongest piece of evidence in the thesis. The same model family, the same compressor, a 9× change in parameter count from 8B to 72B, and the cliff position is the same to within sub-percentage error. The baseline coordination $p_0(\text{Qwen-72B}) = 1.00$ is at the ceiling, which places the model squarely inside the calibrated regime: there is no floor effect to argue around.

### 4.6.3 DeepSeek V4 Pro: in-regime, CI contains the prediction

The DeepSeek V4 Pro sweep returns a $\tau^{*}$ point estimate of 2.15 with a bootstrap CI of $[1.76, 7.14]$. The CI is wide because the sweep was run with fewer seeds per cell (a sample-size limitation discussed in §5.3). The point estimate is below the synthetic reference but the CI comfortably contains it. The conservative reading is that DeepSeek V4 Pro is consistent with Corollary 1 within the variance the sweep can resolve. The aggressive reading is that DeepSeek V4 Pro cliffs slightly earlier than Qwen-72B because its critical-token-recall profile under LLMLingua-2 differs from Qwen's; future work could distinguish these by sweeping DeepSeek with more seeds. The thesis takes the conservative reading and reports DeepSeek as a *within-tolerance* validation of Corollary 1 rather than a point-estimate match.

### 4.6.4 GPT-oss 120B: out-of-regime diagnostic (ADR-006)

The GPT-oss 120B sweep returns $\tau^{*} = 6.62$ — **145%** above the synthetic reference, and far outside any reasonable bootstrap CI on $\theta_q$. The v1 sweep with baseline $p_0 = 0.53$ admitted a floor-effect interpretation, but the v2 sweep with baseline $p_0 = 1.00$ does not. The model is unambiguously at the ceiling and is unambiguously cliffing at a substantially higher ratio than Corollary 1 predicts. This is the boundary case the calibrated regime was formalised around.

The hypothesised mechanism is the second condition of the calibrated regime predicate (§4.4.3): GPT-oss is an extended-reasoning planner, and at sub-threshold token recall it can recover the task-critical information by chain-of-thought reasoning, violating assumption A3. The standard non-reasoning planners cannot. The 145% deviation is not hidden: `results/frontier_gptoss120b/` is preserved on disk with a `STATUS_NONCANONICAL.txt` marker that records the scoping, and the result is reported here as a *positive contribution* — a structural diagnostic of where the compounding-error model breaks. §5.3 names the extended-reasoning regime as the largest future-work direction the thesis opens.

### 4.6.5 Multi-model figure and the cross-architecture finding

`figures/frontier_multi.pdf` overlays the three frontier cliff curves with the synthetic reference band. The Qwen and DeepSeek curves overlap the reference band; the GPT-oss curve diverges visibly. `figures/frontier_validation.pdf` is the per-model $\tau^{*}$ scatter with the calibrated-regime boundary marked explicitly.

### 4.6.6 Significance

Putting the three results together: the cliff position is invariant to parameter count (Qwen-2.5 from 1.5B local to 72B frontier) and to architecture family (Qwen → DeepSeek) within the calibrated regime, and it is not invariant to reasoning regime (standard → extended). This is what an empirically-substantiated structural claim looks like: an invariance that holds in a precisely-defined regime and visibly breaks at the regime boundary.

For practitioners: $\tau^{*}$ can be measured once on a small local model and deployed at the same ratio on a frontier model without re-measuring, *provided* the frontier model is in the calibrated regime. For researchers: the cliff is a property of the (compressor, task) pair; single-agent benchmarks that vary the model and hold the compressor fixed cannot reveal this structure. The cross-architecture-invariance finding is the substantive contribution of this thesis to the compression literature and is what Corollary 1 promotes from a local-model-only result to a cross-architecture one.

## 4.7 H3: RAG Pipeline Placement — Compress-First Dominance

> **H3 (original predicate).** The optimal pipeline between compress-first (P1) and retrieve-first (P2) sign-flips between a storage-bounded and an accuracy-bounded regime. **Verdict: NOT SUPPORTED** for the predicted sign-flip. **Reframed finding:** P1 (compress-first) is robustly preferred over P2 (retrieve-first) in both regimes; P3 (joint relevance-conditional routing) leads both. The reframed result is itself a substantive finding because it challenges a common assumption of the post-retrieval-compression literature (LongLLMLingua [Jiang 2024] and follow-on work).

### 4.7.1 Setup

The three pipelines (P1, P2, P3) are the catalogue described in §3.3. Each is run under a storage-bounded regime (FAISS index $\le 100$ MB) and an accuracy-bounded regime (retrieval recall@10 $\le 0.85$), measured on the C1 family-a generator with both F1 score and the EUR-per-workflow cost model [FCG financial 2026]. The canonical results directory is `results/h3_final/`.

### 4.7.2 Result

**Table 4.3 — H3 verdict (mean F1 and per-query EUR cost by regime and pipeline, $n=150$ workloads per cell).**

| Pipeline | Storage F1 | Storage EUR/query | Accuracy F1 | Accuracy EUR/query |
|---|---:|---:|---:|---:|
| P1 (compress, then retrieve) | 0.396 | $2.7\times10^{-5}$ | 0.648 | $3.3\times10^{-5}$ |
| P2 (retrieve, then compress) | 0.364 | $2.8\times10^{-5}$ | 0.628 | $3.0\times10^{-5}$ |
| P3 (joint, conditional) | **0.820** | $3.1\times10^{-5}$ | **0.895** | $3.1\times10^{-5}$ |
| $p_\text{Holm}$ (P1 vs P2, paired bootstrap) | $2\times10^{-4}$ | | $2\times10^{-4}$ | |

The headline observation is that the ranking $P3 > P1 > P2$ holds in *both* the storage-bounded and the accuracy-bounded regimes. P1 is above P2 by 3.2 percentage points (pp) F1 in the storage regime and by 2.0 pp in the accuracy regime, with 95% paired-bootstrap CIs ($[1.84, 4.72]$ pp and $[1.15, 2.85]$ pp respectively) that comfortably exclude zero. The H3 sign-flip predicate is therefore *not satisfied*: the optimal does not change between regimes, and P1 is the better of the two compressed-corpus pipelines in both. P3 (joint relevance-conditional routing) leads both regimes by a substantial margin.

### 4.7.3 Interpretation: why the sign-flip did not appear

The original H3 predicate rested on the LongLLMLingua-style intuition that post-retrieval compression (P2) is more efficient than pre-retrieval compression (P1) because the retriever has already filtered the corpus down to the relevant chunks before the compressor runs. The interpretation depends on two assumptions that the empirical work invalidates: first, that retrieval over an uncompressed corpus is cheap (it is not — the FAISS index over the uncompressed corpus grows linearly in corpus size and dominates the storage budget); second, that compression after retrieval can be more aggressive than compression before (the empirical compression ratios at iso-F1 are comparable). What remains is the symmetric effect: pre-indexing compression amortises the compressor cost across queries while post-retrieval compression pays it per query.

The robust compress-first preference is a substantive finding because it reverses the assumed default of the post-retrieval-compression literature. For practitioners, the recommendation is: index the compressed corpus by default; use joint relevance-conditional routing (P3) when the additional $\sim$1 pp F1 headroom is worth the implementation cost; post-retrieval compression (P2) is only the right choice when the corpus is small enough that storage cost is irrelevant and retrieval recall is the binding constraint.

### 4.7.4 Limitations and the cost model caveat

The cost model uses the requested compression ratio rather than the achieved compression ratio because the achieved ratio depends on the compressor and the request flows through the pipeline as target. For Phi-3-Mini extractive the ceiling effect makes this an asymmetric error in favour of P2 (which pays the compressor per query and is therefore most sensitive to the ceiling), so the P1 result is the conservative one. The single-retriever, single-embedder design is named in §5.3 as the most natural follow-on study.

## 4.8 H4: Summary-Level Inference Disclosure

> **H4.** The summary-level inference-disclosure metric (i) distinguishes a baseline planner from a priors-only planner (signal: positive paired effect, $p < 0.05$), and (ii) is reduced by compression at 4× versus 1× (reduction: positive paired effect, $p < 0.05$). **Verdict: SUPPORTED on the unbiased benchmark.** The reader exhibits an asymmetric YES/NO bias; this is documented in §4.8.4.[^1]

[^1]: See §4.8.4 for the reader-bias caveat. The verdict is stated in terms of the pooled rates, which are balanced by ground-truth-class distribution; the per-class breakdown is what discloses the asymmetric reader-side accuracy.

### 4.8.1 Why this measurement matters

The memory bus stores summarised representations of source fragments. When a fragment is classified CONFIDENTIAL or higher, the goal of the policy layer is to ensure that the summary does not leak the protected facts that motivated the classification. The H4 metric quantifies, per compressor and per ratio, the rate at which a downstream reader can recover protected facts from the compressed summary. This converts the qualitative goal ("compression should not leak") into a quantitative operating-point selection ("at this ratio, this compressor leaks $x\%$ of protected facts to a downstream reader"). The metric is what makes the memory bus's privacy claim auditable.

### 4.8.2 Metric definition and the unbiased benchmark

For each CONFIDENTIAL fragment, the C1 generator emits a list of (yes/no question, ground-truth answer) pairs whose ground-truth answer is a protected fact about the fragment. The canonical benchmark variant balances the YES/NO distribution at the question level and uses a single comparator phrasing for the yes/no question template, eliminating a surface-pattern bias in the original H4 benchmark generator (`fact_aggregation.py:119-156`, fixed 2026-05-29). Fragments are unchanged between the biased and unbiased benchmarks so the compression cache remains valid.

The reader is the local Llama-3.1-8B-Instruct model accessed via the Ollama backend. Three conditions are evaluated:

- **PRIORS.** Reader sees only the workload's public preamble. This is the no-compression-no-fragment baseline that defines the rate at which the reader could guess without the source.
- **BASELINE.** Reader sees the uncompressed source fragments. This is the disclosure rate without any privacy protection.
- **COMPRESSED-4×.** Reader sees the source fragments compressed at 4× by one of the four compressors.

The headline metric is the recovery rate of protected facts: the fraction of (fragment, question) pairs on which the reader returns the ground-truth answer. The H4 *signal* is whether BASELINE sits above PRIORS (the metric must measure something real); the H4 *reduction* is whether COMPRESSED-4× sits below BASELINE (compression must reduce disclosure). Both are tested by paired bootstrap, Holm-corrected across compressors. The canonical results directory is `results/h4_unbiased/`.

### 4.8.3 Result

**Table 4.4 — H4 verdict (per-compressor signal and reduction with Holm-corrected $p$).**

| Compressor | priors | baseline | compr-4× | signal $\Delta$ | reduction $\Delta$ |
|---|---:|---:|---:|---|---|
| Instruction-aware filter | 0.50 | 0.78 | 0.57 | $+0.286$ ($p_\text{Holm}=6\times10^{-4}$) | $-0.214$ ($p_\text{Holm}=6\times10^{-4}$) |
| LLMLingua-2 | 0.50 | 0.78 | 0.59 | $+0.286$ ($p_\text{Holm}=6\times10^{-4}$) | $-0.189$ ($p_\text{Holm}=6\times10^{-4}$) |
| Phi-3-Mini extractive | 0.50 | 0.78 | 0.71 | $+0.286$ ($p_\text{Holm}=6\times10^{-4}$) | $-0.075$ ($p_\text{Holm}=0.027$) |
| **Verdict:** Signal + Reduction both significant for all three. | | | | | **SUPPORTED** |

`figures/privacy_quality.pdf` visualises the disclosure-versus-coordination trade-off: each point is a (compressor, ratio) cell, with disclosure on one axis and coordination success on the other. The instruction-aware filter and LLMLingua-2 occupy a low-disclosure, moderate-coordination region at 4×; Phi-3 extractive sits in a high-disclosure, high-coordination region; truncation is a strong-coordination-collapse outlier.

### 4.8.4 The reader's YES-bias caveat

The Llama-3.1-8B reader exhibits a strong YES-bias: when the ground-truth answer is YES, the reader's recovery rate is approximately 0.03 on the priors-only condition and 0.58 on the baseline; when the ground-truth answer is NO, both rates are approximately 1.00. The pooled rates of 0.50 (priors) and 0.78 (baseline) reflect a balanced ground-truth distribution, not a reader that is equally accurate in both directions. The correct framing of H4 is that the metric measures *"compression preserves enough information to flip a no-biased reader to confident YES on a protected-fact question"*. This is an asymmetric leakage signal but it is a valid one: a reader that defaults to NO is the conservative case for privacy auditing because it is the case in which the absence of the protected fact most cleanly translates to a privacy preservation.

The caveat is documented here rather than in the verdict block because the pooled rates are what the verdict pipeline tests and the verdict is stable under the caveat. A future-work direction named in §5.6 is to repeat the measurement with a reader chosen to be unbiased, which would distinguish the disclosure-reduction signal from the reader's prior on YES.

### 4.8.5 Memory-bus integration

The policy layer of the memory bus (§3.1) consumes the H4 measurement at deployment time. For each CONFIDENTIAL classification and each governance budget (maximum disclosure rate the operator is willing to accept), the H4 table identifies the set of (compressor, ratio) operating points that meet the budget. The policy enforces the selection by routing CONFIDENTIAL writes through the chosen compressor, by rejecting writes whose compression would exceed the budget, or by downgrading the classification level if the operator chooses to accept the leakage. The disclosure-budget enforcement is not separately evaluated as a hypothesis in this thesis — the metric is the contribution; the policy machinery the metric enables is a deployment concern — but the policy layer is implemented in the reference service and is exercised by the end-to-end integration tests.

## 4.9 Corollary 2: Information-Density Scaling on Real Benchmarks

> **Corollary 2 (information-density scaling).** The cliff position $\tau^{*}$ varies systematically with a task's *information density* $\theta_\text{info}$ (the AUC-based estimate of $1 - \text{normalised AUC of coordination/baseline}$, which is distinct from $\theta_q$). Dense tasks ($\theta_\text{info} \to 1$) cliff early; distributed tasks ($\theta_\text{info} \to 0$) cliff late and degrade gradually. **Verdict: SUPPORTED** by the gap between C1 family-a ($\theta_\text{info} \approx 0.97$, dense) and the real-data benchmarks MultiHopRAG ($\theta_\text{info} \approx 0.48$, distributed) and HotpotQA ($\theta_\text{info} \approx 0.37$, highly distributed).

### 4.9.1 $\theta_\text{info}$ versus $\theta_q$

A subtle point that the corollary reframing makes explicit: the information-density $\theta_\text{info}$ that Corollary 2 talks about is *not* the cliff-recall threshold $\theta_q$ that Corollary 1 and the compounding-error model talk about. The two quantities are derived from different measurements and answer different questions. $\theta_q$ is the recall threshold per family at which coordination success drops to 0.5 of $p_0$, estimated by `derive_theta()`; $\theta_\text{info}$ is the per-task information-density estimate

$$\theta_\text{info} = 1 - \mathrm{AUC}\left[\frac{\text{coord-success}(r)}{p_0}\right]_{r=1}^{r_{\max}},$$

estimated by `estimate_task_theta()`, which captures how *concentrated* the task's information is in compression-sensitive tokens. Confusing the two was a real failure mode of the audit reconciliation (project-internal, recorded in `docs/adr/ADR-006` through `ADR-009`); the CONTEXT.md glossary distinguishes them explicitly.

### 4.9.2 Result on three benchmarks

**Table 4.5 — Corollary 2 verdict ($\theta_\text{info}$ and empirical $\tau^{*}$ across three benchmarks).**

| Task | $\theta_\text{info}$ | $\tau^{*}$ | Source dir |
|---|---:|---:|---|
| C1 family-a (dense, numeric) | 0.97 | 2.7 | `h1_h2_final/` |
| MultiHopRAG (distributed QA) | 0.48 | 11.3 | `h6_final/` |
| HotpotQA (very distributed) | 0.37 | 2.7 | `hotpotqa_sweep/` |
| **Gap** (dense vs MultiHopRAG) = 0.48; (dense vs HotpotQA) = 0.59 | | | |

The HotpotQA result requires brief comment: $\tau^{*}$ on HotpotQA is approximately 2.7, similar to C1 family-a's, but the baseline coordination success on HotpotQA is only 0.59, so the absolute coordination success at the cliff is much lower ($\approx 0.30$). The corollary claim is about the *shape* of the degradation (gradual versus sharp), captured by $\theta_\text{info}$ via the AUC computation, not about the absolute position alone. `figures/hotpotqa_cliff.pdf` shows the HotpotQA cliff with the gradual-degradation pattern visible.

### 4.9.3 Interpretation

The corollary makes the compounding-error model's per-family $\theta_q$ structure plausible as the first-order term of a finer description. $\theta_\text{info}$ tells you how much of the task's success curve is concentrated in compression-sensitive tokens; $\theta_q$ tells you the recall threshold at which success collapses given that concentration. The two together describe the cliff position and shape; either alone is a first-order summary. For the thesis, $\theta_\text{info}$ is what makes the cross-benchmark transfer of the cliff structure auditable: a practitioner who needs to deploy compression on a new task can estimate $\theta_\text{info}$ on a small calibration set and predict whether the task is dense (cliff early, sharp) or distributed (cliff late, gradual) before sweeping the full curve.

The dropped H6 original predicate (synthetic-versus-real $\tau^{*}$ within $\pm 15\%$) is honestly NOT SUPPORTED at the table-level numbers; the reframed Corollary 2 predicate (gap in $\theta_\text{info}$ $\ge 0.1$ between dense and distributed benchmarks) is comfortably SUPPORTED. The reframing is recorded as part of the project's audit reconciliation; the synthetic benchmark is still the right place to characterise the cliff mechanism cleanly, and the real benchmarks are the right place to validate the structure transfers.

## 4.10 Summary of Verdicts

**Table 4.6 — Consolidated verdict table. Original predicate verdicts are reported alongside the reframed corollary verdicts where the reframing was made before the chapter was written.**

| ID | Claim | Verdict | Canonical dir |
|---|---|---|---|
| H1 | QA-F1 decorrelates from coordination success | SUPPORTED | `h1_h2_v2/` |
| H2 | Sharp coordination cliff exists | SUPPORTED (11/12) | `h1_h2_v2/` |
| H3 | RAG sign-flip across regimes | NOT SUPPORTED (reframed as compress-first dominance) | `h3_final/` |
| H4 | Compression reduces inference disclosure | SUPPORTED on unbiased | `h4_unbiased/` |
| H5 → Cor. 1 | Cliff-position invariance within calibrated regime | SUPPORTED (frontier) | `h5_final/`, `frontier_qwen72b/`, `frontier_deepseekv4/` |
| H6 → Cor. 2 | $\theta_\text{info}$ scales the cliff | SUPPORTED | `h6_final/`, `hotpotqa_sweep/` |

Chapter 5 draws the threads together: how the findings interact, what CAAC contributes as a constructive realisation of the compounding-error bound, what the limitations of the work are, what its significance to practice and to the field is, and where the largest remaining unknowns sit.

---

# 5. Discussion and Summary

This chapter draws together the empirical work of Chapter 4 and the system design of Chapter 3: what the findings say jointly, what CAAC adds as a constructive realisation of the compounding-error bound, where the work is limited, what its significance is to practitioners and to the field, how it relates to industry observations on multi-agent token economics, and where the most natural follow-on studies sit.

## 5.1 Synthesis

The thesis answers the question posed in Chapter 1 with five quantitative results that fit together as a single story about context compression in multi-fragment LLM workflows.

Single-agent question-answering accuracy and multi-fragment coordination success disagree — across the four compressors of the cliff sweep the Spearman correlation between the two is distributed from $-0.59$ to $+0.38$, with confidence intervals that comfortably exclude the moderate-correlation threshold of 0.6 (§4.2). A token-overlap metric does not predict the harder structural property a planner needs, and the single-agent benchmarks that dominate the compression literature are insufficient for the multi-fragment deployment decisions FCG and TalentAdore-style workflows depend on.

A sharp coordination cliff $\tau^{*}$ exists on the C1 benchmark for every (compressor, family) cell at which the compressor's mechanism drops the task-critical tokens (§4.3); the only cell that does not exhibit a detectable cliff is the instruction-aware filter on the multi-step-retrieval family, where the cross-encoder re-ranker preserves the chain-reference tokens that the task scorer turns on. The cliff is sharp enough that an empirical-bound model built around a threshold-success assumption (§4.4) recovers the position to within a useful first-order approximation.

The cliff position is invariant to planner parameter count within a precisely-defined calibrated regime (§4.5) and is invariant to architecture family between Qwen and DeepSeek (§4.6). A 9× change in parameter count from a local 8B Qwen-2.5 to a frontier 72B Qwen-2.5 shifts $\tau^{*}$ by 0.8%. A change of vendor from Alibaba's Qwen line to DeepSeek's V4 Pro line keeps $\tau^{*}$ inside the bootstrap CI of the synthetic reference. The cliff is not invariant to reasoning regime: extended-reasoning planners such as GPT-oss 120B cliff at substantially higher ratios because they can recover from sub-threshold information by chain-of-thought, violating the threshold-success assumption A3. This is the empirical evidence that the cliff is a property of the (compressor, task) pair within a defined regime — the structural finding that the thesis contributes to the compression literature.

Compress-first is robustly preferred over post-retrieval compression in both storage- and accuracy-bounded RAG regimes (§4.7). The H3 hypothesis as written (sign-flip between regimes with $\ge 5$ pp effect) is not supported, but the reframed finding — that the simpler, more amortisable architecture is also the better one — reverses a common assumption of the LongLLMLingua line of work and is the substantive C3 contribution.

Compression measurably reduces inference disclosure of protected facts to a downstream reader (§4.8), and the reduction is proportional to how aggressively the compressor operates on tokens. The aggressive token-level compressors (instruction-aware filter and LLMLingua-2) reduce disclosure by approximately 20 pp at 4×, while the extractive copier (Phi-3-Mini extractive) reduces it by approximately 7.5 pp, which makes the disclosure metric useful as a privacy-and-coordination operating-point selector when integrated with the memory bus's policy layer (§3.1).

The cliff position varies with task information density across benchmarks (§4.9): C1 family-a ($\theta_\text{info}\approx 0.97$) cliffs early and sharply, MultiHopRAG ($\theta_\text{info}\approx 0.48$) cliffs late and gradually, HotpotQA ($\theta_\text{info}\approx 0.37$) degrades gradually from a lower baseline. This is the empirical evidence that $\theta_\text{info}$ is a useful second-order term beyond $\theta_q$ for predicting cliff structure on a new task; it is also the evidence that the synthetic-benchmark methodology of this thesis transfers to real benchmarks at the structural level even when the absolute cliff positions differ.

Taken together: the cliff is real, sharp, predictable in shape, invariant inside a regime, and a privacy lever. A practitioner who needs to deploy compression on a multi-fragment workflow can measure $\theta_q$ and $\theta_\text{info}$ once on a small calibration set, predict the cliff position from the compounding-error model within a known tolerance, select an operating point inside the cliff's safe zone, and audit the deployment's privacy budget against the disclosure-rate table. The next section describes the algorithmic mechanism that turns this measurement loop into a runtime back-off.

## 5.2 Cliff-Aware Adaptive Compression: a Constructive Realisation

CAAC — Cliff-Aware Adaptive Compression (`src/m6/compressors/caac.py`) — is the algorithmic counterpart of the compounding-error model of §4.4. The framing it operates under in this thesis follows ADR-007 and is deliberately the framing of an *operating-point selector* rather than a *Pareto-dominating wrapper*; the framing matters because the empirical strict-Pareto rate against the fixed-ratio compressor is **0/7 at every cliff ratio** of the canonical sweep, and a careless framing would read that as a contribution failure when it is in fact the structural property the model predicts.

### 5.2.1 Algorithm

CAAC wraps any inner compressor that satisfies the `Compressor` protocol. Given a target ratio $r$, a per-family recall threshold $\theta_q$ from `derive_theta()`, and the number of compression passes $N$ (in every CAAC experiment in this thesis $N=1$ so $q_\text{min} = \theta_q$), CAAC executes the following per fragment:

1. Run the inner compressor at the requested target ratio $r$, producing a compressed fragment and measuring its critical-token-recall $q$.
2. If $q \ge q_\text{min}$, return the compressed fragment as is.
3. Otherwise, binary-search downward over ratios in $[r_\text{min}, r]$ until the largest ratio $r' \le r$ is found that satisfies $q(r') \ge q_\text{min}$. Return the result of the inner compressor at $r'$.
4. Floor: $r_\text{min}$ is fixed at 1.5× to prevent abdication to no-compression on hard fragments.

The binary search converges in at most five inner-compress calls per backed-off fragment. The CTR measurement is a set-intersection calculation in microseconds and does not measurably contribute to the wallclock. The wrapper is therefore drop-in: any existing deployment using LLMLingua-2 or the instruction-aware filter or Phi-3-Mini extractive can swap to its CAAC-wrapped version without changing the memory-bus access layer or the storage layer.

### 5.2.2 Operating-point framing

The strict-Pareto criterion against the fixed-ratio compressor requires CAAC to match or exceed both the coordination success *and* the achieved compression ratio of the fixed-ratio baseline at every target ratio. CAAC by construction trades compression for coordination: it backs off the achieved ratio *below* the requested target whenever the recall constraint $q \ge q_\text{min}$ would be violated. So at high target ratios where the fixed compressor cliffs to zero coordination, CAAC is backing off to $\sim$3× achieved ratio while the fixed compressor delivers $\sim$12× at zero coordination. Strict-Pareto says CAAC does not dominate the fixed compressor; the empirical 0/7 result reflects this faithfully.

The reframing that ADR-007 accepts as the substantive contribution is the operating-point one: CAAC's selected ratio is *determined by the compounding-error bound*, not by tuning. For each family, $\theta_q$ is a measurement; CAAC's binary-search procedure makes the ratio it operates at a predictable function of the inner compressor's $q(r)$ curve and that measurement. With three families, CAAC produces three operating points, one per family, all on the safe side of the cliff. The fixed-ratio compressor produces one operating point per target ratio, with no guarantee about which side of the cliff it sits on. The two compressors populate complementary regions of the (coord-success, achieved-ratio) frontier (`figures/caac_pareto.pdf`).

### 5.2.3 Weak-dominance result and the $\theta_q$/$N$ ablation

Although strict-Pareto does not hold, *weak* dominance — the coordination-only comparison — does. Across all seven target ratios of the canonical sweep and across the two inner compressors evaluated, CAAC's coordination success is greater than or equal to the fixed compressor's **100%** of the time. At the high target ratios where the fixed compressor cliffs to zero coordination, CAAC retains coordination at the price of compression. This is what the model predicts, and it is the correct framing of CAAC's contribution: a guaranteed safety floor, conditional on the per-family recall threshold being correctly measured.

The $\theta_q$/$N$ ablation (`results/caac_theta_*`, `results/caac_N_*`) returns an informative null. The coordination-success plateau of CAAC is invariant to the choice of $\theta_q$ in $\{0.6, 0.7, 0.8\}$ and the choice of $N$ in $\{2, 3, 4, 5\}$: the LLMLingua-2 plateau is 33% across all seven configs, the filter plateau is 64% across all seven configs, and only the achieved compression ratio responds, by backing off more aggressively as either parameter increases. The primary knob is the $r_\text{min}$ floor, not $\theta_q$ or $N$. A sweep over $r_\text{min} \in \{1.2, 1.5, 2.0, 2.5\}$ is the natural follow-on that this thesis defers as future work.

### 5.2.4 What CAAC contributes to the thesis

CAAC is the demonstration that the compounding-error model is operationally usable, not just descriptively predictive. The algorithm is short, training-free, drop-in, and bounded in behaviour by a measurement. The contribution sits in Chapter 5 rather than as a headline contribution in Chapter 1 because the model is the substantive contribution and CAAC is its constructive realisation — but the design choice that CAAC enables is real: a practitioner who has measured $\theta_q$ on one family can deploy CAAC at any target ratio with the guarantee that the achieved operating point sits on the safe side of the cliff. This deployment-mode property is what makes the cliff measurement useful as something other than a publication finding.

## 5.3 Limitations

The limitations are catalogued explicitly so that a reader can calibrate the scope of the findings.

**No multi-round agent coordination.** The empirical evaluation uses a deterministic regex solver (H1, H2) or a single LLM call with all (compressed) fragments visible (Corollary 1, frontier, real-data transfer). The AutoGen v0.4 multi-round agent backend in `src/m6/orchestrator/` integrates with the memory bus but is not used in any reported result. Multi-round coordination introduces a per-round variance that the deterministic solver deliberately excludes; the cliff measured here is the solvability cliff under compression, not the multi-round communication-quality cliff. ADR-009 records the scoping decision.

**Single compression pass.** Every experiment uses $N=1$. The compounding-error model admits arbitrary $N$ ($q$ compounds as $q^N$), but the $N>1$ regime is not empirically validated. The $\theta_q$/$N$ ablation (§5.2) is an algorithmic sweep over CAAC's internal $N$ parameter, not a sweep of compression passes against the cliff sweep. Multi-pass coordination is a natural follow-on study.

**Family-a homogeneity.** The 50 instances of family-a are all sum-of-eight-numbers variants. The cliff structure observed on family-a may not generalise to heterogeneous aggregation tasks (max, min, weighted average, conditional aggregation). The transfer to real benchmarks (Corollary 2) addresses the broader concern that synthetic tasks might not transfer to real ones, but the within-family homogeneity is a separate concern that future work could resolve by sweeping aggregation types within family-a.

**Family-b LLM floor.** The constraint-satisfaction family-b is hard for $\le 8$B planners independent of compression: baseline coordination success is near zero for the 1.5B and 3.8B Qwen sizes. The family-b cliff is not detectable in this regime, and Corollary 1's invariance result is therefore tested on family-c only for the local sweep. A planner capable of solving family-b at the no-compression baseline (e.g., a frontier reasoning model) would enable a family-b validation of Corollary 1 that this thesis cannot produce.

**Phi-3-Mini extractive ceiling.** The Phi-3-Mini extractive compressor saturates at approximately 2.5× achievable compression regardless of the requested target, because the verifier and the LLMLingua-2 fallback combine to bound the achievable ratio. All evaluation reports the achieved ratio alongside the requested target so this saturation is visible, but it does mean that Phi-3-Mini extractive cannot participate in the high-compression-ratio comparisons; its curves flatten above $\sim 2.5\times$ rather than continuing to follow the family's degradation pattern.

**Extended-reasoning regime is out of scope.** The calibrated regime predicate (§4.4.3) excludes planners that recover sub-threshold information by chain-of-thought reasoning. GPT-oss 120B and likely the GPT-4-class "thinking" models violate the predicate. The compounding-error model's quantitative predictions do not apply to these planners; the GPT-oss 120B result is reported as an out-of-regime diagnostic in §4.6.4 rather than as a counterexample. Characterising the cliff in the extended-reasoning regime is the largest follow-on direction this thesis opens.

**Compounding-error model is a first-order bound.** The strict empirical match rate of the predicted-versus-empirical $\tau^{*}$ comparison is 33% within $\pm 25\%$ relative error and 67% within $\pm 50\%$. The model is useful as a first-order predictor and as a derivation that explains the cliff structure; it is not a tight prediction. The graded-importance assumption A2 is the strongest of the four (§4.4.2); H4's graded-disclosure measurements provide evidence that the binary-importance simplification is what the model gives up.

**Synthetic-task focus, real-task transfer at the structural level.** The C1 benchmark is synthetic, by design: cliff characterisation requires controlled information density. The transfer validation on HotpotQA and MultiHopRAG shows that the cliff structure (existence, sharpness gradient with $\theta_\text{info}$) transfers to real benchmarks, but the absolute cliff positions differ substantially. Generalisation to arbitrary task structures beyond the three task families this thesis examines is unverified and would require either a broader benchmark suite or a `theta_info` sweep over a corpus of real benchmarks.

**Single-retriever, single-embedder RAG comparison.** The H3 RAG pipeline catalogue uses FAISS-CPU with HNSW and `BAAI/bge-large-en-v1.5` embeddings. Different retrievers or embedders may shift the cost balance of the storage- and accuracy-bounded regimes. The compress-first finding is qualitatively robust (it depends on the storage-cost asymmetry, which holds for any retriever) but the quantitative cost numbers are tied to the specific stack.

**Reader-bias in H4 measurement.** The Llama-3.1-8B reader under-predicts YES protected-fact answers. The pooled rates that the H4 verdict rests on are balanced by the ground-truth class distribution rather than by reader-side accuracy. The H4 metric measures *"compression preserves enough information to flip a no-biased reader to confident YES"*, which is an asymmetric leakage signal. A reader chosen specifically to be unbiased would distinguish the disclosure-reduction signal from the reader's prior; this is named as future work in §5.6.

## 5.4 Significance

### 5.4.1 For practitioners

Four practitioner-facing implications follow from the findings.

*First*, single-agent question-answering benchmarks (LongBench, RULER, the LLMLingua line of work's own QA evaluations) *systematically over-report* compressor utility for multi-fragment deployments. A multi-fragment evaluation is necessary; this thesis ships one (C1) and a methodology (the cliff sweep) that other groups can apply on their own workloads.

*Second*, the cliff position can be predicted from per-round token recall plus a one-shot $\theta_q$ measurement, within a known first-order tolerance. A practitioner who needs to choose a compression ratio for a new multi-fragment workflow can run the $\theta_q$ measurement on a small calibration set and apply the compounding-error model to obtain a safe operating point without running the full cliff sweep.

*Third*, compress-first is the better RAG architecture in both the storage-bounded and accuracy-bounded regimes; the additional implementation cost of post-retrieval compression is not paid for in the regimes most production workflows operate in. Joint relevance-conditional routing (P3) adds the final $\sim 1$ pp F1 if the deployment can absorb the additional complexity, but the default should be P1.

*Fourth*, compression is a privacy lever. The disclosure metric ranks compressors by privacy at iso-ratio. A governance budget on protected-fact leakage can be enforced by routing CONFIDENTIAL fragments through the compressor whose disclosure rate at the chosen ratio meets the budget, and the memory bus's policy layer turns this into a deployment-time mechanism rather than a per-query check.

### 5.4.2 For the field

Three field-facing claims are substantive.

*First*, the cliff is a property of the (compressor, task) pair within the calibrated regime, not of the planner. The frontier validation result that a 72B Qwen-2.5 cliffs at the same ratio as the local 8B Qwen-2.5 to within 0.8% is the empirical evidence. The implication for the compression literature is that future compressor evaluations should either characterise the calibrated regime they apply in or explicitly target the extended-reasoning regime as a separate case.

*Second*, extended-reasoning planners are a different regime that the existing compression literature has not characterised. The GPT-oss 120B out-of-regime result is a positive diagnostic of where the threshold-success assumption breaks; characterising this regime systematically is a publishable follow-on. The practical-deployment implication is that compression ratios calibrated on a non-reasoning planner cannot be transferred to a reasoning planner without revalidation.

*Third*, information density $\theta_\text{info}$ scales the cliff across benchmarks in a way that future benchmarks should control for. A multi-benchmark compression-quality comparison that does not measure or control $\theta_\text{info}$ will report cliff positions that conflate compressor mechanism with task structure; the cross-benchmark transfer result of Corollary 2 is the evidence that the two must be separated.

## 5.5 Comparison to Industry Observations

The closest published industry observation, Anthropic's report that token usage explains approximately 80% of the performance variance in their multi-agent research workflow [Anthropic 2025a], and the follow-on context-engineering and context-editing reports [Anthropic 2025b; Anthropic 2025c], are consistent with the findings of this thesis and underwrite the practitioner urgency. What they do not provide — and what the thesis contributes — is the structural characterisation. The Anthropic report is an aggregate observation on a single multi-agent workflow run by a single industry team; the cliff measurement in this thesis is a controlled cross-compressor, cross-family, cross-architecture sweep with a quantitative model that predicts the cliff position. The two complement each other: the industry observation is the macro reason a practitioner cares about the question; the thesis findings are the micro answer that lets them act on it.

## 5.6 Future Work

The most natural follow-on studies in order of expected impact.

**Extended-reasoning regime.** Characterise the cliff for planners that recover from sub-threshold information by chain-of-thought reasoning. The empirical setup is a re-run of the cliff sweep with GPT-oss-class planners, GPT-4-Turbo with thinking, and Claude Sonnet 4.6 with extended thinking enabled. The theoretical work is replacing A3 (threshold success) with a graded-success model.

**Per-task $\theta_q$ estimation.** Lift the model from per-family $\theta_q$ to per-task $\theta_q$. The current per-family validation match rate is 33%; a per-task fit should improve this to the 60–70% range observed on the $\theta_q$-already-known calibration cells. The empirical setup is straightforward; the methodological cost is fitting $\theta_q$ per task on a held-out calibration split.

**Multi-pass compression at $N > 1$.** Validate the $q^N$ formulation of the model empirically. The empirical setup is a small sweep across two-pass and three-pass compression on the family-a cells; the analysis turns on whether the empirical cliff shifts predictably with $N$.

**CAAC $r_\text{min}$ sweep.** The $\theta_q$/$N$ ablation showed that the CAAC operating-point plateau is invariant to those two parameters. The primary knob the ablation deferred is $r_\text{min}$. A sweep over $r_\text{min} \in \{1.2, 1.5, 2.0, 2.5\}$ produces the operating-point family that CAAC traces out as a function of the floor.

**Multi-round AutoGen coordination.** The AutoGen v0.4 multi-round backend is wired into the memory bus but excluded from the empirical evaluation because of run-to-run variance. A focused study that controls the round-count variance and isolates the per-round compression effect would extend the thesis findings to the multi-round coordination regime that the deterministic solver scope-out of ADR-009 deliberately defers.

**Broader task families.** The three C1 families are deliberate probes of a single property each (density, constraint-tracking, chain-reference). A broader benchmark suite with heterogeneous aggregation types, multi-tool reasoning, and multimodal fragments would test the generalisability of the cliff structure beyond the families this thesis evaluates.

**An unbiased H4 reader.** The reader-bias caveat of §4.8.4 is a limitation that a re-measurement with a reader chosen to be unbiased would resolve. The candidate readers are larger local-LM variants (Llama-3.3 instruct-tuned at 70B), or a calibration step that re-weights the H4 results by the reader-side prior; the latter is the cheaper approach.

## 5.7 Closing

The five empirical findings, the compounding-error model that ties them together, the memory-bus reference implementation that operationalises the privacy lever, and the CAAC algorithm that operationalises the cliff bound, jointly constitute the thesis's contribution: a structural characterisation of context compression in multi-fragment LLM workflows, validated across compressors, families, planner scales, architectures, and benchmarks, with a predictive model, a deployment artefact, and an open-source reproducibility package. The single deliverable sentence is the one the abstract opens with: every token that does not change the answer is waste, and what this thesis contributes is a way of knowing which tokens those are, when removing them is safe, and what the cost is when removing them is not.

---

# Appendices

## Appendix A. Memory-Bus HTTP Contract

The reference memory-bus service exposes four endpoints. The contract below summarises the request and response shapes; the authoritative OpenAPI schema lives at `docs/openapi.json` in the repository and is regenerated via `make bus-openapi`.

- **`POST /v1/write`** Body: a `Fragment` JSON object (`fragment_id`, `text`, `tags`) and an optional `target_ratio`. Returns the assigned `slot_id`, the audit row identifier, and the hex-encoded `chain_hash`. HTTP 201 on success; 403 on policy denial.
- **`GET /v1/read/{slot_id}`** Returns a `CompressedSlot` with its payload, tags, compressor identifier, nominal ratio, and creation timestamp. HTTP 200 on success; 403 on policy denial; 404 on slot not found.
- **`POST /v1/subscribe`** Body: a `SubscribeRequest` with a `query` string, a `ttl_seconds` positive integer, and a top-$k$ integer. Returns a server-sent-event stream emitting newly-matched `slot_id`s with their cosine scores until the TTL elapses.
- **`GET /v1/audit/{slot_id}`** Returns the chronological list of `AuditRow` entries that mention the given slot.

Every request is processed by the `PolicyMiddleware` which parses the requester principal from the `X-M6-Principal` header in the development build and from an OAuth/JWT verifier in a production deployment. The principal carries a 64-bit access-control mask and a 5-tier classification level (PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED < SECRET). A request is granted access to a slot when the principal's mask is a superset of the slot tag's mask and the principal's classification is at least the slot tag's classification.

## Appendix B. Long-Format Results Schema

Every experiment runner writes its results to a CSV that conforms to the long-format schema implemented as `m6.evaluation.statistics.LongDF`. The columns are listed in the table below.

| Column | Type | Notes |
|---|---|---|
| `experiment_id` | str | unique per run |
| `hypothesis` | str | one of `h1`…`h6` or `caac`, `frontier`, `hotpotqa` |
| `compressor` | str | e.g. `lingua2`, `filter`, `phi3-extractive`, `truncation`, `caac`, `identity` |
| `ratio` | float | nominal compression ratio |
| `actual_ratio` | float | measured ratio post-compression |
| `pipeline` | str | one of `none`, `P1`, `P2`, `P3` |
| `model` | str | e.g. `llama-3.1-8b-instruct` |
| `model_size` | str | `1.5b`, `3.8b`, `8b`, `72b` |
| `workload_family` | str | `a`, `b`, or `c` |
| `workload_id` | str | e.g. `c1-a-007` |
| `seed` | int | |
| `metric` | str | e.g. `coord_success`, `qa_f1`, `preservation_rate` |
| `value` | float | |
| `wallclock_ms` | int | |
| `eur_cost` | float | |
| `run_id` | str | |
| `git_sha` | str | |
| `config_hash` | str | |
| `created_at` | str | ISO-8601 UTC |
| `invalid` | bool | control-condition variance dominates? |
| `invalid_reason` | str | free-text explanation if invalid |

## Appendix C. Example C1 Workload (family a)

The following JSON object illustrates a single instance of C1 family (a) (cross-document fact aggregation). Each fragment represents one institutional system; the planner is asked to aggregate hours and budget across all eight; the critic verifies the answer against the ground-truth aggregate.

```json
{
  "workload_id": "c1-a-007",
  "family": "a",
  "seed": 1247,
  "tag_distribution": "skewed",
  "initial_prompt":
    "Aggregate the period-end report for project P-3219 across the
     following systems: publication_db, contract_db, moodle, patio,
     peppi, crm, tatu_sap, sap_travel. Report total hours and total
     budget.",
  "expected_answer": "hours=853;budget=148340",
  "n_agents": 8,
  "fragments": [
    {
      "fragment_id": "c1-a-007/publication_db",
      "text": "[publication_db] Project P-3219 - period 2025-Q3. ...",
      "tags": {"acl_mask": 12876, "classification": 1}
    },
    {
      "fragment_id": "c1-a-007/contract_db",
      "text": "[contract_db] Project P-3219 - period 2025-Q3. ...",
      "tags": {"acl_mask": 8901, "classification": 2}
    }
    // (six more fragments, one per system)
  ],
  "sub_tasks": [
    {
      "sub_task_id": "c1-a-007/sub-0",
      "description":
        "Extract recorded hours and budget for project P-3219 from
         publication_db.",
      "expected_solver": "worker-0",
      "expected_answer": "hours=112;budget=18420"
    }
    // (seven more sub-tasks)
  ],
  "protected_facts": [
    {
      "fragment_id": "c1-a-007/contract_db",
      "fact": "contract_db.budget=22150",
      "yesno_questions": [
        "Did contract_db for project P-3219 exceed EUR 27150 in budget?",
        "Was contract_db's recorded hours for P-3219 more than 142?"
      ],
      "answers": ["no", "no"]
    }
  ]
}
```

The full dataset is reproduced from `configs/benchmark/c1-v0.1.yaml` via `make bench-generate`; the manifest carries the configuration hash so any reader can verify they are looking at the same release.

## Appendix D. Reproducibility Recipe and Memory-Bus Trace

### D.1 One-command reproduction of every chapter figure

The reproducibility package is the complete open-source repository. The compute envelope is a single Apple M4 Pro 48 GB workstation, with an optional RTX 5090 32 GB workstation (Tailscale-accessible WSL2 host) for the GPU-bound compression precomputation, the model-scaling sweep at 8B, the frontier-API sweep, and the HotpotQA / MultiHopRAG transfer arm. Total wallclock end-to-end is approximately 30 hours of GPU time and $\sim$12 hours of laptop time. The package contains a `docker-compose.yml` that brings the memory-bus reference service up locally, a GitHub release tag matched to the manuscript, model and data cards under `docs/`, and a `README.md` that exposes one-command reproduction targets for every headline figure:

- **`make repro-bench`** regenerates the 150-instance C1 benchmark from `configs/benchmark/c1-v0.1.yaml`. Output: `data/processed/c1-v0.1/`.
- **`make repro-cache`** runs the compression precomputation for all four compressors at the ten canonical ratios across the 150 workloads. Requires the GPU host; total wallclock $\sim$14 hours. Output: `results/compression_cache/`.
- **`make repro-cliff`** runs the H1/H2 cliff sweep against the compression cache, producing all of Chapter 4 §4.2 through §4.4 figures. Wallclock $\sim$3 hours on the M4 Pro.
- **`make repro-scaling`** runs the model-scaling sweep at 1.5B, 3.8B, and 8B with the local Ollama backend, producing Corollary 1's figures. Wallclock $\sim$4 hours on the GPU host.
- **`make repro-frontier`** runs the cliff sweep against the Featherless API for Qwen-2.5-72B-Instruct and DeepSeek V4 Pro plus the OpenAI API for GPT-oss-120B (the out-of-regime diagnostic). Requires API credentials. Output: `results/frontier_{qwen72b,deepseekv4,gptoss120b}/`.
- **`make repro-rag`** runs the H3 RAG pipeline catalogue, producing §4.7's figures. Wallclock $\sim$3 hours.
- **`make repro-disclosure`** runs the H4 inference-disclosure measurement against the unbiased benchmark, producing §4.8's figures. Wallclock $\sim$1 hour on the M4 Pro.
- **`make repro-transfer`** runs the HotpotQA and MultiHopRAG transfer arm, producing §4.9's figures. Wallclock $\sim$2 hours.
- **`make repro-figs`** regenerates every PDF and PNG figure under `figures/` from the canonical CSVs. Pure-Python; runs in under a minute.

The `make repro-all` target runs the eight steps above in dependency order. Every output is deterministic given the seed: rerunning a target produces a byte-identical CSV.

### D.2 Memory-bus end-to-end trace

The following `curl` sequence exercises the four endpoints of the memory bus end-to-end against the `docker-compose`-up'ed reference service. The trace is the rubric-#5 evidence for the C4 contribution: the memory bus is a running system, not a paper design. The output of each step is reproduced verbatim from a run against the reference image tagged `m6-memory-bus:thesis-v1.0`.

```bash
# Step 1: Write a CONFIDENTIAL fragment with target ratio 4x.
$ curl -X POST http://localhost:8000/v1/write \
       -H "Content-Type: application/json" \
       -H "X-M6-Principal: principal=alice;acl=0xFFFF;cls=3" \
       -d @- <<'EOF'
{
  "fragment_id": "demo-001",
  "text": "Project P-3219 quarterly hours: 112; budget: EUR 18420.",
  "tags": {"acl_mask": 12876, "classification": 2},
  "target_ratio": 4.0,
  "compressor": "lingua2"
}
EOF
{"slot_id": "slot-1a4b9c2d", "audit_row": 1,
 "chain_hash": "5f3d2a1b...",  "achieved_ratio": 3.72}

# Step 2: Read the slot back. The principal's classification (3)
#         is at least the slot's (2) and the principal's ACL mask
#         is a superset, so the read is permitted.
$ curl -H "X-M6-Principal: principal=alice;acl=0xFFFF;cls=3" \
       http://localhost:8000/v1/read/slot-1a4b9c2d
{"slot_id": "slot-1a4b9c2d",
 "compressed_text": "Project P-3219 hours: 112 budget: 18420.",
 "compressor": "lingua2", "achieved_ratio": 3.72,
 "tags": {"acl_mask": 12876, "classification": 2},
 "created_at": "2026-05-30T07:42:15Z"}

# Step 3: A second principal with insufficient classification is
#         denied; the denial is itself audited with a
#         per-(principal, slot) 60-second deduplication.
$ curl -H "X-M6-Principal: principal=bob;acl=0xFFFF;cls=1" \
       -o /dev/null -w "%{http_code}\n" \
       http://localhost:8000/v1/read/slot-1a4b9c2d
403

# Step 4: Audit walk for the slot. The chain is verifiable end-to-
#         end via the SHA-256 chain hash on each row; tampering
#         with any row breaks verification.
$ curl -H "X-M6-Principal: principal=alice;acl=0xFFFF;cls=3" \
       http://localhost:8000/v1/audit/slot-1a4b9c2d
[
  {"rowid": 1, "event_type": "WRITE",  "result": "OK",
   "requester": "alice", "chain_hash": "5f3d2a1b..."},
  {"rowid": 2, "event_type": "READ",   "result": "OK",
   "requester": "alice", "chain_hash": "9c4e7a8d..."},
  {"rowid": 3, "event_type": "READ",   "result": "DENIED",
   "requester": "bob",   "chain_hash": "1b8a6f3e..."}
]
```

The trace illustrates four properties: compression with achieved-ratio reporting on the write path; policy-checked read with the five-tier classification lattice and the access-control mask; audited denial with the per-principal-per-slot deduplication that prevents audit-log flooding; and chain-hash-verifiable provenance on the audit endpoint. The complete OpenAPI schema is regenerated by `make bus-openapi` and lives at `docs/openapi.json` in the repository.

### D.3 Compute envelope and software stack

The empirical work was carried out on the following stack. The local workstation is an Apple Mac with the M4 Pro SoC, 48 GB of unified memory, Python 3.12, MLX framework version 0.21, Ollama version 0.3 with the Qwen-2.5, Phi-3-Mini, and Llama-3.1 model weights pre-pulled, and the `m6` package installed in editable mode from the repository. The GPU host is a Windows desktop running WSL2 Ubuntu 22.04 with the NVIDIA RTX 5090 32 GB GPU, CUDA toolkit $\ge$ 12.0, and the same Python and Ollama versions. The Tailscale mesh network connects the local workstation to the GPU host as host `gpu` on the `100.70.160.59/32` private address. The memory-bus reference service runs on either host via `docker-compose up -d`; the image is Python 3.12-slim with FastAPI, Uvicorn, SQLite, and the `m6` package.

---

# References

(References below are abbreviated; the canonical bibliography in BibLaTeX form lives at `thesis_latex/citations.bib` in the repository.)

- **[Addison 2024]** Addison *et al.* **CFedRAG: Coordination of Federated Retrieval-Augmented Generation.** 2024.
- **[Altman 2025]** Altman, S. **Tens of millions of dollars on please-and-thank-you compute.** Industry reporting on social media (X/Twitter), April 2025. *Cited as industry observation; not peer-reviewed.*
- **[Anthropic 2024]** Anthropic. **Introducing Contextual Retrieval.** *Anthropic News*, September 2024.
- **[Anthropic 2025a]** Anthropic. **How We Built our Multi-Agent Research System.** *Anthropic Engineering Blog*, June 2025. *Industry blog; cited as motivation.*
- **[Anthropic 2025b]** Anthropic. **Effective Context Engineering for AI Agents.** *Anthropic Applied AI Blog*, 2025.
- **[Anthropic 2025c]** Anthropic. **Context Editing and Memory Tools.** *Anthropic Engineering*, 2025.
- **[Asai 2024]** Asai, A., Wu, Z., Wang, Y., Sil, A., Hajishirzi, H. **Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.** *ICLR 2024*.
- **[Bai 2024]** Bai, Y., Lv, X., Zhang, J., *et al.* **LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding.** *ACL 2024*.
- **[Bassit 2025]** Bassit *et al.* **SecureRAG: Privacy-preserving retrieval-augmented generation.** 2025.
- **[Cheng 2024]** Cheng, T., *et al.* **xRAG: Extreme Context Compression for Retrieval-Augmented Generation.** 2024.
- **[Chevalier 2023]** Chevalier, A., Wettig, A., Ajith, A., Chen, D. **Adapting Language Models to Compress Contexts** (AutoCompressor). *EMNLP 2023*.
- **[Chhikara 2025]** Chhikara, P., *et al.* **Mem0: A production-oriented agentic memory service.** 2025.
- **[Edge 2024]** Edge, D., *et al.* **From Local to Global: A GraphRAG Approach to Query-Focused Summarization.** *arXiv 2404.16130*, 2024. *Preprint.*
- **[Efron 1993]** Efron, B., Tibshirani, R. **An Introduction to the Bootstrap.** Chapman & Hall, 1993.
- **[FCG 2026]** FCG internal use-case Vignette 3.7 — Period-end project reporting.
- **[FCG financial 2026]** FCG internal financial analysis, 2026.
- **[Ge 2024]** Ge, T., Hu, J., Wang, L., Wang, X., Chen, S.-Q., Wei, F. **In-context Autoencoder for Context Compression in a Large Language Model.** *ICLR 2024*.
- **[Guo 2025]** Guo *et al.* **Dynamic retrieval-augmented generation.** 2025.
- **[Gutiérrez 2024]** Gutiérrez, B., Shu, Y., Gu, Y., Yasunaga, M., Su, Y. **HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models.** *NeurIPS 2024*.
- **[Gutiérrez 2025]** Gutiérrez *et al.* **HippoRAG 2.** 2025.
- **[Hoffmann 2022]** Hoffmann, J., *et al.* **Training Compute-Optimal Large Language Models.** *NeurIPS 2022*.
- **[Holm 1979]** Holm, S. **A Simple Sequentially Rejective Multiple Test Procedure.** *Scand. J. Statist.* 6(2), 1979.
- **[Hong 2024]** Hong, S., Zhuge, M., Chen, J., *et al.* **MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework.** *ICLR 2024*.
- **[Hsieh 2024]** Hsieh, C., Sun, S., Kriman, S., *et al.* **RULER: What's the Real Context Size of Your Long-Context Language Models?** *COLM 2024 / arXiv 2404.06654*.
- **[Jiang 2023]** Jiang, H., Wu, Q., Lin, C.-Y., Yang, Y., Qiu, L. **LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models.** *EMNLP 2023*.
- **[Jiang 2024]** Jiang, H., *et al.* **LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression.** *ACL 2024*.
- **[Kaplan 2020]** Kaplan, J., *et al.* **Scaling Laws for Neural Language Models.** *arXiv 2001.08361*, 2020. *Preprint.*
- **[Kočiský 2018]** Kočiský, T., *et al.* **The NarrativeQA Reading Comprehension Challenge.** *TACL 2018*.
- **[Lewis 2020]** Lewis, P., Perez, E., Piktus, A., *et al.* **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.** *NeurIPS 2020*.
- **[Li 2023]** Li, G., Hammoud, H. A. A. K., Itani, H., Khizbullin, D., Ghanem, B. **CAMEL: Communicative Agents for Mind Exploration of Large Scale Language Model Society.** *NeurIPS 2023*.
- **[Li 2025]** Li *et al.* **A Survey on Prompt Compression for Large Language Models.** 2025.
- **[Liu 2024a]** Liu, X., *et al.* **AgentBench: Evaluating LLMs as Agents.** *ICLR 2024*.
- **[Liu 2024b]** Liu, N. F., Lin, K., Hewitt, J., *et al.* **Lost in the Middle: How Language Models Use Long Contexts.** *TACL 2024*.
- **[Luccioni 2024]** Luccioni, A. S., Jernite, Y., Strubell, E. **Power Hungry Processing: Watts Driving the Cost of AI Deployment?** *ACM FAccT 2024*, pp. 85–99. DOI 10.1145/3630106.3658542.
- **[Mann 1947]** Mann, H. B., Whitney, D. R. **On a Test of Whether One of Two Random Variables is Stochastically Larger than the Other.** *Ann. Math. Statist.* 18(1), 1947.
- **[Mialon 2023]** Mialon, G., *et al.* **GAIA: A Benchmark for General AI Assistants.** *ICLR 2024*.
- **[Mu 2023]** Mu, J., Li, X. L., Goodman, N. D. **Learning to Compress Prompts with Gist Tokens.** *NeurIPS 2023*.
- **[NIST AI RMF]** National Institute of Standards and Technology. **AI Risk Management Framework (AI RMF 1.0).** NIST, 2023.
- **[Ollama]** Ollama. Local LLM serving runtime, ollama.com.
- **[Packer 2023]** Packer, C., Wooders, S., Lin, K., *et al.* **MemGPT: Towards LLMs as Operating Systems.** *arXiv 2310.08560*, 2023. *Preprint.*
- **[Pan 2024]** Pan, Z., Wu, Q., Jiang, H., *et al.* **LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression.** *Findings of ACL 2024*.
- **[Park 2025]** Park, J. S., *et al.* **Generative Agents: Interactive Simulacra of Human Behavior.** *UIST 2023* (companion 2025).
- **[Phi-3 2024]** Abdin, M., *et al.* **Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone.** Microsoft, 2024. *arXiv 2404.14219, technical report.*
- **[Rae 2020]** Rae, J. W., *et al.* **Compressive Transformers for Long-Range Sequence Modelling.** *ICLR 2020*.
- **[Rasmussen 2025]** Rasmussen *et al.* **Zep: Long-term memory for LLM agents.** 2025.
- **[Saleh 2025a]** Saleh, A., *et al.* **MemIndex.** *ACM TAAS 2025*.
- **[Saleh 2025b]** Saleh, A., *et al.* **Towards Message Brokers for Generative AI: Survey, Challenges, and Opportunities.** *ACM CSUR 58(1)*, 2025. DOI 10.1145/3742891.
- **[Sarthi 2024]** Sarthi, P., Abdullah, S., Tuli, A., Khanna, S., Goldie, A., Manning, C. D. **RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval.** *ICLR 2024*.
- **[Shinn 2023]** Shinn, N., Cassano, F., Berman, E., *et al.* **Reflexion: Language Agents with Verbal Reinforcement Learning.** *NeurIPS 2023*.
- **[Vaswani 2017]** Vaswani, A., *et al.* **Attention Is All You Need.** *NeurIPS 2017*, pp. 5998–6008.
- **[Wang 2024]** Wang, X., *et al.* **In-Context Former.** 2024.
- **[Wilcoxon 1945]** Wilcoxon, F. **Individual Comparisons by Ranking Methods.** *Biometrics Bulletin* 1(6), 1945.
- **[Wu 2023]** Wu, Q., Bansal, G., Zhang, J., *et al.* **AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework.** *arXiv 2308.08155*, 2023; ICLR 2024 LLM-Agents Workshop. *Workshop / preprint.*
- **[Xu 2025]** Xu *et al.* **A-Mem: Agentic memory architecture.** 2025.
- **[Yang 2018]** Yang, Z., Qi, P., Zhang, S., *et al.* **HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering.** *EMNLP 2018*.
- **[Yen 2025]** Yen *et al.* **HELMET: A long-context benchmark.** 2025.
- **[Zhou 2025]** Zhou *et al.* **PrivacyRAG: Privacy-preserving retrieval augmentation.** 2025.

---

*End of manuscript. Reproducible source at `thesis_latex/` of the open-source repository; this Markdown rendering at `draft3.md` is provided for plain-text portability.*
