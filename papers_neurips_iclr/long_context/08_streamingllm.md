# Efficient Streaming Language Models with Attention Sinks

**Authors:** Guangxuan Xiao, Yuandong Tian, Beidi Chen, Song Han, Mike Lewis

**Venue:** ICLR 2024

**arXiv:** [https://arxiv.org/abs/2309.17453](https://arxiv.org/abs/2309.17453)

---

## Abstract

Deploying Large Language Models (LLMs) in streaming applications -- such as multi-round dialogue -- poses significant challenges due to extensive memory consumption from caching key-value (KV) states and inability to generalize to longer sequences than trained on. Window attention, while reducing memory, fails when initial tokens are evicted. The authors identify that keeping the KV of initial tokens will largely recover the performance of window attention, a phenomenon they term "attention sinks." They propose StreamingLLM, a framework enabling LLMs trained with finite-length attention to generalize to infinite sequence lengths without any fine-tuning. StreamingLLM achieves stable and efficient performance with up to 22.2x speedup over sliding window recomputation.

---

## 1. Introduction

LLMs face two deployment challenges for streaming applications:
1. **Memory:** KV cache grows linearly with sequence length, becoming prohibitive
2. **Generalization:** Models cannot reliably process sequences longer than their training length

Existing solutions (sliding window, recurrence) either fail catastrophically or require architectural changes. StreamingLLM provides a simple, training-free solution.

## 2. Key Discovery: Attention Sinks

### 2.1 The Phenomenon

Models allocate disproportionately high attention scores to initial tokens regardless of their semantic relevance. This occurs because:
- Softmax requires attention scores to sum to 1
- When queries lack strong matches, models "dump" excess attention on readily available initial tokens
- Initial tokens are visible to all subsequent tokens during autoregressive training

### 2.2 Why Window Attention Fails

When the sliding window evicts initial tokens, the attention distribution collapses. Without these "sink" tokens to absorb excess attention mass, the softmax normalization produces erratic distributions, causing perplexity to explode.

### 2.3 Universality

The attention sink phenomenon appears across diverse architectures:
- Decoder-only: Llama-2, MPT, Falcon, Pythia
- Encoder models: BERT
- Vision transformers
This suggests it is a fundamental property of how softmax attention allocates resources.

## 3. StreamingLLM Framework

### 3.1 Core Idea

Maintain a small set of initial tokens (attention sinks) plus a rolling window of recent tokens in the KV cache:

```
Cache = [sink tokens (4)] + [recent window tokens]
```

With just 4 initial tokens as anchors plus recent context, models can process texts of arbitrary length.

### 3.2 Cache Management

At each step:
1. Keep the first 4 token KV states permanently
2. Maintain a rolling window of the most recent tokens
3. Evict tokens between sinks and the window boundary

### 3.3 Pre-Training Enhancement: Learnable Sink Token

Adding a dedicated learnable sink token (`[SINK]`) during pre-training consolidates all attention sinking behavior into a single token:
- Eliminates need for multiple initial tokens
- Maintains performance on standard benchmarks
- Achieves superior streaming stability

## 4. Experimental Results

### 4.1 Perplexity Stability

Tested across Llama-2 (7B, 13B, 70B), MPT (7B, 30B), Falcon (7B, 40B), and Pythia (6.9B, 12B):
- **Dense attention:** Fails beyond training length
- **Window attention:** Perplexity spikes immediately when initial tokens evicted
- **StreamingLLM:** Stable perplexity maintained up to **4 million tokens**

### 4.2 Performance Comparison

| Method | Memory | Speed | Quality |
|---|---|---|---|
| Dense (full recompute) | O(L) | 1x | Best within training length |
| Sliding window recompute | O(L) | 1x | Good but slow |
| StreamingLLM | O(W+S) | Up to 22.2x | Comparable to window |

W = window size, S = number of sink tokens, L = full sequence length.

### 4.3 Streaming QA

On streaming question-answering tasks, StreamingLLM achieves comparable accuracy to sample-by-sample baselines while maintaining efficiency. Performance degrades for questions requiring information beyond the cache window boundary.

### 4.4 Number of Sink Tokens

Ablation studies show that 4 sink tokens are sufficient for stable performance. Using fewer (1-2) still works but is slightly less stable. Using more provides no additional benefit.

## 5. Analysis

### 5.1 Attention Sink vs. Semantic Importance

The initial tokens receiving high attention are not semantically important -- they serve purely as numerical anchors for the softmax distribution. Replacing them with random tokens and maintaining their position yields similar results.

### 5.2 Relationship to Positional Encoding

StreamingLLM is compatible with both absolute and relative positional encodings. For relative encodings (RoPE, ALiBi), position IDs must be adjusted to reflect the actual cache positions rather than absolute sequence positions.

## 6. Limitations

- StreamingLLM cannot extend the effective context window -- it only stabilizes the model for streaming use
- Information beyond the cache boundary is inaccessible
- Not a replacement for methods that genuinely extend context understanding

## 7. Related Work

- **Efficient attention:** Sparse attention, linear attention, FlashAttention
- **Context extension:** Position interpolation, YaRN, LongLoRA
- **KV cache compression:** Token dropping, quantization, eviction policies

StreamingLLM is orthogonal to context extension methods and can be combined with them.

## 8. Conclusion

StreamingLLM demonstrates that a simple modification -- preserving a few initial "attention sink" tokens -- enables stable streaming inference for LLMs of arbitrary length. The discovery of attention sinks reveals fundamental properties of how Transformers allocate attention under softmax constraints.

---

## Key Figures

- **Figure 1:** Attention maps showing disproportionate attention to initial tokens across layers.
- **Figure 2:** Perplexity curves comparing dense, window, and StreamingLLM approaches over 4M tokens.
- **Figure 3:** Visualization of attention sink consolidation with the learnable sink token.
- **Figure 4:** Ablation on number of sink tokens showing 4 is sufficient.

---

## Top References

1. Vaswani et al. (2017). Attention Is All You Need. NeurIPS.
2. Touvron et al. (2023). LLaMA 2: Open Foundation and Fine-Tuned Chat Models.
3. Dao et al. (2022). FlashAttention: Fast and Memory-Efficient Exact Attention. NeurIPS.
4. Press et al. (2022). ALiBi: Train Short, Test Long. ICLR.
5. Su et al. (2021). RoFormer: Enhanced Transformer with Rotary Position Embedding.
6. Child et al. (2019). Generating Long Sequences with Sparse Transformers.
7. Dai et al. (2019). Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context. ACL.
8. Chen et al. (2023). Extending Context Window of Large Language Models via Positional Interpolation.
9. Beltagy et al. (2020). Longformer: The Long-Document Transformer.
10. Zhang et al. (2023). H2O: Heavy-Hitter Oracle for Efficient Generative Inference.
