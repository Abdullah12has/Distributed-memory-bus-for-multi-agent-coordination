# SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents

**Authors:** Xuhui Zhou, Hao Zhu, Leena Mathur, Ruohong Zhang, Haofei Yu, Zhengyang Qi, Louis-Philippe Morency, Yonatan Bisk, Daniel Fried, Graham Neubig, Maarten Sap

**Venue:** arXiv preprint, 2023 (ICLR 2024)

**ArXiv:** [2310.11667](https://arxiv.org/abs/2310.11667)

---

## Abstract

SOTOPIA is an environment designed to simulate intricate social interactions between artificial agents. Agents role-play and interact under a wide variety of scenarios to achieve complex social objectives. The research evaluates LLM-based agents using a framework called SOTOPIA-Eval and finds that GPT-4 achieves a significantly lower goal completion rate than humans on challenging scenarios, particularly when social reasoning is required.

---

## 1. Introduction

Existing social intelligence benchmarks lack interactivity or cover only specific domains. SOTOPIA offers an interactive, goal-driven alternative with realistic scenarios, characters, and relationships that are automatically generated.

## 2. SOTOPIA Interaction Environment

### Task Space Components

- 90 scenarios spanning cooperative, competitive, and mixed social goals
- 40 characters with distinct personalities, occupations, secrets, and relationships
- Five relationship types: family, friend, romantic, acquaintance, stranger

### Character Attributes

Characters are generated with:
- Big Five personality traits
- Moral values and personal values frameworks
- Decision-making styles
- Secrets and public information

### Episodes

Agents take turns performing five action types: speaking, non-verbal communication, physical actions, doing nothing (none), or leaving. Maximum 20 turns per episode.

## 3. SOTOPIA-EVAL Framework

Seven evaluation dimensions:

| Dimension | Range | Focus |
|-----------|-------|-------|
| Goal Completion | 0-10 | Extent of goal achievement |
| Believability | 0-10 | Naturalness and character consistency |
| Knowledge | 0-10 | Information acquisition ability |
| Secret | -10 to 0 | Success keeping secrets private |
| Relationship | -5 to 5 | Impact on social bonds |
| Social Rules | -10 to 0 | Adherence to norms/laws |
| Financial/Material | -5 to 5 | Economic utility changes |

## 4. Research Questions and Setup

Three main inquiries:
1. Can GPT-4 serve as a human judgment proxy for evaluation?
2. What differences exist among language models?
3. How do models compare to humans in social interactions?

**Models tested:** GPT-4, GPT-3.5, Llama-2-70b-chat, MPT-30b-chat

**Dataset:** 450 tasks from 90 scenarios x 5 character pairs

## 5. GPT-4 as Evaluator

GPT-4 correlates strongly with human judgment on Goal (0.71), Financial (0.62), and Relationship (0.56) dimensions when evaluating models. However, correlation drops significantly for human performances. GPT-4 tends to rate higher than humans when it disagrees with average human judgment.

## 6. Model-to-Model Interactions

**Performance ranking:** GPT-4 > GPT-3.5 > Llama-2-70b-chat > MPT-30b-chat

Notable findings:
- All models score negatively on Secret and Social Rules dimensions
- Weaker partner models degrade stronger models' performance
- Models occasionally generate creative problem-solving strategies

## 7. Humans vs. Models on SOTOPIA-Hard

SOTOPIA-Hard comprises 20 scenarios identified as challenging for all models.

| Metric | GPT-4 w/ Humans | Humans w/ Humans |
|--------|-----------------|------------------|
| Goal | 4.85 | 6.15* |
| Believability | 9.25 | 9.10 |
| Knowledge | 2.80 | 2.65 |
| Financial | 0.50 | 0.45 |

(*p<0.05)

**Qualitative differences:**
- Humans average 16.8 words per turn; GPT-4 uses 45.5 (more verbose with active listening)
- Humans employ more strategic negotiation tactics
- Humans persist longer in goal pursuit; models compromise earlier

## 8. Related Work

Contextualizes SOTOPIA within:
1. Static social intelligence benchmarks (ToMi, FauxPas, SocialIQA)
2. Task-oriented and open-domain dialogue systems
3. Multi-agent coordination and social learning

## 9. Conclusion

SOTOPIA provides a systematic environment for evaluating goal-driven social interactions of agents across diverse social scenarios, revealing significant gaps between current LLMs and human social intelligence.

---

## Figures

- **Figure 1:** SOTOPIA environment overview showing scenario generation, character creation, and interaction flow
- **Figure 2:** Example social interaction episode between two agents
- **Figure 3:** SOTOPIA-Eval dimension comparisons across models
- **Figure 4:** Human vs. model performance on SOTOPIA-Hard scenarios
- **Figure 5:** Word count and strategy usage differences between humans and GPT-4

---

## Limitations

- Simplified five-relationship model requiring expansion
- Limited character/scenario diversity compared to real-world complexity
- Two-agent dyadic constraints only
- Potential social stereotypes embedded in GPT-4-based evaluation
- Risk of anthropomorphization in AI social agents
- Human subjects research approved by IRB

---

## Key References

1. Park, J.S., et al. (2023) -- Generative agents and behavioral simulation
2. Sap, M., et al. (2019) -- SocialIQA benchmark
3. Lewis, M., et al. (2017) -- Negotiation dialogue datasets
4. OpenAI (2023) -- GPT-4 technical specifications
5. Touvron, H., et al. (2023) -- LLaMA 2: Open foundation models
6. Zhou, X., et al. (2023) -- Social norm evaluation
7. Rashkin, H., et al. (2019) -- Empathetic dialogues
8. Kim, H., et al. (2023) -- SODA: Social dialogue generation
9. Bisk, Y., et al. (2020) -- Physical intuition in language models
10. Morency, L.-P. (2022) -- Multimodal machine learning survey
