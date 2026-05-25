# Walking Down the Memory Maze: Beyond Context Limit through Interactive Reading (MemWalker)

**Authors:** Howard Chen, Ramakanth Pasunuru, Jason Weston, Asli Celikyilmaz

**Venue:** arXiv preprint (cs.CL), 2023

**arXiv:** [https://arxiv.org/abs/2310.05029](https://arxiv.org/abs/2310.05029)

---

## Abstract

Large language models (LLMs) have advanced in large strides due to the effectiveness of the self-attention mechanism that processes and compares all tokens at once. However, this mechanism comes with a fundamental issue -- the predetermined context window is bound to be limited. The authors propose MemWalker, which treats the LLM as an interactive agent that navigates a tree of summary nodes constructed from the long text. Given a query, the model traverses this tree to locate and gather relevant information, then responds once sufficient context is found. MemWalker outperforms baseline approaches on long-text question answering tasks and provides enhanced explainability by highlighting reasoning steps during interactive reading.

---

## 1. Introduction

Existing approaches to long-context processing fall into three categories:
1. **Architectural modifications:** Sparse attention, linear attention, recurrence
2. **Position extrapolation:** RoPE scaling, ALiBi
3. **Retrieval augmentation:** Retrieve relevant chunks before processing

All have limitations: architectural changes require retraining, position extrapolation degrades quality, and retrieval may miss relevant context. MemWalker takes a different approach by treating the LLM as an agent that actively navigates a structured representation of the document.

## 2. Method: MemWalker

### 2.1 Preprocessing: Tree Construction

The long document is converted into a hierarchical tree:

**Step 1: Segmentation**
- Divide the document into segments that fit within the LLM's context window
- Each segment becomes a leaf node

**Step 2: Summarization**
- Each leaf node is summarized by the LLM
- Summaries include key facts, entities, and relationships

**Step 3: Hierarchical Aggregation**
- Groups of summaries are combined into parent nodes
- Parent nodes contain meta-summaries of their children
- Process repeats until a single root node is created

### 2.2 Interactive Navigation

Given a query, the LLM navigates the tree:

**Step 1: Start at Root**
- Read the root summary to get a high-level overview
- Decide which child branch is most likely to contain relevant information

**Step 2: Traverse**
- At each internal node, read the summary and select the most promising child
- The LLM explains its reasoning at each step (enhancing explainability)

**Step 3: Gather and Respond**
- Upon reaching leaf nodes with sufficient information, generate the answer
- If information is insufficient, backtrack and explore alternative branches

### 2.3 Navigation Prompting

The LLM is prompted with instructions for navigation:
- Current node summary
- Available child node summaries
- The original query
- Instruction to select the most relevant child or answer if sufficient information is available

## 3. Experimental Setup

### 3.1 Datasets

- **QuALITY:** Long-document QA with multiple-choice questions, documents up to 8K tokens
- **NarrativeQA:** Story comprehension QA, documents up to 100K+ tokens
- **Extended synthetic tasks:** Custom long documents requiring multi-hop reasoning

### 3.2 Baselines

- **Truncation:** Use only the first/last N tokens
- **Retrieval (BM25/Dense):** Retrieve relevant chunks and answer from retrieved context
- **Recurrence:** Process document sequentially with summary carry-forward
- **Extended context models:** Models with longer context windows

## 4. Results

### 4.1 Long-Document QA

MemWalker outperforms baselines on documents exceeding the model's context window:

| Method | QuALITY Acc. | NarrativeQA F1 |
|---|---|---|
| Truncation | Low | Low |
| BM25 Retrieval | Moderate | Moderate |
| Dense Retrieval | Moderate | Moderate |
| Recurrence | Moderate | Moderate |
| MemWalker | Best | Best |

Performance advantage grows with document length -- the tree structure scales logarithmically while retrieval quality degrades.

### 4.2 Navigation Efficiency

- Average tree depth: 3-4 levels for documents up to 100K tokens
- Average navigation steps: 4-6 per query
- Each step requires only reading a summary and making a selection decision

### 4.3 Explainability

A key advantage of MemWalker is transparency:
- Each navigation step includes the LLM's reasoning for its choice
- The path through the tree highlights which document sections were considered
- Users can verify whether the model found the correct information

## 5. Analysis

### 5.1 Error Analysis

Common failure modes:
- **Misleading summaries:** If a summary fails to capture key details, the model may navigate to wrong branches
- **Ambiguous queries:** Questions requiring information from multiple distant sections
- **Summary quality:** Performance depends heavily on the quality of intermediate summaries

### 5.2 Scalability

The tree structure provides O(log N) navigation complexity:
- A 100K token document with 1K token segments creates ~100 leaves
- With branching factor 10, tree depth is ~2
- Total tokens processed per query: ~3-5 summaries worth

### 5.3 Comparison with RAG

Unlike standard RAG which retrieves then reads, MemWalker:
- Maintains document structure through the hierarchy
- Enables multi-step reasoning across the document
- Provides a reasoning trace for each answer

## 6. Related Work

- **Memory-augmented models:** MemTRM, Memorizing Transformers
- **Retrieval-augmented generation:** RAG, REALM, DPR
- **Long-context models:** Longformer, BigBird, Ring Attention
- **Tree-based reasoning:** Tree-of-thought, hierarchical summarization

MemWalker uniquely combines hierarchical document representation with interactive LLM navigation.

## 7. Limitations

- Preprocessing cost: Building the tree requires multiple LLM calls for summarization
- Summary quality bottleneck: Errors in summaries propagate through the tree
- Sequential navigation: Each query requires multiple LLM calls during traversal
- Single-document focus: Not directly applicable to multi-document scenarios

## 8. Conclusion

MemWalker demonstrates that treating LLMs as interactive agents navigating structured document representations offers a viable path beyond context window limitations. The approach provides both improved accuracy on long-document QA and enhanced explainability through visible reasoning traces. The logarithmic scaling of navigation steps with document length makes it practical for very long documents.

---

## Key Figures

- **Figure 1:** Overview of MemWalker architecture showing tree construction from document segments and interactive navigation.
- **Figure 2:** Example navigation trace showing the LLM's step-by-step reasoning through the tree.
- **Figure 3:** Performance comparison across document lengths, showing MemWalker's advantage growing with length.
- **Figure 4:** Tree structure visualization for different document sizes.

---

## Top References

1. Vaswani et al. (2017). Attention Is All You Need. NeurIPS.
2. Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS.
3. Izacard & Grave (2021). Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering. EACL.
4. Dai et al. (2019). Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context. ACL.
5. Beltagy et al. (2020). Longformer: The Long-Document Transformer.
6. Karpukhin et al. (2020). Dense Passage Retrieval for Open-Domain Question Answering. EMNLP.
7. Yao et al. (2023). Tree of Thoughts: Deliberate Problem Solving with Large Language Models. NeurIPS.
8. Wu et al. (2022). Memorizing Transformers. ICLR.
9. Pang et al. (2022). QuALITY: Question Answering with Long Input Texts, Yes! NAACL.
10. Brown et al. (2020). Language Models are Few-Shot Learners. NeurIPS.
