# Path to a 5 — Remediation Plan for *Memory Bus for Multi-Fragment LLM Workflows*

Target: move the thesis from ~35/42 (strong "very good", Finnish 4) to ~38–40/42 (clear "excellent", Finnish 5).

**Core thesis of this plan:** the *evidence* is already strong; the grade is capped by *framing that overclaims relative to that evidence* (rubric item 5) and by polish gaps (items 4, 6, 9). The cheapest path to a 5 is to make every claim exactly as strong as the data supports — no stronger — and to convert the thesis's many honest *disclosures* into honest *corrections*. Almost all of the lift is rewriting; only Tier 2 needs re-running analysis, and all of it is laptop-fast (the compression cache already exists; no GPU re-runs).

Grade arithmetic this plan targets:
- Item 3 Outlining 4→5 (narrative rebalance)
- Item 4 Intro/SoTA 4→5 (reference cleanup)
- Item 5 Achievement of aims 3→4, reach 5 (deflate overclaims + add 2 rigor analyses)
- Item 6 Evaluation of results 4→5 (disclosure → correction)
- Item 9 Language 4→5 (concision pass)
- Item 7 Significance 4→(4–5) (hardest; partial — see Tier 4)

Items 1, 2, 8, 10 are already at max (or supervisor-owned for 8) and need no work beyond verifying the compiled PDF (item 10).

---

## TIER 1 — Pure text edits, no new compute (the bulk of the grade lift)

These touch only prose/tables. They are the highest impact-per-hour changes and resolve every "A-tier" criticism from the review.

### 1.1 Deflate "predicts the cliff *position*" → "explains the *shape* + first-order position estimate"
**Rubric: item 5 (primary), items 3 & 6 (secondary). This single change is the biggest lever.**

The problem (from Ch4, by the thesis's own numbers): on 8/12 cells τ\* is grid-quantised at the 2.5 floor and "lands at the midpoint with no further resolving power" (Table 4.2 †); and the predicted-τ\* bootstrap band excludes the empirical τ\* on 11/11 testable cells (§5.3). So "predicts position" is not supported; "explains why a sharp threshold exists, and estimates position to first order" is.

Concrete edits:
- **Abstract (C2 sentence, ~line 16):** replace "a compounding-error model that predicts the cliff position from per-round token recall" with "a compounding-error model that *explains the existence and sharpness* of the cliff and gives a *first-order* estimate of its position from per-round critical-token recall (median relative error ≈35%; the model's bootstrap band quantifies sampling, not specification, error and does not contain the empirical position — §4.4.4, §5.3)."
- **§1.4 C2 bullet (~line 137):** change "recovers the empirical position within a useful first-order tolerance" — keep this phrasing, it's already correct; but delete any sentence implying tight prediction, and add one clause: "the model's contribution is the *derivation of the threshold structure*, not a tight position predictor."
- **§4.4 opening (~line 555):** restate the model's job as "produces a *first-order* position estimate and, more importantly, a mechanistic account of why the transition is sharp."
- **§5.1 synthesis (~line 793):** already says "within a useful first-order approximation" — good; make sure no adjacent sentence upgrades it.
- **Keep** the §5.3 "band is tight because θ_q is well-estimated; model is biased because A1–A4 are first-order" paragraph — but move its *conclusion* (the model is first-order, not predictive-to-band) up into the abstract and §4.4 so the reader meets the caveat at first contact, not 50 pages later.

Why it lifts the grade: item 5 level 4 requires aims "achieved better than expected... fresh viewpoints" — honest first-order modelling of a real phenomenon *is* that; an overclaimed predictor that fails its own band is a level-3 "minor shortcomings / insufficient proof." You gain a point by claiming *less*.

### 1.2 Fix "decorrelates" → "the QA↔coordination relationship is compressor-dependent"
**Rubric: items 3, 6.**

|ρ| of 0.38–0.59 are moderate-to-strong correlations, not decorrelation. The real finding (stated well in §4.2 already) is sign/magnitude *instability across compressors*.

- Retitle H1 throughout: "**Question-answering accuracy does not transfer across compressors as a coordination predictor**" (or "compressor-dependent QA–coordination coupling"). Drop "decorrelates" from the abstract, §1.4, §4.2 heading, §5.1.
- One sentence in §4.2.1: "We do not claim ρ≈0; we claim that the *sign and magnitude are compressor-dependent*, so no single F1-based selection rule transfers across compressor families — which is the stronger methodological result."

### 1.3 Restate Corollary 1 as "no shift detected on resolvable cells", and independently motivate the calibrated regime
**Rubric: item 5 (primary), item 6.**

Three sub-edits (matching review A3):
1. **Don't call it "invariant"; call it "no τ\* shift detected."** Abstract, §1.4 C2, §4.5/§4.6, §5.1, §5.4.2. The local arm fails the strict ±20% tolerance (24% spread, §5.3) and the binary verdict rests on one frontier cell — say so wherever the claim appears, not only in §5.3.
2. **Stop blending the two invariance arguments.** §5.1 currently reads as "invariant across the Qwen 1.5B→72B 48× scale" but the local evidence is family-c and the 72B point is family-a×LLMLingua-2. Add one clause making explicit these are *different (family, compressor) cells*, so the reader isn't told it's a clean scaling sweep.
3. **Independently motivate the regime predicate so GPT-oss isn't gerrymandered out.** Add a short paragraph in §4.4.3: define the calibrated regime by an *a-priori, measurable* property (e.g., "planners that do not emit chain-of-thought tokens / whose output length is bounded relative to input") rather than by A3 itself. Then GPT-oss is excluded by an independent criterion you could have stated before seeing its result. If you cannot give an independent criterion, *demote* the exclusion to an open limitation rather than a regime boundary.

### 1.4 Name the family-a circularity explicitly
**Rubric: item 6.**

On family-a the regex solver succeeds iff enough task-critical tokens survive, and CTR *is* the survival fraction of those same tokens — so q(τ\*)=θ_q is partly tautological there. The thesis already admits the generic A3 circularity (§4.4.2); add the specific construct-overlap:
- §4.4.2 (A3 bullet) or §3.4.1: "On family-a the solver's success criterion and the CTR metric are near-identical measurements; the family-a validation therefore primarily confirms *internal consistency*. The non-tautological tests of the position estimate are the LLM-planner families (c) where solver-success and CTR are mechanically decoupled."
- This pre-empts the single most likely defense question and turns a hidden weakness into demonstrated self-awareness (the exact thing item 6 level 4–5 rewards).

### 1.5 Hedge the LongLLMLingua "reversal" everywhere, not just §5.3
**Rubric: items 4, 6.**

§5.3 correctly limits it to "the single retriever/embedder stack (bge-large + FAISS)." The abstract and §1.4 still say compress-first "reverses"/"challenges" LongLLMLingua unhedged.
- Abstract C3, §1.4 C3, §2.8, §5.4.1: append "under the single retriever/embedder stack evaluated here" and downgrade "reverses" → "does not reproduce, on our stack, the post-retrieval-compression preference of."
- This matches the project's own earlier guidance (frame as "compress-first preserves content quality," not a falsification).

### 1.6 Put the H2 "≥30% drop" verdict in observed-range units
**Rubric: items 5, 6.**

Table 4.2's drop column is slope-extrapolated (hits 1.61) and the verdict criterion is checked in those units — so "≥30% drop" is being tested where passing values are 120–160%, which is not the intuitive claim.
- Promote the observed-range drop (currently Appendix B) into Table 4.2 as the primary column; keep the extrapolated Δ as secondary. Re-state the H2 criterion in observed-range terms. (This is a table reorganisation; the numbers already exist in Appendix B.)

### 1.7 Add the privacy-vs-coordination conflict paragraph
**Rubric: items 6, 7.**

§5.4.1 says route CONFIDENTIAL fragments through *more aggressive* compression; the rest of the thesis says aggressive compression destroys coordination. For a fragment that is both sensitive and coordination-critical these conflict, and H4's effect is destruction-driven (so "privacy gain" and "coordination loss" are the *same lever*).
- Add one paragraph in §5.4.1 or §5.3 acknowledging the trade-off and stating the bus has no arbitration rule yet (name it future work). Closing a visible logical hole is a cheap item-6 gain.

### 1.8 Scope C4 honestly: "reference implementation", not "demonstrated operational win"
**Rubric: items 5, 7.**

The curl trace proves the bus *runs*; nothing measures that it *helps* (no latency/throughput/quality-delta vs no-bus baseline; CAAC is 0/7 strict-Pareto, honestly).
- Ensure abstract/§1.4 C4 say "reference implementation + auditable metric," never implying a measured benefit. CAAC stays framed as operating-point selector (already done well in §5.2). This prevents an examiner from reading C4 as an unsupported systems claim.

### 1.9 Reference cleanup
**Rubric: item 4 (4→5).**

Bare-year, no-venue citations on load-bearing claims: Guo 2025 (P3's design basis), Saleh 2025a "MemIndex" (the bus claims to *extend* it), Chhikara 2025, Zhou 2025, Bassit 2025, Xu 2025, Guo 2025, Wang 2024.
- Add venue/DOI for each, or soften the dependent claim ("follows the structural design of" → "is loosely inspired by" if the citation can't be firmed up). The two that *must* be solid are Saleh 2025a (extension claim) and Guo 2025 (P3 design claim).
- De-couple the Altman-tweet from the Luccioni peer-reviewed number rhetorically (already flagged honestly; just don't let them sit adjacent borrowing authority).

### 1.10 Reconcile the cell-count headline
**Rubric: items 3, 10.**

Abstract says "~52,000 evaluation cells"; §4.1.1 says "~30,000" for the cliff sweep. Add a one-line breakdown (cliff 30k + scaling + RAG + disclosure + transfer = ~52k) so the headline is traceable.

---

## TIER 2 — Small analyses you re-run (laptop-fast, cache already exists)

These convert "honest disclosure" into "fixed problem," which is the difference between item-5/6 level 3–4 and level 4–5. None needs the GPU; all consume existing CSVs / the compression cache.

### 2.1 Fix the H1 pseudo-replication and report per-family ρ
**Rubric: item 5 (this is a real statistical defect, not just framing). ~2–3 h.**

Table 4.1's n=1350 = 150 workloads × 9 ratios treats repeated measures on the same workload as independent, inflating n ~9× and making the 10⁻¹²⁹ p-values meaningless.
- Recompute the Spearman at the workload level (one (Δqa, Δcoord) pair per workload, or correlation-within-ratio then aggregated). Report the honest n (~150) and p. The BCa CIs are already workload-level, so the verdict (CIs exclude 0.6) should survive — but the p/n must be defensible.
- **Report per-family ρ** alongside the pooled value. Pooling 3 families with opposite cliff dynamics into one Spearman invites a Simpson's-paradox objection; showing per-family ρ either confirms the compressor-level sign (strengthens H1) or reveals it's a pooling artifact (better to find now than at the defense).
- Deliverable: revised Table 4.1 + a per-family supplementary table.

### 2.2 Replace CI-containment with a TOST equivalence test for Corollary 1
**Rubric: item 5, item 6. ~2 h.**

"DeepSeek's CI contains 2.5" is affirming-the-null, especially with admitted low power (§4.6.3). The rigorous instrument for an *invariance* claim is two-one-sided-tests (TOST) against the ±20% tolerance you already adopted from H2.
- Run TOST on the frontier τ\* estimates vs the synthetic reference. Report "statistically equivalent within ±20%" (if it passes) or "consistent with but not shown equivalent" (if underpowered). Either outcome is more defensible than CI-containment, and *doing an equivalence test at all* is the kind of "fresh, rigorous viewpoint" item 5 level 4 rewards.
- This is the single most credibility-enhancing analysis for the weakest contribution.

### 2.3 Cost-decompose the H3 P3 result
**Rubric: items 5, 6, 7. ~2–3 h.**

P3 beating compress-first by +42pp/+25pp "at indistinguishable EUR cost" is a suspiciously large gap; P3 passes high-relevance fragments *verbatim* (§3.3), which normally costs *more* synthesis tokens. Most likely the storage-bounded regime penalises P1 (compresses whole corpus, loses quality) while P3 keeps a full index — i.e., the gap is a regime mechanism, not a pure routing win.
- Produce a token/EUR decomposition table per pipeline per regime (index storage tokens, retrieval tokens, synthesis tokens, total EUR). Either it confirms cost-parity (then the result is real and *stronger* for being explained) or it reveals the gap is a regime artifact (then you temper the P3≻P1 claim — better now).
- The cost ledger already records all of this (§3.1.4 second SQLite table), so it's a query + table, not a re-run.

### 2.4 Plot Phi-3 cliffs against *achieved* ratio
**Rubric: items 5, 6. ~1–2 h.**

Phi-3 saturates at ~2.5× achieved regardless of target (§3.2.3), so its "cliff at τ\*=2.5 in *target*-ratio units" isn't on the same x-axis as the others and may track the ceiling, not a coordination collapse — yet phi3 cells count toward "11/12."
- Regenerate the phi3 cliff panels against achieved ratio; add a sentence flagging phi3's H2 cells are on a different x-axis. If the cliff vanishes against achieved ratio, drop phi3 from the "11/12" headline and report it separately. (Data exists; this is a figure regen.)

### 2.5 (Optional, higher value for item 5→5) The independent A3 probe
**Rubric: item 5 toward level 5. ~1 day, no GPU.**

The thesis names this as future work (§5.6): hand-curate deletion of k/M critical tokens at controlled fractions and measure whether success follows the threshold–sigmoid shape — breaking the cliff↔A3 circularity directly. This is a *deterministic* experiment (no LLM, no GPU): take the family-a workloads, delete critical tokens at fractions {0.1,…,0.9}, run the regex solver, plot success vs surviving fraction.
- If success shows the predicted sharp threshold, you've converted the model's central assumption from "circular justification" to "directly validated" — that is precisely the "remarkable contribution / scientifically significant" character item 5 level 5 asks for, and it's achievable in a day because the solver and generator already exist.
- This is the one item that could push item 5 from 4 to genuinely-5 territory. Strongly recommended if time allows.

---

## TIER 3 — Language & layout pass (item 9 → 5, item 10 verified)

### 3.1 Concision pass for legibility
**Rubric: item 9 (4→5). ~half day.**

The prose is fluent but sentence length is the legibility risk (rubric's "clumsy sentences"). Target the worst offenders: the abstract's single 200-word C2 sentence (~line 16), the §1.2 vignette sentence, and the §4.1.2 statistical-protocol paragraph. Split each into 2–3 sentences. Aim: no sentence over ~40 words in the abstract and chapter openers. "Revised language" (level 5) literally means evidence of a revision pass — this is it.

### 3.2 Verify the compiled PDF, not the Markdown
**Rubric: item 10. ~1 h.**

Item 10 grades `thesis.pdf`. Confirm: (a) `caac_pareto` and `predicted_vs_empirical` figures are regenerated (flagged stale in §D.4 and your own notes) — and note 2.2/2.4 above change `predicted_vs_empirical` and the phi3 panels anyway, so regenerate after those; (b) all figures render crisply at 72pp; (c) captions are in the manuscript language and consistent; (d) the Finnish title `\otsikko{}` is reviewed (your CLAUDE.md lists this as outstanding). Layout is currently 3/3 *if* the PDF matches the clean Markdown — verify, don't assume.

---

## TIER 4 — The honest ceiling on items 5 & 7 (manage expectations)

Two rubric maxima are effectively gated by *publication*, which is out of scope this sprint:
- **Item 5 level 5** ("remarkably contributed... published in a prominent publication") and **item 7 level 5** ("may be published in a prominent publication or patented") both reference external validation the thesis-only path can't provide. Your own notes defer NeurIPS/ICLR.
- **Therefore the realistic ceiling without publication is 4 on item 7 and a strong 4 / borderline-5 on item 5.** That is fine: the *overall* Finnish grade is 5/excellent at ~38+/42, and you do not need every line item maxed to get there. Tier 1+2 plausibly delivers items 3,4,6,9 at 5 and item 5 at a clean 4 (or 5 if 2.5 lands), which is comfortably an overall 5.
- If you want to genuinely unlock item 7→5 later, the lowest-friction route is a workshop paper on the H1 result (the QA-mis-ranks-compressors finding is the most citable, standalone contribution) — but that's a post-thesis move, bookmarked, not part of this plan.

---

## Recommended sequence (so edits don't collide)

1. **Tier 2 analyses first** (2.1 H1 per-family/n-fix, 2.2 TOST, 2.3 P3 cost, 2.4 phi3 achieved-ratio; 2.5 if time). Do these before the text edits so the rewrites cite final numbers. ~1.5–2 days; all laptop.
2. **Tier 1 text edits** (1.1–1.10), now anchored to the corrected numbers. ~1.5–2 days.
3. **Tier 3** concision pass + figure regen + PDF verify. ~1 day.
4. Update `insights.txt` per the project's logging rule as you go (each fix = one numbered entry), and record the framing changes as an ADR addendum so the deflation is traceable (examiners like seeing decisions documented).

**Total: ~4–5 focused days, zero GPU re-runs.** The model-relevant CSVs and the compression cache already exist; everything above is re-analysis of existing results plus rewriting. The grade lift comes almost entirely from making claims match evidence and from two small rigor analyses (TOST, the A3 probe) — not from new experiments.

### One-line summary
You don't need more results to reach a 5 — you need the claims to stop exceeding the results you already have, plus the TOST equivalence test and (ideally) the one-day A3 deletion probe. Claim less, prove the two things that are currently asserted rather than tested, and the honesty that already pervades the thesis becomes its grade-winning feature instead of a list of disclosed weaknesses.
