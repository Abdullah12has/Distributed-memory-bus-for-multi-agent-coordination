# Leave No Context Behind: Efficient Infinite Context Transformers with Infini-attention

**Authors:** Tsendsuren Munkhdalai, Manaal Faruqui, Siddharth Gopal (Google)

**Venue:** arXiv preprint (cs.CL), 2024

**arXiv:** [https://arxiv.org/abs/2404.07143](https://arxiv.org/abs/2404.07143)

---

## Abstract

This work introduces an efficient method to scale Transformer-based Large Language Models (LLMs) to infinitely long inputs with bounded memory and computation. A key component in the proposed approach is a new attention technique dubbed Infini-attention. Infini-attention incorporates a compressive memory into the vanilla attention mechanism and builds in both masked local attention and long-term linear attention mechanisms in a single Transformer block. The authors demonstrate the effectiveness of the approach by continual pre-training and fine-tuning on language modeling benchmarks, a 1M sequence length passkey context block retrieval task, and a 500K length book summarization task with 1B and 8B LLMs.

---

## 1. Introduction

Standard Transformer attention discards previous segment states, losing context beyond the local window. Approaches like Transformer-XL cache prior states but grow memory linearly with segments. Memorizing Transformers store entire KV states, which is expensive. Infini-attention addresses this by maintaining a fixed-size compressive memory that accumulates information from all prior segments.

## 2. Infini-attention Architecture

### 2.1 Scaled Dot-Product Attention (Local)

Within each segment of length N, standard causal dot-product attention is computed:
- Input projected into Q, K, V using trainable matrices
- Attention scores computed and weighted values aggregated
- This handles local context within the segment

### 2.2 Compressive Memory (Long-term)

The compressive memory reuses Q, K, V from standard attention:

**Memory Retrieval:**
```
A_mem = sigma(Q) * M_{s-1} / (sigma(Q) * z_{s-1})
```
where sigma is an activation function (ELU+1), M is the memory matrix, and z is the normalization term.

**Memory Update (two variants):**
- **Linear:** M_s = M_{s-1} + sigma(K)^T * V
- **Linear + Delta:** M_s = M_{s-1} + sigma(K)^T * (V - sigma(K)*M_{s-1}/sigma(K)*z_{s-1})

The Delta variant subtracts already-stored content before updating, reducing redundancy.

### 2.3 Gated Integration

A learned gating scalar beta combines local and memory outputs:
```
O = sigmoid(beta) * A_mem + (1 - sigmoid(beta)) * A_dot
```

This allows each attention head to specialize in local vs. long-range retrieval.

## 3. Comparison with Prior Work

| Model | Memory Size | Computation | Context |
|---|---|---|---|
| Transformer-XL | O(N * L) KV states | Grows with layers | Bounded |
| Memorizing Transformers | Stores all KV states | Expensive retrieval | Large but costly |
| Infini-Transformer | d_key x d_value + d_key per head | Constant | Unbounded |

Infini-attention achieves **114x compression ratio** in memory size compared to Memorizing Transformers while improving perplexity.

## 4. Experimental Results

### 4.1 Long-Context Language Modeling (1B parameters)

**PG19 Dataset (perplexity, lower is better):**

| Model | Perplexity |
|---|---|
| Transformer-XL | 11.88 |
| Memorizing Transformers | 11.37 |
| Infini-Transformer (Linear) | 9.65 |
| Infini-Transformer (Linear + Delta) | 9.67 |

**Arxiv-math Dataset:**

| Model | Perplexity |
|---|---|
| Transformer-XL | 2.42 |
| Memorizing Transformers | 2.26 |
| Infini-Transformer (Linear) | 2.24 |
| Infini-Transformer (Linear + Delta) | 2.23 |

Training on 100K length sequences further reduced perplexity to 2.20-2.21.

### 4.2 Passkey Retrieval (1M context)

A 1B model fine-tuned on only 5K length inputs achieved **near-perfect token-level retrieval accuracy** across 32K to 1M context lengths after just 400 fine-tuning steps. This demonstrates remarkable length generalization.

### 4.3 Book Summarization (500K length, 8B model)

| Variant | ROUGE-1 | ROUGE-2 | ROUGE-L |
|---|---|---|---|
| Linear | 37.9 | 8.7 | 17.6 |
| Linear + Delta | 40.0 | 8.8 | 17.9 |

Performance improved as additional book text was provided, indicating effective long-range dependency modeling.

## 5. Head Specialization Analysis

Analysis of gating scores (beta) revealed three types of attention heads:
- **Local-specialized heads:** beta near 0, focusing on local attention only
- **Memory-specialized heads:** beta near 1, focusing on long-term memory retrieval
- **Mixer heads:** beta near 0.5, aggregating both local and long-term information

Each layer contained at least one short-range head, ensuring signal propagation throughout the network.

## 6. Training Details

- Learning rate: 0.01 for language modeling, 0.0001 for continual pre-training
- Optimizer: Adafactor with linear warmup (1000 steps) and cosine decay
- Activation function: ELU + 1 for numerical stability
- Gradient checkpointing to reduce memory consumption

## 7. Practical Advantages

1. **Minimal architectural change:** Only one scalar parameter (beta) per attention head added
2. **Plug-and-play:** Supports continual pre-training and fine-tuning of existing LLMs
3. **Streaming inference:** Processes extremely long inputs without storing complete attention states
4. **Length extrapolation:** Models trained on 5K-32K sequences generalize to 1M+ contexts

## 8. Conclusion

Infini-attention demonstrates that compressive memory integration enables practical infinite-context processing. The approach reuses existing attention computation components, reducing implementation complexity while enabling efficient knowledge consolidation across arbitrarily long input sequences. Memory serves as a cornerstone of intelligence by allowing bounded-resource processing of unbounded inputs.

---

## Key Figures

- **Figure 1:** Infini-attention architecture diagram showing local dot-product attention, compressive memory, and gated combination.
- **Figure 2:** Passkey retrieval accuracy across context lengths from 32K to 1M.
- **Figure 3:** Gating score distributions showing head specialization patterns across layers.
- **Figure 4:** Book summarization ROUGE scores vs. input text length.

---

## Top References

1. Dai et al. (2019). Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context. ACL.
2. Wu et al. (2022). Memorizing Transformers. ICLR.
3. Vaswani et al. (2017). Attention Is All You Need. NeurIPS.
4. Katharopoulos et al. (2020). Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention. ICML.
5. Munkhdalai et al. (2019). Metalearned Neural Memory. NeurIPS.
6. Rae et al. (2020). Compressive Transformers for Long-Range Sequence Modelling. ICLR.
7. Press et al. (2022). ALiBi: Train Short, Test Long. ICLR.
8. Dao et al. (2022). FlashAttention. NeurIPS.
9. Choromanski et al. (2021). Rethinking Attention with Performers. ICLR.
10. Beltagy et al. (2020). Longformer: The Long-Document Transformer.
