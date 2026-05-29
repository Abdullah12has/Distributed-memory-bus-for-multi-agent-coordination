# ADR-007: CAAC reframed as operating-point selection (not Pareto dominance)

**Status:** Accepted
**Date:** 2026-05-29
**Deciders:** Syed Abdullah Hassan (author), grilling session 2026-05-29

## Context

CAAC (Cliff-Aware Adaptive Compression — `src/m6/compressors/caac.py`,
`src/m6/experiments/run_caac.py`) was originally framed as a wrapper that
*Pareto-dominates* fixed-ratio compression. The original
`compute_caac_summary()` used a `caac_cs >= fixed_cs` predicate
(weak dominance), which produced the "100% CAAC dominates" claim used
across `insights.txt` §39, `CLAUDE.md`, and the original NeurIPS pitch.

The 2026-05-28 audit identified two issues:
* The weak predicate counts ties on coordination as wins even when CAAC
  compresses *less* than the fixed baseline. At lingua2 r=2.0,
  fixed_coord = CAAC_coord = 0.3333, fixed achieved 2.20×, CAAC achieved
  2.19× — a compression sacrifice scored as a dominance win.
* `derive_theta()` exists but is never wired into `CAACConfig.theta`,
  so CAAC's q_min is a global hardcoded 0.5 instead of the per-family,
  task-adaptive value the docstring claims.

A strict Pareto criterion was added in code (the `caac_dominates_strict`
field in `results/caac/summary_strict.json`). Under strict Pareto,
the CAAC dominance rate is **0/7 for every inner compressor**: at every
target ratio, CAAC trades compression for coordination — at lingua2
r=16, CAAC achieves +32.7pp coordination at 25× *less* effective
compression than fixed.

This is not "dominance failure." It is structural: CAAC backs off
compression when the recall-side safety bound would be violated. By
construction it gives up compression for safety. The two algorithms
populate different points on the (coord_success, achieved_ratio)
frontier.

## Decision

* **Reframe CAAC as a theorem-grounded operating-point selection
  mechanism**, not a Pareto-dominating wrapper. CAAC and fixed-ratio
  compression are *complementary* points on the frontier.
* **Treat the 0/7 strict-Pareto result as expected and correct**, not
  as a contribution-killer. The contribution is the *predictable*
  operating point: given a per-family θ_q, CAAC's selected point is
  determined by the compounding-error bound, not by tuning.
* **Wire `derive_theta()` end-to-end** so that each family's CAAC
  uses its empirically-derived per-family θ_q. With three families
  CAAC produces three operating points, not one.
* **Switch CAAC's internal recall check to `critical_token_recall`**
  to match what the compounding-error model is calibrated against.
* **Demote CAAC to thesis Ch8 (Discussion / Future Work)** as a
  constructive realization of the compounding-error bound, not a
  pre-registered hypothesis.
* **Keep `summary_strict.json` as canonical**; delete `summary.json`
  (which uses the weak predicate) to avoid downstream confusion.
* **Figure 4 (`caac_pareto`) is regenerated as a region plot** — CAAC's
  operating region (high-coord, modest-compression) vs fixed-ratio's
  operating region (low-coord, high-compression), with the model's
  q_min = θ_q curve as the boundary.

## Options considered

### Option A — Patch the weak predicate, claim strict Pareto wins on a subset

Pros: minimum writing change. Cons: under strict Pareto the win rate
is 0/7. There is no subset to claim from.

### Option B — Strike CAAC as a contribution

Pros: cleanest scope cut; the thesis already has C1–C4. Cons:
discards a real artifact that *does* implement the compounding-error
bound constructively. Future-work value is lost.

### Option C — Reframe as operating-point selection *(chosen)*

Pros: honest to the 0/7 result; preserves CAAC as a structural
demonstration that the compounding-error bound is *operational*;
sets up Ch8 as "the algorithm side of the model." Cons: the
"operating-point selection" framing has no precedent in the
compression literature — the writing must justify why this is
a contribution and not a hedge.

### Option D — Reframe as a safety wrapper

Pros: simplest narrative ("CAAC guarantees coord ≥ θ_q^N"). Cons:
without per-family θ_q wiring the guarantee is vacuous (global
θ_q = 0.5 holds nowhere uniformly). Requires the same wiring work
as Option C with weaker positioning.

## Trade-off analysis

Option C buys honesty and a future-work seam for the price of
inventing a framing the literature does not have a slot for. The
risk is mitigated because Ch8 (rather than the headline) carries
the framing — a Discussion-section reframing has a lower rigor bar
than a contribution-section one.

The wiring work (derive_theta + CTR end-to-end) is small (~7h GPU +
3h analysis) and unlocks per-family figures that the
across-family-averaged `caac_pareto.png` previously obscured.

## Consequences

**Easier.**
* `summary_strict.json` already exists. Deleting `summary.json`
  closes the criterion ambiguity.
* The Ch8 framing aligns with the compounding-error model section
  in Ch5 — model and algorithm reinforce each other.
* Future-work ICLR / NeurIPS revival path is unblocked: a follow-up
  paper can promote CAAC back to a method contribution with the
  proper framing in place.

**Harder.**
* The "operating-point selection" framing needs a clear figure
  (the region plot) to land. Without it readers default to
  expecting dominance.
* The audit-flagged `caac_pareto.png` legend confusion (two reds
  for two "Fixed" inner compressors) must be fixed in the
  regenerated figure.

**Revisit when.**
* The follow-up paper targets ICLR / NeurIPS, at which point the
  Ch8 demonstration is promoted to a Section 5 contribution and
  the operating-point framing must defend itself against reviewer
  pressure for a dominance claim.

## Action items

1. [ ] Port `critical_token_recall` from `run_h1_h2.py` into a shared
   module so `caac.py` can call it.
2. [ ] Wire `cfg.theta = derive_theta(prior_sweep, family,
   recall_column="critical_token_recall")` into `run_caac.py`.
3. [ ] Rerun CAAC sweep on GPU (~7h).
4. [ ] Delete `results/caac/summary.json`; promote
   `summary_strict.json` to `summary.json` and `verdicts.json`.
5. [ ] Regenerate `figures/caac_pareto.{png,pdf}` as a region plot.
6. [ ] Write thesis Ch8 section "Cliff-Aware Adaptive Compression:
   a constructive realization of the compounding-error bound"
   (~3 pages).
