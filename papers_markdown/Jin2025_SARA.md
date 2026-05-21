# SARA: Selective and Adaptive Retrieval-Augmented Generation with Context Compression

- **Authors:** Yiqiao Jin, Kartik Sharma, Vineeth Rakesh, Yingtong Dou, Menghai Pan, Mahashweta Das, Srijan Kumar
- **Year:** 2025
- **Venue:** arXiv preprint (cs.CL)
- **ArXiv:** [2507.05633](https://arxiv.org/abs/2507.05633)

## Abstract

Retrieval-augmented generation extends LLMs with external knowledge but faces challenges of restricted effective context length and redundancy in retrieved documents. Pure compression approaches reduce input size but often discard fine-grained details essential for factual accuracy. SARA proposes a unified RAG framework that balances local precision and global knowledge coverage under tight context budgets. It combines natural-language text snippets with semantic compression vectors to jointly enhance context efficiency and answer correctness. Across 9 datasets and 5 open-source LLMs spanning 3 model families (Mistral, Llama, Gemma), SARA consistently improves answer relevance (+17.71), answer correctness (+13.72), and semantic similarity (+15.53).

## Key Contributions

1. **Dual-representation approach**: Combines fine-grained natural-language spans (preserving entities and numerical values) with compact semantic compression vectors (summarizing high-level semantics).
2. **Two-level context representation**: Text snippets for precision, compression vectors for coverage -- addressing the fundamental tension between detail preservation and efficient compression.
3. **Iterative evidence-selection module**: Uses compression vectors for dynamic reranking via embedding-based selection (minimizing query-evidence discrepancy) and conditional self-information (filtering redundancy).
4. **Extensive evaluation**: 9 datasets, 5 LLMs, 3 model families.

## Methodology

- **Text snippets**: Top-k passages retained as readable natural language for detail preservation
- **Compression vectors**: Remaining documents encoded via autoencoding objective (trained to reconstruct original text from compressed representations)
- **Mixed-format reasoning**: LLM reasons over both text and dense vector summaries
- **Evidence selection**: Two strategies -- (a) embedding-based: minimizes discrepancy between query and accumulated evidence in embedding space; (b) conditional self-information: measures novel information gain, filtering redundant content
- **Iterative refinement**: Progressive selection of contexts based on relevance and diversity

## Key Results

| Metric | Improvement (Mistral-7B) |
|--------|-------------------------|
| Answer Relevance | +17.71 |
| Answer Correctness | +13.72 |
| Semantic Similarity | +15.53 |

- TriviaQA: 24.5% F1 improvement over compression baselines under 512-token constraints
- Particularly strong on multi-hop reasoning tasks requiring factual precision

**Ablation findings:**
- Removing context reconstruction: largest drop (7-9 F1 points) -- confirms autoencoding training is essential
- Disabling compression: consistent declines, especially on lengthy noisy documents
- Removing reranking: modest but measurable drops

## Relevance to Thesis

SARA's dual-representation approach (text + compression vectors) directly parallels the thesis's design philosophy of combining hard prompt compression (LLMLingua-2 preserving key tokens) with soft prompt compression (ICAE producing dense representations). The iterative evidence-selection module is relevant to the thesis's P3 (joint) pipeline that combines retrieval and compression decisions. SARA's finding that removing context reconstruction causes the largest performance drop validates the thesis's investment in training the ICAE autoencoder. The 512-token context budget experiments map directly to the thesis's compression ratio sweeps in H1. SARA's success across multiple model families (Mistral, Llama, Gemma) supports the thesis's assumption that compression benefits generalize across LLM backends.
