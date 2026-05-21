# Prompt Compression for Large Language Models: A Survey

- **Authors:** Zongqian Li, Yinhong Liu, Yixuan Su, Nigel Collier
- **Year:** 2024
- **Venue:** arXiv preprint (cs.CL)
- **ArXiv:** [2410.12388](https://arxiv.org/abs/2410.12388)

## Abstract

Leveraging large language models for complex natural language tasks typically requires long-form prompts that increase memory usage and inference costs. This survey comprehensively categorizes prompt compression techniques into hard prompt methods (operating in natural language) and soft prompt methods (using continuous representations). The authors examine compression mechanisms through four interpretive frameworks: attention optimization, Parameter-Efficient Fine-Tuning (PEFT), modality integration, and synthetic language. The survey also discusses downstream applications, current limitations, and future directions including encoder optimization and hybrid approaches.

## Key Contributions

1. **Comprehensive taxonomy**: Clear division into hard prompt methods (filtering, paraphrasing) and soft prompt methods (decoder-only, encoder-decoder).
2. **Four interpretive frameworks**: Attention optimization, PEFT, modality integration, and synthetic language perspectives for understanding compression mechanisms.
3. **Coverage of key methods**: SelectiveContext, LLMLingua (filtering); Nano-Capsulator (paraphrasing); CC, GIST, AutoCompressor (decoder-only soft); ICAE, 500xCompressor, xRAG, UniICL (encoder-decoder soft).
4. **Identification of open challenges and future directions**.

## Methodology (Survey Structure)

**Hard Prompt Methods** (maintain natural language):
- **Filtering** (SelectiveContext, LLMLingua): Remove redundant tokens using perplexity scores
- **Paraphrasing** (Nano-Capsulator): Summarize into concise natural language

**Soft Prompt Methods** (continuous token representations):
- **Decoder-only** (CC, GIST, AutoCompressor): Modify LLM attention mechanisms to compress within the model
- **Encoder-decoder** (ICAE, 500xCompressor, xRAG, UniICL): Use separate compression encoders to produce compact representations

**Four Interpretive Frameworks:**
1. **Attention optimization**: Compressed tokens attend to full input; subsequent tokens attend only to compressed tokens
2. **PEFT**: Soft methods resemble prompt/prefix tuning with trainable embeddings
3. **Modality integration**: Compressed text as a new modality parallel to vision-language architectures
4. **Synthetic language**: Compressed tokens as an "LLM-specific language"

## Key Results (Survey Findings)

**Current Limitations:**
- Fine-tuning risks catastrophic forgetting and overfitting
- Compression time often rivals original prompt encoding; gains appear primarily during generation
- Lack of evaluation against traditional attention optimization (sliding window, sparse attention)

**Future Directions:**
- Optimizing smaller compression encoders
- Combining hard and soft methods (hybrid approaches)
- Applying multimodal architecture insights (cross-attention mechanisms)
- Better benchmarks comparing compression vs. efficient attention

## Relevance to Thesis

This survey provides the taxonomic framework for positioning the thesis's compressor modules. The thesis uses both hard (LLMLingua-2 = filtering) and soft (ICAE = encoder-decoder) prompt compression methods, directly mapping to the survey's two main categories. The survey's identification of hybrid approaches as a future direction validates the thesis's design of multiple compressor backends (lingua2, filter, icae, icae-tag) that can be selected per workload. The ICAE method (In-context Autoencoder) covered in this survey is the basis for the thesis's soft-prompt compressor and its tag-preserving variant (H4). The survey's finding that compression time can rival encoding time motivates the thesis's end-to-end latency measurements in coordination scenarios.
