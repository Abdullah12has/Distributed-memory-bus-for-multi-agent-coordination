# ProPILE: Probing Privacy Leakage in Large Language Models

**Authors:** Siwon Kim, Sangdoo Yun, Hwaran Lee, Martin Gubri, Sungroh Yoon, Seong Joon Oh

**Venue:** arXiv preprint (cs.CR, cs.CL), 2023

**arXiv:** [https://arxiv.org/abs/2307.01881](https://arxiv.org/abs/2307.01881)

---

## Abstract

ProPILE is a probing tool designed to empower data subjects to assess whether their personally identifiable information (PII) has been leaked by large language models. The tool allows individuals to craft prompts using their own PII to gauge privacy intrusion levels. The authors demonstrate ProPILE on the OPT-1.3B model trained on the Pile dataset, showing how individuals can determine whether their information appears in training data. Service providers can also use the tool to evaluate PII leakage in their own models before deployment.

---

## 1. Introduction

### 1.1 The PII Leakage Problem

LLMs trained on massive web-collected datasets inevitably absorb sensitive personal information:
- Personal web pages, social media profiles
- Online forums, professional directories
- Public records inadvertently crawled

Unlike social media platforms where users consciously share information, LLM training data collection operates without individual consent. Anyone with publicly available PII online becomes potentially vulnerable.

### 1.2 Contribution: Empowering Data Subjects

ProPILE enables two key stakeholders:
- **Data subjects:** Individuals can probe whether their PII is memorized by LLMs
- **Service providers:** Companies can audit their models for PII leakage before deployment

## 2. Key Concepts

### 2.1 Linkability

The degree to which disclosed PII can be connected to its owner through contextual associations. Higher linkability means more risk -- knowing name + email + employer makes identification trivial.

### 2.2 Structurality

Classification of PII types:
- **Structured PII:** Phone numbers, email addresses, physical addresses (follow recognizable patterns, easier to detect)
- **Unstructured PII:** Family relationships, affiliations (no standardized format, harder to detect)

## 3. Methodology

### 3.1 Black-Box Probing

For data subjects with only API access:

1. **Construct prompts** using M-1 known PII items about yourself
2. **Query the model** to predict the remaining PII item
3. **Measure likelihood** of the correct PII being generated
4. **Compare to baseline** -- likelihood of random PII items in the same position

If the target PII has significantly higher likelihood than random PII, the model has likely memorized the association.

**Example:**
```
Prompt: "Name: John Smith, Email: john@example.com, Phone:"
Target: "555-1234" (the real phone number)
Baseline: Random phone numbers
```

### 3.2 White-Box Probing

For service providers with full model access:

1. **Soft prompt tuning** -- learn optimal prompt embeddings from a small training data subset
2. **Maximize PII reconstruction** -- optimize prompts to extract maximum PII
3. **Identify worst-case scenarios** -- find the most vulnerable data subjects

This represents the upper bound on privacy leakage.

## 4. Experimental Evaluation

### 4.1 Setup

- **Model:** OPT-1.3B trained on the Pile dataset
- **PII Types:** 5 categories tested

| PII Type | Category | Examples |
|---|---|---|
| Phone numbers | Structured | (555) 123-4567 |
| Email addresses | Structured | user@domain.com |
| Physical addresses | Structured | 123 Main St, City, ST |
| Family relationships | Unstructured | "John's sister is Mary" |
| University affiliations | Unstructured | "Studied at MIT" |

### 4.2 Evaluation Dataset

- 10,000 structured PII quadruplets (name, phone, email, address)
- 10,000 name-family relationship pairs
- 2,000 name-university pairs
- All extracted from the Pile using regex and NER with manual verification

## 5. Results

### 5.1 Likelihood Analysis

Target PII items were generated with **statistically significantly higher likelihood** compared to random PII items across most categories. This confirms memorization of personal information.

### 5.2 Exact Match Rates

**Black-box probing:**
- Modest exact match percentages in basic setup
- Rates increase substantially with additional prompt templates and contextual information
- Multiple probing attempts improve recall

### 5.3 White-Box Amplification

Soft prompt tuning on just 128 data points increased exact match rates dramatically:
- From **0.0047% to 1.3%** -- a ~277x increase
- Demonstrates how optimized prompts dramatically magnify leakage
- Small amounts of auxiliary data enable powerful extraction

### 5.4 Scale Effects

Larger models exhibit increased PII leakage:
- More parameters = more memorization capacity
- Model scaling trends may inadvertently amplify privacy risks
- Tension between model capability and privacy

## 6. Novel Metric: gamma_k

The authors introduce **gamma_k** to quantify practical risk at deployment scale:

**Definition:** The fraction of data subjects whose PII is likely to be revealed within k queries sent.

This metric captures real-world risk:
- gamma_1: risk from a single query
- gamma_100: risk from a determined adversary with 100 attempts
- Provides actionable security assessment for providers

## 7. Transferability

Soft prompts learned on OPT-1.3B successfully transfer to other OPT model sizes:

| Source -> Target | Likelihood Multiplier |
|---|---|
| OPT-1.3B -> OPT-350M | 7.5x |
| OPT-1.3B -> OPT-2.7B | 57.3x |

This means knowledge gained from white-box analysis of one model variant can enhance black-box attacks on related models.

## 8. Analysis

### 8.1 Which PII Types Are Most Vulnerable?

- **Structured PII** (emails, phones) -- more vulnerable due to pattern recognition
- **Unstructured PII** (relationships) -- harder to extract but still detectable
- **Co-occurring PII** -- items that frequently appear together are more linkable

### 8.2 Defense Implications

Current safeguards are inadequate:
- Output filtering: catches some but not all leakage patterns
- Fine-tuning for refusal: can be bypassed with prompt engineering
- Differential privacy training: most promising but reduces model utility

## 9. Societal Impact

ProPILE aims to provide a framework that empowers both data subjects and LLM service providers to thoroughly assess the privacy state of current LLMs. The tool supports:
- Proactive vulnerability identification before deployment
- Individual agency in assessing personal data exposure
- Regulatory compliance assessment (GDPR, CCPA)

## 10. Limitations

- Tested on OPT-1.3B; results may vary for other architectures
- Exact match is a conservative metric; partial leakage is harder to quantify
- Requires some PII knowledge for probing (at least M-1 items)
- White-box probing requires model access

## 11. Conclusion

ProPILE demonstrates that LLMs memorize and can be prompted to reveal personally identifiable information from their training data. The tool provides practical probing methods for both data subjects (black-box) and service providers (white-box), revealing that even modest optimization can dramatically amplify PII extraction rates.

---

## Key Figures

- **Figure 1:** ProPILE framework showing black-box and white-box probing pipelines.
- **Figure 2:** Likelihood distributions for target vs. random PII items.
- **Figure 3:** Exact match rates with increasing prompt complexity.
- **Figure 4:** Transferability of soft prompts across OPT model sizes.
- **Figure 5:** gamma_k curves showing leakage risk vs. number of queries.

---

## Top References

1. Carlini et al. (2021). Extracting Training Data from Large Language Models. USENIX Security.
2. Carlini et al. (2023). Quantifying Memorization Across Neural Language Models. ICLR.
3. Zhang et al. (2022). OPT: Open Pre-trained Transformer Language Models.
4. Gao et al. (2020). The Pile: An 800GB Dataset of Diverse Text for Language Modeling.
5. Dwork et al. (2006). Differential Privacy. ICALP.
6. Shokri et al. (2017). Membership Inference Attacks Against Machine Learning Models. IEEE S&P.
7. Lester et al. (2021). The Power of Scale for Parameter-Efficient Prompt Tuning. EMNLP.
8. Brown et al. (2020). Language Models are Few-Shot Learners. NeurIPS.
9. Li et al. (2023). Multi-step Jailbreaking Privacy Attacks on ChatGPT.
10. Huang et al. (2022). Large Language Models Can Be Strong Differentially Private Learners. ICLR.
