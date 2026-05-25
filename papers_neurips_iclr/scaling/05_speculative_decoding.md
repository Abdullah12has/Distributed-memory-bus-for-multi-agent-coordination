# Accelerating Large Language Model Decoding with Speculative Sampling

**Authors:** Charlie Chen, Sebastian Borgeaud, Geoffrey Irving, Jean-Baptiste Lespiau, Laurent Sifre, John Jumper

**Venue:** arXiv preprint, 2023 (DeepMind)

**arXiv:** [2302.01318](https://arxiv.org/abs/2302.01318)

---

## Abstract

The researchers present an algorithm enabling transformer models to generate multiple tokens per inference call. Their approach uses a faster but less powerful draft model to create short text continuations, which are then scored in parallel. They employ a novel modified rejection sampling scheme to maintain the target model's output distribution. Testing with Chinchilla (70B parameters) demonstrated a 2--2.5x decoding speedup without modifying the model or compromising sample quality.

---

## 1. Introduction

The method generates multiple tokens per transformer call by exploiting the observation that the latency of parallel scoring of short continuations is comparable to that of sampling a single token from the larger target model, due to memory bandwidth bottlenecks dominating computation time.

---

## 2. Core Algorithm

### Three Steps

1. **Draft Generation:** A smaller, faster draft model generates K tokens autoregressively
2. **Parallel Scoring:** The large target model scores all K draft tokens in parallel
3. **Modified Rejection Sampling:** Accepts draft tokens left-to-right using a novel sampling scheme that preserves the target model's distribution

---

## 3. Technical Details

### Conditional Scoring

Three components dominate sampling latency in sharded transformers:

| Component | Behavior |
|-----------|----------|
| Linear Layers | Memory bound; similar time for small K |
| Attention Mechanism | KV-cache size constant; minimal delta with K increase |
| All-reduces | Latency bound; unchanged for small K |

### Modified Rejection Sampling

Accept draft token x with probability: min(1, q(x)/p(x))

If rejected, resample from the normalized positive difference: (q(x) - p(x))_+

**Theorem 1:** This scheme recovers the target distribution exactly (within hardware numerics).

---

## 4. Results

### Benchmark Performance

| Task | Method | Metric | Speed | Speedup |
|------|--------|--------|-------|---------|
| XSum (ROUGE-2) | ArS Nucleus | 0.112 | 14.1ms/token | 1x |
| XSum | SpS Nucleus | 0.114 | 7.52ms/token | 1.92x |
| XSum (Greedy) | ArS | 0.157 | 14.1ms/token | 1x |
| XSum | SpS Greedy | 0.156 | 7.00ms/token | 2.01x |
| HumanEval (100-shot) | ArS Nucleus | 45.1% | 14.1ms/token | 1x |
| HumanEval | SpS Nucleus | 47.0% | 5.73ms/token | 2.46x |

Performance metrics show parity with baseline, confirming distribution preservation.

### Draft Model Specifications

| Model | d_model | Heads | Layers | Parameters |
|-------|---------|-------|--------|------------|
| Target (Chinchilla) | 8192 | 64 | 80 | 70B |
| Draft | 6144 | 48 | 8 | 4B |

Draft model: 1.8ms/token vs. Chinchilla's 14.1ms/token sampling latency.

### Lookahead Parameter Analysis

- As K increases, speedup plateaus or degrades
- XSum optimal at K=3 (not K=4)
- Acceptance rate efficiency decreases with K
- Higher K increases latency variance (problematic for P90/P99 SLAs)

---

## 5. Draft Model Selection

The paper evaluates multiple approaches:

1. **Multi-head integration** (Stern et al., 2018): Requires model retraining
2. **Sequence-level distillation** (Ge et al., 2022): High compute cost
3. **Smaller model variant** (chosen approach): Practical, leverages existing infrastructure

**Distributed serving challenge:** Optimal hardware topology differs between 70B and 7B models. Solution: Train wider, shallower draft (6144 dim, 8 layers) for same-device deployment.

---

## 6. Key Methodological Insights

- Strong draft-target agreement on obvious continuations enables multi-token acceptance
- **No target model modification** required
- **Distribution-preserving** within numerics
- **Compatible** with nucleus sampling, top-k, temperature adjustment
- **Composable** with quantization, multi-query attention

---

## 7. Practical Implications

- Exceeds memory bandwidth ceiling for autoregressive sampling in certain domains
- Domain-dependent acceptance rates (higher for code due to common patterns)
- Trade-off between speedup and latency variance with increasing K
- Applicable to production serving scenarios requiring sub-20ms latencies

---

## 8. Figure Descriptions

- **Figure 1:** Overview of the speculative sampling algorithm showing draft, score, and accept/reject steps
- **Figure 2:** Speedup vs. lookahead parameter K across different tasks
- **Figure 3:** Acceptance rate distributions for different domains

---

## Key References

1. Hoffmann et al. (2022) --- Chinchilla training/compute-optimal models
2. Brown et al. (2020) --- GPT-3 and few-shot learning
3. Shazeer (2019) --- Memory bandwidth bottleneck analysis
4. Stern et al. (2018) --- Block-wise parallel decoding
5. Ge et al. (2022) --- Aggressive decoding
6. Pope et al. (2022) --- PaLM 540B serving optimization
7. Chowdhery et al. (2022) --- PaLM model scaling
8. Shoeybi et al. (2019) --- Megatron-LM parallelism
9. Dettmers et al. (2022) --- 8-bit quantization
10. Leviathan et al. (2022) --- Concurrent speculative decoding work
