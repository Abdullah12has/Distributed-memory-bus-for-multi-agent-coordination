# GAIA: A Benchmark for General AI Assistants

**Authors:** Gregoire Mialon, Clementine Fourrier, Craig Swift, Thomas Wolf, Yann LeCun, Thomas Scialom

**Venue:** arXiv preprint, 2023

**arXiv:** [2311.12983](https://arxiv.org/abs/2311.12983)

---

## Abstract

GAIA is a benchmark designed to evaluate AI systems on real-world questions requiring reasoning, multi-modality handling, web browsing, and generally tool-use proficiency. The benchmark comprises 466 questions that are conceptually simple for humans but challenging for current AI systems. Human respondents achieved 92% accuracy while GPT-4 with plugins reached only 15%, highlighting a significant performance gap. The authors argue that AGI advancement depends on systems demonstrating robustness comparable to average human performance on such tasks.

---

## 1. Introduction

GAIA challenges the trend of making benchmarks "harder for humans" by focusing instead on "easy for humans, hard for AI" tasks that require robust execution. Successfully solving GAIA would represent competence in what the authors term "t-AGI" (time-bounded AGI)---beating expert humans on most tasks when given comparable time.

### Four Design Pillars

1. **Real-world challenging questions** requiring reasoning, multi-modality, web browsing, and tool use
2. **Easy interpretability** through conceptually simple tasks with clear reasoning traces
3. **Non-gameability** --- answers not easily found in plain text; cannot be brute-forced
4. **Simplicity of use** --- factoid, concise, unambiguous answers enabling automatic evaluation

---

## 2. Benchmark Design

### Three Difficulty Levels

| Level | Characteristics | Typical Steps |
|-------|-----------------|---------------|
| 1 | No tools or single tool | <=5 steps |
| 2 | Multiple tools combined | 5--10 steps |
| 3 | Complex sequences, arbitrary actions | >10 steps |

### Required Capabilities

Questions demand proficiency in:
- **Web browsing** (primary capability)
- **Multi-modality** (images, videos, audio)
- **Coding/Computation** (executing scripts, calculations)
- **Diverse filetype reading** (PDFs, Excel, spreadsheets)
- **Reasoning** (complex multi-step logic)

### Dataset Composition

- **Total questions:** 466
- **Released for public:** 166 annotated (development set)
- **Leaderboard set:** 300 without answers
- **File types:** Images, PDFs, Excel files, spreadsheets, audio files

---

## 3. Annotation and Validation

### Annotation Process

1. Question creation by authors and compensated annotators based on sources of truth
2. Independent validation by two new annotators per question
3. 68% of questions valid without modification; 32% required repairs or removal
4. Approximately 2 hours per question (including validation and repairs)

| Metric | Percentage |
|--------|-----------|
| Both validators agree with creator | 55% |
| One agrees, one disagrees | 27% |
| Both disagree | 18% |
| Valid questions (final) | 68% |
| Human success rate | 92% |

### Scoring Approach

- Automatic evaluation via quasi-exact match with ground truth (normalized)
- Required format: numbers, few words, or comma-separated lists

---

## 4. Results

### Performance by Level

| Method | Level 1 | Level 2 | Level 3 |
|--------|---------|---------|---------|
| Human Annotators | 93.9% | 91.8% | 87.3% |
| GPT-4 + plugins | 30.3% | 9.7% | 0% |
| GPT-4 Turbo | 13.0% | 5.5% | 0% |
| GPT-4 baseline | 9.1% | 2.6% | 0% |
| AutoGPT (GPT-4) | 14.4% | 0.4% | 0% |
| Web search baseline | 7.4% | 0% | 0% |

### Time to Answer (Minutes)

- Human: 6--17 minutes depending on difficulty
- GPT-4 + plugins: 0.65--0.53 minutes (faster but less accurate)
- AutoGPT: 7.6--11.7 minutes

---

## 5. Key Findings

- GPT-4 performs better with plugin access, demonstrating the value of tool augmentation
- Models struggle most with Level 3 questions requiring complex action sequences
- Web browsing capability significantly improves performance
- AutoGPT shows unexpected underperformance despite automatic tool selection
- Memorization of pre-training data accounts for some successes on web browsing tasks

---

## 6. Limitations

1. Does not evaluate reasoning traces or multiple valid paths to answers
2. All questions in English only
3. Lacks dialectal variation and non-English web content evaluation
4. Subject to data contamination over time; requires periodic updates
5. Two-round validation creates fixed overhead but ensures quality

---

## 7. Sample Questions

**Level 1:** "What was the actual enrollment count of the clinical trial on H. pylori in acne vulgaris patients from Jan-May 2018 as listed on the NIH website?" (Answer: 90)

**Level 2:** "If this whole pint is made up of ice cream, how many percent above or below the US federal standards for butterfat content is it when using 2020 Wikipedia standards?" (Answer: +4.6)

**Level 3:** "In NASA's Astronomy Picture of the Day on 2006 January 21, which astronaut from the smaller astronaut's NASA Group spent least time in space, and how many minutes?" (Answer: White; 5876)

---

## 8. Figure Descriptions

- **Figure 1:** Overview of GAIA benchmark design showing the four pillars and difficulty level distribution
- **Figure 2:** Capability coverage heatmap showing which questions require web browsing, multi-modality, coding, etc.
- **Figure 3:** Performance comparison across models and difficulty levels, illustrating the human-AI gap

---

## Key References

1. OpenAI (2023) --- GPT-4 Technical Report
2. Anthropic (2023) --- Claude Model Card and Evaluations
3. Hendrycks et al. (2021) --- MMLU benchmark
4. Cobbe et al. (2021) --- GSM8k benchmark
5. Chollet (2019) --- On the Measure of Intelligence
6. Brown et al. (2020) --- GPT-3 few-shot learning capabilities
7. Kiela et al. (2023) --- Plotting Progress in AI
8. Zheng et al. (2023) --- LLM-as-judge evaluation approaches
9. Liang et al. (2022) --- Holistic Evaluation of Language Models
10. Mialon et al. (2023) --- Augmented Language Models Survey
