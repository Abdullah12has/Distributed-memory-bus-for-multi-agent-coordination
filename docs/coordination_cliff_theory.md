# Coordination Cliff Theory: Formal Derivation

## Overview

This document provides the formal mathematical derivation of the Coordination Cliff Theorem, including the Chernoff-bound proof that explains why the cliff is a **sharp phase transition** rather than a gradual decline.

Implementation: `src/m6/theory/cliff_prediction.py`

---

## Setup and Notation

| Symbol | Meaning |
|--------|---------|
| C | A context compressor (e.g., LLMLingua-2, filter, phi3-extractive) |
| r | Compression ratio (target). r=1 means no compression, r=4 means 4x |
| q(r) | Per-token retention probability at ratio r. Measured empirically as `token_recall` |
| M | Number of task-relevant tokens in a fragment |
| theta | Minimum fraction of task-relevant tokens needed for coordination success |
| N | Number of sequential compression passes (N=1 in our experiments) |
| p0 | Baseline success probability at r=1 (no compression) |
| tau* | The cliff position: compression ratio at which coordination fails |

---

## Assumptions

**A1 (Memoryless Compressor):** The compressor retains each token independently with probability q(r). Token retention is i.i.d. across positions. This is approximately true for training-free compressors (LLMLingua-2, filter, truncation) which score tokens independently. Violated by iterative or attention-based compressors.

**A2 (Binary Task Relevance):** Each token is either "task-relevant" or not. There are exactly M task-relevant tokens per fragment. In practice, token importance is non-uniform (see Weighted Extension below).

**A3 (Threshold Success):** The planner succeeds if and only if the fraction of surviving task-relevant tokens is at least theta. This is validated by the sharp empirical cliff in family-a data.

---

## Theorem 1: Coordination Cliff Bound

### Statement

Consider a coordination task with M task-relevant tokens, where compressor C with per-token retention probability q(r) is applied once (N=1). Under assumptions A1-A3:

**(i) Success bound:**
P(success | r) <= p0 * q(r)

**(ii) Cliff existence:**
A coordination cliff exists at r* where q(r*) = theta

**(iii) Model independence:**
r* depends only on C (through q) and the task (through theta), NOT on planner model capacity. The planner affects only p0 (baseline success rate).

### Proof of (i)

Under A1, each of the M task-relevant tokens survives independently with probability q(r). The expected fraction of surviving tokens is:

    E[X/M] = q(r)

where X ~ Binomial(M, q(r)) is the count of surviving tokens.

Under A3, success requires X/M >= theta. The planner with baseline p0 succeeds with probability at most p0 when all tokens survive, and strictly less when tokens are lost:

    P(success | r) <= p0 * P(X/M >= theta)

For the loose bound (Markov's inequality):

    P(X/M >= theta) <= E[X/M] / theta = q(r) / theta

Combined: P(success | r) <= p0 * q(r) / theta. Since theta <= 1, this simplifies to P(success | r) <= p0 * q(r).

### Proof of (ii)

When q(r) > theta, the expected surviving fraction exceeds the threshold, and success is likely. When q(r) < theta, the expected surviving fraction is below the threshold, and success is unlikely. The cliff occurs at the crossover point r* where q(r*) = theta.

### Proof of (iii)

r* = q^{-1}(theta). Since q(r) is determined by C alone and theta is determined by the task alone, r* is independent of the planner model. The planner affects only p0, which scales the success probability but does not shift the transition point. QED.

---

## Theorem 2: Cliff Sharpness (Phase Transition)

### Motivation

Theorem 1 establishes WHERE the cliff occurs but not WHY it is sharp. The Markov bound is loose and does not distinguish between a gradual decline and a sudden drop. We need concentration inequalities to explain the sharpness.

### Statement

Under the same assumptions A1-A3, let X ~ Binomial(M, q(r)). By the Hoeffding-Chernoff concentration inequality:

**Above the cliff (q(r) > theta):**

    P(X/M < theta) <= exp(-2M * (q(r) - theta)^2)

Therefore: P(success | r) >= p0 * (1 - exp(-2M * (q(r) - theta)^2))

**Below the cliff (q(r) < theta):**

    P(X/M >= theta) <= exp(-2M * (theta - q(r))^2)

Therefore: P(success | r) <= p0 * exp(-2M * (theta - q(r))^2)

### Why This Explains Sharpness

The key insight is the **exponential decay** in M. For large M:

- When q(r) is even slightly above theta: P(success) → 1 exponentially fast
- When q(r) is even slightly below theta: P(success) → 0 exponentially fast

The **transition width** (the range of q over which success drops from 90% to 10%) is:

    delta_q = sqrt(ln(10) / (2M)) ≈ 1.07 / sqrt(M)

For a family-a workload with M ≈ 10 task-relevant numbers:

    delta_q ≈ 1.07 / sqrt(10) ≈ 0.34

For a hypothetical workload with M = 100 task-relevant tokens:

    delta_q ≈ 1.07 / sqrt(100) ≈ 0.11

This predicts that **more complex tasks (larger M) have sharper cliffs**, which is consistent with empirical observations:
- Family-a (M ≈ 8-16 numbers): sharp cliff (1.0 → 0.0 in one ratio step)
- Family-c (M ≈ 2-4 chain links): gradual decline over several ratio steps

### Phase Transition Framing

In statistical mechanics language:
- **Ordered phase** (q > theta): coordination succeeds with high probability
- **Disordered phase** (q < theta): coordination fails with high probability
- **Critical point** (q = theta): the coordination cliff
- **Order parameter**: coordination success rate
- **Control parameter**: compression ratio r (through q(r))

The transition sharpens with system size M (analogous to thermodynamic limit), making this a **first-order-like phase transition** in the information-theoretic sense.

---

## Weighted Extension (Non-uniform Token Importance)

### Motivation

Assumption A2 (binary importance) is a simplification. In practice, some tokens matter more than others. For example, in family-a (numerical aggregation), the actual numbers are critical while surrounding text is context.

### Formulation

Let each token t_i have importance weight w_i in [0, 1], with sum(w_i) = 1 over task-relevant tokens. The weighted information surviving compression is:

    S(r) = sum(w_i * B_i)

where B_i ~ Bernoulli(q(r)) indicates whether token i survives.

Under A1 (independent retention):

    E[S(r)] = q(r) * sum(w_i) = q(r)
    Var[S(r)] = q(r)(1-q(r)) * sum(w_i^2)

The effective number of tokens is M_eff = 1 / sum(w_i^2) (inverse of Herfindahl index). When weights are uniform (w_i = 1/M), M_eff = M. When weights are concentrated on a few tokens, M_eff < M.

### Implication

The cliff is **sharper when token importance is distributed** (many equally important tokens, large M_eff) and **softer when importance is concentrated** (a few critical tokens, small M_eff).

This explains the empirical observation:
- **filter** compressor preserves high-weight tokens (via TF-IDF ranking) → achieves higher coordination success at matched generic token_recall
- **lingua2** compressor drops tokens uniformly → coordination success matches the uniform-weight theory prediction
- **critical_token_recall** diverges from generic **token_recall** because important tokens have different survival rates than average tokens

---

## Connection to Existing Theory

### Scaling Laws (Kaplan et al., 2020; Hoffmann et al., 2022)

Scaling laws predict that performance follows a power law in model size and data. Our finding that cliff position is **model-size invariant** (Theorem 1(iii)) extends this: model size affects the performance ceiling (p0) but not the phase transition induced by information loss. Practitioners cannot "scale their way out" of compression degradation.

### Lost in the Middle (Liu et al., TACL 2024)

Lost in the Middle shows a U-shaped attention pattern over token position. Our coordination cliff is orthogonal: it depends on total information loss (compression ratio), not positional bias. At moderate compression (2-4x), our cliff effect dominates the positional effect.

### Information Bottleneck (Tishby et al., 2000)

Context compression creates an information bottleneck I(X; Z) where X is original text and Z is compressed text. Coordination success requires I(Z; T) > threshold, where T is the task solution. The cliff occurs where I(Z; T) drops below the task's minimum information requirement. Our q(r) is an empirical proxy for I(Z; T) / I(X; T).

---

## Implementation Reference

All functions are in `src/m6/theory/cliff_prediction.py`:

| Function | Purpose |
|----------|---------|
| `q_required(theta, N)` | Minimum token recall for success |
| `predicted_tau(curve, N, theta)` | Predicted cliff position from q(r) curve |
| `chernoff_success_probability(q, theta, M, N)` | P(success) with finite-M sharpness |
| `chernoff_success_curve(curve, theta, M, N)` | Full predicted curve with Chernoff |
| `cliff_sharpness(M, theta)` | Transition width in q-space |
| `derive_theta(csv, column)` | Empirically derive theta from data |
| `validate_prediction(curve, tau, N, theta)` | Compare predicted vs empirical |
| `full_validation(csv, N, theta)` | Cross-compressor validation |

### Example Usage

```python
from m6.theory.cliff_prediction import (
    predicted_tau, chernoff_success_curve, cliff_sharpness
)

# Predict cliff from token recall curve
curve = [(1.0, 1.0), (2.0, 0.43), (4.0, 0.11), (8.0, 0.02)]
tau = predicted_tau(curve, n_compression_passes=1, theta=0.5)
# tau ≈ 1.9 (cliff at ~2x compression)

# Predict full success curve with M=10 task-relevant tokens
success = chernoff_success_curve(curve, theta=0.5, m=10)
# [(1.0, 1.0), (2.0, 0.56), (4.0, 0.0), (8.0, 0.0)]

# How sharp is the cliff?
width = cliff_sharpness(m=10)
# width ≈ 0.34 (in q-space; transition from 90% to 10% success)
```
