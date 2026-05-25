# Cognitive Architectures for Language Agents

**Authors:** Theodore R. Sumers, Shunyu Yao, Karthik Narasimhan, Thomas L. Griffiths

**Venue:** TMLR (Transactions on Machine Learning Research), 2024

**arXiv:** [https://arxiv.org/abs/2309.02427](https://arxiv.org/abs/2309.02427)

---

## Abstract

Recent efforts have augmented large language models (LLMs) with external resources (e.g., the Internet) or internal control flows (e.g., prompt chaining) for tasks requiring grounding or reasoning, leading to a new class of language agents. While these agents have achieved substantial empirical success, we argue that there is an important need for a systematic and unifying perspective. Drawing on the rich history of cognitive science and symbolic AI, the paper proposes Cognitive Architectures for Language Agents (CoALA), a conceptual framework describing language agents with modular memory components, a structured action space to interact with internal memory and external environments, and a generalized decision-making process to choose actions.

---

## 1. Introduction

The paper synthesizes the rapidly growing field of language agents by drawing parallels with historical cognitive science and symbolic AI research. It positions LLMs as core components within structured cognitive architectures (analogous to Soar, ACT-R) rather than standalone systems.

## 2. Background: From Strings to Symbolic AGI

### Historical Context
- **Production systems** (Newell & Simon, 1972): condition-action rules operating on working memory
- **Soar** (Laird, 2012): unified cognitive architecture with chunking and learning
- **ACT-R** (Anderson, 1993): modular architecture with declarative and procedural memory

### Connection to LLMs
LLMs can be viewed as production systems where:
- Input prompt = working memory contents
- Generated text = fired production rule
- The key difference: LLMs use soft, learned pattern matching rather than symbolic rules

## 3. CoALA Framework

### 3.1 Memory Organization

| Memory Type | Description | Examples |
|-------------|-------------|---------|
| **Working Memory** | Short-term symbolic variables for current decision cycle | Current task, observations, reasoning traces |
| **Episodic Memory** | Historical experiences and trajectories | Past interaction logs, success/failure records |
| **Semantic Memory** | World knowledge and facts | Knowledge bases, documentation, embeddings |
| **Procedural Memory** | Implicit (LLM weights) + explicit (agent code) | Learned skills, tool definitions, prompt templates |

### 3.2 Action Space

**External Actions (Grounding):**
- Physical environments (robotics with vision-language models)
- Human dialogue and agent interaction
- Digital environments (games, APIs, websites, code execution)

**Internal Actions:**

| Action | Description |
|--------|-------------|
| **Reasoning** | LLM-based working memory updates (e.g., CoT, ToT) |
| **Retrieval** | Loading information from long-term memories |
| **Learning** | Writing to episodic, semantic, or procedural memory |

### 3.3 Decision-Making Cycle

Repeating cycles with two stages:

**Planning Stage:**
1. **Proposal**: Generate action candidates
2. **Evaluation**: Assign values to candidates
3. **Selection**: Choose best action

**Execution Stage:**
- Implement selected action
- Receive environmental feedback
- Update working memory

## 4. Case Studies

### Agent Comparison Table

| Agent | Long-term Memory | Grounding | Internal Actions | Decision Making |
|-------|------------------|-----------|------------------|-----------------|
| SayCan | Procedural only | Physical | Evaluation only | Evaluate fixed actions |
| ReAct | None | Digital | Reasoning | Single reasoning step |
| Voyager | Procedural | Digital | All four | Propose with retrieval |
| Generative Agents | Episodic/Semantic | Digital/Agent | All four | Propose with retrieval/reasoning |
| Tree of Thoughts | None | Digital | Reasoning only | Propose-evaluate-select loop |

### SayCan
- Maps language instructions to robotic actions
- Uses value functions for evaluation (affordance scoring)
- Procedural memory only (pre-trained skills)

### ReAct
- Interleaves reasoning and acting
- No long-term memory between episodes
- Single reasoning step per cycle

### Voyager
- Grows procedural memory (skill library) over time
- Retrieves relevant skills for new tasks
- Automatic curriculum drives exploration

### Generative Agents
- Rich episodic + semantic memory
- Reflection mechanism for higher-level insights
- Agent-to-agent interaction

### Tree of Thoughts
- Pure reasoning without external grounding
- Propose-evaluate-select loop for systematic exploration
- No long-term memory

## 5. Actionable Insights

### Systematic Agent Design
Agents should follow modular, standardized abstractions (analogous to OpenAI Gym for RL). The framework encourages clear separation of memory, action, and decision-making components.

### Structured Reasoning
Move beyond low-level prompt engineering toward higher-level reasoning frameworks. Defining and building good working memory modules is crucial for industry applications.

### Long-term Memory Integration
Combine human-written knowledge with autonomously generated experience for efficient lifelong learning through integrated retrieval and reasoning.

### Complex Decision-Making
Most current agents generate single actions; future work should implement deliberate propose-evaluate-select procedures mixing language-based reasoning and code-based planning.

### Safety Considerations
Procedural memory modifications and external grounding actions present risks requiring task-specific safeguards. Future agents may need worst-case scenario prediction and prevention.

## 6. Discussion

### Open Questions

**Internal vs. External Boundaries:**
Controllability and coupling determine whether components are internal memories or external environments.

**Physical vs. Digital Differences:**
Digital agents can parallelize and reset, enabling bolder exploration strategies that diverge from human-inspired decision-making.

**Learning vs. Acting Trade-offs:**
Future agents should treat learning as a deliberate action competing with external grounding, mirroring biological agent behavior.

---

## Figure Descriptions

- **Figure 1:** CoALA framework overview showing memory modules, action space, and decision-making cycle
- **Figure 2:** Taxonomy of memory types (working, episodic, semantic, procedural) with examples
- **Figure 3:** Action space organization: external grounding vs. internal reasoning/retrieval/learning
- **Figure 4:** Decision-making cycle: proposal -> evaluation -> selection -> execution -> feedback
- **Figure 5:** Case study comparison showing how five agents map onto the CoALA framework

---

## Top 10 References

1. Yao, S., et al. (2022). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
2. Wang, G., et al. (2023). Voyager: An open-ended embodied agent with large language models. *NeurIPS*.
3. Park, J. S., et al. (2023). Generative agents: Interactive simulacra of human behavior. *UIST*.
4. Laird, J. E. (2012). The Soar Cognitive Architecture. *MIT Press*.
5. Ahn, M., et al. (2022). Do as I can, not as I say: Grounding language in robotic affordances. *CoRL*.
6. Yao, S., et al. (2023). Tree of thoughts: Deliberate problem solving with large language models. *NeurIPS*.
7. Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS*.
8. Newell, A. & Simon, H. A. (1972). Human Problem Solving. *Prentice-Hall*.
9. Brown, T., et al. (2020). Language models are few-shot learners. *NeurIPS* (GPT-3).
10. Shinn, N., et al. (2023). Reflexion: Language agents with verbal reinforcement learning. *NeurIPS*.
