# FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning

**Author:** Tri Dao

**Venue:** arXiv preprint, 2023

**arXiv:** [2307.08691](https://arxiv.org/abs/2307.08691)

---

## Abstract

The paper addresses the quadratic runtime and memory scaling of attention layers in Transformers for longer sequences. While the original FlashAttention achieved significant speedups, it operated at only 25--40% of theoretical GPU efficiency. FlashAttention-2 improves this through three key optimizations: reducing non-matmul FLOPs, parallelizing attention computation across thread blocks even for single heads, and distributing work between warps to minimize shared memory communication. These enhancements deliver approximately 2x speedup over FlashAttention, reaching 50--73% theoretical efficiency on A100 GPUs and achieving up to 225 TFLOPs/s during GPT-style model training.

---

## 1. Introduction

FlashAttention-2 is an optimized GPU implementation of the attention mechanism that achieves approximately 2x speedup over the original FlashAttention while reaching 50--73% of theoretical maximum FLOPs/s on A100 GPUs, compared to FlashAttention's 25--40%.

---

## 2. Key Contributions

### Algorithm Optimization

Reduces non-matmul FLOPs by maintaining unscaled output versions and using logsumexp for backward pass calculations instead of separate max and sum values.

### Enhanced Parallelism

Extends parallelization from batch and head dimensions to include the sequence length dimension, improving GPU occupancy for long sequences with small batch sizes.

### Improved Work Partitioning

Restructures intra-block warp distribution to eliminate the "split-K" scheme, reducing shared memory reads/writes.

---

## 3. Technical Details

### Forward Pass Algorithm

The method employs online softmax with tiling:
- Divides inputs into blocks sized Br x Bc
- Maintains running statistics (max and sum of exponentials)
- Stores logsumexp L = m + log(l) instead of separate values
- Processes query blocks in outer loop, key/value blocks in inner loop

### Hardware Utilization

Modern GPUs feature specialized tensor cores with dramatically different throughputs: each non-matmul FLOP is 16x more expensive than a matmul FLOP on A100 hardware. This motivated algorithmic choices emphasizing matrix multiplication over element-wise operations.

### Backward Pass

Uses recomputation to avoid materializing large intermediate matrices while computing gradients for Q, K, and V tensors. Incorporates atomic operations for gradient accumulation across thread blocks.

---

## 4. Results

| Model | Without FA | FlashAttention | FlashAttention-2 |
|-------|-----------|-----------------|------------------|
| GPT3-1.3B 2k | 142 TFLOPs/s | 189 TFLOPs/s | 196 TFLOPs/s |
| GPT3-1.3B 8k | 72 TFLOPs/s | 170 TFLOPs/s | 220 TFLOPs/s |
| GPT3-2.7B 2k | 149 TFLOPs/s | 189 TFLOPs/s | 205 TFLOPs/s |
| GPT3-2.7B 8k | 80 TFLOPs/s | 175 TFLOPs/s | 225 TFLOPs/s |

Peak performance reaches 225 TFLOPs/s per A100 GPU (72% model FLOPs utilization) during end-to-end GPT training.

---

## 5. Key Features

**Causal Masking:** Leverages block structure to skip approximately half the computations in autoregressive settings, yielding 1.7--1.8x speedup.

**Multi-Query and Grouped-Query Attention:** Supports variants where multiple query heads share key/value heads through implicit index manipulation.

**Hardware Compatibility:** Demonstrates 335 TFLOPs/s on H100 GPUs without optimizations leveraging new hardware features.

---

## 6. Figure Descriptions

- **Figure 1:** Block-sparse attention pattern showing how causal masking enables skipping computation blocks
- **Figure 2:** Warp partitioning comparison between FlashAttention and FlashAttention-2
- **Figure 3:** End-to-end training throughput comparison across model sizes and sequence lengths
- **Figure 4:** Scaling of attention throughput with sequence length on A100 and H100 GPUs

---

## 7. Future Directions

- Extend support to H100 GPUs using TMA and 4th-generation Tensor Cores
- Explore FP8 precision
- Combine with algorithmic variants (sparse, local, dilated attention)
- Collaborate with compiler researchers on programmable optimization techniques

---

## Key References

1. Dao et al. (2022) --- FlashAttention: Fast and memory-efficient exact attention
2. Vaswani et al. (2017) --- Attention is All You Need (Transformer architecture)
3. OpenAI (2023) --- GPT-4 Technical Report
4. Shoeybi et al. (2019) --- Megatron-LM training framework
5. Tillet et al. (2019) --- Triton compiler for neural networks
6. Shazeer (2019) --- Multi-query attention architecture
7. Ainslie et al. (2023) --- Grouped-query attention (GQA)
8. Milakov and Gimelshein (2018) --- Online softmax normalization
9. Jia and Van Sandt (2021) --- Ampere GPU architecture analysis
10. Rabe and Staats (2021) --- O(N) memory attention mechanisms
