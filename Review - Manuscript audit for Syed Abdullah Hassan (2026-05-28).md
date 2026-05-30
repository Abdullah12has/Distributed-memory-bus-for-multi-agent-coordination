---
title: "Review — Manuscript audit (draft thesis)"
audience: Syed Abdullah Hassan
author: Lauri Lovén
date: 2026-05-28
status: draft
type: review-report
---

# Manuscript audit — draft thesis

**For:** Syed Abdullah Hassan
**From:** Lauri Lovén
**Date:** 2026-05-28
**Subject:** Pre-experimental-run audit of the thesis source as of the
current state of `thesis_latex/` in the repository. The results sections
are still placeholder, by design — this audit covers everything around them:
references, in-text claims, argumentative structure, design choices,
figures and tables, and overall maturity. The aim is to give you a concrete
fix list before you populate the empirical chapters, so nothing
in the surrounding text quietly breaks on the way in.

---

## 1. Summary

The methodological and engineering depth of the manuscript is unusually
strong for an MSc draft: the pre-registered statistical analysis plan
(Holm–Bonferroni within explicit hypothesis families, BCa bootstrap with
10 000 resamples, the recentred-null percentile bootstrap rather than
tail-doubling, Mann–Whitney for the cliff test, Cliff's δ + Cohen's d),
the no-compression control + deterministic-solver upper bound, the
calibration targets with stop-the-line review, and the manifest-pinned
reproduction targets are all keepers. The bibliography of 86 entries is
substantial and well-organised, no entries appear fabricated, and the
argument for why H1 should hold (the planner sees a compressed view, the
workers retrieve from a compressed scratchpad, the critic verifies
against compressed fragments) is mechanism-aware rather than hand-wavy.

What the audit found, in priority order, is:

- **Three load-bearing in-text misattributions** that need fixing before
  anything posts publicly (Compressive Transformers; ICAE; NIST AI RMF).
- **A citability surface around seven internal references** (five FCG
  techreports plus two FCG papers that are not yet on a preprint server)
  that a public reader cannot retrieve.
- **About 15 placeholder author lists** of the form `{Wang et al.}` /
  `{Park et al.}` etc., one of which is also a bibkey misidentification
  (the paper currently cited as `park2025collaborative` is actually by
  Rezazadeh — there is no Park author).
- **A small set of structural items** that the writing currently leaves
  open: no numbered objectives / research-questions list in the
  introduction, the discussion's hourglass-back-out is not even stubbed
  beyond the H1–H4 placeholders, and several implementation design
  choices are presented without an option-space discussion.
- **A handful of arXiv → peer-reviewed venue upgrades** that have landed
  since the bib was last touched.

The technical core does not need to change. The fixes are correctness,
citability, and structure.

---

## 2. Required corrections (these should land before any public posting)

### R1 — Compressive Transformers "smooth and monotonic"

In `relatedwork.tex`, the soft-prompt-compression subsection attributes to
Rae et al. (2020) the characterisation that compressed memory in transformers has a degradation
curve that is "smooth and monotonic in the single-context regime", and the
sentence positions this as the null hypothesis H2 must distinguish itself
from. Web-verified against arXiv:1911.05507: Rae et al. sweep compression
rates 2/3/4 and report best-of; they do not establish a "smooth and
monotonic" degradation curve. The characterisation belongs to HiPPO-style
signal-reconstruction work, not Rae et al.

This matters because the misattribution sits at the joint where H2 is
defined.

**Fix.** Either (a) state H2's null on your own authority ("we adopt as a
null hypothesis that single-context compression degrades smoothly and
monotonically"); (b) re-cite HiPPO (Gu et al. 2020); or (c) cite the
LLMLingua / LLMLingua-2 ablations where smoothness across ratios is
empirically demonstrated.

### R2 — ICAE evaluated on NaturalQuestions

In `relatedwork.tex`, the ICAE paragraph reads "The ICAE achieves 4×
compression with minor accuracy degradation on NaturalQuestions and other
reading-comprehension benchmarks." Verified against arXiv:2307.06945: the 4× ratio is correct,
but ICAE was evaluated on a custom Prompt-with-Context (PwC) dataset with
BLEU / EM / GPT-4-as-judge. NaturalQuestions is not used.

**Fix.** "on a custom prompt-with-context evaluation set, using
autoencoding metrics and GPT-4-as-judge." If you want a NaturalQuestions-
evaluated compressor in the chapter, AutoCompressor (Chevalier et al.
2023) does evaluate on NQ — it is already in your bibliography.

### R3 — NIST AI RMF as source of the 5-tier classification lattice

The data-model section of `implementation.tex` and the privacy-aware-
retrieval section of `relatedwork.tex` both attribute the classification
lattice `public < internal < confidential < restricted <
secret` to NIST AI RMF 1.0. NIST AI RMF 1.0 (NIST AI 100-1) organises
around four functions (Govern / Map / Measure / Manage) and treats
confidentiality only as one trustworthy-AI characteristic; it does not
prescribe this labelled lattice. The closest NIST schema (FIPS 199 /
SP 800-60) uses a 3-tier scheme (Low / Moderate / High). The 5-tier
P/I/C/R/S lattice is a generic enterprise convention.

Your `summary.tex` limitations-section hedge ("borrows only the vocabulary") partially
acknowledges this, but the original misattribution stays in the text.

**Fix.** Choose one of: (a) drop the NIST AI RMF cite for the lattice and
present it as enterprise practice (cite ISO/IEC 27001 organisational
convention); (b) switch to FIPS 199 with the actual 3-tier scheme; or (c)
keep NIST AI RMF as a general AI-risk reference and add an explicit
"industry practice, not NIST AI RMF" attribution for the lattice.

### R4 — Bibkey misidentification: the "Park" paper is by Rezazadeh

The paper cited multiple times as "Park et al." (in the
introduction's contributions list and in the related-work section on
token-efficient multi-agent coordination) is arXiv 2505.18279,
"Collaborative Memory:
Multi-User Memory Sharing in LLM Agents with Dynamic Access Control".
The actual author list is Alireza Rezazadeh, Zichao Li, Ange Lou, Yuying
Zhao, Wei Wei, Yujia Bao (Accenture Center for Advanced AI). There is no
Park author. Every "(Park et al.)" in the text is wrong, and the bibkey
itself names the wrong person.

This matters because this paper is your closest published precedent for
the C4 tag-preserving extension.

**Fix.** Rename the bibkey to `rezazadeh2025collaborative`; expand the
author list in the bib; update every in-text "(Park et al.)" or
paraphrase.

### R5 — Internal-document citation surface

Five `@techreport` entries cite internal FCG documents
(`fcgsystemarch2026`, `fcgsoftwarearch2026`, `fcgintegratorarch2026`,
`fcgfinancial2026`, `fcgusecase2026`) with corporate author "{Future
Computing Group}" and no public URL. They carry load-bearing
quantitative figures (the ~80 % cloud-payload-reduction claim, the
EUR 2.15 per period-end report figure, the USD 3 / USD 15 per Mtok pricing
that grounds the cost model). A reader of the public thesis cannot
retrieve any of them to verify these numbers.

Additionally, the four `loven2025paper{1,2,3,4}` `@article` entries are
cited as if at IEEE Transactions on Services Computing. Of those, only
Paper 1 is currently on a public preprint server (arXiv:2603.05614) and
genuinely submitted to IEEE TSC. Paper 2A is on arXiv (2605.26604), Paper
2B / 3 / 4 are not yet on any preprint server, and the target venue for
several has moved to ACM TEAC.

**Fix, in increasing order of effort.**
- For the FCG techreports: either replace with public sources where
  available (the Trilogy Paper 1 arXiv preprint covers part of the
  architecture framing), fold the cited content into a thesis appendix so
  the public artifact carries its own evidence (Vignette 3.7 is the focal
  scenario — strong candidate), or arrange institutional publication of
  the techreports on the University of Oulu repository with stable URN
  identifiers.
- For the Trilogy citations: cite Paper 1 by its public arXiv ID
  (`arXiv:2603.05614`) with the full eight-author list and the actual
  title ("Real-Time AI Service Economy: A Framework for Agentic Computing
  Across the Continuum"); cite Paper 2A by its arXiv ID (`2605.26604`)
  with the actual title ("Credibility Trilemma in Polymatroidal Service
  Markets") and full author list; for the others, either mark
  `@unpublished` with explicit "in preparation, 2025" plus correct author
  lists, or remove the citation. A public thesis should not cite forward
  to work that is not yet on a preprint server.

One sub-issue worth a check: `fcgsoftwarearch2026` title currently reads
"**Neutral** AI Service Exchange Software Architecture". Given the
"Neural Router / Neural Pub/Sub" naming convention in the group, verify
"Neutral" vs "Neural" against the source — looks like it may be a typo.

### R6 — In-text quantitative claims to refine

Three numerical figures in the introduction and related-work chapters
need small adjustments after web-verification against the cited sources:

- The "approximately eighty percent of the performance variance" claim in the introduction's motivation paragraph is correct, but the 80 % is specifically for the **BrowseComp evaluation** of the multi-agent research system, not the system in general. Either keep the statement as written and add "on BrowseComp" or accept the slight scope-broadening as a
  bibliographically-honest paraphrase.
- The LLMLingua-2 claim "5× with less than two percentage points of F1 loss on MeetingBank summarisation and GSM8K reasoning tasks" in the related-work hard-prompt-filtering subsection needs nuance: the **MeetingBank** headline ratio in the paper is 3×, not 5× (at 5× the drop is larger); on **GSM8K** the metric is **EM**, not F1. Suggest: "compression ratios of 2×–5× with small task-metric losses on MeetingBank summarisation (≈1 pp F1 at 3×)
  and GSM8K reasoning (≈0 pp EM at 5×)".
- The "USD 3 per million input tokens and USD 15 per million output tokens" frontier-cloud reference price (stated twice in `implementation.tex`, once in the cost-ledger paragraph and once in the RAG-pipeline cost-model paragraph) is specifically **Claude 3.5 / 3.7 Sonnet** pricing, not a generic frontier benchmark. GPT-4o-mini is at USD 0.15 / USD 0.60; Gemini 1.5 Pro is in a different tier. Relabel as "the Claude 3.5 Sonnet reference price" and add an exchange-rate snapshot date (USD/EUR ≈ 0.92 was accurate late 2024 / early 2025; the EUR strengthened to about 0.88 mid-2025).

Two further verifications: the 84 % token-reduction claim in the introduction's motivation paragraph is verbatim correct; and the bib URLs for both Anthropic posts return 404 (correct URLs are `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents`and `https://www.anthropic.com/news/context-management`). The author
names on the context-engineering post are also wrong: the correct authors are Prithvi Rajasekaran, Ethan Dixon, Carly Ryan, Jeremy Hadfield; the bib has Kara Dixon, Jeremy Ryan, Adam Hadfield.

---

## 3. Recommended improvements (fix before submitting, not blocking now)

### I1 — Add an explicit numbered objectives or research-questions section

The thesis-statement subsection of `introduction.tex` (§1.2) refers to "the four research questions accepted at the project's inception" but no numbered RQ or objectives list appears anywhere in the chapter. The four contributions C1–C4 are artefacts (what is built), and the four hypotheses H1–H4 are falsifiable claims; neither is a stated objectives list, and the discussion can't revisit objectives point-by-point if they don't exist.

Two clean ways forward: (a) add an explicit "Objectives" or "Research questions" subsection in §1 with a numbered list mapped to C1–C4 and H1–H4; or (b) rename C1–C4 to numbered research questions and make the H1–H4 mapping explicit. Either resolves the gap.

### I2 — Stub the discussion hourglass-back-out

The opening of `summary.tex` honestly says the empirical-narrative discussion is pending result population. Even before the results land, stub the shape of the back-out: per-hypothesis verdict slot, then one paragraph each on how the result positions the work within the institutional AI-service-economy framing and the TalentAdore-industry-relevance arm. Doing this now also catches whether the H1–H4 → C1–C4 mapping is consistent before the verdicts go in.

### I3 — Bibliography upgrades and placeholder fixes

These are mechanical edits to about 15–20 bib entries.

**arXiv → peer-reviewed venue upgrades that have landed since the bib was written:**

| Bibkey                 | Update to                                                                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `cheng2024xrag`        | NeurIPS 2024                                                                                                                           |
| `li2023camel`          | NeurIPS 2023                                                                                                                           |
| `mialon2023gaia`       | ICLR 2024                                                                                                                              |
| `ragas2023`            | EACL 2024 System Demonstrations                                                                                                        |
| `hsieh2024ruler`       | COLM 2024                                                                                                                              |
| `wang2025agentdropout` | ACL 2025 (Long)                                                                                                                        |
| `zhang2024agentprune`  | ICLR 2025; real title is "Cut the Crap: An Economical Communication Pipeline for LLM-based Multi-Agent Systems" (verify on OpenReview) |
| `bassit2025securerag`  | NeurIPS 2025 GenAI for Health workshop                                                                                                 |
| `faiss`                | add a companion `@article johnson2019faiss` citing IEEE Trans. Big Data 7(3):535–547 (arXiv:1702.08734)                                |

**Placeholder author lists to expand** (IEEE numeric style requires real names): `wang2024icf`, `guo2025dynamic`, `cheng2024xrag`, `xu2025amem`, `chhikara2025mem0`, `rasmussen2025zep`, `zhang2024agentprune`, `wang2025agentdropout`, `park2025collaborative` (also bibkey wrong, see R4), `ye2025kvcomm`, `yu2025memagent`, `zhou2025privacyrag`, `bassit2025securerag`, `zhao2024frag`, `addison2024cfedrag`, `li2025securitylingua`, `saleh2025memindex`. (I have the real author lists from the verification pass; happy to send them in a follow-up.)

**Title and venue corrections beyond R1–R5 already named:**

- `bai2024longbench` — the bib metadata is for **LongBench v2** (arXiv:2412.15204), but the text in the related-work long-context-benchmarks subsection describes the **v1** six-task suite (single-doc QA, multi-doc QA, summarisation, few-shot, synthetic retrieval, code completion). Either switch the bib to v1 (ACL 2024, arXiv:2308.14508), or rewrite the prose to describe v2.
- `wang2024icf` venue should be **Findings of EMNLP 2024**, not main.
- `li2025securitylingua` real title is "SecurityLingua: Efficient Defense of LLM Jailbreak Attacks via Security-Aware Prompt Compression"; first author Yucheng Li.
- `saleh2025memindex` real title ends "...for **Multi-agent Systems**", not "Large Language Model Agents"; DOI is 10.1145/3774946.
- `loven20256g` is a multi-editor white paper at "6G Research Visions No. 14", University of Oulu — should be `@book` or `@techreport` with `editor =`, `series = {6G Research Visions}`, `number = {14}`, `url = URN:NBN:fi:oulu-202501211268`.
- `sheikhi2025cognitive` first author name looks like a typo: the FCG collaborator on cognitive-SOC work with Kostakos is Saeid Sheikhi, not Salim. Verify against the IEEE BigData 2025 programme once available.
- `kokkonen2022autonomy` (arXiv:2205.01423) has 18 authors in the order Kokkonen, Lovén, Hossein Motlagh, ..., Pirttikangas, Riekki — the bib has 3 authors in a different order. Use the full list, or at minimum the correct first three.

**URL fixes** beyond the two Anthropic ones in R6:

- `llamacpp` canonical owner moved to `ggml-org` — replace with `https://github.com/ggml-org/llama.cpp`.
- `mscstudies` URL 404 → `https://www.oulu.fi/en/apply/masters-computer-science-and-engineering`.
- `bscstudies` URL 404 → `https://www.oulu.fi/en/apply/bachelors-computer-science-and-engineering`.

### I4 — Light-pass justification for the implementation design choices

A few load-bearing implementation choices are presented as faits accomplis without an option-space discussion. A one-or-two-sentence justification per item closes this gap quickly:

- ICAE LoRA rank 16 — why 16 over 8 or 32 (the typical resource-vs-quality tradeoff)?
- M = 128 memory tokens — why 128 over 32 / 64 / 256?
- Llama-3.1-8B as both encoder and decoder — why this backbone over Qwen2-7B or Mistral-7B?
- AutoGen v0.4 as the runtime — why over LangChain / MetaGPT / CAMEL?
- InfoNCE temperature τ = 0.07 "following SimCLR" — the SimCLR temperature is for image contrastive; one line on why this transfers to a text- embedding setting would close it.

These are all reasonable defaults; the audit reads them as undefended only because the reasoning isn't in the chapter. Brief is fine.

### I5 — Synthetic-tag distribution defense

`implementation.tex` §3.5.2 acknowledges that the C1 generator uses synthetic ACLs because real ACL data was not available, and offers three distributions (uniform / skewed / hierarchical). The choice of an "exponential family chosen to mimic typical production ACL skews" needs
one sentence on what real-world distributions look like and why the chosen forms approximate them. Currently the choice is defended by "mimic typical production ACL skews" without further support.

---

## 4. Optional polish

- The cost numbers EUR 2.76 / 13.80 / 0.05 per Mtok appear twice (in the FCG-programme paragraph of related work, and again in two paragraphs of `implementation.tex` — the cost-ledger paragraph and the RAG-pipeline cost-model paragraph). They are identical, so this is not a consistency issue; but a single canonical statement with one back-reference would read better than two near-identical paragraphs.
- DOIs missing on the three foundational statistics papers (`wilcoxon1945`, `mannwhitney1947`, `cliff1993dominance`). Easy add for IEEE-style completeness.
- `saleh2025messagebrokers` uses `pages = {Article 20}`; convert to `articleno = {20}, numpages = {37}` for ACM-style accuracy.
- Optional page-range additions on `kocisky2018narrativeqa`,`yang2018hotpotqa`, `lin2004rouge`, `rajpurkar2016squad`, `chen2020simclr`.
- `oord2018cpc` first-author diaeresis: "Aäron van den Oord" matches the canonical form; the bib has "Aaron". Minor.

---

## 5. What the audit could not check

Two whole categories of audit are intentionally deferred until the empirical chapters are populated, because the source explicitly says they are: results-interpretation rigour (overclaiming, missing CIs, single-run findings, claims-exceed-data) and figure-of-results legibility (font sizes at print size, panel crowding, channel discrimination, takeaway emphasis). Both should get a dedicated second pass once the results land.

Internal numerical consistency was checked and is clean. The cost figures, "EUR 2.15 per period-end report", "85 % tag preservation at 4×, ≤5 pp accuracy degradation", and the seed count all appear identically wherever they recur.

Figures and tables (only the architecture figure and three tables render in the current source): no overfull-hbox risk, table column-spec sums fit `\textwidth`, caption placement is uniform (above), rule style is consistent (`\hline` throughout — fine, just not booktabs). The architecture figure is legible from the source as drawn.

---

## 6. Closing

The technical core of the manuscript is genuinely strong — the statistical plan, the no-compression control + deterministic-solver upper round, the smoke-ladder discipline around calibration targets, and the reproducibility envelope are above MSc baseline. None of the items above asks you to change the contribution or the experimental design; they ask for a careful pass to fix the things that survived the otherwise-good literature plumbing.

Suggested order: R1–R6 first (they're correctness, and they're cheap), then I1–I2 in the next writing pass (these will pay off when the discussion gets populated), then I3–I5 and the optional polish whenever convenient. The bibliography upgrades and placeholder fixes are mechanical and worth batching into a single editing pass.

Happy to walk through any of the items.

— Lauri
