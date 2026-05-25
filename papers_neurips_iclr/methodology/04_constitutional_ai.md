# Constitutional AI: Harmlessness from AI Feedback

**Authors:** Yuntao Bai, Saurav Kadavath, Sandipan Kundu, Amanda Askell, Jackson Kernion, Andy Jones, Anna Chen, Anna Goldie, Azalia Mirhoseini, Cameron McKinnon, Carol Chen, Catherine Olsson, Christopher Olah, Danny Hernandez, Dawn Drain, Deep Ganguli, Dustin Li, Eli Tran-Johnson, Ethan Perez, Jamie Kerr, Jared Mueller, Jeffrey Ladish, Joshua Landau, Kamal Ndousse, Kamile Lukosuite, Liane Lovitt, Michael Sellitto, Nelson Elhage, Nicholas Schiefer, Noemi Mercado, Nova DasSarma, Robert Lasenby, Robin Larson, Sam Ringer, Scott Johnston, Shauna Kravec, Sheer El Showk, Stanislav Fort, Tamera Lanham, Timothy Telleen-Lawton, Tom Conerly, Tom Henighan, Tristan Hume, Samuel R. Bowman, Zac Hatfield-Dodds, Ben Mann, Dario Amodei, Nicholas Joseph, Sam McCandlish, Tom Brown, Jared Kaplan

**Venue:** arXiv preprint, 2022 (Anthropic)

**arXiv:** [2212.08073](https://arxiv.org/abs/2212.08073)

---

## Abstract

The researchers propose methods for training harmless AI assistants through self-improvement without human labels. Their approach, termed Constitutional AI, uses a list of rules or principles as guidance. The process combines supervised learning---where the model generates critiques and revisions of its own outputs---with reinforcement learning using AI-generated feedback to train a preference model as the reward signal.

---

## 1. Introduction

Constitutional AI (CAI) trains helpful and harmless AI assistants without human feedback labels for harmlessness. The method uses approximately 10 natural language principles (a "constitution") to guide self-improvement, eliminates the need for human harmfulness labels while improving on prior RLHF approaches, and produces non-evasive responses that explain objections to harmful requests.

---

## 2. Methodology

### Stage 1: Supervised Learning (Critique, Revision, SL)

1. Generate harmful responses from helpful RLHF model
2. Request model self-critique identifying harms
3. Request model revision removing harmful content
4. Repeat process with randomly sampled principles
5. Fine-tune original model on revised responses

### Stage 2: RL from AI Feedback (RLAIF)

1. Sample response pairs from SL-CAI model
2. Use AI feedback (pretrained LM) to evaluate harmlessness via multiple-choice prompting
3. Generate preference labels from AI comparisons
4. Train preference model on human labels (helpfulness) + AI labels (harmlessness)
5. Fine-tune via RL using preference model as reward signal

---

## 3. Results

### Performance (Elo scores from crowdworker comparisons)

- RL-CAI models significantly more harmless than prior RLHF baselines
- Competitive harmlessness vs. human-feedback trained models
- Successfully reduced evasiveness compared to prior HH-RLHF
- Minimal helpfulness tradeoff achieved

### Scaling Observations

- AI harmlessness identification improves with model capability
- Chain-of-thought reasoning substantially improves AI evaluation performance
- 52B+ models approaching human preference model accuracy on HHH evaluations
- Multiple revisions progressively improve harmlessness (diminishing returns after 1--2)

---

## 4. Key Datasets and Scale

- **Red teaming prompts:** 42,496 human-written + 140,335 model-generated = 182,831 total
- **Helpfulness prompts:** 135,296 human-written
- **Constitutional principles:** 16 different principles for harmlessness, ensembled during training
- **Evaluation:** 10,274 helpfulness + 8,135 harmlessness comparisons for final assessment

---

## 5. Technical Details

### Constitutional Principles Format

Critique requests identify specific harms; revision requests rewrite to remove harmful content. Principles address toxicity, racism, sexism, illegality, and other harm categories.

### Chain-of-Thought Enhancement

Models prompted with "Let's think step-by-step" before multiple-choice selection, with probability clamping (40--60%) to improve calibration.

### Goodharting Mitigation Strategies

- Rewrite principles to discourage over-reactive responses
- Ensemble over 16 principles for robustness
- Use soft probability labels rather than hard labels

---

## 6. Important Findings

### Evasiveness vs. Harmlessness Trade-off

Prior work rewarded evasive refusals (e.g., "I can't answer that"). CAI produces thoughtful, non-evasive responses explaining objections---the assistant must refrain from helping with unethical requests but should always engage and explain why it refuses.

### AI Supervision Viability

Larger language models demonstrate >90% accuracy on binary harmlessness comparisons. Models larger than 52B are competitive with human feedback-trained preference models.

### Overtraining Issues

Boilerplate responses ("You are valued and cared for") emerged with excessive RL, mitigated through constitutional principle refinement and ensemble approaches.

---

## 7. Limitations

**Advantages:** Dramatically reduces human annotation burden; increases transparency through natural language principles; enables iterative refinement without new data collection.

**Risks:** Potential for users to train harmful systems more easily; reduced human observation of failures; automation of bias without human oversight.

**Future Directions:** Online training with updated AI feedback; extension to other behavioral axes beyond harmlessness; improved robustness through scaled red-teaming.

---

## 8. Figure Descriptions

- **Figure 1:** Two-stage Constitutional AI pipeline showing SL critique/revision and RLAIF
- **Figure 2:** Harmlessness vs. helpfulness Elo scores across training approaches
- **Figure 3:** Scaling of AI feedback quality with model size
- **Figure 4:** Evasiveness comparison between CAI and standard RLHF models

---

## Key References

1. Christiano et al. (2017) --- Deep reinforcement learning from human preferences
2. Bai et al. (2022) --- Prior work on helpful/harmless training via RLHF
3. Ganguli et al. (2022) --- Red teaming methodology and datasets
4. Wei et al. (2022) --- Chain-of-thought prompting
5. Kadavath et al. (2022) --- Language model calibration for preference labels
6. Gao et al. (2022) --- Scaling laws for reward model optimization
7. Stiennon et al. (2020) --- Summarization from human feedback
8. Ouyang et al. (2022) --- InstructGPT/RLHF for instruction following
9. Glaese et al. (2022) --- Sparrow: dialogue model training with human feedback
10. Askell et al. (2021) --- HHH evaluation framework and dialogue datasets
