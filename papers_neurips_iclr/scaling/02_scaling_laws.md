# Scaling Laws for Neural Language Models

**Authors:** Jared Kaplan, Sam McCandlish, Tom Henighan, Tom B. Brown, Benjamin Chess, Rewon Child, Scott Gray, Alec Radford, Jeffrey Wu, Dario Amodei

**Venue:** arXiv preprint, 2020 (OpenAI)

**arXiv:** [2001.08361](https://arxiv.org/abs/2001.08361)

---

## Abstract

The researchers investigated empirical scaling patterns for language model performance using cross-entropy loss metrics. They discovered that the loss scales as a power-law with model size, dataset size, and the amount of compute. Notable findings include that architectural factors like network width or depth have minimal impact across a broad range. The team identified mathematical relationships governing overfitting and training speed relative to model dimensions, enabling optimal compute budget allocation. A key insight: optimally compute-efficient training involves training very large models on a relatively modest amount of data.

---

## 1. Introduction

This influential paper establishes empirical power-law relationships governing transformer language model performance across scale dimensions. Performance has a power-law relationship with each of the three scale factors N, D, C when not bottlenecked by the other two, with trends spanning more than six orders of magnitude.

---

## 2. Six Critical Insights

1. **Scale > Architecture:** Performance depends primarily on model parameters (N), dataset size (D), and compute (C), not architectural details like depth or width ratios.

2. **Predictable Power Laws:** Three core equations govern performance:
   - L(N) = (Nc/N)^alpha_N, where alpha_N is approximately 0.076
   - L(D) = (Dc/D)^alpha_D, where alpha_D is approximately 0.095
   - L(Cmin) = (Ccmin/Cmin)^alpha_Cmin, where alpha_Cmin is approximately 0.050

3. **Overfitting Patterns:** Every time the model size increases 8x, only approximately 5x more data is needed to avoid penalty, following ratio N^0.74/D.

4. **Training Universality:** Learning curves follow predictable power-laws independent of model size, enabling extrapolation from early training.

5. **Transfer Consistency:** Models generalize to different text distributions with roughly constant loss offset.

6. **Sample Efficiency:** Larger models reach equivalent performance with fewer optimization steps and data points.

---

## 3. Optimal Compute Allocation

**Critical Finding:** Optimal compute-efficient training involves training very large models on relatively modest data and stopping significantly before convergence.

Recommended scaling relationships:
- N proportional to C^0.73 (model size grows with compute)
- B proportional to C^0.24 (batch size grows modestly)
- S proportional to C^0.03 (training steps barely increase)
- D = B x S (data follows from other parameters)

This counterintuitive result suggests most additional compute should expand model size, not training duration.

---

## 4. Combined Loss Function

| Parameters | Conditions | Equation |
|-----------|-----------|----------|
| N, D | Early stopping | L(N,D) = [(Nc/N)^(alpha_N/alpha_D) + Dc/D]^alpha_D |
| N, Smin | Infinite data | L(N,Smin) = (Nc/N)^alpha_N + (Sc/Smin)^alpha_S |

---

## 5. Methodology

- **Models:** Transformer architecture (768 to 1.5B non-embedding parameters)
- **Dataset:** WebText2 (20.3M documents, 96GB text, 2.29 x 10^10 tokens)
- **Training:** Adam optimizer, 2.5 x 10^5 steps, batch size 512 sequences
- **Evaluation:** Cross-entropy loss on 1024-token context

---

## 6. Critical Batch Size

The ideal batch size for training continues to be determinable by measuring gradient noise scale.

Formula: Bcrit(L) = B*/L^(1/alpha_B), where B* is approximately 2 x 10^8 tokens, alpha_B is approximately 0.21.

---

## 7. Emerging Limit Conjecture

Analysis reveals a theoretical intersection point at approximately:
- C* approximately 10^4 PF-days
- N* approximately 10^12 parameters
- D* approximately 10^12 tokens
- L* approximately 1.7 nats/token

The authors hypothesize this represents the point at which Transformer language models reach maximal performance, possibly reflecting natural language entropy limits.

---

## 8. Figure Descriptions

- **Figure 1:** Power-law scaling of loss with model parameters, showing consistent slopes across six orders of magnitude
- **Figure 2:** Loss as a function of compute budget, with optimal frontier
- **Figure 3:** Overfitting curves showing the relationship between model size and required data
- **Figure 4:** Learning curves for different model sizes showing universal shape

---

## Key References

1. Vaswani et al. (2017) --- Attention Is All You Need (Transformer architecture)
2. Radford et al. (2019) --- GPT-2 pretraining scale
3. Brown et al. (2019) --- WebText dataset creation
4. McCandlish et al. (2018) --- Critical batch size theory
5. Devlin et al. (2018) --- BERT encoder-decoder
6. Graves (2012) --- Sequence transduction with RNNs
7. Ba et al. (2016) --- Layer normalization
8. Kingma and Ba (2014) --- Adam optimizer
9. Shazeer et al. (2018) --- Adafactor optimization
10. He et al. (2015) --- ResNet ensemble interpretation
