# Corrective Retrieval Augmented Generation (CRAG)

**Authors:** Shi-Qi Yan, Jia-Chen Gu, Yun Zhu, Zhen-Hua Ling

**Venue:** arXiv preprint (cs.CL), 2024

**ArXiv:** [2401.15884](https://arxiv.org/abs/2401.15884)

---

## Abstract

Large language models inevitably exhibit hallucinations since the accuracy of generated texts cannot be secured solely by the parametric knowledge they encapsulate. Although retrieval-augmented generation (RAG) is a practicable complement to LLMs, it relies heavily on the relevance of retrieved documents, raising concerns about how the model behaves if retrieval goes wrong. CRAG is designed to improve the robustness of generation by implementing self-correction mechanisms for retrieval results. A lightweight retrieval evaluator is designed to assess the overall quality of retrieved documents for a query, returning a confidence degree based on which different knowledge retrieval actions can be triggered. Since large-scale web searches are an important complement when static and limited corpora fail, a decompose-then-recompose algorithm is designed for selectively focusing on key information and filtering out irrelevant information in retrieved documents.

---

## 1. Introduction

RAG approaches indiscriminately incorporate retrieved documents regardless of their relevance, leading to suboptimal generation. CRAG addresses this by evaluating retrieval quality and triggering corrective actions when retrieval is unreliable.

## 2. Core Problem

LLMs suffer from hallucinations due to reliance on parametric knowledge. While RAG helps address this, conventional approaches do not verify the quality of retrieved documents before using them.

## 3. Methodology

### 3.1 Retrieval Evaluator

- Built on T5-large (lightweight at 0.77B parameters)
- Fine-tuned to assess relevance of retrieved documents
- Outperforms ChatGPT-based evaluation (84.3% vs 58-64.7% accuracy)
- Generates confidence scores determining subsequent actions

### 3.2 Action Trigger Mechanism (Three States)

| Action | Condition | Response |
|--------|-----------|----------|
| **Correct** | High confidence score | Refine documents; extract key information |
| **Incorrect** | Low confidence scores | Discard results; initiate web search |
| **Ambiguous** | Intermediate scores | Combine refined internal + external knowledge |

### 3.3 Knowledge Refinement

Implements a decompose-then-recompose algorithm:
- Segments documents into fine-grained knowledge strips
- Filters irrelevant strips using the retrieval evaluator
- Recomposes relevant strips sequentially to form refined knowledge

### 3.4 Web Search Extension

- Triggered when internal retrieval fails (low confidence)
- Queries are rewritten to keywords via ChatGPT
- Prefers authoritative sources (e.g., Wikipedia)
- Applies the same refinement process as internal knowledge

## 4. Experimental Results

### 4.1 Performance Improvements on Four Datasets

**CRAG vs Standard RAG** (SelfRAG-LLaMA2-7b base):

| Dataset | Metric | Improvement |
|---------|--------|-------------|
| PopQA | Accuracy | +7.0% |
| Biography | FactScore | +14.9% |
| PubHealth | Accuracy | +36.6% |
| Arc-Challenge | Accuracy | +15.4% |

**Self-CRAG vs Self-RAG** (LLaMA2-hf-7b base):

| Dataset | Metric | Improvement |
|---------|--------|-------------|
| PopQA | Accuracy | +20.0% |
| Biography | FactScore | +36.9% |

### 4.2 Dataset Characteristics

- **PopQA**: Short-form entity generation (1,399 rare entity queries)
- **Biography**: Long-form generation with detailed content
- **PubHealth**: Binary true/false medical claims
- **Arc-Challenge**: Multiple-choice science questions

### 4.3 Ablation Studies

**Triggered Actions Impact (PopQA):**

| Configuration | LLaMA2-7b | SelfRAG-7b |
|---------------|-----------|------------|
| Full CRAG | 54.9% | 59.8% |
| w/o Correct | 53.2% | 58.3% |
| w/o Incorrect | 54.4% | 59.5% |
| w/o Ambiguous | 54.0% | 59.0% |

**Knowledge Operations Impact:**
- Removing refinement: -5.1% to -9.6% accuracy
- Removing query rewriting: -3.2% to -3.4% accuracy
- Removing knowledge selection: -0.8% to -36.9% accuracy

### 4.4 Computational Analysis

| Approach | TFLOPs/token | Execution Time (s) |
|----------|--------------|-------------------|
| RAG | 26.5 | 0.363 |
| CRAG | 27.2 | 0.512 |
| Self-RAG | 26.5-132.4 | 0.741 |
| Self-CRAG | 27.2-80.2 | 0.908 |

Modest overhead demonstrates the lightweight nature of CRAG.

## 5. Robustness Testing

When deliberately removing accurate retrieval results to simulate low-quality retrieval:
- Self-CRAG maintains performance better than Self-RAG
- Degrades more gradually with decreasing retrieval quality
- Demonstrates superior adaptability to suboptimal conditions

## 6. Key Design Strengths

1. **Plug-and-play design**: Compatible with existing RAG frameworks
2. **Three-level confidence system**: Reduces dependency on evaluator accuracy
3. **Lightweight architecture**: T5-based evaluator outperforms larger LLMs
4. **Dual knowledge sources**: Combines internal retrieval with web augmentation
5. **Fine-grained filtering**: Segment-level analysis removes noise while preserving context

## 7. Limitations

The authors acknowledge that fine-tuning an external retrieval evaluator remains necessary. Future work should explore equipping LLMs with better retrieval evaluation capabilities without requiring separate training.

## 8. Figures

- **Figure 1**: Overview of CRAG framework showing the retrieval evaluator, action triggers (Correct/Incorrect/Ambiguous), knowledge refinement, and web search components.
- **Figure 2**: Robustness analysis showing performance degradation curves when systematically removing correct documents from the retrieval pool.

---

## References (Top 10)

1. Lewis et al. (2020) - Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
2. Asai et al. (2024) - Self-RAG: Learning to Retrieve, Generate, and Critique
3. Touvron et al. (2023) - LLaMA 2: Open Foundation and Fine-tuned Chat Models
4. Min et al. (2023) - FactScore: Fine-grained Atomic Evaluation of Factual Precision
5. Mallen et al. (2023) - When Not to Trust Language Models: PopQA Dataset
6. Ji et al. (2023) - Survey of Hallucination in Natural Language Generation
7. Brown et al. (2020) - Language Models are Few-Shot Learners
8. Raffel et al. (2020) - Exploring the Limits of Transfer Learning with T5
9. Zhang et al. (2023) - SIREN's Song: Survey on Hallucination in LLMs
10. Shi et al. (2023) - Large Language Models Can Be Easily Distracted by Irrelevant Context
