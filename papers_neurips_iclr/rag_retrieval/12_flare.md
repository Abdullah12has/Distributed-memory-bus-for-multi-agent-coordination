# Active Retrieval Augmented Generation (FLARE)

**Authors:** Zhengbao Jiang, Frank F. Xu, Luyu Gao, Zhiqing Sun, Qian Liu, Jane Dwivedi-Yu, Yiming Yang, Jamie Callan, Graham Neubig

**Venue:** EMNLP 2023

**ArXiv:** [2305.06983](https://arxiv.org/abs/2305.06983)

---

## Abstract

Despite the remarkable ability of large language models (LLMs) to generate fluent text, they often hallucinate and produce factually inaccurate content. While retrieval-augmented generation approaches help by retrieving external knowledge, they typically retrieve only once based on the initial input. This paper proposes Forward-Looking Active REtrieval augmented generation (FLARE), which iteratively uses a prediction of the upcoming sentence to anticipate future content, uses it as a query to retrieve relevant documents if it contains low-confidence tokens, and regenerates the sentence with the retrieved information. Experiments on four long-form knowledge-intensive generation tasks demonstrate that FLARE achieves superior or competitive performance across all tasks.

---

## 1. Introduction

Existing RAG methods retrieve once at the beginning, which is insufficient for long-form generation requiring diverse information across different topics. FLARE addresses this by interleaving retrieval and generation throughout the output creation process.

## 2. Core Principles

1. LMs should only retrieve information when they lack necessary knowledge, to avoid unnecessary retrieval that introduces noise
2. Queries should anticipate future content needs rather than reflect past context

## 3. Methodology

### 3.1 FLARE Algorithm

The method operates iteratively at sentence level:
1. Generate a temporary next sentence without retrieved documents
2. Check token confidence levels against threshold theta
3. If low-confidence tokens detected, use the sentence as a retrieval query
4. Retrieve relevant documents and regenerate the sentence with retrieved context
5. Repeat until generation is complete

### 3.2 Two Variants

**FLARE_instruct:**
- Uses few-shot prompting to generate explicit "[Search(query)]" tokens
- LLM learns to issue search commands during generation

**FLARE_direct:**
- Directly uses generated sentences as implicit queries
- Offers two query formulation methods:
  - **Implicit**: Masks low-confidence tokens in generated sentence, uses remaining as query
  - **Explicit**: Converts generated sentence into a question for retrieval

## 4. Experimental Results

### 4.1 Datasets (4 long-form tasks)

| Dataset | Task Type | Metric |
|---------|-----------|--------|
| 2WikiMultihopQA | Multi-hop reasoning | Exact Match |
| StrategyQA | Commonsense reasoning | Accuracy |
| ASQA | Long-form QA with ambiguity | EM, ROUGE-L, D-R |
| WikiAsp | Open-domain summarization | ROUGE-1/2/L |

### 4.2 Key Results

On 2WikiMultihopQA:
- FLARE_direct: 51.0% exact match
- Question decomposition baseline: 47.8%
- Single-retrieval RAG: lower performance

### 4.3 Important Findings

1. **Forward-looking > Past-context retrieval**: Using next sentence for queries substantially outperformed previous-sentence retrieval
2. **Selective retrieval benefits**: Performance plateaus around 40-80% retrieval rate; unnecessary retrieval introduces noise
3. **Query formulation**: Masking low-confidence tokens improved retrieval accuracy by eliminating potentially erroneous content
4. **Confidence threshold**: theta = 0.5-0.7 generally optimal; too low triggers excessive retrieval, too high triggers too little

## 5. Limitations

- Does not provide significant gains on shorter-form tasks (Wizard of Wikipedia)
- Struggles with difficult evaluation scenarios (ELI5)
- Increases computational overhead through multiple LM forward passes
- Relies on token-level confidence as a proxy for knowledge uncertainty

## 6. Figures

- **Figure 1**: Comparison of single-time retrieval, previous-context retrieval, and FLARE's forward-looking active retrieval approach.
- **Figure 2**: Example of FLARE in action, showing how low-confidence tokens trigger retrieval and how the regenerated sentence differs from the initial prediction.
- **Figure 3**: Performance curves as a function of retrieval frequency showing the optimal retrieval rate plateau.

---

## References (Top 10)

1. Lewis et al. (2020) - Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
2. Khandelwal et al. (2020) - Generalization through Memorization: Nearest Neighbor Language Models
3. Borgeaud et al. (2022) - Improving Language Models by Retrieving from Trillions of Tokens
4. Press et al. (2022) - Measuring and Narrowing the Compositionality Gap in Language Models
5. Trivedi et al. (2022) - Interleaving Retrieval with Chain-of-Thought Reasoning
6. Ram et al. (2023) - In-context Retrieval-Augmented Language Models
7. Gao et al. (2022) - Precise Zero-Shot Dense Retrieval Without Relevance Labels
8. Kadavath et al. (2022) - Language Models (Mostly) Know What They Know
9. Brown et al. (2020) - Language Models are Few-Shot Learners
10. Wei et al. (2022) - Chain of Thought Prompting Elicits Reasoning in Large Language Models
