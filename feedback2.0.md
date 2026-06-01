# Examiner & Supervisor Revision Report
### *Memory Bus for Multi-Fragment LLM Workflows* — Syed Abdullah Hassan

This is a working document. It is organized so you can fix things in priority order, not in reading order. Severity legend:

- **[B] BLOCKER** — must fix before submission; an examiner will mark you down or stop trusting the document.
- **[MAJ] MAJOR** — substantive framing/claims issue; weakens the contribution if left.
- **[MOD] MODERATE** — real but localized; fixable with focused edits.
- **[MIN] MINOR / COSMETIC** — quick polish.

Effort legend: 🟢 < 30 min · 🟡 a few hours · 🔴 a day+ / possible rerun.

---

## 0. Triage table (read this first)

| # | Issue | Sev | Effort | Where |
|---|-------|-----|--------|-------|
| 1 | "Coordination" is a misnomer for what you measure | MAJ | 🟡 | Title, abstract, throughout |
| 2 | Abstract/contributions overclaim relative to body | MAJ | 🟡 | p3–4, §1.4 |
| 3 | **§4.8.4 prose contradicts Table 7 / H4 verdict** (Phi-3: −7.5pp p=.027 vs 0.4pp p=.91) | **B** | 🟢 | §4.8.4 |
| 4 | **Memory-bus benchmark numbers differ between §4.8.9 and §5.6** | **B** | 🟢 | §4.8.9, §5.6 |
| 5 | **Table 9 caption self-contradicts on family-a τ\*** (2.6997 vs 2.5) | **B** | 🟢 | §4.9.2 |
| 6 | **Phi-3 workload-level n: 100 (§4.1.2) vs 150 (Table 3)** | **B** | 🟢 | §4.1.2, Table 3 |
| 7 | Compounding-error model contribution is thin + family-a circular | MAJ | 🟡 | §4.4 |
| 8 | Corollary 1 carried by one frontier cell, but sold as cross-arch validation | MAJ | 🟡 | §4.6, abstract, §5.4.2 |
| 9 | H4 privacy claim is destruction-driven (deflationary) but abstract reads positive | MAJ | 🟡 | abstract, §4.8 |
| 10 | H3 cost model can't support the P3 comparison; "cost model" oversold as contribution | MAJ | 🟡 | §4.7, §1.4 |
| 11 | Super-user ACL mask overflow = correctness bug in access-control core | MOD | 🟡 | §5.6 |
| 12 | Duplicated abstract (two versions on p3) | **B** | 🟢 | p3 |
| 13 | "Chapter Chapter N" broken cross-refs everywhere | **B** | 🟢 | throughout |
| 14 | Appendix section titles are literal `*` placeholders | **B** | 🟢 | §7.1–7.4 |
| 15 | Finnish abstract reintroduces "multi-actor" framing English avoids | MOD | 🟢 | Tiivistelmä |
| 16 | Memory bus underdelivered for a title-level artefact | MAJ | 🔴/🟡 | §1.4, title, §4.8.9 |

---

## 1. Framing & claims — the central problem

The single thing an examiner will react to most strongly: **the abstract, title, and contribution list still carry the ambition of the original plan, while the body honestly walks most of it back.** The honesty is your biggest strength, but right now it is distributed across the body and absent from the front matter. Pull the framing down to meet the evidence.

### 1.1 [MAJ 🟡] "Coordination" is the wrong word
- The title and central coinage ("coordination cliff") promise multi-agent coordination. Your instrument is a regex solver or a single flat LLM call; ADR-009 explicitly scopes multi-round agents out.
- What you actually measure is **whether enough task-critical tokens survive compression for a planner to recover the answer** — information survival / multi-fragment *solvability*, not coordination.
- The disclaimer currently lives in scattered "scope reminder" asides (§1.2, §3.7, §4.x). That is not enough; a reader who takes "coordination" at face value will believe you measured something you didn't.
- **Fix (choose one):**
  - (a) Rename the central quantity, e.g. *multi-fragment solvability cliff*; keep "coordination" only where you explicitly mean the structural multi-fragment property; **or**
  - (b) Add one prominent definitional paragraph in §1.2 that operationally defines "coordination success" as the structural multi-fragment property and explicitly disclaims the multi-agent reading — then stop re-disclaiming it five more times.
- Either way, consolidate the repeated scope reminders into one place.

### 1.2 [MAJ 🟡] Abstract overclaims vs body
Specific lines to soften:
- "cross-architecture validated on Qwen-72B and **DeepSeek V4 Pro**" — body says DeepSeek only *weakly corroborates* (CI [1.76, 7.14], bootstrap median 5.7 far from point estimate 2.15). It is not a validation. Drop DeepSeek from the validation claim or label it "weak corroboration."
- "compression measurably reduces protected-fact disclosure" — true but the body shows this is **destruction-driven**, not privacy-specific. Add the qualifier in the abstract (see §9 below).
- "a catalogue of three RAG pipelines showing compress-first is robustly preferred" — fine, but the abstract should not let the "cost model" read as validated (see §10).
- Pre-registration honesty line ("two hold as stated (H1, H2)") — good, keep it. But H2 is 11/12 with a documented exception; say "H2 (11/12)" once so it is not read as a clean 12/12.

### 1.3 [MAJ 🟡] Lead with H1
After all the deflation, your confident, citable, *independent* core is **H1**: single-agent QA accuracy mis-ranks compressors for multi-fragment use. It does not depend on the model, the bus, or the frontier sample.
- Restructure the abstract and §1.4 so H1 is contribution #1 and the headline.
- Demote the compounding-error model, the bus, and the two corollaries to *supporting / exploratory* rather than co-equal headline contributions.
- Add a single "what stands and what doesn't" paragraph at the top of §5.1 so the examiner doesn't have to assemble the verdict themselves.

---

## 2. Internal inconsistencies (these are the credibility-killers — fix all)

These look like leftovers from earlier runs (biased-benchmark era, 3-compressor era, coarse-grid era). Each one individually makes a careful reader doubt the rest.

### 2.1 [B 🟢] §4.8.4 prose contradicts Table 7 and the H4 verdict
- §4.8.4 prose: reduction "for the two aggressive token-level compressors (filter −21 pp, LLMLingua-2 −19 pp) and **borderline for the extractive copier (Phi-3 −7,5 pp, p = 0,027)**."
- Table 7 + verdict block + §4.8.5: **Phi-3 reduction = 0.4 pp, p = 0.91, not significant.**
- The §4.8.4 prose also omits truncation entirely ("two aggressive token-level compressors") while the canonical run is four compressors.
- **This is the most damaging inconsistency in the thesis** — it is in the results prose of a SUPPORTED hypothesis. Rewrite §4.8.4 to match Table 7 (truncation −24.6, filter −20.4, LLMLingua-2 −18.9, Phi-3 −0.4 n.s.).

### 2.2 [B 🟢] Memory-bus benchmark numbers disagree
- §4.8.9 / Table 8 (Host A, M4 Pro): write ≈ **18,200** ops/s, read ≈ **19,900** ops/s, audit verify **1.68 µs/row**, policy ≈ 5.2M ops/s.
- §5.6: write ≈ **16,800** ops/s, read ≈ **18,200** ops/s, audit verify **1.57 µs/row**.
- Pick the canonical numbers (the §4.8.9 Table 8 values, presumably) and make §5.6 cite them verbatim.

### 2.3 [B 🟢] Table 9 caption contradicts itself on family-a τ\*
- Caption says the C1 family-a row "**uses the auxiliary h1_h2_final fit τ\* = 2.6997 rather than the canonical h1_h2_v2 fit τ\* = 2.5**."
- The table cell shows **2.5**, and the note immediately below says "**The τ\* for C1 family-a is the canonical h1_h2_v2 fit 2.5**."
- Decide which value the row uses and make caption, cell, and note agree. (Given §4.6's supersession argument, use 2.5 and delete the 2.6997 sentence, or keep 2.6997 only as a parenthetical "earlier register.")

### 2.4 [B 🟢] Phi-3 workload-level n disagrees
- §4.1.2: "n = 150 ... **n = 100 for Phi-3-Mini extractive** after its ~2.5× ceiling collapses the upper ratio range."
- Table 3: Phi-3-Mini extractive workload-level **n = 150** (pooled n = 750).
- Reconcile: if the ceiling collapses the *ratio* range it changes pooled n (750 = 150×5), not workload n. State workload n = 150 and pooled n = 750 consistently, and delete the "n = 100" claim or explain it.

### 2.5 [MIN 🟢] Rounding drift
- §4.8.4 "29 pp on average" vs table 28.6 pp; "filter −21 / LLMLingua-2 −19" vs 20.4 / 18.9 elsewhere. Standardize to one decimal everywhere (you already use 24.6 / 20.4 / 18.9 in §4.8.5).

### 2.6 [MOD 🟢] τ\* for family-a is quoted as 2.5, 2.7, 2.6997, and 1.1 across the chapter
You manage this deliberately, but the reader has to hold four numbers. Add a one-line "τ\* register table" footnote the first time it matters (§4.3 or §4.5): deterministic coarse-grid 2.5 (artefact) → deterministic fine-grid ≈1.1 (true solver cliff) → LLM-planner ≈2.5–2.8 (deployment-relevant) → auxiliary h1_h2_final fit 2.6997 (superseded). Then reference it instead of re-explaining.

---

## 3. The compounding-error model (§4.4) — deepest scholarly weakness

### 3.1 [MAJ 🟡] State honestly what the model contributes
- Predictive validity is weak: **33% within ±25% (4/12), 67% within ±50%**, median relative error **35.3%**, and the empirical τ\* falls **outside the bootstrap band on 11/11 testable cells**. LOO is worse (25% / 75%).
- You already demote it from "Theorem 1" to "model" — good. But the manuscript still spends a lot of space on the predicted-vs-empirical match-rate table as if it validates *position prediction*. It does not.
- **Reframe:** the model's contribution is a *qualitative explanation of why the transition is sharp* (a recall threshold on critical tokens produces a step). Present position prediction as "first-order, not tight," and move the match-rate table to a subordinate role.

### 3.2 [MAJ 🟡] The family-a circularity undercuts the headline synthetic result
- On family-a the regex solver succeeds **iff** enough critical numeric tokens survive, and CTR (your q(r)) **is** that surviving fraction. So q(τ\*) = θ_q on family-a relates two near-identical measurements.
- You concede this (A3 discussion, §4.4.2), but the abstract still leans on family-a as "the family on which the model is most directly testable." It is most directly *computable*, not most independently *validating*. Make that distinction in the abstract, not just in A3.

### 3.3 [MAJ 🟡] Promote the A3 probe out of Future Work
- The A3 probe (§5.6, `results/a3_probe`) is the **only non-circular test** of the threshold mechanism: hand-curated token deletion + an LLM planner. Its result is genuinely interesting — dense family threshold-like (k≈15, r0≈0.84), distributed family graded (k≈5.9, band≈0.54), and the probed threshold (0.84) exceeds CTR-derived θ_q (0.63) because compressors preferentially keep answer tokens.
- This belongs in the **results chapter** as the validation of the model's central assumption, not buried in future work as a "this probe was carried out" aside. Right now your strongest evidence for the model is hidden.

### 3.4 [MOD 🟢] The N vs N_q notation is a footgun
- N = compression passes (always 1). N_q = CAAC's recall-exponent knob. You flag the confusion, but consider renaming N_q (e.g. β or k_q) so the symbols are not one subscript apart. At minimum, add both to the symbol list (currently only N appears).

---

## 4. Corollary 1 (§4.5–4.6) — the most-promoted, thinnest-supported claim

### 4.1 [MAJ 🟡] Be honest in the abstract about the evidential base
Trace the load-bearing chain after all caveats:
- Deterministic τ\*=2.5 → admitted coarse-grid artefact (true ≈1.1).
- Local 3-architecture sweep → 24% spread, **fails strict ±20%**, passes only ±50%.
- DeepSeek → weakly identified (median 5.7 vs point 2.15).
- GPT-oss → out-of-regime.
- TOST → **neither frontier cell passes ±20% equivalence**.
- **What's left:** Llama-8B (≈2.48) vs Qwen-72B (≈2.79) — two models, one cell.
- §4.6.6 states this correctly ("carried by one well-identified frontier cell"). But the abstract and §5.4.2 ("most promising contribution... to the compression literature") overclaim. Align the front matter and the field-significance section to the §4.6.6 wording.

### 4.2 [MOD 🟡] The corollary1_supported: false flag needs a cleaner explanation
- You explain that `model_independence_20pct.json` reads `corollary1_supported: false` because it is the strict-20% local-arm result. Good that you surface it — but an examiner opening the repo sees a "false" flag against a "SUPPORTED" verdict. Add a one-sentence repo-level note (CONTEXT.md and the verdict table footnote) so the artefact and the manuscript can't be read as contradictory.

### 4.3 [MOD 🟢] Frontier sample size is the binding limitation — say so up front
10 workloads × 3 seeds for the original frontier runs is small. You name it in §4.6.1 and §5.3, but it should be flagged the first time you present a frontier τ\* so the reader calibrates the point estimates immediately.

---

## 5. H2 & the deterministic solver (§4.3)

### 5.1 [MAJ 🟡] Make the solver-vs-LLM divergence a framing caveat, not a mid-chapter correction
- The fine-grid finding (solver cliffs ≈1.1, LLM ≈2.7 on the same cell) is important: it says the deterministic solver is a *brittle proxy that fails the instant one token drops*, which is also *why* it nearly tautologically tracks CTR.
- This currently emerges as a correction inside §4.3. State once, up front (start of §4.1 or §4.3): the deterministic solver is a deliberate conservative lower bound chosen for variance isolation; the LLM-planner cliff is the deployment-relevant quantity; earlier synthetic-reference comparisons were artefacts.

### 5.2 [MOD 🟢] Phi-3 cells in the 11/12 count need a clearer asterisk
- Phi-3 saturates ≈2.5×, so its τ\* is on a different x-axis (achieved vs target). You note this, but the headline "11/12" includes 3 Phi-3 cells whose positions you say shouldn't be compared numerically. Consider reporting "11/12, of which the 3 Phi-3 cells are significant-but-not-position-comparable" so the count isn't read as cleaner than it is.

---

## 6. H1 (§4.2) — strong, but state the within-family evidence precisely

### 6.1 [MOD 🟢] The positive within-family evidence is one cell
- 8/12 cells degenerate (no rank variance), 3 of the remaining 4 n.s., and the only significant within-family relationship is LLMLingua-2/family-c (−0.46). The filter's −0.82 is a between-family artefact (family-a only −0.13 n.s.).
- Your conservative reading ("QA-F1 does not *positively* predict coordination anywhere we can measure within a family") is correct and well argued. Just make sure §4.2.1 says plainly that the within-task positive evidence reduces to one cell — an examiner will find it, so own it.
- The between-family / pseudo-replication decomposition (Table 4) is genuinely sophisticated; keep it foregrounded. It is one of the best things in the thesis.

---

## 7. H3 / RAG catalogue (§4.7) — shrink the claim to what survives

### 7.1 [MAJ 🟡] The "EUR-per-workflow cost model" is oversold as a contribution
- It is corpus-dominated (pipelines differ by 4.1–4.9%), and **does not meter compression compute at all**. That is precisely the flaw that makes the P3 comparison uninterpretable.
- Downgrade it in §1.4 from "contribution" to "first-pass cost instrumentation with a known fidelity limitation," and make the matched-compression problem the *headline* H3 limitation, not an audit-pass afterthought.

### 7.2 [MAJ 🟢] The P3 result is close to a null dressed as a finding
- P3 "leads" only because it routes verbatim (achieved 1.00×). "Not compressing preserves F1" is trivial. You say this in §4.7.4 — good — but the verdict table and §5.4.1 still present "P3 ≻ P1 ≻ P2." Add the achieved-ratio column meaning directly into the ranking statement so the ranking can't be quoted out of context.
- The defensible C3 result is narrow and fine: **compress-first > retrieve-first on one stack**, an explicit single-stack non-reproduction of LongLLMLingua. Make that the stated finding.

---

## 8. H4 / inference disclosure (§4.8) — reframe as a clean negative result

### 8.1 [MAJ 🟡] The privacy contribution is deflationary — present it that way
- Construct-validity (§4.8.5) + oracle-redaction (0.79→0.56, 23.4 pp at ~0% destruction, matching truncation's 24.6 pp) show the disclosure reduction is **destruction-driven**, not privacy-specific.
- This is a *good* negative result. But the abstract and §1.4 read as a positive privacy claim. Restate: "compression reduces disclosure only as a side effect of destroying information; targeted field redaction achieves the same reduction at near-zero coordination cost, so blanket compression is a blunt and confounded privacy lever."
- The oracle-redaction control is one of your strongest moves — it shows the metric *can* detect targeted removal. Foreground it.

### 8.2 [MOD 🟢] The reader YES-bias is a real validity threat, not just a caveat
- The entire signal is "flip a no-biased reader to YES" (priors YES rate ≈0.03). Class-rebalancing keeps reductions within 1 pp — good — but the larger-reader confirmation is still open. Say in the verdict block (not only in §4.8.7) that the metric is an *asymmetric* leakage signal pending an unbiased reader.

---

## 9. The memory bus / C4 (§3.1, §4.8.9, Appendix A/D)

### 9.1 [MAJ 🟡/🔴] Underdelivered for a title-level artefact
- C4's empirical content is the disclosure metric + a single-threaded microbenchmark. No concurrent-HTTP path, no policy-lattice scaling, no audit-verify scaling curve.
- **Preferred fix (cheap):** reposition the bus honestly as an *engineering reference artefact that operationalises the disclosure metric*, and make the **disclosure metric** the C4 *research* contribution. Adjust the title emphasis and §1.4 accordingly.
- **If you have time (🟡):** add the audit-verify scaling curve across chain lengths and a small concurrent-path number — both are cheap and would materially upgrade "characterised single-threaded" → "characterised."

### 9.2 [MOD 🟡] Fix the super-user ACL overflow bug
- `Principal.super_user()` sets `acl_mask = 2^64 − 1`, which overflows the signed-64-bit SQLite INTEGER audit column → a super-user **cannot write to the audit log**. That is a correctness defect in the access-control core, not a cosmetic nit.
- Fix it (store as TEXT/BLOB or cap at 2^63−1) and remove it from "future work." Shipping a known auth-layer correctness bug in the system named in your title is the kind of thing a software-leaning examiner will press on.

### 9.3 [MIN 🟢] Trace/figures consistency
- Appendix D write trace returns `achieved_ratio: 3.72` for target 4.0 — consistent with §3.3 caveats; good. Just confirm the figure/table compressor names match the code identifiers in Appendix B (`lingua2`, `filter`, `phi3-extractive`, `truncation`, `caac`, `identity`) everywhere.

---

## 10. CAAC (§5.2) — keep it, but defend the framing crisply

### 10.1 [MOD 🟢] "0/7 strict Pareto" can be misread as failure
- Your operating-point reframing (ADR-007) is sound: CAAC trades ratio for a recall guarantee, so by construction it does not strict-dominate. Weak dominance (coordination ≥ fixed, 100% of the time) holds.
- But make the *contribution* sentence unmissable: CAAC's contribution is a **measurement-bounded safety floor**, not Pareto improvement. State it before the 0/7 number, not after, so a skimming reader doesn't anchor on "0/7."
- The θ_q/N_q null is informative (r_min is the real knob); keep it, and explicitly defer the r_min sweep as the *one* CAAC future-work item.

---

## 11. Cosmetic / presentation (fast wins — do all of these)

- **[B 🟢] Duplicated abstract (p3):** the structured abstract is followed by a second prose abstract starting "Large language models running in multi-step workflows pay for every token they read." Collapse to one.
- **[B 🟢] "Chapter Chapter 3/4/5" everywhere:** broken cross-reference macro (the `\chapref` doubles "Chapter"). Global find-and-fix.
- **[B 🟢] Appendix titles are literal `*`:** §7.1 *, §7.2 *, §7.4.1 * … placeholder text shipped into the PDF. Replace with the real appendix titles (which already exist as the "Appendix A/B/C/D" lines below them).
- **[MIN 🟢] Copyright page typo:** "There terms are indicated" → "These terms are indicated."
- **[MOD 🟢] Finnish abstract (Tiivistelmä):** opens "Monitoimijallisissa ja monivaiheisissa" (multi-actor *and* multi-stage), reintroducing the multi-agent framing the English abstract avoids ("multi-step"). Align the Finnish to the English scope or the §1 disclaimer is undercut in the official Finnish summary.
- **[MIN 🟢] Symbol list:** add N_q (and θ_info is in the symbol list — good; make sure the N vs N_q distinction is there too).
- **[MIN 🟢] Citation hygiene:** venue labels are specific and look carefully done (AutoGen = workshop; MemGPT/GraphRAG = preprints; Park et al. [35] is labelled "Generative Agents (UIST 2023)" in text but the reference entry is "Collaborative memory… arXiv 2025" — check that [35] mismatch). Do one final pass on [35] specifically.

> Note the [35] item: §2.5 text attributes "Generative Agents [35] (UIST 2023)" but reference [35] is "Park et al., Collaborative memory… arXiv:2505.18279, 2025." Those are two different papers. Fix the citation or the in-text description. **[MOD 🟢]**

---

## 12. Scholarly polish (optional but raises the grade)

- **Related-work formula:** every §2.x ends with "What is missing in prior work." It is thorough but reads mechanically. Consider varying the closers or consolidating into §2.8.
- **Limitations section is excellent but slightly miscategorized:** the A3 circularity is "now broken by a direct probe" — that means the probe result is a *finding*, not a *limitation*. Move it to results (see §3.3) and leave only the residual (graded-success for distributed tasks) in limitations.
- **Future work has 10 items** — prioritize hard to the 3–4 with real payoff (extended-reasoning regime; faithful per-pipeline cost model; per-task θ_q; r_min sweep). The rest can be a single "additional directions" paragraph.
- **No single clean research question answered cleanly:** the thesis is a portfolio. The "results-summary-first" + "lead with H1" restructure (§1.3) fixes most of this perception.

---

## 13. Suggested revision sequence (so you don't thrash)

1. **Day 1 — credibility pass (all 🟢 BLOCKERS):** items 2.1–2.4, the duplicated abstract, "Chapter Chapter", appendix `*` titles, [35] citation, super-user-bug acknowledgment. These are the things  "one well-identified cell" wording.
4. **Day 4 — H3/H4 pass:** downgrade the cost model; restate H3 as single-stack compress-first dominance; restate H4 as the destruction-driven (deflationary) negative result with the oracle-redaction control foregrounded.
5. **Optional 🟡:** fix the super-user bug; add the audit-verify scaling curve; reposition the bus as the disclosure-metric delivery vehicle.

---

## 14. Likely defense questions (prepare crisp answers)

1. *Why is it called "coordination" when there are no agents in any experiment?*
2. *Your model predicts position with ~35% median error and lands outside its own CI on 11/11 cells — what does it contribute beyond "a cliff exists"?*
3. *Corollary 1's cross-architecture evidence is two models on one cell after every other comparison is excluded or fails TOST. How is that "cross-architecture validation"?*
4. *On family-a, CTR and solver-success are the same measurement. What does family-a actually test?*
5. *If disclosure reduction is monotonic in destruction and matched by trivial field redaction, what is the privacy contribution over "delete more text"?*
6. *P3 "wins" by not compressing and the cost model can't see compression. Isn't the RAG result a null?*
7. *Why build and ship a multi-agent memory bus and never run a multi-agent experiment? What does C4 establish empirically beyond the disclosure metric?*
8. *The reader's YES-bias means H4 measures "flip a no-reader to YES." Is the disclosure metric measuring leakage or the reader's prior?*

For each, your honest body text already contains the answer — the prep is to be able to give the deflated version *first*, calmly, without sounding defensive.

---

## 15. Strengths to preserve (don't over-correct)

When you pull claims down, do **not** sand off these — they are why this is a strong thesis:

- **Pre-registration discipline and honest reframing.** Reporting that 4/6 hypotheses were reframed/unsupported is rare and admirable. Keep it explicit.
- **Statistical rigor:** workload-level bootstrap (not pseudo-replicated), BCa CIs, Holm correction, an actual TOST rather than affirming-the-null. Above master's level.
- **The H1 within/between-family decomposition (Table 4)** — your best methodological argument.
- **The oracle-redaction control (§4.8.5)** and **the A3 probe (§5.6)** — these are genuinely good experimental design; promote them.
- **C1 as a reusable, regeneration-from-seed benchmark** — a real, releasable artefact.
- **Reproducibility package** — one-command targets, determinism scope honestly stated ("in distribution, not byte-for-byte" for frontier).

---

### Bottom line
The work is solid and unusually honest. The grade-limiting factor is not the science — it's that the document advertises more than it delivers, and that several stale numbers from earlier runs survive into the final text. Fix the inconsistencies (credibility), pull the framing down to meet the evidence (lead with H1), and promote your two best controls (oracle redaction, A3 probe) out of the footnotes. Do that and this moves from "good but overclaims" to "rigorous and trustworthy."
