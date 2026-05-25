# SCM: Self-Controlled Memory Framework for Large Language Models

**Authors:** Bing Wang, Xinnian Liang, Jian Yang, Hui Huang, Shuangzhi Wu, Peihao Wu, Lu Lu, Zejun Ma, Zhoujun Li

**Venue:** DASFAA 2025 (main conference)

**arXiv:** [https://arxiv.org/abs/2304.13343](https://arxiv.org/abs/2304.13343)

**Code:** [https://github.com/wbbeyourself/SCM4LLMs](https://github.com/wbbeyourself/SCM4LLMs)

---

## Abstract

Large Language Models (LLMs) are constrained by their inability to process lengthy inputs, resulting in the loss of critical historical information. The authors propose the Self-Controlled Memory (SCM) framework to enhance the ability of LLMs to maintain long-term memory and recall relevant information. The framework consists of three components: an LLM-based agent serving as the backbone, a memory stream storing agent memories, and a memory controller updating memories and determining when and how to use them. SCM processes ultra-lengthy texts without requiring modifications or fine-tuning, functioning as a plug-and-play paradigm compatible with any instruction-following LLM. Evaluation on extended dialogues, book summarization, and meeting summarization demonstrates better retrieval recall and more informative responses compared to competitive baselines.

---

## 1. Introduction

LLMs face a fundamental limitation: finite context windows prevent processing of long documents and extended conversations. As conversations grow, models either truncate history (losing critical information) or attempt to fit everything into context (introducing noise). SCM addresses this with an intelligent memory management layer.

## 2. Architecture

### 2.1 LLM-based Agent

The backbone model (text-davinci-003 or gpt-3.5-turbo) generates responses based on well-designed instructions. No fine-tuning is required -- SCM works with any instruction-following LLM.

### 2.2 Memory Stream

Stores historical interactions, each containing:
- **Interaction index** -- sequential identifier
- **Observation** -- user input
- **System response** -- agent's reply
- **Memory summarization** -- condensed version of the interaction
- **Interaction embedding** -- vector representation for retrieval

### 2.3 Memory Controller

The intelligent component that determines memory usage by asking two critical questions:
1. "Is memory activation necessary?" -- Should we retrieve past context?
2. "Can summaries suffice instead of full content?" -- Level of detail needed

This self-controlled decision-making avoids both unnecessary retrieval (adding noise) and missed retrieval (losing context).

## 3. Six-Step Workflow

SCM processes each interaction through six steps:

1. **Input Acquisition** -- Receive and encode user input
2. **Memory Activation** -- Controller decides whether to activate memory retrieval
3. **Memory Retrieval** -- If activated, find relevant historical memories
4. **Memory Reorganization** -- Organize retrieved memories by relevance and recency
5. **Input Fusion** -- Combine current input with retrieved context
6. **Response Generation** -- Generate response using fused input

## 4. Memory Types

### 4.1 Activation Memory

Long-term historical information retrieved based on relevance to current query. Scored by combining:
- **Recency score** -- more recent memories weighted higher
- **Relevance score** -- cosine similarity between query and memory embeddings

### 4.2 Flash Memory

Short-term, immediate prior turn information. Always included to maintain conversational coherence without retrieval overhead.

## 5. Experimental Evaluation

### 5.1 Datasets

| Task | Instances | Max Tokens | Max Turns |
|---|---|---|---|
| Long-term dialogues | 18 | 34K | 200 |
| Book summarization | 10 | 2M | - |
| Meeting summarization | 20 | 50K | - |

### 5.2 Dialogue Results (text-davinci-003)

| Metric | SCM | Without Activation Memory | Without Controller | Without Flash Memory |
|---|---|---|---|---|
| Answer accuracy | 77.1% | 66.6% (-10.5%) | 51.5% (-25.6%) | 72.9% (-4.2%) |
| Memory retrieval recall | 94.0% | - | - | - |
| Multi-turn accuracy | 75.0% | - | 49.4% | - |

### 5.3 Key Findings

**Ablation Results:**
- Removing activation memory: 10.5% accuracy drop -- long-term context matters
- Removing memory controller: 25.6% accuracy drop -- blind retrieval adds noise
- Removing flash memory: 4.2% drop -- minimal but consistent impact

**Summarization Tasks:**
- SCM outperformed RecursiveSum baseline in both coverage and coherence
- Human evaluation confirmed superiority for book and meeting summarization

### 5.4 Research Questions Addressed

**RQ1:** SCM competes with ChatGPT within its token limits and outperforms it on specific long-context tasks.

**RQ2:** Framework scales effectively to retrieve information from hundreds of prior dialogue turns.

**RQ3:** Generalizes successfully to book and meeting summarization scenarios beyond dialogue.

## 6. Analysis

### 6.1 Controller Importance

The memory controller is the most critical component. Without it:
- All turns trigger memory retrieval, adding noise
- Irrelevant memories dilute useful context
- Multi-turn accuracy drops by 25.6 percentage points

### 6.2 Scalability

SCM handles documents up to 2 million tokens through:
- Chunked processing of input documents
- Selective memory activation (not all chunks stored)
- Efficient retrieval via embedding-based similarity search

### 6.3 Plug-and-Play Design

No model modification needed:
- Works with any instruction-following LLM
- Memory operations implemented as prompt engineering
- Controller decisions made by the LLM itself through prompting

## 7. Limitations

- Evaluation tested up to 200 dialogue turns and 34K tokens; truly infinite-length evaluation remains difficult
- Framework effectiveness depends on access to powerful instruction-following models
- Memory controller accuracy depends on the base LLM's reasoning quality
- Embedding quality affects retrieval precision

## 8. Related Work

- **Long-context models:** Longformer, BigBird, Memorizing Transformers
- **Memory-augmented LLMs:** MemoryBank, RET-LLM, LTRM
- **Summarization approaches:** RecursiveSum, hierarchical summarization
- **Retrieval augmentation:** RAG, RETRO

SCM is distinguished by its self-controlled memory activation and plug-and-play compatibility.

## 9. Conclusion

SCM demonstrates that intelligent memory management -- rather than raw context window expansion -- provides a practical pathway for handling ultra-long inputs. The self-controlled approach to memory activation reduces noise while maintaining access to critical historical information.

---

## Key Figures

- **Figure 1:** SCM framework architecture showing the agent, memory stream, and controller components.
- **Figure 2:** Six-step workflow from input acquisition through response generation.
- **Figure 3:** Memory retrieval scoring combining recency and relevance.
- **Figure 4:** Ablation study results showing contribution of each component.

---

## Top References

1. Brown et al. (2020). Language Models are Few-Shot Learners. NeurIPS.
2. Ouyang et al. (2022). Training Language Models to Follow Instructions with Human Feedback. NeurIPS.
3. Vaswani et al. (2017). Attention Is All You Need. NeurIPS.
4. Lewis et al. (2020). Retrieval-Augmented Generation. NeurIPS.
5. Dai et al. (2019). Transformer-XL. ACL.
6. Beltagy et al. (2020). Longformer: The Long-Document Transformer.
7. Wu et al. (2022). Memorizing Transformers. ICLR.
8. Park et al. (2023). Generative Agents: Interactive Simulacra of Human Behavior.
9. Zhong et al. (2023). MemoryBank: Enhancing Large Language Models with Long-Term Memory.
10. Borgeaud et al. (2022). Improving Language Models by Retrieving from Trillions of Tokens. ICML.
