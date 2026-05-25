# OS-Copilot: Towards Generalist Computer Agents with Self-Improvement

**Authors:** Zhiyong Wu, Chengcheng Han, Zichen Ding, Zhenmin Weng, Zhoumianze Liu, Shunyu Yao, Tao Yu, Lingpeng Kong

**Venue:** arXiv preprint (2024)

**arXiv:** [https://arxiv.org/abs/2402.07456](https://arxiv.org/abs/2402.07456)

---

## Abstract

Autonomous agents that accomplish complex computer tasks with minimal human intervention have the potential to transform human-computer interaction. The paper presents OS-Copilot, a framework for building generalist agents capable of interfacing with comprehensive elements in an operating system (OS), including the web, code terminals, files, multimedia, and various third-party applications. The authors build FRIDAY, a self-improving embodied agent within OS-Copilot that learns to control and self-improve on previously unseen applications. FRIDAY achieves 35% better performance than prior methods on the GAIA benchmark and demonstrates notable generalization through accumulated skills, along with evidence of self-improvement on Excel and PowerPoint tasks with minimal supervision.

---

## 1. Introduction

Current computer agents are typically specialized for single domains (web browsing, code execution, or specific applications). OS-Copilot proposes a unified framework enabling agents to interact with the full operating system stack, from file management to web browsing to application control.

### Key Contributions
1. A conceptual framework for building generalist computer agents on Linux and macOS
2. FRIDAY: a self-improving assistant demonstrating outstanding performance and generalization
3. Self-directed learning: autonomous curriculum proposal and tool accumulation

## 2. Core Architecture

### 2.1 Planner

- Decomposes complex user requests into simpler subtasks
- Uses a directed acyclic graph (DAG) enabling parallel task execution
- LLMs formalize plans representing interdependencies between tasks

### 2.2 Configurator

Inspired by biological memory systems, comprising three memory types:

| Memory Type | Function | Analogy |
|-------------|----------|---------|
| **Declarative Memory** | Stores facts, events, user profiles, semantic knowledge | Episodic + semantic memory |
| **Procedural Memory** | Tool repositories functioning as the agent's skill set | Motor skills |
| **Working Memory** | Short-term storage connecting planner, configurator, actor | Active processing |

### 2.3 Actor

Two-stage process:

**Executor:** Generates executable commands or function calls based on configuration prompts. Supports:
- Python code interpreter
- Bash terminal commands
- Mouse/keyboard control
- API calls to third-party applications

**Critic:** Evaluates subtask completion by assessing environmental state changes before and after execution. Provides feedback for self-correction (maximum 3 attempts per subtask).

## 3. Universal Interface

OS-Copilot consolidates multiple interaction modalities:
- Python code interpreter for computation and data processing
- Bash terminal for system operations
- Mouse/keyboard control for GUI interaction
- API calls for application-specific functionality

## 4. Self-Directed Learning

FRIDAY can autonomously:
1. Propose curricula of tasks for unfamiliar applications
2. Attempt tasks through trial-and-error
3. Accumulate successful solutions as reusable tools
4. Apply learned tools to future similar tasks

## 5. Experimental Results

### GAIA Benchmark Performance

| Level | FRIDAY | Previous Best | Relative Improvement |
|-------|--------|---------------|---------------------|
| Level 1 | 40.86% | 30.3% | +35% |
| Level 2 | 20.13% | 9.7% | +107% |
| Level 3 | 6.12% | 0% | New capability |

### Time Efficiency
FRIDAY executes Level 1 tasks in ~105 seconds, compared to 500+ seconds for AutoGPT-4.

### Self-Directed Learning Results

**SheetCopilot-20 (Excel tasks):**

| Configuration | Success Rate |
|---------------|-------------|
| FRIDAY without learning | 0% |
| SheetCopilot (specialized, GPT-4) | 55% |
| **FRIDAY with learning** | **60%** |

**PowerPoint Tasks:**
Successfully learned text box control, image insertion/positioning, and formatting through self-directed exploration without task-specific training.

## 6. Tool Generation

When suitable tools are not found in procedural memory, FRIDAY automatically:
1. Identifies the capability gap
2. Generates application-tailored tool implementations
3. Tests the tool through execution
4. Stores successful tools for future retrieval

## 7. Limitations

- Heavy reliance on prompt engineering rather than fine-tuning
- Cannot handle closed-source applications without APIs
- Limited multimodal/visual GUI interaction capabilities
- Evaluation challenges due to absence of ground truth in OS environments
- Safety and interpretability concerns for OS-level automation

---

## Figure Descriptions

- **Figure 1:** OS-Copilot framework overview showing Planner, Configurator (with three memory types), and Actor components
- **Figure 2:** FRIDAY's self-directed learning pipeline: curriculum proposal -> trial-and-error solving -> tool accumulation
- **Figure 3:** GAIA benchmark performance comparison across difficulty levels
- **Figure 4:** SheetCopilot-20 learning curve showing improvement with self-directed practice
- **Figure 5:** Example execution traces for multi-step OS tasks

---

## Top 10 References

1. Baddeley, A. (2003). Working memory: Looking back and looking forward. *Nature Reviews Neuroscience*.
2. Besta, M., et al. (2023). Graph of thoughts: Solving elaborate problems with large language models. *arXiv*.
3. Brohan, A., et al. (2023). RT-2: Vision-language-action models transfer web knowledge to robotic control. *arXiv*.
4. Deng, X., et al. (2023). Mind2Web: Towards a generalist agent for the web. *NeurIPS*.
5. Driess, D., et al. (2023). PaLM-E: An embodied multimodal language model. *ICML*.
6. Wang, G., et al. (2023). Voyager: An open-ended embodied agent with large language models. *NeurIPS*.
7. Wang, L., et al. (2023). A survey on large language model based autonomous agents. *arXiv*.
8. Yao, S., et al. (2023). Tree of thoughts: Deliberate problem solving with large language models. *NeurIPS*.
9. Li, P., et al. (2023). SheetCopilot: Bringing software productivity to the next level through large language models. *NeurIPS*.
10. Mialon, G., et al. (2023). GAIA: A benchmark for general AI assistants. *arXiv*.
