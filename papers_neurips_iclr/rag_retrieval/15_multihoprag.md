# MultiHop-RAG: Benchmarking Retrieval-Augmented Generation for Multi-Hop Queries

**Authors:** Yixuan Tang, Yi Yang

**Venue:** arXiv preprint (cs.CL), 2024 (CC BY-SA 4.0)

**ArXiv:** [2401.15391](https://arxiv.org/abs/2401.15391)

---

## Abstract

Retrieval-augmented generation (RAG) has shown promise in mitigating LLM hallucinations, but existing benchmarks focus on single-hop queries. This paper introduces MultiHop-RAG, a novel benchmarking dataset for evaluating RAG systems on multi-hop queries -- questions requiring retrieval and reasoning over multiple pieces of evidence from different documents. The dataset comprises a knowledge base, a large collection of multi-hop queries, their ground-truth answers, and the associated supporting evidence. Experiments with state-of-the-art embedding models and LLMs (GPT-4, Llama2-70B) reveal that existing RAG methods perform unsatisfactorily in retrieving and answering multi-hop queries.

---

## 1. Introduction

Current RAG systems are primarily evaluated on single-hop queries where a single retrieved passage suffices to answer the question. Real-world questions often require synthesizing information from multiple sources, exposing significant gaps in existing RAG capabilities.

## 2. Dataset Construction

### 2.1 Pipeline

1. **Article Collection**: 609 news articles (Sept-Dec 2023) beyond LLM training cutoffs
2. **Evidence Extraction**: Factual sentences extracted using a trained model
3. **Claim Paraphrasing**: GPT-4 paraphrases evidence into standalone "claims"
4. **Bridge Entity/Topic Identification**: Links identified between evidence pieces across documents
5. **Query Generation**: Multi-hop queries and answers generated via GPT-4
6. **Quality Assurance**: Manual review and automated consistency checks

### 2.2 Query Types

| Type | Count | Description |
|------|-------|-------------|
| Inference | 816 | Require reasoning across sources |
| Comparison | 856 | Compare data points from multiple documents |
| Temporal | 583 | Sequence events across documents |
| Null | 301 | Unanswerable from the knowledge base |
| **Total** | **2,556** | |

### 2.3 Evidence Requirements

- 42% of queries require 2 evidence pieces
- 30% require 3 evidence pieces
- 15% require 4 evidence pieces
- Remaining require 5+ pieces

## 3. Dataset Statistics

- 609 news articles across 6 categories
- 2,556 total multi-hop queries
- Ground-truth answers with supporting evidence chains
- Articles from after Sept 2023 to avoid training data contamination

## 4. Experimental Results

### 4.1 Retrieval Performance

The highest Hits@10 is only 0.7467 when the Reranker technique is used, indicating significant gaps in retrieving multi-hop evidence with current methods.

| Method | Hits@4 | Hits@10 |
|--------|--------|---------|
| Base Embedding | ~0.45 | ~0.60 |
| + Reranker | ~0.55 | 0.7467 |

### 4.2 Generation Performance

| Model | With Ground-Truth Evidence | With Retrieved Chunks |
|-------|---------------------------|----------------------|
| GPT-4 | 0.89 accuracy | 0.56 accuracy |
| Llama2-70B | Lower | Much lower |
| Mixtral-8x7B | Lower | Much lower |

The 33-point drop from ground-truth to retrieved evidence demonstrates that retrieval quality is the primary bottleneck.

### 4.3 Analysis by Query Type

- Comparison queries: Most challenging for retrieval (require contrasting information)
- Temporal queries: Moderate difficulty (require ordering)
- Inference queries: Require chain-of-reasoning across documents
- Null queries: Test system's ability to abstain when evidence is insufficient

## 5. Key Findings

1. Current RAG systems are fundamentally limited for multi-hop queries
2. Retrieval is the primary bottleneck, not generation capability
3. Even the best retrieval methods miss significant evidence
4. Commercial models (GPT-4) substantially outperform open-source alternatives
5. The gap between single-hop and multi-hop RAG performance is significant

## 6. Dataset Availability

The dataset and RAG system implementation are publicly available on GitHub for reproducibility and benchmarking.

## 7. Figures

- **Figure 1**: Overview of the MultiHop-RAG dataset construction pipeline showing the six-stage process from article collection to quality assurance.
- **Figure 2**: Distribution of query types and evidence requirements across the dataset.
- **Figure 3**: Retrieval performance comparison across different embedding models and reranking strategies.

---

## References (Top 10)

1. Asai et al. (2023) - Retrieval-based Language Models and Applications
2. Borgeaud et al. (2022) - Improving Language Models by Retrieving from Trillions of Tokens
3. Chen et al. (2023) - Benchmarking Large Language Models in Retrieval-Augmented Generation
4. Es et al. (2023) - RAGAS: Automated Evaluation of Retrieval Augmented Generation
5. Gao et al. (2023) - Enabling Large Language Models to Generate Text with Citations
6. Yang et al. (2018) - HotpotQA: A Dataset for Diverse, Explainable Multi-Hop Question Answering
7. Thorne et al. (2018) - FEVER: A Large-Scale Dataset for Fact Extraction and VERification
8. Wadden et al. (2020) - Fact or Fiction: Verifying Scientific Claims
9. Jiang et al. (2020) - HoVer: A Dataset for Many-Hop Fact Extraction and Claim Verification
10. Khashabi et al. (2018) - Looking Beyond the Surface: A Challenge Set for Reading Comprehension Over Multiple Sentences
