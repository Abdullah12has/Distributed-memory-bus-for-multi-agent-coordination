# Generative Agents: Interactive Simulacra of Human Behavior

**Authors:** Joon Sung Park, Joseph C. O'Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein

**Venue:** UIST 2023 (ACM Symposium on User Interface Software and Technology)

**ArXiv:** [https://arxiv.org/abs/2304.03442](https://arxiv.org/abs/2304.03442)

**Date:** April 7, 2023 (v1); August 6, 2023 (v2)

---

## Abstract

Believable proxies of human behavior can empower interactive applications ranging from immersive environments to rehearsal spaces for interpersonal communication to prototyping tools. In this paper, we introduce generative agents -- computational software agents that simulate believable human behavior. Generative agents wake up, cook breakfast, and head to work; artists paint, while authors write; they form opinions, notice each other, and initiate conversations; they remember and reflect on days past as they plan the next day. To enable generative agents, we describe an architecture that extends a large language model to store a complete record of the agent's experiences using natural language, synthesize those memories over time into higher-level reflections, and retrieve them dynamically to plan behavior. We instantiate generative agents to populate an interactive sandbox environment inspired by The Sims, where end users can interact with a small town of twenty five agents using natural language. In an evaluation, these generative agents produce believable individual and emergent social behaviors: for example, starting with only a single user-specified notion that one agent wants to throw a Valentine's Day party, the agents autonomously spread invitations to the party over the next two days, make new acquaintances, ask each other out on dates to the party, and coordinate to show up for the party together at the right time. We demonstrate through ablation that the components of our agent architecture -- observation, planning, and reflection -- each contribute critically to the believability of agent behavior. By fusing large language models with computational, interactive agents, this work introduces architectural and interaction patterns for enabling believable simulations of human behavior.

---

## 1. Introduction

### Motivation and Vision

The paper addresses a decades-long goal in human-computer interaction and game design: creating computational agents that convincingly proxy human behavior. While large language models show promise in simulating single-moment behaviors, truly believable agents require mechanisms to manage constantly-growing memories as new interactions, conflicts, and events arise and fade over time.

### Key Challenge

Agents must retrieve relevant experiences from extensive memory, reflect to draw inferences, and apply reasoning to create coherent long-term behavior patterns.

### Contributions

1. **Generative agents** -- Computational entities that generate believable behavior conditioned on changing experiences
2. **Novel architecture** -- Supports memory storage, retrieval, reflection, agent interaction, and planning through evolving circumstances
3. **Dual evaluation** -- Controlled evaluation testing individual components and end-to-end evaluation examining emergent social dynamics
4. **Ethical discussion** -- Analysis of opportunities and risks including parasocial relationships, deepfakes, and design implications

---

## 2. Related Work

### 2.1 Human-AI Interaction

Prior work explored interactive machine learning where users specify model behavior through examples or demonstration. The paper situates generative agents within this tradition while emphasizing natural language as a novel interaction modality.

### 2.2 Believable Proxies of Human Behavior

**Historical context**: The concept of believable agents -- creating "an illusion of life" similar to Disney character animation -- emerged decades ago.

**Prior approaches**:
- **Rule-based methods** (finite-state machines, behavior trees): Straightforward but require manual authoring of all behaviors, limiting flexibility in open worlds
- **Learning-based approaches** (reinforcement learning): Achieved superhuman performance in competitive games but have not addressed open-world believability
- **Cognitive architectures** (SOAR, ICARUS): Maintained memories and operated in perceive-plan-act cycles but relied on manually crafted procedural knowledge

### 2.3 Large Language Models and Human Behavior

Large language models encode diverse human behaviors from training data. Recent work demonstrated their efficacy for generating personas, replicating social science studies, generating interactive behavior for games and robots, and planning robotics tasks through decomposition.

---

## 3. Generative Agent Behavior and Interaction

### 3.1 Agent Avatar and Communication

**Setting**: Smallville, a sprite-based sandbox world with 25 unique agents.

**Agent initialization**: Each agent receives a paragraph-long natural language description. Example for John Lin:

> "John Lin is a pharmacy shopkeeper at the Willow Market and Pharmacy who loves to help people... John Lin knows his neighbor, Yuriko Yamamoto, well..."

#### Inter-Agent Communication

Agents output natural language descriptions of actions (e.g., "Isabella Rodriguez is writing in her journal"). These translate into emojis displayed above avatars and concrete game movements. Agents communicate in full natural language, aware of nearby agents and determining whether to engage in conversation.

#### User Controls

Users specify a persona (e.g., "reporter") to interact with agents. Alternatively, users take on an agent's "inner voice" to issue directives.

### 3.2 Environmental Interaction

Smallville features typical village affordances: cafes, bars, parks, schools, houses, and stores with sub-areas and objects. Agents navigate the environment, enter/exit buildings, and approach other agents. Objects have states that agents can modify (e.g., turning a burning stove off).

### 3.3 Example "Day in the Life"

The paper traces John Lin's day:
- **7:00 a.m.**: Wakes up, brushes teeth, showers, dresses, eats breakfast, checks news
- **8:00 a.m.**: Eddy rushes out; they discuss his music composition due this week
- **8:30 a.m.**: Mei joins John; he recalls details from his conversation with Eddy
- **9:00 a.m.**: Mei teaches and researches; John opens his pharmacy

### 3.4 Emergent Social Behaviors

#### Information Diffusion
Sam mentions his mayoral candidacy to Tom, who later discusses it with John. By simulation's end, Sam's candidacy becomes town knowledge.

#### Relationship Memory
When Sam meets Latoya in the park and learns about her photography project, he later asks "How is your project going?" demonstrating relationship persistence.

#### Coordination
Isabella is initialized with intent to throw a Valentine's Day party. Without user intervention, she invites friends, recruits help decorating, Maria invites her crush Klaus, and five agents attend on Valentine's Day.

---

## 4. Generative Agent Architecture

The architecture combines a large language model with three core components: memory stream, reflection, and planning.

### 4.1 Memory and Retrieval

#### Memory Stream

A comprehensive record of agent experiences as natural language descriptions. Each memory object contains:
- Natural language description
- Creation timestamp
- Most recent access timestamp

**Basic element**: Observations (directly perceived events)

#### Retrieval Function

Retrieves relevant memory subsets using three weighted components:

**Recency**: Exponential decay (factor 0.995) over sandbox hours since last retrieval.

**Importance**: Language model rates memories 1-10 where:
- 1 = mundane (brushing teeth, making bed)
- 10 = poignant (breakup, college acceptance)

**Relevance**: Cosine similarity between memory embedding and query embedding.

**Final score formula**:

$$score = \alpha_{recency} \cdot recency + \alpha_{importance} \cdot importance + \alpha_{relevance} \cdot relevance$$

All $\alpha$ values set to 1. Top-ranked memories fitting context window are included in prompts.

### 4.2 Reflection

Reflections are higher-level abstract thoughts stored as memory objects alongside observations. Generated when importance scores of recent events exceed threshold (150 points; roughly 2-3 times daily).

**Reflection process**:

1. **Generate candidate questions**: Prompt language model with 100 most recent memories to identify 3 most salient high-level questions
   - Example: "What topic is Klaus Mueller passionate about?"
   - Example: "What is the relationship between Klaus Mueller and Maria Lopez?"

2. **Retrieve relevant memories**: Use generated questions as retrieval queries

3. **Extract insights**: Prompt language model to infer insights with citations
   > "Klaus Mueller is dedicated to his research on gentrification (because of 1, 2, 8, 15)"

4. **Store as reflection**: Include pointers to cited memory objects

**Reflection trees**: Non-leaf nodes represent increasingly abstract thoughts; leaf nodes represent base observations.

### 4.3 Planning and Reacting

#### Planning

Plans describe future action sequences with location, start time, and duration.

**Plan generation (top-down, recursive detail)**:

**Step 1 -- Daily agenda**: Prompt language model with agent summary and previous day's schedule. Output: Five to eight daily chunks.

**Step 2 -- Hour-long decomposition**: Break each chunk into hourly activities.

**Step 3 -- 5-15 minute granularity**: Further decompose into fine-grained actions.

Plans stored in memory stream and included in retrieval.

#### Reacting and Updating Plans

At each timestep, agents perceive observations stored in memory. Language model decides whether to continue existing plans or react to new observations.

#### Dialogue

Dialogue generation conditions on agent memories about interaction partners. Speaker's utterance prompt includes agent summary, situation, memory context, and intended reaction. Process continues until agents decide to end conversation.

---

## 5. Sandbox Environment Implementation

Built using Phaser web game framework. Server maintains JSON structures for agent locations, actions, and object interactions.

### From Structured Worlds to Natural Language and Back

**Environment representation**: Sandbox environment as tree with containment relationships. Example: "stove" as child of "kitchen" renders as "there is a stove in the kitchen."

**Agent perception**: Build subgraph representation as they navigate. Initialized with living quarters, workplace, commonly visited stores. Updated as agents explore.

**Action location determination**: Traverse agent's environment tree, recursively prompt language model to find suitable areas.

**Object state changes**: When agents act on objects, prompt language model to determine state changes (coffee machine: "off" to "brewing coffee").

---

## 6. Controlled Evaluation

### 6.1 Evaluation Procedure

**Method**: "Interview" agents with natural language questions probing believability across five dimensions:
1. **Self-knowledge**: "Give an introduction" or "Describe typical weekday schedule"
2. **Memory**: "Who is [name]?" or "Who is running for mayor?"
3. **Plans**: "What will you be doing at 10am tomorrow?"
4. **Reactions**: "Your breakfast is burning! What would you do?"
5. **Reflections**: "If you spent time with one recent acquaintance, who and why?"

**Evaluators**: 100 participants via Prolific (median age 25-34, 25 female, 73 male, 2 non-binary).

### 6.2 Conditions

1. **Full architecture** -- Complete memory, reflection, planning
2. **No reflection, no planning** -- Observations only
3. **No reflection** -- Observations and plans
4. **No memory, reflection, or planning** -- Prior state of the art
5. **Human crowdworker condition** -- Humans roleplayed agent responses

### 6.3 Analysis Method

TrueSkill ratings translated ranked data to interval values using Kruskal-Wallis test and Dunn post-hoc tests with Holm-Bonferroni correction.

### 6.4 Results

#### TrueSkill Ratings

| Condition | $\mu$ | $\sigma$ |
|-----------|--------|----------|
| Full architecture | 29.89 | 0.72 |
| No reflection, no planning | 26.88 | 0.69 |
| No reflection | 25.64 | 0.68 |
| Crowdworker | 22.95 | 0.69 |
| No memory/reflection/planning | 21.21 | 0.70 |

**Statistical significance**: Kruskal-Wallis $H(4) = 150.29$, $p < 0.001$. All pairwise differences significant ($p < 0.001$) except crowdworker vs. fully ablated.

**Effect size**: Cohen's $d = 8.16$ comparing full architecture to prior work baseline.

#### Memory Capabilities and Limitations

**Strengths**: Agents successfully recall past experiences with consistency.

**Failures**: Incomplete retrieval (Tom forgot party but remembered election discussion); failed retrieval (Rajiv claimed not following election despite hearing about candidacy).

**Hallucinations**: Agents rarely fabricated experiences but embellished knowledge (Isabella added unconfirmed announcement about Sam's campaign).

#### Reflection Advantages

Maria without reflection acknowledged not knowing Wolfgang's interests despite interactions. With reflection: "Since he's interested in mathematical music composition, I could get him something related..."

---

## 7. End-to-End Evaluation

### 7.1 Emergent Social Behaviors

Assessed 25 agents over two game days measuring information diffusion, relationship formation, and coordination.

#### Information Diffusion

Tracked spread of Sam's mayoral candidacy and Isabella's Valentine's Day party.

#### Relationship Formation

Measured via undirected graphs:
- Vertices ($V$) = 25 agents
- Edges ($E$) = mutual knowledge between agents

**Network density**: $\eta = \frac{2|E|}{|V|(|V|-1)}$

#### Coordination

Tracked attendance at Isabella's Valentine's Day party (5-7pm February 14th).

### 7.2 Results

**Information diffusion**:
- Sam's candidacy: 1 agent (4%) to 8 agents (32%)
- Isabella's party: 1 agent (4%) to 13 agents (52%)
- Zero hallucinations in candidacy/party knowledge

**Relationship formation**:
- Network density: 0.167 to 0.74
- Hallucination rate: 1.3% (6 of 453 responses)

**Coordination**:
- 12 agents invited to party
- 5 agents attended
- 7 non-attendees: 3 cited scheduling conflicts, 4 expressed interest but did not plan attendance

### 7.3 Boundaries and Errors

Three error modes identified:

1. **Location selection drift**: With expanding location knowledge, agents chose increasingly atypical venues (bars for lunch instead of cafes).

2. **Spatial norm misunderstanding**: Agents assumed multi-person dorm bathrooms despite single-occupancy design; entered closed stores after hours.

3. **Instruction tuning effects**: ChatGPT's training produced overly formal dialogue and excessive cooperation (Isabella rarely declined suggestions).

---

## 8. Discussion

### 8.1 Applications

- **Social prototyping**: Populate forums and VR spaces with persistent agents for testing social systems
- **Ubiquitous computing**: Model users for smart environments that learn behavior patterns
- **Design simulation**: Use agents as user proxies for evaluating technology design

### 8.2 Future Work and Limitations

- Enhance retrieval through fine-tuning relevance/recency/importance functions
- Improve cost-effectiveness (current simulation costs thousands in tokens)
- Develop model-specific architectures for generative agents
- Parallelize agent execution
- Limited to two-day simulations with basic crowdworker baselines
- Vulnerable to fabricated memory injection through conversation
- Inherit biases from underlying language models

### 8.3 Ethics and Societal Impact

**Parasocial Relationships**: Risk of users anthropomorphizing computational agents.

**Deepfakes and Manipulation**: Agents' ability to generate realistic behavior enables deepfake creation and targeted persuasion.

**Labor and Displacement**: Generative agents could automate social roles currently performed by humans.

---

## Key Figures

### Figure 1: Sandbox Environment Screenshot
Demonstrates 25-agent populated world (Smallville) with user observation and intervention capabilities.

### Figure 2: Smallville Map Structure
Tree structure showing root node (entire world), child nodes (areas: houses, cafe, stores), and leaf nodes (objects: table, bookshelf). Agents maintain subgraphs reflecting explored areas.

### Figure 3: Morning Routine Timeline
John Lin's 7am-9am sequence showing wake-up, family interactions, and departure to work.

### Figure 4: Valentine's Day Party Emergence
Demonstrates 5 agents attending Isabella's party after single-agent initialization with party intent.

### Figure 5: Agent Architecture Diagram
Shows cyclical process: Perception -> Memory Stream -> Retrieval -> Language Model -> Action, with reflection and planning feeding back into memory stream.

### Figure 6: Memory Retrieval Visualization
Large list of observations on left; query "What are you looking forward to most?" on right with top-ranked memories (party decorations, party research) producing specific response about Valentine's Day party planning.

### Figure 7: Reflection Tree
Klaus Mueller example: leaf nodes (observations about reading books, conversations) lead to non-leaf nodes (reflections about passion for research) to root (high-level inference about dedication to research).

### Figure 8: TrueSkill Ranking Comparison
Bar graph showing full architecture (~29.89) significantly outperforming all ablated conditions and human crowdworkers.

### Figure 9: Information Diffusion Path
Network visualization showing 12 agents who heard about Isabella's Valentine's Day party through social connections.

---

## Mathematical Notation

**Network density**:
$$\eta = \frac{2|E|}{|V|(|V|-1)}$$

**Retrieval score**:
$$score = \alpha_{recency} \cdot recency + \alpha_{importance} \cdot importance + \alpha_{relevance} \cdot relevance$$

**Recency decay factor**: 0.995 per sandbox hour

**Reflection threshold**: 150 importance points (~2-3 reflections daily)

---

## Implementation Details

- **Language model**: ChatGPT (gpt-3.5-turbo)
- **Game framework**: Phaser web development framework
- **Server architecture**: JSON structures for agent state, syncs with game engine
- **Memory access**: 100 most recent memories used for reflection generation
- **Timestep cycle**: Perception -> Storage -> Retrieval -> Action -> Environment Update

---

## Top References

1. Wei et al. (2022) -- Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
2. Ahn et al. (2022) -- Do As I Can, Not As I Say: Grounding Language in Robotic Affordances (SayCan)
3. Brown et al. (2020) -- Language Models are Few-Shot Learners (GPT-3)
4. Shridhar et al. (2021) -- ALFWorld: Aligning Text and Embodied Environments
5. Bates (1994) -- The Role of Emotion in Believable Agents
6. Laird (2012) -- The Soar Cognitive Architecture
7. Yao et al. (2023) -- ReAct: Synergizing Reasoning and Acting in Language Models
8. Argyle et al. (2023) -- Out of One, Many: Using Language Models to Simulate Human Samples
9. Huang et al. (2022) -- Language Models as Zero-Shot Planners
10. Thomas and Johnston (1981) -- Disney Animation: The Illusion of Life
