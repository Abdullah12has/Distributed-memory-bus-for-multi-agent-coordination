# Compact Language Models via Pruning and Knowledge Distillation (Minitron)

**Authors:** Saurav Muralidharan, Sharath Turuvekere Sreenivas, Raviraj Joshi, Marcin Chochowski, Mostofa Patwary, Mohammad Shoeybi, Bryan Catanzaro, Jan Kautz, Pavlo Molchanov

**Venue:** arXiv 2024 (cs.CL)

**ArXiv:** [2407.14679](https://arxiv.org/abs/2407.14679)

---

## Abstract

We investigate whether pruning existing large language models and retraining them with minimal data (under 3% of original training) can effectively replace full model retraining. We develop compression techniques combining depth, width, attention, and MLP pruning with knowledge distillation, achieving 2-4x compression of the Nemotron-4 family while requiring 40x fewer training tokens than training from scratch. The resulting Minitron models demonstrate up to 16% MMLU improvements and match performance of community models like Mistral 7B and Llama-3 8B.

---

## 1. Introduction

Training large language models from scratch is extremely expensive. This paper demonstrates that structured pruning of a large model followed by lightweight knowledge distillation retraining can produce competitive smaller models at a fraction of the cost.

---

## 2. Pruning Methodology

Activation-based importance estimation across four dimensions:

- **Width pruning:** Neurons, attention heads, embedding channels via L2-norm aggregation
- **Depth pruning:** Layer removal using perplexity or Block Importance metrics
- **Importance computation:** Uses only forward passes on 1024 calibration samples

---

## 3. Retraining Strategy

Knowledge distillation from the unpruned teacher model, combining:
- Logit-based KL divergence loss
- Intermediate state matching (when depth is significantly reduced)
- Cross-entropy loss against ground truth labels

---

## 4. Ten Best Practices

The paper distills guidance into actionable recommendations:

1. Train largest model, then iteratively prune to smaller variants
2. Use (batch=L2, seq=mean) aggregation for width; PPL/BI for depth
3. Single-shot importance estimation suffices
4. Prefer width over depth pruning for models <= 15B
5. Use distillation-only retraining with KLD
6. Include intermediate states when depth is reduced significantly
7. Logit-only distillation for minimal depth reduction
8. Prune models closest to target size
9. Lightweight retraining stabilizes architecture rankings
10. If multi-phase training used, prune final stage checkpoint

---

## 5. Results

### 5.1 Minitron 8B

- Better accuracy than Nemotron-3 8B and Llama-2 7B
- Comparable performance to Mistral 7B, Gemma 7B, Llama-3 8B
- Uses 94B tokens vs. trillions for training from scratch

### 5.2 Minitron 4B

- Outperforms Gemma2
- Compares favorably to Phi-2

### 5.3 Cost Savings

1.8x reduction for training entire 15B/8B/4B family versus training each separately.

### 5.4 Key Findings

| Finding | Evidence |
|---------|----------|
| Width > Depth initially inferior, but reverses after retraining | Demonstrated in ablation tables |
| Distillation critical for accuracy | 13.5% MMLU gain vs. training from scratch at iso-compute |
| Iterative pruning helps aggressive compression | Two-step 15B->8B->4B outperforms one-shot by 12% MMLU |
| Search with lightweight retraining necessary | Rankings stabilize after ~300 training steps |

---

## 6. Methodology Details

### 6.1 Width Pruning

Importance scores computed per neuron/head using activation magnitudes:
- L2-norm across batch dimension
- Mean across sequence dimension
- Single-shot estimation on 1024 calibration samples

### 6.2 Depth Pruning

Two approaches:
- **Perplexity-based:** Remove layers with least perplexity impact
- **Block Importance (BI):** Measure cosine similarity between layer input and output; remove layers with highest similarity (most redundant)

### 6.3 Combined Pruning

Width and depth pruning can be combined. The paper finds that width-only pruning generally outperforms depth-only for moderate compression (2-4x), but depth pruning becomes necessary for extreme compression.

---

## 7. Ablation Studies

### 7.1 Pruning vs. Training from Scratch

At iso-compute, pruning + distillation significantly outperforms training from scratch:
- 8B model: +16% MMLU improvement
- 4B model: comparable with 40x fewer tokens

### 7.2 Distillation Components

| Component | Contribution |
|-----------|-------------|
| KL divergence (logits) | Primary signal |
| Intermediate states | Important for large depth reduction |
| Cross-entropy | Baseline, outperformed by distillation |

---

## 8. Limitations

- Requires access to original unpruned teacher model
- Structured pruning constraints (less flexibility than unstructured)
- Requires pre-existing large base model
- Tested primarily on Nemotron-4 family; generalization to other architectures needs validation

---

## Figures

- **Figure 1:** Overview of the pruning and distillation pipeline, from 15B teacher to 8B and 4B Minitron models.
- **Figure 2:** Comparison of width-only vs. depth-only vs. combined pruning at different compression ratios.
- **Figure 3:** MMLU scores across model sizes comparing Minitron against community models (Mistral, Llama-3, Gemma).
- **Figure 4:** Training token efficiency: Minitron uses 40x fewer tokens while matching performance.

---

## Key References

1. Touvron et al. (2023) - Llama / Llama-2
2. Jiang et al. (2023) - Mistral
3. Hinton et al. (2015) - Knowledge distillation
4. Frankle & Carlin (2019) - Lottery Ticket Hypothesis
5. Ma et al. (2023) - LLM-Pruner
6. Sun et al. (2024) - Wanda pruning
7. Xia et al. (2023) - Sheared LLaMA
8. Raffel et al. (2020) - T5
9. Hu et al. (2022) - LoRA
10. Team Gemma (2024) - Gemma models
