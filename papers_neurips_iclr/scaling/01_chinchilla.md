# Training Compute-Optimal Large Language Models (Chinchilla)

**Authors:** Jordan Hoffmann, Sebastian Borgeaud, Arthur Mensch, Elena Buchatskaya, Trevor Cai, Eliza Rutherford, Diego de Las Casas, Lisa Anne Hendricks, Johannes Welbl, Aidan Clark, Tom Hennigan, Eric Noland, Katie Millican, George van den Driessche, Bogdan Damoc, Aurelia Guy, Simon Osindero, Karen Simonyan, Erich Elsen, Jack W. Rae, Oriol Vinyals, Laurent Sifre

**Venue:** arXiv preprint, 2022 (DeepMind)

**arXiv:** [2203.15556](https://arxiv.org/abs/2203.15556)

---

## Abstract

The researchers investigated optimal configurations for training transformer language models within fixed compute budgets. Their experiments with over 400 models (70M to 16B parameters, trained on 5--500B tokens) revealed that current large language models are significantly undertrained. They found that model size and training token count should increase proportionally for compute efficiency. The team developed Chinchilla, a 70-billion parameter model using identical compute as Gopher but with 4x more training data, which outperformed Gopher, GPT-3, and other contemporary models, achieving 67.5% accuracy on the MMLU benchmark.

---

## 1. Core Finding

The paper challenges prevailing practices in LLM training, arguing that current large language models are significantly undertrained due to emphasis on scale over training data quantity. Model size and training tokens should scale equally with compute budgets---contradicting prior work suggesting model size should increase 5.5x while tokens increase only 1.8x for a 10x compute increase.

---

## 2. Methodology

### Three Complementary Approaches

**Approach 1: Training Curve Envelope**
- Fixed model families (70M--10B parameters) trained for varying token counts
- Extracted minimum loss per FLOP across all runs
- Found exponents: N_opt proportional to C^0.50, D_opt proportional to C^0.50

**Approach 2: IsoFLOP Profiles**
- Varied model sizes across fixed FLOP budgets (9 different levels)
- Fitted parabolas to identify optimal parameter counts
- Found exponents: N_opt proportional to C^0.49, D_opt proportional to C^0.51

**Approach 3: Parametric Loss Function**
- Modeled loss as: L(N,D) = E + A/N^alpha + B/D^beta
- Derived efficient frontier through constrained optimization
- Found exponents: N_opt proportional to C^0.46, D_opt proportional to C^0.54

---

## 3. The Chinchilla Model

### Design Rationale

Applied predictions to Gopher's compute budget:
- **Gopher:** 280B parameters, 300B tokens
- **Chinchilla:** 70B parameters, 1.4T tokens
- Same total FLOPs, but 4x smaller with 4x more data

### Architecture

80 layers, modified tokenizer, AdamW optimizer (improved over Adam).

### Dataset Composition

| Source | Proportion | Epochs |
|--------|-----------|--------|
| MassiveWeb | 45% | 1.24 |
| Books | 30% | --- |
| C4 | 10% | --- |
| News | 10% | --- |
| GitHub | 4% | --- |
| Wikipedia | 1% | 3.40 |

---

## 4. Results

| Benchmark | Chinchilla | Gopher | Improvement |
|-----------|-----------|--------|-------------|
| MMLU (5-shot) | 67.6% | 60.0% | +7.6% |
| BIG-bench | 65.1% | 54.4% | +10.7% |
| LAMBADA | 77.4% | 74.5% | +3.9% |
| RACE-m | 86.8% | 75.1% | +11.7% |
| RACE-h | 82.3% | 71.6% | +10.7% |

Chinchilla outperformed significantly larger models (GPT-3, Gopher, MT-NLG 530B) across nearly all downstream tasks.

---

## 5. Critical Insights

1. **Training inefficiency:** Models trained on approximately 300B tokens regardless of parameter count represents suboptimal allocation
2. **Dataset scaling importance:** Achieving 1.4T token targets demands substantially larger, higher-quality datasets
3. **Inference advantages:** Smaller models reduce memory footprint and computational costs for deployment
4. **Learning rate optimization:** Cosine schedule length should match training duration for optimal performance

---

## 6. Fairness and Safety

**Gender bias (Winogender):** Chinchilla shows more consistent performance across pronouns (78.3% overall vs. 71.4% for Gopher), though improvements vary by gender.

**Toxicity:** Negligible differences in PerspectiveAPI scores between models, suggesting model quality improvements do not automatically increase harmful output.

---

## 7. Limitations

- Only two large-scale validation runs (Chinchilla vs. Gopher)
- Power-law assumptions may not capture frontier curvature at highest compute regimes
- Analysis limited to single-epoch training
- Significant uncertainty in extrapolations across many orders of magnitude

---

## 8. Figure Descriptions

- **Figure 1:** IsoFLOP profiles showing optimal model size at each compute budget
- **Figure 2:** Comparison of three approaches for deriving optimal scaling
- **Figure 3:** Chinchilla vs. Gopher performance across downstream tasks
- **Figure 4:** Loss curves as a function of training tokens for different model sizes

---

## Key References

1. Kaplan et al. (2020) --- Scaling Laws for Neural Language Models
2. Rae et al. (2021) --- Scaling Language Models: Methods, Analysis and Insights from Training Gopher
3. Brown et al. (2020) --- Language Models are Few-Shot Learners (GPT-3)
4. Smith et al. (2022) --- Using Deepspeed and Megatron to Train Megatron-Turing NLG 530b
5. Thoppilan et al. (2022) --- LaMDA: Language Models for Dialog Applications
6. Clark et al. (2022) --- Unified Scaling Laws for Routed Language Models
7. Hernandez et al. (2021) --- Scaling Laws for Transfer
8. Fedus et al. (2021) --- Switch Transformers
9. Du et al. (2021) --- GLaM: Efficient Scaling with Mixture-of-Experts
10. Hendrycks et al. (2020) --- Measuring Massive Multitask Language Understanding
