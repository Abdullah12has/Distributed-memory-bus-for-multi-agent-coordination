# Rethinking Machine Unlearning for Large Language Models

**Authors:** Sijia Liu, Yuanshun Yao, Jinghan Jia, Stephen Casper, Nathalie Baracaldo, Peter Hase, Yuguang Yao, Chris Yuhao Liu, Xiaojun Xu, Hang Li, Kush R. Varshney, Mohit Bansal, Sanmi Koyejo, Yang Liu

**Venue:** Nature Machine Intelligence (accepted)

**arXiv:** [https://arxiv.org/abs/2402.08787](https://arxiv.org/abs/2402.08787)

---

## Abstract

This work investigates machine unlearning (MU) techniques for large language models, aiming to eliminate undesirable data influence (e.g., sensitive or illegal information) and the associated model capabilities while preserving essential knowledge and model utility. The authors examine conceptual foundations, methodologies, assessment metrics, and practical applications. Key focus areas include unlearning scope, data-model interactions, and comprehensive efficacy evaluation. The paper connects unlearning to related domains such as model editing and influence functions, and explores applications in copyright protection, privacy safeguards, and harm reduction.

---

## 1. Introduction

Machine unlearning has emerged as a critical capability for managing LLM lifecycles. As LLMs are trained on massive web-scale datasets, they inevitably absorb content that may be:
- **Legally problematic** -- copyrighted material, GDPR right-to-be-forgotten requests
- **Harmful** -- toxic, discriminatory, or dangerous content
- **Incorrect** -- outdated facts, hallucinated information

Retraining from scratch is prohibitively expensive. Unlearning offers a targeted alternative.

## 2. Problem Definition

### 2.1 Formal Framework

LLM unlearning seeks to efficiently and effectively eliminate specific unlearning targets while preserving performance on non-targeted content.

### 2.2 Key Dimensions

- **Unlearning targets:** Range from specific data points to higher-level concepts (e.g., removing all Harry Potter content)
- **Influence erasure:** Requires joint examination of data and model components
- **Effectiveness scope:** Must define clear boundaries between what should and should not be forgotten
- **Efficiency:** Computational and memory constraints for large-scale models

### 2.3 Distinction from Traditional MU

| Aspect | Traditional MU | LLM MU |
|---|---|---|
| Target granularity | Individual data points | Concepts, capabilities, knowledge domains |
| Post-unlearning behavior | Clear correction target | May resemble hallucinations |
| Scope | Well-defined | Context-dependent, fuzzy boundaries |
| Mechanism | Output adjustment | Deeper weight modifications needed |

## 3. Methodologies

### 3.1 Model-Based Approaches

**Gradient Ascent Variants:**
- Maximize misprediction loss on the forget set
- Random labeling to disrupt memorized associations
- Regularized variants to preserve general capabilities

**Localization-Informed Methods:**
- Identify specific layers, weights, or neurons responsible for target knowledge
- Selectively modify only those components
- Requires mechanistic interpretability tools

**Parameter-Efficient Fine-Tuning:**
- Use adapters or LoRA to reduce computational costs
- Apply unlearning through lightweight parameter modifications
- More practical for very large models

### 3.2 Input-Based Approaches

- In-context learning: prompt engineering to suppress specific outputs
- System prompts: instructing the model to avoid certain topics
- Limitation: may not achieve genuine unlearning (knowledge persists in weights)

### 3.3 Adversarial Unlearning

Incorporate adversarial training to improve robustness against jailbreak attempts that try to re-extract supposedly unlearned information.

### 3.4 Reinforcement Learning Integration

Use reward functions to guide unlearning, as an alternative to expensive RLHF pipelines.

## 4. Assessment Framework

### 4.1 Effectiveness Metrics

- **Comparison with retraining:** Gold standard but impractical for LLMs
- **Hard in-scope evaluation:** Test with paraphrases, multi-hop questions, and indirect queries
- **Membership inference attacks:** Detect remaining training data presence

### 4.2 Utility Preservation

- Natural language understanding task performance (MMLU, etc.)
- Perplexity on held-out data
- "Hard" out-of-scope examples that are close to but distinct from unlearning targets

### 4.3 Efficiency

- Computational cost (FLOPs, wall-clock time)
- Memory requirements for storage and backpropagation
- Black-box applicability (no parameter access needed)

### 4.4 Benchmarks

| Benchmark | Target | Domain |
|---|---|---|
| Enron dataset | Employee emails | Privacy |
| Harry Potter series | Copyrighted fiction | Copyright |
| Toxicity datasets | Harmful content | Safety |
| TOFU | Fictitious entities | Controlled evaluation |

## 5. Applications

### 5.1 Copyright and Privacy Protection

**Algorithmic Disgorgement:** Regulatory requirement to destroy models trained on illegally-obtained data. Unlearning offers an alternative by removing specific content without full model destruction.

**GDPR Right to be Forgotten:** Individual requests to remove personal data influence from models.

### 5.2 Sociotechnical Harm Reduction

- Reducing toxic, discriminatory, and illegal content generation
- Mitigating hallucinations by forgetting incorrect learned responses
- Addressing gender-profession bias and fairness issues
- Defending against jailbreaking and data poisoning attacks

## 6. Critical Observations

### 6.1 Unlearning Scope Precision

Defining exact boundaries between in-scope (should forget) and out-of-scope (should retain) remains unsolved. Example: unlearning "Harry Potter" -- should the model forget the concept of wizards entirely?

### 6.2 Data-Model Interactions

Understanding how specific model components contribute to undesirable outputs requires integrated analysis of data influence and model architecture.

### 6.3 Adversarial Robustness

Existing methods are vulnerable to test-time attacks that can re-extract supposedly forgotten information through:
- Rephrased queries
- Multi-hop reasoning chains
- Jailbreak prompts

## 7. Future Directions

- **Generality:** Solutions must accommodate diverse targets, datasets, and architectures
- **Authenticity:** Robust removal must withstand adversarial evaluation
- **Precision:** Maintaining clear scope boundaries while preserving general capabilities
- **Scalability:** Methods must work efficiently at the scale of modern LLMs (100B+ parameters)

## 8. Conclusion

Machine unlearning will be a valuable tool for making LLMs more trustworthy, but substantial progress requires paradigm updates beyond current approximate methods. The paper provides a comprehensive framework for understanding the challenges and systematizing future research in LLM unlearning.

---

## Key Figures

- **Figure 1:** Taxonomy of LLM unlearning approaches (model-based, input-based, hybrid).
- **Figure 2:** Assessment framework with effectiveness, utility, and efficiency dimensions.
- **Figure 3:** Relationship between unlearning and related fields (model editing, influence functions, privacy).
- **Figure 4:** Application domains and their specific unlearning requirements.

---

## Top References

1. Bourtoule et al. (2021). Machine Unlearning. IEEE S&P.
2. Jang et al. (2023). Knowledge Unlearning for Mitigating Language Models' Harms. ACL.
3. Eldan & Russinovich (2023). Who's Harry Potter? Approximate Unlearning in LLMs.
4. Maini et al. (2024). TOFU: A Task of Fictitious Unlearning for LLMs.
5. Carlini et al. (2023). Extracting Training Data from Diffusion Models. USENIX Security.
6. Meng et al. (2022). Locating and Editing Factual Associations in GPT. NeurIPS.
7. Hu et al. (2022). LoRA: Low-Rank Adaptation of Large Language Models. ICLR.
8. Dwork et al. (2006). Differential Privacy. ICALP.
9. Yao et al. (2024). Large Language Model Unlearning. ICLR.
10. Shi et al. (2024). MUSE: Machine Unlearning Six-Way Evaluation for Language Models.
