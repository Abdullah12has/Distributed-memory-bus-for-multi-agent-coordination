# HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models

- **Authors:** Bernal Jimenez Gutierrez, Yiheng Shu, Yu Gu, Michihiro Yasunaga, Yu Su
- **Venue:** NeurIPS 2024
- **ArXiv:** [2405.14831](https://arxiv.org/abs/2405.14831)
- **Submitted:** May 23, 2024; revised January 14, 2025

---

## Abstract

In order to thrive in ever-changing environments, humans are able to continuously integrate new experiences into memory and form new connections between them. Large language models (LLMs), however, struggle with this capability due to the difficulty of efficiently integrating new knowledge after training. HippoRAG is a novel retrieval-augmented generation (RAG) framework inspired by the hippocampal indexing theory of human long-term memory. HippoRAG orchestrates LLMs, knowledge graphs, and the Personalized PageRank algorithm to mimic the synergistic interplay between the neocortex and the hippocampus in human memory. The approach achieves up to 20% improvement over existing state-of-the-art RAG methods on multi-hop question answering benchmarks. Single-step retrieval achieves comparable or better performance than iterative retrieval like IRCoT while being 10-30 times cheaper and 6-13 times faster.

---

## 1. Introduction

Current RAG methods treat each passage independently and lack the ability to form cross-passage associations needed for multi-hop reasoning. HippoRAG addresses this by modeling three components of human long-term memory:

1. **Neocortex** -- the LLM processes and understands text
2. **Hippocampal index** -- a knowledge graph stores relational connections
3. **Parahippocampal regions** -- retrieval encoders detect pattern associations

The key insight is that the hippocampus forms a sparse, interconnected index of experiences rather than storing full memories, enabling efficient associative retrieval.

---

## 2. Background: Hippocampal Memory Indexing Theory

The hippocampal memory indexing theory posits that the hippocampus creates a sparse index of neocortical representations rather than storing memories directly. This enables:
- Rapid encoding of new experiences
- Associative retrieval through pattern completion
- Integration of related but separately encountered information

HippoRAG maps these biological functions to computational components.

---

## 3. Methods

### 3.1 Offline Indexing Phase

Uses an instruction-tuned LLM (GPT-3.5-turbo) to extract knowledge graph triples through Open Information Extraction (OpenIE):

1. **Named Entity Extraction:** 1-shot prompting to extract named entities from passages
2. **Triple Extraction:** Extract (subject, predicate, object) triples, guided by previously extracted named entities
3. **Synonym Edge Detection:** Dense retrieval encoders identify semantic synonymies between entities; edges added when cosine similarity exceeds threshold $\tau = 0.8$
4. **Passage-Node Matrix:** Creates $|N| \times |P|$ matrix tracking noun phrase appearances in passages

### 3.2 Online Retrieval Phase

1. **Query Named Entity Extraction:** Extract named entities from the input query
2. **Node Linking:** Map query entities to KG nodes via retrieval encoder similarity
3. **Personalized PageRank (PPR):** Apply PPR algorithm with damping factor 0.5 to perform multi-hop graph traversal in a single retrieval step
4. **Node Specificity Weighting:** Weight nodes by specificity $s_i = |P_i|^{-1}$ (neurobiologically plausible alternative to IDF)
5. **Passage Ranking:** Aggregate PPR node probabilities over passages for final ranking

### 3.3 Key Innovation: Single-Step Multi-Hop Retrieval

Rather than iterative multi-step retrieval, HippoRAG performs "single-step multi-hop retrieval" by leveraging PPR to explore KG neighborhoods efficiently. The graph structure enables traversal of multi-hop paths without repeated LLM calls.

---

## 4. Experimental Setup

### 4.1 Datasets

| Dataset | Passages | Unique Nodes | Triples |
|---------|----------|-------------|---------|
| MuSiQue | 11,656 | 91,729 | 107,448 |
| 2WikiMultiHopQA | 6,119 | 42,694 | 50,671 |
| HotpotQA | 9,221 | 82,157 | 98,709 |

### 4.2 Baselines

- **Single-step:** BM25, Contriever, GTR, ColBERTv2
- **LLM-augmented:** RAPTOR, Propositionizer
- **Multi-step iterative:** IRCoT

### 4.3 Hyperparameters

- Synonymy threshold ($\tau$): 0.8
- PPR damping factor: 0.5
- Tuned on 100 examples from MuSiQue training data

---

## 5. Results

### 5.1 Single-Step Retrieval Performance

| Method | MuSiQue R@2 | MuSiQue R@5 | 2Wiki R@2 | 2Wiki R@5 | HotpotQA R@2 | HotpotQA R@5 |
|--------|-------------|-------------|-----------|-----------|-------------|-------------|
| BM25 | -- | -- | -- | -- | -- | -- |
| Contriever | 34.2 | 44.8 | 53.1 | 66.8 | 52.3 | 69.3 |
| ColBERTv2 | 37.9 | 49.2 | 59.2 | 68.2 | 57.8 | 74.5 |
| RAPTOR | -- | -- | -- | -- | -- | -- |
| **HippoRAG (Contriever)** | **41.0** | **52.1** | **71.5** | **89.5** | -- | -- |
| **HippoRAG (ColBERTv2)** | -- | -- | -- | -- | **60.5** | **77.7** |

### 5.2 Multi-Step Retrieval (IRCoT Integration)

| Method | MuSiQue R@2 | MuSiQue R@5 | 2Wiki R@2 | 2Wiki R@5 |
|--------|-------------|-------------|-----------|-----------|
| IRCoT (baseline) | ~41 | ~53 | ~55 | ~72 |
| **IRCoT + HippoRAG (ColBERTv2)** | **45.3** | **57.6** | **75.8** | **93.9** |

Complementary gains of ~4% and ~20% respectively.

### 5.3 Question Answering Performance

| Method | MuSiQue EM | MuSiQue F1 | 2Wiki EM | 2Wiki F1 |
|--------|-----------|-----------|---------|---------|
| ColBERTv2 | -- | -- | -- | -- |
| HippoRAG (ColBERTv2) | 19.2 | 29.8 | 46.6 | 59.5 |
| IRCoT + HippoRAG | -- | -- | 47.7 | 62.7 |

### 5.4 All-Recall Metric (Complete Supporting Passage Retrieval)

| Method | 2Wiki AR@5 |
|--------|-----------|
| ColBERTv2 | 37.1 |
| **HippoRAG** | **75.7** |

38 percentage point improvement -- demonstrates HippoRAG retrieves all required supporting passages, not just some.

### 5.5 Efficiency

| Metric | HippoRAG vs. IRCoT |
|--------|-------------------|
| Cost | 10-30x cheaper |
| Speed | 6-13x faster |

---

## 6. Ablation Studies

### 6.1 OpenIE Alternatives

| OpenIE Model | MuSiQue R@2 |
|-------------|-------------|
| GPT-3.5-turbo (default) | 41.0 |
| REBEL model | 31.7 |
| Llama-3.1-8B | Competitive (except 2Wiki) |
| Llama-3.1-70B | Outperforms GPT-3.5 on 2/3 datasets |

### 6.2 PPR vs. Alternatives

| Graph Traversal Method | MuSiQue R@2 |
|----------------------|-------------|
| **PPR (default)** | **41.0** |
| Query nodes only | 37.1 |
| Query nodes + neighbors | 25.4 |

PPR is essential for strong results; simple neighborhood expansion hurts performance.

### 6.3 Component Ablations

| Ablation | MuSiQue R@2 Change | 2Wiki R@2 Change |
|----------|-------------------|-----------------|
| Without node specificity | -3.3% | -- |
| Without synonym edges | -0.7% | -1.5% |

---

## 7. Analysis: Question Types

### Path-Following Questions

Follow a single predetermined path (e.g., "In which district was the person born in Alhandra?"). Solvable by iterative methods like IRCoT. HippoRAG achieves comparable performance.

### Path-Finding Questions

Find one path among many possible connections (e.g., "Which Stanford professor works on Alzheimer's neuroscience?"). Requires knowledge integration without explicit path. Current iterative methods fail; HippoRAG succeeds through graph association via PPR.

---

## 8. Limitations and Future Work

1. Heavy reliance on OpenIE quality; errors cascade through the system
2. Performance varies with document length consistency
3. Scalability to massive KGs remains empirically unvalidated
4. All components used off-the-shelf without task-specific fine-tuning
5. Relations could directly guide graph traversal (future improvement)
6. Component fine-tuning could improve NER and OpenIE extraction quality

---

## Figures

- **Figure 1:** Overview of HippoRAG architecture mapping biological memory components to computational ones. Shows neocortex (LLM) performing OpenIE, hippocampal index (knowledge graph) storing relations, and parahippocampal regions (retrieval encoders) performing pattern association. Online retrieval uses PPR to traverse the graph from query entities.

- **Figure 2:** Comparison between path-following and path-finding question types. Path-following has a single clear chain of reasoning; path-finding requires discovering connections among many candidates through associative retrieval.

- **Figure 3:** Knowledge graph visualization showing how HippoRAG connects information across multiple passages through shared entities and synonym edges, enabling single-step multi-hop retrieval.

---

## Key References (Top 10 Most Cited)

1. Lewis et al. (2020) -- RAG: Retrieval-augmented generation for knowledge-intensive NLP (NeurIPS)
2. Karpukhin et al. (2020) -- Dense Passage Retrieval for open-domain QA
3. Trivedi et al. (2022) -- IRCoT: Interleaving retrieval with chain-of-thought reasoning
4. Khattab & Zaharia (2020) -- ColBERT: Efficient and effective passage search
5. Izacard et al. (2022) -- Contriever: Unsupervised dense information retrieval
6. Sarthi et al. (2024) -- RAPTOR: Recursive abstractive processing for tree-organized retrieval
7. Teru et al. (2020) -- Inductive relation prediction by subgraph reasoning
8. Page et al. (1999) -- The PageRank citation ranking: Bringing order to the web
9. Yang et al. (2018) -- HotpotQA: A dataset for diverse, explainable multi-hop QA
10. Trivedi et al. (2022) -- MuSiQue: Multihop questions via single-hop question composition
