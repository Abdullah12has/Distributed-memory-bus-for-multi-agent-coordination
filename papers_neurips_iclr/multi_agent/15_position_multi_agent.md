# Mixture-of-Agents Enhances Large Language Model Capabilities

**Authors:** Junlin Wang, Jue Wang, Ben Athiwaratkun, Ce Zhang, James Zou

**Venue:** arXiv preprint, 2024

**ArXiv:** [2406.04692](https://arxiv.org/abs/2406.04692)

---

## Abstract

The paper proposes a Mixture-of-Agents (MoA) methodology that combines multiple LLMs through a layered architecture. Each agent takes all the outputs from agents in the previous layer as auxiliary information in generating its response. The approach achieved state-of-the-art results on multiple benchmarks, with the open-source version scoring 65.1% on AlpacaEval 2.0, outperforming GPT-4 Omni's 57.5%.

---

## 1. Introduction

The paper introduces the concept of "collaborativeness" -- the observation that LLMs generally produce better responses when provided access to outputs from other models, even if those reference outputs are of lower quality individually. This property motivates the layered MoA architecture.

## 2. Mixture-of-Agents Methodology

### Architecture Design

- Multiple layers (default: 3), each containing multiple LLM agents
- Each layer's agents receive all outputs from the previous layer as auxiliary context
- Final layer produces the consolidated output through an "Aggregate-and-Synthesize" prompt

### Agent Roles

Models are classified into two categories:
- **Proposers:** Generate diverse perspectives and reference responses (high output diversity)
- **Aggregators:** Synthesize high-quality outputs from multiple inputs (strong synthesis capability)

### Key Properties

- No fine-tuning required; operates entirely through prompting
- Composable with different model combinations
- Naturally extends to more layers for iterative refinement

## 3. Evaluation

### Main Results

| Benchmark | MoA Score | Previous Best |
|-----------|-----------|---------------|
| AlpacaEval 2.0 (LC Win Rate) | 65.1-65.7% | 57.5% (GPT-4o) |
| MT-Bench | 9.25-9.40 | 9.31 (GPT-4 Turbo) |
| FLASK | Outperforms GPT-4o | -- |

### Analysis

- Model diversity significantly improves performance vs. single-proposer setups
- MoA substantially outperforms simple ranking-based selection methods
- Achieves roughly 2x more cost effectiveness than GPT-4 Turbo at comparable quality
- Aggregators incorporate the highest-quality proposed answers into their syntheses

### Scaling Behavior

Performance improves with:
- More layers (diminishing returns beyond 3)
- More diverse proposer models
- Higher-quality aggregator models

## 4. Related Work

The paper reviews:
- LLM reasoning enhancement methods (chain-of-thought, self-consistency)
- Ensemble and mixture methods for language models
- Multi-agent collaboration frameworks

## 5. Conclusion

MoA demonstrates that layered multi-agent collaboration using only prompting can surpass individual state-of-the-art models. The framework is flexible, cost-effective, and compatible with both open-source and proprietary models.

### Limitations

- High Time-to-First-Token latency since the model cannot decide the first token until the last MoA layer is reached
- Increased computational cost from running multiple models
- Sequential layer dependency limits parallelism

---

## Figures

- **Figure 1:** LC win rates improve substantially when LLMs receive responses from other models -- demonstrates "collaborativeness" across six architectures
- **Figure 2:** Four-layer MoA structure with three agents per layer showing iterative refinement flow
- **Figure 3:** Performance comparison across benchmarks (bar charts)
- **Figure 4:** Ablation on number of layers and model diversity
- **Figure 5:** Pareto frontier analysis showing MoA achieves superior cost-effectiveness compared to proprietary alternatives

---

## Key References

1. Dubois, Y., et al. (2024) -- AlpacaEval 2.0 benchmark methodology
2. Zheng, L., et al. (2023) -- MT-Bench evaluation framework
3. Wei, J., et al. (2022) -- Chain-of-thought prompting foundations
4. Wang, X., et al. (2023) -- Self-consistency improves chain-of-thought reasoning
5. Jiang, D., et al. (2023) -- LLM-Blender: Ensembling LLMs with pairwise ranking
6. Du, Y., et al. (2023) -- Improving factuality through multiagent debate
7. Li, G., et al. (2023) -- CAMEL: Communicative agents for mind exploration
8. Brown, T., et al. (2020) -- GPT-3: Language models as few-shot learners
9. Touvron, H., et al. (2023) -- LLaMA 2: Open foundation and fine-tuned chat models
10. Shazeer, N., et al. (2017) -- Outrageously large neural networks: The sparsely-gated mixture-of-experts layer
