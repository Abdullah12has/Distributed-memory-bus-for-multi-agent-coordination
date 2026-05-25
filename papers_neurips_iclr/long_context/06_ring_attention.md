# Ring Attention with Blockwise Transformers for Near-Infinite Context

**Authors:** Hao Liu, Matei Zaharia, Pieter Abbeel

**Venue:** arXiv preprint (cs.CL), 2023

**arXiv:** [https://arxiv.org/abs/2310.01889](https://arxiv.org/abs/2310.01889)

**Code:** [https://github.com/lhao499/llm_large_context](https://github.com/lhao499/llm_large_context)

---

## Abstract

Transformers have limitations in handling long sequences due to memory constraints of individual devices. The authors introduce Ring Attention, which leverages blockwise computation of self-attention and feedforward to distribute long sequences across multiple devices while overlapping communication with computation. This approach enables training and inference on sequences significantly longer than prior methods, supporting millions of tokens of context size without approximations or additional overhead beyond the standard Transformer.

---

## 1. Introduction

Transformers process all tokens simultaneously via self-attention, but this creates a fundamental memory bottleneck: the KV cache and attention matrix grow quadratically with sequence length. Prior approaches either approximate attention (sparse patterns, linear attention) or limit context windows. Ring Attention addresses this by distributing the sequence across devices in a ring topology, achieving near-linear scaling of context length with device count.

## 2. Method: Ring Attention

### 2.1 Blockwise Computation

The key insight is that self-attention and feedforward computations can be decomposed into independent blocks. Each device holds one block of queries and iteratively processes blocks of keys and values.

### 2.2 Ring Topology

Devices are arranged in a ring. At each step:
1. Each host maintains one query block locally
2. Key-value blocks are sent to the next device in the ring
3. Key-value blocks are received from the previous device
4. Blockwise attention and feedforward operations are computed concurrently with communication

### 2.3 Overlapping Communication and Computation

The critical property: when the computation time for a block exceeds the transfer time, communication is fully overlapped, yielding zero communication overhead. The minimum block size required is F/B (device FLOPS / interconnect bandwidth), typically 1-24K tokens.

### 2.4 Memory Efficiency

Ring Attention reduces memory requirements to **6bch bytes per layer** (b=batch size, c=block size, h=hidden size), independent of total sequence length. This contrasts with vanilla Transformers requiring O(s^2) memory where s is sequence length.

## 3. Implementation

The implementation uses JAX with `jax.lax.ppermute` for collective operations managing key-value block circulation. It is compatible with existing memory-efficient Transformer implementations including FlashAttention.

## 4. Experimental Results

### 4.1 Maximum Context Lengths

| Configuration | Context Length | Improvement |
|---|---|---|
| 8 A100 GPUs (7B model) | 256K tokens | 8x |
| 32 A100 GPUs (7B model) | 4M tokens | 32x |
| TPUv4-1024 (7B model) | 8.2M tokens | 512x |

### 4.2 Model FLOPs Utilization

Maintains competitive MFU while enabling training with 32-2048x longer contexts across various model sizes.

### 4.3 Applications

- **In-context reinforcement learning:** Evaluated on ExoRL benchmark, demonstrating that longer context enables better in-context policy learning
- **Language model finetuning:** Successfully finetuned LLaMA-13B with 512K context
- **Line retrieval tasks:** Maintained accuracy at extended context lengths, validating that the model attends to distant positions

## 5. Analysis

### 5.1 Scaling Properties

Context length scales linearly with the number of devices. Adding more devices directly translates to proportionally longer sequences without degradation.

### 5.2 Minimal Requirements

The minimum viable block size depends on the FLOPS-to-bandwidth ratio of the hardware. For TPUv4 with ICI interconnect, blocks as small as 1K tokens suffice; for GPU clusters with slower interconnects, 16-24K tokens may be needed.

## 6. Related Work

The paper relates to several lines of work:
- Memory-efficient attention (FlashAttention, blockwise parallel Transformers)
- Sequence parallelism (Megatron-LM, DeepSpeed)
- Long-context methods (ALiBi, RoPE, sparse attention)

Ring Attention differs by providing exact attention (no approximation) with communication overhead that can be fully hidden.

## 7. Conclusion

Ring Attention enables context lengths scaling linearly with device count, eliminating individual device memory bottlenecks. The approach supports sequences exceeding millions of tokens without approximating attention mechanisms, opening possibilities for video-language models, extended feedback learning, and complex reasoning tasks.

---

## Key Figures

- **Figure 1:** Ring topology illustration showing how query blocks remain local while KV blocks circulate around the ring, with computation and communication overlapping at each step.
- **Figure 2:** Scaling curves showing context length vs. number of devices for different model sizes.
- **Figure 3:** In-context RL results on ExoRL, demonstrating improvement with longer context.

---

## Top References

1. Dao et al. (2022). FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness. NeurIPS.
2. Liu et al. (2023). Blockwise Parallel Transformer for Large Context Models. NeurIPS.
3. Touvron et al. (2023). LLaMA: Open and Efficient Foundation Language Models.
4. Brown et al. (2020). Language Models are Few-Shot Learners. NeurIPS.
5. Vaswani et al. (2017). Attention Is All You Need. NeurIPS.
6. Shoeybi et al. (2019). Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism.
7. Rasley et al. (2020). DeepSpeed: System Optimizations Enable Training Deep Learning Models with Over 100 Billion Parameters.
8. Su et al. (2021). RoFormer: Enhanced Transformer with Rotary Position Embedding.
9. Press et al. (2022). ALiBi: Train Short, Test Long. ICLR.
10. Child et al. (2019). Generating Long Sequences with Sparse Transformers.
