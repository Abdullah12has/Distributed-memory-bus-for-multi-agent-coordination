# DyLAN: A Dynamic LLM-Powered Agent Network for Task-Oriented Agent Collaboration

**Authors:** Zijun Liu, Yanzhe Zhang, Peng Li, Yang Liu, Diyi Yang

**Venue:** COLM 2024

**ArXiv:** [2310.02170](https://arxiv.org/abs/2310.02170)

**Code:** https://github.com/SALT-NLP/DyLAN

---

## Abstract

DyLAN proposes a framework that automatically selects a team of agents from candidates to collaborate in a dynamic communication structure toward different tasks and domains. The approach operates in two stages: first, an agent selection algorithm identifies the best-performing agents based on an "Agent Importance Score" metric, then selected agents dynamically collaborate to solve tasks. The researchers demonstrate improvements across code generation, decision-making, reasoning, and arithmetic tasks, with accuracy gains reaching 25% on specific MMLU subjects.

---

## 1. Introduction

DyLAN addresses the challenge of organizing multiple LLM-powered agents for effective collaboration. Unlike static multi-agent frameworks, DyLAN dynamically adjusts both team composition and communication structure during task execution.

## 2. Core Concepts

### Temporal Feed-Forward Networks (T-FFNs)

The framework models agent communication using T-FFNs, where nodes represent agents at specific timesteps and edges represent communication channels. This allows for dynamic adjustment of team composition during task execution.

### Agent Importance Score

An unsupervised metric that evaluates agent contributions through three steps:
1. **Propagation:** Each node rates predecessors' solutions
2. **Aggregation:** Nodes aggregate feedback from successors
3. **Selection:** Top-k agents are selected based on accumulated importance scores

### Agent Team Reformation

During task solving, an LLM Ranker dynamically deactivates low-performing agents between timesteps, creating adaptive communication structures rather than static ones.

## 3. Two-Stage Framework

### Stage 1: Team Optimization
An agent selection algorithm identifies the most contributory agents from a candidate pool based on the Agent Importance Score metric.

### Stage 2: Task Solving
Selected agents collaborate dynamically with agent reformation -- low-performing agents are deactivated between timesteps.

**Early Stopping:** Terminates when more than 2/3 of agents reach consensus.

## 4. Experimental Results

| Task | Dataset | Improvement | API Calls |
|------|---------|-------------|-----------|
| Code Generation | HumanEval | +9.7% over baseline | 16.85 |
| Decision Making | WebShop | +17.7% reward | 24.85 |
| General Reasoning | MMLU | +4.1% accuracy | 4.39 |
| Arithmetic Reasoning | MATH | +4.1% accuracy | 7.15 |

**Notable finding:** On specific MMLU subjects, performance improved by up to 25.0% through agent selection.

## 5. Comparison with Prior Work

DyLAN uniquely combines:
- Multiple agent roles
- Early stopping mechanisms
- Dynamic communication structures
- Principled team optimization

This contrasts with existing methods (LLM-Blender, LLM Debate, CAMEL) that use static agent configurations.

## 6. Conclusion

DyLAN demonstrates that dynamic agent selection and communication structure adaptation significantly improve multi-agent collaboration performance while maintaining computational efficiency.

---

## Figures

- **Figure 1:** Overview of DyLAN's two-stage framework (team optimization and task solving)
- **Figure 2:** T-FFN structure showing agents as nodes across timesteps with dynamic edges
- **Figure 3:** Agent Importance Score computation through propagation, aggregation, and selection
- **Figure 4:** Performance comparison across benchmarks showing DyLAN vs. baselines
- **Figure 5:** Ablation study results on component contributions

---

## Key References

1. Liu et al. (2023) -- BOLAA framework for agent orchestration
2. Chen et al. (2024) -- AgentVerse for multi-agent collaboration
3. Du et al. (2023) -- LLM debate mechanisms
4. Jiang et al. (2023) -- LLM-Blender response fusion
5. Li et al. (2023) -- CAMEL: Communicative agents for mind exploration
6. Yao et al. (2023) -- ReAct: Synergizing reasoning and acting
7. Wei et al. (2022) -- Chain-of-thought prompting
8. Chen et al. (2021) -- Evaluating LLMs trained on code (HumanEval)
9. Hendrycks et al. (2021) -- MMLU benchmark
10. Yao et al. (2022) -- WebShop environment
