# From Local to Global: A Graph RAG Approach to Query-Focused Summarization

- **Authors:** Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Dasha Metropolitansky, Robert Osazuwa Ness, Jonathan Larson
- **Venue:** Microsoft Research (arXiv preprint; integrated into LangChain, LlamaIndex, Neo4J ecosystems)
- **ArXiv:** [2404.16130](https://arxiv.org/abs/2404.16130)
- **Submitted:** April 24, 2024; revised February 19, 2025

---

## Abstract

The use of retrieval-augmented generation (RAG) to retrieve relevant information from an external knowledge source enables large language models (LLMs) to answer questions over private and/or previously unseen document collections. However, RAG fails on global questions directed at an entire text corpus, such as "What are the main themes in the dataset?" since this is inherently a query-focused summarization (QFS) task, for which existing methods struggle. Prior QFS methods, meanwhile, fail to scale to the quantities of text indexed by typical RAG systems. The authors propose a Graph RAG approach to question answering over private text corpora that scales with both the generality of user questions and the quantity of source text to be indexed. Their approach uses an LLM to build a graph-based text index in two stages: first to derive an entity knowledge graph from the source documents, then to pre-generate community summaries for all groups of closely-related entities. Given a query, each community summary is used to generate a partial response, before all partial responses are summarized into a final response to the user. For a class of global sensemaking questions over datasets in the 1 million token range, the approach shows substantial improvements over a naive RAG baseline for both the comprehensiveness and diversity of generated answers.

---

## 1. Introduction

The paper addresses a critical limitation of conventional vector RAG systems: their inability to answer global "sensemaking" questions that require understanding of entire document collections rather than localized retrieval.

Examples of global questions:
- "What are the main themes in this dataset?"
- "How do the topics discussed relate to each other?"
- "What are the most significant trends across all documents?"

These are fundamentally query-focused summarization (QFS) tasks, not simple retrieval tasks. GraphRAG solves this by combining knowledge graph extraction with hierarchical community detection and community-level summarization.

---

## 2. Background

### 2.1 RAG Approaches and Systems

Standard RAG retrieves semantically similar records using text embeddings. "In canonical RAG approaches, the retrieval process returns a set number of records that are semantically similar to the query." The authors term conventional approaches "vector RAG" and distinguish their method by supporting sensemaking -- reasoning over interconnected concepts requiring global understanding.

### 2.2 Using Knowledge Graphs with LLMs and RAG

GraphRAG is positioned within emerging LLM-based knowledge graph extraction research. Key distinction: "GraphRAG contrasts with these approaches by focusing on a previously unexplored quality of graphs in this context: their inherent modularity and the ability to partition graphs into nested modular communities."

### 2.3 Adaptive Benchmarking for RAG Evaluation

The authors develop novel evaluation methodology using LLM-generated personas and use-cases to create corpus-specific questions. "Our adaptive benchmarking approach uses persona generation to create queries that are representative of real-world RAG system usage."

### 2.4 RAG Evaluation Criteria

Three primary criteria evaluate global sensemaking:
- **Comprehensiveness:** How much detail does the answer provide to cover all aspects of the question?
- **Diversity:** How varied and rich is the answer in providing different perspectives and insights?
- **Empowerment:** How well does the answer help the reader understand and make informed judgments?

A control criterion, **Directness** (how specifically and clearly the answer addresses the question), validates results.

---

## 3. Methods

### 3.1 GraphRAG Pipeline

The pipeline comprises six stages:

#### 3.1.1 Source Documents to Text Chunks

Documents split into chunks (default 600 tokens with 100-token overlaps). This represents a fundamental trade-off: larger chunks reduce LLM calls but degrade recall for early-appearing information.

#### 3.1.2 Text Chunks to Entities and Relationships

LLMs extract entities, their descriptions, relationships, and claims from each chunk:
- **Entities:** Name, type, comprehensive description
- **Relationships:** Entity pairs that are "clearly related" with description and strength score
- **Claims:** Verifiable factual statements about entities (dates, events, interactions)

A self-reflection technique improves extraction quality: after initial extraction, the LLM is prompted to assess whether entities were missed and to "glean" additional ones (up to a maximum number of iterations).

#### 3.1.3 Entities and Relationships to Knowledge Graph

Entity and relationship instances become graph nodes and edges. "Entity descriptions are aggregated and summarized for each node and edge. Relationships are aggregated into graph edges, where the number of duplicates for a given relationship becomes edge weights."

Entity reconciliation uses exact string matching, though softer approaches are possible.

#### 3.1.4 Knowledge Graph to Graph Communities

Leiden community detection algorithm recursively partitions the graph hierarchically until leaf communities cannot be further divided. "Each level of this hierarchy provides a community partition that covers the nodes of the graph in a mutually exclusive, collectively exhaustive way."

#### 3.1.5 Graph Communities to Community Summaries

**Leaf-level communities:** Prioritize elements by node degree, iteratively adding element descriptions until token limits are reached.

**Higher-level communities:** Substitute sub-community summaries when element summaries exceed context windows.

Each community produces a JSON-formatted report with:
- Title
- Summary
- Impact severity rating (0-10)
- Rating explanation
- 5-10 key insights with grounding citations

#### 3.1.6 Community Summaries to Global Answer (Map-Reduce)

Query answering proceeds in three steps:
1. **Prepare:** Randomly shuffle community summaries, divide into pre-specified token-sized chunks
2. **Map:** Generate intermediate answers in parallel, each scored 0-100 for helpfulness
3. **Reduce:** Sort answers by score, add to context window until full, generate final global answer

### 3.2 Global Sensemaking Question Generation

**Algorithm 1: Adaptive Question Generation**

```
Input: Corpus description, K users, N tasks/user, M questions/(user,task)
Output: K*N*M high-level corpus-understanding questions

1. Prompt LLM to describe K potential user personas
2. For each user, identify N relevant tasks
3. For each user-task pair, generate M questions requiring full corpus understanding
4. Collect K*N*M test questions
```

For evaluation: $K = M = N = 5$ produces 125 test questions per dataset.

### 3.3 Self-Reflection for Entity Extraction

After entities are extracted from a chunk, the LLM is prompted to assess completeness:
1. Extract entities from chunk
2. Assess completeness with logit bias = 100 forcing yes/no
3. If incomplete, use continuation "MANY entities were missed"
4. Iterate up to maximum specified iterations

Result: Enables larger chunk sizes without recall loss.

---

## 4. Experiments

### 4.1 Experiment 1: LLM-as-Judge Comparison

#### 4.1.1 Datasets

Two corpora (~1 million tokens each):
- **Podcast transcripts:** "Behind the Tech with Kevin Scott" (1,669 chunks x 600 tokens, ~1M tokens)
- **News articles:** Multi-category benchmark (3,197 chunks x 600 tokens, ~1.7M tokens)

#### 4.1.2 Conditions

Six experimental conditions:

| Condition | Description |
|-----------|-------------|
| C0 | Root-level communities (fewest, most abstract) |
| C1 | High-level sub-communities |
| C2 | Intermediate communities |
| C3 | Leaf-level communities (most numerous, most specific) |
| TS | Map-reduce on source texts (no graph) |
| SS | Vector RAG semantic search baseline |

#### 4.1.3 Configuration

Fixed 8K-token context window for all stages. Graph indexing (600-token chunks) required 281 minutes for Podcast dataset.

#### 4.1.4 Results

**Comprehensiveness win rates vs. Vector RAG (SS):**
- Podcast: 72-83% (p < 0.001)
- News: 72-80% (p < 0.001)

**Diversity win rates vs. Vector RAG (SS):**
- Podcast: 75-82% (p < 0.001)
- News: 62-71% (p < 0.01)

**Community summaries vs. source text (TS):**
- Podcast intermediate-level: 57% comprehensiveness win (p < 0.001), 57% diversity win (p = 0.036)
- News low-level: 64% comprehensiveness win (p < 0.001), 60% diversity win (p < 0.001)

#### Community Summary Statistics

| Metric | Podcast C0 | C1 | C2 | C3 | TS | News C0 | C1 | C2 | C3 | TS |
|--------|-----------|----|----|----|----|---------|----|----|----|----|
| Units | 34 | 367 | 969 | 1,310 | 1,669 | 55 | 555 | 1,797 | 2,142 | 3,197 |
| Tokens | 26,657 | 225,756 | 565,720 | 746,100 | 1,014,611 | 39,770 | 352,641 | 980,898 | 1,140,266 | 1,707,694 |
| % Max | 2.6 | 22.2 | 55.8 | 73.5 | 100 | 2.3 | 20.7 | 57.4 | 66.8 | 100 |

C0 requires >97% fewer tokens than source text while maintaining comprehensiveness advantage.

### 4.2 Experiment 2: Claim-Based Validation

Uses "Claimify" -- an LLM-based method that identifies sentences containing factual claims and decomposes them into simple, self-contained claims. Extracted 47,075 unique claims (average 31 per answer).

#### Average Claims per Answer

| Condition | News | Podcast |
|-----------|------|---------|
| C0 | 34.18 | 32.21 |
| C1 | 32.50 | 32.20 |
| C2 | 31.62 | 32.46 |
| C3 | 33.14 | 32.28 |
| TS | 32.89 | 31.39 |
| SS | 25.23 | 26.50 |

All global approaches significantly outperformed vector RAG (p < 0.05).

#### Average Diversity Clusters (News Articles)

| Distance Threshold | C0 | C1 | C2 | C3 | TS | SS |
|-------------------|----|----|----|----|----|----|
| 0.5 | 23.42 | 21.85 | 21.90 | 22.13 | 21.80 | 17.92 |
| 0.6 | 21.65 | 20.38 | 20.30 | 20.52 | 20.13 | 16.78 |
| 0.7 | 20.19 | 19.06 | 19.03 | 19.13 | 18.62 | 15.80 |
| 0.8 | 18.86 | 17.78 | 17.82 | 17.79 | 17.30 | 14.80 |

#### Average Diversity Clusters (Podcast Transcripts)

| Distance Threshold | C0 | C1 | C2 | C3 | TS | SS |
|-------------------|----|----|----|----|----|----|
| 0.5 | 23.16 | 22.62 | 22.52 | 21.93 | 21.14 | 18.55 |
| 0.6 | 21.65 | 21.33 | 21.21 | 20.62 | 19.70 | 17.39 |
| 0.7 | 20.41 | 20.04 | 19.79 | 19.22 | 18.08 | 16.28 |
| 0.8 | 19.26 | 18.77 | 18.46 | 17.89 | 16.66 | 15.07 |

#### LLM-Judge vs. Claim-Based Agreement

With non-tie aggregations: 78% agreement for comprehensiveness, 69-70% for diversity across distance thresholds.

---

## 5. Key Findings

### Graph Statistics

| Dataset | Nodes | Edges |
|---------|-------|-------|
| Podcast | 8,564 | 20,691 |
| News | 15,754 | 19,520 |

### Empowerment Criterion

Mixed results across global approaches vs. vector RAG and GraphRAG vs. source text. "Using an LLM to analyze LLM reasoning for this measure indicated that the ability to provide specific examples, quotes, and citations was judged to be key."

### Directness Criterion (Control)

Vector RAG produced the most direct responses across all comparisons, validating that comprehensiveness/diversity gains involve trade-offs in conciseness.

---

## Figures

- **Figure 1:** GraphRAG pipeline flow diagram. Shows the progression from Source Documents through Text Chunks, Entity and Relationship Extraction, Knowledge Graph Construction, Community Detection, Community Summarization, to final Global Answer via map-reduce. Separates indexing-time stages from query-time stages.

- **Figure 2:** Head-to-head win rate percentages comparing all six conditions across two datasets, four evaluation metrics, and 125 questions (5 replicates each, averaged). Bold entries indicate winners per dataset/metric. GraphRAG conditions substantially outperform naive RAG on comprehensiveness and diversity.

- **Figure 3:** Entity references detected in HotPotQA dataset versus chunk size (600, 1,200, 2,400 tokens) and self-reflection iterations (0-3). Demonstrates that self-reflection enables use of larger chunks without quality degradation.

- **Figure 4:** Leiden algorithm community detection visualization on MultiHop-RAG dataset showing hierarchical clustering at two levels, with entity node sizes proportional to degree centrality.

---

## Implementation Details

- Leiden community detection via graspologic library
- Fixed 8K-token context window across all pipeline stages
- Entity reconciliation via exact string matching
- Community summaries include structured JSON reports
- Open-source with integrations into LangChain, LlamaIndex, Neo4J, and NebulaGraph

---

## Key References (Top 10 Most Cited)

1. Lewis et al. (2020) -- RAG: Retrieval-augmented generation for knowledge-intensive NLP tasks (NeurIPS)
2. Traag et al. (2019) -- From Louvain to Leiden: Guaranteeing well-connected communities
3. Brown et al. (2020) -- Language models are few-shot learners (GPT-3, NeurIPS)
4. Achiam et al. (2023) -- GPT-4 technical report
5. Trivedi et al. (2022) -- IRCoT: Interleaving retrieval with chain-of-thought reasoning
6. Sarthi et al. (2024) -- RAPTOR: Recursive abstractive processing for tree-organized retrieval
7. Gao et al. (2023) -- Retrieval-augmented generation for large language models: A survey
8. Khattab et al. (2022) -- Demonstrate-search-predict: Composing retrieval and language models
9. Yang et al. (2018) -- HotpotQA: A dataset for diverse, explainable multi-hop QA
10. Newman (2006) -- Modularity and community structure in networks (PNAS)
