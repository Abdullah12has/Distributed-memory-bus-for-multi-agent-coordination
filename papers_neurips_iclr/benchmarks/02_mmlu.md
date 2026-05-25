# Measuring Massive Multitask Language Understanding

**Authors:** Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, Jacob Steinhardt

**Venue:** ICLR 2021

**arXiv:** [2009.03300](https://arxiv.org/abs/2009.03300)

---

## Abstract

This paper presents a comprehensive evaluation benchmark covering 57 academic and professional tasks spanning elementary mathematics, US history, computer science, law, and more. The authors discover that while most models perform near chance level, GPT-3's largest variant surpasses random accuracy by almost 20 percentage points. However, all models require substantial improvements before they can reach expert-level accuracy. The work reveals that models struggle with socially important subjects and often lack awareness of their own errors.

---

## 1. Introduction

The paper addresses a gap between language model pretraining on diverse internet content and existing benchmarks that achieve near-human performance. Previous benchmarks (GLUE, SuperGLUE) became saturated quickly. This work proposes evaluation in zero-shot and few-shot settings without fine-tuning, better reflecting how models acquire knowledge during pretraining.

**Main Finding:** Few-shot models up to 13 billion parameters achieve random chance performance of 25%, but the 175 billion parameter GPT-3 model reaches 43.9% accuracy.

---

## 2. Benchmark Design

### Dataset Composition

- **Total Questions:** 15,908 across 57 tasks
- **Few-shot Dev Set:** 5 questions per subject
- **Validation Set:** 1,540 questions
- **Test Set:** 14,079 questions
- **Minimum Examples per Task:** 100

### Subject Categories

**Humanities:** Law, Philosophy, History, Ethics and Moral Reasoning

**Social Sciences:** Economics, Psychology, Sociology, Politics, Geography, International Relations

**STEM:** Physics, Chemistry, Mathematics (elementary to college), Computer Science, Engineering

**Other:** Professional Medicine, Business, Finance, Accounting, Global Facts

### Human Performance Baseline

- Unspecialized humans (Amazon Mechanical Turk): 34.5% accuracy
- Expert-level accuracy: approximately 89.8%

---

## 3. Experiments and Results

### Model Performance

| Model | Humanities | Social Science | STEM | Other | Average |
|-------|-----------|-----------------|------|-------|---------|
| Random Baseline | 25.0 | 25.0 | 25.0 | 25.0 | 25.0 |
| RoBERTa | 27.9 | 28.8 | 27.0 | 27.7 | 27.9 |
| ALBERT | 27.2 | 25.7 | 27.7 | 27.9 | 27.1 |
| GPT-2 | 32.8 | 33.3 | 30.2 | 33.1 | 32.4 |
| UnifiedQA | 45.6 | 56.6 | 40.2 | 54.6 | 48.9 |
| GPT-3 Small (few-shot) | 24.4 | 30.9 | 26.0 | 24.1 | 25.9 |
| GPT-3 Medium (few-shot) | 26.1 | 21.6 | 25.6 | 25.5 | 24.9 |
| GPT-3 Large (few-shot) | 27.1 | 25.6 | 24.3 | 26.5 | 26.0 |
| GPT-3 X-Large (few-shot) | 40.8 | 50.4 | 36.7 | 48.8 | 43.9 |

---

## 4. Key Findings

1. **Emergent Ability with Scale:** Only the 175B parameter GPT-3 substantially exceeds random chance; smaller models perform at or near baseline levels.

2. **Lopsided Performance:** GPT-3's accuracy ranges from 69% for US Foreign Policy to 26% for College Chemistry, lacking mastery in any single subject.

3. **Calculation Weakness:** 9 out of the 10 lowest-accuracy tasks are STEM subjects that emphasize mathematics or calculations, suggesting models acquire declarative knowledge more readily than procedural knowledge.

4. **Unusual Learning Pattern:** GPT-3 does better on College Medicine (47.4%) and College Mathematics (35.0%) than calculation-heavy Elementary Mathematics (29.9%), diverging from typical human learning progression.

5. **Calibration Problems:** GPT-3's average confidence can be off from actual accuracy by up to 24 percentage points, indicating poor calibration, particularly in zero-shot settings.

6. **Value-Related Gaps:** Poor performance on morality and law tasks raises concerns about alignment with human values.

---

## 5. Procedural vs. Declarative Knowledge

The paper demonstrates that while GPT-3 knows about PEMDAS (order of operations), it frequently fails to apply it correctly to actual mathematical problems. Attempts to improve Professional Law performance through domain-specific pretraining on 1.6 million legal case summaries yielded only modest gains (36.1% accuracy vs baseline performance).

---

## 6. Methodology Innovation

The paper proposes assessing models "more like how humans learn"---through reading diverse texts rather than training exclusively on task-specific datasets. This methodology encourages models to develop broader knowledge acquisition during pretraining.

---

## 7. Figure Descriptions

- **Figure 1:** Subject-level accuracy heatmap for GPT-3, showing variation from 26% (College Chemistry) to 69% (US Foreign Policy)
- **Figure 2:** Scaling curves showing the emergence of non-random performance only at the 175B parameter scale
- **Figure 3:** Calibration plots comparing model confidence vs. actual accuracy

---

## Key References

1. Brown et al. (2020) --- GPT-3 paper
2. Wang et al. (2018) --- GLUE benchmark
3. Wang et al. (2019) --- SuperGLUE benchmark
4. Raffel et al. (2019) --- T5 model
5. Devlin et al. (2019) --- BERT
6. Petroni et al. (2019) --- Language models as knowledge bases
7. Geirhos et al. (2020) --- Shortcut learning in neural networks
8. Zellers et al. (2019) --- HellaSwag benchmark
9. Khashabi et al. (2020) --- UnifiedQA
10. Kaplan et al. (2020) --- Scaling laws for language models
