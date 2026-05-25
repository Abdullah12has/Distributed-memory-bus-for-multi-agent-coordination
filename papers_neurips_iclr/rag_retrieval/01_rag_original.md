# Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

- **Authors:** Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Kuttler, Mike Lewis, Wen-tau Yih, Tim Rocktaschel, Sebastian Riedel, Douwe Kiela
- **Venue:** NeurIPS 2020
- **ArXiv:** [2005.11401](https://arxiv.org/abs/2005.11401)
- **Submitted:** May 22, 2020; revised April 12, 2021

---

## Abstract

Large pre-trained language models have been shown to store factual knowledge in their parameters, and achieve state-of-the-art results when fine-tuned on downstream NLP tasks. However, their ability to access and precisely manipulate knowledge is still limited, and hence on knowledge-intensive tasks, their performance lags behind task-specific architectures. Additionally, providing provenance for their decisions and updating their world knowledge remain open research problems. Pre-trained models with a differentiable access mechanism to explicit non-parametric memory can overcome this issue, but have so far been only investigated for extractive downstream tasks. The authors explore a general-purpose fine-tuning recipe for retrieval-augmented generation (RAG) -- models which combine pre-trained parametric and non-parametric memories for language generation. RAG models are introduced where the parametric memory is a pre-trained seq2seq model and the non-parametric memory is a dense vector index of Wikipedia, accessed with a pre-trained neural retriever. Two RAG formulations are compared: one which conditions on the same retrieved passages across the whole generated sequence, and another which can use different passages per token. The models are fine-tuned and evaluated on a wide range of knowledge-intensive NLP tasks and set the state of the art on three open-domain QA tasks, outperforming parametric seq2seq models and task-specific retrieve-and-extract architectures. For language generation tasks, RAG models generate more specific, diverse and factual language than a state-of-the-art parametric-only seq2seq baseline.

---

## 1. Introduction

Pre-trained language models store factual knowledge in parameters but struggle with knowledge access and manipulation. The authors note that "hybrid models that combine parametric memory with non-parametric (i.e., retrieval-based) memories can address some of these issues because knowledge can be directly revised and expanded."

RAG brings retrieval-augmented capabilities to sequence-to-sequence models, leveraging pre-trained components without task-specific training. The approach enables knowledge updates through index replacement without retraining, providing interpretability advantages over purely parametric systems.

---

## 2. Methods

### 2.1 Models

The authors treat the retrieved documents as a latent variable. Two models are proposed that marginalize over retrieved documents in different ways to produce a distribution over generated text.

#### RAG-Sequence

Uses the same retrieved document to generate the complete sequence. The model marginalizes over retrieved documents across entire sequences:

$$p_{\text{RAG-Sequence}}(y|x) \approx \sum_{z \in \text{top-}k(p(\cdot|x))} p_\eta(z|x) \prod_i p_\theta(y_i|x, z, y_{1:i-1})$$

where $z$ represents the top-K documents, $p_\eta$ is the retriever, and $p_\theta$ is the generator.

#### RAG-Token

Allows different latent documents for each target token. This can be seen as a standard auto-regressive seq2seq generator with transition probabilities marginalized over documents:

$$p_{\text{RAG-Token}}(y|x) \approx \prod_i \sum_{z \in \text{top-}k(p(\cdot|x))} p_\eta(z|x) \cdot p_\theta(y_i|x, z, y_{1:i-1})$$

### 2.2 Retriever: DPR

Uses Dense Passage Retriever (DPR) with a bi-encoder architecture. Document encoder $\text{BERT}_d(z)$ and query encoder $\text{BERT}_q(x)$ produce dense representations:

$$p_\eta(z|x) \propto \exp\left(d(z)^\top q(x)\right)$$

enabling efficient Maximum Inner Product Search (MIPS) over 21M Wikipedia passages (100-word chunks from December 2018 dump).

### 2.3 Generator: BART

BART-large (400M parameters) serves as the seq2seq generator. The input $x$ and retrieved content $z$ are concatenated for processing.

### 2.4 Training

Joint end-to-end training optimizes negative marginal log-likelihood without direct document supervision. The document encoder remains frozen; only the query encoder and BART generator are fine-tuned.

### 2.5 Decoding

- **RAG-Token:** Uses standard beam search with marginalized transition probabilities.
- **RAG-Sequence:** Employs "Thorough Decoding" (additional forward passes ensuring complete marginalization) or "Fast Decoding" (approximates zero probability for ungenerated hypotheses).

---

## 3. Experiments

### 3.1 Open-Domain Question Answering

Evaluated on four benchmarks: Natural Questions, TriviaQA, WebQuestions, and CuratedTrec. Training uses top-5 or top-10 documents; test time uses dev-optimized K values.

### 3.2 Abstractive Question Answering

MS-MARCO NLG v2.1 dataset used without supplied passages to evaluate open-domain performance.

### 3.3 Jeopardy Question Generation

Novel task requiring generation of complex, factual questions from answer entities. Uses SearchQA splits (100K train, 14K dev, 27K test).

### 3.4 Fact Verification

FEVER task adapted for RAG, mapping class labels to single tokens without retrieval supervision, unlike most competing approaches.

---

## 4. Results

### 4.1 Open-Domain QA

| Model | NQ (EM) | TriviaQA (EM) | WebQ (EM) | CT (EM) |
|-------|---------|---------------|-----------|---------|
| T5-11B | 36.6 | -- | -- | -- |
| REALM | 40.4 | -- | 40.7 | 46.8 |
| DPR | 41.5 | 57.9 | 41.1 | 50.6 |
| RAG-Token | 44.1 | 55.2 | 45.5 | 50.0 |
| **RAG-Sequence** | **44.5** | **56.8** | **45.2** | **52.2** |

RAG achieves new state-of-the-art without specialized pre-training. RAG generates correct answers in 11.8% of cases on NQ where no document contains the answer verbatim, impossible for extractive models.

### 4.2 Abstractive Question Answering

RAG-Sequence outperforms BART baseline by 2.6 BLEU and 2.6 ROUGE-L on Open MS-MARCO. Qualitatively produces fewer hallucinations and more factually correct text.

### 4.3 Jeopardy Question Generation

| Model | Q-BLEU-1 | Human Factuality (%) | Human Specificity (%) |
|-------|----------|---------------------|-----------------------|
| BART | 19.7 | 7.1 | 16.8 |
| **RAG-Token** | **22.2** | **42.7** | **37.4** |

RAG-Token performs best, suggesting advantage in combining content from multiple documents. Analysis shows "parametric and non-parametric memories work together" -- retrieved documents guide generation while parametric knowledge completes sequences.

### 4.4 Fact Verification

FEVER 3-way classification: RAG achieves 72.5% label accuracy (vs. SotA 76.8% with gold evidence). Within 4.3% of pipeline approaches despite no retrieval supervision. Retrieved documents match gold evidence titles in 71% of top-1 and 90% of top-10 cases.

### 4.5 Additional Results

#### Generation Diversity

RAG-Sequence produces 83.5% distinct trigrams (vs. BART 70.7%) without diversity-promoting decoding.

#### Retrieval Ablations

Learned retrieval improves all tasks. BM25 baseline substantially underperforms dense retrieval on most tasks (except FEVER, which is entity-centric).

#### Index Hot-Swapping

RAG answers 70% correctly with 2016 Wikipedia for 2016 queries, 68% with 2018 Wikipedia for 2018 queries, demonstrating "knowledge can be easily updated at test time."

#### Effect of Retrieved Documents

Performance generally improves with more documents; RAG-Token peaks at 10 documents while RAG-Sequence continues improving to 50 documents.

---

## 5. Related Work

### Single-Task Retrieval

Previous work demonstrates retrieval benefits across QA, fact-checking, dialogue, translation, and language modeling individually.

### General-Purpose Architectures

BERT, GPT-2, BART, and T5 showed success with unified architectures. RAG extends this paradigm by integrating learned retrieval.

### Learned Retrieval

Recent neural approaches using pre-trained models optimize retrieval for downstream tasks via search, reinforcement learning, or latent variable methods. RAG shows a single architecture performs across multiple tasks.

### Memory-Based Architectures

Memory networks and fact embeddings provide precedent. RAG's advantage: "raw text rather than distributed representations... human-readable, lending a form of interpretability" and enabling dynamic updates.

### Retrieve-and-Edit Approaches

Similarities to retrieve-and-edit methods in translation and semantic parsing, though RAG emphasizes aggregating multiple documents rather than lightweight editing.

---

## 6. Discussion

RAG successfully combines parametric and non-parametric memory for generation. Key contributions include state-of-the-art open-domain QA, more factual generation, learned retrieval validation, and index hot-swapping capability. Future directions include joint pre-training of both components.

### Broader Impact

- **Positive:** Reduced hallucinations, grounding in real knowledge, improved interpretability and control.
- **Negative:** Wikipedia bias inherited, potential misuse for generating misleading content, job automation concerns. Mitigation: employ AI systems against disinformation and automated spam.

---

## Figures

- **Figure 1:** Overview of RAG architecture. Shows the query encoder producing a query representation, the retriever (DPR) performing MIPS over the document index to retrieve top-K documents, and the BART generator producing output conditioned on concatenated query and retrieved documents. Two variants illustrated: RAG-Sequence (same document for full sequence) and RAG-Token (different documents per token).

- **Figure 2:** Effect of number of retrieved documents on performance across tasks for both RAG-Sequence and RAG-Token models. RAG-Token peaks around 10 documents; RAG-Sequence continues improving up to 50.

---

## Implementation Details

- Training on 8 V100 GPUs
- 15-50 retrieved documents depending on task
- Specific beam sizes and decoding approaches per task type
- Built on Fairseq and HuggingFace Transformers
- 8-bit compression reduces document index memory from ~100GB to 36GB
- Total trainable parameters: 626M + 15.3B index values (non-trainable)

---

## Key References (Top 10 Most Cited)

1. Lewis et al. (2020) -- BART: Denoising sequence-to-sequence pre-training
2. Karpukhin et al. (2020) -- Dense Passage Retrieval for open-domain QA
3. Devlin et al. (2019) -- BERT: Pre-training of deep bidirectional transformers
4. Raffel et al. (2020) -- T5: Exploring the limits of transfer learning
5. Guu et al. (2020) -- REALM: Retrieval-augmented language model pre-training
6. Petroni et al. (2019) -- Language models as knowledge bases
7. Kwiatkowski et al. (2019) -- Natural Questions benchmark
8. Joshi et al. (2017) -- TriviaQA reading comprehension benchmark
9. Thorne et al. (2018) -- FEVER: Fact extraction and verification
10. Radford et al. (2019) -- Language models are unsupervised multitask learners (GPT-2)
