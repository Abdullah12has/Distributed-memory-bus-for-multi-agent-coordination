# Compressive Transformers for Long-Range Sequence Modelling

**Authors:** Jack W. Rae, Anna Potapenko, Siddhant M. Jayakumar, Chloe Hillier, Timothy P. Lillicrap

**Venue:** ICLR 2020

**ArXiv:** [1911.05507](https://arxiv.org/abs/1911.05507)

---

## Abstract

We present the Compressive Transformer, a sequence model that compresses past memories for long-range sequence learning. The model achieves state-of-the-art results on WikiText-103 (17.1 ppl) and Enwik8 (0.97 bpc) benchmarks, demonstrates effectiveness on speech modeling, and can serve as a memory mechanism for reinforcement learning tasks. We also introduce PG-19, a new benchmark dataset for language modeling derived from books.

---

## 1. Introduction

The paper motivates compression through human memory: humans build compressed representations of narratives rather than storing every detail. While RNNs compress history into hidden states and Transformers maintain granular external memories, the Compressive Transformer combines both approaches.

Key observation: "The Transformer will thus represent the past with a tensor that is, in practice, an order of magnitude larger than an LSTM's hidden state." This storage and computational cost motivates the proposed compression strategy.

---

## 2. Related Work

- **Transformer-XL:** Keeps past activations in memory with relative positional embeddings -- incorporated into the Compressive Transformer.
- **Sparse Transformer:** Uses fixed sparse attention patterns but requires custom kernels.
- **Adaptive Attention Spans:** Different heads learn variable attention lengths but requires dynamic computation unsuitable for TPUs.

The Compressive Transformer uses "simple dense linear-algebra components, such as convolutions," enabling efficient implementation on standard accelerators.

---

## 3. Model

### 3.1 Architecture

The model processes input sequences of fixed size n_s in windows. When memory reaches capacity, the oldest n_s activations are not discarded but compressed via function f_c that maps R^{n_s x d} -> R^{floor(n_s/c) x d}, where c is the compression rate and d is the hidden dimension.

**Algorithm:**
1. Initialize memory and compressed memory to zeros
2. For each layer, concatenate compressed memory and regular memory
3. Apply multi-head attention over combined memories
4. Compress oldest memories and store in secondary FIFO buffer
5. Update both memory structures

### 3.2 Compression Functions and Losses

**Compression approaches tested:**
- Max/mean pooling (baseline)
- 1D convolution
- Dilated convolutions
- Most-used (based on attention weights)

**Training objectives:**

| Loss Type | Description | Purpose |
|-----------|-------------|---------|
| Auto-encoding | Reconstruct original memories from compressed form | Lossless reconstruction |
| Attention-reconstruction | Match attention outputs over compressed vs. original memories | Task-relevant compression |

The attention-reconstruction loss proved most effective. Gradients from compression losses do not flow back to the main network, preventing interference with task optimization.

### 3.3 Temporal Range

- Transformer-XL range: l x n
- Compressive Transformer range: l x (n_m + c * n_cm)

Example: Setting n_cm = n_m = n/2 and c=3 achieves 2x temporal range with identical attention cost.

---

## 4. PG-19 Benchmark

A new book-level language modeling benchmark extracted from Project Gutenberg texts published before 1919.

| Dataset | Avg Length | Train Size | Vocab | Type |
|---------|-----------|-----------|-------|------|
| 1B Word | 27 | 4.15 GB | 793K | News (sentences) |
| Penn Treebank | 355 | 5.1 MB | 10K | News (articles) |
| WikiText-103 | 3.6K | 515 MB | 267K | Wikipedia |
| **PG-19** | **69K** | **10.9 GB** | **open** | **Books** |

Statistics: 28,752 books, 11 GB of text, over 2x larger than BookCorpus.

---

## 5. Experiments

### 5.1 PG-19 Results

| Model | Valid PPL | Test PPL |
|-------|----------|----------|
| 36L Transformer-XL | 45.5 | 36.3 |
| 36L Compressive Transformer | 43.4 | **33.6** |

Configuration: 512 window size, 512 memory, 512 compressed memory, compression rate C=2.

### 5.2 Enwik8 (Character-level)

| Model | BPC |
|-------|-----|
| 24L Transformer-XL (Dai et al.) | 0.99 |
| Sparse Transformer | 0.991 |
| Adaptive Transformer | 0.98 |
| **24L Compressive Transformer** | **0.97** |

**Compression function comparison:**

| Function | Loss Type | BPC |
|----------|-----------|-----|
| Conv | BPTT | 0.996 |
| Max pooling | -- | 0.986 |
| Conv | Auto-encoding | 0.984 |
| Dilated conv | Attention | 0.977 |
| Conv | Attention | **0.973** |

### 5.3 WikiText-103 (Word-level)

Test perplexity: **17.1** (vs. Transformer-XL 18.3), a 1.2 ppl improvement over prior SOTA.

**Performance by word frequency:**

| Frequency Bucket | >10K | 1K-10K | 100-1K | <100 | All |
|------------------|------|--------|--------|------|-----|
| LSTM (2018) | 12.1 | 219 | 1,197 | 9,725 | 36.4 |
| Transformer-XL | 7.8 | 61.2 | 188 | 1,123 | 18.1 |
| **Compressive Transformer** | 7.6 | 55.9 | 158 | **937** | **17.1** |
| **Relative gain** | 2.6% | 9.5% | 21% | **19.9%** | 5.8% |

Key insight: Primary improvements occur for infrequent words (~20% gain vs. 2.6% for frequent words).

### 5.4 Compressibility Analysis

Compression loss across layers: "The first layer of the Transformer is highly compressible. However there is not a clear trend of compression cost increasing with layer depth."

### 5.5 Attention Patterns

Most attention concentrates on current sequence; notably, "there is an increase in attention at the transition from memory to compressed memory," indicating the model learns to preserve salient information during compression.

### 5.6 Speech Modeling

20-layer models trained on 24.6 hours of 24kHz speech data. The Compressive Transformer with C=4 outperforms Transformer-XL and maintains a slim advantage over WaveNet with comparable parameters (~40M).

### 5.7 Reinforcement Learning

Tested as drop-in LSTM replacement in IMPALA agent on DMLab-30 task requiring long-range memory. Compression rate C=4 proved optimal; C=1 (no compression) failed to learn effectively. Best-performing agents solve the task to human-level.

---

## 6. Compressed Memory Size Ablation

| Compressed Memory Size | 512 | 1024 | 2048 | 3072 | 4096 |
|------------------------|-----|------|------|------|------|
| Enwik8 BPC | 1.01 | 0.99 | 0.98 | **0.97** | 1.00 |

---

## 7. Training Insight

Reducing learning rate during training degrades performance significantly. Solution: reduce update frequency (every 4 steps after 60,000 iterations) rather than reducing learning rate. This increases effective batch size and improves generalization.

Transformer-XL baseline improvement: 0.995 -> 0.984 bpc on Enwik8 with this technique.

---

## Figures

- **Figure 1:** Architecture diagram showing the two-level memory hierarchy with regular memory and compressed memory, connected via multi-head attention.
- **Figure 2:** Attention distribution over 20,000 test sequences showing concentration on current sequence with increased attention at the memory-to-compressed-memory transition.
- **Figure 3:** PG-19 example generations showing multi-hundred-word coherent text with character name consistency.

---

## Key References

1. Dai et al. (2019) - Transformer-XL
2. Child et al. (2019) - Sparse Transformer
3. Sukhbaatar et al. (2019) - Adaptive Attention Span
4. Graves et al. (2014) - Neural Turing Machines
5. Espeholt et al. (2018) - IMPALA
6. Van den Oord et al. (2016) - WaveNet
7. Merity et al. (2017) - WikiText-103
8. Baevski & Auli (2019) - Adaptive input representations
9. Al-Rfou et al. (2019) - Character Transformers
10. Zhu et al. (2015) - BookCorpus
