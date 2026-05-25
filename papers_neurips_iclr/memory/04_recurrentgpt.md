# RecurrentGPT: Interactive Generation of (Arbitrarily) Long Text

**Authors:** Wangchunshu Zhou, Yuchen Eleanor Jiang, Peng Cui, Tiannan Wang, Zhenxin Xiao, Yifan Hou, Ryan Cotterell, Mrinmaya Sachan

**Venue:** arXiv preprint (2023)

**arXiv:** [https://arxiv.org/abs/2305.13304](https://arxiv.org/abs/2305.13304)

---

## Abstract

The paper presents RecurrentGPT, a language-based simulacrum of the recurrence mechanism in RNNs. RecurrentGPT is built upon a large language model (e.g., ChatGPT) and uses natural language to simulate the Long Short-Term Memory mechanism. At each timestep, RecurrentGPT generates a paragraph of text and updates its language-based long-short term memory stored on the hard drive and the prompt, respectively. RecurrentGPT can generate texts of arbitrary length without forgetting. Furthermore, users can observe and edit these memories, providing an interactive and controllable generation process. RecurrentGPT is used as an interactive fiction that directly interacts with consumers, moving AI-generated content from a "tool" paradigm to a "content" paradigm.

---

## 1. Introduction

Transformers have fixed context windows that limit their ability to generate coherent long-form text. RecurrentGPT addresses this by replacing vectorized LSTM components (hidden states, cell states) with natural language equivalents, implementing recurrence through prompting rather than architectural modifications.

### Key Innovation
All recurrent state (memory, plans) is represented in natural language, making it:
- Interpretable by humans
- Editable during generation
- Usable with frozen LLMs (no finetuning)

## 2. Architecture

### Language-Based Building Blocks

| Component | LSTM Analogy | Description |
|-----------|-------------|-------------|
| **Content** | Output | 200-400 word paragraphs (actual text output) |
| **Plan** | Cell state (partial) | 3-5 sentence outlines for upcoming paragraphs |
| **Short-term Memory** | Hidden state | 10-20 sentence summary of recent context |
| **Long-term Memory** | External memory | Vector database of all previously generated content |

### Generation Cycle

At each timestep t, RecurrentGPT:
1. Receives: short-term memory (t-1), relevant long-term memories, plan (t-1), user input
2. Generates: new paragraph (content), updated short-term memory, new plan options (typically 3)
3. Stores: new paragraph embeddings in long-term memory vector database

### Long-term Memory Retrieval

- All previously generated paragraphs are embedded and stored in a vector database
- At each step, the current context is used to retrieve semantically relevant past content
- Retrieved memories are prepended to the prompt to maintain coherence with earlier text

### User Interaction Points

- Users can select from multiple plan options (typically 3)
- Users can edit plans before generation continues
- Users can modify short-term memory to steer narrative direction
- Users can write custom plans entirely

## 3. Application Domains

### Autonomous Generation
Produces thousands of tokens maintaining coherence without human intervention. The system runs in a loop, automatically selecting plans and generating content.

### Interactive Writing Assistant
Human-AI collaboration where writers:
- Review generated paragraph drafts
- Select or edit proposed plans
- Modify memory to adjust narrative direction
- Maintain creative control while leveraging AI generation

### Interactive Fiction ("AI as Content")
Players choose narrative directions from model-generated options or create custom plans. This shifts generative AI from a tool paradigm (AI assists human creators) to a content paradigm (AI generates consumable experiences directly).

## 4. Experimental Results

### Human Preference Study (6 Literary Genres)

Comparison against baselines across sci-fi, romance, fantasy, horror, mystery, thriller:

| Comparison | Preference for RecurrentGPT |
|-----------|---------------------------|
| vs. Rolling-ChatGPT | 85-95% (interestingness) |
| vs. RE3 baseline | 60-70% |
| vs. DOC baseline | 55-80% |

Margins increase for longer texts (~6000 words), confirming the value of memory management.

### Ablation Study

| Configuration | Coherence Impact |
|--------------|-----------------|
| Full RecurrentGPT | Baseline |
| Remove short-term memory | -30 to -35% coherence |
| Remove long-term memory | -25 to -40% coherence |
| GPT-4 backbone (vs ChatGPT) | Substantial improvement |

Both memory components are essential; long-term memory becomes increasingly important as text length grows.

## 5. Advantages Over Prior Work

| Feature | RecurrentGPT | Rolling Window | Hierarchical (RE3/DOC) |
|---------|-------------|----------------|----------------------|
| Arbitrary length | Yes | Limited | Outline-constrained |
| Interpretable state | Yes | No | Partially |
| Human editable | Yes | No | Outline only |
| No architectural change | Yes | Yes | Yes |
| No finetuning needed | Yes | Yes | Sometimes |
| Error prevention | Via human oversight | None | None |
| Granularity | Paragraph-level | Token-level | Section-level |

## 6. Limitations

- Evaluations limited to ~5000-word texts
- Requires sufficiently powerful LLM backbones (ChatGPT minimum)
- Small-scale user studies
- Potential for generating harmful content
- Quality degrades with weaker base models
- Long-term memory retrieval may miss relevant but semantically distant content

---

## Figure Descriptions

- **Figure 1:** RecurrentGPT architecture showing the analogy between LSTM components and language-based equivalents
- **Figure 2:** Generation cycle: input (memories + plan) -> LLM -> output (content + updated memory + new plans)
- **Figure 3:** Interactive fiction interface showing plan selection and memory editing
- **Figure 4:** Human preference results across six literary genres
- **Figure 5:** Example generated text showing coherence over thousands of words

---

## Top 10 References

1. Radford, A., et al. (2018). Improving language understanding by generative pre-training (GPT).
2. Radford, A., et al. (2019). Language models are unsupervised multitask learners (GPT-2).
3. Brown, T., et al. (2020). Language models are few-shot learners (GPT-3). *NeurIPS*.
4. Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback. *NeurIPS*.
5. OpenAI (2023). GPT-4 technical report. *arXiv:2303.08774*.
6. Vaswani, A., et al. (2017). Attention is all you need. *NeurIPS*.
7. Hochreiter, S. & Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*.
8. Dai, Z., et al. (2019). Transformer-XL: Attentive language models beyond a fixed-length context. *ACL*.
9. Yang, K., et al. (2022). RE3: Generating longer stories with recursive reprompting and revision. *EMNLP*.
10. Yang, K., et al. (2022). DOC: Improving long story coherence with detailed outline control. *ACL*.
