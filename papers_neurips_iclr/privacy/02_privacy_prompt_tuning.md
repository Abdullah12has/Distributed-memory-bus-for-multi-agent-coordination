# Privacy-Preserving In-Context Learning for Large Language Models (DP-ICL)

**Authors:** Tong Wu, Ashwinee Panda, Jiachen T. Wang, Prateek Mittal

**Venue:** arXiv preprint (cs.LG, cs.AI, cs.CR), 2023

**arXiv:** [https://arxiv.org/abs/2305.01639](https://arxiv.org/abs/2305.01639)

---

## Abstract

In-context learning (ICL) is an important capability of Large Language Models (LLMs), enabling these models to dynamically adapt based on specific, in-context exemplars, thereby improving accuracy and relevance. However, LLM's responses may leak the sensitive private information contained in in-context exemplars. To address this challenge, the authors propose Differentially Private In-context Learning (DP-ICL), a general paradigm for privatizing ICL tasks. The key idea is generating differentially private responses through a noisy consensus among an ensemble of LLM's responses based on disjoint exemplar sets. The authors instantiate several techniques for text classification and language generation, demonstrating a strong utility-privacy tradeoff across benchmarks.

---

## 1. Introduction

### 1.1 The Privacy Risk in ICL

In-context learning relies on providing examples (exemplars) in the prompt to guide LLM behavior. These exemplars may contain:
- Personal information from real users
- Proprietary business data
- Medical records, financial information
- Any sensitive content used as demonstrations

The LLM's response can inadvertently memorize and leak these exemplars, especially when:
- The model directly quotes or paraphrases exemplars
- Pattern matching reveals exemplar structure
- Membership inference attacks detect exemplar presence

### 1.2 Differential Privacy for ICL

The authors propose DP-ICL, which provides formal privacy guarantees through the framework of differential privacy. The core mechanism ensures that changing any single exemplar has bounded influence on the model's output distribution.

## 2. Method: DP-ICL

### 2.1 General Paradigm

**Step 1: Partition exemplars into disjoint subsets**
- Divide the private exemplar pool into K non-overlapping groups
- Each group forms an independent ICL prompt

**Step 2: Generate ensemble responses**
- Query the LLM with each group's prompt independently
- Collect K candidate responses

**Step 3: Noisy consensus**
- Aggregate responses through a differentially private mechanism
- Add calibrated noise to the aggregation process
- Output the privatized response

### 2.2 Text Classification Instantiation

For classification tasks (e.g., sentiment analysis):
- Each exemplar subset produces a label prediction
- Labels are aggregated via noisy majority voting
- The Report Noisy Max mechanism selects the private output
- Privacy cost: epsilon per query, composing across queries

### 2.3 Language Generation Instantiation

For generation tasks (e.g., summarization, QA):
- Each exemplar subset produces a text response
- Token-level aggregation with noise injection
- More complex due to the open-ended output space
- Uses techniques from private text generation literature

## 3. Privacy Analysis

### 3.1 Differential Privacy Guarantees

DP-ICL satisfies (epsilon, delta)-differential privacy where:
- epsilon controls the privacy budget (lower = more private)
- delta is the probability of privacy failure
- Privacy composes across multiple queries

### 3.2 Key Properties

- **Group privacy:** Changing any single exemplar has bounded effect
- **Post-processing invariance:** Any function of the private output remains private
- **Composability:** Multiple DP-ICL queries compose gracefully

### 3.3 Privacy-Utility Tradeoff

As privacy budget (epsilon) decreases:
- Privacy protection increases
- Utility (accuracy) decreases
- The tradeoff is controlled by the number of exemplar subsets K

## 4. Experimental Results

### 4.1 Text Classification

**Benchmarks:** SST-2, AGNews, TREC, DBpedia

| Method | SST-2 Acc. | AGNews Acc. | Privacy (epsilon) |
|---|---|---|---|
| Non-private ICL | ~94% | ~85% | Infinity |
| DP-ICL (epsilon=1) | ~88% | ~78% | 1.0 |
| DP-ICL (epsilon=0.1) | ~82% | ~72% | 0.1 |
| Zero-shot (no exemplars) | ~80% | ~70% | 0 |

### 4.2 Language Generation

Evaluated on summarization and QA tasks:
- DP-ICL maintains reasonable generation quality
- ROUGE/BLEU scores degrade gracefully with tighter privacy budgets
- Output diversity increases with noise (sometimes beneficial)

### 4.3 Key Findings

- **Strong baseline:** Even with tight privacy budgets, DP-ICL outperforms zero-shot
- **Model size matters:** Larger models achieve better utility at the same privacy level
- **K sensitivity:** More subsets improve privacy but reduce per-subset exemplar quality
- **Task difficulty:** Simple tasks (binary classification) tolerate more noise than complex generation

## 5. Analysis

### 5.1 Comparison with Alternatives

| Approach | Privacy Guarantee | Utility | Applicability |
|---|---|---|---|
| No protection | None | Best | Universal |
| Data anonymization | Heuristic | Good | Limited |
| DP fine-tuning (DP-SGD) | Formal | Moderate | Requires training |
| DP-ICL | Formal | Good | Training-free |

DP-ICL's key advantage: provides formal privacy guarantees without requiring model fine-tuning, making it applicable to API-only LLMs.

### 5.2 Limitations

- Requires multiple LLM queries per output (cost scales with K)
- Language generation privacy is harder to guarantee than classification
- Privacy budget must be managed across an interaction session
- Assumes exemplars can be meaningfully partitioned

## 6. Related Work

- **Differential privacy:** Foundational framework (Dwork et al., 2006)
- **DP-SGD:** Private training (Abadi et al., 2016) -- requires gradient access
- **Private prediction:** PATE (Papernot et al., 2018) -- teacher ensemble approach
- **LLM privacy:** Training data extraction attacks (Carlini et al., 2021)
- **In-context learning:** ICL theory and practice (Brown et al., 2020)

DP-ICL bridges the gap between formal privacy and practical ICL by adapting ensemble-based private prediction to the in-context learning setting.

## 7. Conclusion

DP-ICL demonstrates that differential privacy can be practically applied to in-context learning, providing formal privacy guarantees while maintaining strong utility. The approach is training-free, applicable to API-only models, and achieves favorable privacy-utility tradeoffs across both classification and generation tasks.

---

## Key Figures

- **Figure 1:** DP-ICL framework overview showing exemplar partitioning, ensemble querying, and noisy aggregation.
- **Figure 2:** Privacy-utility curves across different epsilon values and tasks.
- **Figure 3:** Effect of number of subsets K on privacy and accuracy.
- **Figure 4:** Comparison with non-private ICL and zero-shot baselines.

---

## Top References

1. Dwork et al. (2006). Calibrating Noise to Sensitivity in Private Data Analysis. TCC.
2. Brown et al. (2020). Language Models are Few-Shot Learners. NeurIPS.
3. Abadi et al. (2016). Deep Learning with Differential Privacy. CCS.
4. Papernot et al. (2018). Scalable Private Learning with PATE. ICLR.
5. Carlini et al. (2021). Extracting Training Data from Large Language Models. USENIX Security.
6. Dwork & Roth (2014). The Algorithmic Foundations of Differential Privacy.
7. Li et al. (2022). Large Language Models Can Be Strong Differentially Private Learners. ICLR.
8. Yu et al. (2022). Differentially Private Fine-tuning of Language Models. ICLR.
9. Tang et al. (2023). Privacy-Preserving In-Context Learning with Differentially Private Few-Shot Generation.
10. Min et al. (2022). Rethinking the Role of Demonstrations in In-Context Learning. EMNLP.
