# ADR-009: Thesis title scoped to "Multi-Fragment LLM Workflows" (not "Multi-Agent Coordination")

**Status:** Accepted
**Date:** 2026-05-29
**Deciders:** Syed Abdullah Hassan (author), grilling session 2026-05-29 (Q3 / thesis-PLAN grill)

## Context

The codebase, project name in CLAUDE.md, plan-v3, and the working thesis title
have all carried *"Distributed Memory Bus for Multi-Agent Coordination"* since
the project's inception. The phrase is also embedded in repository URLs and
prior commits.

The 2026-05-29 grilling session against `thesis_PLAN.md` surfaced a credibility
risk: the manuscript title promises multi-agent simulation, but no production
experiment uses one. H1/H2 use a deterministic regex parser; H5/H6 and the
frontier validation use a single LLM call with all (compressed) fragments
visible. The AutoGen multi-round backend exists in `src/m6/orchestrator/`
but was excluded from production experiments because round-to-round LLM
variance dominated the compression signal — documented in CONTEXT.md
("coordination success" entry) and in plan-v3.

An examiner who reads the title and abstract forms a mental model of
"multi-round LLM agent coordination", then in Ch 3 §3.3 discovers the
methodology is "task solvability under compression". That gap is a
rubric #6 (honest evaluation of results, max 5) hazard: the thesis can be
read as overclaiming.

## Decision

* **Thesis manuscript title becomes:**
  *"Distributed Memory Bus for Multi-Fragment LLM Workflows:
  Context Compression, the Coordination Cliff, and Privacy"*
* **"Coordination" stays** as a term throughout — it refers to the structural
  property that the planner needs information drawn from multiple fragments
  to produce the expected answer. CONTEXT.md "Coordination success" entry
  is preserved.
* **"Multi-fragment"** is added as a CONTEXT.md term and used in the
  abstract, Ch 1 problem statement, and Ch 3 framing.
* **The codebase, GitHub repository name, and plan-v3 internal references
  remain "Multi-Agent Coordination"** for back-compat with existing artefacts
  and commits. The manuscript is what renames; the code does not.
* **The disclosure that experiments use a deterministic solver or a single
  LLM call is promoted from Ch 3 §3.3 to the Abstract and Ch 1 P5
  (problem statement)** so it is impossible for an examiner to miss.
* **The memory bus's stated design audience (multi-agent systems) is
  preserved** in Ch 3 §3.1; the *evaluation* uses a multi-fragment proxy.
  This is the same compromise the AutoGen orchestrator backend reflects:
  the artefact is multi-agent-capable, the experiments are not.

## Options considered

### Option A — Keep "Multi-Agent Coordination" title, bury the disclosure in Ch 3

Pros: title continuity with codebase, plan-v3, and existing commits;
zero rewriting of project naming.
Cons: examiner reads title and abstract as multi-agent simulation; the
disclosure in Ch 3 §3.3 reads as defensive backtracking. Rubric #6
hazard. The thesis evaluation lives or dies on whether the title
matches the evidence.

### Option B — Rename to "Multi-Fragment LLM Workflows" *(chosen)*

Pros: title now matches the methodology end-to-end. Disclosure becomes
descriptive ("we study multi-fragment workflows; the memory bus is
designed for multi-agent systems") rather than confessional.
"Coordination cliff" still appears in the subtitle, preserving the
headline finding's branding. Honest evaluation rubric #6 protected.
Cons: codebase project name diverges from the manuscript title.
Future readers seeing the GitHub repo "Distributed-memory-bus-for-
multi-agent-coordination" must read this ADR to understand why the
manuscript is titled differently.

### Option C — Drop "coordination" entirely, retitle around the cliff

Pros: maximum honesty; the cliff is what's measured.
Cons: discards the "coordination cliff" coinage that the thesis builds
around. Reframing every chapter title and figure caption is significant
rework with marginal grade benefit. Plan-v3's entire framing
("coordination cliff", "Corollary 1: ceiling-cliff separation") would
need rewriting.

### Option D — Add a "Notes on Scope" subsection before Ch 1

Pros: lightweight; no title change.
Cons: examiners do not read notes before introductions. The disclosure
must be in places they will actually read.

## Trade-off analysis

Option B pays the cost of one ADR and one repo-vs-manuscript naming
mismatch in exchange for an examiner-credibility-safe title that
matches the evidence. The mismatch is bounded to existing artefacts
that already carry the old name; future commits and the thesis live
under the new name.

The risk that the title sounds less compelling than "Multi-Agent
Coordination" is mitigated by the subtitle, which carries the headline
findings ("the Coordination Cliff" + "Privacy"). Reviewers in the
adjacent areas (LLM compression, RAG, agent systems) will recognise
"multi-fragment" as the more precise term and read it as a positive
signal that the author knows what was measured.

## Consequences

**Easier.**
* Abstract, Ch 1, and Ch 3 framing become descriptive rather than
  defensive. Rubric #6 hazard eliminated.
* "Coordination" is freed to mean exactly what CONTEXT.md says it
  means — a task-structure property, not an agent-architecture claim.
* The memory bus contribution (C4) cleanly separates "designed for
  multi-agent" from "evaluated on multi-fragment" — both true.

**Harder.**
* The codebase repository name no longer matches the manuscript title.
  Anyone arriving at the GitHub URL via the manuscript bibliography
  must traverse this ADR or the README to understand the naming.
* Plan-v3 references to "multi-agent coordination" become slightly
  stale; they are preserved as planning artefacts (not renamed) but
  future plan revisions should follow the new naming.

**Revisit when.**
* The AutoGen backend is brought online for a future paper or thesis
  extension, at which point the multi-fragment scoping can be relaxed.

## Action items

1. [ ] Update `thesis_PLAN.md` and `/Users/abdullah/.claude/plans/
   inherited-chasing-nebula.md` to use the new title and the promoted
   disclosure in Abstract / Ch 1.
2. [ ] Add **"multi-fragment"** as a CONTEXT.md term, cross-referenced
   to this ADR.
3. [ ] Keep `CLAUDE.md`'s project header unchanged (it documents the
   codebase, not the manuscript); add a one-line note under Project
   Structure that the manuscript title is scoped per ADR-009.
4. [ ] When the GitHub release tag is cut at submission, the release
   notes link to this ADR for the naming mismatch.


---

## Addendum (2026-05-30): "Distributed" dropped from title

A subsequent audit pass on 2026-05-30 flagged that the title's leading word "Distributed" overstates the implementation: the reference memory bus is a single FastAPI process backed by SQLite (WAL mode), an in-memory scratchpad with TTL eviction, and FAISS-CPU. There is no replication, no consensus, no horizontal sharding, and no cross-node coordination. The "distributed" affordance is the multi-fragment access pattern and the slot-namespacing that make multi-tenant deployment possible — but the artefact this thesis ships is single-host.

**Decision (2026-05-30).** Drop "Distributed" from the title. New title:

> *Memory Bus for Multi-Fragment LLM Workflows: Context Compression, the Coordination Cliff, and Privacy*

**Scope of the change.** Title-page (`main.tex`), abstract banner, manuscript markdown headers, `CLAUDE.md`, `thesis_PLAN.md` title line, citations.bib comment block, ADR-009 (this addendum). The codebase repository path `Distributed-memory-bus-for-multi-agent-coordination/` is preserved for back-compat with existing artefacts, GitHub links, and ssh aliases.

**Why not keep it and justify.** The trade-off was: drop (clean), justify in §3.1 (defensive), or punt to Lauri post-submission. The drop option avoids carrying a defensive paragraph into Ch 3 that doesn't serve the chapter's argument. Future distribution work belongs in §5.6 future-work if and when it becomes load-bearing.

**Revisit when.** A future deployment ships horizontal scaling (slot replication, consensus across nodes, cross-region access). At that point "Distributed" earns its way back into the title.
