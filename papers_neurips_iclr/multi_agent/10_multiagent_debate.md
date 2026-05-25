# Improving Factuality and Reasoning in Language Models through Multiagent Debate

**Authors:** Yilun Du, Shuang Li, Antonio Torralba, Joshua B. Tenenbaum, Igor Mordatch

**Venue:** arXiv preprint, 2023

**ArXiv:** [2305.14325](https://arxiv.org/abs/2305.14325)

---

## Abstract

The paper presents an approach where multiple language model instances propose and debate their individual responses and reasoning processes over multiple rounds to arrive at a common final answer. The researchers found this method enhances mathematical and strategic reasoning while improving factual accuracy and reducing hallucinations in contemporary models. The approach applies to existing black-box language models without requiring fine-tuning.

---

## 1. Introduction

LLMs suffer from hallucinations and reasoning errors even with techniques like chain-of-thought prompting. Inspired by Minsky's "Society of Mind," the authors propose having multiple LLM instances debate their answers, drawing parallels to multi-threaded human reasoning and multi-source fact verification.

## 2. Language Generation through Multiagent Debate

### Methodology

1. Multiple agents independently generate initial answers to a query
2. Each agent reads and critiques other agents' responses
3. Agents update their answers based on the debate
4. Process repeats for multiple rounds until convergence

Two prompt variants (short/long form) control debate duration and convergence speed. The approach requires only black-box API access to language models.

## 3. Experiments

### 3.1 Reasoning Tasks

| Model | Arithmetic (%) | Grade School Math (%) | Chess (Delta-PS) |
|-------|---|---|---|
| Single Agent | 67.0 +/- 4.7 | 77.0 +/- 4.2 | 91.4 +/- 10.6 |
| Single Agent (Reflection) | 72.1 +/- 4.5 | 75.0 +/- 4.3 | 102.1 +/- 11.9 |
| Multi-Agent (Majority) | 69.0 +/- 4.6 | 81.0 +/- 3.9 | 102.2 +/- 6.2 |
| **Multi-Agent (Debate)** | **81.8 +/- 2.3** | **85.0 +/- 3.5** | **122.9 +/- 7.6** |

### 3.2 Factuality Tasks

| Model | Biographies | MMLU | Chess Validity |
|-------|---|---|---|
| Single Agent | 66.0 +/- 2.2 | 63.9 +/- 4.8 | 29.3 +/- 2.6 |
| Single Agent (Reflection) | 68.3 +/- 2.9 | 57.7 +/- 5.0 | 38.8 +/- 2.9 |
| **Multi-Agent (Debate)** | **73.8 +/- 2.3** | **71.1 +/- 4.6** | **45.2 +/- 2.9** |

### 3.3 Analysis

Key findings:
- Performance improves monotonically with additional agents and debate rounds
- Summarizing agent responses enhances efficiency without sacrificing quality
- Debate works synergistically with chain-of-thought prompting
- Different model types (ChatGPT + Bard) can debate effectively together
- All models may initially give incorrect responses, yet debate still converges to the correct answer
- Models demonstrate selective persuadability based on confidence -- disagreements suggest uncertainty

## 4. Related Work

The paper positions multiagent debate within:
- AI safety via debate (Irving et al., 2018)
- Self-consistency and verification methods
- Multi-agent communication in reinforcement learning
- Society of Mind (Minsky, 1988)

## 5. Limitations and Discussion

- Increased computational cost requiring multiple generations per query
- Models sometimes focus only on recent debate inputs with long contexts
- Confident incorrect answers can persist despite debate
- Convergence does not guarantee correctness

---

## Figures

- **Figure 1:** Multiagent debate outperforms traditional inference across six benchmarks
- **Figure 2:** Illustration of the debate procedure workflow (agents generate, share, revise)
- **Figures 4-5:** Qualitative examples showing debate trajectories toward correct answers
- **Figure 6:** Debate gains compound with chain-of-thought prompting
- **Figure 7:** Biography generation debate showing convergence
- **Figure 10:** Performance scaling with number of agents and debate rounds (monotonic improvement)

---

## Key References

1. Kojima, T., et al. (2022) -- Large language models are zero-shot reasoners
2. Irving, G., et al. (2018) -- AI safety via debate
3. Wei, J., et al. (2022) -- Chain-of-thought prompting elicits reasoning
4. Minsky, M. (1988) -- Society of Mind (conceptual foundation)
5. Ouyang, L., et al. (2022) -- Training LLMs with human feedback (RLHF)
6. Wang, X., et al. (2023) -- Self-consistency improves chain-of-thought reasoning
7. Cobbe, K., et al. (2021) -- Training verifiers to solve math word problems
8. Brown, T., et al. (2020) -- Language models are few-shot learners (GPT-3)
9. Touvron, H., et al. (2023) -- LLaMA: Open foundation language models
10. Bubeck, S., et al. (2023) -- Sparks of artificial general intelligence (GPT-4 analysis)
