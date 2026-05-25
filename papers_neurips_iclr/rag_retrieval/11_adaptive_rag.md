# Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity

**Authors:** Soyeong Jeong, Jinheon Baek, Sukmin Cho, Sung Ju Hwang, Jong C. Park

**Venue:** NAACL 2024

**ArXiv:** [2403.14403](https://arxiv.org/abs/2403.14403)

---

## Abstract

Retrieval-Augmented Large Language Models (LLMs) have emerged as a promising approach for addressing knowledge-intensive tasks. However, existing approaches often employ a one-size-fits-all strategy, applying the same retrieval-augmented method regardless of the query's complexity. This paper presents Adaptive-RAG, a framework that dynamically selects the most suitable strategy for retrieval-augmented LLMs from the simplest to the most sophisticated ones based on the query complexity. The system uses a trained classifier to assess incoming questions and route them to the appropriate retrieval strategy, demonstrating improved overall efficiency and accuracy across multiple open-domain question-answering datasets.

---

## 1. Introduction

Current RAG approaches fall into two categories:
- **Simple approaches**: Efficient but inadequate for complex queries requiring multi-document reasoning
- **Complex approaches**: Powerful but computationally wasteful when applied to straightforward questions

Real-world scenarios involve queries of varying complexity, necessitating an adaptive system.

## 2. Methodology

### 2.1 Three QA Strategies

| Strategy | Formulation | Use Case |
|----------|-------------|----------|
| **No Retrieval** | a = LLM(q) | Simple queries answerable from parametric knowledge |
| **Single-Step** | a = LLM(q, d) | Moderate complexity, single evidence source |
| **Multi-Step** | a_i = LLM(q, d_i, c_i) | Complex multi-hop questions requiring iterative retrieval |

### 2.2 Query Complexity Classifier

A smaller language model trained to classify queries into three complexity levels:

| Label | Complexity | Strategy |
|-------|-----------|----------|
| A | Simple | No retrieval |
| B | Moderate | Single-step retrieval |
| C | Complex | Multi-step retrieval |

### 2.3 Automatic Training Data Generation

Two mechanisms for creating classifier training data without manual annotation:

1. **Model-based (silver) labels**: Assign labels based on which approaches successfully answer queries, with priority given to simpler methods
2. **Dataset-based labels**: Assign B to single-hop datasets and C to multi-hop datasets, leveraging inherent dataset biases

## 3. Experimental Setup

### 3.1 Datasets

| Category | Datasets |
|----------|----------|
| Single-hop | SQuAD v1.1, Natural Questions, TriviaQA |
| Multi-hop | MuSiQue, HotpotQA, 2WikiMultiHopQA |

### 3.2 Models Tested

- FLAN-T5-XL (3B parameters)
- FLAN-T5-XXL (11B parameters)
- GPT-3.5 Turbo

### 3.3 Evaluation Metrics

- **Effectiveness**: F1 score, Exact Match (EM), Accuracy (Acc)
- **Efficiency**: Number of retrieval steps, time per query

## 4. Main Results

### 4.1 Aggregated Performance

On FLAN-T5-XL across all datasets:

| Approach | F1 | Steps | Time |
|----------|-----|-------|------|
| No Retrieval | 21.12 | 0.00 | 0.11 |
| Single-step | 44.31 | 1.00 | 1.00 |
| Adaptive-RAG | 46.94 | 2.17 | 3.60 |
| Multi-step | 48.85 | 4.69 | 8.81 |
| Oracle Adaptive-RAG | 56.28 | 1.28 | 2.11 |

Key findings:
- Adaptive-RAG achieves substantially better F1 (46.94) compared to Adaptive Retrieval (32.24) and Self-RAG (20.79)
- Efficiency is significantly better than multi-step while maintaining competitive accuracy
- Oracle classifier results (56.28 F1) show substantial headroom for classifier improvement

### 4.2 Classifier Performance

The classifier achieves approximately:
- 54.52% accuracy for no-retrieval queries
- 66.28% for single-step queries
- 65.45% for multi-step queries

Confusion matrix shows "C (Multi)" sometimes misclassified as "B (One)" (~31%), and "A (No)" frequently confused with "B" (~47%).

### 4.3 Efficiency Analysis

| Classification | Time/Query (sec) | Percentage |
|----------------|------------------|-----------|
| No (A) | 0.35 | 8.60% |
| One (B) | 3.08 | 53.33% |
| Multi (C) | 27.18 | 38.07% |

Most queries (53%) classified as moderate complexity, requiring single-step retrieval.

### 4.4 Ablation Studies

**Training Data Analysis:**

| Data Source | F1 | Steps |
|-------------|-----|-------|
| Combined (silver + dataset bias) | 46.94 | 1084 |
| Silver data only | 48.79 | 1464 |
| Dataset bias only | 43.43 | 640 |

**Classifier Size Sensitivity:**

| Model Size | F1 | Classifier Accuracy |
|-----------|-----|-------------------|
| Small (60M) | 45.83 | 53.48% |
| Base (223M) | 45.97 | 53.41% |
| Large (770M) | 46.94 | 54.52% |

Minimal performance differences across classifier sizes indicate resource-efficient deployment is viable.

## 5. Case Studies

**Single-hop query**: "Which famous corporate logo changed to flat sans-serif font in first major change since 1999?"
- Adaptive Retrieval: Incorrectly retrieved info about Microsoft
- Adaptive-RAG: Classified as "A" (no retrieval), correctly identified Google

**Multi-hop query**: "Who is child of Italian navigator exploring eastern coast where Cesar Gaytan was born?"
- Adaptive Retrieval: Classified as "A", failed without retrieval
- Adaptive-RAG: Classified as "C", correctly identified Sebastian Cabot through multi-step reasoning

## 6. Limitations

- Automatic label generation may introduce errors; no human-annotated complexity dataset exists
- Substantial performance gap between oracle (56.28 F1) and actual classifier (46.94 F1)
- Simple T5-based classifier design may be suboptimal
- Three complexity levels is relatively coarse granularity

## 7. Figures

- **Figure 1**: Overview of Adaptive-RAG showing the query complexity classifier routing queries to one of three strategies (no retrieval, single-step, multi-step).
- **Figure 2**: Performance-efficiency trade-off visualization comparing Adaptive-RAG with fixed-strategy baselines.
- **Figure 3**: Confusion matrix of the query complexity classifier.

---

## References (Top 10)

1. Trivedi et al. (2023) - Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions (ACL 2023)
2. Mallen et al. (2023) - When Not to Trust Language Models: Investigating Effectiveness of Parametric and Non-Parametric Memories (ACL 2023)
3. Asai et al. (2024) - Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection (ICLR 2024)
4. Press et al. (2023) - Measuring and Narrowing the Compositionality Gap in Language Models (EMNLP Findings 2023)
5. Khattab et al. (2022) - Demonstrate-Search-Predict: Composing Retrieval and Language Models for Knowledge-Intensive NLP
6. Izacard et al. (2023) - Atlas: Few-shot Learning with Retrieval Augmented Language Models (JMLR)
7. Borgeaud et al. (2022) - Improving Language Models by Retrieving from Trillions of Tokens (ICML 2022)
8. Brown et al. (2020) - Language Models are Few-Shot Learners (NeurIPS 2020)
9. Karpukhin et al. (2020) - Dense Passage Retrieval for Open-Domain Question Answering (EMNLP 2020)
10. Yang et al. (2018) - HotpotQA: A Dataset for Diverse, Explainable Multi-Hop Question Answering (EMNLP 2018)
