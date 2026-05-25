# Evaluating Large Language Models Trained on Code

**Authors:** Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde de Oliveira Pinto, Jared Kaplan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, Alex Ray, Raul Puri, Gretchen Krueger, Michael Petrov, Heidy Khlaaf, Girish Sastry, Pamela Mishkin, Brooke Chan, Scott Gray, Nick Ryder, Mikhail Pavlov, Alethea Power, Lukasz Kaiser, Mohammad Bavarian, Clemens Winter, Philippe Tillet, Felipe Petroski Such, Dave Cummings, Matthias Plappert, Fotios Chantzis, Elizabeth Barnes, Ariel Herbert-Voss, William Hebgen Guss, Alex Nichol, Alex Paino, Nikolas Tezak, Jie Tang, Igor Babuschkin, Suchir Balaji, Shantanu Jain, William Saunders, Christopher Hesse, Andrew N. Carr, Jan Leike, Josh Achiam, Vedant Misra, Evan Morikawa, Alec Radford, Matthew Knight, Miles Brundage, Mira Murati, Katie Mayer, Peter Welinder, Bob McGrew, Dario Amodei, Sam McCandlish, Ilya Sutskever, Wojciech Zaremba

**Venue:** arXiv preprint, 2021

**arXiv:** [2107.03374](https://arxiv.org/abs/2107.03374)

---

## Abstract

This paper introduces Codex, a GPT model adapted for code, and evaluates its capability to synthesize Python programs from documentation. On the HumanEval benchmark, the model solved 28.8% of problems, significantly outperforming prior baselines. When using repeated sampling with 100 attempts per task, success rates reached 70.2%. The researchers also identify key limitations and discuss deployment considerations regarding safety and security.

---

## 1. Introduction

The paper presents Codex, a GPT language model fine-tuned on publicly available GitHub code. GPT-3 achieves approximately 0% on code generation tasks, whereas Codex-12B solves 28.8% of HumanEval problems with single samples.

---

## 2. Evaluation Framework

### Pass@k Metric

The paper introduces an unbiased estimator for pass@k evaluation, addressing limitations of match-based metrics like BLEU. The unbiased formula uses the probability of drawing k failed samples without replacement rather than naive approaches.

### HumanEval Dataset

- 164 hand-written Python programming problems
- Includes function signatures, docstrings, bodies, and unit tests
- Average 7.7 tests per problem
- Covers language comprehension, algorithms, and mathematics

### Sandbox Environment

Uses gVisor container runtime with eBPF-based firewalls to safely execute untrusted code during evaluation.

---

## 3. Training Methodology

### Data Collection

- 54 million public GitHub repositories (May 2020)
- 179 GB of unique Python files under 1 MB
- Final filtered dataset: 159 GB
- Removed auto-generated files, extreme line lengths, low alphanumeric content

### Fine-tuning Approach

- Started from GPT-3 model family
- 100 billion tokens training budget
- Adam optimizer with specific hyperparameters
- Modified tokenizer adding whitespace tokens (approximately 30% efficiency gain)
- Nucleus sampling with top p=0.95

### Scaling Laws

Test loss follows power law: (N/5.92 x 10^7)^(-0.13), where N = non-embedding parameters.

---

## 4. Results

### Comparative Performance

| Model | pass@1 | pass@100 |
|-------|--------|----------|
| GPT-Neo-2.7B | 6.41% | 21.37% |
| GPT-J-6B | 11.62% | 27.74% |
| TabNine | 2.58% | 7.59% |
| Codex-300M | 13.17% | 36.27% |
| Codex-12B | 28.81% | 72.31% |

### Supervised Fine-Tuning (Codex-S)

- Fine-tuned on correctly implemented standalone functions
- Two data sources: competitive programming (10,000 problems) and continuous integration (approximately 40,000 functions)
- Codex-S-12B achieves 37.7% on pass@1
- Average 6.5 percentage point gain on pass@1, 15.1 on pass@100

### Docstring Generation (Codex-D)

- Trained to generate docstrings from code (reverse task)
- Codex-D-12B achieves 20.3% pass@1, 46.5% pass@10

---

## 5. Model Limitations

1. **Training Inefficiency:** Requires hundreds of millions of lines of code despite modest performance
2. **Long Chain Operations:** Exponential performance degradation with chained operations (each step reduces success approximately 2--3x)
3. **Variable Binding:** Struggles binding operations to variables, especially with multiple variables and operations
4. **System-Level Synthesis:** Difficulty with complex, multi-step specifications

---

## 6. Broader Impacts and Hazard Analysis

### Seven Risk Categories

1. **Over-reliance** --- Novice programmers may trust superficially correct but incorrect suggestions
2. **Misalignment** --- Models generate training-distribution-similar code rather than user-intended code
3. **Bias and Representation** --- Generates harmful content reflecting training data biases
4. **Economic Impact** --- May reduce programming costs but engineers spend only partial time writing code
5. **Security** --- Can generate vulnerable code; enables polymorphic malware diversity
6. **Environmental** --- Significant compute requirements; training consumed hundreds of petaflop/s-days
7. **Legal** --- Training on public GitHub repositories considered fair use; rare exact training data matches (<0.1%)

---

## 7. APPS Dataset Results

- Codex-12B with 1-shot learning achieves 4.14% introductory, 0.14% interview, 0.02% competition difficulty
- Significant timeout issues on harder problems
- Filtered pass@1: 22.78% (introductory)

---

## 8. Figure Descriptions

- **Figure 1:** pass@k scaling curves showing log-linear improvement with more samples
- **Figure 2:** Scaling laws: test loss vs. model parameters following power-law relationship
- **Figure 3:** Chain-of-operation degradation showing exponential failure rates with task complexity

---

## Key References

1. Brown et al. (2020) --- GPT-3: Language Models are Few-Shot Learners
2. Vaswani et al. (2017) --- Attention is All You Need
3. Hendrycks et al. (2021) --- APPS: Measuring Coding Challenge Competence
4. Radford et al. (2019) --- Language Models are Unsupervised Multitask Learners (GPT-2)
5. Devlin et al. (2018) --- BERT: Pre-training of Deep Bidirectional Transformers
6. Kulal et al. (2019) --- SPoC: Search-based Pseudocode to Code
7. Feng et al. (2020) --- CodeBERT: Pre-trained Model for Code
8. Wang and Komatsuzaki (2021) --- GPT-J-6B
9. Lachaux et al. (2020) --- Unsupervised Translation of Programming Languages
10. Gao et al. (2020) --- The Pile: Large-Scale Diverse Text Dataset
