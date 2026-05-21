# Memory as a Service (MaaS): Rethinking Contextual Memory as Service-Oriented Modules for Collaborative Agents

- **Authors:** Haichang Li
- **Year:** 2025
- **Venue:** Workshop position paper
- **ArXiv:** [2506.22815](https://arxiv.org/abs/2506.22815)

## Abstract

Current LLM-based agent systems treat memory as local state attached to specific contexts, creating "memory silos" that limit collaboration. This paper proposes Memory as a Service (MaaS) -- decoupling memory from interaction byproducts and encapsulating it as an independently callable, dynamically composable, governed modular service. MaaS leverages memory's dual nature (private yet publicly serviceable) to enable controlled interoperability across entities. The paper presents a two-dimensional design space defined by entity structure and service type, and outlines research directions addressing governance, security, and ethics for collaborative agents operating across entity boundaries.

## Key Contributions

1. **MaaS conceptual framework**: Architectural alternative to "bound memory" where memory becomes an independently addressable, composable, governed service.
2. **Two-dimensional design space**: Entity structure (intra-entity, inter-entity, group-level) crossed with service type (injective/unidirectional vs. exchange-based/multidirectional).
3. **Three core design principles**: Independent addressability (standardized, permission-gated protocols), contextual composability (microservice-like flexible combination), intent-aware governability (authorization considers "who" and "why").
4. **Governance framework**: Identifies public-side (dynamic permissioning, interoperability), privacy-side (integrity verification, provenance, privacy-preserving computation), and ecosystem-side (economic models, ethics) challenges.

## Methodology

MaaS proposes three core architectural components:

- **Memory Containers**: Package data with access policy metadata, embedding governance logic directly into the asset
- **Memory Routing Layer**: Semantically and goal-oriented adjudication and routing of service requests
- **Permission Control Mechanism**: Dynamic authorization based on context, identity, and permission levels

The framework distinguishes itself from existing systems (MemGPT, Mem0, MCP) that treat memory as local state bound to specific contexts or entities.

## Key Results

This is a position paper proposing an architectural framework rather than presenting empirical results. The contribution is conceptual: defining the MaaS paradigm and its design space.

## Relevance to Thesis

MaaS is the most conceptually aligned paper to the thesis's distributed memory bus architecture. The thesis's memory bus (FastAPI service with /write, /read, /subscribe, /audit endpoints) is essentially an implementation of the MaaS vision -- memory decoupled from individual agents and exposed as a shared service. The thesis's slot-based storage model with SSE subscriptions implements the "independent addressability" principle. The distinction between injective and exchange-based service types maps to the thesis's write/read vs. subscribe (SSE) patterns. MaaS's governance concerns (access control, provenance) are addressed in the thesis through the audit endpoint. The key gap between MaaS (conceptual) and the thesis (implemented) is that the thesis adds context compression as a core memory bus capability, which MaaS does not address.
