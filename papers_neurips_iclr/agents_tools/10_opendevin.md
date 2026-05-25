# OpenHands: An Open Platform for AI Software Developers as Generalist Agents

**Authors:** Xingyao Wang, Boxuan Li, Yufan Song, Frank F. Xu, Xiangru Tang, Mingchen Zhuge, Jiayi Pan, Yueqi Song, Bowen Li, Jaskirat Singh, Hoang H. Tran, Fuqiang Li, Ren Ma, Mingzhang Zheng, Bill Qian, Yanjun Shao, Niklas Muennighoff, Yizhe Zhang, Binyuan Hui, Junyang Lin, Robert Brennan, Hao Peng, Heng Ji, Graham Neubig

**Venue:** ICLR 2025

**arXiv:** [https://arxiv.org/abs/2407.16741](https://arxiv.org/abs/2407.16741)

---

## Abstract

Software is one of the most powerful tools that humans have at their disposal; it allows a skilled programmer to interact with the world in complex and profound ways. OpenHands is an open platform for the development of powerful AI agents that interact with the world in ways similar to a human developer: by writing code, interacting with a command line, and browsing the web. The platform supports multiple agents, sandboxed execution environments, and comprehensive evaluation across 15 benchmarks. Released as MIT-licensed open source, OpenHands has garnered over 32K GitHub stars with contributions from 188+ contributors across academia and industry.

---

## 1. Introduction

OpenHands (formerly OpenDevin) provides a unified platform for developing AI software agents. Unlike specialized tools, it enables generalist agents that can write code, execute commands, browse the web, and interact with diverse applications through a single framework.

## 2. Core Architecture

### 2.1 Agent Definition and Implementation

Agents perceive environmental state and produce actions. The platform uses an **event stream architecture** tracking chronological action-observation pairs.

Core actions:
- `IPythonRunCellAction`: Execute Python code in Jupyter
- `CmdRunAction`: Execute bash commands
- `BrowserInteractiveAction`: Web interaction via BrowserGym's DSL

### 2.2 Agent Runtime

Docker-sandboxed environment providing:
- Isolated container per task session with configurable workspace
- REST API server managing bash shell, Jupyter IPython server, and Chromium browser (Playwright-based)
- Support for arbitrary Docker images with OpenHands API installation
- Rich browser observations: HTML, DOM, accessibility trees, screenshots

### 2.3 AgentSkills: Extensible Agent-Computer Interface

Reusable utility library automatically imported into Jupyter:
- File editing (`edit_file`, `scroll_up/down`)
- Multi-modal document parsing (`parse_image`, `parse_pdf`)
- Inclusion criteria: tasks difficult for LLMs to code directly OR requiring external model calls
- Rigorous unit testing for reliability

### 2.4 Agent Delegation

`AgentDelegateAction` enables task distribution between specialized agents. Example: generalist CodeActAgent delegates web browsing to specialized BrowsingAgent.

## 3. AgentHub

Community-contributed agent implementations:

| Agent | Description |
|-------|-------------|
| **CodeActAgent** | Default generalist; code execution + NL conversation |
| **BrowsingAgent** | Web specialist; improved observations/actions, zero-shot |
| **GPTSwarm** | Multi-agent system using optimizable graphs |
| **Micro Agents** | Specialized agents with custom prompts on top of generalists |

## 4. Evaluation Framework

### Integrated Benchmarks (15 total)

| Category | Benchmarks |
|----------|-----------|
| Software Engineering | SWE-Bench, HumanEvalFix, BIRD, BioCoder, ML-Bench, Gorilla APIBench, ToolQA |
| Web Browsing | WebArena, MiniWoB++ |
| Miscellaneous | GAIA, GPQA, AgentBench, MINT, ProofWriter, Entity Deduction Arena |

### 4.1 Software Engineering Results

| Benchmark | Model | Performance |
|-----------|-------|-------------|
| SWE-Bench Lite | claude-3.5-sonnet | 26.0% |
| HumanEvalFix | gpt-4o-2024-05-13 | 79.3% |
| ML-Bench | gpt-4o-2024-05-13 | 76.5% |
| BIRD (Text-to-SQL) | gpt-4o-2024-05-13 | 47.3% |
| BioCoder (Java) | gpt-4o-2024-05-13 | 44.0% |
| Gorilla APIBench | gpt-4o-2024-05-13 | 36.4% |
| ToolQA | gpt-4o-2024-05-13 | 47.2% |

Key: HumanEvalFix nearly doubles non-agent approaches. ML-Bench 76.5% exceeds specialist SWE-Agent (42.6%). BioCoder shows 44% vs 6.4% for GPT-4 alone.

### 4.2 Web Browsing Results

| Benchmark | Agent/Model | Performance |
|-----------|-------------|-------------|
| WebArena | BrowsingAgent (claude-3.5-sonnet) | 15.5% |
| WebArena | CodeActAgent v1.8 (claude-3.5-sonnet) | 15.3% |
| MiniWoB++ | BrowsingAgent (gpt-4o) | 40.8% |

### 4.3 Miscellaneous Results

| Benchmark | Agent/Model | Performance |
|-----------|-------------|-------------|
| GAIA (L1) | GPTSwarm (gpt-4o) | 32.1% |
| GPQA (Diamond) | CodeActAgent (claude-3.5-sonnet) | 52.0% |
| AgentBench (OS) | CodeActAgent v1.5 (gpt-4o) | 57.6% |
| MINT (Math) | CodeActAgent v1.5 (gpt-4o) | 77.3% |
| ProofWriter | CodeActAgent v1.5 (gpt-4o) | 78.8% |

GPQA improvements exceed prior state-of-the-art by 9.6% (main) and 12.3% (diamond subset).

## 5. Framework Comparison

OpenHands uniquely provides all of the following:
- Graphical UI
- Standardized tool library
- Sandboxed code execution
- Web browser integration
- Multi-agent collaboration
- Human-AI collaboration
- AgentHub (community agents)
- Comprehensive evaluation framework
- Quality control integration tests

## 6. Key Contributions

1. **Event stream architecture** for flexible agent-environment interaction
2. **Sandboxed Docker runtime** enabling safe cross-platform code execution
3. **Standardized tool library** (AgentSkills) for agent development
4. **Multi-agent delegation** supporting specialized agent composition
5. **Comprehensive evaluation** across 15 benchmarks spanning diverse domains

---

## Figure Descriptions

- **Figure 1:** OpenHands platform overview showing agents, runtime, and evaluation components
- **Figure 2:** Event stream architecture with action-observation pairs
- **Figure 3:** Docker sandbox architecture with REST API server
- **Figure 4:** AgentHub showing community-contributed agent implementations
- **Figure 5:** Performance radar chart across all 15 benchmarks

---

## Top 10 References

1. Wang, X., et al. (2024). Executable code actions elicit better LLM agents (CodeAct). *arXiv*.
2. Jimenez, C. E., et al. (2024). SWE-Bench: Can language models resolve real-world GitHub issues? *ICLR*.
3. Yang, J., et al. (2024). SWE-agent: Agent-computer interfaces enable automated software engineering. *NeurIPS*.
4. Zhou, S., et al. (2023). WebArena: A realistic web environment for building autonomous agents. *ICLR*.
5. Zhuge, M., et al. (2024). Language agents as optimizable graphs (GPTSwarm). *arXiv*.
6. Liu, X., et al. (2023). AgentBench: Evaluating LLMs as agents. *ICLR*.
7. Rein, D., et al. (2023). GPQA: A graduate-level Google-proof Q&A benchmark. *arXiv*.
8. Mialon, G., et al. (2023). GAIA: A benchmark for general AI assistants. *arXiv*.
9. Wu, Q., et al. (2023). AutoGen: Enabling next-gen LLM applications via multi-agent conversation. *arXiv*.
10. Hong, S., et al. (2023). MetaGPT: Meta programming for multi-agent collaborative framework. *arXiv*.
