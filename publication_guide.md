# Publication Guide: From Master's Thesis to NeurIPS/ICLR Paper

**Distributed Memory Bus for Multi-Agent Coordination**
*Syed Abdullah Hassan, University of Oulu*

This guide provides concrete, actionable advice for converting the M6 thesis into a venue-ready submission. It draws patterns from accepted papers at NeurIPS 2023 (DPO), ICLR 2024 (MetaGPT, AutoGen, Self-RAG, MemGPT), ACL Findings 2024 (LLMLingua-2), and TACL 2023 (Lost in the Middle), all of which were studied for structural and rhetorical patterns.

---

# PART 1: Paper Structure for NeurIPS/ICLR

---

## 1. Title Formulation

### Patterns from accepted papers

Top-venue titles follow one of three templates:

**Template A: Action Verb + Novel Concept + Scope**
- "Direct Preference Optimization: Your Language Model is Secretly a Reward Model" (DPO, NeurIPS 2023)
- "ReAct: Synergizing Reasoning and Acting in Language Models" (ICLR 2023)
- "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection" (ICLR 2024)

**Template B: System Name + Positioning Metaphor**
- "MemGPT: Towards LLMs as Operating Systems" (ICLR 2024 Spotlight)
- "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework" (ICLR 2024)

**Template C: Finding-Led (Provocative Claim)**
- "Lost in the Middle: How Language Models Use Long Contexts" (TACL 2023)
- "GAIA: A Benchmark for General AI Assistants" (arXiv 2023)

### What makes these titles work

1. They are self-contained -- a reader understands the contribution from the title alone.
2. They contain a concrete technical noun (not vague "improvement" or "framework").
3. They avoid listing methods or results; they convey the conceptual insight.
4. System-name titles use a colon followed by a one-line positioning statement.
5. Finding-led titles promise a surprising empirical result that compels reading.

### What to avoid

- Titles longer than 15 words (excluding subtitle).
- Titles that read like thesis titles ("A Study of..." or "Towards Understanding...").
- Titles that list components ("Compression, Coordination, and Privacy in Multi-Agent Systems").

---

## 2. Abstract Template

A NeurIPS/ICLR abstract is 150-250 words and follows a strict five-sentence arc. Here is the sentence-by-sentence breakdown, with the rhetorical function of each:

**Sentence 1 -- Context and Importance.** Establish why the domain matters. Do not start with "In recent years." Start with a concrete technical fact.

> Example (DPO): "While large language models (LLMs) are trained with RLHF to align with human preferences, existing methods require fitting a reward model and then optimizing a policy with reinforcement learning."

> Example (LLMLingua-2): "This paper addresses prompt compression for large language models from a task-agnostic perspective."

**Sentence 2 -- Gap or Problem.** Identify what is missing, broken, or unknown. Use a "however" or "but" transition.

> Example (Self-RAG): "However, indiscriminately retrieving and incorporating a fixed number of retrieved passages, regardless of whether retrieval is necessary, or passages are relevant, diminishes LM versatility or can lead to unhelpful response generation."

**Sentence 3 -- Your Contribution (Method/System).** State what you do. Use active voice. Name your system or framework.

> Example (MetaGPT): "Here we introduce MetaGPT, an innovative meta-programming framework incorporating efficient human workflows into LLM-based multi-agent collaborations."

**Sentence 4 -- Key Results (Quantitative).** Give 2-3 headline numbers. Be specific.

> Example (ReAct): "ReAct demonstrates effectiveness over state-of-the-art baselines, with improvements including a 34% absolute improvement on ALFWorld and a 10% absolute improvement on WebShop."

**Sentence 5 -- Broader Impact or Surprising Implication.** What does this change about how we think?

> Example (Lost in the Middle): "This U-shaped performance curve persists even in models specifically designed for long contexts."

### Template to fill in

```
[Domain context -- why multi-agent coordination under compression matters].
[Gap -- nobody has measured how compression degrades coordination, as opposed to QA].
[Method -- we introduce [SystemName], a memory bus with three training-free compressors,
 a synthetic coordination benchmark, and a compounding-error model].
[Results -- coordination cliff at ~4x, QA decorrelated from coordination (rho < 0.3),
 compression reduces inference disclosure by 14pp].
[Implication -- model size raises ceilings but does not shift cliff; the cliff is
 compressor-driven, predictable from token recall].
```

---

## 3. Introduction Flow

The introduction at top venues follows a 4-paragraph structure, typically spanning 1.5-2 columns (about 600-900 words).

### Paragraph 1: Hook + Context

Open with a concrete, surprising, or provocative fact. Avoid throat-clearing ("Large language models have shown remarkable progress..."). Instead, start with the problem.

**Pattern from ReAct:** Opens by stating that reasoning and acting have been studied separately, immediately framing the gap. The first paragraph establishes the landscape in 4-5 sentences.

**Pattern from Lost in the Middle:** Opens with the observation that models claim 100K+ context windows but nobody knows how well they actually use them. This is a hook -- it challenges a widely held assumption.

**For this thesis:** Open with the fact that multi-agent LLM systems (AutoGen, MetaGPT, CrewAI) are being deployed with shared context windows of 8K-128K tokens, but nobody has measured what happens to coordination -- not just QA accuracy -- when that shared context is compressed.

### Paragraph 2: Gap + Motivation

State explicitly what is unknown or wrong. Cite 2-3 papers that establish the closest prior work and explain why they do not address your question.

**Pattern from Self-RAG:** Second paragraph reviews RAG limitations with 3 bullet points (increased cost, difficulty identifying relevant information, irrelevant documents degrading performance).

**For this thesis:** The gap is three-fold:
1. Prior compression work (LLMLingua, LLMLingua-2, RECOMP) measures QA accuracy, not coordination success.
2. Prior multi-agent work (MetaGPT, AutoGen) assumes uncompressed context.
3. No existing work characterizes the coordination cliff -- the ratio at which multi-agent coordination fails sharply.

### Paragraph 3: Contributions

Use a numbered list. Each contribution should be a single sentence with a concrete deliverable. NeurIPS/ICLR papers typically list 3-4 contributions.

**Pattern from LLMLingua-2:** Lists five contributions as single sentences: (1) task-agnostic formulation, (2) data distillation, (3) bidirectional encoding, (4) efficiency, (5) faithfulness.

**Pattern from DPO:** Lists three contributions clearly separated: (1) theoretical equivalence, (2) the DPO algorithm, (3) experimental validation.

**For this thesis, aim for four:**
1. We identify a coordination cliff at approximately 4x compression, where multi-agent coordination drops by 30%+ while QA accuracy remains above 70%.
2. We show that QA accuracy under compression is a poor predictor of coordination success (Spearman rho < 0.3 across all three compressors), challenging the implicit assumption that compression benchmarks based on QA transfer to multi-agent settings.
3. We propose a compounding-error model that predicts the cliff position from per-round token recall, and show that cliff position is compressor-driven, not model-size-driven.
4. We demonstrate that context compression reduces inference disclosure of protected facts by up to 14 percentage points, establishing compression as a privacy mechanism.

### Paragraph 4: Outline (Optional)

Some papers include a brief roadmap. At NeurIPS this is optional and can be omitted to save space. If included, keep it to 2 sentences.

---

## 4. Related Work

### Strategic positioning, not survey

Related work at NeurIPS/ICLR is 0.5-1 column. It is not a literature review. Its purpose is to position your contribution relative to the nearest neighbors and explain why your work is not subsumed by them.

### Structure

Organize by theme, not by chronology. Use 3-4 subsections of 1-2 paragraphs each.

**Pattern from Self-RAG:** Four subsections (Retrieval-Augmented Generation, Training with Critics, Control Tokens, LLM Refinement), each 2-4 sentences establishing the prior work and then one sentence explaining how Self-RAG differs.

**Pattern from MetaGPT:** Two subsections (Automatic Programming, LLM-Based Multi-Agent Frameworks), each concluding with a differentiating sentence.

### Recommended subsections for this thesis

1. **Context compression for LLMs.** Cover LLMLingua, LLMLingua-2 (token classification), RECOMP (extractive + abstractive), gist tokens. Differentiator: all prior work evaluates compression via downstream QA; we evaluate via multi-agent coordination.

2. **Multi-agent LLM systems.** Cover AutoGen (conversable agents), MetaGPT (SOPs + publish-subscribe), MemGPT (virtual context management). Differentiator: none of these study the effect of shared-context compression on coordination.

3. **Long-context and positional effects.** Cover Lost in the Middle (U-shaped performance), RULER, LongBench. Differentiator: we study compression-induced degradation, not positional degradation.

4. **Privacy in LLM pipelines.** Cover differential privacy in RAG, output filtering. Differentiator: we measure inference disclosure through the compressor itself, not the retrieval index.

### How to cite without being redundant

Each cited paper should appear for exactly one of three reasons:
- It establishes that a problem exists (motivating your work).
- It provides a method you build on (acknowledging lineage).
- It addresses a related problem differently (contrasting your approach).

Never cite a paper just to show you have read it. If a paper does not serve one of these three functions, remove the citation.

---

## 5. Method Section

### What to include

The method section should let a knowledgeable reader reimplement your system. At NeurIPS/ICLR, this means:

**5.1 System Architecture Diagram**

A single figure showing the full pipeline. This is the most important figure in the paper.

**Pattern from MemGPT:** Figure 2 shows the full architecture with labeled components (main context, external storage, function executor). Each box is annotated with its role.

**Pattern from Self-RAG:** Figure 1 shows the full pipeline with retrieval, generation, and reflection token production. Arrows show data flow.

For this thesis, the diagram should show: (1) the memory bus with access/compression/storage layers, (2) the three compressors as interchangeable modules, (3) the planner-worker-critic loop, (4) the coordination metrics being measured at each round.

**5.2 Algorithm Boxes**

NeurIPS papers use algorithm pseudocode boxes (Algorithm 1, Algorithm 2) for core procedures. These are not code listings -- they are mathematical pseudocode with clear inputs, outputs, and loop structures.

For this thesis, provide:
- Algorithm 1: Planner-worker-critic coordination loop with compression
- Algorithm 2: Compounding-error model prediction of cliff position

**5.3 Notation**

Define all symbols in a single paragraph or table at the start of the method section. Common convention:

| Symbol | Meaning |
|--------|---------|
| tau* | Coordination cliff position (compression ratio) |
| q | Per-round token recall |
| N | Number of planner-worker-critic rounds |
| rho | Spearman correlation coefficient |

**5.4 Level of detail**

Include enough detail to reproduce, but defer implementation specifics (hyperparameters, prompts, compute) to the appendix. The main text should focus on the conceptual architecture and the key design decisions.

**Pattern from DPO:** The main text derives the loss function (7 equations over 1.5 pages). Implementation details are in Section 5 and the appendix.

**Pattern from LLMLingua-2:** The main text describes the token classification formulation and data distillation process. Quality control metrics (Variation Rate, Alignment Gap) are defined with equations. The actual prompt template is in the appendix.

---

## 6. Experiment Section

### Structure

The experiment section at NeurIPS/ICLR typically follows this order:

1. **Setup** (datasets, baselines, metrics, compute) -- 0.5 column
2. **Main results** (headline tables) -- 1-1.5 columns
3. **Ablations** (what happens when you remove components) -- 0.5-1 column
4. **Analysis** (deeper investigation of findings) -- 0.5-1 column

### Baselines

**Pattern from Self-RAG:** 7 baselines spanning both smaller models (Alpaca 7B, Llama2 7B) and larger models (ChatGPT, GPT-4). Includes both retrieval-augmented and non-retrieval-augmented variants.

**Pattern from MetaGPT:** Compares against 4 framework-level baselines (AutoGPT, LangChain, AgentVerse, ChatDev) and 6 model-level baselines (AlphaCode, CodeGeeX, GPT-4, etc.).

For a NeurIPS submission, you need at minimum:
- Your 3 compressors + identity control
- At least 2 external baselines (e.g., RECOMP extractive, gist tokens, or random-token-drop as a naive baseline)
- An oracle baseline (what is the best possible coordination at each ratio?)

### Tables vs Figures

Use tables for:
- Main results (exact numbers matter)
- Ablation results (comparison across configurations)
- Statistical summaries (CIs, p-values, effect sizes)

Use figures for:
- Trends across a continuous variable (compression ratio vs. coordination success -- this is the cliff curve)
- Distributions (bootstrap distributions of rho)
- Architecture diagrams

**Pattern from LLMLingua-2:** Main results are in tables (Tables 1-4), each with a clear caption explaining what is being compared. Bold for best results. Compression ratios and token counts included alongside accuracy.

**Pattern from Lost in the Middle:** The headline finding (U-shaped curve) is presented as a figure, because the shape of the curve IS the finding. The paper would be far less effective if the U-shape were a table.

For this thesis, the cliff curve MUST be a figure. The coordination success vs. compression ratio plot, with the cliff annotated, is the visual centerpiece of the paper.

### Statistical reporting

NeurIPS/ICLR expect:
- **Means with standard deviations** or **medians with interquartile ranges** (not just means)
- **Confidence intervals** (95% bootstrap CIs are standard)
- **Significance tests** where claims of difference are made (Mann-Whitney U, paired bootstrap, etc.)
- **Effect sizes** (Cohen's d, Cliff's delta) in addition to p-values
- **Multiple comparison correction** (Holm-Bonferroni) when testing multiple hypotheses

State the number of seeds explicitly: "All results are averaged over 5 random seeds with 95% bootstrap confidence intervals."

---

## 7. Results Presentation

### How to present negative results as valuable findings

Negative results (H3: compress-first always wins; H5: model size does not shift cliff) are publishable and valuable if framed correctly. The key is to frame them as *discoveries that challenge assumptions*, not as *failures to confirm hypotheses*.

**Pattern from Lost in the Middle:** The paper's entire contribution is a negative finding -- models do not use long contexts well. This is framed as a discovery about architectural limitations, not a failure of models.

**Pattern from RECOMP:** The paper acknowledges that abstractive compressors struggle with multi-hop reasoning (Table faithfulness results). This is presented as an insight about the limits of the approach.

### Framing strategy for negative results

1. State the expected result and the prior work that motivated it.
2. Present the actual result with full statistical support.
3. Explain why the actual result is more interesting than the expected result.
4. State the implication for practitioners.

**Example for H5:**

> *Expected*: Larger models tolerate higher compression ratios before coordination failure, implying cliff position scales with model size.
> *Observed*: All models (1.5B through 14B) exhibit the coordination cliff at the same compression ratio (~4x). Model size affects the ceiling coordination performance but not the cliff position.
> *Implication*: The coordination cliff is a property of the compressor, not the downstream model. This means practitioners cannot "scale their way out" of compression degradation -- they must improve the compressor.

**Example for H3:**

> *Expected*: Compress-before-retrieve (P1) and retrieve-before-compress (P2) exhibit a sign-flip depending on whether the objective is storage savings or accuracy.
> *Observed*: P1 dominates P2 in both regimes. Compress-first is always better.
> *Implication*: This contradicts the LongLLMLingua assumption that query-aware compression is necessary. Compression before retrieval removes noise that would otherwise confuse the retriever.

---

## 8. Discussion/Limitations

### What reviewers expect

Reviewers at NeurIPS/ICLR look for three things in the discussion:

1. **Honest acknowledgment of limitations** -- not burying them, but stating them clearly.
2. **Scope boundaries** -- what claims do you make and what claims do you explicitly not make.
3. **Future directions** -- concrete, not vague ("future work could explore...").

### How to be honest without being defensive

**Pattern from MemGPT (Limitations section):**
- "Added latency from multiple LLM calls per user interaction"
- "Memory management overhead increases with conversation length"
- "Relies on LLM's ability to correctly use function calls"
- "No guarantee of optimal memory management strategies"

Each limitation is stated as a fact, not apologized for. No hedging ("we believe this might be a concern"). No defensive counterarguments inline.

**Pattern from RECOMP:**
- "Abstractive compressors struggle with multi-document synthesis (HotpotQA)"
- "Training requires access to base LM for scoring -- not applicable to truly black-box systems"

### Recommended limitations for this thesis

1. **Synthetic benchmark.** C1 is synthetic, not drawn from real multi-agent deployments. While the three workload families cover diverse coordination patterns, real-world multi-agent interactions may exhibit additional complexity. (Mitigate: H6 addresses this with MultiHopRAG transfer.)

2. **Training-free compressors only.** We study only training-free compressors. Trained compressors (ICAE, gist tokens) may exhibit different cliff characteristics. (Mitigate: training-free is the practical regime for most deployments.)

3. **Small model scale.** The largest model tested is 14B parameters. Cliff behavior at 70B+ is unknown. (Mitigate: the compounding-error model predicts that cliff position is compressor-driven regardless of model size, and the 14B result is consistent with this prediction.)

4. **Piecewise-linear cliff fitting.** The tau* estimate defaults to x.max() when the curve is gradual, meaning cliff position is unreliable for gradually degrading families. (Mitigate: we report cliff magnitude as well as position, and flag cases where the fit is degenerate.)

5. **Single coordination metric.** coord_success is a binary metric (task solved or not). Partial-credit metrics might reveal subtler degradation patterns.

---

## 9. Figures and Tables

### What makes a NeurIPS figure great

1. **Self-contained.** The figure caption should explain what the figure shows without requiring the reader to find the explanation in the text. Captions are typically 2-4 sentences.

2. **Minimal ink-to-data ratio.** Remove grid lines, unnecessary legends, chart junk. Use whitespace.

3. **Consistent color scheme.** Use a colorblind-friendly palette (e.g., Okabe-Ito or ColorBrewer2). Assign one color per compressor throughout all figures.

4. **Large axis labels.** Labels should be readable at 50% zoom. Minimum 10pt font in the final PDF.

5. **Annotations on the figure.** Annotate the cliff position directly on the curve with an arrow and label. Do not make the reader look up tau* in a separate table.

### Recommended figure set for this paper

**Figure 1 (Architecture).** System diagram of the memory bus, showing the planner-worker-critic loop, the compression layer with three compressor options, and the coordination/QA metric extraction points. This should be a clean block diagram, not a flowchart.

**Figure 2 (Headline Result: The Cliff).** Coordination success vs. compression ratio for all three compressors + identity, on the family with the sharpest cliff (family-a). X-axis: compression ratio (1x to 16x, log scale). Y-axis: coordination success (0-100%). Annotate tau* with a vertical dashed line. Include shaded 95% CI bands.

**Figure 3 (QA vs. Coordination Decorrelation).** Scatter plot of QA accuracy vs. coordination success at each compression ratio, one panel per compressor. Color points by ratio. Show the Spearman rho and 95% CI in each panel. The visual message: QA stays high while coordination crashes.

**Figure 4 (Model-Size Independence of Cliff).** Cliff curves for 1.5B, 3.8B, 8B, and 14B overlaid on the same axes. The message: curves shift vertically (ceiling) but not horizontally (cliff position).

**Figure 5 (Inference Disclosure).** Bar chart showing disclosure rate at 1x vs. 4x compression for each compressor, with the priors-only baseline as a horizontal line. Include error bars. The message: compression reduces leakage.

### Chart types to use and avoid

| Use | Avoid |
|-----|-------|
| Line plots for trends over a continuous variable | 3D plots of any kind |
| Scatter plots for correlation | Pie charts |
| Bar charts for categorical comparisons | Stacked area charts |
| Heatmaps for large tables | Radar/spider charts |
| Violin plots for distributions | Word clouds |

### Color scheme recommendation

Assign fixed colors across all figures:
- LLMLingua-2: blue (#0072B2)
- Phi-3-extractive: orange (#E69F00)
- Instruction-aware filter: green (#009E73)
- Identity (control): gray (#999999)

Use solid lines for main results, dashed lines for baselines, and shaded regions for confidence intervals at 20% opacity.

---

# PART 2: What Separates Accepted from Rejected

---

## 1. Novelty Framing

### How to position incremental-seeming work as novel

The most common rejection reason at NeurIPS/ICLR is "limited novelty." This does not mean the work lacks novelty -- it means the novelty was not communicated effectively.

### Strategy 1: Reframe as a new research question

Do not say: "We apply compression to multi-agent systems." This sounds like an engineering exercise.

Say: "We ask whether the QA-centric evaluation paradigm for prompt compression transfers to multi-agent coordination, and discover that it does not." This frames the work as questioning a foundational assumption.

**Pattern from Lost in the Middle:** The paper does not say "we test models on long contexts." It says "we investigate how language models use long contexts" -- framing it as a scientific investigation with a surprising answer.

### Strategy 2: Name the phenomenon

The "coordination cliff" is your most valuable coinage. Name it, define it precisely, and use it consistently. Published papers that name phenomena become reference points.

**Pattern from Lost in the Middle:** The "lost in the middle" phenomenon became a widely cited finding precisely because it was named and demonstrated with a clean visual.

**Pattern from DPO:** The insight that "your language model is secretly a reward model" is a reframing of a mathematical equivalence, but the naming makes it memorable.

### Strategy 3: Present the theoretical model

The compounding-error model (q^N crossing a threshold) is a genuine theoretical contribution. It takes the cliff from an empirical observation to a predicted phenomenon. This is the difference between a benchmark paper and a scientific paper.

### Strategy 4: Show unexpected implications

The fact that model size does not shift the cliff is more interesting than if it did. The fact that compress-first always beats retrieve-first contradicts LongLLMLingua's assumption. These are the results that make reviewers pay attention.

---

## 2. Experimental Rigor

### What NeurIPS/ICLR expect

**Baselines:** Minimum 3-5 baselines for the main comparison. At least one should be a strong recent baseline (published within the last 12 months). At least one should be a simple/naive baseline (random token drop, uniform subsampling) to establish the lower bound.

**Seeds:** Minimum 3 seeds, preferably 5. Report mean and standard deviation. Some papers report median and IQR for non-normal distributions.

**Ablations:** Remove each component and measure the impact. For this thesis:
- Ablation 1: Remove the verifier from Phi-3-extractive (does extractive verification matter?)
- Ablation 2: Replace piecewise cliff fitting with simple threshold detection
- Ablation 3: Remove the instruction-aware component from the filter (does task-awareness matter?)

**Scaling experiments:** Show results across at least 2 axes (compression ratio, model size). You have both.

**Pattern from LLMLingua-2:** 4 evaluation domains (MeetingBank, LongBench, ZeroSCROLLS, GSM8K+BBH), 5 baselines, generalization to a different model (Mistral-7B), latency analysis, and 3 ablation studies. This is the expected level of thoroughness.

---

## 3. Statistical Reporting

### What to report and where

**In the main text:**
- All claims of "better" or "worse" must be supported by a test with a reported p-value.
- Confidence intervals for all key numbers (rho, tau*, drop magnitude).
- Effect sizes alongside p-values (e.g., "lingua2 reduces disclosure by 14.3pp, Cohen's d = 0.82, p = 0.0001").

**In a table footnote or appendix:**
- Test names and assumptions (e.g., "Mann-Whitney U, two-sided, Holm-corrected for 9 comparisons").
- Bootstrap parameters (e.g., "10,000 resamples, percentile method").
- Software versions (scipy, statsmodels).

### Common mistakes to avoid

- Reporting p < 0.05 without effect size (statistically significant but practically meaningless).
- Using parametric tests (t-test) on non-normal data without justification.
- Omitting multiple comparison correction when testing multiple hypotheses.
- Reporting only means without variance (reviewers will ask for error bars).

---

## 4. Reproducibility

### What reviewers check

Since NeurIPS 2019, reproducibility checklists are standard. Reviewers explicitly check:

1. **Code availability.** Link to a repository with instructions. Anonymize for submission (Anonymous GitHub or OpenReview supplementary).
2. **Data availability.** If synthetic, provide the generation script. If proprietary, provide summary statistics.
3. **Compute requirements.** State GPU type, total GPU-hours, and estimated cost.
4. **Hyperparameters.** List all hyperparameters in a table in the appendix.
5. **Random seeds.** Report which seeds were used and confirm that results are seed-stable.

### For this thesis

- C1 benchmark: provide the generation script (single-command regeneration).
- Compressors: all training-free and open-source (LLMLingua-2 MIT, Phi-3 MIT, BGE reranker MIT).
- Compute: "All experiments run on a single RTX 5090 (32GB) in approximately 22 hours total. No API keys required."
- Code: release as a pip-installable package (already structured as `m6`).

---

## 5. Writing Quality

### Precision

Every sentence should contain exactly one idea. If a sentence contains "and" connecting two independent claims, split it into two sentences.

Bad: "LLMLingua-2 achieves high compression ratios and generalizes to out-of-domain tasks while maintaining low latency."

Good: "LLMLingua-2 achieves 3x compression with less than 1% QA degradation. It generalizes to out-of-domain tasks (LongBench, ZeroSCROLLS) despite training only on meeting transcripts."

### Conciseness

NeurIPS main text is 9 pages (excluding references). Every word must earn its place. Common cuts:
- Remove "In this paper, we..." -- just state what you do.
- Remove "It is worth noting that..." -- if it is worth noting, just note it.
- Remove adverbs ("significantly," "remarkably," "interestingly") unless they carry technical meaning ("statistically significant" is fine; "significantly better" without a test is not).

### Avoiding hedging

Academic hedging undermines confidence in your results.

Bad: "Our results seem to suggest that compression might affect coordination."
Good: "Compression at 4x reduces coordination success by 33% (p < 0.001)."

Reserve hedging for genuinely uncertain claims: "We hypothesize that the cliff position may shift at model scales beyond 14B, though our data does not extend to this regime."

### Active voice

Bad: "It was observed that the coordination cliff was found at approximately 4x compression."
Good: "The coordination cliff occurs at approximately 4x compression."

---

## 6. Common Reviewer Complaints -- And How to Preempt Them

### Complaint 1: "Synthetic benchmark only"

**Preemption:** Acknowledge this explicitly in limitations. Point to H6 (MultiHopRAG transfer) as a validation step. Argue that synthetic benchmarks enable controlled measurement (you can vary exactly one parameter at a time), which is impossible with real-world traces. Cite GAIA as precedent -- GAIA is also synthetic/curated and was accepted precisely because it enables controlled evaluation.

### Complaint 2: "Only training-free compressors"

**Preemption:** Frame this as a deliberate scope decision. Training-free compressors are the practical regime (no fine-tuning budget, no training data). State explicitly: "We restrict our study to training-free compressors because they represent the practical deployment regime for most multi-agent systems. Trained compressors (ICAE, gist tokens) are an important direction for future work."

### Complaint 3: "Small model scale"

**Preemption:** Report the 14B result alongside 1.5B/3.8B/8B. Argue via the compounding-error model that the cliff is compressor-driven, not model-driven, so larger models are predicted to show the same cliff. State: "Our theoretical model predicts, and our 14B validation confirms, that cliff position is invariant to model scale."

### Complaint 4: "Limited baselines"

**Preemption:** Add at minimum a random-token-drop baseline and a RECOMP-style extractive baseline. If MemGPT is feasible to run, add it as a system-level baseline (MemGPT manages context through paging, not compression -- this is a different approach to the same problem).

### Complaint 5: "Negative results are not contributions"

**Preemption:** Frame H3 and H5 as discoveries, not failures. The compress-first finding (H3) directly challenges LongLLMLingua's design. The model-size invariance (H5) has immediate practical implications (do not assume scaling solves compression). Cite precedent: Lost in the Middle is entirely a negative finding and is one of the most cited papers in the long-context literature.

### Complaint 6: "The compounding-error model is too simple"

**Preemption:** Simplicity is the point. The model predicts cliff position from two measurable quantities (token recall and round count). Show the prediction vs. observation plot. If the fit is good, the simplicity is a feature. Cite DPO as precedent -- DPO's contribution is that a complex problem (RLHF) reduces to a simple loss function.

---

# PART 3: Specific Advice for This Thesis

---

## 1. Title Options

Following the patterns identified in Part 1:

**Option 1 (Finding-Led, Template C):**
> The Coordination Cliff: How Context Compression Breaks Multi-Agent LLM Systems

This follows the Lost in the Middle pattern. The title names the phenomenon and states the finding.

**Option 2 (System + Positioning, Template B):**
> MemBus: Characterizing Coordination Failure Under Context Compression in Multi-Agent LLMs

This follows the MemGPT pattern. It names the system and the research question.

**Option 3 (Action Verb + Concept, Template A):**
> Compressing Shared Context Breaks Coordination: A Cliff Effect in Multi-Agent LLM Systems

This follows the DPO pattern (provocative subtitle). It leads with the action and the consequence.

**Option 4 (Concise + Provocative):**
> Scaling Cannot Save You: Coordination Cliffs in Compressed Multi-Agent LLMs

This is the most aggressive framing. It leads with the H5 finding (model size does not help) and names the phenomenon.

**Option 5 (Descriptive + Benchmark):**
> Beyond QA Accuracy: Measuring Coordination Cliffs Under Context Compression for Multi-Agent LLMs

This follows the GAIA pattern (positioning against an existing paradigm).

**Recommendation:** Option 1 or Option 3. They are concise, name the contribution, and promise a surprising finding.

---

## 2. Core Narrative

### The single storyline

A NeurIPS paper needs one clear storyline, not five hypotheses. The thesis has five hypotheses; the paper should have one narrative with supporting evidence.

**Recommended narrative:** *Context compression that preserves QA accuracy destroys multi-agent coordination, and this coordination cliff is predictable from token recall and invariant to model scale.*

This narrative:
- Opens with a surprising disconnect (QA stays high, coordination crashes) -- H1
- Establishes the cliff as a measurable phenomenon -- H2
- Shows the cliff is predictable from a simple model -- compounding-error theory
- Demonstrates that scaling models does not help -- H5
- Offers a privacy benefit as a secondary finding -- H4
- Provides a practical pipeline recommendation -- H3

### How to arrange the hypotheses

Do not present them as H1-H5. Instead, organize the results section around three themes:

1. **The coordination cliff exists and is decorrelated from QA.** (Combines H1 + H2)
2. **The cliff is compressor-driven, not model-driven.** (H5 + compounding-error model)
3. **Practical implications: pipeline design (H3) and privacy (H4).**

---

## 3. Handling Negative Results

### H3: Compress-first always wins

**Frame as:** "Compress-before-retrieve dominates retrieve-before-compress across all conditions, contradicting the assumption underlying query-aware compression methods (LongLLMLingua)."

**Why this is interesting:** It simplifies system design. Practitioners do not need to choose a pipeline based on their optimization target -- compress-first is always the right choice. This is a strong, actionable finding.

**How to present it:** One paragraph in the results section, one table showing P1 vs. P2 vs. P3 across conditions. Do not spend a full page explaining why P2 failed -- spend a paragraph explaining why P1 succeeds (compression removes noisy tokens that would confuse the retriever).

### H5: Model size does not shift cliff

**Frame as:** "Coordination cliff position is invariant to planner model size (1.5B-14B), challenging the assumption that scaling models can compensate for compression loss."

**Why this is interesting:** It has the strongest practical implication in the paper. If cliff position were model-dependent, the advice would be "use a bigger model." Since it is not, the advice is "improve the compressor" -- a fundamentally different R&D direction.

**How to present it:** Figure 4 (overlaid curves). One sentence stating the finding. One sentence stating the implication. The visual should make the point immediately.

---

## 4. Positioning the Compounding-Error Model

### What it is

The compounding-error model predicts the cliff position tau* from two quantities:
- q: per-round token recall (what fraction of tokens survives compression)
- N: number of planner-worker-critic rounds

The cliff occurs where q^N crosses the planner's task-completion threshold.

### How to position it

This is a theoretical contribution, but a modest one. Do not overclaim.

**Good framing:** "We propose a simple predictive model relating token recall to cliff position. The model predicts tau* within +/-0.5 ratio units for families with sharp cliffs (a and b), validating the compounding-error hypothesis."

**Bad framing:** "We derive a novel theoretical framework for understanding multi-agent coordination under compression." (Too grandiose for a two-parameter model.)

### Where to put it

In the method section, after the system architecture. Present the model (2-3 equations), then validate it in the results section by comparing predicted vs. observed tau*. If the fit is good, this is a contribution. If the fit is approximate, present it as a useful heuristic.

---

## 5. Expected Baselines

Reviewers familiar with the compression and multi-agent literatures will ask about the following systems. For each, explain whether you include it, and if not, why.

### Baselines reviewers will expect

**RECOMP (Xu et al., 2023).** Extractive and abstractive compression for RAG. You should include RECOMP-extractive as a baseline compressor if feasible (it uses Contriever, 110M parameters, and is training-free at inference time though the selector was trained). If not feasible, explain: "RECOMP's extractive compressor requires a trained dual-encoder selector, placing it outside our training-free scope."

**MemGPT (Packer et al., ICLR 2024).** Virtual context management through paging. This is a system-level comparison, not a compressor-level comparison. You should cite it and explain: "MemGPT manages context through hierarchical paging, which is complementary to compression. Our compression layer could be integrated into MemGPT's archival storage, but this integration is beyond our scope."

**LongLLMLingua (Jiang et al., 2023).** Query-aware compression. This is the most natural baseline for H3 (pipeline placement). If you can run it, include it. If not, explain that your instruction-aware filter serves a similar function (query-conditioned token selection).

**Gist tokens (Mu et al., NeurIPS 2023).** Learned compression tokens. This requires training, so it is outside your training-free scope. Cite it and explain the scope restriction.

**Random token drop.** A naive baseline that drops tokens uniformly at random. This is trivial to implement and essential for showing that your compressors are doing something meaningful. Include it.

**No-compression control.** Already included as the identity compressor. Good.

### Minimum viable baseline set

| Baseline | Status | Justification |
|----------|--------|---------------|
| Identity (no compression) | Included | Upper bound on coordination |
| Random token drop | Must add | Lower bound on compression quality |
| LLMLingua-2 | Included | State-of-the-art training-free compressor |
| Phi-3-extractive | Included | LLM-based extractive compressor |
| Instruction-aware filter | Included | Query-conditioned compressor |
| RECOMP-extractive (optional) | Not included | Requires trained selector (out of scope) |
| MemGPT (optional) | Not included | System-level, not compressor-level |

---

## 6. Potential Weaknesses -- And How to Address Them

### Weakness 1: Synthetic benchmark limits external validity

**Address:** Include a transfer validation (H6 on MultiHopRAG). In the discussion, argue that synthetic benchmarks are the standard for controlled measurement in the field (cite GAIA, ALFWorld, WebShop from the ReAct paper). State: "Synthetic benchmarks enable isolation of variables; we complement this with a transfer study on MultiHopRAG."

### Weakness 2: Three compressors may not generalize

**Address:** Argue that the three compressors span three different compression paradigms (token classification, LLM-based extraction, TF-IDF+reranking). If the cliff appears across all three, it is unlikely to be an artifact of one paradigm. This is a design-of-experiments argument.

### Weakness 3: The compounding-error model is post-hoc

**Address:** Present the model as a hypothesis before showing results. Show that it was formulated based on the family-a data and validated on family-c data (out-of-distribution validation). If this is not the case, be honest: "The compounding-error model was developed alongside the empirical observations and should be validated on new workload families."

### Weakness 4: Binary coordination metric is coarse

**Address:** Acknowledge this and show that the cliff appears even in the more fine-grained qa_f1 metric. Argue that binary coordination success is the metric practitioners care about (the agent either solved the task or did not). Partial credit metrics are a direction for future work.

### Weakness 5: Ollama inference may introduce variability

**Address:** Report the Ollama model versions and quantization levels used. Show that temperature 0.0 produces deterministic outputs. Report the 5-seed variance to demonstrate stability. State: "All experiments use temperature 0.0 with quantized models via Ollama. Variance across 5 seeds reflects benchmark sampling, not model stochasticity."

### Weakness 6: No comparison with longer-context models as an alternative to compression

**Address:** Acknowledge that using longer-context models (e.g., Llama-3.1-128K) is an alternative to compression. Argue that compression remains relevant because: (a) longer contexts incur quadratic attention cost, (b) the Lost in the Middle effect means longer contexts do not guarantee better utilization, and (c) compression can serve privacy goals (H4) that longer contexts cannot.

---

## 7. Draft NeurIPS Abstract

Below is a draft abstract following the five-sentence template from Part 1, Section 2. It is 198 words, within the NeurIPS 150-250 word guideline.

---

Multi-agent LLM systems share context through message buses that quickly exceed token limits, making context compression essential for practical deployment. Prior compression work evaluates quality through single-agent QA accuracy, implicitly assuming that QA-preserving compression also preserves multi-agent coordination -- an assumption that has never been tested. We introduce a coordination benchmark spanning three workload families (150 instances) and systematically measure how three training-free compressors (LLMLingua-2, Phi-3-extractive, instruction-aware filtering) affect both QA accuracy and coordination success across 1.5B-14B parameter planners. We identify a *coordination cliff*: a sharp drop in coordination success at approximately 4x compression, even when QA accuracy remains above 70%. QA accuracy and coordination success are weakly correlated (Spearman rho < 0.3 across all compressors), demonstrating that QA-based compression benchmarks do not predict coordination failure. A compounding-error model that relates per-round token recall to cliff position correctly predicts the cliff within 0.5 ratio units. Critically, the cliff position is invariant to model scale (1.5B-14B), establishing it as a compressor property rather than a model limitation. As a secondary finding, 4x compression reduces inference disclosure of protected facts by up to 14 percentage points.

---

### Notes on this abstract

- Sentence 1 establishes the practical context (message buses, token limits).
- Sentence 2 identifies the gap (QA-centric evaluation, untested assumption).
- Sentence 3 states the method (benchmark, three compressors, four model sizes).
- Sentences 4-6 present the results (cliff, decorrelation, compounding-error model, model-size invariance).
- Sentence 7 adds the secondary finding (privacy).
- The abstract names the phenomenon ("coordination cliff") and gives specific numbers (4x, rho < 0.3, 14pp).
- It does not mention system names, implementation details, or paper structure.

---

# Appendix: Paper Checklist

Before submission, verify all items:

### Formatting
- [ ] 9 pages main text (NeurIPS) or 10 pages (ICLR), excluding references and appendix
- [ ] All figures readable at 50% zoom
- [ ] All tables have captions above (NeurIPS style) or below (ICLR style)
- [ ] References use venue format (not arXiv when published version exists)
- [ ] Author names anonymized for double-blind review

### Content
- [ ] Abstract is 150-250 words
- [ ] Introduction states contributions as a numbered list
- [ ] Related work positions against nearest neighbors with differentiating sentences
- [ ] Method section includes architecture diagram and algorithm box
- [ ] All notation defined before first use
- [ ] Main results table includes all baselines
- [ ] All claims of "better/worse" supported by statistical tests
- [ ] Negative results framed as findings
- [ ] Limitations section is honest and specific
- [ ] Broader impact statement included (if required by venue)

### Statistical
- [ ] All results averaged over >= 3 seeds
- [ ] 95% confidence intervals reported
- [ ] Effect sizes reported alongside p-values
- [ ] Multiple comparison correction applied
- [ ] Bootstrap parameters stated (number of resamples, method)

### Reproducibility
- [ ] Code repository linked (anonymized)
- [ ] Data generation script included
- [ ] Compute requirements stated (GPU type, hours, cost)
- [ ] All hyperparameters in appendix table
- [ ] Random seeds listed

### Figures
- [ ] Architecture diagram (Figure 1)
- [ ] Coordination cliff curve (Figure 2 -- the headline figure)
- [ ] QA vs. coordination scatter (Figure 3)
- [ ] Model-size invariance overlay (Figure 4)
- [ ] Inference disclosure bars (Figure 5)
- [ ] Consistent color scheme across all figures
- [ ] Colorblind-friendly palette

---

# Appendix: Venue Selection Guide

| Venue | Deadline | Fit | Notes |
|-------|----------|-----|-------|
| NeurIPS 2026 | May 2026 | Strong | Accepts empirical papers with theoretical grounding. The cliff + compounding-error model fits well. |
| ICLR 2027 | Sep 2026 | Strong | Accepts systems papers (AutoGen, MetaGPT, MemGPT were all ICLR 2024). Multi-agent + compression is on-topic. |
| ACL 2026 | Jan 2026 | Good | Strong NLP venue. Compression papers (LLMLingua-2) appear at ACL. Less emphasis on multi-agent systems. |
| EMNLP 2026 | Jun 2026 | Good | Accepts empirical studies. MultiHopRAG was EMNLP 2024. |
| AAMAS 2027 | Oct 2026 | Moderate | Multi-agent systems venue. Would reach the right audience but lower visibility than NeurIPS/ICLR. |
| AAAI 2027 | Aug 2026 | Moderate | Broad AI venue. Accepts both systems and empirical papers. |

**Recommendation:** Target ICLR 2027 (September 2026 deadline). The paper fits the venue profile (systems + empirical evaluation), the timeline allows thorough preparation, and three directly related papers (MetaGPT, AutoGen, MemGPT) appeared at ICLR 2024.

---

*End of publication guide.*
