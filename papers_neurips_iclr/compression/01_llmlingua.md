# LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models

**Authors:** Huiqiang Jiang, Qianhui Wu, Chin-Yew Lin, Yuqing Yang, Lili Qiu

**Venue:** EMNLP 2023

**arXiv:** [2310.05736](https://arxiv.org/abs/2310.05736)

---

## Abstract

Large language models (LLMs) have been applied in various applications where they process lengthy prompts for tasks such as chain-of-thought reasoning, in-context learning, and document retrieval. However, these long prompts incur significant computational costs. LLMLingua introduces a coarse-to-fine prompt compression method that includes a budget controller to maintain semantic integrity under high compression ratios, a token-level iterative compression algorithm, and instruction tuning for distribution alignment between the small compression model and the target LLM. Testing across four datasets (GSM8K, BBH, ShareGPT, and Arxiv-March23) demonstrates that LLMLingua achieves state-of-the-art performance with up to 20x compression with little performance loss.

---

## 1. Introduction

Modern LLM applications rely on increasingly lengthy prompts -- chain-of-thought demonstrations, retrieved documents, and multi-turn conversation histories -- that demand substantial computational resources. The cost of processing these prompts scales with token count, creating practical limits on what can be achieved with context-window-limited models. LLMLingua addresses the challenge of balancing compression aggressiveness with semantic preservation when prompts exceed tens of thousands of tokens.

The key insight is that prompts contain significant redundancy that can be exploited by a smaller language model to identify and remove less informative tokens, while preserving the essential information needed by the target LLM.

---

## 2. Problem Formulation

The prompt compression problem is formulated as minimizing the KL divergence between the target LLM's output distribution when given the compressed prompt versus the original prompt:

$$\min \text{KL}(P(\tilde{x}_G | \tilde{x}), P(x_G | x))$$

where $x$ is the original prompt, $\tilde{x}$ is the compressed prompt, and $x_G$ is the generated output.

A prompt is decomposed into three components:
- **Instructions** ($x^{ins}$): task descriptions
- **Demonstrations** ($x^{dems}$): in-context examples
- **Question** ($x^{que}$): the actual query

---

## 3. Methodology: Three-Component Framework

### 3.1 Budget Controller

The budget controller dynamically allocates different compression ratios to prompt components based on their importance:

- **Instructions and Questions**: Lower compression (higher retention), with $\tau_{ins} = 0.85$, $\tau_{que} = 0.9$
- **Demonstrations**: Higher compression, selected by perplexity ranking
- **Demonstration-level filtering**: Entire demonstrations are ranked by perplexity and the least informative ones are dropped first, preserving linguistic integrity at high compression ratios

The budget controller ensures that semantically critical components (instructions, questions) retain more tokens than demonstrations, which contain redundant exemplar information.

### 3.2 Iterative Token-level Prompt Compression (ITPC)

Prior work (Selective Context) assumes token independence when computing information content. LLMLingua addresses this limitation through iterative compression:

1. Divide the prompt into segments
2. Iteratively compute conditional probabilities incorporating previously compressed segments:

$$p(\tilde{s}_j) = \prod p(\tilde{s}_{j,i} | \tilde{s}_{j,<i}, \tilde{s}_{<j})$$

3. Dynamically set compression thresholds $\gamma_j$ based on perplexity distributions of each segment
4. Retain tokens with perplexity $> \gamma_j$

This iterative approach captures inter-segment dependencies that single-pass methods miss.

### 3.3 Distribution Alignment

To bridge the gap between the small compression model (e.g., LLaMA-7B) and black-box target LLMs (e.g., GPT-3.5/4), LLMLingua uses instruction tuning on LLM-generated outputs from the Alpaca dataset. This aligns the small model's token importance estimates with the target LLM's actual information needs.

---

## 4. Experimental Setup

### Datasets
- **GSM8K**: Grade school math reasoning (8-shot CoT)
- **BBH (Big-Bench Hard)**: 27 challenging reasoning tasks (3-shot CoT)
- **ShareGPT**: Multi-turn conversation data
- **Arxiv-March23**: Academic paper summarization

### Baselines
- Selective Context (Li, 2023)
- Sentence-level selection
- GPT-4 generation-based compression

### Small Language Models
- **Alpaca-7B** (primary): LLaMA-7B instruction-tuned
- **GPT2-Alpaca**: GPT-2 with Alpaca fine-tuning (ablation)

---

## 5. Results

### 5.1 GSM8K (Math Reasoning)

| Constraint | Method | EM (%) | Tokens | Ratio |
|---|---|---|---|---|
| Full-shot | Original | 78.85 | 2,366 | -- |
| 1-shot (5x) | Selective-Context | 53.98 | 452 | 5x |
| 1-shot (5x) | **LLMLingua** | **79.08** | 446 | 5x |
| half-shot (14x) | Selective-Context | 52.99 | 218 | 11x |
| half-shot (14x) | **LLMLingua** | **77.41** | 171 | 14x |
| quarter-shot (20x) | Selective-Context | 44.20 | 157 | 15x |
| quarter-shot (20x) | **LLMLingua** | **77.33** | 117 | 20x |

LLMLingua at 5x compression (79.08%) slightly exceeds full-shot performance (78.85%). At 20x compression, it outperforms Selective-Context by 33.10 points.

### 5.2 BBH (Reasoning Tasks)

| Constraint | Method | EM (%) | Tokens | Ratio |
|---|---|---|---|---|
| Full-shot | Original | 70.07 | 774 | -- |
| 1-shot (3x) | Selective-Context | 54.27 | 276 | 3x |
| 1-shot (3x) | **LLMLingua** | **70.11** | 288 | 3x |
| half-shot (5x) | Selective-Context | 54.02 | 155 | 5x |
| half-shot (5x) | **LLMLingua** | **61.60** | 171 | 5x |
| quarter-shot (7x) | Selective-Context | 47.37 | 108 | 7x |
| quarter-shot (7x) | **LLMLingua** | **56.85** | 110 | 7x |

### 5.3 ShareGPT and Arxiv-March23

| Methods | ShareGPT BLEU (1.9x) | Arxiv BLEU (4x) | ShareGPT BLEU (3.3x) | Arxiv BLEU (9x) |
|---|---|---|---|---|
| Sentence Selection | 28.59 | 22.77 | 18.94 | 12.41 |
| Selective-Context | 25.42 | 21.41 | 15.79 | 12.23 |
| **LLMLingua** | **27.36** | **23.15** | **19.55** | **13.45** |

BERTScore F1 remains at 89-90% even at 3.3-4x compression.

### 5.4 Ablation Study (GSM8K, 1-shot)

| Variant | EM (%) | Tokens | Ratio |
|---|---|---|---|
| LLMLingua (full) | 79.08 | 439 | 5x |
| w/o Iterative Token Compression | 72.93 | 453 | 5x |
| w/o Budget Controller | 73.62 | 486 | 5x |
| w/o Dynamic Compression Ratio | 77.26 | 457 | 5x |
| w/ Random Selection | 72.78 | 477 | 5x |
| w/o Distribution Alignment | 78.62 | 452 | 5x |
| w/ Remove Stop Words | 76.27 | 1,882 | 1.3x |

The iterative token compression component contributes the most (6.15 point improvement).

---

## 6. Computational Efficiency

### 6.1 Latency

| Compression Ratio | End-to-End (s) | Speedup | LLMLingua Overhead (s) |
|---|---|---|---|
| 1x (no compression) | 8.6 | -- | -- |
| 2x | 4.9 | 1.7x | 0.8 |
| 5x | 2.3 | 3.3x | 0.3 |
| 10x | 1.3 | 5.7x | 0.2 |

### 6.2 Cost Savings (GPT-3.5-Turbo API)

| Dataset | Original Cost | LLMLingua Cost | Savings |
|---|---|---|---|
| GSM8K | $5.20 | $0.50 | 90% |
| BBH | $12.80 | $4.80 | 62% |
| ShareGPT | $0.70 | $0.30 | 57% |
| Arxiv | $1.30 | $0.20 | 85% |

---

## 7. Cross-Model Generalization

### Claude-v1.3 Results (GSM8K)

| Setting | EM (%) | Tokens | Ratio |
|---|---|---|---|
| 1-shot LLMLingua | 83.51 | 439 | 5x |
| half-shot LLMLingua | 82.61 | 171 | 14x |
| Simple Prompt | 81.80 | 691 | 3x |

### Different Small LMs (GSM8K)

| Model | 1-shot EM | half-shot EM | quarter-shot EM |
|---|---|---|---|
| Alpaca-7B | 79.08 | 77.41 | 77.33 |
| GPT2-Alpaca | 77.02 | 76.42 | 76.27 |

GPT2-Alpaca shows 2.06 point degradation, highlighting the importance of distribution alignment.

---

## 8. Notable Findings

1. **LLM Recovery Capability**: GPT-4 can reconstruct compressed prompts with high fidelity, recovering 9-step reasoning chains from 17x compressed text. GPT-3.5-Turbo cannot perform this recovery.

2. **Generation Length Reduction**: Compressed prompts produce shorter outputs, providing additional computational savings beyond the input compression.

3. **Reasoning Preservation**: The method excels at maintaining chain-of-thought logic. The zero-shot gap of 51.55 points on GSM8K validates that in-context learning information is preserved through compression.

---

## 9. Limitations

- Significant performance degradation at extreme compression (25x-30x)
- Tokenizer discrepancies between small compression models and black-box target LLMs
- Distribution gap remains even with alignment via instruction tuning
- Performance varies by task complexity

---

## Figures

**Figure 1:** Framework overview of LLMLingua showing the three-component pipeline: budget controller allocating ratios across prompt components, iterative token-level compression within each component, and the distribution-aligned small LM used for compression decisions.

**Figure 2:** Distribution of generated token lengths at varying compression ratios, showing that compressed prompts lead to shorter LLM outputs.

**Figure 3:** Performance curves of various prompt compression methods at different compression ratios on GSM8K, with dashed line showing full-shot baseline. LLMLingua maintains performance far longer than Selective Context as compression increases.

**Figure 4:** Example of GPT-4 recovering a compressed prompt (17x compression via Alpaca-7B) from GSM8K, reconstructing a 9-step chain-of-thought reasoning process.

**Figure 5:** Similar recovery example at 19x compression via GPT2-Alpaca, showing 7-step reconstruction.

**Figure 6:** Recovery of a compressed BBH prompt (7x compression via Alpaca-7B) using GPT-4.

---

## Key References

1. Li (2023). "Unlocking Context Constraints of LLMs: Enhancing Context Efficiency with Self-Information-Based Content Filtering." -- Selective Context baseline
2. Wei et al. (2022). "Chain of thought prompting elicits reasoning in large language models." NeurIPS 2022.
3. Mu et al. (2023). "Learning to compress prompts with gist tokens." -- Gist tokens approach
4. Ge et al. (2023). "In-context autoencoder for context compression in LLM." -- ICAE approach
5. Chevalier et al. (2023). "Adapting language models to compress contexts." -- AutoCompressor
6. Shannon (1951). "Prediction and entropy of printed English." Bell System Technical Journal.
7. Frantar & Alistarh (2023). "SparseGPT: Massive language models can be accurately pruned in one-shot." ICML 2023.
8. Zhang et al. (2020). "BERTScore: Evaluating text generation with BERT." ICLR 2020.
9. Cobbe et al. (2021). "Training verifiers to solve math word problems."
10. Taori et al. (2023). "Stanford Alpaca: An instruction-following LLaMA model."
