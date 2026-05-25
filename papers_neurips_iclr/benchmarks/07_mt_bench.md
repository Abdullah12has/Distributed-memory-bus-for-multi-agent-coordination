# Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena

**Authors:** Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu, Yonghao Zhuang, Zi Lin, Zhuohan Li, Dacheng Li, Eric P. Xing, Hao Zhang, Joseph E. Gonzalez, Ion Stoica

**Venue:** NeurIPS 2023 (Datasets and Benchmarks Track)

**arXiv:** [2306.05685](https://arxiv.org/abs/2306.05685)

---

## Abstract

The authors investigate using advanced LLMs as evaluators for chat-based AI assistants. They identify biases in this approach and propose mitigation strategies. Using two new benchmarks---MT-bench and Chatbot Arena---they demonstrate that strong LLM judges like GPT-4 can match both controlled and crowdsourced human preferences well, achieving over 80% agreement.

---

## 1. Introduction

Open-ended question evaluation is costly and slow with human judges. This paper systematically evaluates using strong LLMs (particularly GPT-4) as judges for assessing other language models' performance on open-ended tasks.

---

## 2. Key Components

### MT-Bench Dataset

- 80 high-quality multi-turn questions across 8 categories
- Categories: writing, roleplay, extraction, reasoning, math, coding, STEM knowledge, humanities
- Designed to test conversational ability and instruction-following

### Chatbot Arena

- Crowdsourced platform with anonymous model battles
- 30K+ collected votes from diverse users
- Real-world unrestricted use cases

### LLM-as-Judge Methods

Three implementation variations:
- **Pairwise comparison:** two answers, determine better
- **Single answer grading:** absolute scoring
- **Reference-guided grading:** providing model's own solution

---

## 3. Identified Biases and Limitations

| Limitation | Finding |
|-----------|---------|
| Position bias | LLM judges favor certain positions (Claude-v1: 75% toward first) |
| Verbosity bias | Judges favor longer responses even if lower quality |
| Self-enhancement bias | Models show modest preference for their own outputs |
| Math/reasoning failure | Limited capability grading complex problems |

---

## 4. Results

### Agreement Rates

GPT-4 achieves 85% agreement with human experts (second turn), matching human-human agreement at 81%. Agreement increases from 70% to nearly 100% as performance disparity widens between models.

### Proposed Solutions

1. **Position bias:** Swap positions twice; declare tie if inconsistent
2. **Math problems:** Chain-of-thought prompting; reference-guided method (reduced failure from 70% to 15%)
3. **Few-shot examples:** Improved consistency from 65% to 77.5% for GPT-4
4. **Fine-tuned open models:** Vicuna-13B fine-tuned on arena data achieves 85.5% agreement

### Complementary Benchmarking

Traditional benchmarks (MMLU, TruthfulQA) and preference-based MT-Bench measure different aspects---comprehensive evaluation requires both.

---

## 5. Figure Descriptions

- **Figure 1:** Overview of the LLM-as-Judge framework comparing pairwise and single-answer approaches
- **Figure 2:** Position bias analysis across different judge models
- **Figure 3:** Agreement rates between LLM judges and human evaluators by model pair difficulty
- **Figure 4:** Chatbot Arena Elo ratings compared with MT-Bench scores

---

## Key References

1. Wei et al. (2023) --- GPT-4 Technical Report
2. Ouyang et al. (2022) --- RLHF for alignment
3. Touvron et al. (2023) --- LLaMA models
4. Hendrycks et al. (2019) --- MMLU benchmark
5. Cobbe et al. (2021) --- GSM-8K math benchmark
6. Wei et al. (2023) --- Chain-of-thought prompting
7. Liang et al. (2022) --- HELM evaluation framework
8. Lin (2004) --- ROUGE metric
9. Papineni et al. (2002) --- BLEU metric
10. Brown et al. (1986) --- Self-enhancement bias (psychology foundation)
