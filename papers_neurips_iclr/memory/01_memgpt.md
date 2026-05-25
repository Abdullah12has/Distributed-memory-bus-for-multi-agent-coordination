# MemGPT: Towards LLMs as Operating Systems

**Authors:** Charles Packer, Sarah Wooders, Kevin Lin, Vivian Fang, Shishir G. Patil, Ion Stoica, Joseph E. Gonzalez

**Venue:** ICLR 2024 (Spotlight)

**arXiv:** [https://arxiv.org/abs/2310.08560](https://arxiv.org/abs/2310.08560)

---

## Abstract

Large language models (LLMs) have revolutionized AI, but their limited context windows restrict their utility in tasks demanding sustained reasoning or interaction over extended periods. MemGPT proposes virtual context management, a technique drawing inspiration from hierarchical memory systems in traditional operating systems. MemGPT manages different memory tiers to effectively provide extended context within the LLM's limited context window, and utilizes interrupts to manage control flow between itself and the user. The system is evaluated on document analysis and multi-session chat, demonstrating its ability to handle documents and conversations that vastly exceed the underlying LLM's native context window capacity.

---

## 1. Introduction

The fundamental limitation of LLMs is their fixed context window. MemGPT draws a direct analogy to OS memory management:
- **Context windows** function as main memory (fast, limited)
- **External storage** acts as disk (slow, unlimited)
- **Events** trigger LLM inference (like hardware interrupts)
- **Function calls** enable self-directed memory management

## 2. Core Architecture

### Memory Hierarchy

MemGPT divides memory into two tiers:

**Main Context (Physical Memory):**

| Section | Type | Description |
|---------|------|-------------|
| System instructions | Static, read-only | Core behavioral guidelines |
| Working context | Fixed-size, read/write | Editable via function calls |
| FIFO queue | Rolling, summarized | Message history with recursive summaries |

**External Context (Disk Storage):**

| Component | Description |
|-----------|-------------|
| Recall storage | Complete message database (searchable) |
| Archival storage | Arbitrary-length text objects (vector-indexed) |

### Key Mechanisms

**Queue Manager:**
- Memory pressure warnings at 70% capacity
- Queue flushing at 100% capacity with recursive summarization
- All messages stored permanently in recall storage

**Function Executor:**
- Interprets LLM outputs as function calls
- Moves data between memory tiers
- Modifies working context
- Retrieves historical information

**Function Chaining:**
- Special flags enable sequential function execution
- Multi-step operations complete before returning to user
- Enables complex memory management workflows

### OS Analogy

| OS Concept | MemGPT Equivalent |
|-----------|-------------------|
| Virtual memory | Virtual context management |
| Main memory (RAM) | LLM context window |
| Disk storage | External databases |
| Page faults | Context cache misses |
| Interrupts | User messages, system events |
| System calls | Memory management functions |

## 3. Experimental Evaluation

### Task 1: Conversational Agents

**Deep Memory Retrieval (DMR) -- Consistency Testing:**

| Model | Accuracy | ROUGE-L |
|-------|----------|---------|
| GPT-3.5 Turbo | 38.7% | 0.394 |
| MemGPT + GPT-3.5 | **66.9%** | **0.629** |
| GPT-4 | 32.1% | 0.296 |
| MemGPT + GPT-4 | **92.5%** | **0.814** |
| GPT-4 Turbo | 35.3% | 0.359 |
| MemGPT + GPT-4 Turbo | **93.4%** | **0.827** |

MemGPT provides a 2-3x improvement across all base models.

**Conversation Opener Task -- Engagement Testing:**
MemGPT achieved similarity scores approaching or exceeding human-written openings across multiple base models.

### Task 2: Document Analysis

**Multi-Document Question Answering:**
- MemGPT maintained consistent performance as document count increased
- Fixed-context baselines showed performance ceiling at retriever limitations
- Baselines required document truncation, causing accuracy degradation

**Nested Key-Value Retrieval:**

| Nesting Level | GPT-3.5/4 Baseline | MemGPT + GPT-4 |
|---------------|--------------------|--------------:|
| 0 | ~100% | ~100% |
| 1 | 0% | ~95% |
| 2 | 0% | ~90% |
| 3 | 0% | ~85% |
| 4 | 0% | ~80% |

Demonstrates multi-hop retrieval capability through iterative function calls.

## 4. Released Resources

- Augmented Multi-Session Chat dataset
- Nested key-value retrieval benchmark
- 20M Wikipedia article embeddings

## 5. Discussion

### Key Innovations
- Architectural solutions overcome LLM limitations without model retraining
- Self-directed memory management via function calls
- Interrupts enable complex control flow

### Limitations
- Added latency from multiple LLM calls per user interaction
- Memory management overhead increases with conversation length
- Relies on LLM's ability to correctly use function calls
- No guarantee of optimal memory management strategies

---

## Figure Descriptions

- **Figure 1:** OS memory hierarchy analogy: main memory (context window) vs. disk storage (external databases) with paging mechanism
- **Figure 2:** MemGPT system architecture showing main context sections (system, working memory, FIFO queue) and external storage (recall, archival)
- **Figure 3:** Function chaining example demonstrating multi-step memory operations
- **Figure 4:** Deep Memory Retrieval accuracy comparison across models with and without MemGPT
- **Figure 5:** Document analysis scaling behavior as document count increases

---

## Top 10 References

1. Vaswani, A., et al. (2017). Attention is all you need. *NeurIPS*.
2. Brown, T., et al. (2020). Language models are few-shot learners. *NeurIPS*.
3. Liu, N., et al. (2023). Lost in the middle: How language models use long contexts. *arXiv*.
4. Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS*.
5. Schick, T., et al. (2023). Toolformer: Language models can teach themselves to use tools. *NeurIPS*.
6. Park, J. S., et al. (2023). Generative agents: Interactive simulacra of human behavior. *UIST*.
7. Beltagy, I., et al. (2020). Longformer: The long-document transformer. *arXiv*.
8. Karpukhin, V., et al. (2020). Dense passage retrieval for open-domain question answering. *EMNLP*.
9. Yao, S., et al. (2022). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
10. Xu, X., et al. (2021). Beyond goldfish memory: Long-term open-domain conversation. *ACL*.
