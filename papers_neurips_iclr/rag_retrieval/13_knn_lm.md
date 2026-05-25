# Generalization through Memorization: Nearest Neighbor Language Models

**Authors:** Urvashi Khandelwal, Omer Levy, Dan Jurafsky, Luke Zettlemoyer, Mike Lewis

**Venue:** ICLR 2020

**ArXiv:** [1911.00172](https://arxiv.org/abs/1911.00172)

---

## Abstract

This paper introduces kNN-LM, which extends a pre-trained neural language model by linearly interpolating it with a k-nearest neighbors (kNN) model. The nearest neighbors are computed according to distance in the pre-trained LM embedding space. Applying this augmentation to a strong Wikitext-103 LM, with neighbors drawn from the original training set, the approach achieves a new state-of-the-art perplexity of 15.79 -- a 2.9 point improvement with no additional training. The method also allows rare patterns such as factual knowledge to be memorized explicitly, rather than implicitly in model parameters. It can also be used for domain adaptation by simply varying the nearest neighbor datastore, again without further training.

---

## 1. Introduction

Neural language models learn patterns from training data but must encode all knowledge implicitly in their parameters. This creates tension between memorization (which can hurt generalization) and generalization (which may miss rare patterns). kNN-LM resolves this by separating memorization (explicit datastore lookup) from generalization (neural network representations).

## 2. Methodology

### 2.1 Architecture

The kNN-LM extends pre-trained LMs through three components:

1. **Datastore Construction**: For each training example (c_i, w_i), store a key-value pair: the context representation f(c_i) as key and target word w_i as value
2. **Inference**: Given test context x, retrieve k nearest neighbors using L2 distance in embedding space
3. **Interpolation**: Final distribution = lambda * p_kNN + (1-lambda) * p_LM

### 2.2 Technical Details

- Representations extracted from the final transformer layer's feedforward input
- FAISS library used for efficient nearest-neighbor retrieval
- Full-precision L2 distance (superior to quantized alternatives)
- Softmax over negative distances weighted by frequency to compute p_kNN

## 3. Experimental Results

### 3.1 Performance Improvements

| Dataset | Baseline PPL | kNN-LM PPL | Improvement |
|---------|-------------|------------|-------------|
| Wikitext-103 | 18.65 | 15.79 | -2.86 |
| Books corpus | 11.89 | 10.89 | -1.00 |

State-of-the-art on Wikitext-103 with no additional training.

### 3.2 Scaling Properties

A model trained on 100M tokens with a 3B-token datastore outperforms a model trained directly on all 3B tokens. This demonstrates that kNN retrieval can substitute for explicit training on larger datasets.

### 3.3 Domain Adaptation

Using the Books corpus datastore with a Wikipedia-trained model (lambda=0.65):
- Effective domain adaptation without any retraining
- Simply swapping the datastore adapts the model to new domains

### 3.4 Hyperparameter Analysis

| Parameter | Optimal Value | Notes |
|-----------|--------------|-------|
| k (neighbors) | 1024 | Though k=8 already achieves SOTA |
| lambda (interpolation) | 0.25 | For Wikitext-103; 0.65 for domain adaptation |
| Distance metric | Full-precision L2 | Superior to quantized alternatives |

## 4. Analysis: Why kNN-LMs Work

Three key factors identified:

1. The Transformer LM learns an excellent representation function for contexts with an implicit notion of similarity
2. Neural models can memorize training data but this reduces representation generalization quality
3. kNN approach enables memorization while preserving effective similarity functions

### 4.1 Comparison to Alternatives

- N-gram interpolation provides minimal gains (0.2 perplexity points)
- Models trained without dropout memorize training data perfectly (0 training loss) but severely overfit (validation PPL: 28.59)
- Implicit memorization via parameters is less effective than explicit kNN retrieval

## 5. Practical Benefits

1. **No additional training**: Improvements come from datastore construction only
2. **Domain adaptation**: Swap datastores for different domains without retraining
3. **Factual knowledge**: Explicit memorization of rare patterns and facts
4. **Scalability**: Performance scales with datastore size, complementing model capacity

## 6. Figures

- **Figure 1**: Overview of kNN-LM architecture showing datastore construction from training data and interpolation during inference.
- **Figure 2**: Performance as a function of k (number of neighbors), showing diminishing returns beyond k=1024.
- **Figure 3**: Analysis of which tokens benefit most from kNN retrieval, showing factual knowledge and rare patterns benefit most.

---

## References (Top 10)

1. Baevski & Auli (2019) - Adaptive Input Representations for Neural Language Modeling (baseline model)
2. Grave et al. (2017) - Continuous Cache for Language Modeling (related caching approach)
3. Johnson et al. (2017) - FAISS: Billion-Scale Similarity Search with GPUs (implementation tool)
4. Vaswani et al. (2017) - Attention Is All You Need (Transformer architecture)
5. Merity et al. (2017) - Pointer Sentinel Mixture Models and Wikitext-103 benchmark
6. Devlin et al. (2019) - BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding
7. Gu et al. (2018) - Search Engine Guided Neural Machine Translation
8. Guu et al. (2018) - Generating Sentences by Editing Prototypes
9. Dai et al. (2019) - Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context
10. Press & Wolf (2017) - Using the Output Embedding to Improve Language Models
