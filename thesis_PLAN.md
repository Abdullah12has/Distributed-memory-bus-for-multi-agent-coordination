# Master's Thesis Writing Plan
**Title:** *Distributed Memory Bus for Multi-Fragment LLM Workflows: Context Compression, the Coordination Cliff, and Privacy*
**Author:** Syed Abdullah Hassan, University of Oulu
**Deliverable:** Single Master's thesis manuscript. No external publication scaffolding (NeurIPS / ICLR scope dropped per ADR-008 and grilling session §55). Target: top score across all 10 evaluation criteria (max 42 / 42).
**Format:** Oulu ITEE LaTeX thesis template (bibliography style dictated by template).
**Title-scope ADR:** ADR-009 records the rename from "Multi-Agent Coordination" to "Multi-Fragment LLM Workflows" and the promotion of the deterministic-solver disclosure to the Abstract / Ch 1 P5.
**Resolved decisions:** Twelve design forks were resolved in the 2026-05-29 thesis-PLAN grilling session — see §11 "Decisions log" at the bottom of this plan.

---

## 0. Context — why this plan exists

You have ~1 week to convert ~8 weeks of experiment work (six hypotheses, 30+ bugs found-and-fixed, a derivation, two corollaries, a prototype memory-bus service, and a constructive algorithm) into a Master's thesis at University of Oulu. The evidence base is complete and frozen on disk (`results/*_final`, `results/h4_unbiased`, `results/caac*`, `results/frontier*`, `results/hotpotqa_sweep`). The narrative is reconciled (ADR-006 / 007 / 008, insights §55). The terminology is locked (`CONTEXT.md`).

What is *not* done is the writing. This plan tells you, section by section and paragraph by paragraph, exactly what to put on the page so the manuscript scores the maximum on every line of `Evaluation_Instructions.md`. It is calibrated to two non-negotiable constraints:

1. **Every claim in the manuscript must trace to a canonical `results/*` directory or a verified peer-reviewed citation from plan-v3 §9.** No paraphrased numbers, no preprint-only sources presented as peer-reviewed.
2. **Every CONTEXT.md term must be used exactly as defined.** A single drift between θ_q and θ_info, or one stray "Theorem 1" in narrative prose, costs a Language point.

The order of writing is *not* the order of chapters. Methods + Results chapters are written first (you already know what they say); Background and Intro are written last (you can only motivate properly once you know what the results actually show).

---

## 1. The evaluation rubric → writing levers (the scoring map)

The rubric (`Evaluation_Instructions.md`) has 10 criteria, 42 points total. Every paragraph you write should be traceable to which criterion it advances.

| # | Criterion | Max | Where it's won |
|---|---|---|---|
| 1 | Scope | 3 | Already won — three task families × five compressors × four planner scales × disclosure + RAG. Just *show* the breadth in Ch 1 outline. |
| 2 | Challenge | 3 | Already won — derivation + bootstrap CI + frontier-model validation. *Mention* the methodological depth in Ch 1. |
| 3 | Outlining (1–5) | 5 | Numbered subsections, clear thesis statement in Ch 1.5, every chapter opens with a 3-line abstract, every hypothesis closes with a one-line verdict block. **5 is achievable** with discipline. |
| 4 | Intro + SoTA (1–5) | 5 | Ch 2 must be deep, comparative, and explicit about what *this* thesis adds beyond each cited line of work. Bare reference lists kill this score. **5 requires the comparative tables and the "what's missing in prior work" paragraph closing each subsection.** |
| 5 | Achievement of aims (1–5) | 5 | C1 + C2 + C4 supported, C3 reframed honestly. 5 requires *naming* the contributions explicitly and showing each is delivered. |
| 6 | Evaluation of results (1–5) | 5 | Every result reported with: point estimate, 95% CI, statistical test, effect size, *interpretation paragraph*, *comparison to prior work*, *significance discussion*. Skip any of these → drop to 3 or 4. |
| 7 | Significance (1–5) | 5 | Practitioner implications + scientific implications stated explicitly in Ch 8. Tie to industry cost-of-context numbers in Ch 1 closes the loop. |
| 8 | Initiative | 3 | Already won by the work you did. No action needed. |
| 9 | Language (1–5) | 5 | Impeccable + clear + revised. Read each chapter aloud once. Run a spell-check on the final PDF. Consistent terminology (CONTEXT.md). One round of feedback from Lauri before submission. |
| 10 | Layout (1–3) | 3 | Every figure caption is a complete sentence. Every table has units in the header. Every figure regenerated with `scripts/regen_figures.py`. Color-blind-safe palette. |

**Three rubric criteria where a careless thesis loses points unnecessarily and where this plan focuses extra effort: 4 (intro/SoTA), 6 (evaluation depth), 7 (significance).** Every chapter's plan below has dedicated guidance for these.

---

## 2. Structural skeleton (chapter map, page targets, evidence sources)

The chapter mapping is from `plan-v3.md §6`, validated against ADR-006/007/008.

| Ch | Title | Target pp | Hypotheses / Evidence | Canonical results dir |
|----|-------|-----------|-----------------------|------------------------|
| Front | Title / Abstract / Foreword / TOC / List of Figures / List of Tables / Abbreviations | 5–7 | — | — |
| 1 | Introduction | 4–5 | — | — |
| 2 | Background and Related Work | 12–14 | — | — |
| 3 | System Design and Implementation | 5–6 | — | `src/m6/memory_bus/` |
| 4 | The C1 Benchmark | 5–6 | C1 | `data/processed/c1-v0.1/` |
| 5 | Compression Effects on Coordination | 11–13 | H1, H2, H5, frontier | `h1_h2_final`, `h5_final`, `frontier`, `frontier_qwen72b`, `frontier_deepseekv4` |
| 6 | RAG Pipeline Placement and Cost | 4–5 | H3 | `h3_final` |
| 7 | Inference Disclosure, Memory-Bus Integration, and Information-Density Scaling | 6–7 | H4 (canonical = `h4_unbiased`), H6/Cor2 | `h4_unbiased`, `h6_final`, `hotpotqa_sweep` |
| 8 | Discussion, CAAC, Limitations, Future Work | 7–9 | CAAC, all corollaries | `caac` (canonical strict), `caac_N_*`, `caac_theta_*` |
| Back | References / Appendix A reproducibility / Appendix B per-cell tables / Appendix C derivation expansion / Appendix D figure index | 8–12 | — | — |

**Body total: ~55–65 pages. Total document with front + back matter: ~70–85 pages.** This is in the normal range for an Oulu Master's thesis. No page-count requirement is specified in `Evaluation_Instructions.md`, but going below 50 body pages risks looking thin on a project of this scope (rubric #1).

---

## 3. Terminology guardrails (load-bearing — read before writing any chapter)

Drawn verbatim from `CONTEXT.md` and ADR-006/007/008/009. Violating any of these is a Language-point hit and, worse, a credibility hit.

- **θ_q** (cliff-recall threshold) — per-family, depends on recall metric. Critical-token-recall canonical values: family-a 0.632, family-b 0.838, family-c 0.590. **Never** write bare "θ" when θ_info is also in scope.
- **θ_info** (task information density) — AUC-based, per-task. C1-a≈0.97, MultiHopRAG≈0.48, HotpotQA≈0.37. **θ_q ≠ θ_info.** Confusing them was an actual failure mode of the audit reconciliation.
- **τ\*** — cliff position, per (compressor, family, planner) cell. Empirical via piecewise or logistic fit; predicted from q(r*) = θ_q^(1/N).
- **q(r)** — token-recall curve. Use **critical_token_recall** (CTR) end-to-end per the 2026-05-29 framework reconciliation (insights §55, ADR-007).
- **N** — compression passes. **N = 1 in every experiment.** With N=1, q_min = θ_q.
- **p₀** — baseline success at r = 1. Used in Corollary 1 and the calibrated-regime predicate.
- **"compounding-error model"** — never "Theorem 1" in narrative prose (ADR-008). Code identifiers (`theorem_validation.json`, `validate_theorem.py`) keep the old name for backward compatibility; the manuscript does not. One footnote in Ch 5 documents the mapping.
- **"Calibrated regime"** — the set of (planner, compressor, task) configurations where assumptions A1–A4 approximately hold. Defined in Ch 5; cited every time you claim model independence. GPT-oss 120B is *out of regime* (ADR-006) — note this in Ch 5 and Ch 8 limitations.
- **"Coordination success"** — binary per-cell outcome. *"Coordination"* refers to **task structure** (planner combines information across fragments), not agent architecture. Per ADR-009, the manuscript scope is **multi-fragment LLM workflows**, not multi-agent simulation; the disclosure that experiments use a deterministic regex parser (H1/H2) or a single LLM call (H5/H6/frontier) appears in the Abstract and Ch 1 P5, not buried in Ch 3.
- **"Multi-fragment"** — property of the task (planner needs information drawn from ≥2 fragments, each compressible independently). All three C1 task families are multi-fragment. Multi-fragment ≠ multi-agent: the memory bus is *designed for* multi-agent use but *evaluated on* multi-fragment workloads. Distinct concept; do not confuse.
- **CAAC** — wrapper, *not* a fifth compressor family (CONTEXT.md line 104). Operating-point selection, *not* Pareto-dominating (ADR-007). 0/7 strict-Pareto rate is **expected and correct**, not a contribution-killer.
- **"Compress-first dominance"** — preferred phrasing for the H3 NOT-SUPPORTED reframing. Never call H3 "a failed hypothesis"; the predicted sign-flip did not appear, but the *finding* (P1 robustly > P2) is itself useful.
- **Verdicts H5 (original) and H6 (original)** are NOT SUPPORTED. Both are reframed as Corollaries 1 and 2 respectively. Always lead with the corollary verdict (SUPPORTED), then disclose the original predicate did not hold; do not lead with NOT SUPPORTED.

---

## 4. Chapter-by-chapter spec

Each chapter below contains:
- **Argument arc** — the thread the chapter must follow
- **Subsection paragraph direction** — what every paragraph should *do* (not what it should *say* — that's writing)
- **Evidence** — figures, tables, numbers, citations the chapter must surface
- **Rubric anchors** — which evaluation criteria this chapter wins points on
- **Pitfalls** — terminology and framing traps

---

### Front matter — Title, Abstract, Foreword, TOC, Lists (5–7 pp)

**Title page.** Title per ADR-009 (above). Author, supervisor (Lauri), University of Oulu, Faculty of ITEE, month / year. Template-driven layout.

**Abstract (~250 words, English).** Structured per Oulu template convention:
- 1–2 sentences: context + cost-of-LLM motivation
- 1 sentence: problem (multi-fragment compression × coordination quality)
- 1 sentence: scope disclosure per ADR-009 ("…task solvability under compression with deterministic or single-call planners; multi-round agent simulation out of scope.")
- 2–3 sentences: method (C1 benchmark, compounding-error model, three compressor families + truncation baseline, frontier validation, inference-disclosure metric)
- 4–5 sentences: headline findings (H1 SUPPORTED, H2 SUPPORTED, Corollary 1 SUPPORTED on Qwen 72B + DeepSeek V4 Pro within the calibrated regime, H3 reframed compress-first dominance, H4 SUPPORTED with reader-bias caveat, Corollary 2 SUPPORTED)
- 1 sentence: significance / practitioner implication
- Keywords: context compression, multi-agent systems, LLM, coordination cliff, inference disclosure, privacy, memory bus

**Finnish abstract (Tiivistelmä, ~250 words).** Oulu typically requires both English and Finnish abstracts. The template provides the section. Direct translation of the English abstract is acceptable; if Finnish is not your strong suit, hand-translate the structured items and ask Lauri to refine on the final read.

**Foreword / Acknowledgments (~0.5 pp).** Three short paragraphs:
1. Project context, supervisor (Lauri), University of Oulu / FCG / Oulu internal partners cited in plan-v3 §9.
2. Thanks (supervisor, partners, anyone who reviewed drafts).
3. **Use-of-AI-Tools statement** (per grilling Q12, verify exact required wording from the Oulu template before finalising): *"Generative-AI assistants (Claude, used via Claude Code) were used during this thesis to: (a) draft and revise prose under the author's supervision; (b) assist with code review, debugging, and the experiment-orchestration scripts. All scientific claims, experimental design, results interpretation, and final manuscript text are the author's responsibility."* Adjust wording to match the template's prescribed format if one is provided.

**Table of Contents, List of Figures, List of Tables, Abbreviations.** Auto-generated by LaTeX template. Verify all chapter headings render correctly before the final PDF build.

---

### Chapter 1 — Introduction (4–5 pp)

**Argument arc:**
Start at the felt cost of running LLMs at scale (electricity, money, latency). Zoom into multi-agent systems where that cost compounds per agent per round per token of shared context. Identify context compression as the natural lever. Surface the gap: existing compression evaluations measure single-agent QA quality; multi-agent coordination quality is unmeasured. Stake the claim: this thesis measures it, predicts when it breaks, characterises model-scale and task-structure dependencies, quantifies the privacy implications, and ships a memory-bus service that operationalises the findings.

**Paragraph-by-paragraph direction:**

P1 — **The hellos-and-thank-yous opening.** Open with the most concrete framing the user explicitly asked for: the per-token energy and dollar cost of LLM inference, multiplied by the fraction of those tokens that are conversational filler ("Hello", "Thank you", repeated system prompts, restated history). Anchor it numerically. Sam Altman's widely-cited "tens of millions of dollars" remark on please/thank-you compute is the natural hook for the cost-of-politeness framing; cite as industry observation, not academic claim. If a peer-reviewed environmental-impact paper on LLM inference (e.g., a 2024 paper on per-query Wh) is available and verified, prefer that. **Do not invent numbers.** If a specific number cannot be verified by submission day, use a range and cite the source. The paragraph closes with: "Every token that does not change the model's answer is waste. Compression is the lever that removes it."

P2 — **From token-greedy to context-engineered.** Trace the trajectory: GPT-3 era prompts were treated as free; modern systems pay attention to context windows, caching, and routing. Cite Anthropic's "How We Built our Multi-Agent Research System" (2025) for the industry observation that token usage explains ~80% of performance variance in a multi-agent workflow — labelled honestly as an industry blog, not a controlled measurement.

P3 — **Multi-agent multiplies the bill.** A single agent's context is one expense; an N-agent system broadcasts shared context to N receivers, each maintaining its own history, each prepending its own scaffolding. The cost is not N× but worse. Cite AutoGen, MetaGPT, CAMEL as the practical landscape (with their venues from plan-v3 §9 — AutoGen is an ICLR workshop, not main-conference, and *must* be labelled as such).

P4 — **Compression is the lever, but it has a blind spot.** LLMLingua / LLMLingua-2 / Selective Context / Gist Tokens / AutoCompressor — the field has matured rapidly. The evaluation, however, is overwhelmingly **single-agent QA** (LongBench, RULER, in-domain QA F1). The question this thesis answers is: *does compression that preserves QA also preserve the kind of structured cross-fragment reasoning a multi-agent planner needs?* Foreshadow the answer (it does not; QA-F1 and coordination success are decorrelated — Spearman ρ in [−0.59, +0.38] across compressors).

P5 — **Problem statement (one sentence, bold) + scope disclosure (one sentence, immediately after).**
- Problem statement: "*How does context compression affect multi-fragment coordination quality across compressors, task structures, and planner scales — and when and how can a memory-bus service exploit that understanding to compress safely, predictably, and privately?*"
- Scope sentence (per ADR-009): "*All experiments measure task-solvability under compression: the planner is either a deterministic regex parser (H1/H2) or a single LLM call with all (compressed) fragments visible (H5/H6/frontier). The memory bus is designed for multi-agent integration, but multi-round LLM agent simulation is outside the scope of this thesis's empirical evaluation.*"
- This sentence is also lifted (slightly shortened) into the **Abstract** so no examiner can miss it.

P6 — **Contributions.** Four contributions, numbered C1–C4, each one paragraph. Use the wording of plan-v3 §1 verbatim (it is already polished) but update verdicts:
- **C1.** The C1 benchmark — 150 instances, three workload families, reproducible from a seed.
- **C2.** The coordination cliff — empirical characterisation (H1, H2 SUPPORTED), the compounding-error model (derivation + bootstrap-CI predicted-τ\* band), ceiling-cliff separation (Corollary 1 SUPPORTED, frontier-validated on Qwen 72B and DeepSeek V4 Pro within the calibrated regime).
- **C3.** RAG pipeline placement — three pipelines (P1/P2/P3) under matched storage- and accuracy-bounded conditions with a EUR-per-workflow cost model. The predicted sign-flip (H3) **did not appear**; the *finding* is that compress-first (P1) is robustly better than post-retrieve compression (P2) in both regimes, which itself challenges a standard assumption.
- **C4.** Memory bus + summary-level inference-disclosure metric (H4 SUPPORTED on the unbiased benchmark). Information-density scaling (Corollary 2 SUPPORTED on HotpotQA + MultiHopRAG vs C1-a).

P7 — **Outline.** Two-sentence summary of each chapter, with explicit verdict for chapters carrying hypotheses. Closes with: "All artefacts — code, data, configs, results CSVs, and the LaTeX manuscript source — are released under a permissive licence (Appendix A)."

**Rubric anchors:** #3 (clear statement of problem + outline), #4 (intro signposts SoTA), #7 (significance framed in industry-cost terms from sentence one).

**Pitfalls:**
- Do not lead with "AI is exciting" or "LLMs are revolutionary". Lead with cost. The reader is an examiner who has read a dozen of those.
- Do not state contributions without verdicts. An examiner who has to flip to Ch 5 to find out if H2 held costs you a point on rubric #3.
- Do not mention NeurIPS, ICLR, the dropped paper plan, or "publishing" outside the thesis. Per the user's instruction and ADR-008, the thesis is the singular deliverable.

---

### Chapter 2 — Background and Related Work (12–14 pp)

**This chapter is the make-or-break for rubric #4 (max 5 points).** A bare reference list earns 2. A descriptive survey earns 3. A *comparative* survey that closes each subsection by naming what's missing earns 5.

**Subsections (numbered 2.1–2.8):**

#### 2.1 Transformer architecture and the cost of context (~2 pp)

**Audience reminder (per grilling Q6):** target reader is an engineering MSc-holder *without* an LLM/NLP background. This subsection includes a **figure (transformer block schematic — Q/K/V projection → attention → FFN)** and a **worked complexity example** (e.g., "for N = 8K tokens, attention scores require 64M floats per head; at 32 heads, that is 8 GB per layer of intermediate state"). Do not assume the reader knows what self-attention is.

- Origins: Vaswani et al. "Attention Is All You Need" (NeurIPS 2017). Self-attention complexity is **O(N²) in sequence length N** for compute and memory. Briefly walk through Q/K/V projections, scaled-dot-product attention, and the FFN block.
- **Decoder-only architecture** (the user explicitly asked for this). Trace the lineage: encoder-decoder (original Transformer, T5) → encoder-only (BERT) → **decoder-only with causal masking (GPT-2, GPT-3, GPT-4, Llama, Qwen, DeepSeek)**. Explain *why* decoder-only won: (1) unified next-token-prediction objective scales cleanly with data + parameters; (2) KV-cache makes autoregressive decoding cheap per token *after* the prefill; (3) the in-context-learning behavior that motivated agentic systems is a decoder-only phenomenon.
- **Per-token cost.** Prefill cost is FLOPs ≈ 2 · N_params · N_tokens (Kaplan et al. 2020 scaling laws — verify venue before citing). Memory cost is dominated by KV cache: ≈ 2 · N_layers · N_heads · d_head · N_tokens bytes per request, times every concurrent request. This grows linearly in context length; at long contexts, KV cache dominates parameter memory.
- Close with: "Every token in the context window has measurable compute, memory, and energy cost. The opportunity in compression is exactly proportional to the fraction of those tokens that do not change the answer."

#### 2.2 Scaling laws and the modern LLM (~1.5 pp)

- Trace: GPT-2 (1.5B, 2019) → GPT-3 (175B, 2020) → GPT-4 (undisclosed, 2023) → frontier models 2024–2026 (Llama-3.x, Qwen-72B/2.5, DeepSeek-V3/V4, Claude-Sonnet-4.x, GPT-oss-120B).
- Cite Kaplan et al. 2020 / Hoffmann et al. 2022 (Chinchilla) scaling laws. **Verify venues** before citing; Chinchilla appeared at NeurIPS 2022.
- Note the inference-cost asymmetry: scaling laws gave us a recipe to spend training compute productively, but inference cost — paid per query, forever — is proportional to (parameters × tokens), with tokens growing as contexts grow.
- Close with: "The frontier of capability is moving toward longer context windows; the frontier of cost is moving against them. Context compression sits at that intersection."

#### 2.3 The cost of running LLMs at scale (~1.5 pp)

This is where the **electricity-cost-and-wasted-tokens** motif (per the user's instruction) is developed in technical depth. P1 of the Introduction was the hook; this is the substance.

- **Energy (peer-reviewed anchor, per grilling Q5).** Open with Luccioni, Jernite & Strubell (2023/2024), *"Power Hungry Processing: ⚡ Watts ⚡ Driving the Cost of AI Deployment?"* — per-inference Wh measurements for open models, peer-reviewed. Quote the inference-Wh figures directly. Optionally extend with Patterson et al. (2021/2022) on ML carbon emissions as historical anchor.
- **Token economics.** Industry pricing as a proxy for cost: as of 2026, a frontier API charges roughly $3 / 1M input tokens and $15 / 1M output tokens (reference: plan-v3 §3 C3 cost model, citing fcgfinancial2026 internal). At a million calls a day, every 100 tokens of waste in the prompt template is $300/day input cost.
- **Politeness as waste (industry hook, labelled).** Altman's widely-reported remark that please/thank-you compute costs OpenAI "tens of millions of dollars" — cited explicitly as "press / industry reporting" alongside the peer-reviewed energy anchor above. The contrast (a tweet vs a measurement) is part of the rhetorical point: even informal observations agree that token waste is non-trivial in scale.
- **Multi-agent multiplier.** Anthropic's "How We Built our Multi-Agent Research System" (2025): token usage explains ~80% of performance variance in their multi-agent workflow. Cite honestly as industry observation, not academic measurement. Note that multi-agent systems pass shared context between agents, often more than once per round; the per-token cost is therefore multiplied by (agents × rounds × redundancy factor).
- Close with: "These costs motivate compression as an *engineering* lever, not a research curiosity. But applying compression in a multi-agent setting raises a question the literature has not yet asked: does the compressor preserve enough information for the agents to *still complete the task*?"

#### 2.4 Multi-agent LLM systems and shared context (~1.5 pp)

- Survey the major frameworks with their verified venues:
  - AutoGen (Wu et al., ICLR 2024 **LLM-Agents Workshop** — *not* main conference; honest)
  - MetaGPT (Hong et al., ICLR 2024)
  - CAMEL (Li et al., NeurIPS 2023)
  - Reflexion (Shinn et al., NeurIPS 2023)
  - MemGPT (Packer et al., arXiv 2310.08560 — preprint, label as such)
  - Generative Agents (Park et al., UIST 2023)
- For each, in one sentence: what coordination problem does it address, and *how does context flow between agents*. The point is to surface that each framework has its own implicit assumption about how much context to pass; none formally bounds the loss introduced when that context is compressed.
- Close with: "Multi-agent frameworks have proliferated, but the question of how much information must reach each agent for the system to function has been addressed empirically per-framework, never structurally. This thesis offers a structural answer (the coordination cliff and its predictive model)."

#### 2.5 Context compression — the breakthrough works (~3 pp, the largest 2.x subsection)

The user specifically asked for **related breakthrough works in compression**. Treat this subsection as a small standalone literature review.

Organise by *family*, with the venue and the algorithmic mechanism for each. Close every family with a "what this thesis does differently" line.

**2.5.1 Token-level pruning (the LLMLingua family)**
- Jiang et al. **LLMLingua** (EMNLP 2023) — small LM scores token importance, drop tail.
- Jiang et al. **LongLLMLingua** (ACL 2024) — question-aware compression for long retrieval contexts.
- Pan et al. **LLMLingua-2** (Findings of ACL 2024) — distil token-importance into a small XLM-RoBERTa classifier; the compressor used in this thesis.
- *What's missing:* coordination-quality evaluation. All three papers measure QA-F1 or perplexity; none measures whether a downstream planner can solve a multi-fragment task. **This thesis fills that gap (Ch 5, H1).**

**2.5.2 Selective and instruction-aware compression**
- Li et al. **Selective Context** (EMNLP 2023) — drop tokens with low self-information.
- Xu et al. **RECOMP** (ICLR 2024) — task-aware compression for retrieval-augmented LMs.
- *What's missing:* training-free instruction-awareness without an LM in the compressor. **This thesis includes an instruction-aware filter (TF-IDF + cross-encoder reranker) as a deliberately lightweight baseline (Ch 3, Ch 5).**

**2.5.3 Learned compression (parameter-cost compressors)**
- Mu et al. **Gist Tokens** (NeurIPS 2023) — fine-tuned compression into special tokens.
- Chevalier et al. **AutoCompressor** (EMNLP 2023) — recursive compression with summary tokens.
- Ge et al. **In-context Autoencoder** (ICLR 2024) — learned encoder/decoder.
- Rae et al. **Compressive Transformers** (ICLR 2020) — architectural compression of past memory.
- *What's missing:* training-free portability across compressor and planner. **This thesis stays entirely training-free, which both enables fair cross-compressor comparison and matches how practitioners deploy compression in production (Ch 3 §3.X compressor abstraction).**

**2.5.4 Extractive compression with small LLMs (the Phi-3 family)**
- Phi-3-Mini-3.8B (Microsoft, 2024 — model card; verify reference).
- *What's missing:* a principled way to prevent the small LM from paraphrasing — extractive constraints are easy to ask for, hard to enforce. **This thesis uses a post-hoc verifier (`Phi3ExtractiveCompressor._verify_extractive`) with a 15% novel-token tolerance and an LLMLingua-2 fallback (Ch 3 §3.X).** Document the limitation in Ch 8: even with the verifier, Phi-3 saturates at ~2.5× achievable compression regardless of target, which bounds its position on the compression frontier.

Close §2.5 with a **mandatory comparison table** (per grilling Q6 — the audience is non-NLP, so a side-by-side comparison is load-bearing). Rows are compressor families (LLMLingua-2, Selective Context, RECOMP, Gist Tokens, AutoCompressor, In-context Autoencoder, Phi-3 extractive). Columns: {training-free?, instruction-aware?, evaluated on multi-fragment coordination?, deployed in this thesis?}. The third column is all "No" except for this thesis. This table is the visual anchor for the rubric-#4 "what's missing in prior work" closing.

#### 2.6 RAG and long-context engineering (~1.5 pp)

Brief, because Ch 6 carries this load. Just the landmarks:
- Lewis et al. **RAG** (NeurIPS 2020).
- Sarthi et al. **RAPTOR** (ICLR 2024).
- Edge et al. **GraphRAG** (preprint 2024 — label as preprint).
- Gutiérrez et al. **HippoRAG** (NeurIPS 2024).
- Asai et al. **Self-RAG** (ICLR 2024).
- Liu et al. **Lost in the Middle** (TACL 2024).
- Bai et al. **LongBench** (ACL 2024); Hsieh et al. **RULER** (COLM 2024 / arXiv).
- Close: "None of these benchmarks measures the multi-fragment, multi-agent task structure of this thesis (coordination success under compression). This thesis treats LongBench / RULER as orthogonal: they measure context capacity; we measure compression behaviour under that capacity."

#### 2.7 Privacy in LLM and agentic memory systems (~1 pp)

- Survey: prior privacy-aware RAG protects the *retrieval index*; differential-privacy-finetuning protects the *model weights*. **None measures leakage through the compressor itself.**
- Cite at least one recent venue paper on RAG privacy (verify before submission) and one on LLM-memorisation / training-data extraction.
- Close: "Compression is a privacy lever in its own right — what is not in the compressed output cannot be inferred from it. The summary-level inference-disclosure metric (Ch 7) quantifies that lever directly."

#### 2.8 The gap this thesis closes (~0.5 pp)

A single, sharp paragraph. Four claims, each one sentence, each tied to one of C1–C4:
1. There is no shared multi-agent coordination benchmark probing the cliff. → C1.
2. There is no operational bound that predicts cliff position from compressor and task. → C2.
3. There is no honest catalogue of RAG pipeline placement under matched cost regimes. → C3.
4. There is no compressor-level disclosure measurement. → C4.

**Rubric anchors:** #4 (max), #3 (subsection structure), #9 (this chapter is the prose showcase; revise twice).

**Pitfalls:**
- *Do not* mark arXiv-only papers as peer-reviewed. plan-v3 §9 already disciplines this; copy the labels.
- *Do not* list 50 references with no commentary. The "what's missing" sentence at the end of each subsection is what differentiates a 5 from a 3 on rubric #4.
- *Do not* claim novelty against industry blog posts (Anthropic 2025). Call them "industry observations" and contrast methodology, not findings.

---

### Chapter 3 — System Design and Implementation (5–6 pp)

**Argument arc:**
The artefacts the experiments rest on, in just enough detail that a reader can replicate them. Lead with the memory bus (the user-facing contribution), then the compressor abstraction (the experimental substrate), then the deterministic-solver-vs-LLM-planner split (the honest framing — this is *not* multi-agent simulation).

**Subsections:**

#### 3.1 Memory bus architecture (~1.5 pp)
- Storage layer: scratchpad (TTL ephemeral), SQLite audit log (append-only, SHA-256 chain), FAISS vector store.
- Policy engine: Principal × Classification × Tag-based ACLs. Middleware intercepts every read/write.
- API: POST /v1/write (compress + store + audit), GET /v1/read/{slot_id} (policy-checked), POST /v1/subscribe (SSE bus), GET /v1/audit/{slot_id} (provenance chain).
- Compressor abstraction (CompressorAPI protocol). Wraps lingua2, filter, phi3-extractive, truncation, identity, CAAC interchangeably.
- One architecture figure (`figures/architecture_overview.{png,pdf}` — already generated; check caption).
- **"Designed for multi-agent, evaluated on multi-fragment" framing (per ADR-009).** The memory bus is built so a multi-agent system *could* use it; this thesis evaluates it under the multi-fragment proxy described in §3.3. Both claims are true; state them in the same paragraph so the scope is explicit.
- **Live-system evidence (per grilling Q8):** Appendix A includes a verbatim `curl` trace (write → read → audit) showing the bus accepting a fragment, compressing it, returning a CompressedSlot, and emitting a tamper-evident audit row. Half a page; cheapest "this thing actually runs" evidence and the rubric-#5 evidence for C4 delivery.

#### 3.2 Compressors (~2 pp)
For each, a 5–6 line paragraph: algorithm, parameters, deterministic-or-not, quirks. **This is the subsection that defines the q(r) curves that drive Ch 5.**
- LLMLingua-2 — XLM-RoBERTa token classifier; sentence-boundary force-tokens; smooth q(r).
- Phi-3-Mini extractive — Ollama-hosted Phi-3 + extractive prompt; `_strip_novel_tokens` post-hoc; 15% novel-token tolerance; LLMLingua-2 fallback; **2.5× compression ceiling** (call out — limitation).
- Instruction-aware filter — TF-IDF prune → BAAI/bge-reranker-base rerank → stop-word + short-token drop.
- Truncation — prefix keep, baseline.
- Identity — control.
- CAAC — wrapper, deferred to Ch 8. *Mention only in passing* in this chapter ("CAAC is a wrapper compressor reviewed in Ch 8 as a constructive realisation of the compounding-error model").

#### 3.3 Scope of evaluation: the multi-fragment proxy (~0.5 pp)
- Under ADR-009, the scope rename makes this subsection **descriptive rather than confessional**. Since the Abstract and Ch 1 P5 already state the scope, §3.3 just restates the method:
- "Per the manuscript scope (Abstract; Ch 1 P5), all experiments measure planner solvability on multi-fragment workloads. H1/H2 use a deterministic regex-based information-extraction solver to isolate compression effects from LLM variance; H5, H6, and the frontier validation use a single LLM call with all (compressed) fragments visible. An AutoGen multi-round agent backend exists in `src/m6/orchestrator/` and integrates with the memory bus described in §3.1, but is outside the empirical scope of this thesis."
- This subsection no longer reads defensively because §3.3 is no longer where the reader first learns the scope — the title and abstract already said so. Rubric #6 protected by construction.

#### 3.4 Critical-token-recall (CTR) metric (~0.5 pp)
- Why generic token-recall is insufficient (Phi-3 preserves "the"/"and" but drops numbers → high recall, low coordination).
- CTR is family-specific: multi-digit numbers (family-a), all digits (family-b), chain references + FINAL (family-c).
- Per the 2026-05-29 reconciliation (insights §55, ADR-007), CTR is canonical for cliff prediction, CAAC, and theorem validation.

#### 3.5 Compression cache (~0.5 pp)
- `CompressionCache` + `CachedCompressor` (`src/m6/compressors/cache.py`) — JSON store keyed by (compressor, ratio, fragment_id, task_hint_hash).
- Precompute on GPU once (`precompute_cache.py`); evaluation runs locally. Decouples compression from evaluation.
- This unblocks reproducibility (Appendix A): you can rerun every figure on a laptop without rerunning the compressor.

#### 3.6 Reproducibility envelope (~0.5 pp)
- Single Apple M4 Pro 48GB (laptop) + optional RTX 5090 32GB (GPU server, WSL2). Python 3.12 + Ollama. Total wallclock ~22 h (core) + ~8 h (frontier + HotpotQA).
- Single `make` target per chapter figure. Docker compose for full reproducibility (Appendix A).

**Rubric anchors:** #5 (delivery of C4 — memory bus), #6 (honest description of the solver), #10 (architecture figure clean).

**Pitfalls:**
- *Do not* describe AutoGen multi-agent as if it ran in production. It didn't. §3.3 is non-negotiable.
- *Do not* paper over the Phi-3 2.5× ceiling. It's a real constraint and reviewers will notice when they read Ch 5.

---

### Chapter 4 — The C1 Benchmark (5–6 pp)

**Argument arc:**
Why a synthetic benchmark (controlled cliff probing, reproducible). How the three families differ in information-density structure (foreshadowing Corollary 2). How workloads are generated, scored, and audited.

**Subsections:**

#### 4.1 Why synthetic (~0.5 pp)
- The cliff is a position on the (compression-ratio, coordination-success) curve. Real benchmarks (HotpotQA, MultiHopRAG) confound the cliff with task difficulty and dataset distribution. Synthetic generation lets you place θ_info wherever you want, then verify the cliff appears where the model predicts.
- Explicit limitation: "C1 is a controlled probe of the cliff, not a benchmark of real-world task performance. Ch 7 validates the cliff persists on real datasets (HotpotQA, MultiHopRAG); Ch 8 discusses generalisation."

#### 4.2 Three task families (~3 pp)
Half a page each (a, b, c) plus a comparison table.
- **Family-a (cross-document fact aggregation)**: sum N numbers across 8 fragments; deterministic regex scoring. θ_info ≈ 0.97 (dense). Critical tokens = multi-digit numbers.
- **Family-b (constraint-satisfaction planning)**: assign sub-tasks to workers under capacity; feasibility scoring (commit 9d006f7). θ_info intermediate. Critical tokens = all digits. **Limitation**: LLM planners (1.5B–8B) struggle with constraint tracking even uncompressed; family-b baseline near zero for small models — discuss in §4.5 limitations.
- **Family-c (multi-step retrieval)**: chain-of-references to a FINAL answer. θ_info ≈ 0.59 (distributed). Critical tokens = "entry X" + "FINAL-XXXX". Filter compressor preserves these even under aggressive compression — discuss in Ch 5 as evidence that compressor + task interact.

#### 4.3 Workload schema (~0.5 pp)
- Fragment, task_hint, tags (PUBLIC / INTERNAL / CONFIDENTIAL), expected_answer, seeds.
- Reproducibility: every workload regeneratable from `data/processed/c1-v0.1/` + seed.

#### 4.4 Coordination success and supporting metrics (~0.5 pp)
- Binary per-cell outcome; aggregated across seeds.
- Supporting: qa_f1 (token overlap, the H1 "wrong metric"), coord_success (the right metric), token_recall, critical_token_recall, achieved_ratio.
- **achieved_ratio vs target_ratio** — Phi-3 ceiling makes this non-trivial; report achieved throughout.

#### 4.5 Limitations of C1 (~0.5 pp)
- Family-a: all 50 instances are sum-of-N-numbers — zero reasoning-type variability. Generalisation to heterogeneous aggregation is future work.
- Family-b: capacity-inflated to ensure feasibility; trivial for the deterministic solver, hard for LLM planners. The baseline gap masks compression effects for small models. We retain the family in H5 as a deliberately hard cell.
- Family-c: chain length capped at 4. Longer chains may shift θ_info.

**Rubric anchors:** #5 (C1 delivery), #6 (limitations stated proactively).

---

### Chapter 5 — Compression Effects on Coordination (11–13 pp) — **the headline chapter**

This is where rubric #5, #6, and #7 are won or lost. Plan its structure twice; write the rest of the thesis around its claims.

**Argument arc:**
QA-F1 and coordination success are decorrelated (H1). The cliff exists, is sharp, and is statistically robust (H2). A simple compounding-error model derives where it lives (θ_q + q(r) → predicted τ\*). Bootstrap CIs on θ_q give a *predicted-τ\* band* that overlaps empirical τ\* on most cells. Model scale moves the *ceiling* p₀, not the cliff position — this is Corollary 1, validated on Qwen-72B and DeepSeek V4 Pro within the calibrated regime. Extended-reasoning planners (GPT-oss 120B) violate the calibrated-regime predicate; this is a finding, not an embarrassment.

**Subsections:**

#### 5.1 Experimental design (~0.5 pp)
- Sweep: **4 compressors (lingua2, phi3-extractive, filter, truncation)** × 10 ratios × 3 families × 50 workloads × 5 seeds = 30,000 cells.
- **Canonical results: `results/h1_h2_v2/`** (per grilling Q4). The 4-compressor sweep adds the truncation baseline, which gives a clean lower-bound argument ("even a trivial prefix-truncation baseline cliffs"; "any learned compressor must beat truncation to justify its cost"). Headline numbers in this chapter are taken from `h1_h2_v2/verdicts.json` and `h1_h2_v2/summary.json` — refresh from `h1_h2_v2` (not `h1_h2_final`) on the writing pass; existing CLAUDE.md / insights numbers were from `h1_h2_final` and need a one-pass update.
- Statistical protocol: paired Wilcoxon (within-workload), bootstrap 95% CI (workload-level), Holm correction across (compressor × family) cells (12 cells for the 4-compressor variant).

#### 5.2 H1 — QA accuracy decorrelates from coordination (~1.5 pp)
- **Verdict block at the top of the subsection** (so the reader does not have to search): *"H1 SUPPORTED. Spearman ρ between Δqa-F1 and Δcoord-success ranges [−0.59, +0.38] across compressors; all 95% bootstrap CIs exclude 0.6 from above."*
- Per-compressor table: ρ, p-value, 95% CI, n. Use h1_h2_final numbers (see inventory). Note that *filter* has a *negative* correlation — surprising: this is the rerank-keeps-task-keywords effect. **Discuss in interpretation paragraph.**
- Figure: `figures/h1_scatter.png` (already generated; check it points to h1_h2_final).
- **Interpretation paragraph (rubric #6 territory):** Compression that preserves "average token quality" (QA-F1) is not the same as compression that preserves "task-critical token quality" (coordination success). For multi-agent systems, the latter is what matters; for single-agent QA benchmarks (LongBench, LongLLMLingua), the former is what is measured. This invalidates single-agent benchmarks as proxies for multi-agent coordination performance. Cite LongBench / RULER for contrast.
- **Comparison to prior work paragraph:** LongLLMLingua reports QA-F1 retention at 4× compression; we report coordination success at the same operating point. The QA-F1 metric *over-reports* compressor utility for multi-agent settings.

#### 5.3 H2 — A coordination cliff exists, is sharp, and is statistically robust (~2 pp)
- **Verdict block:** *"H2 SUPPORTED. 8/9 (compressor × family) cells show paired-Wilcoxon p < 0.0001 (Holm-corrected) with relative drop ≥ 30%. Only filter/family-c shows no detectable cliff (the filter preserves chain-reference tokens; this is itself a finding)."*
- Headline τ\* table — 3 compressors × 3 families, with bootstrap CI.
- Cliff hero figure: `figures/cliff_hero.png` — coord_success vs ratio, sharp drop on family-a, gradual on family-c.
- Family breakdown figure: `figures/cliff_families.png`.
- **Interpretation paragraph:** The cliff is not a smooth degradation; it is an S-curve crossing. The shape is consistent with a threshold-success generative process (q exceeds θ ⇒ success; q falls below θ ⇒ failure). This motivates §5.4.

#### 5.4 The compounding-error model (~2 pp) — the theoretical core

Follow ADR-008 verbatim: *model*, not *theorem*; *derivation paragraph*, not *formal proof*; **calibrated regime defined here**.

- **Setup (~0.5 pp).** Define X_i / M_i (task-relevant tokens surviving / total task-relevant tokens), the threshold-success model success_i = 1[X_i / M_i ≥ θ_q], per-token retention q(r) at compression ratio r, and the number of compression passes N (= 1 throughout). Cite CONTEXT.md definitions.
- **Derivation (~0.5 pp).** From independence (A1) and threshold success (A3): E[X_i / M_i] = q(r), so P(success | r) → 1[q(r) ≥ θ_q] in expectation. The cliff position r\* solves q(r\*) = θ_q^(1/N). With N=1, r\* solves q(r\*) = θ_q. **This is a paragraph, not a Lemma 1.2.3 hierarchy.**
- **Assumptions A1–A4 (~0.5 pp).** Round independence (A1, approximately true at N=1), binary token importance (A2, approximately true but graded importance is what H4 measures), threshold success (A3, approximately true given the observed cliff sharpness), per-round retention measured as critical_token_recall (A4).
- **The calibrated regime (~0.5 pp).** Definition (ADR-006): A planner is in the calibrated regime if (a) p₀(planner) ≥ θ_q (no floor effect) AND (b) the planner does not recover from sub-threshold information via extended reasoning beyond what the priors-only baseline supplies. The priors-only-baseline measurement is reused from H4 to operationalise (b). Out-of-regime planners (e.g., GPT-oss 120B) are noted; the model's predictions are scoped to in-regime planners.

#### 5.5 Predicted vs empirical τ\* (~1.5 pp)
- The bootstrap-CI-on-θ_q machinery (insights §55 Decision 3, ADR-008 trade-off analysis): bootstrap θ_q estimates from h1_h2_final per-family CTR sweeps, propagate through q(r*) = θ_q to produce a **predicted-τ\* band**.
- Figure: a *replacement* for the audit-flagged `figures/predicted_vs_empirical.{png,pdf}` showing the band on top of empirical τ\*. Family-c is the most informative (per insights §53 — empirical cliff at r ≈ 6–7, predicted at r ≈ 3.5, so the model is *conservative*; the gap is what Corollary 2 explains).
- **Empirical match rate:** 33% strict per-family with critical_token_recall (per insights §55), 58% at ±25% tolerance. **Report both numbers honestly.** This is not a refutation; it is a first-order model with quantified residuals — explicitly invite future work to refine.
- **Interpretation paragraph:** The model is a *first-order* bound. Its tightness depends on how well A2 (binary token importance) holds — graded importance is what H4 demonstrates, and Corollary 2 hints that per-task θ_info captures the second order.

#### 5.6 H5 reframed as Corollary 1 (ceiling-cliff separation) (~2 pp)
- **Verdict block:** *"Original H5 (τ\* monotonic in planner scale on ≥ 2/3 families): NOT SUPPORTED. Reframed as Corollary 1: τ\* is invariant to planner scale within the calibrated regime (family-c, all three Qwen sizes, τ_spread = 24%). Floor effects (family-a 1.5B/3.8B, family-b all scales) correctly identify out-of-regime cells."*
- Always lead with the corollary verdict.
- Figure: `figures/scaling_auc.png` and `figures/h5_model_overlay.png`. Verify both point to h5_final.
- **Interpretation paragraph:** Model capacity affects the *ceiling* p₀ (a larger model succeeds more often at r=1), not the *cliff position* τ\* (the ratio at which it falls off). This is what the compounding-error model predicts: τ\* depends on the compressor's q(r) and the task's θ_q, not on the planner.
- **Limitation paragraph:** All three sizes are Qwen variants; cross-architecture validation appears in §5.7.

#### 5.7 Frontier validation within the calibrated regime (~2–3 pp, per grilling Q7)

This is the strongest single finding in the thesis. Promoted from a single page to 2–3 pp with sub-paragraph structure so the cross-architecture invariance result lands with the weight it deserves. Rubric #7 (significance, max 5) is largely won or lost here.

**5.7.1 Setup (~0.3 pp).** Frontier validation uses the same C1 family-a sweep used for the synthetic τ\* reference, but the planner is swapped for a frontier model accessed via API (`run_frontier.py`). All three frontier models receive identical compressed fragments produced by LLMLingua-2 at matched ratios; only the planner varies. Sample size: 180 cells per model. Statistical protocol: paired bootstrap on τ\*, Holm correction across the three models.

**5.7.2 Qwen 72B — in-regime, 0.8 % off (~0.5 pp).** Empirical τ\* = 2.68 vs synthetic reference τ\* = 2.70. The bootstrap CI on the frontier τ\* contains the synthetic point estimate. **Interpretation:** a 72B Qwen-2.5 frontier planner cliffs at the same compression ratio as the local 8B Qwen-2.5 planner used in the synthetic reference. The model's prediction holds across a 9× parameter-count change within the same architecture family.

**5.7.3 DeepSeek V4 Pro — in-regime, CI contains synthetic (~0.5 pp).** Empirical τ\* point estimate 2.15; bootstrap CI [1.76, 7.14] contains synthetic 2.70. **Interpretation:** the model's prediction holds across architecture families (Qwen ⇆ DeepSeek), not just across parameter counts. Wider CI than Qwen-72B because the sweep was run with fewer seeds; this is documented as a sample-size limitation in §8.3.

**5.7.4 GPT-oss 120B — out-of-regime diagnostic (~0.5 pp, per ADR-006).** Empirical τ\* = 6.62 vs synthetic 2.70 (145% off). v1 has a floor effect (baseline = 0.53 < θ_q), v2 does not (baseline = 1.0) — yet both produce τ\* substantially above the prediction. **Diagnosis (ADR-006):** extended-reasoning planners (GPT-oss class) recover from sub-threshold information via chain-of-thought reasoning, violating assumption A3 (threshold success). Standard non-reasoning planners (Qwen, DeepSeek, Llama-3.1) do not. The 145 % deviation is preserved on disk under `STATUS_NONCANONICAL.txt` (scoping, not hiding) and reported here as a **positive contribution**: an empirical boundary on where the compounding-error model breaks. This sets up §8.6 future work on extended-reasoning planners.

**5.7.5 Multi-model figure walkthrough (~0.3 pp).** `figures/frontier_validation.{png,pdf}` shows the in-regime models against the synthetic reference; `figures/frontier_multi.{png,pdf}` overlays all three frontier curves with the synthetic reference band. Caption explicitly marks GPT-oss as "out-of-regime per ADR-006". Both figures verified post-§55 audit.

**5.7.6 Significance — the cross-architecture invariance result (~0.4 pp, rubric #7).** Putting the three results together: τ\* is invariant to (parameter count: 1.5B → 72B, within Qwen family) **and** to (architecture family: Qwen → DeepSeek). It is *not* invariant to (reasoning regime: standard → extended). Within the calibrated regime, the cliff is a property of the compressor and the task, **not** the planner — this is the empirical centrepiece of Corollary 1. Outside the calibrated regime, the cliff position shifts; characterising this regime is the largest future-work direction the thesis opens.
- **Practitioner significance:** measure τ\* on a small local model; deploy at the same τ\* on a frontier model without re-measuring — *provided* the frontier model is in the calibrated regime.
- **Scientific significance:** the cliff is a property of the **(compressor, task) pair**, not a model-scaling artefact. Single-agent benchmarks that vary the model and hold the compressor fixed cannot reveal this; the controlled sweep methodology of this thesis can.

#### 5.8 Mechanism discussion (~0.5 pp)
- Why the cliff is sharp (Chernoff concentration: P(success) ≤ exp(−2M(q − θ_q)²) for q < θ_q — explain in plain language).
- Why filter / family-c does not show a cliff (filter's TF-IDF preserves rare task-keywords like "FINAL"; the task degrades gracefully).
- Foreshadow Ch 8 §8.2 CAAC: the compounding-error model's q_min = θ_q is exactly what CAAC uses as its backoff floor.

**Rubric anchors:**
- #4 (compare to LongLLMLingua / LongBench), #5 (C2 delivered), #6 (every result has a verdict block, table, figure, interpretation, comparison, significance paragraph), #7 (cross-architecture cliff invariance is the publishable finding).

**Pitfalls:**
- *Never* write "Theorem 1". The word is reserved for the codebase identifier `theorem_validation.json` (mention once in a footnote with the CONTEXT.md mapping).
- *Always* qualify model-independence claims with "within the calibrated regime".
- *Do not* hide GPT-oss 120B. ADR-006 says: scoping, not hiding.

---

### Chapter 6 — RAG Pipeline Placement and Cost (4–5 pp) — H3

**Argument arc:**
Three pipelines (P1 compress→retrieve, P2 retrieve→compress, P3 joint routing) under matched cost regimes. H3 predicted a sign-flip between storage- and accuracy-bounded regimes; **the sign-flip did not appear**. Instead, P1 (compress-first) is robustly ahead of P2 in both regimes — which itself **challenges the standard LongLLMLingua assumption** that post-retrieval compression is the more efficient placement.

**Subsections:**

#### 6.1 Pipeline design (~1 pp)
- P1, P2, P3 architectures (figure: `figures/rag_pipelines.{png,pdf}`).
- FAISS index + BAAI/bge-large-en-v1.5 retriever. EUR/workflow cost model.

#### 6.2 Results (~1.5 pp)
- **Verdict block:** *"H3 NOT SUPPORTED for the predicted sign-flip. Reframed finding: P1 (compress-first) ≻ P2 (retrieve-first) in both storage- and accuracy-bounded regimes; P3 (joint routing) ≻ both."*
- Per-regime tables: F1 + EUR/workflow for {P1, P2, P3}, with paired bootstrap CIs and Holm-corrected p-values from `h3_final`.
- Figure: `figures/h3_pipelines.{png,pdf}` (verify caption reflects honest reframing).

#### 6.3 Interpretation (~1 pp)
- **Why the sign-flip didn't appear:** P2's storage cost is amortised over the *uncompressed* corpus, which scales worse than P1's compressed corpus. The retrieval-cost-amortisation argument that motivated post-retrieval compression in LongLLMLingua assumed retrieval was cheap; in practice the FAISS index for an uncompressed corpus is the dominant cost.
- **Significance:** This is a *positive* finding for practitioners: the simpler architecture (compress once, index forever) is also the cheaper architecture. The thesis recommends compress-first as the default and joint routing for highest-quality workflows where the extra implementation cost is justified.

#### 6.4 Limitations (~0.5 pp)
- Single retriever, single embedder. Different retrievers may shift the cost balance.
- Cost model uses target compression ratio, not achieved ratio (Phi-3 ceiling). Discuss in Ch 8 limitations.

**Rubric anchors:** #5 (C3 delivered as reframed finding), #6 (honest verdict and significance), #7 (concrete practitioner recommendation).

**Pitfalls:**
- *Do not* phrase H3 as "a failed hypothesis". The cleanest framing per ADR / CLAUDE.md: "predicted sign-flip did not appear; the *robustness* of compress-first is itself a finding".

---

### Chapter 7 — Inference Disclosure, Memory-Bus Integration, and Information-Density Scaling (6–7 pp) — H4 + H6/Cor2

**Argument arc:**
The memory bus stores summaries — what does the summary leak? Define a per-fragment protected-fact-recovery metric using a held-out local Llama-3.1-8B reader. Run three conditions (priors-only, baseline=uncompressed, compressed=4×). Show that the metric distinguishes baseline from priors (compression preserves something measurable), and that 4× compression reduces disclosure relative to baseline. Discuss the reader's "no" bias caveat openly. Bridge to Corollary 2: information-density scaling — θ_info varies across tasks, and the cliff varies accordingly.

**Subsections:**

#### 7.1 Why this matters (~0.5 pp)
- A memory bus that summarises CONFIDENTIAL fragments is a privacy boundary. If the compressed summary leaks the protected fact, the classification was meaningless.
- The summary-level inference-disclosure metric quantifies that boundary as a function of compressor and ratio.

#### 7.2 Metric definition (~1 pp)
- Per CONFIDENTIAL fragment, a list of (yes/no question, ground-truth answer) pairs whose ground truth is a protected fact (e.g., "Did agent A approve more than €N?").
- Three conditions: `priors` (reader sees only the public preamble), `baseline` (uncompressed fragments), `compressed_4x` (Phi-3 / lingua2 / filter at 4×).
- Reader: local Llama-3.1-8B (Ollama-hosted). The metric is the true-positive recovery rate, with paired-bootstrap CIs.
- **Question-design note:** the original h4_final benchmark had a question-template surface-pattern bias (insights §X, CLAUDE.md 2026-05-29 note); the benchmark generator was fixed (`fact_aggregation.py:119-156`). **The canonical results directory for thesis numbers is `h4_unbiased`, not `h4_final`.**

#### 7.3 Results (~2 pp)
- **Verdict block:** *"H4 SUPPORTED on the unbiased benchmark. Signal +29 pp (priors 0.50 → baseline 0.78, p=0.0001). Compression reduces disclosure by −21 pp (filter), −19 pp (lingua2), both p=0.0001; −7.5 pp (phi3-extractive, p=0.027, borderline)."*
  - **Footnote (per grilling Q11):** *"The reader (Llama-3.1-8B) exhibits asymmetric YES/NO accuracy — see §7.4 for full discussion. Pooled rates report balanced ground-truth performance; per-class breakdowns are documented before the verdict is interpreted."* — this single sentence in the verdict block protects rubric #6: the examiner cannot read further without knowing the asymmetry exists.
- Table from `h4_unbiased/verdicts.json`.
- Figure: `figures/privacy_quality.{png,pdf}` (the compressor fingerprints view).
- **Interpretation paragraph:** Compression aggressiveness correlates with disclosure reduction. Aggressive token-level compressors (filter, lingua2) drop more protected tokens; extractive copying (phi3) preserves enough surface tokens that the leak persists. This makes the disclosure metric *useful*: it ranks compressors by privacy, not just by ratio.

#### 7.4 Reader-bias caveat (~0.5 pp)
- Llama-3.1-8B under-predicts YES: when ground truth = YES, priors_rate ≈ 0.03; when ground truth = NO, priors_rate ≈ 1.00. Pooled priors ≈ 0.50 reflects balanced ground-truth distribution.
- Framing per CLAUDE.md: "H4 measures *compression preserves enough to flip a no-biased reader to confident yes* — asymmetric but still a valid leakage signal." State this in plain prose.

#### 7.5 Memory-bus integration (~0.5 pp)
- How the policy engine uses the metric: per-classification, per-compressor disclosure budget. A CONFIDENTIAL fragment with disclosure > budget triggers (a) re-compression at a higher ratio, (b) downgrade to a stricter compressor, or (c) deny.
- No empirical evaluation of the budget policy is required (out of scope); the metric *enables* the policy — that's the contribution.

#### 7.6 H6 reframed as Corollary 2 (information-density scaling) (~1.5 pp)
- **Verdict block:** *"Original H6 (synthetic τ\* within ±15% of MultiHopRAG τ\*): NOT SUPPORTED (MHR τ\* = 11.3 vs C1-a τ\* = 2.7, 320% off). Reframed as Corollary 2: θ_info scales with task information density. MultiHopRAG θ_info = 0.484, C1-a θ_info = 0.967, HotpotQA θ_info = 0.373 — gaps of 0.48 and 0.59 respectively, well above the 0.1 threshold. Corollary 2 SUPPORTED."*
- Lead with the corollary verdict. Disclose the original predicate did not hold and explain *why* (the synthetic prediction assumed θ_info ≈ const; the real result is that θ_info is task-structure-dependent).
- Cite `h6_final` and `hotpotqa_sweep` as canonical.
- **θ_q vs θ_info reminder (CONTEXT.md):** Corollary 2 uses θ_info (AUC-based, per-task), distinct from θ_q (recall-threshold, per-family) used in the cliff equation. The CTR end-to-end switch for CAAC and the compounding-error model does *not* affect Corollary 2.
- Figure: `figures/hotpotqa_cliff.{png,pdf}` (verified by insights §55 audit-hygiene status to be backed by real data).

**Rubric anchors:** #5 (C4 delivered, plus Corollary 2 as a bonus), #6 (reader-bias caveat is exactly the kind of honest evaluation rubric #6 rewards at 5).

---

### Chapter 8 — Discussion, CAAC, Limitations, Future Work (7–9 pp)

**Argument arc:**
Pull every thread together. What we measured (cliff exists, is sharp, is model-invariant within regime, scales with task density, leaks predictably). What we built (memory bus + CAAC — the latter is the constructive realisation of the compounding-error model). What we cannot claim (limitations). What's next.

**Subsections:**

#### 8.1 Synthesis (~1 pp)
- The cliff is real (H2). It is decorrelated from QA accuracy (H1). It is determined by compressor + task, not by model scale within the calibrated regime (Corollary 1, frontier-validated). It is sharper for dense tasks than for distributed tasks (Corollary 2). It is privacy-relevant (H4).
- Practitioner takeaway: pick a compression ratio below your task's τ\*, choose a compressor whose q(r) curve gives you that ratio with margin, and accept that you cannot brute-force past τ\* with a bigger model.

#### 8.2 CAAC: a constructive realisation of the compounding-error model (~3 pp)

Per ADR-007, this is the home of the CAAC discussion. **Framing is operating-point selection, not Pareto dominance.**

- **What CAAC does:** wraps any inner compressor; checks per-fragment critical_token_recall after compression; if recall < θ_q^(1/N), back off (binary search down to min_ratio = 1.5) until recall ≥ q_min.
- **The strict-Pareto rate is 0/7. This is correct and expected.** CAAC by construction trades compression for safety; at lingua2 r=16, CAAC achieves +32.7 pp coordination at 25× *less* effective compression than fixed. The two algorithms populate complementary regions of the (coord_success, achieved_ratio) frontier.
- **The contribution is the *predictable* operating point:** given per-family θ_q (from `derive_theta()`), CAAC's selected point is *determined by the compounding-error bound*, not by tuning. Three families → three operating points → a *family* of compressors generated from the model.
- **Figure:** `figures/caac_pareto.{png,pdf}` regenerated as the **region plot** prescribed by ADR-007 — CAAC's high-coord modest-compression region vs fixed-ratio's low-coord high-compression region, with the q_min = θ_q curve as the boundary. **This figure must exist by submission day**; it's the visual that lands the operating-point framing.
- **Ablation summary (one paragraph + one table):** θ ∈ {0.6, 0.7, 0.8} and N ∈ {2, 3, 4, 5} sweeps (insights §54). All seven configs are NOT SUPPORTED on strict Pareto and 100% weak-dominant. CAAC's coord output is *invariant* to θ and N (lingua2 plateau 33.3%, filter plateau 64.0%); θ and N only change *how aggressively CAAC backs off compression*. The primary knob is `min_ratio`; a min_ratio sweep is named in §8.6 future work.
- **Foreshadow CAAC's positioning for any future research:** as an *operationalisation* of the compounding-error model, CAAC turns a measurement (cliff position) into a control (operating-point selection). The reframe is the thesis-relevant contribution; a future paper could promote CAAC back to a method contribution.

#### 8.3 Limitations (~1.5 pp)

Enumerate honestly. Rubric #6 rewards this directly.

- **No multi-round agent coordination:** deterministic regex solver (H1/H2) and single-LLM-call planner (H5/H6/frontier) measure *task solvability under compression*, not multi-round communication quality. The AutoGen backend exists but was excluded due to variance masking compression effects.
- **N=1:** the q^N formulation is in the model but unvalidated empirically for N > 1.
- **Family-a homogeneity:** 50 instances are all "sum 8 numbers" — generalisation to heterogeneous aggregation types is unverified.
- **Family-b LLM ceiling:** small planners (1.5B/3.8B) score near zero baseline; compression effects are unmeasurable in this regime. Documented in Ch 5 H5 verdict.
- **Phi-3 compression ceiling at ~2.5×:** the extractive verifier + fallback prevent compression beyond this point. Reported as achieved_ratio throughout; the cliff curves for phi3 truncate accordingly.
- **Extended-reasoning planners out of the calibrated regime:** GPT-oss 120B (and likely GPT-4o + thinking) violate A3; the model's predictions do not apply. ADR-006 formalises this as the calibrated-regime predicate.
- **Compounding-error model is first-order:** 33% strict / 58% ±25% match rate on per-family CTR validation. The model is a useful bound, not a tight predictor.
- **Synthetic-task focus:** C1 is synthetic; HotpotQA and MultiHopRAG validate the cliff exists on real tasks but at different θ_info. Generalisation to arbitrary task structures requires further validation.
- **Single embedder / single retriever (Ch 6):** RAG cost balance may shift under different retrievers.
- **Reader bias in H4:** Llama-3.1-8B under-predicts YES; the metric measures asymmetric leakage. Documented in Ch 7 §7.4.

#### 8.4 Significance — practitioner and scientific (~1.5 pp)

**Rubric #7 territory. Make both claims explicit.**

- **For practitioners:** (a) you can predict your task's cliff from token-recall measurements alone, without expensive end-to-end coordination evaluation; (b) compress-first (P1) is the cheaper and better RAG architecture in both cost regimes; (c) compression is a privacy lever — choose your compressor by ratio *and* by disclosure; (d) CAAC gives you a safe operating point with zero tuning if you have per-family θ_q.
- **For the field:** (a) single-agent QA benchmarks (LongBench, RULER, LongLLMLingua eval) systematically *over-report* compressor utility for multi-agent settings — coordination-aware evaluation is necessary; (b) the cliff is a property of the compressor and task within the calibrated regime, not of model scale — bigger models don't fix it; (c) extended-reasoning planners are a *different regime* that prior compression work has not characterised; (d) information density (θ_info) scales the cliff in a way that future benchmarks should control for.

#### 8.5 Comparison to industry observations (~0.5 pp)
- Anthropic's 80%-token-usage observation (industry blog 2025) is consistent with the cliff: above τ\*, removing tokens removes the information the agents need. Our contribution: *characterising* that relationship structurally, not just observing it.

#### 8.6 Future work (~1 pp)
- **Extended-reasoning regime:** characterise the cliff for planners that recover from sub-threshold information via chain-of-thought. This is the gap left by ADR-006.
- **Per-task θ_q estimation:** lift the model from per-family to per-task; current 33% strict match should improve to ≥ 60%.
- **N > 1 (multi-pass compression):** validate q^N empirically.
- **CAAC min_ratio sweep:** the primary knob, untested in insights §54 (deferred).
- **Multi-round AutoGen evaluation:** replace the deterministic solver with multi-round agents and measure the additional variance compression adds.
- **Broader task families:** heterogeneous aggregation, multi-tool reasoning, multimodal.

**Rubric anchors:** #5 (CAAC honest framing), #6 (limitations + significance), #7 (practitioner + scientific significance both made explicit).

---

### References (8–12 pp)

- Organise by topic, matching plan-v3 §9 categories.
- **Verify every venue.** Specifically: AutoGen is ICLR workshop (not main), GraphRAG is preprint, MemGPT is preprint, LLM-Lingua-2 is *Findings of ACL* (not main ACL), RULER is COLM 2024 / arXiv. Label honestly.
- Use a consistent style — IEEE or APA. IEEE is more common in engineering theses at Oulu; check the supervisor's preference. Default: IEEE.
- 30–50 references is appropriate for a thesis of this scope. plan-v3 §9 already lists ~35 verified references plus statistics / industry / internal.

### Appendix A — Reproducibility (~3 pp)

- One `make` target per chapter figure.
- Docker-compose for the memory-bus service.
- GitHub release tag for the codebase.
- Model cards: Qwen2.5-{1.5B, 3.8B, 8B, 72B}-Instruct, Phi-3-Mini-3.8B-Instruct, Llama-3.1-8B-Instruct, DeepSeek-V4-Pro, LLMLingua-2 (XLM-RoBERTa).
- Data cards: C1, MultiHopRAG, HotpotQA.
- Compute envelope: M4 Pro 48 GB + RTX 5090 32 GB (WSL2); total wallclock ~30 h end-to-end.

### Appendix B — Full per-cell results tables (~3 pp)

- One table per hypothesis. Rows = (compressor, family, planner). Columns = baseline coord, τ\*, τ\* CI, drop_rel, p-value, q(τ\*), critical_token_recall.
- Pulled directly from `results/*_final/results.csv` + `verdicts.json`.

### Appendix C — Expanded derivation of the compounding-error model (~1 pp)

- If a reader wants more than the Ch 5 paragraph, this is the deeper version: assumptions A1–A4 spelled out, Chernoff bound for the cliff sharpness, q^N reduction to N=1.
- Per ADR-008, this is *not* a formal proof; it's the longer-form derivation.

### Appendix D — Figure index (~1 pp)

- Every figure with its filename, generator script, caption, and the canonical CSV it draws from.

---

## 5. Figure / table inventory (with regeneration plan)

Per the results-inventory agent, all 22 figures × 2 formats (PNG + PDF) exist in `figures/`. Before submission:

| Figure | Status | Action before submission |
|--------|--------|--------------------------|
| `architecture_overview` | ok | Verify caption mentions FastAPI + SQLite + FAISS |
| `compressor_overview` | ok | Caption should clarify "the four compressor families evaluated in this thesis" |
| `h1_scatter` | ok | Caption: ρ, CI, n per compressor |
| `cliff_hero` | ok | Caption: dominant family-a cell, baseline, τ\* |
| `cliff_families` | ok | Caption: 3×3 grid; mark filter/c as "no cliff detected" |
| `cliff_mechanism` | ok | Schematic; verify text matches Ch 5 §5.8 mechanism |
| `h3_pipelines` | ok | Caption: honest reframing — P1 ≻ P2 in both regimes |
| `compressor_fingerprints` | ok | Caption: H4 unbiased numbers (refresh from h4_unbiased) |
| `scaling_auc` | ok | Caption: corollary 1 framing, calibrated-regime qualifier |
| `h5_model_overlay` | ok | Caption: 3 Qwen scales, family-c shown |
| `predicted_vs_empirical` | **regenerate** | Replace with predicted-τ\* band figure (per ADR-008, insights §55 audit-hygiene action) |
| `theta_density` | demote | Move to Appendix as "future work data" per insights §55 audit-hygiene |
| `caac_pareto` | **regenerate** | Replace with region plot per ADR-007 (high-coord vs high-compression regions, q_min = θ_q boundary) |
| `caac_ablation` | ok | Caption: θ/N sweep informative null per §54 |
| `caac_flowchart` | ok | Caption: algorithm description |
| `frontier_validation` | ok | Caption: Qwen 72B + DeepSeek V4 Pro within calibrated regime; GPT-oss noted as out-of-regime |
| `frontier_multi` | ok | Same caveat |
| `hotpotqa_cliff` | ok | Backed by real data per insights §55 audit-hygiene |
| `privacy_quality` | ok | Refresh from h4_unbiased |
| `pareto_privacy_coordination` | ok | Caption: H4 + H1 joint view |
| `corollary_visual` | ok | Caption: schematic of Corollary 1 + 2 |
| `rag_pipelines` | ok | Caption: P1/P2/P3 schematic |

**Critical:** **Run `scripts/regen_figures.py` before the final PDF build.** The `_find()` auto-discovery bug in `generate.py` (silently picks alphabetical-last, often a smoke/quick CSV) is the difference between cliff figures showing the real data and showing a flat line. Audit §1.3 (cited in insights §52) documents the failure mode.

---

## 6. Citation strategy (anchors per chapter)

Pulled from plan-v3 §9. **All verified.** Counts target ~30–50 references in the bibliography.

| Chapter | Primary citations |
|---------|--------------------|
| 1 (Intro) | Anthropic 2025 multi-agent blog (industry, labelled); Altman please/thank-you (industry, verify quote); Vaswani 2017 (attention); a verified LLM-inference-energy paper if one exists |
| 2.1 (Transformer) | Vaswani 2017; Radford GPT-2; Brown GPT-3; Touvron Llama-2; Kaplan 2020 scaling; Hoffmann 2022 Chinchilla |
| 2.2 (Scaling) | Same; plus Qwen-2.5 / DeepSeek-V3 papers (verify venue) |
| 2.3 (Cost) | Anthropic 2025; LLM-energy paper (verify); industry pricing notes (cited as industry) |
| 2.4 (Multi-agent) | AutoGen (ICLR workshop), MetaGPT (ICLR 2024), CAMEL (NeurIPS 2023), Reflexion (NeurIPS 2023), MemGPT (preprint), Generative Agents (UIST 2023) |
| 2.5 (Compression) | LLMLingua (EMNLP 2023), LongLLMLingua (ACL 2024), LLMLingua-2 (Findings ACL 2024), Selective Context (EMNLP 2023), RECOMP (ICLR 2024), Gist Tokens (NeurIPS 2023), AutoCompressor (EMNLP 2023), In-context Autoencoder (ICLR 2024), Compressive Transformers (ICLR 2020) |
| 2.6 (RAG/Long-ctx) | RAG (NeurIPS 2020), RAPTOR (ICLR 2024), GraphRAG (preprint), HippoRAG (NeurIPS 2024), Self-RAG (ICLR 2024), LongBench (ACL 2024), RULER (COLM 2024), Lost in the Middle (TACL 2024) |
| 2.7 (Privacy) | Recent RAG-privacy paper (verify); training-data extraction work (verify) |
| 4 (Benchmark) | HotpotQA (EMNLP 2018), MultiHopRAG (EMNLP 2024 Findings), 2WikiMultiHopQA (COLING 2020), GAIA (ICLR 2024), AgentBench (ICLR 2024) |
| 5 (Cliff + theorem) | Efron-Tibshirani bootstrap (1993); Holm 1979; Wilcoxon 1945; Anthropic 2025 (contrast) |
| 6 (RAG pipelines) | LongLLMLingua (ACL 2024) — the assumption this thesis challenges |
| 7 (Disclosure) | RAG-privacy work, training-data extraction; LLM memorisation papers |
| 8 (Discussion) | Re-cite the comparative anchors |

---

## 7. Order of writing (week-1 sprint plan)

**Do not write in chapter order.** Methods + results first; intro + background last (so the intro can foreshadow what you actually found, not what you hoped to find).

| Day | Chapters to draft | Why this order |
|-----|---------------------|----------------|
| 1 | Ch 3 (System) + Ch 4 (Benchmark) | Both are descriptive; warm up the writing pipeline; establishes terminology you'll use everywhere |
| 2 | Ch 5 §5.1–§5.5 (sweep + H1 + H2 + compounding-error model + predicted-vs-empirical) | Hardest chapter; do it while fresh |
| 3 | Ch 5 §5.6–§5.8 (Corollary 1 + frontier + mechanism) | Continuation; cliff-validation completes |
| 4 | Ch 6 (RAG) + Ch 7 (H4 + Corollary 2) | Shorter chapters; pace recovery |
| 5 | Ch 8 (Discussion + CAAC + Limitations + Future Work) | Now you know the full story; CAAC framing per ADR-007 |
| 6 | Ch 2 (Background / Related Work) | Written last on purpose: now you know exactly what the related work is *missing* relative to your results |
| 7 (morning) | Ch 1 (Intro) + Abstract | Written last because the contributions are now fully verified |
| 7 (afternoon) | Polish — terminology pass against CONTEXT.md; regenerate figures with `scripts/regen_figures.py`; final reference verification; reading-aloud pass; submit |

**If you slip by one day, drop Appendix C (expanded derivation) — Ch 5 §5.4 paragraph is sufficient.** Do not drop Appendix A (reproducibility) — it is rubric #5 evidence.

---

## 8. Pre-submission checklist (don't skip any line)

**Terminology / framing (CONTEXT.md + ADRs)**
- [ ] Every occurrence of "Theorem 1" in narrative prose changed to "compounding-error model" (codebase identifiers untouched)
- [ ] Every model-independence claim qualified with "within the calibrated regime"
- [ ] No bare "θ" — always θ_q or θ_info
- [ ] CAAC framed as operating-point selection, not Pareto dominance; 0/7 strict reported as expected, not a failure
- [ ] H3 framed as "predicted sign-flip did not appear; compress-first dominance" — not "failed hypothesis"
- [ ] H5 leads with Corollary 1 SUPPORTED; H6 leads with Corollary 2 SUPPORTED
- [ ] GPT-oss 120B mentioned and scoped out per ADR-006; not hidden
- [ ] No "NeurIPS / ICLR / publication" language anywhere in the manuscript

**Evidence integrity**
- [ ] All H1/H2 numbers from `h1_h2_final/`
- [ ] All H4 numbers from `h4_unbiased/` (not `h4_final/`)
- [ ] All CAAC numbers from `caac/summary_strict.json` (and the θ/N ablation from `caac_{theta,N}_*`)
- [ ] All Corollary 1 numbers from `h5_final/`
- [ ] All Corollary 2 numbers from `h6_final/` + `hotpotqa_sweep/`
- [ ] All frontier numbers from `frontier_qwen72b/` + `frontier_deepseekv4/`; `frontier_gptoss120b*` cited only as the out-of-regime diagnostic
- [ ] **No** numbers from smoke / micro / quick / diag / v3_quick / bt_* directories — the inventory agent has flagged these explicitly

**Figures**
- [ ] Every figure regenerated with `scripts/regen_figures.py` from the canonical CSV
- [ ] `predicted_vs_empirical` replaced with the predicted-τ\* band figure
- [ ] `caac_pareto` replaced with the region plot
- [ ] Every caption a complete sentence; every legend labelled; color-blind-safe palette
- [ ] PDF version of every figure embedded (vector); PNG fallback only if PDF generation fails

**Statistical rigour**
- [ ] Every hypothesis verdict block contains: point estimate, 95% bootstrap CI, paired-test p-value (Wilcoxon for H1/H2, paired-bootstrap for H4), effect size, sample size, Holm correction noted
- [ ] Bootstrap CIs computed at the workload level, not the cell level (per insights audit #10 fix)
- [ ] Holm correction across the relevant hypothesis family declared

**References**
- [ ] Every cited paper has a verified venue or is explicitly labelled "preprint" / "industry blog"
- [ ] AutoGen labelled as ICLR LLM-Agents Workshop, not main conference
- [ ] LLMLingua-2 labelled as Findings of ACL, not ACL main
- [ ] GraphRAG, MemGPT labelled as preprints
- [ ] Anthropic blog posts labelled as industry, not academic

**Language pass (rubric #9)**
- [ ] Each chapter read aloud once
- [ ] No undefined acronyms; first use of every acronym is spelled out
- [ ] No stacked relative clauses ≥ 3 levels deep
- [ ] Active voice in results sentences ("the model predicts...", not "is predicted by...")
- [ ] Final spell-check on the rendered PDF

**Layout pass (rubric #10)**
- [ ] Consistent font and line spacing
- [ ] New page per chapter
- [ ] Table captions above tables, figure captions below figures
- [ ] Units in column headers
- [ ] Page numbers
- [ ] Consistent citation format

**Final**
- [ ] Reproducibility package (Docker, model cards, data cards, release tag) ready
- [ ] Manuscript compiled to PDF
- [ ] Title on cover matches ADR-009; bibliography style matches Oulu LaTeX template; Foreword carries the AI-use declaration
- *Note (per grilling Q10):* Lauri reviews the final draft post-submission; no mid-sprint feedback gate. Mid-sprint informal feedback is welcome but not required to ship.

---

## 9. Verification — how to know the plan worked

The plan worked if the manuscript scores the maximum on every line of `Evaluation_Instructions.md`. A self-review pass before submission:

1. **Scope (3/3)** — Open Ch 1 outline + Ch 5 verdict tables. Three compressor families × three task families × multiple planner scales + RAG + disclosure visible at a glance? → 3.
2. **Challenge (3/3)** — Open Ch 5 §5.4 (model derivation) + §5.7 (frontier validation). Demanding theoretically + in implementation? → 3.
3. **Outlining (5/5)** — Open the TOC. Does every chapter have numbered subsections and a clear emphasis? → 5.
4. **Intro/SoTA (5/5)** — Read Ch 2. Does each subsection close with "what's missing"? → 5.
5. **Achievement of aims (5/5)** — Open Ch 1 contributions list and trace each to a chapter. C1 → Ch 4. C2 → Ch 5. C3 → Ch 6. C4 → Ch 7. All delivered (with C3 honestly reframed)? → 5.
6. **Evaluation of results (5/5)** — Spot-check three hypothesis verdict blocks at random. Each has point estimate, CI, p-value, effect size, interpretation, comparison-to-prior-work, significance? → 5.
7. **Significance (5/5)** — Read Ch 8 §8.4. Are practitioner and scientific significance both made explicit? → 5.
8. **Initiative (3/3)** — Already won by the work. → 3.
9. **Language (5/5)** — Read three random pages aloud. Impeccable + clear + revised? → 5.
10. **Layout (3/3)** — Spot-check three figures. Caption complete sentence + units in tables + readable font? → 3.

**Total: 42/42.** If any line scores < max, fix it and re-check.

The plan does not control rubric items #1, #2, #8 (those are won by the work already done). It controls items #3, #4, #5, #6, #7, #9, #10 — and each of those is addressed by a specific chapter / paragraph / pre-submission checklist item above.

---

## 10. What this plan does *not* do

- It does not write the thesis. The text on the page is what scores; this plan tells you what text to put there.
- It does not regenerate figures or rerun experiments. The CAAC sweep with CTR + per-family θ_q (ADR-007 action items #1–#3) is still on the punch-list; if it does not complete by submission day, the `summary_strict.json` already on disk is the canonical source (insights §55 confirmed it exists and is valid).
- It does not negotiate with the supervisor. Per grilling Q10, Lauri reviews the final draft post-submission rather than gating Ch 8 mid-sprint.

---

## 11. Decisions log (2026-05-29 thesis-PLAN grilling session)

Twelve forks in the plan's design tree were resolved before writing started. Each is reflected in the plan body above; this section is the durable, scannable summary.

| # | Fork | Resolution | Locked at |
|---|------|-----------|-----------|
| 1 | NeurIPS-quality content posture | **Keep ADRs 006/007/008 as-written.** Compounding-error MODEL (not Theorem 1), CAAC in Ch 8 as operating-point selection, GPT-oss as out-of-regime diagnostic. No formal proof. Honest framing wins rubric #6. | §3 terminology, §4 Ch 5/8 |
| 2 | Sprint length | **~7 days.** All three pending ADR action items (CAAC rerun, bootstrap CI, audit hygiene) are in-scope. | §7 writing order |
| 3 | Title scope | **Rename to "Distributed Memory Bus for Multi-Fragment LLM Workflows: Context Compression, the Coordination Cliff, and Privacy"**. Disclosure of deterministic-solver / single-LLM-call methodology promoted to Abstract and Ch 1 P5; §3.3 becomes descriptive. Captured in **ADR-009**. CONTEXT.md gets a "multi-fragment" entry. | Title line, §3 terminology, §4 Front matter / Ch 1 P5 / Ch 3 §3.1 §3.3 |
| 4 | Compressor count for H1/H2 canonical | **`h1_h2_v2` canonical with 4 compressors including truncation.** Lower-bound argument: any learned compressor must beat truncation. Headline numbers refreshed from `h1_h2_v2` on the writing pass. | §4 Ch 5 §5.1 |
| 5 | Energy / wasted-tokens citation | **Luccioni et al. (peer-reviewed inference-Wh) + Altman as labelled industry hook.** Rigorous anchor with the memorable hook the user asked for; rubric #4 protected. | §4 Ch 2.3 |
| 6 | Target reader pedagogy | **Engineering-MSc-holder without LLM background.** Ch 2.1 includes transformer schematic + worked complexity example; Ch 2.5 includes mandatory compressor-comparison table; jargon is defined on first use. | §4 Ch 2.1, Ch 2.5 |
| 7 | Frontier-validation weight | **Expand §5.7 to 2–3 pp** with subsection structure (per-model detail, GPT-oss out-of-regime diagnostic, significance paragraph). Rubric #7 leverage maximised on the strongest single finding. | §4 Ch 5 §5.7 |
| 8 | Memory-bus presentation | **Architecture figure + verbatim `curl` trace + audit-log excerpt in Appendix A.** Cheapest "this thing actually runs" evidence for C4 rubric-#5 delivery. | §4 Ch 3 §3.1 |
| 9 | Submission format | **Oulu ITEE LaTeX template.** Bibliography style + abstract format dictated by template; layout decisions resolved by structure. | §4 Front matter |
| 10 | Supervisor feedback timing | **No mid-sprint Lauri feedback gate.** Lauri reviews the final draft post-submission; the 7-day sprint produces the final manuscript. Pre-submission checklist line removed. | §8 Pre-submission checklist |
| 11 | H4 reader-bias surfacing | **Footnote in §7.3 verdict block + full §7.4 discussion.** Examiner cannot read past the verdict without seeing the asymmetry exists; rubric #6 protected. | §4 Ch 7 §7.3 |
| 12 | AI-usage declaration | **Subsection placeholder reserved in Foreword.** Exact wording verified against Oulu template before final submission. | §4 Front matter |

---

*End of plan.*
