## Integrator System Architecture

## **Contents**

|1.|What the Theory Requires of an Integrator . . . . . . . . . . . . . . . . . . . . . .|1|
|---|---|---|
|2.|Integrator Internal Architecture . . . . . . . . . . . . . . . . . . . . . . . . . . . .|3|
|3.|Data Flow per Mechanism Epoch<br>. . . . . . . . . . . . . . . . . . . . . . . . . .|7|
|4.|Requirement-to-Subsystem Traceability<br>. . . . . . . . . . . . . . . . . . . . . . .|8|
|5.|Major Implementation Challenges<br>. . . . . . . . . . . . . . . . . . . . . . . . . .|10|
|6.|Challenge Summary<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|14|
|7.|Key Architectural Insight . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|15|



Detailed internal architecture for the integrator component, synthesised from the requirements of all three IEEE TSC papers.

## **1. What the Theory Requires of an Integrator**

The integrator sits at the boundary between service composition (the physical sub-DAG of compute resources) and market design (the abstract slice traded at auction). Every theoretical result in the trilogy constrains what happens inside that boundary.

## **1.1 Requirements from Paper 1 (Base Framework)**

|ID|Requirement|Source|Type|
|---|---|---|---|
|R1.1|Encapsulate a service-dependency|Prop. 1, Lemma 1|Hard|
||sub-DAG into a**polymatroidal slice**|||
||with scalar capacity equal to the|||
||max-fow of the sub-DAG|||
|R1.2|Preserve**gross-substitutes (GS)**|Lemma 1, GS1-GS3|Hard|
||structure at the market interface (unit|||
||demand, additive separability, fxed|||
||attributes within epoch)|||
|R1.3|Enforce**governance capacity**|Prop. 1 extension|Hard|
||**bounds**𝑥𝑙≤𝑢𝑙(𝑡)per leaf,|||
||intersected with resource feasibility|||
||before each epoch|||



1

|ID|Requirement|Source|Type|
|---|---|---|---|
|R1.4|Support**cross-domain**|Architecture (Sec. III)|Hard|
||**coordination**: an integrator may|||
||procure resources from multiple local|||
||marketplaces and aggregate them|||
||into a single slice type|||
|R1.5|Maintain a**rank function**𝑓(𝑆)for|Prop. 1 proof|Hard|
||the polymatroid that is consistent|||
||with the physical sub-DAG’s|||
||max-fow|||
|R1.6|Operate within the**two-level hybrid**|Architecture (Sec. III)|Hard|
||**architecture**: Level 1 (slice|||
||marketplace) above, Level 2 (local|||
||resource marketplaces) below|||



## **1.2 Requirements from Paper 2 (Credibility)**

|ID|Requirement|Source|Type|
|---|---|---|---|
|R2.1|Execute the**prescribed mechanism**|Credibility (Def. 2)|Hard|
||**faithfully**(allocation and payments|||
||match the announced rules)|||
|R2.2|Provide a**commitment device**so|Thm. 2, B1-B2|Hard|
||agents can verify execution:|||
||broadcast channel (ascending|||
||auction), smart contract (DRA), or|||
||neutral exchange|||
|R2.3|Accept**domain separation**(the|T3|Hard|
||operator entity is structurally distinct|||
||from agents and resource providers)|||
|R2.4|Revenue model: either|T3, Thm. 2|Design choice|
||**payment-based**|||
||𝜋𝑗= ∑𝑖𝑝(𝑗)<br>𝑖<br>−cost𝑗(requires|||
||commitment) or**per-unit fee**𝜙|||
||(VCG-credible without commitment)|||
|R2.5|Produce an**append-only transcript**|Thm. 2|Hard|
||of(𝑏𝑖𝑑𝑠, 𝑎𝑙𝑙𝑜𝑐𝑎𝑡𝑖𝑜𝑛, 𝑝𝑎𝑦𝑚𝑒𝑛𝑡𝑠)|||
||per epoch for external audit|||
|R2.6|When using ascending auction:|Thm. 2, B1-B2|Conditional|
||support**broadcast of agent**|||
||**demand/exit messages**so clinch|||
||quantities are publicly reconstructible|||



## **1.3 Requirements from Paper 3 (Adversarial Credibility)**

2

|ID|Requirement|Source|Type|
|---|---|---|---|
|R3.1|**Never share private bid**|Thm. 1|Hard|
||**information**{𝑏(𝑗)<br>𝑖}with other|||
||integrators outside the audit protocol|||
|R3.2|Participate in**cross-market audit**:|Cor. 1, Rem. 1|Hard|
||submit encrypted bid transcripts to|||
||FCA, or commit hash𝐻𝑗=|||
||Hash(𝑏𝑖𝑑𝑠𝑗, 𝑎𝑙𝑙𝑜𝑐𝑗, 𝑝𝑎𝑦𝑚𝑒𝑛𝑡𝑠𝑗, {𝐻𝑘})|||
||including adjacent integrators’|||
||hashes|||
|R3.3|Post a**slashing deposit**|Thm. 2|Hard|
||𝐵≥<br>Δ/Pr(detected∣𝛿)at|||
||registration, subject to partial or full|||
||forfeiture on detected deviation|||
|R3.4|When facing contextual-bandit|Thm. 2(ii)|Conditional|
||adversaries: accept|||
||**state-dependent penalty schedule**|||
||𝑝𝐹(𝑠) = 𝛼⋅<br>Δ(𝑠)for all observable|||
||states𝑠|||
|R3.5|Generate**audit signals**|Prop. 1|Hard|
||𝑧𝑡∈{compliant,anomalous}with|||
||known emission probabilities for|||
||Bayesian type tracking|||
|R3.6|Accept**decertifcation**when|Prop. 1(ii)|Hard|
||posterior<br>𝜋𝑆<br>𝑡> 𝜏𝑑, with<br>recertifcation possible under|||
||elevated prior|||
|R3.7|Accept**forgetting-factor updates**𝜌|Prop. 1(iii)|Hard|
||tuned by the marketplace for|||
||non-stationary type tracking|||
|R3.8|Publish**credibility quality**𝑞𝑗derived|Prop. 2|Hard|
||from the posterior, enabling strategic|||
||agents to make informed|||
||participation decisions|||
|R3.9|Coalition penalty must exceed|Thm. 1|Hard|
||per-member share:|||
||𝐵≥∑𝑗∈𝐶𝜋𝑗(𝛿𝐶)/|𝐶||||



## **2. Integrator Internal Architecture**

The requirements above decompose naturally into seven internal subsystems. Each subsystem maps to one or more theoretical requirements.

┌─────────────────────────────────────────────────────────────────────┐ │ INTEGRATOR (Level 1) │ │ │

3

|│|┌──────────────┐|┌──────────────┐|┌──────────────┐|┌──────────────┐|┌──────────────┐|┌──────────────┐|┌──────────────┐|┌──────────────────────┐|┌──────────────────────┐|┌──────────────────────┐|┌──────────────────────┐|┌──────────────────────┐|┌──────────────────────┐|│|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|│|│|Sub-DAG|│───►│||Slice||│───►│||||Mechanism||│|│|
|│|│|Manager|│|│|Constructor||│|│|||Executor||│|│|
|│|│||│|│|||│|│|||||│|│|
|│|│|• topology|│|│|•|max-flow|│|│|||• VCG / ascending|│||│|
|│|│|registry|│|│||compute|│|│|||• bid collection|│||│|
|│|│|• health|│|│|•|GS|│|│|||• allocation rule||│|│|
|│|│|monitor|│|│||validation│||│|||• payment rule||│|│|
|│|│|• failover|│|│|•|capacity|│|│|||• transcript emit|│||│|
|│|│||│|│||publish|│|│|||||│|│|
|│|└──────┬───────┘|||└──────────────┘||||└──────────┬───────────┘||||||│|
|│||│|||||||||│|||│|
|│||│<br>resource||state|||||transcript│|||||│|
|│||▼|||||||||▼|||│|
|│|┌──────────────┐|||||||┌──────────────────────┐||||||│|
|│|│|Resource|│|||||│|||Commitment &||│|│|
|│|│|Procurer|│|||||│|||Audit Interface||│|│|
|│|│||│|||||│|||||│|│|
|│|│|• Level-2|│|||||│|||• broadcast channel||│|│|
|│|│|bidding|│|||||│|||• hash commitment||│|│|
|│|│|• capacity|│|||||│|||• FCA transcript||│|│|
|│|│|assembly|│|||||│|||submission||│|│|
|│|│|• cost|│|||||│|||• deposit mgmt|│||│|
|│|│|tracking|│|||||│|||• penalty accept||│|│|
|│|└──────────────┘|||||||└──────────┬───────────┘||||||│|
|│|||||||||||│|||│|
|│|||||||||governance│signals|||||│|
|│|||||||||||▼|||│|
|│||||||||┌──────────────────────┐||||||│|
|│|┌──────────────┐|||||||│|||Governance||│|│|
|│|│|Revenue &|│◄───────────────────────│||||||||Interface||│|│|
|│|│|Accounting|│|penalties,|||||│||||│|│|
|│|│||│|certification|||||│||• audit signal gen||│|│|
|│|│|• payment|│|state|||||│||• posterior receive||│|│|
|│|│|collection│||||||│|||• certification||│|│|
|│|│|• cost|│|||||│|||state machine||│|│|
|│|│|tracking|│|||||│|||• credibility q_j||│|│|
|│|│|• deposit|│|||||│|||publication||│|│|
|│|│|balance|│|||||│|||• policy bounds||│|│|
|│|│|• net π_j|│|||||│|||enforcement||│|│|
|│|└──────────────┘|||||||└──────────────────────┘||||||│|
|│||||||||||||||│|
|└─────────────────────────────────────────────────────────────────────┘|||||||||||||||
|||│|||||||||▲||||
|||│bids for|resources||||||||│agent bids, participation||||
|||▼|||||||||│||||
|┌──────────────┐||||||||||┌──────────────┐|||||
|│||Local<br>│||||||||│|Agents<br>│||||



4

│ Marketplace │ │ (Level 2) │ └──────────────┘

│ (Level 0) │ │ │ └──────────────┘

## **2.1 Sub-DAG Manager**

**Owns** : The physical service-dependency graph 𝐺𝑗 = (𝑉𝑗, 𝐸𝑗) with per-node capacities.

**Responsibilities** : - Maintain a registry of compute nodes (device, edge, cloud) and the dependency edges between them. - Continuously monitor node health, latency, and available capacity. - Detect topology changes (node failure, link degradation, new resource availability) and propagate them to the Slice Constructor. - Enforce that the sub-DAG remains tree or series-parallel after any topology change (R1.1). If a reconfiguration would introduce entanglement, reject it or decompose into multiple sub-DAGs.

**Interfaces** : - IN: heartbeats and capacity reports from compute nodes; topology-change events. - OUT: current 𝐺𝑗 with per-node capacities to Slice Constructor; resource requirements to Resource Procurer.

**Maps to** : R1.1, R1.4, R1.6.

## **2.2 Slice Constructor**

**Owns** : The abstraction from sub-DAG to tradeable slice.

**Responsibilities** : - Compute the **max-flow** of 𝐺𝑗 to determine aggregate slice capacity 𝑓({𝑙}) for each leaf service 𝑙. This is the scalar capacity offered at the Level-1 marketplace. - Validate that the resulting slice satisfies **GS conditions** (R1.2): unit demand per agent per task, additive separability across tasks, fixed attributes within epoch. - Intersect resource capacity 𝒳res with governance bounds 𝒳gov to produce the feasible polymatroid for the upcoming epoch. - Publish the slice catalogue (available types, capacities, attributes) to the Mechanism Executor.

**Critical invariant** : The rank function 𝑓(𝑆) = max-flow(𝐺𝑗, 𝑆) must be **submodular** (R1.5). If the sub-DAG violates this (e.g., due to entangled topology), the Slice Constructor must either: - Conservatively underestimate capacity (safe but wasteful), or - Signal to Sub-DAG Manager to decompose the topology.

**Interfaces** : - IN: current 𝐺𝑗 and capacities from Sub-DAG Manager; governance bounds from Governance Interface. - OUT: polymatroid parameters (𝐸, 𝑓) and slice catalogue to Mechanism Executor.

**Maps to** : R1.1, R1.2, R1.3, R1.5.

## **2.3 Mechanism Executor**

**Owns** : The auction/mechanism that allocates slices to agents.

**Responsibilities** : - Collect bids 𝑏𝑖 from agents (or demand schedules in ascending format). - Compute the welfare-maximising allocation 𝑥[∗] over the polymatroid. - Compute payments 𝑝𝑖 via VCG or clinching rule. - Emit an **append-only transcript** of (𝑏𝑖𝑑𝑠, 𝑎𝑙𝑙𝑜𝑐𝑎𝑡𝑖𝑜𝑛, 𝑝𝑎𝑦𝑚𝑒𝑛𝑡𝑠) (R2.5). - If ascending auction mode: manage the price-clock, broadcast agent demand/exit messages (R2.6), compute clinch quantities.

5

**Mechanism modes** (selectable per deployment): 1. **Sealed-bid VCG** : Simpler. Agents submit sealed bids; integrator computes allocation and VCG payments. Vulnerable to execution deviation unless externally audited. 2. **Ascending with broadcast** : Agents broadcast their own messages. Clinch quantities are publicly reconstructible. Embeds commitment into the mechanism itself. 3. **Deferred-revelation auction (DRA)** : Agents submit hash-committed bids; revelation and allocation happen in a second phase. Requires blockchain or escrow for commitment.

**Critical property** : The Mechanism Executor must faithfully implement the announced mechanism (R2.1). Any deviation (bid suppression, payment inflation, allocation manipulation) must be detectable via the transcript.

**Interfaces** : - IN: polymatroid parameters from Slice Constructor; agent bids from agents. - OUT: allocation 𝑥[∗] and payments 𝑝𝑖 to agents and Revenue module; transcript to Commitment & Audit Interface.

**Maps to** : R1.2, R2.1, R2.2, R2.5, R2.6.

## **2.4 Resource Procurer**

**Owns** : The integrator’s demand-side participation in Level-2 local marketplaces.

**Responsibilities** : - Translate the committed slice allocation into concrete resource bids at one or more local marketplaces (R1.4, R1.6). - Manage multi-marketplace procurement: if a slice requires resources from domain A (edge) and domain B (cloud), bid in both markets and assemble the results. - Track procurement costs for the Revenue module. - Handle procurement failures: if a local marketplace cannot supply the required resources, either degrade the slice (reduce capacity) or procure from an alternative source.

**Interfaces** : - IN: required resources from Sub-DAG Manager; committed allocations from Mechanism Executor. - OUT: resource bids to Level-2 marketplaces; procurement costs to Revenue module; actual capacity to Sub-DAG Manager.

**Maps to** : R1.4, R1.6.

## **2.5 Commitment and Audit Interface**

**Owns** : All external verifiability and audit interactions.

**Responsibilities** : - **Commitment device management** : Operate the broadcast channel (ascending mode), hash-commitment protocol (DRA mode), or transcript escrow (institutional mode). - **Cross-market hash chain** : At epoch end, compute 𝐻𝑗 = Hash(𝑏𝑖𝑑𝑠𝑗, 𝑎𝑙𝑙𝑜𝑐𝑗, 𝑝𝑎𝑦𝑚𝑒𝑛𝑡𝑠𝑗, {𝐻𝑘 ∶ 𝑘∈ adj(𝑗)}), incorporating hashes from adjacent integrators (R3.2). - **FCA transcript submission** : Encrypt and submit the epoch transcript to the Federated Certification Authority for cross-market consistency verification (R3.2). - **Deposit management** : Maintain the slashing deposit 𝐵 (R3.3), handle partial forfeiture on penalty events. - **Penalty acceptance** : Receive and execute penalty decisions from the FCA/Penalty Engine: state-independent slashing or state-dependent fines (R3.3, R3.4).

**Critical constraint** : This module must be **tamper-evident** . The transcript it produces must be the same one seen by agents (via broadcast) and by the FCA (via submission). Any divergence is itself a detectable deviation.

6

**Interfaces** : - IN: transcript from Mechanism Executor; hashes from adjacent integrators; penalty decisions from Governance Interface. - OUT: committed transcript to FCA; broadcast messages to agents; deposit status to Revenue module.

**Maps to** : R2.2, R2.5, R3.1, R3.2, R3.3, R3.4, R3.9.

## **2.6 Governance Interface**

**Owns** : All interactions with the external governance stack (FCA, Reputation Service, Policy Engine, Market Segmentation Controller).

**Responsibilities** : - **Audit signal generation** : Produce signal 𝑧𝑡 ∈{compliant, anomalous} from internal consistency checks (R3.5). The emission probabilities Pr(𝑧𝑡 ∣𝜔𝑡) must match the governance model’s assumptions. - **Posterior reception** : Receive the current Bayesian posterior ̂𝜋[𝑆][the FCA/Reputation Service.][-] **[Certification][state][machine]**[:][Track][the][integrator’s own] 𝑡[from] certification status (certified, warning, decertified, recertifying) and comply with state transitions (R3.6). - **Credibility publication** : Compute and publish 𝑞𝑗 (credibility quality) derived from the posterior, for agent consumption (R3.8). - **Policy bounds enforcement** : Receive per-leaf governance bounds 𝑢𝑙(𝑡) from the Policy Engine and forward them to the Slice Constructor (R1.3). - **Forgetting factor acceptance** : Receive and apply the marketplace-tuned 𝜌 for non-stationary type tracking (R3.7).

**Interfaces** : - IN: posterior ̂𝜋𝑡[𝑆][and][certification][decisions][from][FCA;][governance][bounds][from] Policy Engine; forgetting factor from marketplace. - OUT: audit signals to FCA; credibility quality 𝑞𝑗 to agents and Market Segmentation Controller; governance bounds to Slice Constructor; certification state to Revenue module.

**Maps to** : R1.3, R3.5, R3.6, R3.7, R3.8.

## **2.7 Revenue and Accounting**

**Owns** : Financial tracking and deposit management.

**Responsibilities** : - Collect payments 𝑝𝑖 from agents (via Mechanism Executor outcomes). - Track − procurement costs from Resource Procurer. - Compute net revenue 𝜋𝑗 = ∑𝑖 𝑝𝑖[(𝑗)] cost𝑗 (R2.4). - Maintain deposit balance 𝐵, accounting for any slashing events. - Provide financial data for penalty calibration (historical ̄Δ estimation).

**Interfaces** : - IN: payments from Mechanism Executor; costs from Resource Procurer; penalty events from Commitment & Audit Interface; certification state from Governance Interface. - OUT: net revenue reports; deposit balance; historical revenue data for penalty calibration.

**Maps to** : R2.4, R3.3.

## **3. Data Flow per Mechanism Epoch**

A single epoch proceeds in seven phases:

Phase 1: Pre-epoch preparation Sub-DAG Manager →Slice Constructor: current G_j, capacities Governance Interface →Slice Constructor: governance bounds u_l(t)

7

Slice Constructor: compute max-flow, validate GS, produce (E, f)

Phase 2: Mechanism execution Agents →Mechanism Executor: bids b_i (or demand schedules) Mechanism Executor: compute x*, p_i Mechanism Executor →Commitment & Audit: transcript (bids, x*, p)

Phase 3: Commitment Commitment & Audit: broadcast/hash-commit transcript Commitment & Audit ↔Adjacent integrators: exchange hashes H_k Commitment & Audit →FCA: submit encrypted transcript

- Phase 4: Resource procurement Mechanism Executor →Resource Procurer: required resources for x* Resource Procurer →Level-2 marketplaces: resource bids Resource Procurer →Revenue: procurement costs

Phase 5: Settlement Revenue: collect p_i from agents, pay Level-2 costs Revenue: compute π_j = Σp_i - costs

- Phase 6: Audit and governance FCA: cross-market consistency check FCA →Governance Interface: audit signal z_t, updated π̂_t^S Governance Interface: update certification state Governance Interface →agents: publish q_j

- Phase 7: Penalty (if triggered) FCA →Commitment & Audit: penalty decision Commitment & Audit →Revenue: execute slashing Revenue: update deposit balance B

## **4. Requirement-to-Subsystem Traceability**

||Sub-|Slice|Mech.|Res.|Commit &||
|---|---|---|---|---|---|---|
|Requirement|DAG|Constr.|Exec.|Procurer|Audit|GovernanceRevenue|
|R1.1 Poly-|●|●|||||
|matroid|||||||
|encapsu-|||||||
|lation|||||||
|R1.2 GS||●|●||||
|preserva-|||||||
|tion|||||||
|R1.3 Gov-||●||||●|
|ernance|||||||
|bounds|||||||



8

||Sub-|Slice|Mech.|Res.|Commit &||
|---|---|---|---|---|---|---|
|Requirement|DAG|Constr.|Exec.|Procurer|Audit|GovernanceRevenue|
|R1.4|●|||●|||
|Cross-|||||||
|domain|||||||
|procure-|||||||
|ment|||||||
|R1.5 Sub-||●|||||
|modular|||||||
|rank|||||||
|function|||||||
|R1.6|●|||●|||
|Two-level|||||||
|architec-|||||||
|ture|||||||
|R2.1|||●||||
|Faithful|||||||
|execution|||||||
|R2.2|||●||●||
|Commit-|||||||
|ment|||||||
|device|||||||
|R2.4||||||●|
|Revenue|||||||
|model|||||||
|R2.5|||●||●||
|Append-|||||||
|only|||||||
|transcript|||||||
|R2.6|||●||●||
|Broad-|||||||
|cast|||||||
|messages|||||||
|R3.1 No|||||●||
|bid|||||||
|sharing|||||||
|R3.2|||||●|●|
|Cross-|||||||
|market|||||||
|audit|||||||
|R3.3|||||●|●|
|Slashing|||||||
|deposit|||||||
|R3.4|||||●|●|
|State-|||||||
|dependent|||||||
|penalties|||||||



9

||Sub-|Slice|Mech.|Res.|Commit &||
|---|---|---|---|---|---|---|
|Requirement|DAG|Constr.|Exec.|Procurer|Audit|GovernanceRevenue|
|R3.5||||||●|
|Audit|||||||
|signal|||||||
|genera-|||||||
|tion|||||||
|R3.6||||||●|
|Decertif-|||||||
|cation|||||||
|accep-|||||||
|tance|||||||
|R3.7||||||●|
|Forgetting|||||||
|factor|||||||
|R3.8||||||●|
|Credibility|||||||
|publica-|||||||
|tion|||||||
|R3.9|||||●|●|
|Coalition|||||||
|penalty|||||||
|bound|||||||



## **5. Major Implementation Challenges**

## **Challenge 1: Max-Flow Recomputation Under Dynamic Topology**

**Problem.** The Slice Constructor must recompute 𝑓(𝑆) = max-flow(𝐺𝑗, 𝑆) whenever the subDAG changes (node failure, capacity fluctuation, new resource onboarding). For a sub-DAG with |𝑉| nodes and |𝐸| edges, max-flow is 𝑂(|𝑉| ⋅|𝐸|) per subset 𝑆. The rank function must be evaluated for exponentially many subsets during mechanism execution.

**Why it matters.** The integrator advertises slice capacities at the start of each epoch. If the subDAG changes mid-epoch (e.g., an edge node goes offline), the advertised capacity may no longer be deliverable. This creates a gap between the polymatroid the market traded on and the physical resources available.

**Tension.** Recomputing more frequently improves accuracy but increases latency and may destabilise the mechanism (agents see changing capacities mid-auction). Recomputing less frequently risks over-promising.

**Severity: HIGH.** This is the fundamental abstraction that makes the entire market architecture work. If max-flow computation is too slow or too stale, the polymatroidal guarantee breaks.

## **Challenge 2: GS Validation at the Boundary**

**Problem.** The Slice Constructor must verify that the slices it produces satisfy GS conditions (GS1: unit demand, GS2: additive separability, GS3: fixed attributes). These are properties of the

10

_interaction_

**Why it matters.** GS is required for the welfare-maximising allocation to coincide with a Walrasian equilibrium (Gul-Stacchetti), which in turn is required for VCG to be DSIC (Paper 1, Prop. 2). If GS fails, the mechanism may not be truthful, and agents have incentive to misreport.

**Tension.** The integrator controls slice definition but not agent valuations. GS2 (no cross-task complementarities) is a restriction on agent preferences that the integrator cannot enforce; it can only design slices to make complementarities unlikely (e.g., by bundling complementary sub-services into a single slice type).

**Severity: HIGH.** The DSIC guarantee is the foundation of the entire incentive structure. If GS fails silently, all downstream guarantees (truthful bidding, efficient allocation, penalty calibration) are undermined.

## **Challenge 3: Transcript Integrity Across Mechanism Modes**

**Problem.** The Commitment & Audit Interface must produce a transcript that is simultaneously: - **Complete** : contains all information needed for the FCA to verify bid-allocation-payment consistency. - **Tamper-evident** : any modification is detectable. - **Privacy-preserving** : does not leak agent bids to competing integrators or third parties beyond what the audit requires.

**Why it matters.** The entire credibility architecture (Papers 2-3) rests on the assumption that deviations are detectable from the transcript. If the integrator can produce a consistent-looking but fabricated transcript, all detection mechanisms fail.

**Tension.** In sealed-bid mode, only the integrator sees the bids; the transcript is self-reported. In ascending mode, agents broadcast their own messages, making fabrication harder but exposing bid information. In DRA mode, hash commitments provide some integrity but require a trusted execution environment or blockchain for verification.

**Severity: CRITICAL.** This is the single point of failure for the entire governance stack. A compromised transcript module renders the FCA, penalties, and type tracking useless.

## **Challenge 4: Deposit Sizing Under Uncertainty**

**Problem.** The slashing deposit 𝐵≥ ̄Δ/ Pr(detected ∣𝛿) requires estimating: - ̄Δ: the maximum expected deviation gain, which depends on agent bid distributions, the non-modularity gap 𝛾𝑖𝑗, and the specific deviation strategy. - Pr(detected ∣𝛿): the detection probability, which depends on audit frequency, signal accuracy, and the deviation’s subtlety.

**Why it matters.** If 𝐵 is set too low, deviation is profitable despite the deposit. If 𝐵 is set too high, it creates a barrier to entry that reduces competition (fewer integrators can afford to participate), which ironically weakens the market-discipline layer.

**Tension.** ̄Δ is not directly observable; it must be estimated from historical data or worst-case analysis. In new markets with no history, conservative (high) deposits may be necessary, potentially excluding smaller integrators.

**Severity: HIGH.** Under-depositing creates a systematic incentive to deviate; over-depositing suppresses competition. Both undermine the market.

11

## **Challenge 5: State-Dependent Penalty Estimation**

**Problem.** For contextual-bandit adversaries (Thm. 2(ii)), the penalty schedule 𝑝𝐹 (𝑠) = 𝛼⋅ ̄Δ(𝑠) must hold for ALL observable states 𝑠∈𝒮. This requires: - Defining the state space 𝒮 (what market conditions are observable?). - Estimating ̄Δ(𝑠) for each state (how profitable is deviation in state 𝑠?). - Ensuring no state is left under-penalised.

**Why it matters.** If even a single state 𝑠[∗] has 𝑝𝐹 (𝑠[∗] ) < ̄Δ(𝑠[∗] ), a contextual learner will discover and repeatedly exploit it, converging to deviation frequency 𝜋(𝑠[∗] ) (the stationary probability of that state).

**Tension.** The state space may be high-dimensional (load level, number of active agents, bid distribution, time of day, etc.). Estimating ̄Δ(𝑠) requires sufficient historical data per state, which grows exponentially with state dimensionality. Coarsening the state space (fewer states) makes estimation feasible but may miss exploitable substates.

**Severity: HIGH.** This is the gap between Theorem 2(i) (fixed penalties work for simple learners) and Theorem 2(ii) (contextual learners need state-dependent penalties). Bridging this gap in practice is an open estimation problem.

## **Challenge 6: Audit Signal Calibration**

**Problem.** The Governance Interface must generate audit signals 𝑧𝑡 with known emission probabilities: Pr(anomalous ∣ honest) = 𝜀 and Pr(anomalous ∣ strategic) = 1 −𝜀, where 𝜀< 1/2. The Bayesian type tracker (Prop. 1) assumes these probabilities are fixed and known.

**Why it matters.** If the actual false-positive rate differs from the assumed 𝜀, the posterior ̂𝜋𝑡[𝑆][is] miscalibrated. Too many false positives cause premature decertification of honest integrators; too few cause delayed detection of strategic ones.

**Tension.** In practice, the “anomalous” signal is generated by statistical tests on the transcript (bidallocation consistency, payment inflation tests). The false-positive rate of these tests depends on the bid distribution, which changes over time. A fixed 𝜀 is a modelling convenience, not a practical guarantee.

**Severity: MEDIUM-HIGH.** Miscalibrated signals degrade the entire dynamic credibility system. The theory provides convergence guarantees conditional on correct 𝜀; violations break those guarantees.

## **Challenge 7: Cross-Hash Synchronisation**

**Problem.** The cryptographic cross-hashing protocol requires each integrator to include in its commitment hash the hashes received from all adjacent integrators: 𝐻𝑗 = Hash(𝑏𝑖𝑑𝑠𝑗, 𝑎𝑙𝑙𝑜𝑐𝑗, 𝑝𝑎𝑦𝑚𝑒𝑛𝑡𝑠𝑗, {𝐻𝑘 ∶ 𝑘∈ adj(𝑗)}). This creates a dependency chain across integrators.

**Why it matters.** All adjacent integrators must complete their epochs and exchange hashes before any can finalise commitment. If one integrator is slow or unresponsive, it blocks the chain. With 𝑚 integrators in a chain, the worst-case latency is 𝑂(𝑚) sequential hash exchanges.

**Tension.** Real-time service markets require sub-second epochs. If the hash chain introduces seconds of synchronisation delay, it may be incompatible with the latency budget. Asynchronous

12

alternatives (each integrator commits independently, FCA checks consistency post-hoc) sacrifice the tamper-evidence that the chain provides.

**Severity: MEDIUM.** The cross-hash is one of two audit options (the other being FCA-based). If cross-hashing is impractical, the system falls back to FCA, which introduces a trusted third party.

## **Challenge 8: Dual-Role Trust Concentration**

**Problem.** The integrator simultaneously: 1. **Encapsulates** the sub-DAG (infrastructure role: managing physical resources). 2. **Operates** the mechanism (market role: running the auction, computing payments).

These roles create a concentration of trust. The integrator knows the bids (as mechanism operator), controls the resources (as infrastructure manager), and determines the mapping between abstract slices and physical resources (as encapsulator). No other entity in the architecture has comparable information or control.

**Why it matters.** Every credibility mechanism in Papers 2-3 addresses _execution_ deviations (the integrator running a different mechanism than announced). But the dual role enables _design_ deviations that are harder to detect: the integrator can design slice definitions that systematically favour certain agents, or set capacity bounds that create artificial scarcity.

**Tension.** Separating the roles (one entity manages infrastructure, another runs the auction) would reduce trust concentration but introduce a new coordination problem and potentially break the polymatroidal abstraction (the mechanism operator needs to know the true capacity, which only the infrastructure manager knows).

**Severity: CRITICAL (under payment-based revenue); RESOLVED (under per-unit-fee).** This is the fundamental trust bottleneck of the architecture. The theory addresses execution credibility thoroughly but largely assumes the encapsulation (sub-DAG to slice mapping) is performed honestly. Paper 3’s Remark 2 shows that domain separation (per-unit-fee revenue) resolves this: the integrator’s profit is increasing in allocation volume, making truthful capacity reporting incentivecompatible. Under payment-based revenue, encapsulation credibility remains open.

## **Challenge 9: Death Spiral Feedback Loop**

**Problem.** Proposition 2 establishes that when an integrator’s credibility degrades, high-value agents exit first (assortative sorting). This reduces revenue, which may reduce the integrator’s investment in compliance, further degrading credibility. The loop is self-reinforcing.

**Why it matters.** The Governance Interface publishes 𝑞𝑗, and strategic agents condition their participation on it. A single credibility event can trigger a cascade that is difficult to reverse, even if the integrator subsequently behaves honestly.

**Tension.** The theory bounds the welfare loss (Prop. 2) but does not provide a mechanism to halt the cascade once it begins. The Market Segmentation Controller (governance-architecture.md, Component 2.6) can detect the spiral, but intervention options (routing agents to alternative integrators, subsidising the affected integrator) require mechanisms not specified in the theory.

**Severity: MEDIUM-HIGH.** The death spiral is a market-level failure that affects agents, not just the integrator. Recovery requires external intervention (governance) and time (rebuilding reputation with elevated prior).

13

## **Challenge 10: Epoch Boundary Synchronisation**

**Problem.** The seven-phase epoch (Section 3) requires strict sequencing: slice construction before mechanism execution, mechanism execution before commitment, commitment before audit, audit before governance update. Across multiple integrators, epochs must be synchronised (or at least their boundaries aligned) for cross-market audit to be meaningful.

**Why it matters.** If integrator 𝑗 runs epoch 𝑡 while integrator 𝑘 is still in epoch 𝑡−1, the cross-hash chain cannot be computed, and the FCA cannot perform simultaneous cross-market verification. Asynchronous epochs create windows where coalition deviations are undetectable.

**Tension.** Different service domains may have different natural epoch lengths (a latency-sensitive edge service may need 100ms epochs; a batch cloud service may use 10s epochs). Forcing all domains to the same epoch length is wasteful for some and insufficient for others.

**Severity: MEDIUM.** Epoch synchronisation is an engineering challenge with known solutions (barrier synchronisation, epoch alignment protocols), but it introduces latency overhead that compounds with the number of integrators.

## **Challenge 11: Recursive Credibility of Audit Infrastructure**

**Problem.** The FCA audits integrators. But who audits the FCA? If the FCA is a trusted third party, its own credibility is assumed, not verified. If it is a consortium of domain operators, those operators may have incentives to collude. If it is a smart contract, its correctness depends on the oracle that feeds it market data.

**Why it matters.** The entire governance stack terminates at the FCA. If the FCA is compromised, all detection, penalty, and certification mechanisms fail simultaneously. This is not a gradual degradation; it is a single point of catastrophic failure.

**Tension.** Making the FCA itself auditable (e.g., via multi-party computation among domain operators) adds latency and complexity. Using blockchain anchoring provides tamper-evidence but requires consensus mechanisms that may be too slow for real-time markets. Regulatory backing provides authority but not technical verifiability.

**Severity: CRITICAL.** This is the recursive credibility problem flagged in all three papers. No purely technical solution exists within the current framework; external commitment (regulation, reputation, multi-party computation) is required.

## **6. Challenge Summary**

|#|Challenge|Severity|Subsystem(s)|Theoretical Basis|Mitigation Status|
|---|---|---|---|---|---|
|1|Max-fow|HIGH|Sub-DAG,|R1.1, R1.5|Incremental|
||recomputa-||Slice Constr.||max-fow algorithms;|
||tion||||epoch-based|
||||||updates|
|2|GS|HIGH|Slice Constr.,|R1.2, Lemma 1|Slice design|
||validation||Mech. Exec.||constraints; runtime|
||||||checks|



14

|#|Challenge|Severity|Subsystem(s)|Theoretical Basis|Mitigation Status|
|---|---|---|---|---|---|
|3|Transcript|CRITICAL|Mech. Exec.,|R2.1, R2.5|Broadcast mode;|
||integrity||Commit &||hash chains; TEE|
||||Audit|||
|4|Deposit|HIGH|Commit &|R3.3, R3.9|Historical estimation;|
||sizing||Audit, Revenue||conservative bounds|
|5|State-|HIGH|Commit &|R3.4, Thm. 2(ii)|State-space|
||dependent||Audit, Revenue||coarsening;|
||penalties||||Bayesian estimation|
|6|Audit signal|MEDIUM-|Governance|R3.5, Prop. 1|Adaptive𝜀|
||calibration|HIGH|||estimation;|
||||||calibration tests|
|7|Cross-hash|MEDIUM|Commit &|R3.2, Cor. 1|Async fallback to|
||synchroni-||Audit||FCA; epoch|
||sation||||alignment|
|8|Dual-role|CRITICAL|All|R2.1, Thm. 1, Rem.|Per-unit-fee resolves|
||trust con-|/ RE-||2|it (Rem. 2);|
||centration|SOLVED|||payment-based|
||||||remains open|
|9|Death spiral|MEDIUM-|Governance,|R3.8, Prop. 2|External intervention;|
||feedback|HIGH|Revenue||gradual recovery|
|10|Epoch|MEDIUM|All|R3.2, Cor. 1|Barrier protocols;|
||synchroni-||||fexible epoch|
||sation||||lengths|
|11|Recursive|CRITICAL|Commit &|All papers|MPC; blockchain|
||credibility of||Audit,||anchoring; regulation|
||FCA||Governance|||



Three challenges are rated CRITICAL: - **Transcript integrity** (Challenge 3): single point of failure for the entire governance stack. - **Dual-role trust concentration** (Challenge 8): the integrator is trusted more than the theory can verify. - **Recursive credibility** (Challenge 11): the audit infrastructure itself needs credibility guarantees.

These three are interconnected: if transcript integrity fails, audit is useless; if the dual role is exploited at the design level, transcripts look clean; if the FCA is compromised, no one detects any of it. The robustness of the integrator architecture depends on addressing all three simultaneously.

## **7. Key Architectural Insight**

The integrator is the component where theory meets implementation most tensely. The trilogy’s theoretical results provide strong guarantees (DSIC, coalition detection, learning deterrence, dynamic certification) but all of them assume the integrator faithfully performs the encapsulation step (sub-DAG to polymatroidal slice). This assumption is:

1. : No external entity can independently verify that the integrator’s reported max-flow matches the true physical capacity of its sub-DAG.

15

2. **Incentive-incompatible under payment-based revenue** : VCG revenue is non-monotone in supply; under-reporting capacity creates artificial scarcity that increases agent externalities and thus VCG payments.

3. **Undetectable** : The mechanism transcript is consistent with honest execution over the reported (under-reported) polymatroid, so no execution-level audit detects the misreport.

**Resolution (Remark 2 in Paper 3).** Domain separation (per-unit-fee revenue) resolves the encapsulation credibility gap. Under per-unit-fee revenue 𝜙⋅|{𝑖∶𝑥[∗] 𝑖[> 0}|][ with][ 𝜙][exceeding marginal] provision cost, the integrator’s profit is increasing in allocation volume. Since a larger polymatroid serves weakly more agents, truthful capacity reporting maximises profit. Over-reporting is detectable via SLA violations. This extends Paper 2’s domain separation result: per-unit-fee provides both execution credibility (Paper 2) and encapsulation credibility (Paper 3, Remark 2).

**What remains open.** For payment-based revenue with commitment devices, encapsulation credibility is not addressed by any formal result in the trilogy. Possible approaches include: - **Capacity attestation** : Trusted hardware (TEE) or zero-knowledge proofs that the reported max-flow matches the actual sub-DAG. - **Competitive pressure** : Multiple integrators offering overlapping slice types, enabling agents to cross-check capacity claims. - **Empirical monitoring** : Statistical tests comparing advertised capacity to actual service delivery over time, feeding into the reputation system.

None of these is sufficient alone; a layered approach (mirroring the credibility stack for mechanism execution) is likely needed.

16
