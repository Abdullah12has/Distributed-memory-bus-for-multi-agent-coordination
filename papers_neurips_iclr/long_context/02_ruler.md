# RULER: What's the Real Context Size of Your Long-Context Language Models?

**Authors:** Cheng-Ping Hsieh, Simeng Sun, Samuel Kriman, Shantanu Acharya, Dima Rekesh, Fei Jia, Yang Zhang, Boris Ginsburg

**Venue:** COLM 2024

**ArXiv:** [2404.06654](https://arxiv.org/abs/2404.06654)

---

## Abstract

The needle-in-a-haystack (NIAH) test is a popular method for evaluating long-context language models. However, this simple retrieval-based test is insufficient for comprehensively evaluating the capabilities of long-context models. This paper introduces RULER, a synthetic benchmark with flexible configurations for evaluating long-context language models beyond simple retrieval. RULER expands the vanilla NIAH test to include diverse needle configurations and introduces new task categories: multi-key needle-in-a-haystack, multi-hop tracing, aggregation, and question answering with distractors. Despite achieving nearly perfect accuracy in the vanilla NIAH test, almost all models exhibit large performance drops as the context length increases on RULER tasks. The benchmark is open-sourced to support comprehensive assessment of long-context capabilities.

---

## 1. Introduction

Models claim support for 32K-200K+ token contexts, but claims are often validated only with the simple NIAH test. RULER provides a more comprehensive evaluation with diverse task types that stress-test different aspects of long-context processing.

## 2. Task Categories

### 2.1 Overview

| Category | Tasks | Purpose |
|----------|-------|---------|
| **Retrieval (NIAH)** | Single/Multi-key, Multi-value, Multi-query | Find specific information in long context |
| **Multi-hop Tracing (VT)** | Variable tracking with coreference chains | Track entity relationships across context |
| **Aggregation (CWE/FWE)** | Common/Frequent word extraction | Synthesize information across full context |
| **Question Answering** | QA with distractor documents | Real-world-like reasoning with noise |

### 2.2 NIAH Variants

- **Single NIAH**: Standard needle retrieval (baseline)
- **Multi-key NIAH**: Multiple needles with different keys
- **Multi-value NIAH**: Single key with multiple associated values
- **Multi-query NIAH**: Multiple queries requiring multiple retrievals

### 2.3 Variable Tracking (VT)

Traces variable assignments through coreference patterns across the context. Tests the ability to follow chains of references -- a proxy for multi-hop reasoning over long sequences.

### 2.4 Aggregation Tasks

- **Common Word Extraction (CWE)**: Find the most common word in a long sequence
- **Frequent Word Extraction (FWE)**: Find words appearing more than a threshold number of times
- These serve as proxies for summarization capability over long contexts

## 3. Evaluation Metrics

- **Effective Context Length**: Maximum length exceeding Llama2-7B baseline (85.6% at 4K)
- **Weighted Average Scores**: Two schemes simulating different real-world length distributions:
  - Increasing weights (more weight on longer contexts)
  - Decreasing weights (more weight on shorter contexts)

## 4. Main Results

### 4.1 Model Rankings (Weighted Average, Increasing Weights)

| Rank | Model | Score | Claimed Length | Effective Length |
|------|-------|-------|---------------|-----------------|
| 1 | GPT-4 | 89.0% | 128K | 64K |
| 2 | Command-R | 85.5% | 128K | 32K |
| 3 | Yi-34B | 84.8% | 200K | 32K |
| 4 | Mixtral | 72.8% | 32K | 32K |

**Critical finding**: Only 4 of 10 models maintain satisfactory performance at their claimed 32K+ lengths.

### 4.2 NIAH vs RULER Performance Gap

Despite near-perfect vanilla NIAH scores, all models show substantial degradation on RULER:
- Models scoring 95%+ on NIAH may score 60-70% on RULER tasks
- Aggregation and multi-hop tracing are the most challenging categories

## 5. Failure Modes Analysis (Yi-34B, 200K claimed)

| Failure Mode | Impact |
|-------------|--------|
| Non-robustness to key type (UUID vs word-number) | Significant drop |
| Distractor sensitivity | 40-point degradation |
| Incomplete multi-item retrieval | ~15-point drop |
| Context copying from demonstrations | 80%+ output copied at 128K |
| Unreliable multi-hop tracking | Poor beyond simple chains |
| Hallucination in QA | Parametric knowledge overrides context |

## 6. Key Findings

### 6.1 Training Context Length vs Performance

Larger training contexts generally improve performance, but ranking inconsistencies emerge at extrapolation lengths beyond training maximum.

### 6.2 Model Size Effect

Scaling matters significantly:
- Yi-34B substantially outperforms Yi-6B on both absolute performance and relative degradation rate

### 6.3 Architecture Comparison

Non-Transformer architectures (RWKV, Mamba) underperform Transformers substantially, with major degradation beyond 8K tokens.

## 7. Critical Insights

1. **Claimed vs. Effective**: Claims of 200K contexts are misleading when effective length is 32K or lower
2. **NIAH Insufficient**: Perfect vanilla NIAH scores do not predict performance on realistic complex tasks
3. **Emerging Problematic Behaviors**: Context length scaling triggers unhelpful strategies (copying, parametric knowledge reliance)
4. **Aggregation Challenges**: Tasks requiring synthesis across long spans remain fundamentally difficult

## 8. Reproducibility

- Benchmark open-sourced at: https://github.com/hsiehjackson/RULER
- 500 examples per task per context length
- vLLM inference framework with 8 A100 GPUs
- BFloat16 precision, greedy decoding

## 9. Figures

- **Figure 1**: Performance heatmap across all models and context lengths for each RULER task category.
- **Figure 2**: Comparison of vanilla NIAH scores vs RULER aggregate scores, showing the gap between simple and complex evaluation.
- **Figure 3**: Failure mode analysis for Yi-34B showing specific degradation patterns at long contexts.
- **Figure 4**: Architecture comparison (Transformer vs RWKV vs Mamba) across context lengths.

---

## References (Top 10)

1. Kamradt (2023) - Needle in a Haystack: Pressure Testing LLMs (original NIAH test)
2. Dao et al. (2022) - FlashAttention: Fast and Memory-Efficient Exact Attention
3. Liu et al. (2024) - World Model on Million-Length Video and Language with RingAttention
4. Xiong et al. (2023) - Effective Long-Context Scaling of Foundation Models (RoPE variants)
5. Mohtashami & Jaggi (2023) - Landmark Attention: Random-Access Infinite Context Length (passkey retrieval)
6. Chen et al. (2023) - Extending Context Window of Large Language Models via Positional Interpolation
7. Shaham et al. (2023) - ZeroSCROLLS: A Zero-Shot Benchmark for Long Text Understanding
8. Bai et al. (2023) - LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding
9. Zhang et al. (2024) - InfiniteBench: Extending Long Context Evaluation Beyond 100K Tokens
10. Gu & Dao (2023) - Mamba: Linear-Time Sequence Modeling with Selective State Spaces
