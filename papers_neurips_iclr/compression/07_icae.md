# In-context Autoencoder for Context Compression in a Large Language Model (ICAE)

**Authors:** Tao Ge, Jing Hu, Lei Wang, Xun Wang, Si-Qing Chen, Furu Wei

**Venue:** ICLR 2024

**ArXiv:** [2307.06945](https://arxiv.org/abs/2307.06945)

---

## Abstract

We propose the In-context Autoencoder (ICAE), which leverages LLMs to compress a long context into short compact memory slots that can be directly conditioned on by the LLM for various purposes. The method undergoes pretraining on autoencoding and language modeling objectives, then fine-tuning on instruction data. Results show the lightweight approach achieves approximately 4x context compression using Llama while adding only 1% additional parameters, reducing latency and GPU memory costs.

---

## 1. Introduction

Long contexts are expensive for LLMs due to quadratic attention complexity. ICAE addresses this by learning to compress contexts into a small number of "memory slots" -- continuous vector representations that the frozen target LLM can condition on directly, similar to soft prompts.

---

## 2. Architecture

### 2.1 Encoder

A LoRA-adapted LLM that converts a long context into k memory slots. Learnable memory tokens are appended to the input, and the model processes them through its layers. The output representations of the memory tokens serve as the compressed representation.

### 2.2 Decoder

The original (frozen) LLM, which conditions on memory slots to accomplish tasks without any modification to its parameters.

---

## 3. Training

Two-stage training approach:

### 3.1 Pretraining (on Pile dataset)

- **Autoencoding objective:** Reconstruct original text from memory slots.
- **Text continuation objective:** Predict tokens following the context, ensuring the compressed representation captures information useful for generation.

### 3.2 Fine-tuning

Instruction-based training on the PwC dataset (240k context-prompt-response samples) to improve task-specific performance.

---

## 4. Main Results

| Metric | Performance |
|--------|-------------|
| Compression ratio | 4x (512 -> 128 tokens) |
| Autoencoding BLEU | 99.1% at 512-token contexts |
| Inference speedup | 2-3.5x depending on batch size |
| Win rate vs baselines | 56.7-74.1% (Llama-7b) |
| Additional parameters | ~1% of base model |

### 4.1 Memory Efficiency

- Saves approximately 20GB GPU memory for 4096-token contexts.
- Over 7x speedup when memory slots are pre-cached.

### 4.2 Scalability

Performance improves with larger base models (Llama-2-13b outperforms Llama-7b). Memory slots work across diverse prompt types without task-specific retraining.

---

## 5. Key Findings

### 5.1 Semantic Compression

ICAE memorization patterns parallel human memory. Testing on random text shows dramatically worse performance (BLEU 0.2-3.5%) compared to normal text (BLEU 99.3%), suggesting the model learns semantic representations rather than rote memorization.

### 5.2 Compression Quality

At 4x compression, ICAE preserves the vast majority of contextual information needed for downstream tasks. The compressed representation functions as an effective "soft prompt" for the frozen decoder.

---

## 6. Limitations

- Performance degradation compared to uncompressed contexts in task-specific evaluation.
- Maximum testing limited to 13B parameter models due to computational constraints.
- Requires LoRA training of the encoder, though this is lightweight.

---

## Figures

- **Figure 1:** ICAE architecture diagram showing the LoRA-adapted encoder compressing context into memory slots, which are then used by the frozen LLM decoder.
- **Figure 2:** Autoencoding BLEU scores across different context lengths, showing graceful degradation as context increases.
- **Figure 3:** Comparison of ICAE memory slots vs. full context on instruction-following tasks.

---

## Key References

1. Hu et al. (2022) - LoRA
2. Touvron et al. (2023) - Llama
3. Chevalier et al. (2023) - AutoCompressors
4. Mu et al. (2023) - GIST tokens
5. Wingate et al. (2022) - Prompt compression
6. Gao et al. (2020) - The Pile dataset
7. Brown et al. (2020) - GPT-3
8. Dai et al. (2019) - Transformer-XL
9. Rae et al. (2020) - Compressive Transformers
10. Bulatov et al. (2022) - Recurrent Memory Transformer
