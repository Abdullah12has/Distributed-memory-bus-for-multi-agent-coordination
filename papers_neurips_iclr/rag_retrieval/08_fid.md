# Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering (Fusion-in-Decoder)

**Authors:** Gautier Izacard, Edouard Grave

**Venue:** EACL 2021 (cs.CL)

**ArXiv:** [2007.01282](https://arxiv.org/abs/2007.01282)

---

## Abstract

Generative models for open-domain question answering generate answers token by token, conditioned on retrieved passages. This paper investigates how the number of retrieved passages affects performance, demonstrating that generative models can effectively aggregate information across many passages. The performance of this method significantly improves when increasing the number of retrieved passages, enabling a 770M-parameter model to outperform an 11B-parameter closed-book T5 model.

---

## 1. Introduction

Open-domain question answering requires accessing external knowledge since parametric model knowledge alone is insufficient. This work combines passage retrieval (using BM25 or DPR) with a sequence-to-sequence generative model (T5/BART) to produce answers.

## 2. Methodology

### 2.1 Two-Stage Pipeline

1. **Retrieval Stage**: Passages are retrieved using either:
   - BM25 (sparse, term-matching retrieval)
   - DPR (Dense Passage Retrieval with learned embeddings)
2. **Reading Stage**: A pretrained seq-to-seq model (T5 or BART) generates answers from question + retrieved passages

### 2.2 Fusion-in-Decoder (FiD)

The key innovation is in how retrieved passages are processed:

- Each retrieved passage is independently processed by the encoder along with the question
- The decoder performs attention over the concatenation of all encoder representations
- This enables linear computational scaling with the number of passages (rather than quadratic)
- Supports up to 100 passages efficiently

**Input format**: Each passage is formatted as "question: [question] title: [title] context: [passage text]" and independently encoded.

## 3. Experimental Results

### 3.1 Main Results

| Model | NQ (EM) | TriviaQA (EM) |
|-------|---------|---------------|
| FiD-Large (DPR) | 51.4% | 67.6% |
| FiD-Base (DPR) | 48.2% | 65.0% |
| RAG | 44.5% | 56.8% |
| T5-11B (closed-book) | 36.6% | 60.5% |
| REALM | 40.4% | - |

### 3.2 Scaling with Number of Passages

Performance improves significantly from 10 to 100 passages:
- TriviaQA: ~6% gain
- NaturalQuestions: ~3.5% gain

This contrasts with extractive models that plateau around 10-20 passages.

### 3.3 Training Efficiency

Training with fewer passages (5-50) then evaluating with more still yields competitive results, reducing computational requirements during training.

## 4. Datasets Evaluated

- **Natural Questions** (NQ): Wikipedia-based open-domain QA
- **TriviaQA**: Trivia questions with unfiltered web evidence
- **SQuAD v1.1**: Open-domain variant

## 5. Key Insights

1. Generative models excel at aggregating evidence from multiple passages, unlike extractive models that plateau
2. A 770M parameter model with retrieval outperforms an 11B parameter model without retrieval
3. The FiD architecture enables efficient scaling to many passages through independent encoding
4. Evidence aggregation across passages is a key advantage of generative over extractive approaches

## 6. Figures

- **Figure 1**: Architecture diagram showing independent encoding of passages followed by joint decoding with cross-attention over concatenated encoder outputs.
- **Figure 2**: Performance curves showing continued improvement as the number of retrieved passages increases from 10 to 100.

---

## References (Top 10)

1. Roberts et al. (2020) - How Much Knowledge Can You Pack Into the Parameters of a Language Model?
2. Karpukhin et al. (2020) - Dense Passage Retrieval for Open-Domain Question Answering
3. Chen et al. (2017) - Reading Wikipedia to Answer Open-Domain Questions
4. Lewis et al. (2020) - Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
5. Raffel et al. (2019) - Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer
6. Min et al. (2020) - AmbigQA: Answering Ambiguous Open-Domain Questions
7. Kwiatkowski et al. (2019) - Natural Questions: A Benchmark for Question Answering Research
8. Joshi et al. (2017) - TriviaQA: A Large Scale Distantly Supervised Challenge Dataset for Reading Comprehension
9. Guu et al. (2020) - REALM: Retrieval-Augmented Language Model Pre-Training
10. Wang et al. (2019) - Multi-Passage BERT: A Globally Normalized BERT Model for Open-Domain Question Answering
