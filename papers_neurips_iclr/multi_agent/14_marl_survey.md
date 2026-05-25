# Multi-agent Reinforcement Learning: A Comprehensive Survey

**Authors:** Dom Huh, Prasant Mohapatra

**Venue:** arXiv preprint, 2023

**ArXiv:** [2312.10256](https://arxiv.org/abs/2312.10256)

---

## Abstract

The paper examines challenges in multi-agent systems (MAS) where multiple agents must make decisions to achieve their objectives in a shared environment. It synthesizes concepts from game theory and machine learning, connecting them to recent advances in multi-agent reinforcement learning (MARL). The survey provides comprehensive coverage of MARL dimensions, opportunities, and inherent challenges while exploring past efforts, proposed solutions, and applications.

---

## 1. Introduction

MARL is established as a pivotal domain in AI for developing solutions addressing complex tasks involving multiple goal-oriented agents. Key themes include facilitating decision-making alongside understanding social dynamics through data-driven approaches.

## 2. Related Surveys

Previous MARL literature spans general overviews and specialized topics including non-stationarity, independent learners, communication, ad-hoc team-play, agent modeling, safety, and knowledge transfer. This work positions itself as more comprehensive, weaving together game theory and machine learning into a unified framework.

## 3. Background

### 3.1 Multi-agent Environment

Multi-agent systems consist of decision-making agents within shared environments with constrained observation and communication due to decentralization. Agents devise strategies mapping perceived states to actions, receiving feedback through environmental responses.

### 3.2 Stochastic Game

Formal representation using the 5-tuple framework (N, S, A, r, T):

| Component | Description |
|-----------|-------------|
| N | Set of agents |
| S | State space |
| A | Joint action space |
| r | Reward functions |
| T | State transition function |

Key concepts covered:

| Concept | Description |
|---------|-------------|
| Sequential/Macro-Actions | Asynchronous or temporally-extended actions |
| Imperfect Information | Limited observations; POSG/Bayesian game frameworks |
| Reward Function | Scalar-valued feedback guiding agent behavior |
| Nature of Interaction | Cooperative, adversarial, or mixed settings |
| Social Context | Conventions and role assignments |
| Networked Games | Communication networks connecting agents |
| Coordination | Dependencies via coordination graphs |
| Return/Value Functions | Cumulative discounted rewards |

### 3.3 Game Theory

Core concepts:

- **Utility and Prospect Theory:** Decision-making under uncertainty; risk aversion and loss sensitivity
- **Incentives and Mechanisms:** Contract theory; mechanism design for desired outcomes
- **Solution Concepts:** Pareto efficiency, best response, Nash equilibrium, correlated equilibrium
- **Equilibrium Computation:** PPAD-completeness of Nash equilibrium; existence and tractability
- **Learning Dynamics:** Best-response dynamics (fictitious play, value iteration, gradient methods) and no-regret dynamics (regret matching, CFR, FTL)

### 3.4 Machine Learning

**Deep Learning:** ANNs optimize parameters through cost functions using SGD. Enables scalable end-to-end solutions.

**Reinforcement Learning approaches:**

| Method | Focus |
|--------|-------|
| Value Function Approximation | Estimating Q-functions via dynamic programming |
| Policy Gradient | Direct policy optimization |
| Actor-Critic | Combined value and policy estimation |
| Model-based | Learning environment dynamics |
| Successor Representation | Temporal abstraction |
| Foundation Models | Control via pretrained representations |

## 4. Learning in a Multi-agent Environment

### 4.1 Benefits of MARL
Scalability, emergent behaviors, robustness through redundancy.

### 4.2 Challenges of MARL

| Challenge | Description |
|-----------|-------------|
| Computational Complexity | Exponential growth in joint action/state spaces |
| Non-stationarity | Dynamic agent policies creating unstable learning |
| Coordination | Miscoordination, relative overgeneralization |
| Performance Evaluation | Assessing multi-agent system behaviors |

## 5. Prospects of MARL

### 5.1 Simulating MARL Tasks
Parallelized processing, multilevel simulation, and open-source environments.

### 5.2 Training Schemes

| Scheme | Approach |
|--------|----------|
| CTCE | Centralized training, centralized execution |
| DTDE | Decentralized training, decentralized execution |
| CTDE | Centralized training, decentralized execution |
| Parameter/Subtask Sharing | Reducing computational complexity |
| Off-policy Learning | Learning from exploration data |
| Offline Learning | Learning from fixed datasets |

### 5.3 Agent Awareness
Learning that accounts for other agents' presence and behaviors.

### 5.4 Multi-agent Credit Assignment
Attributing contributions via difference rewards and value factorization.

### 5.5 Communication

| Category | Elements |
|----------|----------|
| Infrastructure | Proxy, networked, implicit communication |
| Representation | Graph neural networks for relational modeling |
| Learning to Communicate | Message computation, policies, integration |
| Evaluation | Metrics for communication effectiveness |

### 5.6 Modeling Other Agents
Representation, learning, and utilization of other agents' behaviors.

### 5.7 Ad-Hoc Team-Play
Adapting to unknown teammate behaviors in dynamic compositions.

### 5.8 Social Learning
Knowledge transfer through action advising, reward shaping, and knowledge distillation.

## 6. Conclusion

The survey provides a unified treatment of MARL connecting game theory foundations with modern deep learning approaches, identifying key open challenges and research directions.

---

## Key Definitions

- **Decentralization:** "Each agent is capable of perceiving its environment, communicating with other agents, and taking action autonomously."
- **Rationality:** "Rational agents take actions that will maximize the expected cumulative reward over time."
- **Pareto Efficiency:** "A strategy profile is Pareto efficient if not Pareto dominated by any other strategy profiles."
- **Nash Equilibrium:** "A state where no individual agent can increase its expected return by unilaterally deviating from their policy."

---

## Figures

- **Figure 1:** Overview of MARL landscape connecting game theory and machine learning
- **Figure 2:** Stochastic game formulation with agents, states, and transitions
- **Figure 3:** Training scheme taxonomy (CTCE, DTDE, CTDE)
- **Figure 4:** Communication architecture categories
- **Figure 5:** Credit assignment methods taxonomy

---

## Key References

1. Shoham, Y., et al. (2007) -- Bounded rationality in multi-agent systems
2. Stone, P. and Veloso, M. (2000) -- Foundational MARL overview
3. Sutton, R. and Barto, A. (2018) -- Reinforcement learning textbook
4. Hu, J. and Wellman, M. (2003) -- Nash Q-Learning
5. Mnih, V., et al. (2013) -- Deep Q-Networks
6. Daskalakis, C., et al. (2009) -- PPAD-completeness of Nash equilibrium
7. Zinkevich, M., et al. (2007) -- Counterfactual regret minimization
8. Foerster, J., et al. (2018) -- COMA: Counterfactual multi-agent policy gradients
9. Rashid, T., et al. (2018) -- QMIX: Monotonic value function factorisation
10. Lowe, R., et al. (2017) -- MADDPG: Multi-agent actor-critic
