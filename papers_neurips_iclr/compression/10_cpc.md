# Prompt Compression with Context-Aware Sentence Encoding for Fast and Improved LLM Inference (CPC)

**Authors:** Barys Liskavets, Maxim Ushakov, Shuvendu Roy, Mark Klibanov, Ali Etemad, Shane Luke

**Venue:** AAAI 2025

**ArXiv:** [2409.01227](https://arxiv.org/abs/2409.01227)

---

## Abstract

We propose Context-aware Prompt Compression (CPC), which uses a novel context-aware sentence encoder that provides a relevance score for each sentence for a given question. The method trains using contrastive learning on question-answer pairs, achieving superior results on benchmark datasets while being up to 10.93x faster at inference compared to the best token-level compression method.

---

## 1. Introduction

Token-level compression methods (e.g., LLMLingua, LongLLMLingua) achieve good compression but are slow due to per-token scoring with large language models. CPC operates at the sentence level, using a fine-tuned encoder to assign relevance scores, enabling faster inference while maintaining or improving quality.

Key advantages:
- Sentence-level compression preserves readability
- Context-aware encoding captures question-document relevance
- Up to 10.93x faster than LongLLMLingua

---

## 2. Methodology

### 2.1 Dataset Creation (CQR Dataset)

- **Source:** WikiText documents as contexts
- **Process:**
  - Generate Q&A pairs from sampled sentences using GPT-3.5
  - Verify that answers require context, not isolated sentences
  - Filter negatives using similarity-based and KL-divergence methods
- **Result:** Context-Aware Question-Relevance (CQR) dataset with question-positive-negative tuples

### 2.2 Context-Aware Encoding

Fine-tune Mistral-7B-Instruct with dual losses:
- **Contrastive loss (L_SC):** Learns relevance by contrasting positive and negative sentence pairs relative to a question
- **Masked Next Token Prediction (L_MNTP):** Enables bidirectional attention for better sentence representations

### 2.3 Inference

1. Compute embeddings for each sentence and the question
2. Rank sentences by cosine similarity to the question
3. Select top sentences until reaching target compression ratio tau

---

## 3. Experimental Results

### 3.1 Main Results

| Metric | LongBench (3K tokens) | ZeroSCROLLS (3K tokens) |
|--------|----------------------|------------------------|
| CPC Performance | 50.0 | 34.9 |
| Prior SOTA | 48.8 | 32.8 |
| Improvement | +1.2% | +1.3% |

### 3.2 Domain Generalization

Improvements across medical, academic, and meeting transcription tasks, demonstrating robust cross-domain transfer.

### 3.3 Speed Comparison

CPC is up to 10.93x faster at inference compared to LongLLMLingua while achieving better accuracy. Linear complexity vs. the quadratic complexity of token-level methods.

### 3.4 Scaling with Larger Models

Better performance observed with larger target models (GPT-4o experiments), suggesting the compressed context is higher quality than token-level alternatives.

---

## 4. Ablation Studies

| Component | Impact |
|-----------|--------|
| MNTP loss removal | -6.92 points |
| KL-based filtering removal | -1.67 points |
| Optimal negatives per positive | 2 |

Both loss components are essential. Dataset filtering is critical for training quality. Two negatives per positive provides optimal training efficiency.

---

## 5. Limitations

- Slightly lower performance on summarization tasks compared to retrieval methods
- Sentence-level granularity may be too coarse for some applications
- Requires fine-tuning a large encoder model (Mistral-7B)

---

## Figures

- **Figure 1:** CPC pipeline overview showing context-aware sentence encoding, relevance scoring, and sentence selection for compression.
- **Figure 2:** Speed comparison between CPC and token-level methods (LLMLingua, LongLLMLingua) across different compression ratios.
- **Figure 3:** Ablation study results showing the contribution of each training component.

---

## Key References

1. Jiang et al. (2023) - LongLLMLingua
2. Jiang et al. (2023) - LLMLingua
3. Pan et al. (2024) - LLMLingua-2
4. Li et al. (2023) - Selective Context
5. Xu et al. (2023) - RECOMP
6. Chevalier et al. (2023) - AutoCompressors
7. Ge et al. (2024) - ICAE
8. Gao et al. (2024) - Mistral
9. Reimers & Gurevych (2019) - Sentence-BERT
10. Bai et al. (2024) - LLM benchmarks
