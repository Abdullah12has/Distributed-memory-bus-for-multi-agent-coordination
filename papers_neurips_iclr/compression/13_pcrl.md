# Discrete Prompt Compression with Reinforcement Learning (PCRL)

**Authors:** Hoyoun Jung, Kyung-Joong Kim

**Venue:** IEEE Access 2024

**ArXiv:** [2308.08758](https://arxiv.org/abs/2308.08758)

**DOI:** 10.1109/ACCESS.2024.3403426

**Note:** The user-provided arxiv ID 2401.14043 was incorrect (leads to a prompt engineering survey). The correct ID for PCRL is 2308.08758.

---

## Abstract

We present PCRL, a method for reducing prompt length by directly editing tokens rather than training embeddings. The approach works with various language model architectures and can be trained without gradient access to the LMs or labeled data. The technique achieves approximately 24.6% token reduction while preserving performance, with policies transferable to larger models.

---

## 1. Introduction

While soft prompt methods offer efficiency, they suffer from interpretability issues, fixed token counts, and poor transferability across models. PCRL addresses these limitations through discrete token-level compression using reinforcement learning.

Key advantages:
- Works without gradient access to language models
- Applicable to black-box APIs
- Transferable between different LM architectures
- Achieves 24.6% average token reduction

---

## 2. Related Work

### 2.1 Discrete Prompt Optimization
Prior work focused on optimizing discrete prompts through gradient-based search or LM-based generation, prioritizing performance enhancement over compression.

### 2.2 Prompt Compression
Most compression research employs soft prompts with distillation objectives (training embeddings to encapsulate original contexts, decomposing prompts, or filtering based on self-information).

### 2.3 Unsupervised Summarization
PCRL adopts extractive summarization techniques but differs by evaluating compression based on LM-generated responses rather than source text.

---

## 3. Method

### 3.1 Task Definition

Given original prompt p = {x_1, x_2, ..., x_n}, find compressed prompt p' such that:
- delta(P_LM(y|p), P_LM(y|p')) < epsilon
- |p'| < |p|

The optimization objective balances faithfulness and compression ratio using balance term beta.

### 3.2 MDP Formulation

- **State:** Tokenized prompt
- **Actions:** Binary labels (include/exclude) for each token
- **Reward:** Based on output similarity and compression ratio
- **Environment:** Single-step (contextual multi-armed bandit)

**Policy Gradient Training (Self-Critical Sequence Training):**
```
gradient_J(theta) = E[(R(p,a) - R(p,a_hat)) * gradient log pi_theta(a|p)]
```

### 3.3 Model Architecture

- Frozen pre-trained LM (DistilBERT) for contextual embeddings
- Binary classification MLP layers (2 hidden layers, 4,096 width)
- Action masks preventing removal of statement tokens
- Only MLP parameters updated during training

### 3.4 Reward Design

**Faithfulness:** R_f = ROUGE-L(LM(p), LM(p^pi))

**Final Reward:**
- If R_f >= tau (0.9): reward = 1 - |p^pi|/|p|
- Else: reward = -lambda (-0.01)

---

## 4. Experiments

### 4.1 Instruction Prompt Results

**Datasets:** Alpaca+ (104,664 unique tasks), with seen/unseen/human splits

**Models:** GPT2-XL (1.5B), FLAN-T5-XL (3.0B)

| Model | Dataset | ROUGE-L | ChatGPT % | Compression |
|-------|---------|---------|-----------|-------------|
| GPT2-XL | Seen | 51.0 (93.6%) | 47.3 (94.6%) | 21.8% |
| GPT2-XL | Unseen | 42.3 (95.1%) | 49.1 (98.2%) | 23.2% |
| GPT2-XL | Human | 20.5 (88.6%) | 47.1 (94.3%) | 24.3% |
| FLAN-T5-XL | Seen | 41.1 (92.9%) | 45.0 (90.0%) | 27.4% |
| FLAN-T5-XL | Unseen | 40.6 (92.8%) | 43.6 (87.2%) | 25.1% |
| FLAN-T5-XL | Human | 21.1 (90.5%) | 41.9 (83.8%) | 27.6% |

### 4.2 Cross-Model Transfer

Policies trained on smaller models evaluated on larger LMs without retraining:

| Generation Model | Policy Source | ChatGPT % | Compression |
|------------------|--------------|-----------|-------------|
| Falcon-7B | GPT2-XL | 43.7 | 22.0% |
| LLaMa2-7B | GPT2-XL | 47.3 | 21.7% |
| FLAN-T5-XXL | GPT2-XL | 44.8 | 22.2% |
| GPT-3.5-Turbo | GPT2-XL | 49.8 | 21.8% |
| GPT-3.5-Turbo | FLAN-T5-XL | 47.7 | 27.0% |

GPT-3.5-Turbo achieves superior results, suggesting more powerful LMs are less susceptible to redundant tokens.

### 4.3 Token Importance Analysis

**Most removed tokens:**
- Grammatical suffixes: "ify" (99.96%), "ize" (97.40%), "ate" (95.45%)
- Stop words: "a" (97.86%), "the" (83.89%), "also" (80.32%)
- Punctuation: "." (98.70%)

**Preserved tokens:**
- Action verbs: "Create" (0%), "Explain" (0%)
- Interrogatives: "What" (0%)

---

## 5. Hyperparameters

| Parameter | Value |
|-----------|-------|
| Policy LM | DistilRoBERTa |
| Hidden Layers | 2 |
| Learning Rate | 3e-5 |
| Training Steps | 4,000 (GPT2-XL), 3,000 (FLAN-T5) |
| Batch Size | 32 |
| Max Tokens (Training) | 30 |
| Entropy Coefficient (alpha) | 0.001 |
| Penalty (lambda) | 0.01 |
| ROUGE Threshold (tau) | 0.9 |
| SCST Samples (k) | 4 |

---

## 6. Limitations

- Requires fine-tuned instruction models rather than off-the-shelf LMs
- Uses extractive compression, limiting potential for paraphrasing-based reduction
- Risk of hallucinations when critical information is removed
- Policy training limited to context length constraints
- ROUGE-based faithfulness may undervalue semantically correct but lexically different responses

---

## Figures

- **Figure 1:** PCRL pipeline showing the policy network scoring tokens for inclusion/exclusion, with the compressed prompt evaluated by the target LM.
- **Figure 2:** Token importance visualization showing which tokens are retained (action verbs, interrogatives) vs. removed (stop words, suffixes).
- **Figure 3:** Cross-model transfer results demonstrating policy generalization from small to large models.

---

## Key References

1. Wang et al. (2022) - Self-Instruct framework
2. Taori et al. (2023) - Stanford Alpaca dataset
3. Rennie et al. (2017) - Self-Critical Sequence Training
4. Lin & Hovy (2003) - ROUGE evaluation metric
5. Li et al. (2023) - SelectiveContext
6. Wingate et al. (2022) - Prompt compression via distillation
7. Mu et al. (2023) - GIST tokens
8. Sanh et al. (2019) - DistilBERT
9. Touvron et al. (2023) - Llama-2
10. Brown et al. (2020) - GPT-3
