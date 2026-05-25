# Ghost in the Minecraft: Generally Capable Agents for Open-World Environments via Large Language Models with Text-based Knowledge and Memory

**Authors:** Xizhou Zhu, Yuntao Chen, Hao Tian, Chenxin Tao, Weijie Su, Chenyu Yang, Gao Huang, Bin Li, Lewei Lu, Xiaogang Wang, Yu Qiao, Zhaoxiang Zhang, Jifeng Dai

**Venue:** arXiv preprint (2023)

**arXiv:** [https://arxiv.org/abs/2305.17144](https://arxiv.org/abs/2305.17144)

---

## Abstract

The paper presents GITM (Ghost In The Minecraft), a novel framework that integrates Large Language Models (LLMs) with text-based knowledge and memory to create generally capable agents for open-world environments. By leveraging the extensive world knowledge encoded in LLMs, GITM is able to achieve a remarkable improvement of +47.5% in success rate over prior methods on the challenging ObtainDiamond task in Minecraft. GITM became the first agent to successfully acquire all items in the Overworld of Minecraft's technology tree. Notably, the approach requires no GPU training for LLMs and demonstrates superior performance compared to traditional reinforcement learning approaches.

---

## 1. Introduction

Open-world environments like Minecraft present unique challenges for AI agents: vast state spaces, sparse rewards, long-horizon planning, and the need for diverse skills. Prior approaches using reinforcement learning (RL) required extensive training and struggled with generalization. GITM proposes using LLMs as the reasoning backbone, augmented with structured text-based knowledge and memory.

### Key Challenges Addressed
- Hierarchical goal decomposition for complex multi-step tasks
- Knowledge representation without visual perception
- Long-horizon planning with sparse reward signals
- Generalization across the full Minecraft technology tree

## 2. Framework Architecture

### 2.1 LLM Decomposer

Breaks down high-level goals into structured sub-goal trees:
- **Goal decomposition**: Complex goals (e.g., "obtain diamond") are recursively decomposed into simpler sub-goals
- **Dependency tracking**: Sub-goals are organized with explicit prerequisite relationships
- **Dynamic replanning**: Failed sub-goals trigger re-decomposition with updated context

### 2.2 Text-based Knowledge Base

Structured knowledge about Minecraft, represented entirely in text:
- **Item recipes**: Crafting requirements and dependencies
- **Entity information**: Properties, behaviors, and interactions
- **Environment knowledge**: Biome characteristics, resource locations
- **Action templates**: Pre-defined action patterns for common tasks

### 2.3 Text-based Memory System

Maintains agent experience and state:
- **Action memory**: Records of previously executed actions and outcomes
- **Feedback memory**: Success/failure signals from environment interactions
- **State memory**: Current inventory, position, and environmental observations

### 2.4 LLM Planner

Generates action plans by combining:
- Current sub-goal from the decomposer
- Relevant knowledge from the knowledge base
- Historical memory of past attempts
- Current environmental state

## 3. Experimental Results

### ObtainDiamond Task

| Method | Success Rate |
|--------|-------------|
| DreamerV3 (RL baseline) | ~1% |
| DEPS | ~5% |
| GITM (GPT-3.5) | ~20% |
| GITM (GPT-4) | **~52.5%** |

GITM achieves a +47.5% improvement in success rate over prior state-of-the-art on ObtainDiamond.

### Technology Tree Coverage

GITM became the first agent to successfully obtain **all items** in the Minecraft Overworld technology tree, covering:
- Basic resources (wood, stone, iron, gold, diamond)
- Crafted tools and weapons
- Food items and agricultural products
- Redstone components
- Complex multi-step items

### Comparison with RL Approaches

| Aspect | RL Methods | GITM |
|--------|-----------|------|
| Training required | Millions of steps | None (zero-shot) |
| GPU training | Required | Not required |
| Generalization | Limited | Broad |
| Success rate (ObtainDiamond) | ~1-5% | ~52.5% |
| Technology tree coverage | Partial | Complete |

## 4. Key Design Decisions

### Text-Only Representation
All environment interactions are converted to text, avoiding the need for visual perception models. This enables direct LLM reasoning without multimodal integration overhead.

### Hierarchical Goal Decomposition
Rather than flat action sequences, GITM uses recursive decomposition that mirrors human planning strategies. This enables handling of tasks requiring 50+ sequential steps.

### Feedback-Driven Replanning
When sub-goals fail, the system:
1. Records the failure in memory
2. Analyzes the failure reason
3. Generates alternative sub-goal decompositions
4. Retries with updated knowledge

## 5. Ablation Studies

Key ablation findings:
- Removing the knowledge base significantly degrades performance on crafting tasks
- Memory system is crucial for recovering from failures
- GPT-4 provides substantially better goal decomposition than GPT-3.5
- Hierarchical decomposition outperforms flat planning approaches

## 6. Limitations

- Relies on text-based environment interface (no visual perception)
- API costs for GPT-4 are significant for long-horizon tasks
- Knowledge base requires manual curation for domain specifics
- Cannot handle tasks requiring precise spatial reasoning or construction

---

## Figure Descriptions

- **Figure 1:** Overview of GITM framework showing decomposer, knowledge base, memory, and planner
- **Figure 2:** Goal decomposition tree for the ObtainDiamond task
- **Figure 3:** Technology tree coverage comparison with prior methods
- **Figure 4:** Success rate curves across different task categories
- **Figure 5:** Example action sequences generated by the LLM planner

---

## Top 10 References

1. Fan, L., et al. (2022). MineDojo: Building open-ended embodied agents with internet-scale knowledge. *NeurIPS*.
2. Hafner, D., et al. (2023). Mastering diverse domains through world models (DreamerV3). *arXiv*.
3. Wang, G., et al. (2023). Voyager: An open-ended embodied agent with large language models. *NeurIPS*.
4. Brown, T., et al. (2020). Language models are few-shot learners. *NeurIPS*.
5. OpenAI (2023). GPT-4 technical report. *arXiv:2303.08774*.
6. Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning. *NeurIPS*.
7. Yao, S., et al. (2022). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
8. Huang, W., et al. (2022). Language models as zero-shot planners. *ICML*.
9. Baker, B., et al. (2022). Video PreTraining (VPT): Learning to act by watching unlabeled online videos. *NeurIPS*.
10. Shinn, N., et al. (2023). Reflexion: Language agents with verbal reinforcement learning. *NeurIPS*.
