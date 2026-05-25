# RECOMP: Improving Retrieval-Augmented LMs with Compression and Selective Augmentation

**Authors:** Fangyuan Xu, Weijia Shi, Eunsol Choi

**Venue:** arXiv 2023 (cs.CL)

**ArXiv:** [2310.04408](https://arxiv.org/abs/2310.04408)

---

## Abstract

We propose RECOMP, a method to compress retrieved documents into textual summaries prior to in-context integration for retrieval-augmented language models. Two compressors are developed: one that extracts relevant sentences and another that synthesizes information into summaries. The approach achieves a compression rate of as low as 6% with minimal loss in performance on language modeling and open-domain question answering tasks. The compressors can selectively determine when retrieved documents lack relevance, potentially returning empty output rather than unhelpful information.

---

## 1. Introduction

Retrieved documents in retrieval-augmented LMs typically span hundreds of words, creating three key challenges:
- Increased computational costs during inference
- Language models struggling to identify relevant information in lengthy contexts
- Irrelevant retrieved documents confusing models and degrading performance

RECOMP introduces an intermediate processing step: compress retrieved documents into concise textual summaries before prepending them to model inputs.

---

## 2. Proposed Compressors

### 2.1 Extractive Compressor

A dual-encoder model that selects relevant sentences from retrieved documents by computing similarity between input queries and candidate sentences. Initialized with Contriever (110M parameters) and trained via contrastive learning.

**Training:** Positive sentences are those that improve LM output likelihood; negatives are high-retrieval sentences below a performance threshold. Contrastive loss maximizes similarity between input-positive pairs while minimizing negative pairs.

### 2.2 Abstractive Compressor

An encoder-decoder model (initialized from T5-large, 775M parameters) that generates synthetic summaries from multiple documents. Training employs symbolic distillation from GPT-3.5-turbo, selecting summaries that maximize end-task performance.

### 2.3 Selective Augmentation

Both compressors implement selective augmentation -- outputting empty strings when retrieved documents are irrelevant or unhelpful. Training optimizes for:
- **Conciseness:** Minimal token count
- **Effectiveness:** Improved end-task performance when summary is prepended
- **Faithfulness:** Summaries remain true to source documents

---

## 3. Experimental Results

### 3.1 Language Modeling (WikiText-103)

Evaluated on GPT-2 (117M), GPT2-XL (1.5B), and GPT-J (6B):
- **Extractive approach:** 25% compression ratio with minimal performance drop
- **Abstractive approach:** Achieves highest compression through selective augmentation (prepending summaries to only 33% of examples)

### 3.2 Open-Domain QA

| Task | Method | Compression Ratio | Performance Loss |
|------|--------|-------------------|------------------|
| NQ | Abstractive | 5% tokens | 2 EM points |
| TriviaQA | Abstractive | 5% tokens | 3.7 EM points |
| HotpotQA | Extractive | 11% tokens | 2.4 EM points |

### 3.3 Oracle Performance

Oracle compression methods reveal substantial room for improvement -- achieving compression rates as low as 6% while maintaining or improving performance over full document prepending.

---

## 4. Analysis

### 4.1 Evidence Utilization

Models tend to copy answers verbatim from in-context documents:
- Top 5 documents increase incorrect copying (81%) versus top 1 (51%)
- GPT-3 summaries inadvertently increase incorrect copying (85%)
- Trained compressors reduce this to 39%

### 4.2 Faithfulness and Comprehensiveness

Manual evaluation of abstractive summaries:

| Source | NQ Faithful | TriviaQA Faithful | HotpotQA Faithful |
|--------|-------------|-------------------|-------------------|
| GPT-3.5 | 83% | 83% | 50% |
| RECOMP | 80% | 77% | 40% |

Both struggle with multi-hop reasoning tasks (HotpotQA).

### 4.3 Transferability

Compressors trained on one LM transfer to larger models. For language modeling, compressors trained on GPT-2 transfer effectively to GPT2-XL and GPT-J. Transfer to different architectures (LLaMA) shows degradation but maintains 5% compression with <5 EM point drops.

---

## 5. Data Statistics

| Dataset | Training Examples | Filtered % | Empty Summary % |
|---------|-------------------|------------|-----------------|
| NQ | 39,466 | 50% | 25% |
| TriviaQA | 48,322 | 32% | 16% |
| HotpotQA | 26,556 | 42% | 4% |
| WikiText | 38,410 | 0% | 24% |

---

## 6. Implementation Details

- Extraction uses top 20 sentences from top 5 retrieved documents
- BM25 retriever for language modeling; Contriever MS-MARCO for QA tasks
- Documents truncated to 100-word non-overlapping chunks
- Wikipedia page titles prepended to extracted sentences for decontextualization

---

## 7. Limitations

- Abstractive compressors struggle with multi-document synthesis (HotpotQA)
- Manual evaluation reveals lower faithfulness for complex tasks
- Extractive approach uses fixed sentence counts; adaptive extraction could improve results
- Training requires access to base LM for scoring -- not applicable to truly black-box systems

---

## Figures

- **Figure 1:** Overview of RECOMP pipeline showing retriever, compressor, and LM stages with both extractive and abstractive compression paths.
- **Figure 2:** Compression rates vs. performance across different tasks, showing the Pareto frontier.
- **Figure 3:** Distribution of abstractive summary lengths, demonstrating automatic selective augmentation.

---

## Key References

1. Khandelwal et al. (2020) - kNN-LM
2. Borgeaud et al. (2022) - RETRO
3. Izacard & Grave (2021) - FiD (Fusion-in-Decoder)
4. Raffel et al. (2020) - T5
5. Izacard et al. (2022) - Contriever
6. Brown et al. (2020) - GPT-3
7. West et al. (2022) - Symbolic distillation
8. Shi et al. (2023) - Irrelevant context effects on LMs
9. Wang et al. (2022) - Self-Instruct
10. Kwiatkowski et al. (2019) - Natural Questions
