# AOI: Context-Aware Multi-Agent Operations via Dynamic Scheduling and Hierarchical Memory Compression

- **Authors:** Zishan Bai, Hanxuan Chen, Jing Luo, Ziyi Ni, Enze Ge, Jiacheng Shi, Yichao Zhang, Jiayi Gu, Zhimo Han, Riyang Bao, Junfeng Hao
- **Year:** 2025
- **Venue:** arXiv preprint (cs.MA, cs.AI)
- **ArXiv:** [2512.13956](https://arxiv.org/abs/2512.13956)

## Abstract

The proliferation of cloud-native architectures with microservices and dynamic orchestration has made modern IT infrastructures exceedingly complex. This generates overwhelming operational data, leading to bottlenecks in information processing, task coordination, and contextual continuity during fault diagnosis. AOI (AI-Oriented Operations) proposes a multi-agent collaborative framework integrating three specialized agents with an LLM-based Context Compressor. The system features dynamic task scheduling based on real-time system states and a three-layer memory architecture optimizing context retention. It achieves 72.4% context compression while preserving 92.8% critical information, improving task success to 94.2% and reducing mean time to resolution (MTTR) by 34.4%.

## Key Contributions

1. **Three specialized agents**: Observer (task analysis/decomposition), Probe (read-only information gathering), Executor (system modifications with safety checkpoints and rollback).
2. **Three-layer memory architecture**: Raw Context Storage (24h retention), Task Queue Management (lifecycle tracking), Compressed Context Cache (7-day LLM-processed strategic info).
3. **Dynamic task scheduling**: Prioritization based on real-time system state rather than static rules.
4. **LLM-based context compression**: Sliding window mechanism (768 tokens, 50% overlap) preserving operationally critical information.

## Methodology

- **Observer Agent**: Hierarchical task breakdown and adaptive scheduling
- **Probe Agent**: Strictly read-only, non-destructive system queries and log analysis
- **Executor Agent**: Performs modifications with safety checkpoints; instant rollback on failures
- **Context Compressor**: Sliding window (768 tokens, 50% overlap) using LLM semantic understanding to identify and preserve critical information
- **Memory layers**: Layer 1 (raw, 24h), Layer 2 (structured task queue), Layer 3 (compressed cache, 7 days)

## Key Results

| Metric | AOI | vs. Baseline |
|--------|-----|-------------|
| Task Success Rate | 94.2% | +34.9% over rule-based |
| Mean Time to Resolution | 22.1 min | -34.4% reduction |
| Context Compression | 72.4% reduction | -- |
| Information Preservation | 92.8% | -- |
| False Positive Rate | 3.1% | Lowest among methods |

Evaluated on AIOpsLab (1000 fault scenarios, 50 fault types), Loghub benchmark, and HDFS/BGL/OpenStack production environments.

## Relevance to Thesis

AOI is the most architecturally similar system to the thesis's distributed memory bus. Its three-layer memory hierarchy (raw/task queue/compressed cache) directly parallels the thesis's memory bus storage layers. The context compression approach (sliding window with LLM-based semantic preservation) validates the thesis's core premise that compression can maintain coordination quality. The 92.8% information preservation at 72.4% compression provides a concrete benchmark for the thesis's H1 hypothesis. The Observer/Probe/Executor agent specialization pattern aligns with the PlannerWorkerCritic architecture. The key difference is that AOI targets IT operations while the thesis targets campus multi-agent coordination.
