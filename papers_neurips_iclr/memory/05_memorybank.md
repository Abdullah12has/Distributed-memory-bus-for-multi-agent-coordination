# MemoryBank: Enhancing Large Language Models with Long-Term Memory

**Authors:** Wanjun Zhong, Lianghong Guo, Qiqi Gao, He Ye, Yanlin Wang

**Venue:** AAAI 2024

**arXiv:** [https://arxiv.org/abs/2305.10250](https://arxiv.org/abs/2305.10250)

---

## Abstract

Revolutionary advancements in Large Language Models have reshaped the landscape of AI. Despite this, a notable gap persists in endowing them with long-term memory capabilities. The paper introduces MemoryBank, a novel mechanism designed to equip LLMs with the ability to summon relevant memories, continually evolve through continuous memory updates, and comprehend and adapt to a user's personality. Inspired by the Ebbinghaus Forgetting Curve theory, MemoryBank incorporates a dynamic memory mechanism that mirrors human-like forgetting and reinforcement processes. The authors demonstrate the system through SiliconFriend, an LLM-based chatbot equipped with MemoryBank for long-term companionship, which shows strong capability for providing empathetic responses, recalling relevant memories, and understanding user personality.

---

## 1. Introduction

LLMs lack persistent memory across conversations, limiting applications requiring long-term interaction such as:
- Personal companionship and psychological counseling
- Secretarial assistance with user preferences
- Adaptive tutoring with learner modeling

MemoryBank addresses this by providing a psychologically-grounded memory mechanism that mimics human memory dynamics.

## 2. MemoryBank Architecture

### Three Pillars

#### 2.1 Memory Storage

Maintains multiple levels of information:

| Storage Component | Description |
|-------------------|-------------|
| Conversation records | Complete dialogue history |
| Daily event summaries | Synthesized summaries of each day's interactions |
| Global event summaries | High-level summaries across all interactions |
| User personality profiles | Dynamically updated understanding of user traits |

The system generates daily event summaries from conversation records and synthesizes them into comprehensive global summaries over time.

#### 2.2 Memory Retrieval

Employs a dual-tower dense retrieval model (similar to Dense Passage Retrieval):
- Pre-encodes conversation turns and event summaries as memory representations
- Indexes via FAISS for efficient similarity-based retrieval
- Queries are encoded using the same encoder for symmetric matching

#### 2.3 Memory Updating (Ebbinghaus Forgetting Curve)

Inspired by psychological memory theory, the system models memory decay:

**Forgetting Formula:**
```
R = e^(-t/S)
```

Where:
- R = retention strength (probability of recall)
- t = elapsed time since last access
- S = memory strength (stability)

**Update Rules:**
- When a memory is recalled (accessed): S increases by 1, t resets to 0
- Frequently accessed memories become more stable
- Rarely accessed memories gradually decay
- Memories below a threshold are deprioritized (not deleted)

## 3. SiliconFriend Implementation

### Two-Stage Development

**Stage 1: Psychological Tuning**
- Parameter-efficient tuning using LoRA (Low-Rank Adaptation)
- Training data: 38,000 psychological dialogue examples
- Configuration: LoRA rank=16, 3 training epochs, A100 GPUs
- Goal: Enable empathetic, psychologically-aware responses

**Stage 2: MemoryBank Integration**
- Connect tuned model to MemoryBank storage and retrieval
- Enable personality understanding from accumulated interactions
- Support context-aware responses using retrieved memories

### Supported LLM Backends
- ChatGPT (API-based)
- ChatGLM (open-source, bilingual)
- BELLE (open-source, Chinese-focused)

## 4. Experimental Evaluation

### Test Setup
- Synthetic memory storage spanning 10 days
- 15 virtual users across diverse topics
- 194 probing questions (97 English, 97 Chinese)

### Evaluation Metrics

| Metric | Description |
|--------|-------------|
| Memory Retrieval Accuracy | Binary: did the system retrieve a relevant memory? |
| Response Correctness | Three-level scale: wrong / partial / correct |
| Contextual Coherence | Natural connection between dialogue and retrieved memory |
| Model Ranking Score | Comparative ranking (s = 1/r where r in {1,2,3}) |

### Quantitative Results

| Language | Model | Retrieval Acc. | Correctness | Coherence | Ranking |
|----------|-------|---------------|-------------|-----------|---------|
| English | ChatGLM | 0.809 | 0.438 | 0.680 | 0.498 |
| English | BELLE | 0.814 | 0.479 | 0.582 | 0.517 |
| English | ChatGPT | 0.763 | 0.716 | 0.912 | 0.818 |
| Chinese | ChatGLM | 0.840 | 0.418 | 0.428 | 0.510 |
| Chinese | BELLE | 0.856 | 0.603 | 0.562 | 0.565 |
| Chinese | ChatGPT | 0.711 | 0.655 | 0.675 | 0.758 |

### Key Findings
- ChatGPT achieves highest coherence and ranking scores across both languages
- Open-source variants demonstrate strong retrieval accuracy (comparable or better than ChatGPT)
- ChatGPT's advantage is mainly in response quality, not memory retrieval
- Language-specific performance varies: ChatGLM/BELLE better at Chinese retrieval, ChatGPT better at English response quality

### Qualitative Analysis
- **Memory recall demonstrations**: System successfully retrieves relevant past conversations when prompted
- **Personality understanding**: Adapts response style based on accumulated user interaction patterns
- **Empathetic responses**: Psychological tuning enables emotionally appropriate responses

## 5. User Personality Modeling

MemoryBank constructs dynamic user profiles by:
1. Analyzing conversation patterns and topics
2. Identifying recurring preferences and interests
3. Detecting emotional states and communication styles
4. Updating personality understanding as new interactions occur

## 6. Related Work

- **Memory-augmented neural networks**: Neural Turing Machines, Memory Networks
- **Long-term dialogue systems**: Beyond Goldfish Memory, conversation summarization
- **Psychological AI**: Empathetic dialogue, personality modeling
- **Retrieval-augmented LLMs**: RAG, RETRO, knowledge-grounded dialogue

## 7. Limitations

- Forgetting curve parameters require tuning for different applications
- Retrieval accuracy is limited by the quality of memory embeddings
- User personality modeling is shallow compared to psychological assessments
- Evaluation is primarily on synthetic rather than real long-term users
- Memory storage grows linearly with interaction history

---

## Figure Descriptions

- **Figure 1:** MemoryBank architecture showing storage, retrieval, and updating components
- **Figure 2:** Ebbinghaus Forgetting Curve visualization showing memory decay over time
- **Figure 3:** SiliconFriend system architecture with LoRA tuning and MemoryBank integration
- **Figure 4:** Example dialogues showing memory recall and personality-adapted responses
- **Figure 5:** Retrieval accuracy comparison across models and languages

---

## Top 10 References

1. Brown, T., et al. (2020). Language models are few-shot learners (GPT-3). *NeurIPS*.
2. OpenAI (2022). ChatGPT: Optimizing language models for dialogue.
3. OpenAI (2023). GPT-4 technical report. *arXiv:2303.08774*.
4. Touvron, H., et al. (2023). LLaMA: Open and efficient foundation language models. *arXiv*.
5. Hu, E., et al. (2021). LoRA: Low-rank adaptation of large language models. *ICLR*.
6. Graves, A., et al. (2014). Neural Turing Machines. *arXiv*.
7. Karpukhin, V., et al. (2020). Dense passage retrieval for open-domain question answering. *EMNLP*.
8. Ebbinghaus, H. (1885/1964). Memory: A contribution to experimental psychology.
9. Xu, X., et al. (2021). Beyond goldfish memory: Long-term open-domain conversation. *ACL*.
10. Zeng, A., et al. (2022). GLM-130B: An open bilingual pre-trained model. *ICLR*.
