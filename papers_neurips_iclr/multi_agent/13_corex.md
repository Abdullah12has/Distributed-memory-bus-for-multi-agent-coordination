# Corex: Pushing the Boundaries of Complex Reasoning through Multi-Model Collaboration

**Authors:** Qiushi Sun, Zhangyue Yin, Xiang Li, Zhiyong Wu, Xipeng Qiu, Lingpeng Kong

**Venue:** COLM 2024 / ICLR 2024 Workshop on LLM Agents

**ArXiv:** [2310.00280](https://arxiv.org/abs/2310.00280) (Note: user-provided ID 2310.00299 maps to a different paper; the correct COREX ID is 2310.00280)

---

## Abstract

Corex introduces strategies transforming LLMs into autonomous agents through multi-model collaboration. The framework employs three collaborative paradigms -- Debate, Review, and Retrieve -- to enhance the factuality, faithfulness, and reliability of the reasoning process. Testing across four reasoning task categories demonstrates that coordinated multiple LLM approaches substantially outperform existing solutions while maintaining cost-effectiveness and supporting diverse model combinations.

---

## 1. Introduction

Large language models excel at NLP tasks but struggle with complex reasoning. Rather than merely scaling models or refining prompts, the authors propose enabling models to "think outside the box" through collaborative approaches inspired by human behavior.

## 2. Related Work

Three research areas:
- **Chain-of-Thought Prompting:** Methods like CoT, self-consistency decoding, and PAL
- **External Knowledge and Tools:** Using retrieval and code generation for reasoning
- **Multi-Model Synergy:** Emerging work on collaborative LLM systems

## 3. Core Framework

### 3.1 Debate Mode

Agents are divided randomly into two groups with one reserved as a judge. Groups iteratively refine reasoning chains through structured discussions rather than forcing convergence to a single answer. The judge evaluates competing arguments and selects the most well-reasoned solution.

### 3.2 Review Mode

One primary agent generates solutions; others sequentially review and improve them. This addresses cumulative errors in chain-of-thought reasoning and bugs in generated code through a peer-review-style collaboration process.

### 3.3 Retrieve Mode

Agents independently generate reasoning chains and predictions. A retriever agent evaluates faithfulness between reasoning processes and final answers, selecting the most internally consistent pair rather than relying on simple majority voting.

## 4. Experiments

### Task Categories and Results

| Task Category | Key Finding |
|---|---|
| Mathematical Reasoning | Corex surpasses CoT-SC(10) with only 5 agents |
| Commonsense Reasoning | Outperforms ComplexCoT by >6% on StrategyQA |
| Symbolic Reasoning | Multi-model collaboration notably exceeds baselines on Big-Bench |
| Semi-structured Reasoning | Significant gains on FinQA and ConvFinQA |

### Analysis

**Cost-Effectiveness:** Corex achieves comparable or superior performance using 5-10% of computational costs versus majority voting methods.

**Model Synergies:** Judge capability in Debate mode correlates with task performance. Retrieve mode shows robustness across different LLM retrievers.

**Annotation Efficiency:** Performance remains stable with fewer few-shot examples, reducing reliance on curated demonstrations.

## 5. Limitations

- Open-source models were not tested in the main experiments
- Stability issues emerge when integrating multiple diverse LLMs
- Better orchestration strategies needed for heterogeneous model ensembles

## 6. Conclusion

Corex demonstrates that multi-model collaboration provides a cost-effective and reliable approach to improving complex reasoning, with three complementary paradigms suited to different task characteristics.

---

## Figures

- **Figure 1:** Overview of three collaboration modes (Debate, Review, Retrieve)
- **Figure 2:** Debate mode workflow showing group division, argumentation rounds, and judge evaluation
- **Figure 3:** Review mode pipeline with sequential agent improvements
- **Figure 4:** Retrieve mode showing independent generation and faithfulness-based selection
- **Figure 5:** Cost-performance tradeoff analysis across methods

---

## Key References

1. Wei, J., et al. (2022b) -- Chain-of-thought prompting
2. Wang, X., et al. (2023d) -- Self-consistency decoding
3. Gao, L., et al. (2022) -- Program-aided language models (PAL)
4. Du, Y., et al. (2023) -- Multi-agent debate for factuality
5. Kojima, T., et al. (2022) -- Zero-shot reasoning in LLMs
6. Chen, W., et al. (2022) -- Program of thoughts prompting
7. Liang, T., et al. (2023) -- Encouraging divergent thinking in LLMs
8. Yao, S., et al. (2023) -- Tree of thoughts reasoning
9. Brown, T., et al. (2020) -- GPT-3: Language models as few-shot learners
10. OpenAI (2023) -- GPT-4 technical report
