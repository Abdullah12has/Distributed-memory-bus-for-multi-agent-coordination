# Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models (BIG-bench)

**Authors:** Aarohi Srivastava, Abhinav Rastogi, Abhishek Rao, and 450+ authors across 132 institutions

**Venue:** Transactions on Machine Learning Research (TMLR), 2022

**arXiv:** [2206.04615](https://arxiv.org/abs/2206.04615)

---

## Abstract

The paper introduces BIG-bench, a benchmark consisting of 204 diverse tasks designed to evaluate language model capabilities. The benchmark spans linguistics, childhood development, math, common-sense reasoning, biology, physics, social bias, software development, and beyond. The authors evaluated several model classes across scales from millions to billions of parameters, finding that model performance and calibration both improve with scale, but are poor in absolute terms.

---

## 1. Introduction

The paper argues that larger language models demonstrate qualitatively new behaviors including code generation, chess playing, and medical diagnosis capabilities. Current benchmarks suffer from limited scope, short lifespans (SuperGLUE achieved superhuman performance within 18 months), and reliance on non-expert labeling.

---

## 2. BIG-bench Structure

### Components

- 204+ diverse tasks from 450 authors across 132 institutions
- Topics span linguistics, math, biology, physics, social bias, software development
- Approximately 80% JSON tasks (specification-based evaluation)
- Approximately 20% programmatic tasks (multi-round interactions)
- BIG-bench Lite: curated 24-task subset for lightweight evaluation

### Task Categories (by keyword frequency)

- Knowledge-based reasoning
- Code understanding and generation
- Common-sense reasoning
- Logical deduction
- Social bias detection
- Non-English language tasks

---

## 3. Models Evaluated

- **BIG-G (Google):** 13 dense decoder-only Transformers trained on 2.8 trillion BPE tokens
- **BIG-G Sparse:** Switch Transformer variants with top-2 routing across 32 experts
- **GPT Series:** 8 OpenAI models (125M to 175B parameters)
- **PaLM:** Pathways Language Model results included

---

## 4. Core Findings

### 4.1 Aggregate Performance

- Model performance improves predictably with scale but remains poorly in absolute terms
- Best models achieved normalized scores below 20 (where 100 indicates excellence)
- Human expert baseline substantially outperforms all models
- Performance gains from few-shot prompting are consistent

### 4.2 Calibration

- Brier scores and expected calibration error (ECE) both improve with scale
- Sparse models demonstrate approximately 10x better calibration efficiency than dense models
- All models remain poorly calibrated in absolute terms (ECE: 0.25--0.45)

### 4.3 Model Class Similarities

- Dense and sparse models show similar cross-entropy scaling
- GPT and BIG-G perform comparably
- Sparse models achieve approximately 2x inference cost reduction for equivalent performance

### 4.4 Scaling Behaviors: Linearity and Breakthroughness

**Linearity (L):** Tasks showing predictable improvement with scale
- Correlates with knowledge-heavy, memorization-based tasks
- Example: trivia answering, linguistic mappings

**Breakthroughness (B):** Tasks showing sudden capability emergence
- Approximately 5% of BIG-bench tasks exhibit this pattern
- Correlates with composite tasks requiring multiple steps
- Often an artifact of evaluation metrics (exact string match vs. BLEU/ROUGE)

### 4.5 Brittleness and Sensitivity

- Multiple-choice performance improves when answer options are excluded from inputs
- Models perform at chance when explicitly asked to identify causality, but achieve strong performance with alternative formulations
- Formatting sensitivity persists even in few-shot settings

### 4.6 Social Bias Results

**Finding 1:** Bias increases with scale in ambiguous contexts. At 128B parameters, white boys rated 22x more likely to become good doctors than Native American girls.

**Finding 2:** Bias decreases with scale in unambiguous contexts. Larger models better leverage disambiguating evidence.

**Finding 3:** Few-shot prompts indicating neutral responses reduce bias significantly.

### 4.7 Non-English Performance

- Performance on non-English tasks substantially worse than English equivalents
- Inconsistent scaling improvements across languages
- Parallel tasks show divergent scaling trajectories

---

## 5. Methodology Details

### Evaluation Protocol

- Zero-shot and few-shot evaluation (primarily greedy sampling at temperature=0)
- Temperature=1 sampling consistently underperformed
- Normalized preferred metrics: (raw score - low) / (high - low) x 100
- Human expert raters used internet search and all available resources

### Data Leakage Prevention

- Canary string embedded in all tasks
- Training data collected before BIG-bench repository creation
- Indirect leakage possible through internet text

---

## 6. Selected Task Analysis

**Checkmate-in-One Chess Task:** Shows breakthrough behavior in exact match metric but smoother improvement when decomposed into legal moves and valid mates.

**Periodic Elements Task:** Multiple-choice format shows sudden accuracy jump at 10^10 parameters. Log-probability analysis reveals smooth divergence preceding this threshold.

**Emoji Movie Task:** Exact string match exhibits breakthroughs; multiple-choice metric shows gradual improvement. Manual inspection reveals intermediate stages.

---

## 7. Limitations

1. Different task formulations yield qualitatively different scaling patterns
2. Breakthrough behavior often reflects metric artifacts rather than genuinely discontinuous capability emergence
3. Task difficulty depends heavily on implementation details beyond core task design

---

## 8. Figure Descriptions

- **Figure 1:** Aggregate performance scaling curves across model families
- **Figure 2:** Linearity vs. breakthroughness classification of all 204 tasks
- **Figure 3:** Social bias scaling with model size in ambiguous vs. unambiguous contexts
- **Figure 4:** Calibration improvement with scale across model families

---

## Key References

1. Brown et al. (2020) --- GPT-3 paper
2. Vaswani et al. (2017) --- Transformer architecture
3. Kaplan et al. (2020) --- Scaling laws for language models
4. Bommasani et al. (2021) --- Opportunities and risks of foundation models
5. Hendrycks et al. (2021) --- Code generation capabilities
6. Fedus et al. (2021) --- Switch Transformers sparse models
7. Zhang et al. (2020) --- Qualitative behaviors at scale
8. Wang et al. (2019) --- SuperGLUE benchmark
9. Thoppilan et al. (2022) --- LaMDA architecture and training
10. Hoffmann et al. (2022) --- Chinchilla optimal scaling laws
