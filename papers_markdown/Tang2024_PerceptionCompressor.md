# Perception Compressor: A Training-Free Prompt Compression Framework in Long Context Scenarios

- **Authors:** Jiwei Tang, Jin Xu, Tingwei Lu, Zhicheng Zhang, Yiming Zhao, Lin Hai, Hai-Tao Zheng
- **Year:** 2024
- **Venue:** NAACL 2025 Findings
- **ArXiv:** [2409.19272](https://arxiv.org/abs/2409.19272)

## Abstract

Large language models demonstrate exceptional capabilities but suffer from redundant information and sensitivity to key information positioning in extended contexts. Perception Compressor introduces a training-free approach to prompt compression featuring three components: a perception retriever that uses guiding questions to find relevant demonstrations, a dual-slope ratio allocator for dynamic compression parameter adjustment, and semi-guided iterative compression to preserve critical tokens while eliminating distracting ones. The method achieves state-of-the-art results on NaturalQuestions, LongBench, and MuSiQue benchmarks without requiring any model fine-tuning.

## Key Contributions

1. **Perception retriever**: Leverages guiding questions and instructions to identify the most relevant demonstrations/context segments before compression.
2. **Dual-slope ratio allocator**: Dynamically determines compression ratios per segment rather than using a uniform ratio, allocating more budget to information-dense sections.
3. **Semi-guided iterative compression**: Token-level compression that preserves critical tokens while removing distracting ones through an iterative refinement process.
4. **Training-free design**: No fine-tuning or additional training required, making it immediately deployable with any LLM.

## Methodology

- The perception retriever generates guiding questions from the input query and uses them to score and rank context segments by relevance
- The dual-slope ratio allocator assigns higher compression budgets to more relevant segments and lower budgets to less relevant ones, using a piecewise-linear allocation function
- Semi-guided iterative compression operates at the token level, using the LLM's own attention patterns to identify which tokens carry critical information
- The entire pipeline is training-free, relying on the base LLM's existing capabilities

## Key Results

- State-of-the-art performance on NaturalQuestions, LongBench, and MuSiQue benchmarks
- Outperforms prior training-free methods (LLMLingua, Selective Context) and matches or exceeds some trained methods
- Effective across varying context lengths and compression ratios
- Maintains performance even at high compression ratios in long-context scenarios

## Relevance to Thesis

Perception Compressor represents an alternative compression paradigm (training-free, retrieval-guided) to the trained compressors (LLMLingua-2, ICAE) used in the thesis. Its perception retriever concept parallels the P2 (retrieve-then-compress) pipeline design in the thesis memory bus, where retrieval precedes compression. The dual-slope ratio allocation strategy is relevant to hypothesis H1's investigation of how different compression ratios affect coordination quality -- adaptive per-segment ratios could mitigate the coordination cliff phenomenon studied in H2. The training-free nature also positions it as a useful reference point for evaluating whether training overhead (as in ICAE) provides sufficient benefit.
