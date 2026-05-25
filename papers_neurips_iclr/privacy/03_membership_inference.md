# Practical Membership Inference Attacks against Fine-tuned Large Language Models via Self-prompt Calibration (SPV-MIA)

**Authors:** Wenjie Fu, Huandong Wang, Chen Gao, Guanghua Liu, Yong Li, Tao Jiang

**Venue:** NeurIPS 2024

**arXiv:** [https://arxiv.org/abs/2311.06062](https://arxiv.org/abs/2311.06062)

**Note:** The user-provided arxiv ID 2311.17477 resolved to an unrelated physics paper. The correct ID for this membership inference paper is 2311.06062.

---

## Abstract

Membership inference attacks (MIA) aim to determine whether a specific data point was used in training a machine learning model. Existing reference-based attacks for LLMs depend heavily on having appropriate reference datasets with similar distributions to the training data. The authors propose SPV-MIA, which uses a self-prompt method where the adversary collects a dataset with a similar distribution from public APIs by having the target LLM generate training data for reference models. The approach introduces probabilistic variation as a membership signal grounded in model memorization rather than overfitting. Comprehensive evaluation across three datasets and four LLMs shows that SPV-MIA raises the AUC of MIAs from 0.7 to a significantly high level of 0.9.

---

## 1. Introduction

### 1.1 Problem Setting

Membership inference attacks determine whether a specific text was part of an LLM's fine-tuning dataset. This is relevant for:
- **Privacy auditing:** Verifying compliance with data protection regulations
- **Copyright enforcement:** Detecting unauthorized use of proprietary text
- **Security assessment:** Evaluating model vulnerability to data extraction

### 1.2 Limitations of Existing Approaches

Prior MIA methods for LLMs suffer from:
- **Reference model dependency:** Require access to data from the same distribution as training data
- **Overfitting assumption:** Detect overfitting signals that may not exist in well-regularized models
- **Distribution mismatch:** Performance degrades when reference data differs from training data

## 2. Method: SPV-MIA

### 2.1 Novel Membership Signal: Probabilistic Variation

Instead of relying on raw probability scores, SPV-MIA detects **local maxima in the probability landscape**:

- Use a mask-filling model (T5) to generate paraphrased variants of the target text
- Measure whether the original text occupies a probability distribution peak
- Detect local maxima via second partial derivative test
- **Insight:** Memorized texts sit at probability peaks; non-member texts do not

This signal is based on **memorization** rather than overfitting, making it effective even for well-regularized models.

### 2.2 Self-Prompt Reference Model

**Key innovation:** Instead of requiring external reference data:

1. **Prompt the target LLM** to generate text similar to what it was trained on
2. **Collect generated samples** as a proxy training dataset
3. **Fine-tune a reference model** on this self-generated data
4. **Calibrate membership scores** by comparing target and reference model probabilities

This eliminates the need for assumptions about training data distribution.

### 2.3 Attack Pipeline

```
1. Target text -> T5 mask-filling -> Generate paraphrases
2. Compute probabilities on target LLM for original + paraphrases
3. Measure probabilistic variation (peak detection)
4. Self-prompt target LLM -> Generate reference data
5. Fine-tune reference model on generated data
6. Calibrate scores using reference model
7. Output: member / non-member decision
```

## 3. Experimental Setup

### 3.1 Target Models

- GPT-2 (124M parameters)
- GPT-J (6B parameters)
- Falcon-7B
- LLaMA-7B

### 3.2 Datasets

- AG News (news classification)
- XSUM (summarization)
- WikiText (language modeling)

### 3.3 Baselines

- Loss-based attack (Yeom et al.)
- Reference-based attack (Carlini et al.)
- LiRA (Likelihood Ratio Attack)
- LiRA-Candidate (strongest prior baseline)
- Neighborhood attack
- Min-K% attack

## 4. Results

### 4.1 Main Results

| Method | Average AUC | Improvement |
|---|---|---|
| Loss-based | ~60% | Baseline |
| Neighborhood | ~65% | +5% |
| LiRA-Candidate | 74.4% | +14.4% |
| Min-K% | ~70% | +10% |
| **SPV-MIA** | **92.4%** | **+32.4%** |

SPV-MIA achieves approximately **23.6% AUC improvement** over the strongest baseline (LiRA-Candidate).

### 4.2 Across Models

Performance remains strong across all four LLMs:
- GPT-2: High AUC (smaller model, more memorization)
- GPT-J: High AUC
- Falcon-7B: High AUC
- LLaMA-7B: High AUC

### 4.3 Robustness

- **Limited reference data:** Effective with as few as 1,000 self-prompted samples
- **Fine-tuning methods:** Works across full fine-tuning, LoRA, and prefix tuning
- **Dataset sources:** Consistent across diverse text domains

## 5. Defense Evaluation

### 5.1 DP-SGD Defense

Testing under differential privacy (DP-SGD) training:
- At moderate privacy budgets (epsilon=15): SPV-MIA maintains **77.4% AUC**
- At tight budgets (epsilon=3): AUC drops to ~65%
- DP-SGD provides only partial mitigation

### 5.2 Implications

- Existing defenses are insufficient against sophisticated MIA
- Fine-tuned LLMs are fundamentally vulnerable to membership inference
- Privacy budgets must be carefully chosen to balance utility and protection

## 6. Analysis

### 6.1 Why Self-Prompting Works

The target LLM generates text reflecting its training distribution, providing a natural reference without requiring external data access. This is effective because:
- Fine-tuned models reproduce patterns from training data
- Generated text captures style, vocabulary, and topic distributions
- Reference models trained on this data achieve good calibration

### 6.2 Probabilistic Variation vs. Raw Probability

Raw probability fails because:
- Non-member text can have high probability (common patterns)
- Member text can have low probability (rare but memorized patterns)

Probabilistic variation succeeds because:
- Memorized text sits at sharp probability peaks
- Non-memorized text has flatter probability landscapes
- Peak detection is robust to absolute probability differences

## 7. Related Work

- **Membership inference:** Shokri et al. (2017), Yeom et al. (2018), Carlini et al. (2022)
- **LLM privacy:** Training data extraction, memorization analysis
- **Privacy defenses:** DP-SGD, knowledge distillation, regularization
- **Reference-based attacks:** LiRA, shadow model approaches

## 8. Conclusion

SPV-MIA demonstrates that fine-tuned LLMs are highly vulnerable to membership inference attacks that leverage self-prompting and probabilistic variation analysis. The approach eliminates unrealistic assumptions about reference data availability and achieves dramatically higher attack success rates than prior methods. This underscores the need for stronger privacy protections in LLM fine-tuning pipelines.

---

## Key Figures

- **Figure 1:** SPV-MIA pipeline showing self-prompting, probabilistic variation computation, and calibration.
- **Figure 2:** Probability landscape visualization for member vs. non-member texts.
- **Figure 3:** AUC comparison across methods and models.
- **Figure 4:** Defense effectiveness (DP-SGD) at various privacy budgets.

---

## Top References

1. Shokri et al. (2017). Membership Inference Attacks Against Machine Learning Models. IEEE S&P.
2. Carlini et al. (2022). Membership Inference Attacks From First Principles. IEEE S&P.
3. Yeom et al. (2018). Privacy Risk in Machine Learning. CSF.
4. Carlini et al. (2021). Extracting Training Data from Large Language Models. USENIX Security.
5. Abadi et al. (2016). Deep Learning with Differential Privacy. CCS.
6. Hu et al. (2022). LoRA: Low-Rank Adaptation. ICLR.
7. Mattern et al. (2023). Membership Inference Attacks against Language Models via Neighbourhood Comparison.
8. Shi et al. (2024). Detecting Pretraining Data from Large Language Models.
9. Duan et al. (2024). Membership Inference Attacks on LLMs: A Survey.
10. Touvron et al. (2023). LLaMA: Open and Efficient Foundation Language Models.
