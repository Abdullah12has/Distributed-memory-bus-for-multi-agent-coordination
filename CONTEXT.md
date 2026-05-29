# M6 Thesis — Domain Glossary

This file is a glossary of the precise meaning of each domain term. It is
not a spec, a decision log, or a status report. When a term in this file
appears in code, writing, or discussion, it carries this exact meaning.

When a new term is resolved, add it here. When a term's meaning is
disputed, fix the dispute before adding.

---

## θ_q — cliff-recall threshold

The recall fraction at which coordination success first drops below a
success threshold. Per-family; depends on the recall metric (token_recall
vs critical_token_recall). Appears in Theorem 1's cliff equation
`q(r*) = θ_q^(1/N)`. Derived by `derive_theta()` in
`src/m6/theory/cliff_prediction.py`. CAAC's `q_min` is set to this value.

Canonical per-family values under critical_token_recall (h1_h2_v2):
a=0.632, b=0.838, c=0.590.

Aliases to avoid: "theta_q", "θ", "cliff threshold", "task threshold".
Use **θ_q** in writing; never write just "θ" without subscript when
both θ_q and θ_info are in scope.

## θ_info — task information density

An AUC-based estimate of how concentrated task-essential information is
in a task. θ_info ≈ 1 − normalized AUC of (coord_success / baseline) vs
ratio. Dense tasks (numeric aggregation): high θ_info. Distributed tasks
(multi-doc QA): low θ_info. Per-task; **not** per-family within C1.
Derived by `estimate_task_theta()`. Appears in Corollary 2's
"theta scales with information density" claim.

Canonical values: C1 family-a ≈ 0.97 (dense), MHR ≈ 0.48 (distributed),
HotpotQA ≈ 0.37 (highly distributed).

**θ_q and θ_info are not interchangeable.** A single task has one θ_info
and a (per-family, per-recall-metric) family of θ_q values. Confusing
them was a real failure mode during the 2026-05-29 audit reconciliation.

## τ* (tau-star) — cliff position

The compression ratio at which coordination success drops below a
threshold (typically 0.5 × baseline). Per (compressor, family, planner)
cell. Predicted by Theorem 1 as `r* where q(r*) = θ_q^(1/N)`; with N=1,
`r* where q(r*) = θ_q`. Empirical τ* extracted via piecewise-linear or
logistic fit to coord_success curve.

## q(r) — token-recall curve

The fraction of task-relevant tokens preserved at compression ratio r.
The compressor-specific curve that feeds Theorem 1. Two flavors:
- **token_recall(r)** — generic set-overlap recall
- **critical_token_recall(r)** — family-specific tokens (multi-digit
  numbers for family-a, all numbers for b, chain references + FINAL for c)

CAAC and Theorem 1 use **critical_token_recall** end-to-end after the
2026-05-29 framework reconciliation.

## N — compression passes

The number of sequential compression steps between source and the
solver's view of a fragment. **In all M6 experiments, N=1** (single
compression pass before the solver). The Theorem 1 statement allows
arbitrary N but is empirically only validated at N=1. The q^N
formulation degenerates to q with N=1, i.e., `q_min = θ_q`.

## p₀ — baseline success probability

Coordination success probability at r=1 (no compression). Per
(planner, compressor, family) cell. Used by Theorem 1(iv) and
Corollary 1 (ceiling-cliff separation: model capacity affects p₀,
not τ*).

## Coordination success

A binary per-cell outcome: did the planner (or deterministic solver)
produce the expected coordination outcome? Computed from trace logs
without LLM-in-the-loop scoring. Per-workload metric; aggregated as
a mean across workloads × seeds.

**"Coordination" denotes task structure, not agent architecture.**
The planner (deterministic regex for H1/H2; single LLM call for
H5/H6/frontier) must combine information drawn from multiple
fragments. This is the **multi-fragment** property (see next entry).
The AutoGen multi-round backend exists in `src/m6/orchestrator/` but
was excluded from production experiments due to round-to-round LLM
variance dominating the compression signal. The thesis manuscript
title (per ADR-009) renames the scope to "Multi-Fragment LLM
Workflows" to match this evaluation methodology end-to-end; the
codebase project name is preserved for back-compat.

## Multi-fragment

A property of the task — not of the agent architecture. A workload
is **multi-fragment** if the planner needs information distributed
across two or more fragments (each compressible independently) to
produce the expected answer. All three C1 task families are
multi-fragment by construction: family-a aggregates numbers across
fragments; family-b assigns sub-tasks specified across fragments;
family-c chains references across fragments.

Multi-fragment is distinct from multi-agent. A multi-agent system
*may* operate over multi-fragment workloads (the memory bus is
designed for this case), but multi-fragment evaluation does not
require multi-agent simulation — a single planner with multi-fragment
input is sufficient to study the compression effects this thesis
measures.

Per ADR-009, the manuscript title carries "Multi-Fragment LLM
Workflows" as its primary scope. The codebase, GitHub repository
name, and existing planning artefacts (plan-v3) retain "Multi-Agent
Coordination" for back-compat.

## Compressor families

Four compressors are evaluated:
- **LLMLingua-2** — token-level XLM-RoBERTa classifier. Calibrated.
- **Phi-3-Mini extractive** — verbatim span selection via Ollama,
  with novel-token stripping + LLMLingua-2 fallback. Saturates: even
  at r=1, recall < 1 (CTR=0.399 for family-a).
- **Instruction-aware filter** — TF-IDF + cross-encoder reranker.
- **Truncation** — prefix truncation baseline. Brutal; predicts cliff
  at no-compression for family-c.
- **Identity** — no compression (control).

CAAC is a *wrapper*, not a fifth family — it wraps an inner compressor
with theorem-grounded backoff.

## Task families (C1 benchmark)

- **Family-a (cross-document fact aggregation)**: sum N numbers across
  fragments. Critical tokens = multi-digit numbers. Dense (θ_info ≈ 0.97).
- **Family-b (constraint-satisfaction planning)**: assign sub-tasks to
  workers under capacity constraints. Critical tokens = all numbers.
- **Family-c (multi-step retrieval)**: follow chain references to a
  final answer. Critical tokens = "entry X" / "FINAL-XXXX" patterns.

## Calibrated regime (for Theorem 1)

The set of (planner, compressor, task) configurations for which the
theorem's assumptions hold:
- A1 (round independence) — approximately true at N=1
- A2 (binary token importance) — approximately true (H4 measures graded
  importance; discussed in limitations)
- A3 (threshold success) — approximately true (cliffs are sharp)
- A4 (per-round retention) — measured as critical_token_recall

Extended-reasoning planners (e.g., GPT-oss 120B) violate A3 by
recovering from sub-threshold information via reasoning chains. These
are explicitly out-of-scope for Theorem 1's quantitative predictions
and excluded from the validation set.
