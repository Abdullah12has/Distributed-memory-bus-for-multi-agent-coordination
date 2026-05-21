# Multi-Agent Memory from a Computer Architecture Perspective: Visions and Challenges Ahead

- **Authors:** Zhongming Yu, Naicheng Yu, Hejia Zhang, Wentao Ni, Mingrui Yin, Jiaying Yang, Yujie Zhao, Jishen Zhao
- **Year:** 2026
- **Venue:** arXiv preprint (cs.AR)
- **ArXiv:** [2603.10062](https://arxiv.org/abs/2603.10062)

## Abstract

As LLM agents evolve into collaborative multi-agent systems, their memory requirements grow rapidly in complexity. This position paper frames multi-agent memory as a computer architecture problem. It distinguishes shared and distributed memory paradigms, proposes a three-layer memory hierarchy (I/O, cache, and memory), and identifies two critical protocol gaps: cache sharing across agents and structured memory access control. The authors argue that multi-agent memory consistency is the most pressing open challenge and that their architectural framing provides a foundation for building reliable, scalable multi-agent systems.

## Key Contributions

1. **Computer architecture framing**: Positions multi-agent memory as analogous to hardware memory hierarchies, treating agent performance as a data movement problem.
2. **Shared vs. distributed memory paradigm analysis**: Shared memory (common vector store/DB) enables knowledge reuse but has coherence problems; distributed memory (local with selective sync) improves isolation but risks state divergence.
3. **Three-layer memory hierarchy**: I/O layer (input/output interfaces), cache layer (fast, limited-capacity for immediate reasoning), memory layer (large-capacity, slower, for persistence and retrieval).
4. **Two critical protocol gaps**: (a) No principled protocol for sharing cached artifacts across agents; (b) Memory access control (permissions, scope, granularity) remains under-specified.
5. **Memory consistency as frontier problem**: Multi-agent memory consistency has not been formally defined, and no framework exists to detect or classify consistency violations.

## Methodology

This is a position paper providing architectural analysis rather than empirical methodology. The authors draw parallels between:

- CPU cache hierarchies and agent memory layers
- Shared-memory multiprocessor coherence protocols and multi-agent state synchronization
- Hardware memory consistency models and agent coordination guarantees

Key open questions identified:
- **Update-time visibility**: When writes from one agent become observable to others
- **Read-time conflict resolution**: How agents handle conflicting or stale information

## Key Results

No empirical results (position paper). The contribution is the architectural framework and identification of open problems.

## Relevance to Thesis

This paper provides the strongest theoretical foundation for the thesis's "distributed memory bus" metaphor. The thesis's architecture directly instantiates several concepts from this paper: the memory bus acts as a shared memory layer with structured access (read/write/subscribe endpoints); the slot-based storage with vector store backend implements the cache+memory layers; the SSE subscription mechanism addresses update-time visibility. The thesis advances beyond this paper by actually implementing a working system and adding context compression as a first-class memory bus operation -- directly addressing the cache layer's "limited capacity for immediate reasoning" through compression rather than eviction. The two protocol gaps identified (cache sharing, access control) map precisely to thesis features: the bus provides cache sharing via shared slots, and the audit endpoint provides access control primitives.
