# Technical Reference v3 — Implementation Detail per Hypothesis

> **Companion document to `plan-v3.md`.** This document specifies exactly
> *how* to implement each of the five core hypotheses (plus the optional
> H6), including code paths, configs, expected wallclock, falsification
> tests, and the precise CSV columns the runner must emit. Use this as the
> reference when writing code; the plan is the *what*, this is the *how*.

---

## Table of contents

1. [Architecture deltas vs v1](#1-architecture-deltas-vs-v1)
2. [The Phi-3-Mini extractive compressor](#2-the-phi-3-mini-extractive-compressor)
3. [H1 — QA vs coordination correlation](#3-h1--qa-vs-coordination-correlation)
4. [H2 — Coordination cliff](#4-h2--coordination-cliff)
5. [H3 — RAG pipeline placement](#5-h3--rag-pipeline-placement)
6. [H4 — Inference disclosure](#6-h4--inference-disclosure)
7. [H5 — Three-point model-size scaling](#7-h5--three-point-model-size-scaling)
8. [Optional H6 — MultiHopRAG transfer](#8-optional-h6--multihoprag-transfer)
9. [Token-recall metric (compounding-error model)](#9-token-recall-metric-compounding-error-model)
10. [How to actually run everything (chronological)](#10-how-to-actually-run-everything-chronological)

---

## 1. Architecture deltas vs v1

What stays the same:

* The 3-layer memory bus (access / compression / storage).
* The `Compressor` Protocol, the `CompressedSlot` dataclass.
* LLMLingua-2 wrapper, instruction-aware filter, identity control.
* C1 benchmark generator (all 3 families).
* FastAPI service, SQLite append-only audit log, FAISS-CPU vector store.
* AutoGen v0.4 deterministic + Ollama orchestrators.
* Statistical protocol (bootstrap CI, paired bootstrap, Mann-Whitney,
  Holm correction, Cliff's δ, Cohen's d).
* CLI + Makefile targets + reproduce-chapter scripts.

What changes for v3:

| Component | Change |
|-----------|--------|
| `src/m6/compressors/icae.py` | Dead code; kept for git history but excluded from `make_compressor` factory. |
| `src/m6/compressors/training/*` | Same — dead. |
| `src/m6/compressors/phi3_extractive.py` | **NEW** — implements the extractive Phi-3-Mini compressor with post-hoc verifier. |
| `src/m6/inference/ollama_backend.py` | Add `model_size` introspection helper for H5. |
| `src/m6/experiments/h5_model_scaling.py` | **NEW** — three-point scaling on family (a). |
| `src/m6/experiments/h6_real_trace.py` | **NEW (optional)** — MultiHopRAG-via-Ollama. |
| `src/m6/corpus/multihoprag.py` | **NEW (optional)** — loader + reformulator. |
| `src/m6/evaluation/metrics/token_recall.py` | **NEW** — per-fragment token-recall measure for the compounding-error model. |
| Headline configs `configs/experiments/h{1,2,3,4,5}.yaml` | Replace `icae` with `phi3-extractive`; set `require_trained_compressors: false`. |

---

## 2. The Phi-3-Mini extractive compressor

### File: `src/m6/compressors/phi3_extractive.py`

Implements the `Compressor` Protocol. Construction parameters:

```python
class Phi3ExtractiveCompressor:
    compressor_id: str = "phi3-extractive"
    tokenizer_id: str = "phi3"

    def __init__(
        self,
        *,
        ollama_model: str = "phi3:3.8b-mini-instruct-q4_K_M",
        ollama_url: str = "http://127.0.0.1:11434",
        target_ratio: float = 4.0,
        max_input_tokens: int = 4096,
        verify_extractive: bool = True,
        max_violation_rate: float = 0.05,
    ): ...
```

### The prompt (frozen)

```text
You are a passage selector, NOT a writer. Your job is to select the minimal
set of contiguous spans from the PASSAGE that a downstream reader would need
to answer the QUESTION.

RULES:
  1. Output ONLY tokens that appear verbatim in the PASSAGE.
  2. Do NOT summarise, paraphrase, infer, or add new tokens.
  3. Separate selected spans with a single newline.
  4. Target output length: at most {target_tokens} tokens.
  5. If unsure whether a span is relevant, include it.

PASSAGE:
{passage}

QUESTION (task hint):
{task_hint}

SELECTED SPANS:
```

Temperature `0.0`. `num_predict = max(target_tokens, 32)`.

### Post-hoc verifier

```python
def _verify_extractive(self, source: str, output: str) -> tuple[bool, float]:
    """Return (passed, fraction_extractive).

    A token is "extractive" if it appears in the source. Punctuation and
    whitespace are stripped before the membership test (small forgiveness
    margin — the model often re-quotes with the cleaner punctuation).
    """
    src_tokens = set(_normalise(t) for t in re.findall(r"\w+", source))
    out_tokens = [_normalise(t) for t in re.findall(r"\w+", output) if t]
    if not out_tokens:
        return True, 1.0
    n_extractive = sum(1 for t in out_tokens if t in src_tokens)
    fraction = n_extractive / len(out_tokens)
    return fraction >= (1.0 - self.max_violation_rate), fraction
```

On a verifier failure, the compressor retries once with a stricter prompt
("Repeat the source spans verbatim. DO NOT alter casing or punctuation.").
On second failure, falls back to LLMLingua-2 at the same target ratio and
records a `_fallback_count` for later reporting.

### Unit tests

`tests/unit/test_phi3_extractive.py`:

* `test_extractive_prompt_does_not_hallucinate` — feed a short paragraph,
  assert all output tokens are in the source.
* `test_target_ratio_respected` — output length within ±20% of target.
* `test_fallback_on_paraphrase` — when verifier fails twice, returns
  LLMLingua-2 output.
* `test_compressor_id_is_phi3_extractive` — for cache-key correctness.

### Why this design

The cognitive-offloading concern is the single biggest critique against
LLM-as-compressor. By forcing token-level extraction with a verifier we
restrict Phi-3-Mini to a *selection* task — closer to LLMLingua-2's
spirit than to abstractive summarisation. The extractive constraint is
visible in the prompt AND enforced post-hoc; a reviewer can verify both.

---

## 3. H1 — QA vs coordination correlation

### Falsifiable claim (verbatim)

> Spearman ρ between the single-agent QA-accuracy delta and the
> multi-agent coordination-success delta across matched compression ratios
> is below 0.6 on at least two of the three compressors with the default
> 8B planner, with 95% bootstrap CI excluding 0.6 from above on the same
> two.

### Runner: `src/m6/experiments/h1_qa_vs_coordination.py`

Already implemented; no v3 change. The only v3 difference: `cfg.compressors`
now reads `["lingua2", "phi3-extractive", "filter"]` instead of `[..., "icae"]`.

### Procedure

For each $(c \in \text{compressors}, r \in \{1, 2, 4, 8, 16\}, w \in C1,
s \in \{0..4\})$:

1. **Single-agent QA derivative.** Build a single-agent QA task from $w$:
   same source fragments concatenated, planner's initial prompt becomes
   the question, no workers, no critic. Record F1.
2. **Full planner-worker-critic loop** with the same $(c, r, w, s)$.
   Record `coord_success`, `subtask_acc`, `rounds`, `critic_flagged_rate`.

Compute deltas per workload and seed:

* $\Delta_\text{qa}(c, r, w, s) = \text{F1}(c, r, w, s) - \text{F1}(c, 1, w, s)$
* $\Delta_\text{coord}(c, r, w, s) = \text{coord}(c, r, w, s) - \text{coord}(c, 1, w, s)$

Per compressor, compute Spearman $\rho(\Delta_\text{qa}, \Delta_\text{coord})$
across the union of $(r > 1) \times \text{workload} \times \text{seed}$
cells. Bootstrap CI 10,000 resamples.

### Output schema (`results/h1/<run_id>/results.csv`)

```
compressor, ratio, workload_family, workload_id, seed,
qa_f1, qa_em, coord_success, subtask_acc, rounds,
critic_flagged_rate, delta_qa, delta_coord
```

Plus `spearman.json`:

```json
{
  "lingua2":         {"rho": 0.42, "p_value": 0.001, "ci_low": 0.31, "ci_high": 0.52, "supported": true},
  "phi3-extractive": {"rho": 0.55, "p_value": 0.003, "ci_low": 0.44, "ci_high": 0.65, "supported": true},
  "filter":          {"rho": 0.71, "p_value": 0.000, "ci_low": 0.62, "ci_high": 0.79, "supported": false},
  "h1_supported_at_least_2_of_3": true
}
```

### Wallclock

Shared with H2 (single sweep produces both verdict sets).

---

## 4. H2 — Coordination cliff

### Falsifiable claim

> For each (compressor, workload) cell with the default 8B planner, a
> piecewise-linear function $f(r; a, b, \tau)$ fitted to the
> (ratio, success) curve detects a cliff at $\tau^{*}$ with relative drop
> $\ge 30\%$. Mann-Whitney U on below-vs-above-$\tau$ samples returns
> Holm-adjusted $p < 0.05$ on at least 7 of the 9
> (compressor × workload-family) cells. $\tau^{*}$ varies by workload but
> not by compressor family within $\pm 20\%$.

### Runner: `src/m6/experiments/h2_coordination_cliff.py`

Already implemented. v3 difference: the sweep ratios use the denser
$\{1, 2, 3, 4, 5, 6, 8, 10, 12, 16\}$ list.

### Procedure

1. Sweep ratios for each cell with 5 seeds.
2. Per cell: fit `m6.evaluation.cliff_fitting.fit_piecewise` →
   $(\tau, \text{slope}_\text{left}, \text{slope}_\text{right}, \text{rmse},
   \text{drop}_\text{rel})$.
3. Mann-Whitney U: success below $\tau$ vs success above $\tau$,
   alternative `"greater"`.
4. Holm correction within the $\{H_1, H_2, H_5\}$ family.

### Headline figure (Chapter 5)

For each compressor in $\{\text{LLMLingua-2}, \text{Phi-3-extractive},
\text{filter}\}$, a 3-panel figure (one per workload family) showing:

* Mean coordination success across seeds vs ratio (line + error band).
* Piecewise-linear fit overlay.
* $\tau^{*}$ marked with a vertical line.
* `drop_rel` and `p_holm` annotated in the panel corner.

### Output schema

`results/h2/<run_id>/per_cell.csv`:

```
compressor, workload_family, tau, slope_left, slope_right,
drop_rel, rmse, n_below, n_above, mw_u, mw_p, mw_p_holm,
verdict_drop, verdict_p, verdict_overall
```

Plus `tau_spread.json` reporting per-family `(max_tau - min_tau)/mean_tau`
and whether it falls within the ±20% claim.

### Wallclock

~10 h on M4 Pro (22,500 cells × ~1.6 s/cell on a deterministic backend).

---

## 5. H3 — RAG pipeline placement

### Falsifiable claim

> P1 vs P2 effect-size $\ge 5$ pp F1 with paired-bootstrap CI excluding
> $0$ in **both** budget regimes, with the sign flipping between regimes
> (P1 > P2 storage-bounded; P2 > P1 accuracy-bounded). P3 wins the
> combined $F_1 / \text{EUR}$ ranking in both regimes with Holm-adjusted
> $p < 0.05$.

### Runner: `src/m6/experiments/h3_rag_placement.py`

Already implemented with in-code verdict computation. Dispatched via
`m6.experiments.base.configure_runner("h3", ...)` which imports
`H3Runner` from this module.

### Two budget regimes

* **Storage-bounded:** FAISS index size capped at 100 MB. Both P1 and P2
  tune their chunking to fit. At ratio 8×, P1 compresses fragments before
  indexing (small index); P2 indexes full fragments (large index — may
  not fit).
* **Accuracy-bounded:** retrieval recall@10 capped at 0.85. Both tune
  chunking to meet that recall ceiling.

P3 swept on $(\theta_\text{high}, \theta_\text{low}) \in
\{(0.75, 0.45), (0.70, 0.50), (0.80, 0.40)\}$.

### Cost model

`m6.pipelines.cost_model.eur_for_call(model, in_tokens, out_tokens)`.
For H3 the stub model is `gpt-4o-mini` with fixed token estimate
(`_STUB_INPUT_TOKENS = 1500`, `_STUB_OUTPUT_TOKENS = 200`) — gives a
per-pipeline EUR/query without making API calls.

### Output

`results/h3/<run_id>/results.csv` + `verdicts.json` with per-regime
paired-bootstrap diff, leader-by-score, Holm-adjusted p-values, and the
boolean `h3_supported`.

### Wallclock

~3 h.

---

## 6. H4 — Inference disclosure

### Falsifiable claim

> The disclosure metric distinguishes priors-only from baseline
> ($\text{recall}_\text{baseline} > \text{recall}_\text{priors}$,
> paired-bootstrap $p < 0.05$), AND $4\times$ compression reduces
> disclosure relative to baseline
> ($\text{recall}_{4\times} < \text{recall}_\text{baseline}$,
> paired-bootstrap $p < 0.05$, Holm-corrected within $\{H_4\}$).

### Runner: `src/m6/experiments/h4_tag_preservation.py`

(Filename retains the v1 nomenclature for git-history continuity; the
hypothesis it runs in v3 is **H4 inference disclosure**, not the v1
"tag preservation" framing. Dispatched via
`configure_runner("h4", ...)` which imports `H4Runner` from this file.)

Already implemented and now defaults to **local Ollama** (no API key).

### Procedure

For each workload with `protected_facts` non-empty:

1. **Priors-only:** reader sees the workload's `initial_prompt` only,
   none of the source fragments. Reader is local Llama-3.1-8B via Ollama.
2. **Baseline (1×):** reader sees the uncompressed source fragments
   verbatim.
3. **C4 / 4× compressed:** reader sees the Phi-3-extractive compressed
   summaries at $r = 4$.

For each (workload, condition), ask the reader each yes/no question from
`workload.protected_facts`. Recall = fraction of true-positive answers.

### Note on the falsification claim

The original v1 framing was "C4 < baseline" assuming a *trained*
tag-preserving compressor reduces disclosure. In v3 we ask whether
**any compression** at $4\times$ reduces disclosure relative to the
uncompressed baseline. If true: compression has an incidental privacy
benefit. If false: compression preserves enough source text for fact
recovery — also a publishable finding.

### Output

`results/h4/<run_id>/disclosure.csv`:

```
condition (priors|baseline|compressed_4x), workload_id, seed,
n_protected_facts, recall_protected, recall_false_positive
```

Plus `verdicts.json` with both paired-bootstrap tests.

### Wallclock

~3 h (Ollama inference for ~200 protected-fact questions × 3 conditions ×
2-3 yes/no per question).

---

## 7. H5 — Three-point model-size scaling

### Falsifiable claim

> Across $\{1.5\text{B}, 3.8\text{B}, 8\text{B}\}$ with LLMLingua-2 as the
> fixed compressor, $\tau^{*}_{8B} \ge \tau^{*}_{3.8B} \ge \tau^{*}_{1.5B}$
> on at least 2 of 3 workload families, with the largest-vs-smallest gap
> $\ge 1.5$ ratio units.

### Runner: `src/m6/experiments/h5_model_scaling.py` (NEW)

```python
class H5Runner(ExperimentRunner):
    HYPOTHESIS = "h5"

    PLANNER_MODELS = [
        ("qwen2.5:1.5b-instruct-q4_K_M", "1.5b"),
        ("phi3:3.8b-mini-instruct-q4_K_M", "3.8b"),
        ("llama3.1:8b-instruct-q4_K_M", "8b"),
    ]

    async def run(self) -> ExperimentResult:
        workloads = self.load_workloads()  # C1 family-(a) only, 30 instances
        compressor = make_compressor("lingua2", target_ratio=1.0)
        rows = []
        for model_id, size_label in self.PLANNER_MODELS:
            # Switch the orchestrator's planner LLM to model_id via Ollama.
            for r in self.cfg.ratios:  # {1, 2, 3, 4, 5, 6, 8, 10, 12, 16}
                for w in workloads:
                    for s in self.cfg.seeds:
                        result = await self._score_with_planner(
                            w, model_id, compressor, r, s
                        )
                        rows.append(self.emit_row(
                            compressor="lingua2", ratio=r,
                            workload_family=w.family.value,
                            workload_id=w.workload_id, seed=s,
                            metric="coord_success", value=result,
                            model_size=size_label,
                        ))
        df = pd.DataFrame(rows)
        verdict = self._fit_tau_per_size(df)
        self.write_results(df, verdicts=verdict)
        ...
```

### Per-family τ\* fitting

For each `(size, family)` pair, fit `fit_piecewise` to the mean
coord-success curve. Verdict block:

```json
{
  "tau_per_size_per_family": {
    "a": {"1.5b": 2.1, "3.8b": 3.8, "8b": 5.4},
    "b": {"1.5b": 1.9, "3.8b": 3.0, "8b": 4.7},
    "c": {"1.5b": 2.5, "3.8b": 2.7, "8b": 3.0}
  },
  "monotonic_per_family": {"a": true, "b": true, "c": false},
  "gap_8b_minus_1.5b_per_family": {"a": 3.3, "b": 2.8, "c": 0.5},
  "h5_supported": true
}
```

### Wallclock

~6 h. 3 planner sizes × 30 workloads × 10 ratios × 5 seeds = 4,500 cells;
Ollama ~5 s/cell averaged across model sizes.

---

## 8. Optional H6 — MultiHopRAG transfer

### Step-by-step implementation

**Step 1.** Add `src/m6/corpus/multihoprag.py`:

```python
from datasets import load_dataset
from m6.benchmark.schemas import (
    Workload, WorkloadFamily, Fragment, SubTask, ProtectedFact, TagDistribution,
)
from m6.memory_bus.schemas import Classification, TagVector

def load_multihoprag_30(seed: int = 0) -> list[Workload]:
    """Load 30 MultiHopRAG questions, reformulate as C1 workloads."""
    ds = load_dataset("yixuantt/MultiHopRAG", split="train")
    rng = np.random.default_rng(seed)
    picks = rng.choice(len(ds), size=30, replace=False)
    out: list[Workload] = []
    for i, idx in enumerate(picks):
        ex = ds[int(idx)]
        fragments = [
            Fragment(
                fragment_id=f"mhr-{i:03d}/ev-{j}",
                text=ev["fact"] + " (source: " + ev.get("title", "") + ")",
                tags=TagVector(acl_mask=0, classification=Classification.PUBLIC),
                task_hint=ex["query"],
            )
            for j, ev in enumerate(ex["evidence_list"])
        ]
        sub_tasks = tuple(
            SubTask(
                sub_task_id=f"mhr-{i:03d}/sub-{j}",
                description=f"Summarise the fact relevant to: {ex['query']}",
                expected_solver=f"worker-{j}",
                expected_answer=ev["fact"][:200],
            )
            for j, ev in enumerate(ex["evidence_list"])
        )
        out.append(Workload(
            workload_id=f"mhr-{i:03d}",
            family=WorkloadFamily.CROSS_DOC_FACT_AGGREGATION,
            seed=seed,
            tag_distribution=TagDistribution.UNIFORM,
            fragments=tuple(fragments),
            sub_tasks=sub_tasks,
            initial_prompt=ex["query"],
            n_agents=len(fragments),
            expected_answer=ex["answer"],
        ))
    return out
```

**Step 2.** Add `src/m6/experiments/h6_real_trace.py`:

```python
class H6Runner(H2Runner):
    """H6 is structurally H2 on a different workload set."""
    HYPOTHESIS = "h6"

    def load_workloads(self) -> list[Workload]:
        from m6.corpus.multihoprag import load_multihoprag_30
        return load_multihoprag_30(seed=self.cfg.seeds[0])

    def _compute_verdicts(self, df) -> dict[str, object]:
        synth_path = self.cfg.out_dir + "/../h2/.../verdicts.json"
        # Compare τ* and curve shape; tolerance ±15% on τ, ±10pp on success.
        ...
```

**Step 3.** Add `configs/experiments/h6.yaml`:

```yaml
hypothesis: h6
benchmark_path: data/processed/multihoprag-30   # populated by load_multihoprag_30
compressors: ["lingua2", "phi3-extractive", "filter", "none"]
ratios: [1, 2, 3, 4, 5, 6, 8, 10, 12, 16]
seeds: [0, 1, 2, 3, 4]
n_workloads: 30
workload_families: ["a"]
model_size: "8b"
backend: ollama
out_dir: results
include_no_compression_control: true
require_trained_compressors: false
notes: "H6 real-trace transfer to MultiHopRAG (Tang & Yang, EMNLP 2024)."
```

**Step 4.** Add to Makefile:

```makefile
exp-h6-real: ## H6 — real-trace transfer to MultiHopRAG.        # WALLCLOCK ~4h
	$(PY) -m m6.experiments.cli run --hypothesis h6 --config configs/experiments/h6.yaml
```

**Step 5.** Comparison plot in Chapter 7. Two side-by-side coordination-vs-ratio
curves: synthetic C1 family-(a) on the left, MultiHopRAG on the right. Mark
$\tau^{*}$ on each. Verdict if both within tolerance.

### Wallclock

~4 h. 4 compressors × 30 workloads × 10 ratios × 5 seeds = 6,000 cells;
Ollama ~2.4 s/cell averaged.

---

## 9. Token-recall metric (compounding-error model)

### File: `src/m6/evaluation/metrics/token_recall.py`

```python
def token_recall(source: str, compressed: str, gold_answer: str) -> float:
    """Fraction of gold-answer tokens that survive in the compressed text.

    Used by the compounding-error model in Chapter 5. ``q = token_recall``
    is the per-step preservation fraction; surviving information after
    N rounds is approximately q^N.
    """
    gold_tokens = set(_normalize_tokens(gold_answer))
    if not gold_tokens:
        return 1.0
    compressed_tokens = set(_normalize_tokens(compressed))
    return len(gold_tokens & compressed_tokens) / len(gold_tokens)
```

### How the compounding-error model produces a predicted τ\*

```python
def predicted_tau(token_recall_curve: list[tuple[float, float]],
                  n_rounds: int, theta: float) -> float:
    """Given the per-ratio token-recall curve and the planner's threshold,
    return the predicted cliff position.

    Args:
        token_recall_curve: list of (ratio, q) measured on the corpus.
        n_rounds: typical rounds-to-completion (e.g., 3 for family (a)).
        theta: fraction of source information the planner needs to succeed.

    Returns:
        Predicted τ* = the ratio at which q^n_rounds first crosses theta.
    """
    q_required = theta ** (1.0 / n_rounds)
    for ratio, q in sorted(token_recall_curve):
        if q < q_required:
            return ratio
    return float("inf")  # cliff outside the swept range
```

The Chapter 5 figure overlays the predicted τ\* (from this function) on
top of the empirical τ\* (from `fit_piecewise`). Closeness — even within
a factor of 2 — supports the compounding-error story.

---

## 10. How to actually run everything (chronological)

```bash
# Week 1, Day 1 — code
cd m6-thesis
git checkout -b v3-experiments
# Write src/m6/compressors/phi3_extractive.py from the spec in §2 above.
# Add tests/unit/test_phi3_extractive.py.
make check                                    # ruff + mypy + unit tests

# Week 1, Day 2 — model
ollama pull phi3:3.8b-mini-instruct-q4_K_M    # ~2 GB
ollama pull qwen2.5:1.5b-instruct-q4_K_M      # ~1 GB (for H5)
ollama pull llama3.1:8b-instruct-q4_K_M       # ~5 GB (default planner + H4 reader)

# Week 1, Day 2 — quick smoke
make baselines-smoke                          # ~2 min; verifies the pipeline

# Week 1, Days 3-4 — H1 + H2 (single sweep)
# Edit configs/experiments/h2.yaml:
#   compressors: ["lingua2", "phi3-extractive", "filter"]
#   require_trained_compressors: false
make exp-h2                                   # ~10 h
# H1 is extracted from the same data in post-processing:
.venv/bin/python -c "
from m6.experiments.h1_qa_vs_coordination import H1Runner
H1Runner.from_h2_csv('results/h2/<latest>/results.csv').write()
"

# Week 1, Day 5 — figures
make reproduce-ch5                            # generates the Chapter 5 figure

# Week 2, Day 6 — H3 (RAG pipeline placement)
make exp-h3                                   # ~3 h

# Week 2, Day 7 — H4 (inference disclosure)
make exp-h4                                   # ~3 h (code file: h4_tag_preservation.py)

# Week 2, Day 8 — H5
make exp-h5                                   # ~6 h, 3-point model-size scaling

# Week 2, Day 9 — figures
make reproduce-ch6 && make reproduce-ch7

# Optional, Week 2 Day 10 — H6 real-trace
# Add src/m6/corpus/multihoprag.py + src/m6/experiments/h6_real_trace.py
.venv/bin/python -c "
from m6.corpus.multihoprag import load_multihoprag_30
from m6.benchmark.generator import _dump_workload
import pathlib, json
out_dir = pathlib.Path('data/processed/multihoprag-30')
out_dir.mkdir(parents=True, exist_ok=True)
with (out_dir / 'family-a.jsonl').open('w') as f:
    for w in load_multihoprag_30(seed=0):
        f.write(json.dumps(_dump_workload(w)) + '\\n')
"
make exp-h6-real                              # ~4 h

# Week 3 onward — writing
# Paste verdicts from results/h{1,2,3,4,5,6}/*/verdicts.json into the
# % RESULTS: placeholders in thesis_latex/Chapters/{experiments,summary}.tex.
cd thesis_latex && latexmk -pdf -bibtex main.tex
```

---

### Definition-of-done for each artefact

| Artefact | DoD |
|----------|-----|
| `phi3_extractive.py` | All 4 unit tests pass; verifier fallback rate < 5% on a 20-workload smoke set |
| H1 verdict | `spearman.json` exists with all 3 compressors + `h1_supported_at_least_2_of_3` |
| H2 verdict | `per_cell.csv` complete; ≥ 7/9 cells have `verdict_overall=true`; `tau_spread` figures emitted |
| H3 verdict | Sign flip in `regimes` dict + P3 leader in both regimes |
| H4 verdict | Both paired-bootstrap p-values < 0.05 OR a documented falsification finding |
| H5 verdict | `tau_per_size_per_family` complete; monotonic on ≥ 2/3 families; gap ≥ 1.5 |
| H6 verdict | $|\tau^{*}_\text{real} - \tau^{*}_\text{synth}| / \tau^{*}_\text{synth} \le 0.15$ AND coord-success curves within 10 pp |
| Chapter 5 figure | One panel per compressor; cliff fit overlaid; predicted-vs-empirical τ\* labelled |
| Chapter 6 figure | P1/P2/P3 bars across both regimes with bootstrap CI error bars; EUR/query annotated |
| Chapter 7 figure | Disclosure recall under (priors, baseline, 4×) with paired-bootstrap CI |
| Optional Ch.7 H6 subsection | Synthetic-vs-real curve comparison plot |
