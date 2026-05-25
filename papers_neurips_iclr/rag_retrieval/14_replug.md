# REPLUG: Retrieval-Augmented Black-Box Language Models

**Authors:** Weijia Shi, Sewon Min, Michihiro Yasunaga, Minjoon Seo, Rich James, Mike Lewis, Luke Zettlemoyer, Wen-tau Yih

**Venue:** arXiv preprint (cs.CL), 2023

**ArXiv:** [2301.12652](https://arxiv.org/abs/2301.12652)

---

## Abstract

This paper introduces REPLUG, a retrieval-augmented language modeling framework that treats the language model (LM) as a black box and augments it with a tuneable retrieval model. Unlike prior retrieval-augmented LMs that train language models with special cross-attention mechanisms, REPLUG simply prepends retrieved documents to the input for the frozen LM. This simple design can be easily applied to any existing retrieval and language models. Furthermore, the paper shows that the LM can be used to supervise the retrieval model, which can then find documents that help the LM make better predictions. Experiments demonstrate that REPLUG with the tuned retriever significantly improves the performance of GPT-3 (175B) on language modeling by 6.3%, as well as the performance of Codex on five-shot MMLU by 5.1%.

---

## 1. Introduction

Prior retrieval-augmented LMs require access to model internals (cross-attention layers, gradients), limiting applicability to proprietary models. REPLUG treats the LM as a frozen black box, only requiring the ability to prepend text to inputs and read output probabilities.

## 2. Methodology

### 2.1 REPLUG (Basic)

- Uses an off-the-shelf dense retriever (Contriever) with frozen parameters
- Retrieves top-k relevant documents for each input
- Prepends each document separately to the input
- Ensembles probability outputs across multiple forward passes

**Ensemble formula**: p(y|x, D') = sum of p(y|d concatenated with x) * lambda(d, x), where lambda weights are based on retrieval similarity scores.

### 2.2 REPLUG LSR (LM-Supervised Retrieval)

- Trains the retriever using LM perplexity as supervision signal
- Minimizes KL divergence between retrieval likelihood and LM-computed document quality distribution
- The LM scores each document by the perplexity improvement it provides
- Adapts retrieval specifically to the target language model

### 2.3 Technical Details

- Training data: 800K sequences from the Pile
- Document corpus: 36M documents
- Retrieval: top-10 documents per query
- Each document prepended separately (not concatenated together)

## 3. Experimental Results

### 3.1 Language Modeling (Pile Dataset)

| Model | Baseline BPB | REPLUG BPB | REPLUG LSR BPB | Relative Improvement |
|-------|-------------|------------|----------------|---------------------|
| GPT-3 Davinci (175B) | 0.749 | 0.718 | 0.702 | 6.3% |
| GPT-2 (1.5B) | 1.136 | 1.100 | 1.077 | 5.2% |
| OPT (66B) | 0.815 | 0.790 | 0.773 | 5.2% |

Consistent 4-7% gains across model sizes and families.

### 3.2 MMLU (5-shot)

| Model | Baseline | REPLUG LSR | Improvement |
|-------|----------|------------|-------------|
| Codex | 67.7% | 72.8% | +5.1% |

Achieves comparable results to Flan-PaLM (540B).

### 3.3 Open-Domain QA

| Dataset | Baseline Codex | REPLUG LSR | Improvement |
|---------|---------------|------------|-------------|
| Natural Questions | - | +12.0% | Over baseline |
| TriviaQA | - | +5.0% | Over baseline |

## 4. Key Findings

1. **Performance gains are not ensemble effects alone** -- relevant retrieval is crucial; random documents do not help
2. **Improvements consistent across diverse model architectures** (GPT-2, GPT-3, OPT, BLOOM)
3. **Rare entity handling** significantly benefits from retrieved context
4. **Gains increase with more retrieved documents** (tested up to 10)
5. **LSR training adapts retriever to specific LM characteristics**, providing additional gains over off-the-shelf retrieval

## 5. Design Advantages

1. **Black-box compatibility**: Works with any LM that accepts text input and produces probabilities
2. **No model modification**: No special cross-attention or architectural changes needed
3. **Modular**: Retriever and LM can be independently upgraded
4. **Scalable**: Benefits extend to models >100B parameters

## 6. Limitations

- Lacks interpretability regarding when models rely on retrieved versus parametric knowledge
- Multiple forward passes (one per retrieved document) increase inference cost
- Requires access to output probabilities for LSR training

## 7. Figures

- **Figure 1**: REPLUG architecture showing document retrieval, separate prepending to input, and probability ensemble.
- **Figure 2**: REPLUG LSR training loop where LM perplexity scores supervise retriever updates.
- **Figure 3**: Performance improvement curves as a function of the number of retrieved documents.

---

## References (Top 10)

1. Brown et al. (2020) - Language Models are Few-Shot Learners (GPT-3)
2. Izacard et al. (2022) - Atlas: Few-shot Learning with Retrieval Augmented Language Models
3. Borgeaud et al. (2022) - Improving Language Models by Retrieving from Trillions of Tokens (RETRO)
4. Khandelwal et al. (2020) - Generalization through Memorization: Nearest Neighbor Language Models
5. Gao et al. (2020) - The Pile: An 800GB Dataset of Diverse Text for Language Modeling
6. Izacard et al. (2022) - Unsupervised Dense Information Retrieval with Contrastive Learning (Contriever)
7. Karpukhin et al. (2020) - Dense Passage Retrieval for Open-Domain Question Answering
8. Lewis et al. (2020) - Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
9. Chowdhery et al. (2022) - PaLM: Scaling Language Modeling with Pathways
10. Johnson et al. (2019) - Billion-Scale Similarity Search with GPUs (FAISS)
