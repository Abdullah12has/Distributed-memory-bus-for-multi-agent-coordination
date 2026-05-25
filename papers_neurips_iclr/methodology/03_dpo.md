# Direct Preference Optimization: Your Language Model is Secretly a Reward Model

**Authors:** Rafael Rafailov, Archit Sharma, Eric Mitchell, Stefano Ermon, Christopher D. Manning, Chelsea Finn

**Venue:** NeurIPS 2023

**arXiv:** [2305.18290](https://arxiv.org/abs/2305.18290)

---

## Abstract

The paper introduces Direct Preference Optimization (DPO), a method that enables extraction of the corresponding optimal policy in closed form, allowing the standard RLHF problem to be solved with only a simple classification loss. The approach is more stable and computationally efficient than traditional reinforcement learning from human feedback, avoiding the need for reward model training and RL sampling during fine-tuning.

---

## 1. Key Innovation

Under the Bradley-Terry preference model, the optimal policy can be expressed in closed form:

r(x,y) = beta * log(pi_theta(y|x) / pi_ref(y|x)) + beta * log(Z(x))

This enables optimizing policies directly using standard supervised learning techniques.

### DPO Loss Function

L_DPO = -E[log sigma(beta * log(pi_theta(y_w|x) / pi_ref(y_w|x)) - beta * log(pi_theta(y_l|x) / pi_ref(y_l|x)))]

The gradient increases preferred completions while decreasing dispreferred ones, weighted by how incorrectly the implicit reward model ranks them.

---

## 2. Theoretical Contributions

1. **Equivalence Relation:** Two reward functions differing only by a prefix-dependent function yield identical preferences and optimal policies.

2. **Representational Completeness:** All reward classes consistent with Plackett-Luce models can be represented with r(x,y) = beta * log(pi(y|x) / pi_ref(y|x)).

3. **Implicit Reward Modeling:** The language model parameters simultaneously represent both the policy and an implicit reward function.

---

## 3. Experimental Results

| Task | DPO Performance | Notes |
|------|-----------------|-------|
| Sentiment Control | Dominates reward-KL frontier vs. PPO and PPO-GT | More efficient optimization |
| Summarization (TL;DR) | 61% win rate vs. PPO's 57% | More robust to temperature variation |
| Dialogue (Anthropic-HH) | Matches/exceeds Best-of-128 baseline | Only efficient method improving over preferences |

### Tasks Evaluated

- **Controlled sentiment generation** (IMDb dataset with classifier-based preferences)
- **Abstractive summarization** (Reddit TL;DR with human-annotated preferences)
- **Single-turn dialogue** (Anthropic HH dataset with 170k human-preferred pairs)

### Baselines

SFT, Preferred-FT, Unlikelihood, PPO (with learned/ground-truth rewards), Best-of-N sampling

---

## 4. Methodological Advantages

- **Computational Efficiency:** No RL loop or sampling required during training
- **Stability:** Single-stage optimization eliminates complexities of actor-critic methods
- **Simplicity:** Binary cross-entropy loss replaces sophisticated RL algorithms
- **Hyperparameter Sensitivity:** Minimal tuning needed; DPO less temperature-sensitive than PPO

---

## 5. Human Evaluation Validation

GPT-4 judgments correlated strongly with human evaluations (65--79% agreement), supporting automated assessment reliability. The authors validated this through explicit human studies on summarization tasks.

---

## 6. Limitations and Future Directions

- Out-of-distribution generalization requires further study
- Reward over-optimization behavior in direct preference setting unclear
- Current experiments limited to models up to 6B parameters
- Potential for applications beyond language models (multimodal generation)

---

## 7. Figure Descriptions

- **Figure 1:** Comparison of RLHF pipeline (reward model + PPO) vs. DPO pipeline (direct optimization)
- **Figure 2:** Reward-KL frontier plots showing DPO dominating PPO on sentiment control
- **Figure 3:** Win rate comparisons across summarization and dialogue tasks
- **Figure 4:** Temperature sensitivity analysis comparing DPO and PPO

---

## Key References

1. Ziegler et al. (2020) --- Foundational RLHF approach
2. Ouyang et al. (2022) --- InstructGPT alignment methods
3. Schulman et al. (2017) --- PPO algorithm
4. Bai et al. (2022a,b) --- Constitutional AI training
5. Bradley and Terry (1952) --- Preference modeling theory
6. Christiano et al. (2017) --- Learning from human preferences
7. Levine (2018) --- Control as inference framework
8. Stiennon et al. (2022) --- Learning to summarize from feedback
9. Plackett (1975) --- Ranking preference models
10. Dudik et al. (2015) --- Contextual dueling bandits
