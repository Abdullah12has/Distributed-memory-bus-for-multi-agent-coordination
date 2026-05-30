---
title: "Review — Proof audit of the Coordination Cliff Theorem"
audience: Syed Abdullah Hassan
author: Lauri Lovén
date: 2026-05-28
status: draft
type: review-report
derived-from:
  - Research/FUSILLI/research-notes/2026-05-28-01-abdullah-m6-cliff-theorem-proof-audit.md
---

# Proof audit — Coordination Cliff Theorem

**For:** Syed Abdullah Hassan
**From:** Lauri Lovén
**Date:** 2026-05-28
**Subject:** Technical review of the formal claims in `docs/coordination_cliff_theory.md` and `src/m6/theory/cliff_prediction.py`, ahead of the NeurIPS submission.

---

## 1. Summary

The engineering around the cliff theory is strong. The repo has a real statistical-analysis plan, ADRs for the major architectural choices, smoke configs, a compression cache, cross hypothesis correction, the piecewise-linear fit with the right monotonicity constraint, and an empirical sweep that already runs across compressors and families. The thesis itself is in good shape: the experiments chapter ships only the falsifiable H1–H4 claims with Mann–Whitney-Holm and the piecewise-linear cliff fit, so the formal theorem isn't load-bearing there.

The formal theorem document and the NeurIPS-bound proofs are where this review focuses. The good news: Theorem 2 (Hoeffding) is correctly applied to the binomial. The headline issue: **Theorem 1(i) as stated is not what your proof delivers** — your Markov chain gives `p₀·q(r)/θ`, not `p₀·q(r)`. There are also a factor-of-2 inconsistency in the sharpness derivation, an
unfalsifiability problem in Corollary 1, a definitional mismatch in Corollary 1, and a circularity in how θ is derived and then validated. Each has a clean fix; none requires re-running experiments.

The fixes below are listed in priority order. The single most important one is the Theorem 1(i) decision (issue 2); everything else cascades from it.

---

## 2. Findings

### Issue 1 — Theorem 1(i): the stated bound is not what the proof establishes

**Stated** (`cliff_theory.md`, §"Theorem 1: Coordination Cliff Bound"):

> (i) Success bound: `P(success | r) <= p0 * q(r)`

**What the proof actually delivers.** Following the chain in the same section:

1. From A3, `P(success | r) ≤ p₀ · P(X/M ≥ θ)`. ✓ (this step is fine.)
2. By Markov's inequality on the non-negative random variable `X/M`:

   `P(X/M ≥ θ) ≤ E[X/M] / θ = q(r) / θ`.

3. Combining: `P(success | r) ≤ p₀ · q(r) / θ`.

The stated bound `p₀·q(r)` is **strictly tighter** than the proved bound `p₀·q(r)/θ` (since `θ < 1`), and isn't implied by anything else in the document. The text after the proof acknowledges this — "This bound is coarse and can exceed 1 when q is large. The tighter, operationally useful bound comes from Theorem 2 (concentration)…" — and then continues to assert (i) as proved. The concentration form of Theorem 2 is not `p₀·q(r)` either; for large M it is the indicator-like `≈ p₀` when `q > θ` and `≈ 0` when `q < θ`.

The N-pass generalisation in the docstring of `cliff_prediction.py` (lines 3–13) repeats the same pattern: it states `p₀·q^N` as the bound when the algebra delivers `p₀·q^N/θ`.

**Severity:** high. This is the only formally load-bearing inequality of the theorem.

**Fix options** (pick one):

- **Option A (recommended for the paper).** Drop (i) entirely. Lead with (ii) and Theorem 2; let the concentration form carry the quantitative content. This is the cleanest cut and it loses nothing: (i)'s actual job in the paper is to motivate the cliff, and (ii) does that on its own.
- **Option B.** Keep (i) but state it as the proved Markov bound: `P(success | r) ≤ p₀ · q(r) / θ`. Note that this bound is vacuous when `q > θ` (RHS > p₀), and refer the reader to Theorem 2 for the operationally tight version.
- **Option C.** Replace (i) with the large-M concentration form: `P(success | r) → p₀` if `q > θ`, `→ 0` if `q < θ`, as `M → ∞`. Same content as Theorem 2 in different framing.

### Issue 2 — Theorem 1(ii): characterisation, not theorem

**Stated:** "A coordination cliff exists at `r*` where `q(r*) = θ`."

The given proof — "When `q(r) > θ`, expected surviving fraction exceeds threshold, success is likely; when `q(r) < θ`, …" — is an informal characterisation. The rigorous content is exactly Theorem 2. Also, existence of `r*` is conditional on `q(r)` actually crossing `θ` on the measured range; your implementation correctly handles the no-cliff case by returning `inf`, but the theorem statement doesn't declare the existence condition.

**Fix.** Reframe (ii) as a *definition* — `τ* := q⁻¹(θ) when it exists in the measured range` — and present its existence + sharpness as a corollary of Theorem 2.

### Issue 3 — Theorem 1(iii): tautological under A3

**Stated:** "`r*` depends only on C (through q) and the task (through θ), NOT on planner model capacity."

The proof "`r* = q⁻¹(θ)`; q is C-only, θ is task-only, therefore r* is planner-independent" is a tautology *given* the assumption that θ is planner-independent — which is the strong reading of A3. Empirically, a more capable planner can usually succeed with fewer surviving task-relevant tokens, so θ should depend on planner capacity. The theorem's substantive content is A3, not a deduced consequence of it. The H5 family-c result (1.5B/3.8B/8B cliff at the same ratio) is suggestive but small-n; the family-a "floor effect" interpretation (issue 6 below) is the other side of this.

**Fix.** Restate (iii) as: "Under A3 with planner-independent θ, `r*` does not depend on planner capacity." Treat the planner-independence of θ as a *testable hypothesis* (which H5 partially probes), not a theorem premise.

### Issue 4 — Theorem 2 (Hoeffding application): correct

For `X ~ Binomial(M, q)`, the one-sided Hoeffding inequality applied to the sample mean `X/M` gives exactly your two bounds with `t = |q − θ|`. Both are correct and applied correctly. ✓

### Issue 5 — Sharpness derivation: factor of 2 between definition and numerics

**Stated** (`cliff_theory.md`, §"Theorem 2"):

> The transition width (the range of q over which success drops from 90% to 10%) is `Δq = √(ln 10 / (2M)) ≈ 1.07 / √M`.

**Algebra.** Setting `1 − exp(−2M(q−θ)²) = 0.9` gives the 90%-above-cliff crossing at `q⁺ = θ + √(ln 10 / 2M)`. Setting `exp(−2M(θ−q)²) = 0.1` gives the 10%-below-cliff crossing at `q⁻ = θ − √(ln 10 / 2M)`. Therefore:

- Distance from θ to either crossing: `√(ln 10 / 2M) ≈ 1.07/√M` (your formula).
- Full transition width (90% above to 10% below): `q⁺ − q⁻ = 2·√(ln 10 / 2M) = √(2 ln 10 / M) ≈ 2.15/√M`.

Your formula is the **half-width**, but the prose calls it the full range "from 90% to 10%". `cliff_sharpness()` in `cliff_prediction.py` line 248 matches the half-width formula, so the code and the formula are self-consistent — only the prose interpretation and the numerical examples are off by 2×. For `M=10`: half-width 0.34, full width 0.68. For `M=100`: half-width 0.11, full width 0.21.

**Severity:** low. The `O(1/√M)` scaling and the qualitative sharpness-with-M claim are unaffected.

**Fix.** Pick one convention, name it explicitly (`Δ_half` vs `Δ_full`), and update the prose + numerical examples together.

### Issue 6 — Corollary 1 (Ceiling-Cliff Separation): unit mismatch and unfalsifiability

**Stated:** "When `p₀(m) < θ`, no cliff is detectable (floor effect). When `p₀(m) ≥ θ`, `r*` is invariant to m."

Two problems.

**(a) Unit mismatch.** `p₀` is a success probability in `[0,1]`; `θ` is a fraction of task-relevant tokens in `[0,1]`. They're comparable as numbers but they measure different things, and the document never builds the bridge that would make the comparison meaningful (e.g., "baseline success rate equals minimum token retention"). Right now `p₀ < θ` is a comparison without
a stated semantic.

**(b) Unfalsifiability + loose tolerance.** The "p₀ < θ ⇒ no cliff detectable" clause makes the most natural disconfirming evidence — a model whose cliff position differs from the others — explainable as a floor effect. `validate_model_independence()` filters out models with baseline below `baseline_threshold=0.5` and accepts "invariance" with `tau_tolerance_pct=50.0` (line 575). So the empirical "supported" verdict needs only that one family has at least two surviving models whose τ-spread is below 50%. That bar is much lower than your H2 thesis falsifiable claim (±20%).

**Fix.** (i) Either give `p₀ < θ` a semantic (e.g. measure θ by an independent probe that doesn't go through the cliff), or recast it as "p₀ below the success-detection floor". (ii) Tighten `tau_tolerance_pct` to 20% to match the H2 spec. (iii) Report the *distribution* of τ across models as the primary outcome, with the binary "supported" as secondary.

### Issue 7 — Corollary 2 (information density scaling): conjecture, not corollary

The statement "for tasks with information density `d`, `θ ~ d`" is a hypothesis, not a deduction from Theorems 1–2. `d` isn't formally defined, and the empirical "evidence" (family-a `θ=0.48, τ=2.5`; family-c `θ=0.38, τ=6.7`; MultiHopRAG `θ~0.08, τ~11.3`) is consistent with the
hypothesis but is a 3-point trend. Your recent commit `fix: Corollary 2 criterion — theta varies across tasks, not absolute threshold` is exactly the right correction direction (stop treating it as a universal constant).

**Fix.** Reframe as a *conjecture* or *empirical observation* with a falsifiable test, not a corollary. Define `d` operationally (e.g., conditional entropy of the task answer given the input, or the fraction of input tokens that appear in any chain-of-reasoning trace).

### Issue 8 — Internal incompatibility between T1(i) and T2

Theorem 1(i) as currently stated has `P(success | r) ≤ p₀ · q(r)` — linear in q (gradual). Theorem 2's concentration says the transition is a step at `q = θ` for large M (sharp). A reader cannot hold both forms simultaneously. This resolves once issue 1 is fixed (either drop (i), state it as Markov, or state it as concentration); right now the two statements are inconsistent.

---

## 3. Cross-cutting

### Assumption A1 is violated by one of the three audited compressors

A1 is acknowledged in the doc as "approximately true for training-free compressors (LLMLingua-2, filter, truncation); violated by iterative or attention-based compressors." But `full_validation()` includes `phi3-extractive`, which is an attention/LLM-driven compressor and violates A1 by your own statement. If A1 fails, Theorem 2's Hoeffding application fails (token-survival independence is essential), and the cliff-position prediction for phi3-extractive is not a theorem-derived prediction.

**Fix.** Either (a) drop phi3-extractive from theorem validation and report it as a "compressor outside A1's regime" case study, or (b) make an explicit argument that approximate independence still holds (with evidence — e.g. empirical correlation between adjacent token-survival events).

### θ is derived from the cliff and then used to predict the cliff

`derive_theta()` defines θ as the token-recall at the first ratio where coord-success drops below the success threshold. Then `full_validation()` uses that θ to predict the cliff position. This is *in-sample*: the metric measures what the parameter was set to measure.

`cross_validate_theta()` (lines 451–521) does leave-one-family-out correctly. That is the right move; it should be the *primary* validation reported, with `full_validation()` shown only as a sanity check. The current `validate_theorem.py` CLI runs the in-sample version; switch it to LOO-CV for the headline number.

### Match-tolerance of 25 % is loose for a theorem prediction

`validate_prediction()` marks a "match" at `rel_err ≤ 25 %`. For a quantitative point prediction from a theorem, 25 % is generous. Report the full distribution of relative errors (median, IQR, max) alongside any binary match-rate.

### A3 is motivated by the cliff and then used to "explain" the cliff

The doc says A3 is "validated by the sharp empirical cliff in family-a data." That sentence has the form "X is justified by Y, and Y is derived from X", which over-fits. An independent probe of A3 — e.g. measuring the sigmoid steepness of success vs surviving-fraction-of-task-tokens, with the surviving fraction varied directly rather than through compression — would
break the circularity.

---

## 4. Suggested next step

The most useful single action is a focused 30–45 min session with me on **just issue 1 (Theorem 1(i))**. We pick one of the three options (drop / Markov / concentration), and the rest of the document reorganises around that decision: (ii) and (iii) become a definition + corollary structure, the prose around "the tighter operationally useful bound" disappears, and the internal incompatibility (issue 8) resolves itself.

The other issues can be fixed in parallel and don't require new experiments:

- Sharpness factor of 2 — pick a convention, fix prose + numerics (1 hour).
- Corollary 1 tolerance + p₀-vs-θ comparison — change two defaults and add an independent θ probe to the experiment plan (small).
- Corollary 2 — relabel as conjecture; define d (1 paragraph).
- A1 / phi3-extractive — decide drop vs argue; document the decision.
- θ-circularity — switch the CLI default from `full_validation` to `cross_validate_theta` (one-line change).
- Match tolerance — report the error distribution (small).
- A3 probe — add to "future work" if you don't want to run it now.

The thesis (H1–H4 empirical claims, piecewise-linear fit, Holm correction) is not affected by any of this and can proceed independently. The NeurIPS draft is where the audit matters — let's get the theorem in defensible shape before that goes anywhere public.

Good work on the empirical infrastructure and the rigour around the statistical plan — those are usually the hard parts. The theorem text just needs a careful pass with the algebra honest.