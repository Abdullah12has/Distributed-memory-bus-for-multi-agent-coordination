# Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity

**Authors:** William Fedus, Barret Zoph, Noam Shazeer

**Venue:** Journal of Machine Learning Research (JMLR), 2022

**arXiv:** [2101.03961](https://arxiv.org/abs/2101.03961)

---

## Abstract

The paper introduces Switch Transformer, which applies Mixture of Experts to enable sparse activation with massive parameter counts while maintaining constant computational costs. Key contributions include simplifying the MoE routing algorithm and demonstrating that large sparse models may be trained, for the first time, with lower precision (bfloat16) formats. The researchers achieved up to 7x pre-training speed improvements and successfully trained trillion-parameter models.

---

## 1. Architecture Design

### Simplifying Sparse Routing

- Switches from traditional top-k MoE to single-expert routing (k=1)
- Benefits: reduced router computation, halved expert capacity requirements, simplified communication
- Contradicts prior assumptions that k>1 was necessary for gradient flow

### Efficient Routing Elements

- Expert capacity formula: (tokens_per_batch / num_experts) x capacity_factor
- Auxiliary load-balancing loss encourages uniform token distribution across experts
- Loss coefficient alpha = 10^-2 balances stability and training effectiveness

### Routing Mechanism

Router produces logits: h(x) = Wr * x. Gate value: pi(x) = exp(h(x)_i) / sum_j exp(h(x)_j). Output: y = pi(x) * E_i(x) (single expert only).

### Training Innovations

- **Selective precision:** Router computations in float32 while maintaining bfloat16 elsewhere
- **Reduced initialization:** Scale parameter reduced by 10x (sigma = 0.1 instead of 1.0)
- **Expert dropout:** Higher dropout (0.4) on expert layers, lower (0.1) on non-expert layers during fine-tuning

---

## 2. Scaling Properties

| Metric | Result |
|--------|--------|
| Step efficiency | 7.5x speedup vs T5-Base to reach same perplexity |
| Wall-clock time | 7x faster training (Switch-Base 64 expert) |
| vs T5-Large | 2.5x speedup despite T5-Large using 3.5x more FLOPs |
| Sample efficiency | Consistent improvements with increasing experts |

**Key insight:** Parameter count independent of FLOPs is a valuable scaling axis.

---

## 3. Downstream Performance

### Fine-tuning Results

| Task | Switch-Base | T5-Base | Switch-Large | T5-Large |
|------|------------|---------|--------------|----------|
| SuperGLUE | 79.5 | 75.1 | 84.7 | 82.7 |
| SQuAD | 87.2 | 85.5 | 88.6 | 88.1 |
| Winogrande | 73.3 | 66.6 | 83.0 | 79.1 |

### Distillation Achievements

- 99% compression ratio while preserving 28% of teacher quality gains
- Non-expert weight initialization from teacher improves distillation
- 0.75 hard loss / 0.25 soft loss mixture optimal

### Multilingual Results (101 languages)

- Improvements across all 101 languages tested
- 91% achieved 4x or greater speedup over mT5-Base
- Mean speedup: 5x on step-basis

---

## 4. Parallelism Strategies

| Strategy | Configuration | Key Property |
|----------|---------------|--------------|
| Data | n=N, m=1 | No inter-step communication |
| Model | n=1, m=N | All-reduce after each forward pass |
| Expert+Data | Experts per core | All-to-all communication for routing |
| Expert+Model+Data | Hybrid | Balances memory, FLOPs, communication |

### Trillion-parameter models achieved

- **Switch-XXL:** 395B parameters, 64 experts
- **Switch-C:** 1.6T parameters, 2048 experts
- 4x speedup over T5-XXL baseline

---

## 5. Training Stability

- Switch-C (1.6T params) trained stably throughout
- Switch-XXL (395B params) exhibited occasional instabilities
- Instability inversely related to experts but directly related to FLOPs/token

---

## 6. Notable Findings

1. **Parameter count matters independently:** More parameters improve performance even with identical FLOPs
2. **Small-scale viability:** Benefits observable with just 2 experts on standard GPUs/TPUs
3. **Upstream-downstream gap:** Large sparse models sometimes underperform on reasoning tasks despite better pre-training perplexity
4. **Memory efficiency:** Each core maintains constant memory footprint despite exponential parameter growth

---

## 7. Limitations and Future Directions

- Switch-XXL training instability unresolved despite interventions
- Weak downstream translation of upstream improvements for reasoning tasks
- Need comprehensive scaling relationship studies for architecture design
- Exploration of heterogeneous (differently-sized) experts
- Extension beyond FFN layers (attention layers showed promise but instability)

---

## 8. Figure Descriptions

- **Figure 1:** Switch Transformer architecture showing single-expert routing vs. traditional MoE
- **Figure 2:** Scaling curves comparing Switch Transformer vs. dense T5 models
- **Figure 3:** Expert utilization and load balancing across training
- **Figure 4:** Trillion-parameter model training stability curves

---

## Key References

1. Shazeer et al. (2017, 2018) --- Original MoE for NLP
2. Lepikhin et al. (2020) --- GShard: billion-scale MoE transformer
3. Kaplan et al. (2020) --- Scaling laws for neural language models
4. Raffel et al. (2019) --- T5 model framework
5. Brown et al. (2020) --- GPT-3 scaling
6. Vaswani et al. (2017) --- Transformer architecture
7. Hinton et al. (2015) --- Knowledge distillation
8. Jacobs et al. (1991) --- Mixture of experts foundations
9. Gray et al. (2017) --- Sparse training overview
10. Sanh et al. (2019) --- BERT distillation methods
