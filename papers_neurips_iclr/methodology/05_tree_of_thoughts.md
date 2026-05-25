# Tree of Thoughts: Deliberate Problem Solving with Large Language Models

**Authors:** Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Thomas L. Griffiths, Yuan Cao, Karthik Narasimhan

**Venue:** NeurIPS 2023

**arXiv:** [2305.10601](https://arxiv.org/abs/2305.10601)

---

## Abstract

The paper introduces Tree of Thoughts (ToT), a framework extending Chain of Thought prompting. Rather than linear token-by-token inference, ToT enables language models to consider multiple different reasoning paths and self-evaluate choices across coherent text units. This allows deliberate decision-making with lookahead and backtracking capabilities. The method demonstrated significant improvements on complex tasks---achieving a 74% success rate on Game of 24 compared to 4% with standard approaches.

---

## 1. Introduction

ToT frames problem-solving as search through a combinatorial problem space, represented as a tree where each node represents a partial solution. This mirrors classical AI planning approaches from the 1950s while leveraging modern LM capabilities. The framework represents "System 2" thinking---deliberate and analytical---compared to the "System 1" associative token-level decisions of standard LM inference.

---

## 2. Key Components

### Four Design Questions

1. **Thought Decomposition:** How to break problems into intermediate steps (varies by task: equations, writing plans, or word clues)
2. **Thought Generation:** Two strategies---sampling i.i.d. thoughts (rich solution spaces) or proposing sequentially (constrained spaces)
3. **State Evaluation:** LM-based heuristics either valuing states independently or comparing them through voting
4. **Search Algorithm:** Breadth-first (BFS) for shallow trees or depth-first (DFS) with backtracking for deeper exploration

### Evaluation Methods

- **Independent valuation:** LM assigns scalar scores (1--10) or classifications (sure/maybe/impossible)
- **Comparative voting:** LM selects the most promising state among candidates

---

## 3. Search Algorithms

### BFS Algorithm

Maintains b most promising states per step; evaluates all candidates and retains top-b performers through iterative refinement.

### DFS Algorithm

Explores most promising branch first; backtracks when states fall below a value threshold or after T steps; includes pruning for efficiency.

---

## 4. Results

| Task | Baseline (CoT) | ToT Success |
|------|----------------|------------|
| Game of 24 | 4% | 74% (b=5) |
| Creative Writing | 6.93 (score) | 7.56 (score) |
| Mini Crosswords | 40.6% | 78% (letters), 60% (words), 20% (games) |

### Key Findings

- ToT significantly enhances language models' problem-solving abilities on three novel tasks requiring non-trivial planning or search
- Game of 24 shows particularly dramatic improvement---CoT achieves only 4%, while ToT reaches 74%
- Performance gains persist across different model scales (GPT-4 and GPT-3.5)

---

## 5. Cost-Benefit Analysis

ToT requires substantially more computation:
- **Game of 24:** approximately 5,500 completion tokens (vs. 6,700 for 100 CoT samples), cost approximately $0.74
- **Creative Writing:** approximately 4,000 tokens, cost approximately $0.32
- Trade-off: Higher computational cost for substantially better performance on hard reasoning tasks

---

## 6. Broader Context

The approach is general and flexible enough to support different levels of thoughts, different ways to generate and evaluate thoughts, and different search algorithms. It provides a way to translate classical insights about problem-solving into actionable methods for contemporary LMs, combining the interpretability and reasoning of structured search with the generality and flexibility of large language models.

---

## 7. Limitations and Future Work

- Most beneficial for tasks where standard approaches struggle
- Requires more resources than sampling baselines
- Authors suggest fine-tuning LMs with high-level counterfactual decision making could enhance performance
- More advanced search algorithms (A*, MCTS) left for future exploration

---

## 8. Figure Descriptions

- **Figure 1:** Comparison of IO prompting, CoT, CoT with self-consistency, and Tree of Thoughts approaches
- **Figure 2:** Game of 24 tree search visualization showing branching and pruning
- **Figure 3:** Creative writing task pipeline with coherent plan generation and evaluation
- **Figure 4:** Mini crossword solving with DFS and backtracking

---

## Key References

1. Wei et al. (2022) --- Chain of Thought Prompting
2. OpenAI (2023) --- GPT-4 Technical Report
3. Wang et al. (2022) --- Self-Consistency with CoT
4. Newell et al. (1959, 1972) --- Classical problem-solving research
5. Kahneman (2011) --- Thinking, Fast and Slow (dual process theory)
6. Silver et al. (2017) --- AlphaGo
7. Chowdhery et al. (2022) --- PaLM
8. Brown et al. (2020) --- GPT-3
9. Daw et al. (2005) --- Uncertainty-based behavioral control
10. Campbell et al. (2002) --- Deep Blue
