# xRAG: Extreme Context Compression for Retrieval-augmented Generation with One Token

**Authors:** Xin Cheng, Xun Wang, Xingxing Zhang, Tao Ge, Si-Qing Chen, Furu Wei, Huishuai Zhang, Dongyan Zhao

**Venue:** NeurIPS 2024

**ArXiv:** [2405.13792](https://arxiv.org/abs/2405.13792)

---

## Abstract

We introduce xRAG, a method that compresses context for retrieval-augmented generation by treating document embeddings as features from the retrieval modality. Through modality fusion, it integrates these embeddings into language model representations while keeping both the retriever and language model frozen. The approach achieves an average improvement of over 10% across six knowledge-intensive tasks and reduces overall FLOPs by a factor of 3.53 while matching uncompressed model performance on several datasets.

---

## 1. Introduction

Standard RAG prepends full retrieved documents to the input, consuming valuable context window tokens. xRAG reinterprets document embeddings from dense retrieval as a separate "retrieval modality" and fuses them into the LLM's representation space using a lightweight projector, compressing each document to a single token.

---

## 2. Technical Architecture

### 2.1 Modality Projector

A two-layer MLP (W) that projects document embeddings from the retrieval space into the language model's representation space. Only ~0.1% of the LLM's parameters require training.

### 2.2 Frozen Components

Both the retriever and language model remain frozen, preserving plug-and-play functionality and avoiding catastrophic forgetting.

### 2.3 Two-Stage Training

**Stage 1 -- Paraphrase Pretraining:**
Train the model to recover document text from its embedding, establishing compatibility between retrieval and language modalities.

**Stage 2 -- Context-aware Instruction Tuning:**
Fine-tune on ~1 million examples using two objectives:
- Language modeling loss
- Self-distillation loss (comparing outputs with/without text context)

---

## 3. Experimental Results

### 3.1 Performance

Across six knowledge-intensive tasks (Natural Questions, TriviaQA, WebQuestions, HotpotQA, TruthfulQA, FactKG):

- **Mistral-7b:** 16.2% improvement over no-retrieval baseline
- **Mixtral-8x7b:** 9.7% improvement
- Compression ratio: 175.1 tokens -> 1 token

### 3.2 Computational Efficiency

| Metric | Improvement |
|--------|------------|
| CUDA Time | 1.64x faster |
| GFLOPs | 3.53x reduction |

### 3.3 Robustness Analysis

Novel evaluation metrics:
- **Resilience Rate:** Percentage of previously correct answers remaining correct after retrieval (xRAG: 82-85%; standard RAG: 75.2%)
- **Boost Rate:** Percentage of incorrect answers corrected by retrieval (xRAG: 20-22%)

Standard RAG shows only 75.2% average resilience, meaning retrieved documents can mislead the model. xRAG demonstrates superior robustness, particularly with irrelevant or misleading retrieval results.

---

## 4. Ablation Studies

| Finding | Detail |
|---------|--------|
| Pretraining essential for small models | Critical for Mistral-7b, less so for larger models |
| Self-distillation > LM loss alone | Self-distillation specifically improves resilience rates |
| Reading comprehension data strongest | Provides best training signal among data types |

---

## 5. Comparative Analysis

xRAG outperforms existing compression methods:

| Method | Improvement | Token Overhead |
|--------|------------|----------------|
| xRAG | 10%+ average | 1 token/doc |
| LLMLingua | 4% | Higher |
| TF-IDF compression | 2.6% | Higher |
| Soft-prompting (Gist, ICAE) | Comparable | 1.05 MB/token memory |

---

## 6. Implementation Details

- **LLM Backbones:** Mistral-7B and Mixtral-8x7B
- **Embedding Model:** SFR (leading on MTEB leaderboard at time of writing)
- **Corpus:** Wikipedia with 37 million passages (~180 tokens each)
- **Training Data:** Mixed instruction-tuning corpus across reading comprehension, QA, and summarization

---

## 7. Limitations

- Limited to single dense vector retrieval (not sparse methods or multi-vector approaches)
- Performance lags in reasoning-intensive tasks like HotpotQA and FactKG
- Only considers top-1 document retrieval, not multi-document ensembles

---

## 8. Theoretical Insight

The work pioneers applying multimodal fusion principles to retrieval augmentation, treating document embeddings analogously to how vision-language models treat visual encodings. This perspective shift enables leveraging information already condensed through contrastive learning in dense retrieval systems.

---

## Figures

- **Figure 1:** xRAG architecture showing the retriever producing an embedding, the MLP projector mapping it to LLM space, and the frozen LLM consuming the single compressed token alongside the query.
- **Figure 2:** Performance comparison across six knowledge-intensive benchmarks vs. baselines.
- **Figure 3:** Resilience and boost rate analysis showing xRAG's robustness to noisy retrieval.
- **Figure 4:** Ablation of training components showing the importance of each stage.

---

## Key References

1. Lewis et al. (2020) - RAG
2. Karpukhin et al. (2020) - DPR
3. Izacard & Grave (2021) - FiD
4. Jiang et al. (2023) - LLMLingua
5. Ge et al. (2024) - ICAE
6. Mu et al. (2023) - GIST
7. Chevalier et al. (2023) - AutoCompressors
8. Liu et al. (2023) - LLaVA (vision-language fusion analogy)
9. Xu et al. (2023) - RECOMP
10. Jiang et al. (2024) - Mistral-7B
