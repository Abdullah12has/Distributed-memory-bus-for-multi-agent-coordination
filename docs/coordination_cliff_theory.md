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

**A1 (Memoryless Compressor):** The compressor retains each token independently with probability q(r). Token retention is i.i.d. across positions. This is approximately true for training-free token-level compressors (LLMLingua-2, filter, truncation) which score tokens independently. It is violated by iterative or attention-based compressors: in particular **phi3-extractive** selects whole spans by LLM judgement, so adjacent token-survival events are correlated within a span. The empirical match-rate cells for phi3-extractive should therefore be read as a robustness check of the bound *outside* its formal regime, not as a within-regime prediction.

**A2 (Binary Task Relevance):** Each token is either "task-relevant" or not. There are exactly M task-relevant tokens per fragment. In practice, token importance is non-uniform (see Weighted Extension below).

**A3 (Threshold Success):** The planner succeeds if and only if the fraction of surviving task-relevant tokens is at least theta.

*Independent-probe caveat.* A3 is currently *motivated* by the sharp empirical cliff observed in family-a data, and the cliff in turn is *explained* by A3 — the justification is circular. An independent probe of A3 (sweeping the surviving fraction of task-relevant tokens directly rather than through compression, and measuring the sigmoid steepness of success against retention) would break the circularity. This is named as a future-work direction in the thesis's limitations chapter.

---

## Theorem 1: Coordination Cliff Bound

> **Naming note (ADR-008).** In thesis prose this artefact is called the **compounding-error model**, not "Theorem 1", because the empirical match rate (~33% strict, ~67% at ±50% tolerance) places it in the empirical-bound-with-residuals register rather than the formal-theorem-with-proof register. The "Theorem 1" name is retained in this supplementary document and in the codebase identifier `theorem_validation.json` for back-compat only.

### Statement

Consider a coordination task with M task-relevant tokens, where compressor C with per-token retention probability q(r) is applied once (N=1). Under assumptions A1-A3:

**(i) Threshold-success bound (concentration form).**
By Hoeffding-Chernoff on X ~ Binomial(M, q(r)), as M grows the
probability of success converges to a step at q(r) = theta:

    P(success | r) -> p0 * 1[q(r) >= theta]   in expectation.

The finite-M form is the two-sided Chernoff bound of Theorem 2 below; in particular, the spurious "Markov" form `P(success | r) <= p0 * q(r)` is NOT a valid bound and is not used. The Markov inequality on X/M only yields the coarse `P(success | r) <= p0 * q(r) / theta`, which is vacuous when q > theta. The operationally useful statement is the concentration form above (and its finite-M Chernoff refinement).

**(ii) Cliff position (definition, not deduction).**
Provided q(r) crosses theta on the measured range, define the cliff position

    r* := q^{-1}(theta)

(undefined / +infinity when q never crosses theta — the no-cliff case, which the implementation handles by returning `inf`). The sharpness of the transition at r* is the content of Theorem 2; the existence of r* is a property of the chosen q(r) curve.

**(iii) Model independence (conditional on A3).**
*Conditional* on A3 with planner-independent theta, r* depends only on C (through q) and the task (through theta), NOT on planner model capacity. The planner affects only p0. The planner-independence of theta is itself a *testable hypothesis*, not a derived consequence — the H5/Corollary-1 experiment is the test. Corollary 1 below formalises the result and the calibrated regime in which (iii) is empirically supported.

### Derivation

Under A1, each of the M task-relevant tokens survives independently with probability q(r). The expected fraction of surviving tokens is:

    E[X/M] = q(r)

where X ~ Binomial(M, q(r)) is the count of surviving tokens. Under A3, success requires X/M >= theta, conditioned on the planner being competent at the no-compression operating point (p0). The Chernoff concentration of Theorem 2 then gives the indicator-in-expectation statement (i), and the cliff position r* is the inversion (ii). Statement (iii) is then a *consequence of A3 with planner-independent theta*, not an independent claim.

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

**Transition width — half-width vs full-width convention (explicit).** Two
different "transition width" numbers appear in the literature; both follow
from the same Chernoff bound. We use **delta_q_half** throughout this
document and in `cliff_prediction.py`:

    delta_q_half = sqrt(ln(10) / (2M)) ≈ 1.07 / sqrt(M)

This is the **one-sided** distance from theta to the q value at which
P(success) reaches 90% (or equivalently, the distance from theta to the q
value at which P(success) drops to 10%). The full transition width — the
range of q from the 90%-above-cliff crossing to the 10%-below-cliff
crossing — is twice this:

    delta_q_full = 2 * delta_q_half = sqrt(2 * ln(10) / M) ≈ 2.15 / sqrt(M)

For a family-a workload with M ≈ 10 task-relevant numbers:

    delta_q_half ≈ 0.34   (one-sided)
    delta_q_full ≈ 0.68   (90%-to-10% range)

For a hypothetical workload with M = 100 task-relevant tokens:

    delta_q_half ≈ 0.11   (one-sided)
    delta_q_full ≈ 0.21   (90%-to-10% range)

The function `cliff_sharpness(M, theta)` in `cliff_prediction.py` returns
**delta_q_half** (the one-sided distance). To get the full 90%-to-10%
range, multiply its return value by 2.

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

## Corollary 1: Ceiling–Cliff Separation (calibrated regime)

The planner's parameter count m determines its baseline coordination success p0(m); the cliff position r* is determined by the compressor's q(r) and the task's theta. The corollary holds *within the calibrated regime*, defined by two conditions:

1. **Ceiling condition.** p0(m) is at least theta. (See "unit-bridge" note below.)
2. **No-extended-reasoning condition.** The planner does not recover from sub-threshold information via chain-of-thought reasoning beyond what its priors-only baseline supplies.

When both conditions hold, r* is approximately invariant to m. When (1) fails the floor effect prevents cliff detection; when (2) fails (e.g., GPT-oss-class extended-reasoning planners), r* shifts substantially upward — this is the empirical content of the GPT-oss diagnostic in the thesis.

**Unit-bridge note on `p0 < theta`.** As numbers, p0 lives in [0,1] (a success probability) and theta lives in [0,1] (a fraction of task-relevant tokens). They are not the same quantity. The calibrated-regime condition `p0 >= theta` should be read operationally as *"the planner's no-compression baseline is at least as accurate as the threshold the threshold-success model needs in order to predict success at all"* — equivalently, p0 is at the success-detection floor that the threshold model otherwise vacuously satisfies. This re-reading is what makes the comparison meaningful; the comparison itself is mathematically a comparison of two numbers in [0,1], not a unit-checked physical statement.

**Empirical status.** Family-c across three Qwen-2.5 sizes (1.5B, 3.8B, 8B): tau spread ≈ 24%. Frontier validation on Qwen-2.5-72B (0.8% off the synthetic reference) and DeepSeek V4 Pro (bootstrap CI contains the synthetic reference) extends the result across architecture families. GPT-oss-120B is the calibrated-regime boundary case (145% off; out-of-regime per ADR-006).

**Implementation tolerance.** The `validate_model_independence()` function uses a default `tau_tolerance_pct = 20` to match the H2 falsifiable-claim spec; the older `tau_tolerance_pct = 50` default was loosened during initial development and has been tightened. The function also reports the full distribution of relative tau-spreads per family alongside the binary invariance verdict.

---

## Corollary 2 (information-density scaling) — empirical conjecture

For tasks with information density d (the fraction of input tokens that are task-critical, operationalised in the thesis as `theta_info = 1 - normalized_AUC(success_curve)`), theta_info varies systematically across task structures: dense quantitative tasks (d high) cliff early, distributed qualitative tasks (d low) cliff late or degrade gradually.

This is reported as a **conjecture / empirical observation** rather than as a derived corollary of Theorem 1+2. The derivation does not imply it; the three-point trend (C1 family-a theta_info ≈ 0.97, MultiHopRAG ≈ 0.48, HotpotQA ≈ 0.37) is consistent with it. The thesis keeps the name "Corollary 2" by convention (ADR-008 §"naming"), but the document and the thesis prose both flag that the falsifiable content is empirical, not deductive. `theta_info` is also distinct from `theta_q` — see the module docstring of `cliff_prediction.py` for the definitional split.

---

## Theta circularity — in-sample derivation, bootstrap-CI rigour lift

`derive_theta()` defines theta from the same sweep that `full_validation()` then uses to score predicted-vs-empirical tau. This is in-sample and the audit flagged it as a circularity.

Two mitigations are in place:

1. **Bootstrap CI on theta_q.** `scripts/bootstrap_theta_q.py` resamples workloads to produce a CI on theta_q, which is propagated through q(r) = theta_q to produce a **predicted-tau-star band**. The thesis reports coverage of empirical tau within this band as the primary uncertainty measure, alongside the binary match rate.
2. **Leave-one-family-out cross-validation.** `cross_validate_theta()` derives theta on the other families and predicts tau on the held-out family. This is the not-in-sample test the audit asked for. The `validate_theorem.py` CLI exposes a `--validation-mode` flag with `loo` as the recommended default; the in-sample `full_validation` mode remains available as a sanity check.

The thesis prose reports both in-sample (33% strict / 67% at ±50%) and the bootstrap-CI band; the LOO-CV numbers are available via the CLI for any reader who wants the not-in-sample reference.

---

## Connection to Existing Theory

### Scaling Laws (Kaplan et al., 2020; Hoffmann et al., 2022)

Scaling laws predict that performance follows a power law in model size and data. Our finding that cliff position is **model-size invariant within the calibrated regime** (Theorem 1(iii) + Corollary 1) extends this: model size affects the performance ceiling (p0) but not the phase transition induced by information loss. Practitioners cannot "scale their way out" of compression degradation — *unless* the larger model is also an extended-reasoning planner that exits the calibrated regime, in which case it can.

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
| `cliff_sharpness(M, theta)` | Transition **half-width** in q-space (one-sided; multiply by 2 for full 90→10% range) |
| `derive_theta(csv, column)` | Empirically derive theta_q from sweep data (in-sample) |
| `validate_prediction(curve, tau, N, theta)` | Compare predicted vs empirical tau; returns binary match plus rel_error_pct |
| `full_validation(csv, N, theta)` | Cross-compressor validation (in-sample; sanity check only) |
| `cross_validate_theta(csv, ...)` | **Leave-one-family-out** cross-validation of theta_q (preferred headline number) |
| `validate_model_independence(...)` | Corollary 1 test; default `tau_tolerance_pct=20` matches the H2 spec |
| `estimate_task_theta(curve)` | theta_info via 1 - normalized_AUC (Corollary 2) |

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
half_width = cliff_sharpness(m=10)
# half_width ≈ 0.34  (one-sided distance from theta to the 90%-success point)
full_width = 2 * half_width
# full_width ≈ 0.68  (90%-to-10% transition range)
```
