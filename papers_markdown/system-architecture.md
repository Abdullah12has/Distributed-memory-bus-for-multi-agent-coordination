**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

## **System Architecture for Real-Time AI Service Markets**

University of Oulu, Faculty of ITEE, CSE Research Unit

## **Contents**

|**1. **|**Architectural Overview**||**2**|
|---|---|---|---|
||Design Principles . . . . . . . . .|. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|3|
|**2. **|**The Integrator: Dual Role**||**4**|
||2.1 Encapsulator (Architectural Role, Paper 1)<br>. . . . . . . . . . . . . . . . . . . . . .||4|
||2.2 Operator (Mechanism-Design|Role, Paper 2) . . . . . . . . . . . . . . . . . . . . .|4|
|**3. **|**Integrator Internal Architecture**||**4**|
||3.1 Sub-DAG Manager<br>. . . . .|. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|4|
||3.2 Internal Scheduler . . . . . .|. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|5|
||3.3 Slice Interface<br>. . . . . . . .|. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|5|
||3.4 Mechanism Executor<br>. . . .|. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|5|
||3.5 Resource Procurer . . . . . .|. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|5|
||3.6 Governance Interface . . . .|. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|5|
|**4. **|**Inter-Component Communication**||**6**|
||4.1 Agent-to-Integrator (Level 1)|. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|6|
||4.2 Integrator-to-Integrator (Cross-Domain) . . . . . . . . . . . . . . . . . . . . . . . .||6|
||4.3 Integrator-to-Local-Marketplace (Level 2) . . . . . . . . . . . . . . . . . . . . . . .||6|
||4.4 Integrator-to-Governance . .|. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|7|
|**5. **|**Overall System Architecture**||**7**|



Page 1 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

|**6. **|**Major Implementation Challenges**|**8**|
|---|---|---|
||6.1 The Max-Flow Abstraction Is Lossy . . . . . . . . . . . . . . . . . . . . . . . . . .|8|
||6.2 GS Valuations Are Fragile . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|9|
||6.3 Integrator Credibility (Who Watches the Integrator?) . . . . . . . . . . . . . . . . .|9|
||6.4 The Broadcast Channel Assumption . . . . . . . . . . . . . . . . . . . . . . . . . .|10|
||6.5 Real-Time Latency Budget . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|10|
||6.6 Dynamic Topology . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|11|
||6.7 Agent-Learner Feedback Loop . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|11|
||6.8 Privacy-Audit-Latency Triangle . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|12|
||6.9 Recursive Credibility . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|12|
||6.10 Empirical Calibration Gap . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|12|
||6.11 Penalty Calibration for Contextual Adversaries<br>. . . . . . . . . . . . . . . . . . .|13|
|**7. **|**Summary: Challenge Severity and Mitigation Status**|**13**|



Analysis of the overall system architecture, the integrator component, and major implementation challenges, based on the theory in the three IEEE TSC papers.

Companion document to governance-architecture.md.

## **1. Architectural Overview**

The trilogy defines a three-layer hybrid architecture for managing real-time AI service economies across the device-edge-cloud continuum.

┌───────────────────────────────────────────────────────────────────┐ │ AGENT LAYER │ │ Autonomous AI agents with latency-sensitive, multi-stage tasks │ │ Private types: (location, budget, tasks, capabilities, role) │ - │ Quasilinear utility: V_ik(T_s, q_s) payment │ └──────────────────────────┬────────────────────────────────────────┘ │bids / demand ▼

┌───────────────────────────────────────────────────────────────────┐ │ LEVEL 1: SLICE MARKETPLACE │ │ Cross-domain allocation of integrator-formed slices to agents │ ───────────────────────────────────────────────────────────── │ │ │ Mechanism: ascending clinching (RT) / VCG / DRA (batch) │ │ Feasibility: polymatroidal (by construction, via encapsulation) │ │ Credibility: commitment + audit + penalties (Papers 2-3) │ │ Settlement: per-epoch; agents observe (allocation, payment) │

Page 2 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

**==> picture [386 x 387] intentionally omitted <==**

**----- Start of picture text -----**<br>
└──────────┬───────────────────────────────────┬────────────────────┘<br>│ │<br>│slices │slices<br>▼ ▼<br>┌────────────────────┐ ┌────────────────────┐<br>│ INTEGRATOR A │ │ INTEGRATOR B │<br>────────────── ──────────────<br>│ │ │ │<br>│ Encapsulates │ │ Encapsulates │<br>│ sub-DAG into │ hash chain │ sub-DAG into │<br>│ polymatroidal │◄────────────►│ polymatroidal │<br>│ slice with │ │ slice with │<br>│ capacity C_bar_A │ │ capacity C_bar_B │<br>└─────────┬──────────┘ └──────────┬─────────┘<br>│resource bids │resource bids<br>▼ ▼<br>┌───────────────────────────────────────────────────────────────────┐<br>│ LEVEL 2: LOCAL MARKETPLACES │<br>│ Within-domain allocation of fungible resources │<br>─────────────────────────────────────────────────────────────<br>│ │<br>│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │<br>│ │ Edge MKT │ │ Cloud MKT │ │ Device MKT │ │<br>│ │ (city) │ │ (provider) │ │ (personal) │ │<br>│ │ GPU, BW, │ │ Model EP, │ │ Sensor, │ │<br>│ │ storage │ │ GPU, cache │ │ local comp │ │<br>│ └─────────────┘ └─────────────┘ └─────────────┘ │<br>│ Clearing: lightweight auctions / posted prices │<br>│ Credibility: implicit (domain separation, single admin domain) │<br>│ Governance: local trust thresholds, data-handling, admission │<br>└───────────────────────────────────────────────────────────────────┘<br>**----- End of picture text -----**<br>


## **Design Principles**

1. **Topology determines tractability** (Paper 1). Tree and series-parallel DAGs yield polymatroidal feasibility regions, enabling efficient allocation and DSIC mechanisms. Arbitrary DAGs break all three guarantees.

2. **Encapsulation restores structure** (Paper 1, Proposition 3). Integrators absorb complementarities inside domain boundaries and expose substitutable slice interfaces. If the quotient graph (after contraction) is tree or SP, the agent-facing region is polymatroidal.

3. **Credibility requires commitment** (Paper 2). No sealed-bid mechanism on a non-modular polymatroid is simultaneously revenue-optimal, DSIC, and credible. Broadcast channels, domain separation, or blockchain deposits resolve this.

4. **Adversarial resilience requires layered governance** (Paper 3). Coalition audit, adaptive penalties, dynamic certification, and market discipline are complementary layers; removing any one creates an exploitable gap.

## **2. The Integrator: Dual Role**

Page 3 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

The integrator is the central architectural component. Papers 1 and 2 reveal that it simultaneously fills two roles that create a fundamental tension.

## **2.1 Encapsulator (Architectural Role, Paper 1)**

The integrator manages a connected sub-DAG of the service-dependency graph:

**Inputs:** - Internal sub-DAG G_j with node capacities C_v - Raw resources procured from Level 2 local marketplaces - Governance constraints (data-locality, trust thresholds, jurisdictional tags)

**Internal processing:** - Max-flow computation: C_bar_j = maxflow(G_j) using Ford-Fulkerson or push-relabel - Node-splitting for node capacities: v -> (v_in, v_out) with edge capacity C_v - Super-source/super-sink construction for multi-entry/exit sub-DAGs - Internal scheduling optimisation (efficiency factor: 0.75 for SP, 0.85 for entangled) - Governance constraint enforcement (capacity partitioning, trust-gated access)

**Output:** - A single composite slice with: - Scalar capacity C_bar_j (max-flow of internal subDAG) - Deterministic latency T_s - Quality q_s - Fixed attributes within each mechanism epoch

## **2.2 Operator (Mechanism-Design Role, Paper 2)**

The integrator also executes the allocation mechanism within its domain:

**Functions:** - Receives agent bids for slices - Computes allocation and payments (VCG, ascending clinching, DRA) - Observes all bids (information advantage over agents) - Could deviate: capacity misreporting, price manipulation, discriminatory allocation

**The tension:** The same entity that (a) knows its true internal capacity and (b) sets the mechanism rules also (c) has a revenue incentive to deviate from faithful execution. This is the credibility gap that Paper 2 formalises (Theorem 1: credibility trilemma) and Papers 2-3 resolve via commitment, audit, and penalties.

## **3. Integrator Internal Architecture**

Based on the theory across all three papers, the integrator requires these internal subsystems:

## **3.1 Sub-DAG Manager**

**Function:** Maintains the internal service-dependency graph, computes max-flow, handles topology changes.

- **engine:** Polynomial-time computation (Ford-Fulkerson / push-relabel), recom-

- puted periodically as internal conditions change

- **Node-splitting:** Converts node-capacitated DAGs to edge-capacitated networks

- **Super-source/sink:** Handles multi-entry/exit sub-DAGs

- **Topology monitor:** Detects when internal services join, leave, or change capacity; triggers max-flow recomputation

**Recomputation frequency:** At minimum once per mechanism epoch. More frequent recomputation enables tighter capacity tracking at the cost of compute overhead.

Page 4 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

## **3.2 Internal Scheduler**

**Function:** Allocates internal resources to fulfill slice commitments. This is where encapsulation creates value: centralised scheduling absorbs complementarities that would destabilise market-based allocation.

- Routes tasks through the internal sub-DAG

- Manages latency-throughput trade-offs (the Pareto frontier that the scalar max-flow abstraction simplifies)

- Enforces internal governance constraints

- Produces the efficiency factor (0.75-0.85 in simulation)

## **3.3 Slice Interface**

**Function:**

- Publishes (C_bar_j, T_s, q_s) per epoch

- Attributes are fixed within each epoch (required for GS property; see Lemma 1 condition (c))

- Must faithfully summarise internal capacity (assumption E2 in Paper 2; violation is a deviation)

## **3.4 Mechanism Executor**

**Function:** Runs the allocation mechanism for its domain at Level 1.

- Ascending clinching auction (real-time, with broadcast)

- VCG (sealed-bid, requires commitment for credibility)

- DRA (batch, with blockchain deposits)

- Commitment interface: publishes hash commitments, participates in cross-hashing with adjacent integrators

## **3.5 Resource Procurer**

**Function:**

- Translates slice demand into resource-level bids (compute, bandwidth, storage, inference endpoints)

- May bid at multiple local marketplaces across domains

- Manages cross-domain resource assembly

## **3.6 Governance Interface**

**Function:** Interfaces with the governance stack (see governance-architecture.md).

- Reports bid transcripts to FCA (encrypted, per-epoch)

Page 5 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

- Publishes commitment hashes and receives adjacent integrators’ hashes

- Maintains slashing deposit with Penalty Engine

- Responds to certification signals (warning, decertification, recertification)

- Enforces governance capacity constraints (X_gov) within its domain

## **4. Inter-Component Communication**

## **4.1 Agent-to-Integrator (Level 1)**

|Signal|Direction|Content|Frequency|
|---|---|---|---|
|Slice advertisement|Integrator -> Agent|(C_bar_j, T_s,|Per epoch|
|||q_s, price)||
|Bid|Agent ->|b_i = V_ik(T_s,|Per epoch|
||Marketplace|q_s)||
|Allocation + payment|Marketplace ->|(x_i, p_i)|Per epoch|
||Agent|||
|Demand/exit|Agent -> All|Demand at current|Per price step|
|broadcast|(broadcast)|price|(ascending)|



## **4.2 Integrator-to-Integrator (Cross-Domain)**

|Signal|Direction|Content|Frequency|
|---|---|---|---|
|Hash commitment|Bidirectional|H_j = Hash(bids,|Per epoch|
||(adjacent)|alloc, payments,||
|||{H_k})||
|Coarse coordination|Bidirectional|Congestion indicator,|Periodic|
|||residual capacity||
|Coalition detection|Via FCA|Discrepancy fags|Per epoch|



## **4.3 Integrator-to-Local-Marketplace (Level 2)**

|Signal|Direction|Content|Frequency|
|---|---|---|---|
|Resource bid|Integrator -> L2|Demand for com-|Per epoch|
||Market|pute/BW/storage||
|Resource allocation|L2 Market ->|Allocated resources|Per epoch|
||Integrator|+ price||
|Congestion signal|L2 Market ->|Queue depth,|Periodic|
||Integrator|utilisation ratio||
|Trust/policy tags|Integrator -> L2|Cross-domain|On change|
||Market|governance||
|||metadata||



Page 6 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

## **4.4 Integrator-to-Governance**

|Signal|Direction|Content|Frequency|
|---|---|---|---|
|Bid transcript|Integrator -> FCA|Encrypted (bids,|Per epoch|
|||alloc, payments)||
|Audit signal|FCA -> Integrator|z_t in {compliant,|Per epoch|
|||anomalous}||
|Certifcation state|FCA -> Integrator|{certified,|On change|
|||warning,||
|||decertified}||
|Deposit status|Penalty Engine <->|Bond balance,|On change|
||Integrator|slashing events||
|Credibility quality|FCA -> Market Seg.|q_j|Per epoch|
||Controller|(posterior-derived)||



## **5. Overall System Architecture**

Combining the market structure, integrator internals, and governance stack from all three papers:

**==> picture [370 x 359] intentionally omitted <==**

**----- Start of picture text -----**<br>
┌──────────────────────────────────────────────────────────────┐<br>│ GOVERNANCE LAYER │<br>│ │<br>│ ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐ │<br>│ │ FCA │ │Penalty │ │Market │ │ Policy │ │<br>│ │(audit, │ │Engine │ │Segment. │ │ Engine │ │<br>│ │ certif.) │ │(deposit,│ │(q_j, │ │ (X_gov, │ │<br>│ │ │ │ fines) │ │ spiral) │ │ r_i(t)) │ │<br>│ └─────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘ │<br>│ │ │ │ │ │<br>└────────┼──────────────┼─────────────┼───────────────┼─────────┘<br>│transcripts │penalties │q_j │bounds<br>│audit signals │ │ │<br>┌────────┼──────────────┼─────────────┼───────────────┼─────────┐<br>│ ▼ ▼ ▼ ▼ │<br>│ ┌──────────────────────────────────────────────────────┐ │<br>│ │ COMMITMENT INFRASTRUCTURE │ │<br>│ │ Broadcast channel / append-only log / blockchain │ │<br>│ └──────────────────────┬───────────────────────────────┘ │<br>│ │ │<br>│ ┌──────────────────────┴───────────────────────────┐ │<br>│ │ LEVEL 1: SLICE MARKETPLACE │ │<br>│ │ Ascending clinching / VCG / DRA │ │<br>│ │ Polymatroidal feasible region (by construction)│ │<br>│ └──────┬──────────────────────────────────┬────────┘ │<br>│ │ │ │<br>│┌───────┴────────┐ hash chain ┌──────────┴───────┐ │<br>**----- End of picture text -----**<br>


Page 7 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

**==> picture [370 x 401] intentionally omitted <==**

**----- Start of picture text -----**<br>
││ INTEGRATOR A │◄────────────►│ INTEGRATOR B │ │<br>││ │ │ │ │<br>││┌────────────┐│ │┌────────────┐ │ │<br>│││Sub-DAG Mgr ││ ││Sub-DAG Mgr │ │ │<br>│││(max-flow) ││ ││(max-flow) │ │ │<br>││├────────────┤│ │├────────────┤ │ │<br>│││Internal ││ ││Internal │ │ │<br>│││Scheduler ││ ││Scheduler │ │ │<br>││├────────────┤│ │├────────────┤ │ │<br>│││Slice Iface ││ ││Slice Iface │ │ │<br>││├────────────┤│ │├────────────┤ │ │<br>│││Mech. Exec. ││ ││Mech. Exec. │ │ │<br>││├────────────┤│ │├────────────┤ │ │<br>│││Resource ││ ││Resource │ │ │<br>│││Procurer ││ ││Procurer │ │ │<br>││├────────────┤│ │├────────────┤ │ │<br>│││Governance ││ ││Governance │ │ │<br>│││Interface ││ ││Interface │ │ │<br>││└────────────┘│ │└────────────┘ │ │<br>│└───────┬────────┘ └──────────┬───────┘ │<br>│ │resource bids │resource bids │<br>│ ┌──────┴──────────────────────────────────┴──────────┐ │<br>│ │ LEVEL 2: LOCAL MARKETPLACES │ │<br>│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │<br>│ │ │Edge MKT │ │Cloud MKT │ │Device MKT│ │ │<br>│ │ └──────────┘ └──────────┘ └──────────┘ │ │<br>│ └────────────────────────────────────────────────────┘ │<br>│ │<br>│ MARKET LAYER │<br>└───────────────────────────────────────────────────────────────┘<br>**----- End of picture text -----**<br>


## **6. Major Implementation Challenges**

The challenges below are ordered roughly from most fundamental (structural) to most practical (engineering).

## **6.1 The Max-Flow Abstraction Is Lossy**

**Source:** Paper 1, Proposition 3 scope limitations.

The integrator summarises its internal sub-DAG as a scalar capacity C_bar_j = maxflow(G_j). This abstraction is valid when the integrator exports a single, homogeneous slice type. It breaks in three identified ways:

**(a) Multi-output integrators.** When an integrator exports multiple service types, C_bar_j generalises to a vector-valued capacity, requiring each integrator’s external feasibility set to itself be polymatroidal. This is a strictly stronger structural condition.

**(b) Latency-throughput Pareto frontiers.** Internal scheduling involves non-trivial trade-offs (e.g., routing through a fast-but-narrow path vs a slow-but-wide one). The scalar max-flow

Page 8 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

abstraction loses this decision-relevant information. Agents observe only T_s (a single latency point), not the frontier.

**(c) Shared leaf nodes.** When multiple integrators share underlying infrastructure (e.g., a common cloud GPU pool), hidden feasibility constraints couple their capacities externally, violating the independence assumption of Proposition 3.

**Implication:** Real integrators must either (i) genuinely export a single slice type (limiting architectural flexibility), (ii) implement internal polymatroidal feasibility (nested complexity), or (iii) accept that the theoretical guarantees degrade gracefully but not perfectly.

## **6.2 GS Valuations Are Fragile**

**Source:** Paper 1, Lemma 1 conditions.

The gross-substitutes property that enables Walrasian equilibrium, efficient computation, and DSIC holds only if:

- Each agent requires at most one slice per task (unit demand)

- Tasks are additively separable (no cross-task complementarity)

- Slice attributes (T_s, q_s)

Any of the following breaks GS: shared agent-side budgets across tasks, cross-task latency coupling (e.g., total pipeline latency matters, not per-stage), or endogenous quality changes within an epoch.

**Implication:** Realistic AI agent workloads often exhibit cross-task coupling (a multi-stage inference pipeline where total end-to-end latency determines value, not individual stage latencies). Encapsulation helps (an integrator can bundle the entire pipeline into one slice), but this pushes complexity inward and may require very coarse-grained slicing.

## **6.3 Integrator Credibility (Who Watches the Integrator?)**

**Source:** Paper 2, assumption E2; Paper 3, recursive credibility.

The integrator has four deviation channels:

1. **Capacity misreporting:** understating C_bar_j to create artificial scarcity

2. **Price manipulation:**

3. **Selective information revelation:** sharing bid information with affiliated agents

4. **Discriminatory allocation:**

Paper 2 addresses channels 2-4 via commitment (broadcast ascending auction makes deviations detectable). Paper 3 addresses multi-integrator coalitions via cross-market audit.

**But channel 1 remains open.** The integrator privately knows its true max-flow. No external party can verify C_bar_j without full visibility into the internal sub-DAG. Paper 2 lists “integrator credibility theory” (faithful max-flow reporting) as an explicit open problem (assumption E2). Competition among integrators (Proposition 2 of Paper 2) provides indirect discipline, but only for pricing, not capacity reporting.

Page 9 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

**Implication:** A practical system needs either (a) independent capacity verification (possibly via redundant monitoring or benchmark probing), (b) incentive-compatible capacity reporting mechanisms (designing a mechanism where truthful capacity reporting is a dominant strategy), or (c) competitive pressure from alternative integrators offering substitutable slices.

## **6.4 The Broadcast Channel Assumption**

**Source:** Paper 2, Theorem 2 assumptions B1-B2.

The ascending clinching auction’s credibility depends on two assumptions:

- **(B1)** Agents broadcast their own demand/exit messages _directly_ to all participants (not relayed by the operator)

- **(B2)** The rank function f (polymatroid structure) is publicly known

**B1 requires independent communication infrastructure.** In practice, this means a peer-topeer broadcast overlay, an independent message bus, or a blockchain. All options add latency, which conflicts with the 100-200ms budget for real-time AI services.

**B2 requires topology transparency.** The polymatroid rank function encodes the capacity constraints of the service-dependency DAG. Publishing it reveals infrastructure topology and capacity, which may be proprietary. ZKP-based alternatives exist in principle but add computational overhead.

**Implication:** The most theoretically appealing credibility mechanism (ascending clinching with broadcast) has the hardest deployment requirements. Domain-separated neutral exchanges avoid B1-B2 but require institutional trust. The system architect must choose based on the deployment context.

## **6.5 Real-Time Latency Budget**

**Source:** All three papers; Paper 2 deployment hierarchy.

The mechanism must complete within the epoch’s latency budget. Competing demands:

|Operation|Typical latency|Budget pressure|
|---|---|---|
|Max-fow recomputation|O(V * E) per integrator|Per-epoch|
|Ascending auction (price|Proportional to V_max * K|Per-epoch|
|steps)|||
|Broadcast round-trip|Network-dependent|Per price step|
|FCA cross-market audit|Proportional to m integrators|Post-epoch|
|Hash chain computation|O(m) hashes|Post-epoch|
|Bayesian posterior update|O(1) per integrator|Post-epoch|



For real-time AI services with 100-200ms interactive deadlines, the ascending auction with broadcast may consume most of the budget. The FCA audit and hash chain can run postepoch (non-blocking), but their results inform the _next_ epoch’s governance state (one-epoch detection delay).

**Implication:** The system may need to separate the _allocation path_ (latency-critical: ascending auction or posted prices) from the _audit path_ (latency-tolerant: FCA verification, hash

Page 10 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

chains, penalty enforcement). Allocation runs at real-time speed; governance catches up asynchronously.

## **6.6 Dynamic Topology**

**Source:** Paper 1, open challenge; Paper 3, non-stationarity.

The theory assumes the service-dependency DAG G_res is fixed within each epoch. In practice, AI service pipelines recompose at runtime: new services deploy, existing ones fail, agents switch between pipeline configurations.

## **Three sub-problems:**

**(a) Intra-epoch changes.** If a service fails mid-epoch, the integrator’s capacity changes, but the mechanism has already committed to allocations. Requires either epoch-aligned failure handling or a rollback/reallocation mechanism.

**(b) Cross-epoch structural changes.** If the quotient graph changes topology (e.g., from tree to entangled due to a new cross-domain dependency), the polymatroidal guarantee may break between epochs. The system must detect this and either (i) refuse the topology change, (ii) deploy additional integrators to restore structure, or (iii) degrade gracefully.

**(c) Integrator lifecycle.** Integrators may join or leave the system, changing the competitive landscape and the quotient graph structure. The governance layer (certification, deposits) must handle integrator churn.

**Implication:** The architecture needs a topology monitor that validates the polymatroidal property of the quotient graph before each epoch and triggers restructuring (re-partitioning, new integrator deployment) when it’s violated.

## **6.7 Agent-Learner Feedback Loop**

**Source:** Paper 3, Discussion limitations.

The theory treats two phenomena independently:

- **Theorem 2** (learning deterrence) assumes i.i.d. agent bids across rounds

- **Proposition 2** (strategic agents) models agents exiting in response to credibility failures

In reality, these interact: operator deviations trigger agent exit, which changes the bid distribution, which alters the operator’s learning signal. This feedback loop creates non-stationarity that neither result captures alone.

**Concrete risk:** A learning operator explores deviations, triggering a wave of agent departures. The depleted agent pool changes the optimal deviation strategy. The operator’s learner may converge to a sub-optimal policy calibrated to the depleted market, or oscillate between exploitation and recovery phases.

**Implication:** The monitoring layer (Proposition 1’s Bayesian type tracking) must be robust to the non-stationarity created by this feedback. The simulation (Exp 11) tests this interaction empirically, but finite-time bounds on welfare loss remain open.

Page 11 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

## **6.8 Privacy-Audit-Latency Triangle**

**Source:** Paper 3, Discussion.

The system faces a three-way tension:

- **Audit requires bid transcripts.** The FCA needs (bids, alloc, payments) from all domains to detect coalition deviations.

- **Privacy requires bid** Agents may not want bids disclosed; integrators resist revealing proprietary pricing.

- **Latency requires speed.** ZKP/MPC for privacy-preserving audit adds computational overhead that may be incompatible with real-time epochs.

**State of the art:** ZKP-based auction verification exists in the blockchain literature but typically operates on timescales of seconds to minutes, not the 100-200ms required for real-time service markets.

**Implication:** The system may need to accept a trade-off: full audit (with privacy costs) for highvalue cross-domain allocations, and lighter-touch statistical monitoring for latency-sensitive flows. This creates a gap that sophisticated coalitions could exploit by restricting deviations to the lightly-audited fast path.

## **6.9 Recursive Credibility**

**Source:** Paper 3, Discussion.

The governance stack requires penalty enforcement, but the entity enforcing penalties may itself have incentives to deviate.

**Chain of trust:** 1. Agents trust the mechanism (if DSIC) 2. DSIC requires credible execution (commitment) 3. Credible execution requires audit (FCA) 4. Audit requires penalty enforcement (Penalty Engine) 5. **Who enforces the Penalty Engine?**

**Three resolution paths:** - **Smart contracts:** Automatic slashing, but requires blockchain infrastructure (latency cost) - **Regulatory authority:** External legal enforcement, but slow and jurisdiction-dependent - **Multi-party computation:** Distributed governance with no single point of trust, but computationally expensive

**Implication:** Every practical deployment must ground the trust chain somewhere. The choice of grounding mechanism (blockchain, regulation, consortium agreement) is a deploymentcontext decision that the theory does not resolve.

## **6.10 Empirical Calibration Gap**

**Source:** Paper 3, Discussion.

The theory uses stylised parameters:

|Parameter|Theory assumes|Reality|
|---|---|---|
|Non-modularity gap|Fixed, known|Unknown; varies by topology|
|gamma_ij||and load|



Page 12 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

|Parameter|Theory assumes|Reality|
|---|---|---|
|Deviation gain Delta_bar|Fixed or state-dependent|Must be estimated from bid|
|||distributions|
|Forgetting factor rho|Confgurable|Requires calibration from|
|||transition data|
|Agent outside option u_0|Homogeneous|Heterogeneous, possibly|
|||unknown|
|Signal accuracy 1-epsilon|Fixed|Depends on audit|
|||mechanism quality|



**Implication:** Before deployment, each parameter requires either (a) empirical measurement from real edge-cloud service traces (proprietary data), (b) conservative worst-case bounds (which may make the system uneconomical), or (c) adaptive estimation procedures running alongside the mechanism (adding complexity and convergence time).

## **6.11 Penalty Calibration for Contextual Adversaries**

**Source:** Paper 3, Theorem 2(ii).

State-independent penalties (fixed slashing deposits) suffice for epsilon-greedy and no-regret learners but fail against contextual-bandit adversaries. These adversaries learn to deviate only in states where Delta_bar(s) > p_F, requiring state-dependent penalty schedules.

**Implementation requires:** 1. An estimator for Delta_bar(s) conditioned on each observable state (needs historical bid data, may be noisy) 2. A commitment device that credibly promises state-dependent penalties (either smart contract with oracle access or FCA-managed fine schedule) 3. Safety margin alpha > 1 to account for estimation error

**Implication:** Adaptive penalty estimation is itself a learning problem operating concurrently with the adversary’s learning. If the penalty estimator lags behind the adversary’s state exploitation, a window of vulnerability opens.

## **7. Summary: Challenge Severity and Mitigation Status**

||||Mitigation in||
|---|---|---|---|---|
|#|Challenge|Severity|trilogy|Open?|
|6.1|Lossy max-fow|High|Single-slice|Yes|
||abstraction||assumption|(multi-output)|
|6.2|Fragile GS|High|Encapsulation +|Partially|
||valuations||conditions||
|6.3|Integrator|High|Competition|Yes (E2 open)|
||capacity||(indirect)||
||credibility||||
|6.4|Broadcast|Medium|Three-tier|Engineering|
||channel||hierarchy||
||deployment||||
|6.5|Real-time|Medium|Allocation/audit|Engineering|
||latency budget||separation||



Page 13 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

||||Mitigation in||
|---|---|---|---|---|
|#|Challenge|Severity|trilogy|Open?|
|6.6|Dynamic|Medium|Per-epoch fxity|Yes|
||topology||assumption||
|6.7|Agent-learner|Medium|Empirical (Exp|Yes (no bounds)|
||feedback||11)||
|6.8|Privacy-audit-|Medium|Acknowledged|Yes|
||latency||as open||
|6.9|Recursive|High|Three paths|Yes (not|
||credibility||proposed|resolved)|
|6.10|Empirical|Medium|Simulation|Yes (real data)|
||calibration||calibration||
|6.11|Contextual|Medium|Adaptive fnes|Partially|
||penalty||(theory)||
||calibration||||



The three highest-severity open challenges (6.1, 6.3, 6.9) share a common theme: **the integrator is trusted more than the theory can verify** . It is trusted to report capacity honestly (6.1/6.3), and the governance layer is trusted to enforce penalties honestly (6.9). Resolving this trust bottleneck, whether through verifiable computation, competitive pressure, or institutional design, is the single most important step toward practical deployment.

Page 14 of 14
