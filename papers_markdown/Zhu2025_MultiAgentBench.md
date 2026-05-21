# MultiAgentBench: Evaluating the Collaboration and Competition of LLM Agents

- **Authors:** Kunlun Zhu, Hongyi Du, Zhaochen Hong, Xiaocheng Yang, Shuyi Guo, Zhe Wang, Zhenhailong Wang, Cheng Qian, Xiangru Tang, Heng Ji, Jiaxuan You
- **Year:** 2025
- **Venue:** arXiv preprint (cs.MA)
- **ArXiv:** [2503.01935](https://arxiv.org/abs/2503.01935)

## Abstract

Existing benchmarks for LLM agents either focus on single-agent tasks or are confined to narrow domains, failing to capture the dynamics of multi-agent coordination and competition. MultiAgentBench is a comprehensive benchmark designed to evaluate LLM-based multi-agent systems across diverse, interactive scenarios. The framework measures not only task completion but also the quality of collaboration and competition using novel, milestone-based key performance indicators. The benchmark evaluates various coordination protocols (star, chain, tree, and graph topologies) and strategies such as group discussion and cognitive planning. Key findings: gpt-4o-mini reaches the highest average task score, graph structure performs best among coordination protocols in research scenarios, and cognitive planning improves milestone achievement rates by 3%.

## Key Contributions

1. **Milestone-based KPIs**: Novel evaluation metrics that track progress through flexible milestones rather than binary success/failure, with LLM-based detection of milestone achievement.
2. **Coordination protocol evaluation**: Systematic comparison of star, chain, tree, and graph topologies for multi-agent communication.
3. **Dual evaluation dimensions**: Task completion (KPI scores) and coordination quality (communication + planning scores on five-point scales).
4. **Diverse scenario coverage**: Six scenarios spanning collaborative (research, Minecraft, database analysis, coding) and competitive (Werewolf, bargaining) domains, each with 100 test cases.

## Methodology

- Six interactive scenarios with both collaborative and competitive dynamics
- Each scenario has 100 test cases with variations
- Milestone-based KPIs: LLM-based detector continuously monitors iterative processes to identify achieved milestones; individual contributions tracked per agent
- Coordination score combines communication score and planning score (both on 5-point scales)
- Evaluation of five LLMs: Meta-Llama-3.1-8B, Meta-Llama-3.1-70B, Meta-Llama-3.3-70B, GPT-3.5-turbo, GPT-4o-mini

## Key Results

| Finding | Detail |
|---------|--------|
| Best task performance | GPT-4o-mini across multiple domains |
| Best coordination protocol | Graph topology (research scenario) |
| Worst protocol efficiency | Tree configuration (highest token consumption) |
| Cognitive planning benefit | +3% milestone achievement rate |
| Star vs Graph | Comparable task scores |

## Relevance to Thesis

MultiAgentBench provides the most directly relevant evaluation framework for the thesis's multi-agent coordination experiments. Its milestone-based KPIs parallel the thesis's approach to measuring coordination quality beyond simple task completion. The coordination protocol topologies (star, chain, tree, graph) inform the PlannerWorkerCritic architecture's communication patterns. The benchmark's finding that graph structures outperform others validates the thesis's bus-based communication model (which is effectively a shared-bus variant enabling graph-like connectivity). The distinction between collaborative and competitive scenarios maps to the thesis's workload families (a: fact aggregation, b: multi-step retrieval, c: mixed).
