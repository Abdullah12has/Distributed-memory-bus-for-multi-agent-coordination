# AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation

**Authors:** Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Beibin Li, Erkang Zhu, Li Jiang, Xiaoyun Zhang, Shaokun Zhang, Jiale Liu, Ahmed Hassan Awadallah, Ryen W. White, Doug Burger, Chi Wang

**Venue:** ICLR 2024

**ArXiv:** [https://arxiv.org/abs/2308.08155](https://arxiv.org/abs/2308.08155)

**Date:** August 16, 2023 (v1); October 3, 2023 (v2)

---

## Abstract

AutoGen is an open-source framework that allows developers to build LLM applications via multiple agents that can converse with each other to accomplish tasks. AutoGen agents are customizable, conversable, and can operate in various modes that employ combinations of LLMs, human inputs, and tools. Using AutoGen, developers can also flexibly define agent interaction behaviors. Both natural language and computer code can be used to program flexible conversation patterns for different applications. AutoGen serves as a generic infrastructure to build diverse applications of various complexities and LLM capacities. Empirical studies demonstrate the effectiveness of the framework in many example applications, with domains ranging from mathematics, coding, question answering, operations research, online decision-making, entertainment, etc.

---

## 1. Introduction

The paper addresses a fundamental question: how can developers build LLM applications spanning diverse domains and complexities using multi-agent approaches? Three key insights motivate this work:

1. Chat-optimized LLMs can incorporate feedback and cooperate through conversations
2. Single LLMs exhibit broad capabilities that can be combined modularly across differently configured agents
3. Complex tasks benefit from decomposition into simpler subtasks

The framework addresses two critical design questions:
- How to design capable, reusable, customizable agents for multi-agent collaboration
- How to provide unified interfaces accommodating diverse agent conversation patterns

---

## 2. The AutoGen Framework

### 2.1 Conversable Agents

A conversable agent is an entity with a specific role that can pass messages to send and receive information to and from other conversable agents. Agents maintain internal context from sent/received messages and possess configurable capabilities.

#### Agent Capabilities

**LLM-backed agents** exploit advanced LLM capabilities including role playing, state inference, feedback provision, and coding through novel prompting techniques. Enhanced inference features include result caching, error handling, and message templating.

**Human-backed agents** enable human participation through configurable involvement levels. The default UserProxyAgent solicits human inputs at specified conversation rounds with options to skip input.

**Tool-backed agents** execute tools via code execution or function calls. The UserProxyAgent can execute code suggested by LLMs or make LLM-suggested function calls.

#### Agent Customization

The ConversableAgent class provides the highest-level abstraction. Pre-configured subclasses include:
- **AssistantAgent**: Acts as AI assistant (LLM-backed)
- **UserProxyAgent**: Solicits human input or executes code/function calls (human/tool-backed)

### 2.2 Conversation Programming

Conversation programming centers on two concepts: computation (agent actions generating responses) and control flow (sequences/conditions for computations).

#### Design Patterns

**Unified interfaces and auto-reply mechanisms**: Agents possess unified conversation interfaces including `send`/`receive` functions and `generate_reply` functions. The auto-reply mechanism invokes `generate_reply` automatically when messages arrive unless termination conditions are met. This creates a decentralized, modular, and unified way to define the workflow.

**Control through programming and natural language fusion**:

1. **Natural-language control**: LLM-backed agents receive prompts directing conversation flow
2. **Programming-language control**: Python code specifies termination conditions, human input modes, and execution logic
3. **Control transitions**: Flexible switching between natural language and code control

#### Dynamic Conversation Patterns

AutoGen supports both static and dynamic conversation flows:
- **Customized generate_reply**: Agents hold current conversations while invoking others based on message content
- **Function calls**: LLMs decide whether to call functions based on conversation status
- **GroupChatManager**: Dynamically selects speakers and broadcasts responses to agents

---

## 3. Applications of AutoGen

### A1: Math Problem Solving

Three scenarios demonstrate AutoGen's flexibility:

**Scenario 1 -- Autonomous Problem Solving**: AutoGen achieves 69.48% accuracy on the entire MATH dataset compared to GPT-4's 55.18%, outperforming alternatives including ChatGPT+Code Interpreter and ChatGPT+Plugin.

**Scenario 2 -- Human-in-the-loop**: Developers enable human feedback by setting `human_input_mode='ALWAYS'` in UserProxyAgent, allowing humans to provide hints during problem-solving.

**Scenario 3 -- Multi-user Collaboration**: AutoGen supports multiple human users (student and expert) collaborating simultaneously. When the assistant cannot solve problems satisfactorily, it automatically invokes an `ask_for_expert` function via GPT's function_call feature.

### A2: Retrieval-Augmented Code Generation and Question Answering

The Retrieval-augmented Chat system extends built-in agents with vector database capabilities using Chroma and SentenceTransformers.

**Workflow**:
1. Retrieval-augmented User Proxy retrieves document chunks based on embedding similarity
2. Assistant generates code/answers based on question and context
3. If context insufficient, LLM replies "UPDATE CONTEXT" triggering new retrieval
4. User Proxy executes code and provides feedback

**Scenario 1**: On the Natural Questions dataset, the system achieves F1 score of 23.40% (with interactive retrieval showing ~19.4% of questions trigger "Update Context" operations).

**Scenario 2**: Retrieval-augmented Chat successfully generates code using Spark-related APIs from FLAML (added December 2022), which GPT-4 was not trained on.

### A3: Decision Making in Text World Environments

The system solves ALFWorld tasks using two designs:

**Two-agent design**: Assistant generates plans; Executor performs actions and reports feedback.

**Three-agent design**: Adds a grounding agent providing commonsense knowledge like "You must find and take the object before examining it." This design achieves a 15% performance gain on average over the two-agent approach.

### A4: Multi-Agent Coding

Based on OptiGuide, the workflow involves:
- **Commander**: Coordinates between agents
- **Writer**: Crafts code
- **Safeguard**: Checks code safety

Using AutoGen, core workflow code was reduced from over 430 lines to 100 lines. Multi-agent approach boosts F-1 score identifying unsafe code by 8% (GPT-4) and 35% (GPT-3.5-turbo).

### A5: Dynamic Group Chat

GroupChatManager dynamically selects speakers using role-play style prompts. In pilot studies on 12 manually crafted complex tasks, role-play prompts led to higher success rate and fewer LLM calls compared to task-based prompts.

### A6: Conversational Chess

Features customizable agents supporting AI-AI, AI-human, and human-human modes. A board agent validates moves against standard rules, maintaining game integrity. Without board agent enforcement, relying only on prompts caused illegitimate moves and game disruptions.

---

## 4. Discussion

AutoGen offers numerous benefits:
- **Improved performance**: Exceeds state-of-the-art approaches
- **Reduced development effort**: Significantly decreases required code
- **Flexibility**: Enables dynamic rather than fixed interaction patterns
- **Modularity**: Separate agent development, testing, and maintenance

### Ethical Considerations

**Privacy and Data Protection**: User data and conversations require appropriate protective measures.

**Bias and Fairness**: LLMs exhibit training data biases requiring mitigation and fairness awareness.

**Accountability and Transparency**: Multi-agent decision-making demands clear accountability mechanisms so users understand reasoning processes.

**Trust and Reliance**: Clear communication about system capabilities and limitations proves essential.

**Unintended Consequences**: Code execution and function calls pose risks requiring appropriate safeguards.

---

## Key Figures

### Figure 1: AutoGen Agent Architecture
Shows the ConversableAgent as the base class with LLM-backed, human-backed, and tool-backed capabilities. AssistantAgent and UserProxyAgent are pre-configured subclasses.

### Figure 2: Conversation Programming Patterns
Illustrates static two-agent conversations, dynamic multi-agent group chats, and hierarchical conversation patterns with nested agent interactions.

### Figure 3: Application Examples
Demonstrates six diverse applications (A1-A6) showing different agent topologies and conversation patterns for math problem solving, retrieval-augmented QA, ALFWorld decision-making, multi-agent coding, group chat, and chess.

---

## Key Tables

### Table 1: Comparison with Multi-Agent Systems

| Aspect | AutoGen | Multi-Agent Debate | CAMEL | BabyAGI | MetaGPT |
|--------|---------|-------------------|-------|---------|---------|
| Infrastructure | Yes | No | Yes | No | No |
| Flexible conversation patterns | Yes | No | No | No | No |
| Execution-capable | Yes | No | No | No | Yes |
| Human involvement | Yes | No | No | No | No |

### Table 2: Math Problem Solving Results (MATH Dataset)

| Method | Accuracy |
|--------|----------|
| AutoGen | 69.48% |
| GPT-4 (vanilla) | 55.18% |
| ChatGPT + Code Interpreter | Lower |
| ChatGPT + Plugin | Lower |
| LangChain ReAct | Lower |
| Multi-Agent Debate | Lower |

---

## Appendix

### A: Related Work

**Single-Agent Systems**: AutoGPT, ChatGPT+, LangChain Agents, Transformers Agent -- all follow single-agent paradigms without native multi-agent collaboration.

**Multi-Agent Systems**: BabyAGI (predefined communication order), CAMEL (static role-playing patterns), Multi-Agent Debate (divergent thinking), MetaGPT (specialized for software development).

### B: General Guidelines for Using AutoGen

1. Use built-in agents first (AssistantAgent and UserProxyAgent)
2. Start with simple topologies (two-agent or group chat)
3. Reuse built-in reply methods before custom implementations
4. Begin with humans in the loop (`human_input_mode='ALWAYS'`)
5. Consider complementary libraries (LangChain, LlamaIndex)

### C: Future Work Directions

- **Designing optimal multi-agent workflows**: Determining ideal agent counts, role assignments, capabilities
- **Creating highly capable agents**: Application-specific agents with diverse skill sets
- **Enabling scale, safety, and human agency**: Debugging complexity, safety considerations, fail-safes

---

## Top References

1. Yao et al. (2023) -- ReAct: Synergizing Reasoning and Acting in Language Models
2. Park et al. (2023) -- Generative Agents: Interactive Simulacra of Human Behavior
3. Li et al. (2023) -- CAMEL: Communicative Agents for Mind Exploration
4. Hong et al. (2023) -- MetaGPT: Meta Programming for Multi-Agent Collaboration
5. Liang et al. (2023) -- Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate
6. Schick et al. (2023) -- Toolformer: Language Models Can Teach Themselves to Use Tools
7. Shen et al. (2023) -- HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face
8. Shinn et al. (2023) -- Reflexion: Language Agents with Verbal Reinforcement Learning
9. Wei et al. (2022) -- Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
10. OpenAI (2023) -- GPT-4 Technical Report
