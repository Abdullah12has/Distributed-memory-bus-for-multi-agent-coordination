# LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression

- **Authors:** Zhuoshi Pan, Qianhui Wu, Huiqiang Jiang, Menglin Xia, Xufang Luo, Jue Zhang, Qingwei Lin, Victor Ruhle, Yuqing Yang, Chin-Yew Lin, H. Vicky Zhao, Lili Qiu, Dongmei Zhang
- **Year:** 2024
- **Venue:** Findings of ACL 2024
- **ArXiv:** [2403.12968](https://arxiv.org/abs/2403.12968)

## Abstract

LLMLingua-2 addresses task-agnostic prompt compression through data distillation from large language models. The authors identify limitations in existing entropy-based approaches (which use causal LLMs and miss bidirectional context) and reformulate prompt compression as a token classification problem. Using GPT-4 to distill knowledge into an extractive text compression dataset, they train a Transformer encoder (XLM-RoBERTa-large or mBERT) to predict which tokens to preserve or discard. The method achieves 3x-6x faster compression than existing methods with end-to-end latency improvements of 1.6x-2.9x at 2x-5x compression ratios.

## Key Contributions

1. **Data distillation procedure**: Uses GPT-4 to create extractive compression labels from MeetingBank transcripts, with chunk-wise compression (512-token chunks) and quality control via Variation Rate and Alignment Gap metrics.
2. **Token classification formulation**: Reframes compression as binary classification (preserve/discard) rather than entropy-based selection, ensuring faithfulness to original content.
3. **Bidirectional context**: Employs Transformer encoders that capture full bidirectional context, unlike prior causal-LM-based methods.
4. **Extractive text compression dataset**: A new resource for training compression models.

## Methodology

- GPT-4 generates compression labels with instructions to "ONLY remove unimportant words" (no reordering, changing, or adding content)
- Quality control filters: top 5% by Variation Rate (new words) and top 10% by Alignment Gap (poor annotations) are removed
- XLM-RoBERTa-large or mBERT serves as the compression encoder with a linear classification head
- Token-level binary predictions at inference, with configurable compression ratio

## Key Results

| Benchmark | Metric | Score | vs. Original |
|-----------|--------|-------|-------------|
| MeetingBank QA | Exact Match | 86.92 | 87.75 |
| MeetingBank Summary | ROUGE-1 | 48.64 | 47.28 |
| GSM8K | EM | 79.08 | 79.08 |
| BBH | EM | 70.02 | 70.07 |
| LongBench (5x) | Average | 39.1 | -- |

- Compression model is 3x-6x faster than baselines
- End-to-end latency improvement: 1.6x-2.9x
- GPU memory reduced 8x compared to LLaMA-2-7B baselines
- Average compression ratio in training data: 2.57x

## Relevance to Thesis

LLMLingua-2 is a core component of the thesis memory bus system, serving as the primary "hard prompt" compressor in the `lingua2` compressor module. Its token-classification approach directly informs hypothesis H1 (compression vs. coordination quality tradeoff) and provides the baseline compression method against which ICAE soft-prompt approaches are compared. The method's task-agnostic nature makes it suitable for the diverse workload families (fact aggregation, multi-step retrieval) in the C1 benchmark. Its speed advantage is critical for the real-time coordination scenarios evaluated in H2 (coordination cliff detection).
