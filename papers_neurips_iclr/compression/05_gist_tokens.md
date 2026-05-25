# Learning to Compress Prompts with Gist Tokens

**Authors:** Jesse Mu, Xiang Lisa Li, Noah Goodman

**Venue:** NeurIPS 2023

**arXiv:** [2304.08467](https://arxiv.org/abs/2304.08467)

---

## Abstract

Prompting is the primary way to use large language models (LLMs), but prompts occupy valuable space in the context window and require recomputation for each new input. This paper introduces gisting, a method that trains language models to compress prompts into smaller sets of "gist tokens" whose activations can be cached and reused. The method works by modifying Transformer attention masks during standard instruction finetuning, requiring no additional training cost. Testing on decoder (LLaMA-7B) and encoder-decoder (FLAN-T5-XXL) models achieves up to 26x prompt compression, yielding up to 40% reduction in FLOPs, 4.2% wall-time improvement, and storage savings, with minimal quality loss on both seen and unseen instructions.

---

## 1. Introduction

Prompts in modern LLM applications serve as task instructions, few-shot examples, and system-level configurations. These prompts have two key inefficiencies:

1. **Redundant computation**: The same prompt is processed repeatedly for every new input
2. **Context window consumption**: Long prompts leave less space for actual inputs and outputs

Gisting addresses both by compressing prompt information into a small number of virtual "gist tokens" whose key-value activations can be cached and reused across inputs, analogous to how KV-cache works for previously processed tokens.

The key innovation is that gisting requires no separate training phase -- it emerges naturally from a simple modification to attention masks during standard instruction finetuning.

---

## 2. Method

### 2.1 Gist Token Mechanism

The approach inserts $k$ special gist tokens between the instruction (prompt) and the input:

$$[\text{instruction}] \; [\text{gist}_1] \; [\text{gist}_2] \; \ldots \; [\text{gist}_k] \; [\text{input}] \; [\text{output}]$$

### 2.2 Attention Mask Modification

The core idea is to modify the causal attention mask so that:
- **Gist tokens** can attend to the instruction (prompt) tokens
- **Input/output tokens** can attend to gist tokens but NOT directly to instruction tokens

This forces the model to compress all instruction information into the gist token representations, since downstream tokens can only access the instruction through the gist bottleneck.

For **decoder-only models** (LLaMA), the standard lower-triangular causal mask is modified by zeroing out the attention connections from input/output positions to instruction positions.

For **encoder-decoder models** (FLAN-T5), additional constraints prevent encoder input tokens from attending to prompt tokens and vice versa, with gist tokens mediating all information flow.

### 2.3 Training

The method adopts a meta-learning perspective: "gisting adopts a meta-learning approach, where we simply predict the gist prefixes zero-shot given only the prompt, allowing for generalization to unseen instructions without any additional training."

Training uses the standard next-token prediction objective on instruction-following datasets, with the only modification being the attention mask. No additional loss terms or training costs are needed.

### 2.4 Inference with Caching

At inference time:
1. Process the instruction through the model up to and including gist tokens
2. Cache the gist token KV activations
3. For subsequent inputs with the same instruction, skip step 1 and use cached gist KVs directly

This enables 26x compression: a prompt that originally consumed 26 tokens of context now requires only 1 gist token's cached activations.

---

## 3. Experimental Setup

### 3.1 Training Data

**Alpaca+ dataset**: 130,321 examples combining Self-Instruct and Stanford Alpaca datasets.

### 3.2 Models

- **LLaMA-7B**: Decoder-only, trained ~3 epochs
- **FLAN-T5-XXL (11B)**: Encoder-decoder, trained ~2 epochs

### 3.3 Number of Gist Tokens

Tested $k \in \{1, 2, 5, 10\}$ gist tokens. Single-token ($k=1$) models performed best or comparably, suggesting extreme compression is achievable.

### 3.4 Evaluation

- **Seen instructions**: 252 held-out examples from Alpaca+
- **Unseen instructions**: 252 examples with novel instructions not in training
- **Human-written**: 252 instructions from Super-NaturalInstructions (out-of-distribution)

Evaluation metrics:
- ROUGE-L
- ChatGPT-based pairwise comparison (win rate vs. positive control)
- Human evaluation (100 examples, 3 annotators)

---

## 4. Results

### 4.1 Automated Evaluation (Single Gist Token)

| Model | Metric | Seen | Unseen | Human-Written |
|---|---|---|---|---|
| LLaMA-7B | ROUGE-L (Pos baseline) | 58.0 | 48.1 | 27.0 |
| LLaMA-7B | ROUGE-L (Gist) | 57.8 (99.2%) | 46.6 (91.0%) | 23.9 (75.4%) |
| LLaMA-7B | ChatGPT Win% (Pos baseline) | 50.0 | 50.0 | 50.0 |
| LLaMA-7B | ChatGPT Win% (Gist) | 48.6 (92.4%) | 49.7 (98.8%) | 45.8 (84.9%) |
| FLAN-T5-XXL | ROUGE-L (Pos baseline) | 50.6 | 45.7 | 23.9 |
| FLAN-T5-XXL | ROUGE-L (Gist) | 48.9 (93.2%) | 43.8 (88.6%) | 21.7 (80.9%) |
| FLAN-T5-XXL | ChatGPT Win% (Pos baseline) | 50.0 | 50.0 | 50.0 |
| FLAN-T5-XXL | ChatGPT Win% (Gist) | 50.8 (103.9%) | 46.2 (84.4%) | 42.5 (63.2%) |

LLaMA-7B with gisting achieves 49.7% ChatGPT win rate on unseen instructions -- virtually indistinguishable from the positive control (50%).

### 4.2 Human Evaluation

| Model | H1 | H2 | H3 | Human Avg | ChatGPT Avg | Human kappa | ChatGPT kappa |
|---|---|---|---|---|---|---|---|
| LLaMA-7B | 51.1 | 44.5 | 59.8 | 52.3 (CI: 46.1-58.4) | 48.0 (CI: 38.0-58.2) | .24 | .29 |
| FLAN-T5-XXL | 43.0 | 41.9 | 37.2 | 40.6 (CI: 34.6-46.8) | 42.0 (CI: 32.2-52.3) | .33 | .29 |

LLaMA-7B gisting achieves 52.3% human win rate, slightly favoring gist over the full prompt. FLAN-T5 shows more degradation. Cohen's kappa between human and ChatGPT evaluation is 0.29, indicating fair agreement.

### 4.3 Efficiency Gains

| Model | Metric | No Cache | With Instruction Cache | With Gist Cache | vs. No Cache | vs. Instruction |
|---|---|---|---|---|---|---|
| LLaMA-7B | CUDA time (ms) | 23.4 +/- 6.88 | 22.1 +/- 6.58 | 21.8 +/- 6.55 | 6.8% reduction | 1.0% reduction |
| LLaMA-7B | GFLOPs | 915 +/- 936 | 553 +/- 900 | 552 +/- 899 | **40% reduction** | 0.11% reduction |
| FLAN-T5-XXL | CUDA time (ms) | 31.0 +/- 5.31 | N/A | 29.7 +/- 5.07 | **4.2% reduction** | N/A |
| FLAN-T5-XXL | GFLOPs | 716 +/- 717 | N/A | 427 +/- 684 | **40% reduction** | N/A |

The primary benefit is in FLOPs (40% reduction) rather than wall-time (4.2-6.8%), because memory bandwidth rather than compute is often the bottleneck. The storage benefit is significant: gist caching allows storing 26x more cached prompts in the same memory.

---

## 5. Analysis

### 5.1 Number of Gist Tokens

Single gist token ($k=1$) performs as well or better than $k \in \{2, 5, 10\}$, suggesting the model can compress typical instruction information into a single token's activations across all layers. This achieves maximum compression (26x average).

### 5.2 Failure Cases

Gisting struggles when instructions contain:
- Specific details requiring verbatim copying (e.g., "respond in the style of Shakespeare")
- Complex structured output requirements
- Highly specific formatting constraints

The authors note that "achieving such compression necessarily results in some loss of nuance of the original instruction."

### 5.3 Comparison to Distillation

Unlike knowledge distillation or soft prompt tuning, gisting:
- Does not require task-specific training
- Generalizes zero-shot to new instructions
- Works at inference time without modifying model parameters
- Can be combined with standard instruction finetuning at no extra cost

---

## 6. Related Work

Gisting relates to several lines of work:

- **Prompt tuning / Prefix tuning** (Lester et al., 2021; Li & Liang, 2021): Learn continuous prompts, but task-specific and require gradient-based optimization
- **Context distillation** (Snell et al., 2022): Distills context into model parameters, but loses generality
- **Compressive Transformers** (Rae et al., 2020): Compress past activations in recurrent settings
- **AutoCompressor** (Chevalier et al., 2023): Concurrent work also compressing context into summary tokens

---

## 7. Conclusions

Gisting provides a practical, zero-cost method for prompt compression during instruction finetuning. A single gist token achieves 26x compression with minimal quality loss on seen instructions and graceful degradation on unseen/out-of-distribution instructions. The primary benefits are computational (40% FLOPs reduction) and storage (26x more cached prompts), enabling more efficient deployment of instruction-following LLMs.

---

## Figures

**Figure descriptions based on paper content:**

**Figure 1 (conceptual):** Illustration of the gist token mechanism. An instruction is followed by gist tokens, then the input. The attention mask prevents input tokens from directly attending to instruction tokens, forcing all instruction information through the gist bottleneck.

**Figure 2 (attention masks):** Comparison of standard causal attention mask vs. gist attention mask for decoder-only models. The gist mask zeros out connections from post-gist positions to pre-gist (instruction) positions.

**Figure 3 (results):** Bar charts comparing ROUGE-L and ChatGPT win rates across seen, unseen, and human-written instructions for different numbers of gist tokens (k=1,2,5,10).

---

## Key References

1. Brown et al. (2020). "Language Models are Few-Shot Learners." NeurIPS 2020.
2. Vaswani et al. (2017). "Attention Is All You Need." NeurIPS 2017.
3. Li & Liang (2021). "Prefix-Tuning: Optimizing Continuous Prompts for Generation." ACL 2021.
4. Lester et al. (2021). "The Power of Scale for Parameter-Efficient Prompt Tuning." EMNLP 2021.
5. Hu et al. (2022). "LoRA: Low-Rank Adaptation of Large Language Models." ICLR 2022.
6. Touvron et al. (2023). "LLaMA: Open and Efficient Foundation Language Models."
7. Raffel et al. (2020). "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer." JMLR.
8. Snell et al. (2022). "Learning by Distilling Context."
9. Wingate et al. (2022). "Prompt Compression and Contrastive Conditioning for Controllability." EMNLP 2022.
10. Rae et al. (2020). "Compressive Transformers for Long-Range Sequence Modelling." ICLR 2020.
