# Unlocking Context Constraints of LLMs: Enhancing Context Efficiency of LLMs with Self-Information-Based Content Filtering

**Authors:** Yucheng Li

**Venue:** arXiv preprint (cs.CL), 2023

**arXiv:** [2304.12102](https://arxiv.org/abs/2304.12102)

---

## Abstract

Large language models (LLMs) have received significant attention by achieving remarkable performance across various tasks. However, their fixed context length poses challenges when processing long documents or maintaining extended conversations. This paper proposes a method called Selective Context that employs self-information to filter out less informative content, thereby enhancing the efficiency of the fixed context length. The authors demonstrate the effectiveness of their approach on tasks of summarisation and question answering across different data sources, including academic papers, news articles, and conversation transcripts.

---

## 1. Introduction

LLMs cannot retain information beyond their context window, creating fundamental challenges for processing lengthy documents or extended conversations. While increasing context length is possible, it incurs significant computational costs due to the quadratic scaling of the self-attention mechanism.

The core insight behind Selective Context is that "LLMs do not need all content in a document or the entire conversation history to answer users' queries." By identifying and removing less informative tokens, phrases, or sentences, the remaining context can convey the same essential information in fewer tokens.

---

## 2. Self-Information Framework

Selective Context uses self-information (surprisal) as the metric for content informativeness. For a token $x_t$ in context, its self-information is:

$$I(x_t) = -\log_2 P(x_t | x_0, x_1, \ldots, x_{t-1})$$

This metric quantifies how surprising or informative a token is given the preceding context. The additive property of self-information allows computing informativeness scores for larger units by summing token-level values:

$$I(U) = \sum_{t \in U} I(x_t)$$

where $U$ is a lexical unit (sentence, phrase, or token group).

---

## 3. Method: Selective Context

### 3.1 Three-Step Process

1. **Compute self-information scores** for each token using a base language model (GPT-2 Curie)
2. **Merge tokens into lexical units** at one of three granularities:
   - Sentence-level
   - Phrase-level
   - Token-level
3. **Apply percentile-based filtering** to retain high-information content:

$$C' = \{U_i \mid I(U_i) \geq I_p, \; 1 \leq i \leq n\}$$

where $I_p$ is the percentile threshold (e.g., the 50th percentile retains only the top 50% most informative units).

### 3.2 Granularity Options

- **Sentence-level**: Computes mean self-information per sentence, drops least informative sentences
- **Phrase-level**: Groups tokens into noun phrases, verb phrases, etc., filters at phrase level
- **Token-level**: Direct token filtering (finest granularity, most aggressive)

---

## 4. Experimental Design

### 4.1 Datasets

| Dataset | Documents | Avg. Sentences | Avg. Phrases | Avg. Tokens |
|---|---|---|---|---|
| ArXiv | 408 | 28.20 | 514.55 | 864.85 |
| ShareGPT | 470 | 27.35 | 389.42 | 689.32 |
| BBC News | 294 | 25.63 | 523.96 | 732.54 |

### 4.2 Tasks Evaluated

1. **Original context reconstruction**: Can the LLM reconstruct the original text from the filtered version?
2. **Summarization**: Quality of summaries generated from filtered context
3. **Question answering**: Accuracy of QA from filtered context
4. **Conversation response generation**: Quality of responses from filtered conversation history

### 4.3 Evaluation Metrics

BLEU, METEOR, ROUGE (1, 2, L), BERTScore (Precision, Recall, F1)

### 4.4 Models

- **Generation**: ChatGPT (GPT-3.5-turbo)
- **Self-information computation**: GPT-2 Curie

---

## 5. Results

### 5.1 Main Results Across Reduction Ratios

| Method | Task | BLEU | METEOR | ROUGE-1 | ROUGE-2 | ROUGE-L | BERTScore F1 |
|---|---|---|---|---|---|---|---|
| Original | Summarisation | .274 | .481 | .570 | .321 | .416 | .911 |
| Original | QA | .529 | .664 | .690 | .581 | .664 | .940 |
| Original | Conversation | .238 | .343 | .451 | .249 | .332 | .877 |
| Original | Avg. | .347 | .496 | .571 | .383 | .471 | .909 |
| SC-0.2 | Avg. | .295 | .460 | .540 | .346 | .438 | .902 |
| SC-0.35 | Avg. | .243 | .421 | .504 | .294 | .396 | .897 |
| SC-0.5 | Avg. | .179 | .362 | .449 | .237 | .344 | .887 |
| SC-0.65 | Avg. | .127 | .299 | .391 | .178 | .287 | .877 |
| SC-0.8 | Avg. | .070 | .224 | .311 | .122 | .225 | .863 |

### 5.2 Performance at Key Reduction Points

**At 20% content reduction (SC-0.2):**
- BLEU drop: 0.05 (from 0.347 to 0.295)
- ROUGE-1 drop: 0.03
- BERTScore: 0.902 (minimal loss from 0.909)
- Performance described as near-lossless

**At 35% reduction (SC-0.35):**
- BERTScore remains ~0.90
- ROUGE-1 exceeds 0.50
- "Impressive" results with moderate compression

**At 50% reduction (SC-0.5):**
- Average BLEU drops by 0.17
- Average ROUGE-1 drops by 0.12
- Performance "acceptable" for most use cases

**At 80% reduction (SC-0.8):**
- Significant degradation across all metrics
- BERTScore drops to 0.863
- BLEU drops to 0.070

### 5.3 Task-Specific Observations

Summarization and conversation tasks show greater robustness to content reduction than question-answering and reconstruction tasks. The authors note that "summarisation and conversation tasks focus on overall context understanding, whereas QA and reconstruction tasks require more fine-grained information."

### 5.4 Comparison with Random Filtering

Selective Context substantially outperforms random filtering at all reduction ratios:
- At 35% reduction: SC achieves ~0.55 ROUGE-1 vs significantly lower for random
- The gap widens at higher compression ratios, validating that self-information meaningfully identifies important content

---

## 6. Analysis

### 6.1 Strengths

1. **Simplicity**: No training required, uses off-the-shelf language model for scoring
2. **Flexibility**: Works at multiple granularities (token, phrase, sentence)
3. **Domain generality**: Effective across academic, news, and conversational text
4. **Moderate compression**: 20-50% reduction with minimal quality loss

### 6.2 Limitations

1. **No question awareness**: Filtering is context-only, ignoring what information the downstream task actually needs
2. **Independence assumption**: Each token's self-information is computed independently, ignoring inter-token dependencies in the filtering decision
3. **Limited compression ceiling**: Performance degrades significantly beyond 50% reduction
4. **Single-model scoring**: Uses GPT-2 Curie, which may not align with the target LLM's information needs

---

## 7. Conclusions

Selective Context demonstrates that "optimizing the use of context length by filtering out less informative content is possible without sacrificing performance," supported by testing across multiple domains and task types. The optimal reduction ratio appears to be between 20-50% depending on task requirements.

The method provides a simple but effective baseline for prompt compression that later work (LLMLingua, LongLLMLingua, LLMLingua-2) builds upon and significantly improves.

---

## Figures

**Figure 1:** Demonstration that LLMs can answer correctly even with less informative content deleted from the context, motivating the Selective Context approach.

**Figure 2:** Visualization of self-information-based content filtering applied to a paragraph, with token coloring indicating self-information values. High-information tokens (darker) are retained while low-information tokens (lighter) are filtered.

**Figure 3:** Performance comparison of Selective Context vs. random filtering baselines across reduction ratios, showing consistent superiority of information-based filtering.

**Figure 4:** Performance of Selective Context across different NLP tasks (summarization, QA, conversation, reconstruction), showing task-dependent sensitivity to reduction ratio.

**Figure 5:** Performance across different data sources (ArXiv, ShareGPT, BBC), showing domain-dependent variation.

**Figure 6:** Example of Selective Context applied to a conversation transcript at 50% reduction, showing which content is retained vs. filtered.

**Figure 7:** Example applied to BBC News article at 50% reduction.

---

## Key References

1. Shannon (1948). "A Mathematical Theory of Communication." Bell System Technical Journal.
2. Brown et al. (2020). "Language Models are Few-Shot Learners." NeurIPS 2020.
3. Vaswani et al. (2017). "Attention Is All You Need." NeurIPS 2017.
4. Lin (2004). "ROUGE: A Package for Automatic Evaluation of Summaries." ACL 2004.
5. Papineni et al. (2002). "BLEU: A Method for Automatic Evaluation of Machine Translation." ACL 2002.
6. Zhang et al. (2019). "BERTScore: Evaluating Text Generation with BERT."
7. Banerjee & Lavie (2005). "METEOR: An Automatic Metric for MT Evaluation."
8. Touvron et al. (2023). "LLaMA: Open and Efficient Foundation Language Models."
9. Bubeck et al. (2023). "Sparks of Artificial General Intelligence: Early Experiments with GPT-4."
10. Dong et al. (2023). "A Survey on Long Text Modeling with Transformers."
