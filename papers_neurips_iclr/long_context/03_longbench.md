# LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding

**Authors:** Yushi Bai, Xin Lv, Jiajie Zhang, Hongchang Lyu, Jiankai Tang, Zhidian Huang, Zhengxiao Du, Xiao Liu, Aohan Zeng, Lei Hou, Yuxiao Dong, Jie Tang, Juanzi Li

**Venue:** ACL 2024

**ArXiv:** [2308.14508](https://arxiv.org/abs/2308.14508)

---

## Abstract

This paper presents LongBench, the first bilingual, multitask benchmark for long context understanding, comprising 21 datasets across 6 task categories in both English and Chinese. The benchmark averages 6,711 words (English) and 13,386 characters (Chinese) per instance. Tasks span single-document and multi-document question answering, summarization, few-shot learning, synthetic tasks, and code completion. Evaluation of 8 language models reveals that commercial models outperform open-source alternatives, though all struggle with longer contexts. Scaled position embeddings and fine-tuning on longer sequences lead to substantial improvement.

---

## 1. Introduction

While long-context models have proliferated, comprehensive evaluation has lagged behind. LongBench fills this gap with bilingual coverage, diverse task types, and controlled length distributions.

## 2. Benchmark Design

### 2.1 Six Task Categories

| Category | Datasets | Description |
|----------|----------|-------------|
| **Single-Doc QA** | NarrativeQA, Qasper, MultiFieldQA-en/zh | Questions on lengthy documents |
| **Multi-Doc QA** | HotpotQA, 2WikiMultihopQA, MuSiQue, DuReader | Reasoning across multiple documents |
| **Summarization** | GovReport, QMSum, MultiNews, VCSUM | Key information extraction from long texts |
| **Few-shot Learning** | TREC, TriviaQA, SAMSum, LSHT | In-context learning with examples |
| **Synthetic Tasks** | PassageCount, PassageRetrieval-en/zh | Controlled evaluation scenarios |
| **Code Completion** | LCC, RepoBench-P | Repository-level code generation |

### 2.2 Dataset Statistics

- **Total instances**: 4,750 test instances
- **Average length (English)**: 6,711 words
- **Average length (Chinese)**: 13,386 characters
- **Evaluation metrics**: ROUGE-L, F1 scores, Edit Similarity, Accuracy (task-dependent)

### 2.3 Construction Approach

- 6 datasets extracted directly from original sources
- 10 datasets adapted from existing resources for long context evaluation
- 5 newly created and annotated datasets
- Two sampling strategies: random (LongBench) and uniform by length (LongBench-E)

## 3. Evaluation Framework

- Zero-shot assessment across 8 LLMs
- Models tested: GPT-3.5-Turbo-16k, Llama2-7B, ChatGLM2-6B, ChatGLM2-6B-32k, and others
- Greedy decoding for reproducibility
- Middle truncation strategy when inputs exceed model context windows
- Customized prompts for each task type

## 4. Key Findings

### 4.1 Model Performance

| Finding | Detail |
|---------|--------|
| Commercial > Open-source | GPT-3.5-Turbo-16k leads across most categories |
| Context extension helps | ChatGLM2-6B-32k showed 62% relative improvement over 6B base |
| All models degrade | Performance drops as context length increases for all models |

### 4.2 Context Compression Analysis

- Retrieval techniques help only weaker models
- Improvements of -2%, 21%, and -5% for three tested models (inconsistent)
- Summarization-based compression: mixed results, helps only on longer meeting transcripts

### 4.3 Task Correlation

Tasks within the same category showed high correlation, while PassageCount and code-related tasks exhibited lower correlations, indicating the benchmark evaluates diverse capabilities.

## 5. LongBench-E (Balanced Version)

A variant with evenly distributed context lengths across three bins:
- 0-4k tokens
- 4k-8k tokens
- 8k+ tokens

This isolates long-context modeling ability from task-specific capabilities by ensuring each length range is equally represented.

## 6. Figures

- **Figure 1**: Overview of LongBench task categories and dataset distribution.
- **Figure 2**: Performance comparison across 8 models on each task category.
- **Figure 3**: Performance degradation curves as context length increases for different models.
- **Figure 4**: Correlation matrix between task categories showing diversity of evaluation.

---

## References (Top 10)

1. Chen et al. (2023) - Extending Context Window of Large Language Models via Positional Interpolation
2. Press et al. (2022) - Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation
3. Tay et al. (2022) - Efficient Transformers: A Survey
4. Shaham et al. (2023) - ZeroSCROLLS: A Zero-Shot Benchmark for Long Text Understanding
5. An et al. (2023) - L-Eval: Instituting Standardized Evaluation for Long Context Language Models
6. Dai et al. (2019) - Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context
7. Sun et al. (2021) - Do Long-Range Language Models Actually Use Long-Range Context?
8. Hendrycks et al. (2021) - Measuring Massive Multitask Language Understanding (MMLU)
9. Srivastava et al. (2023) - Beyond the Imitation Game Benchmark (BIG-bench)
10. Beltagy et al. (2020) - Longformer: The Long-Document Transformer
