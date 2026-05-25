# Walking Down the Memory Maze: Beyond Context Limit through Interactive Reading (MemWalker)

**Authors:** Howard Chen, Ramakanth Pasunuru, Jason Weston, Asli Celikyilmaz

**Venue:** arXiv preprint (cs.CL), 2023

**arXiv:** [https://arxiv.org/abs/2310.05029](https://arxiv.org/abs/2310.05029)

**Note:** This is the same paper as long_context/10_memwalker.md, included here for the memory category as well.

---

## Abstract

Large language models (LLMs) have advanced in large strides due to the effectiveness of the self-attention mechanism that processes and compares all tokens at once. However, this mechanism comes with a fundamental issue -- the predetermined context window is bound to be limited. The authors propose MemWalker, which treats the LLM as an interactive agent that navigates a tree of summary nodes constructed from the long text. Given a query, the model traverses this tree to locate and gather relevant information, then responds once sufficient context is found. MemWalker outperforms baseline approaches on long-text question answering tasks and provides enhanced explainability by highlighting reasoning steps during interactive reading.

---

## 1. Introduction

Existing approaches to handling long contexts fall into three categories, each with limitations:
1. **Architectural modifications** (sparse/linear attention, recurrence) -- require retraining
2. **Position extrapolation** (RoPE scaling, ALiBi) -- quality degrades with distance
3. **Retrieval augmentation** (RAG) -- may miss relevant context, loses document structure

MemWalker takes a fundamentally different approach: the LLM actively navigates a structured representation of the document, choosing which parts to examine based on the query.

## 2. Method

### 2.1 Tree Construction (Preprocessing)

**Step 1: Segmentation** -- Divide the document into segments fitting within the context window, creating leaf nodes.

**Step 2: Summarization** -- Each leaf is summarized by the LLM, capturing key facts, entities, and relationships.

**Step 3: Hierarchical Aggregation** -- Groups of summaries form parent nodes with meta-summaries. Process repeats until a single root node is created.

### 2.2 Interactive Navigation (Query Time)

**Step 1:** Start at the root, read the overview summary.

**Step 2:** At each internal node, read child summaries and select the most promising branch.

**Step 3:** At leaf nodes, gather sufficient information and generate the answer. Backtrack if needed.

The LLM explains its reasoning at each navigation step, providing full transparency.

### 2.3 Navigation Complexity

- Tree depth: O(log N) where N is document length
- Navigation steps per query: typically 4-6
- Total tokens processed: proportional to tree depth, not document length

## 3. Experimental Results

### 3.1 Datasets

- **QuALITY:** Long-document multiple-choice QA (up to 8K tokens)
- **NarrativeQA:** Story comprehension QA (up to 100K+ tokens)
- **Extended synthetic tasks:** Custom multi-hop reasoning over long documents

### 3.2 Performance

MemWalker outperforms baselines (truncation, BM25/dense retrieval, recurrence) on long-document QA. The performance advantage grows with document length due to logarithmic scaling.

### 3.3 Explainability

Each navigation step includes the LLM's reasoning for its choice, creating a transparent audit trail of how the answer was derived.

## 4. Analysis

### 4.1 Error Modes

- Misleading summaries directing to wrong branches
- Ambiguous queries needing information from multiple sections
- Summary quality as a bottleneck

### 4.2 Comparison with RAG

Unlike standard RAG (retrieve then read), MemWalker:
- Preserves document structure through hierarchy
- Enables multi-step reasoning across the document
- Provides reasoning traces for each answer

## 5. Limitations

- Preprocessing cost: multiple LLM calls for tree construction
- Summary errors propagate through the tree
- Sequential navigation requires multiple inference calls per query
- Focused on single-document scenarios

## 6. Conclusion

MemWalker demonstrates that interactive agent-based navigation of hierarchical document representations provides an effective approach to long-context understanding, with the added benefit of explainable reasoning traces.

---

## Key Figures

- **Figure 1:** MemWalker architecture: tree construction from segments and interactive query-time navigation.
- **Figure 2:** Example navigation trace with step-by-step reasoning.
- **Figure 3:** Performance scaling with document length.

---

## Top References

1. Vaswani et al. (2017). Attention Is All You Need. NeurIPS.
2. Lewis et al. (2020). Retrieval-Augmented Generation. NeurIPS.
3. Izacard & Grave (2021). Leveraging Passage Retrieval with Generative Models. EACL.
4. Dai et al. (2019). Transformer-XL. ACL.
5. Beltagy et al. (2020). Longformer.
6. Karpukhin et al. (2020). Dense Passage Retrieval. EMNLP.
7. Yao et al. (2023). Tree of Thoughts. NeurIPS.
8. Wu et al. (2022). Memorizing Transformers. ICLR.
9. Pang et al. (2022). QuALITY. NAACL.
10. Brown et al. (2020). Language Models are Few-Shot Learners. NeurIPS.
