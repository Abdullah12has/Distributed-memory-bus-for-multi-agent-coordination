# AgentScope: A Flexible yet Robust Multi-Agent Platform

**Authors:** Dawei Gao, Zitao Li, Xuchen Pan, Weirui Kuang, Zhijian Ma, Bingchen Qian, Fei Wei, Wenhao Zhang, Yuexiang Xie, Daoyuan Chen, Liuyi Yao, Hongyi Peng, Zeyu Zhang, Lin Zhu, Chen Cheng, Hongzhu Shi, Yaliang Li, Bolin Ding, Jingren Zhou

**Venue:** arXiv preprint, 2024

**ArXiv:** [2402.14034](https://arxiv.org/abs/2402.14034)

**Code:** https://github.com/modelscope/agentscope

---

## Abstract

AgentScope addresses challenges in multi-agent development by introducing a platform centered on message exchange for agent communication. Key features include syntactic tools, built-in agents and service functions, user-friendly interfaces, and mechanisms for fault tolerance. The system employs an actor-based distribution framework enabling conversion between local and distributed setups with automatic optimization.

---

## 1. Introduction

The paper identifies four core challenges in multi-agent development: agent coordination complexity, LLM unreliability, multi-modal data handling, and distributed deployment difficulties.

## 2. Overview

### Basic Concepts

| Concept | Description |
|---------|-------------|
| Message | Python dictionaries with mandatory fields (name, content) and optional field (url) for multi-modal data |
| Agent | Primary actors with `reply` and `observe` interfaces |
| Workflow | Ordered sequences of agent executions |
| Service Functions/Tools | APIs returning formatted responses |

### Architecture

Three hierarchical layers:
1. **Utility Layer:** Core services and model API invocation
2. **Manager and Wrapper Layer:** Resource management and fault tolerance
3. **Agent Layer:** Workflow construction and communication

User interaction through Terminal, Web UI, Gradio interface, and workstation.

## 3. High Usability

### Syntactic Sugar

Pipeline abstraction supports sequential, conditional, and iterative patterns. Message Hub enables broadcast communication among agent groups.

### Built-in Agent Types

| Agent Name | Function |
|---|---|
| UserAgent | User proxy |
| DialogAgent | General dialog agent with configurable role |
| DictDialogAgent | Dictionary-format response agent |
| ReActAgent | Reasoning and tool-using agent |
| ProgrammerAgent | Python code writing and execution |
| TextToImageAgent | Image generation |
| RpcUserAgent | Distributed user proxy |
| RpcDialogAgent | Distributed dialog agent |

### Graphical Application Development

Drag-and-drop workstation using DAG representation with JSON execution or Python compilation options. Six node types: model, service, agent, pipeline, message, copy.

### Automatic Prompt Tuning

System prompt generation from natural language descriptions with in-context learning and customizable matching strategies.

## 4. Fault-Tolerant Mechanisms

### Error Classification

| Error Type | Example | Strategy |
|---|---|---|
| Accessibility errors | Timeouts, network issues | Auto-retry |
| Rule-resolvable errors | Formatting problems | Rule-based correction |
| Model-resolvable errors | Content issues | Agent-level fault handling |
| Unresolvable errors | API key expiration | Graceful failure |

Customizable fault handlers via `parse_func` and `fault_handler` parameters. Logging system with CHAT level for agent conversations.

## 5. Multi-Modal Applications

Data management through generation (DALL-E, GPT-4V), storage (local file manager), and transmission (URL-based message attributes with lazy loading).

## 6. Tool Usage

Implements ReAct algorithm with four steps:
1. Function Preparation: Parse and preprocess service functions
2. Instruction Preparation: Generate tool descriptions and calling formats
3. Iterative Reasoning: LLMs generate strategic reasoning
4. Iterative Acting: Parse responses, execute functions, handle errors

## 7. Retrieval-Augmented Generation (RAG)

- "One-Stop" configuration via single JSON file
- Knowledge banks for shared knowledge across agents
- RAG agents supporting multiple RAG objects with customizable fusion
- Dynamic knowledge updates and directory monitoring

## 8. Actor-based Distributed Framework

Key innovations:
- Automatic parallel optimization without static graphs
- Single procedural style programming for distributed workflows
- Hybrid local/distributed agent support
- Placeholder messages for non-blocking execution
- One-click deployment with AgentScope Studio

## 9. Signature Applications

1. Basic conversation (user-agent dialogue)
2. Group conversation with @mentions
3. Werewolf game (complex multi-agent role-playing)
4. Distributed deployed agents (parallel cross-machine operations)
5. RAG agents (AgentScope Copilot)
6. Web search and retrieval agents
7. ReAct agents (natural language to SQL)
8. AgentScope Workstation (graphical builder)

---

## Figures

- **Figure 1:** Three-layer architecture showing utility, manager/wrapper, agent layers, and user interaction interfaces
- **Figure 2:** Terminal dialogue display from a werewolf game
- **Figure 3:** Multi-modal web UI interactions between agents
- **Figure 4:** Drag-and-drop programming workstation interface
- **Figure 5:** Multi-modal data lifecycle (generation, storage, transmission)
- **Figure 6:** ReAct-based tool usage workflow
- **Figure 7:** Response parsers (Markdown blocks, JSON, tagged contents)
- **Figure 8:** Distributed application example showing parallel processes

---

## Key References

1. Park, J.S., et al. (2023) -- Generative agents: Interactive simulacra of human behavior
2. Wu, Q., et al. (2023) -- AutoGen: Enabling next-gen LLM applications
3. Hong, S., et al. (2023) -- MetaGPT: Meta programming for multi-agent collaboration
4. Li, G., et al. (2023) -- CAMEL: Communicative agents for mind exploration
5. Qian, C., et al. (2023) -- ChatDev: Communicative agents for software development
6. Yao, S., et al. (2023) -- ReAct: Synergizing reasoning and acting
7. Wei, J., et al. (2022) -- Chain-of-thought prompting
8. Lewis, P., et al. (2020) -- Retrieval-augmented generation
9. Hewitt, C. (1977) -- Actor model of computation
10. Chen, W., et al. (2023) -- AgentVerse: Multi-agent collaboration
