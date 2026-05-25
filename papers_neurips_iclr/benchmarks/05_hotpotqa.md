# HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering

**Authors:** Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Bengio, William W. Cohen, Ruslan Salakhutdinov, Christopher D. Manning

**Venue:** EMNLP 2018

**arXiv:** [1809.09600](https://arxiv.org/abs/1809.09600)

---

## Abstract

HotpotQA is a large-scale dataset containing 113k Wikipedia-based QA pairs that require finding and reasoning over multiple supporting documents to answer. The questions are diverse and not constrained to any pre-existing knowledge bases or knowledge schemas. The work also provides sentence-level supporting facts for explainability and introduces a new type of factoid comparison questions to test QA systems' ability to extract relevant facts and perform necessary comparison.

---

## 1. Introduction

The dataset addresses gaps in existing question answering systems by requiring genuine multi-hop reasoning. HotpotQA leverages Wikipedia's hyperlink structure to create questions that naturally span multiple documents.

---

## 2. Data Collection Methodology

### Wikipedia Hyperlink Graph Construction

The authors built a directed graph from Wikipedia's first paragraphs, where edges represent hyperlinks between articles. This approach leverages the observation that hyperlinks in Wikipedia articles often naturally entail a relation between two entities.

### Candidate Paragraph Pair Generation

- **Bridge Entity Approach:** Uses entities as connectors between document pairs (e.g., "Thom Yorke" connects questions about Radiohead's frontman to his birthdate)
- **Curated Pages:** Bridge entities restricted to 591 manually curated Wikipedia categories
- **Comparison Questions:** Randomly samples entity pairs from 42 manually curated lists of similar entities

### Supporting Facts Collection

Crowd workers explicitly identified sentences necessary for answering questions, providing strong supervision on which facts matter for reasoning.

---

## 3. Data Splits

| Dataset | Description | Count |
|---------|-------------|-------|
| train-easy | Single-hop questions | 18,089 |
| train-medium | Multi-hop (model-solvable) | 56,814 |
| train-hard | Hard multi-hop | 15,661 |
| dev | Hard multi-hop validation | 7,405 |
| test-distractor | Hard multi-hop with 8 distractors | 7,405 |
| test-fullwiki | Hard multi-hop with full Wikipedia | 7,405 |
| **Total** | | **112,779** |

---

## 4. Benchmark Settings

1. **Distractor Setting:** Models receive 2 gold paragraphs plus 8 TF-IDF retrieved distractors, testing noise filtering ability
2. **Full Wiki Setting:** Models search entire Wikipedia first paragraphs without gold paragraph access, testing real-world retrieval plus reasoning

---

## 5. Multi-hop Reasoning Types

| Type | Percentage | Description |
|------|-----------|-------------|
| Type I (Bridge Entity Inference) | 42% | Identify bridge entity to complete second hop |
| Comparison | 27% | Compare two entities on shared properties |
| Type II (Property Intersection) | 15% | Locate answer by checking multiple properties |
| Type III (Bridge Property Inference) | 6% | Infer entity property through bridge entity |
| Other | 2% | Require >2 supporting facts |
| Single-hop/Unanswerable | 8% | Single-hop or unanswerable questions |

### Answer Type Distribution

- Person: 30%
- Group/Organization: 13%
- Location: 10%
- Date: 9%
- Number: 8%
- Yes/No: 6%
- Other: 24%

---

## 6. Results

### Main Performance

| Setting | Answer EM | Answer F1 | Sup Fact F1 | Joint F1 |
|---------|-----------|-----------|------------|----------|
| Distractor (dev) | 44.44% | 58.28% | 66.66% | 40.86% |
| Distractor (test) | 45.46% | 58.99% | 66.62% | 41.37% |
| Full Wiki (dev) | 24.68% | 34.36% | 40.98% | 17.73% |
| Full Wiki (test) | 25.23% | 34.40% | 40.69% | 17.85% |

### Human Performance (1,000 samples)

| Metric | Gold Only | Distractor | Human | Human Upper Bound |
|--------|-----------|-----------|-------|------------------|
| Answer EM | 65.87% | 60.88% | 83.60% | 96.80% |
| Answer F1 | 74.67% | 68.99% | 91.40% | 98.77% |
| Supporting Fact F1 | 90.41% | 74.67% | 90.04% | 97.56% |
| Joint F1 | 68.15% | 52.37% | 82.55% | 96.37% |

### Ablation Study (Distractor/Dev)

| Configuration | EM | F1 |
|---------------|----|----|
| Full model | 44.44 | 58.28 |
| Without supporting fact supervision | 42.79 | 56.19 |
| Without self-attention | 41.59 | 55.19 |
| Without character model | 41.66 | 55.25 |
| Without train-easy | 41.61 | 55.12 |
| Without train-medium | 31.07 | 43.61 |

---

## 7. Evaluation Metrics

**Joint F1 Formula:**
- Precision: P(joint) = P(answer) x P(supporting facts)
- Recall: R(joint) = R(answer) x R(supporting facts)
- Joint F1 = 2 x P(joint) x R(joint) / (P(joint) + R(joint))

Joint EM requires both tasks achieving exact match simultaneously.

---

## 8. Notable Findings

1. 30% EM gap between models and humans in distractor setting; 58% in full wiki setting
2. Bridge entity questions outperform comparison questions (59% vs 55% F1) in distractor setting
3. Oracle supporting facts yield 10+ F1 improvement over baseline
4. Supporting fact supervision yields approximately 2 F1 improvement

---

## 9. Figure Descriptions

- **Figure 1:** Example multi-hop question showing bridge entity connecting two Wikipedia articles
- **Figure 2:** Distribution of question types and reasoning categories
- **Figure 3:** Performance comparison across settings and question types

---

## Key References

1. Clark and Gardner (2017) --- Simple and effective multi-paragraph reading comprehension
2. Rajpurkar et al. (2016) --- SQuAD: 100,000+ questions for machine comprehension
3. Chen et al. (2017) --- Reading Wikipedia to answer open-domain questions
4. Wang et al. (2017) --- Gated self-matching networks for reading comprehension
5. Seo et al. (2017) --- Bidirectional attention flow for machine comprehension
6. Welbl et al. (2018) --- QAngaroo: Constructing datasets for multi-hop reading comprehension
7. Talmor and Berant (2018) --- ComplexWebQuestions: The web as knowledge-base
8. Joshi et al. (2017) --- TriviaQA: Large scale distantly supervised challenge dataset
9. Dunn et al. (2017) --- SearchQA: New Q&A dataset augmented with search engine context
10. Miller et al. (2017) --- ParlAI: Dialog research software platform
