# ADR-008: "Compounding-error model", not "Theorem 1"

**Status:** Accepted
**Date:** 2026-05-29
**Deciders:** Syed Abdullah Hassan (author), grilling session 2026-05-29

## Context

The NeurIPS upgrade plan (`neurIPS.md` §4) framed the cliff-position
prediction as **Theorem 1 (Coordination Cliff Bound)**, with a
four-part statement (i)–(iv) and a proof sketch. The thesis plan
(`plan-v3.md` §3 C2) uses gentler language: *the compounding-error
model* — "a single paragraph in Chapter 5."

The audit-period decision was to commit to the formal "Theorem 1"
framing and write a publication-grade proof in `paper/sections/theorem.tex`.

The subsequent grilling-session decision (Q13) was to ship thesis-only
within ~1 week and skip the NeurIPS submission. Under that timeline:

* The formal proof costs ~2 days of careful writing (especially around
  reconciling assumption A2 — binary token importance — with H4's
  graded-disclosure data).
* The naming benefit of "theorem" over "model" is rhetorical: thesis
  examiners do not require a formal proof to call something a "model"
  but do require one to call it a "theorem".
* The empirical match rate (33% strict, per-family CTR) reads more
  like a model validation than a theorem validation.
* Plan-v3 already gives publication-quality language ("compounding-error
  model") that the thesis can ship without inventing new terminology.

## Decision

* **Rename "Theorem 1" to "compounding-error model"** throughout the
  thesis manuscript.
* **In Chapter 5**, present the model as a derivation: P(success | r) ≤
  q(r)^N follows from the independence of per-round retention (A1) and
  the threshold-success assumption (A3); the cliff position r\* solves
  q(r\*) = θ_q^(1/N). The derivation is a paragraph; not a formal proof.
* **Drop the planned `paper/sections/theorem.tex` LaTeX proof.**
* **Drop the "(i)–(iv)" lemma decomposition** from the model statement.
  The four parts collapse into the single bound + cliff equation + the
  calibrated-regime predicate from ADR-006.
* **Keep the theorem-named code identifiers** (`validate_theorem`,
  `theorem_validation.json`, `theorem_validated`) for backwards
  compatibility with existing artifacts. The thesis manuscript is what
  changes; the codebase nomenclature is stable.
* **Keep the bootstrap-CI-on-θ_q machinery** ("model with uncertainty")
  per Q7's commitment. The renaming does not change the rigor lift —
  it changes the level of formal claim being made.

## Options considered

### Option A — Keep "Theorem 1" + write the formal proof

Pros: publication-grade rigor; future paper revival is cheaper.
Cons: ~2 days writing in a 1-week sprint; A2 reconciliation with H4
is non-trivial; reviewers will compare to actual theorems and find
the empirical match weak.

### Option B — Keep "Theorem 1" + skip the proof

Pros: keeps the name. Cons: a "theorem" without a proof is a
liability. Examiners notice. Reviewers (if the work is ever
re-targeted at a venue) will treat the omission as a red flag.

### Option C — Rename to "compounding-error model" *(chosen)*

Pros: matches plan-v3's own language; aligns expectations
(empirical model + derivation, not formal theorem); examiner-grade
rigor without the 2-day proof cost. Cons: forfeits the "Theorem 1"
naming-currency that the NeurIPS upgrade plan invested in.

### Option D — Rename to "Conjecture 1" or "Proposition 1"

Pros: precise about uncertainty. Cons: "conjecture" reads as "we
don't know"; "proposition" still implies a proof obligation.
Neither matches the empirical-model character of the artifact.

## Trade-off analysis

Option C downgrades naming-currency in exchange for ~2 days of
writing time and a more honest characterization of the artifact.
Under thesis-only timeline, the trade is heavily in favor of C.

The bootstrap-CI-on-θ_q machinery (~2h) keeps the rigor where it
matters (predicted-τ\* band vs empirical-τ\*); only the formal-proof
overhead is dropped.

## Consequences

**Easier.**
* Ch5 narrative ships in ~3 hours instead of ~2 days.
* The 33% match rate reads as a model validation finding, not a
  theorem failure.
* Plan-v3 and the thesis manuscript use the same language end-to-end.

**Harder.**
* If the work is later promoted to NeurIPS / ICLR, the "theorem"
  framing must be re-introduced and the formal proof finally written.
  This ADR is the bookmark for that revival.
* Existing artifacts on disk (`theorem_validation.json`,
  `theorem_validation_ctr.json`) carry the old name. The codebase is
  permitted to stay on "theorem" terminology because changing it
  would invalidate existing JSONs and CSVs; the thesis manuscript
  carries the new name. **The mapping is documented in CONTEXT.md.**

**Revisit when.**
* The work is re-targeted at a venue that expects formal theorems
  (NeurIPS / ICLR / TMLR). At that point, the formal proof must be
  written (~2 days) and the bound's tightness defended (the q^N
  bound is achievable; weighted-importance refinement is not).

## Action items

1. [ ] Update CLAUDE.md and insights.txt to use "compounding-error
   model" in narrative text; preserve "theorem_validation" in
   file-path references.
2. [ ] Add a CONTEXT.md note mapping codebase identifiers
   (`theorem_*`) to manuscript term ("compounding-error model").
3. [ ] Integrate plan-v3 §3's derivation into Ch5 prose (~3h).
4. [ ] Delete or repurpose the empty `paper/sections/theorem.tex`
   stub if it exists.
