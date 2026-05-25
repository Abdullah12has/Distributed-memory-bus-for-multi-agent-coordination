# Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection

- **Authors:** Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, Hannaneh Hajishirzi
- **Venue:** ICLR 2024
- **ArXiv:** [2310.11511](https://arxiv.org/abs/2310.11511)
- **Submitted:** October 17, 2023

---

## Abstract

Despite their remarkable capabilities, large language models (LLMs) often produce responses containing inaccurate factual information due to their sole reliance on the parametric knowledge they encapsulate. Retrieval-Augmented Generation (RAG), an ad hoc approach that augments LMs with retrieval of relevant knowledge, decreases such issues. However, indiscriminately retrieving and incorporating a fixed number of retrieved passages, regardless of whether retrieval is necessary, or passages are relevant, diminishes LM versatility or can lead to unhelpful response generation. The authors introduce a new framework called Self-RAG that trains a single arbitrary LM to adaptively retrieve passages on-demand, and generate and reflect on retrieved passages and its own generations using special tokens, called reflection tokens. Generating reflection tokens makes the LM controllable during the inference phase, enabling it to tailor its behavior to diverse task requirements. Experiments show that Self-RAG (7B and 13B parameters) significantly outperforms state-of-the-art LLMs and retrieval-augmented models on a diverse set of tasks, including open-domain QA, reasoning, fact verification, and long-form generation. Self-RAG outperforms ChatGPT and retrieval-augmented ChatGPT on tasks requiring factual accuracy and citation, while it shows significant improvements in terms of long-form generation quality.

---

## 1. Introduction

LLMs frequently generate factually inaccurate text despite their capabilities. Standard RAG approaches retrieve passages indiscriminately, regardless of necessity, which can hurt performance on tasks where retrieval is unnecessary or when retrieved passages are irrelevant.

Self-RAG addresses these limitations through three key innovations:
1. **Adaptive retrieval** -- the model decides when to retrieve
2. **Self-reflection** -- the model evaluates retrieved passages and its own generations
3. **Controllable inference** -- test-time behavior can be adjusted via reflection token weights

---

## 2. Related Work

### Retrieval-Augmented Generation

Traditional RAG methods augment LM inputs with retrieved passages but retrieve indiscriminately. Self-RAG improves upon this through "on-demand retrieval for diverse instruction-following queries."

### Training with Critics

Wu et al. introduce fine-grained RLHF with multiple reward models, but Self-RAG achieves similar goals through offline critic training rather than expensive reinforcement learning.

### Control Tokens

Prior work uses control tokens to guide generation, but "Self-RAG uses reflection tokens to decide retrieval necessity and self-evaluate generation quality."

### LLM Refinement

Recent refinement work iteratively prompts models for feedback and revision at inference-time cost that Self-RAG avoids through offline critic training.

---

## 3. Self-RAG: Learning to Retrieve, Generate, and Critique

### 3.1 Problem Formulation and Overview

Given input $x$, the model generates output $y$ consisting of multiple segments. For each segment, the model:
1. Decides whether retrieval is needed (Retrieve token)
2. If yes, retrieves passages and evaluates relevance (IsRelevant token)
3. Generates a response segment
4. Evaluates whether the output is supported (IsSupported token)
5. Assesses overall utility (IsUse token)

### 3.2 Reflection Tokens

| Type | Input | Output | Definition |
|------|-------|--------|------------|
| Retrieve | $x$ or $(x, y)$ | {yes, no, continue} | Decides when to retrieve with retriever $\mathcal{R}$ |
| IsRelevant | $(x, d)$ | {relevant, irrelevant} | Passage $d$ provides useful information for input $x$ |
| IsSupported | $(x, d, y)$ | {fully supported, partially supported, no support} | Verification-worthy statements in $y$ are supported by $d$ |
| IsUse | $(x, y)$ | {5, 4, 3, 2, 1} | Output $y$ is a useful response to input $x$ |

### 3.3 Training the Critic Model

The critic $\mathcal{C}$ is trained on GPT-4-generated reflection token labels across ~4K-20K examples per token type. It achieves >90% agreement with GPT-4 predictions.

**Critic learning objective:**

$$\max_{\mathcal{C}} \mathbb{E}_{((x,y),r) \sim \mathcal{D}_\text{critic}} \log p_{\mathcal{C}}(r | x, y)$$

where $r$ represents reflection tokens.

### 3.4 Training the Generator

The generator $\mathcal{M}$ is trained on 150K instruction-output pairs augmented offline with reflection tokens and retrieved passages. Uses standard language modeling objective without reinforcement learning.

**Generator learning objective:**

$$\max_{\mathcal{M}} \mathbb{E}_{(x,y,r) \sim \mathcal{D}_\text{gen}} \log p_{\mathcal{M}}(y, r | x)$$

The model learns to predict both task output and reflection tokens simultaneously.

### 3.5 Inference with Self-RAG

The system employs segment-level beam search that:
1. Evaluates whether retrieval is needed via Retrieve token
2. Processes multiple passages in parallel when retrieval is triggered
3. Scores candidates using weighted combinations of critique token probabilities
4. Enables test-time customization through adjustable weights

**Segment score function:**

$$f(y_t, d, \text{Critique}) = p(y_t | x, d, y_{<t}) + \mathcal{S}(\text{Critique})$$

**Critique score computation:**

$$\mathcal{S}(\text{Critique}) = \sum_{G \in \mathcal{G}} w^G \cdot s_t^G$$

where weights $w^G$ are adjustable hyperparameters and $s_t^G$ normalizes the probability of desirable reflection tokens.

---

## 4. Experiments

### 4.1 Tasks and Datasets

Six diverse tasks:
- **PopQA:** Short-form open-domain QA (accuracy)
- **TriviaQA (TQA):** Open-domain QA (accuracy)
- **PubHealth:** Fact verification (accuracy)
- **ARC-Challenge:** Reasoning (accuracy)
- **Biography Generation:** Long-form factual generation (FactScore)
- **ASQA:** Long-form QA with citations (EM, ROUGE, MAUVE, precision, recall)

### 4.2 Baselines

- Llama2 (7B, 13B), Alpaca (7B, 13B)
- ChatGPT, Retrieval-augmented ChatGPT
- Llama2-chat 13B
- Specialized models: CoVE 65B, Toolformer 6B, SAIL 7B, Perplexity.ai

### 4.3 Main Results

| Model | PopQA | TQA | PubHealth | ARC | Bio (FS) | ASQA (EM) |
|-------|-------|-----|-----------|-----|----------|-----------|
| Llama2-chat 13B | 20.0 | 59.3 | 49.4 | 38.4 | 55.9 | 22.4 |
| ChatGPT | 29.3 | 74.3 | 70.1 | 75.3 | 71.8 | 35.3 |
| Ret-ChatGPT | 50.8 | 65.7 | 54.7 | 75.3 | -- | 40.7 |
| Alpaca 7B + retrieval | 46.7 | 64.1 | 40.2 | 48.0 | 76.6 | 30.9 |
| Llama2-FT 7B | 48.7 | 57.3 | 64.3 | 65.8 | 78.2 | 31.0 |
| **Self-RAG 7B** | **54.9** | **66.4** | **72.4** | **67.3** | **81.2** | **30.0** |
| **Self-RAG 13B** | **55.8** | **69.3** | **74.5** | **73.1** | **80.2** | **31.7** |

Self-RAG 7B and 13B outperform ChatGPT on PopQA, PubHealth, and Biography generation. Self-RAG 13B achieves 70.3% citation precision on ASQA versus 65.1% for retrieval-augmented ChatGPT.

---

## 5. Analysis

### 5.1 Retrieval Frequency Analysis

Self-RAG retrieves adaptively rather than uniformly. On tasks requiring factual knowledge (PopQA, Bio), retrieval occurs frequently. On reasoning tasks (ARC), retrieval is less frequent, preserving model versatility.

### 5.2 Ablation Studies

| Configuration | PopQA | PubHealth | ASQA (EM) |
|---------------|-------|-----------|-----------|
| Self-RAG (50K training) | 45.5 | 73.5 | 32.1 |
| No Retriever $\mathcal{R}$ | 43.6 | 67.8 | 31.0 |
| No Critic $\mathcal{C}$ | 42.6 | 72.0 | 18.1 |
| No retrieval (test-time) | 24.7 | 73.0 | -- |
| Hard constraints only | 28.3 | 72.6 | -- |
| Retrieve top-1 only | 41.8 | 73.1 | 28.6 |
| Remove IsSup token | 44.1 | 73.2 | 30.6 |

Key findings:
- Removing the critic model causes substantial drops, especially on ASQA (18.1 vs. 32.1)
- Disabling retrieval entirely drops PopQA to 24.7%
- All critique dimensions contribute meaningfully; IsSup removal slightly reduces ASQA
- Adjusting soft weights enables balancing citation precision against fluency without retraining

### 5.3 Customization at Inference

Test-time weight adjustment allows trading off between different quality dimensions (e.g., citation precision vs. fluency on ASQA) without retraining.

---

## Figures

- **Figure 1:** Overview of Self-RAG. Shows the model adaptively retrieving passages on demand, generating text segments, and producing reflection tokens (Retrieve, IsRelevant, IsSupported, IsUse) to critique its own output. The process is iterative across segments.

- **Figure 2:** Self-RAG training examples. Left example shows generation without retrieval (no factual lookup needed). Right example demonstrates retrieval-augmented generation with inserted passages and reflection tokens evaluating relevance and support.

---

## Implementation Details

- Base models: Llama2-7B and Llama2-13B
- Retriever: Contriever-MS MARCO
- Critic training: GPT-4-generated labels, ~4K-20K examples per reflection token type
- Generator training: 150K instruction-output pairs from Open-Instruct
- Training objective: Standard next-token prediction (no RL)
- Reflection tokens added as special vocabulary entries

---

## Key References (Top 10 Most Cited)

1. Lewis et al. (2020) -- RAG: Retrieval-augmented generation for knowledge-intensive NLP
2. Guu et al. (2020) -- REALM: Retrieval-augmented language model pre-training
3. Touvron et al. (2023) -- Llama 2: Open foundation and fine-tuned chat models
4. OpenAI (2023) -- GPT-4 technical report
5. Ouyang et al. (2022) -- Training language models to follow instructions with RLHF
6. Izacard et al. (2022) -- Contriever: Unsupervised dense information retrieval
7. Karpukhin et al. (2020) -- Dense Passage Retrieval for open-domain QA
8. Mallen et al. (2023) -- When not to trust language models: Investigating effectiveness of parametric and non-parametric memories (PopQA)
9. Stelmakh et al. (2022) -- ASQA: Factoid questions meet long-form answers
10. Min et al. (2023) -- FActScore: Fine-grained atomic evaluation of factual precision in long-form text generation
