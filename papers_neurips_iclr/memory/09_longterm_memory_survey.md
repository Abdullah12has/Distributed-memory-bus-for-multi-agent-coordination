# A Survey on the Memory Mechanism of Large Language Model based Agents

**Authors:** Zeyu Zhang, Xiaohe Bo, Chen Ma, Rui Li, Xu Chen, Quanyu Dai, Jieming Zhu, Zhenhua Dong, Ji-Rong Wen

**Venue:** arXiv preprint (cs.AI), 2024 (39 pages, 5 figures, 4 tables)

**arXiv:** [https://arxiv.org/abs/2404.13501](https://arxiv.org/abs/2404.13501)

**Note:** The user-provided arxiv ID 2404.11221 resolved to an unrelated paper. The correct ID for this memory survey is 2404.13501.

---

## Abstract

LLM-based agents are featured in their self-evolving capability, which is the basis for solving real-world problems that need long-term and complex agent-environment interactions. The key component supporting this self-evolving capability is the memory module. While promising memory mechanisms have emerged in the literature, they lack systematic organization from a comprehensive perspective. This survey provides a systematic review of memory mechanisms in LLM-based agents, covering what memory means in this context, why it is needed, how to design and evaluate memory modules, and practical applications where memory plays a critical role. The authors identify current limitations and outline future research directions, maintaining a GitHub repository to track ongoing developments.

---

## 1. Introduction

### 1.1 Memory as Foundation for Agent Intelligence

LLM-based agents differ from standalone LLMs in their ability to interact with environments over extended periods. Memory enables:
- **Continuity** across interactions
- **Learning** from past experiences
- **Adaptation** to changing environments
- **Self-evolution** through accumulated knowledge

### 1.2 Scope and Motivation

Despite growing interest in LLM-based agents, memory mechanisms have been studied in isolation. This survey provides the first systematic framework for understanding memory in LLM agents.

## 2. What is Memory in LLM Agents?

### 2.1 Narrow Definition

Memory as explicit storage and retrieval of information beyond the context window -- external datastores, databases, or structured knowledge bases.

### 2.2 Broad Definition

Memory encompasses all mechanisms by which an agent retains and uses past information:
- **Parametric memory** -- knowledge encoded in model weights
- **In-context memory** -- information within the current context window
- **External memory** -- stored outside the model in retrievable formats

### 2.3 Connection to Cognitive Psychology

Drawing from human memory research:
- **Sensory memory** -- raw input processing (analogous to tokenization)
- **Short-term / working memory** -- context window, active processing
- **Long-term memory** -- persistent storage beyond context limits
  - Episodic: specific experiences
  - Semantic: general knowledge
  - Procedural: skills and actions

## 3. Why Do LLM Agents Need Memory?

### 3.1 Context Window Limitations

All current LLMs have finite context windows. Memory enables:
- Processing of information beyond window limits
- Maintenance of coherent long-term interactions
- Accumulation of knowledge over time

### 3.2 Self-Evolution

Memory enables agents to:
- Learn from mistakes without retraining
- Build on prior successful strategies
- Develop specialized knowledge for recurring tasks

### 3.3 Multi-Agent Coordination

In multi-agent settings, memory enables:
- Shared knowledge bases
- Communication history tracking
- Coordinated strategy development

## 4. How to Design Memory Modules

### 4.1 Memory Sources

| Source | Description | Examples |
|---|---|---|
| Conversation history | Past dialogue turns | ChatGPT conversation threads |
| Task results | Outcomes of prior actions | Tool call results, code execution outputs |
| Environment observations | Sensory data from interactions | Game states, web page contents |
| External knowledge | Pre-existing databases | Wikipedia, knowledge graphs |
| Agent reflections | Self-generated insights | Summarized lessons, strategy notes |

### 4.2 Memory Forms

**Natural Language:**
- Most common representation
- Human-readable and interpretable
- Compatible with LLM processing
- Examples: summaries, notes, dialogue logs

**Structured Data:**
- Knowledge graphs, databases, tables
- Efficient querying and aggregation
- Less flexible for nuanced information
- Examples: triplet stores, SQL databases

**Embeddings:**
- Dense vector representations
- Efficient similarity-based retrieval
- Not human-interpretable
- Examples: FAISS indices, embedding databases

**Hybrid:**
- Combining multiple forms
- Natural language with embedding indices
- Structured metadata with free-text content

### 4.3 Memory Operations

**Writing (Storage):**
- Raw storage: save information as-is
- Summarized storage: compress before saving
- Structured extraction: convert to structured format
- Selective storage: decide what to keep/discard

**Reading (Retrieval):**
- Recency-based: most recent memories first
- Relevance-based: similarity to current query
- Importance-based: priority scoring
- Hybrid: combining multiple signals

**Management:**
- Forgetting: removing outdated/irrelevant memories
- Consolidation: merging related memories
- Reflection: generating higher-level insights from memory
- Compression: reducing memory footprint

## 5. How to Evaluate Memory

### 5.1 Evaluation Dimensions

- **Recall accuracy** -- can the agent retrieve relevant memories?
- **Response quality** -- does memory improve output quality?
- **Consistency** -- are responses coherent across time?
- **Efficiency** -- computational cost of memory operations
- **Scalability** -- performance as memory grows

### 5.2 Benchmarks and Tasks

- Long-term dialogue evaluation
- Multi-session interaction
- Knowledge-intensive QA
- Agent simulation (e.g., Generative Agents)

## 6. Applications

### 6.1 Role-Playing Agents

Memory stores character traits, relationship history, and personality consistency across interactions.

### 6.2 Social Simulation

Agents maintain social memory for interactions with other agents, enabling emergent social behaviors (e.g., Generative Agents / Smallville).

### 6.3 Personal Assistants

Long-term user preference learning, task history, and personalized response generation.

### 6.4 Open-World Gaming

Storing exploration history, learned strategies, and environmental knowledge for games like Minecraft.

### 6.5 Code Generation

Maintaining code context, prior debugging sessions, and project-level understanding.

### 6.6 Recommendation Systems

User preference modeling through interaction history and evolving taste profiles.

### 6.7 Expert Systems

Domain-specific knowledge accumulation and retrieval for specialized tasks.

## 7. Challenges and Future Directions

### 7.1 Current Limitations

- **Scalability:** Memory retrieval degrades with size
- **Quality control:** No robust mechanisms for validating stored memories
- **Integration:** Combining parametric and external memory remains difficult
- **Evaluation:** Lack of standardized benchmarks for memory assessment

### 7.2 Future Research Directions

- **Continual learning integration:** Bridging memory and model parameter updates
- **Multi-modal memory:** Supporting vision, audio, and other modalities
- **Collaborative memory:** Shared memory across multiple agents
- **Memory-efficient architectures:** Reducing computational overhead
- **Theoretical foundations:** Formalizing memory capacity and retrieval guarantees

## 8. Conclusion

Memory is a cornerstone capability for LLM-based agents, enabling self-evolution and complex long-term interactions. The survey systematizes existing approaches across memory sources, forms, operations, and evaluation, providing a framework for future research in this rapidly developing area.

---

## Key Figures

- **Figure 1:** Taxonomy of memory mechanisms in LLM-based agents.
- **Figure 2:** Memory operation pipeline: write, read, manage.
- **Figure 3:** Cognitive psychology mapping to agent memory types.
- **Figure 4:** Application domains and their memory requirements.
- **Figure 5:** Timeline of key papers in LLM agent memory research.

---

## Key Tables

- **Table 1:** Comparison of memory forms (natural language, structured, embeddings, hybrid).
- **Table 2:** Overview of memory operations across surveyed systems.
- **Table 3:** Evaluation benchmarks and their covered memory dimensions.
- **Table 4:** Summary of surveyed agent systems and their memory designs.

---

## Top References

1. Park et al. (2023). Generative Agents: Interactive Simulacra of Human Behavior. UIST.
2. Shinn et al. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning. NeurIPS.
3. Zhong et al. (2023). MemoryBank: Enhancing Large Language Models with Long-Term Memory.
4. Wang et al. (2023). Voyager: An Open-Ended Embodied Agent with Large Language Models. NeurIPS.
5. Weston et al. (2015). Memory Networks. ICLR.
6. Lewis et al. (2020). Retrieval-Augmented Generation. NeurIPS.
7. Yao et al. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. ICLR.
8. Wei et al. (2022). Chain-of-Thought Prompting. NeurIPS.
9. Sumers et al. (2023). Cognitive Architectures for Language Agents.
10. Wang et al. (2023). A Survey on Large Language Model based Autonomous Agents.
