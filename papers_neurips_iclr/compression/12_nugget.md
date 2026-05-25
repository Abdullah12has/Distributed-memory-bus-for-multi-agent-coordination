# Nugget: Neural Agglomerative Embeddings of Text

**Authors:** Guanghui Qin, Benjamin Van Durme

**Venue:** ICML 2023

**ArXiv:** [2310.01732](https://arxiv.org/abs/2310.01732)

**Note:** The user-provided arxiv ID 2310.06736 was incorrect (leads to a QCD physics paper). The correct ID for Nugget is 2310.01732.

---

## Abstract

We address limitations of constant-size text representations by proposing Nugget, which encodes language into a representation based on a dynamically selected subset of input tokens. The method learns meaningful units (nuggets) through autoencoding and machine translation tasks, demonstrating improved performance on semantic comparison tasks and enabling extended contextual windows for language models.

---

## 1. Introduction

The core contribution addresses a fundamental limitation: "You can't cram the meaning of a whole sentence into a single vector." Instead of constant-size or per-token representations, Nugget generates k <= n embeddings where k scales with document length using a configurable compression ratio r.

---

## 2. Technical Approach

### 2.1 Nugget Generator

Three main steps:
1. **Scoring:** A feedforward network assigns importance scores to contextualized token embeddings.
2. **Selection:** Top-k tokens are selected via a TopK operator.
3. **Encoding:** Selected embeddings are transformed into nugget representations.

The compression ratio follows k = ceil(n * r), where r is in (0, 1].

### 2.2 Ensuring Differentiability

Since TopK is non-differentiable, the authors introduce a residual connection through the decoder's cross-attention mechanism. The attention logits incorporate nugget selection scores, enabling gradient flow: "the nugget logit s_i tends to increase if the model tends to pay more attention to the corresponding nugget vector z_i."

### 2.3 Informed Nugget Encoding

To guide the encoder toward meaningful nugget selection:
- Compute selection scores at intermediate encoder layer l
- Add type embeddings distinguishing nugget vs. non-nugget tokens
- Freeze lower encoder layers for training stability

---

## 3. Intrinsic Evaluation

### 3.1 Compression Quality

With compression ratio r=0.1, the model achieves BLEU >0.99 on autoencoding, demonstrating "almost lossless text encoding" while using only 10% of tokens.

### 3.2 Nugget Selection Patterns

The model preferentially selects:
- Punctuation tokens (periods, commas)
- Conjunction words ("and")
- End-of-sequence markers

Notably, "the" comprises 5.2% of corpus tokens but only 0.7% of nuggets, showing learned selectivity rather than frequency-based selection.

### 3.3 Information Distribution

Each nugget encodes "a contiguous segment of text preceding clausal delimiters," implementing a "divide-and-conquer strategy."

---

## 4. Extrinsic Evaluation

### 4.1 Document Similarity Tasks

**Paraphrase Identification (ParaBank):**

| Configuration | Paraphrase ID | Passage Ranking |
|---------------|---------------|-----------------|
| Nugget (r=0.25, MT) | 97.38 | 56.51 |
| Nugget (r=0.1, MT) | 96.69 | 50.04 |
| TSDAE (AE) | 95.59 | 50.48 |
| ColBART | 94.83 | 52.44 |

Nugget with r=0.05 matches ColBART performance while using 20x fewer vectors on paraphrase identification.

### 4.2 Long-Range Sequence Modeling

Using segment length s=128, measured on WikiText-103 perplexity:

| Model | h=1 (256 ctx) | h=2 (384 ctx) | h=4 (640 ctx) | h=8 (1152 ctx) |
|-------|---------------|---------------|---------------|----------------|
| Nugget (r=0.05) | 29.88 | 29.25 | 28.24 | 28.14 |
| Nugget (r=0.1) | 29.83 | 29.21 | 28.44 | 28.10 |
| TSDAE | 30.09 | 29.55 | 29.01 | 28.77 |
| Compressive Transformers | -- | -- | 30.52 | -- |
| Full Attention (128 ctx) | -- | -- | -- | 31.46 |

All Nugget variants outperform the full-attention baseline.

---

## 5. Ablation Studies

| Configuration | MRR Score |
|---------------|-----------|
| Learned selection | 96.69 |
| Chunking (rule-based) | 95.56 |
| Sentence boundary (rule-based) | 87.91 |
| Without nugget feedback | 96.29 |
| With nugget feedback | 96.69 |

Learned nugget selection substantially outperforms rule-based alternatives. The nugget feedback mechanism provides modest improvements.

Using features from encoder layer 3 (l=3) performs optimally.

---

## 6. Multilingual Findings

The preference for delimiter tokens generalizes across 9 languages beyond English, indicating language-universal properties of the learned selection mechanism.

---

## 7. Training Details

- **Architecture:** Modified BART encoder-decoder (602M parameters)
- **Objectives:** Autoencoding or machine translation
- **Dataset:** English-Chinese WMT19 (concatenated to 128-token documents)
- **Optimization:** Adam (5e-5 learning rate)
- **Hardware:** 4 NVIDIA RTX 6000 GPUs

---

## 8. Discussion and Future Work

- **Contrastive learning** could further improve downstream performance.
- **Long-context LLMs:** Compressed nuggets enable conditioning on significantly longer textual inputs.
- **Chain-of-thought generation:** Decoding nugget sequences may reduce computational cost versus full token decoding.

Nuggets achieve "highly accurate reconstruction," positioning them as "a compressed unit of language" suitable for scaling language models to longer contexts.

---

## Figures

- **Figure 1:** Nugget architecture showing scoring, selection, and encoding stages with gradient flow through cross-attention.
- **Figure 2:** Nugget selection heatmap showing which tokens are selected across different texts, with preference for delimiters and content words.
- **Figure 3:** Information distribution analysis showing each nugget covers a contiguous text segment.
- **Figure 4:** Perplexity curves for long-range language modeling with increasing history length.

---

## Key References

1. Pennington et al. (2014) - GloVe
2. Devlin et al. (2019) - BERT
3. Lewis et al. (2020) - BART
4. Karpukhin et al. (2020) - DPR
5. Khattab & Zaharia (2020) - ColBERT
6. Wang et al. (2022) - TSDAE
7. Rae et al. (2020) - Compressive Transformers
8. Dai et al. (2019) - Transformer-XL
9. Hu et al. (2020) - ParaBank
10. Merity et al. (2017) - WikiText-103
