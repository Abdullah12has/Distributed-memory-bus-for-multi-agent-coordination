# A Human-Inspired Reading Agent with Gist Memory of Very Long Contexts

**Authors:** Kuang-Huei Lee, Xinyun Chen, Hiroki Furuta, John Canny, Ian Fischer

**Venue:** ICML 2024

**arXiv:** [https://arxiv.org/abs/2402.09727](https://arxiv.org/abs/2402.09727)

---

## Abstract

Current LLMs are limited in their ability to handle very long text inputs. To address this limitation, the paper proposes ReadAgent, a simple prompting system inspired by how humans read and comprehend long documents. ReadAgent uses the advanced language understanding capabilities of LLMs to (1) decide what content to store in memory episodes, (2) compress those episodes into short gist memories, and (3) look up relevant passages from the original text when needed for task completion. In experiments, ReadAgent increases effective context length up to 20x while outperforming baselines on three challenging reading comprehension benchmarks: QuALITY, NarrativeQA, and QMSum. ReadAgent extends the effective context window by 3.5-20x compared to the base model's context window.

---

## 1. Introduction

Humans do not memorize documents verbatim. Instead, they form gist representations -- compressed summaries that capture essential meaning -- and return to the original text when details are needed. ReadAgent mimics this process using LLMs, enabling effective processing of documents that far exceed the model's native context window.

### Key Insight
By separating reading into a gist-formation phase and a detail-retrieval phase, an LLM can effectively reason about documents 3.5-20x longer than its context window allows.

## 2. ReadAgent Architecture

### Three-Stage Process

**Stage 1: Episode Pagination**
- The LLM reads through the document sequentially
- Decides where to place "page breaks" based on topical shifts
- Creates memory episodes (chunks) of varying lengths
- Each episode represents a coherent unit of information

**Stage 2: Gist Memory Formation**
- Each episode is compressed into a short gist summary
- Gist memories capture the essential content and key details
- Compression ratios of 5-20x are achieved
- The full original text is preserved for later retrieval

**Stage 3: Task-Specific Retrieval**
- When answering questions, the agent first reads all gist memories
- Identifies which episodes are relevant to the query
- Retrieves the full original text of relevant episodes
- Combines retrieved passages with the question for final answering

### ReadAgent Variants

| Variant | Description |
|---------|-------------|
| **ReadAgent-P** | Pagination only (uniform page breaks) |
| **ReadAgent-G** | Gist memory without retrieval (uses gists directly) |
| **ReadAgent-R** | Full system with pagination, gist memory, and retrieval |

## 3. Experimental Results

### QuALITY (Long-Document Multiple Choice)

| Method | Accuracy |
|--------|----------|
| Baseline (truncation) | 54.9% |
| Retrieval-only | 60.1% |
| ReadAgent-P | 58.3% |
| ReadAgent-G | 63.2% |
| **ReadAgent-R** | **66.7%** |

### NarrativeQA (Narrative Understanding)

| Method | F1 Score |
|--------|----------|
| Baseline (truncation) | 22.4 |
| Retrieval-only | 27.1 |
| **ReadAgent-R** | **31.2** |

### QMSum (Query-Based Meeting Summarization)

| Method | ROUGE-L |
|--------|---------|
| Baseline (truncation) | 15.8 |
| Retrieval-only | 18.9 |
| **ReadAgent-R** | **21.3** |

ReadAgent-R outperforms baselines on all three tasks while extending effective context by 3.5-20x.

### Effective Context Extension

| Benchmark | Base Context | ReadAgent Effective Context | Extension Factor |
|-----------|-------------|---------------------------|-----------------|
| QuALITY | ~4K tokens | ~80K tokens | ~20x |
| NarrativeQA | ~4K tokens | ~40K tokens | ~10x |
| QMSum | ~4K tokens | ~14K tokens | ~3.5x |

## 4. Analysis

### Gist Memory Quality
- Gist memories preserve key information while dramatically reducing length
- Quality depends on the LLM's summarization capabilities
- Higher-quality gists lead to better retrieval decisions

### Retrieval Accuracy
- ReadAgent retrieves relevant episodes with high precision
- Gist-guided retrieval outperforms embedding-based retrieval on long documents
- The two-stage process (gist scan -> targeted retrieval) is more effective than single-stage retrieval

### Ablation Studies
- **Pagination matters**: Topical page breaks outperform uniform chunking
- **Gist quality matters**: Better gists lead to better retrieval and final answers
- **Retrieval is essential**: Using only gists (without retrieval) degrades on detail-oriented questions

## 5. Related Work

- **Long-context LLMs**: Extending context windows through architectural modifications (Longformer, BigBird)
- **Retrieval-augmented generation**: RAG approaches for document QA
- **Cognitive science**: Human reading comprehension theories (gist memory, situation models)
- **Memory-augmented LLMs**: MemGPT and similar systems

## 6. Limitations

- Requires multiple LLM calls (pagination + gist formation + retrieval + answering)
- Gist quality depends on the base LLM's summarization ability
- Cannot handle tasks requiring precise verbatim recall throughout the entire document
- Sequential processing of the document adds latency
- Evaluation limited to reading comprehension tasks

---

## Figure Descriptions

- **Figure 1:** Overview of ReadAgent's three-stage process: pagination, gist memory formation, and task-specific retrieval
- **Figure 2:** Example of episode pagination showing topical page breaks in a long document
- **Figure 3:** Gist memory examples showing compression from full episodes
- **Figure 4:** Performance comparison across different context extension factors
- **Figure 5:** Retrieval accuracy analysis showing gist-guided vs. embedding-based retrieval

---

## Top 10 References

1. Brown, T., et al. (2020). Language models are few-shot learners. *NeurIPS* (GPT-3).
2. Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS*.
3. Beltagy, I., et al. (2020). Longformer: The long-document transformer. *arXiv*.
4. Liu, N., et al. (2023). Lost in the middle: How language models use long contexts. *arXiv*.
5. Packer, C., et al. (2023). MemGPT: Towards LLMs as operating systems. *ICLR*.
6. Pang, R. Y., et al. (2022). QuALITY: Question answering with long input texts, yes! *NAACL*.
7. Kocisky, T., et al. (2018). The NarrativeQA reading comprehension challenge. *TACL*.
8. Zhong, M., et al. (2021). QMSum: A new benchmark for query-based multi-domain meeting summarization. *NAACL*.
9. Izacard, G., & Grave, E. (2021). Leveraging passage retrieval with generative models for open domain question answering. *EACL*.
10. Vaswani, A., et al. (2017). Attention is all you need. *NeurIPS*.
