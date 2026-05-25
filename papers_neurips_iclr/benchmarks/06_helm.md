# Holistic Evaluation of Language Models (HELM)

**Authors:** Percy Liang, Rishi Bommasani, Tony Lee, Dimitris Tsipras, Dilara Soylu, Michihiro Yasunaga, Yian Zhang, Deepak Narayanan, Yuhuai Wu, Ananya Kumar, Benjamin Newman, Binhang Yuan, Bobby Yan, Ce Zhang, Christian Cosgrove, Christopher D. Manning, Christopher Re, Diana Acosta-Navas, Drew A. Hudson, Eric Zelikman, Esin Durmus, Faisal Ladhak, Frieda Rong, Hongyu Ren, Huaxiu Yao, Jue Wang, Keshav Santhanam, Laurel Orr, Lucia Zheng, Mert Yuksekgonul, Mirac Suzgun, Nathan Kim, Neel Guha, Niladri Chatterji, Omar Khattab, Peter Henderson, Qian Huang, Ryan Chi, Sang Michael Xie, Shibani Santurkar, Surya Ganguli, Tatsunori Hashimoto, Thomas Icard, Tianyi Zhang, Vishrav Chaudhary, William Wang, Xuechen Li, Yifan Mai, Yuhui Zhang, Yuta Koreeda

**Venue:** Transactions on Machine Learning Research (TMLR), 2023

**arXiv:** [2211.09110](https://arxiv.org/abs/2211.09110)

---

## Abstract

HELM is a comprehensive evaluation framework designed to enhance clarity regarding language model capabilities and limitations. The work evaluates 30 prominent language models across 42 scenarios using seven performance dimensions: accuracy, calibration, robustness, fairness, bias, toxicity, and efficiency. The authors significantly improved coverage in standardized benchmarking, with nearly all evaluated models assessed on identical scenarios and metrics.

---

## 1. Introduction

HELM provides the first large-scale, multi-dimensional evaluation of language models under standardized conditions. The framework produces 4,939 evaluation runs across 30 models and 42 scenarios.

### Three Elements of Holistic Evaluation

1. **Broad Coverage with Acknowledged Incompleteness** --- Taxonomizes scenarios and metrics while explicitly identifying what is missing
2. **Multi-Metric Measurement** --- Evaluates accuracy, calibration, robustness, fairness, bias, toxicity, and efficiency across all scenarios
3. **Standardization** --- All 30 models evaluated under identical conditions (5-shot prompting)

---

## 2. Scenario Architecture

Scenarios are decomposed into three components:
- **Task:** question answering, information retrieval, summarization, sentiment analysis, toxicity detection, text classification
- **Domain:** genre, time period, demographic groups
- **Language:** English varieties (including African American English and international variants)

### 16 Core Scenarios

- **Question Answering (9):** BoolQ, NewsQA, NarrativeQA, NaturalQuestions, QuAC, HellaSwag, OpenBookQA, TruthfulQA, MMLU
- **Information Retrieval (2):** MS MARCO regular and TREC tracks
- **Summarization (2):** CNN/DailyMail, XSUM
- **Sentiment Analysis (1):** IMDB
- **Toxicity Detection (1):** CivilComments
- **Text Classification (1):** RAFT

### 7 Targeted Evaluations (26 Scenarios)

- Language modeling and linguistic understanding
- Knowledge-intensive tasks
- Reasoning capabilities
- Memorization/copyright concerns
- Disinformation generation
- Social bias assessment
- Toxicity generation

---

## 3. Models Evaluated (30 Total)

**Organizations:** AI21 Labs, Anthropic, BigScience, Cohere, EleutherAI, Google, Meta, Microsoft/NVIDIA, OpenAI, Tsinghua, Yandex

**Scale Range:** 6B to 530B parameters

**Accessibility Distribution:**
- Open (10): GPT-NeoX, OPT, BLOOM, GLM, GPT-J, YaLM
- Limited-access (17): text-davinci-002, davinci (175B), others
- Closed (3): Anthropic-LM, TNLG v2, others

---

## 4. Key Metrics

| Metric Category | Description |
|---|---|
| Accuracy | Task-specific correctness measures |
| Calibration | Alignment between confidence and correctness (ECE) |
| Robustness | Performance under input perturbations (typos, formatting) |
| Fairness | Worst-case accuracy across demographic groups |
| Bias | Stereotypes in model generations |
| Toxicity | Harmful content generation |
| Efficiency | Training and inference cost metrics |

---

## 5. Major Empirical Findings

1. **Instruction-Tuning Advantage:** text-davinci-002 and Anthropic-LM v4-s3 demonstrate superior performance across accuracy, robustness, and fairness despite the latter being 10x smaller.

2. **Access-Performance Gap:** Consistent gap on all core scenarios between current open models and non-open models, though the gap has narrowed with recent releases.

3. **Calibration Variability:** Accuracy-calibration relationships are scenario-dependent; improving accuracy sometimes worsens calibration.

4. **Demographic Performance Disparities:** OPT (175B) accuracy degrades from 1.506 bits per byte for White English to 2.114 bits per byte for African American English.

5. **Robustness Vulnerabilities:** TNLG v2 (530B) drops from 72.6% standard accuracy to 38.9% under robustness perturbations on NarrativeQA.

6. **Low Toxicity on Core Tasks:** Biases and toxicity in model generations are largely constant across models and low overall for core scenarios.

7. **No Accuracy-Efficiency Trade-off:** Across 30 models, no strong inverse relationship observed.

8. **Knowledge-Intensive Task Leaders:** text-davinci-002 demonstrates a 62.0% TruthfulQA accuracy compared to second place at 36.2%.

9. **Code Models Excel at Reasoning:** code-davinci-002 achieves 52.1% on GSM8K vs. 35.0% for next-best text model.

10. **Copyright Memorization:** Regurgitation risk clearly correlates with model accuracy.

11. **Prompt Sensitivity:** All models show significant sensitivity to formatting, choice, and number of in-context examples.

12. **Multiple-Choice Format Sensitivity:** OPT (175B) on HellaSwag: 79.1% with separate presentation vs. 30.2% with joint presentation.

13. **Scale Threshold Effect:** All models winning head-to-head comparisons are at least 50B parameters.

14. **Perplexity-Performance Disconnect:** BPB on The Pile is a poor predictor of downstream accuracy.

---

## 6. Resource Utilization

- **Total Evaluation Runs:** 4,939
- **Token Cost:** 12.2 billion tokens
- **API Spending:** $38,001
- **Compute:** approximately 19,500 GPU hours

---

## 7. Missing Coverage (Explicitly Acknowledged)

**Scenarios:** All non-English languages; machine translation, dialogue, multimodal tasks; clinical/medical domains

**Metrics:** Comprehensive fairness operationalizations; long-horizon evaluation; user satisfaction; privacy and security

**Models:** PaLM, Gopher, and other major closed models

---

## 8. Figure Descriptions

- **Figure 1:** Taxonomy of scenarios and metrics in the HELM framework
- **Figure 2:** Model comparison dashboard showing multi-metric performance across all 42 scenarios
- **Figure 3:** Accuracy vs. robustness scatter plots across models
- **Figure 4:** Demographic performance disparities visualization

---

## Key References

1. Bommasani et al. (2021) --- Foundation Models report
2. Brown et al. (2020) --- GPT-3; pioneered few-shot prompting paradigm
3. Devlin et al. (2019) --- BERT; foundational pre-trained language model
4. Wang et al. (2019a,b) --- GLUE/SuperGLUE; prior benchmarking approaches
5. Srivastava et al. (2022) --- BIG-Bench; large-scale evaluation effort
6. Gao et al. (2021) --- EleutherAI LM Harness; evaluation infrastructure
7. Ouyang et al. (2022) --- Instruction-following models
8. Lin et al. (2021) --- Neural IR survey
9. Zhang et al. (2022) --- BERTScore; evaluation metric
10. Wei et al. (2022) --- Chain-of-thought prompting
