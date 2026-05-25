# LongRoPE: Extending LLM Context Window Beyond 2 Million Tokens

**Authors:** Yiran Ding, Li Lyna Zhang, Chengruidong Zhang, Yuanyuan Xu, Ning Shang, Jiahang Xu, Fan Yang, Mao Yang

**Venue:** arXiv preprint (cs.CL), 2024

**ArXiv:** [2402.13753](https://arxiv.org/abs/2402.13753)

---

## Abstract

This paper presents LongRoPE, a method that extends the context window of pre-trained LLMs to an impressive 2,048k tokens, with up to only 1k fine-tuning steps at 256k length. The approach identifies and exploits two forms of non-uniformities in positional interpolation: varying optimal rescale factors across different RoPE dimensions, and varying optimal factors for token positions. Using an efficient evolutionary search algorithm, LongRoPE discovers non-uniform interpolation schemes. A progressive extension strategy first fine-tunes to 256k then extends to 2048k via a second search. Additionally, the method readjusts on shorter contexts to recover performance within the original window size.

---

## 1. Introduction

Extending context windows beyond 100K tokens remains challenging due to the sensitivity of positional embeddings. LongRoPE identifies that uniform interpolation schemes are suboptimal and proposes a search-based approach to find dimension-specific and position-specific scaling factors.

## 2. Key Innovations

### 2.1 Non-Uniform Positional Interpolation

Two critical forms of non-uniformity identified:

1. **Dimension Non-Uniformity**: Different RoPE dimensions require different interpolation levels. Lower dimensions and initial token positions benefit from less interpolation, but optimal solutions depend on the target extended length.

2. **Position Non-Uniformity**: Initial tokens in sequences should use minimal interpolation due to their high attention weights (attention sinks), making them crucial to model performance.

## 3. Methodology

### 3.1 Problem Formulation

The optimization seeks rescale factors lambda_i (per dimension) and position threshold n_hat that minimize language modeling loss across extended contexts.

### 3.2 Evolutionary Search Algorithm

To navigate the exponentially large search space:
- Optimized initial population using PI, NTK, and YaRN baselines
- Monotonically non-decreasing constraint (lambda_i <= lambda_{i+1}) to reduce invalid candidates
- Mutation and crossover operations guided by perplexity evaluation
- Population size: 64 candidates per generation

### 3.3 Progressive Extension Strategy

Rather than direct training to 2048k:

| Step | Action | Result |
|------|--------|--------|
| 1 | Search + fine-tune | 256k context (64x extension) |
| 2 | Secondary search on fine-tuned model | 2048k context (8x additional) |
| 3 | Readjust factors for short context | Recovery of 4k-8k performance |

### 3.4 Short Context Recovery

After aggressive extension (512x), performance on short contexts degrades. A readjustment step searches for modified factors specifically for 4k-8k lengths, recovering original-window performance.

## 4. Experimental Results

### 4.1 Long-Context Language Modeling (Proof-pile)

- Maintains decreasing perplexity from 4k to 256k evaluation lengths
- LongRoPE-2048k significantly outperforms baselines like YaRN within 256k context
- LLaMA2-7B achieves comparable or superior perplexity to state-of-the-art methods

### 4.2 Passkey Retrieval (Million-Token Scale)

| Model | Max Accurate Length | Notes |
|-------|-------------------|-------|
| LongRoPE-LLaMA2 | 2048k | >=90% accuracy throughout |
| LongRoPE-Mistral | 1800k | 100% accuracy up to 1800k |
| Existing methods | 128k | Accuracy drops to 0% beyond |

### 4.3 Standard Benchmarks

| Benchmark | LongRoPE-Mistral | Original Mistral |
|-----------|------------------|-----------------|
| ARC-Challenge | Comparable | Baseline |
| HellaSwag | Comparable | Baseline |
| MMLU | Comparable | Baseline |
| TruthfulQA | +0.5% | Baseline |

Comparable results despite 512x context extension.

## 5. Ablation Studies

1. **Non-uniformity contributions**: RoPE dimension-specific factors provide substantial gains; position-specific factors improve shorter extensions significantly
2. **Secondary interpolation**: Second search on fine-tuned models maintains consistent low perplexity across 512k-2048k extensions
3. **Short-context recovery**: Readjustment recovers performance drops from aggressive 512x extension

## 6. Implementation Details

### 6.1 Fine-tuning Requirements

| Configuration | Steps | Hardware | Time |
|--------------|-------|----------|------|
| LLaMA2-128k | 400 | 8 A100 GPUs | ~1 week |
| LLaMA2-256k | 600 | 16 A100 GPUs | ~2 weeks |
| Mistral | - | 4 GPUs | 2 days |

### 6.2 Search Costs

| Target Length | Time | Hardware |
|--------------|------|----------|
| Up to 256k | 3 days | Single A100 |
| 2048k | 5 days | 4-8 A100s |

## 7. Comparison with Related Approaches

| Method | Mechanism | Typical Extension | Limitation |
|--------|-----------|-------------------|------------|
| **PI** (Position Interpolation) | Linear rescaling all dimensions | 4-8x | Information crowding |
| **NTK-based** | Per-dimension hand-crafted rules | 4x without fine-tuning | Limited extension ratio |
| **YaRN** | Grouped dimension interpolation | 32x | Suboptimal at high ratios |
| **LongRoPE** | Searched per-dimension + per-position | 512x | Search cost |

## 8. Limitations

- Position-specific non-uniformity shows diminishing returns at extremely long lengths (2048k)
- Mistral performs better with shorter fine-tuning sequences (16k) than LLaMA2, suggesting model-specific optimization remains important
- Evolutionary search has non-trivial computational cost

## 9. Figures

- **Figure 1**: Visualization of non-uniform interpolation factors across RoPE dimensions, showing the dimension-dependent scaling discovered by evolutionary search.
- **Figure 2**: Progressive extension strategy diagram showing the three-step process (256k fine-tune, 2048k search, short-context recovery).
- **Figure 3**: Passkey retrieval accuracy curves comparing LongRoPE with baselines across context lengths up to 2048k.
- **Figure 4**: Perplexity curves on Proof-pile comparing LongRoPE with PI, NTK, and YaRN methods.

---

## References (Top 10)

1. Su et al. (2021) - RoFormer: Enhanced Transformer with Rotary Position Embedding
2. Chen et al. (2023a) - Extending Context Window of Large Language Models via Positional Interpolation
3. Peng et al. (2023) - YaRN: Efficient Context Window Extension of Large Language Models
4. Touvron et al. (2023) - Llama 2: Open Foundation and Fine-Tuned Chat Models
5. LocalLLaMA (2023b) - NTK-Aware Scaled RoPE
6. Chen et al. (2023b) - LongLoRA: Efficient Long-Context Fine-Tuning of Large Language Models
7. Jacot et al. (2018) - Neural Tangent Kernels: Convergence and Generalization in Neural Networks
8. Tancik et al. (2020) - Fourier Features Let Networks Learn High Frequency Functions
9. Xiao et al. (2023) - Efficient Streaming Language Models with Attention Sinks
10. Jiang et al. (2023) - Mistral 7B
