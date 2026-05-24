# Essential Reading List for M6 Thesis

Organised by theme. Priority: **must-read** (core to your contribution), **should-read** (context/methods), **nice-to-have** (broadens framing).

---

## 1. Context Compression (Core — Your Compressors)

### LLMLingua (EMNLP 2023) — MUST-READ
**Jiang et al.** "LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models"

Your thesis uses LLMLingua-2, but this is the original. Introduces budget-controller + iterative token pruning using a small LM's perplexity to decide which tokens to drop. Key idea: low-perplexity tokens are redundant (the LM "expects" them). Demonstrates 2-20x compression with <5% performance loss on GSM8K, BBH, etc. **You need this to explain why token-level compression works at all.**

### LLMLingua-2 (ACL Findings 2024) — MUST-READ
**Pan et al.** "LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression"

Your primary compressor. Key upgrade: replaces GPT-4-based perplexity with a distilled XLM-RoBERTa classifier trained on token-level "keep/drop" labels extracted from GPT-4 compressions. **Task-agnostic** (no query needed). 3-6x faster than LLMLingua. This is the model behind your `lingua2.py`. **Understand the token-classification approach because your thesis measures what happens when it drops the wrong tokens.**

### LongLLMLingua (ACL 2024) — SHOULD-READ
**Jiang et al.** "LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression"

Extends LLMLingua to long-context with **question-aware** compression (conditions on the query). Your H3 hypothesis directly challenges this paper's assumption that retrieve-first-then-compress (their approach) is better than compress-first-then-retrieve. Your finding that P1 > P2 in both regimes contradicts LongLLMLingua's design rationale. **Cite this as the foil for H3.**

### Selective Context (EMNLP 2023) — SHOULD-READ
**Li et al.** "Compressing Context to Enhance Inference Efficiency of Large Language Models"

Simpler approach: uses self-information (negative log probability) to select informative tokens. No training. Predecessor to LLMLingua. Good for your related-work chapter to show the evolution from simple selection to trained classifiers. Your `filter.py` (TF-IDF + reranker) is spiritually similar — both rank tokens/sentences by informativeness.

### RECOMP (ICLR 2024) — SHOULD-READ
**Xu, Shi, Choi.** "RECOMP: Improving Retrieval-Augmented LMs with Compression and Selective Augmentation"

Two approaches: extractive (select sentences) and abstractive (generate summary). Directly relevant to your Phi-3-extractive compressor design. RECOMP trains the compressor; you use zero-shot prompting + post-hoc verification. **Compare your approach to theirs in the related work — your novelty is the training-free extractive constraint.**

### Gist Tokens (NeurIPS 2023) — NICE-TO-HAVE
**Mu, Li, Goodman.** "Learning to Compress Prompts with Gist Tokens"

Trains the LM itself to compress prompts into a few "gist" tokens in the embedding space. Fundamentally different from your approach (yours operates on text tokens, theirs on hidden states). Good for positioning your work as complementary: text-level compression is interpretable and auditable; gist tokens are not.

### In-Context Autoencoder / ICAE (ICLR 2024) — NICE-TO-HAVE
**Ge et al.** "In-context Autoencoder for Context Compression in a Large Language Model"

You originally planned to use ICAE but abandoned it (training failed). Still worth citing as the approach you chose NOT to take. ICAE requires LoRA fine-tuning of the target LLM, making it non-portable. Your thesis argument is that training-free compression is more practical for multi-agent systems where the downstream LLM may change.

---

## 2. Multi-Agent LLM Systems (Core — Your Problem Domain)

### AutoGen (ICLR 2024 Workshop) — MUST-READ
**Wu et al.** "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework"

Your orchestrator is modeled on AutoGen's planner-worker-critic pattern. Key concepts: conversable agents, group chat, conversation patterns. **You use a deterministic version of this for H1/H2 and an Ollama-backed version for H5.** Understand the conversation flow to explain why information loss compounds across rounds (your compounding-error model).

### MetaGPT (ICLR 2024) — SHOULD-READ
**Hong et al.** "MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework"

SOP-driven multi-agent system where agents communicate through structured artifacts (documents, code). Relevant contrast: MetaGPT assumes agents share a global message pool (like your memory bus). They don't study what happens when that shared memory is compressed. **Your work fills this gap.**

### CAMEL (NeurIPS 2023) — SHOULD-READ
**Li et al.** "CAMEL: Communicative Agents for Mind Exploration of Large Scale Language Model Society"

Role-playing multi-agent communication. Studies emergent cooperation/competition. Less technical than AutoGen/MetaGPT but influential. Relevant for your intro/related-work to establish that multi-agent LLM systems are an active research area. The "inception prompting" technique is interesting for understanding how agents coordinate.

### Generative Agents (UIST 2023) — SHOULD-READ
**Park et al.** "Generative Agents: Interactive Simulacra of Human Behavior"

25 LLM-powered agents in a sandbox world with memory, reflection, and planning. Their memory architecture (observation → reflection → planning) is the closest prior art to your memory bus. Key difference: they use uncompressed memory with retrieval; you compress the stored content. **Cite for the memory-architecture lineage.**

### MemGPT (Preprint, 2023) — SHOULD-READ
**Packer et al.** "MemGPT: Towards LLMs as Operating Systems"

Treats the LLM's context window as "virtual memory" with paging in/out of a larger store. Directly relevant: MemGPT's core problem (context window too small) is what your compression layer solves. They use hierarchical memory; you use compression. **Your approach is complementary — compression + retrieval vs. paging.**

### Reflexion (NeurIPS 2023) — NICE-TO-HAVE
**Shinn et al.** "Reflexion: Language Agents with Verbal Reinforcement Learning"

Agents that learn from their mistakes by storing verbal feedback in memory. The "verbal reinforcement" is stored text that compounds across episodes — analogous to your multi-round compression concern. If compression corrupts the feedback, the agent can't learn from errors.

---

## 3. RAG and Long-Context (Core — Your H3 Pipeline Work)

### RAG Original (NeurIPS 2020) — MUST-READ
**Lewis et al.** "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"

The foundational RAG paper. Combines a pretrained retriever (DPR) with a generator (BART). Your H3 tests three different orderings of compression within this retrieve-then-generate pipeline. **You need to understand the base architecture to explain why pipeline ordering matters.**

### RAPTOR (ICLR 2024) — SHOULD-READ
**Sarthi et al.** "RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval"

Builds a tree of document summaries (leaf → cluster → abstract). Relevant to your P3 pipeline (relevance-conditional routing). RAPTOR pre-compresses at index time (like your P1); your P2 compresses at query time. The tree structure is a more sophisticated version of your compress-first approach.

### GraphRAG (Microsoft, Preprint 2024) — NICE-TO-HAVE
**Edge et al.** "From Local to Global: A GraphRAG Approach to Query-Focused Summarization"

Builds a knowledge graph from documents, then generates community summaries. An alternative to your FAISS-based retrieval. Good for the "future work" section — could your memory bus integrate graph-based retrieval?

### Self-RAG (ICLR 2024) — NICE-TO-HAVE
**Asai et al.** "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection"

The LLM decides when to retrieve and self-critiques its outputs. The "critic" role parallels your planner-worker-critic loop. Relevant for understanding how retrieval quality affects downstream generation.

### HippoRAG (NeurIPS 2024) — NICE-TO-HAVE
**Gutierrez et al.** "HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models"

Hippocampus-inspired memory with pattern separation and completion. Interesting for your discussion chapter — their biological framing complements your engineering approach to agent memory.

### Lost in the Middle (TACL 2024) — SHOULD-READ
**Liu et al.** "Lost in the Middle: How Language Models Use Long Contexts"

Shows that LLMs attend most to the beginning and end of long contexts, missing information in the middle. Directly relevant: your compression removes tokens uniformly, but this paper suggests the LLM wouldn't have used middle tokens anyway. **Could explain why moderate compression (2-4x) sometimes improves performance — it removes the "lost middle."**

---

## 4. Benchmarks (Your C1 Design and Evaluation)

### MultiHopRAG (EMNLP Findings 2024) — SHOULD-READ
**Tang & Yang.** "MultiHopRAG: Benchmarking Retrieval-Augmented Generation for Multi-Hop Queries"

Your optional H6 transfer validation uses this. 2,556 multi-hop questions over news articles. Key property: each answer requires aggregating evidence across 2-4 documents — same structure as your C1 family-(a). If you run H6, you must understand this benchmark's scoring.

### HotpotQA (EMNLP 2018) — NICE-TO-HAVE
**Yang et al.** "HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering"

Classic multi-hop QA benchmark. Your early sanity checks used this. Less relevant now (you use C1 synthetic benchmark), but cite for comparison to show your C1 is structurally similar to established benchmarks.

### AgentBench (ICLR 2024) — NICE-TO-HAVE
**Liu et al.** "AgentBench: Evaluating LLMs as Agents"

Evaluates LLMs across 8 agent environments (OS, DB, web, etc). Relevant for positioning your C1 benchmark: AgentBench tests general agent capability; your C1 tests coordination under compression specifically. **Different evaluation dimensions.**

### LongBench (ACL 2024) — NICE-TO-HAVE
**Bai et al.** "LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding"

Tests long-context abilities across many tasks. Relevant if reviewers ask "why not test on LongBench?" — answer: LongBench tests single-agent long-context, your C1 tests multi-agent coordination.

### RULER (COLM 2024) — NICE-TO-HAVE
**Hsieh et al.** "RULER: What's the Real Context Size of Your Long-Context Language Models?"

Shows that effective context size is much smaller than the advertised window. Supports your thesis argument: even with long-context models, compression matters because models can't use the full window effectively.

---

## 5. Statistics and Methodology

### Efron & Tibshirani — Bootstrap (1993) — MUST-READ (Chapter 16)
**"An Introduction to the Bootstrap"** — Chapman & Hall

Your statistical protocol uses bootstrap CI and paired bootstrap with recentered null. Chapter 16 specifically covers the recentered-null p-value construction you use. **You don't need the whole book — just Chapter 16 for the p-value method and Chapter 14 for bootstrap CI.**

### Holm (1979) — SHOULD-READ
**"A Simple Sequentially Rejective Multiple Test Procedure"** — Scand. J. Statist.

Your Holm-Bonferroni correction for multiple comparisons. Short paper (6 pages). Understand why Holm is preferred over Bonferroni (less conservative, uniformly more powerful) and when to apply it (within hypothesis families, not across).

---

## 6. Industry Context (Motivation, Not Evidence)

### Anthropic Multi-Agent Blog (2025) — SHOULD-READ
**"How We Built our Multi-Agent Research System"**

Industry validation that multi-agent systems face context/memory challenges at scale. They report "token usage explains ~80% of performance variance" — your thesis provides controlled measurements of exactly this phenomenon. **Cite as motivation, not evidence.**

### Anthropic Context Engineering Blog (2025) — NICE-TO-HAVE
**"Effective Context Engineering for AI Agents"**

Practical guide to managing context for agents. Complements your theoretical framing with industry practice.

---

## 7. FCG / University of Oulu Internal

### Saleh et al. — Message Brokers for GenAI (ACM CSUR 2025) — MUST-READ
**"Towards Message Brokers for Generative AI: Survey, Challenges, and Opportunities"**

Your research group's survey. Positions your memory bus in the broader context of message-passing for AI systems. You're extending this work with the compression layer.

### Saleh et al. — MemIndex (ACM TAAS 2025) — SHOULD-READ
Direct predecessor. Memory indexing for multi-agent systems. Your memory bus builds on this infrastructure.

---

## Reading Order Recommendation

If you have limited time, read in this order:

1. **LLMLingua-2** (your main compressor — understand what it does)
2. **AutoGen** (your orchestrator pattern)
3. **RAG Original** (your pipeline foundation)
4. **Lost in the Middle** (explains why compression can help)
5. **LongLLMLingua** (your H3 foil)
6. **Efron Ch.16** (your statistical method)
7. **Generative Agents** (memory architecture lineage)
8. **MemGPT** (closest context-management approach)
9. **RECOMP** (position your phi3-extractive against)
10. **Saleh CSUR** (your group's context)
