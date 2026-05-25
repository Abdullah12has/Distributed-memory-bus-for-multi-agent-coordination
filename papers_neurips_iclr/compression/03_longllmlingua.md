# LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression

**Authors:** Huiqiang Jiang, Qianhui Wu, Xufang Luo, Dongsheng Li, Chin-Yew Lin, Yuqing Yang, Lili Qiu

**Venue:** ACL 2024

**arXiv:** [2310.06839](https://arxiv.org/abs/2310.06839)

---

## Abstract

Large language models face three key challenges when processing lengthy contexts: (1) higher computational/financial costs, (2) performance degradation with increased context length, and (3) position bias ("lost in the middle" phenomenon). LongLLMLingua addresses these by introducing question-aware prompt compression. The method uses conditional perplexity to rank document relevance, contrastive perplexity for fine-grained token selection, document reordering to mitigate position bias, dynamic compression ratios, and subsequence recovery for post-processing. On NaturalQuestions, it achieves up to 21.4% performance improvement with ~4x token reduction using GPT-3.5-Turbo. On LongBench at 3x compression, it scores 48.8 vs 44.0 for original prompts. End-to-end latency accelerates 1.4x-2.6x for 2x-6x compression ratios, with up to 94% cost reduction on LooGLE.

---

## 1. Introduction

Long-context scenarios are increasingly common in LLM applications: retrieval-augmented generation concatenates multiple retrieved documents, few-shot learning uses many demonstrations, and agents accumulate lengthy interaction histories. Three problems arise:

1. **Cost**: Processing 10K+ tokens is expensive (quadratic attention)
2. **"Lost in the Middle"**: LLMs attend more to the beginning and end of context, missing information placed in the middle (Liu et al., 2024)
3. **Noise sensitivity**: Irrelevant context actively degrades performance, not just wastes computation

LongLLMLingua extends LLMLingua with question-aware compression strategies that selectively preserve query-relevant information while aggressively compressing irrelevant content.

---

## 2. Method

### 2.1 Question-Aware Coarse-Grained Compression

Documents are ranked by their relevance to the question using conditional perplexity:

$$\text{score}(x_k^{doc}) = \text{PPL}(x^{que} | x_k^{doc})$$

A **restrictive statement** is appended to the question (e.g., "We can get the answer to this question in the given documents") to strengthen the context-document association.

Low-relevance documents are dropped entirely before fine-grained compression begins.

### 2.2 Question-Aware Fine-Grained Compression

**Contrastive perplexity** measures the distribution shift caused by conditioning on the question:

$$\text{CPL}(x_i) = \frac{p(x_i | x_{<i}, x^{que})}{p(x_i | x_{<i})}$$

This is mathematically equivalent to conditional pointwise mutual information (PMI). Tokens with high contrastive perplexity are most relevant to the question and are preserved.

### 2.3 Document Reordering

After compression, documents are reordered by their relevance scores, placing the most question-relevant documents at prominent positions (beginning or end of context) where LLMs attend more effectively. This directly addresses the "lost in the middle" problem.

### 2.4 Dynamic Compression Ratios

Different documents receive different compression budgets based on relevance:
- High-relevance documents: lower compression (more tokens retained)
- Low-relevance documents: higher compression (fewer tokens retained)

This allocates the token budget where it matters most.

### 2.5 Subsequence Recovery

A post-processing step that matches token sequences from the LLM's output (generated from compressed prompts) back to the original uncompressed text. This recovers entity names, numbers, and specific details that may have been altered during tokenization of the compressed text.

---

## 3. Experimental Setup

### Datasets
- **NaturalQuestions**: 20 retrieved documents per question, answer position varied (1st-20th)
- **LongBench**: 6 task categories (SingleDoc QA, MultiDoc QA, Summarization, Few-Shot, Synthetic, Code)
- **LooGLE**: Long-context benchmark

### Target LLMs
- GPT-3.5-Turbo
- LongChat-13B-16K

### Compression Model
- LLaMA-2-7B-Chat

### Baselines
- BM25 retrieval
- SBERT retrieval
- OpenAI embeddings retrieval
- Gzip-based retrieval
- Selective Context
- LLMLingua

---

## 4. Results

### 4.1 NaturalQuestions (20 documents)

#### 2x Compression Constraint

| Method | 1st | 5th | 10th | 15th | 20th | Reorder | Tokens | Ratio | Latency | Speedup |
|---|---|---|---|---|---|---|---|---|---|---|
| SBERT | 72.5 | 67.9 | 63.3 | 65.0 | 66.2 | 68.7 | 1,549 | 1.9x | 2.2s | 1.9x |
| OpenAI | 73.0 | 65.6 | 66.5 | 65.4 | 65.5 | 69.9 | 1,550 | 1.9x | 4.9s | 0.8x |
| Selective-Context | 45.4 | 39.0 | 33.8 | 33.5 | 41.5 | -- | 1,478 | 2.0x | 7.4s | 0.6x |
| LLMLingua | 39.7 | 39.5 | 40.4 | 37.1 | 42.3 | 41.5 | 1,410 | 2.1x | 2.8s | 1.5x |
| **LongLLMLingua** | **77.2** | **72.9** | **70.8** | **70.5** | **70.6** | **76.2** | 1,429 | 2.1x | 2.9s | 1.4x |
| Original Prompt | 75.7 | 57.3 | 54.1 | 55.4 | 63.1 | -- | 2,946 | -- | 4.1s | -- |

LongLLMLingua surpasses the original prompt at every answer position, achieving 77.2% when the answer is in the 1st document vs 75.7% for the full prompt.

#### 4x Compression Constraint

| Method | 1st | 5th | 10th | 15th | 20th | Reorder | Tokens | Ratio |
|---|---|---|---|---|---|---|---|---|
| SBERT | 66.9 | 61.1 | 59.0 | 61.2 | 60.3 | 64.4 | 808 | 3.6x |
| Selective-Context | 31.4 | 19.5 | 24.7 | 24.1 | 43.8 | -- | 791 | 3.7x |
| LLMLingua | 25.5 | 27.5 | 23.5 | 26.5 | 30.0 | 27.0 | 775 | 3.8x |
| **LongLLMLingua** | **75.0** | **71.8** | **71.2** | **71.2** | **74.7** | **75.5** | 748 | 3.9x |

At 4x compression, LongLLMLingua maintains 75% accuracy while LLMLingua drops to 27%.

### 4.2 LongBench

#### 3,000-token Constraint

| Method | SingleDoc | MultiDoc | Summ. | FewShot | Synth. | Code | AVG | Tokens | Ratio |
|---|---|---|---|---|---|---|---|---|---|
| Original | 39.7 | 38.7 | 26.5 | 67.0 | 37.8 | 54.2 | 44.0 | 10,295 | -- |
| BM25 | 32.3 | 34.3 | 25.3 | 57.9 | 45.1 | 48.9 | 40.6 | 3,417 | 3x |
| SBERT | 35.3 | 37.4 | 26.7 | 63.4 | 51.0 | 34.5 | 41.4 | 3,399 | 3x |
| LLMLingua | 31.8 | 37.5 | 26.2 | 67.2 | 8.3 | 53.2 | 37.4 | 3,421 | 3x |
| **LongLLMLingua** | **40.7** | **46.2** | **27.2** | **70.6** | **53.0** | **55.2** | **48.8** | 3,283 | 3x |

LongLLMLingua at 3x compression (48.8) exceeds the original uncompressed prompt (44.0) by 4.8 points, demonstrating that removing noise improves performance.

#### 2,000-token Constraint

| Method | SingleDoc | MultiDoc | Summ. | FewShot | Synth. | Code | AVG |
|---|---|---|---|---|---|---|---|
| Original | 39.7 | 38.7 | 26.5 | 67.0 | 37.8 | 54.2 | 44.0 |
| LLMLingua | 22.4 | 32.1 | 24.5 | 61.2 | 10.4 | 56.8 | 34.6 |
| **LongLLMLingua** | **39.9** | **43.2** | **27.4** | **69.8** | **53.0** | **56.7** | **48.3** |

### 4.3 Ablation Study (NaturalQuestions, 2x constraint)

| Method | 1st | 5th | 10th | 15th | 20th |
|---|---|---|---|---|---|
| LongLLMLingua (Full) | 77.2 | 72.9 | 70.8 | 70.5 | 70.6 |
| w/o Question-awareness | 42.1 | 40.3 | 39.7 | 40.1 | 40.3 |
| w/ SBERT (coarse) | 73.2 | 68.5 | 65.7 | 66.1 | 66.7 |
| w/o Restrictive statement | 75.1 | 72.2 | 70.3 | 70.3 | 70.2 |
| w/o Question-aware Fine-grained | 75.8 | 71.0 | 68.9 | 68.4 | 69.3 |
| w/o Dynamic Compression Ratio | 74.4 | 70.7 | 68.7 | 67.9 | 68.1 |
| w/o Subsequence Recovery | 76.7 | 71.7 | 69.4 | 69.3 | 69.7 |
| w/ Document Reordering | 76.2 | 76.2 | 76.2 | 76.2 | 76.2 |
| w/ GPT2-small | 74.6 | 71.7 | 70.1 | 69.8 | 68.5 |
| LLMLingua (baseline) | 39.7 | 39.5 | 40.4 | 37.1 | 42.3 |

**Key finding**: Removing question-awareness drops performance from 77.2 to 42.1 (35.1 point drop), confirming it is the most critical component. Document reordering eliminates position dependency entirely (76.2% at all positions).

---

## 5. Latency and Cost

End-to-end latency improvements on NaturalQuestions:
- 2x compression: 1.4x speedup
- 4x compression: 2.0-2.4x speedup
- 6x compression: 2.6x speedup

LooGLE benchmark: 94% cost reduction with maintained performance.

---

## 6. Limitations

1. **Query-dependent compression**: Each new question requires re-compressing the context, preventing caching of compressed representations
2. **Computational overhead**: Question-aware scoring roughly doubles compression time compared to LLMLingua
3. **Subtle relationships**: May struggle when the connection between context and query requires complex reasoning rather than lexical/semantic overlap

---

## Figures

**Figure 1:** (a) Performance degrades as noise (irrelevant documents) increases in the prompt. Documents kept based on ground-truth relevance vs. LongLLMLingua relevance scores show the method effectively identifies relevant content. (b) "Lost in the middle" phenomenon: LLM performance varies based on where relevant information appears in the prompt, with U-shaped accuracy curves.

**Figure 2:** Framework of LongLLMLingua showing the pipeline from question-aware coarse-grained document ranking, through fine-grained contrastive perplexity-based token selection, dynamic ratio allocation, and subsequence recovery. Gray italic components are inherited from LLMLingua.

**Figure 3:** (a) Recall distribution comparison across retrieval methods on NaturalQuestions. LongLLMLingua achieves highest recall. (b) Standard perplexity vs contrastive perplexity for individual tokens, showing contrastive perplexity better identifies question-relevant tokens.

**Figure 4:** Subsequence recovery example: red text shows original content, blue shows tokenized result using LLaMA-2-7B tokenizer. The recovery step maps compressed-prompt-based output back to original text spans.

---

## Key References

1. Liu et al. (2024). "Lost in the Middle: How Language Models Use Long Contexts." TACL 12:157-173.
2. Jiang et al. (2023). "LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models." EMNLP 2023.
3. Li et al. (2023). "Compressing Context to Enhance Inference Efficiency of Large Language Models." EMNLP 2023 (Selective Context).
4. Lewis et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." NeurIPS 2020.
5. Mu et al. (2023). "Learning to Compress Prompts with Gist Tokens." NeurIPS 2023.
6. Ge et al. (2024). "In-context Autoencoder for Context Compression in a Large Language Model." ICLR 2024.
7. Kwiatkowski et al. (2019). "Natural Questions: A Benchmark for Question Answering Research." TACL 7:452-466.
8. Reimers & Gurevych (2019). "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." EMNLP 2019.
9. Xu et al. (2024). "RECOMP: Improving Retrieval-Augmented LMs with Context Compression and Selective Augmentation." ICLR 2024.
10. Chevalier et al. (2023). "Adapting Language Models to Compress Contexts." EMNLP 2023 (AutoCompressor).
