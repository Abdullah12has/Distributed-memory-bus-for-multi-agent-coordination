IEEE TRANSACTIONS ON SERVICES COMPUTING

1

## Real-Time AI Service Economy: A Framework for Agentic Computing Across the Continuum

Lauri Lov´en, _Senior Member, IEEE_ , Alaa Saleh, _Student Member, IEEE_ , Reza Farahani, _Member, IEEE_ , Ilir Murturi, _Senior Member, IEEE_ , Sujit Gujar, Miguel Bordallo L´opez, _Senior Member, IEEE_ , Praveen Kumar Donta, _Senior Member, IEEE_ , and Schahram Dustdar, _Fellow, IEEE_

_**Abstract**_ **—Real-time AI services increasingly operate across the device–edge–cloud continuum, where autonomous AI agents generate latency-sensitive workloads, orchestrate multi-stage processing pipelines, and compete for shared resources under policy and governance constraints. This article shows that the structure of service-dependency graphs, modelled as DAGs whose nodes represent compute stages and whose edges encode execution ordering, is a primary determinant of whether decentralised, price-based resource allocation can work reliably at scale. When dependency graphs are hierarchical (tree or series–parallel), prices converge to stable equilibria, optimal allocations can be computed efficiently, and under appropriate mechanism design (with quasilinear utilities and discrete slice items), agents have no incentive to misreport their valuations within each decision epoch. When dependencies are more complex, with cross-cutting ties between pipeline stages, prices oscillate, allocation quality degrades, and the system becomes difficult to manage. To bridge this gap, we propose a hybrid management architecture in which crossdomain integrators encapsulate complex sub-graphs into resource slices that present a simpler, well-structured interface to the rest of the market. A systematic ablation study across six experiments (** 1 _,_ 620 **runs,** 10 **seeds each) confirms that** _**(i)**_ **dependency-graph topology is a first-order determinant of price stability and scalability,** _**(ii)**_ **the hybrid architecture reduces price volatility by up to** 70 **–** 75% **without sacrificing throughput,** _**(iii)**_ **governance constraints create quantifiable efficiency–compliance trade-offs that depend jointly on topology and load, and** _**(iv)**_ **under truthful bidding the decentralised market matches a centralised valueoptimal baseline, confirming that decentralised coordination can replicate centralised allocation quality; the theoretical results further establish that incentive-compatible (DSIC) mechanisms can sustain this equivalence in cross-domain settings where no single authority controls all resources. These results provide concrete design guidance: systems whose service pipelines form hierarchical DAGs can achieve centralised-quality coordination through decentralised pricing without requiring a single controlling authority, while systems with entangled cross-domain**

L. Lov´en (lauri.loven@oulu.fi) and A. Saleh are with the Future Computing Group, University of Oulu, Finland. R. Farahani is with the Department of Information Technology (ITEC), University of Klagenfurt, Austria. I. Murturi (Corresponding Author) is with the Department of Mechatronics, University of Prishtina, Kosova. S. Gujar is with Machine Learning Laboratory, International Institute of Information Technology (IIITH), Hyderabad, India. M. B. L´opez is with the Multimodal Sensing Lab, University of Oulu, Finland. P. K. Donta is with the Department of Computer and Systems Sciences, Stockholm University, Sweden. S. Dustdar is with ICREA Barcelona, Spain and the Distributed Systems Group, TU Wien, Vienna.

Funding: This work was supported by the Research Council of Finland through the 6G Flagship program (grant 318927) and the CO2CREATION Strategic Research Council project (grant 372355), by the EC through HEU NEUROCLIMA project (GA 101137711) as well as the ERDF (project numbers A81568, A91867), and by the Business Finland through the Neural pub/sub research project (diary number 8754/31/2022).

## **dependencies benefit from integrator-mediated encapsulation.**

_**Index Terms**_ **—Agentic Computing, Service Management, Service Composition, Mechanism Design, Edge–Cloud Continuum, Polymatroid, Service-Dependency Graph, Governance.**

## I. INTRODUCTION

Recently, AI has moved from a niche capability to a mainstream requirement across industries, pushing services to embed real-time model decisions into everyday workflows. These real-time AI services increasingly run across heterogeneous device–edge–cloud environments. Meeting strict latency and quality-of-service (QoS) constraints therefore requires careful allocation and orchestration of compute, storage, bandwidth, and data-processing resources [1]. This coordination challenge becomes even harder with emerging applications such as multi-modal inference, collaborative agents, and autonomous cyber-physical systems, which place unprecedented pressure on the management plane to coordinate dynamic workloads under capacity variability, changing network conditions, and policy constraints [2]. More recently, the service ecosystem has shifted toward _agentic computing_ , where autonomous AI agents generate tasks, procure services, negotiate resources, and adapt their behavior based on observed performance, incentives, and environmental feedback [3], [4], [5]. In contrast to static clients, these agents actively select services, negotiate resources, and compose multi-step execution pipelines. Consequently, orchestration no longer remains purely centralized [6]; it increasingly becomes a distributed process in which agent decisions directly shape system load, resource contention, and end-to-end QoS.

Modern distributed AI services form layered supply chains. For example, a real-time urban-monitoring agent may invoke an inference service that depends on edge-processed sensor streams and a cloud-hosted foundation model, with each stage consuming compute, storage, and bandwidth at distinct tiers of the continuum [2]. These dependencies form a multi-layer, directed acyclic graph (DAG) that couples tiers across the continuum, making end-to-end placement, scheduling, and capacity management significantly more complex. Governance requirements, such as trust, access control, data locality, and regulatory compliance, further restrict which service paths are admissible [7]. Feasible allocations must therefore simultaneously satisfy resource, dependency, network, and policy

IEEE TRANSACTIONS ON SERVICES COMPUTING

2

constraints. Traditional management-plane approaches optimize these decisions centrally. However, cross-domain continuum deployments that span multiple operators and trust boundaries make unified centralized control impractical, motivating economic constraints (e.g., pricing and auctions) to coordinate agents in a decentralized manner [8]. Neither alone addresses the latency sensitivity, structural dependencies, autonomous agents, and governance constraints of emerging real-time AI ecosystems. In particular, complex dependency graphs introduce complementarities that can destabilize naive resource markets or lead to inefficient service placement. Recent red-teaming studies provide empirical evidence of these risks. Shapira et al. [9] show that autonomous AI agents in multi-agent deployments can engage in unauthorized resource consumption and false reporting, failure modes that formal mechanism design aims to deter.

This article develops a unified framework for managing real-time AI services in agentic computing environments. The framework integrates _(i)_ latency-aware valuations that reflect the QoS sensitivity of AI tasks, _(ii)_ a dependencyaware resource model that captures the structure of multi-layer service compositions, and _(iii)_ governance constraints that restrict feasible allocations based on trust, policy, and locality. We synthesize concepts from networked resource management, service function chaining, and economic coordination to characterize conditions for stable and efficient autonomous agent interactions. A primary outcome is the identification of structural regimes, specifically tree and series–parallel servicedependency topologies, under which the feasible allocation set forms a _polymatroid_ . This yields a convex feasible region with submodular (diminishing-returns) capacity constraints, which in turn enables efficient polynomial-time optimization. Under these conditions, agents’ valuations satisfy the _gross-substitutes_ (GS) property: services are interchangeable rather than complementary. This, in turn, guarantees the existence of market-clearing prices ( _Walrasian equilibria_ [10]) and renders truthful bidding a dominant strategy for every agent. Conversely, arbitrary dependency graphs can break these properties: cross-resource complementarities can cause price oscillations and render welfare maximization computationally intractable. Motivated by these observations, we propose a _hybrid management architecture_ in which crossdomain integrators encapsulate complex service compositions into governance-compliant slices with agent-facing interfaces that are polymatroidal by construction. In parallel, local marketplaces coordinate the underlying fungible services and resources. This architecture preserves tractability at the agentfacing layer while enabling decentralized coordination of the resource substrate. Our contributions are sixfold:

- 1) _Unified framework for real-time AI service management under agentic demand._ We introduce a model that integrates latency-sensitive task valuations generated by autonomous AI agents, resource availability, network conditions, and governance constraints into a single service management abstraction (Sect. III).

- 2) _Service-dependency model._ We formalise multi-stage AI service pipelines using a service-dependency DAG that

captures how services at varying levels of composition, from raw compute and data ingestion through inference and analytics to compound agentic capabilities, depend on one another across device–edge–cloud layers (Sect. III).

- 3) _Formal characterization of structurally stable management regimes._ We prove that when service-dependency graphs follow tree or series–parallel structure, the feasible allocation space is polymatroidal, enabling efficient welfare maximization and incentive-compatible mechanisms. We contrast these with arbitrary dependency graphs, which introduce complementarities that can preclude stable orchestration (Sect. IV).

- 4) _Hybrid management architecture._ We propose a slicebased architecture in which complex service compositions are encapsulated within integrators, exposing simplified, substitutable capacity interfaces to the agent layer (Sect. IV-G).

- 5) _Governance-aware management model._ We incorporate trust thresholds and capacity-partitioning policies directly into the definition of feasible allocations, modeling governance as coordinate-wise capacity restrictions on the service-feasibility region that preserve polymatroidal structure (Sects. III and IV).

- 6) _Systematic ablation evaluation._ We evaluate the framework through a systematic ablation study across six experiments, confirming that dependency topology governs system stability, that encapsulation restores price stability, that governance creates quantifiable efficiency– compliance trade-offs, and that DSIC mechanisms sustain market–oracle equivalence where centralised orchestration is infeasible (Sect. V).

The remainder formalises this framework, characterises structurally stable regimes, and evaluates the design through simulation.

## II. RELATED WORK

Edge, fog, and cloud computing have been extensively studied as platforms for low-latency, resource-aware service delivery [2]. Prior work investigates workload placement [11], [12], mobility-aware orchestration [13], and capacity management [14] within edge-cloud collaborative networks, highlighting the challenges of heterogeneous resources, dynamic network conditions, and real-time QoS requirements [15].

The literature formulates edge-cloud coordination as centralized system-level optimization [16], [17], without addressing decentralized autonomous agent interaction or marketmediated coordination. These contributions establish the foundations for distributed service management, but generally assume a centralized orchestrator with limited consideration of autonomous resource negotiation among service consumers and providers. Service function chaining and distributed execution paradigms formalize the inter-dependencies among computational tasks and the implications for placement and performance optimization [18], [19]. The resulting service graphs couple compute, data, and communication resources, complicating scheduling, latency management, and capacity

IEEE TRANSACTIONS ON SERVICES COMPUTING

3

allocation. Prior work models these dependencies for performance optimization [20], but does not examine their role in autonomous agent interactions or market-mediated coordination. Further, some of recent works on autonomous and agentic behaviors in distributed systems for AI agents initiate tasks, adapt preferences, and negotiate resources are studied in [21], [3]. In addition, Sedlak et al. [22] envision an autonomous service orchestration framework for the computing continuum grounded in Active Inference within a multi-agent coordination context. While these studies identify interaction and coordination challenges, they do not develop a comprehensive analytical framework that systematically integrates agent behavior, service interdependencies, governance mechanisms, and resource allocation across the continuum.

Governance constraints including privacy, locality, and compliance requirements have been studied in multi-agent systems and distributed computing [7]. Trust and reputation mechanisms are widely used to evaluate service providers, enforce reliability, and mediate access [23], [24]. These two works show how governance shapes feasible behaviors, but they do not integrate these constraints into the structure of large-scale service allocation or examine their interaction with autonomous agents and dynamic resource markets. Pricing, auctions, and credit mechanisms have long been explored as tools for resource coordination in distributed systems [25]. Market-based control has been proposed for cloud scheduling, bandwidth allocation, and multi-tenant resource sharing, with emphasis on fairness and efficiency under load. Recent work has advanced auction-based resource coordination in mobile edge computing. For example, repeated auction mechanisms have been proposed for load-aware dynamic resource allocation under multi-tenant demand [26], and double-auction pricing schemes have been developed to jointly address allocation and network pricing in MEC systems [27]. These approaches demonstrate the practical viability of economic coordination in distributed edge environments, but typically assume independently traded resources. Classical mechanismdesign results such as double auctions and equilibrium conditions [8] provide valuable insights but typically assume independent resources or substitutable goods. In contrast, realtime AI services rely on interdependent resource bundles whose dependency structure can fundamentally alter stability, efficiency, and incentive properties.

From the literature, no existing framework simultaneously accounts for latency-sensitive AI agents, service–dependency structures, governance constraints, and autonomous marketmediated interactions across the computing continuum.

## III. PRELIMINARIES

We define our system while considering a distributed service-computing environment spanning devices, edge platforms, and cloud infrastructure [2], populated by autonomous AI agents that generate tasks, compose services, and interact economically across the continuum. Fig. 1 provides a highlevel overview. The framework rests on standard assumptions from network/service management and mechanism design (enumerated in the supplementary material, which also provides full notation). Agents condition their valuations on a

**==> picture [151 x 211] intentionally omitted <==**

**----- Start of picture text -----**<br>
Agentic Layer<br>Tasks  Ti(t) , Messages  mi(t)<br>Valuation Layer<br>Vik (Tik , qik )<br>Service Layer / Dependency DAG<br>Capacities  C(t) Gres = (R, E)<br>Feasible Set<br>Xres ∩ Xgov<br>Mechanism  M<br>(mi(t), st) → (xt, Pi(t))<br>State Update<br>st+1 = Ψ(st, xt, P (t), ξt)<br>Trust<br>i(t) ϕ<br>, Policy  Governance<br>G(t)<br>**----- End of picture text -----**<br>


Fig. 1. Model overview: agentic layer, latency-aware valuations, resource dependencies, governance constraints, mechanism, and state evolution.

commonly accepted system state _st_ ; we focus on normative allocation and mechanism design given this shared operational state.

The set of agents _A_ includes service consumers, providers, integrators, and autonomous AI agents. Each agent _i ∈A_ has a private type _θi_ ( _t_ ) = ( _ℓi, Bi_ ( _t_ ) _, Ti_ ( _t_ ) _, κi, ρi, ϕi_ ( _t_ )) drawn from a type space Θ _i_ , encoding location, budget, tasks, capabilities, role, and governance attributes [7]. Time proceeds in discrete periods _t_ = 1 _,_ 2 _, . . ._ .

Each task _k_ issued at time _t_ has parameters

**==> picture [175 x 13] intentionally omitted <==**

where _qk_ represents workload, _d_[max] _k_ is a deadline, and _λk_ is a latency sensitivity parameter. If task _k_ is allocated to agent _i_ , it experiences latency _Tik_ and yields latency-aware value

**==> picture [192 x 11] intentionally omitted <==**

where _vik_ ( _q_ ) is the base value from completing task k at quality q, and _δik_ is defined by exponential or deadline-based decay functions. Within each mechanism epoch, the latency and quality attributes ( _Ts, qs_ ) of available slices are treated as _exogenous_ parameters determined by the current system state _st_ ; the mechanism treats them as fixed throughout the allocation round. This ensures that the items over which agents bid do not change endogenously with the allocation or prices within a round.

## _A. Service-Dependency Model_

Let _R_ denote the set of service types, where services in _R_ range from infrastructure primitives (CPU, GPU, bandwidth, storage) through data-processing and inference services to compound agentic capabilities. The available capacity of service _r_ at location _ℓ_ and time _t_ is _Cr,ℓ_ ( _t_ ), representing throughput (e.g., requests/s for an inference endpoint, GB/s for a data stream, or cores for raw compute).

IEEE TRANSACTIONS ON SERVICES COMPUTING

4

Resources exhibit structural dependencies: certain services require bundles of underlying resources. We model this by a DAG – _G_ res = ( _R, E_ ), where an edge _E_ = ( _r → r[′]_ ) indicates that service _r[′]_ depends on service _r_ , for example, an inference service depends on a pre-processing pipeline and a model-hosting service, each of which in turn depends on underlying compute and storage. Node capacities _Cv_ (suppressing location and time within each epoch) are _integral_ (representing discrete units such as request slots, GPU cores, or bandwidth quanta), and allocations are integer-valued. Tree and series–parallel structures arise naturally in hierarchical service compositions [28], [29]. Arbitrary DAGs, however, introduce complementarities that can undermine tractability in allocation and mechanism design [30].

## _B. System State_

**==> picture [181 x 10] intentionally omitted <==**

**==> picture [200 x 13] intentionally omitted <==**

where _C_ ( _t_ ) collects all resource capacities; Λ( _t_ ) captures network latencies across the continuum; _D_ ( _t_ ) denotes exogenous demand or load; _R_ ( _t_ ) represents agents’ trust or reputation states; and _G_ ( _t_ ) is the governance state (distinct from the resource DAG _G_ res) specifying applicable policies, compliance constraints, or institutional rules [7]. The state evolves according to exogenous events and the realized allocation.

## _C. Social Welfare and Objective_

At each time _t_ , the social welfare generated by an allocation _xt_ is

**==> picture [251 x 34] intentionally omitted <==**

where cost _j_ ( _xt_ ) denotes the operational cost incurred by provider _j_ and Ext( _xt_ ) captures externalities such as energy use or congestion, with trade-off parameter _µ ≥_ 0. Because _W_ ( _t_ ) depends only on the allocation, payments serve purely as incentive instruments and do not alter social surplus. Provider costs are exogenous: providers participate only when payments cover cost _j_ (individual rationality). The per-epoch mechanism (Sect. IV) maximises demand-side valuations[�] _i[v][i]_[; costs and] externalities are deployment parameters with the planner.

The system operator maximizes the discounted sum of _W_ ( _t_ ) subject to feasibility ( _xt ∈Xt_ , defined below), incentive compatibility, individual rationality, and budget balance. In our simulations, _W_ ( _t_ ) or its time average is the welfare metric.

requiring provider _j_ ’s resources), then _ul_ = 0 for all services _l_ that would route through _j_ for that class; data-locality rules similarly set _ul_ = 0 for services in disallowed jurisdictions. Formally, _X_ gov = _{x ≥_ 0 : _xl ≤ ul_ ( _t_ ) for all _l ∈ L_ ( _G_ ) _}_ , where _L_ ( _G_ ) _⊆R_ denotes the leaf services of the DAG consumed directly by agents.

In practice, the coordinate-wise upper-bound formulation abstracts multi-stakeholder trust boundaries, data-locality restrictions, and capacity-partitioning policies without modeling institutional processes explicitly.

An allocation _xt_ specifies resources and execution pathways. Feasibility is _Xt_ = _X_ res( _st, G_ res) _∩X_ gov( _G_ ( _t_ )), where _X_ res enforces capacity and DAG constraints and _X_ gov enforces governance via coordinate-wise upper bounds. In tree and series–parallel DAGs, _X_ res is polymatroidal [31], [29]; the coordinate truncations of _X_ gov preserve polymatroidal structure (see Sect. IV-C).

## _E. Messages, Mechanisms, and Utilities_

Agent _i_ sends a message _mi_ ( _t_ ) from a message space _Mi_ , reporting bids, asks, task parameters, or policy preferences. We focus on _direct mechanisms_ in which _Mi_ = Θ _i_ ; that is, each agent reports its type. General message spaces are not needed for the results that follow. A mechanism

**==> picture [243 x 23] intentionally omitted <==**

maps messages and the current state to an allocation and payments, where _Pi_ ( _t_ ) is the net payment by agent _i_ (positive when paying, negative when receiving).

The per-period utility of agent _i_ under message profile _m_ ( _t_ ) = ( _m_ 1( _t_ ) _, . . . , m|A|_ ( _t_ )) and type profile _θ_ ( _t_ ) = ( _θ_ 1( _t_ ) _, . . . , θ|A|_ ( _t_ )) is _quasilinear_ in payments:

**==> picture [248 x 25] intentionally omitted <==**

where _γi ≥_ 0 is a risk-aversion coefficient and risk _i_ ( _t_ ) measures uncertainty in agent _i_ ’s own allocation (e.g., variance of experienced latency on the assigned slice); it depends on _xi_ , not on payments or other agents’ allocations, so the quasilinear structure _ui_ = _vi_ ( _xi, θi_ ) _− Pi_ is preserved. For notational convenience, we write _ui_ ( _t_ ) when the dependence on messages and types is clear from context. This quasilinear, private-values structure is required for the DSIC, VCG, and clinching-auction results in Sect. IV.

## IV. MECHANISM DESIGN

## _D. Governance, Trust, and Feasible Allocations_

For each agent _i_ , a reputation score _ri_ ( _t_ ) _∈_ [0 _,_ 1] is updated from verifiable outcomes: _ri_ ( _t_ + 1) = Φ( _ri_ ( _t_ ) _, oi_ ( _t_ ) _,_ logs( _t_ )), where _oi_ ( _t_ ) records SLA compliance or violations [7]. Governance feasibility _X_ gov( _G_ ( _t_ ) _, R_ ( _t_ )) imposes _coordinate-wise capacity restrictions_ : for each leaf service _l_ , an upper bound _ul_ ( _t_ ) _∈_ [0 _, Cl_ ] determined by trust, locality, or role-based access control. For example, if provider _j_ ’s trust score falls below the threshold for task class _k_ (i.e., a category of tasks

This section identifies the structural conditions under which efficient, incentive-compatible allocation is achievable.

## _A. Message Spaces and Direct Mechanisms_

Recall the mechanism _M_ , feasibility set _Xt_ , and message spaces from Sect. III. We focus on direct mechanisms in which agent _i_ reports its type, _mi_ ( _t_ ) = _θ_[ˆ] _i_ ( _t_ ) _∈_ Θ _i_ . A strategy is a mapping _σi_ : Θ _i →Mi_ ; a strategy profile is _σ_ = ( _σi_ ) _i∈A_ .

5

IEEE TRANSACTIONS ON SERVICES COMPUTING

## _B. Incentive Properties_

Given a strategy profile _σ_ , the per-period utility _ui_ ( _t_ ) is as defined in Sect. III. We adopt standard incentive-theoretic desiderata.

- _Dominant-strategy incentive compatibility (DSIC)._ The mechanism is DSIC if, within each decision epoch, truthful reporting maximizes per-period utility for each agent _i_ regardless of what other agents report [32]:

**==> picture [213 x 27] intentionally omitted <==**

where the first argument is the report, the subscript _−i_ collects all other agents’ reports, and the argument after the semicolon is agent _i_ ’s true type (which determines the valuation). A weaker notion, _Bayes–Nash IC_ (BNIC), requires truthfulness only in expectation over other agents’ types. The main results of this article (Prop. 2) establish DSIC, the stronger property.

- _Individual rationality (IR)._ The mechanism is individually rational if, under truthful reporting, _ui_ ( _θi, θ−i_ ; _θi_ ) _≥_ 0 for all _θ−i_ and all participating agents _i_ .

- _(Weak) budget balance (BB)._ The mechanism is weakly budget-balanced if it does not run a deficit, i.e.,

**==> picture [156 x 23] intentionally omitted <==**

Our goal is to characterize when these classical properties are compatible with efficiency in the presence of latency-aware valuations, dependency-aware resources, and governance constraints.

_where x_ ( _S_ ) =[�] _l∈S[x][l][. When][ G]_[res] _[is a rooted tree, the family] L_ = _{Lv} is_ laminar _: any two members are either nested or disjoint. As shown in Prop. 1, the same laminar property holds for series–parallel networks. Given a laminar family, the polymatroid rank function is_

**==> picture [172 x 23] intentionally omitted <==**

_minimized over anti-chains A in L such that S ⊆_[�] _v∈A[L][v][.]_

**Proposition 1** (Polymatroidal Structure under Tree/SP DAGs) **.** _Let G_ res _be a rooted tree or two-terminal series–parallel network (under the leaf-block semantics of Definition 1) with node capacities Cv >_ 0 _. Then:_

- _(i) the capacity function f defined in Definition 1 is submodular, monotone, and normalized (f_ ( _∅_ ) = 0 _);_

- _(ii) X_ res _is a polymatroid with rank function f ; and_

- _(iii) the base polytope B_ ( _f_ ) = _{x ∈X_ res : _x_ ( _L_ ( _G_ )) = _f_ ( _L_ ( _G_ )) _} is the set of tight allocations (i.e., allocations that saturate total leaf-level throughput)._

## _Proof._ See the supplementary material.

Governance constraints _X_ gov impose coordinate-wise upper bounds _xl ≤ ul_ on each leaf service (Sect. III). The intersection of a polymatroid with such coordinate truncations is again a polymatroid [29], so _Xt_ = _X_ res _∩X_ gov inherits polymatroidal structure. This preservation relies on governance being expressible as independent per-leaf bounds; more complex couplings would generally not preserve polymatroidal structure (details in supplementary material).

## _D. From Per-Task Valuations to Gross Substitutes_

## _C. Structural Regimes for Efficient Allocation_

The service–dependency DAG _G_ res and governance constraints induce a feasible allocation set _Xt_ . The structure of _Xt_ is critical for both optimization and mechanism design. A _polymatroid_ is the polytope _{x ≥_ 0 : _x_ ( _S_ ) _≤ f_ ( _S_ ) _∀S}_ for a normalized, monotone, submodular rank function _f_ (formal definition in the supplementary material; intuitively, a system of capacity constraints with diminishing returns). We formalize the conditions under which classical results from polymatroid optimization and gross-substitutes valuations apply.

**Definition 1** (Service-Feasibility Region) **.** _Given the servicedependency DAG G_ res = ( _R, E_ ) _with node capacities Cv for each v ∈R, let L_ ( _G_ ) _⊆R denote the_ leaf services _consumed directly by agents. For each internal node v, let Lv ⊆ L_ ( _G_ ) _be the set of leaves reachable from v. (For trees, Lv is the leaf set of the subtree rooted at v; for series–parallel networks, Lv is defined via the recursive SP decomposition with designated source and sink, see the supplementary material for details.) Each allocation variable xl represents a_ throughput token _: a unit of demand counted consistently at every ancestor constraint. The service-feasibility region is_

**==> picture [233 x 27] intentionally omitted <==**

The mechanism-design results of the next subsection require that agents’ valuations over resources satisfy the grosssubstitutes (GS) condition. We now show that the latencyaware valuations introduced in Sect. III satisfy GS under the architectural encapsulation proposed in this work.

**Lemma 1** (GS Valuations under Slice Encapsulation) **.** _Suppose integrators encapsulate multi-resource service paths into composite_ slices _, where each slice s is a discrete, indivisible unit with fixed internal routing, deterministic latency Ts, and quality qs. Suppose further that: (a) each agent requires at most one slice per task (unit demand); (b) an agent’s tasks are_ additively separable _—its valuation decomposes as a sum across tasks with no cross-task complementarity or shared feasibility coupling; and (c) within each mechanism epoch, slice attributes_ ( _Ts, qs_ ) _are determined by the current system state st and remain fixed throughout the allocation round (so that the items over which GS is defined do not change endogenously with prices). Then the agent’s induced valuation over slices satisfies the gross-substitutes condition._

## _Proof._ See the supplementary material.

Additive separability (condition (b)) is critical: shared agentside budgets, cross-task latency coupling, or shared token caps would destroy the GS property. Without encapsulation, agents

6

IEEE TRANSACTIONS ON SERVICES COMPUTING

would bid on resource bundles along DAG paths, introducing complementarities that violate GS. Further discussion of conditions (b) and (c) is in the supplementary material.

**Proposition 2** (Efficient Mechanism Design under Structured DAGs) **.** _Suppose Xt is polymatroidal (Prop. 1), agents’ valuations satisfy GS (Lemma 1), agents have quasilinear utility, and slices are discrete items with integral capacities. Then:_

- _(i) a Walrasian equilibrium exists with per-type prices supporting the welfare-maximising allocation [33], [34], [35], [28];_

- _(ii) the welfare-maximising allocation is computable in polynomial time via a Kelso–Crawford-style ascending auction under bounded integer valuations [33]; and_

- _(iii) the efficient allocation is implementable in DSIC. Under GS, every Walrasian equilibrium allocation maximises social welfare (the sum of valuations) [34], so VCG payments [32] apply directly to the allocation of Part (i) and yield DSIC (see the supplementary proof for the detailed argument). VCG may run a deficit. In the single-type-per-task case, the polymatroid clinching auction [36], [37] additionally guarantees weak budget balance. When tasks may choose among heterogeneous slice types, VCG remains the appropriate mechanism._

_The full statement with detailed parameter conditions is in the supplementary material._

## _Proof._ See the supplementary material.

Together, Props. 1 and 2 and Lemma 1 establish that, _within each decision epoch_ , real-time AI service economies with tree or SP dependency structures admit mechanisms that are efficient, DSIC, and individually rational. The guarantees apply epoch-by-epoch; cross-epoch strategic dynamics (learning, reputation gaming) lie outside their scope. An extended discussion of the polymatroid’s three distinct roles and the interepoch limitations is provided in the supplementary material.

## _E. Instability in General Dependency Graphs_

When the service–dependency graph is an arbitrary DAG, dependencies among services can generate strong complementarities: the value of a bundle may be strictly greater than the sum of its parts. From a market-design perspective, this pushes the environment outside the GS domain [34] and need not preserve the polymatroidal structure of _X_ res (cross-cutting dependencies typically destroy the laminar property required by Prop. 1). Specifically, winner determination in combinatorial auctions with general valuations is NP-hard [38], [39], [40], Walrasian equilibria may fail to exist when valuations violate the gross-substitutes condition [34], [30], and the Myerson– Satterthwaite impossibility [41] illustrates a fundamental tension: even in bilateral trade, no mechanism can simultaneously satisfy efficiency, DSIC, IR, and budget balance—providing indicative impossibility pressure for the richer multi-agent setting, though a formal reduction would require matching the specific assumptions. Consequently, naive market-based allocation on a complex dependency graph can be unstable or inefficient.

## _F. Restoring Tractability via Architectural Encapsulation_

The following proposition shows that encapsulation restores tractability even for arbitrary DAGs.

**Proposition 3** (Polymatroidal Encapsulation of Arbitrary DAGs) **.** _Let G_ res _be an arbitrary service-dependency DAG. Suppose integrators partition the non-leaf nodes into disjoint clusters, each managing a connected sub-DAG internally. Assume:_

- _(i) each integrator j exposes a single composite service (slice) with scalar capacity C_[¯] _j equal to the maximum flow of its sub-DAG;_

- _(ii) C_ ¯ _j faithfully summarises the sub-DAG’s aggregate external capacity (valid when each integrator exports a single, homogeneous slice type);_

- _(iii) no external feasibility constraints couple different integrators beyond the shared quotient-graph structure._

_Let G[′] be the quotient graph from contracting each cluster to a single node. If G[′] has tree or series–parallel structure, the agent-facing feasible region is polymatroidal._

## _Proof._ See the supplementary material.

Prop. 3 is the formal basis for the hybrid market architecture: by ensuring that the quotient graph seen by agents is structurally disciplined, encapsulation restores the conditions under which Prop. 2 guarantees efficient, incentive-compatible allocation. The integrator absorbs the complementarities that would otherwise destabilise market-based coordination.

## _G. Hybrid Market Architecture_

The results above indicate that efficient mechanism design requires the agent-facing service space to satisfy polymatroidal and GS conditions, even when the underlying infrastructure does not. We propose a three-layer hybrid architecture that achieves this through encapsulation.

_Cross-Domain Integrators:_ Integrators form the agentfacing layer of the architecture. Each integrator encapsulates a complex multi-resource service path into a governancecompliant slice (Prop. 3), internally managing the dependency DAG of its sub-system and exposing a simplified, substitutable capacity interface with capacity equal to the max-flow of its internal sub-DAG. In realistic continuum deployments, sensing, compute, and radio interactions are tightly coupled within physical or operational domains, often under heterogeneous ownership and trust boundaries[42]. Within such a domain, cross-resource and cross-layer complementarities are resolved internally through coordinated management before any service is exposed externally. The integrator plays precisely this role. It performs an internal consolidation of the sub-DAG’s structural dependencies and governance constraints, and presents outward-facing slices as simplified abstractions. As a result, complementarities are absorbed inside the domain boundary, while the inter-domain market only encounters substitutable slice interfaces. Internally, each integrator absorbs the complementarities of its sub-DAG through centralised management, at some efficiency cost; the agent-facing market never encounters the non-polymatroidal structure. Agents trade over

IEEE TRANSACTIONS ON SERVICES COMPUTING

7

these slice interfaces, whose feasible regions are polymatroidal by construction. The number of integrators is determined by the deployment: Prop. 3 requires only that the quotient graph remain tree or series–parallel, so one integrator per natural domain boundary is typical. Governance constraints spanning multiple domains (cross-border data sovereignty, inter-domain trust, jurisdictional restrictions) are enforced at the integrator level [7].

_Local Marketplaces:_ Beneath the integrators, autonomous markets operating at device or edge scope coordinate the fungible services and resources (compute, bandwidth, storage, standard inference endpoints) that integrators draw on to fulfil slice commitments. Local markets clear via lightweight auctions or posted prices and enforce local governance policies (trust thresholds, data-handling rules, domainspecific admission control) [43], [2]. For simple, singledomain services that do not require cross-domain encapsulation, agents may also interact with a local marketplace directly. _Inter-Market Coordination:_ Local markets and integrators exchange coarse-grained signals (aggregate demand, congestion indicators, trust updates) to maintain cross-domain consistency without full system-wide optimisation. Global constraints involving governance and cross-domain feasibility flow through the integrators; purely local resource signals may be exchanged directly between marketplaces [44].

This architecture co-designs the economic and infrastructure layers: agents trade over integrator-exposed slices using mechanisms that exploit GS valuations and polymatroid structure (Prop. 2), while fungible services and resources are coordinated through local marketplaces. Non-fungible services (e.g., jurisdiction-bound datasets, specialised model instances) are allocated via discrete assignment mechanisms [30]. The integrator layer is the architectural embodiment of Prop. 3, ensuring that the market seen by agents remains tractable even when the underlying DAG is complex. Fig. 2 illustrates the resulting architecture. The separation between internal domain-level consolidation and inter-domain economic coordination allows slice trading and local market clearing to remain distributed across domains, without requiring global centralised clearing.

_Scope and Failure Modes:_ The guarantee of Prop. 3 rests on the three conditions stated in the proposition, whose violation defines the architecture’s failure modes: _(a)_ multioutput integrators or heterogeneous bundles may reintroduce complementarities at the agent-facing layer; _(b)_ when internal scheduling involves non-trivial trade-offs (e.g., latency– throughput Pareto frontiers), the scalar max-flow abstraction may lose decision-relevant information; and _(c)_ shared accelerators, multi-tenant network links, or cross-domain policy couplings can create hidden feasibility constraints. When any condition fails, the polymatroidal guarantee does not hold. The simulation results of Sect. V quantify the consequences.

_Illustrative Example:_ Recall the urban-monitoring scenario from Sect. I: a real-time monitoring agent consumes an inference service that depends on sensor-data streams processed at the edge and a cloud-hosted foundation model. Without architectural encapsulation, the agent would bid simultaneously on edge GPU cycles, camera bandwidth, cloud

model endpoints, and cross-tier network capacity, a multidimensional bundle with strong complementarities: all resources are needed together; any one alone is worthless. These violate the GS condition and destabilise market prices.

The hybrid architecture resolves this through two crossdomain integrators and two local marketplaces. _Integrator 1_ (sensor-to-feature) encapsulates the edge-side sub-DAG spanning camera streams, frame extraction, and feature-vector computation. It internally manages device–edge dependencies and enforces the constraint that raw video frames must not leave the city domain, exposing a single “feature-extraction slice” with capacity _C_[¯] 1 equal to the max-flow of its internal sub-DAG. _Integrator 2_ (feature-to-inference) encapsulates the cross-domain sub-DAG spanning feature vectors, cloud foundation-model inference, and post-processing. It manages the edge–cloud handoff and enforces the cloud provider’s data-handling policies, exposing a “model-inference slice” with capacity _C_[¯] 2. From the agent’s perspective, the market reduces to two substitutable slices at posted prices, i.e., a unit-demand valuation satisfying GS (Lemma 1). The quotient graph (agent _→_ slice 1 _→_ slice 2) is series–parallel, so the agent-facing feasible region is polymatroidal (Prop. 3), and Prop. 2 guarantees efficient, incentive-compatible allocation. Under this DSIC guarantee, agents truthfully reveal their valuations, enabling the decentralised slice market to achieve the same allocation a centralised planner with full knowledge of both city-infrastructure and cloud-provider resources would compute, without requiring any single entity to control both domains.

To fulfil their slice commitments, the integrators draw on two local marketplaces. _Local Market A_ (city-infrastructure domain) coordinates fungible edge services and resources (GPU cycles at street-level compute nodes, bandwidth to camera feeds, frame-extraction endpoints) via lightweight auctions and enforces municipal data-locality policies. _Local Market B_ (cloud-provider domain) coordinates fungible cloud services and resources (model-hosting endpoints, GPU instances for inference, result-caching storage) where multiple integrators and other workloads bid for capacity under the provider’s terms. Governance is handled at the appropriate layer: Integrator 1 enforces municipal data-locality; Integrator 2 enforces cross-domain data-handling compliance; Local Market A enforces city-domain admission control; Local Market B enforces cloud-provider terms. No single layer requires global knowledge of the entire system.

Operational coordination between these entities relies on a small set of coarse-grained signals. At the inter-market level, Market A broadcasts an edge-GPU congestion indicator to Market B so that the cloud domain can pre-scale inferenceendpoint capacity for incoming feature vectors; Market B reports model-endpoint queue depth back, enabling Market A’s local price adjustment to anticipate downstream conditions rather than reacting only to local state. At the market– integrator level, Market A reports aggregate feature-extraction demand to Integrator 1, which responds with its current slice price and residual capacity. Before admitting a cross-domain slice, Integrator 2 verifies that Integrator 1’s output (feature vectors via Market A) and cloud capacity (at Market B)

IEEE TRANSACTIONS ON SERVICES COMPUTING

8

**==> picture [172 x 196] intentionally omitted <==**

**----- Start of picture text -----**<br>
AI Agents<br>service consumers<br>bids for slices  bids for slices<br>Cross-Domain Integrator(s)<br>( one or more per domain boundary)<br>slice encapsulation<br>prices, prices,<br>availability availability<br>Governance<br>bids, trust, policies bids,<br>queries rules, queries<br>Marketplace A reput. Marketplace B<br>local clearing of coord. local clearing of<br>fungible resources & fungible resources &<br>services services<br>offers offers<br>allocations allocations<br>AI Agents<br>service & resource producers<br>**----- End of picture text -----**<br>


Fig. 2. Hybrid architecture. Service-consuming agents trade over integratorexposed slices (Prop. 3); integrators bid for capacity at local marketplaces, which coordinate service and resource offerings from provider agents; governance flows through integrators (cross-domain) and marketplaces (local). For simple single-domain services, agents may also interact with a local marketplace directly.

are both available; this is a flow dependency through the quotient-graph series connection, not a shared-resource coupling between integrators. When forwarding a slice request, Integrator 2 attaches trust scores and data-handling policy tags from the city domain so that Market B can enforce its own policies without direct visibility into Market A’s operations. Each of these signals is a scalar or small vector, e.g., a utilisation ratio, a price, a capacity count, or a trust score, keeping coordination overhead low while providing sufficient information for local tˆatonnement processes to converge without centralised clearing.

## V. EVALUATION

We evaluate the framework through a systematic ablation study over four removable components: **(S)** structural discipline (tree/SP topology yielding polymatroidal feasibility), **(H)** hybrid architecture (integrator encapsulation with EMA price smoothing and efficiency factor), **(G)** governance (trust-gated capacity partitioning), and **(M)** market mechanism (price-based coordination via tˆatonnement). Six experiments (1 _,_ 620 runs, 10 seeds each) progressively remove or vary these components; the current simulations evaluate resourceallocation and queueing behaviour under different structural regimes, while full auction mechanisms with strategic agents remain future work. In particular, the tˆatonnement market baseline serves as a price-discovery and coordination proxy; it is not itself a strategy-proof mechanism and does not test the DSIC properties established in Prop. 2. All results include bootstrap 95% CIs (BCa, 2 _,_ 000 resamples); full statistical tables are in the supplementary material.

## _A. Experimental Setting_

The simulation models a heterogeneous device–edge– cloud environment with three compute tiers (capacities

TABLE I

COMPONENT ABLATION SUMMARY. EACH ROW SHOWS THE EFFECT OF REMOVING ONE DESIGN COMPONENT UNDER ITS MOST INFORMATIVE CONDITION. _σp_ : PRICE VOLATILITY (STD. DEV. OF LOG-RETURNS). FULL RESULTS IN SUPPLEMENTARY MATERIAL.

||**Component**|**Condition**|**With**<br>**Without**|
|---|---|---|---|
||_−S: Tree →Entangled (high _<br>_σp_||_load, Exps. 1–2)_<br>0<br>0_._273|
|||Drop rate|49%<br>99_._8%|
||_−H: Hybrid _|Scaling ceiling<br>None<br>_N_=20–30<br> _→Na¨ıve (SP, high, N_=60_, Exp. 4)_||
|||_σp_<br>0_._10<br>0_._34<br>Latency<br>181ms<br>197ms<br>EMA: stability; eff. factor: latency/welfare||
||_−G: None →Strict (ent., high, Exp. 3)_|||
|||Latency|404ms<br>266ms|
|||Coverage|0_._4%<br>0_._2%|
|||Side-effect:|governance induces _σp >_0|
||_H×G: Na¨ıve/strict →Hybrid/strict (SP, med, Exp. 5)_|||
|||_σp_<br>0_._78<br>0_._20<br>Three regimes: additive, sub-/super-additive||
||_−M: Market _|_→Value-greedy _|_(all conditions, Exp. 6)_|
|||Welfare diff|_<_1% (prices redundant)|
|||Value model<br>(greedy vs.|8_._4a.u.<br>0_._26a.u.<br> random, ent./med; 32_×_)|



_{_ 200 _,_ 300 _,_ 500 _}_ , base delays _{_ 5 _,_ 15 _,_ 50 _}_ ms) and 50 agents (default) generating latency-aware tasks via Poisson arrivals ( _λ_ =1 _._ 0 tasks/round/agent). Tasks traverse multi-tier execution paths defined by service-dependency DAGs [18], [45]. Market clearing uses tˆatonnement over per-tier capacities with an online logistic model that learns deadline-feasibility success rates. Trust evolves via asymmetric SLA-compliance updates (+0 _._ 03/ _−_ 0 _._ 08) [23], [24]. Each run spans 200 rounds; we record latency, drop rate, price volatility ( _σ_ of logreturns), welfare (realised value minus cost), and service coverage. Full parameter details are in the supplementary material; simulation code is available at https://github.com/ lloven/agentic-economy-sim.

## _B. Ablation Results_

Table I summarises the key finding for each component ablation; Fig. 3 visualises the structural result. A theory-toexperiment mapping table, detailed per-experiment figures, result tables, and statistical tests (Kruskal–Wallis, pairwise Wilcoxon with Holm correction, Cliff’s _δ_ , ART ANOVA) are in the supplementary material.

_Structural discipline (S):_ The first experiment varies the dependency-graph topology from polymatroidal (linear, tree, SP) to non-polymatroidal (entangled) across three load levels (120 runs), directly testing the prediction of Prop. 1. As Fig. 3 shows, polymatroidal topologies (linear, tree) maintain zero price volatility and moderate drop rates across all loads, while the entangled DAG exhibits _σp_ = 0 _._ 273 and 99 _._ 8% drops under high load ( _λ_ = 1 _._ 5). The SP topology is polymatroidal yet shows intermediate volatility ( _σp_ = 0 _._ 112) at high load

IEEE TRANSACTIONS ON SERVICES COMPUTING

9

**==> picture [239 x 191] intentionally omitted <==**

**----- Start of picture text -----**<br>
Load level low medium high<br>500 90%<br>400<br>70%<br>300<br>50%<br>200<br>0.5<br>0.9 0.4<br>0.3<br>0.6<br>0.2<br>0.3 0.1<br>0.0<br>DAG topology DAG topology<br>linear tree spentangled linear tree spentangled<br>Latency (ms) Drop rate (%)<br>Utilisation )Price vol. (σ<br>**----- End of picture text -----**<br>


Fig. 3. Structural ablation (Experiment 1): DAG topology _×_ load. Polymatroidal topologies (linear, tree) maintain zero price volatility; entangled DAGs degrade sharply under load.

because its demand profile pushes per-tier utilisation toward saturation, where the tˆatonnement fails to converge despite equilibrium existence. The ordering (linear _≈_ tree _<_ SP _<_ entangled) confirms the theory: structural complexity governs market stability. A scaling stress test (Experiment 2, supplementary material) reinforces this result: the topologydependent “scaling ceiling” at which the system transitions from stable to degraded operation is absent for tree topologies within the tested range ( _N_ = 10–60), occurs around _N_ = 40 for SP, and appears by _N_ = 20–30 for entangled DAGs.

_Hybrid architecture (H):_ The fourth experiment (480 runs) tests the encapsulation prediction of Prop. 3 by incrementally adding the hybrid architecture’s subcomponents. Under na¨ıve allocation, price volatility grows with agent count and load ( _σp_ = 0 _._ 34 for SP at _N_ = 60/high); under hybrid allocation, volatility remains at or below _σp_ = 0 _._ 10, a reduction of 70–75%. An EMA-only ablation (efficiency = 1 _._ 0) confirms that EMA smoothing accounts for the majority of the volatility reduction (e.g., SP/high/ _N_ = 60: _σ_ = 0 _._ 097), while latency and welfare improvements depend on the efficiency factor (315 ms EMA-only vs. 181 ms full hybrid). The benefit is concentrated in the congestedbut-not-saturated regime; beyond saturation, no architectural intervention overcomes fundamental capacity constraints.

_Governance (G) and component interaction:_ The governance ablation (120 runs) varies trust-gated capacity partitioning from none to strict (70/30 split with trust threshold _≥_ 0 _._ 75). Governance trades throughput for quality: for entangled/high load, strict governance reduces median latency by 34% (from 404 to 266 ms) by excluding congestion-prone allocations, but halves service coverage. A secondary effect is that governance _induces_ price volatility even in structurally stable topologies, because capacity partitioning creates smaller subpools that saturate more easily. An architecture _×_ governance interaction experiment (240 runs) shows that the hybrid architecture substantially mitigates this governance-induced volatility (SP/medium: _σ_ from 0 _._ 78 to 0 _._ 20, a 75% reduc-

tion). Formal synergy testing reveals three topology-dependent interaction regimes: additive for SP (components deploy independently), sub-additive for tree/high (governance adds less when hybrid is active), and mildly super-additive for entangled (complementary benefits). Detailed interaction results are in the supplementary material.

_Market mechanism (M):_ Experiments 1–5 all use the tˆatonnement market mechanism; the mechanism ablation (480 runs) tests whether this price-based coordination adds value over simpler alternatives by comparing four allocation rules: random feasible packing, earliest-deadline-first (EDF), value-greedy (packing by expected value E[ _V_ ] with no prices), and the full market. The market and value-greedy produce near-identical outcomes across all conditions (welfare difference _<_ 1%): under truthful bidding, tˆatonnement prices converge to near-zero, making surplus ordering equivalent to value ordering. The value model itself is the primary driver of allocation quality, yielding a 32 _×_ welfare improvement over random allocation for the entangled topology at medium load (8 _._ 4 vs. 0 _._ 26 a.u.) by identifying tasks with sufficient deadline slack to survive high-congestion paths. For SP topologies under certain conditions, simpler heuristics (random, EDF) outperform value-greedy through implicit load balancing, demonstrating that value-optimal allocation can be welfare-suboptimal when it concentrates demand. These findings confirm that the market mechanism’s contribution under truthful bidding is not informational but incentivetheoretic; its value would emerge under strategic behaviour, where agents could inflate reported values to manipulate nonmarket baselines.

## VI. DISCUSSION AND FUTURE DIRECTIONS

The evaluation results have several implications for the design and operation of real-time AI service systems.

_Structural design of AI pipelines:_ The strong dependence of system performance on DAG topology (Sect. V-B) suggests that the structural organisation of AI service pipelines should be treated as a first-class design concern, not merely an implementation detail. Service architects should favour treelike and series–parallel compositions where possible, as these preserve the polymatroidal properties that enable tractable orchestration (Prop. 1). This aligns with modularity principles emerging in edge-cloud orchestration [2] and extends them with a formal rationale grounded in mechanism design.

_Safe integration of agentic behaviour:_ The hybrid architecture demonstrates that autonomous agents can participate in service negotiation without destabilising the system, provided the market-facing service abstractions are encapsulated (Sect. V-B). The up to 70–75% reduction in price volatility achieved by the hybrid integrator, without sacrificing throughput or latency, confirms that encapsulation into slice interfaces is an effective practical strategy for absorbing the complexity of multi-tier service markets. The ablation study (supplementary material) further shows that the EMA pricesmoothing mechanism is the primary driver of this stability gain, while the efficiency factor, modelling the internal scheduling optimisation inherent to encapsulation, primarily

IEEE TRANSACTIONS ON SERVICES COMPUTING

10

improves latency and welfare. Importantly, the efficiency factor is not an independent tuning knob but an architectural consequence: an integrator that manages a sub-DAG internally can schedule tasks more efficiently than per-tier allocation exposes, yielding a natural demand-reduction effect. This finding is relevant to the broader trend toward intent-driven networking and dynamic service slicing in 5G/6G systems [43], [46], where agentic workloads are expected to grow.

_Governance as a structural component:_ The governance experiments (Sect. V-B) reveal that trust and policy constraints actively reshape the system’s operating regime rather than merely filtering an otherwise fixed optimisation. By construction, all allocated tasks are policy-compliant (compliance = 100%), but stricter governance reduces service coverage, the fraction of tasks that receive any allocation. For the entangled topology under high load, strict governance reduced median latency by 34% (from 404 to 266 ms) at the cost of halving service coverage. This demonstrates that governance trades throughput for quality: fewer tasks are served, but those that are served experience materially better outcomes.

The current governance model (capacity partitioning with trust-gated access) represents one point in a broader design space; richer models incorporating data-locality restrictions, cross-domain policy negotiation, and dynamic trust evolution would likely amplify the observed trade-offs (see supplementary material for an extended discussion). System designers must explicitly navigate the efficiency–compliance trade-off, potentially adjusting governance strictness dynamically based on current topology and load conditions [23], [24].

_Interplay of topology, governance, and load:_ The simulation results show that the three factors interact nontrivially: governance effects are most pronounced for entangled DAGs near capacity and less visible for tree-like topologies at moderate load. Similarly, the hybrid architecture’s pricestabilisation benefit is most valuable in the congested-butnot-saturated regime; beyond saturation, no architectural intervention overcomes fundamental capacity constraints. The topology-dependent scaling behaviour of Exp. 2 (supp. material) reinforces this point. This interaction suggests that management policies should be adaptive, adjusting governance strictness and architectural encapsulation based on current topology and load conditions rather than applying uniform rules.

_Robustness of findings:_ The simulation findings vary in their sensitivity to model specifics. _Structural findings_ , that topology governs market stability (Sect. V-B), that encapsulation restores tractability (Sect. V-B), and that the market matches a centralised oracle under truthful bidding (Sect. V-B), follow from the polymatroidal structure established in Prop. 1 and hold across all tested parameter configurations; they are likely robust to model details. _Quantitative findings_ , such as exact volatility-reduction percentages, latency improvements, welfare magnitudes, and the specific conditions under which SP topologies exhibit the congestion reversal, depend on the parameterisation of arrival rates, deadline distributions, tier capacities, and the efficiency-factor model. These should be interpreted as indicative of the direction and relative magnitude of effects rather than as precise predictions for production

deployments.

_Broader implications for real-time AI service markets:_ The theoretical results of Sect. IV establish that the distinction between structurally disciplined and entangled dependency graphs is not one of degree but of kind: for entangled DAGs, Walrasian equilibria may fail to exist and welfare maximisation is NP-hard—under standard complexity assumptions, no polynomial-time algorithm can guarantee an efficient allocation. The simulations quantify this gap (Sect. V-B). In the latency-sensitive domains motivating this work, such structural market failures translate into an inability to sustain time-critical service composition. Because the hybrid architecture restores tractability through encapsulation (Prop. 3), the choice of dependency topology becomes a design-time structural commitment with long-term consequences for market viability, not an optimisation parameter that can be tuned post-deployment; retrofitting encapsulation onto an alreadydeployed entangled pipeline requires restructuring the servicedependency graph. These findings suggest that emerging standardisation efforts for AI service composition and network slicing [43], as well as nascent protocols for agent-driven economic transactions [4], should explicitly account for dependency topology as a determinant of whether stable, marketbased coordination is achievable. Recent empirical evidence reinforces this point: Shapira et al. [9] show that AI agents operating without structural safeguards exhibit cascading failures, unauthorised resource consumption, and identity spoofing— precisely the instabilities that the DSIC and polymatroidal guarantees developed here are designed to preclude.

_Mechanism value under truthful bidding:_ The mechanism ablation (Sect. V-B) shows that the tˆatonnement market and a value-greedy oracle (which requires full knowledge of every agent’s valuation) produce near-identical welfare (difference _<_ 1%). Under a polymatroidal structure, greedy allocation is provably welfare-optimal (Edmonds’ theorem; see supplementary material), so this equivalence is expected. Crucially, it obtains _because_ agents report truthfully, not despite it: a value-greedy rule allocates by reported value, giving any strategic agent an incentive to inflate its bid. The market mechanism’s contribution is therefore not informational but _incentive-theoretic_ : the DSIC property (Prop. 2) makes truthful reporting a dominant strategy, causing agents to voluntarily reveal private valuations that a centralised planner could not obtain across trust and organisational boundaries. Without this guarantee, the very baseline that matches the market would break down under strategic behaviour. The ablation also reveals that value-optimal allocation can be welfaresuboptimal for SP topologies, where concentrating capacity on high-value tasks increases congestion externalities; simpler heuristics achieve better outcomes through implicit load balancing, suggesting that practical deployments should incorporate congestion-aware rules even when the structural conditions for DSIC are satisfied.

_Theoretical positioning:_ The individual mechanismdesign results instantiate classical polymatroid theory, the gross-substitutes characterisation, and VCG design in a novel domain; the paper’s contribution is problem formulation (identifying that AI service-dependency graphs have the right

IEEE TRANSACTIONS ON SERVICES COMPUTING

11

structure for these classical results) and the architectural consequence of encapsulation (Prop. 3), which makes the classical results operationally deployable (see supplementary for an extended discussion).

_Limitations:_ The simulations model resource allocation and queueing dynamics under the structural regimes identified by the theory, but do not implement the full auction mechanisms from Sect. IV with strategically behaving agents. In particular, truthful reporting is assumed rather than tested, and VCG or clinching-auction dynamics are not simulated. The mechanism ablation (Sect. V-B) confirms that under this assumption the market mechanism’s allocation is indistinguishable from a non-market value-greedy baseline, isolating incentive alignment as the untested theoretical contribution and motivating the strategic extension below. Of the ten modelling assumptions enumerated in the supplementary material, two are not exercised: time-varying capacities (assumption v) and strategic misreporting (assumption vii). The stylised DAG topologies capture qualitative structural effects but do not reflect the full complexity of production AI pipelines. Agents bid using power-law congestion estimates while execution follows a queueing model on the DAG critical path; this intentional mismatch models realistic information asymmetry, partially compensated by online success learning.

_Toward strategic agent behaviour:_ Under strategic behaviour, agents would inflate reported values to gain priority, degrading welfare. The market mechanism’s role would shift from redundant to essential: the DSIC property would sustain truthful reporting as a dominant strategy, preventing manipulation that would undermine any non-market baseline. Testing this hypothesis could proceed by replacing tˆatonnement with ascending clinching auctions [37] (applicable in the singletype-per-task case; see Prop. 2), introducing RL agents to test whether learning dynamics destabilise allocation under different topologies, and extending integrator pricing to posted-price mechanisms with commitment. These extensions would bridge the gap between the theoretical results of Sect. IV and the operational simulation.

_Future directions:_ Beyond strategic behaviour, several research directions follow naturally. First, the structural analysis could be extended to _dynamically evolving pipelines_ where services recompose at runtime, raising open questions about stability under structural change. Second, _richer governance models_ , incorporating auditability, privacy guarantees, and cross-domain coordination with expressive policy languages, would strengthen the framework’s practical applicability. Third, while encapsulation restores tractability at the market layer, it shifts the complexity of managing nonpolymatroidal sub-DAGs into the integrators themselves. The simulation’s efficiency factors (0 _._ 75–0 _._ 85) quantify this cost under a simple scheduling model, but determining optimal _internal management strategies_ for integrators (e.g., centralised optimisation, learning-based scheduling, or adaptive overprovisioning), as well as optimal _slicing and encapsulation boundaries_ including semantics-aware variants [46], remains an important open problem. Relatedly, the current framework treats integrators as non-strategic infrastructure; modelling integrators as self-interested agents that may misreport ca-

pacity or extract rents, and determining whether competition among integrators or regulatory constraints suffice to prevent monopoly pricing, is an open mechanism design question. One practical avenue is implementing integrator logic as smart contracts, which would make encapsulation rules and pricing transparent and immutable, enforcing the non-strategic role by construction. Finally, deploying the architecture in _realistic testbeds_ would provide insights into interoperability, overheads, and operational complexity, and help validate the theoretical and simulation-based findings of this work.

## VII. CONCLUSION

We presented a framework for managing real-time AI services across the device–edge–cloud continuum under agentic computing. The main analytical results establish that when service-dependency graphs have tree or series–parallel structure, the feasible allocation space is polymatroidal (Prop. 1), latency-aware valuations satisfy the gross-substitutes condition under slice encapsulation (Lemma 1), and, within each decision epoch, efficient, incentive-compatible mechanisms exist, with the ascending clinching auction additionally guaranteeing weak budget balance in the single-type-per-task case (Prop. 2). For arbitrary dependency graphs, these properties can break down due to complementarities; however, architectural encapsulation by integrators can restore polymatroidal structure at the agent-facing interface (Prop. 3). Based on this structural analysis, we proposed a hybrid architecture in which cross-domain integrators encapsulate complex service compositions into slices, exposing tractable resource interfaces to autonomous agents. A systematic ablation study confirmed these structural predictions and showed that the decentralised market replicates centralised-quality allocation under truthful bidding, without requiring a single controlling authority. The DSIC guarantee (Prop. 2) sustains this truthful bidding in cross-domain deployments, causing agents to voluntarily reveal private valuations that centralised planning would require but could not obtain.

The mechanism ablation motivates the most immediate open challenge: implementing and validating the proposed auction mechanisms (ascending clinching auctions, VCG) under strategic agent behaviour, where the DSIC guarantee would shift from theoretically redundant to operationally essential. Further challenges include extending the structural analysis to dynamically evolving pipelines and deploying the architecture in realistic multi-domain testbeds. As real-time AI service ecosystems grow in scale and criticality, the structural properties identified here, polymatroidal feasibility, gross-substitutes valuations, and encapsulation-based tractability restoration, become prerequisites for reliable market-based coordination rather than merely desirable theoretical properties. The framework provides platform designers and infrastructure operators with formal criteria for distinguishing service architectures that can sustain stable autonomous coordination from those that structurally cannot.

## REFERENCES

[1] H. F. Shahid _et al._ , “Iot service orchestration in edge-cloud continuum with 6g: A review,” _IEEE Internet of Things Journal_ , 2026.

IEEE TRANSACTIONS ON SERVICES COMPUTING

12

- [2] T. Meuser, L. Lov´en _et al._ , “Revisiting edge AI: Opportunities and challenges,” _IEEE Internet Computing_ , vol. 28, no. 4, pp. 49–59, 2024.

- [3] S. Deng _et al._ , “Agentic services computing,” 2025, arXiv preprint arXiv:2509.24380.

- [4] Google Cloud, “Announcing agent payments protocol (AP2),” Google Cloud Blog, 2025, accessed: 2026-02-21. [Online]. Available: https://cloud.google.com/blog/products/ai-machine-learning/ announcing-agents-to-payments-ap2-protocol

- [5] P. K. Donta _et al._ , “Socio-technical aspects of agentic ai,” 2025. [Online]. Available: https://arxiv.org/abs/2601.06064

- [6] H. Kokkonen _et al._ , “Autonomy and intelligence in the computing continuum: Challenges, enablers, and future directions for orchestration,” _arXiv preprint arXiv:2205.01423_ , 2022.

- [7] N. Fornara, _Specifying and Monitoring Obligations in Open Multiagent Systems Using Semantic Web Technology_ . Berlin, Heidelberg: Springer Berlin Heidelberg, 2011, pp. 25–45.

- [8] R. P. McAfee, “A dominant strategy double auction,” _Journal of Economic Theory_ , vol. 56, no. 2, pp. 434–450, 1992.

- [9] N. Shapira _et al._ , “Agents of chaos,” 2026, arXiv preprint arXiv:2602.20021.

- [10] F. Gul and E. Stacchetti, “Walrasian equilibrium with gross substitutes,” _Journal of Economic theory_ , vol. 87, no. 1, pp. 95–124, 1999.

- [11] H. Hu _et al._ , “Intelligent resource allocation for edge-cloud collaborative networks: A hybrid ddpg-d3qn approach,” _IEEE Transactions on Vehicular Technology_ , vol. 72, no. 8, pp. 10 696–10 709, 2023.

- [12] Y. Liu _et al._ , “Data orchestration service placement and resource allocation scheme for cloud-edge system,” _IEEE Transactions on Services Computing_ , 2026.

- [13] C. Tang _et al._ , “Collaborative service caching, task offloading, and resource allocation in caching-assisted mobile edge computing,” _IEEE Transactions on Services Computing_ , 2025.

- [14] S. Li _et al._ , “Tiered-pricing-based task offloading strategy in collaborative edge-cloud computing: A matching game approach,” _IEEE Internet of Things Journal_ , vol. 12, no. 11, pp. 15 114–15 129, 2025.

- [15] I. Taleb _et al._ , “A survey on services placement algorithms in integrated cloud-fog/edge computing,” _ACM Computing Surveys_ , vol. 57, no. 11, pp. 1–36, 2025.

- [16] X. Xie _et al._ , “Coedge: A collaborative architecture for efficient task offloading among multiple edge service providers,” _IEEE Internet of Things Journal_ , 2025.

- [17] C. Shang _et al._ , “Joint computation offloading and service caching in mobile edge-cloud computing via deep reinforcement learning,” _IEEE Internet of Things Journal_ , vol. 11, no. 24, pp. 40 331–40 344, 2024.

- [18] H. Hantouti _et al._ , “Service function chaining in 5g & beyond networks: Challenges and open research issues,” 2022, arXiv preprint arXiv:2201.05455.

- [19] W. Fan _et al._ , “Drl-based service function chain edge-to-edge and edgeto-cloud joint offloading in edge-cloud network,” _IEEE Transactions on Network and Service Management_ , vol. 20, no. 4, pp. 4478–4493, 2023.

- [20] M. R. G. Oskoui and B. Sans`o, “Distributed dependency-aware task offloading and service caching in cloudlet-based edge computing networks,” _IEEE Transactions on Services Computing_ , 2026.

- [21] J. S. Park _et al._ , “Generative agents: Interactive simulacra of human behavior,” in _Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology_ , ser. UIST ’23. New York, NY, USA: Association for Computing Machinery, 2023.

- [22] B. Sedlak _et al._ , “Service orchestration in the computing continuum: Structural challenges and vision,” 2026, arXiv preprint arXiv:2602.15794.

- [23] H. Li and M. Singhal, “ Trust Management in Distributed Systems ,” _Computer_ , vol. 40, no. 02, pp. 45–53, Feb. 2007.

- [24] X. Wang _et al._ , “A survey on trustworthy edge intelligence: From security and reliability to transparency and sustainability,” _IEEE Communications Surveys & Tutorials_ , vol. 27, no. 3, pp. 1729–1757, 2025.

- [25] C. Weinhardt _et al._ , “Cloud computing – a classification, business models, and research directions,” _Business & Information Systems Engineering_ , vol. 1, no. 5, pp. 391–399, 2009.

- [26] U. Habiba _et al._ , “A repeated auction model for load-aware dynamic resource allocation in multi-access edge computing,” _IEEE Transactions on Mobile Computing_ , vol. 23, no. 7, pp. 7801–7817, 2023.

- [27] X. Zheng _et al._ , “Resource allocation and network pricing based on double auction in mobile edge computing,” _Journal of Cloud Computing_ , vol. 12, no. 1, p. 56, 2023.

- [30] S. Bikhchandani and J. W. Mamer, “Competitive equilibrium in an exchange economy with indivisibilities,” _Journal of Economic Theory_ , vol. 74, no. 2, pp. 385–413, 1997.

- [31] J. Edmonds, “Submodular functions, matroids, and certain polyhedra,” in _Combinatorial Optimization—Eureka, You Shrink!_ Berlin, Heidelberg: Springer-Verlag, 2003, pp. 11–26, originally published in _Combinatorial Structures and their Applications_ , Gordon and Breach, 1970.

- [32] L. M. Ausubel and P. Milgrom, “The lovely but lonely Vickrey auction,” in _Combinatorial Auctions_ , P. Cramton, Y. Shoham, and R. Steinberg, Eds. MIT Press, 2006, pp. 17–40.

- [33] A. S. Kelso and V. P. Crawford, “Job matching, coalition formation, and gross substitutes,” _Econometrica_ , vol. 50, no. 6, pp. 1483–1504, 1982.

- [34] F. Gul and E. Stacchetti, “Walrasian equilibrium with gross substitutes,” _Journal of Economic Theory_ , vol. 87, no. 1, pp. 95–124, 1999.

- [35] S. Fujishige and Z. Yang, “A note on Kelso and Crawford’s gross substitutes condition,” _Mathematics of Operations Research_ , vol. 28, no. 3, pp. 463–469, 2003.

- [36] G. Goel _et al._ , “Polyhedral clinching auctions and the adwords polytope,” _Journal of the ACM_ , vol. 62, no. 3, pp. 1–27, 2015.

- [37] L. M. Ausubel, “An efficient ascending-bid auction for multiple objects,” _American Economic Review_ , vol. 94, no. 5, p. 1452–1475, December 2004.

- [38] N. Nisan, “Bidding and allocation in combinatorial auctions,” in _Combinatorial Auctions_ , P. Cramton, Y. Shoham, and R. Steinberg, Eds. MIT Press, 2006, pp. 215–244.

- [39] M. H. Rothkopf _et al._ , “Computationally manageable combinational auctions,” _Management Science_ , vol. 44, no. 8, pp. 1131–1147, 1998.

- [40] B. Lehmann _et al._ , “Combinatorial auctions with decreasing marginal utilities,” in _Proceedings of the 3rd ACM Conference on Electronic Commerce_ . ACM, 2001, pp. 18–28, extended version in _Games and Economic Behavior_ , 55(2):270–296, 2006.

- [41] R. B. Myerson and M. A. Satterthwaite, “Efficient mechanisms for bilateral trading,” _Journal of Economic Theory_ , vol. 29, no. 2, pp. 265– 281, 1983.

- [42] R. Fatima _et al._ , “Resource management in the edge–cloud continuum: Trends, algorithms, and open challenges,” _Journal of Systems Engineering and Electronics (ISSN NO: 1671-1793)_ , vol. 35, no. 12, 2025.

- [43] X. Foukas _et al._ , “Network slicing in 5G: Survey and challenges,” _IEEE Communications Magazine_ , vol. 55, no. 5, pp. 94–100, 2017.

- [44] L. Lov´en _et al._ , “Agentic edge intelligence: A research agenda,” in _Proceedings of the 18th IEEE/ACM International Conference on Utility and Cloud Computing_ , ser. UCC ’25. New York, NY, USA: Association for Computing Machinery, 2026.

- [45] Z. Zhou _et al._ , “Edge intelligence: Paving the last mile of artificial intelligence with edge computing,” _Proceedings of the IEEE_ , vol. 107, no. 8, pp. 1738–1762, 2019.

- [46] L. Lov´en _et al._ , “Semantic slicing across the distributed intelligent 6G wireless networks,” in _Proc. IEEE SECON_ , Madrid, Spain, 2023.

**Lauri Lov´en** is an Assistant Professor (tenure track) and head of the Future Computing Group at the University of Oulu, Finland.

**Alaa Saleh** is a doctoral candidate at the Future Computing Group, in the Center for Applied Computing, University of Oulu, Finland.

**Reza Farahani** is a Postdoctoral Researcher and Lecturer at the University of Klagenfurt, Austria.

**Ilir Murturi** is an Assistant Professor at the University of Prishtina and an external Senior Researcher at the Distributed Systems Group, TU Wien.

**Sujit Gujar** is an Associate Professor and the CA Technologies Faculty Chair at the International Institute of Information Technology, Hyderabad (IIITH), India.

**Miguel Bordallo L´opez** is an Associate Professor with the University of Oulu, where he leads distributed intelligence research at the 6G Flagship program.

**Praveen Kumar Donta** is associate professor (docent) at the Department of Computer and Systems Sciences, Stockholm University, Sweden.

**Schahram Dustdar** is Full Professor of Computer Science heading the Research Division of Distributed Systems at the TU Wien, Austria, and ICREA Research Professor in Barcelona, Spain.

- [28] K. Murota, _Discrete Convex Analysis_ , ser. Monographs on Discrete Mathematics and Applications. SIAM, 2003.

- [29] S. Fujishige, _Submodular Functions and Optimization_ , 2nd ed. Elsevier, 2005, vol. 58.
