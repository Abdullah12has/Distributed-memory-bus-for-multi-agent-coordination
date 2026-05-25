# ChatDev: Communicative Agents for Software Development

**Authors:** Chen Qian, Wei Liu, Hongzhang Liu, Nuo Chen, Yufan Dang, Jiahao Li, Cheng Yang, Weize Chen, Yusheng Su, Xin Cong, Juyuan Xu, Dahai Li, Zhiyuan Liu, Maosong Sun

**Venue:** ACL 2024

**ArXiv:** [2307.07924](https://arxiv.org/abs/2307.07924)

**Code:** https://github.com/OpenBMB/ChatDev

---

## Abstract

ChatDev presents a framework where specialized agents driven by large language models (LLMs) are guided in what to communicate (via chat chain) and how to communicate (via communicative dehallucination). These agents collaborate through natural language across design, coding, and testing phases. The authors found that natural language benefits system design while programming language aids debugging, establishing language as a bridge for multi-agent autonomous problem-solving.

---

## 1. Introduction

The paper addresses software engineering's complexity by proposing an LLM-driven paradigm that encompasses requirements analysis, code development, system testing, and documentation generation. The framework mitigates code hallucinations through structured task decomposition and cross-examination mechanisms rather than requiring specialized models at each development phase.

## 2. ChatDev Architecture

### Core Components

- **Chat Chain:** Decomposes development into sequential atomic subtasks using a waterfall model with four phases: designing, coding, testing, and documenting
- **Multi-Agent Roles:** CEO, CPO, CTO, programmers, reviewers, testers, and designers collaborate through structured dialogue
- **Memory Stream:** Maintains comprehensive dialogue history enabling context-aware decision-making

### Key Mechanisms

| Mechanism | Purpose |
|-----------|---------|
| Role Specialization | Assigns distinct functions via system prompts |
| Memory Stream | Records dialogue history for informed decisions |
| Self-Reflection | Extracts conclusions when consensus is reached |
| Thought Instruction | Explicitly guides code modifications through role-swapping |
| Version Evolution | Restricts visibility to latest code versions |

## 3. Development Phases

**Designing Phase:** CEO, CPO, and CTO determine software modality and programming language through collaborative discussion.

**Coding Phase:** CTO and programmers implement source code; designers create GUI graphics using text-to-image tools.

**Testing Phase:** Programmers, reviewers, and testers identify and resolve bugs through peer review and system testing.

**Documenting Phase:** CEO, CPO, CTO, and programmers generate dependency specifications and user manuals.

## 4. Experimental Results

| Metric | Min | Max | Average |
|--------|-----|-----|---------|
| Code Files | 2.0 | 8.0 | 4.26 |
| Asset Files | 0.0 | 21.0 | 8.74 |
| Lines of Code | 39 | 359 | 131.61 |
| Version Updates | 5 | 42 | 13.23 |
| Development Time (s) | 169 | 1,030 | 409.84 |
| Total Tokens | 15,294 | 111,019 | 48,469.60 |
| Average Cost | -- | -- | $0.2967 |

**Key findings:**
- Approximately 86.66% of generated software executed flawlessly
- 13.33% failures attributed to token limits (50%) and dependency issues (50%)
- Average development time: under 7 minutes
- Most common code issues: unimplemented methods (34.85%), missing imports (19.70%)
- Most frequent runtime bugs: module not found (45.76%), attribute errors (15.25%)

## 5. NLDD Dataset

The researchers created a Natural Language Dataset for Dev (NLDD) containing 1,200 software prompt entries using a three-stage strategy (random sampling, sequential sampling, and verification) to facilitate NL2Software research.

## 6. Discussion and Limitations

- Inherent randomness produces variable outputs across runs
- Designer-generated images may not consistently enhance UI aesthetics
- LLM biases may produce non-standard code patterns
- Framework struggles with large-scale, high-level software requirements
- Lacks malicious intent identification for sensitive file operations

---

## Figures

- **Figure 1:** Overview of ChatDev showing the chat chain architecture with four development phases
- **Figure 2:** Role-playing dialogue examples between CEO, CTO, and programmers
- **Figure 3:** Examples of generated software applications (Gomoku, 2048, calculator)
- **Figure 4:** Thought instruction mechanism for code modification guidance

---

## Key References

1. Brown, T., et al. (2020) -- Language models are few-shot learners (GPT-3)
2. Chen, M., et al. (2021) -- Evaluating large language models trained on code (Codex)
3. Du, Y., et al. (2023) -- Improving factuality and reasoning through multiagent debate
4. Li, G., et al. (2023) -- CAMEL: Communicative agents for mind exploration
5. Park, J.S., et al. (2023) -- Generative agents: Interactive simulacra of human behavior
6. Wei, J., et al. (2022) -- Chain-of-thought prompting elicits reasoning
7. Yao, S., et al. (2023) -- ReAct: Synergizing reasoning and acting
8. Hong, S., et al. (2023) -- MetaGPT: Meta programming for multi-agent collaborative framework
9. Qin, Y., et al. (2023) -- Tool learning with foundation models
10. Touvron, H., et al. (2023) -- LLaMA: Open and efficient foundation language models
