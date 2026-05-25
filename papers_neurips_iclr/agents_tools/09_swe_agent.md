# SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

**Authors:** John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, Ofir Press

**Venue:** NeurIPS 2024

**arXiv:** [https://arxiv.org/abs/2405.15793](https://arxiv.org/abs/2405.15793)

---

## Abstract

Software engineering is a challenging task requiring interaction with code repositories, understanding of codebases, and the ability to create and edit files, navigate repositories, and execute tests. This paper introduces SWE-agent, a system that facilitates LM agents to autonomously use computers to solve software engineering tasks. SWE-agent's custom agent-computer interface (ACI) significantly enhances an agent's ability to create and edit code files, navigate entire repositories, and execute programs. On SWE-bench, SWE-agent achieves a 12.5% fix rate using GPT-4 Turbo, achieving the state-of-the-art among open-source methods at time of publication. On HumanEvalFix, it achieves an 87.7% pass@1, significantly surpassing the performance of non-interactive approaches.

---

## 1. Introduction

The paper draws an analogy to human-computer interaction (HCI): just as well-designed user interfaces improve human productivity, well-designed agent-computer interfaces (ACIs) improve LM agent performance. SWE-agent introduces a custom ACI specifically designed for software engineering tasks.

### Key Insight
The design of the interface between the agent and the computer is as important as the underlying model capability. A good ACI can dramatically improve agent performance on complex tasks.

## 2. Agent-Computer Interface (ACI) Design

### Design Principles

1. **Actions should be simple and easy to understand**: Complex bash pipelines are replaced with atomic, well-documented commands
2. **Actions should be compact and efficient**: Minimize the number of actions needed to accomplish common tasks
3. **Environment feedback should be informative**: Error messages should guide the agent toward correction
4. **Guardrails for robustness**: Prevent common failure modes through interface design

### Custom Commands

| Command | Description |
|---------|-------------|
| `open <file> [line_num]` | Opens a file with a scrollable window (100 lines) |
| `goto <line_num>` | Navigates to a specific line in the opened file |
| `scroll_up` / `scroll_down` | Scrolls the file view |
| `search_file <query> [file]` | Searches within a file |
| `search_dir <query> [dir]` | Searches across a directory |
| `find_file <name> [dir]` | Finds files by name |
| `create <file>` | Creates a new file |
| `edit <start>:<end>` | Edits lines in the current file with lint validation |

### Key ACI Features

**File Editor:**
- Shows a window of 100 lines at a time with line numbers
- Edit command includes syntax checking (linting) before applying changes
- If lint fails, the edit is rejected with an informative error message
- Prevents common issues like unclosed brackets, indentation errors

**Search Interface:**
- Unified search across files and directories
- Returns results with file paths and line numbers
- Avoids overwhelming output through pagination

**Error Handling:**
- Informative error messages guide agent toward corrections
- Guardrails prevent destructive operations
- Timeout mechanisms for hanging processes

## 3. Agent Architecture

### Thought-Action-Observation Loop

SWE-agent follows a ReAct-style loop:
1. **Thought**: Agent reasons about the current state and next steps
2. **Action**: Agent executes a command via the ACI
3. **Observation**: Environment returns output/feedback

### Prompt Design
- System message describes available commands and their syntax
- Demonstration examples show effective problem-solving patterns
- History window maintains recent interaction context

## 4. Experimental Results

### SWE-bench

| Method | Resolve Rate |
|--------|-------------|
| RAG (Claude 2) | 4.33% |
| RAG (GPT-4) | 1.31% |
| SWE-agent (GPT-4 Turbo) | **12.47%** |
| SWE-agent (Claude 3 Opus) | 10.50% |

SWE-agent resolves 12.47% of issues, the state-of-the-art among open-source methods at time of publication.

### HumanEvalFix

| Method | Pass@1 |
|--------|--------|
| CodeLlama-13B-Instruct | 20.7% |
| GPT-4 (non-interactive) | 47.0% |
| SWE-agent (GPT-4 Turbo) | **87.7%** |

### SWE-bench Lite

| Method | Resolve Rate |
|--------|-------------|
| SWE-agent (GPT-4 Turbo) | 18.00% |
| SWE-agent (Claude 3.5 Sonnet) | 33.60% |

## 5. ACI Design Ablations

### Impact of Interface Design Choices

| Configuration | SWE-bench Resolve Rate |
|--------------|----------------------|
| Shell-only (no custom ACI) | 3.97% |
| + File viewer | 6.73% |
| + File editor | 9.23% |
| + Search tools | 10.70% |
| + Error feedback | 12.47% |

Each ACI component contributes meaningfully to overall performance. The full ACI provides a 3.1x improvement over the shell-only baseline.

### Key Ablation Findings
- **File viewer** is the single most impactful component (+2.76%)
- **Linting on edit** prevents many syntactic errors that waste agent steps
- **Search interface** reduces navigation overhead in large repositories
- **Informative error messages** enable faster self-correction

## 6. Analysis

### Behavioral Patterns
- Successful trajectories show focused, systematic exploration
- Failed trajectories often involve repetitive editing without testing
- Agent spends ~40% of actions on navigation, ~30% on editing, ~30% on testing

### Cost Analysis
- Average cost per instance: ~$1.50 (GPT-4 Turbo)
- Average trajectory length: ~25 actions
- Average time per instance: ~3 minutes

## 7. Limitations

- Performance still far below human developers
- Struggles with complex multi-file changes
- Cannot handle tasks requiring external dependencies or environment setup
- ACI design is specific to text-based code editing (no IDE features)
- Cost per issue resolution is non-trivial at scale

---

## Figure Descriptions

- **Figure 1:** Comparison between shell-only interface and SWE-agent's custom ACI showing improved agent interaction patterns
- **Figure 2:** SWE-agent architecture with the ACI mediating between the LM agent and the computer
- **Figure 3:** File editor with linting feedback example
- **Figure 4:** Performance comparison across different ACI configurations (ablation)
- **Figure 5:** Example successful trajectory solving a real GitHub issue

---

## Top 10 References

1. Jimenez, C. E., et al. (2024). SWE-bench: Can language models resolve real-world GitHub issues? *ICLR*.
2. Yao, S., et al. (2022). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
3. OpenAI (2023). GPT-4 technical report. *arXiv:2303.08774*.
4. Chen, M., et al. (2021). Evaluating large language models trained on code. *arXiv* (Codex/HumanEval).
5. Shinn, N., et al. (2023). Reflexion: Language agents with verbal reinforcement learning. *NeurIPS*.
6. Wang, X., et al. (2024). Executable code actions elicit better LLM agents. *arXiv* (CodeAct).
7. Zhou, S., et al. (2023). WebArena: A realistic web environment for building autonomous agents. *ICLR*.
8. Liu, X., et al. (2023). AgentBench: Evaluating LLMs as agents. *ICLR*.
9. Anthropic (2024). Claude 3 model card. *Technical report*.
10. Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning. *NeurIPS*.
