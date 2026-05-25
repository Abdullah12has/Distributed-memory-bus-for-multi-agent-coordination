# MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework

**Authors:** Sirui Hong, Mingchen Zhuge, Jiaqi Chen, Xiawu Zheng, Yuheng Cheng, Ceyao Zhang, Jinlin Wang, Zili Wang, Steven Ka Shing Yau, Zijuan Lin, Liyang Zhou, Chenyu Ran, Lingfeng Xiao, Chenglin Wu, Jurgen Schmidhuber

**Venue:** ICLR 2024

**ArXiv:** [https://arxiv.org/abs/2308.00352](https://arxiv.org/abs/2308.00352)

**Date:** August 1, 2023

---

## Abstract

Remarkable progress has been made on automated problem solving through societies of agents based on large language models (LLMs). Existing LLM-based multi-agent systems can already solve simple dialogue tasks. Solutions to more complex tasks, however, are complicated through logic inconsistencies due to cascading hallucinations caused by naively chaining LLMs. Here we introduce MetaGPT, an innovative meta-programming framework incorporating efficient human workflows into LLM-based multi-agent collaborations. MetaGPT encodes Standardized Operating Procedures (SOPs) into prompt sequences for more streamlined workflows, thus allowing agents with human-like domain expertise to verify intermediate results and reduce errors. MetaGPT utilizes an assembly line paradigm to assign diverse roles to various agents, efficiently breaking down complex tasks into subtasks involving many agents working together. On collaborative software engineering benchmarks, MetaGPT generates more coherent solutions than previous chat-based multi-agent systems.

---

## 1. Introduction

Current LLM-based multi-agent systems struggle to achieve effective, coherent, and accurate problem-solving processes, particularly when there is a need for meaningful collaborative interaction. MetaGPT addresses this by encoding SOPs into prompt sequences, enabling agents to break down complex tasks into subtasks with specialized roles.

The framework prevents unproductive LLM interactions by requiring structured outputs, such as high-quality requirements documents, design artifacts, flowcharts, and interface specifications rather than idle dialogue between agents.

---

## 2. Related Work

### Automatic Programming

Historical context traces from 1969's PROW system through modern approaches using natural language processing. Recent LLM-based agents like ReAct and Reflexion utilize a chain of thought prompts to generate reasoning trajectories and action plans. MetaGPT distinguishes itself by requiring structured outputs rather than relying solely on chat-based frameworks.

### LLM-Based Multi-Agent Frameworks

Recent works have improved the problem-solving abilities of LLMs by integrating discussions among multiple agents, including Generative Agents and Natural Language-Based Society of Mind (NLSOM). MetaGPT applies advanced concepts such as Standard Operating Procedures to reduce unproductive cycles and maintain consistency.

---

## 3. MetaGPT: A Meta-Programming Framework

### 3.1 Agents in Standard Operating Procedures

#### Specialization of Roles

Five primary roles are defined:

| Role | Responsibility |
|------|---------------|
| Product Manager | Analyzes requirements, creates PRDs with User Stories and Requirement Pool |
| Architect | Translates requirements into system design with File Lists, Data Structures, and Interface Definitions |
| Project Manager | Distributes tasks across engineering team |
| Engineer | Executes designated classes and functions |
| QA Engineer | Formulates test cases for validation |

Each agent has a specified profile including name, profile, goal, and constraints, with role-specific tools (e.g., web search for Product Manager, code execution for Engineer).

#### Workflow Across Agents

The sequential workflow follows standard software development practices:

1. **Product Manager** analyzes requirements and creates detailed PRDs including User Stories and Requirement Pool
2. **Architect** translates requirements into system design with File Lists, Data Structures, and Interface Definitions
3. **Project Manager** distributes tasks
4. **Engineers** execute designated classes and functions
5. **QA Engineer** formulates test cases

### 3.2 Communication Protocol

#### Structured Communication Interfaces

Rather than unconstrained natural language, MetaGPT uses structured outputs. The Architect generates system interface design and a sequence flow diagram containing system module design and interaction sequences, preventing irrelevant or missing content.

#### Publish-Subscribe Mechanism

A shared message pool eliminates inefficient one-to-one communication. Agents select information to follow based on their role profiles, with an agent activating its action only after receiving all its prerequisite dependencies.

### 3.3 Iterative Programming with Executable Feedback

The framework implements an executable feedback mechanism to improve the code iteratively. Engineers write code, execute unit tests, and debug the code before resuming programming until tests pass or maximum retries are reached.

---

## 4. Experiments

### 4.1 Experimental Setting

#### Datasets

- **HumanEval**: 164 handwritten programming tasks
- **MBPP**: 427 Python tasks
- **SoftwareDev**: 70 representative software development examples with diverse scopes

#### Evaluation Metrics

For HumanEval/MBPP: Pass@k metric measuring functional accuracy

For SoftwareDev:
- (A) Executability (1-4 scale)
- (B) Cost (time, tokens, expenses)
- (C) Code Statistics (files, lines per file)
- (D) Productivity (tokens per code line)
- (E) Human Revision Cost (revision rounds needed)

#### Baselines

Comparisons with domain-specific models (AlphaCode, CodeGeeX, CodeGen, CodeX) and general LLMs (PaLM, GPT-4), plus frameworks (AutoGPT, LangChain, AgentVerse, ChatDev).

### 4.2 Main Results

#### Code Generation Performance

MetaGPT with GPT-4 achieves 85.9% and 87.7% in Pass@1 on HumanEval and MBPP respectively.

#### Software Development Performance

| Metric | ChatDev | MetaGPT |
|--------|---------|---------|
| Executability | 2.25 | 3.75 |
| Running Time (s) | 762 | 541 |
| Token Usage | 19,292 | 31,255 |
| Total Code Lines | 77.5 | 251.4 |
| Productivity (tokens/line) | 248.9 | 124.3 |
| Human Revision Cost | 2.5 | 0.83 |

MetaGPT demonstrates more coherent solutions than previous chat-based multi-agent systems while requiring fewer tokens per code line despite higher total token usage. The 100% task completion rate and significantly lower human revision cost (0.83 vs 2.5) highlight the value of structured SOPs.

### 4.3 Capabilities Analysis

| Capability | AutoGPT | LangChain | AgentVerse | ChatDev | MetaGPT |
|-----------|---------|----------|-----------|---------|---------|
| PRD generation | No | No | No | No | Yes |
| Technical design | No | No | No | No | Yes |
| API interface generation | No | No | No | No | Yes |
| Code generation | Yes | Yes | Yes | Yes | Yes |
| Precompilation execution | No | No | No | No | Yes |
| Role-based task management | No | No | No | Yes | Yes |
| Code review | No | No | Yes | Yes | Yes |

### 4.4 Ablation Study

#### Effectiveness of Roles

Adding specialized roles beyond Engineer consistently improves executability and reduces human revision needs. Complete 4-agent configuration achieves executability of 4.0 with human revision cost of 2.5.

#### Effectiveness of Executable Feedback

Executable feedback yields 4.2% and 5.4% improvement in Pass@1 on HumanEval and MBPP respectively, improving feasibility from 3.67 to 3.75 and reducing revision cost from 2.25 to 0.83.

---

## 5. Conclusion

MetaGPT presents a novel meta-programming framework that leverages SOPs to enhance the problem-solving capabilities of multi-agent systems. The integration of human-like SOPs inspires future research on human-inspired techniques for artificial multi-agent systems.

---

## Key Figures

### Figure 1: MetaGPT Framework Overview
Shows the assembly-line workflow from user requirements through Product Manager, Architect, Project Manager, Engineer, and QA Engineer roles, each producing structured outputs that feed into the next stage.

### Figure 2: Communication Protocol
Illustrates the publish-subscribe mechanism with a shared message pool. Agents subscribe to relevant message types based on their role profiles rather than engaging in unconstrained dialogue.

### Figure 3: Iterative Programming with Executable Feedback
Depicts the code-test-debug cycle where Engineers write code, run unit tests, receive execution results, and iteratively refine until tests pass or max retries reached.

### Figure 4: Software Development Example
Shows a complete development trace from user input ("write a python3 GUI app such that you can draw an image with it") through PRD generation, architectural design, task distribution, code generation, and QA testing.

---

## Appendix

### A: Outlook

#### A.1 Self-Improvement Mechanisms

Future implementations would enable agents to learn from the experience gained by developing each project, thus becoming more compatible and successful over time, connecting to recursive self-improvement concepts.

#### A.2 Multi-Agent Economies

The paper discusses potential integration with market-based credit assignment through the principles of supply and demand in free markets to assign value to contributing agents.

### B: Demo of Execution

**User Input Example**: "write a python3 GUI app such that you can draw an image with it"

**Product Manager Output**: Comprehensive PRD with Product Goals, User Stories, Competitive Analysis, Requirement Pool with prioritized features.

**Architect Output**: System design specifying implementation approach (Python's Tkinter for GUI, PIL for color capture), file list, data structures, and interface definitions.

**Project Manager Output**: Task distribution and shared knowledge requirements.

**Engineer Output**: Functional code files (ColorPicker class, GUI implementation).

**QA Engineer Output**: Comprehensive unit tests verifying functionality.

### C: SoftwareDev Dataset

| Task ID | Task | Prompt |
|---------|------|--------|
| 0 | Snake game | Create a snake game |
| 1 | Brick breaker | Create a brick breaker game |
| 2 | 2048 game | Create a 2048 game for web |
| 3 | Flappy bird | p5.js implementation with mouse controls |
| 4 | Tank battle | Create a tank battle game |
| 5 | Excel data processing | Streamlit + pandas data processing |
| 6 | CRUD management | Customer database with SQLite |
| 7 | Music transcriber | Sheet music transcription with neural networks |
| 8 | Press releases | Company news extraction and PDF export |
| 9 | Gomoku game | Gomoku with AI opponent |
| 10 | Weather dashboard | Interactive weather dashboard |

---

## Top References

1. Chen et al. (2021) -- Evaluating Large Language Models Trained on Code (Codex, HumanEval)
2. Austin et al. (2021) -- Program Synthesis with Large Language Models (MBPP)
3. Yao et al. (2023) -- ReAct: Synergizing Reasoning and Acting in Language Models
4. Shinn et al. (2023) -- Reflexion: Language Agents with Verbal Reinforcement Learning
5. Park et al. (2023) -- Generative Agents: Interactive Simulacra of Human Behavior
6. Li et al. (2023) -- CAMEL: Communicative Agents for Mind Exploration
7. Qian et al. (2023) -- ChatDev: Communicative Agents for Software Development
8. OpenAI (2023) -- GPT-4 Technical Report
9. Li et al. (2023) -- AlphaCode: Competition-Level Code Generation
10. Schmidhuber (1987) -- Evolutionary Principles in Self-Referential Learning
