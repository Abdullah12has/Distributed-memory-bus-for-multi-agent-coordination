# Think-in-Memory: Recalling and Post-thinking Enable LLMs with Long-Term Memory

**Authors:** Lei Liu, Xiaoyan Yang, Yue Shen, Binbin Hu, Zhiqiang Zhang, Jinjie Gu, Guannan Zhang

**Venue:** arXiv preprint (cs.CL), 2023

**arXiv:** [https://arxiv.org/abs/2311.08719](https://arxiv.org/abs/2311.08719)

---

## Abstract

The authors propose TiM (Think-in-Memory), a novel memory mechanism for large language models that enables them to maintain an evolved memory for storing historical thoughts along the conversation stream. The approach operates in two stages: (1) before generating a response, the LLM recalls relevant historical thoughts from memory; (2) after generation, a post-thinking phase incorporates both historical and newly generated thoughts back into memory. The framework organizes thoughts using insert, forget, and merge operations, and employs Locality-Sensitive Hashing (LSH) for efficient retrieval in long-term conversations. Experiments on real-world and simulated dialogues demonstrate significant performance improvements across diverse topics.

---

## 1. Introduction

### 1.1 Problem: Repeated Reasoning Bias

In long-term conversations, LLMs face a critical challenge: they repeatedly reason about the same topics without building on prior conclusions. This leads to:
- Inconsistent responses across conversation turns
- Wasted computation on redundant reasoning
- Inability to develop evolving understanding over time

### 1.2 Key Insight

Rather than storing raw conversation history (as in retrieval-augmented approaches), TiM stores the *results of reasoning* (thoughts). This means:
- The model builds on prior conclusions rather than re-deriving them
- Memory evolves as new information arrives
- Retrieved thoughts provide higher-quality context than raw history

## 2. Method: Think-in-Memory (TiM)

### 2.1 Overall Framework

TiM consists of two stages that bracket the response generation:

**Pre-Response: Recall Stage**
1. Given a new user input, compute its representation
2. Use LSH to efficiently retrieve relevant thoughts from memory
3. Provide retrieved thoughts as additional context for response generation

**Post-Response: Post-Think Stage**
1. After generating the response, the LLM reflects on the conversation
2. New thoughts are generated based on the current exchange
3. Memory is updated using three operations:
   - **Insert:** Add entirely new thoughts
   - **Forget:** Remove outdated or contradicted thoughts
   - **Merge:** Combine related thoughts into more comprehensive ones

### 2.2 Thought Representation

Each thought is stored as:
- Natural language description of the reasoning/conclusion
- Vector embedding for similarity-based retrieval
- Metadata (creation time, update count, source turns)

### 2.3 Memory Operations

**Insert Operation:**
- Triggered when the post-thinking phase produces thoughts on new topics
- New thoughts are embedded and added to the memory store

**Forget Operation:**
- Triggered when new information contradicts or supersedes stored thoughts
- Outdated thoughts are marked for removal

**Merge Operation:**
- Triggered when new and existing thoughts overlap significantly
- Related thoughts are combined into a more comprehensive thought
- Reduces memory redundancy while preserving information

### 2.4 Efficient Retrieval with LSH

Locality-Sensitive Hashing enables sub-linear retrieval time:
- Thoughts are hashed into buckets based on embedding similarity
- Query embeddings are hashed to identify candidate buckets
- Only candidates in matching buckets are scored for relevance
- Scales to thousands of stored thoughts efficiently

## 3. Experimental Setup

### 3.1 Datasets

- **Real-world dialogues:** Multi-turn conversations from diverse domains
- **Simulated dialogues:** Controlled scenarios testing specific memory capabilities
- Topics span personal assistants, knowledge-intensive QA, and opinion tracking

### 3.2 Baselines

- Standard LLM (no memory)
- Sliding window context
- Full conversation history (when feasible)
- RAG with raw history retrieval
- Other memory-augmented approaches

### 3.3 Metrics

- Response quality (relevance, coherence, informativeness)
- Consistency across conversation turns
- Memory retrieval precision and recall
- Reasoning efficiency (reduced repeated computation)

## 4. Results

### 4.1 Response Quality

TiM demonstrates significant improvements across all dialogue scenarios:
- Higher relevance scores when prior context matters
- More consistent responses across long conversations
- Better handling of topic revisits and follow-up questions

### 4.2 Memory Evolution

The merge and forget operations prove critical:
- Without merge: memory grows unboundedly, retrieval quality degrades
- Without forget: contradicted thoughts persist, causing inconsistencies
- Full TiM: memory remains compact and high-quality over extended conversations

### 4.3 Efficiency

- LSH retrieval scales well with memory size
- Post-thinking adds modest overhead per turn but saves computation in subsequent turns
- Total computation across long conversations is reduced compared to re-processing full history

## 5. Analysis

### 5.1 Thought Quality

Stored thoughts are more useful than raw conversation excerpts because:
- They capture conclusions rather than deliberation
- They are pre-processed for relevance
- Merged thoughts consolidate information from multiple turns

### 5.2 Memory Dynamics

Over the course of a conversation:
- Memory size grows sub-linearly due to merge operations
- Average thought quality improves as redundancies are removed
- Retrieval precision increases as the memory becomes more structured

### 5.3 Ablation Studies

| Component | Impact on Quality |
|---|---|
| Full TiM | Best performance |
| Without post-thinking | Significant degradation |
| Without recall | Large degradation |
| Without merge | Moderate degradation (memory bloat) |
| Without forget | Moderate degradation (contradictions) |
| Without LSH (brute force) | Same quality, slower retrieval |

## 6. Related Work

- **Memory-augmented LLMs:** MemoryBank, SCM, ReadAgent
- **Retrieval augmentation:** RAG, RETRO, kNN-LM
- **Cognitive architectures:** SOAR, ACT-R (inspiration for thought-based memory)
- **Long-context processing:** Transformer-XL, Memorizing Transformers

TiM is distinguished by storing reasoning results rather than raw data, and by actively evolving memory through post-thinking.

## 7. Conclusion

Think-in-Memory demonstrates that storing and evolving reasoning outputs (thoughts) provides a more effective long-term memory than raw history retrieval. The two-stage recall-and-post-think framework, combined with insert/forget/merge operations, enables LLMs to build on prior reasoning, maintain consistency, and efficiently handle long-term conversations.

---

## Key Figures

- **Figure 1:** TiM framework overview showing the recall and post-think stages around response generation.
- **Figure 2:** Memory evolution over conversation turns, showing insert/forget/merge operations.
- **Figure 3:** LSH-based retrieval pipeline for efficient thought access.
- **Figure 4:** Comparison of response quality across baselines and ablations.

---

## Top References

1. Vaswani et al. (2017). Attention Is All You Need. NeurIPS.
2. Lewis et al. (2020). Retrieval-Augmented Generation. NeurIPS.
3. Dai et al. (2019). Transformer-XL. ACL.
4. Wu et al. (2022). Memorizing Transformers. ICLR.
5. Weston et al. (2015). Memory Networks. ICLR.
6. Park et al. (2023). Generative Agents: Interactive Simulacra of Human Behavior.
7. Zhong et al. (2023). MemoryBank: Enhancing Large Language Models with Long-Term Memory.
8. Wang et al. (2023). SCM: Self-Controlled Memory Framework for LLMs.
9. Borgeaud et al. (2022). RETRO: Improving Language Models by Retrieving from Trillions of Tokens. ICML.
10. Andoni & Indyk (2008). Near-Optimal Hashing Algorithms for Approximate Nearest Neighbor.
