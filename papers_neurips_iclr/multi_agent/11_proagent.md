# ProAgent: Building Proactive Cooperative Agents with Large Language Models

**Authors:** Ceyao Zhang, Kaijie Yang, Siyi Hu, Zihao Wang, Guanghe Li, Yihang Sun, Cheng Zhang, Zhaowei Zhang, Anji Liu, Song-Chun Zhu, Xiaojun Chang, Junge Zhang, Feng Yin, Yitao Liang, Yaodong Yang

**Venue:** AAAI 2024

**ArXiv:** [2308.11339](https://arxiv.org/abs/2308.11339)

---

## Abstract

ProAgent is a framework employing LLMs to develop adaptive agents capable of dynamically adapting their behavior to enhance cooperation with teammates. The system analyzes environmental states, infers teammate intentions from observations, and updates beliefs based on actual teammate behaviors. The authors emphasize the approach's modularity and interpretability, demonstrating superior performance in the Overcooked-AI environment compared to five baseline methods, with over 10% average improvement when paired with human proxy models.

---

## 1. Introduction

ProAgent addresses zero-shot coordination challenges -- cooperating effectively with previously unseen teammates without prior training. The framework uses LLMs for reasoning about teammate behavior rather than learning from extensive interaction histories.

## 2. Related Works

### Reasoning and Planning with LLMs
Discusses Chain-of-Thought prompting, ReAct framework, and planning capabilities of LLMs.

### Multi-agent Coordination
Covers zero-shot coordination methods, Theory of Mind approaches, and learning-based coordination strategies.

## 3. Method

### Framework Components

The system comprises five interconnected modules:

1. **Memory Module:** Stores knowledge library (Task, Rules, Demos) and trajectory history using a FIFO buffer
2. **Planner Module:** Uses Chain-of-Thought reasoning to analyze scenes, predict teammate intentions, and generate high-level skill plans
3. **Verificator Module:** Validates proposed skills through multi-round prompting; handles failure analysis and replanning
4. **Belief Correction:** Updates teammate intention predictions based on actual observed behavior vs. predicted behavior
5. **Controller Module:** Translates high-level skills to low-level executable actions

### Prompt Construction

Knowledge library structured around:
- **Task:** Cooperative objectives and goals
- **Rules:** Legal skills and action constraints
- **Demos:** Example scenarios for in-context learning

States are converted from tensor representations to natural language descriptions.

### Processing Pipeline

1. Knowledge library + state grounding
2. High-level skill planning (with CoT)
3. Belief correction (comparing predicted vs. actual teammate behavior)
4. Skill validation and execution
5. Memory storage

## 4. Experiments

### Collaborating with AI Agents (Player 0)

| Layout | SP | PBT | FCP | MEP | COLE | ProAgent |
|--------|----|----|-----|-----|------|----------|
| Cramped Room | 168.5+/-15.2 | 178.8+/-16.5 | 196.3+/-16.8 | 185+/-15 | 163.8+/-24.1 | **197.3+/-6.1** |
| Asymmetric Adv. | 183.3+/-27.5 | 182.2+/-27.9 | 185.7+/-22.7 | 155.7+/-63.9 | 201.3+/-34.5 | **228.7+/-23** |
| Coordination Ring | 122+/-17.2 | 141.3+/-28 | 148.8+/-19.4 | 167.2+/-22.4 | 168.8+/-26.1 | **175.3+/-29** |
| Forced Coordination | 6.7+/-6.7 | 15.3+/-17.1 | 44.7+/-36.4 | 23.3+/-19.8 | 24+/-21.8 | **49.7+/-33.1** |
| Counter Circuit | 64.7+/-45.8 | 64.7+/-45.9 | 58.3+/-37.5 | 74.3+/-39.1 | 95.5+/-25.2 | **126.3+/-32.3** |

### Collaborating with Humans

ProAgent shows >10% average improvement versus state-of-the-art when partnering with human proxy models (behavior cloning models trained on human play data).

### Ablation Studies

| Configuration | Score |
|---|---|
| With analysis and belief | 204 |
| Without belief correction | 184 |
| Without analysis or belief | 100 |

Removing the Verificator module reduced success rate to 20% (over 100 steps), demonstrating its critical role.

## 5. Discussion

- ProAgent demonstrates strategic planning, dynamic path adjustment, and effective failure recovery
- The framework is modular -- individual components can be upgraded independently
- LLM-based reasoning provides interpretable decision traces
- Zero-shot capability eliminates need for environment-specific training

## 6. Conclusion

ProAgent demonstrates that LLMs can enable proactive cooperative behavior in multi-agent settings without prior training, outperforming learning-based baselines across diverse coordination scenarios.

---

## Figures

- **Figure 1:** System overview showing ProAgent's pipeline with coordination task workflow -- state translation, planning, belief updates, skill validation, and action execution
- **Figure 2:** Human proxy collaboration performance across five Overcooked-AI layouts showing average cumulative rewards over 400 timesteps with error bars

---

## Key References

1. Wei, J., et al. (2022) -- Chain-of-Thought prompting for reasoning
2. Yao, S., et al. (2023) -- ReAct: Synergizing reasoning and acting
3. Carroll, M., et al. (2019) -- Overcooked-AI environment and human coordination
4. Strouse, D., et al. (2021) -- Zero-shot coordination via population-based training
5. Li, Y., et al. (2023) -- Cooperative learning frameworks
6. Wang, G., et al. (2023) -- LLM-based planning for multi-task agents
7. Hu, H. and Wellman, M. (2003) -- Nash Q-learning
8. Stone, P. and Veloso, M. (2000) -- Multi-agent systems survey
9. Shinn, N., et al. (2023) -- Reflexion: Language agents with verbal reinforcement learning
10. Zhu, S.-C. and Mumford, D. (2007) -- Stochastic grammar of images
