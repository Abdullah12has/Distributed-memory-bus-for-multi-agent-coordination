# Adapting Language Models to Compress Contexts (AutoCompressor)

**Authors:** Alexis Chevalier, Alexander Wettig, Anirudh Ajith, Danqi Chen

**Venue:** EMNLP 2023

**ArXiv:** [2305.14788](https://arxiv.org/abs/2305.14788)

---

## Abstract

We propose AutoCompressors, which adapt pre-trained language models to compress long contexts into compact summary vectors, which are then accessible to the model as soft prompts. The method uses unsupervised training where documents are processed in segments, with summary vectors from prior segments informing language modeling. OPT and Llama-2 models were fine-tuned on sequences up to 30,720 tokens, demonstrating improvements in perplexity. The approach was evaluated on in-context learning tasks and retrieval-augmented modeling, positioning it as a simple and inexpensive solution to extend the context window of LMs.

---

## 1. Introduction

Large language models are limited by fixed context windows. AutoCompressors address this by learning to generate compact summary vectors that represent long contexts, enabling the model to process documents far beyond its training context length.

Three main contributions:
1. A context compression technique that extends context windows by learning to generate summary vectors, incorporating summary accumulation and randomized segmenting strategies.
2. Demonstration that summary vectors encode useful information for downstream tasks while reducing inference costs in in-context learning.
3. Evidence that pre-computing summary vectors benefits corpus-scale retrieval-augmented language modeling and passage re-ranking.

---

## 2. Technical Approach

### 2.1 Summary Vectors Architecture

The method builds on the Recurrent Memory Transformer (RMT) by extending the input vocabulary with special tokens (`<Sum>_1` ... `<Sum>_k`) whose output representations serve as compressed context summaries. These vectors are passed to subsequent segments as soft prompts.

### 2.2 Summary Accumulation

Rather than using only the previous segment's compression, the approach concatenates summary vectors from all prior segments, enabling direct information pathways between each segment and all preceding ones. This avoids the information bottleneck of passing only the most recent summary.

### 2.3 Randomized Segmenting

Training documents use variable-length segments, improving model robustness to different compression scenarios during evaluation.

### 2.4 Gradient Stopping

Computing summary vectors with stopped gradients after two compression steps reduces memory requirements while maintaining performance.

---

## 3. Experimental Results

### 3.1 Language Modeling Performance

| Model | Context Tokens | Perplexity |
|-------|---------------|------------|
| OPT-2.7B baseline | 2,048 | 6.28 |
| AutoCompressor | 6,144 | 5.93 |
| Extended Full Attention | 6,144 | 5.94 |

AutoCompressors achieve comparable perplexity to extended full attention while using significantly fewer token representations (150 summary vectors vs. 2,048 tokens).

### 3.2 In-Context Learning

Testing on 11 classification tasks reveals that compressed demonstrations outperform plain-text equivalents on 8/11 tasks, while substantially reducing inference costs.

### 3.3 Retrieval-Augmented Language Modeling

The "Fused Summaries" approach concatenates pre-computed summary vectors from retrieved passages, achieving 1.5x perplexity improvements compared to plain-text passages at equivalent sequence lengths.

### 3.4 Scaling Results

Models successfully scale from OPT-2.7B to Llama-2-7B, fine-tuned on up to 30,720-token sequences with single GPU training. Memory efficiency improvements enable training scenarios where RMT baselines encounter out-of-memory errors.

---

## 4. Practical Applications

- **Extended Context Windows:** Processing documents substantially longer than pre-training context while maintaining computational efficiency.
- **Efficient In-Context Learning:** Replacing verbose demonstrations with compact vector representations.
- **Corpus Pre-Processing:** Pre-computing summary vectors for retrieval systems, balancing storage and inference speed.

---

## 5. Limitations

- Limited evaluation on models larger than 7B parameters.
- Incomplete information preservation compared to full attention mechanisms.
- Quadratic complexity growth with segment accumulation despite improvements over standard attention.

---

## Figures

- **Figure 1:** Overview of the AutoCompressor architecture showing how documents are split into segments, each producing summary vectors that accumulate and are passed to subsequent segments as soft prompts.
- **Figure 2:** Perplexity curves comparing AutoCompressor against RMT and full attention baselines across varying context lengths.
- **Figure 3:** In-context learning accuracy across 11 classification tasks, showing compressed demonstrations matching or exceeding plain-text performance.

---

## Key References

1. Bulatov et al. (2022) - Recurrent Memory Transformer
2. Radford et al. (2019) - GPT-2
3. Zhang et al. (2022) - OPT
4. Touvron et al. (2023) - Llama-2
5. Brown et al. (2020) - GPT-3 / In-context learning
6. Dai et al. (2019) - Transformer-XL
7. Borgeaud et al. (2022) - RETRO
8. Izacard & Grave (2021) - FiD
9. Mu et al. (2023) - GIST tokens
10. Wingate et al. (2022) - Prompt compression via distillation
