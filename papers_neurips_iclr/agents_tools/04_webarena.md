# WebArena: A Realistic Web Environment for Building Autonomous Agents

**Authors:** Shuyan Zhou, Frank F. Xu, Hao Zhu, Xuhui Zhou, Robert Lo, Abishek Sridhar, Xianyi Cheng, Tianyue Ou, Yonatan Bisk, Daniel Fried, Uri Alon, Graham Neubig

**Venue:** ICLR 2024

**arXiv:** [https://arxiv.org/abs/2307.13854](https://arxiv.org/abs/2307.13854)

---

## Abstract

With advances in generative AI, there is now potential for autonomous agents to manage daily digital tasks for humans. This paper builds an environment for language-guided agents that is highly realistic and reproducible. Specifically, the authors design an environment with fully functional websites from four common domains -- e-commerce, social forum discussions, collaborative software development, and content management. The environment is enriched with tools and knowledge resources to facilitate human-like task solving. The authors also release a set of benchmark tasks focusing on evaluating functional correctness of task completions. The best GPT-4-based agent achieves only a 14.41% end-to-end task success rate, significantly below the human performance of 78.24%, highlighting the challenges in building capable web agents.

---

## 1. Introduction

WebArena addresses limitations of existing web agent benchmarks that either use simplified environments (MiniWoB++) or static datasets (Mind2Web). It provides a standalone, self-hosted web environment with fully functional websites for evaluating autonomous agents on realistic tasks.

## 2. Environment Architecture

### Self-Hosted Web Applications

| Domain | Application | Data Scale |
|--------|------------|------------|
| E-commerce | OneStopShop | ~90,000 products, 300+ categories |
| Social Forum | Reddit-like (Postmill) | 95 subreddits, 661,781 users |
| Collaborative Dev | GitLab | 300 repositories |
| Content Management | Adobe Magento Admin | Full store management |

Additional utilities: map, calculator, scratchpad, Wikipedia knowledge base.

### Observation Space

- Raw HTML DOM trees
- Screenshots (pixel-based RGB arrays)
- Accessibility trees (structured, compact DOM subset)
- **Multi-tab browsing support** (first web environment with this feature)

### Action Space

| Action Type | Description |
|-------------|-------------|
| Element Operations | click, hover, type, key combinations, scroll |
| Tab Management | new_tab, tab_focus, close_tab |
| Navigation | goto URL, go_back, go_forward |
| Completion | stop with answer |

Elements can be referenced by coordinates or unique IDs, transforming selection into an n-way classification problem.

### User Role Simulation

Distinct profiles across platforms:
- **E-commerce**: Customer with 35+ orders over two years
- **GitLab**: Maintainer of popular and personal projects
- **Reddit**: Active participant with numerous posts
- **CMS**: Shop owner with full read-write access

## 3. Benchmark Suite

### Task Composition
- **Total**: 812 instantiated intents from 241 templates
- **Average instantiations**: 3.3 examples per template
- **Task categories**:
  1. **Information-seeking**: Textual responses requiring multi-page navigation
  2. **Site navigation**: Locating specific information via search/links
  3. **Content & configuration**: Creating, revising, or modifying web content

### Evaluation Metrics

**Information-Seeking Tasks (r_info):**
- `exact_match`: Identical string matching
- `must_include`: Presence of required keywords
- `fuzzy_match`: GPT-4 semantic equivalence evaluation

**Navigation & Content Tasks (r_prog):**
- Programmatic validation through database queries, API calls, JavaScript selectors
- Keyword verification in retrieved content

### Human Baseline

Five CS graduate students completed 170 sampled tasks:
- **Overall success rate**: 78.24%
- **Information-seeking**: 74.68%
- **Other categories**: 81.32%
- **Average completion time**: 110 seconds per task

## 4. Baseline Agents and Results

### Models Tested
- GPT-4-0613
- GPT-3.5-turbo-16k-0613
- text-bison-001

### Results

| Model | Strategy | Success Rate | Achievable Rate | Unachievable Detection |
|-------|----------|-------------|----------------|----------------------|
| GPT-4 | CoT + UA hint | 11.70% | 8.63% | 77.78% |
| GPT-4 | CoT (no hint) | **14.41%** | 13.02% | 44.44% |
| GPT-3.5 | CoT + UA hint | 8.75% | 6.44% | 58.33% |
| text-bison | CoT + UA hint | 5.05% | 4.00% | 27.78% |
| **Human** | - | **78.24%** | **77.30%** | **100.00%** |

### Key Findings

**Early Stopping Problem:** GPT-4 incorrectly identified 54.9% of feasible tasks as impossible when given the unachievable task hint. Removing this instruction improved overall performance to 14.41%.

**Consistency Issues:** GPT-4 achieved 100% success on only 4 of 61 templates. Models struggled with task variations from identical templates.

**Error Patterns:**
- 50% of human failures: misinterpretation, incomplete answers/execution
- Common agent failures: observation bias, interpretation errors, lack of error recovery

## 5. Comparison to Existing Benchmarks

| Benchmark | Dynamic | Realistic | Diverse Tasks | Functional Eval |
|-----------|---------|-----------|---------------|----------------|
| Mind2Web | No | Yes | Yes | No |
| MiniWoB++ | Yes | No | No | Yes |
| WebShop | Yes | No | No | Yes |
| ALFRED | Yes | No | No | Yes |
| **WebArena** | **Yes** | **Yes** | **Yes** | **Yes** |

WebArena uniquely combines all four desirable properties.

## 6. Technical Implementation

### Reproducibility
- Docker containerization with self-contained databases
- No external volume dependencies
- Deterministic environment reset to initial state
- Pre-cached user cookies for role-based access

## 7. Limitations and Future Directions

1. Current LLMs lack active exploration and failure recovery
2. Models inconsistently handle task variations
3. Limited hierarchical planning and state tracking
4. Potential benefits from memory-augmented approaches and program synthesis

---

## Figure Descriptions

- **Figure 1:** Overview of WebArena showing the four web applications, utility tools, and knowledge resources
- **Figure 2:** Examples of tasks across different categories (information-seeking, navigation, content management)
- **Figure 3:** Agent architecture showing observation processing and action generation pipeline
- **Figure 4:** Consistency analysis across task template instantiations
- **Figure 5:** Error analysis breakdown for GPT-4 agent

---

## Top 10 References

1. Anderson, P., et al. (2018). Vision-and-language navigation: Interpreting visually-grounded navigation instructions. *CVPR*.
2. Shi, T., et al. (2017). World of Bits: An open-domain platform for web-based agents. *ICML*.
3. Liu, E., et al. (2018). Reinforcement learning on web interfaces using workflow-guided exploration. *ICLR* (MiniWoB++).
4. Yao, S., et al. (2022). WebShop: Towards scalable real-world web interaction. *NeurIPS*.
5. Shridhar, M., et al. (2020). ALFRED: A benchmark for interpreting grounded instructions. *CVPR*.
6. Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning. *NeurIPS*.
7. Deng, X., et al. (2023). Mind2Web: Towards a generalist agent for the web. *NeurIPS*.
8. OpenAI (2023). GPT-4 technical report. *arXiv:2303.08774*.
9. Nakano, R., et al. (2021). WebGPT: Browser-assisted question answering. *arXiv*.
10. Zhou, S., et al. (2022). Hierarchical control of situated agents through natural language. *arXiv*.
