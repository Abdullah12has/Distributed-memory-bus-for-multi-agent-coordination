# Prompt Compression for Large Language Models: A Survey

**Authors:** Zongqian Li, Yinhong Liu, Yixuan Su, Nigel Collier

**Venue:** arXiv 2024 (cs.CL)

**ArXiv:** [2410.12388](https://arxiv.org/abs/2410.12388)

---

## Abstract

This survey examines efficient methods for reducing long prompts used with large language models. It categorizes approaches into hard and soft prompt techniques, analyzes their mechanisms through attention optimization and Parameter-Efficient Fine-Tuning perspectives, and explores downstream applications and future research directions.

---

## 1. Introduction

Lengthy prompts increase memory usage and inference costs. Two main efficiency strategies exist: model-centric approaches (pruning, quantization) and prompt-centric methods. The authors note that "prompt-centric methods typically introduce minimal or no changes to the parameters of the LLM, allowing them to be used in a plug-and-play fashion."

**Main contributions:**
- Interpretation of compression mechanisms through multiple lenses
- Identification of current limitations (overfitting, latency, comparison gaps)
- Proposed future research directions

---

## 2. Preliminary Definitions

**Hard Prompts:** Natural language tokens from the model's vocabulary. Limitations include ambiguity and susceptibility to variations affecting performance.

**Soft Prompts:** Trainable continuous vectors with embedding-space dimensions. Trade-off between task performance and explainability.

**Prompt Compression Goal:** Reduce the length of prompts to improve the efficiency of processing LLM inputs, through either filtering or continuous representation encoding.

---

## 3. Hard Prompt Methods

Three representative approaches:

| Method | Approach | Key Features |
|--------|----------|--------------|
| **SelectiveContext** | Filtering | Uses self-information and syntactic parsing; no external models required |
| **LLMLingua** | Filtering | Employs GPT-2 for perplexity calculation; achieves up to 20x compression |
| **Nano-Capsulator** | Paraphrasing | Summarizes prompts into fluent natural language; includes semantic preservation loss |

Additional methods include LongLLMLingua, AdaComp, LLMLingua-2, and approaches enhanced by reinforcement learning or embeddings.

---

## 4. Soft Prompt Methods

### 4.1 Architectures

| Architecture | Encoder Type | Decoder Status | Compression Ratio | Key Innovation |
|--------------|--------------|----------------|-------------------|----------------|
| **CC** | N/A | Decoder-only | Task-specific | Minimizes KL divergence across sequences |
| **GIST** | Fine-tuned LLM | Fine-tuned | Up to 26x | Modified attention mechanism |
| **AutoCompressor** | Fine-tuned LLM | Fine-tuned | Long context | Recursive compression process |
| **ICAE** | Fine-tuned LLM | Frozen | 4x-16x | Handles detailed contexts; frozen decoder |
| **500xCompressor** | LoRA-enhanced | Frozen | 6x-480x | Uses K-V values instead of embeddings |
| **xRAG** | Embedding model | Frozen | High | Designed for retrieval-augmented generation |
| **UniICL** | Frozen LLM | Frozen | Varies | Compresses demonstrations only; minimal parameters |

### 4.2 Four Interpretive Perspectives

1. **Attention Optimization:** Compression reduces input length in two stages -- special tokens attend to full input, then generation uses only compressed tokens. Differs from sliding window or sparse attention approaches.

2. **PEFT Connection:** Similar to prompt and prefix tuning. ICAE parallels prompt tuning (embeddings); 500xCompressor resembles prefix tuning (K-V values). "These K-V values contain more parameters than embeddings and are assumed to store richer details."

3. **Modality Integration:** Compressed text functions as a new modality, analogous to vision-language models. Text compression requires greater precision than image encoding due to higher information density.

4. **Synthetic Language:** Compressed tokens represent "a new, more efficient language for LLMs" through three properties: information encoding, transmission between systems, and adaptive evaluation.

---

## 5. Downstream Applications

Prompt compression methods adapt across diverse domains:

- **General QA:** Compressing instructions or contexts
- **RAG:** xRAG exemplifies document compression for question answering
- **In-Context Learning (ICL):** UniICL compresses demonstration examples
- **Agent Systems:** API documentation compression for tool use
- **Domain-Specific Tasks:** Role-playing, function calling, specialized applications

---

## 6. Challenges and Future Directions

### 6.1 Current Challenges

**Fine-tuning Problems:** Methods avoiding decoder fine-tuning still face issues analogous to prompt/prefix tuning: catastrophic forgetting, overfitting, and model drift. Encoder dependency on specific decoder versions necessitates retraining upon model updates.

**Limited Efficiency Gains:** Despite significant compression ratios, gains materialize primarily during token generation. "For tasks with short outputs, these improvements may not be substantial." Hardware variability introduces inconsistencies.

**Comparison Gap:** Soft prompt methods lack systematic comparison with traditional attention optimization techniques, which avoid encoder overhead but apply uniform mechanisms to inputs and generation.

### 6.2 Proposed Future Directions

1. **Encoder Optimization:** Employ smaller, well-trained models (BERT-scale) instead of LLM-scale encoders; explore alternative PEFT methods (QLoRA, DoRA, MoRA).

2. **Hybrid Approaches:** Combine hard and soft methods for orthogonal mechanism synergy, though sequential compression timing presents challenges.

3. **Multimodal Insights:** Adapt cross-attention mechanisms from vision-language models; leverage image-text alignment training strategies.

---

## 7. Conclusions

Prompt compression offers significant potential but requires addressing fine-tuning limitations, efficiency bottlenecks, and comparison standardization. Insights from multimodal architectures present promising avenues for advancement.

---

## Figures

- **Figure 1:** Taxonomy of prompt compression methods showing the hard/soft division and sub-categories.
- **Figure 2:** Architecture comparison of soft prompt methods (CC, GIST, AutoCompressor, ICAE, 500xCompressor, xRAG, UniICL).
- **Figure 3:** Four interpretive perspectives on soft prompt compression mechanisms.
- **Figure 4:** Downstream application domains for prompt compression.

---

## Key References

1. Li et al. (2023) - SelectiveContext
2. Jiang et al. (2023) - LLMLingua
3. Jiang et al. (2023) - LongLLMLingua
4. Pan et al. (2024) - LLMLingua-2
5. Chevalier et al. (2023) - AutoCompressors
6. Ge et al. (2024) - ICAE
7. Mu et al. (2023) - GIST
8. Cheng et al. (2024) - xRAG
9. Lester et al. (2021) - Prompt tuning
10. Hu et al. (2022) - LoRA
