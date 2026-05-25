# AgentBench: Evaluating LLMs as Agents

**Authors:** Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu, Hangliang Ding, Kaiwen Men, Kejuan Yang, Shudan Zhang, Xiang Deng, Aohan Zeng, Zhengxiao Du, Chenhui Zhang, Sheng Shen, Tianjun Zhang, Yu Su, Huan Sun, Minlie Huang, Yuxiao Dong, Jie Tang

**Venue:** ICLR 2024

**arXiv:** [https://arxiv.org/abs/2308.03688](https://arxiv.org/abs/2308.03688)

---

## Abstract

Large Language Models (LLMs) are becoming increasingly smart and autonomous, targeting real-world pragmatic missions beyond traditional NLP tasks. As a result, there has been a surge in research on LLMs as autonomous agents. This paper introduces AgentBench, a multi-dimensional evolving benchmark that currently consists of 8 distinct environments to assess LLM-as-Agent's reasoning and decision-making abilities in a multi-turn open-ended generation setting. The evaluation comprehensively examines 29 LLMs, revealing a significant performance gap between top commercial LLMs and open-source competitors. The research identifies key limitations including weak long-term reasoning and instruction-following capabilities, and finds that training on high-quality multi-round alignment data can boost performance, while code-based training shows mixed results.

---

## 1. Introduction

AgentBench addresses the need for systematic evaluation of LLMs as autonomous agents. Prior benchmarks either focus on single domains or static tasks. AgentBench provides a comprehensive, multi-dimensional evaluation across diverse interactive environments.

### Key Contributions
1. Comprehensive benchmark framework with 8 distinct environments across 3 grounding types
2. Empirical evaluation of 29 LLMs (commercial and open-source)
3. Integrated modular evaluation toolkit with Server-Client architecture

## 2. Benchmark Composition

### Eight Environments

| Category | Environment | Key Characteristics |
|----------|-------------|-------------------|
| Code-grounded | Operating System (OS) | Bash command execution |
| Code-grounded | Database (DB) | SQL queries |
| Code-grounded | Knowledge Graph (KG) | Entity relationships, SPARQL-like |
| Game-grounded | Digital Card Game (DCG) | Strategic reasoning |
| Game-grounded | Lateral Thinking Puzzles (LTP) | Creative problem solving |
| Game-grounded | House-Holding (HH) | ALFWorld commonsense tasks |
| Web-grounded | Web Shopping (WS) | WebShop navigation |
| Web-grounded | Web Browsing (WB) | Mind2Web-style browsing |

### Dataset Statistics

The benchmark includes 269 development and 1,014 test samples across environments, with estimated interaction rounds ranging from 5 to 50 per task.

## 3. Methodology

### POMDP Framework

Evaluation follows a Partially Observable Markov Decision Process (POMDP) with:
- State space, action space, transition functions
- Reward assignments, task instructions, observation spaces
- Chain-of-thought prompting with temperature=0 for determinism

### Scoring Mechanism

Rather than simple averaging (which favors naturally higher-scoring tasks), each task's average score is normalized to 1.0 across all tested models before computing overall scores, ensuring balanced representation.

### Outcome Classifications

Five categories:
- **Complete:** Successful task resolution
- **Task Limit Exceeded (TLE):** Ran out of interaction steps
- **Invalid Format (IF):** Output doesn't match expected format
- **Invalid Action (IA):** Action violates environment constraints
- **Context Limit Exceeded (CLE):** Exceeded context window

## 4. Main Results

### Overall Performance

| Model | Overall Score | OS | DB | KG | DCG | LTP | HH | WS | WB |
|-------|-------------|----|----|----|----|-----|----|----|-----|
| GPT-4 | 4.01 | 42.4 | 32.5 | 47.6 | 78.8 | 4.17 | 78.0 | 73.6 | 3.01 |
| ChatGPT | 2.76 | 37.2 | 30.1 | 33.0 | 36.4 | 7.22 | 39.0 | 62.0 | 2.79 |
| Claude | 2.30 | 27.2 | 22.5 | 28.0 | 66.7 | 3.89 | 42.0 | 63.6 | 2.51 |
| codellama-34b (best OSS) | 0.96 | - | - | - | - | - | - | - | - |

**Key finding:** GPT-4 achieves 4.01 overall; the highest-performing open-source model (codellama-34b) scores only 0.96.

### Failure Analysis

| Environment | TLE (%) | IF (%) | IA (%) | CLE (%) |
|-------------|---------|--------|--------|---------|
| Knowledge Graph | 67.9 | 12.3 | 8.4 | 11.4 |
| Database | 28.3 | 53.3 | 5.0 | 13.4 |
| Digital Card Game | 22.7 | 38.5 | 30.3 | 8.5 |
| House Holding | 14.1 | 6.4 | 64.1 | 15.4 |
| Web Browsing | 52.1 | 28.4 | 8.4 | 11.1 |

### Impact of Training Approaches

**Code Training Effects:**
- CodeLlama vs Llama-2 comparison shows code-focused training improves procedural tasks (Web Shopping) but may diminish general reasoning (Digital Card Game)
- Creates an "ambivalent impact" on agent capabilities

**High-Quality Alignment Data:**
- Vicuna-13b (aligned with GPT-4 ShareGPT data) outperforms identically-sized Llama-2-13b
- "High-quality alignment remains key to developing better LLM agents"

**Unexpected Finding:**
- Llama-2-13b and Llama-2-70b show surprisingly similar performance despite 5x parameter difference
- Hypothesized cause: insufficient pre-training or inadequate instruction-following alignment in the larger model

## 5. Technical Architecture

### Evaluation Toolkit

- **Decoupled Architecture:** Separate Task Servers, Agent Servers, and Evaluation Clients via HTTP
- **Docker Containerization:** Prevents cross-task environment conflicts
- **Network Flow Optimization:** Edmonds-Karp maximum flow algorithm for optimal worker allocation

## 6. Recommendations for Improvement

1. **Enhanced instruction following**: Invalid format errors are a significant failure source
2. **Long-term reasoning**: TLE failures dominate many environments
3. **Balanced training strategy**: Code training should be balanced against general reasoning
4. **High-quality alignment data**: Premium datasets substantially improve agent performance

---

## Figure Descriptions

- **Figure 1:** Overview of AgentBench's 8 environments organized by grounding type (code, game, web)
- **Figure 2:** Architecture diagram showing Server-Client evaluation framework
- **Figure 3:** Performance comparison across models showing the commercial-vs-open-source gap
- **Figure 4:** Failure mode distribution across environments
- **Figure 5:** Scaling analysis of model size vs. agent performance

---

## Top 10 References

1. Brown, T. B., et al. (2020). Language models are few-shot learners. *NeurIPS*.
2. Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS*, 35:24824-24837.
3. Yao, S., et al. (2023). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
4. Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback. *NeurIPS*, 35:27730-27744.
5. OpenAI (2023). GPT-4 technical report. *arXiv:2303.08774*.
6. Touvron, H., et al. (2023). Llama 2: Open foundation and fine-tuned chat models. *arXiv:2307.09288*.
7. Shridhar, M., et al. (2020). ALFWorld: Aligning text and embodied environments for interactive learning. *ICLR*.
8. Cote, M., et al. (2019). TextWorld: A learning environment for text-based games. *CGW 2018*.
9. Chen, M., et al. (2021). Evaluating large language models trained on code. *arXiv:2107.03374*.
10. Hendrycks, D., et al. (2021). Measuring massive multitask language understanding (MMLU). *ICLR*.
