# ADR-006: GPT-oss scoping and Theorem 1 "calibrated regime"

**Status:** Accepted
**Date:** 2026-05-29
**Deciders:** Syed Abdullah Hassan (author), grilling session 2026-05-29

## Context

Frontier validation of the compounding-error model's model-independence claim
(originally Theorem 1(iii): *r\* depends on the compressor and task, not the
planner*) was run against four frontier models:

| Model | τ\* (empirical) | τ\* (synth reference) | Validates? |
|---|---|---|---|
| Qwen 72B | 2.68 | 2.70 | yes (0.8% off) |
| DeepSeek V4 Pro | 2.15 | 2.70 | yes (bootstrap CI contains synth) |
| GPT-oss 120B (v1, baseline=0.53) | 6.53 | 2.70 | "floor effect" rescue available |
| GPT-oss 120B (v2, baseline=1.00) | 6.62 | 2.70 | 145% off, **no rescue available** |

GPT-oss 120B v2 has no floor effect (baseline=1.0) and still produces τ\*
substantially above the model's prediction. This contradicts the original
1(iii) claim with no graceful out — no reasonable bootstrap CI on θ_q catches
a 2.4× factor.

Hypothesis: extended-reasoning planners (GPT-oss class) violate the
threshold-success assumption (A3) by recovering from sub-threshold information
via chain-of-thought reasoning. Standard non-reasoning planners
(Qwen, DeepSeek, Llama-3.1) do not.

## Decision

* **Remove GPT-oss 120B from the frontier-validation set** of the thesis.
* **Retain `results/frontier_gptoss120b*` on disk** with a
  `STATUS_NONCANONICAL.txt` marker. No silent deletion — this is scoping,
  not hiding.
* **Soften Theorem 1(iii)** to: *r\* is approximately model-independent
  within the calibrated regime, where the calibrated regime requires
  (a) p₀(planner) ≥ θ_q (no floor effect) AND (b) planner does not
  recover from sub-threshold information via extended reasoning beyond
  what the priors-only baseline supplies.*
* **Formalize "calibrated regime"** by the priors-only baseline measurement
  already collected in H4: a planner is in the regime if its accuracy at
  q→0 is no greater than its priors-only baseline plus ε.
* **Mention the scoping explicitly** in thesis Ch8 limitations and in the
  Discussion's "future work" paragraph.

## Options considered

### Option A — Strike Theorem 1(iii) entirely

Pros: maximum honesty. Cons: discards the model-invariance result
which holds robustly for Qwen 72B, DeepSeek V4 Pro, and H5's 1.5B/3.8B/8B
local models. One exception is being weighted against five validations.

### Option B — Reinterpret θ_q as planner-dependent

Pros: theorem applies more broadly. Cons: requires per-(family, planner)
θ_q estimation, doubling experimental burden. Theorem reads ad-hoc
("θ_q is whatever we need it to be"). Reviewer-bait.

### Option C — Treat GPT-oss as an unflagged outlier

Pros: simplest. Cons: corrosive to credibility. A theorem that quietly
ignores its pre-registered exception is not a theorem.

### Option D — Scope GPT-oss out + formalize the regime *(chosen)*

Pros: keeps the model-invariance result for the calibrated regime
where it robustly holds; flags the exception with a structural
explanation (extended reasoning) rather than hiding it; reuses
existing H4 priors-only measurement to operationalize the regime
predicate. Cons: introduces one extra term ("calibrated regime") that
the reader must internalize. The 145% deviation is acknowledged as a
diagnostic finding rather than a counterexample.

## Trade-off analysis

Option D pays a small terminological cost (the regime predicate) for
preserving five validations that genuinely hold, while keeping the
GPT-oss observation as a *positive contribution* (an empirical
diagnostic of where the model breaks). The honest framing turns an
embarrassment into a finding.

## Consequences

**Easier.**
* Theorem 1's empirical match rate (33% strict CTR per-family) holds
  within the scoped regime without requiring an additional rescue
  framework for GPT-oss.
* H4's existing priors-only measurement gains a second use as the
  regime predicate.
* Future work has a concrete, named gap to fill (extended-reasoning
  planners).

**Harder.**
* The thesis must define "calibrated regime" precisely in Ch5 and
  refer to it in every model-independence claim.
* Future readers see `results/frontier_gptoss120b*` and must read the
  `STATUS_NONCANONICAL.txt` to understand why it is not in the headline.

**Revisit when.**
* Extended-reasoning frontier models become a thesis or paper target
  in their own right — at which point the regime predicate becomes
  the boundary between two empirical regimes rather than a scoping
  device.

## Action items

1. [ ] Write `results/frontier_gptoss120b/STATUS_NONCANONICAL.txt` and
   the same for `_v2`.
2. [ ] Remove GPT-oss claims from `insights.txt` §38 and CLAUDE.md;
   replace with a one-sentence limitations note.
3. [ ] Add the "calibrated regime" definition to thesis Ch5
   (compounding-error model section).
4. [ ] Cite the priors-only-baseline-derived regime predicate in the
   thesis Ch8 limitations.
