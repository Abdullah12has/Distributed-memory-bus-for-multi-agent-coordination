# ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction

**Authors:** Keshav Santhanam, Omar Khattab, Jon Saad-Falcon, Christopher Potts, Matei Zaharia

**Venue:** NAACL 2022

**ArXiv:** [2112.01488](https://arxiv.org/abs/2112.01488)

---

## Abstract

Neural information retrieval (IR) has greatly advanced search and other knowledge-intensive language tasks. While many neural IR methods encode queries and documents into single-vector representations, late interaction models tokenize queries and documents, computing relevance via multi-vector representations at the token level. This paper introduces ColBERTv2, which employs an aggressive residual compression mechanism combined with a denoised supervision strategy to achieve state-of-the-art retrieval quality while reducing the space footprint of late interaction models by 6-10x.

---

## 1. Introduction

Late interaction models like ColBERT provide high-quality retrieval by computing fine-grained token-level similarity between queries and documents. However, the multi-vector representation approach incurs significant storage costs. ColBERTv2 addresses this with residual compression while improving quality through denoised supervision.

## 2. Methodology

### 2.1 Supervision Strategy

ColBERTv2 employs distillation from cross-encoders combined with hard-negative mining:
- Uses a 22M-parameter MiniLM cross-encoder to score retrieved passages
- Creates 64-way training tuples
- Trains via KL-Divergence loss distillation
- Hard negatives sampled from ColBERT v1 retrieval results

### 2.2 Representation and Compression

The core innovation leverages residual compression by encoding vectors as:
- Nearest centroid index (from k-means clustering)
- Quantized residual (1-2 bits per dimension)

This reduces per-vector storage from 256 bytes to 20-36 bytes while largely preserving quality.

### 2.3 Clustering Analysis

The residual compression mechanism hypothesizes that vectors corresponding to each sense of a word cluster closely. Empirical analysis of 600M embeddings across 27,000 unique tokens validates this, showing 90% of clusters contain 16 or fewer distinct tokens compared to less than 50% for random embeddings.

## 3. Experimental Results

### 3.1 In-Domain Performance (MS MARCO)

ColBERTv2 achieves the highest MRR@10 (39.7%) among standalone retrievers:

| Model | MRR@10 |
|-------|--------|
| ColBERTv2 | 39.7% |
| RocketQAv2 | 38.8% |
| SPLADEv2 | 36.8% |
| DPR | 31.1% |

### 3.2 Out-of-Domain Evaluation

- **BEIR**: Outperforms competitors on 6+ benchmarks
- **Wikipedia Open-QA**: 68.9% Success@5 on Natural Questions
- **LoTTE**: Highest performance on 22 of 28 test sets with improvements reaching 8% relative gain

### 3.3 Efficiency Gains

| Metric | ColBERT v1 | ColBERTv2 |
|--------|-----------|-----------|
| Index Size | 154 GiB | 16-25 GiB |
| Compression Ratio | 1x | 6-10x |
| Latency | 50-250ms | 50-250ms |

## 4. LoTTE Benchmark

A new evaluation resource for long-tail, cross-domain retrieval:
- 12 test sets with 500-2,000 queries and 100k-2M passages
- Spans Writing, Recreation, Science, Technology, Lifestyle domains
- Two query types: Search queries (from GooAQ) and Forum queries (StackExchange titles)
- Natural information-seeking intent over long-tail topics

## 5. Figures

- **Figure 1**: Architecture overview showing the late interaction mechanism between query and document token embeddings, with residual compression applied to document embeddings.
- **Figure 2**: Cluster purity analysis comparing ColBERTv2 token embedding clusters to random baselines.

---

## References (Top 10)

1. Khattab & Zaharia (2020) - ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT
2. Thakur et al. (2021) - BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models
3. Formal et al. (2021) - SPLADE v2: Sparse Lexical and Expansion Model for Information Retrieval
4. Ren et al. (2021) - RocketQAv2: A Joint Training Method for Dense Passage Retrieval and Passage Re-ranking
5. Khattab et al. (2021) - Relevance-guided Supervision for OpenQA with ColBERT
6. Devlin et al. (2019) - BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding
7. Karpukhin et al. (2020) - Dense Passage Retrieval for Open-Domain Question Answering
8. Johnson et al. (2019) - Billion-Scale Similarity Search with GPUs
9. Gao & Callan (2021) - Unsupervised Corpus Aware Language Model Pre-training for Dense Passage Retrieval
10. Jegou et al. (2010) - Product Quantization for Nearest Neighbor Search
