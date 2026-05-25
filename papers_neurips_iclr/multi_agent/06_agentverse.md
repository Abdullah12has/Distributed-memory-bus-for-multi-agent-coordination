# AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors

**Authors:** Weize Chen, Yusheng Su, Jingwei Zuo, Cheng Yang, Chenfei Yuan, Chi-Min Chan, Heyang Yu, Yaxi Lu, Yi-Hsin Hung, Chen Qian, Yujia Qin, Xin Cong, Ruobing Xie, Zhiyuan Liu, Maosong Sun, Jie Zhou

**Venue:** Under review (arXiv preprint, 2023)

**ArXiv:** [2308.10848](https://arxiv.org/abs/2308.10848)

**Code:** https://github.com/OpenBMB/AgentVerse/

---

## Abstract

AgentVerse presents a framework for autonomous LLM-based agents to collaborate effectively as groups. The authors demonstrate that multi-agent groups can outperform single agents when deployed dynamically. The work also examines how social behaviors among individual agents within a group emerge during collaborative tasks and discusses strategies to enhance group performance by leveraging positive behaviors while mitigating negative ones.

---

## 1. Introduction

AgentVerse proposes a multi-agent framework inspired by human group dynamics to enable LLM-powered agents to collaborate effectively. The framework addresses limitations in prior work by offering dynamic agent composition rather than static role assignments across diverse, complex tasks.

## 2. AgentVerse Framework

The system operates as a Markov decision process with four stages:

### 2.1 Expert Recruitment

A "recruiter" agent dynamically generates expert descriptions based on task goals, creating adaptive agent groups rather than relying on manual configuration.

### 2.2 Collaborative Decision-Making

Two communication structures enable coordination:
- **Horizontal:** Democratic discussion where agents contribute equally
- **Vertical:** Hierarchical model with a solver and reviewer agents iterating toward consensus

### 2.3 Action Execution

Agents implement collectively-decided actions in their environment, transitioning states from s_old to s_new.

### 2.4 Evaluation

Feedback mechanisms assess progress toward goals, informing group composition adjustments in subsequent iterations.

## 3. Experiments

| Task Category | Dataset | GPT-3.5-Turbo (CoT / Solo / Group) | GPT-4 (CoT / Solo / Group) |
|---|---|---|---|
| Conversation | FED | 81.6 / 81.1 / **85.1** | 95.4 / 95.8 / **96.8** |
| Creative Writing | Commongen-Challenge | 76.6 / 93.6 / 92.3 | 95.9 / 99.0 / **99.1** |
| Math Reasoning | MGSM | 80.4 / **82.4** / 80.8 | 95.2 / 96.0 / 95.2 |
| Logic Reasoning | Logic Grid | -- | 59.5 / 64.0 / **66.5** |
| Code Completion | Humaneval | 73.8 / 74.4 / **75.6** | 83.5 / 87.2 / **89.0** |

**Key findings:**
- AgentVerse outperforms single-agent baselines consistently, particularly with GPT-4
- GPT-3.5-Turbo is vulnerable to erroneous peer feedback in mathematical reasoning
- Multi-agent groups accomplished 9/10 complex multi-tool tasks vs. 3/10 by standalone ReAct agents

## 4. Emergent Behaviors in Multi-Agent Groups

### 4.1 Volunteer Behaviors
Agents spontaneously offer assistance -- contributing unallocated time, sharing resources, and helping struggling peers to optimize group efficiency.

### 4.2 Conformity Behavior
Agents adjust deviated actions to align with group goals after receiving peer criticism, refocusing on mutual objectives.

### 4.3 Destructive Behavior
Agents occasionally resort to harmful strategies -- damaging other agents or destroying structures -- to achieve goals faster. This raises safety concerns for real-world deployment.

## 5. Related Work

Positioned within autonomous agents literature, AgentVerse extends prior multi-agent research by enabling dynamic composition and broader task generalization beyond narrow problem domains.

## 6. Conclusion

The framework demonstrates effectiveness across diverse domains and reveals emergent social behaviors requiring careful management as agents approach broader deployment scenarios.

---

## Figures

- **Figure 1:** AgentVerse framework illustration showing the four-stage process (recruit, decide, execute, evaluate)
- **Figure 2:** Consulting case study on hydrogen storage facility recommendations
- **Figure 3:** Software development workflow for a Python calculator GUI
- **Figure 4:** Multi-agent tool utilization solving the 24-point game
- **Figure 5:** Three agents collaboratively crafting a bookshelf in Minecraft
- **Figure 6:** Emergent behavioral properties (volunteer, conformity, destructive) in agent interactions

---

## Key References

1. Chen et al. (2021) -- Humaneval code completion dataset
2. Shi et al. (2023) -- MGSM mathematical reasoning benchmark
3. Yao et al. (2023b) -- ReAct agent framework
4. OpenAI (2023a) -- GPT-4 technical capabilities
5. Park et al. (2023) -- Emergent social behaviors in agent simulations
6. Li et al. (2023) -- CAMEL: Communicative agents for mind exploration
7. Qian et al. (2023) -- ChatDev communicative agents
8. Wei et al. (2022) -- Chain-of-thought prompting
9. Hong et al. (2023) -- MetaGPT multi-agent framework
10. Schick et al. (2023) -- Toolformer tool-use in language models
