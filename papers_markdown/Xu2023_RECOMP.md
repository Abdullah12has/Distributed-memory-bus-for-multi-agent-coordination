# RECOMP: Improving Retrieval-Augmented LMs with Compression and Selective Augmentation

- **Authors:** Fangyuan Xu, Weijia Shi, Eunsol Choi
- **Year:** 2023
- **Venue:** arXiv preprint (cs.CL)
- **ArXiv:** [2310.04408](https://arxiv.org/abs/2310.04408)

## Abstract

RECOMP proposes compressing retrieved documents into textual summaries before integration into language model inputs. The paper presents two compression approaches: extractive (selecting useful sentences from retrieved documents) and abstractive (synthesizing information across documents into concise summaries). Both compressors can return empty strings when documents lack relevance, enabling selective augmentation. The method achieves compression rates as low as 6% with minimal performance loss, significantly outperforming standard summarization models on language modeling and open-domain question answering tasks. The compressors demonstrate transferability across different language models.

## Key Contributions

1. **Dual compression strategies**: Extractive compressor (dual-encoder, Contriever-based, 110M params) selects useful sentences; abstractive compressor (T5-large, 775M params) synthesizes across documents.
2. **Selective augmentation**: Compressors output empty strings for irrelevant documents, avoiding the problem of prepending irrelevant retrieval results that confuse LMs.
3. **Symbolic distillation training**: Abstractive compressor trained via distillation from GPT-3.5-turbo generated summaries.
4. **Cross-model transferability**: Compressors trained with one LM can transfer to others.

## Methodology

**Extractive Compressor:**
- Dual-encoder initialized from Contriever (110M parameters)
- Computes query-sentence similarity via inner product
- Trained with contrastive learning: positives are sentences improving task performance, negatives are top-ranked sentences below a performance threshold

**Abstractive Compressor:**
- T5-large encoder-decoder (775M parameters)
- Training data created via symbolic distillation: GPT-3.5-turbo generates summaries with multiple prompt templates, best summary (maximizing end-task performance) is selected
- Outputs empty string when compression hurts performance vs. no-retrieval baseline

## Key Results

| Task | Compression Rate | Performance Impact |
|------|-----------------|-------------------|
| WikiText-103 (LM) | 25% tokens | Minimal PPL drop |
| Natural Questions | 5% tokens | -2 EM points |
| TriviaQA | 5% tokens | -3.7 EM points |
| HotpotQA | 11% tokens | -2.4 EM points |

- Oracle methods achieve 6% compression with strong performance
- Abstractive compressor outputs empty summaries for 4-24% of examples (selective augmentation)
- Transfer from GPT-2 to GPT2-XL and GPT-J succeeds; transfer to LLaMA-13B shows degradation

## Relevance to Thesis

RECOMP directly informs the thesis's pipeline design, particularly the P1 (compress-then-retrieve) and P2 (retrieve-then-compress) architectures tested in hypothesis H3. The extractive vs. abstractive compressor distinction maps to the thesis's hard (LLMLingua-2) vs. soft (ICAE) compression methods. RECOMP's selective augmentation concept (returning empty strings for irrelevant documents) is relevant to the memory bus's decision of when to compress vs. pass through. The compression rate benchmarks (5-25% of tokens with minimal loss) provide reference points for the thesis's compression ratio experiments in H1. The cross-model transferability finding supports the thesis's approach of training compressors independently from the downstream LLM.
