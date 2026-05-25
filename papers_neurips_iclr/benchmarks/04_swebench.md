# SWE-bench: Can Language Models Resolve Real-World GitHub Issues?

**Authors:** Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik Narasimhan

**Venue:** ICLR 2024

**arXiv:** [2310.06770](https://arxiv.org/abs/2310.06770)

---

## Abstract

The researchers present an evaluation framework with 2,294 software engineering problems from real GitHub repositories. Language models are tasked with editing codebases to resolve issues, requiring comprehension of multiple functions and files simultaneously. Their findings show that even state-of-the-art models struggle significantly, with Claude 2 able to solve a mere 1.96% of the issues.

---

## 1. Introduction

SWE-bench evaluates whether language models can resolve actual bugs and feature requests by generating patches to codebases. The benchmark sources tasks from real GitHub issues and pull requests across 12 popular Python repositories.

---

## 2. Benchmark Construction (3-Stage Pipeline)

**Stage I --- Repository Selection:** Collected pull requests from 12 popular Python repositories, yielding approximately 90,000 PRs total.

**Stage II --- Attribute Filtering:** Selected merged PRs that (1) resolve a GitHub issue and (2) modify test files.

**Stage III --- Execution-Based Filtering:** Retained only instances with at least one test changing from fail-to-pass status, excluding installation/runtime errors.

Final dataset: 2,294 task instances from initial 90,000 PRs.

### Task Formulation

- **Input:** Issue description + complete codebase snapshot
- **Output:** Patch file specifying code modifications
- **Evaluation:** Patch applies successfully and passes all associated tests

---

## 3. Benchmark Characteristics

| Metric | Value |
|--------|-------|
| Issue description length | 195 words (average) |
| Codebase files | 3,010 (average) |
| Codebase lines | 438K (average) |
| Lines edited per solution | 32.8 (average) |
| Files edited per solution | 1.7 (average) |
| Functions edited | 3.0 (average) |
| Fail-to-pass tests | 9.1 (average) |
| Total tests per instance | 120.8 (average) |

### Key Repositories (12 Total)

astropy, django, flask, matplotlib, pylint, pytest, requests, scikit-learn, seaborn, sphinx, sympy, xarray

---

## 4. Results

### Model Performance

| Model | Oracle Retrieval | BM25 Retrieval |
|-------|-----------------|----------------|
| Claude 2 | 4.8% | 1.96% |
| GPT-4 | 1.7% | --- |
| ChatGPT-3.5 | 0.52% | --- |
| SWE-Llama 13b | 4.0% | --- |

### SWE-Llama Fine-tuning

- **Dataset:** 19,000 issue-PR pairs from 37 additional Python repositories
- **Method:** LoRA fine-tuning on CodeLlama (7b and 13b variants)
- **Training:** Used DeepSpeed Ulysses and Flash Attention for long-context handling
- **Constraint:** Excluded sequences exceeding 30,000 tokens

---

## 5. Analysis

### Context Length Challenges

As total context length increases, Claude 2's performance drops considerably---models struggle localizing problematic code amid extensive context.

### Patch Quality Observations

Model-generated patches average 30.1 lines versus 74.5 in gold patches. Models tend toward simpler, shorter edits and rarely modify multiple files.

### Common Failure Patterns

- Models write primitive Python without leveraging existing libraries
- Greedy problem-solving ignoring code style/logical constraints
- Gold patches often implement broader structural improvements

---

## 6. Limitations

- Python-only coverage currently
- All tasks from single evaluation date preventing future temporal analysis
- Execution-based testing alone insufficient for reliability guarantees
- Models need better context retrieval and localization strategies

---

## 7. Figure Descriptions

- **Figure 1:** Overview of the SWE-bench task pipeline from GitHub issue to patch evaluation
- **Figure 2:** Distribution of task difficulty across repositories
- **Figure 3:** Performance degradation with increasing context length

---

## Key References

1. Chen et al. (2021) --- HumanEval benchmark
2. Roziere et al. (2023) --- CodeLlama foundation
3. Hu et al. (2022) --- LoRA methodology
4. Liu et al. (2023) --- Long context analysis
5. Srivastava et al. (2023) --- LM evaluation frameworks
6. Monperrus (2018) --- Automated program repair survey
7. Gazzola et al. (2019) --- Automatic software repair review
8. Cassano et al. (2022) --- MultiPL-E code benchmark
9. Austin et al. (2021) --- Program synthesis with LLMs
10. Hendrycks et al. (2021) --- APPS coding challenge
