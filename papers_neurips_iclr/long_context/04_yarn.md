# YaRN: Efficient Context Window Extension of Large Language Models

**Authors:** Bowen Peng, Jeffrey Quesnelle, Honglu Fan, Enrico Shippole

**Venue:** arXiv preprint (cs.CL, cs.AI, cs.LG), 2023

**ArXiv:** [2309.00071](https://arxiv.org/abs/2309.00071)

---

## Abstract

Rotary Position Embeddings (RoPE) have been widely adopted in transformer-based language models but suffer from limited context windows determined during pre-training. This paper introduces YaRN (Yet another RoPE extensioN method), a compute-efficient method to extend the context window of these models, requiring 10x less tokens and 2.5x less training steps than previous methods. YaRN demonstrates that LLaMA models can handle longer sequences than originally trained for while surpassing previous state-of-the-art results. The method also exhibits the ability to generalize beyond its fine-tuning dataset's context limitations.

---

## 1. Introduction

Extending the context window of pre-trained LLMs is crucial for processing long documents, but naive approaches fail due to the sensitivity of positional embeddings. YaRN combines multiple technical innovations to achieve efficient, high-quality context extension.

## 2. Background: RoPE and Its Limitations

Rotary Position Embeddings encode position through rotation matrices applied to query and key vectors. The rotation frequency varies across dimensions, with higher dimensions encoding longer-range positional information. Direct extrapolation beyond training length fails because the model encounters unseen rotation angles.

## 3. Methodology

### 3.1 NTK-Aware Interpolation

Modifies the base parameter b to spread interpolation pressure across dimensions rather than scaling uniformly:
- b' = b * s^(|D|/(|D|-2))
- Addresses the loss of high-frequency positional information critical for distinguishing nearby tokens
- Avoids the information crowding problem of linear Position Interpolation (PI)

### 3.2 NTK-by-Parts Approach

Selective interpolation based on wavelength ratios:

| Wavelength Category | Interpolation | Rationale |
|-------------------|---------------|-----------|
| Short (frequent dimensions) | None | Preserves local position resolution |
| Long (infrequent dimensions) | Full | These dimensions already handle long range |
| Intermediate | Ramped (smooth transition) | Gradual blend between extremes |

Parameters alpha and beta control the transition boundaries. Recommended: alpha=1, beta=32 for Llama models.

### 3.3 Dynamic Scaling

An inference-time technique that dynamically adjusts the scale factor s based on actual sequence length:
- Allows graceful degradation beyond trained context limits
- No additional training required
- Enables models to handle variable-length inputs

### 3.4 Attention Scaling

Incorporates a temperature factor t in the softmax computation:
- softmax(q_m^T k_n / (t * sqrt(|D|)))
- Temperature formula: sqrt(1/t) = 0.1 * ln(s) + 1
- Compensates for the increased entropy in attention distributions at longer contexts

## 4. Experimental Results

### 4.1 Training Efficiency

- Extended Llama 2 7B and 13B models
- Only 400 training steps (0.1% of pre-training compute)
- Used 64k token segments from PG19 dataset

### 4.2 Language Modeling Performance (Proof-pile, 128k evaluation)

| Model | Scale Factor | 64k Context PPL | 128k Context PPL |
|-------|-------------|-----------------|------------------|
| YaRN 7B | s=32 | 2.45 | 2.37 |
| YaRN 13B | s=32 | 2.31 | 2.24 |

### 4.3 Standard Benchmark Results

| Benchmark | YaRN (s=32) | Baseline Llama2 |
|-----------|-------------|-----------------|
| ARC-Challenge | 52.1 | 53.1 |
| HellaSwag | 78.4 | 77.8 |
| MMLU | 46.1 | 46.9 |
| TruthfulQA | 39.3 | 38.8 |

Minimal degradation on standard benchmarks despite 32x context extension.

### 4.4 Passkey Retrieval

Both 7B and 13B models achieved >99% accuracy retrieving passkeys at 128k context length.

## 5. Extrapolation Capability

A significant finding: YaRN models trained on 64k context successfully extrapolate to 128k during evaluation, demonstrating transfer learning from s=16 to s=32 without the network needing to relearn interpolated embeddings.

## 6. Key Advantages

1. **Computational Efficiency**: 10x fewer tokens and 2.5x fewer training steps than Position Interpolation
2. **No Inference Overhead**: Compatible with Flash Attention 2
3. **Better Generalization**: Maintains performance on short contexts while extending long context
4. **Universal Parameters**: Temperature formula generalizable across Llama and Llama 2 variants

## 7. Limitations

- Parameters alpha and beta require case-by-case tuning (though defaults work well for Llama)
- Perplexity alone does not fully capture "effective context size"
- Not compared against all concurrent methods (ReRoPE, LM-Infinite excluded)

## 8. Figures

- **Figure 1**: Comparison of Position Interpolation, NTK-aware, and YaRN interpolation strategies across RoPE dimensions.
- **Figure 2**: Perplexity curves across context lengths for YaRN vs baselines (PI, NTK, Code Llama).
- **Figure 3**: Passkey retrieval accuracy as a function of context length and passkey position.
- **Figure 4**: Wavelength analysis showing which RoPE dimensions benefit from interpolation vs preservation.

---

## References (Top 10)

1. Su et al. (2022) - RoFormer: Enhanced Transformer with Rotary Position Embedding
2. Chen et al. (2023) - Extending Context Window of Large Language Models via Positional Interpolation
3. Black et al. (2022) - GPT-NeoX-20B: An Open-Source Autoregressive Language Model
4. Touvron et al. (2023a) - LLaMA: Open and Efficient Foundation Language Models
5. Touvron et al. (2023b) - Llama 2: Open Foundation and Fine-Tuned Chat Models
6. Roziere et al. (2023) - Code Llama: Open Foundation Models for Code
7. Dao (2023) - FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning
8. Press et al. (2022) - Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation (ALiBi)
9. Tancik et al. (2020) - Fourier Features Let Networks Learn High Frequency Functions in Low Dimensional Domains
10. Chowdhery et al. (2022) - PaLM: Scaling Language Modeling with Pathways
