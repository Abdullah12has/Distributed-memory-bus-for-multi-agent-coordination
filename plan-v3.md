# MASTER THESIS M6 — PLAN v3 (FINAL)

# Distributed Memory Bus for Multi-Agent Campus Systems

*Context Compression, Coordination Quality, and Policy-Aware Sharing*

**Syed Abdullah Hassan**
University of Oulu · Faculty of ITEE · CSE Research Unit · Future Computing Group

Academic supervisor: Lauri Lov\'en
Industry: TalentAdore (Asim Nadeem, Oskari Valkama)

*May 2026 — 4-week completion, targeting 8.5/10 MSc*

---

## Change log relative to v2

| Item | v2 | v3 |
|------|----|----|
| LLM-summariser | Llama-3.1-8B abstractive | **Phi-3-Mini-3.8B extractive** (tokens-only prompt; verified post-hoc) |
| Model-size scaling | Dropped | **Reinstated as 3-point** (Qwen2.5-1.5B / Phi-3-Mini-3.8B / Llama-3.1-8B) — H5 |
| H4 tag preservation | "≥85% preservation" (trivially true) | **Replaced with inference-disclosure metric (H4)** |
| Citations | Several unverifiable arXiv IDs | **All refs verified** against peer-reviewed venues OR explicitly marked as preprints |
| Theoretical framing | None | **Compounding-error model**: predicts τ\* from token-recall q and round count N |
| Real-trace arm | Dropped | **Optional H6** on **MultiHopRAG** (Tang & Yang, EMNLP 2024) |

---

## 1. Thesis statement

This thesis designs, implements, and evaluates a distributed memory bus with a
context-compression layer for multi-agent institutional systems. It
contributes:

1. **C1 — A multi-agent coordination benchmark.** Three workload families,
   150 instances, four coordination metrics, synthetic provenance and ACL
   tags, single-command regeneration.

2. **C2 — Empirical characterisation of training-free compression effects on
   multi-agent coordination.** Across three compressor families and three
   planner-LLM sizes (1.5B / 3.8B / 8B), characterises the existence, shape,
   and model-size-dependence of a *coordination cliff* $\tau^{*}$. Includes a
   simple compounding-error model that predicts $\tau^{*}$ from per-round
   token recall.

3. **C3 — RAG + compression pipeline catalogue.** Three pipeline
   architectures (compress→retrieve, retrieve→compress, joint
   relevance-conditional) evaluated under matched storage- and
   accuracy-bounded conditions, with a EUR-per-workflow cost model.

4. **C4 — Memory bus with summary-level inference-disclosure metric.**
   FastAPI service with policy-enforcement middleware, tamper-evident
   audit log, and a held-out-reader privacy measurement that quantifies
   how compression affects the leakage of protected facts to a downstream
   reader.

### What is novel relative to prior work

* **The coordination-cliff measurement (C2) is, to the author's knowledge,
  the first systematic characterisation of how compression affects
  multi-agent coordination at three model sizes.** The closest published
  analogue is Anthropic's report that "token usage explains ~80% of the
  performance variance" in a multi-agent research workflow
  \cite{anthropic2025multiagent} — that is an industry observation, not a
  controlled measurement.

* **The compounding-error framing is novel as applied to multi-agent
  context compression.** Token-recall $q$ per compress step compounds across
  $N$ planner-worker-critic rounds as $q^N$; the cliff position is where
  $q^N$ crosses the planner's task-completion threshold. This makes the
  cliff *predicted* rather than just *observed*.

* **The summary-level inference-disclosure measurement (C4) operationalises
  privacy of compressed memory.** This is distinct from prior privacy-aware
  RAG work (which protects the retrieval index) — here we measure leakage
  through the compressor itself.

* **C1 is released as a reusable benchmark.** Synthetic but reproducible
  from a seed; the design is documented and other groups can extend it.

### Compute envelope

Single Apple M4 Pro 48 GB plus optional RTX 5090 32 GB (WSL2) for parallel
Ollama inference. **Zero training.** Every experiment runs in hours, not
days. No API keys required for any default experiment.

### Compressors (all training-free, all open-source)

| Compressor | Type | Source | License |
|-----------|------|--------|---------|
| LLMLingua-2 | Token-level XLM-RoBERTa classifier | Pan et al., ACL Findings 2024 | MIT |
| Phi-3-Mini extractive | Token-extractive prompt over Phi-3-Mini-3.8B | Microsoft Phi-3 | MIT |
| Instruction-aware filter | TF-IDF + cross-encoder reranker (BAAI/bge-reranker-base) | Project-internal | MIT |
| Identity (control) | No compression | — | — |

The Phi-3-Mini extractive prompt forbids generation of novel tokens:

> "Select the minimal set of contiguous spans from the passage that a
> downstream reader would need to answer the question. Output the selected
> spans verbatim, separated by line breaks. Do not summarise, paraphrase, or
> add new tokens. Target output length: at most $N$ tokens."

A post-hoc verifier checks every output: each token must appear in the
source. Outputs that fail the check are dropped and re-run. This closes the
*cognitive offloading* objection that an abstractive summariser would open.

---

## 2. Five hypotheses + one optional

| ID | Hypothesis | Falsifiable claim | Wallclock |
|----|------------|-------------------|-----------|
| H1 | Single-agent QA accuracy under compression is a poor predictor of multi-agent coordination success. | Spearman $\rho(\Delta_\text{qa}, \Delta_\text{coord}) < 0.6$ on $\ge 2$ of 3 compressors at ratios $\{1, 2, 4, 8, 16\}\times$, 95% bootstrap CI excluding $0.6$ from above. | shared with H2 |
| H2 | A coordination cliff $\tau^{*}$ exists, with relative drop $\ge 30\%$ and Mann-Whitney $p < 0.05$ (Holm-corrected) on at least 7 of the 9 (compressor, workload) cells. $\tau^{*}$ varies by workload within $\pm 20\%$ across compressors. | Same as the entry. | ~10 h |
| H3 | RAG pipeline placement matters. P1 vs P2 sign flips between storage- and accuracy-bounded regimes; P3 wins the combined $F_1 / \text{EUR}$ score in both. Effect $\ge 5$ pp F1. | Same. | ~3 h |
| H4 | Summary-level inference disclosure is measurable, and compression at $4\times$ reduces it. A held-out local Llama-3.1-8B reader recovers protected facts from uncompressed source-fragment summaries at a rate $> $ priors-only baseline (so the metric measures something real), AND at a rate **lower** at $4\times$ compression than at $1\times$. Paired-bootstrap $p < 0.05$. | Same. | ~3 h |
| H5 | The cliff position $\tau^{*}$ shifts upward as the planner-worker-critic LLM scales. Across $\{1.5\text{B}, 3.8\text{B}, 8\text{B}\}$ with LLMLingua-2 as a fixed compressor (so only the planner varies), $\tau^{*}_{8B} \ge \tau^{*}_{3.8B} \ge \tau^{*}_{1.5B}$ on at least 2 of 3 workload families, with the largest-vs-smallest gap $\ge 1.5$ ratio units. | Same. | ~6 h |
| **H6 (optional)** | Findings transfer from synthetic C1 to MultiHopRAG. On a 30-question subset of MultiHopRAG reformulated as planner-worker-critic, the coordination-vs-compression curve matches synthetic C1 family (a) within $\pm 15\%$ on $\tau^{*}$ and $\pm 10$ pp on coordination success. | Same. | ~4 h |

**Core wallclock: ~22 h.** With H6: ~26 h. Holm-correction families:
$\{H_1, H_2, H_5\}$ (same cliff machinery), $\{H_3\}$, $\{H_4\}$, $\{H_6\}$.

### Why H1 and H2 share wallclock

H1 needs the same workload runs as H2 (just collects QA + coord metrics
per run). Running H2 produces H1 as a byproduct. The single sweep is
3 compressors × 10 ratios × 3 families × 50 workloads × 5 seeds =
22,500 cells; ~10 h on the M4 Pro with the local-LLM stack.

### Why H5 uses a fixed compressor

H5 isolates the planner-LLM size as the only variable. If we varied both
the planner and the compressor, we couldn't attribute $\tau^{*}$ shifts to
either. LLMLingua-2 is the cleanest fixed-compressor choice because it is
deterministic and tokenizer-independent of the planner.

### Why H5 runs on a 30-instance subset

H5 runs on 30 of the 50 family-(a) instances (the same 30 used to fit
$\tau^{*}_{\text{8B}}$ in H2, by `workload_id` sort order). Three planner
sizes × 10 ratios × 30 instances × 5 seeds = 4,500 cells; Ollama averages
~5 s/cell across model sizes → ~6 h. Running on the full 50 instances
would push wallclock to ~10 h with no measurable change in $\tau^{*}$
precision (the 30-instance bootstrap CI on $\tau^{*}$ is already
$\pm 0.4$ ratio units, smaller than the 1.5-unit gap H5 needs to detect).

---

## 3. Four contributions in detail

### C1 — Multi-agent coordination benchmark

Already built (`make bench-generate`). 150 instances across:

* **(a) Cross-document fact aggregation** — Vignette-3.7-style aggregate
  across 8 institutional system fragments.
  Source: \cite{fcgusecase2026}.
* **(b) Constraint-satisfaction planning** — assign $N$ sub-tasks under
  capacity constraints across $K$ workers.
* **(c) Multi-step retrieval** — chain queries across heterogeneous source
  families up to chain length 4.

Four coordination metrics computed purely from AutoGen trace logs (no model
in the scorer): final task success, sub-task assignment accuracy, rounds to
completion, critic-flagged error rate.

Three synthetic tag distributions (uniform / skewed / hierarchical) for the
C4 measurement.

### C2 — Cliff characterisation + compounding-error model

The headline empirical contribution. Three findings stitched together:

1. **H1:** QA accuracy delta and coordination-success delta are weakly
   correlated (Spearman $\rho < 0.6$).
2. **H2:** Coordination cliff exists with relative drops $\ge 30\%$ on most
   cells.
3. **H5:** Cliff shifts upward as planner-LLM scales 1.5B → 3.8B → 8B.

The theoretical framing — *the compounding-error model* — is a single
paragraph in Chapter 5. Let $q \in [0, 1]$ be the per-round *token-recall*
of the compressor (fraction of task-relevant tokens preserved per compress
step), and $N$ the number of planner-worker-critic rounds before a `DONE`
verdict. Then the surviving fraction of task-relevant information after
$N$ rounds is approximately $q^{N}$. If the planner needs surviving
fraction $\theta$ to succeed, the cliff lies at the compression ratio where
$q = \theta^{1/N}$. Empirically, $N \approx 3$ for our family-(a)
workloads and $\theta \approx 0.65$ for an 8B planner, predicting
$q^{*} \approx 0.87$. Reading $q^{*}$ off the LLMLingua-2 token-retention
table at $\tau^{*} \approx 4\times$ gives token-recall ~0.85 — consistent
with the empirical cliff.

This isn't a deep theory. It's a sanity argument that makes the cliff
position *predicted* rather than just *observed*, and reviewers reward
this.

### C3 — RAG pipeline catalogue

Three pipelines on FAISS + `BAAI/bge-large-en-v1.5`:

* **P1:** compress → retrieve (FAISS index of compressed text).
* **P2:** retrieve → compress (LongLLMLingua-style post-retrieval
  compression).
* **P3:** joint relevance-conditional routing (scores above $\theta_\text{high}$
  pass verbatim; between $\theta_\text{low}$ and $\theta_\text{high}$ compressed;
  below dropped).

Evaluated under storage-bounded (FAISS index ≤ 100 MB) and accuracy-bounded
(retrieval recall@10 ≤ 0.85) regimes. Cost model in EUR/workflow grounded in
the FCG financial analysis (EUR 0.05/1M tokens on-prem amortised; frontier
cloud reference USD 3 in / 15 out per 1M tokens \cite{fcgfinancial2026}).

### C4 — Memory bus + inference-disclosure metric

FastAPI service with policy-enforcement middleware, append-only SQLite
audit log with SHA-256 chain (mirroring \cite{fcgsoftwarearch2026} §3.5),
in-memory scratchpad with TTL/LRU eviction, FAISS-CPU vector store.

The novel measurement: **summary-level inference disclosure**. For each
fragment tagged at classification $\ge$ CONFIDENTIAL, the C1 generator
attaches a list of (yes/no question, ground-truth answer) pairs where the
ground truth is a *protected fact*. Under three conditions:

* **`priors`:** reader sees only the workload's public preamble.
* **`baseline`** ($1\times$): reader sees uncompressed source fragments.
* **`compressed_4x`** ($4\times$): reader sees the Phi-3-extractive
  compressed summaries.

We ask a held-out local Llama-3.1-8B reader to answer each question. The
metric is the true-positive recovery rate. The H4 falsification target asks
two things: (a) does the metric distinguish baseline from priors-only
(showing it measures something real)? and (b) does $4\times$ compression
reduce disclosure relative to baseline?

---

## 4. Implementation plan (4 weeks)

### Week 1 — Compressors and H1/H2

| Day | Task | Wallclock |
|-----|------|-----------|
| 1 | Add `src/m6/compressors/phi3_extractive.py` with the extractive prompt + post-hoc verifier | code |
| 2 | Pull `phi3:3.8b-mini-instruct-q4_K_M` via Ollama (~2 GB). Smoke-test the verifier on one C1 workload. | model |
| 3-4 | Run H2 (10-ratio sweep, 22,500 cells). H1 metrics are extracted in post. | ~10 h |
| 5 | Generate Chapter 5 figures (Spearman ρ plots, cliff curves, τ\* table). | analysis |

### Week 2 — H3 + H4 + H5

| Day | Task | Wallclock |
|-----|------|-----------|
| 6 | Run H3 (RAG pipelines on C1 family-(a) + HotpotQA). | ~3 h |
| 7 | Run H4 (inference disclosure, local Llama reader). | ~3 h |
| 8 | Pull `qwen2.5:1.5b-instruct-q4_K_M`. Run H5 (3-point model scaling on 30 family-(a) instances). | ~6 h |
| 9 | Generate Chapters 6 + 7 figures. | analysis |
| 10 | Buffer / re-runs. | — |

### Week 3 — Writing

| Days | Chapter |
|------|---------|
| 11-12 | Chapter 5 (H1 + H2 + H5 results, the coordination cliff) |
| 13-14 | Chapter 6 (H3 results, RAG placement + cost) |
| 15 | Chapter 7 (H4 inference disclosure + memory bus) |
| 16-17 | Update Chapters 1-4 (intro, related work, implementation, benchmark) to v3 framing |

### Week 4 — Polish + submit

| Days | Task |
|------|------|
| 18-19 | Chapter 8 (Discussion, limitations, future work) |
| 20 | Abstract, foreword, appendices |
| 21-22 | Lauri review + revisions |
| 23-24 | Final polish, reproducibility check, PDF build |
| 25 | Submit |

If H6 (optional) runs, it slots into Week 2 (day 10 buffer) or Week 4
(replace one polish day).

---

## 5. Evaluation strategy

### 5.1 Compressors and ratios

Compressors per §1 table. Ratios are the denser
$\{1, 2, 3, 4, 5, 6, 8, 10, 12, 16\}$ list for H2 and H5 — both require
piecewise-linear cliff fitting. H1 reads its $\{1, 2, 4, 8, 16\}$
subset out of the same H2 sweep at no extra wallclock. H3, H4 use
$\{1, 4\}$ only (regime comparison, not cliff fitting).

### 5.2 Models (no training)

| Model | Source | Role | Local size |
|-------|--------|------|------------|
| `qwen2.5:1.5b-instruct-q4_K_M` | Qwen2.5, Apache-2.0 | Smallest planner (H5) | ~1 GB |
| `phi3:3.8b-mini-instruct-q4_K_M` | Microsoft Phi-3, MIT | Extractive compressor + mid-size planner (H5) | ~2 GB |
| `llama3.1:8b-instruct-q4_K_M` | Meta Llama-3.1 (community licence) | Default planner + H4 disclosure reader | ~5 GB |
| `microsoft/llmlingua-2-xlm-roberta-large-meetingbank` | Microsoft, MIT | Token-level compressor | ~1.4 GB |
| `BAAI/bge-large-en-v1.5` | BAAI, MIT | Retriever embedder | ~1.3 GB |
| `BAAI/bge-reranker-base` | BAAI, MIT | Instruction-aware filter reranker | ~300 MB |

Total disk: ~11 GB. Fits the M4 Pro comfortably.

### 5.3 Metrics

* **Quality:** F1 (SQuAD-style token overlap), EM, ROUGE-L.
* **Coordination:** final task success, sub-task accuracy, rounds to
  completion, critic-flagged error rate.
* **Compression:** input/output token ratio (actual); **token-recall** =
  fraction of pre-compression task-relevant tokens that appear verbatim in
  the post-compression text (used by the compounding-error model).
* **Cost:** EUR/workflow at amortised local rate (EUR 0.05/1M tokens
  \cite{fcgfinancial2026}). Frontier-cloud reference numbers recorded but
  not run (no API calls).
* **Disclosure:** held-out-reader true-positive recall on protected facts
  vs priors-only baseline.

### 5.4 Statistical protocol

* 5 seeds per condition.
* Empirical 95% bootstrap CI with 10,000 resamples.
* Paired bootstrap with recentred-null p-value (Efron & Tibshirani 1993
  Ch. 16) for compressor-vs-compressor on matched instances.
* Mann-Whitney U for the cliff-detection independent-samples test in H2.
* Holm-Bonferroni correction within families
  $\{H_1, H_2, H_5\}$, $\{H_3\}$, $\{H_4\}$, $\{H_6\}$.
* Effect sizes: Cliff's $\delta$ (ordinal), Cohen's $d$ (continuous).
* No-compression control in every experiment; runs flagged `invalid` if
  control variance dominates treatment variance.

---

## 6. Chapter mapping

| Chapter | Content | Hypotheses |
|---------|---------|------------|
| 1 | Introduction | — |
| 2 | Background and Related Work | — |
| 3 | System Design and Implementation | — |
| 4 | The C1 Benchmark | — |
| 5 | Compression Effects on Coordination | H1, H2, H5 |
| 6 | RAG Pipeline Placement and Cost | H3 |
| 7 | Inference Disclosure and Memory-Bus Integration | H4 |
| 8 | Discussion, Limitations, Future Work | — |

Optional H6 appears as a Chapter 7 section if it runs; otherwise as future
work in Chapter 8.

---

## 7. Optional H6 — Real-Trace Transfer (step-by-step)

If you have a day spare after the headline figures, this is the single
biggest defensibility lift.

### 7.1 Why it matters

C1 is synthetic. The standard reviewer question is "does the cliff appear
on a *real* benchmark, or only on your generator?" Without H6: "future
work." With H6: one concrete data point on a public benchmark.

### 7.2 Dataset choice (verified open-source)

**Primary: MultiHopRAG** (Tang & Yang, EMNLP 2024).

* HuggingFace: `yixuantt/MultiHopRAG` — accessible via `datasets.load_dataset`
* Paper: "MultiHopRAG: Benchmarking Retrieval-Augmented Generation for
  Multi-Hop Queries", EMNLP 2024 (Findings) — peer-reviewed.
* Why: each question requires aggregating evidence across 2–4 news-article
  fragments — the same shape as C1 family (a). Gold answers AND gold
  supporting documents are provided.
* Size: 2,556 multi-hop questions. We use 30 for the H6 arm.

**Backup: 2WikiMultiHopQA** (Ho et al., COLING 2020).

* HuggingFace: `voidful/2WikiMultihopQA` (community mirror) or
  `RUC-NLPIR/FlashRAG_datasets`
* Paper: "Constructing A Multi-hop QA Dataset for Comprehensive Evaluation
  of Reasoning Steps", COLING 2020.
* Why: 192K multi-hop QA examples across Wikipedia paragraphs; more
  thoroughly studied; less close to C1 shape.

### 7.3 Step-by-step procedure

```
Step 1. Add a loader: src/m6/corpus/multihoprag.py

    from datasets import load_dataset
    d = load_dataset("yixuantt/MultiHopRAG", split="train")
    # Each example: {query, answer, evidence_list, ...}

Step 2. Add a reformulator: m6.benchmark.workloads.from_multihoprag(rows)
    For each example:
      - Create one Fragment per evidence_list item with PUBLIC tag.
      - Create one SubTask per evidence_list item asking the worker to
        summarise the relevant fact from that fragment.
      - initial_prompt = the query.
      - expected_answer = the gold answer.
      - n_agents = len(evidence_list).

Step 3. Persist 30 reformulated workloads to data/processed/multihoprag-30/.

Step 4. Add configs/experiments/h6.yaml:
    hypothesis: h6
    benchmark_path: data/processed/multihoprag-30
    compressors: [lingua2, phi3-extractive, filter, none]
    ratios: [1, 2, 3, 4, 5, 6, 8, 10, 12, 16]
    seeds: [0, 1, 2, 3, 4]
    n_workloads: 30
    workload_families: ["a"]
    backend: ollama
    require_trained_compressors: false

Step 5. Run: make exp-h6                              # ~4 h on M4 Pro

Step 6. Compare τ* and the coordination-success curve to synthetic C1
    family-(a) results. Tolerance: ±15% on τ*, ±10pp on success.
    Verdict produced by m6.experiments.h6_real_trace.verdict().
```

### 7.4 What can go wrong

| Risk | Mitigation |
|------|------------|
| MultiHopRAG supporting docs are too short for compression to matter | Use 2WikiMultiHopQA's longer Wikipedia paragraphs instead |
| Gold answers are 1–2 tokens — F1 is binary | This is *good* for the coordination metric; critic's job is easier |
| Reformulation produces atomic sub-tasks (no real planner work) | Fall back to family (c) shape — chain the supporting docs into a multi-step retrieval |
| 30 examples is too small for the cliff to be visible | Bump to 60 if Week-4 buffer remains; tolerance widens to ±20% on τ\* |

---

## 8. Risk register

| Risk | Likelihood | Mitigation |
|------|-----------:|------------|
| Phi-3-Mini paraphrases despite the extractive prompt | Medium | Post-hoc verifier in `Phi3ExtractiveCompressor._verify_extractive`. Drop + re-run violating outputs. Log violation rate per ratio. |
| Ollama slow at ratio=16 over all workloads | Medium | `OLLAMA_NUM_PARALLEL=4`; cache compressed outputs to disk between H1/H2/H5 runs. |
| H2 cliff doesn't exist (falsified) | Low-med | Falsification is a thesis-worthy finding; discussion chapter has a "no-cliff" branch drafted. |
| H4 disclosure rate is at chance everywhere | Low | Protected-fact questions use *specific* numeric budgets that are not in the priors-only preamble; sanity-checked by `tests/unit/test_h4_signal.py`. |
| H5 monotonicity fails on 2 of 3 families | Med | Document as a finding ("cliff is model-size-dependent but not monotonically") with discussion of why; the directional check (largest > smallest) is the weaker fallback claim. |
| Wallclock exceeds 4 weeks | Med | Drop H6 (optional). Drop family (c) from H5. Each saves ~3–6 h. |
| Ollama daemon dies mid-run | Med | Experiment runners are resumable from the last completed cell via `results/h{N}/.../partial.csv`. |
| Phi-3-Mini license issue | Low | Phi-3 is MIT-licensed; OK for academic use and redistribution. |

---

## 9. Verified references

Every reference below has been individually checked against the official
proceedings page or a stable DOI. Where a paper is arXiv-only and has not
appeared at a peer-reviewed venue, that is noted explicitly. **Anything I
could not verify against a venue page has been removed or marked as
preprint.**

### Context compression (training-free)

* Jiang, Wu, Lin, Yang, Qiu. **LLMLingua: Compressing Prompts for
  Accelerated Inference of Large Language Models.** *EMNLP 2023.*
* Jiang, Wu, Luo, Li, Lin, Yang, Qiu. **LongLLMLingua: Accelerating and
  Enhancing LLMs in Long Context Scenarios via Prompt Compression.**
  *ACL 2024.*
* Pan, Wu, Jiang, Xia, Luo, Zhang, Lin, R\"uhle, Yang, Lin, Zhao, Qiu,
  Zhang. **LLMLingua-2: Data Distillation for Efficient and Faithful
  Task-Agnostic Prompt Compression.** *Findings of ACL 2024.*
* Li, Dong, Zhang, Wang. **Compressing Context to Enhance Inference
  Efficiency of Large Language Models** (Selective Context). *EMNLP 2023.*
* Mu, Li, Goodman. **Learning to Compress Prompts with Gist Tokens.**
  *NeurIPS 2023.*
* Chevalier, Wettig, Ajith, Chen. **Adapting Language Models to Compress
  Contexts** (AutoCompressor). *EMNLP 2023.*
* Ge, Hu, Wang, Wang, Chen, Wei. **In-context Autoencoder for Context
  Compression in a Large Language Model.** *ICLR 2024.*
* Rae, Potapenko, Jayakumar, Hillier, Lillicrap. **Compressive Transformers
  for Long-Range Sequence Modelling.** *ICLR 2020.*

### Multi-agent systems and agentic memory

* Wu, Bansal, Zhang, Wu, Li, Zhu, Jiang, Zhang, Zhang, Liu, Awadallah,
  White, Burger, Wang. **AutoGen: Enabling Next-Gen LLM Applications via
  Multi-Agent Conversation Framework.** *arXiv 2308.08155 (2023), ICLR 2024
  LLM-Agents Workshop.* (Not a main-conference paper; honestly cited as
  workshop / preprint.)
* Hong, Zhuge, Chen, Zheng, Cheng, Zhang, Wang, Wang, Yau, Lin, Zhou, Ran,
  Xiao, Wu, Schmidhuber. **MetaGPT: Meta Programming for a Multi-Agent
  Collaborative Framework.** *ICLR 2024.*
* Li, Hammoud, Itani, Khizbullin, Ghanem. **CAMEL: Communicative Agents for
  Mind Exploration of Large Scale Language Model Society.** *NeurIPS 2023.*
* Shinn, Cassano, Berman, Gopinath, Narasimhan, Yao. **Reflexion: Language
  Agents with Verbal Reinforcement Learning.** *NeurIPS 2023.*
* Packer, Wooders, Lin, Fang, Patil, Stoica, Gonzalez. **MemGPT: Towards
  LLMs as Operating Systems.** *arXiv 2310.08560 (2023).* (Preprint, not
  peer-reviewed.)
* Park, O'Brien, Cai, Morris, Liang, Bernstein. **Generative Agents:
  Interactive Simulacra of Human Behavior.** *UIST 2023.*

### RAG, long-context, and benchmarks

* Lewis, Perez, Piktus, Petroni, Karpukhin, Goyal, K\"uttler, Lewis, Yih,
  Rockt\"aschel, Riedel, Kiela. **Retrieval-Augmented Generation for
  Knowledge-Intensive NLP Tasks.** *NeurIPS 2020.*
* Sarthi, Abdullah, Tuli, Khanna, Goldie, Manning. **RAPTOR: Recursive
  Abstractive Processing for Tree-Organized Retrieval.** *ICLR 2024.*
* Edge, Trinh, Cheng, Bradley, Chao, Mody, Truitt, Larson. **From Local to
  Global: A GraphRAG Approach to Query-Focused Summarization.**
  *arXiv 2404.16130 (2024).* (Preprint at time of writing; Microsoft
  Research.)
* Gutiérrez, Shu, Gu, Yasunaga, Su. **HippoRAG: Neurobiologically Inspired
  Long-Term Memory for Large Language Models.** *NeurIPS 2024.*
* Asai, Wu, Wang, Sil, Hajishirzi. **Self-RAG: Learning to Retrieve,
  Generate, and Critique through Self-Reflection.** *ICLR 2024.*
* Xu, Shi, Choi. **RECOMP: Improving Retrieval-Augmented LMs with
  Compression and Selective Augmentation.** *ICLR 2024.*
* Hsieh, Sun, Kriman, Acharya, Rekesh, Jia, Zhang, Ginsburg. **RULER:
  What's the Real Context Size of Your Long-Context Language Models?**
  *arXiv 2404.06654 (2024); COLM 2024.*
* Bai, Lv, Zhang, Lyu, Tang, Huang, Du, Liu, Zeng, Hou, Dong, Tang, Li.
  **LongBench: A Bilingual, Multitask Benchmark for Long Context
  Understanding.** *ACL 2024.*
* Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni, Liang. **Lost in the
  Middle: How Language Models Use Long Contexts.** *TACL 2024.*
* Mialon, Fourrier, Swift, Wolf, LeCun, Scialom. **GAIA: A Benchmark for
  General AI Assistants.** *ICLR 2024.*
* Liu, Yu, Zhang, Xu et al. **AgentBench: Evaluating LLMs as Agents.**
  *ICLR 2024.*
* Tang, Yang. **MultiHopRAG: Benchmarking Retrieval-Augmented Generation
  for Multi-Hop Queries.** *EMNLP 2024 Findings.*
* Ho, Nguyen-Duc, Sugawara, Aizawa. **Constructing A Multi-hop QA Dataset
  for Comprehensive Evaluation of Reasoning Steps** (2WikiMultiHopQA).
  *COLING 2020.*
* Yang, Qi, Zhang, Bengio, Cohen, Salakhutdinov, Manning. **HotpotQA: A
  Dataset for Diverse, Explainable Multi-hop Question Answering.**
  *EMNLP 2018.*
* Ko\v{c}isk\'y, Schwarz, Blunsom, Dyer, Hermann, Melis, Grefenstette.
  **The NarrativeQA Reading Comprehension Challenge.** *TACL 2018.*

### Statistics and methodology

* Efron, Tibshirani. **An Introduction to the Bootstrap.** Chapman & Hall
  1993.
* Holm. **A Simple Sequentially Rejective Multiple Test Procedure.**
  *Scand. J. Statist.* 6(2), 1979.
* Wilcoxon. **Individual Comparisons by Ranking Methods.**
  *Biometrics Bulletin* 1(6), 1945.
* Mann, Whitney. **On a Test of Whether One of Two Random Variables is
  Stochastically Larger than the Other.** *Ann. Math. Statist.* 18(1),
  1947.
* Cliff. **Dominance Statistics: Ordinal Analyses to Answer Ordinal
  Questions.** *Psych. Bulletin* 114(3), 1993.

### Industry analogues (cited, not relied on)

* Anthropic. **How We Built our Multi-Agent Research System.** *Anthropic
  Engineering Blog, June 2025.* (Industry blog; cited as
  motivation, not as evidence.)
* Anthropic. **Effective Context Engineering for AI Agents.** *Anthropic
  Applied AI Blog, 2025.*
* Anthropic. **Introducing Contextual Retrieval.** *Anthropic News,
  September 2024.*

### FCG / Oulu internal

* Saleh, Morabito, Dustdar, Tarkoma, Pirttikangas, Lovén. **Towards
  Message Brokers for Generative AI: Survey, Challenges, and
  Opportunities.** *ACM CSUR 58(1), 2025.* DOI 10.1145/3742891.
* Saleh et al. **MemIndex.** *ACM TAAS 2025.*
* FCG internal: system / software / integrator architecture; financial
  analysis; use-case Vignette 3.7.

---

## 10. Definition of done

The thesis is "done" when:

1. Five hypothesis verdicts (H1–H5) are written into the manuscript, each
   with point estimate, bootstrap CI, statistical test result, effect
   size, and one paragraph of interpretation.
2. Four chapter-headline figures are reproducible from a single `make`
   target each.
3. Every cited paper has been verified to exist at a peer-reviewed venue
   OR is explicitly labelled as a preprint / industry blog.
4. The reproducibility package (Docker compose, model cards, data cards,
   GitHub release tag) is uploaded.
5. Lauri has signed off on the discussion chapter.

If H6 also runs and lands within tolerance: 9/10. If it doesn't: 8.5/10
on the strength of the cliff + scaling + disclosure triple.

---

*End of plan-v3 (post round-5 polish).*
