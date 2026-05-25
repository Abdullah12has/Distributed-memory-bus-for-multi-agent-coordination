# TaskWeaver: A Code-First Agent Framework

**Authors:** Bo Qiao, Liqun Li, Xu Zhang, Shilin He, Yu Kang, Chaoyun Zhang, Fangkai Yang, Hang Dong, Jue Zhang, Lu Wang, Minghua Ma, Pu Zhao, Si Qin, Xiaoting Qin, Chao Du, Yong Xu, Qingwei Lin, Saravan Rajmohan, Dongmei Zhang

**Venue:** arXiv preprint (Microsoft Research, 2023)

**arXiv:** [https://arxiv.org/abs/2311.17541](https://arxiv.org/abs/2311.17541)

---

## Abstract

The increasing demand for efficient handling of domain-specific tasks with LLM-powered agents necessitates a flexible and extensible framework. Existing frameworks face limitations in supporting rich data structures, flexible plugin usage, and dynamic plugin composition. TaskWeaver addresses these limitations by converting user requests into executable code and treating user-defined plugins as callable functions. It supports rich data structures (e.g., DataFrames), flexible plugin usage with automatic selection, leverages LLM coding capabilities for complex logic, and incorporates domain-specific knowledge through configurable examples. TaskWeaver provides a powerful and flexible framework for creating intelligent conversational agents capable of handling complex tasks.

---

## 1. Introduction

TaskWeaver is developed by Microsoft Research to address limitations in existing LLM agent frameworks (LangChain, Semantic Kernel) that rely on text-based expression and struggle with rich data structures. The code-first approach leverages Python's dominance in data analysis.

## 2. Core Architecture

### Three Primary Components

**Planner:**
- Entry point for user requests
- Decomposes requests into subtasks
- Orchestrates overall system execution
- Maintains dialogue with users
- Two-phase planning: initial plans refined by merging sequential subtasks

**Code Generator (CG):**
- Synthesizes Python code snippets based on incoming requests
- Incorporates available plugins and domain-specific examples
- Supports restricted code generation via AST-based verification

**Code Executor (CE):**
- Executes generated code within isolated environments
- Maintains state throughout conversations (like Jupyter notebooks)
- Reports execution results back to the Planner

## 3. Key Design Considerations

| # | Design Principle | Description |
|---|-----------------|-------------|
| 1 | Code-First Analysis | Generates executable Python programs rather than text-based expressions |
| 2 | Restricted Code Generation | AST-based post-verification ensures safety before execution |
| 3 | Stateful Execution | Maintains Python state across conversation rounds |
| 4 | Intelligent Plan Decomposition | Merges sequential subtasks to minimize LLM calls |
| 5 | Self-Reflection | Error correction at both planning and code generation stages |
| 6 | Scalable Plugin Usage | Dynamic plugin selection for specific tasks |
| 7 | Domain Knowledge Integration | YAML-formatted examples guide domain-specific behavior |
| 8 | Security and Safety | Separate Docker containers for worker processes |
| 9 | Usability | Python function -> plugin conversion tools |
| 10 | Cost Effectiveness | Different LLM models per role based on complexity |

## 4. Conceptual Framework

| Concept | Definition |
|---------|-----------|
| **Session** | Initiated by user's initial request, terminated upon reset/expiration |
| **Round** | Spans from receiving user input to providing response |
| **Post** | Individual messages between Planner and Code Interpreter |
| **Example** | In-context learning demonstrations in YAML format |
| **Plugin** | User-defined Python functions encapsulating domain logic |
| **Role** | Conversational objects implementing reply interfaces |

## 5. Plugin System

**Plugin Schema:** YAML-formatted definitions including function name, parameters, return types, and descriptions used for code generation.

**Plugin Implementation:** Actual Python implementations distinct from schemas, allowing LLMs to generate code without implementation details.

## 6. Multi-Agent Expansion

Two integration strategies:
1. **Agent Collaboration via Plugins/Roles**: Invoke external agents through plugin functions or encapsulate agent functionality within new roles
2. **Integration into Existing Frameworks**: Embed TaskWeaver agents into pre-existing multi-agent systems

## 7. Evaluation

### Evaluation Methodology

Two novel roles:
- **Examiner Role**: Supervises task-aligned conversations, authorizes agent clarification requests
- **Judge Role**: Compares solutions against ground truth

### Benchmarks

| Dataset | Description | Scale |
|---------|-------------|-------|
| Eval-Cases | Custom test cases for design requirements | 23 cases |
| DS-1000 | Data science code generation from StackOverflow | 816 cases |
| InfiAgent-DABench | Data analytics tasks with CSV inputs | 258 cases |
| DSEval | Four benchmarks (Exercise, SO, LeetCode, Kaggle) | 294 problems |

### Results

| Benchmark | GPT-3.5 | GPT-4 |
|-----------|---------|-------|
| Eval-Cases | 0.42 | 0.87 |
| DS-1000 | 0.40 | 0.60 |
| InfiAgent-DABench | 0.70 | 0.88 |
| DSEval | 0.36 | 0.72 |

## 8. Case Studies

### Anomaly Detection
Integrates `pull_data_sql()` and `anomaly_detection()` plugins. Successfully identified 11 anomalies in time series data through sequential plugin invocation and visualization code generation.

### Stock Price Forecasting
Demonstrates auto-correction: initial attempts using deprecated `pandas_datareader` API were automatically corrected to use `yfinance`, generating ARIMA-based forecasts.

### Design Verification Demonstrations
- **ReAct Capability**: Sequential file reading chain navigation
- **Plan Decomposition**: Merged data loading + statistical calculations, reducing LLM calls from 6 to 3
- **Plugin-Only Mode**: Restrictive configuration preventing arbitrary code
- **Stateful Execution**: DataFrame preservation across conversation rounds
- **Auto-Correction**: Error-informed code regeneration
- **Safety Verification**: Prevented file deletion and env variable access

## 9. Experience and Personalization

The framework implements "experience memory" extracting actionable insights from conversation histories. Tips stored in pools for retrieval during similar future requests.

## 10. Related Work Comparison

| Framework | Limitation vs. TaskWeaver |
|-----------|-------------------------|
| LangChain, Semantic Kernel | Text-based expression, poor rich data support |
| AutoGen, XAgent, JARVIS | Limited flexibility for ad-hoc custom code |
| Open Interpreter, Cradle, UFO | Specialized for particular tasks |
| MetaGPT Data Interpreter | Single-agent focus |

---

## Figure Descriptions

- **Figure 1:** TaskWeaver architecture showing Planner, Code Generator, and Code Executor components
- **Figure 2:** Plugin system architecture with schema and implementation separation
- **Figure 3:** Anomaly detection case study workflow
- **Figure 4:** Stock price forecasting with auto-correction example
- **Figure 5:** Multi-agent integration patterns

---

## Top 10 References

1. Brown, T., et al. (2020). Language models are few-shot learners. *NeurIPS*.
2. Yao, S., et al. (2022). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
3. Wu, Q., et al. (2023). AutoGen: Enabling next-gen LLM applications via multi-agent conversation. *arXiv*.
4. Hong, S., et al. (2023). MetaGPT: Meta programming for multi-agent collaborative framework. *arXiv*.
5. Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning. *NeurIPS*.
6. Lai, Y., et al. (2022). DS-1000: A natural and reliable benchmark for data science code generation. *arXiv*.
7. Hu, X., et al. (2024). InfiAgent-DABench: Evaluating agents on data analysis tasks. *arXiv*.
8. Zhang, Y., et al. (2024). Benchmarking data science agents. *arXiv*.
9. OpenAI (2023). GPT-4 technical report. *arXiv:2303.08774*.
10. Wang, L., et al. (2023). A survey on large language model based autonomous agents. *arXiv*.
