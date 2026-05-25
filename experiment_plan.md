# Experiment Improvement Plan: NeurIPS/ICLR Publication Readiness

**Target**: NeurIPS 2026 / ICLR 2027 main track
**Working title**: *Coordination Cliffs: Sharp Phase Transitions in Multi-Agent LLM Systems Under Context Compression*
**Date**: 2026-05-25

---

## Part A: Strengthening Existing Results (No New GPU Time Needed)

This section details analysis, visualization, and reframing work that can be performed on already-collected CSV data from the GPU server results directories (`h1_h2_v3_quick2`, `h3_full`, `h4_v2`, `h5_full`, `h5_diagnostic`, `h5_diag1_cliff`, `h5_diag4_14b`).

---

### A1. H1 (QA vs Coordination Decorrelation)

**Current state**: SUPPORTED (3/3 compressors below rho=0.6). Data in `h1_h2_v3_quick2/results.csv`, columns: `compressor`, `ratio`, `family`, `workload_id`, `seed`, `qa_f1`, `qa_em`, `coord_success`, `subtask_acc`, `rounds`, `critic_rate`, `token_recall`.

#### A1.1 Missing Statistical Tests

1. **Cliff's delta (ordinal effect size)**: Plan-v3 section 5.4 specifies Cliff's delta and Cohen's d, but neither is computed in `run_h1_h2.py`. For each compressor, compute Cliff's delta between (delta_qa, delta_coord) pairs where rho < 0.6 vs a hypothetical strong-correlation baseline.
   - Implementation: ~15 lines in `compute_h1_verdict()` using `scipy.stats` or manual computation.
   - Report in the paper as: "The effect size of the decorrelation was large (Cliff's delta = X.XX) for all three compressors."

2. **Partial correlation controlling for ratio**: The current Spearman rho pools all ratios. A reviewer may argue that both qa_f1 and coord_success decline with ratio, creating a spurious positive correlation. Compute partial Spearman controlling for ratio (i.e., within each ratio band, correlate delta_qa and delta_coord across workloads).
   - If partial rho is lower than marginal rho: the decorrelation is even stronger after removing ratio confound.
   - If partial rho is higher: the marginal rho is suppressed by ratio, which is also interesting (ratio affects both but differently).
   - Implementation: `pingouin.partial_corr()` or manual rank-residualization. ~20 lines.

3. **Per-family breakdown**: Currently rho is computed across all families pooled. Report per-family rho to show whether family-a (numeric aggregation) vs family-c (pattern matching) have different correlation structures. This is free data -- just groupby `family` before computing Spearman.

#### A1.2 Visualization

1. **Scatter plot: delta_qa vs delta_coord**, colored by compressor, one panel per family. Each point is a (workload, ratio) pair. Annotate the Spearman rho + CI in each panel. This is Figure 1 of the paper's H1 section.
   - X-axis: `qa_f1(ratio=r) - qa_f1(ratio=1)` (information preservation drop)
   - Y-axis: `coord_success(ratio=r) - coord_success(ratio=1)` (coordination drop)
   - Expected pattern: points scatter widely, not along the diagonal, confirming weak correlation.

2. **Filter's negative rho visualization**: The filter compressor has rho = -0.287, meaning coord improves slightly as qa_f1 drops. Show this as a separate inset or callout figure. This is a publishable micro-finding: the reranker preserves task-relevant tokens disproportionately.

#### A1.3 Reframing for Maximum Impact

- **Rename**: "QA accuracy vs coordination" -> "Information preservation vs coordination success" (per insight 25, CRITICAL-1). The metric (`qa_f1`) measures token-level information survival, not answer accuracy.
- **Thesis statement**: "Standard single-agent QA metrics are unreliable proxies for multi-agent coordination quality. A system designer who optimizes for QA F1 under compression may inadvertently cross the coordination cliff."
- **Position against**: LLMLingua-2 (Pan et al., ACL 2024) evaluates compression via QA F1 on MeetingBank/LongBench but never measures coordination effects. RECOMP (Xu et al., ICLR 2024) evaluates on single-agent QA tasks. Neither paper considers multi-agent downstream effects.

---

### A2. H2 (Coordination Cliff)

**Current state**: SUPPORTED (8/9 cells). Data in `h1_h2_v3_quick2/results.csv`.

#### A2.1 Missing Analysis

1. **Logistic fit comparison**: Per insight 25 (CRITICAL-3), `_fit_logistic()` was added but its results need to be reported. For each (compressor, family) cell, compare piecewise RMSE vs logistic RMSE. If logistic fits better, report logistic tau (inflection point). This addresses the reviewer question "why piecewise, not smooth?"
   - The compounding-error model predicts `q^N`, which is smooth, not piecewise. A logistic fit is theoretically more appropriate.
   - Code location: `run_h1_h2.py:364-399`. The `model_selected` field already exists; just report it.

2. **Effect size for H2 drops**: Compute Cohen's d or Cliff's delta for the pre-cliff vs post-cliff comparison in each cell. Currently only Mann-Whitney (now Wilcoxon per fix) p-value is reported.
   - Formula: `d = (mean_above - mean_below) / pooled_sd`
   - Report alongside the drop percentage.

3. **Cross-compressor tau comparison**: Report whether tau* differs across compressors within each family (not just within-compressor). If filter/c has no cliff (tau=N/A) but lingua2/c does (tau=1.0), this directly supports Theorem 1(iii) -- cliff position is compressor-dependent.
   - Simple table: rows = families, columns = compressors, cells = tau* with CI.

4. **Compounding-error prediction validation**: Use `src/m6/theory/cliff_prediction.py::predicted_tau()` with the empirical `token_recall` column from the CSV. For each (compressor, family):
   - Extract the token_recall curve: `df.groupby('ratio')['token_recall'].mean()`
   - Compute `predicted_tau(curve, n_rounds=3, theta=0.65)`
   - Compare to empirical tau from piecewise/logistic fit
   - This is the single most important strengthening for the paper -- it validates the theorem empirically.
   - Implementation: ~30 lines of post-processing script.

#### A2.2 Visualization

1. **Hero cliff figure** (Figure 1 in the paper): Coordination success (y-axis) vs compression ratio (x-axis), one line per compressor, for family-a. Show the sharp 1.0 -> 0.0 transition. Annotate the predicted tau from Theorem 1 as a vertical dashed line.
   - Data: `df[df['family']=='a'].groupby(['compressor','ratio'])['coord_success'].mean()`

2. **Three-panel cliff shape comparison**: One panel per family (a, b, c). Shows that family-a has a sharp cliff, family-c has a gradual decline, family-b has a qa_f1 cliff but coord stays high.
   - This demonstrates that cliff shape is task-dependent (another publishable finding).

3. **Predicted vs empirical tau scatter**: One point per (compressor, family) pair. X = predicted tau from Theorem 1, Y = empirical tau from logistic fit. The closer to the y=x line, the better the theory.

#### A2.3 Reframing

- **Phase transition language**: Frame the cliff as a first-order phase transition (sharp boundary between "coordination works" and "coordination fails"), not a gradual degradation. Reference the phase transition literature (Barak et al., NeurIPS 2022).
- **Practical implication**: "A system deployer cannot linearly trade compression for quality. There is a hard boundary."

---

### A3. H3 (RAG Pipeline Placement)

**Current state**: NOT SUPPORTED (P1 > P2 in both regimes, no sign-flip). Data in `h3_full/results.csv`. Columns: `compressor`, `pipeline`, `regime`, `workload_id`, `f1`, `eur_per_workflow`, `f1_over_eur`.

#### A3.1 Missing Analysis

1. **Per-compressor P1 vs P2 effect**: Currently the verdict aggregates across compressors. Report P1-P2 difference for each (compressor, regime) cell. If some compressors show sign-flip while others do not, this is nuanced.

2. **Cost-effectiveness analysis**: Report `f1_over_eur` (F1 per EUR) as the primary metric, not just F1. P3 trivially dominates because it passes high-relevance fragments verbatim. The interesting finding is the *cost* of the P1 advantage over P2.
   - Report: "P1 achieves +7.7pp F1 over P2 at equal cost, OR achieves equal F1 at X% lower cost."

3. **Achieved compression ratio**: If `h3_full` records actual token counts, compute the achieved compression ratio (which may differ from target, especially for phi3-extractive with the salvage path). Compare target vs achieved.

#### A3.2 Visualization

1. **Pareto frontier**: F1 (y-axis) vs EUR/workflow (x-axis), one marker per (pipeline, compressor, regime) cell. Show that P3 dominates the Pareto frontier, P1 is second, P2 is third.

2. **Bar chart**: Grouped bars for P1/P2/P3, one cluster per regime, bars colored by compressor. Error bars from bootstrap CI.

#### A3.3 Reframing

- **Do NOT claim to falsify LongLLMLingua** (per insight 25, IMPORTANT-8). LongLLMLingua claims efficiency, not accuracy.
- **Frame as**: "Compress-first (P1) preserves content quality better than retrieve-first (P2) across both storage-bounded and accuracy-bounded regimes. This is because compression is the quality bottleneck, not retrieval."
- **Negative results are publishable** at NeurIPS if clearly presented. The fact that pipeline order matters less than compressor choice is itself useful guidance.

---

### A4. H4 (Inference Disclosure)

**Current state**: SUPPORTED (signal +5pp, lingua2 reduction -14.3pp). Data in `h4_v2/results.csv`. Columns: `compressor`, `condition` (priors/baseline/compressed), `workload_id`, `question_id`, `correct`, `expected`, `predicted`, `has_error`.

#### A4.1 Missing Analysis

1. **Per-question-type analysis**: Are "yes" and "no" questions equally affected by compression? Group by `expected` and compute disclosure rates separately.

2. **Per-compressor disclosure gradient**: Plot disclosure rate (y-axis) vs compression aggressiveness (x-axis, ordered as: filter < phi3-extractive < lingua2 by measured `token_recall`). This shows the compression-privacy gradient.
   - Already known: lingua2 -14.3pp, phi3 -3.2pp, filter -0.7pp. The gradient is monotonic.

3. **Odds ratio**: Report odds ratio (baseline vs compressed) for each compressor as a standardized effect measure. More interpretable than raw percentage point difference for reviewers.

4. **Error analysis**: Per insight 25 (IMPORTANT-5), rows with `has_error=True` should be filtered. Report how many errors occurred and whether they are balanced across conditions.

#### A4.2 Visualization

1. **Privacy-quality tradeoff figure** (Figure 5 in the NeurIPS plan): Dual y-axis plot. X = compressor (ordered by aggressiveness), left Y = coord_success at 4x (from H2 data), right Y = disclosure rate at 4x. Shows the tension: more aggressive compression reduces disclosure but also reduces coordination.

2. **Bar chart**: Three groups (priors, baseline, compressed), one bar per compressor, showing disclosure rate with bootstrap error bars.

#### A4.3 Reframing

- **Terminology**: Use "protected-fact recovery rate" instead of "inference disclosure" (per insight 25, METHOD-11). Not DP, not k-anonymity -- an empirical privacy operationalization.
- **Connection to H2**: "Compression creates a privacy benefit proportional to its aggressiveness, but the coordination cliff imposes a hard limit on how aggressively one can compress."

---

### A5. H5 (Model-Size Scaling)

**Current state**: NOT SUPPORTED (gap negligible). Data in `h5_full/results.csv` and multiple diagnostic runs. Columns: `planner_model`, `planner_model_name`, `compressor`, `ratio`, `family`, `workload_id`, `seed`, `coord_success`, `f1`, `subtask_acc`.

#### A5.1 Missing Analysis

1. **Baseline (ratio=1) success rates table**: Report `coord_success` at ratio=1.0 for each (model, family) cell. This is the "ceiling" that model size affects. Currently buried in insights but not in any figure.

2. **Cliff shape overlay**: For family-a, overlay the coordination curve for all 4 models (1.5B, 3.8B, 8B, 14B). The curves should cliff at the same x-position but start at different y-intercepts. This is the key visualization for "ceiling not cliff."

3. **AUC (area under cliff curve)**: Instead of tau* (which has boundary bias), use AUC of the coord_success vs ratio curve as a model-quality metric. This is well-defined even for gradual declines.
   - `auc = np.trapz(coord_success_means, ratio_values) / (ratio_max - ratio_min)`
   - Compare AUC across models: 8B should dominate.

4. **Acknowledging phi-3 confound**: Phi-3 (3.8B) scores 0% on family-a even at ratio=1. This is a model capability failure, not a scaling finding. Report this explicitly and exclude the (phi3, family-a) cell from the scaling analysis.

#### A5.2 Visualization

1. **Cliff overlay figure**: coord_success vs ratio, one line per model, for family-a. Include 14B from `h5_diag4_14b`. Show that all lines cliff at 3-4x but start at different baselines (1.5B: 0.25, 8B: 1.0, 14B: 0.9).

2. **Heatmap**: Models (rows) x ratios (columns), color = coord_success, one panel per family. Visually shows where each model fails.

3. **AUC bar chart**: One bar per model, showing AUC across ratios. Clear monotonic ordering expected.

#### A5.3 Reframing

- **Reframe as positive finding**: "Model size affects ceiling, not cliff position" is MORE interesting than "tau* increases monotonically." It validates Theorem 1(iii).
- **Practical implication**: "Deploying a larger planner does not allow more aggressive compression. The safe compression ratio is determined by the compressor, not the model."
- **This is the surprise finding** that reviewers at NeurIPS reward.

---

### A6. H6 (MultiHopRAG Transfer)

**Current state**: Code implemented (`run_h6.py`, `multihoprag.py`), not yet run on GPU.

#### A6.1 Post-Run Analysis Plan

1. **Direct curve comparison**: Overlay C1-family-a cliff curve and MultiHopRAG cliff curve on the same axes. If within +/-15% on tau*, H6 is supported.

2. **Per-question difficulty analysis**: Group MultiHopRAG questions by number of supporting documents (2-hop vs 3-hop vs 4-hop). Do more hops produce earlier cliffs?

---

### A7. Cross-Hypothesis Analysis (New, No GPU Needed)

These analyses combine data from multiple experiments already collected.

#### A7.1 Unified Compression Quality Table

Create a master table: rows = compressors, columns = (token_recall at 4x, qa_f1 at 4x, coord_success at 4x, disclosure_rate at 4x, H3 P1 F1 at 4x). This gives reviewers a single-glance comparison of all compressor properties.

Source data: H1/H2 CSV for token_recall + qa_f1 + coord_success, H4 CSV for disclosure_rate, H3 CSV for P1 F1.

#### A7.2 Cross-Hypothesis Holm Correction

Plan-v3 specifies Holm correction within families {H1, H2, H5} and {H3} and {H4}. Currently each runner applies Holm only within its own tests. Implement cross-hypothesis correction in a post-processing script:

```python
# Collect all p-values from H1 (3 per-compressor tests) + H2 (9 cells) + H5 (3 families)
all_pvals = h1_pvals + h2_pvals + h5_pvals  # total: 3 + 9 + 3 = 15
adjusted = holm_bonferroni(all_pvals)
```

Implementation: ~30 lines in a standalone `cross_hypothesis_correction.py` script.

#### A7.3 Compounding-Error Model Summary Figure

A single figure combining:
- Left panel: empirical token_recall curve q(r) per compressor
- Middle panel: predicted P(success) = p0 * q(r)^3 for N=3
- Right panel: empirical coord_success overlaid on predictions

This validates Theorem 1 visually and is the figure that makes the paper.

---

## Part B: New Experiments for Publication Quality

Experiments are listed in priority order. Each entry specifies whether it is required (reviewer dealbreaker) or nice-to-have (bonus).

---

### B1. CAAC vs Fixed-Ratio Baselines [CRITICAL]

**Description**: Run `run_caac.py` (already implemented) comparing CAAC-wrapped compressors against fixed-ratio baselines on all three C1 families. CAAC uses token_recall monitoring to back off compression per-fragment when approaching the cliff, using Theorem 1's q_min threshold.

**Hypothesis**: CAAC achieves 70-80% of target compression while maintaining >80% coordination success, compared to 0% for fixed-ratio compression at the same target on family-a.

**Implementation effort**: Already implemented in `src/m6/compressors/caac.py` (~150 lines) and `src/m6/experiments/run_caac.py` (~275 lines). Needs only a production run.

**GPU hours**: ~4 hours (3 compressors x 6 target ratios x 50 workloads x 3 families x 3 seeds, reusing compressed cache).

**Impact**: CRITICAL -- this is the method contribution. Without CAAC, the paper is "we measured something." With CAAC, it is "we measured it, explained it, and fixed it."

**Required vs Nice-to-have**: REQUIRED. NeurIPS expects method + theory + experiments. CAAC is the method.

**CLI**: `python -m m6.experiments.run_caac --out results/caac_full`

---

### B2. Frontier Model Validation (GPT-4o-mini) [CRITICAL]

**Description**: Run `run_frontier.py` (already implemented) to validate the coordination cliff at frontier scale using GPT-4o-mini via OpenAI API. Same C1 benchmark, same LLMLingua-2 compressor, but a much larger planner model.

**Hypothesis**: The cliff occurs at the same compression ratio (3-4x) as with 8B local models, validating Theorem 1(iii) that cliff position is model-independent.

**Implementation effort**: Already implemented in `src/m6/experiments/run_frontier.py` (~386 lines). Needs API key and ~$20 budget.

**GPU hours**: 0 (API calls). Wall-clock ~2 hours. Cost: ~$20.

**Impact**: CRITICAL -- addresses the "only tested on small models" concern. If GPT-4o-mini shows the same cliff at 3-4x, Theorem 1 is validated across 10x scale difference.

**Required vs Nice-to-have**: REQUIRED. Reviewers will ask "does this hold for real models?"

**CLI**: `OPENAI_API_KEY=sk-xxx python -m m6.experiments.run_frontier --out results/frontier_gpt4omini`

---

### B3. H6 MultiHopRAG Transfer Validation [HIGH]

**Description**: Run `run_h6.py` (already implemented) on GPU. Tests whether the coordination cliff found on synthetic C1 transfers to real multi-hop QA data from MultiHopRAG (Tang & Yang, EMNLP 2024).

**Hypothesis**: Cliff appears at similar position (+/-15% on tau*) on real data, demonstrating the phenomenon is not an artifact of synthetic benchmark design.

**Implementation effort**: Already implemented in `src/m6/experiments/run_h6.py` and `src/m6/corpus/multihoprag.py`. Needs only a production run.

**GPU hours**: ~1 hour (30 workloads x 10 ratios x 5 seeds x 1 compressor x 1 planner = 1,500 Ollama calls).

**Impact**: HIGH -- directly addresses the "only synthetic benchmark" concern.

**Required vs Nice-to-have**: Required for a strong submission. The single biggest defensibility improvement.

**CLI**: `python -m m6.experiments.run_h6 --synth-results results/h5_full --out results/h6_full`

---

### B4. Simple Truncation Baseline [CRITICAL]

**Description**: Add a "truncation" baseline that simply takes the first N tokens of each fragment (where N is determined by the target ratio). This is the simplest possible compression strategy and MUST be included as a control. Every compression paper at NeurIPS includes truncation.

**Hypothesis**: Truncation cliff occurs at a different position than LLMLingua-2 because truncation preserves prefix tokens regardless of importance, while LLMLingua-2 selects high-importance tokens.

**Implementation effort**: ~40 lines in `src/m6/compressors/truncation.py`:
```python
class TruncationCompressor:
    def compress(self, fragment, ratio=1.0, **kw):
        tokens = fragment.text.split()
        keep = max(1, int(len(tokens) / ratio))
        return " ".join(tokens[:keep])
```
Register in `src/m6/compressors/__init__.py::make_compressor()`. Then re-run H1/H2 with the additional compressor.

**GPU hours**: ~2 hours for H1/H2 sweep (truncation itself is instant; only the coordination scoring needs compute).

**Impact**: CRITICAL -- every compression paper needs this baseline. Reviewers at ICLR 2024 (RECOMP) and ACL 2024 (LLMLingua-2) both include truncation.

**Required vs Nice-to-have**: REQUIRED. Absence of truncation baseline is a guaranteed reviewer complaint.

---

### B5. Full H1/H2 Rerun with 10 Ratios [HIGH]

**Description**: The production H1/H2 run (`h1_h2_v3_quick2`) used 5 ratios (1,4,8,12,16) instead of the planned 10 (1,2,3,4,5,6,8,10,12,16). The piecewise/logistic fit needs denser sampling around the cliff region (2-6x) to pin down tau* precisely.

**Hypothesis**: Denser ratio sampling around 2-6x will produce tighter confidence intervals on tau* and resolve the boundary bias (tau* clustering at 15.9-16.0).

**Implementation effort**: 0 lines of code. Just change the ratio list in the run command or config.

**GPU hours**: ~6-8 hours (3 compressors x 10 ratios x 3 families x 50 workloads x 5 seeds).

**Impact**: HIGH -- fixes the tau* boundary bias problem documented in insight 16. The current piecewise fit defaults to tau=16.0 because it has too few points in the 2-6x range where the actual cliff occurs.

**Required vs Nice-to-have**: Required. The current 5-ratio results have the boundary bias artifact.

**CLI**: `python -m m6.experiments.run_h1_h2 --out results/h1_h2_full_10ratios`

---

### B6. Selective Context as 4th Compressor [HIGH]

**Description**: Add Selective Context (Li et al., EMNLP 2023) as a fourth compressor. Selective Context uses self-information (negative log probability) to rank tokens for removal, compared to LLMLingua-2's classifier-based approach and phi3-extractive's LLM-guided span selection.

**Hypothesis**: Selective Context produces a cliff at a different position than LLMLingua-2, validating that cliff position is compressor-specific (Theorem 1(iii)). Since Selective Context preserves high-perplexity tokens (opposite of LLMLingua-2 which preserves high-importance tokens), the cliff may occur earlier (lower ratio).

**Implementation effort**: ~80 lines in `src/m6/compressors/selective_context.py`. The `selective-context` pip package provides the core logic; the wrapper adapts it to the `Compressor` protocol.

**GPU hours**: ~3 hours for H1/H2 sweep with this additional compressor.

**Impact**: HIGH -- adds diversity to compressor comparison. Three compressors that all use different selection mechanisms (classifier, LLM-guided, self-information) showing different cliff positions is strong evidence for Theorem 1.

**Required vs Nice-to-have**: Nice-to-have but strongly recommended. Three compressors is the minimum; four is more convincing.

---

### B7. CAAC Ablation Studies [HIGH]

**Description**: Run CAAC with varied hyperparameters to demonstrate robustness:
- Theta sensitivity: {0.50, 0.60, 0.65, 0.70, 0.80}
- N sensitivity: {1, 2, 3, 4, 5}
- Per-compressor CAAC: wrap lingua2, phi3-extractive, filter separately

**Hypothesis**: CAAC is robust to theta within +/-0.1 and N within +/-1 of the true values. Different compressors under CAAC produce different backing-off patterns (lingua2 backs off more on numeric fragments).

**Implementation effort**: ~30 lines to parameterize theta/N in `run_caac.py` (already exposed in `CAACConfig`). The per-compressor runs just vary `inner_compressors`.

**GPU hours**: ~3 hours for theta sweep + ~2 hours for N sweep + ~3 hours for per-compressor = ~8 hours total.

**Impact**: HIGH -- ablations are expected at NeurIPS for any proposed algorithm.

**Required vs Nice-to-have**: Required. Reviewers will ask "how sensitive is CAAC to theta and N?"

---

### B8. Seed Variance Analysis [MEDIUM]

**Description**: Analyze variance across seeds for all experiments. Currently 5 seeds are used for H1/H2 and H5, but the inter-seed variance is not reported. Compute:
- Standard deviation of coord_success across seeds at each (compressor, ratio, workload) triple
- Coefficient of variation (CV) across seeds
- Whether verdict changes if any single seed is dropped (leave-one-out stability)

**Hypothesis**: The coordination cliff is robust across seeds (CV < 0.1 at ratio=1 and ratio=4), confirming that the deterministic solver's binary output is not sensitive to seed-dependent randomness.

**Implementation effort**: ~50 lines of post-processing on existing CSVs. No new runs needed.

**GPU hours**: 0.

**Impact**: MEDIUM -- strengthens statistical rigor but unlikely to change conclusions.

**Required vs Nice-to-have**: Nice-to-have but easy to do.

---

### B9. HotpotQA Cliff Sweep [MEDIUM]

**Description**: Add 50 HotpotQA multi-hop questions reformulated as C1-style workloads. Run the cliff sweep with LLMLingua-2 at ratios {1, 2, 4, 8, 16}. This is a second real-world benchmark alongside MultiHopRAG (H6).

**Hypothesis**: The cliff appears on HotpotQA at a similar position to C1 family-a (numeric aggregation is similar in difficulty to multi-hop reasoning).

**Implementation effort**: ~100 lines for a HotpotQA loader and reformulator (similar to `multihoprag.py`). ~50 lines for a runner (or reuse `run_h6.py` with a different dataset path).

**GPU hours**: ~2 hours.

**Impact**: MEDIUM -- strengthens external validity. Two real benchmarks is better than one.

**Required vs Nice-to-have**: Nice-to-have. MultiHopRAG (B3) already addresses the "only synthetic" concern.

---

### B10. Cost/Latency Measurements [MEDIUM]

**Description**: Measure and report actual computational costs:
- Compression latency per fragment (ms) for each compressor at each ratio
- End-to-end pipeline latency (compression + coordination)
- GPU memory footprint during compression
- Tokens per second throughput for Ollama inference

This data is partially available from timestamps in the CSVs. Supplement with explicit timing measurements.

**Hypothesis**: LLMLingua-2 is ~100x faster than phi3-extractive (0.01s vs 11s per fragment, as measured in insight 11). CAAC adds <10% overhead from binary search.

**Implementation effort**: ~40 lines of timing instrumentation in each runner. Alternatively, compute from existing `timestamp` columns in CSVs (if timestamps are per-row).

**GPU hours**: ~1 hour for a dedicated timing run with 20 workloads.

**Impact**: MEDIUM -- cost analysis is expected in applied ML papers. LLMLingua-2's speed advantage (from their paper: 3-6x faster than LLMLingua) should be confirmed in our multi-agent setting.

**Required vs Nice-to-have**: Nice-to-have for NeurIPS (they care more about novelty), but REQUIRED for ICLR (which values thoroughness).

---

### B11. GPT-4o Spot Check [MEDIUM]

**Description**: Run 10 workloads on GPT-4o (not mini) at ratios {1, 4} as a ceiling validation. If GPT-4o at ratio=1 achieves near-perfect coordination, it establishes the upper bound on model capability.

**Hypothesis**: GPT-4o at ratio=1 achieves >95% coord_success. At ratio=4, it either (a) still cliffs (validates theorem) or (b) partially survives (higher theta).

**Implementation effort**: 0 -- already implemented in `run_frontier.py`. Just change config to use GPT-4o.

**GPU hours**: 0. Cost: ~$15.

**Impact**: MEDIUM -- useful data point but GPT-4o-mini already covers the "frontier" angle.

**Required vs Nice-to-have**: Nice-to-have.

---

### B12. Human Evaluation (Small-Scale) [MEDIUM]

**Description**: Have 2-3 human annotators evaluate 30 compressed fragments (10 per compressor at 4x compression) on a 1-5 scale for:
- Readability: "Can you understand the main points?"
- Completeness: "Are key facts preserved?"
- Coherence: "Does the text flow logically?"

Compare human judgments to automated token_recall and qa_f1 metrics.

**Hypothesis**: Human readability correlates weakly with coordination success (supporting H1 -- QA/readability is a poor proxy for coordination). Lingua2 outputs are less readable than phi3-extractive but lose more task-relevant content.

**Implementation effort**: ~2 hours to prepare the annotation spreadsheet + ~3 hours annotator time per person.

**GPU hours**: 0.

**Impact**: MEDIUM -- human evaluation adds credibility but is not essential for the core claims.

**Required vs Nice-to-have**: Nice-to-have for NeurIPS. More important for ICLR (which is pickier about evaluation).

---

### B13. MemGPT Paging Baseline [LOW]

**Description**: Implement a MemGPT-style (Packer et al., ICLR 2024) paging baseline where fragments are stored in archival storage and retrieved on-demand via function calls, rather than compressed and placed in context. This tests whether virtual context management is an alternative to compression.

**Hypothesis**: MemGPT-style paging avoids the cliff entirely (no information loss from compression) but incurs higher latency (multiple LLM calls per retrieval).

**Implementation effort**: ~200 lines for a simplified MemGPT paging wrapper. Would need to integrate with Ollama function calling.

**GPU hours**: ~6 hours (paging requires multiple LLM calls per workload).

**Impact**: LOW -- interesting comparison but adds significant implementation complexity. The paper can mention MemGPT paging as an alternative approach in related work without empirically comparing.

**Required vs Nice-to-have**: Nice-to-have. No reviewer will require this for a first submission.

---

### B14. RECOMP Trained Compressor Baseline [LOW]

**Description**: Add RECOMP's extractive compressor (Xu et al., ICLR 2024) as a trained baseline. RECOMP trains a Contriever-based dual encoder on task-specific data.

**Hypothesis**: RECOMP may produce a later cliff (higher tau*) because it is trained to preserve answer-relevant information.

**Implementation effort**: ~150 lines + training time (~2 hours on GPU for the Contriever encoder). Requires reformulating C1 workloads as RECOMP training data.

**GPU hours**: ~2 hours training + ~3 hours sweep = ~5 hours.

**Impact**: LOW -- the paper is positioned around training-free compression. Adding a trained baseline is interesting but tangential to the main contribution.

**Required vs Nice-to-have**: Nice-to-have. Could be mentioned as future work.

---

### B15. Multi-Round CAAC (Dynamic N) [LOW]

**Description**: Extend CAAC to dynamically estimate N (number of coordination rounds) per workload based on task complexity, rather than using a fixed N=3.

**Hypothesis**: Dynamic N improves CAAC's per-fragment compression decisions by adapting to task difficulty.

**Implementation effort**: ~50 lines to add a complexity estimator to CAAC (e.g., based on fragment count or expected answer complexity).

**GPU hours**: ~2 hours.

**Impact**: LOW -- incremental improvement over CAAC. Better suited for a follow-up paper.

**Required vs Nice-to-have**: Nice-to-have.

---

## Part C: Publication Timeline (14-Day Plan)

Assumes: GPU server available 24/7, experiments run overnight, analysis during the day. OpenAI API key available for frontier validation.

---

### Day 1 (May 26): Data Collection and Truncation Baseline

**Morning**:
- Copy all results CSVs from GPU server to local machine
- Implement truncation baseline (`src/m6/compressors/truncation.py`, ~40 lines)
- Register in `make_compressor()`
- Smoke-test locally: `python -m m6.experiments.run_h1_h2 --smoke`

**Afternoon**:
- Implement seed variance analysis script (~50 lines, on existing CSVs)
- Implement cross-hypothesis Holm correction script (~30 lines)
- Run both on existing data

**Evening (GPU, overnight)**:
- Start full H1/H2 rerun with 10 ratios + truncation baseline: `python -m m6.experiments.run_h1_h2 --out results/h1_h2_10ratios`
- Estimated: ~8 hours

---

### Day 2 (May 27): CAAC + Frontier Setup

**Morning**:
- Results from overnight H1/H2 run (if complete, otherwise monitor)
- Run frontier validation: `python -m m6.experiments.run_frontier --out results/frontier_gpt4omini`
- Cost: ~$20. Wall-clock: ~2 hours.

**Afternoon**:
- Implement compounding-error prediction validation script using `cliff_prediction.py` + H1/H2 token_recall data
- Generate predicted-vs-empirical tau comparison
- Compute Cliff's delta and Cohen's d for all hypotheses

**Evening (GPU, overnight)**:
- Start CAAC experiment: `python -m m6.experiments.run_caac --out results/caac_full`
- Start H6 MultiHopRAG: `python -m m6.experiments.run_h6 --synth-results results/h5_full --out results/h6_full`
- Estimated: 4 + 1 = 5 hours (run sequentially to avoid model thrashing)

---

### Day 3 (May 28): CAAC Ablation + Analysis

**Morning**:
- Collect CAAC and H6 results
- Analyze CAAC Pareto frontier
- Analyze H6 transfer results

**Afternoon**:
- Start CAAC ablations (theta sensitivity): modify `CAACConfig.theta` and loop
- Run on GPU: ~3 hours

**Evening (GPU, overnight)**:
- CAAC N sensitivity ablation: ~2 hours
- Per-compressor CAAC: ~3 hours

---

### Day 4 (May 29): Selective Context + Remaining Experiments

**Morning**:
- Implement Selective Context wrapper (`src/m6/compressors/selective_context.py`, ~80 lines)
- Smoke-test locally

**Afternoon**:
- Analyze all ablation results
- Begin figure generation (see below)

**Evening (GPU, overnight)**:
- Run Selective Context H1/H2 sweep: ~3 hours
- Run GPT-4o spot check (10 workloads, ratios {1,4}): ~$15, ~1 hour

---

### Day 5 (May 30): Figure Generation Day

Generate all paper figures from collected data. Target: 6 main figures + 3 appendix figures.

**Main figures**:
1. **Hero cliff figure**: coord_success vs ratio for family-a, 4+ compressors, with predicted tau vertical line
2. **Three-panel family comparison**: family-a sharp cliff, family-c gradual, family-b qa_f1 cliff
3. **Predicted vs empirical tau**: scatter plot validating Theorem 1
4. **CAAC Pareto frontier**: achieved_ratio vs coord_success, CAAC dominates fixed
5. **Privacy-quality tradeoff**: dual y-axis (coord_success + disclosure rate) vs compressor aggressiveness
6. **Frontier validation**: GPT-4o-mini cliff overlaid on local 8B cliff

**Appendix figures**:
7. H1 scatter plots (delta_qa vs delta_coord)
8. H5 model-size overlay (4 models on family-a)
9. CAAC ablation grids (theta x N sensitivity)

**Tool**: Use matplotlib/seaborn. Create `src/m6/figures/` directory with one script per figure.

---

### Day 6 (May 31): Paper Writing -- Introduction + Related Work

Write the NeurIPS 9-page paper in LaTeX.

**Introduction** (1 page):
- Hook: multi-agent LLM systems use compression, nobody has measured coordination effects
- Discovery: coordination cliffs (sharp phase transitions)
- Theory: cliff position is compressor-determined (Theorem 1)
- Method: CAAC exploits the theorem to avoid cliffs
- Results: validates across model scales (1.5B to GPT-4o-mini) and benchmarks (synthetic + real)

**Related Work** (1 page):
- Context compression: LLMLingua-2, RECOMP, Gist Tokens, Selective Context
- Multi-agent LLMs: AutoGen, MetaGPT, MemGPT
- Scaling laws and phase transitions

---

### Day 7 (Jun 1): Paper Writing -- Theorem + CAAC

**Theorem section** (1.5 pages):
- Statement, proof, assumptions, discussion
- Empirical validation figure (predicted vs empirical tau)

**CAAC section** (1 page):
- Algorithm box
- Implementation details (binary search, per-fragment backing-off)
- Computational overhead analysis

---

### Day 8 (Jun 2): Paper Writing -- Experimental Setup + Results

**Experimental setup** (1 page):
- C1 benchmark, MultiHopRAG, HotpotQA (if B9 completed)
- 4-5 compressors + CAAC wrapper
- Model sizes: 1.5B through GPT-4o-mini
- Statistical protocol

**Results** (2 pages):
- 7.1: Cliff exists and is sharp (H2)
- 7.2: Cliff position is compressor-determined (H5 + frontier)
- 7.3: CAAC Pareto-dominates fixed compression
- 7.4: Transfer to real benchmarks
- 7.5: Privacy-quality tradeoff (H4)

---

### Day 9 (Jun 3): Paper Writing -- Discussion + Appendix

**Discussion and limitations** (0.5 page):
- Theorem assumptions (independence, binary importance)
- Synthetic benchmark limitations
- Future: trained CAAC, weighted token importance, multi-round adaptation

**Conclusion** (0.5 page)

**Appendix**:
- Full result tables for all experiments
- Effect sizes (Cliff's delta, Cohen's d) for all tests
- Benchmark details and data cards
- Reproducibility checklist

---

### Day 10 (Jun 4): Internal Review Round 1

- Self-review of complete draft
- Check: all figures referenced, all results tables consistent with code, all statistical tests correct
- Verify reproducibility: can the paper's claims be verified from the released code + data?
- Fix any gaps identified

---

### Day 11 (Jun 5): Revisions from Review

- Address any issues found in Day 10 review
- Run any quick supplementary experiments identified as gaps
- Polish figures for camera-ready quality
- Ensure consistent notation throughout

---

### Day 12 (Jun 6): Code Release Preparation

- Clean up experiment code: remove dead code, add docstrings
- Create `requirements.txt` / `pyproject.toml` with pinned versions
- Write `Makefile` targets for all experiments
- Test full reproducibility from clean checkout
- Prepare Docker compose for GPU environment

---

### Day 13 (Jun 7): Final Polish

- Final proofread of entire paper
- Check all references are correct and peer-reviewed (or explicitly marked as preprint)
- NeurIPS reproducibility checklist
- Generate camera-ready PDF
- Upload code to anonymous GitHub for double-blind review

---

### Day 14 (Jun 8): Submit

- Final check of PDF (page limit, formatting, figure quality)
- Submit to NeurIPS / prepare for ICLR deadline
- Upload reproducibility package

---

## Priority Matrix Summary

| Experiment | Priority | GPU Hours | $ Cost | Impact | Status |
|-----------|----------|-----------|--------|--------|--------|
| B1: CAAC vs baselines | P0 | 4h | $0 | Critical | Code ready |
| B2: GPT-4o-mini frontier | P0 | 0h | $20 | Critical | Code ready |
| B4: Truncation baseline | P0 | 2h | $0 | Critical | 40 lines to write |
| B5: H1/H2 10-ratio rerun | P0 | 8h | $0 | High | Config change only |
| B3: H6 MultiHopRAG | P1 | 1h | $0 | High | Code ready |
| B7: CAAC ablations | P1 | 8h | $0 | High | Config changes |
| B6: Selective Context | P1 | 3h | $0 | High | 80 lines to write |
| B8: Seed variance | P1 | 0h | $0 | Medium | 50 lines post-proc |
| B10: Cost/latency | P2 | 1h | $0 | Medium | 40 lines timing |
| B9: HotpotQA | P2 | 2h | $0 | Medium | 150 lines to write |
| B11: GPT-4o spot check | P2 | 0h | $15 | Medium | Config change |
| B12: Human eval | P2 | 0h | $0 | Medium | Manual work |
| B13: MemGPT paging | P3 | 6h | $0 | Low | 200 lines to write |
| B14: RECOMP trained | P3 | 5h | $0 | Low | 150 lines + training |
| B15: Dynamic N CAAC | P3 | 2h | $0 | Low | 50 lines to write |

**Total P0 GPU hours**: 14h
**Total P0+P1 GPU hours**: 26h
**Total P0 cost**: $20
**Total all cost**: $35

All P0 experiments can complete in 2 overnight GPU runs. P0+P1 experiments complete in 4 overnight runs. This is well within the 14-day timeline.
