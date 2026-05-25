# LoRA: Low-Rank Adaptation of Large Language Models

**Authors:** Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen

**Venue:** ICLR 2022

**arXiv:** [2106.09685](https://arxiv.org/abs/2106.09685)

---

## Abstract

The paper proposes Low-Rank Adaptation (LoRA), a method that freezes the pre-trained model weights and injects trainable rank decomposition matrices into each layer to enable efficient fine-tuning of large language models. Key findings include reducing trainable parameters by 10,000x compared to GPT-3 175B and achieving performance on par with or exceeding full fine-tuning while maintaining faster training speeds and no additional inference latency.

---

## 1. Core Innovation

### Reparametrization Strategy

Instead of updating all weights W_0 -> W_0 + Delta_W, LoRA constrains updates as:

W_0 + Delta_W = W_0 + BA

where B is in R^(d x r) and A is in R^(r x k), with rank r much less than min(d, k).

### Implementation Details

- Freezes pre-trained weights
- Trains only A and B matrices
- Scales outputs by alpha/r for hyperparameter stability
- No additional inference latency (weights mergeable at deployment)

---

## 2. Empirical Results

### Performance Across Models

| Model | Dataset | LoRA Performance | Trainable Parameters |
|-------|---------|------------------|----------------------|
| RoBERTa large | GLUE avg | 88.6% | 0.8M |
| DeBERTa XXL | GLUE avg | 91.3% | 4.7M |
| GPT-2 Large | E2E NLG | 70.4 BLEU | 0.77M |
| GPT-3 175B | WikiSQL | 73.4% | 4.7M |
| GPT-3 175B | MNLI | 91.7% | 4.7M |

LoRA matches or exceeds full fine-tuning baseline performance across all tested models.

---

## 3. Key Findings on Low-Rank Structure

### Rank Analysis

Surprisingly low optimal ranks---rank 1 suffices for {Wq, Wv} adaptation on GPT-3, while higher ranks show minimal improvements.

### Subspace Similarity

Top singular vectors of Delta_W overlap significantly between r=8 and r=64, indicating most useful information concentrates in lowest dimensions.

### Delta_W Characteristics

Analysis shows Delta_W amplifies directions not emphasized in original W---with amplification factor approximately 21.5 for r=4, suggesting adaptation amplifies important features for specific downstream tasks.

---

## 4. Advantages Over Alternatives

**vs. Adapter Layers:** Adapters introduce up to 30.3% inference latency at batch size 1, while LoRA adds none.

**vs. Prefix-Tuning:** Prefix methods suffer performance degradation with large token counts and consume sequence length, limiting downstream task inputs.

---

## 5. Practical Benefits

- Enables rapid task-switching (swap 35MB vs. 350GB models)
- Reduces training memory from 1.2TB to 350GB for GPT-3 175B
- 25% training speedup compared to full fine-tuning
- Allows multiple task-specific models without proportional storage costs

---

## 6. Limitations

- Batching different tasks with different LoRA modules complicates implementation
- Weight matrix selection is heuristic-based rather than principled
- Primarily focuses on attention weights, not MLP or LayerNorm layers

---

## 7. Figure Descriptions

- **Figure 1:** LoRA reparametrization diagram showing frozen weights W with injected low-rank matrices A and B
- **Figure 2:** Performance comparison across adaptation methods (LoRA, adapters, prefix-tuning, full fine-tuning)
- **Figure 3:** Subspace similarity analysis showing overlap between different rank settings
- **Figure 4:** Inference latency comparison between LoRA and adapter approaches

---

## Key References

1. Aghajanyan et al. (2020) --- Intrinsic Dimensionality work motivating low-rank hypothesis
2. Brown et al. (2020) --- GPT-3 paper providing baseline model
3. Houlsby et al. (2019) --- Original adapter layer proposal
4. Li and Liang (2021) --- Prefix-tuning comparative baseline
5. Vaswani et al. (2017) --- Transformer architecture foundation
6. Devlin et al. (2019) --- BERT pre-training paradigm
7. Liu et al. (2019) --- RoBERTa optimization improvements
8. He et al. (2021) --- DeBERTa model for experiments
9. Rebuffi et al. (2017) --- Early adapter work
10. Allen-Zhu and Li (2019) --- Theoretical low-rank neural network properties
