# Toolformer: Language Models Can Teach Themselves to Use Tools

**Authors:** Timo Schick, Jane Dwivedi-Yu, Roberto Dessi, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Cancedda, Thomas Scialom

**Venue:** NeurIPS 2023 (originally arXiv preprint, February 2023)

**arXiv:** [https://arxiv.org/abs/2302.04761](https://arxiv.org/abs/2302.04761)

---

## Abstract

Language models (LMs) exhibit remarkable abilities to solve new tasks from just a few examples or textual instructions, especially at scale. They also, sometimes, struggle with basic functionality, such as arithmetic or factual lookup, where much simpler and smaller models excel. This paper shows that LMs can teach themselves to use external tools via simple APIs and achieve the best of both worlds. Toolformer is trained to decide which APIs to call, when to call them, what arguments to pass, and how to best incorporate the results into future token prediction. This is done in a self-supervised way, requiring nothing more than a handful of demonstrations for each API. Toolformer incorporates a range of tools, including a calculator, a Q&A system, a search engine, a translation system, and a calendar, and achieves substantially improved zero-shot performance across a variety of downstream tasks, often competitive with much larger models, without sacrificing its core language modeling abilities.

---

## 1. Introduction

The paper addresses a fundamental tension: LLMs are powerful general reasoners but struggle with specific capabilities like arithmetic, factual retrieval, and temporal reasoning that simple tools handle easily. Prior work on tool-augmented LMs required large amounts of human annotations or was limited to specific tasks. Toolformer addresses this by enabling self-supervised learning of tool use.

**Key desiderata:**
- Learn tool use in a self-supervised manner (no human annotations at scale)
- Not sacrifice general language modeling ability
- Autonomously decide when and how to use tools

## 2. Approach

### Self-Supervised Training Pipeline

The training process consists of three steps:

**Step 1: Sample API Calls.** Given a dataset of text, the model uses in-context learning with a few demonstrations to annotate positions where API calls might be useful, generating candidate API call insertions.

**Step 2: Execute API Calls.** Each sampled API call is executed to obtain results.

**Step 3: Filter Based on Usefulness.** API calls are retained only if they reduce the model's perplexity on subsequent tokens. Formally, an API call is kept if it satisfies a filtering criterion based on weighted cross-entropy loss reduction exceeding threshold tau_f.

### API Call Representation

API calls are encoded as special token sequences:
- Without result: `<API>name(input)</API>`
- With result: `<API>name(input) -> result</API>`

### Filtering Criterion

An API call is considered helpful if "providing it with both the input and the output makes it easier for the model to predict future tokens, compared to not receiving the API call at all."

## 3. Tools

Five external tools are integrated:

| Tool | Description | API Format |
|------|-------------|------------|
| **Calculator** | Basic arithmetic operations | `[Calculator(expression)]` |
| **Q&A System** | Atlas-based question answering | `[QA(question)]` |
| **Wikipedia Search** | BM25 retriever over Wikipedia | `[WikiSearch(query)]` |
| **Machine Translation** | NLLB model (200 languages) | `[MT(text, target_lang)]` |
| **Calendar** | Current date retrieval | `[Calendar()]` |

## 4. Experiments

### 4.1 Experimental Setup

- Base model: GPT-J (6.7B parameters)
- Training data: Subset of CCNet
- Finetuning: Standard language modeling on augmented data (API calls inserted)

### 4.2 Downstream Task Performance

| Task | Toolformer (6.7B) | GPT-3 (175B) | OPT (66B) |
|------|-------------------|-------------|----------|
| SQuAD | 33.8 | 29.9 | - |
| Google-RE | 38.0 | 31.5 | - |
| T-REx | 53.5 | 39.8 | 30.1 |
| LAMA (avg) | 41.8 | 33.7 | - |
| Math (ASDiv) | 40.4 | 27.5 | 13.5 |
| Math (SVAMP) | 29.4 | 15.5 | 5.2 |
| Math (MAWPS) | 44.0 | 19.8 | 7.9 |
| TempLAMA | 20.4 | 14.2 | 6.4 |
| WebQS | 26.3 | 29.0 | 18.6 |
| NQ | 22.1 | 29.9 | 21.8 |
| Multilingual QA (avg) | 14.1 | - | 7.2 |

**Key finding:** 6.7B Toolformer outperforms 175B GPT-3 on LAMA and math tasks.

### 4.3 Language Modeling Performance

Perplexity on WikiText and CCNet showed that adding API calls comes without a cost in terms of perplexity for language modeling without any API calls. The model maintains its core language modeling abilities.

### 4.4 Scaling Laws

- Tool-use ability emerges at approximately **775M parameters**
- Smaller models show minimal benefit from tool augmentation
- Larger models develop improved capability to leverage external tools

## 5. Analysis

### Decoding Strategy
- Greedy decoding is sufficient for API calls
- The model uses appropriate tools approximately **98% of the time** for well-suited tasks

### Data Quality
- Perplexity-based filtering successfully identifies useful API calls
- Higher filtering thresholds produce fewer but more accurate annotations

## 6. Related Work

The paper connects to three threads:
- **LM pretraining and prompting**: Building on GPT-3 and PaLM capabilities
- **Tool use in NLP**: Extending TALM, WebGPT, and LaMDA approaches
- **Bootstrapping and self-training**: Using self-generated data for improvement

## 7. Limitations

- **No tool chaining**: Cannot compose multiple API calls sequentially
- **No interactive use**: Single-turn tool use, no multi-step dialogue
- **Sample efficiency**: Requires large training corpus for self-supervised annotation
- **Prompt sensitivity**: Tool use patterns depend on few-shot demonstrations
- **Limited tool set**: Five tools tested; unclear how well approach scales

---

## Figure Descriptions

- **Figure 1:** Overview of the Toolformer approach showing how the model annotates text with API calls, filters useful ones, and finetunes
- **Figure 2:** Examples of model-generated API calls across different tools (calculator, Q&A, search, translation, calendar)
- **Figure 3:** Scaling laws showing tool-use emergence at ~775M parameters
- **Figure 4:** Perplexity comparison with and without API calls

---

## Top 10 References

1. Brown, T., et al. (2020). Language models are few-shot learners. *NeurIPS* (GPT-3).
2. Chowdhery, A., et al. (2022). PaLM: Scaling language modeling with Pathways. *arXiv*.
3. Komeili, K., et al. (2022). Internet-augmented dialogue generation. *ACL*.
4. Parisi, A., et al. (2022). TALM: Tool augmented language models. *arXiv*.
5. Thoppilan, R., et al. (2022). LaMDA: Language models for dialog applications. *arXiv*.
6. Gao, L., et al. (2022). PAL: Program-aided language models. *arXiv*.
7. Nakano, R., et al. (2021). WebGPT: Browser-assisted question answering with human feedback. *arXiv*.
8. Izacard, G., et al. (2022). Atlas: Few-shot learning with retrieval augmented language models. *arXiv*.
9. Wang, B., & Komatsuzaki, A. (2021). GPT-J-6B: A 6 billion parameter autoregressive language model.
10. Yao, S., et al. (2022). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
