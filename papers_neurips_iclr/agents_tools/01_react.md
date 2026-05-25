# ReAct: Synergizing Reasoning and Acting in Language Models

**Authors:** Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao

**Venue:** ICLR 2023

**arXiv:** [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

---

## Abstract

While large language models (LLMs) have demonstrated impressive capabilities across tasks in language understanding and interactive decision making, their abilities for reasoning (e.g. chain-of-thought prompting) and acting (e.g. action plan generation) have primarily been studied as separate topics. ReAct introduces a general paradigm that enables language models to generate both reasoning traces and task-specific actions in an interleaved manner, allowing for greater synergy between the two: reasoning traces help the model induce, track, and update action plans as well as handle exceptions, while actions allow it to interface with external sources, such as knowledge bases or environments, to gather additional information. ReAct is applied to a diverse set of language and decision making tasks and demonstrates effectiveness over state-of-the-art baselines, with improvements including a 34% absolute improvement on ALFWorld and a 10% absolute improvement on WebShop over imitation and reinforcement learning methods. ReAct also demonstrates improved human interpretability and trustworthiness. On HotpotQA and Fever, ReAct overcomes issues of hallucination and error propagation prevalent in chain-of-thought reasoning by interacting with a simple Wikipedia API, and generates human-like task-solving trajectories that are more interpretable than baselines without reasoning traces.

---

## 1. Introduction

The paper addresses the disconnect between reasoning and acting in LLMs. Chain-of-thought (CoT) prompting enables reasoning but suffers from hallucination. Action-based approaches interact with environments but lack structured reasoning. ReAct bridges this gap by augmenting the action space to include both domain-specific actions and language-based thoughts.

The key innovation is that thoughts (reasoning traces) help the model "induce, track, and update action plans as well as handle exceptions," while actions allow it to "interface with and gather additional information from external sources."

## 2. ReAct: Synergizing Reasoning and Acting

### Formulation

ReAct augments the agent's action space to include both:
- **Task-specific actions** (from the domain action space A)
- **Language-based thoughts** (from the language space L)

Thoughts serve multiple purposes: decomposing goals, tracking subgoal progress, injecting commonsense knowledge, extracting information from observations, and handling exceptions.

### Prompting Design

ReAct prompts are simple to design -- human annotators write their thoughts in natural language on top of actions taken. No special formatting, thought templates, or careful example selection is required. Only 1-6 examples are used for in-context learning.

## 3. Knowledge-Intensive Reasoning Tasks

### Domains
- **HotpotQA**: Multi-hop question answering
- **FEVER**: Fact verification

### Action Space
Simple Wikipedia API with three operations:
- `search[entity]` -- returns first 5 sentences of a Wikipedia entity
- `lookup[string]` -- returns next sentence containing the string
- `finish[answer]` -- finishes with an answer

### Results

| Method | HotpotQA (EM) | FEVER (Acc) |
|--------|---------------|-------------|
| Standard | 28.7 | 57.1 |
| CoT (chain-of-thought) | 29.4 | 56.3 |
| CoT-SC (self-consistency) | 33.4 | 60.4 |
| ReAct | 27.4 | 60.9 |
| ReAct -> CoT-SC | 35.1 | 62.0 |
| CoT-SC -> ReAct | 34.2 | 64.6 |

### Key Findings
- Combined approaches (ReAct + CoT-SC) outperform individual methods
- ReAct demonstrates **0% hallucination** in success modes versus CoT's **14%**
- ReAct excels at grounding reasoning in external facts

### Failure Analysis (HotpotQA)
- **ReAct success rate:** 94% (with 6% false positives from hallucination)
- **CoT success rate:** 86% (with 14% false positives)
- Major ReAct failure: repetitive thought-action loops (reasoning error)
- Major CoT failure: hallucinated facts (56% of failures)

## 4. Decision Making Tasks

### ALFWorld (Text-based Household Simulation)

| Method | Success Rate (%) |
|--------|-----------------|
| BUTLER baseline (IL, 10^5 trajectories) | 37 |
| Act (best of 6) | 45 |
| ReAct (average) | 57 |
| ReAct (best of 6) | 71 |

ReAct achieves a **34% absolute improvement** over imitation learning methods while using only 1-2 in-context examples.

### WebShop (E-commerce Navigation)

| Method | Score | Success Rate |
|--------|-------|-------------|
| IL (imitation learning) | 59.9 | 29.1 |
| IL+RL | 62.4 | 28.7 |
| Act | 62.3 | 30.1 |
| ReAct | 66.6 | 40.0 |
| Human Expert | 82.1 | 59.6 |

ReAct achieves a **10% absolute improvement** over IL+RL baselines.

## 5. Ablation: ReAct vs. Inner Monologue

Comparing against "Inner Monologue" style prompting with dense external feedback, ReAct substantially outperforms (71% vs 53% on ALFWorld), demonstrating the value of high-level reasoning over simple environmental feedback reflection.

## 6. Human-in-the-Loop

**Figure 5** demonstrates controllability: by editing only two thoughts in a failing trajectory, the model's behavior shifts to succeed, enabling human-machine collaboration superior to action-only editing.

## 7. Finetuning Results

On HotpotQA with 3,000 self-generated trajectories:
- PaLM-8B finetuned ReAct outperforms all PaLM-62B prompting methods
- PaLM-62B finetuned ReAct outperforms all PaLM-540B prompting methods
- ReAct finetuning substantially outperforms Standard/CoT finetuning

## Key Advantages

1. **Interpretability:** Humans can readily distinguish model's internal knowledge vs. external environment information
2. **Generalization:** Few-shot learning (1-6 examples) outperforms methods trained on thousands of examples
3. **Robustness:** Flexible thought-action occurrence patterns accommodate diverse task needs
4. **Controllability:** Enables human thought editing for behavior correction

## Limitations

- Prompting-based approach limited by input length constraints
- Complex tasks with large action spaces require extensive demonstrations
- Future work should focus on scaling with multi-task training and RL integration

---

## Figure Descriptions

- **Figure 1:** Comparison of four prompting paradigms: (a) Standard prompting, (b) Chain-of-thought (CoT), (c) Act-only, (d) ReAct with interleaved reasoning and acting
- **Figure 2:** Example ReAct trajectory on HotpotQA showing interleaved thought/action/observation steps
- **Figure 3:** ReAct example on FEVER showing fact verification with Wikipedia lookups
- **Figure 4:** ReAct trajectory on ALFWorld household task with goal decomposition
- **Figure 5:** Human-in-the-loop editing demonstration

---

## Top 10 References

1. Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS*.
2. Chowdhery, A., et al. (2022). PaLM: Scaling language modeling with Pathways. *arXiv*.
3. Brown, T., et al. (2020). Language models are few-shot learners. *NeurIPS*.
4. Huang, W., et al. (2022). Inner Monologue: Embodied reasoning through planning with language models. *CoRL*.
5. Shridhar, M., et al. (2020). ALFWorld: Aligning text and embodied environments for interactive learning. *ICLR*.
6. Yang, Z., et al. (2018). HotpotQA: A dataset for diverse, explainable multi-hop question answering. *EMNLP*.
7. Thorne, J., et al. (2018). FEVER: A large-scale dataset for fact extraction and verification. *NAACL*.
8. Zelikman, E., et al. (2022). STaR: Bootstrapping reasoning with reasoning. *NeurIPS*.
9. Yao, S., et al. (2022). WebShop: Towards scalable real-world web interaction with grounded language agents. *NeurIPS*.
10. Ahn, M., et al. (2022). Do As I Can, Not As I Say: Grounding language in robotic affordances. *CoRL*.
