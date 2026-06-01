# Reproducibility Section — Plan Doc

Short plan for adding a consolidated reproducibility section to the thesis
manuscript. Author-facing working document. Status date: 2026-06-01.

**Scope:** plan only — no LaTeX edits in this doc. The actual section, if
approved, would go in `thesis_latex/Chapters/experiments.tex` (as §4.10)
or `thesis_latex/Chapters/summary.tex` (as §5.3.x, after the limitations
list). Target length: ~3/4 page, one figure-free.

---

## Why a dedicated section is worth adding

Right now reproducibility info is **scattered across four places**:

1. Abstract closing paragraph (3 sentences on the M4 laptop + GPU cache +
   frontier-not-deterministic distinction).
2. `\S{}1.5` Outline closing paragraph (one line about Appendix D).
3. **Appendix D.1** (the substantive one-command recipe with `make` targets
   and a per-arm wallclock budget, plus a determinism-scope paragraph at
   the end of the recipe).
4. `\S{}5.3` Limitations (the new "Frontier bootstrap samples not retained"
   caveat, added during the draft 3.1 mirror).

The 3-tier determinism story (byte-deterministic local / practically-
deterministic local-LLM / non-reproducible frontier) is **implicit and
fragmented** across these four locations. Reviewers asking "can I rerun
this and get the same numbers?" currently have to assemble the answer
themselves.

Reference-paper convention is to fold reproducibility into "Experimental
Design" rather than dedicate a section
(`papers_neurips_iclr/compression/04_selective_context.md` §4 is typical:
Datasets / Tasks / Metrics / Models / no separate reproducibility block).
A *thesis* has the room a workshop paper does not, and the NeurIPS
Reproducibility Checklist (mandatory since 2019; ACL/EMNLP since 2024)
is the natural template — but the checklist itself is too long to drop
in verbatim; a *narrative summary keyed to the checklist's structure* is
the right shape.

**Decision criterion:** if the section can be made to consolidate
(remove duplication from the abstract + appendix) rather than restate,
it pays for itself. If it would only restate, leave the appendix as is.

---

## Proposed structure (~3/4 page)

### Opening paragraph (4–5 sentences)

State the 3-tier determinism guarantee in one place. Cross-reference
Appendix~D for the one-command recipe. Quote (with cite) the NeurIPS
reproducibility checklist as the template the section follows.

### A 3-row table (the consolidating artefact)

| Arm | Byte-deterministic? | Reason | Canonical artefact |
|---|---|---|---|
| H1 / H2 / H3 cliff sweep, scoring, bootstrap CIs, figure regeneration | **Yes**, given seed + compression cache | Pure Python: regex solver, `numpy.random` for resampling, deterministic compressors (truncation, LLMLingua-2 argmax, TF-IDF+CE filter) | `results/h1_h2_v2/`, `results/h3_final/` |
| H4 reader, H5 planner, Phi-3 extractive compressor | **In distribution only** | Ollama greedy decode (`temperature=0`) with fixed seed is deterministic per call modulo CUDA kernel reduction order; pinned Ollama build required | `results/h4_unbiased/`, `results/h5_final/` |
| Frontier API arm (Qwen-2.5-72B, DeepSeek V4 Pro, GPT-oss 120B) | **No** | Server-side batching changes per-token logits; vendor silently versions weights; the `seed` parameter is best-effort, not contractual | `results/frontier_{qwen72b,deepseekv4,gptoss120b}/results.csv` is itself the canonical record |

### Three short paragraphs, one per tier

**Tier 1 — byte-deterministic local.** What you get: rerun `make
repro-cliff` from the cache, the produced CSV diffs zero against the
published CSV. Seed plumbing reference: `src/m6/utils/seed.py:Seeds.derive`
seeds numpy, Python `random`, `PYTHONHASHSEED`, torch. Bootstrap CIs are
exact to the last decimal because `n_boot=1000` with the same RNG state.

**Tier 2 — distributionally deterministic local LLM.** What you get:
rerunning produces numbers within ~0–1 token drift per call on the same
hardware; verdict-level aggregates (per-cell coordination success means,
τ\* fits) reproduce to the published values within the bootstrap CI. The
known non-determinism source is CUDA reduction-order across cuBLAS
calls; the published CSVs were produced on RTX 5090 32 GB with Ollama
0.5.x and pinned model digests recorded in
`docs/MODEL_CARDS.md` (verify with `ollama list`'s SHA column). Cite
the (small but documented) Ollama-side non-determinism issue from the
project's audit trail.

**Tier 3 — frontier API not reproducible.** What you get: rerunning
`make repro-frontier` produces *closely-similar but not identical*
numbers because of the three causes above. The thesis treats the
published `results/frontier_*/results.csv` as the canonical artefact —
analyses downstream of those CSVs (τ\* fit, bootstrap CI) are
themselves Tier 1 again. Forward-pointer to the new §5.3 limitation
about non-retained frontier bootstrap samples.

### Closing 1-line policy statement

Every claim in the manuscript that quotes a number is traceable to one
named directory under `results/` via the CANONICAL_NUMBERS registry
(reference Phase 0 of `draft3_remediation_plan.md`).

---

## What the section deliberately does NOT do

- **No new `make` targets, no new recipe.** Appendix~D.1 already has
  the one-command recipe; this section points to it once, doesn't
  duplicate it.
- **No NeurIPS Reproducibility Checklist verbatim.** Too long; cite it
  in the opening paragraph and let the table do the work.
- **No model cards / data cards inline.** Those live under `docs/`
  (`MODEL_CARDS.md`, `DATA_CARDS.md`) and are linked from Appendix~D.
- **No discussion of "why local is faster than reproducing from
  scratch."** That's an Appendix~D-style ergonomics point, not a
  scientific reproducibility point.

---

## Edits required if approved (estimate: 2–3 hours, no compute)

1. **New section** in either `experiments.tex` (after §4.9 Corollary 2,
   before §4.10 Summary of Verdicts) or `summary.tex` (new §5.3.5
   after the existing limitations list). Recommendation: `experiments.tex`
   §4.10 — the section is about how to reproduce *experimental* results,
   and the limitations chapter is already long.
2. **Compress the abstract closing paragraph** by ~3 lines: keep the
   one-laptop / one-GPU envelope, drop the "frontier-server batching"
   sentence (it's now in the new section), point to the new section.
3. **Compress Appendix D.1** by ~6 lines: keep the make-targets list
   and the wallclock budget; drop the determinism-scope paragraph at the
   end (it's now in the new section's table).
4. **Cross-reference cleanup:** add `\ref{sec:repro}` from §5.3
   limitations ("Frontier bootstrap samples not retained"), `\ref{sec:repro}`
   from §5.6 future work ("Frontier equivalence testing"), and from the
   `STATUS_NONCANONICAL.txt` note in §4.6.4.
5. **Insights log** entry once the section lands (one paragraph in
   `insights.txt` documenting the consolidation, per project rule).

---

## How the results CAN be reproduced (the concrete recipe, for the
section to summarise)

This is the substance the new section is consolidating. It already
exists in Appendix~D but is worth restating compactly here so the plan
is self-contained.

### Local arm — full reproduction from scratch (~12 h laptop + 14 h GPU)

1. `git clone <repo> && git checkout <release-tag>` — the manuscript
   ships with a fixed git tag; `git_sha` is recorded in every result
   CSV's metadata column.
2. `pip install -e .` (Python 3.12). Pin file at
   `requirements.lock.txt`.
3. `make repro-bench` — regenerates the 150-instance C1 benchmark from
   `configs/benchmark/c1-v0.1.yaml` and the fixed master seed. Output
   diffs zero against `data/processed/c1-v0.1/*.jsonl`.
4. `make repro-cache` on the GPU host — runs LLMLingua-2 +
   instruction-aware filter + Phi-3-Mini extractive + truncation across
   150 workloads × 10 ratios. ~14 h on RTX 5090. Output:
   `results/compression_cache/`. The cache is the canonical
   compression artefact; everything downstream consumes it.
5. `make repro-cliff` on the laptop — H1 + H2 against the cache, ~3 h.
   Produces `results/h1_h2_v2/` byte-identical to the published CSVs.
6. `make repro-scaling` on the GPU host — H5 (model-scaling sweep),
   ~4 h. Tier 2 reproducibility: numbers within bootstrap CI.
7. `make repro-rag`, `repro-disclosure`, `repro-transfer` — H3 + H4 +
   Corollary 2, all ≤3 h each. H3/H4 are Tier 1 (regex scoring +
   Llama-3.1-8B reader respectively).
8. `make repro-figs` — pure Python figure regeneration from the
   canonical CSVs, <1 min.
9. `make repro-all` runs (3)–(8) in dependency order. End-to-end
   wallclock: ~30 h GPU + ~12 h laptop.

### Local arm — verification only (~10 min laptop, no GPU)

Skip (4): download the pre-computed cache from the release tag's
artefacts, then run (5)–(8). End-to-end wallclock: ~6 h on M4 Pro,
zero GPU.

### Frontier arm — what "reproduce" means

- The published `results/frontier_qwen72b/results.csv` and
  `results/frontier_deepseekv4/results.csv` *are* the artefacts to cite.
- Re-running `make repro-frontier` requires Featherless API credentials
  for Qwen-72B + DeepSeek V4 Pro, and OpenAI Responses API credentials
  for GPT-oss 120B. Pinned model IDs are in
  `configs/experiments/frontier.yaml`.
- Re-run results will not byte-match the published CSVs (Tier 3). The
  τ\* fit and bootstrap CI on a re-run should overlap the published CI;
  divergence beyond the published CI is the trigger for noting a
  vendor-side model update.
- GPT-oss 120B specifically has `STATUS_NONCANONICAL.txt` because
  ADR-006 scoped it out; rerunning the diagnostic is optional.

### What's in the open-source release (the "reproducibility package")

- Manuscript source (`thesis_latex/`) + compiled PDF (`thesis.pdf`).
- Code (`src/m6/`) + configs (`configs/`) + tests.
- Canonical CSVs and JSONs under `results/` for every reported number.
- Model cards (`docs/MODEL_CARDS.md`) and data cards
  (`docs/DATA_CARDS.md`).
- The `docker-compose.yml` that brings the memory-bus reference service
  up locally (the C4 contribution as a running system, not just code).
- `CANONICAL_NUMBERS.md` (Phase 0 from `draft3_remediation_plan.md`) —
  the registry that links every manuscript number to its source artefact.
- This plan doc and the audit-trail markdown drafts in the project
  root (not strictly required for reproducibility but document the
  manuscript's evolution).

---

## Open question for the user

**Where should the section live?**

- **(A) §4.10 in experiments chapter, before §4.10 Summary of
  Verdicts.** Recommended. Reproducibility is an experimental-design
  property, and the limitations chapter is already saturated with
  scope-narrowing paragraphs.
- **(B) §5.3.5 in summary chapter, after the limitations list.**
  Defensible if you treat reproducibility as a meta-limitation
  ("frontier arm cannot be rerun"). The downside is it gets buried
  under twelve other limitation paragraphs.
- **(C) Skip the section, just add a one-line forward-pointer from the
  abstract to Appendix D.** Cheapest option; loses the consolidation
  benefit. Defensible if the user judges the appendix is already doing
  the work.

Recommendation: **(A)**. The section's value is consolidating the
3-tier story in front of the reader before they hit the limitations
chapter, where two of the new limitations (bootstrap-not-retained,
cost-model-identical-EUR) become much easier to read against an
explicit tier table.
