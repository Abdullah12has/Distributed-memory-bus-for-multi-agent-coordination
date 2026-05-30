# draft3.md — Remediation Plan

Plan for addressing the issues raised in the senior-researcher review of `draft3.md`.
Author-facing working document. Status date: 2026-05-30.

## How to use this plan

Each issue has: **severity**, the **action** required, the **artefacts** to touch,
a **verification** step, and an **effort/route** tag:

- **[WRITE]** — manuscript text only; no data or code touched.
- **[RECONCILE]** — read an existing on-disk CSV/JSON, pick the canonical number, propagate it. No re-run.
- **[RERUN]** — needs new compute (GPU/API). Expensive; for a 1-week thesis sprint prefer *caveat-and-scope* over re-running unless the claim is load-bearing.
- **[SOFTEN]** — the honest fix is to weaken/scope the claim to what the existing data supports, not to generate new data.

**Golden rule for this sprint:** where a fix would otherwise require new experiments,
the default is to *scope the claim down to what the canonical CSVs already show*, not to
run more compute. Every number in the manuscript must trace to one named directory under
`results/`.

---

## Phase 0 — Establish a single source of truth (do this first; everything depends on it)

The single biggest class of problems is that numbers in the prose, the tables, the
abstract, and `CLAUDE.md` disagree. Before editing any prose, build one authoritative
number sheet.

**Task 0.1 [RECONCILE] — Build a canonical number registry.**
Create `results/CANONICAL_NUMBERS.md` (or a small CSV) with one row per headline
number used in the manuscript: claim ID, value, source directory, source file, and the
exact column/JSON key it was read from. Populate it by reading the actual artefacts, not
by copying from `CLAUDE.md` or the draft. Minimum entries:

- family-a × LLMLingua-2 τ\* (the one the frontier arm compares against)
- per-family θ_q (a, b, c) and per-family θ_info (a, b, c)
- H1 Spearman ρ per compressor + CI + n
- H2 per-cell τ\*, drop, p
- frontier τ\* per model + CI + row count
- H3 per-pipeline F1 and EUR per regime
- H4 per-compressor priors/baseline/compr-4× + Δ
- Corollary 2 per-task θ_info and τ\*
- total evaluation-cell count (sum the canonical run row counts)

**Verification:** every later WRITE task cites a row in this registry. If a number isn't
in the registry, it doesn't go in the manuscript.

**Effort:** ~3–4h. Blocks: almost everything below.

---

## Phase 1 — Blocking issues (must fix; thesis is not defensible without these)

### Issue 1 — family-a τ\* reference: 2.5 (canonical) vs 2.70 (frontier baseline)
**Severity: BLOCKING.** The strongest claim ("Qwen-72B 0.8% off") is measured against
`h1_h2_final/` (2.70), which §4.1.1 declares non-canonical; the canonical `h1_h2_v2/`
table says 2.5.

**Action [RECONCILE → WRITE]:**
1. Read family-a × lingua2 τ\* from BOTH `results/h1_h2_v2/` and `results/h1_h2_final/`
   verdict JSONs. Determine why they differ (different ratio grid? different fit? 3- vs
   4-compressor run?).
2. Decide the canonical family-a τ\* and use it *everywhere*: Table 4.2, §4.6.1 reference,
   Table 4.5, abstract.
3. Recompute the Qwen-72B and DeepSeek relative differences against the canonical value.
   If Qwen-72B is now ~7% off rather than 0.8%, **rewrite the claim honestly** — 7% across
   a 9× scale change is still a strong invariance result; it does not need to be 0.8%.
4. If you keep 2.70, you must justify in-text why the frontier arm uses `h1_h2_final/`
   and ideally re-run the frontier comparison's reference fit on `h1_h2_v2/` for parity.

**Artefacts:** §4.6.1–4.6.2, Table 4.2, Table 4.5, abstract, §5.3.
**Verification:** grep the manuscript for every occurrence of `2.5`, `2.68`, `2.70`, `0.8%`
and confirm each traces to the registry.
**Effort:** 3h. **Route:** RECONCILE + WRITE (no re-run unless you choose option 4's parity fit).

### Issue 2 — Qwen-2.5 has no 3.8B or 8B variant
**Severity: BLOCKING (factual error + Corollary 1 confound).** Qwen-2.5 sizes are
0.5/1.5/3/7/14/32/72B. "3.8B" is Phi-3-mini; "8B" is Llama-3.1.

**Action:**
1. **[RECONCILE]** Determine from `results/h5_final/` manifests / config which models were
   *actually* run in the local scaling sweep. Three sub-cases:
   - **(a)** It really was Qwen-2.5 at 1.5B / **3B** / **7B**, and the draft has typos →
     **[WRITE]** correct the sizes everywhere. Easiest, best outcome.
   - **(b)** It was Qwen-1.5B + Phi-3-3.8B + Llama-8B (three families) → the local arm is
     **cross-architecture, not a parameter-count ladder**. You must **[WRITE]** re-describe
     Corollary 1's local arm as cross-architecture evidence and **remove** the "9× parameter
     count within a family" reading from the *local* sweep (the within-family scale claim
     then rests only on the Qwen-8B→72B step — but 8B isn't Qwen either, so see (c)).
   - **(c)** If the 8B→72B "same family" step is actually Llama-8B→Qwen-72B, the
     within-family invariance claim is unsupported and must be **[SOFTEN]**ed to
     cross-architecture invariance only.
2. Propagate corrected identities to abstract, C2, §3.7, §4.5, §4.6, §5.4.2, Appendix D.3.
3. Confirm "DeepSeek V4 Pro" is a real, correctly-named model (GPT-oss-120B verified real;
   DeepSeek V4 not yet verified). If misnamed, correct it.

**Verification:** model-card JSON / Ollama tags in the results manifests; cross-check each
named size against the vendor's actual release list.
**Effort:** 2–4h depending on sub-case. **Route:** RECONCILE + WRITE (no re-run).

### Issue 3 — Table 4.3 (P3 ≫ P1) contradicts the "~1 pp" prose
**Severity: BLOCKING (internal contradiction inverts the C3 conclusion).**

**Action [RECONCILE → WRITE]:**
1. Read `results/h3_final/` and confirm the true per-pipeline F1s. Two outcomes:
   - If P3 really beats P1 by 25–42 pp, the **headline is wrong**: rewrite §4.7 and §5.4.1
     so P3 (joint routing) is the leading pipeline, and reframe "compress-first dominance"
     as "compress-first beats retrieve-first (P1>P2), and joint routing beats both." The
     P1>P2 finding survives; the "P3 only adds ~1 pp" claim must be deleted.
   - If the table is wrong (e.g., P3 numbers are from a different metric/regime), fix the
     table from the CSV.
2. Reconcile every "~1 pp" / "small margin" phrase (§4.7.2, §4.7.3, §5.4.1) with the table.
3. Note the EUR costs are near-identical across pipelines — **[SOFTEN]** the "EUR-per-workflow
   cost model" framing to acknowledge cost is not the discriminating axis here; F1 is.

**Verification:** recompute P1−P2 and P3−P1 gaps and CIs from the CSV; confirm signs and magnitudes.
**Effort:** 2–3h. **Route:** RECONCILE + WRITE.

### Issue 4 — "Relative drop" column values > 1.0, and τ\* grid-quantization
**Severity: BLOCKING (uninterpretable / contradicts the 30% predicate).**

**Action:**
1. **[RECONCILE]** Open the H2 verdict computation. Determine what "rel. drop" actually is
   (values 1.61, 1.60, 1.36 cannot be fractional drops). Likely it's an absolute logit
   delta, a pre/post ratio, or a slope. Rename the column to what it is, OR convert to a
   true relative drop in [0,1] and re-check the "≥30%" predicate against it.
2. **[WRITE]** Address the τ\*=2.5 clustering: 2.5 is the midpoint of the {2,3} grid gap and
   repeats across 5 cells. State explicitly that piecewise-fit τ\* positions are
   **grid-resolution-limited** (your bug list #8 already documents this failure mode), that
   the *existence and significance* of the drops are robust but the *position* is quantized
   to ±0.5 ratio units, and report the bootstrap CI on τ\* so the uncertainty is visible.
3. Consider denser ratio sampling near the cliff as **[RERUN, optional/future-work]** —
   for the thesis, the caveat is sufficient.

**Verification:** recompute the drop column from raw coord_success curves for two cells by hand.
**Effort:** 3h. **Route:** RECONCILE + WRITE.

---

## Phase 2 — Major analytical issues (fix or the contribution weakens under questioning)

### Issue 5 — Corollary 2: HotpotQA is a position counterexample; n=3; circular θ_info
**Severity: MAJOR.**

**Action [SOFTEN, primarily WRITE]:**
1. State plainly that cliff *position* (τ\*) is **not monotonic** in θ_info across the three
   tasks (HotpotQA, the most distributed, cliffs earliest). Do not let §4.9.2 quietly
   redefine the claim.
2. Reframe Corollary 2 around what the data *does* support: θ_info correlates with the
   **shape/gradualness** of degradation (AUC-based), explicitly acknowledging that because
   θ_info is *defined* from the AUC this is a descriptive summary, not an independent
   prediction. Drop any "predicts cliff position" language for Corollary 2.
3. Acknowledge n=3 tasks is too few for a "scaling" claim; downgrade "scaling law" to
   "preliminary cross-benchmark observation." Name a 4th/5th benchmark as future work.
4. Optional **[RERUN]**: add one more real benchmark (e.g., 2WikiMultiHopQA, which you
   already cite) to make n=4 and test whether the shape-ordering holds. Only if compute allows.

**Verification:** plot τ\* vs θ_info for the 3 points; confirm non-monotonicity is stated.
**Effort:** 3h WRITE (+ ~2h compute if adding a benchmark). **Route:** SOFTEN/WRITE.

### Issue 6 — H4 metric cannot separate privacy from general destruction
**Severity: MAJOR (construct validity).**

**Action:**
1. **[RECONCILE]** Pull truncation's disclosure number (it's missing from Table 4.4) and the
   per-compressor *coordination* numbers at 4×. Build the key comparison: does disclosure
   drop *more* than task-relevant information for filter/lingua2 than for truncation?
2. **[WRITE]** Add truncation to Table 4.4 (or explain its omission). If truncation also
   shows low disclosure *and* collapsed coordination, state that disclosure reduction
   partly reflects information destruction, and that the *privacy-relevant* claim is the
   **disclosure-vs-coordination trade-off** (per-compressor position on `privacy_quality.pdf`),
   not the raw disclosure drop. Reframe H4's contribution as "compressors differ in
   disclosure *at iso-coordination*," which is the defensible, useful claim.
3. **[WRITE]** Keep the reader-bias caveat but elevate it from footnote to a validity
   paragraph; the metric measures "flip a NO-biased reader to YES," and you should say what
   that does and does not establish about a capable adversary.
4. Optional **[RERUN, future-work]**: unbiased/larger reader (already named in §5.6).

**Verification:** the iso-coordination disclosure ordering is computable from existing CSVs.
**Effort:** 3–4h. **Route:** RECONCILE + WRITE.

### Issue 7 — Frontier sample size 1,500 vs 180; DeepSeek seed contradiction; vacuous CI
**Severity: MAJOR.**

**Action [RECONCILE → WRITE]:**
1. Read the actual row counts in `results/frontier_qwen72b/`, `frontier_deepseekv4/`.
   Reconcile against the "1,500 cells per model" claim in §4.6.1 (likely the sweep used
   fewer ratios/seeds than stated). Correct the protocol description to match reality.
2. Fix the internal contradiction: §4.6.1 says 5 seeds for all; §4.6.3 says DeepSeek used
   fewer. State the true per-model seed/ratio/workload counts in a small table.
3. **[SOFTEN]** the DeepSeek CI [1.76, 7.14] claim: a CI that wide "containing" 2.70 is
   "not inconsistent with invariance," not a positive validation. Say so. The Qwen-72B
   point is the real evidence; DeepSeek is corroborating-but-underpowered.

**Verification:** `wc -l` / row count of the frontier CSVs vs the stated cell count.
**Effort:** 2h. **Route:** RECONCILE + WRITE.

### Issue 8 — H1 framing: "decorrelation" vs strong anti-correlation; arbitrary 0.6
**Severity: MAJOR (conceptual clarity of the lead contribution).**

**Action [WRITE]:**
1. Reframe H1's headline as **"compressors disagree on the sign of the QA↔coordination
   relationship"** — filter is strongly *negative* (−0.59), the others weakly positive.
   This is stronger and more accurate than "all below 0.6."
2. Justify or replace the 0.6 threshold. If you keep it, cite a source for "0.6 = moderate
   correlation" and frame H1 as "QA-F1 is not a *reliable* predictor (sign-unstable across
   compressors)," not "QA-F1 is uncorrelated."
3. Separate the two phenomena in the interpretation: weak-positive (QA-F1 carries some but
   insufficient signal) vs strong-negative (QA-F1 is actively misleading for the filter).

**Verification:** none beyond the existing Table 4.1 numbers.
**Effort:** 2h. **Route:** WRITE.

---

## Phase 3 — Consistency, scoping, and honesty alignment

### Issue 9 — θ_info / θ_q possible conflation for family-c (both = 0.59)
**[RECONCILE]** Read family-c θ_info (`estimate_task_theta`) and θ_q (`derive_theta`) from
the canonical JSONs. If genuinely both ≈0.59, add a footnote noting the coincidence; if a
copy error, fix it. **Effort:** 1h.

### Issue 10 — Reproducibility overclaims (commodity HW; byte-identical CSV)
**[WRITE]** (1) Qualify "single command on commodity hardware" — the cached/local pipeline
is laptop-reproducible; cache precompute needs the GPU host and the frontier arm needs paid
API credentials. (2) Delete or scope "byte-identical CSV" — true only for the
deterministic/cached local pipeline; frontier API calls are not byte-reproducible. State
which targets are deterministic and which are not. **Effort:** 1h.

### Issue 11 — Abstract/intro "predicts cliff position" vs 25–33% match rate
**[WRITE/SOFTEN]** Align the abstract verb with §4.4.4. Use "estimates / first-order
predictor with a quantified match rate (33% strict, 67% at ±50%)" rather than unqualified
"predicts." Carry the LOO numbers (25%/75%) into the abstract or at least the contributions.
**Effort:** 1h.

### Issue 12 — In-regime vs out-of-regime cells blended in the 33% match rate
**[RECONCILE → WRITE]** Report the match rate on the three token-level compressors
(in-A1-regime) separately from the phi3-extractive robustness cells. You already flag phi3
violates A1; don't then average it into the headline. **Effort:** 1–2h.

### Issue 13 — "~100,000 evaluation cells" likely ~2× overstated
**[RECONCILE → WRITE]** Sum the row counts of the canonical runs (h1_h2_v2 27k + h5 9k +
h6 1.5k + caac 13.5k + h3 + h4 + frontier + hotpotqa). Replace the abstract figure with the
true sum, or change "approximately one hundred thousand" to the verified number. **Effort:** 0.5h.

### Issue 14 — family-b "floor effect" vs family-b cliff cells (planner-dependent)
**[WRITE]** Make explicit, at first mention, that family-b *is* solvable (and cliffs) under
the **deterministic regex solver** (H1/H2) but *floors* under small **LLM planners**
(Corollary 1). The "floor effect" is planner-specific. State how θ_q^(b)=0.838 was derived
given the floor (it's derived on the regex-solver curve, not the LLM curve). **Effort:** 1h.

---

## Phase 4 — Citations and scholarly hygiene

### Issue 15 — Citation corrections [WRITE, ~half a day total]
1. **MultiHopRAG** → add a **Tang & Yang (2024)** reference entry and cite it; stop
   attributing MultiHopRAG to **[Addison 2024]** (which is CFedRAG). Fix §2.6, §4.9, Table 4.5.
2. **Selective Context** → cite **Li et al. (2023, EMNLP)**, not **[Cheng 2024]** (xRAG).
   Fix §2.4.2 and the comparison table.
3. **RECOMP** (Xu et al. 2023/2024) → add a reference entry or remove the named citation.
4. **2WikiMultiHopQA** (Ho et al., COLING 2020) → add a reference entry.
5. **NIST AI RMF** → either find the correct source for a PUBLIC<…<SECRET classification
   lattice (a data-classification standard, not the AI RMF) or stop attributing the lattice
   to NIST AI RMF. Fix §3.1.4, §3.4.3, Appendix A, and the abbreviation table.
6. **§1.6 "seven strands"** vs the five enumerated vs eight subsections → make the count
   consistent with §2's actual structure.
7. Sweep all bracketed citations against the reference list for orphans
   (cited-but-not-listed) and unused entries.

**Verification:** script or manual pass extracting every `[Author Year]` token and diffing
against the reference list; confirm every dataset/method is cited to its *originating* paper.

---

## Phase 5 — Theory vulnerabilities to pre-empt in the defense (mostly WRITE)

### Issue 16 — A3 circularity
**[WRITE]** You already concede it; strengthen the framing: describe the hand-curated
token-deletion probe (§5.6) as the experiment that would *falsify* A3's threshold–sigmoid
shape, not merely illustrate it. Make clear the cliff's *existence* is model-agnostic; A3 is
only the tractable *explanation*. This is acceptable for a thesis if framed as known-open.

### Issue 17 — "lattice" precision
**[WRITE, minor]** A total order PUBLIC<…<SECRET is a chain; combined with the OR-mask it
forms a product lattice. Tighten the wording or define the join explicitly. Low priority.

---

## Suggested sequencing (1-week sprint)

| Day | Work |
|---|---|
| 1 | Phase 0 (number registry). Issue 1 (τ\* reconcile), Issue 2 (model identities) — both RECONCILE from `results/` manifests. These two unblock the abstract. |
| 2 | Issue 3 (H3 table vs prose), Issue 4 (drop column + τ\* quantization), Issue 7 (frontier counts). All RECONCILE+WRITE. |
| 3 | Issue 5 (Corollary 2 reframing), Issue 6 (H4 validity), Issue 8 (H1 framing). Mostly WRITE/SOFTEN. |
| 4 | Phase 3 consistency cluster (Issues 9–14). |
| 5 | Phase 4 citations (Issue 15) + Phase 5 theory framing (16–17). |
| 6 | Full read-through: grep every number against the registry; rebuild figures from canonical CSVs; recompile LaTeX. |
| 7 | Buffer / optional RERUNs if compute allows (denser cliff sampling, 4th benchmark, unbiased H4 reader). |

## Decision points that need YOUR input (cannot be resolved from the draft alone)

1. **Issue 2 sub-case:** which models did the local scaling sweep actually run? This
   determines whether Corollary 1's local arm is a parameter ladder or cross-architecture.
2. **Issue 1:** keep 2.70 (and justify/re-fit) or move everything to the canonical 2.5
   (and rewrite the 0.8% claim)?
3. **Issue 3:** is Table 4.3 correct (→ P3 is the headline) or is the prose correct
   (→ table is wrong)?
4. **Scope:** for Issues 5/6, do you have compute budget for any RERUN, or is everything
   SOFTEN-to-existing-data?

## What NOT to do
- Do not re-run experiments to "rescue" a predicate the data doesn't support. The reframing-
  to-corollary pattern you already use is the correct, examiner-respected move.
- Do not tighten the abstract's confidence to paper over the honest limitations in §5.3 —
  move the limitations' honesty *up* into the abstract instead.
