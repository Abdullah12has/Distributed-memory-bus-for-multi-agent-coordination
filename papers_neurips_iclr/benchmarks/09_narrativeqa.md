# The NarrativeQA Reading Comprehension Challenge

**Authors:** Tomas Kocisky, Jonathan Schwarz, Phil Blunsom, Chris Dyer, Karl Moritz Hermann, Gabor Melis, Edward Grefenstette

**Venue:** arXiv preprint, 2017 (DeepMind / University of Oxford)

**arXiv:** [1712.07040](https://arxiv.org/abs/1712.07040)

---

## Abstract

This work introduces a dataset requiring readers to comprehend full narratives. The authors note that existing RC datasets and tasks are dominated by questions that can be solved by selecting answers using superficial information. Their contribution presents tasks where readers answer questions about stories from complete books or movie scripts, designed to test deeper understanding beyond pattern matching. Humans readily solve these tasks, while conventional reading comprehension models perform poorly.

---

## 1. Introduction

The paper argues that existing reading comprehension datasets suffer from a critical flaw: questions can be solved using superficial information (e.g., local context similarity or global term frequency) rather than requiring genuine narrative understanding. NarrativeQA addresses this limitation.

---

## 2. Dataset Composition

- **1,572 stories** (evenly split between books and movie scripts)
- **46,765 human-generated question-answer pairs**
- Questions averaged 9.8 tokens; answers averaged 4.73 tokens
- Only 44.05% of answers appear as spans in summaries; 29.57% in full stories
- Dataset split: 1,102 training documents, 115 validation, 355 test documents

### Two Reading Tasks

1. **Summary-based task:** Answer questions from human-written plot summaries
2. **Full-story task:** Answer questions from complete books or movie scripts

---

## 3. Data Collection

- Stories sourced from Project Gutenberg (books) and web scrapers (movie scripts)
- Plot summaries matched from Wikipedia
- Amazon Mechanical Turk annotators created 10 QA pairs per summary
- Annotators were explicitly instructed to use their own words, avoid yes/no questions, and create diverse question types

### Question Type Distribution

- "What" (38.04%)
- "Who" (23.37%)
- "Why" (9.78%)
- "How" (8.85%)
- "Where" (7.53%)

### Question Categories

- Person (30.54%)
- Description (24.50%)
- Location (9.73%)
- Why/reason (9.40%)
- How/method (8.05%)

---

## 4. Baseline Models

### Information Retrieval Baselines

- Bleu-1, Rouge-L, and cosine similarity using TF-IDF and GloVe embeddings
- Span extraction from documents of varying lengths

### Neural Models

1. **Seq2Seq:** Basic sequence-to-sequence model without context
2. **Attention Sum Reader:** Adapted from CNN/Daily Mail dataset work
3. **Span Prediction:** Simplified Bi-Directional Attention Flow network
4. **Two-step Retrieval + Neural:** For full stories, retrieved relevant chunks first using TF-IDF cosine similarity

---

## 5. Results

### Summary-Based Task

| Model | Bleu-1 | Bleu-4 | Rouge-L |
|-------|--------|--------|---------|
| Span Prediction | 33.72 | 15.53 | 36.30 |
| Attention Sum Reader | 23.20 | 6.39 | 22.26 |
| Human baseline | 44.43 | 19.65 | 57.02 |

### Full Story Task

| Model | Bleu-1 | Bleu-4 | Rouge-L |
|-------|--------|--------|---------|
| Attention Sum Reader (10 chunks) | 19.09 | 1.81 | 14.02 |
| Span Prediction | 5.68 | 0.25 | 6.22 |
| Human baseline | 44.43 | 19.65 | 57.02 |

The dramatic performance drop on full stories compared to summaries demonstrates the challenge's difficulty.

---

## 6. Technical Details

### Entity Handling

Named entities replaced with markers (e.g., "@entity42") and embeddings permuted during training/testing, enabling generalization to unseen entities.

### Retrieval Strategy for Full Stories

Since processing 60,000+ token documents directly is computationally infeasible, the approach retrieves 200-word chunks using TF-IDF cosine similarity, then applies neural models to concatenated chunks.

---

## 7. Critical Findings

### Limitations of Prior Datasets

- **MCTest:** Too small (660 stories)
- **CNN/Daily Mail:** Cloze-form answers favoring entity selection
- **SQuAD/NewsQA:** Answers restricted to document spans; questions answerable from single sentences
- **MS MARCO:** Many answers are verbatim span copies despite being labeled free-form

### NarrativeQA Advantages

The dataset requires integration of information distributed across several statements throughout the document rather than pattern matching. Stories are self-contained, and annotators created questions based on summaries alone, reducing localization bias.

---

## 8. Figure Descriptions

- **Figure 1:** Example question-answer pairs from books and movie scripts showing narrative complexity
- **Figure 2:** Distribution of question types and categories
- **Figure 3:** Performance comparison between summary-based and full-story tasks

---

## Key References

1. Richardson et al. (2013) --- MCTest dataset
2. Hermann et al. (2015) --- CNN/Daily Mail dataset
3. Rajpurkar et al. (2016) --- SQuAD dataset
4. Hill et al. (2016) --- Children's Book Test
5. Seo et al. (2016) --- Bi-Directional Attention Flow
6. Kadlec et al. (2016) --- Attention Sum Reader
7. Bajgar et al. (2016) --- BookTest dataset
8. Trischler et al. (2016) --- NewsQA dataset
9. Papineni et al. (2002) --- BLEU metric
10. Lin (2004) --- ROUGE metric
