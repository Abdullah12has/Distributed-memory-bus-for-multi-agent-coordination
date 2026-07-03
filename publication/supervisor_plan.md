# Research Plan: The Recombination Gap

**From:** Syed Abdullah Hassan · **For discussion with:** Lauri Lovén
**Date:** 2026-07-03 · **Status:** proposal for sign-off
**Prior work:** Hassan (2026), *The Coordination Cliff: How Context Compression Breaks
Multi-Fragment LLM Workflows*, MSc thesis, University of Oulu (published).

---

## 1. Summary

I propose a follow-up paper that takes the thesis's headline finding (single-fragment
compression fidelity fails to predict, and mis-ranks, compressors for multi-fragment
workflows) and scales it into a **pre-registered measurement study with a released
benchmark and a replacement metric**. Three deltas over the thesis: (i) 8–12 compressors
including the learned and query-aware families the thesis did not test, (ii) 4–6 real
multi-hop corpora at 10–20× the thesis's real-data sample sizes, (iii) a constructive
contribution: critical-token recall (CTR) validated as the metric that *does* predict
multi-fragment failure, shipped as a practitioner tool.

**Target: ICLR 2027** (submission ~late Sep 2026; official dates expected in August),
with a **NeurIPS 2026 workshop paper (~Aug 29)** as an early milestone and **ARR Oct 12 →
ACL 2027/Findings** as the confirmed-date fallback. Timeline: ~12 weeks, starting mid-July.

---

## 2. The paper

**Working title:** *The Recombination Gap: Single-Fragment Fidelity Misranks Prompt
Compressors for Multi-Fragment Workflows.*

**Claim.** Prompt compressors are ranked by single-context QA/summarization fidelity, but
that ranking does not transfer, and often inverts, when information must be recombined
across independently-compressed fragments. The failure is predicted not by average
fidelity but by critical-token recall. We quantify the gap across compressors and
datasets, and release the benchmark and metric that measure it.

**Contributions:**
1. **Benchmark (named, released):** compression-ratio-swept, coordination-scored
   evaluation over independently-compressed fragments; synthetic families + 4–6 real
   multi-hop corpora; HF dataset + data card + one-command harness + leaderboard.
2. **Selection-regret result:** how much coordination a deployer loses by choosing the
   compressor the single-fragment leaderboard recommends, measured across the full
   modern compressor landscape (training-free, learned, query-aware).
3. **CTR as replacement metric + tool:** cross-validated evidence that CTR-at-ratio
   predicts multi-fragment failure where average recall does not, plus a "compression
   safety card" CLI (measure a compressor's CTR curve once → get its safe operating
   ratio per task-density class).
4. **Two scaling findings:** cliff shape vs. task information density across ≥10
   datasets (promoting the thesis's n=3 observation to a relationship), and the first
   multi-pass (N>1) compounding measurements.

**Deliberately out of scope** (kept for separate outputs): the memory bus (→ SoftwareX
artifact paper), CAAC as an algorithm, the formal theorem, and the disclosure/privacy
axis. This paper is empirical; the compounding-error mechanism is used qualitatively.

---

## 3. The gap, and why this publishes

**The gap (verified against the literature corpus collected during the thesis):**
1. **No compression paper evaluates recombination.** Every major method (LLMLingua-1/2,
   LongLLMLingua, Selective Context, RECOMP, PROVENCE, SARA, CPC, xRAG, Gist/ICAE)
   is validated on single-context answer fidelity. RECOMP and xRAG *document* multi-hop
   weakness but treat it as a hard dataset, not a compression regime; none isolates the
   cross-fragment mechanism. Query-aware methods additionally assume the query is known
   at compression time, which fails in memory/cache settings where fragments are
   compressed before the consuming query exists.
2. **No benchmark has a compression axis for multi-fragment tasks.** RULER and LongBench
   vary context *length*; MultiHop-RAG and HotpotQA measure retrieval/QA; MultiAgentBench
   measures coordination with no compression axis.
3. **Agent-memory systems assert what we measure.** AOI (2025) claims compression
   preserves coordination without a ratio sweep; MaaS (2025) and Yu et al. (2026) frame
   memory architecture but run no compression experiments.

**Why it gets accepted:**
- **Not a "compression hurts" paper:** the headline is that the field's *ranking* is
  wrong (decision-relevant regret, inversions), which is a benchmark-validity result.
- **Constructive, not only critical:** CTR + safety card give reviewers and
  practitioners the fix, not just the complaint.
- **Hedged by design:** if the newest query-aware compressors close the gap, the result
  is still a headline ("the gap is a property of cacheable, task-agnostic compression");
  both readings are pre-registered (§6, RH4).
- **Pre-registered (OSF) with a power analysis:** directly addresses the honest-stats
  culture at ICLR/ARR and repairs the thesis's own named pre-specification weakness.
- **Artifact-complete:** released dataset, harness, leaderboard, matching the pattern of
  well-cited eval papers (RULER, LongBench, Lost-in-the-Middle).

---

## 4. Venues (deadlines verified 2026-07-03 against official CFPs)

| Venue | Deadline | Status | Fit |
|---|---|---|---|
| NeurIPS 2026 workshops | ~**Aug 29, 2026** (per-workshop; list out after Jul 11) | CONFIRMED framework | early results + feedback |
| EACL 2027 | ARR **Aug 3, 2026** → commit Oct 11 | CONFIRMED | **excluded: Aug 3 is 4 weeks away**; would force a thesis rehash |
| **ICLR 2027** | ~mid/late Sep 2026 | ESTIMATE (official ~Aug) | empirical/eval papers do well; MemGPT/MetaGPT precedent |
| **ARR Oct 12, 2026** → ACL 2027 / Findings | **Oct 12, 2026** | CONFIRMED (venue mapping TBA) | classic *ACL shape for eval-methodology + benchmark |
| ICML 2027 | ~late Jan 2027 | ESTIMATE | fallback |
| **COLM 2027** | ~late Mar 2027 | ESTIMATE | LM-science venue; strong fit |
| NeurIPS 2027 Evals & Datasets | ~May 2027 | ESTIMATE | natural home if benchmark becomes the headline |

**Top-3 recommendation (in order):**
1. **ICLR 2027** (primary): the 12-week plan lands exactly on its window; the paper
   shape (large empirical study + released benchmark + actionable metric) matches what
   ICLR rewards. *Decision rule:* when official dates land in August, confirm; if the
   deadline falls before ~Sep 15, drop to path 2.
2. **ARR Oct 12, 2026 → ACL 2027 / Findings** (fallback, confirmed date): +2.5 weeks of
   buffer; Findings is a high-probability floor for this paper shape. Note: no concurrent
   submission with ICLR; this is a sequenced fallback, not a parallel track.
3. **COLM 2027** (recovery): if ICLR reviews (Jan 2027) are negative, revise and
   resubmit here (~Mar 2027); COLM's empirical-LM-science scope fits this paper best of
   all three, only its date makes it third.

**Milestone regardless of path:** NeurIPS 2026 workshop submission ~Aug 29 with the core
sweep: stakes the claim and gets external reviews before the main submission.

---

## 5. Experiment plan

**Phase 0: code recovery (weeks 1–2, blocker).** The thesis experiment runners survive
only as compiled bytecode; results/data are intact. Recover runners (decompile, then
clean to release quality; the released harness is a deliverable), and **gate:**
reproduce the thesis's H1/H2 numbers from the archived CSVs before any new run.

**Design.** Fragments compressed **independently** at target ratios r ∈ {1, 2, 3, 4, 6,
8, 12, 16}; a planner must recombine them; coordination scored deterministically (and by
LLM judge where the deterministic scorer does not apply). Per cell: achieved ratio,
average token recall, CTR, single-fragment fidelity, coordination success.

**Two compute tiers** (final scale depends on available compute):

| Axis | Tier A: existing hardware (M4 Pro + RTX 5090 + ~€150 API) | Tier B: with CSC/cloud + ~€1k |
|---|---|---|
| Compressors (8 → 12) | thesis four (LLMLingua-2, truncation, instruction-aware filter, Phi-3-extractive) + Selective Context, LongLLMLingua, RECOMP-extractive, PROVENCE | + SARA, CPC, Perception Compressor, xRAG **or** ICAE (decoder-coupled) |
| Real corpora | HotpotQA (~500), MuSiQue (~300), MultiHop-RAG (~300) | + 2WikiMultiHopQA, FanOutQA; scale to ~1k/corpus |
| Synthetic | C1-v2: 3 thesis families regenerated + 1 new heterogeneous-aggregation family | + multi-tool family |
| Planners | deterministic solver + Llama-3.1-8B (local) + one API model (GPT-4o-mini-class) | + 72B-class + one extended-reasoning model (regime study, sampled) |
| Seeds | 3 | 5 |
| Multi-pass | N ∈ {1, 2} on synthetic | N ∈ {1, 2, 3} incl. real corpora |

Tier A alone supports RH1–RH3 and a credible paper; Tier B adds the compressor-landscape
completeness and the reasoning-model regime that push it from Findings-grade to
main-conference-grade.

---

## 6. Hypothesis-testing plan (pre-registered on OSF before the first new sweep)

| ID | Hypothesis | Metric | Test | Decision criterion |
|---|---|---|---|---|
| **RH1** (confirmatory) | Selecting a compressor by single-fragment fidelity incurs positive coordination regret on multi-fragment tasks | Selection regret: Δpp coordination between fidelity-chosen and coordination-best compressor at matched achieved ratio | Workload-level BCa bootstrap per dataset; Holm across datasets | 95% CI on median regret > 0 in ≥4/6 datasets; report magnitude |
| **RH2** (confirmatory) | CTR predicts coordination out-of-sample; average recall does not add predictive value | AUROC of CTR@r → coordination, leave-one-compressor-out and leave-one-dataset-out | Cross-validated logistic model; bootstrap ΔAUROC (CTR vs. average recall) | ΔAUROC 95% CI > 0 in both CV schemes |
| **RH3** (confirmatory) | The sharp coordination transition generalizes beyond the thesis's four compressors | Relative drop ≥30% with fitted transition | Permutation cliff test + paired Wilcoxon, Holm within compressor family | Significant transition in ≥70% of (compressor × dataset) cells |
| **RH4** (confirmatory, two-sided, both outcomes publishable) | Query-aware compression moderates the gap | Regret difference: query-aware vs. task-agnostic group | Mixed-effects / stratified bootstrap on group contrast | CI excluding 0 in either direction is a finding; CI containing 0 reported as bounded-effect null |
| **RH5** (exploratory) | Multi-pass compression compounds: coordination at N=2,3 < N=1 at matched cumulative ratio | Coordination vs. N at matched achieved ratio | Paired per-workload comparison; descriptive fit of the q^N form | Effect direction + CI; q^N fit quality reported, not claimed |
| **RH6** (exploratory) | Cliff shape scales with task information density | Logistic steepness k and τ* vs. θ_info across ≥10 datasets/families | Spearman with bootstrap CI | Descriptive; promotes the thesis's n=3 observation to n≥10 |

**Protocol.** Statistics at workload level (never per-row); BCa bootstrap CIs throughout;
Holm correction within hypothesis families; power analysis from the thesis's archived
per-cell variance to size instances/seeds for 80% power on a 5pp regret (RH1) before
freezing the pre-registration; all exclusion rules (e.g., compressor achieved-ratio
saturation, planner floor effects p₀ < 0.5) pre-specified: both known thesis failure
modes (Phi-3 ceiling, small-model floors) become pre-registered exclusions rather than
post-hoc rescues.

---

## 7. Timeline (Jul to Oct 2026)

| Weeks | Dates | Work | Milestone |
|---|---|---|---|
| 1–2 | Jul 6–19 | Phase 0: recover runners, reproduce thesis numbers (gate); draft pre-registration; pick benchmark name | repo runs end-to-end |
| 3–6 | Jul 20–Aug 16 | **Core sweep** (Tier A: 8 compressors × core corpora × planners); freeze OSF pre-reg before first sweep | core data in |
| 6 | ~Aug 14 | **Checkpoint with Lauri**: core F1/F3 results; ICLR official dates known by now → confirm path | go/no-go on ICLR |
| 7 | Aug 17–29 | Workshop paper from core results | **NeurIPS 2026 workshop, ~Aug 29** |
| 8–9 | Aug 31–Sep 13 | Stretch sweep (Tier B compressors/corpora), multi-pass, θ_info analysis, safety-card CLI | full grid in |
| 10–11 | Sep 14–25 | Analysis freeze → figures → paper; internal review | **ICLR 2027, ~late Sep** |
| later | Oct 12 | Fallback: ARR October cycle (reformat only, no new experiments) | if ICLR dates land badly |
| later | Jan–Mar 2027 | If ICLR rejects: revise per reviews → COLM 2027 (~Mar) | recovery path |

---

## 8. Relationship to the published thesis

The thesis is cited as the prior work it is; the paper states its delta explicitly.
Differentiation: 8–12 compressors vs. 4; learned + query-aware families vs. training-free
only; 4–6 real corpora at ~10–20× the thesis's real-data n vs. n=30/50; selection-regret
+ CTR-prediction analyses vs. correlation only; multi-pass N>1 vs. N=1; pre-registered vs.
author-run pre-specification; benchmark released vs. proprietary repo. No thesis figure
or table is reused; the C1 generator is re-run and extended (C1-v2). MSc theses do not
count as prior publication at these venues; the overlap is disclosed to editors where
policy asks.

---

## 9. Risks

| Risk | Mitigation |
|---|---|
| "Compression hurting is expected" (reviewer) | Headline is mis-ranking/regret + the CTR fix, not degradation |
| Query-aware compressors close the gap | RH4 two-sided; both outcomes pre-registered as findings |
| Code recovery slower than planned | Two-week box; if exceeded, cut Tier-B compressors before cutting corpora |
| ICLR dates land early | Confirmed fallback: ARR Oct 12 (+2.5 weeks) |
| Compute ask unfunded | Tier A alone supports RH1–RH3; scope statement in the paper adjusts |
| n≈12 compressors too few for rank statistics | Regret (per-instance bootstrap) carries the claim; rank correlation is secondary |
