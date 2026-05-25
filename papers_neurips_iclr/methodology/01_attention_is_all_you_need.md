# Attention Is All You Need

**Authors:** Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin

**Venue:** NeurIPS 2017

**arXiv:** [1706.03762](https://arxiv.org/abs/1706.03762)

---

## Abstract

The paper introduces the Transformer, a neural network design that relies exclusively on attention mechanisms rather than recurrence or convolutions. The researchers demonstrate superior performance on machine translation benchmarks---achieving 28.4 BLEU on English-to-German and 41.8 BLEU on English-to-French tasks---while requiring less training time. They additionally show the model's effectiveness on English constituency parsing with varying data availability.

---

## 1. Introduction

Recurrent neural networks process sequences sequentially, preventing parallelization within training examples. This becomes critical with longer sequences due to memory constraints. The Transformer eschews recurrence and instead relies entirely on an attention mechanism to draw global dependencies between input and output. It is the first transduction model relying entirely on self-attention to compute representations.

---

## 2. Model Architecture

### Encoder and Decoder Stacks

| Component | Specification |
|-----------|--------------|
| Encoder layers | N = 6 identical layers |
| Decoder layers | N = 6 identical layers |
| Model dimension | d_model = 512 |
| Sub-layers | Multi-head self-attention + Feed-forward networks |
| Normalization | LayerNorm(x + Sublayer(x)) with residual connections |

The decoder includes a third sub-layer performing multi-head attention over encoder outputs. Masking prevents attending to subsequent positions.

### Scaled Dot-Product Attention

```
Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) V
```

Where Q, K, V are queries, keys, and values matrices. d_k is the key dimension. The scaling factor 1/sqrt(d_k) prevents softmax saturation for large d_k values.

### Multi-Head Attention

| Parameter | Value |
|-----------|-------|
| Number of heads (h) | 8 |
| d_k per head | d_model/h = 64 |
| d_v per head | 64 |

Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions.

### Three Attention Applications

1. **Encoder-decoder attention:** Decoder queries attend to encoder outputs
2. **Encoder self-attention:** Each position attends to all previous positions
3. **Decoder self-attention:** Masked to preserve auto-regressive property

### Position-wise Feed-Forward Networks

```
FFN(x) = max(0, xW1 + b1)W2 + b2
```

- Input/output dimension: d_model = 512
- Inner dimension: d_ff = 2048

### Positional Encoding

Uses sine and cosine functions at different frequencies:

```
PE(pos,2i) = sin(pos/10000^(2i/d_model))
PE(pos,2i+1) = cos(pos/10000^(2i/d_model))
```

This allows the model to easily learn to attend by relative positions.

---

## 3. Why Self-Attention

### Computational Complexity Comparison

| Layer Type | Complexity/Layer | Sequential Operations | Max Path Length |
|------------|-----------------|----------------------|-----------------|
| Self-Attention | O(n^2 * d) | O(1) | O(1) |
| Recurrent | O(n * d^2) | O(n) | O(n) |
| Convolutional | O(k * n * d^2) | O(1) | O(log_k(n)) |
| Self-Attention (restricted) | O(r * n * d) | O(1) | O(n/r) |

Self-attention connects all positions with constant sequential operations, whereas recurrence requires O(n) operations. Self-attention is faster when sequence length n < representation dimensionality d. Individual attention heads clearly learn to perform different tasks, including syntactic and semantic structure learning.

---

## 4. Training

### Data and Batching

| Dataset | Size | Vocabulary | Batch Size |
|---------|------|-----------|-----------|
| WMT 2014 EN-DE | 4.5M sentence pairs | 37K tokens (BPE) | ~25K source tokens |
| WMT 2014 EN-FR | 36M sentences | 32K tokens (word-piece) | ~25K target tokens |

### Hardware and Schedule

| Model Type | Hardware | Step Time | Training Steps | Duration |
|-----------|----------|-----------|----------------|----------|
| Base | 8 NVIDIA P100 GPUs | 0.4s | 100,000 | 12 hours |
| Big | 8 NVIDIA P100 GPUs | 1.0s | 300,000 | 3.5 days |

### Optimizer

Adam optimizer with beta_1 = 0.9, beta_2 = 0.98, epsilon = 10^-9. Learning rate schedule: increasing linearly for first warmup steps (4000), then decreasing proportionally to inverse square root.

### Regularization

1. **Residual Dropout:** P_drop = 0.1 (base model)
2. **Label Smoothing:** epsilon_ls = 0.1

---

## 5. Results

### Machine Translation

| Model | EN-DE BLEU | EN-FR BLEU | Training Cost (FLOPs) |
|-------|-----------|-----------|----------------------|
| Transformer (base) | 27.3 | 38.1 | 3.3 x 10^18 |
| Transformer (big) | **28.4** | **41.8** | 2.3 x 10^19 |
| Previous SOTA ensemble | 26.36 | 41.29 | 7.7 x 10^19 |

- EN-DE: Outperforms all previously published models by >2.0 BLEU
- EN-FR: SOTA single-model at <1/4 the training cost of previous best

### Model Variations (Ablation)

| Variation | Impact |
|-----------|--------|
| Single-head vs. 8-head | -0.9 BLEU worse |
| Reducing attention key size | Hurts model quality |
| Bigger models | Better performance |
| Dropout regularization | Very helpful |
| Sinusoidal vs. learned positional encoding | Nearly identical |

### English Constituency Parsing

| Configuration | WSJ 23 F1 Score |
|--------------|-----------------|
| Transformer (4 layers, WSJ only) | 91.3 |
| Transformer (4 layers, semi-supervised) | 92.7 |
| Previous SOTA | 93.3 |

Despite the lack of task-specific tuning, the model performs surprisingly well.

---

## 6. Key Metrics Summary

- **Parameters (base model):** 65M
- **Parameters (big model):** 213M
- **Positional encoding dimensions:** 512
- **Feed-forward inner layer:** 2048
- **Attention heads:** 8
- **Query/key/value dimensions per head:** 64 each

---

## 7. Figure Descriptions

- **Figure 1:** Transformer architecture diagram showing encoder-decoder structure with multi-head attention
- **Figure 2:** Scaled dot-product attention and multi-head attention mechanisms
- **Figure 3:** Encoder self-attention in layer 5 tracking long-distance dependencies
- **Figures 4-5:** Attention heads learning anaphora resolution and syntactic/semantic structure

---

## Key References

1. Bahdanau et al. (2014) --- Neural machine translation by attending and aligning
2. Cho et al. (2014) --- RNN encoder-decoder for statistical machine translation
3. Hochreiter and Schmidhuber (1997) --- Long short-term memory networks
4. He et al. (2016) --- Residual learning for deep neural networks
5. Hochreiter et al. (2001) --- Gradient flow in recurrent nets
6. Kingma and Ba (2015) --- Adam optimizer
7. Wu et al. (2016) --- Google's neural machine translation system
8. Kalchbrenner et al. (2017) --- Neural machine translation in linear time (ByteNet)
9. Gehring et al. (2017) --- Convolutional sequence-to-sequence learning
10. Sennrich et al. (2015) --- Neural machine translation of rare words with subword units
