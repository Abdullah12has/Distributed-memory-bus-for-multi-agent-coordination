# MASTER THESIS M6 — PLAN v3 (FINAL)

# The Coordination Cliff: How Context Compression Breaks Multi-Fragment LLM Workflows

*Context compression, coordination quality, and policy-aware sharing*

**Syed Abdullah Hassan**
University of Oulu · Faculty of ITEE · CSE Research Unit · Future Computing Group

Academic supervisor: Lauri Lov\'en
Industry: TalentAdore (Asim Nadeem, Oskari Valkama)

*May 2026 — 4-week completion, targeting 8.5/10 MSc*

---

## Change log relative to v2

| Item | v2 | v3 |
|------|----|----|
| Scope framing | "multi-agent coordination" | **multi-fragment LLM workflows** — the planner is a deterministic regex parser (H1/H2) or a single LLM call with all compressed fragments visible (H5/H6/frontier). The memory bus is *designed for* multi-agent integration but multi-round agent simulation is outside the empirical scope. |
| LLM-summariser | Llama-3.1-8B abstractive | **Phi-3-Mini-3.8B extractive** (tokens-only prompt; verified post-hoc, novel-token stripping, LLMLingua-2 fallback) |
| Compressors swept | 3 (lingua2, filter, phi3-extractive) | **4** — added **truncation** as the destructive lower-bound baseline; the lower-bound argument is that any learned compressor must beat truncation on coordination to justify its cost. |
| Model-size scaling | Dropped | **Reinstated as 3-point cross-architecture sweep**: Qwen-2.5-1.5B, Phi-3-Mini-3.8B, Llama-3.1-8B (three *different* architecture families, not a within-Qwen scaling) — H5 |
| Frontier validation | Not in v2 | **Frontier arm** (Qwen-2.5-72B, DeepSeek V4 Pro, GPT-oss 120B) via Featherless / OpenAI API to test cliff-position transfer across a 9× scale-up and a change of architecture |
| H4 tag preservation | "$\ge 85\%$ preservation" (trivially true) | **Replaced with inference-disclosure metric (H4)** — held-out Llama-3.1-8B reader, three conditions (priors / baseline / compressed-4×), paired-bootstrap test on protected-fact recovery rate |
| Citations | Several unverifiable arXiv IDs | **All refs verified** against peer-reviewed venues OR explicitly marked as preprints / industry blogs |
| Theoretical framing | None | **Compounding-error model** — derives the cliff's threshold structure from per-round critical-token-recall $q(r)$ against a per-family threshold $\theta_q$; assumptions A1–A4 stated; *calibrated regime* predicate formalised |
| Cliff-recall metric | Generic token-recall | **Critical-token-recall (CTR)** — family-specific restriction to task-critical tokens (multi-digit numerics, all digits, chain-reference + `FINAL` marker); generic token-recall retained as a reporting column only |
| Statistical test for H2 | Mann–Whitney $U$ | **Paired Wilcoxon signed-rank** — same workloads appear in both conditions, which violates independence assumption of $U$ |
| Optional real-trace arm | Dropped | **H6 on MultiHopRAG + HotpotQA** to test whether the cliff structure transfers from synthetic C1 to real multi-hop benchmarks |
| CAAC | Not in v2 | **Cliff-Aware Adaptive Compression** — a wrapper, not a fifth compressor family. Operating-point selector (per the compounding-error bound), discussed in the closing chapter as the constructive realisation of the model |

---

## 1. Thesis statement

This work designs, implements, and evaluates a **memory bus for multi-fragment
LLM workflows** with a context-compression layer. A *multi-fragment LLM
workflow* is one where the answer cannot be read out of any single fragment
in isolation and requires combining information across two or more fragments,
each of which may be compressed independently before the planner sees it.
Cross-document fact aggregation, constraint-satisfaction planning, and
multi-step retrieval are three representative instances.

### Scope disclosure (load-bearing — stated in Abstract and Chapter 1)

All experiments measure **task solvability under compression**. The planner
is either:
- a **deterministic regex information-extraction solver** (H1, H2) — used to
  isolate compression effects from LLM run-to-run variance; or
- a **single LLM call with all (compressed) fragments visible** (H5, H6,
  frontier) — used to demonstrate that the cliff structure measured by the
  deterministic solver appears under a non-trivial language-model planner.

A multi-round AutoGen v0.4 backend exists in `src/m6/orchestrator/` and
integrates with the memory bus, but is **not used in any reported experiment**.
The reason is mechanical: round-to-round LLM variance dominates the
compression signal at the C1 ratios we sweep, so cleanly attributing
coordination drops to compression rather than to agent variance requires
isolating the compressor on the critical path. The memory bus is *designed
for* multi-agent integration; the experiments *evaluate* on a multi-fragment
proxy.

### Four contributions

1. **C1 — A reproducible multi-fragment coordination benchmark.** Three
   workload families × 50 instances = 150 instances, synthetic provenance
   and access-control tag distributions, four coordination-quality metrics
   (final task success, sub-task assignment accuracy, critical-token-recall,
   achieved compression ratio), single-command regeneration from a fixed
   seed.

2. **C2 — Empirical characterisation of the coordination cliff plus a
   compounding-error model that explains it.** Across four training-free
   compressors and three planner-LLM scales (cross-architecture local arm
   plus a frontier validation), characterises the *existence*, *shape*, and
   *model-scale dependence* of a coordination cliff $\tau^*$. The
   compounding-error model derives the cliff's threshold structure from
   per-round critical-token-recall against a per-family threshold $\theta_q$;
   it is presented as a first-order bound with quantified residuals, not as
   a tight predictor. Two structural corollaries (Ceiling–Cliff Separation;
   Information-Density Scaling) are stated alongside H5 and H6 as the
   sharpened forms we will publish if the original monotonicity / transfer
   predicates do not hold.

3. **C3 — RAG + compression pipeline catalogue.** Three pipeline
   architectures (compress→retrieve, retrieve→compress, joint
   relevance-conditional) evaluated under matched storage- and
   accuracy-bounded regimes, with a EUR-per-workflow cost model.

4. **C4 — Memory bus with summary-level inference-disclosure metric.**
   FastAPI service with policy-enforcement middleware, tamper-evident SQLite
   audit log, five-tier classification lattice over a 64-bit access-control
   mask, in-memory scratchpad with TTL eviction, FAISS-CPU vector store. The
   novel measurement is a held-out-reader privacy quantification that
   measures leakage *through the compressor itself*, distinct from
   prior privacy-aware RAG work which protects the retrieval *index*.

The thesis also presents **CAAC** (Cliff-Aware Adaptive Compression) in the
discussion as a constructive realisation of the compounding-error bound:
given a per-family $\theta_q$, CAAC binary-searches downward over compression
ratios until per-fragment CTR sits on the safe side of the cliff. CAAC is
framed as **operating-point selection** under the model's bound, not as a
Pareto-dominating wrapper — the strict-Pareto rate against the fixed-ratio
compressor is expected to be near zero by construction.

### What is novel relative to prior work

* **The coordination-cliff measurement (C2) is, to the author's knowledge,
  the first systematic characterisation of how compression affects
  multi-fragment task solvability across a controlled compressor × family ×
  planner-scale × architecture sweep.** The closest published analogue is
  Anthropic's industry report that "token usage explains ~80% of the
  performance variance" in a multi-agent research
  workflow~\cite{anthropic2025multiagent} — an industry observation, not a
  controlled measurement.

* **The compounding-error model is novel in its application to multi-fragment
  compression evaluation.** Per-round token recall $q$ compounds as $q^N$
  over $N$ sequential passes (in our experiments $N = 1$); the cliff
  position is where $q^N$ crosses the per-family threshold $\theta_q$. The
  combination of a position prediction with a bootstrap-CI band and a
  per-cell match rate is absent from the prior literature.

* **The summary-level inference-disclosure metric (C4) operationalises
  privacy of compressed memory.** This is distinct from prior privacy-aware
  retrieval work~\cite{zhou2025privacyrag, bassit2025securerag} (which
  protects the retrieval index) and from SecurityLingua~\cite{li2025securitylingua}
  (which uses compression as an input-side defence against jailbreaks). We
  measure leakage *through the compressor itself*, on the assumption that
  the index is access-controlled but the compressed summaries are exposed to
  the planner and any downstream reader the planner shares them with.

* **C1 is released as a reusable benchmark.** Synthetic but reproducible
  from a seed; the design is documented and other groups can extend it to
  new compressors, new planner regimes, or new task families.

### Why "multi-fragment" rather than "multi-agent"

The deliberate scope rename, captured in ADR-009, reflects three things.
First, what we actually measure is *task solvability under compression* on
workloads whose answer requires combining information from multiple
independently-compressed fragments — a property of the *task structure*, not
of the agent architecture. Second, the round-to-round LLM variance we
observed in pilot AutoGen runs dominates the compression signal at the
ratios we care about, so a multi-round evaluation would conflate compression
quality with agent dynamics. Third, the memory bus is *designed for* multi-
agent integration (the access layer, the policy middleware, the audit log
all assume multiple principals); the evaluation choice does not constrain
the design.

### Compute envelope

Single Apple M4 Pro 48 GB workstation for cliff-sweep development and the
deterministic-solver pipeline, plus an RTX 5090 32 GB host (WSL2
Ubuntu 22.04, Tailscale-accessible) for compression precomputation, the
8B-planner model-scaling sweep, the frontier API arm, and the HotpotQA /
MultiHopRAG transfer arm. **Zero training.** Every experiment runs in hours,
not days. Frontier API access (Featherless OpenAI-compatible endpoint plus
the OpenAI Responses API for the GPT-oss diagnostic) is required only for the
frontier validation arm; every other experiment is fully local.

Estimated wallclock: **~30 h GPU + ~12 h laptop** for the canonical pipeline
end-to-end with a precomputed compression cache.

### Compressors (all training-free)

| Compressor | Type | Source | License | Role |
|-----------|------|--------|---------|------|
| LLMLingua-2 | Token-level XLM-RoBERTa classifier | Pan et al., Findings of ACL 2024 | MIT | Swept (headline token-level) |
| Phi-3-Mini extractive | Token-extractive prompt over Phi-3-Mini-3.8B via Ollama, with `_strip_novel_tokens` and LLMLingua-2 fallback | Microsoft Phi-3 | MIT | Swept (privacy-friendly extractive) |
| Instruction-aware filter | TF-IDF prune + cross-encoder reranker (BAAI/bge-reranker-base) + stop-word/short-token trim | Project-internal | MIT | Swept (training-free heuristic baseline) |
| Truncation | Prefix-keep | Project-internal | — | Swept (destructive lower-bound baseline) |
| Identity | No compression | — | — | Control |
| CAAC | Wrapper around any inner compressor; backs off by CTR against $\theta_q$ | Project-internal | MIT | Discussion chapter, not swept |

**Counting once for the manuscript: six** `Compressor` implementations
total; **five** active (identity is the control); **four** swept in the
H1/H2 cliff experiments. CAAC is a wrapper, not a fifth compressor family.

The Phi-3-Mini extractive prompt forbids generation of novel tokens:

> "Select the minimal set of contiguous spans from the passage that a
> downstream reader would need to answer the question. Output the selected
> spans verbatim, separated by line breaks. Do not summarise, paraphrase, or
> add new tokens. Target output length: at most $N$ tokens."

A post-hoc verifier checks every output: every token must appear in the
source. Two practical loosenings were necessary in pilot work: a 15%
novel-token tolerance (small LMs frequently insert function words even when
told not to), and a `_strip_novel_tokens` post-pass that drops any token not
in the source after the verifier passes. Outputs whose extractive fraction
is below 50% fall back to LLMLingua-2 at the same target ratio. This closes
the *cognitive offloading* objection that an abstractive summariser would
open.

**Compression ceiling note.** Span selection plus the strip-pass plus the
LLMLingua-2 fallback bound Phi-3-Mini extractive's achievable compression at
approximately $2.5\times$ regardless of the requested target. This is a
documented limitation; every evaluation reports the **achieved compression
ratio** alongside the requested target so the ceiling is visible.

### Critical-token-recall (CTR) — the load-bearing recall metric

Generic token-recall $q_\text{token}(r) = |T_\text{compressed} \cap T_\text{source}| / |T_\text{source}|$
counts every preserved token equally. Pilot work showed this is a poor proxy
for task-relevant information preservation: Phi-3-Mini extractive at low
ratios preserves common function words ("the", "and") but can drop critical
numeric tokens — its generic token-recall is high; its coordination success
is low.

**Critical-token-recall (CTR)** restricts to the family-specific set of
task-critical tokens:

| Family | Task-critical tokens |
|--------|----------------------|
| a (cross-document fact aggregation) | Multi-digit numeric tokens (≥ 2 digits, to exclude single-digit noise) |
| b (constraint-satisfaction planning) | All numeric tokens (load and capacity values) |
| c (multi-step retrieval) | Chain-reference tokens (`entry-X` patterns) and the literal `FINAL` marker |

CTR is what the compounding-error model uses as the per-round retention
rate $q(r)$; CAAC uses CTR as its back-off signal; and the
predicted-vs-empirical $\tau^*$ analysis uses CTR to derive $\theta_q$.
Generic token-recall is retained as a reporting column for backwards
compatibility with prior analyses but is not used in the verdict pipeline.

---

## 2. Six hypotheses

| ID | Hypothesis (falsifiable form) | Wallclock |
|----|--------------------------------|-----------|
| H1 | Single-fragment information preservation under compression is not a transferable predictor of multi-fragment coordination success: workload-level Spearman $\rho(\Delta_\text{F1}, \Delta_\text{coord}) < 0.6$ for every swept compressor, with 95 % BCa bootstrap CIs excluding 0.6 from above. The single-agent F1 is operationalised as token-overlap between the compressed fragment representation and the original source text (`qa_f1` column in `run_h1_h2.py`), not answer-level QA-F1 against a gold answer. | shared with H2 |
| H2 | A coordination cliff $\tau^*$ exists for each (compressor, family) cell, with a relative drop $\ge 30\%$ and a paired-Wilcoxon signed-rank $p < 0.05$ after Holm correction across the 12 (compressor × family) cells. Cliffs need not appear in every cell: the falsification bar is $\ge 7$ of 12. | ~10 h |
| H3 | RAG pipeline placement matters: P1 (compress-first) vs P2 (retrieve-first) sign-flip between storage- and accuracy-bounded regimes with $\ge 5$ pp F1 effect; P3 (joint relevance-conditional routing) wins the combined $F_1 / \text{EUR}$ score in both. | ~3 h |
| H4 | (i) The summary-level inference-disclosure metric distinguishes a baseline planner from a priors-only planner (signal: positive paired effect, $p < 0.05$). (ii) Compression at $4\times$ reduces disclosure relative to baseline (reduction: positive paired effect, $p < 0.05$). Both tested with paired bootstrap and Holm correction across compressors. | ~3 h |
| H5 | The cliff position $\tau^*$ shifts upward as the planner-LLM scales. Across {Qwen-2.5-1.5B, Phi-3-Mini-3.8B, Llama-3.1-8B} — three different architecture families — with LLMLingua-2 as the fixed compressor (so only the planner varies), $\tau^*_\text{8B} \ge \tau^*_\text{3.8B} \ge \tau^*_\text{1.5B}$ on $\ge 2$ of 3 workload families, with the largest-vs-smallest gap $\ge 1.5$ ratio units. | ~6 h |
| H6 | The cliff structure transfers from synthetic C1 to real multi-hop benchmarks. On a 30-question subset of MultiHopRAG and on HotpotQA, the coordination-vs-compression curve matches synthetic C1 family-(a) within $\pm 15\%$ on $\tau^*$ and $\pm 10$ pp on coordination success. | ~4 h |

**Core wallclock: ~26 h.** Holm-correction families: $\{H_1, H_2\}$ (same
cliff machinery), $\{H_3\}$, $\{H_4\}$, $\{H_5\}$, $\{H_6\}$. We do **not**
correct jointly across hypotheses because each one is an independent
falsifiable claim and joint correction across them would be over-conservative.

### Refinement paths (registered up-front, not post-hoc rescues)

The corollaries below are pre-registered *sharpened* forms of H5 and H6.
They are the structural claims we will publish if the original monotonicity /
absolute-position predicates do not hold but the qualitative structure does.
Registering them up-front is what distinguishes principled refinement from
post-hoc rescue.

- **Corollary 1 — Ceiling–Cliff Separation.** Planner parameter count $m$
  determines $p_0(m)$, the no-compression baseline coordination success;
  the cliff position $\tau^*$ is determined by the compressor's $q(r)$ and
  the task's $\theta_q$, not by $m$. When $p_0(m) < \theta_q$ a floor effect
  prevents detection of the cliff; when $p_0(m) \ge \theta_q$ the cliff
  position should be invariant across $m$ *within the calibrated regime*.
  Test: a two-one-sided-tests (TOST) equivalence procedure at $\pm 20\%$
  tolerance against a synthetic reference $\tau^*$. The frontier validation
  arm tests this across a 9$\times$ scale-up and a change of architecture
  family.
- **Corollary 2 — Information-Density Scaling.** The cliff *shape*
  (sharpness, pre-cliff plateau height) varies systematically with an
  AUC-based per-task information-density estimate $\theta_\text{info}$,
  distinct from the per-family recall threshold $\theta_q$. Dense tasks
  ($\theta_\text{info} \to 1$) cliff early and sharply; distributed tasks
  ($\theta_\text{info} \to 0$) degrade gradually from a lower baseline.
  Test: $\Delta\theta_\text{info} \ge 0.1$ between the dense C1 family-a
  benchmark and the distributed MultiHopRAG / HotpotQA benchmarks.

### Falsifiability bars as practitioner-relevant minima

Each numerical bar was chosen as the smallest effect a practitioner relying
on this work would care about, not as an arbitrary statistical threshold.

- **$\rho < 0.6$ (H1)** is Cohen's convention for "less than moderate" rank
  correlation; above this bar the single-agent F1 metric remains
  operationally useful as a deployment proxy.
- **$\ge 30\%$ relative drop (H2)** is the smallest coordination-success
  drop a practitioner cares about: 10 % sits within typical run-to-run
  variance, 50 % is obvious without measurement; 30 % is the value below
  which the operating point would still be deployable.
- **$\ge 5$ pp F1 with opposite sign (H3)** is the smallest gap the
  EUR-per-workflow cost model makes operationally meaningful; opposite
  sign is what justifies regime-conditional deployment.
- **Paired-bootstrap $p < 0.05$ (H4)** is conventional; the paired structure
  follows from the same workloads appearing in all conditions.
- **$\pm 20\%$ TOST band (Corollary 1)** is the strict cliff-position
  detectability tolerance; a $\pm 50\%$ permissive default is also reported
  as the local-arm absorbing fixture.
- **$\Delta\theta_\text{info} \ge 0.1$ (Corollary 2)** is the smallest
  information-density gap producing visually distinct cliff shapes on the
  three benchmarks evaluated.

### Why H1 and H2 share wallclock

H1 needs the same workload runs as H2 (it collects source-retention F1 and
coordination-success per run). Running H2 produces H1 as a byproduct. The
single sweep is **4 compressors × 10 ratios × 3 families × 50 workloads × 5
seeds ≈ 30,000 cells**, ~10 h on the M4 Pro with the local-LLM stack and the
precomputed compression cache in place.

### Why H5 uses a fixed compressor

H5 isolates the planner-LLM as the only variable. If both the planner and
the compressor varied we could not attribute $\tau^*$ shifts to either.
LLMLingua-2 is the cleanest fixed-compressor choice because its scoring is
deterministic at greedy decoding and its $q(r)$ curve is smooth and
monotonic across the swept ratios.

### Why the H5 local arm is cross-architecture

The three local planners — Qwen-2.5-1.5B, Phi-3-Mini-3.8B, Llama-3.1-8B —
are **three different architecture families**, deliberately chosen so that
an invariance result generalises across architecture rather than only across
parameter count within a single family. If the cliff position is determined
by the compressor and task and not by the planner (Corollary 1), then
swapping architectures at fixed compressor and task should leave $\tau^*$
unchanged. A within-Qwen sweep would be a weaker test because the three
sizes would share an inductive bias.

### The frontier validation arm

The frontier validation re-runs the family-a cliff sweep with the planner
swapped for **Qwen-2.5-72B-Instruct** (a $\sim 9\times$ scale-up from the
local Llama-3.1-8B used as the LLM-planner reference) and
**DeepSeek V4 Pro** (a different architecture and vendor). Both are accessed
via the OpenAI-compatible Featherless endpoint, which exposes a flat
per-token price for both models so the EUR-per-workflow cost model compiles
correctly. The question is whether the cliff position transfers across the
9$\times$ scale-up and the architecture-family change while the compressor
and task are held fixed.

A third planner, **GPT-oss 120B**, is run separately as an
**extended-reasoning diagnostic**. The compounding-error model's calibrated-
regime predicate (below) explicitly excludes planners that recover from
sub-threshold information via chain-of-thought reasoning. GPT-oss is the
candidate boundary case; if it cliffs at a substantially different position
than the standard non-reasoning frontier models, the discrepancy is reported
as a *positive contribution* — an empirical boundary on where the model's
predictions apply — rather than as a counterexample.

Sample size for the frontier arm is **10 family-a workloads × 6 sweep
ratios × 3 seeds = 180 cells per model**, with an extended Qwen-72B re-run at
$30 \times 3$ for tighter CI. The bootstrap CI on $\tau^*$ is computed by
resampling workloads ($n_\text{boot} = 500$, BCa).

---

## 3. Four contributions in detail

### C1 — Multi-fragment coordination benchmark

Built via `make bench-generate`. 150 instances across:

* **(a) Cross-document fact aggregation** — Vignette-3.7-style aggregate
  across 8 institutional system fragments (FCG use case
  \cite{fcgusecase2026}). Critical tokens are multi-digit numerics; expected
  information density $\theta_\text{info} \approx 1$ (dense).
* **(b) Constraint-satisfaction planning** — assign $N$ sub-tasks under
  capacity constraints across $K$ workers. The generator constructs a
  feasible solution by a capacity-respecting greedy algorithm that bumps
  capacities only when strictly necessary, guaranteeing at least one
  feasible assignment per workload. The scorer is a **feasibility checker**
  (any valid assignment scores 1), not exact match.
* **(c) Multi-step retrieval** — linear chain of fragments where each
  fragment carries either a pointer to the next (`entry-X`) or, at the leaf,
  the answer (`FINAL-XXXX`). Chain lengths 2–4; each fragment padded with
  4–8 distractor sentences. Expected information density
  $\theta_\text{info}$ lower than family-a (distributed).

The three families together span a deliberate range of information densities
so that the cliff mechanism (a recall threshold $\theta_q$) and the cliff-
position shift mechanism (information density $\theta_\text{info}$) can be
separated. This separation is what enables Corollary 2.

**Coordination success and supporting metrics.** The coordination scorer is
a pure function of the workload and the planner's output; it does not call
any LLM. It returns one primary metric (per-instance binary coordination
success) and four supporting metrics: F1 over extracted answer tokens
(used by H1 as the single-fragment information-preservation proxy);
achieved compression ratio; generic token-recall; critical-token-recall
(CTR). Aggregation across workloads × seeds is by arithmetic mean; 95 %
confidence intervals are workload-level BCa bootstrap, **never** per-row.

**Three tag distributions** — uniform, skewed, hierarchical — for the H4
governance axis. The hierarchical distribution sets higher classification
levels to imply strict supersets at lower levels, matching enterprise tag
hierarchies (ISO/IEC 27001-style schemes; the broader risk-management
framing follows NIST AI RMF, though the five-tier lattice itself is
industry convention rather than NIST-prescribed).

### C2 — Cliff characterisation + compounding-error model

The headline empirical contribution. Three findings stitched together:

1. **H1:** Source-retention F1 change under compression does not positively
   predict coordination-success change at the workload level for any swept
   compressor.
2. **H2:** A coordination cliff $\tau^*$ exists for each (compressor, family)
   cell with a relative drop $\ge 30\%$ on at least 7 of 12 cells.
3. **H5 / Corollary 1:** Either $\tau^*$ shifts monotonically with planner
   scale (H5 strict), or $\tau^*$ is invariant across planner scale within
   the calibrated regime while only the ceiling $p_0$ shifts (Corollary 1).
   The frontier validation arm extends this across architecture families.

### The compounding-error model

The theoretical framing is a paragraph, not a formal theorem (ADR-008).

Let $T_i^\text{crit}$ be the set of task-critical tokens in workload $i$,
$X_i$ the number that survive compression at ratio $r$, $M_i = |T_i^\text{crit}|$
the total, and $q(r) = E[X_i / M_i]$ the per-round critical-token-recall
function of the compressor. Let $\theta_q \in [0, 1]$ be the **cliff-recall
threshold** — the minimum fraction of task-critical tokens the planner needs
to succeed. The threshold-success model

$$\text{success}_i = \mathbf{1}\!\left[\frac{X_i}{M_i} \ge \theta_q\right]$$

produces, in expectation, the bound $P(\text{success} \mid r) \to \mathbf{1}[q(r) \ge \theta_q]$,
so the cliff position $\tau^*$ solves $q(\tau^*) = \theta_q$. When $N$
sequential compression passes are applied the surviving fraction is
approximately $q(r)^N$ and the cliff equation generalises to
$q(\tau^*) = \theta_q^{1/N}$. **In every experiment $N = 1$**, so the cliff
equation reduces to $q(\tau^*) = \theta_q$. The multi-pass form is recorded
as future work.

This is not a deep theory. It is a sanity argument that makes the cliff
position *predicted* rather than just *observed*, and which lets the cliff
be characterised structurally rather than only descriptively.

### Assumptions A1–A4

The bound rests on four assumptions, each satisfied approximately rather
than strictly. Naming them makes the calibrated-regime predicate
operational.

| ID | Assumption | Honesty note |
|----|------------|---------------|
| **A1** | Round independence of retention; within a pass, per-token retention independent across positions | Trivially satisfied at $N = 1$ across passes. Within a pass, holds approximately for token-level compressors (LLMLingua-2, the instruction-aware filter, truncation) but is violated by Phi-3-Mini extractive (span-level selection induces correlated token-survival events). The phi3-extractive cells are a *robustness check* outside the formal regime. |
| **A2** | Binary token importance — each task-critical token is equally important; non-task tokens are irrelevant | Strongest of the four assumptions. The H4 graded-disclosure measurements are evidence that A2 is a first-order simplification; the predicted-vs-empirical gap absorbs the empirical price the model pays for A2. |
| **A3** | Threshold success — coordination success is binary at a single recall threshold $\theta_q$ | Licensed *operationally* by the cliff sharpness it explains, which is circular in the strict sense. The independent **A3 probe** (Section 5.4 below) breaks the circularity by varying the surviving fraction of task-relevant tokens directly via curated deletion rather than through compression. |
| **A4** | Per-round retention is measured by critical-token-recall, not generic token-recall | This is the substantive methodological commitment of the model and the reason CTR is the canonical recall metric. |

### The calibrated regime

A planner is **in the calibrated regime** if both:

1. baseline coordination success $p_0$ at $r = 1$ is at least $\theta_q$
   (no floor effect); **and**
2. the planner does not recover from sub-threshold information via extended
   reasoning beyond what the priors-only baseline supplies.

The second condition is operationalised by the H4 priors-only baseline
measurement: a planner is in-regime if its accuracy at $q \to 0$ is no
greater than its priors-only rate plus a small slack. This formalisation is
what makes the model's quantitative predictions scope-able; outside the
regime — specifically for extended-reasoning planners (e.g., the GPT-oss
diagnostic) — the cliff position can shift substantially, and that shift is
itself a finding rather than a refutation of the model.

### Direct A3 probe — a non-circular test of the threshold mechanism

The match-rate evaluation of $\theta_q$ on the dense aggregation family is
limited by a circularity in A3: on family-a both "success" and "surviving
critical-token fraction" are near-identical measurements of the same
underlying quantity, so $q(\tau^*) = \theta_q$ is more an identity than a
prediction. The **A3 probe** breaks this by replacing the compressor with a
hand-curated deletion procedure that removes a controlled fraction of the
per-task critical tokens directly. The LLM planner then runs on the
remainder; success is measured as a function of the surviving-token
fraction $k / M$. By construction the surviving fraction is the
experimental knob, and success is read out *after* the knob is set — the
two are not the same measurement.

The probe will be run on family-a (dense) and family-c (distributed). The
expected qualitative outcome is that the dense family exhibits the step
shape A3 posits, while the distributed family exhibits a graded transition
— consistent with the broader information-density scaling claim. If the
dense family does *not* exhibit a step, the compounding-error model's
threshold-success assumption is falsified directly.

### C3 — RAG pipeline catalogue

Three pipelines on FAISS-CPU + HNSW with `BAAI/bge-large-en-v1.5` as the
embedder:

* **P1: compress → retrieve.** Corpus compressed up-front; FAISS index over
  the compressed representation. Retrieval and synthesis both operate on
  compressed text. Trades quality for storage efficiency.
* **P2: retrieve → compress.** Corpus indexed in full; compressor runs as a
  post-retrieval node-processor over the top-$k$ retrieved fragments before
  synthesis. This is the classical LongLLMLingua configuration
  \cite{jiang2024longllmlingua}.
* **P3: joint, conditional on relevance.** Each retrieved fragment is routed
  by its retrieval relevance score $s$ into one of three branches: $s \ge
  \theta_\text{high}$ pass verbatim; $\theta_\text{low} \le s < \theta_\text{high}$
  are compressed; $s < \theta_\text{low}$ are discarded. Defaults
  $\theta_\text{high} = 0.75$ and $\theta_\text{low} = 0.45$ on `bge-cosine`
  similarities are chosen from a pilot HotpotQA score distribution.

Evaluated under **storage-bounded** (FAISS index $\le 100$ MB) and
**accuracy-bounded** (retrieval recall@10 $\le 0.85$) regimes. Cost model in
EUR/workflow grounded in the FCG financial
analysis~\cite{fcgfinancial2026}: amortised on-premises marginal cost
EUR 0.05 per million tokens; frontier-cloud reference USD 3 in / USD 15 out
per million tokens (≈ EUR 2.76 / EUR 13.80 at USD-to-EUR 0.92).

**Cost-attribution caveat.** The cost model uses target compression ratio
rather than achieved ratio because the achieved ratio depends on the
compressor and the request flows through the pipeline as target. For
Phi-3-Mini extractive the ceiling effect makes this an asymmetric error in
favour of P2 (which pays the compressor per query and is therefore most
sensitive to the ceiling). A cost-instrumented re-run that records
*achieved* compression per pipeline is planned (`results/h3_eprice`) so the
cross-pipeline cost comparison can be reported honestly even if it does not
admit a cost-parity claim across all three pipelines.

### C4 — Memory bus + inference-disclosure metric

**Three-layer architecture.** Access layer (FastAPI + PolicyMiddleware
reading the `X-M6-Principal` header), compression layer (the six-implementation
`Compressor` framework above), storage layer (SQLite WAL with append-only
audit log, in-memory TTL scratchpad, FAISS-CPU HNSW vector store). Each
layer depends only on the one below it; the storage backends are hidden
behind `Protocol`s so they can be replaced without touching the access or
compression layers. The architecture is a direct extension of
MemIndex~\cite{saleh2025memindex} with two material differences: compression
is promoted to a first-class layer rather than treated as a downstream
optimisation, and per-slot tags are part of the data model rather than
out-of-band metadata.

**Tag vector.** Every fragment and slot carries a four-field tag vector:
a `uint64` access-control mask, a five-tier classification level
(PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED < SECRET) drawn from
enterprise data-classification practice (ISO/IEC 27001-style schemes; the
broader risk-management framing follows the NIST AI RMF), a tuple of
source identifiers (provenance), and a tuple of parent-slot identifiers
(which previously-compressed slots this slot inherits from). On slot merges
the union ACL mask is the bitwise OR, the union classification is the
maximum; the policy predicate is symmetric for reads and writes.

**Audit log.** Append-only SQLite table with a SHA-256 chain
($\text{chain\_hash} = \text{SHA-256}(\text{prev\_hash} \mathbin\Vert \text{payload\_hash})$).
An `INSTEAD OF UPDATE` and an `INSTEAD OF DELETE` trigger refuse any
mutation; a unit test drops the trigger, edits a `payload_hash` byte, and
confirms `verify()` reports failure. DENY rows are appended with synthesised
slot identifier `deny-<uuid8>` and a 60-second per-(subject, fragment-id)
deduplication so adversarial clients cannot inflate the audit log.

**The novel measurement: summary-level inference disclosure.** For each
fragment tagged at classification $\ge$ CONFIDENTIAL the C1 generator
attaches a list of (yes/no question, ground-truth answer) pairs where the
ground truth is a *protected fact*. Three conditions:

* **`priors`:** reader sees only the workload's public preamble.
* **`baseline`** ($1\times$): reader sees uncompressed source fragments.
* **`compressed_4x`** ($4\times$): reader sees fragments compressed by one
  of the four swept compressors at $4\times$.

A held-out local Llama-3.1-8B reader answers each question. The metric is
the true-positive recovery rate of protected facts. H4 tests (a) whether
baseline > priors (the metric measures something real) and (b) whether
$4\times$ compressed < baseline (compression reduces disclosure).

**Question-template care.** The original H4 question generator can produce
surface-pattern biases (e.g., "at least X" templates with always-YES
ground-truth, "exceed X" with always-NO). A reader can in principle score
high on verb alone. Before the canonical H4 run we will balance the
ground-truth distribution at the question level and use a single comparator
phrasing with parity-based threshold sign. Fragments are unchanged between
biased and unbiased generations so the compression cache remains valid.

**Construct-validity control.** An **oracle field-redaction** comparator
will be run (`results/h4_oracle`): an unrealistic-but-instructive procedure
that redacts *only* the answer-bearing numeric values while leaving every
other token intact. If H4's disclosure-reduction metric is measuring
privacy-specific filtering, the four swept compressors should each beat
oracle redaction by a substantial margin. If the metric is in fact tracking
general information destruction, then aggressive compression and oracle
redaction will reduce disclosure by indistinguishable amounts — a useful
honesty test for the privacy interpretation rather than for the existence
of the effect.

### CAAC — constructive realisation of the compounding-error bound

CAAC sits in the closing chapter as a constructive demonstration of the
model, not as a fifth headline contribution.

**Algorithm.** Given an inner compressor satisfying the `Compressor`
protocol, a per-family $\theta_q$ from `derive_theta()`, and $N_q$ (with
$N = 1$ throughout so $q_\text{min} = \theta_q$):

1. Run the inner compressor at the requested target ratio $r$, measure CTR
   $q$.
2. If $q \ge q_\text{min}$, return as-is.
3. Otherwise binary-search downward over $[r_\text{min}, r]$ for the largest
   $r' \le r$ satisfying $q(r') \ge q_\text{min}$.
4. Floor: $r_\text{min} = 1.5\times$ to prevent abdication to no-compression.

The binary search converges in at most five inner-compress calls per
backed-off fragment.

**Operating-point framing (per ADR-007).** CAAC by construction trades
compression for a recall guarantee, so it cannot strict-dominate a
fixed-ratio compressor that makes the opposite trade. We expect the
strict-Pareto rate against the fixed-ratio baseline to be near zero — that
result, if it appears, is the structural property the model predicts, not a
contribution-killer. The substantive contribution is the *predictable
operating point*: given per-family $\theta_q$ from one calibration pass,
CAAC's selected ratio is determined by the bound rather than by tuning.

**Ablation.** A $\theta_q \in \{0.6, 0.7, 0.8\}$ × $N_q \in \{2, 3, 4, 5\}$
sweep is planned to confirm that the coordination plateau is invariant to
these two knobs and that the primary lever is $r_\text{min}$. A
$r_\text{min}$ sweep is deferred to future work.

---

## 4. Implementation plan (4 weeks)

### Week 1 — Compressors and H1/H2

| Day | Task | Wallclock |
|-----|------|-----------|
| 1 | Add `src/m6/compressors/phi3_extractive.py` (extractive prompt + post-hoc verifier + `_strip_novel_tokens` + LLMLingua-2 fallback) and `src/m6/compressors/truncation.py` (prefix-keep baseline) | code |
| 2 | Pull `phi3:3.8b-mini-instruct-q4_K_M` via Ollama (~2 GB). Smoke-test the verifier on one C1 workload. | model |
| 3 | Run the precompute_cache.py script on the GPU host for all four compressors at the canonical ratios | ~14 h GPU |
| 4 | Run H2 against the cache (10-ratio sweep, ~30 000 cells). H1 metrics are extracted in post. | ~3 h |
| 5 | Generate Chapter 4 figures (Spearman ρ plots, cliff curves, $\tau^*$ table). Run the A3 probe (curated-deletion experiment on family-a and family-c). | analysis + ~1 h |

### Week 2 — H3 + H4 + H5 + frontier

| Day | Task | Wallclock |
|-----|------|-----------|
| 6 | Run H3 (RAG pipelines on C1 family-a + HotpotQA). | ~3 h |
| 7 | Run H4 on the unbiased benchmark (inference disclosure, local Llama reader) and the oracle field-redaction control. | ~3 h |
| 8 | Pull `qwen2.5:1.5b-instruct-q4_K_M`. Run H5 cross-architecture sweep on family-c (the cell on which Corollary 1 is testable across all three local sizes). | ~6 h |
| 9 | Frontier API sweep: Qwen-2.5-72B on family-a × LLMLingua-2; DeepSeek V4 Pro on the same; GPT-oss 120B as the out-of-regime diagnostic. | ~3 h |
| 10 | Buffer / re-runs. Generate Chapter 4 figures (scaling AUC, frontier overlay, predicted-$\tau^*$ band). | analysis |

### Week 3 — Writing (chapters 1–4)

| Days | Chapter |
|------|---------|
| 11-12 | Chapter 3 (System Design and Implementation) and Chapter 4's experimental-design / metric-choice / statistical-protocol scaffolding |
| 13-14 | Chapter 4 §H1 + §H2 + the compounding-error model + the A3 probe |
| 15 | Chapter 4 §Corollary 1 + Frontier validation |
| 16 | Chapter 4 §H3 + §H4 + memory-bus operation benchmark + §Corollary 2 + Reproducibility |
| 17 | Buffer / revisions |

### Week 4 — Discussion, related work, intro, polish

| Days | Task |
|------|------|
| 18 | Chapter 5 (Discussion + CAAC + Limitations + Significance + Future Work) |
| 19 | Chapter 2 (Background and Related Work) — written after results so the gap statements can name what each prior strand does not measure |
| 20 | Chapter 1 (Introduction) + Abstract — written last because the contributions are now fully verified; foreword + abbreviations + appendices |
| 21-22 | Lauri review + revisions |
| 23-24 | Final polish, reproducibility check, PDF build |
| 25 | Submit |

If the GPU host or the Featherless endpoint is unavailable during Week 2,
the frontier sweep slips to Week 4 (replacing one polish day). All other
arms are local.

---

## 5. Evaluation strategy

### 5.1 Compressors and ratios

Compressors per §1 table. Ratios are the dense grid
$\{1, 2, 3, 4, 5, 6, 8, 10, 12, 16\}\times$ for H2 and H5 — both require
piecewise-linear or logistic cliff fitting. H1 reads its subset out of the
same H2 sweep at no extra wallclock. H3 and H4 use $\{1, 4\}\times$ only
(regime comparison, not cliff fitting). The frontier sweep uses a six-ratio
subset $\{1, 2, 4, 6, 8, 16\}$ to keep API cost bounded.

The grid is geometrically denser at the low end (where the cliff sits on the
dense family-a) and sparser at the high end (where every compressor has
collapsed). A fine-grid re-resolution adding $\{1.25, 1.5, 1.75\}$ between
$r = 1$ and $r = 2$ is planned as a diagnostic in case the
deterministic-solver cliff on family-a sits below the coarse-grid midpoint.

### 5.2 Models (no training)

| Model | Source | Role | Local size |
|-------|--------|------|------------|
| `qwen2.5:1.5b-instruct-q4_K_M` | Qwen-2.5, Apache-2.0 | Smallest local planner (H5) | ~1 GB |
| `phi3:3.8b-mini-instruct-q4_K_M` | Microsoft Phi-3, MIT | Extractive compressor + mid-size local planner (H5) | ~2 GB |
| `llama3.1:8b-instruct-q4_K_M` | Meta Llama-3.1 (community licence) | Largest local planner + H4 disclosure reader | ~5 GB |
| `microsoft/llmlingua-2-xlm-roberta-large-meetingbank` | Microsoft, MIT | Token-level compressor | ~1.4 GB |
| `BAAI/bge-large-en-v1.5` | BAAI, MIT | Retriever embedder | ~1.3 GB |
| `BAAI/bge-reranker-base` | BAAI, MIT | Instruction-aware filter reranker | ~300 MB |
| Qwen-2.5-72B-Instruct (Featherless) | Frontier API | Frontier in-regime planner | — |
| DeepSeek V4 Pro (Featherless) | Frontier API | Frontier in-regime planner, different vendor | — |
| GPT-oss 120B (OpenAI Responses API) | Frontier API | Out-of-regime extended-reasoning diagnostic | — |

Total local disk: ~11 GB. Fits the M4 Pro comfortably.

### 5.3 Metrics

* **Quality:** F1 (SQuAD-style token overlap) on the H1 source-retention
  axis; coordination success (binary per-instance) as the primary outcome.
* **Compression:** input/output token ratio (target *and* achieved
  separately so the Phi-3 ceiling is visible); **critical-token-recall
  (CTR)** as the load-bearing recall metric for the cliff equation; generic
  token-recall retained as a reporting column only.
* **Cost:** EUR/workflow at amortised on-premises rate (EUR 0.05 / 1M tokens
  \cite{fcgfinancial2026}); frontier-cloud reference numbers recorded
  through the cost ledger so the per-pipeline cost can be audited.
* **Disclosure:** held-out-reader true-positive recovery on protected facts
  vs priors-only baseline.

### 5.4 Statistical protocol

* **5 seeds per condition.**
* **Workload-level statistical unit.** Per-workload means are computed first;
  95 % confidence intervals are constructed by **resampling workloads with
  replacement**, never by resampling per-row (which double-counts the seed
  dimension) and never by resampling (workload, ratio) pairs (which
  double-counts the ratio dimension as if independent draws).
* **BCa bootstrap** ($n_\text{boot} = 10{,}000$) for H1/H2/H3/H4 verdict
  pipelines; the $\theta_q$ resampling pipeline and the frontier-$\tau^*$
  bootstrap run at $n_\text{boot} = 500$ because per-iteration curve fits
  dominate the cost.
* **Paired Wilcoxon signed-rank** for the two-cell drop comparison in H2,
  chosen over Mann–Whitney $U$ because the same workloads appear in both
  conditions (independence assumption of $U$ is violated).
* **Holm sequentially-rejective correction** applied *within* each
  hypothesis's family (12 cells for H2; 4 compressors for H4; 3 pipelines
  per regime for H3) — *not* across hypotheses, because each hypothesis is
  an independent claim.
* **TOST equivalence test** (Corollary 1) at $\pm 20\%$ tolerance against
  the synthetic-reference $\tau^*$; permissive $\pm 50\%$ band reported
  alongside.
* **Effect sizes:** Cliff's $\delta$ (ordinal), Cohen's $d$ (continuous),
  observed relative drop (H2 verdict bar).
* **No-compression control in every experiment.** Runs are flagged
  `invalid` and excluded if the control-condition variance dominates the
  treatment variance.

### 5.5 Cliff-fitting procedure

For each (compressor, family) cell both a piecewise-linear model and a
logistic
$$f(r) = p_0 + \frac{p_\infty - p_0}{1 + e^{-k(r - \tau^*)}}$$
are fitted to the coordination-success-vs-ratio curve, and the model with
the lower root-mean-squared error is selected. The piecewise fit is
constrained to an interior $10\%$ margin from the sweep boundaries to
prevent the optimiser from parking $\tau^*$ at $r_\text{max} = 16$, a
degenerate fit the unconstrained optimiser would otherwise sometimes select.

---

## 6. Chapter mapping

The compiled manuscript will instantiate **five body chapters** plus front
matter and appendices, matching the Oulu ITEE template's structure for an
engineering MSc thesis with a substantial empirical core.

| Chapter | Content | Hypotheses / contributions |
|---------|---------|------------------------------|
| 1 | Introduction (motivation, multi-fragment workflow scope, problem statement, contributions, novelty, outline) | — |
| 2 | Background and Related Work (transformer architecture and the cost of context; scaling era; cost of running LLMs at scale; compression literature; multi-agent and agentic memory; RAG and long-context benchmarks; privacy in compressed retrieval; the gap this thesis closes) | — |
| 3 | System Design and Implementation (memory bus architecture; RAG pipeline catalogue; compressor framework; C1 benchmark; CTR metric; compression cache; inference backends; design choices and alternatives; scope of evaluation; reproducibility envelope) | C1, C4 delivered |
| 4 | Experiment Design and Protocol (pre-specification + refinement; statistical protocol; metric choices; **H1**; **H2** + fine-grid re-resolution; compounding-error model + A3 probe; **Corollary 1 / H5** + frontier validation; **H3** + cost-attribution caveat; **H4** + construct-validity finding; memory-bus operation benchmark; **Corollary 2 / H6**; reproducibility tiers; verdict summary) | H1, H2, H3, H4, H5/Corollary 1, H6/Corollary 2 |
| 5 | Discussion and Summary (synthesis; CAAC as the constructive realisation; design iteration and methodological course corrections; limitations; significance for practitioners and the field; comparison to industry observations; future work; closing) | CAAC; limitations; future work |
| Back | References (BibLaTeX); Appendix A (memory-bus HTTP contract); Appendix B (long-format results schema); Appendix C (example C1 workload, family a); Appendix D (reproducibility recipe + `curl` trace) | — |

The C1 benchmark sits in Chapter 3 alongside the memory bus and the
compressor framework because it is an *artefact of the system* rather than
a stand-alone contribution chapter. The "implementation" chapter and the
"benchmark" chapter of earlier draft outlines merge cleanly here.

---

## 7. H6 — Real-trace transfer (step-by-step)

H6 is **part of the canonical evaluation**, not optional. Without H6 there
is no evidence that the cliff structure of the synthetic C1 benchmark
transfers to real benchmarks; with H6 there is one concrete data point per
real benchmark.

### 7.1 Why it matters

C1 is synthetic. The standard reviewer question is "does the cliff appear
on a *real* benchmark, or only on your generator?" H6 puts a single data
point on a public benchmark in front of that question.

### 7.2 Dataset choice (verified open-source)

**Primary: MultiHopRAG** (Tang & Yang, COLM 2024 / EMNLP 2024 Findings).

* HuggingFace: `yixuantt/MultiHopRAG` via `datasets.load_dataset`
* Peer-reviewed. Each question requires aggregating evidence across 2–4
  news-article fragments — the same multi-fragment shape as C1 family-a.
  Gold answers and gold supporting documents are provided.
* 2,556 multi-hop questions total; we use 30 for the canonical H6 arm.

**Secondary: HotpotQA** (Yang et al., EMNLP 2018).

* HuggingFace: `hotpot_qa`
* Peer-reviewed. Multi-hop QA on Wikipedia paragraphs. We use 50 questions
  on the LLMLingua-2 cliff sweep to give Corollary 2 a third
  information-density data point distinct from the synthetic dense and
  semi-distributed C1 families.

**Backup (not in canonical run): 2WikiMultiHopQA** (Ho et al., COLING 2020),
held as a slot if MultiHopRAG fragments are too short for compression to
matter.

### 7.3 Step-by-step procedure

```
Step 1. Add a loader: src/m6/corpus/multihoprag.py

    from datasets import load_dataset
    d = load_dataset("yixuantt/MultiHopRAG", split="train")
    # Each example: {query, answer, evidence_list, ...}

Step 2. Add a reformulator: m6.benchmark.workloads.from_multihoprag(rows)
    For each example:
      - Create one Fragment per evidence_list item with PUBLIC tag.
      - Create one SubTask per evidence_list item asking the worker to
        summarise the relevant fact from that fragment.
      - initial_prompt = the query.
      - expected_answer = the gold answer.
      - n_agents = len(evidence_list).

Step 3. Persist 30 reformulated workloads to data/processed/multihoprag-30/.

Step 4. Add configs/experiments/h6.yaml:
    hypothesis: h6
    benchmark_path: data/processed/multihoprag-30
    compressors: [lingua2, phi3-extractive, filter, truncation]
    ratios: [1, 2, 3, 4, 5, 6, 8, 10, 12, 16]
    seeds: [0, 1, 2, 3, 4]
    n_workloads: 30
    workload_families: ["a"]
    backend: ollama
    require_trained_compressors: false

Step 5. Run: make exp-h6                              # ~4 h on M4 Pro

Step 6. Add the HotpotQA sweep target make exp-hotpotqa with the same
    ratio grid against LLMLingua-2 only (the second θ_info data point).

Step 7. Compare τ* and the coordination-success curve to synthetic C1
    family-(a) results. Original H6 tolerance: ±15% on τ*, ±10pp on success.
    If outside tolerance, the sharpened Corollary 2 framing is the
    pre-registered fallback: estimate θ_info per benchmark via
    estimate_task_theta() and report the gap to C1 family-a.
```

### 7.4 What can go wrong

| Risk | Mitigation |
|------|------------|
| MultiHopRAG supporting docs are too short for compression to matter | Fall back to 2WikiMultiHopQA's longer Wikipedia paragraphs |
| Gold answers are 1–2 tokens — F1 binary | Acceptable for the coordination metric; the critic's job is easier |
| Reformulation produces atomic sub-tasks (no real planner work) | Chain the supporting docs into a multi-step retrieval (family-c shape) |
| 30 examples is too small for the cliff to be visible | Bump to 60 if buffer remains in Week 4 |
| Original $\pm 15\%$ tolerance not met | Switch to Corollary 2 framing (pre-registered fallback above) |

---

## 8. Reproducibility tiers

Empirical claims will be tagged with one of three reproducibility tiers so
a reader can calibrate what a re-run delivers.

| Tier | Definition | Members | Canonical artefact |
|------|------------|---------|----------------------|
| **1 — Byte-deterministic local** | A rerun produces a CSV that diffs zero against the published one given the same seed and compression cache | H1/H2/H3 cliff sweep, scoring, bootstrap CIs, figure regeneration | `results/h1_h2_v2/`, `results/h3_final/` |
| **2 — In-distribution local LLM** | Verdict-level aggregates (per-cell means, $\tau^*$ fits) reproduce within published bootstrap CI; individual rows may differ | H4 reader, H5 planner, Phi-3 extractive compressor | `results/h4_unbiased/`, `results/h5_final/` |
| **3 — Frontier API, not reproducible** | Closely-similar but not identical numbers; published CSVs are the canonical record | Qwen-2.5-72B, DeepSeek V4 Pro, GPT-oss 120B | `results/frontier_*/` |

The structure follows the NeurIPS reproducibility-checklist
convention~\cite{pineau2021checklist} of separating *code-and-data
availability* from *computational reproducibility*. Every quantitative claim
will be traceable to one named directory under `results/` through a
`CANONICAL_NUMBERS.md` registry mapping each reported figure to its source
artefact and the key or column that yields it.

---

## 9. Risk register

| Risk | Likelihood | Mitigation |
|------|-----------:|------------|
| Phi-3-Mini paraphrases despite the extractive prompt | Medium | Post-hoc verifier in `Phi3ExtractiveCompressor._verify_extractive`, $15\%$ novel-token tolerance, `_strip_novel_tokens` post-pass, LLMLingua-2 fallback at extractive fraction $< 50\%$ |
| Ollama slow at ratio = 16 over all workloads | Medium | `OLLAMA_NUM_PARALLEL=4`; compression cache (`src/m6/compressors/cache.py`) decouples compression from evaluation |
| H2 cliff doesn't exist (falsified) | Low-medium | Falsification is a thesis-worthy finding; discussion chapter has a "no-cliff" branch drafted |
| H4 disclosure rate is at chance everywhere | Low | Protected-fact questions use specific numeric values not in the priors-only preamble; `tests/unit/test_h4_signal.py` sanity-checks the question bank |
| H5 monotonicity fails on $\ge 2$ families | Medium | Pre-registered Corollary 1 (ceiling–cliff separation) is the sharpened fallback; the local cross-architecture arm and the frontier arm jointly test the invariance claim that the original monotonicity claim relied on |
| Frontier arm $\tau^*$ fits are weakly identified | Medium | Bootstrap CI on $\tau^*$ + TOST equivalence test against the synthetic reference; honest framing as "no shift detected" rather than "equivalence demonstrated" if the strict bar is not met; extended Qwen-72B re-run at $n = 30$ is the targeted tightening |
| GPT-oss 120B violates the calibrated regime | Medium-high (by design) | Reported as an out-of-regime diagnostic, scoped out per ADR-006; preserved on disk with a `STATUS_NONCANONICAL.txt` marker |
| H6 fragments too short for compression | Medium | Fall back to 2WikiMultiHopQA; or pivot to Corollary 2 framing on $\theta_\text{info}$ scaling |
| H4 question-template surface-pattern bias | Medium | Balance YES/NO ground-truth distribution at generation; use single comparator phrasing with parity-based threshold sign; oracle field-redaction control as the construct-validity comparator |
| Wallclock exceeds 4 weeks | Medium | Drop $r_\text{min}$ ablation of CAAC. Drop family (c) from H5. Each saves ~3–6 h. |
| Ollama daemon dies mid-run | Medium | Experiment runners are resumable from the last completed cell via `results/h{N}/.../partial.csv` |
| Phi-3-Mini licence issue | Low | Phi-3 is MIT-licensed; OK for academic use and redistribution |
| Featherless API rate-limits during the frontier sweep | Medium | Frontier sweep is small (180 cells per model); retry with exponential backoff; if DeepSeek V4 Pro fails repeatedly, accept the $n = 10$ result as weak corroboration and document the bootstrap-CI width |

---

## 10. Verified references

Every reference below has been individually checked against the official
proceedings page or a stable DOI. Where a paper is arXiv-only and has not
appeared at a peer-reviewed venue, that is noted explicitly. **Anything that
could not be verified against a venue page has been removed or marked as
preprint.**

### Foundation: transformer architecture and scaling

* Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin.
  **Attention Is All You Need.** *NeurIPS 2017.*
* Kaplan, McCandlish, Henighan, Brown, Chess, Child, Gray, Radford, Wu, Amodei.
  **Scaling Laws for Neural Language Models.** *arXiv 2001.08361 (2020).*
* Hoffmann, Borgeaud, Mensch, Buchatskaya, Cai, Rutherford, de las Casas,
  Hendricks, Welbl, Clark, Hennigan, Noland, Millican, van den Driessche,
  Damoc, Guy, Osindero, Simonyan, Elsen, Rae, Vinyals, Sifre. **Training
  Compute-Optimal Large Language Models** (Chinchilla). *NeurIPS 2022.*

### Cost of inference at scale

* Luccioni, Jernite, Strubell. **Power Hungry Processing: ⚡ Watts ⚡ Driving
  the Cost of AI Deployment?** *FAccT 2024.*
* Samsi, Zhao, McDonald, Li, Michaleas, Jones, Bergeron, Kepner, Tiwari,
  Gadepally. **From Words to Watts: Benchmarking the Energy Costs of Large
  Language Model Inference.** *IEEE HPEC 2023.*
* Pope, Douglas, Chowdhery, Devlin, Bradbury, Levskaya, Heek, Xiao,
  Agrawal, Dean. **Efficiently Scaling Transformer Inference.** *MLSys 2023.*
* Patterson, Gonzalez, Le, Liang, Munguia, Rothchild, So, Texier, Dean.
  **Carbon Emissions and Large Neural Network Training.** *arXiv 2104.10350
  (2021).*

### Context compression (training-free)

* Jiang, Wu, Lin, Yang, Qiu. **LLMLingua: Compressing Prompts for
  Accelerated Inference of Large Language Models.** *EMNLP 2023.*
* Jiang, Wu, Luo, Li, Lin, Yang, Qiu. **LongLLMLingua: Accelerating and
  Enhancing LLMs in Long Context Scenarios via Prompt Compression.**
  *ACL 2024.*
* Pan, Wu, Jiang, Xia, Luo, Zhang, Lin, R\"uhle, Yang, Lin, Zhao, Qiu,
  Zhang. **LLMLingua-2: Data Distillation for Efficient and Faithful
  Task-Agnostic Prompt Compression.** *Findings of ACL 2024.*
* Li, Dong, Zhang, Wang. **Compressing Context to Enhance Inference
  Efficiency of Large Language Models** (Selective Context). *EMNLP 2023.*
* Mu, Li, Goodman. **Learning to Compress Prompts with Gist Tokens.**
  *NeurIPS 2023.*
* Chevalier, Wettig, Ajith, Chen. **Adapting Language Models to Compress
  Contexts** (AutoCompressor). *EMNLP 2023.*
* Ge, Hu, Wang, Wang, Chen, Wei. **In-context Autoencoder for Context
  Compression in a Large Language Model.** *ICLR 2024.*
* Rae, Potapenko, Jayakumar, Hillier, Lillicrap. **Compressive Transformers
  for Long-Range Sequence Modelling.** *ICLR 2020.*
* Cheng, Liu, et al. **xRAG: Extreme Context Compression for Retrieval-
  Augmented Generation with One Token.** *arXiv 2405.13792 (2024).* (Preprint
  at time of writing.)
* Li et al. **Prompt Compression for Large Language Models: A Survey.**
  *arXiv 2410.12388 (2024).*

### Multi-agent systems and agentic memory

* Wu, Bansal, Zhang, Wu, Li, Zhu, Jiang, Zhang, Zhang, Liu, Awadallah,
  White, Burger, Wang. **AutoGen: Enabling Next-Gen LLM Applications via
  Multi-Agent Conversation Framework.** *ICLR 2024 LLM-Agents Workshop /
  COLM 2024.* (Workshop and COLM, not main ICLR.)
* Hong, Zhuge, Chen, Zheng, Cheng, Zhang, Wang, Wang, Yau, Lin, Zhou, Ran,
  Xiao, Wu, Schmidhuber. **MetaGPT: Meta Programming for a Multi-Agent
  Collaborative Framework.** *ICLR 2024.*
* Li, Hammoud, Itani, Khizbullin, Ghanem. **CAMEL: Communicative Agents for
  Mind Exploration of Large Scale Language Model Society.** *NeurIPS 2023.*
* Shinn, Cassano, Berman, Gopinath, Narasimhan, Yao. **Reflexion: Language
  Agents with Verbal Reinforcement Learning.** *NeurIPS 2023.*
* Packer, Wooders, Lin, Fang, Patil, Stoica, Gonzalez. **MemGPT: Towards
  LLMs as Operating Systems.** *arXiv 2310.08560 (2023).* (Preprint.)
* Park, O'Brien, Cai, Morris, Liang, Bernstein. **Generative Agents:
  Interactive Simulacra of Human Behavior.** *UIST 2023.*
* Saleh, Morabito, Dustdar, Tarkoma, Pirttikangas, Lov\'en. **MemIndex.**
  *ACM TAAS 2025.*
* Saleh, Morabito, Dustdar, Tarkoma, Pirttikangas, Lov\'en. **Towards
  Message Brokers for Generative AI: Survey, Challenges, and Opportunities.**
  *ACM CSUR 58(1), 2025.* DOI 10.1145/3742891.
* Xu et al. **A-MEM.** *(2025 preprint.)*
* Chhikara et al. **Mem0.** *(2025 preprint.)*
* Rasmussen et al. **Zep.** *(2025 preprint.)*
* Rezazadeh et al. **Collaborative Memory.** *(2025 preprint.)*

### RAG, long-context, and benchmarks

* Lewis, Perez, Piktus, Petroni, Karpukhin, Goyal, K\"uttler, Lewis, Yih,
  Rockt\"aschel, Riedel, Kiela. **Retrieval-Augmented Generation for
  Knowledge-Intensive NLP Tasks.** *NeurIPS 2020.*
* Sarthi, Abdullah, Tuli, Khanna, Goldie, Manning. **RAPTOR: Recursive
  Abstractive Processing for Tree-Organized Retrieval.** *ICLR 2024.*
* Edge, Trinh, Cheng, Bradley, Chao, Mody, Truitt, Larson. **From Local to
  Global: A GraphRAG Approach to Query-Focused Summarization.**
  *arXiv 2404.16130 (2024).* (Preprint.)
* Guti\'errez, Shu, Gu, Yasunaga, Su. **HippoRAG: Neurobiologically Inspired
  Long-Term Memory for Large Language Models.** *NeurIPS 2024.*
* Asai, Wu, Wang, Sil, Hajishirzi. **Self-RAG: Learning to Retrieve,
  Generate, and Critique through Self-Reflection.** *ICLR 2024.*
* Xu, Shi, Choi. **RECOMP: Improving Retrieval-Augmented LMs with
  Compression and Selective Augmentation.** *ICLR 2024.*
* Guo et al. **Dynamic Adaptive Context-Compression for RAG (ACC-RAG).**
  *arXiv 2025.*
* Hsieh, Sun, Kriman, Acharya, Rekesh, Jia, Zhang, Ginsburg. **RULER:
  What's the Real Context Size of Your Long-Context Language Models?**
  *COLM 2024.*
* Bai, Lv, Zhang, Lyu, Tang, Huang, Du, Liu, Zeng, Hou, Dong, Tang, Li.
  **LongBench: A Bilingual, Multitask Benchmark for Long Context
  Understanding.** *ACL 2024.*
* Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni, Liang. **Lost in the
  Middle: How Language Models Use Long Contexts.** *TACL 2024.*
* Mialon, Fourrier, Swift, Wolf, LeCun, Scialom. **GAIA: A Benchmark for
  General AI Assistants.** *ICLR 2024.*
* Liu, Yu, Zhang, Xu et al. **AgentBench: Evaluating LLMs as Agents.**
  *ICLR 2024.*
* Tang, Yang. **MultiHopRAG: Benchmarking Retrieval-Augmented Generation
  for Multi-Hop Queries.** *COLM 2024 / EMNLP 2024 Findings.*
* Ho, Nguyen-Duc, Sugawara, Aizawa. **Constructing A Multi-hop QA Dataset
  for Comprehensive Evaluation of Reasoning Steps** (2WikiMultiHopQA).
  *COLING 2020.*
* Yang, Qi, Zhang, Bengio, Cohen, Salakhutdinov, Manning. **HotpotQA: A
  Dataset for Diverse, Explainable Multi-hop Question Answering.**
  *EMNLP 2018.*
* Ko\v{c}isk\'y, Schwarz, Blunsom, Dyer, Hermann, Melis, Grefenstette.
  **The NarrativeQA Reading Comprehension Challenge.** *TACL 2018.*

### Privacy in compressed retrieval

* Zhou et al. **PrivacyRAG.** *(2025.)*
* Bassit et al. **SecureRAG.** *(2025.)*
* Li, Wu, Jiang, et al. **SecurityLingua: Efficient Defense of LLM Jailbreak
  Attacks via Security-Aware Prompt Compression.** *CoLM 2025.*
* Addison et al. **CFedRAG: Coordinated Federated Retrieval-Augmented
  Generation.** *(2024.)*

### Statistics and methodology

* Efron, Tibshirani. **An Introduction to the Bootstrap.** Chapman & Hall
  1993.
* Holm. **A Simple Sequentially Rejective Multiple Test Procedure.**
  *Scand. J. Statist.* 6(2), 1979.
* Wilcoxon. **Individual Comparisons by Ranking Methods.**
  *Biometrics Bulletin* 1(6), 1945.
* Mann, Whitney. **On a Test of Whether One of Two Random Variables is
  Stochastically Larger than the Other.** *Ann. Math. Statist.* 18(1),
  1947.
* Cliff. **Dominance Statistics: Ordinal Analyses to Answer Ordinal
  Questions.** *Psych. Bulletin* 114(3), 1993.
* Pineau, Vincent-Lamarre, Sinha, Larivi\`ere, Beygelzimer, d'Alch\'e-Buc,
  Fox, Larochelle. **Improving Reproducibility in Machine Learning Research
  (A Report from the NeurIPS 2019 Reproducibility Program).** *JMLR 2021.*

### Industry analogues (cited as motivation, not as evidence)

* Anthropic. **How We Built our Multi-Agent Research System.** *Anthropic
  Engineering Blog, June 2025.*
* Anthropic. **Effective Context Engineering for AI Agents.** *Anthropic
  Applied AI Blog, 2025.*
* Anthropic. **Context Editing.** *Anthropic, 2025.*
* Anthropic. **Introducing Contextual Retrieval.** *Anthropic News,
  September 2024.*
* Altman. **Please / thank-you compute cost remark.** *(2025, public.)* Cited
  as corroborating colour, not evidence.
* NIST. **AI Risk Management Framework.** *(NIST AI 100-1, 2023.)*

### FCG / Oulu internal

* FCG financial analysis (`fcgfinancial2026`): per-token cost model
  underpinning the EUR/workflow figures in Chapter 4 §H3.
* FCG software architecture (`fcgsoftwarearch2026`): audit-log SHA-256 chain
  pattern that Chapter 3 §3.1 mirrors.
* FCG use case Vignette 3.7 (`fcgusecase2026`): the cross-document
  fact-aggregation source for C1 family-a.

---

## 11. Definition of done

The thesis is "done" when:

1. Hypothesis verdicts (H1–H6, with Corollary 1 and Corollary 2 as the
   pre-registered sharpened forms) are written into the manuscript, each
   with point estimate, $95\%$ bootstrap CI, statistical test result,
   effect size, sample size, Holm correction noted, and one paragraph of
   interpretation.
2. Chapter-headline figures are reproducible from a single `make` target
   each. Every figure caption is a complete sentence; every legend is
   labelled; the palette is colour-blind-safe.
3. Every cited paper has been verified to exist at a peer-reviewed venue
   OR is explicitly labelled as a preprint / industry blog.
4. The reproducibility package (`docker-compose.yml`, model and data cards
   under `docs/`, pinned `requirements.lock.txt`, reference release tag)
   is uploaded with one-command reproduction targets for every headline
   figure.
5. Every quantitative claim in the manuscript is traceable to one named
   directory under `results/` through the `CANONICAL_NUMBERS.md` registry.
6. Lauri has signed off on the discussion chapter (post-submission review
   per the grilling-session decision; no mid-sprint feedback gate).

Target score against the Oulu MSc rubric: **8.5 / 10** on the strength of
the cliff + cross-architecture invariance + disclosure triple, lifted to
9 / 10 if the H6 transfer arm holds within the original tolerance and the
Corollary 2 fallback is not needed. The plan does not control rubric items
#1 (scope), #2 (challenge), and #8 (initiative) — those are won by the work
itself; it controls items #3 (outlining), #4 (intro + SoTA), #5 (achievement
of aims), #6 (evaluation of results), #7 (significance), #9 (language), and
#10 (layout).

---

*End of plan-v3 (post round-5 polish).*
