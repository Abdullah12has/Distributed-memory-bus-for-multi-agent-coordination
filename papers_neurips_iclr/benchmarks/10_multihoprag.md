# MultiHop-RAG: Benchmarking Retrieval-Augmented Generation for Multi-Hop Queries

**Authors:** Yixuan Tang, Yi Yang

**Venue:** arXiv preprint, 2024 (Hong Kong University of Science and Technology)

**arXiv:** [2401.15391](https://arxiv.org/abs/2401.15391)

---

## Abstract

The paper introduces a dataset addressing limitations in existing RAG systems. Existing RAG systems are inadequate in answering multi-hop queries, which require retrieving and reasoning over multiple pieces of supporting evidence. The MultiHop-RAG dataset includes a knowledge base built from English news articles, multi-hop queries, ground-truth answers, and supporting evidence. Testing shows that existing RAG methods perform unsatisfactorily in retrieving and answering multi-hop queries when evaluated against state-of-the-art LLMs like GPT-4, PaLM, and Llama2-70B.

---

## 1. Introduction

RAG systems augment LLMs with external knowledge, reducing hallucinations. Existing benchmarks (RGB, RECALL) evaluate only single-evidence scenarios. Multi-hop queries require integrating information from multiple documents. Real-world examples include comparing profit margins across companies and analyzing temporal trends.

---

## 2. Multi-Hop Query Types

| Query Type | Definition | Example |
|-----------|-----------|---------|
| **Inference** | Reasoning across multiple pieces deduces answers | Which report discusses Apple's supply chain risk? |
| **Comparison** | Comparing evidence across sources yields yes/no answers | Did Netflix or Google report higher 2023 revenue? |
| **Temporal** | Analyzing chronological information from multiple sources | Did AirTag launch before or after iPad Pro generation 5? |
| **Null** | Answer cannot be derived from knowledge base; tests hallucination resistance | Sales of non-existent company ABCD? |

---

## 3. Dataset Construction Pipeline

**Step 1 --- Dataset Collection:** Downloaded 609 English news articles (Sept--Dec 2023). Dates selected beyond LLM knowledge cutoffs. Categories: technology, entertainment, sports, science, business, health. Articles averaged 2,046 tokens.

**Step 2 --- Evidence Extraction:** Extracted factual sentences using fact-vs-opinion classifier. Retained articles with potential keyword overlap across sources.

**Step 3 --- Claim, Bridge-Entity, Bridge-Topic Generation:** GPT-4 paraphrased raw evidence into structured claims. UniEval fact-checking verified alignment. Identified shared entities/topics linking multiple evidence pieces.

**Step 4 --- Query and Answer Generation:** Grouped claims sharing bridge-entities/topics (2--4 claims per set). GPT-4 generated query types with specified instructions. Answers: single words, entities, or temporal indicators.

**Step 5 --- Quality Assurance:** Manual review and GPT-4 validation against criteria including query completeness, answerability, and type correctness.

---

## 4. Dataset Statistics

| Category | Count | Percentage |
|----------|-------|------------|
| Inference Queries | 816 | 31.92% |
| Comparison Queries | 856 | 33.49% |
| Temporal Queries | 583 | 22.81% |
| Null Queries | 301 | 11.78% |
| **Total Queries** | **2,556** | **100%** |

### Evidence Requirements

- 2 pieces: 42.18% of queries
- 3 pieces: 30.48% of queries
- 4 pieces: 15.56% of queries
- 0 pieces (null): 11.78% of queries

---

## 5. Evaluation Metrics

**Retrieval Evaluation:**
- MAP@K (Mean Average Precision)
- MRR@K (Mean Reciprocal Rank)
- Hit@K (Evidence appearance in top-K results)

**Response Evaluation:**
- Accuracy comparison of LLM outputs versus ground truth

---

## 6. Results

### Embedding Model Performance

| Embedding Model | MRR@10 | MAP@10 | Hits@10 | Hits@4 |
|----------------|--------|--------|---------|--------|
| voyage-02 | 0.5860 | 0.4795 | 0.7467 | 0.6625 |
| text-embedding-ada-002 | 0.5477 | 0.4625 | 0.7059 | 0.6169 |
| bge-large-en-v1.5 | 0.5630 | 0.4759 | 0.7183 | 0.6364 |
| hkunlp/instructor-large | 0.5115 | 0.4118 | 0.6590 | 0.5775 |
| jina-embeddings-v2 | 0.1412 | 0.0772 | 0.1909 | 0.1639 |

### LLM Generation Performance

| Model | Retrieved Accuracy | Ground-Truth Accuracy |
|-------|------------------|----------------------|
| GPT-4 | 0.56 | 0.89 |
| ChatGPT (GPT-3.5) | 0.44 | 0.57 |
| Claude-2.1 | 0.52 | 0.56 |
| Google-PaLM | 0.47 | 0.74 |
| Llama-2-70B | 0.28 | 0.32 |
| Mixtral-8x7B | 0.32 | 0.36 |

---

## 7. Key Findings

1. **Retrieval Bottleneck:** Multi-hop query retrieval remains challenging; simple similarity matching inadequate
2. **Reasoning Limitations:** Even with perfect evidence, open-source models underperform significantly
3. **Hallucination Risk:** Null query performance indicates models generally avoid hallucinating when evidence unavailable
4. **Model Variance:** 61-point accuracy gap between GPT-4 and Llama-2-70B with ground truth evidence

---

## 8. Limitations

- Ground-truth answers restricted to short responses (single words, yes/no, temporal indicators)
- Maximum 4 evidence pieces per query
- Limited to basic LlamaIndex RAG framework
- Future work should explore advanced RAG approaches and free-text answers

---

## 9. Figure Descriptions

- **Figure 1:** Overview of the MultiHop-RAG dataset construction pipeline
- **Figure 2:** Distribution of query types and evidence requirements
- **Figure 3:** Performance comparison across embedding models with and without reranking

---

## Key References

1. Asai et al. (2023) --- Retrieval-based language models and applications
2. Borgeaud et al. (2022) --- Improving language models by retrieving from trillions of tokens
3. Chen et al. (2023) --- Benchmarking large language models in retrieval-augmented generation (RGB dataset)
4. Gao et al. (2023) --- Enabling large language models to generate text with citations
5. Yang et al. (2018) --- HotpotQA: A dataset for diverse, explainable multi-hop question answering
6. Ho et al. (2020) --- Constructing a multi-hop QA dataset for comprehensive evaluation
7. Liu et al. (2023) --- Recall: A benchmark for LLMs robustness against counterfactual knowledge
8. Thorne et al. (2018) --- Fever: A large-scale dataset for fact extraction and verification
9. Es et al. (2023) --- RAGAS: Automated evaluation of retrieval augmented generation
10. Touvron et al. (2023) --- Llama 2: Open foundation and fine-tuned chat models
