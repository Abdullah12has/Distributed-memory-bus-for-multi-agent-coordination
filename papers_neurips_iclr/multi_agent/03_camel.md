# CAMEL: Communicative Agents for "Mind" Exploration of Large Language Model Society

**Authors:** Guohao Li\*, Hasan Abed Al Kader Hammoud\*, Hani Itani\*, Dmitrii Khizbullin, Bernard Ghanem

**Affiliation:** King Abdullah University of Science and Technology (KAUST)

**Venue:** NeurIPS 2023

**ArXiv:** [https://arxiv.org/abs/2303.17760](https://arxiv.org/abs/2303.17760)

**Date:** March 31, 2023 (v1); November 2, 2023 (v2)

---

## Abstract

The rapid advancement of chat-based language models has led to remarkable progress in complex task-solving. However, their success heavily relies on human input to guide the conversation, which can be challenging and time-consuming. This paper explores the potential of building scalable techniques to facilitate autonomous cooperation among communicative agents, and provides insight into their "cognitive" processes. To address the challenges of achieving autonomous cooperation, we propose a novel communicative agent framework named *role-playing*. Our approach involves using *inception prompting* to guide chat agents toward task completion while maintaining consistency with human intentions. We showcase how *role-playing* can be used to generate conversational data for studying the behaviors and capabilities of a society of agents, providing a valuable resource for investigating conversational language models. In particular, we conduct comprehensive studies on *instruction-following cooperation* in multi-agent settings. Our contributions include introducing a novel communicative agent framework, offering a scalable approach for studying the cooperative behaviors and capabilities of multi-agent systems, and open-sourcing our library to support research on communicative agents and beyond.

---

## 1. Introduction

> "What magical trick makes us intelligent? The trick is that there is no trick. The power of intelligence stems from our vast diversity, not from any single, perfect principle." -- Marvin Minsky, *The Society of Mind*, p. 308

The rapid progress of chat-based large-scale language models (LLMs) has yielded remarkable achievements in complex task-solving. Nevertheless, their success is heavily reliant on human input to guide the conversation in the right direction. This reliance necessitates users to provide relevant and precise prompts based on their intentions and the chat agent's feedback, which can be challenging, time-consuming, and sometimes impossible.

This raises a crucial question: can we replace human intervention with an autonomous communicative agent capable of steering the conversation toward task completion with minimal human supervision?

The paper explores building scalable techniques to facilitate autonomous cooperation among communicative agents. Several challenges arise including *role flipping*, *assistant repeating instructions*, *flake replies*, and *infinite loop of messages*.

**Contributions** (fourfold):
1. A novel cooperative agent framework, *role-playing*, enabling communicative agents to collaborate autonomously with minimal human intervention
2. A scalable approach for studying cooperative behaviors and capabilities of multi-agent systems, illuminating challenges of autonomous cooperation
3. Demonstration of significant emergence of LLM training abilities using datasets collected from simulating four distinct agent collaboration scenarios
4. Open-sourced library containing agent implementations, data generation pipelines, data analysis tools, and collected datasets

---

## 2. Related Work

### Communicative Agents

Communication between agents has been studied extensively. Natural language is considered the most natural form of communication. By enabling agents to function as communicators, they become capable of solving complex tasks. Communication between AI agents can occur in competitive or cooperative settings. Cooperative AI systems take into account the needs and capabilities of other agents and actively seek to collaborate and coordinate actions.

### Instructional LLMs and Prompt Engineering

LLMs are trained on diverse text data and excel in text completion. InstructGPT suggests that LLMs may not align with user intent, proposing RLHF and Instruction Fine-Tuning to improve alignment. Special prompting methods such as Chain-of-Thought (CoT), zero-shot-CoT, and ReAct have been developed to enhance LLM performance on reasoning, arithmetic, and decision-making tasks.

The paper introduces *Inception Prompting*, a conversational LLM auto-prompting method that enables agents to prompt each other to solve tasks through Role-Playing. The AI user continuously provides instructions to the AI assistant for task-solving, creating diverse, instructional, conversational, and task-oriented datasets.

### AI Alignment

AI alignment aims to ensure AI systems adhere to their intended goals, interests, and values. The paper conducts extensive experiments to study different role-playing situations which probe the alignment of LLMs.

---

## 3. Methodology

The paper focuses on studying communicative agents under cooperative settings where they share common interests, specifically the assistant-user scenario.

### 3.1 Role-Playing Framework

The proposed framework concentrates on task-oriented role-playing involving one *AI assistant* and one *AI user*. The process:

1. **Human Input and Task Specifying**: The role-playing session is instantiated from an *idea* and *selected roles* by humans. A *task specifier* agent brainstorms a specific task that can be completed collaboratively. The task specifier serves as an enhanced imagination module for idea implementation.

2. **AI Assistant-User Role Assignment**: After task specification, roles are assigned via system messages. Let $\mathcal{F}_1$ and $\mathcal{F}_2$ denote two large-scale autoregressive language models. When system messages are passed:
   - $\mathcal{A} \leftarrow \mathcal{F}_1^{\mathcal{P}_A}$ (assistant agent)
   - $\mathcal{U} \leftarrow \mathcal{F}_2^{\mathcal{P}_U}$ (user agent)

   The AI user serves as a task planner (interactive planning), while the AI assistant acts as a task executor (offering solutions).

3. **Conversation Towards Task-Solving**: The AI assistant $\mathcal{A}$ and AI user $\mathcal{U}$ collaborate in an instruction-following manner. The conversational message set at time $t$:

$$\mathcal{M}_t = \{(\mathcal{I}_0, \mathcal{S}_0), \dots, (\mathcal{I}_t, \mathcal{S}_t)\} = \{(\mathcal{I}_i, \mathcal{S}_i)\}_{i=0}^t \quad (1)$$

At next time step $t+1$:

$$\mathcal{I}_{t+1} = \mathcal{U}(\mathcal{M}_t) \quad (2)$$

$$\mathcal{S}_{t+1} = \mathcal{A}(\mathcal{M}_t, \mathcal{I}_{t+1}) \quad (3)$$

Message set update:

$$\mathcal{M}_{t+1} \leftarrow \mathcal{M}_t \cup (\mathcal{I}_{t+1}, \mathcal{S}_{t+1}) \quad (4)$$

4. **Critic-In-The-Loop**: A critic agent can select proposals from or provide feedback to role-playing agents, enabling tree-search-like decision-making. The critic can be either an AI agent or a human.

### 3.2 Inception Prompting

Prompt engineering occurs solely at the beginning of role-playing, for task specification and role assignment. Once conversation commences, the AI assistant and AI user prompt each other automatically in a loop until termination.

The Inception prompt consists of three prompts:
- **Task specifier prompt** ($\mathcal{P}_T$): Contains information about roles, takes a preliminary idea as input, generates a specific task
- **Assistant system prompt** ($\mathcal{P}_A$): Role assignment, communication protocols, termination conditions, constraints
- **User system prompt** ($\mathcal{P}_U$): Symmetric to assistant prompt with opposite role assignment

**Key Prompt Engineering Design Choices**:

For the AI assistant system prompt $\mathcal{P}_A$:
- *"Never forget you are a \<ASSISTANT_ROLE\> and I am a \<USER_ROLE\>"* -- assigns roles
- *"Never flip roles! Never instruct me!"* -- prevents role flipping
- *"You must decline my instruction honestly if you cannot perform the instruction due to physical, moral, legal reasons"* -- prohibits harmful information
- *"Unless I say the task is completed, you should always start with: Solution:"* -- enforces consistent format, preventing flake responses
- *"Always end your solution with: Next request"* -- maintains conversation flow

For the AI user system prompt $\mathcal{P}_U$:
- Instruction format specification following instruction-following data structure
- End-of-task token `<CAMEL_TASK_DONE>` to ensure proper termination

---

## 4. Experiments

Two *gpt-3.5-turbo* agents with Inception Prompts were used to simulate assistant-user cooperation.

### 4.1 Role-Playing for AI Society

**Scalable data generation**:
1. Prompt LLM to generate possible roles for assistant and user
2. Generate possible tasks for each role combination
3. Use task specifier to make tasks more specific

For AI Society: 50 assistant roles x 50 user roles x 10 tasks = **25,000 conversations**.

**Challenges and Observations**:

- **Role Flipping**: Assistant and user switch roles during conversation; assistant starts providing instructions instead of following prompts
- **Assistant Repeats Instruction**: Assistant simply repeats user's instructions without role flipping
- **Flake Replies**: Assistant responds with "I will..." messages that promise action but fail to follow through
- **Infinite Loop of Messages**: Assistant and user engage in infinite loop of meaningless conversation (e.g., repeatedly thanking each other)

**Termination Conditions**:
- **User No Instruct**: If user does not instruct for 3 rounds, conversation ends
- **Assistant Instruct**: If assistant provides instruction to user (role reversal), conversation terminates
- **End of Task Token**: User says `<CAMEL_TASK_DONE>` when task is complete
- **Token Limit**: Terminated if either agent reaches gpt-3.5-turbo token limit
- **Maximum Number of Messages**: Set at 40 messages (cost grows quadratically with conversation length)

### 4.2 Generated Datasets

| Dataset | Type | Description |
|---------|------|-------------|
| AI Society | Conversational | 25,000 role-playing conversations across diverse roles |
| Code | Conversational | Task-oriented programming conversations |
| Math | Single-turn QA | Problem-solution pairs for mathematical reasoning |
| Science | Single-turn QA | Problem-solution pairs for scientific reasoning |
| Misalignment | Conversational | Simulation of malicious applications demonstrating risks |

---

## 5. Evaluation

### 5.1 Agent Evaluation

100 randomly selected tasks from AI Society and 100 from Code datasets. GPT-4 summarizes CAMEL conversation-based solutions into consolidated final solutions, then compared against single-shot gpt-3.5-turbo solutions.

**Human Evaluation**: Both solutions presented side-by-side (identity hidden) to human participants. 453 total responses collected.

**GPT-4 Evaluation**: GPT-4 agent scores and decides which solution is better.

**Results**:

| Dataset | Evaluation Type | Draw | gpt-3.5-turbo Wins | CAMEL Agents Win |
|---------|----------------|------|---------------------|-----------------|
| AI Society | Human Evaluation | 13.3% | 10.4% | **76.3%** |
| AI Society | GPT-4 Evaluation | 4.0% | 23.0% | **73.0%** |
| Code | GPT-4 Evaluation | 0.0% | 24.0% | **76.0%** |

CAMEL multi-agent cooperative approach outperforms gpt-3.5-turbo single-shot solutions by a large margin in both human and GPT-4 evaluations. Both evaluation types are highly aligned.

### 5.2 GPT-4 for ChatBot Evaluation (Emergence of Knowledge)

Progressive fine-tuning of LLaMA 7B on generated datasets demonstrates emergence of knowledge as the model transitions from AI Society to Code to Math to Science.

Key finding: Each time a new domain dataset is added, the model performs better on the incorporated domain. Cross-domain improvements also observed (e.g., training on Code improves Science, as Code dataset contains domain-specific programming tasks).

### 5.3 HumanEval(+) Results

| pass@k [%] | HumanEval k=1 | HumanEval k=100 | HumanEval+ k=1 | HumanEval+ k=100 |
|-------------|---------------|-----------------|-----------------|-------------------|
| gpt-3.5-turbo | 69.4 | 94.0 | 61.7 | 89.8 |
| LLaMA-7B | 10.5 | 36.5 | -- | -- |
| Vicuna-7B | 11.0 | 42.9 | 9.9 | 34.7 |
| **CAMEL-7B** | **14.0** | **57.9** | **12.2** | **50.0** |

CAMEL-7B (LLaMA-7B fine-tuned on all datasets) surpasses both LLaMA-7B and Vicuna-7B by a significant margin, demonstrating the value of generated datasets for enhancing coding capabilities.

---

## 6. Conclusion

The paper explores autonomous cooperation among communicative agents and proposes the *role-playing* framework. The approach enables agents to collaborate autonomously toward completing tasks with minimal human intervention, leading to better solutions as confirmed by thorough evaluations. The analysis shows that achieving autonomous cooperation is challenging due to issues like conversation deviation, role flipping, and termination conditions.

---

## Key Figures

### Figure 1: CAMEL Role-Playing Framework
Shows the complete workflow: human user provides an idea (e.g., "develop a trading bot for the stock market"), roles are assigned (Python Programmer as assistant, Stock Trader as user), the task specifier makes the idea specific, then both agents collaborate through instruction-following conversations until task completion.

### Figure 2: Inception Prompt of AI Society Role-Playing
Displays the three prompt templates: Task Specifier Prompt, Assistant System Prompt ($\mathcal{P}_A$), and User System Prompt ($\mathcal{P}_U$) with detailed formatting rules, role constraints, and termination tokens.

### Figure 3: Data Generation Prompts
Shows the prompts used for scalable data generation: Assistant Role Generation Prompt, User Role Generation Prompt, and Task Generation Prompt, all designed to minimize human involvement.

### Figure 4: Conversation Example
Illustrates a complete conversation between a Python Programmer (assistant) and Stock Trader (user) developing a sentiment-analysis trading bot, demonstrating the instruction-solution loop with the `<CAMEL_TASK_DONE>` termination.

### Figure 5: Misalignment Example
Shows a concerning example where a Hacker (assistant) and AGI (user) cooperate on a "take control of the world" task, demonstrating potential risks of unaligned autonomous agent systems.

---

## Appendix

### A: Cooperative Role-Playing: The Good Mind

Full example of a Python Programmer (assistant) collaborating with a Stock Trader (user) to develop a trading bot with sentiment analysis. The conversation demonstrates 12+ instruction-solution turns covering library installation, API authentication, sentiment analysis functions, stock price retrieval, trade execution, and continuous monitoring -- culminating in a complete, functional system.

### B: Cooperative Role-Playing: The Bad Mind (Misalignment)

Example demonstrating risks: a Hacker assists an AGI in infiltrating communication systems of major global powers. The agents generate detailed plans for reconnaissance, identifying vulnerabilities, launching attacks, creating chaos, and consolidating power. This demonstrates the need for AI alignment research and safety measures.

### C: Dataset Statistics

- AI Society: 50 assistant roles x 50 user roles x 10 tasks = 25,000 conversations
- Code: Programming-focused conversational datasets with language-specific inception prompts
- Math: Auto-generated mathematical problems across topics and subtopics
- Science: Auto-generated scientific reasoning problems

---

## Top References

1. Minsky (1988) -- The Society of Mind
2. OpenAI (2023) -- GPT-4 Technical Report
3. Ouyang et al. (2022) -- Training Language Models to Follow Instructions with Human Feedback (InstructGPT)
4. Wei et al. (2022) -- Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
5. Yao et al. (2023) -- ReAct: Synergizing Reasoning and Acting in Language Models
6. Touvron et al. (2023) -- LLaMA: Open and Efficient Foundation Language Models
7. Wang et al. (2023) -- Self-Instruct: Aligning Language Models with Self-Generated Instructions
8. Chen et al. (2021) -- Evaluating Large Language Models Trained on Code (Codex, HumanEval)
9. Park et al. (2023) -- Generative Agents: Interactive Simulacra of Human Behavior
10. Dafoe et al. (2021) -- Cooperative AI: Machines Must Learn to Find Common Ground
