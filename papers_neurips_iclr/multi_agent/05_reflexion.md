# Reflexion: Language Agents with Verbal Reinforcement Learning

**Authors:** Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao

**Venue:** NeurIPS 2023

**ArXiv:** [https://arxiv.org/abs/2303.11366](https://arxiv.org/abs/2303.11366)

**Date:** March 20, 2023

---

## Abstract

Large language models (LLMs) have been increasingly used to interact with external environments (e.g., games, compilers, APIs) as goal-driven agents. However, it remains challenging for these language agents to quickly and efficiently learn from trial-and-error as traditional reinforcement learning methods require extensive training samples and expensive model fine-tuning. We propose Reflexion, a novel framework to reinforce language agents not by updating weights, but instead through linguistic feedback. Concretely, Reflexion agents verbally reflect on task feedback signals, then maintain their own reflective text in an episodic memory buffer to induce better decision-making in subsequent trials. Reflexion is flexible enough to incorporate various types (scalar values or free-form language) and sources (external or internally simulated) of feedback signals, and obtains significant improvements over a baseline agent across diverse tasks (sequential decision-making, coding, language reasoning). For example, Reflexion achieves a 91% pass@1 accuracy on the HumanEval coding benchmark, surpassing the previous state-of-the-art GPT-4 that achieves 80%. We also conduct ablation and analysis studies using different feedback signals, feedback incorporation methods, and agent types, and provide insights into how they affect performance.

---

## 1. Introduction

Recent advances including ReAct, SayCan, Toolformer, HuggingGPT, generative agents, and WebGPT have demonstrated autonomous decision-making agents built on LLM cores. These approaches rely on in-context examples rather than traditional reinforcement learning optimization due to computational constraints of massive models.

**Reflexion's Core Innovation**: Reflexion converts binary or scalar feedback from the environment into verbal feedback in the form of a textual summary, which is then added as additional context for the LLM agent in the next episode.

The framework mirrors human iterative learning through reflection on failures. Unlike traditional RL, Reflexion offers four advantages:
1. Lightweight without LLM fine-tuning
2. Enables nuanced feedback beyond scalar rewards
3. Provides explicit, interpretable episodic memory
4. Offers explicit hints for future episodes

**Key Contributions**:
- Novel "verbal" reinforcement paradigm parameterizing policy through agent memory and LLM parameters
- Empirical demonstration of self-reflection usefulness for complex task learning
- Introduction of LeetcodeHardGym, a code-generation environment with 40 Leetcode hard questions across 19 languages
- State-of-the-art results across code generation benchmarks

---

## 2. Related Work

### Reasoning and Decision-Making

Self-Refine employs iterative self-refinement for autonomous generation improvement through self-evaluation conditioned on task constraints, though limited to single-generation tasks. Recent works by Pryzant et al., Paul et al., Xie et al., Yoran et al., Nair et al., Kim et al., and Goodman explore various self-evaluation and decider approaches.

Reflexion extends these concepts by implementing persisting memory of self-reflective experiences which allows an agent to identify its own errors and self-suggest lessons to learn from its mistakes over time.

**Comparative Advantages:**

| Feature | Self-Refine | Beam Search | Reflexion |
|---------|-------------|-------------|-----------|
| Self-refinement | Yes | No | Yes |
| Hidden constraints | No | No | Yes |
| Decision-making | No | Yes | Yes |
| Binary reward | No | Yes | Yes |
| Memory | No | No | Yes |

### Programming

AlphaCode, CodeT, Self-Debugging, and CodeRL employ test-driven development or code debugging practices. However:
- AlphaCode, Self-Debugging, CodeRL rely on ground truth test cases, invalidating pass@1 eligibility
- None implement self-reflection bridging error identification and implementation improvement
- CodeT lacks self-learning mechanisms

---

## 3. Reflexion: Reinforcement via Verbal Reflection

The framework uses three distinct model components working collaboratively:

### Actor ($M_a$)

Built on LLMs specifically prompted to generate text and actions from state observations. The actor samples actions from policy $\pi_\theta$ at time $t$, receives environmental observations. Diverse generation models (Chain of Thought, ReAct) explore different text and action generation aspects. A memory component ($mem$) provides additional context inspired by policy iteration approaches.

### Evaluator ($M_e$)

Assesses quality of Actor-generated outputs by computing reward scores. Variants include:
- **Reasoning tasks**: Exact match (EM) grading ensuring output-solution alignment
- **Decision-making tasks**: Predefined heuristic functions for specific criteria
- **Alternative approach**: Using different LLM instantiation as evaluator

### Self-Reflection ($M_{sr}$)

The Self-Reflection model, instantiated as an LLM, generates verbal self-reflections to provide valuable feedback for future trials. Given sparse reward signals (binary success/failure), current trajectory, and persistent memory ($mem$), the model generates nuanced, specific feedback exceeding scalar reward informativeness. This enables the agent to infer mistakes in multi-step tasks and suggest improved action sequences.

### Memory

Reflexion incorporates short-term and long-term memory components:
- **Short-term memory**: Trajectory history capturing fine-grain recent details
- **Long-term memory**: Self-Reflection model outputs storing distilled important experiences

### The Reflexion Process (Algorithm 1)

1. **Initialization**: Actor ($M_a$), Evaluator ($M_e$), Self-Reflection ($M_{sr}$), and policy $\pi_\theta$
2. **First Trial**: Actor generates trajectory $\tau_0$; Evaluator produces score $r_0 = M_e(\tau_0)$
3. **Reflection Amplification**: Self-Reflection analyzes $\{\tau_0, r_0\}$ to produce summary $sr_0$ stored in memory
4. **Iterative Loop**: Process continues until Evaluator deems $\tau_t$ correct or max trials reached
5. **Memory Management**: $sr_t$ appended to $mem$; bounded by maximum $\Omega$ (typically 1-3) for LLM context limitations

---

## 4. Experiments

Evaluation spans three task categories: decision-making, reasoning, and code generation. Reflexion improves performance by 22% in AlfWorld, 20% in HotPotQA, and 11% in HumanEval.

### 4.1 Sequential Decision-Making: ALFWorld

**Task Description**: Suite of 134 text-based environments requiring multi-step tasks (finding hidden objects, moving objects, manipulating objects). ReAct serves as the action generator.

**Self-Evaluation Implementation**: Two techniques enable fully autonomous behavior:
1. **Natural language classification**: LLM-based evaluation
2. **Hand-written heuristic**: Triggers reflection if same action receives identical response >3 cycles OR >30 total actions taken (inefficient planning)

**Results**:
- ReAct + Reflexion: 130/134 tasks completed
- Performance improvement across 12 consecutive trials
- ReAct-only: Plateaus between trials 6-7

**Analysis**: Common baseline error -- agent believes possessing item without verification, executing long unsuccessful trajectories without backtracking. Reflexion eliminates these cases using self-reflection converting lengthy failures into usable experiences.

Two primary memory-assisted scenarios:
1. Identifying early trajectory mistakes for new action or plan suggestions
2. Exploiting experience memory across trials for thorough location searches

### 4.2 Reasoning: HotpotQA

**Task Description**: Wikipedia-based dataset with 113k question-answer pairs requiring content parsing and multi-document reasoning.

**Implementations**:
- **Reflexion + Chain-of-Thought (CoT)**: $Q \to A$ and $Q, C_{gt} \to A$ implementations isolating reasoning ability
- **Reflexion + ReAct**: Holistic question-answering incorporating Wikipedia API context retrieval and step-by-step thinking

Exact match answer grading provides binary success signals. Memory limit set to 3 experiences.

**Results**:
- Reflexion outperforms all baselines significantly over learning steps
- ReAct-only, CoT-only, CoT(GT)-only: No probabilistic improvement (temperature 0.7)
- Reflexion + CoT(GT): 14% accuracy improvement despite 39% continued error rate

**Ablation** (isolating self-reflection advantage using CoT(GT) baseline):
- Baseline CoT(GT): Ground-truth context testing reasoning over long contexts
- CoT(GT) + Episodic Memory (EPM): Includes most recent trajectory
- Full Reflexion: Implements standard self-reflection step
- Self-reflection achieves 8% absolute improvement over episodic memory alone

### 4.3 Programming

**Datasets**:
- MBPP: Function body generation from natural language descriptions
- HumanEval: Similar function generation task
- LeetcodeHardGym: New benchmark with 40 Leetcode hard-level questions (post-October 8, 2022 release date)
- MultiPL-E translations enabling Rust evaluation

**Test Suite Generation**: Chain-of-Thought prompting produces diverse, extensive tests with descriptions. Syntactically valid tests constructed via abstract syntax tree (AST) validation. Maximum 6 unit tests sampled from validated collection.

**Results**:

| Benchmark + Language | Previous SOTA Pass@1 | SOTA Pass@1 | Reflexion Pass@1 |
|---|---|---|---|
| HumanEval (PY) | 65.8 (CodeT + GPT-3.5) | 80.1 (GPT-4) | **91.0** |
| HumanEval (RS) | -- | 60.0 (GPT-4) | **68.0** |
| MBPP (PY) | 67.7 (CodeT + Codex) | 80.1 (GPT-4) | 77.1 |
| MBPP (RS) | -- | 70.9 (GPT-4) | **75.4** |
| Leetcode Hard (PY) | -- | 7.5 (GPT-4) | **15.0** |

Reflexion achieves state-of-the-art on all benchmarks except MBPP Python.

**Test Generation Performance**:

| Benchmark + Language | Base | Reflexion | TP | FN | FP | TN |
|---|---|---|---|---|---|---|
| HumanEval (PY) | 0.80 | 0.91 | 0.99 | 0.40 | 0.01 | 0.60 |
| MBPP (PY) | 0.80 | 0.77 | 0.84 | 0.59 | 0.16 | 0.41 |
| HumanEval (RS) | 0.60 | 0.68 | 0.87 | 0.37 | 0.13 | 0.63 |
| MBPP (RS) | 0.71 | 0.75 | 0.84 | 0.51 | 0.16 | 0.49 |

**MBPP Python Analysis**: Performance gap attributed to test quality variance. False negatives are preferred over false positives as the agent may be able to use self-reflection to identify incorrect tests. MBPP Python exhibits 16.3% false positive rate versus HumanEval Python's 1.4%.

**Ablation Study (HumanEval Rust, 50 hardest)**:

| Approach | Test Generation | Self-reflection | Pass@1 (Acc) |
|---|---|---|---|
| Base model | No | No | 0.60 |
| Test generation omission | No | Yes | 0.52 |
| Self-reflection omission | Yes | No | 0.60 |
| Reflexion | Yes | Yes | 0.68 |

Omitting test generation: 52% vs 60% baseline -- agent cannot determine correctness without unit tests. Omitting self-reflection: No improvement over baseline -- natural language explanations crucial for error identification.

---

## 5. Limitations

At its core, Reflexion is an optimization technique that uses natural language to do policy optimization. Policy optimization is a powerful approach to improve action choice through experience, but it may still succumb to non-optimal local minima solutions.

Specific constraints:
- Long-term memory bounded to sliding window with maximum capacity
- Code generation limitations: non-deterministic functions, impure API-invoking functions, hardware-dependent output, parallel/concurrent behavior prediction difficulties

Future work encouraged: advanced memory structures (vector embedding databases, SQL databases).

---

## 6. Broader Impact

Reflexion empowers autonomous agents toward greater automation and efficiency but amplifies risks in misuse scenarios. The verbal reinforcement learning approach addresses traditional RL's black-box policy interpretability challenges: self-reflections could be monitored to ensure proper intent before using the tool.

---

## 7. Conclusion

Reflexion demonstrates language agents learning from prior failures through verbal reinforcement. Results significantly outperform current decision-making approaches via self-reflection. Future work encourages applying advanced RL techniques (value learning in natural language, off-policy exploration) within this framework.

---

## Key Figures

### Figure 1: Reflexion Framework Overview
Shows the three components (Actor, Evaluator, Self-Reflection) and the iterative loop: Actor generates trajectory, Evaluator scores it, Self-Reflection produces verbal feedback stored in memory, which conditions the Actor's next trial.

### Figure 2: AlfWorld Learning Curves
Demonstrates performance across 12 consecutive trials. ReAct + Reflexion approaches near-perfect scores while ReAct-only plateaus at ~78% (22% hallucination rate).

### Figure 3: Reflexion Process Diagram
Illustrates the conversion of binary/scalar feedback into verbal self-reflections stored in episodic memory buffer, conditioning subsequent trial behavior.

### Figure 4: HotpotQA Results
Shows consistent performance growth across trials for Reflexion variants, while baselines (ReAct-only, CoT-only) show no improvement with additional trials.

### Figure 5: Programming Ablation
Bar charts comparing base model, test-generation-only, self-reflection-only, and full Reflexion on HumanEval Rust (50 hardest problems).

---

## Appendix

### A: Evaluation with Additional Models

Self-correction ability emerges as stronger model capability:

| Model + Approach | Performance |
|---|---|
| starchat-beta | 0.26 pass@1 (no improvement with Reflexion) |
| text-davinci-003 | Reflexion: CoT 60->77%, ReAct 30->55% |
| gpt-3.5-turbo | Reflexion: CoT 57->71%, ReAct 26->38% |
| gpt-4 | Reflexion: CoT 68->80%, ReAct 39->51% |

### B: Decision-Making Details

**AlfWorld Example**: Trial #1 fails due to improper action sequencing. Self-reflection identifies error. Trial #2 succeeds with corrected action order.

**WebShop Limitation**: Reflexion struggles with tasks requiring significant exploration diversity. No improvement after 4 trials on WebShop (e-commerce navigation) due to ambiguous natural language search requiring highly diverse, unique behaviors.

### C: Programming Details

Includes full prompts for function implementation, self-reflection instruction, and ablation examples.

### D: Reasoning Details

Full HotpotQA multi-trial examples demonstrating how self-reflection enables successful search strategy changes and corrects reasoning errors across trials.

---

## Top References

1. Yao et al. (2023) -- ReAct: Synergizing Reasoning and Acting in Language Models
2. Wei et al. (2022) -- Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
3. Madaan et al. (2023) -- Self-Refine: Iterative Refinement with Self-Feedback
4. Chen et al. (2021) -- Evaluating Large Language Models Trained on Code (Codex)
5. OpenAI (2023) -- GPT-4 Technical Report
6. Shridhar et al. (2021) -- ALFWorld: Aligning Text and Embodied Environments
7. Yang et al. (2018) -- HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering
8. Park et al. (2023) -- Generative Agents: Interactive Simulacra of Human Behavior
9. Cassano et al. (2023) -- MultiPL-E: A Scalable and Polyglot Approach to Benchmarking Neural Code Generation
10. Le et al. (2022) -- CodeRL: Mastering Code Generation through Pretrained Models and Deep Reinforcement Learning
