# Publication Plan — Follow-up Paper from the "Coordination Cliff" Thesis

**Author:** Syed Abdullah Hassan · **Date:** 2026-07-03
**Baseline (do-not-duplicate):** Hassan, S. (2026). *The Coordination Cliff: How Context
Compression Breaks Multi-Fragment LLM Workflows.* MSc thesis, University of Oulu. **Published.**

---

## 0. TL;DR (the recommendation)

Build **one** new paper on the thesis's own headline result — **single-fragment
compression quality does not predict, and actively mis-ranks, compressors for
multi-fragment workflows** — and turn it from a 4-compressor / 150-instance MSc finding
into a **large-scale measurement study + released benchmark**:

- **10–12 compressors** incl. the *learned* and *query-aware* families the thesis never
  tested (LongLLMLingua, RECOMP, PROVENCE, SARA, xRAG, Gist/ICAE, Selective Context, CPC),
- **several real multi-hop corpora at scale** (HotpotQA, 2WikiMultiHopQA, MuSiQue,
  MultiHop-RAG, FanOutQA) alongside a bigger synthetic C1,
- the **money figure**: deployer *selection regret* — how many pp of coordination you
  lose by picking the compressor the single-fragment leaderboard recommends,
- the **positive contribution** (not just critique): **critical-token recall (CTR)** as
  the cheap compressor-side metric that *does* predict multi-fragment failure, shipped as
  a "compression safety card" tool,
- two near-free scaling findings: **θ_info → cliff-shape** across ≥10 datasets, and
  **multi-pass (N>1)** compounding (thesis-named future work).

**Leave out** the memory bus, CAAC, and the formal theorem (the thesis's weak links) —
they become *separate* spin-off outputs, not this paper's spine. That keeps the paper
clean, high-probability, and clearly **different** from the published thesis.

**Venues (deadlines verified 2026-07-03; detail in §5 and `supervisor_plan.md`):**
EACL 2027 turned out to be fed by ARR **Aug 3, 2026** — too soon; excluded. Primary
**ICLR 2027** (~late Sep 2026, official dates ~Aug); fallback **ARR Oct 12, 2026 →
ACL 2027/Findings** (confirmed date); de-risk **NeurIPS 2026 workshop (~Aug 29)**;
recovery **COLM 2027** (~Mar).

**Before any of this works: recover the experiment code** — the runners are `.pyc`-only
(source was stripped). See §7 (Step Zero).

---

## 1. What the thesis already published (the baseline we must differ from)

| Piece | Thesis status | Strength |
|---|---|---|
| **H1** — single-fragment retention F1 fails to predict / mis-ranks coordination | Headline, SUPPORTED | **Strong.** ρ (workload-level): filter −0.818, phi3 +0.315, lingua2 +0.026, trunc +0.051. At 4×/family-a, QA-F1 ranks phi3>filter>trunc>lingua2 but coordination is 0.40 for phi3, **0.00 for the other three** — the ranking inverts. |
| **H2** — a sharp coordination cliff τ* exists | SUPPORTED 11/12 cells | **Strong.** LLM-planner τ*≈2.5–2.7; family-c ≈5–6.7. Permutation + Wilcoxon, Holm. |
| **Compounding-error model** (P(succ)≤p₀·q^N, cliff at q(τ*)=θ_q^{1/N}) | "Model", not theorem | **Weak.** In-sample match 33% (≤25% err); **bootstrap-CI coverage 0/11**; median rel-err 35%. Supervisor audit found the load-bearing inequality mis-stated. |
| **Corollary 1** — cliff position invariant to planner scale/architecture | "No shift detected" | **Underpowered.** TOST equivalence *fails* (Qwen 22%, DeepSeek 6% of bootstrap in ±20% band). Carried by one Qwen-72B cell. |
| **Corollary 2** — cliff *shape* tracks task info-density θ_info | Empirical, n=3 | Suggestive. θ_info: C1-a 0.97, MHR 0.48, HotpotQA 0.37. Position does **not** transfer (MHR τ*=11.3). |
| **H3** — RAG pipeline placement (P1/P2/P3) | NOT supported → appendix | Negative (effect 2–3.2pp < 5pp bar). |
| **H4** — summary-level inference disclosure | SUPPORTED 3/4 | Signal +28.6pp; reductions 18.9–24.6pp; but **destruction-driven** (oracle redaction matches), phi3 n.s. |
| **CAAC** — cliff-aware backoff wrapper | Ch.5 / future work | **0/7 strict Pareto by design**; weak dominance only. |
| **Memory bus** — FastAPI + SQLite(WAL) + FAISS-CPU + scratchpad | Engineering payload | Real but single-host; microbench only (write ~0.047ms, ~18k ops/s). |

**Scope facts:** 4 training-free compressors + identity; 150 synthetic C1 instances (3
families × 50); 10 ratios; 5 seeds; **N=1 everywhere**; H1–H4 use a *deterministic* solver
(no generative planner); only the frontier arm touches large models (Qwen-72B, DeepSeek-V4,
GPT-oss-120B) and only on family-a. Compute: one Apple M4 Pro 48GB + one RTX 5090 32GB.

---

## 2. The contribution to build on — and why

**Build on H1 (the mis-ranking finding), mechanistically anchored by H2 (the cliff).**

Reasoning:
1. **The thesis says so.** Its own hierarchy makes H1 "the central, load-bearing result,"
   with the cliff as its mechanism and everything else "deliberately secondary."
2. **It attacks the whole field's evaluation practice.** Every major compressor
   (LLMLingua-2, LongLLMLingua, RECOMP, PROVENCE, SARA, xRAG, Selective Context) is
   validated on single-context QA/summarization fidelity. The lit review confirms **no
   compression paper evaluates whether independently-compressed fragments can be
   recombined to solve a task** — multi-hop is treated as a hard dataset, not a distinct
   compression regime. This is a clean, citable, field-level gap.
3. **It's the most robust part of the thesis** (large n, tight CIs, independent recompute)
   and the most *under-explored* — only 4 training-free compressors were tested. The
   surprising claim ("compressors that ace QA fail coordination") becomes far stronger
   when it holds across *learned* and *query-aware* compressors too.
4. **It has a natural "so what" for practitioners:** a benchmark + a rule ("measure
   critical-token recall, not average fidelity") that changes how people pick compressors.

**Why not the alternatives (for *this* paper):**
- *Theory-first* (promote the model to a real theorem): the audit found the central
  inequality wrong; 0/11 CI coverage. High-risk, long. → §6 spin-off / future.
- *Method-first* (CAAC): 0/7 strict Pareto; the win doesn't exist yet. → §6 spin-off.
- *Systems* (memory bus): single-host microbench; least novel. → §6 SoftwareX artifact.
- *Privacy* (H4): destruction-driven, construct-validity-limited. → §6 AISec, after a defense.

---

## 3. The differentiation contract (mandatory — the thesis is published)

The paper **must not** be re-run of the thesis. Non-negotiable deltas, each of which is
independently a reviewer-visible novelty:

| Axis | Thesis | This paper |
|---|---|---|
| Compressors | 4 training-free | **10–12**, adding learned (RECOMP, ICAE/Gist, xRAG), query-aware (LongLLMLingua, PROVENCE, SARA), self-info (Selective Context), sentence-level (CPC, Perception Compressor) |
| Framing | Systems thesis w/ memory bus + CAAC | **Field-level eval-methodology + benchmark** paper; no bus, no CAAC |
| Benchmark | 150 synthetic + 30/50 real | **Released** benchmark: larger synthetic C1 + **5 real multi-hop corpora at scale**, data card, public protocol |
| Real-data transfer | Weak (n=30 MHR, n=50 HotpotQA) | Hundreds/thousands of instances; multiple corpora |
| Passes | N=1 only | **N>1 multi-pass** experiment (thesis-named future work) |
| Headline analysis | ρ decorrelation | **Selection regret** (pp coordination lost choosing by the single-fragment leaderboard, per dataset, bootstrap CIs) + rank scatter; Kendall τ secondary |
| Contribution type | Measurement only | Measurement **+ replacement metric** (CTR as validated predictor) **+ practitioner tool** (safety card) |
| Planner | Deterministic solver for H1/H2 | Deterministic solver **and** LLM planner across scales, reported side-by-side |
| Stats | Underpowered invariance/theory | Pre-registered power analysis; properly powered claims or honest nulls |

Cite the thesis explicitly as prior work and state the delta in the intro. (Anonymize for
review per each venue's dual-submission / self-plagiarism policy — a published MSc thesis
is generally *not* a blocking prior publication at these venues, but disclose it.)

---

## 4. The paper

**Working title (pick one; do NOT reuse "The Coordination Cliff"):**
1. *"The Recombination Gap: Single-Fragment Fidelity Misranks Prompt Compressors for
   Multi-Fragment Workflows"* ← **recommended** — coins a citable term (the
   *Lost-in-the-Middle* playbook) while carrying the finding in the subtitle
2. *"Compression Benchmarks Mislead: Single-Fragment Fidelity Does Not Predict
   Multi-Fragment LLM Performance"* (pure critique lead — weaker: no coinage, no offer)
3. *"<BenchmarkName>: Measuring Context Compression Under Cross-Fragment Recombination"*
   (benchmark-led — right shape for NeurIPS D&B if that becomes the venue)

**Benchmark needs a name** (impact multiplier — people cite names): candidates
*RecombBench*, *FragBench*, *MultiFrag*. Pick one, use it everywhere.

**One-sentence thesis:** *Prompt compressors are ranked by single-context QA fidelity, but
that ranking does not transfer — and often inverts — when information must be recombined
across independently-compressed fragments; the failure is predicted not by average
fidelity but by critical-token recall, which we validate as the metric to report, and we
release the benchmark + tool that measure it.*

**Framing note — critique alone caps impact.** A "your metric is wrong" paper gets read
once; a "report this metric instead" paper gets *used*. CTR is therefore promoted from
mechanism-figure to co-headline contribution, with a practitioner artifact (E11).

**Heads-we-win on the new compressors (E1):** if query-aware compressors (LongLLMLingua,
PROVENCE, SARA) *also* mis-rank → the gap is universal (strongest result). If they *close*
the gap → the finding becomes "the recombination gap is a property of task-agnostic /
cacheable compression — query-awareness fixes it at the price of per-query recompression
(no caching)." Either outcome is a headline; write the intro so both fit.

**Core claims / figures (the paper's spine):**
- **F1 — selection regret (money figure):** scatter of single-fragment fidelity vs
  multi-fragment coordination per compressor per dataset; headline number = pp
  coordination lost when choosing by the single-fragment leaderboard (bootstrap CIs).
  Kendall τ reported as secondary (n≈12 compressors is too few to carry the claim alone).
- **F2 — the cliff, generalized:** coordination vs ratio across the expanded compressor
  set and real corpora; sharp transition persists.
- **F3 — CTR as the replacement predictor:** critical tokens drop faster than average
  (mechanism), and CTR@ratio predicts coordination out-of-sample across compressors ×
  datasets where average recall does not (cross-validated regression / AUROC). *The
  positive contribution.*
- **F4 — multi-pass (N>1):** compounding across passes (new).
- **F5 — θ_info scaling:** cliff shape (logistic k, τ*) vs task information density
  across ≥10 datasets/families — Corollary 2 promoted from n=3 anecdote to a scaling
  relationship, nearly free on top of E2.

**Deliverables (productize or the benchmark won't get adopted):** named HF dataset +
data card; pip-installable eval harness (one command per figure); public leaderboard
table in the README; the safety-card CLI (E11).

**Explicitly out of scope for this paper:** memory bus, CAAC, disclosure/privacy, the
formal theorem. Mention the cliff mechanism qualitatively; don't stake the paper on the
q^N equation (see §8).

---

## 5. Venue analysis & recommendation

### Deadline reality check (verified against official CFPs, 2026-07-03)

COLM 2026 (~March) and ACL/EMNLP/NeurIPS 2026 main-track (~Feb–May) deadlines have
**already passed**. Key verified fact: **EACL 2027 is fed by the ARR Aug 3, 2026 cycle**
(commitment closes Oct 11 — before the Oct 12 ARR cycle opens), so the originally-planned
"ARR Oct → EACL 2027" path does not exist, and Aug 3 is too soon for the differentiation
sweep. The live ladder:

| Venue | Deadline | Status | Role |
|---|---|---|---|
| **NeurIPS 2026 workshops** | ~**Aug 29, 2026** (per-workshop; accepted-workshop list out after Jul 11) | CONFIRMED framework | **De-risk** — core results, external feedback |
| EACL 2027 | ARR **Aug 3, 2026** → commit Oct 11 | CONFIRMED | **Excluded** — 4 weeks away; would force a thesis rehash |
| **ICLR 2027** | ~mid/late Sep 2026 | ESTIMATE (official ~Aug) | **Primary** — 12-week plan lands on its window; empirical/eval fit; MemGPT/MetaGPT precedent. Decision rule: if the official deadline lands before ~Sep 15, drop to ARR |
| **ARR Oct 12, 2026** → ACL 2027 / Findings | **Oct 12, 2026** | CONFIRMED (venue mapping TBA) | **Fallback** (+2.5 wks). No concurrent submission with ICLR — sequenced, not parallel |
| **ICML 2027** | ~late Jan 2027 | ESTIMATE | Fallback |
| **COLM 2027** | ~late Mar 2027 | ESTIMATE | **Recovery** after ICLR reviews (~Jan 2027); best topical fit, latest date |
| **NeurIPS 2027 Evals & Datasets** | ~May 2027 | ESTIMATE | Fallback; natural home if the benchmark becomes the headline |

**Common risk at all of them:** "compression hurts, obviously" — answered by the
selection-regret framing (the field's *ranking* is wrong, not just degraded) and by CTR
as the constructive fix.

### Spin-off outputs (separate papers, not this one — cover the rest of your venue list)
- **SoftwareX / JSS / IEEE Access** — an **artifact/tool paper** on the memory bus +
  released benchmark harness. Low novelty bar, reuses existing code, good "second output."
  (Needs the concurrent/networked benchmark the thesis lacks to be more than a microbench.)
- **AISec (CCS workshop) / ACM SACMAT / RAID** — a **security paper** on "compression as an
  inference-disclosure side-channel in agentic memory," *after* building a real defense
  (current H4 is destruction-driven, not a privacy mechanism). Future, not now.
- **NeurIPS/ICML main track / TMLR** — only if the theory is genuinely repaired (§8);
  high-risk, treat as a later, separate theory paper.

**Recommendation:** NeurIPS-2026 workshop (~Aug 29) for de-risk + feedback; **ICLR 2027
primary** (confirm when official dates land in August); **ARR Oct 12** fallback; **COLM
2027** recovery after ICLR reviews. Do the SoftwareX artifact paper opportunistically
(cheap). Defer AISec and any theory-track paper. Full supervisor-facing version:
`publication/supervisor_plan.md`.

---

## 6. New experiments (the "run more experiments" ask)

Priority: **P0** = paper doesn't exist without it; **P1** = strongly expected by reviewers;
**P2** = strengthens.

| ID | Experiment | Priority | Why / delta vs thesis | Rough effort |
|---|---|---|---|---|
| E1 | **Add learned + query-aware compressors** (RECOMP-extractive/abstractive, LongLLMLingua, PROVENCE, SARA, Selective Context, CPC; stretch: xRAG, Gist/ICAE) to the H1/H2 sweep | **P0** | Thesis only had 4 training-free; the mis-ranking claim must survive the *whole* compressor landscape | ~2–3 wks eng + GPU sweep |
| E2 | **Scale real multi-hop corpora**: HotpotQA, 2WikiMultiHopQA, MuSiQue, MultiHop-RAG, FanOutQA — hundreds+ instances each, C1-style reformulation | **P0** | Thesis real-data was n=30/50 and weak; external validity is the #1 reviewer attack | ~2 wks eng + GPU |
| E3 | **Selection-regret analysis (F1)**: per dataset, pp coordination lost when choosing the compressor the single-fragment leaderboard recommends (at matched budget), bootstrap CIs; fidelity-vs-coordination scatter; Kendall τ as secondary | **P0** | The paper's central figure; regret is decision-relevant and statistically honest where τ over n≈12 compressors is not | ~3–4 days analysis |
| E4 | **CTR as replacement predictor (F3)**: critical tokens lost faster than average (mechanism) + cross-validated test that CTR@ratio predicts coordination out-of-sample across compressors × datasets where average recall does not | **P0** | Upgraded from mechanism-figure to the paper's *positive* contribution — the metric the field should report | ~4–5 days analysis |
| E5 | **Multi-pass N>1 (F4)**: compress→solve→compress→solve for N=2,3; test compounding | **P1** | Thesis is N=1 everywhere; this is its named future work and tests the q^N story directly | ~1 wk eng + GPU |
| E6 | **LLM planner across scales for H1/H2** (not just deterministic solver), incl. ≥1 frontier API model | **P1** | Thesis used deterministic solver for the headline; reviewers want a real generative planner | ~1 wk + API budget |
| E7 | **Pre-registered power analysis + seed/instance scale-up** (enough seeds/instances for the CIs the claims need) | **P1** | Thesis chose 5 seeds/50 instances "at budget," no power analysis | analysis + more GPU |
| E8 | **Task-family diversity**: heterogeneous aggregation + one multi-tool family beyond a/b/c | **P2** | family-a is 50× "sum of 8 numbers"; reviewers will flag homogeneity | ~1 wk eng |
| E9 | **Reasoning-model regime**: characterize the cliff for extended-reasoning planners (the GPT-oss out-of-regime case) | **P2** | Thesis scoped these out; turning the exception into a mapped regime is genuinely new | API budget |
| E10 | **θ_info scaling study (F5)**: compute info-density + cliff shape (logistic k, τ*) across all ~10 datasets/families from E2; test the shape–density relationship | **P1** | Promotes thesis Corollary 2 from n=3 anecdote to a scaling relationship; **near-free** on top of E2 (analysis only) | ~2–3 days analysis |
| E11 | **Compression safety card (tool)**: small CLI — measure a compressor's CTR-vs-ratio curve on ~100 task fragments → emit its safe max ratio per task-density class | **P1** | The practitioner artifact that gets the paper *used*; resurrects CAAC's operating-point insight as measurement, minus its 0/7-Pareto baggage | ~3–4 days eng |

**Compute reality:** the thesis ran on one M4 Pro + one RTX 5090. E1–E2 at scale (12
compressors × 6 datasets × ratios × seeds, with an LLM planner) is **well beyond** that
envelope. Budget for a cloud GPU (A100/H100) window and an API spend line (frontier
planners). This is the main cost driver — quantify it before committing to a deadline.

---

## 7. Step Zero — recover the code (blocker)

The load-bearing runners **exist only as `.pyc` bytecode** (source stripped in commits
`d753ed5`/`195ad26`/`e0e9e4d`): `run_h1_h2`, `run_h3`, `run_h4`, `run_h5`, `run_h6`,
`run_caac`, `run_frontier`, `theory/cliff_prediction.py`, `compressors/caac.py`, and 2/3 C1
generators (`fact_aggregation`, `multi_step_retrieval`). Result CSVs/JSONs and generated
data survive.

Options: (a) **decompile** the `.pyc` (`decompyle3`/`pycdc`) and clean up — fastest; (b)
**rewrite** the runners from the CSV schemas + CONTEXT.md + configs — slower but yields
publishable, releasable code. Given a benchmark *release* is the point, plan for (b)-quality
even if starting from (a). **Do this first; nothing else runs until it's done.**

---

## 8. Statistics & theory fixes (if any theory is included)

From the supervisor's proof audit — apply before making *any* formal claim:
- **Drop / restate the bound.** The Markov step yields `p₀·q^N/θ`, not the stated
  `p₀·q^N`. Either present only the Markov form or **lead with the Hoeffding concentration
  bound** (which *is* correct and explains sharpness: transition half-width ≈ 1.07/√M — and
  fix the factor-2 prose error).
- **Break the θ circularity:** θ_q is derived from the cliff then used to predict it. Use
  strict leave-one-family-out / held-out estimation; report a predicted-τ* **band**, not a
  point.
- **Make invariance falsifiable:** report the TOST honestly (it currently fails); either
  power it up (more seeds/models) to pass, or state it as a bounded-effect null, not
  "invariant."
- **A2 (binary importance)** is the weakest assumption; H4's graded data contradicts it —
  acknowledge, or move to a graded-success model.
- **Pre-register the expanded study** (OSF) *before* running E1/E2: hypotheses, regret
  metric definition, CTR-prediction test, exclusion rules. Cheap, fixes the thesis's
  named "author-run pre-spec" weakness, disarms the forking-paths critique, and is a
  differentiator few benchmark papers have.

**Recommendation:** keep the primary paper *empirical*; use the cliff mechanism
qualitatively and, at most, the correct concentration argument for "why sharp." Save the
full theory for a later TMLR/workshop paper only if repaired.

---

## 9. Risks & reviewer attacks (with mitigations)

| Attack | Mitigation |
|---|---|
| "Compression hurts, obviously." | Lead with **mis-ranking/inversion** (not "hurts"); show QA-best compressor is coordination-worst. |
| "Only synthetic." | E2: 5 real multi-hop corpora at scale. |
| "Only training-free compressors." | E1: learned + query-aware families. |
| "Multi-hop is just hard, not a compression regime." | E4: critical-token mechanism isolates *compression-induced* loss vs task difficulty. |
| "Your benchmark isn't the first multi-hop benchmark." | Claim only the *compression-swept, coordination-scored, independently-compressed-fragment* framing; cite RULER/HotpotQA/MuSiQue as the non-compression comparators. |
| "Deterministic solver isn't a real workflow." | E6: LLM planner across scales. |
| "Theory is hand-wavy." | §8: don't over-claim; correct concentration form only. |
| "This is your thesis." | §3 differentiation contract; explicit self-citation + delta. |
| Query-aware compressors close the gap (finding "fails"). | Heads-we-win (§4): the result becomes "the gap is a property of cacheable, task-agnostic compression — query-awareness fixes it at the cost of per-query recompression." Pre-register both readings. |
| n≈12 compressors too few for ranking statistics. | Regret metric (per-instance bootstrap) carries the headline; τ is secondary color. |

**Do not over-claim** (lit review): don't present the cliff as the first evidence
compression degrades long-context tasks (RULER, Lost-in-the-Middle exist); don't lean on
model-invariance without fixing its power; don't call C1 the first multi-hop benchmark.

---

## 10. Timeline (anchored to live deadlines; weeks from mid-July 2026)

1. **Weeks 1–2 (mid/late Jul) — Step Zero (§7) + pre-registration draft:** recover/rewrite
   runners; reproduce the thesis's H1/H2 numbers from CSVs as a correctness gate; freeze
   the OSF pre-reg (§8).
2. **Weeks 3–6 (Aug) — E1-core + E2-core:** 6–8 compressors × 3 real corpora — the minimum
   set that supports F1/F3. Full breadth continues after the gate.
3. **Week 6 (~Aug 14) — checkpoint:** core results in hand; ICLR official dates known by
   now → confirm ICLR path or drop to ARR Oct 12.
4. **Week 7 (Aug 17–29) — workshop paper** from core results → **NeurIPS 2026 workshop
   (~Aug 29)**; doubles as the ICLR dry run.
5. **Weeks 8–9 (Aug 31–Sep 13) — full E1/E2 + E5/E6 + E10/E11:** remaining
   compressors/corpora; multi-pass; LLM planner; θ_info scaling; safety-card tool.
6. **Weeks 10–11 (Sep 14–25) — analysis freeze, figures, writing + benchmark release**
   (named HF dataset, data card, harness, leaderboard) + stats pass (§8) → **submit
   ICLR 2027 (~late Sep)**. Fallback: ARR Oct 12 (reformat only). Recovery: COLM 2027
   after ICLR reviews (~Jan 2027).

---

## 11. Open decisions for you

1. **Angle confirm:** measurement + benchmark + CTR-as-metric paper (recommended), or do
   you want the method (CAAC) or theory promoted into the spine instead? (I advise
   against — see §2/§6.)
2. ~~The week-6 gate~~ **DECIDED (2026-07-03):** ICLR 2027 primary (EACL 2027 is fed by
   ARR Aug 3 — too soon); ARR Oct 12 fallback; COLM 2027 recovery. Effort: near-full-time;
   compute: plan both tiers, ask supervisor (see `supervisor_plan.md` §10).
3. **Compute budget:** is there a cloud-GPU + frontier-API budget? This gates E1/E2 scale
   and therefore the whole plan — including whether the ICLR gate is even reachable.
4. **Code recovery:** decompile-and-clean (fast) vs rewrite-for-release (slower, cleaner)?
5. **Benchmark name:** RecombBench / FragBench / MultiFrag / other — needed before the
   HF release and the workshop paper.
6. **Spin-offs:** queue the SoftwareX artifact paper too, or focus solely on the main
   paper first?