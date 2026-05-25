# LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression

**Authors:** Zhuoshi Pan, Qianhui Wu, Huiqiang Jiang, Menglin Xia, Xufang Luo, Jue Zhang, Qingwei Lin, Victor Ruhle, Yuqing Yang, Chin-Yew Lin, H. Vicky Zhao, Lili Qiu, Dongmei Zhang

**Venue:** Findings of ACL 2024

**arXiv:** [2403.12968](https://arxiv.org/abs/2403.12968)

---

## Abstract

This paper addresses prompt compression for large language models from a task-agnostic perspective. The authors identify two key limitations of existing approaches that use information entropy from causal language models: (1) the causal nature limits bidirectional context modeling, and (2) information entropy may not align well with compression objectives. Instead, LLMLingua-2 formulates prompt compression as a token classification problem, using a Transformer encoder as the base architecture to capture all essential information from bidirectional context. The method employs data distillation from GPT-4 to build a training dataset of extractive compressions from meeting transcripts. Despite training only on meeting data, LLMLingua-2 generalizes effectively across diverse benchmarks (MeetingBank, LongBench, ZeroSCROLLS, GSM8K, BBH), achieving 3x-6x faster compression speed than existing approaches with improved faithfulness.

---

## 1. Introduction

Prior prompt compression methods like LLMLingua rely on causal language models (e.g., LLaMA) to estimate token importance via perplexity. This has two fundamental issues:

1. **Unidirectional context**: Causal LMs only see left context, missing important bidirectional dependencies
2. **Misaligned objective**: Information entropy measures surprise, not necessarily relevance for compression

LLMLingua-2 reconceptualizes compression as an extractive text compression problem -- deciding which tokens to keep vs. discard -- and uses a small bidirectional encoder (XLM-RoBERTa-large or multilingual BERT) trained on GPT-4-distilled compression data.

---

## 2. Data Distillation

### 2.1 Dataset Construction

The training data is built from the MeetingBank dataset (meeting transcripts) using GPT-4 with carefully designed instructions enforcing five constraints:

1. Only remove words (no additions)
2. Maintain original word order
3. No word changes or paraphrasing
4. No abbreviations
5. No new content generation

The compression is performed chunk-wise (processing text in segments) rather than on entire documents, which significantly improves compression quality.

### 2.2 Quality Control

Two metrics ensure dataset quality:

- **Variation Rate (VR)**: Measures hallucinated content -- words in compressed text not found in original. Lower is better.
- **Alignment Gap (AG)**: Assesses annotation accuracy by comparing token-level labels derived from compressed text against ideal compression. Lower is better.

Bottom-quality samples are filtered out based on these metrics.

### 2.3 Dataset Statistics

| Data Part | Size | Chunks | Avg Sentences | Avg Tokens | Compression |
|---|---|---|---|---|---|
| Original | 5,169 | 41,746 | 232 | 3,635 | -- |
| Compressed | 5,169 | 41,746 | 132 | 1,415 | 2.57x |

---

## 3. Model Architecture

LLMLingua-2 uses a Transformer encoder for binary token classification:

- **Input**: Tokenized text from the original prompt
- **Output**: Binary label per token (preserve = 1, discard = 0)
- **Base models**: XLM-RoBERTa-large (LLMLingua-2) or multilingual BERT (LLMLingua-2-small)
- **Training**: Standard cross-entropy loss with Adam optimizer

The key advantage over causal LM-based approaches is that the encoder sees full bidirectional context when making each token's preserve/discard decision.

### Compression at Inference

At inference time, the model outputs preservation probabilities for each token. A target compression ratio is achieved by selecting the top-k tokens by probability, where k is determined by the desired ratio. Tokens are kept in their original order to maintain coherence.

---

## 4. Experimental Results

### 4.1 In-Domain: MeetingBank

| Methods | QA (EM) | Summary (BLEU) | Rouge1 | Rouge2 | RougeL | BERTScore | Tokens | Ratio |
|---|---|---|---|---|---|---|---|---|
| Original | 87.75 | 22.34 | 47.28 | 26.66 | 35.15 | 88.96 | 3,003 | 1.0x |
| Selective-Context | 66.28 | 10.83 | 39.21 | 18.73 | 27.67 | 84.48 | 1,222 | 2.5x |
| LLMLingua | 67.52 | 8.94 | 37.98 | 14.08 | 26.58 | 86.42 | 1,176 | 2.5x |
| LLMLingua-2-small | 85.82 | 17.41 | 48.33 | 23.07 | 34.36 | 88.77 | 984 | 3.0x |
| **LLMLingua-2** | **86.92** | **17.37** | **48.64** | **22.96** | **34.24** | **88.27** | **970** | **3.1x** |

LLMLingua-2 achieves near-original QA performance (86.92% vs 87.75%) while compressing 3.1x, dramatically outperforming LLMLingua (67.52%) and Selective-Context (66.28%).

### 4.2 Out-of-Domain: LongBench and ZeroSCROLLS (2,000-token constraint)

| Methods | SingleDoc | MultiDoc | Summ. | FewShot | Synth. | Code | AVG | ZeroSCROLLS AVG |
|---|---|---|---|---|---|---|---|---|
| Original Prompt | 39.7 | 38.7 | 26.5 | 67.0 | 37.8 | 54.2 | 44.0 | 34.7 |
| Selective-Context | 16.2 | 34.8 | 24.4 | 15.7 | 8.4 | 49.2 | 24.8 | 19.4 |
| LLMLingua | 22.4 | 32.1 | 24.5 | 61.2 | 10.4 | 56.8 | 34.6 | 27.2 |
| LongLLMLingua | 39.0 | 42.2 | 27.4 | 69.3 | 53.8 | 56.6 | 48.0 | 32.5 |
| LLMLingua-2-small | 29.5 | 32.0 | 24.5 | 64.8 | 22.3 | 56.2 | 38.2 | 33.3 |
| **LLMLingua-2** | **29.8** | **33.1** | **25.3** | **66.4** | **21.3** | **58.9** | **39.1** | **33.4** |

### 4.3 Out-of-Domain: Reasoning (GSM8K and BBH)

| Methods | GSM8K 1-shot EM | GSM8K half-shot EM | BBH 1-shot EM | BBH half-shot EM |
|---|---|---|---|---|
| Full-Shot | 78.85 | 78.85 | 70.07 | 70.07 |
| Selective-Context | 53.98 | 52.99 | 54.27 | 54.02 |
| LLMLingua | 79.08 | 77.41 | 70.11 | 61.60 |
| LLMLingua-2-small | 78.92 | 77.48 | 69.54 | 60.35 |
| **LLMLingua-2** | **79.08** | **77.79** | **70.02** | **61.94** |

LLMLingua-2 matches LLMLingua on GSM8K despite training only on meeting transcripts, demonstrating strong generalization.

### 4.4 Generalization to Mistral-7B

| Methods | MeetingBank QA EM | LongBench SingleDoc (2k) | LongBench SingleDoc (3k) |
|---|---|---|---|
| Original Prompt | 66.95 | 24.5 | 24.5 |
| Selective-Context | 58.13 | 22.0 | 26.0 |
| LLMLingua | 50.45 | 19.5 | 20.8 |
| LLMLingua-2-small | 75.97 | 25.3 | 27.9 |
| **LLMLingua-2** | **76.22** | **26.8** | **27.3** |

Notably, LLMLingua-2 improves over the original prompt on Mistral-7B (76.22% vs 66.95%), suggesting compression removes noise that confuses smaller models.

---

## 5. Efficiency Analysis

### 5.1 Compression Latency (MeetingBank)

| Compression Ratio | End2End w/o Compression | End2End w/ LLMLingua-2 | Selective-Context | LLMLingua | LLMLingua-2 |
|---|---|---|---|---|---|
| 1x | 14.9s | -- | -- | -- | -- |
| 2x | -- | 9.4s (1.6x speedup) | 15.9s | 2.9s | **0.5s** |
| 3x | -- | 7.5s (2.1x speedup) | 15.6s | 2.1s | **0.4s** |
| 5x | -- | 5.2s (2.9x speedup) | 15.5s | 1.5s | **0.4s** |

LLMLingua-2's compression step is 3x-6x faster than LLMLingua and orders of magnitude faster than Selective-Context. GPU memory requirement is 8x lower.

---

## 6. Ablation Studies

### 6.1 Instruction Design Impact

| Instruction Variant | Compression Ratio | Variation Rate | QA F1 |
|---|---|---|---|
| Instruction1 (naive) | 123x | 13.7% | 19.1 |
| Instruction2 | 27x | 7.8% | 26.1 |
| Instruction3 | 78x | 9.6% | 23.7 |
| Instruction4 | 49x | 9.4% | 24.9 |
| LLMLingua-2 w/o Chunk | 21x | 6.0% | 27.9 |
| **LLMLingua-2 (chunked)** | **2.6x** | **2.2%** | **36.7** |

Chunk-wise compression dramatically reduces hallucination (VR: 2.2% vs 6.0%) and improves downstream QA performance.

---

## 7. Key Contributions

1. **Task-agnostic formulation**: Compression as token classification rather than entropy-based filtering
2. **Data distillation**: GPT-4-based extractive compression dataset with quality control
3. **Bidirectional encoding**: XLM-RoBERTa captures full context for better token importance estimation
4. **Efficiency**: 3-6x faster compression, 8x less GPU memory, 1.6-2.9x end-to-end speedup
5. **Faithfulness**: Extractive-only approach prevents hallucination in compressed output

---

## Figures

**Figure 1:** Overview of LLMLingua-2 pipeline: data distillation from GPT-4 creates token-level labels, which train a bidirectional encoder for binary classification (preserve/discard).

**Figure 2:** GPT-4 instruction template used for data distillation, showing the five constraints enforced for extractive compression.

**Figure 3:** Distribution of compression ratios achieved by chunk-wise compression on MeetingBank, showing concentration around 2-3x.

**Figure 4:** Compression ratio vs. original context length on MeetingBank, showing that longer texts achieve higher compression.

**Figure 5:** Challenges in data annotation: (i) ambiguity in which tokens to keep, (ii) variation in valid compressions, (iii) reordering artifacts.

**Figure 6:** Visualization of context-aware compression at different ratios (2x, 3x, 5x), with color intensity indicating preservation priority.

**Figure 11-12:** Side-by-side comparison of LLMLingua vs LLMLingua-2 compressed outputs on BBH and GSM8K, showing LLMLingua-2 produces more coherent compressed text.

---

## Key References

1. Jiang et al. (2023). "LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models." EMNLP 2023.
2. Li et al. (2023). "Compressing Context to Enhance Inference Efficiency of Large Language Models." EMNLP 2023 (Selective Context).
3. Jiang et al. (2023). "LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression."
4. Conneau et al. (2020). "Unsupervised Cross-lingual Representation Learning at Scale." ACL 2020 (XLM-RoBERTa).
5. Devlin et al. (2019). "BERT: Pre-training of Deep Bidirectional Transformers." NAACL 2019.
6. Ge et al. (2024). "In-context Autoencoder for Context Compression in a Large Language Model." ICLR 2024.
7. Mu et al. (2023). "Learning to Compress Prompts with Gist Tokens." NeurIPS 2023.
8. Liu et al. (2024). "Lost in the Middle: How Language Models Use Long Contexts." TACL.
9. Hu et al. (2023). "MeetingBank: A Benchmark Dataset for Meeting Summarization."
10. Wei et al. (2022). "Chain of Thought Prompting Elicits Reasoning in Large Language Models." NeurIPS 2022.
