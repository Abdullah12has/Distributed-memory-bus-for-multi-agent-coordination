# REALM: Retrieval-Augmented Language Model Pre-Training

**Authors:** Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasupat, Ming-Wei Chang

**Venue:** ICML 2020 (cs.CL, cs.LG)

**ArXiv:** [2002.08909](https://arxiv.org/abs/2002.08909)

---

## Abstract

Language model pre-training captures a significant amount of world knowledge, but this knowledge is stored implicitly in the neural network parameters, requiring ever-larger networks to cover more facts. This paper proposes augmenting language model pre-training with a latent knowledge retriever, which allows the model to retrieve and attend over documents from a large corpus such as Wikipedia, used during pre-training, fine-tuning, and inference. For the first time, the paper demonstrates how to pre-train such a knowledge retriever in an unsupervised manner, using masked language modeling as the learning signal, and backpropagating through a retrieval step that considers millions of documents. On the challenging task of Open-domain Question Answering, REALM outperforms all previous methods by a significant margin (4-16% absolute accuracy) while also providing the benefits of interpretability and modularity.

---

## 1. Introduction

Knowledge-intensive NLP tasks require models to access factual information. Traditional approaches store knowledge implicitly in model parameters, requiring extremely large networks. REALM instead uses an explicit retrieval mechanism that can be updated independently of model parameters.

## 2. Methodology

### 2.1 Generative Process

REALM decomposes p(y|x) into two steps:
1. **Retrieve**: Sample document z from corpus Z based on input x
2. **Predict**: Generate output y conditioned on both z and x

The model marginalizes over retrieved documents as latent variables.

### 2.2 Architecture Components

**Knowledge Retriever** (p(z|x)):
- Dense inner-product scoring with BERT-style Transformers
- Computes relevance scores between query and document embeddings
- Uses Maximum Inner Product Search (MIPS) for efficient retrieval

**Knowledge-Augmented Encoder** (p(y|z,x)):
- Joins input x and retrieved document z into a single sequence
- Applies cross-attention before prediction
- Uses [CLS] token representation for span extraction

### 2.3 Technical Challenges and Solutions

| Challenge | Solution |
|-----------|----------|
| Computational scale (millions of docs) | MIPS with asynchronous index refreshes |
| Training stability | Salient span masking, null document, no trivial retrievals |
| Cold start | Warm-start embeddings using Inverse Cloze Task |

### 2.4 Salient Span Masking

Rather than random masking, REALM preferentially masks named entities and dates -- spans likely to require world knowledge. This focuses the learning signal on knowledge-dependent predictions.

## 3. Experimental Results

### 3.1 Open-Domain QA Benchmarks

| Model | NQ (EM) | WQ (EM) | CT (EM) |
|-------|---------|---------|---------|
| REALM (Wikipedia) | 39.2% | 40.2% | 46.8% |
| REALM (CC-News) | 40.4% | 40.7% | 42.9% |
| ORQA | 33.3% | 36.4% | 30.1% |
| T5-11B (closed-book) | 36.6% | 37.4% | - |

REALM with 330M parameters exceeds T5-11B (11.3B parameters) on NQ and WQ.

### 3.2 Ablation Studies

Key findings from ablations:
- Both retriever and encoder benefit from REALM pre-training
- Salient span masking significantly outperforms random masking strategies
- Frequent MIPS index refreshes (every ~500 steps) are critical for stable optimization
- Retrieved documents meaningfully improve prediction of knowledge-dependent masked tokens

## 4. Pre-training Details

- 200k steps on 64 TPUs
- Batch size: 512
- Learning rate: 3e-5
- Marginalizes over top 8 documents including null document
- Knowledge corpus: 13M+ Wikipedia passages (288-word blocks)

## 5. Fine-tuning Details

- Reuses ORQA hyperparameters for direct comparison
- Fixed retriever index (documents not updated during fine-tuning)
- Retrieves top-5 documents during inference

## 6. Key Advantages

**vs. Implicit Knowledge Storage (BERT, T5):**
- Interpretability: explicitly shows which documents inform predictions
- Modularity: corpus can be updated without retraining
- Parameter efficiency: 330M params outperform 11B params

**vs. Prior Retrieval-Based Systems:**
- End-to-end learned retriever during pre-training (not fixed heuristic)
- Retrieves only 5 documents vs. competitors' 20-80

## 7. Figures

- **Figure 1**: Overview of REALM pre-training showing masked language modeling with latent retrieval step, backpropagating through MIPS.
- **Figure 2**: Comparison of REALM retrieval with TF-IDF, showing REALM retrieves more contextually relevant passages.
- **Figure 3**: Training curves showing the impact of index refresh frequency on convergence.

---

## References (Top 10)

1. Devlin et al. (2018) - BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding
2. Lee et al. (2019) - Latent Retrieval for Weakly Supervised Open Domain Question Answering (ORQA)
3. Chen et al. (2017) - Reading Wikipedia to Answer Open-Domain Questions (DrQA)
4. Raffel et al. (2019) - Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer (T5)
5. Petroni et al. (2019) - Language Models as Knowledge Bases?
6. Liu et al. (2019) - RoBERTa: A Robustly Optimized BERT Pretraining Approach
7. Min et al. (2019) - A Discrete Hard EM Approach for Weakly Supervised Question Answering
8. Asai et al. (2019) - Learning to Retrieve Reasoning Paths over Wikipedia Graph for Question Answering
9. Roberts et al. (2020) - How Much Knowledge Can You Pack into the Parameters of a Language Model?
10. Khandelwal et al. (2019) - Generalization through Memorization: Nearest Neighbor Language Models
