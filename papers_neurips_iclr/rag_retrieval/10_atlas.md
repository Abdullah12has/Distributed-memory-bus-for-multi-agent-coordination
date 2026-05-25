# Atlas: Few-shot Learning with Retrieval Augmented Language Models

**Authors:** Gautier Izacard, Patrick Lewis, Maria Lomeli, Lucas Hosseini, Fabio Petroni, Timo Schick, Jane Dwivedi-Yu, Armand Joulin, Sebastian Riedel, Edouard Grave

**Venue:** JMLR 2023 (cs.CL)

**ArXiv:** [2208.03299](https://arxiv.org/abs/2208.03299)

---

## Abstract

Large language models can perform many tasks with limited supervision, but their reliance on internal memorization limits their flexibility and knowledge capacity. This paper presents Atlas, a carefully designed and pre-trained retrieval-augmented language model that is able to learn knowledge-intensive tasks with very few training examples. Atlas reaches over 42% accuracy on Natural Questions using only 64 examples, outperforming a 540B parameters model by 3% despite having 50x fewer parameters. The work evaluates performance across multiple benchmarks including MMLU, KILT, and NaturalQuestions.

---

## 1. Introduction

Large language models store knowledge implicitly in their parameters, requiring enormous model sizes for broad coverage. Atlas instead pairs a relatively small language model (11B parameters) with a dense retriever, achieving state-of-the-art few-shot performance across knowledge-intensive benchmarks.

## 2. Architecture

### 2.1 Retriever Module

- Built on Contriever using a dual-encoder architecture with BERT-base
- Independently embeds queries and documents
- Computes similarity via dot product of embeddings
- Retrieves from large corpora (Wikipedia, Common Crawl)

### 2.2 Language Model

- Uses T5 sequence-to-sequence architecture
- Employs Fusion-in-Decoder (FiD) modifications
- Processes retrieved documents independently in the encoder
- Concatenates encoder outputs for cross-attention in the decoder

## 3. Retriever Training Objectives

Four loss functions evaluated for joint training:

| Objective | Mechanism | Key Property |
|-----------|-----------|--------------|
| **ADist** (Attention Distillation) | Uses cross-attention scores from LM | Leverages LM internal signals |
| **EMDR2** | Treats docs as latent variables via EM | Principled probabilistic framework |
| **PDist** (Perplexity Distillation) | Predicts per-document perplexity improvement | Most efficient to compute |
| **LOOP** | Leave-one-out: measures degradation when removing docs | Robust but expensive |

PDist was selected for main experiments due to its efficiency.

## 4. Pre-training

Three pretext tasks evaluated:
- **Prefix language modeling**: Split documents into two halves (context -> continuation)
- **Masked language modeling**: 15% masking ratio (marginal best)
- **Title-to-section generation**: Wikipedia title -> section content

## 5. Efficient Fine-tuning Strategies

| Strategy | Mechanism | Overhead |
|----------|-----------|----------|
| Full index update | Refreshes embeddings every R steps | ~30% |
| Re-ranking | Retrieves L docs, re-embeds, passes top-K to LM | ~10% |
| Query-side fine-tuning | Freezes document encoder, trains query encoder only | Minimal |

Query-side fine-tuning proved effective in few-shot settings without performance degradation.

## 6. Experimental Results

### 6.1 MMLU (Massive Multitask Language Understanding)

| Setting | Atlas-11B | Closed-book T5-11B | PaLM-540B |
|---------|-----------|-------------------|-----------|
| 5-shot | 47.9% | 36.1% | 69.3% |
| 5-shot multitask | 56.6% | 43.5% | - |
| Full/Transfer | 66.0% | 54.0% | - |

Atlas-11B zero-shot (47.1%) exceeds GPT-3's 5-shot (43.9%) with 15x fewer parameters.

### 6.2 Open-Domain Question Answering

**NaturalQuestions (64-shot):**

| Model | Parameters | EM |
|-------|-----------|-----|
| Atlas-11B | 11B | 42.4% |
| PaLM | 540B | 39.6% |
| Chinchilla | 70B | 35.5% |

**Full dataset setting:** 60.4% exact match (state-of-the-art), improving from previous best of 55.9%.

**TriviaQA (64-shot):** 74.5% filtered, 84.7% unfiltered.

### 6.3 FEVER Fact Checking

- 15-shot accuracy: 56.2% vs Gopher's 51.1% (+5.1 points)
- Full dataset: 78.0% (80.1% with FEVER-matched Wikipedia index)

## 7. Analysis

### 7.1 Leakage Assessment

Manual inspection detected approximately 2.8% of MMLU questions with high n-gram overlap to CCNet corpus. Filtering leaked passages reduced performance from 56.4% to 55.8% (-0.5%), confirming result reliability.

### 7.2 Retrieved Content Utility

- 44% of correct answers: partially useful background information retrieved
- 26%: complete necessary information in straightforward form
- 30%: correct answer text appearing in top 25 passages

### 7.3 Temporal Sensitivity

Atlas successfully adapted to temporal index changes. When trained on 2017 answers with 2017 Wikipedia index and switching to 2020 index without retraining, accuracy rose from 1.5% to 53.1% on 2020 test questions.

### 7.4 Index Compression

Product quantization enabled significant compression:
- Wikipedia index: 49GB -> 4GB with negligible performance loss
- Combined index: 587GB -> 50GB
- Enables deployment on single 80GB GPU

## 8. Figures

- **Figure 1**: Atlas architecture showing the dual-encoder retriever coupled with the Fusion-in-Decoder language model.
- **Figure 2**: Few-shot scaling curves comparing Atlas to PaLM and Chinchilla across different numbers of training examples.
- **Figure 3**: Temporal adaptation experiment showing knowledge base swapping without retraining.

---

## References (Top 10)

1. Izacard & Grave (2020) - Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering (FiD)
2. Lewis et al. (2020) - Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
3. Guu et al. (2020) - REALM: Retrieval-Augmented Language Model Pre-Training
4. Raffel et al. (2019) - Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer (T5)
5. Brown et al. (2020) - Language Models are Few-Shot Learners (GPT-3)
6. Karpukhin et al. (2020) - Dense Passage Retrieval for Open-Domain Question Answering
7. Izacard et al. (2022) - Unsupervised Dense Information Retrieval with Contrastive Learning (Contriever)
8. Borgeaud et al. (2021) - Improving Language Models by Retrieving from Trillions of Tokens (RETRO)
9. Chowdhery et al. (2022) - PaLM: Scaling Language Modeling with Pathways
10. Hoffmann et al. (2022) - Training Compute-Optimal Large Language Models (Chinchilla)
