# RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval

- **Authors:** Parth Sarthi, Salman Abdullah, Aditi Tuli, Shubh Khanna, Anna Goldie, Christopher D. Manning
- **Venue:** ICLR 2024
- **ArXiv:** [2401.18059](https://arxiv.org/abs/2401.18059)
- **Submitted:** January 31, 2024

---

## Abstract

Retrieval-augmented language models can better adapt to changes in world state and incorporate long-tail knowledge. However, most existing methods retrieve only short contiguous chunks from a retrieval corpus, limiting holistic understanding of the overall document context. The authors introduce RAPTOR, a novel tree-based retrieval system that constructs a recursive tree structure from documents. Text chunks are recursively embedded, clustered, and summarized, constructing a tree with differing levels of summarization from the bottom up. At inference time, the RAPTOR model retrieves from this tree, integrating information across lengthy documents at different levels of abstraction. Controlled experiments show that retrieval with recursive summaries offers significant improvements over traditional retrieval-augmented LMs on several tasks. On question-answering tasks, RAPTOR with GPT-4 achieves a 20% absolute accuracy improvement on the QuALITY benchmark over the best results achieved by any baseline.

---

## 1. Introduction

Retrieval-augmented language models combine external knowledge retrieval with language model generation. However, existing retrieval approaches segment text into contiguous, short chunks, limiting them to surface-level retrieval. This fails to capture higher-level thematic or abstract information spread across documents.

RAPTOR addresses this by building a hierarchical tree structure that captures information at varying levels of abstraction, from fine-grained details in leaf nodes to high-level summaries at root nodes.

---

## 2. Related Work

### Why Retrieval

Models underutilize long-range context and experience performance degradation with increased context length, despite expanded capability windows. Long context usage remains computationally expensive and slow.

### Retrieval Methods

Evolution from TF-IDF/BM25 to dense neural retrievers (DPR, ColBERT). Recent approaches include Fusion-in-Decoder (FiD), RETRO, end-to-end systems (Atlas, REALM, RAG). Hierarchical methods include Dense Hierarchical Retrieval (DHR) and Hybrid Hierarchical Retrieval (HHR). Limitation: "contiguous segmentation might not capture the complete semantic depth of the text."

### Recursive Summarization

Prior work includes Gao et al. (2023) combining summaries with snippets, Wu et al. (2021) employing task decomposition, and LlamaIndex retaining intermediate nodes. RAPTOR's innovation: semantic-similarity clustering versus adjacency-based grouping.

---

## 3. Methods

### 3.1 Tree Construction

The system begins by segmenting documents into 100-token chunks, preserving sentence boundaries. These chunks are embedded using SBERT and serve as leaf nodes. The algorithm then iteratively:

1. Clusters semantically similar chunks using Gaussian Mixture Models (GMMs)
2. Generates abstractive summaries via GPT-3.5-turbo
3. Re-embeds the summaries as new nodes
4. Repeats until clustering becomes infeasible

This creates a multi-layered tree with varying levels of abstraction.

### 3.2 Clustering: Gaussian Mixture Models

Uses soft clustering with GMMs and UMAP dimensionality reduction. The Bayesian Information Criterion (BIC) selects optimal cluster numbers.

**GMM probability distribution:**

$$P(x|k) = \mathcal{N}(x; \mu_k, \Sigma_k)$$

$$P(x) = \sum_{k=1}^{K} \pi_k \mathcal{N}(x; \mu_k, \Sigma_k)$$

**BIC for model selection:**

$$\text{BIC} = \ln(N)k - 2\ln(\hat{L})$$

where $N$ = number of data points, $k$ = number of parameters, $\hat{L}$ = maximized likelihood.

Soft clustering allows nodes to appear in multiple clusters, enabling richer multi-faceted representations.

### 3.3 Summarization

Language model generates abstractive summaries of clustered nodes. Compression statistics:

| Metric | Value |
|--------|-------|
| Average summary length | 131 tokens |
| Average child node length | 85.6 tokens |
| Compression ratio | 0.28 (72% compression) |
| Average child nodes per parent | 6.7 |

### 3.4 Retrieval Strategies

**Tree Traversal:** Hierarchical layer-by-layer search selecting top-k nodes at each level, then descending into children of selected nodes.

**Collapsed Tree (preferred):** Flattens all tree layers into a single set and retrieves nodes by cosine similarity until reaching token budget limits.

---

## 4. Experiments

### 4.1 Datasets

Three benchmarks:
- **NarrativeQA:** Long narrative comprehension
- **QASPER:** Scientific paper QA
- **QuALITY:** Multiple-choice reading comprehension with hard subset

### 4.2 Baselines

- BM25 (sparse retrieval)
- Dense Passage Retrieval (DPR)
- SBERT (dense retrieval without tree)

### 4.3 Language Models

Three models tested: UnifiedQA-3B, GPT-3 (text-davinci-003), GPT-4.

---

## 5. Results

### 5.1 NarrativeQA (UnifiedQA-3B)

| Method | ROUGE (%) | BLEU-1 (%) | BLEU-4 (%) | METEOR (%) |
|--------|-----------|------------|------------|------------|
| SBERT baseline | 29.26 | 22.56 | 5.95 | 18.15 |
| SBERT + RAPTOR | 30.87 | 23.50 | 6.42 | 19.20 |
| DPR + RAPTOR | 30.94 | 23.51 | 6.45 | 19.05 |

### 5.2 QASPER (F-1 Match)

| Method | GPT-3 | GPT-4 | UnifiedQA |
|--------|-------|-------|-----------|
| BM25 | -- | -- | ~26 |
| DPR | ~49 | ~51 | ~32 |
| RAPTOR | **53.1** | **55.7** | **36.6** |

RAPTOR surpasses CoLT5 XL prior SotA of 53.9%.

### 5.3 QuALITY (Accuracy)

| Method | GPT-3 | GPT-4 | UnifiedQA |
|--------|-------|-------|-----------|
| DPR | 60.4 | -- | 53.9 |
| RAPTOR | **62.4** | **82.6** | **56.6** |
| Prior SotA (CoLISA) | 62.3 | -- | -- |

**QuALITY Hard Subset:**
- RAPTOR + GPT-4: 76.2% (21.5% absolute improvement over prior SotA of 54.7%)

### 5.4 State-of-the-Art Comparison on QuALITY

| Model | Overall (%) | Hard Subset (%) |
|-------|------------|----------------|
| CoLISA (prior SotA) | 62.3 | 54.7 |
| **RAPTOR + GPT-4** | **82.6** | **76.2** |

20.3 absolute point improvement on full set, 21.5 on hard subset.

---

## 6. Analysis and Ablation Studies

### 6.1 Collapsed Tree vs. Tree Traversal

Collapsed tree retrieval consistently outperforms tree traversal across all settings. On 20 QASPER stories, collapsed tree with 2000-token budget is optimal.

### 6.2 Clustering Mechanism Ablation

| Method | Accuracy (%) |
|--------|-------------|
| RAPTOR (semantic clustering) | 56.6 |
| Contiguous chunk summarization | 55.8 |

Semantic grouping captures homogeneous content better than adjacency-based approach.

### 6.3 Layer Contribution Analysis

| Configuration | Accuracy (%) |
|--------------|-------------|
| Single-layer (leaf only) | 57.9 |
| Two-layer queries | 52.6-63.2 (varies) |
| Three-layer (full tree) | **73.7** |

Full tree utilization significantly outperforms single-layer retrieval.

### 6.4 Non-Leaf Node Retrieval

Approximately 18.5-57% of retrieved nodes originate from non-leaf layers, demonstrating that hierarchical summaries effectively capture information at varying abstraction levels beyond surface-level text chunks.

### 6.5 Hallucination Analysis

- 150 sampled nodes across 40 stories examined
- Hallucination rate: 4% (6 nodes)
- Hallucinations did not propagate to parent nodes
- No discernible impact on QA task performance

---

## 7. Scalability

The system demonstrates linear scaling:
- Token expenditure scales linearly with document length
- Build time scales linearly with document length (up to 80K tokens)
- Tree construction is computationally efficient even on consumer hardware (M1 Mac, 16GB RAM)

---

## Figures

- **Figure 1:** Tree construction process showing recursive clustering of text chunks based on vector embeddings and generation of text summaries, building from bottom up. Leaf nodes are original text chunks; intermediate and root nodes are summaries of clusters.

- **Figure 2:** Illustration contrasting tree traversal (layer-by-layer top-k selection descending through children) with collapsed tree retrieval (flattened multi-layer evaluation by cosine similarity).

- **Figure 3:** Comparison chart showing collapsed tree retrieval outperforming tree traversal on 20 QASPER stories, with 2000-token collapsed tree as optimal configuration.

- **Figure 4:** Cinderella story example demonstrating RAPTOR's retrieval of thematic information across tree layers versus DPR's limitation to leaf-node retrieval of surface-level details only.

- **Figure 5:** Linear scaling of token expenditure versus document length (12,500-78,000 tokens) across three datasets.

- **Figure 6:** Linear relationship between document length and build time for documents up to 80,000 tokens.

- **Figure 7:** Histogram revealing non-leaf node retrieval percentages (18.5-57%) across datasets and retrievers, showing substantial use of higher-level summary nodes.

---

## Key References (Top 10 Most Cited)

1. Karpukhin et al. (2020) -- Dense Passage Retrieval (DPR) for open-domain QA
2. Lewis et al. (2020) -- RAG: Retrieval-augmented generation for knowledge-intensive NLP
3. Reimers & Gurevych (2019) -- Sentence-BERT (SBERT) for sentence embeddings
4. Borgeaud et al. (2022) -- RETRO: Retrieval-enhanced transformer
5. Izacard & Grave (2022) -- Fusion-in-Decoder (FiD) for open-domain QA
6. Guu et al. (2020) -- REALM: Retrieval-augmented language model pre-training
7. Brown et al. (2020) -- GPT-3: Language models are few-shot learners
8. Khashabi et al. (2020) -- UnifiedQA: Crossing format boundaries
9. Pang et al. (2022) -- QuALITY: Question answering with long input texts
10. McInnes et al. (2018) -- UMAP: Uniform manifold approximation and projection
