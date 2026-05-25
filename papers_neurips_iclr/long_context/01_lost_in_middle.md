# Lost in the Middle: How Language Models Use Long Contexts

**Authors:** Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang

**Venue:** Transactions of the Association for Computational Linguistics (TACL), 2023

**ArXiv:** [2307.03172](https://arxiv.org/abs/2307.03172)

---

## Abstract

While recent language models have the ability to take long contexts as input, relatively little is known about how well they use longer context. This paper analyzes language model performance on two tasks that require identifying relevant information in input contexts: multi-document question answering and key-value retrieval. The findings reveal that performance is often highest when relevant information occurs at the very beginning or end of the input context, and significantly degrades when models must access relevant information in the middle of long contexts. This U-shaped performance curve persists even in models specifically designed for long contexts.

---

## 1. Introduction

Language models are being deployed with ever-longer context windows (up to 100K+ tokens), but the question of how effectively they utilize these extended contexts remains largely unexplored. This paper systematically investigates position-dependent performance degradation.

## 2. Experimental Setup

### 2.1 Multi-Document Question Answering

- Models receive a question plus k documents (exactly one containing the answer)
- Tests ability to locate and use relevant information among distractors
- Uses NaturalQuestions benchmark data from Wikipedia
- Relevant document position systematically varied across all positions

### 2.2 Key-Value Retrieval (Synthetic)

- Models retrieve values from JSON-formatted key-value pairs using UUID strings
- Isolates basic retrieval capability without semantic complexity
- Tests exact token matching from input context
- Fully controlled synthetic task to eliminate confounds

## 3. Key Results

### 3.1 U-Shaped Performance Curve

All models exhibit a characteristic U-shaped curve:
- **Best performance**: When relevant information is at the beginning or end of context
- **Worst performance**: When relevant information is in the middle
- GPT-3.5-Turbo's middle-position performance (56.1%) falls below its closed-book baseline

### 3.2 Length Degradation

| Number of Documents | Performance Trend |
|--------------------|-------------------|
| 10 | Moderate U-shape |
| 20 | Pronounced U-shape |
| 30 | Severe U-shape, middle performance near chance |

Performance consistently decreases as context grows longer, even for extended-context models.

### 3.3 Architecture Insights

- **Decoder-only models** (GPT-3.5, Claude): Strong U-shaped curves at all lengths
- **Encoder-decoder models** (Flan-T5, Flan-UL2): Robust within training sequence lengths but exhibit U-shaped curves beyond them
- Extended-context models show the same U-shaped pattern despite training on longer sequences

### 3.4 Query Placement

- Adding query both before and after documents helps key-value retrieval
- Minimal improvement for multi-document QA
- The position effect is primarily about document position, not query position

## 4. Practical Implications

### 4.1 Open-Domain QA Case Study

Model performance saturates around 20 retrieved documents:
- Using more than 20 retrieved documents provides only marginal improvement (~1.5% for GPT-3.5-Turbo)
- Additional documents may actually hurt performance due to the U-shaped effect
- Optimal number of retrieved documents depends on model architecture

### 4.2 Design Recommendations

1. Place most relevant information at the beginning or end of context
2. Limit the number of retrieved documents to avoid middle-position degradation
3. Consider architectural changes to attention mechanisms for more uniform position utilization

## 5. Analysis

### 5.1 Attention Pattern Analysis

The U-shaped curve correlates with attention patterns that preferentially attend to tokens at the beginning (primacy bias) and end (recency bias) of the input sequence.

### 5.2 Robustness

The effect is robust across:
- Different model families (GPT, Claude, Llama, Flan)
- Different model sizes
- Different task types (QA, retrieval)
- Different context lengths

## 6. Figures

- **Figure 1**: U-shaped performance curves for multiple models across different document positions, showing consistent degradation in the middle.
- **Figure 2**: Performance as a function of context length (number of documents) for various models.
- **Figure 3**: Key-value retrieval accuracy across positions, showing similar U-shaped patterns on the fully synthetic task.
- **Figure 4**: Open-domain QA performance as a function of the number of retrieved documents, showing diminishing returns beyond 20.

---

## References (Top 10)

1. Vaswani et al. (2017) - Attention is All You Need (Transformer architecture foundation)
2. Dao et al. (2022) - FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness
3. Khandelwal et al. (2018) - Sharp Nearby, Fuzzy Far Away: How Neural Language Models Use Context
4. Petroni et al. (2020) - Context Effects on Language Model Factuality
5. Sun et al. (2021) - Do Long-Range Language Models Actually Use Long-Range Context?
6. Krishna et al. (2022) - RankGen: Improving Text Generation with Large Ranking Models
7. O'Connor & Andreas (2021) - What Context Features Can Transformer Language Models Use?
8. Izacard et al. (2021) - Unsupervised Dense Information Retrieval with Contrastive Learning (Contriever)
9. Li et al. (2023) - How Long Can Open-Source LLMs Truly Promise on Context Length? (LongChat)
10. Raffel et al. (2020) - Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer (T5)
