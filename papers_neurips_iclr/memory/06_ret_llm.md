# RET-LLM: Towards a General Read-Write Memory for Large Language Models

**Authors:** Ali Modarressi, Ayyoob Imani, Mohsen Fayyaz, Hinrich Schutze

**Venue:** arXiv preprint (cs.CL), 2023

**arXiv:** [https://arxiv.org/abs/2305.14322](https://arxiv.org/abs/2305.14322)

**Note:** The user-provided arxiv ID 2307.16069 resolved to an unrelated paper. The correct ID for RET-LLM is 2305.14322.

---

## Abstract

The authors propose RET-LLM, a novel framework that equips large language models with a general read-write memory unit, allowing them to extract, store, and recall knowledge from text as needed for task performance. Drawing from Davidsonian semantics, knowledge is represented as triplets within a scalable, updatable memory system. The approach demonstrates effectiveness in question-answering and temporal reasoning tasks, showing advantages over baseline methods. This concept was later extended in the follow-up work MemLLM (Modarressi et al., 2024).

---

## 1. Introduction

Current LLMs encode knowledge implicitly within their parameters rather than maintaining dedicated, inspectable memory units. This creates several problems:
- Knowledge becomes outdated as the world changes
- Updating requires expensive retraining
- Stored knowledge is not interpretable or verifiable
- Models cannot selectively store and retrieve information

RET-LLM addresses these by providing an explicit, structured memory that supports both read and write operations.

### 1.1 Desirable Memory Properties

The authors identify five key characteristics an ideal LLM memory should possess:
1. **Read and write operations** -- bidirectional access
2. **Scalability** -- ability to grow with information needs
3. **Diverse data source support** -- not limited to a single domain
4. **Interpretability** -- stored knowledge should be human-readable
5. **Aggregatable information** -- ability to combine knowledge across sources

## 2. Architecture

RET-LLM comprises three components:

### 2.1 Fine-tuned LLM (Agent)

- Base model: Alpaca-7B (instruction-following LLaMA variant)
- Fine-tuned with LoRA for parameter efficiency
- Trained to generate memory API calls when appropriate

### 2.2 Controller

Manages interactions between the LLM and the memory unit:
- Parses LLM-generated API calls
- Executes memory operations
- Returns results to the LLM for response generation

### 2.3 Memory Unit

Stores information as structured triplets following Davidsonian semantics:

**Storage Format:**
```
(concept_1, relationship, concept_2)
```
Example: `(Mark Zuckerberg, CEO, Meta Inc.)`

**Retrieval Mechanisms:**
- Text-based exact matching in three-column tables
- Vector representations for fuzzy/semantic matching
- Locality-Sensitive Hashing (LSH) for efficient similarity search

## 3. Memory API

Two primary operations enable LLM-memory interaction:

### 3.1 MEM_WRITE

Triggered when the LLM encounters informative statements:
- Extracts knowledge as triplets
- Stores in the memory unit with vector embeddings
- Supports updating existing entries

### 3.2 MEM_READ

Triggered when the LLM needs stored information:
- Queries using one or two triplet parameters
- Supports exact and approximate matching
- Returns relevant triplets for answer generation

## 4. Training Methodology

### 4.1 Synthetic Training Data

- Randomly generated person names paired with real organization names
- Five relationship types: employment, manager, investor, founder, customer
- Six distinct query pattern types requiring different response strategies

### 4.2 Fine-tuning Details

- Base: Instruction-following Alpaca-7B
- Method: LoRA (Low-Rank Adaptation)
- Hardware: Single A6000 48GB GPU
- Loss applied only to API query and answer segments (not provided context)

## 5. Results

### 5.1 Qualitative Evaluation

- **Zero-shot Alpaca-7B:** Failed on tasks despite having necessary context information
- **RET-LLM:** Successfully answered identical questions after storing extracted triplets
- **Temporal QA:** Correctly handled temporal fact updates through memory modification

### 5.2 Advantages Over Baselines

| Aspect | Previous RAG Methods | RET-LLM |
|---|---|---|
| Memory granularity | Document-level | Triplet-level |
| Knowledge aggregation | Limited | Cross-document |
| Updateability | Re-index documents | Modify individual triplets |
| Interpretability | Opaque chunks | Readable triplets |

## 6. Temporal Knowledge Handling

A key advantage: when facts change (e.g., current U.S. president), users simply update the relevant memory entries rather than retraining the model. This enables:
- Real-time knowledge updates
- User-controlled fact correction
- Temporal reasoning across fact versions

## 7. Related Work

- **Retrieval-augmented generation:** RAG, REALM, RETRO -- limited to document-level retrieval
- **Knowledge graphs:** Structured but require external construction pipelines
- **Memory networks:** End-to-end differentiable but less interpretable
- **Tool-augmented LLMs:** Toolformer, API-based approaches

RET-LLM uniquely combines structured knowledge storage with LLM-native read/write operations.

## 8. Limitations and Future Work

- Concept-stage work requiring empirical evaluation on real datasets
- Relationship type generalization needs further development
- Quantitative benchmarking against established baselines needed
- Scalability to millions of triplets not yet demonstrated

## 9. Conclusion

RET-LLM introduces a triplet-based external memory architecture for LLMs with a text-based API schema enabling standardized model-memory communication. The framework prioritizes interpretability, scalability, and modifiability, allowing users to understand, expand, and update model knowledge without retraining.

---

## Key Figures

- **Figure 1:** RET-LLM architecture showing the LLM agent, controller, and memory unit with read/write operations.
- **Figure 2:** Example interaction flow: user provides information, LLM generates MEM_WRITE call, later retrieves with MEM_READ.
- **Figure 3:** Triplet storage and retrieval pipeline with LSH-based similarity search.

---

## Top References

1. Touvron et al. (2023). LLaMA: Open and Efficient Foundation Language Models.
2. Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS.
3. Borgeaud et al. (2022). Improving Language Models by Retrieving from Trillions of Tokens. ICML.
4. Schick et al. (2023). Toolformer: Language Models Can Teach Themselves to Use Tools. NeurIPS.
5. Hu et al. (2022). LoRA: Low-Rank Adaptation of Large Language Models. ICLR.
6. Weston et al. (2015). Memory Networks. ICLR.
7. Karpukhin et al. (2020). Dense Passage Retrieval for Open-Domain Question Answering. EMNLP.
8. Davidson, D. (1967). The Logical Form of Action Sentences.
9. Taori et al. (2023). Stanford Alpaca: An Instruction-following LLaMA Model.
10. Guu et al. (2020). REALM: Retrieval-Augmented Language Model Pre-Training. ICML.
