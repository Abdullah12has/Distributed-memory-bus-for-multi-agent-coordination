# Voyager: An Open-Ended Embodied Agent with Large Language Models

**Authors:** Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Linxi Fan, Anima Anandkumar

**Venue:** NeurIPS 2023 (Spotlight)

**arXiv:** [https://arxiv.org/abs/2305.16291](https://arxiv.org/abs/2305.16291)

---

## Abstract

We introduce Voyager, the first LLM-powered embodied lifelong learning agent in Minecraft that continuously explores the world, acquires diverse skills, and makes novel discoveries without human intervention. Voyager consists of three key components: (1) an automatic curriculum that maximizes exploration, (2) an ever-growing skill library of executable code that stores and retrieves complex behaviors, and (3) a new iterative prompting mechanism that incorporates environment feedback, execution errors, and self-verification for program improvement. Voyager interacts with GPT-4 via blackbox queries, which bypasses the need for model parameter fine-tuning. The empirical results show that Voyager obtains 3.3x more unique items, travels 2.3x longer distances, and unlocks key tech tree milestones up to 15.3x faster than prior state-of-the-art. Voyager is able to utilize the learned skill library in a new Minecraft world to solve novel tasks from scratch, while other techniques struggle to generalize.

---

## 1. Introduction

Voyager is the first LLM-powered embodied lifelong learning agent. It operates in Minecraft, a domain requiring exploration, resource gathering, crafting, and combat. Unlike prior approaches that require model finetuning or human intervention, Voyager uses GPT-4 as a blackbox and learns continuously through code generation.

## 2. Core Architecture

### 2.1 Automatic Curriculum

The automatic curriculum generates progressively challenging objectives based on:
- Current exploration progress and agent state
- Inventory, equipment, and nearby biome information
- Previously completed and failed tasks

GPT-4 proposes achievable goals that encourage discovery of diverse items and skills. The curriculum adapts dynamically rather than following predetermined tasks.

### 2.2 Skill Library

The skill library serves as a persistent knowledge repository:
- Stores executable JavaScript code for complex behaviors
- Each skill is indexed using embedding vectors of its description
- Enables efficient retrieval when tackling similar future tasks
- Promotes skill composition and reuse across activities
- Grows continuously as the agent learns new capabilities

### 2.3 Iterative Prompting Mechanism

Code generation is refined through feedback loops incorporating three types of information:
1. **Environmental observations** revealing task progress
2. **Execution errors** from the JavaScript interpreter
3. **Self-verification** confirming successful task completion

The cycle operates as: generate code -> execute -> collect feedback -> refine until verification confirms success, then commit the learned skill and request the next curriculum task.

### Code as Action Space

The approach uses code (JavaScript via Mineflayer API) as the action space rather than primitive commands, enabling "temporally extended, interpretable, and compositional" actions essential for long-horizon Minecraft tasks.

## 3. Experimental Results

### Performance Metrics

| Metric | Voyager | Best Baseline | Improvement |
|--------|---------|--------------|-------------|
| Unique items discovered | ~63 | ~19 (AutoGPT) | 3.3x |
| Distance traveled | ~2300 | ~1000 | 2.3x |
| Wooden tools milestone | ~2 min | ~30 min (ReAct) | 15.3x |
| Stone tools milestone | ~5 min | ~60 min | 12x |
| Iron tools milestone | ~20 min | Not achieved | - |

### Zero-Shot Generalization

Voyager can utilize its learned skill library in a completely new Minecraft world to solve novel tasks from scratch, while other techniques (ReAct, Reflexion, AutoGPT) struggle to generalize.

### Baseline Comparisons

Three NLP-focused methods adapted for embodied tasks:
- **ReAct**: Chain-of-thought prompting with reasoning traces
- **Reflexion**: Self-reflection for improved action planning
- **AutoGPT**: Task decomposition into executable subgoals

All baselines lacked the skill library, structured curriculum, and self-verification components.

## 4. Ablation Study

| Component Removed | Impact on Item Discovery |
|-------------------|------------------------|
| Automatic Curriculum | -93% |
| Skill Library | Plateau effect in later stages |
| Self-Verification | -73% |
| GPT-3.5 instead of GPT-4 | -5.7x reduction |

Self-verification is the most critical element, followed by the automatic curriculum.

## 5. Experimental Framework

- Platform: MineDojo (open-source Minecraft AI framework built on Mineflayer APIs)
- Evaluation dimensions: exploration performance (unique items), technology tree progression, map coverage, generalization
- GPT-4 used via API for all code generation and curriculum planning

## 6. Limitations

- **Cost**: GPT-4 API expenses are 15x higher than GPT-3.5, though necessary for code quality
- **Hallucinations**: Curriculum occasionally proposes non-existent items (e.g., "copper swords"); code generation sometimes references invalid functions
- **Stuck states**: Despite iterative refinement, the agent occasionally becomes stuck
- **No visual perception**: Operates through text-based APIs only; cannot handle construction tasks requiring visual feedback

## 7. Future Directions

- Multimodal perception integration for visual tasks
- Open-source LLM fine-tuning to reduce API costs
- Transfer to robotics domains
- More sophisticated self-verification mechanisms

---

## Figure Descriptions

- **Figure 1:** Overview of Voyager's three components: automatic curriculum, skill library, and iterative prompting mechanism
- **Figure 2:** Technology tree progression comparison showing Voyager unlocking milestones faster
- **Figure 3:** Unique item discovery curves over time for Voyager vs. baselines
- **Figure 4:** Skill library growth over exploration iterations
- **Figure 5:** Example generated code skills (mining, crafting, combat)
- **Figure 6:** Map coverage visualization showing Voyager's exploration range

---

## Top 10 References

1. Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS*.
2. Yao, S., et al. (2022). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
3. Shinn, N., et al. (2023). Reflexion: Language agents with verbal reinforcement learning. *NeurIPS*.
4. Liang, J., et al. (2023). Code as Policies: Language model programs for embodied control. *ICRA*.
5. Fan, L., et al. (2022). MineDojo: Building open-ended embodied agents with internet-scale knowledge. *NeurIPS*.
6. OpenAI (2023). GPT-4 technical report. *arXiv:2303.08774*.
7. Eysenbach, B., et al. (2019). Diversity is all you need: Learning skills without a reward function. *ICLR*.
8. Brown, T., et al. (2020). Language models are few-shot learners. *NeurIPS*.
9. Ellis, K., et al. (2021). DreamCoder: Growing generalizable, interpretable knowledge with wake-sleep Bayesian program learning. *PLDI*.
10. Huang, W., et al. (2022). Inner Monologue: Embodied reasoning through planning with language models. *CoRL*.
