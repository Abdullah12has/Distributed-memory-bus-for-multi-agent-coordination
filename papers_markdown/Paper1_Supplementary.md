1

## Supplementary Material for “Real-Time AI Service Economy: A Framework for Agentic Computing Across the Continuum”

This document provides supplementary material for the main paper, including background definitions with a full notation reference, detailed proof sketches, a related work comparison, simulation parameter specifications with result summary tables, and detailed statistical analysis.

## I. BACKGROUND DEFINITIONS

The formal results in the main paper rely on three standard concepts from combinatorial optimisation and economic theory. We collect their definitions here for self-containedness; readers familiar with these concepts may proceed directly to the proofs. Notation is provided in Table I.

## _A. Polymatroid_

**Definition 1** (Polymatroid) **.** _Let E be a finite ground set and ρ_ : 2 _[E] →_ R _≥_ 0 _a set function that is (i)_ normalised _: ρ_ ( _∅_ ) = 0 _; (ii)_ monotone _: S ⊆ T ⇒ ρ_ ( _S_ ) _≤ ρ_ ( _T_ ) _; and (iii)_ submodular _: ρ_ ( _S ∪{e}_ ) _− ρ_ ( _S_ ) _≥ ρ_ ( _T ∪{e}_ ) _− ρ_ ( _T_ ) _for all S ⊆ T and e ∈/ T . The_ polymatroid _associated with ρ is the polytope_

_P_ ( _ρ_ ) = � _x ∈_ R _[E] ≥_ 0[:] _[ x]_[(] _[S]_[)] _[ ≤][ρ]_[(] _[S]_[)] _[ for][all][S][⊆][E]_ � _,_

_where x_ ( _S_ ) =[�] _e∈S[x][e][.][The][function][ρ][is][called][the]_[rank] function _of the polymatroid [1], [2]._

_Intuition._ A polymatroid captures a system of capacity constraints with diminishing returns: the more resources already committed within a subset, the less additional throughput any new resource can contribute. In the context of this paper, the ground set _E_ corresponds to the leaf services consumed by agents, and the rank function _ρ_ encodes the bottleneck capacities imposed by internal nodes of the service-dependency DAG. When the DAG is a tree or series–parallel network, its constraint sets form a _laminar_ (nested) family, and the resulting feasible region is a polymatroid. This structure is important for two reasons: (i) Edmonds’ [1] greedy algorithm maximises any separable concave objective (including social welfare) over a polymatroid in polynomial time, and (ii) polymatroidal feasible sets are compatible with gross-substitutes valuations, jointly guaranteeing market equilibrium existence.

## _B. Walrasian (Competitive) Equilibrium_

**Definition 2** (Walrasian Equilibrium) **.** _An allocation–price pair_ ( _x[∗] , p[∗]_ ) _is a_ Walrasian _(or_ competitive _)_ equilibrium _if (i) every agent maximises its utility at prices p[∗] , and (ii) aggregate demand equals aggregate supply (market clearing)._

_Intuition._ A Walrasian equilibrium is a vector of perresource prices at which every agent is individually satisfied

with its allocation and no resource is over- or under-demanded. Its existence implies that fully decentralised coordination via prices alone can replicate the outcome of a benevolent central planner. The Kelso–Crawford [3] fixed-point argument guarantees existence whenever agents’ valuations satisfy the gross-substitutes condition (defined below), which holds in this paper’s setting under slice encapsulation (Lemma 1 in the main paper).

## _C. Gross Substitutes and Dominant-Strategy Incentive Compatibility_

**Definition 3** (Gross-Substitutes (GS) Condition) **.** _An agent’s valuation function satisfies the_ gross-substitutes _condition if, whenever the price of one item increases (with all other prices unchanged), the agent’s demand for every other item whose price did not change weakly increases [4]._

**Definition 4** (Dominant-Strategy Incentive Compatibility (DSIC)) **.** _A mechanism is_ dominant-strategy incentive compatible _(DSIC) if truthful reporting of valuations maximises each agent’s utility regardless of what other agents report [5]._

_Intuition._ The GS condition captures the idea that resources are interchangeable rather than complementary: raising the price of one service slice causes an agent to substitute towards alternatives rather than to abandon the market entirely. This rules out the “I need both or neither” complementarity pattern that makes combinatorial auctions intractable. When GS holds on a polymatroidal feasible set, classical results [4], [3] guarantee the existence of a Walrasian equilibrium, and the VCG mechanism implements the welfare-maximising allocation in dominant strategies (DSIC): no agent can gain by misreporting, making the market robust to strategic behaviour. Under additional single-parameter conditions (e.g., when each task maps to a unique slice type so that each bidder’s private information is a scalar willingness-to-pay), the ascending clinching auction [6], [7] provides an alternative DSIC implementation with the added benefit of weak budget balance.

## II. PROOF DETAILS

## _A. Proof of Proposition 1 (Polymatroidal Structure under Tree/SP DAGs)_

**Proposition 1** (Polymatroidal Structure under Tree/SP DAGs) **.** _Let G_ res _be a rooted tree or two-terminal series–parallel network with node capacities Cv >_ 0 _. Then:_

- (i) _the capacity function f (the rank function defined by the laminar constraint family) is submodular, monotone, and normalised (f_ ( _∅_ ) = 0 _);_

2

TABLE I

SUMMARY OF NOTATION

|**Symbol**|**Meaning**|
|---|---|
|_A_|Set of agents (consumers, providers, integrators, AI agents)|
|_t_<br>_θi_(_t_)<br>Θ_i_|Discrete time index, _t_= 1_,_2_, . . ._<br>Type of agent _i_ at time _t_<br>Type space for agent _i_|
|_ℓi_|Physical location or region of agent _i_|
|_Bi_(_t_)<br>_Ti_(_t_)<br>_κi_<br>_ρi_<br>_ϕi_(_t_)<br>_ηk_(_t_)<br>_qk_<br>_d_max<br>_k_<br>_λk_|Budget or credit of agent _i_<br>Tasks issued or served by agent _i_<br>Capabilities of agent _i_<br>Role of agent _i_ (consumer, provider, integrator)<br>Governance attributes (trust, compliance, policy fags)<br>Parameters of task _k_ (quality, deadline, sensitivity)<br>Quality or workload of task _k_<br>Maximum acceptable latency (deadline)<br>Latency sensitivity parameter|
|_Tik_|Latency experienced by task _k_ served by agent _i_|
|_vik_(_q_)|Base value from completing task _k_ at quality _q_|
|_δik_(_T_)<br>_Vik_(_T, q_)|Latency discount factor<br>Latency-aware task value for agent _i_|
|_R_<br>_Cr,ℓ_(_t_)<br>_G_res<br>_L_(_G_)<br>_f_<br>_st_|Set of service types<br>Capacity of service _r_ at location _ℓ_<br>Service–dependency DAG<br>Set of leaf services in DAG _G_<br>Polymatroid rank function of _X_res<br>System state at time _t_|
|Λ(_t_)|Network latency conditions across the continuum|
|_D_(_t_)|Exogenous demand or load|
|_R_(_t_)<br>_ri_(_t_)<br>_G_(_t_)|Reputation or trust states of all agents<br>Reputation score of agent _i_, _ri_(_t_)_∈_[0_,_1]<br>Governance/policy state at time _t_|
|_xt_<br>_Pi_(_t_)<br>_Xt_<br>_X_res|Allocation at time _t_<br>Net payment by agent _i_ (_>_0: pays; _<_0: receives)<br>Feasible allocation set<br>Service- and DAG-based feasibility constraints|
|_X_gov<br>_mi_(_t_)<br>_Mi_<br>_M_<br>_W_(_t_)<br>_µ_<br>_ui_(_t_)|Governance feasibility constraints<br>Message sent by agent _i_<br>Message space for agent _i_ (= Θ_i_ under direct mechanisms)<br>Mechanism mapping messages to (_xt, P_(_t_))<br>Social welfare at time _t_<br>Externality trade-off parameter (_µ ≥_0)<br>Per-period utility of agent _i_|
|_γi_<br>cost_j_(_xt_)|Risk-aversion coeffcient<br>Operational cost of provider _j_ under allocation _xt_|



- (ii) _X_ res _is a polymatroid with rank function f ; and_

- (iii) _the base polytope B_ ( _f_ ) = _{x ∈X_ res : _x_ ( _L_ ( _G_ )) = _f_ ( _L_ ( _G_ )) _} is the set of tight allocations._

_Proof._ For tree-structured DAGs, the constraint sets _{Lv}_ form a laminar family by the nesting property of subtrees. Edmonds [1] established that the polytope _{x ≥_ 0 : _x_ ( _Lv_ ) _≤ Cv}_ defined by a laminar family is a polymatroid. Submodularity of _f_ follows from the structure of laminar covers: for any _S[′] ⊇ S_ and element _l ∈/ S[′]_ , the marginal contribution _f_ ( _S[′] ∪{l}_ ) _− f_ ( _S[′]_ ) is bounded by the capacity of the smallest constraint set containing _l_ , which can only become a tighter bottleneck as _S[′]_ grows [2]. Monotonicity is immediate from

non-negative capacities; _f_ ( _∅_ ) = 0 is trivial.

For series–parallel (SP) networks, we use the standard recursive definition of two-terminal SP graphs (see, e.g., [2]). An SP graph _G_ = ( _V, E_ ) with designated source _s_ and sink _t_ is built from primitive edges via series and parallel composition. We adopt the following structural conventions, which are maintained as invariants throughout the induction:

- **(I1)** _Leaf semantics._ The leaf set _L_ ( _G_ ) consists of all sinkadjacent terminal nodes that correspond to services consumed by agents. Every internal (non-leaf) node _v_ has a well-defined leaf block _Lv_ = _{l ∈ L_ ( _G_ ) : _l_ is reachable from _v}_ .

- **(I2)** _Disjoint components._ Before composition, the two component graphs _G_ 1 _, G_ 2 have disjoint node sets (except for the identified glue node in series composition).

- **(I3)** _Glue-node semantics._ In series composition _G_ = _G_ 1 _·G_ 2 (identifying _t_ 1 = _s_ 2), the glue node _t_ 1 = _s_ 2 becomes internal in _G_ , and its leaf block in _G_ is the union of the leaves reachable through _G_ 2 and any leaves reachable through _G_ 1 via the glue node. Specifically, for any node _v_ in _G_ 1 that is an ancestor of _t_ 1, the composed leaf block is _Lv_ = _L_[(1)] _v ∪ L_ ( _G_ 2), where _L_[(1)] _v_ = _{l ∈ L_ ( _G_ ) _∩ V_ ( _G_ 1) : _l_ reachable from _v}_ is the restriction of _v_ ’s reachable leaves to those that remain leaves in _G_ (excluding _t_ 1, which becomes internal).

_Induction hypothesis:_ for any SP graph built from fewer than _k_ primitive edges satisfying (I1)–(I3), the family _{Lv_ : _v_ internal _}_ is laminar (every two members are nested or disjoint).

_Base case._ A single edge ( _s, t_ ) with capacity _Cs_ : here _s_ is the sole internal node and _t_ is the sole leaf, so the family _L_ = _{Ls}_ = _{{t}}_ is indexed by the single internal node _s_ and is trivially laminar. Invariants (I1)–(I3) hold vacuously.

_Series composition._ Let _G_ 1 (source _s_ 1, sink _t_ 1) and _G_ 2 (source _s_ 2, sink _t_ 2) have laminar families _L_ 1 and _L_ 2 over disjoint leaf sets _L_ 1 and _L_ 2, respectively (by invariant (I2)). The composed graph _G_ = _G_ 1 _· G_ 2 identifies _t_ 1 = _s_ 2, with source _s_ 1 and sink _t_ 2. Consider any two members _Lv, Lw_ in the composed family _L_ . There are three cases: (a) both _v, w_ lie in _G_ 2, so _Lv, Lw ∈L_ 2 and laminarity follows by induction; (b) _v_ lies in _G_ 1 and _w_ in _G_ 2: if _v_ is an ancestor of _t_ 1 in _G_ 1, then _Lv_ = _L_[(1)] _v ∪ L_ 2 where _L_[(1)] _v ⊆ L_ 1, and _Lw ⊆ L_ 2, so _Lw ⊂ Lv_ (nested); if _v_ is not an ancestor of _t_ 1, then _Lv ⊆ L_ 1 and _Lw ⊆ L_ 2, hence disjoint; (c) both _v, w_ lie in _G_ 1: every internal node of a two-terminal SP graph lies on a source–sink path, so all internal nodes of _G_ 1 reach _t_ 1; thus both _v_ and _w_ are ancestors of _t_ 1. We show their composed leaf blocks are nested. The sink of any SP graph produced by this construction is always a leaf (base case: _t_ is the sole leaf; parallel composition: the shared sink remains terminal; series composition: the new sink _t_ 2 is a leaf of _G_ 2 by induction). Since both _v_ and _w_ reach _t_ 1 and _t_ 1 _∈ L_ ( _G_ 1), the leaf blocks of _v_ and _w within G_ 1 _’s own leaf set_ (which includes _t_ 1) both contain _t_ 1. Hence these _G_ 1-leaf-blocks are not disjoint; laminarity of _L_ 1 forces nesting, say the _G_ 1-leaf-block of _v_ is contained in that of _w_ . Removing _t_ 1 preserves the inclusion: _L_[(1)] _v ⊆ L_[(1)] _w_[.][Therefore] _[L] v_[=] _[L]_[(1)] _v ∪ L_ 2 _⊆ L_[(1)] _w[∪][L]_ 2[=] _[L] w_

3

(nested). Hence _L_ is laminar.

_Invariant preservation (series)._ (I1): the leaf set of _G_ is _L_ 1 _∪ L_ 2; the glue node _t_ 1 = _s_ 2 is internal, and every internal node _v_ has a well-defined _Lv_ as constructed above. (I2): the only shared node is the glue node _t_ 1 = _s_ 2; all other nodes are disjoint by induction. (I3): for any ancestor _v_ of the glue node in _G_ 1, the composed leaf block _Lv_ = _L_[(1)] _v ∪ L_ ( _G_ 2) is exactly the definition in (I3). For nodes in _G_ 2 or non-ancestor nodes in _G_ 1, leaf blocks are unchanged. Hence (I1)–(I3) are preserved.

_Parallel composition._ Let _G_ 1 and _G_ 2 share source _s_ and sink _t_ , with disjoint internal nodes and laminar families _L_ 1 _, L_ 2 over disjoint leaf sets _L_ 1 _, L_ 2 (by invariant (I2)). The composed family is _L_ = _L_ 1 _∪L_ 2 _∪{L_ 1 _∪L_ 2 _}_ , where _L_ 1 _∪L_ 2 = _Ls_ is the leaf set of source _s_ . Members within _L_ 1 (resp. _L_ 2) are laminar by induction; any _Lv ∈L_ 1 and _Lw ∈L_ 2 satisfy _Lv ⊆ L_ 1 and _Lw ⊆ L_ 2, hence disjoint; and _Ls_ contains all members as subsets. Hence _L_ is laminar.

_Invariant preservation (parallel)._ (I1): the leaf set of _G_ is _L_ 1 _∪ L_ 2; the shared source _s_ has leaf block _Ls_ = _L_ 1 _∪ L_ 2, and all other internal nodes retain their original leaf blocks. (I2): _G_ 1 and _G_ 2 share only _s_ and _t_ ; internal nodes are disjoint by induction. (I3): no glue-node identification occurs (the shared source and sink are already present in both components), so (I3) applies vacuously. Hence (I1)–(I3) are preserved.

Since _L_ is laminar in both cases, the rank function _f_ is submodular by the standard laminar-family result [1], [2], and the composed feasible region is a polymatroid. Parts (ii) and (iii) are standard consequences of the polymatroid definition [2].

## _B. Proof of Lemma 1 (GS Valuations under Slice Encapsulation)_

**Lemma 1** (GS Valuations under Slice Encapsulation) **.** _Suppose integrators encapsulate multi-resource service paths into composite_ slices _, where each slice s is a discrete, indivisible unit with fixed internal routing, deterministic latency Ts, and quality qs. Suppose further that: (a) each agent requires at most one slice per task (unit demand); (b) an agent’s tasks are_ additively separable _—its valuation decomposes as a sum across tasks with no cross-task complementarity or shared feasibility coupling; and (c) within each mechanism epoch, slice attributes_ ( _Ts, qs_ ) _are determined by the current system state st and remain fixed throughout the allocation round. Then the agent’s induced valuation over slices satisfies the gross-substitutes condition._

_Proof._ Under encapsulation, agent _i_ ’s valuation for assigning task _k_ to slice _s_ is _Vik_ ( _Ts, qs_ ), where ( _Ts, qs_ ) are fixed within the current epoch by condition (c). Since each task requires exactly one slice, the agent selects whichever slice maximises _Vik_ ( _Ts, qs_ ) _−ps_ , where _ps_ is the slice price. This defines a unitdemand valuation. By Proposition 2 of Gul and Stacchetti [4], unit-demand valuations satisfy GS: raising the price of one slice causes the agent either to retain it or to switch to another, but never to drop demand for an unrelated slice whose price has not changed. For agents with multiple tasks, additive

separability (condition (b)) ensures the aggregate valuation is a finite sum of GS (specifically, unit-demand) valuations. Since finite sums of GS valuations are GS [4], additive task separability preserves the GS property. Note that shared agentside budgets, per-agent latency coupling, or shared token caps across tasks would generally break this additivity and can break GS. Note that slice capacities (the number of available units of each type) are determined by the polymatroid _X_ res; this is a feasibility condition relevant to Proposition 2 rather than a requirement for GS itself.

## _C. Proof Sketch of Proposition 2 (Efficient Mechanism Design under Structured DAGs)_

_Note._ The following proof sketch reduces each part to standard results from auction theory and discrete convex analysis; the underlying theorems are cited explicitly at each step rather than re-derived.

**Proposition 2** (Efficient Mechanism Design under Structured DAGs) **.** _Suppose Xt is polymatroidal, agents’ valuations satisfy the GS condition under slice encapsulation, agents have_ quasilinear _utility (value minus payment), and slices are discrete items with integral capacities. Then:_

- (i) _a Walrasian equilibrium exists in the discrete market of K heterogeneous slice types whose integer supply capacities are jointly governed by the polymatroidal feasibility region Xt (encoding both per-type upper bounds and cross-type bottleneck constraints from shared DAG resources), with per-type prices supporting the welfaremaximising allocation [3], [4], [8], [9];_

- (ii) _under a bounded integer encoding—explicit per-slice valuations in {_ 0 _, . . . , V_ max _}, K slice types, n agents, at most T_ max _tasks per agent, and a fixed price-increment rule—the welfare-maximising allocation is computable in time polynomial in n, K, T_ max _, and V_ max _via a Kelso– Crawford-style ascending auction with explicit demand computation [3]; and_

- (iii) _the efficient allocation is implementable through a DSIC, individually rational mechanism: VCG [5] applies in full generality (but may run a deficit). In the restricted case where each task class maps to a_ unique _admissible slice type—so that each agent–task pair demands at most one unit of a specific slice type and its private information reduces to a scalar willingness-to-pay for that type—the polymatroid clinching auction of Goel et al. [7], extending Ausubel [6], provides an alternative DSIC implementation that additionally guarantees weak budget balance under nonnegative valuations. When tasks may choose among multiple heterogeneous slice types, VCG remains the appropriate DSIC mechanism._

_Proof._ Part (i): Under slice encapsulation (Lemma 1), each slice type _s_ has an integral capacity _cs_ (determined by the polymatroid rank function), and agents treat each unit of each slice type as an indivisible item. Each agent has unit demand per task (one slice per task). The supply of _K_ slice types is governed by the integer polymatroid _P_ Z( _f_ ) = _{x ∈_ Z _[K] ≥_ 0[:] _[x]_[(] _[S]_[)] _[≤][f]_[(] _[S]_[)][for][all] _[S][}]_[,][where] _[f]_[is][the][rank]

4

function from Proposition 1. This imposes not only per-type upper bounds _xs ≤ f_ ( _{s}_ ) but also cross-type bottleneck constraints _x_ ( _S_ ) _≤ f_ ( _S_ ) for subsets _S_ of types sharing internal DAG resources (integral node capacities yield an integral rank function, ensuring integer vertices [2]). With per-type prices _ps_ and quasilinear payoffs _Vik_ ( _Ts, qs_ ) _− ps_ , unit-demand valuations satisfy the GS condition [4]. Fujishige and Yang [8] established that GS valuations are equivalent to M _[♮]_ -concave functions in the framework of discrete convex analysis; the integer polymatroid supply set is M- convex [9]. Under this equivalence, the Kelso–Crawford fixedpoint construction [3] extends to polymatroid-coupled supply (see Murota [9, Ch. 11]), guaranteeing a Walrasian equilibrium with per-type prices supporting the welfare-maximising integer allocation.

Part (ii): Under GS valuations, the Walrasian equilibrium of Part (i) is welfare-maximising [4]. Since the allocation problem involves _discrete_ indivisible slices with integral capacities, the appropriate algorithmic framework is the ascending auction for GS valuations. We assume the following representation: each agent _i_ reports an explicit scalar value _Vik_ ( _Ts, qs_ ) _∈{_ 0 _,_ 1 _, . . . , V_ max _}_ for each task–slice pair, where _V_ max is bounded; the demand oracle for agent _i_ at prices _p_ is computable in _O_ ( _K_ ) time by maximizing ( _Vik − ps_ ) over slice types for each task. Under this explicit representation, the ascending auction of Kelso and Crawford [3] terminates in a number of price-increment steps polynomial in _n_ (agents), _K_ (slice types), _T_ max (maximum tasks per agent), and _V_ max (the valuation range), since prices are bounded by _V_ max and each step requires _O_ ( _n · T_ max _· K_ ) demand-oracle work (each agent evaluates _K_ types for each of its tasks). The precise step count depends on the price-update rule, tie-breaking conventions, and price granularity, which we do not fully specify here; what matters for our purposes is that running time is polynomial under bounded integer valuations with explicit demand oracles. For practical deployments, _V_ max and _K_ are small, so computational cost is modest. (For a single-agent separable concave objective over a continuous polymatroid, Edmonds’ greedy algorithm [1] provides an alternative _O_ ( _|R|_ log _|R|_ )- time solution [2], but the multi-agent discrete-item setting of this paper relies on the ascending auction route.)

Part (iii): Within the static-epoch setting of Parts (i)–(ii), given the welfare-maximising allocation and quasilinear utility, VCG payments implement this outcome in dominant strategies (DSIC) and guarantee individual rationality (IR) [5]. (This is a per-epoch DSIC result, not a dynamic repeated-game guarantee.) We note that, in general, pairing a Walrasian allocation with VCG payments need not be DSIC, because a Walrasian allocation need not maximise social welfare. Our DSIC claim relies on the GS structure established in Lemma 1: under gross substitutes, the welfare-maximising allocation coincides with a Walrasian equilibrium allocation [4], so VCG payments apply to the exact social-welfare maximiser and the standard DSIC guarantee follows. However, VCG does not generically guarantee weak budget balance: the sum of VCG payments can be negative (a deficit) in multi-item settings.

For the clinching-auction claim, we require an explicit reduction to the single-parameter polymatroid clinching frame-

work of Goel et al. [7]. This reduction is valid when each task class maps to a _unique_ admissible slice type. Under this condition, task _k_ of agent _i_ demands at most one unit of its designated slice type _s_ ( _k_ ), and its private information reduces to the scalar willingness-to-pay _Vik_ ( _Ts_ ( _k_ ) _, qs_ ( _k_ ))—a singleparameter value. Additive separability across tasks (Lemma 1, condition (b)) ensures that the agent’s aggregate demand decomposes into independent per-task single-parameter demands with no cross-task coupling. The resulting environment—a collection of single-parameter bidders, each seeking one unit of their designated type, subject to a polymatroidal supply constraint—matches the polymatroidal clinching framework of Goel et al. [7], extending the ascending clinching auction of Ausubel [6]. Under this reduction, the clinching auction provides a DSIC implementation that additionally satisfies weak budget balance (non-negative revenue) under nonnegative valuations, and reveals equilibrium prices iteratively. Our setting specialises the Goel et al. framework [7] to agents with quasilinear utility and no binding budget constraints; the budget-constrained variant additionally handles agents with hard budgets, but that generalisation is not needed here since our utility model (Section II-F in the main paper) is quasilinear throughout.

The single-type-per-task condition holds naturally in the proposed architecture: Proposition 3 assumes each integrator exports a single homogeneous slice type, and when each task class is served by exactly one integrator, each task’s demand is one-dimensional. When tasks may choose among _multiple heterogeneous_ slice types (different ( _Ts, qs_ )), a scalar willingness-to-pay max _s Vik_ ( _Ts, qs_ ) does not faithfully encode item-specific preferences—the mechanism may allocate a non-utility-maximising slice, breaking the single-parameter equivalence. In this general heterogeneous case, VCG remains the appropriate DSIC mechanism; extending budget-balanced DSIC implementation to heterogeneous GS valuations under polymatroid constraints is an open problem left to future work.

## _D. Proof of Proposition 3 (Polymatroidal Encapsulation of Arbitrary DAGs)_

**Proposition 3** (Polymatroidal Encapsulation of Arbitrary DAGs) **.** _Let G_ res _be an arbitrary service-dependency DAG. Suppose a collection of integrators partitions the non-leaf nodes of G_ res _into disjoint clusters, where each cluster j manages a connected sub-DAG internally and exposes a single, homogeneousC_ ¯ _j equal to thecompositemaximumservicethroughput(slice)of withits sub-DAG.scalar capacityLet G[′] denote the quotient graph obtained by contracting each cluster to a single node. If G[′] has tree or series–parallel structure, then the agent-facing feasible region is polymatroidal._

_Proof._ Each integrator _j_ replaces an internal sub-DAG with a single node whose capacity _C_[¯] _j_ bounds the aggregate throughput available to the slices it exposes. Concretely, _C_[¯] _j_ is the maximum flow from the sources to the sinks of the sub-DAG managed by integrator _j_ . When a sub-DAG has multiple entry or exit points, a standard super-source/super-sink construction (adding a virtual source connected to all entry nodes and a

5

virtual sink connected to all exit nodes, each with infinitecapacity arcs) reduces the problem to a single-source singlesink max-flow. When the sub-DAG has node capacities, the standard node-splitting reduction—replacing each node _v_ with two nodes _v_[in] _, v_[out] connected by an arc of capacity _Cv_ — converts to an edge-capacity network; max-flow is then a standard polynomial-time computation (e.g., Ford–Fulkerson or push-relabel) that the integrator can recompute periodically as internal conditions change.

Every node _v_ in the quotient graph _G[′]_ carries a welldefined capacity: for contracted integrator nodes, the capacity is _C_[¯] _v_ = _C_[¯] _j_ (the max-flow of integrator _j_ ’s sub-DAG); for uncontracted nodes that were not absorbed into any integrator cluster, the capacity is the original _C_[¯] _v_ = _Cv_ . The agent-facing constraints are _x_ ( _L[′] v_[)] _[ ≤][C]_[¯] _[v]_[for][each][node] _[v]_[in] _[G][′]_[,][where] _[L][′] v_ is the set of slices in _v_ ’s sub-DAG. Since _G[′]_ is tree or series– parallel by assumption, the constraint family _{L[′] v[}]_[is][laminar] and Proposition 1 applies directly. The exported throughput token is a single commodity, measured in the same units (e.g., requests per second) as the agent-facing allocation variable _xl_ ; this unit consistency is ensured by the max-flow computation, which yields a scalar in the same throughput units as the original node capacities. Internal optimisation within each integrator (scheduling, routing, and capacity allocation across the sub-DAG) is a separate, lower-level problem solved by platform-specific orchestration. Provided the scalar-summary and no-cross-coupling assumptions hold (single homogeneous exported slice per integrator, no shared leaves across integrators), the polymatroidal guarantee holds at the agent-facing interface for arbitrary internal sub-DAG topology.

_Remark (scope of scalar-summary assumption)._ The scalar summary _C_[¯] _j_ is valid when each integrator exports a single, homogeneous slice type so that feasible throughput does not depend on the mix of external requests. In realistic service graphs, feasible throughput may depend on request mix, route contention, and internal compatibility constraints; a single scalar is then insufficient. When an integrator exports multipleservice types, _C_ ¯ _j_ generalises to a vector-valued capacity, and the quotient-graph polymatroid argument requires each integrator’s external feasibility set to itself be polymatroidal— a stronger structural condition that we leave to future work. Additionally, if leaf nodes are shared across integrators (e.g., common cloud GPUs used by multiple domains), external coupling can re-enter through leaf capacities unless explicitly captured in the quotient-graph structure.

## III. RELATED WORK COMPARISON

Table II positions this article relative to prior work across five research areas, identifying the specific gaps each area leaves and how the present framework addresses them.

## IV. SIMULATION DETAILS

## _A. Baseline Parameter Configuration_

All simulations share a common baseline configuration. We simulate 50 autonomous agents over 200 rounds with independent Poisson task arrivals ( _λ_ = 1 _._ 0 tasks/round/agent). Task values are drawn from Uniform[1 _,_ 2] with exponential latency

discount _δ_ ( _T_ ) = _e[−][λ][l][T]_ , _λl_ = 0 _._ 005 per ms (i.e., 5 _._ 0 per second, so value decays to _e[−]_[1] _≈_ 0 _._ 37 at the longest deadline), and class-dependent deadlines in _{_ 100 _,_ 150 _,_ 200 _}_ ms. The environment spans three tiers (device, edge, cloud) with capacities _{_ 200 _,_ 300 _,_ 500 _}_ units; base propagation delays are _{_ 5 _,_ 15 _,_ 50 _}_ ms. Two latency models are used: agents form bids using a power-law congestion estimate _L_[ˆ] = _L_ base + _α ρ[p]_ ( _α_ = 200, _p_ = 1 _._ 2), while actual execution latency follows an M/M/1-inspired queueing model _L_ = _L_ base +min� _λ_ load _·_ 1 _−ρ ρ[·]_ 2 _,_ 500� ms per tier, where _ρ_ = min(0 _._ 99 _,_ demand _/_ capacity) and the 500 ms cap prevents divergence near saturation. Pertask end-to-end latency is drawn from _N_ ( _L_ crit _,_ 0 _._ 1 _L_ crit), where _L_ crit is the critical-path latency through the DAG (coefficient of variation 10%). Trust scores initialise at 0 _._ 8 and update asymmetrically (+0 _._ 03 per successful SLA event, _−_ 0 _._ 08 per violation), reflecting a failure-dominant reputation model; governance violations result in hard rejection. Results are averaged over 10 random seeds for reproducibility.

Each DAG topology induces a distinct per-tier resource demand profile, reflecting the structural properties formalised in the main text. Linear and tree topologies distribute demand roughly evenly across tiers, whereas series–parallel (SP) topologies concentrate demand on cloud resources (reflecting parallel inference branches), and entangled topologies create heavy, asymmetric demand on device tiers with crosstier coupling. These demand profiles determine how rapidly per-tier capacity saturates and whether the resulting excessdemand signal induces stable or oscillatory price dynamics in the tˆatonnement.

The tˆatonnement runs 15 iterations per round with price step _η_ = 0 _._ 25 (normalised by tier capacity), a price floor of 0 and cap of 1000. The online success model uses a logistic sigmoid ˆ _p_ (success _| ρ_ ) = _σ_ ( _a_ + _b_ ˆ _ρ_ ) initialised at _a_ = 2 _._ 0, _b_ = _−_ 2 _._ 0 and updated via stochastic gradient descent with learning rate 0 _._ 3. Welfare is computed as realised latency-aware value minus a congestion penalty _γc_ � _r_[[max(] _[ρ][r][−]_[1] _[,]_[ 0)]][2][with] _γc_ = 0 _._ 05. Tasks that miss their deadline receive zero value (salvage fraction = 0). In Experiment 4, the hybrid integrator uses EMA smoothing coefficient _β_ ema = 0 _._ 8, a 10% markup over unit resource cost, slice price step 0 _._ 15, and topologydependent efficiency factors (0 _._ 75 for SP, 0 _._ 85 for entangled) that reduce the effective per-task resource footprint during execution. An ablation condition (“hybrid EMA only”) applies the same EMA smoothing but sets efficiency = 1 _._ 0, isolating the price-smoothing effect from the demand-reduction effect (Section IV-D). Table III consolidates all baseline parameters with their values and justifications.

## _B. Experiment-Specific Parameter Settings_

Table IV summarises the factors varied in each experiment and the parameters held fixed.

## _C. Result Summary Tables_

Tables V to VIII and X consolidate the key numeric results from Experiments 1–5. Values are reported as mean [bootstrap 95% CI] over 10 random seeds; latency is in milliseconds. Point estimates without CIs are shown where the bootstrap interval is negligibly narrow (width _<_ 1 unit).

6

TABLE II

COMPARISON OF RELATED WORK AND POSITIONING OF THIS ARTICLE

|**Category**||||**Strengths**|**Limitations**|**How This Article Addresses the Gap**|
|---|---|---|---|---|---|---|
|**Edge/Fog/**|||**Cloud**|Low-latency orchestration; mobility-|Assume centralized control; Limited mod-|Introduce an agentic layer; unify resource|
|**Service Mgmt** [10],||||and multi-resource-aware manage-|eling of multi-stage service dependencies;|management with autonomous task gener-|
|[11], [12],||[13], [14],||ment.|absence of explicit agent-driven decisions;|ation and negotiation; incorporate service-|
|[15]|||||and restricted adaptability under dynamic|DAG constraints.|
||||||conditions.||
|**Service**||**Function**||Optimize dependency-aware service|Do not consider strategic agents; lack inte-|Model service-dependency DAGs formally;|
|**Chaining**||[16], [17],||caching;<br>capture<br>placement<br>con-|grated economic or governance constraints;|analyse structural regimes (tree/SP) en-|
|[18]||||straints.|ignore market or negotiation dynamics.|abling stable coordination; embed into an|
|||||||economic/management framework.|
|**Agentic/**||||Identify autonomous AI agents as|No resource-DAG model; no governance-|Provide<br>a<br>full<br>agent–service–resource–|
|**Autonomous Systems**||||active system participants; highlight|aware allocation; no management-plane in-|governance model; link agent behavior to|
|[19], [20],||[21]||emergent coordination challenges.|tegration or tractable orchestration frame-|system feasibility and market outcomes.|
||||||work.||
|**Governance,**|||**Trust,**|Formalize policies, trust, locality,|Not integrated with latency/QoS constraints,|Embed governance directly into feasibil-|
|**Norms**|[22],||[23],|compliance; mature models of norm|dependency-aware placement, or market-|ity<br>(_X_gov);<br>model<br>reputation-dependent|
|[24]||||enforcement.|based coordination.|access; evaluate governance–performance|
|||||||trade-offs.|
|**Market-Based**||||Provide incentive-compatible mech-|Assume independent or substitutable items;|Identify structural conditions where market|
|**Resource **||**Allocation**||anisms; effcient pricing and alloca-|break down under interdependent resource|stability is preserved (polymatroid regimes);|
|[25], [26],||[27],|[28]|tion for substitutable resources.|bundles or service graphs; no governance.|propose hybrid slice-based architecture in-|
|||||||sulating the market from deep complemen-|
|||||||tarities.|



_D. Experiment 4 Ablation: EMA Smoothing vs. Efficiency Factor_

The hybrid architecture applies two simultaneous changes relative to the na¨ıve baseline: (i) EMA price smoothing ( _β_ ema = 0 _._ 8, 10% markup), and (ii) an efficiency factor (SP: 0 _._ 75, entangled: 0 _._ 85) that reduces per-task resource consumption during execution. To disentangle these effects, we run a _hybrid (EMA only)_ condition with efficiency = 1 _._ 0 (no demand reduction), yielding 3 _×_ 2 _×_ 2 _×_ 4 _×_ 10 = 480 runs total. Table IX reports the full results.

_Price volatility.:_ EMA smoothing alone accounts for the majority of the volatility reduction. For SP DAGs, the EMAonly condition achieves _σ ≤_ 0 _._ 097 across all agent counts and loads, matching the full hybrid and representing up to a 72% reduction from na¨ıve levels (e.g., SP/high/ _N_ = 60: na¨ıve _σ_ = 0 _._ 337, EMA only _σ_ = 0 _._ 097, full hybrid _σ_ = 0 _._ 096). For entangled DAGs, EMA alone achieves comparable volatility reduction in most conditions, with two exceptions: entangled/high at _N_ = 20 ( _σ_ = 0 _._ 141 vs. full hybrid 0 _._ 096) and entangled/medium at _N_ = 40 ( _σ_ = 0 _._ 262 vs. full hybrid 0 _._ 096). In these cases, the efficiency factor contributes additional stabilisation by reducing effective demand below the congestion threshold.

_Latency and welfare.:_ Unlike price volatility, latency and welfare improvements depend substantially on the efficiency factor. Under SP/high/ _N_ = 60, EMA only achieves 315 ms median latency versus 181 ms for full hybrid and 197 ms for na¨ıve: the efficiency factor’s demand reduction delays the onset of queueing saturation, producing a 42% latency improvement beyond EMA alone. Similarly, welfare at SP/high/ _N_ = 40 is 14 _._ 4 under EMA only (identical to na¨ıve) versus 14 _._ 9 under full hybrid. At higher _N_ values where the

system saturates regardless, all three conditions converge to near-total drop rates and zero welfare.

_Interpretation.:_ The ablation confirms that the two components of the hybrid architecture serve distinct functions: EMA smoothing is the primary mechanism for price stabilisation (the _architectural_ effect), while the efficiency factor provides latency and welfare improvements by reducing effective resource consumption (the _operational_ effect). In conditions far below or far above capacity, the effects are negligible; the benefits concentrate in the congested-but-not-saturated regime.

## V. DETAILED EXPERIMENT RESULTS

This section presents figures and extended discussion for each experiment. The main paper reports condensed ablation results; here we provide the per-experiment visualisations and condition-by-condition analysis.

## _A. Experiment 1: Structural Ablation_

Fig. 1 summarises the results across four panels. Price volatility, measured as the standard deviation of log-returns of per-tier prices across rounds, is the key metric linking the simulation to the theoretical prediction of Proposition 1: topologies with polymatroidal feasibility regions should exhibit convergent, stable prices.

At low load ( _λ_ = 0 _._ 5), all four topologies achieve comparable median latencies (126–143 ms), moderate drop rates (34– 44%), and zero price volatility. Under high load ( _λ_ = 1 _._ 5), linear and tree topologies maintain median latencies of 134 and 142 ms with moderate drop rates (37% and 49%) and, crucially, zero price volatility.

In contrast, the entangled DAG under high load reaches a median latency of 404 ms ( _p_ 95 = 473 ms), a drop rate of

7

TABLE III

BASELINE SIMULATION PARAMETERS

|**Parameter**|**Symbol**|**Value**|**Justifcation**|
|---|---|---|---|
|_General_||||
|Agent count|_N_|50|Suffcient for stable averages; varied in Exp 2,|
||||4|
|Simulation rounds|—|200|Allows tˆatonnement and learning convergence|
|Monte Carlo seeds|—|10|Standard for variance estimation|
|_Task model_||||
|Arrival rate|_λ_|1.0 tasks/round/agent|Poisson; varied in Exp 1 (0_._5, 1_._0, 1_._5)|
|Task value|_v_|Uniform[1_,_2]|Normalised; focuses analysis on structural ef-|
||||fects|
|Latency decay rate|_λl_|0.005 /ms|Value halves at _≈_139 ms; spans deadline range|
|Deadlines|_D_|_{_100_,_150_,_200_}_ ms|Tight to relaxed relative to tier latencies|
|Salvage fraction|—|0|Hard deadline: missed _⇒_zero value|
|_Environment_||||
|Tier capacities|_Cr_|_{_200_,_300_,_500_}_|Device _<_ edge _<_ cloud capacity|
|Base propagation delays|_L_base|_{_5_,_15_,_50_}_ ms|Device _<_ edge _<_ cloud latency|
|Latency CV|—|10%|Gaussian noise around critical-path latency|
|_Bidding and execution models_||||
|Bidding congestion|ˆ_L_|_L_base+ 200_ρ_1_._2|Power-law; intentional mismatch with execution|
|Execution latency|_L_|M/M/1 with 500 ms cap|Standard queueing; cap prevents divergence|
|_Trust_||||
|Trust initialisation|_τ_0|0.8|Moderate prior trust|
|Trust update (success)|—|+0_._03|Asymmetric per [23]|
|Trust update (violation)|—|_−_0_._08|Failure-dominant per [23]|
|_Tˆatonnement and learning_||||
|Iterations per round|—|15|Suffcient for price convergence|
|Price step|_η_|0.25|Normalised by tier capacity|
|Price foor / cap|—|0 / 1000|Prevents negative or runaway prices|
|Online success model|—|_σ_(2_._0_−_2_._0 ˆ_ρ_)|Conservative initial prior; learns from outcomes|
|Learning rate|—|0.3|Balances responsiveness and stability|
|Congestion penalty|_γc_|0.05|Mild welfare penalty for over-utilisation|
|_Hybrid integrator (Exp 4 and 5)_||||
|EMA smoothing|_β_ema|0.8|Smooths round-to-round price oscillations|
|Markup|—|10%|Covers integrator overhead|
|Slice price step|—|0.15|Integrator price adjustment rate|
|Effciency factor (SP)|_η_SP|0.75|Moderate internal scheduling gain|
|Effciency factor (entangled)|_η_ent|0.85|Higher gain for more complex sub-DAGs|



99 _._ 8%, and a price volatility of _σ_ = 0 _._ 273. The SP topology exhibits intermediate behaviour: median latency of 146 ms at high load but a drop rate of 89 _._ 8% and price volatility of _σ_ = 0 _._ 112. Under medium load, the entangled topology already shows substantial price volatility ( _σ_ = 0 _._ 373), while SP, tree, and linear remain at zero.

The utilisation panel reveals the structural mechanism: entangled DAGs push effective demand to 1 _._ 11 _×_ capacity at high load, creating persistent excess demand that drives price oscillation; SP reaches 0 _._ 83 _×_ ; tree and linear remain below the critical threshold. The SP topology is fully polymatroidal, yet exhibits non-zero volatility at high load because its demand profile pushes per-tier utilisation toward saturation, where the tˆatonnement fails to converge despite equilibrium existence. The ordering (linear _≈_ tree _<_ SP _<_ entangled) reflects both structural complexity and demand-profile effects, motivating the encapsulation approach.

## _B. Experiment 3: Governance Ablation_

Three governance regimes are compared: no governance (all tasks share a single resource pool); moderate governance (capacity split 50/50 between compliant and general pools); and strict governance (70/30 split with trust gate _≥_ 0 _._ 75).

Fig. 2 reports median latency, drop rate, service coverage, and price volatility. By construction, all allocated tasks are policy-compliant; the meaningful trade-off appears in service coverage. For the tree topology under high load, service coverage falls from 59% (no governance) to 30% (strict), while median latency remains largely unchanged (138–142 ms). For the entangled topology under high load, service coverage falls from 0 _._ 4% to 0 _._ 2%, but median latency decreases substantially from 404 ms to 266 ms (a 34% reduction), as governance excludes the most congestion-prone allocations.

The price-volatility panel reveals a secondary effect: strict governance substantially increases price volatility across all conditions, because capacity partitioning creates smaller subpools that saturate more easily. This is most pronounced for

8

TABLE IV

EXPERIMENT-SPECIFIC PARAMETER SETTINGS

|**Exp.**|**Varied Aspect**|**Settings**|**Fixed**|
|---|---|---|---|
|1|Service-dependency graph shape|Linear, tree, series–parallel (SP), entangled DAG; low,|_N_ = 50; governance: baseline; architec-|
||_×_ load|medium, high (_λ ∈{_0_._5_,_1_._0_,_1_._5_}_)|ture: na¨ıve (no slicing)|
|2|Agent population _×_ topology|_N ∈{_10_,_20_,_30_,_40_,_50_,_60_}_; tree, SP, and entangled topolo-|Load: medium (_λ_<br>=<br>1_._0); governance:|
|||gies|baseline; architecture: na¨ıve|
|3|Governance policy|None, moderate (50/50 capacity split with task-sensitivity|Graph: tree and entangled; load: medium|
|||routing), strict (70/30 split with trust-gated access, threshold|and high; _N_ = 50|
|||_≥_0_._75)||
|4|Architecture _×_ agents|Na¨ıve vs. hybrid; _N ∈{_20_,_40_,_60_,_80_}_; per-agent arrival|Graph: SP and entangled; load: medium and|
|||rate fxed (total demand scales with _N_)|high|
|5|Architecture _×_ governance|Na¨ıve vs. hybrid (full); none vs. strict governance; tree, SP,|_N_ = 50; load: medium and high; 2_×_2_×_|
|||entangled topologies|3_×_2_×_10 = 240 runs|
|6|Allocation mechanism|Random,<br>EDF,<br>value-greedy<br>(no<br>prices),<br>market|Tree, SP, entangled; load: medium and high;|
|||(tˆatonnement); na¨ıve and hybrid architecture|_N_ = 50; no governance; 4_×_3_×_2_×_2_×_|
||||10 = 480 runs|



TABLE V

EXPERIMENT 1: IMPACT OF DAG TOPOLOGY AND LOAD LEVEL

|**Topology**|**Load**|**Med. **|**Lat. **|**(ms)**|_p_95|**Lat. **|**(ms)**|**Drop **|**Rate**|**Utilisation**|**Price **|**Vol. (**_σ_**)**|
|---|---|---|---|---|---|---|---|---|---|---|---|---|
|Linear|Low|||126|||145||0.34|0.14||0.000|
|Linear|Medium|||130|||150||0.35|0.29||0.000|
|Linear|High|||134|||154||0.37|0.43||0.000|
|Tree|Low|||136|||156||0.39|0.17||0.000|
|Tree|Medium|||138|||159||0.40|0.35||0.000|
|Tree|High|||142|||163||0.49|0.52||0.000|
|SP|Low|||137|||157||0.39|0.28||0.000|
|SP|Medium|||140|||160||0.53|0.55||0.000|
|SP|High|||146|||168||0.90|0.83||0.112|
|Entangled|Low|||143|||164||0.44|0.37||0.000|
|Entangled|Medium|||149|||170||0.77|0.74||0.373|
|Entangled|High|||404|||473||1.00|1.11||0.273|



Values averaged over 10 seeds. All topologies achieve comparable latency at low load (126–143 ms) with zero price volatility. Degradation under medium and high load is topology-dependent.

**==> picture [253 x 201] intentionally omitted <==**

**----- Start of picture text -----**<br>
Load level low medium high<br>500 90%<br>400<br>70%<br>300<br>50%<br>200<br>0.5<br>0.9 0.4<br>0.3<br>0.6<br>0.2<br>0.3 0.1<br>0.0<br>DAG topology DAG topology<br>linear tree spentangled linear tree spentangled<br>Latency (ms) Drop rate (%)<br>Utilisation )Price vol. (σ<br>**----- End of picture text -----**<br>


**==> picture [253 x 201] intentionally omitted <==**

**----- Start of picture text -----**<br>
Load level medium high<br>Topology tree entangled<br>100%<br>500<br>400 80%<br>300<br>60%<br>200<br>40%<br>80%<br>1.5<br>60%<br>1.0<br>40%<br>20% 0.5<br>0% 0.0<br>none moderate strict none moderate strict<br>Policy Policy<br>Latency (ms) Drop rate (%)<br>)σ<br>Price volatility (<br>Service coverage (%)<br>**----- End of picture text -----**<br>


Fig. 1. Experiment 1: Effect of DAG topology and load on median latency (top-left), drop rate (top-right), utilisation (bottom-left), and price volatility (bottom-right). Polymatroidal topologies (linear, tree) maintain stable prices; entangled DAGs degrade sharply under load.

Fig. 2. Experiment 3: Effect of governance policy (none/moderate/strict) on performance for tree and entangled DAGs under medium and high load. Panels: median latency, drop rate, service coverage, price volatility.

9

TABLE VI

EXPERIMENT 2: TOPOLOGY-DEPENDENT SCALING ( _N ∈{_ 10 _, . . . ,_ 60 _}_ , MEDIUM LOAD)

|**Topology**|_N_|**Med. **|**Lat. **|**(ms)**|**Drop **|**Rate**|**Deadline **|**Sat.**|**Price **|**Vol. (**_σ_**)**|
|---|---|---|---|---|---|---|---|---|---|---|
|Tree|10|||136||0.38||0.62||0.000|
|Tree|20|||136||0.38||0.62||0.000|
|Tree|30|||137||0.39||0.61||0.000|
|Tree|40|||138||0.40||0.60||0.000|
|Tree|50|||138||0.40||0.60||0.000|
|Tree|60|||139||0.40||0.60||0.000|
|SP|10|||136||0.38||0.62||0.000|
|SP|20|||138||0.40||0.60||0.000|
|SP|30|||139||0.40||0.60||0.000|
|SP|40|||140||0.42||0.58||0.000|
|SP|50|||140||0.53||0.47||0.000|
|SP|60|||139||0.67||0.33||0.000|
|Entangled|10|||142||0.43||0.57||0.000|
|Entangled|20|||145||0.46||0.54||0.000|
|Entangled|30|||148||0.49||0.51||0.116|
|Entangled|40|||149||0.63||0.37||0.287|
|Entangled|50|||149||0.77||0.23||0.373|
|Entangled|60|||152||0.93||0.07||0.301|



Values averaged over 10 seeds. Tree topology shows graceful scaling with near-constant metrics. Entangled topology reaches market failure by _N_ = 60.

## TABLE VII

EXPERIMENT 3: GOVERNANCE AND TRUST EFFECTS (TREE AND ENTANGLED, MEDIUM AND HIGH LOAD)

|**Topology**|**Load**|**Governance**|**Med. **|**Lat. **|**(ms)**|**Drop **|**Rate**|**Coverage**|**Price **|**Vol. (**_σ_**)**|
|---|---|---|---|---|---|---|---|---|---|---|
|Tree|Medium|None|||138||0.40|0.76||0.000|
|Tree|Medium|Moderate|||138||0.40|0.76||0.000|
|Tree|Medium|Strict|||137||0.63|0.45||0.882|
|Tree|High|None|||142||0.49|0.59||0.000|
|Tree|High|Moderate|||142||0.49|0.60||0.246|
|Tree|High|Strict|||138||0.72|0.30||1.686|
|Entangled|Medium|None|||149||0.77|0.25||0.373|
|Entangled|Medium|Moderate|||148||0.77|0.25||0.347|
|Entangled|Medium|Strict|||146||0.89|0.12||1.338|
|Entangled|High|None|||404||1.00|0.004||0.273|
|Entangled|High|Moderate|||347||1.00|0.004||0.259|
|Entangled|High|Strict|||266||1.00|0.002||0.433|



Values averaged over 10 seeds. All allocated tasks are policy-compliant by construction. Strict governance substantially increases price volatility due to capacity partitioning into smaller sub-pools.

tree topologies, which exhibit zero volatility without governance but significant volatility under strict partitioning. This does not contradict polymatroidal preservation: governanceinduced capacity partitioning pushes per-pool utilisation toward saturation, where the tˆatonnement fails to converge despite equilibrium existence. The observation demonstrates that governance can introduce _operational_ market instability even in structurally well-behaved topologies.

_Governance design-space considerations.:_ The capacitypartitioning model tested above captures the structural effect of policy constraints on feasibility but represents only one point in a broader design space. In practice, governance may involve _data-locality restrictions_ that constrain which tiers are admissible for specific task classes (e.g., medical data confined to jurisdiction-compliant nodes), _cross-domain policy negotiation_ where integrators must reconcile conflicting jurisdictional rules before admitting cross-domain slices, and _dynamic trust_

_evolution_ where reputation scores respond to adversarial behaviour or changing compliance requirements. The simulation results establish that even a relatively simple governance model produces quantifiable efficiency–compliance trade-offs that depend jointly on topology and load; richer models would likely amplify these interactions. This complements findings in trustworthy distributed systems [23], [24] by providing a resource- and dependency-aware perspective.

## _C. Experiment 4: Architecture Ablation_

Three strategies are compared: _na¨ıve_ (per-tier pricing), _hybrid (EMA only)_ (smoothed slice price, efficiency = 1 _._ 0), and _hybrid (full)_ (EMA plus efficiency factor: SP 0 _._ 75, entangled 0 _._ 85).

Figs. 3 and 4 present results in four panels. The pricevolatility panel directly tests the encapsulation prediction.

10

## TABLE VIII

EXPERIMENT 4: NA¨IVE VS. HYBRID ARCHITECTURE (SP AND ENTANGLED, MEDIUM AND HIGH LOAD)

|**Topology**<br>**Load**|**Arch.**<br>_N_<br>**Med. Lat. (ms)**<br>**Drop Rate**<br>**Welfare**<br>**Price Vol. (**_σ_**)**|
|---|---|
|SP<br>Medium<br>SP<br>Medium<br>SP<br>Medium<br>SP<br>Medium<br>SP<br>Medium<br>SP<br>Medium<br>SP<br>Medium<br>SP<br>Medium|Na¨ıve<br>20<br>138<br>0.40<br>9.2<br>0.000<br>Na¨ıve<br>40<br>140<br>0.42<br>17.4<br>0.000<br>Na¨ıve<br>60<br>139<br>0.67<br>14.8<br>0.000<br>Na¨ıve<br>80<br>149<br>0.95<br>2.9<br>0.198|
||Hybrid<br>20<br>137<br>0.39<br>9.3<br>0.096<br>Hybrid<br>40<br>138<br>0.41<br>17.9<br>0.096<br>Hybrid<br>60<br>138<br>0.67<br>15.1<br>0.096<br>Hybrid<br>80<br>139<br>0.95<br>3.0<br>0.096|
|SP<br>High<br>SP<br>High<br>SP<br>High<br>SP<br>High<br>SP<br>High<br>SP<br>High<br>SP<br>High<br>SP<br>High|Na¨ıve<br>20<br>141<br>0.42<br>12.9<br>0.000<br>Na¨ıve<br>40<br>141<br>0.68<br>14.4<br>0.000<br>Na¨ıve<br>60<br>197<br>0.99<br>0.3<br>0.338<br>Na¨ıve<br>80<br>635<br>1.00<br>0.0<br>0.286|
||Hybrid<br>20<br>139<br>0.41<br>13.4<br>0.096<br>Hybrid<br>40<br>139<br>0.67<br>14.9<br>0.096<br>Hybrid<br>60<br>181<br>0.99<br>0.4<br>0.096<br>Hybrid<br>80<br>674<br>1.00<br>0.0<br>0.097|
|Entangled<br>Medium<br>Entangled<br>Medium<br>Entangled<br>Medium<br>Entangled<br>Medium<br>Entangled<br>Medium<br>Entangled<br>Medium<br>Entangled<br>Medium<br>Entangled<br>Medium|Na¨ıve<br>20<br>145<br>0.46<br>8.0<br>0.000<br>Na¨ıve<br>40<br>149<br>0.63<br>10.8<br>0.287<br>Na¨ıve<br>60<br>152<br>0.93<br>3.1<br>0.301<br>Na¨ıve<br>80<br>439<br>1.00<br>0.0<br>0.274|
||Hybrid<br>20<br>144<br>0.45<br>8.2<br>0.096<br>Hybrid<br>40<br>146<br>0.61<br>11.4<br>0.096<br>Hybrid<br>60<br>155<br>0.93<br>2.9<br>0.154<br>Hybrid<br>80<br>473<br>1.00<br>0.0<br>0.097|
|Entangled<br>High<br>Entangled<br>High<br>Entangled<br>High<br>Entangled<br>High<br>Entangled<br>High<br>Entangled<br>High<br>Entangled<br>High<br>Entangled<br>High|Na¨ıve<br>20<br>151<br>0.53<br>10.1<br>0.066<br>Na¨ıve<br>40<br>157<br>0.93<br>3.0<br>0.307<br>Na¨ıve<br>60<br>683<br>1.00<br>0.0<br>0.270<br>Na¨ıve<br>80<br>688<br>1.00<br>0.0<br>0.346|
||Hybrid<br>20<br>147<br>0.50<br>10.9<br>0.096<br>Hybrid<br>40<br>162<br>0.93<br>3.0<br>0.097<br>Hybrid<br>60<br>684<br>1.00<br>0.0<br>0.097<br>Hybrid<br>80<br>684<br>1.00<br>0.0<br>0.097|



Values averaged over 10 seeds. Hybrid architecture reduces price volatility by up to 70–75%. Both architectures saturate similarly beyond capacity ( _N ≥_ 60 for entangled/high, _N ≥_ 80 for SP/high).

**==> picture [516 x 202] intentionally omitted <==**

**----- Start of picture text -----**<br>
Naive Naive<br>medium medium<br>Hybrid EMA Hybrid EMA<br>high high<br>Hybrid full Hybrid full<br>SP Entangled SP Entangled<br>700 12<br>600 600 15 9<br>500<br>400 400 10 6<br>300 5 3<br>200 200<br>0 0<br>SP Entangled SP Entangled<br>100% 100% 0.5<br>0.4 0.4<br>80% 80% 0.3<br>60% 60% 0.2 0.2<br>0.1<br>40% 0.0 0.0<br>20 40 60 80 20 40 60 80 20 40 60 80 20 40 60 80<br>Number of agents (N) Number of agents (N)<br>Latency (ms) Welfare (a.u.)<br>)σ<br>Drop rate (%) Price vol. (<br>**----- End of picture text -----**<br>


Fig. 3. Experiment 4 (operational): Na¨ıve, hybrid (EMA only), and hybrid (full) architecture across agent counts, DAG types, and loads. Panels: latency, drop rate.

Fig. 4. Experiment 4 (economic): Welfare and price volatility under the same conditions as Fig. 3.

11

**==> picture [253 x 201] intentionally omitted <==**

**----- Start of picture text -----**<br>
naive / none naive / strict<br>Condition<br>hybrid / none hybrid / strict<br>high medium<br>1.0<br>0.5<br>0.0<br>high medium<br>30<br>20<br>10<br>0<br>DAG topology<br>tree sp entangled tree sp entangled<br>)σ<br>Price vol. (<br>Welfare<br>**----- End of picture text -----**<br>


Fig. 5. Experiment 5: Architecture _×_ governance interaction. Top row: price volatility by topology and condition; bottom row: welfare. The hybrid architecture mitigates the volatility penalty introduced by governance.

Under na¨ıve allocation, price volatility grows with _N_ and load ( _σ_ = 0 _._ 35 for entangled at _N_ = 80/high, _σ_ = 0 _._ 34 for SP at _N_ = 60/high). Under hybrid allocation, volatility remains at or below _σ_ = 0 _._ 10 in nearly all conditions, a reduction of 70–75%.

For latency, hybrid provides modest but consistent improvements (SP/high at _N_ = 60: 181 ms vs. 197 ms for na¨ıve). Both architectures saturate at similar thresholds ( _N ≈_ 60 for entangled/high, _N ≈_ 80 for SP/high), reaching median latencies of 635–688 ms with near-total drop rates, confirming that the hybrid architecture’s primary contribution is price stability rather than raw latency reduction.

An EMA-only ablation confirms that EMA smoothing accounts for the majority of volatility reduction (SP/high/ _N_ = 60: _σ_ = 0 _._ 097 vs. na¨ıve 0 _._ 337), while latency and welfare improvements depend on the efficiency factor (315 ms EMAonly vs. 181 ms full hybrid). The two serve distinct roles: EMA stabilises prices (architectural), while the efficiency factor reduces congestion (operational).

## _D. Experiment 5: Architecture × Governance Interaction_

This experiment crosses architecture (na¨ıve / hybrid) _×_ governance (none / strict) _×_ topology (tree / SP / entangled) _×_ load (medium / high), yielding 240 runs.

Fig. 5 presents price volatility and welfare across the four condition combinations. When both the hybrid architecture and strict governance are active, the hybrid architecture substantially mitigates the governance-induced volatility penalty: for SP under medium load, _σ_ drops from 0 _._ 78 (na¨ıve/strict) to 0 _._ 20 (hybrid/strict), a 75% reduction. For tree/high, hybrid/strict reduces volatility from _σ_ = 1 _._ 15 to _σ_ = 0 _._ 50 (57%). For entangled/medium, _σ_ = 1 _._ 32 to _σ_ = 0 _._ 39 (70%).

Welfare results reveal the interaction’s nature. For SP topologies, the combination is approximately additive (synergy CI includes zero). For tree/high, the interaction is significantly

**==> picture [253 x 201] intentionally omitted <==**

**----- Start of picture text -----**<br>
Random EDF<br>Greedy EV Market<br>Medium High Medium High<br>30 2.5<br>2.0<br>20 1.5<br>10 1.0<br>0.5<br>0 0.0<br>Medium High Medium High<br>100% 700<br>600<br>80% 500<br>400<br>60% 300<br>200<br>40%<br>DAG topology DAG topology<br>treeentangledsp treeentangledsp treeentangledsp treeentangledsp<br>Efficiency<br>Welfare (a.u.)<br>Drop rate (%) Latency (ms)<br>**----- End of picture text -----**<br>


Fig. 6. Experiment 6: Mechanism ablation comparing random, EDF, valuegreedy, and market allocation across topologies and load levels (na¨ıve architecture). Panels: welfare (top-left), efficiency ratio (top-right), drop rate (bottom-left), median latency (bottom-right).

sub-additive (∆synergy = _−_ 0 _._ 83 [ _−_ 1 _._ 04, _−_ 0 _._ 59]): governance reduces welfare more sharply when hybrid is active because the efficiency factor leaves less slack. For entangled topologies, the interaction is mildly super-additive (0 _._ 39 [0 _._ 18, 0 _._ 64]).

## _E. Experiment 6: Mechanism Ablation_

Four allocation rules are compared: random feasible packing, earliest-deadline-first (EDF), value-greedy (packing by E[ _V_ ] without prices), and the full tˆatonnement market mechanism. Each level adds one component (scheduling awareness, value model, price signals).

Fig. 6 presents results for the na¨ıve architecture. The market and value-greedy curves overlap almost exactly across all conditions (welfare difference _<_ 1%), because tˆatonnement prices converge to near-zero under truthful bidding.

The mechanism ordering is topology-dependent. For tree/high load, value-greedy/market achieve welfare of 28 _._ 6 a.u. vs. 24 _._ 3–24 _._ 4 for random/EDF (17% improvement). For entangled/medium, the value model yields 8 _._ 4 a.u. vs. 0 _._ 26 for random/EDF (32 _×_ ), as it identifies tasks with sufficient deadline slack to survive high-congestion paths. For SP/medium, all mechanisms perform comparably (17 _._ 4– 17 _._ 8 a.u.), with random and EDF marginally outperforming.

Under hybrid architecture, the SP reversal is amplified at high load (random/EDF: 18 _._ 2–18 _._ 3 a.u. vs. valuegreedy/market: 5 _._ 9 a.u.), because the efficiency factor creates headroom where load-spreading heuristics outperform value concentration.

## VI. STATISTICAL ANALYSIS

This section describes the statistical methodology used throughout the evaluation and presents detailed test results for each experiment. All analyses use non-parametric methods

12

appropriate for small-sample simulation studies ( _n_ = 10 seeds per condition).

## _A. Methodology_

_Confidence intervals.:_ All reported metrics use biascorrected and accelerated (BCa) bootstrap 95% confidence intervals with _B_ = 2 _,_ 000 resamples over the 10 seeds per condition [29]. For conditions where the BCa method fails to converge (e.g., zero-variance metrics), we fall back to the percentile method.

_Hypothesis tests.:_ For multi-group comparisons (e.g., topology with 4 levels), we use the Kruskal–Wallis _H_ - test [30], a non-parametric analogue of one-way ANOVA. Post-hoc pairwise comparisons use two-sided Wilcoxon ranksum (Mann–Whitney _U_ ) tests with Holm correction for multiple comparisons [31]. The choice of non-parametric tests is motivated by the small sample size ( _n_ = 10), which precludes reliable normality assessment, and by the nature of simulation metrics (latency, drop rate, price volatility), which are typically non-normal with skewed or bounded distributions.

_Effect sizes.:_ Pairwise effect sizes are reported as Cliff’s delta ( _δ_ ), a non-parametric measure appropriate for ordinal and non-normal data [32]. Magnitude thresholds follow Romano et al. [33]: _|δ| <_ 0 _._ 147 (negligible), _<_ 0 _._ 33 (small), _<_ 0 _._ 474 (medium), _≥_ 0 _._ 474 (large).

_Interaction analysis.:_ Factorial interactions (e.g., topology _×_ load in Exp 1, architecture _×_ governance in Exp 5) are tested using Aligned Rank Transform (ART) ANOVA [34], a non-parametric method that supports multi-factor interaction analysis without normality assumptions. We report _F_ -statistics and _p_ -values for main effects and two-way interactions.

_Synergy analysis.:_ For Experiment 5, we assess whether the combination of hybrid architecture and governance yields super-additive (synergistic) or sub-additive (redundant) effects. Let _Wij_ denote the mean welfare under architecture _i ∈{_ na¨ıve _,_ hybrid _}_ and governance _j ∈{_ none _,_ strict _}_ . The synergy measure is:

**==> picture [248 x 57] intentionally omitted <==**

Bootstrap 95% CIs are computed for ∆synergy; if the interval includes zero, the composition is additive.

though price volatility is identically zero across all topologies (no test applicable).

Pairwise Wilcoxon tests (Holm-corrected) show that the entangled topology differs significantly from all other topologies on all metrics at medium and high load ( _p_ adj _<_ 0 _._ 002). The ordering linear _≈_ tree _<_ SP _<_ entangled is confirmed by the pairwise test structure: all entangled-vs-other comparisons are significant, while linear-vs-tree comparisons are significant but with smaller effect magnitudes.

## _C. Experiment 2: Statistical Summary_

Spearman rank correlations between agent count ( _N_ ) and each metric confirm topology-dependent scaling. For the tree topology, all metrics show strong monotonic relationships with _N_ ( _ρ_ = 0 _._ 78–0 _._ 99, _p <_ 10 _[−]_[13] ), but the absolute magnitudes of change are small (e.g., median latency increases by only 3 ms across _N_ = 10–60). For SP, correlations are similarly strong ( _ρ_ = 0 _._ 73–0 _._ 99, _p <_ 10 _[−]_[10] ), with price volatility remaining at zero throughout (correlation not applicable). For the entangled topology, the correlations are also strong ( _ρ >_ 0 _._ 7, _p <_ 10 _[−]_[10] for latency, drop rate, utilisation, and welfare), confirming the steep monotonic degradation visible in the figures. Price volatility for the entangled topology shows a non-monotonic pattern (rising then falling), reflecting the transition from stable to fully saturated operation where price oscillations collapse.

## _D. Experiment 3: Statistical Summary_

Kruskal–Wallis tests show that governance policy has a significant effect on all metrics for the tree topology under high load: median latency ( _H_ (2) = 19 _._ 4, _p <_ 10 _[−]_[4] ), drop rate ( _H_ (2) = 19 _._ 4, _p <_ 10 _[−]_[4] ), welfare ( _H_ (2) = 19 _._ 4, _p <_ 10 _[−]_[4] ), coverage ( _H_ (2) = 19 _._ 4, _p <_ 10 _[−]_[4] ), and price volatility ( _H_ (2) = 24 _._ 1, _p <_ 10 _[−]_[5] ). Pairwise Wilcoxon tests (Holmcorrected) confirm that the none-vs-strict contrast is significant for all metrics ( _p_ adj _<_ 0 _._ 001).

For the entangled topology under high load, governance effects are more nuanced. Welfare ( _H_ (2) = 6 _._ 10, _p_ = 0 _._ 048) and coverage ( _H_ (2) = 8 _._ 72, _p_ = 0 _._ 013) show significant effects, but median latency does not ( _H_ (2) = 1 _._ 86, _p_ = 0 _._ 39), reflecting the fact that the system is already saturated regardless of governance policy. Price volatility shows a significant governance effect ( _H_ (2) = 11 _._ 0, _p_ = 0 _._ 004), confirming that capacity partitioning amplifies price oscillations even in structurally unstable topologies.

## _E. Experiment 4: Statistical Summary_

## _B. Experiment 1: Statistical Summary_

Kruskal–Wallis tests confirm that topology has a highly significant main effect on all key metrics at every load level. At high load, the effect of topology on median latency ( _H_ (3) = 36 _._ 6, _p <_ 10 _[−]_[7] ), drop rate ( _H_ (3) = 36 _._ 6, _p <_ 10 _[−]_[7] ), welfare ( _H_ (3) = 36 _._ 6, _p <_ 10 _[−]_[7] ), and price volatility ( _H_ (3) = 26 _._ 3, _p <_ 10 _[−]_[5] ) is significant. At medium load, all four metrics remain significant ( _p <_ 10 _[−]_[7] for latency, drop rate, and welfare; _p <_ 10 _[−]_[7] for volatility). At low load, topology still significantly affects latency, drop rate, and welfare ( _p <_ 10 _[−]_[7] ),

Kruskal–Wallis tests for the effect of architecture (na¨ıve, EMA-only, full hybrid) show that the primary significant effect is on price volatility, not on latency or welfare directly. For entangled/medium load, architecture significantly affects price volatility ( _H_ (2) = 11 _._ 1, _p_ = 0 _._ 004) but not latency ( _H_ (2) = 2 _._ 74, _p_ = 0 _._ 25) or welfare ( _H_ (2) = 0 _._ 72, _p_ = 0 _._ 70). For SP/high load, architecture has a marginally significant effect on latency ( _H_ (2) = 6 _._ 14, _p_ = 0 _._ 046) but not on drop rate ( _p_ = 0 _._ 69) or welfare ( _p_ = 0 _._ 57). This confirms that the hybrid architecture’s primary contribution is price stabilisation

13

rather than raw throughput improvement, consistent with the main text’s interpretation that the benefit concentrates in the congested-but-not-saturated regime.

## _F. Experiment 5: Statistical Summary_

_Main effects.:_ Kruskal–Wallis tests across all 240 runs confirm that governance policy has a highly significant main effect on all metrics: latency ( _H_ (1) = 16 _._ 8, _p <_ 10 _[−]_[4] ), drop rate ( _H_ (1) = 15 _._ 6, _p <_ 10 _[−]_[4] ), welfare ( _H_ (1) = 10 _._ 5, _p_ = 0 _._ 001), and price volatility ( _H_ (1) = 118, _p <_ 10 _[−]_[26] ). Architecture has a significant main effect on latency ( _H_ (1) = 10 _._ 1, _p_ = 0 _._ 001) and price volatility ( _H_ (1) = 10 _._ 3, _p_ = 0 _._ 001), but not on drop rate ( _p_ = 0 _._ 57) or welfare ( _p_ = 0 _._ 52), confirming that the hybrid architecture acts primarily through price stabilisation.

_Synergy analysis.:_ The synergy measure ∆synergy (see Section VI methodology) reveals topology-dependent interaction patterns. For the tree topology under high load, ∆synergy = _−_ 0 _._ 83 [95% CI: _−_ 1 _._ 04, _−_ 0 _._ 59], indicating significant sub-additivity: the combination achieves less than the sum of individual gains. For tree/medium, ∆synergy = _−_ 0 _._ 13 [ _−_ 0 _._ 38, 0 _._ 10], with the CI including zero (additive). For SP topologies, the synergy term is near zero and CIs include zero in both load conditions (SP/medium: 0 _._ 10 [ _−_ 0 _._ 21, 0 _._ 48]; SP/high: 0 _._ 01 [ _−_ 0 _._ 31, 0 _._ 24]), confirming additive composition. For entangled topologies, the synergy term is positive with CIs excluding zero (entangled/medium: 0 _._ 39 [0 _._ 18, 0 _._ 64]; entangled/high: 0 _._ 08 [0 _._ 004, 0 _._ 24]), suggesting mildly superadditive effects where the combination of price smoothing and governance partitioning provides more benefit than predicted by individual contributions, though the absolute magnitude is small given that entangled/high is near total saturation.

## _G. Experiment 6: Mechanism Ablation Results_

Experiment 6 compares four allocation mechanisms (random, EDF, value-greedy, market) across three topologies, two load levels, and two architectures (4 _×_ 3 _×_ 2 _×_ 2 _×_ 10 = 480 runs). The main text presents na¨ıve architecture results; here we report the full result table and statistical summary including hybrid architecture conditions.

_Key finding: market ≈ value-greedy.:_ Across all 480 runs, the market mechanism and value-greedy allocation produce near-identical outcomes: the maximum welfare difference is 0 _._ 07 a.u. ( _<_ 1% of peak welfare), and the maximum droprate difference is 0 _._ 16 percentage points. This occurs because tˆatonnement prices converge to near-zero under truthful bidding: with no strategic misreporting, the price signal is informationally redundant and surplus ordering reduces to value ordering.

_Hybrid architecture.:_ The market–value-greedy nearequivalence holds under hybrid architecture. A notable architecture-dependent result appears for SP/high load: under hybrid, random and EDF allocation achieve welfare of 18 _._ 2– 18 _._ 3 a.u. versus 5 _._ 9 for value-greedy/market. The hybrid architecture’s efficiency factor reduces effective demand, creating headroom where load-spreading heuristics outperform valueconcentrating strategies. This reversal does not occur under

**==> picture [177 x 246] intentionally omitted <==**

**----- Start of picture text -----**<br>
Agentic Layer<br>Tasks  Ti(t) , Messages  mi(t)<br>Valuation Layer<br>Vik (Tik , qik )<br>Service Layer / Dependency DAG<br>Capacities  C(t) Gres = (R, E)<br>Feasible Set<br>Xres ∩ Xgov<br>Mechanism  M<br>(mi(t), st) → (xt, Pi(t))<br>State Update<br>st+1 = Ψ(st, xt, P (t), ξt)<br>Trust<br>i(t) ϕ<br>, Policy  Governance<br>G(t)<br>**----- End of picture text -----**<br>


Fig. 7. Model overview: agentic layer, latency-aware valuations, resource dependencies, governance constraints, mechanism, and state evolution.

na¨ıve architecture at the same load, demonstrating that the optimal allocation strategy depends jointly on topology, load, and architectural context.

## _H. Experiment 6: Statistical Summary_

_Main effects (na¨ıve architecture).:_ Kruskal–Wallis tests for the mechanism factor are highly significant in all topology _×_ load conditions when stratified by architecture (all _p <_ 0 _._ 002). The strongest effects appear for entangled/medium ( _H_ (3) = 29 _._ 4, _p <_ 10 _[−]_[6] ) and tree/high ( _H_ (3) = 29 _._ 5, _p <_ 10 _[−]_[6] ).

_Pairwise comparisons (Wilcoxon, Holm-corrected).:_ The greedy ev vs. market contrast is non-significant in every condition ( _p_ adj _≥_ 0 _._ 59; Cliff’s _δ ≤_ 0 _._ 15, negligible), confirming they are statistically indistinguishable. The greedy ev vs. random contrast is significant and large in most conditions: tree/high ( _p_ = 0 _._ 001, _δ_ = 1 _._ 0), entangled/medium ( _p_ = 0 _._ 001, _δ_ = 1 _._ 0), SP/high ( _p_ = 0 _._ 001, _δ_ = 1 _._ 0). The SP/medium reversal (random outperforms greedy ev) is also statistically significant ( _p_ = 0 _._ 022, _δ_ = _−_ 0 _._ 78, large effect). EDF and random are not distinguishable in any condition ( _p ≥_ 0 _._ 24).

_Theory-to-experiment mapping.:_ Table XII links each formal result from the main paper to the experiment that tests its predictions and the key observables used for evaluation.

_Ablation table (complete).:_ The following table summarises the full ablation matrix across all six experiments. Each row indicates which components are ablated and the corresponding experiment.

## VII. ADDITIONAL MATERIAL

## _A. Model Overview and Assumptions_

The framework in the main paper rests on assumptions standard in network/service management and mechanism design.

14

**==> picture [253 x 201] intentionally omitted <==**

**----- Start of picture text -----**<br>
Topology tree sp entangled<br>155<br>150 80%<br>145<br>60%<br>140<br>40%<br>135<br>100% 0.5<br>75% 0.4<br>0.3<br>50%<br>0.2<br>25%<br>0.1<br>0% 0.0<br>20 40 60 20 40 60<br>Number of agents (N) Number of agents (N)<br>Latency (ms) Drop rate (%)<br>)σ<br>Price vol. (<br>Deadline satisfaction (%)<br>**----- End of picture text -----**<br>


Fig. 8. Experiment 2: Topology-dependent scaling as agent count increases ( _N_ = 10–60). Panels: median latency, drop rate, deadline satisfaction, price volatility.

In particular, we assume that: (i) autonomous agents drive service demand and resource negotiation [35], [19]; (ii) tasks are latency- and QoS-sensitive [36]; (iii) the system spans heterogeneous device–edge–cloud resources [37], [36]; (iv) services depend on multi-layer resource compositions [36], [16]; (v) resource availability and network conditions vary over time [36], [38]; (vi) governance and policies constrain resource usage [22]; (vii) agents may withhold or misreport private information [25]; (viii) reputation reflects provider reliability [23], [24]; (ix) architectural encapsulation (slicing, virtualisation) is possible [39], [16]; and (x) at each decision epoch, agents evaluate allocations with respect to a sufficiently aligned representation of the system state [40], [41]. That is, while private information and strategic incentives remain, agents condition their valuations on a commonly accepted state description _st_ capturing resource capacities, network conditions, governance constraints, and reputational signals. The paper therefore focuses on normative allocation and mechanism design given a shared operational state, and does not model heterogeneous beliefs or epistemic disagreement about the underlying environment. The system state evolves in a Markovian manner driven by allocations, network conditions, and stochastic events.

## _B. Experiment 2: Topology-Dependent Scaling_

The second experiment tests whether the rate of performance degradation as the agent population increases depends on DAG topology, reinforcing that structure is a first-order determinant of scalability. We compare three topologies (tree, SP, entangled) across _N ∈{_ 10 _,_ 20 _,_ 30 _,_ 40 _,_ 50 _,_ 60 _}_ agents under medium load ( _λ_ = 1 _._ 0), with na¨ıve architecture and no governance. This yields 3 _×_ 6 _×_ 10 = 180 runs.

Fig. 8 reveals three qualitatively different scaling regimes. The tree topology exhibits graceful degradation: median latency increases by only 3 ms across the full range (136 ms at _N_ = 10 to 139 ms at _N_ = 60), drop rates rise gently from

38% to 40%, deadline satisfaction remains approximately 60% throughout, and price volatility stays at zero. The balanced per-tier demand of tree-structured tasks distributes load evenly across tiers, preventing any single tier from saturating.

The SP topology shows moderate degradation. Latency and drop rates remain stable up to approximately _N_ = 40 (median latency 140 ms, drop rate 42%), then increase as cloud-tier demand exceeds capacity: by _N_ = 60, the drop rate reaches 67% and deadline satisfaction falls to 33%. However, prices remain stable (zero volatility) even at _N_ = 60, indicating that the SP topology’s fully polymatroidal structure (Proposition 1) supports convergent tˆatonnement when utilisation remains below the saturation threshold.

The entangled topology degrades earliest and most sharply. Drop rates rise steeply from 43% at _N_ = 10 to 93% at _N_ = 60, and deadline satisfaction falls from 57% to just 7%. Critically, price volatility emerges at _N_ = 30 ( _σ_ = 0 _._ 116) and peaks at _σ_ = 0 _._ 373 around _N_ = 50, confirming that the onset of price instability coincides with the point at which per-tier demand exceeds the capacity threshold. Median latency for the entangled topology increases from 142 ms to 152 ms across the range, a modest absolute increase that obscures the far more dramatic degradation visible in drop rate and price stability.

These results show that the “scaling ceiling”, the agent count at which the system transitions from stable to degraded operation, depends critically on topology. For the tree topology, no such ceiling is visible within the tested range. For SP, degradation begins around _N_ = 40. For entangled, degradation begins by _N_ = 20–30, with complete market failure (near-total drops, persistent price oscillation) by _N_ = 60. This confirms that topology is a first-order determinant of scalability, not merely a secondary factor behind load.

## _C. Extended Mechanism-Design Discussion_

This section provides additional detail on three aspects of the mechanism-design results that are condensed in the main paper for space.

_Governance preservation of polymatroidal structure.:_ Governance constraints _X_ gov impose coordinate-wise upper bounds _xl ≤ ul_ on each leaf service, encoding trust-based admission, jurisdictional filters, and access control. The intersection of a polymatroid _P_ ( _f_ ) with coordinate truncations _{x_ : _xl ≤ ul}_ is again a polymatroid, with rank function _f[′]_ ( _S_ ) = min _T ⊆S_ � _f_ ( _T_ ) +[�] _l∈S\T[u][l]_ � [2]. Hence _Xt_ = _X_ res _∩X_ gov inherits polymatroidal structure. This preservation result relies on governance constraints being expressible as independent per-leaf upper bounds; more complex governance couplings (e.g., mutual exclusivity across leaves, crossjurisdictional budget quotas, or path-specific exclusions) would generally not preserve polymatroidal structure and require separate treatment.

_Conditions for gross-substitutes valuations.:_ Condition (c) of Lemma 1 ensures that the items over which GS is defined have stable characteristics during each allocation round; between epochs, slice attributes may change as congestion and routing conditions evolve, and GS is re-established under the updated parameters. Note that slice capacities (the

15

number of available units of each slice type) are determined by the polymatroid _X_ res, not by the valuations; this is a feasibility condition relevant to Proposition 2 rather than a requirement for GS itself. Additive separability (condition (b)) is critical: shared agent-side budgets, cross-task latency coupling, or shared token caps would break it and can destroy the GS property. Without encapsulation, agents would bid on resource bundles along DAG paths, introducing complementarities that violate GS. Encapsulation eliminates these by absorbing them into the integrator.

_Roles of polymatroidal structure and inter-epoch limitations.:_ Together, Propositions 1–2 and Lemma 1 establish that, _within each decision epoch_ (during which slice attributes are exogenous and fixed), real-time AI service economies with tree or series–parallel dependency structures admit mechanisms that are efficient, DSIC, and individually rational. The polymatroidal structure serves three distinct roles in this chain: characterising the feasibility geometry of the supply region (Proposition 1), enabling Walrasian equilibrium existence under GS valuations via discrete convex analysis (Proposition 2(i)), and supporting the clinching-auction implementation in the singleparameter case (Proposition 2(iii)). When agents’ demands decompose into independent per-task single-parameter demands, the ascending clinching auction additionally guarantees weak budget balance, with polynomial-time complexity that is practical when the number of slice types and the valuation range are moderate. Across epochs, load-induced changes to slice latencies and capacities may alter the items being traded; the mechanism is re-invoked at each epoch under updated parameters, and the GS/equilibrium guarantees apply epoch-by-epoch rather than as a dynamic-equilibrium result. In particular, the repeated interaction across epochs can induce strategic dynamics—such as learning, reputation gaming, or inter-epoch demand manipulation—that are outside the scope of the present per-epoch theorems.

_Theoretical positioning.:_ The formal results in this paper apply classical polymatroid theory, the gross-substitutes characterisation, and VCG mechanism design to a novel application domain: real-time AI service economies across the computing continuum. The main contribution is problem formulation, not new mechanism-design theory: identifying that AI service-dependency graphs with tree or series–parallel structure satisfy the structural conditions (polymatroidal feasibility, gross substitutes) under which efficient, incentivecompatible mechanisms exist and are polynomial-time computable. Individual results (Propositions 1–2 and Lemma 1) instantiate known theorems in the service-dependency setting; the encapsulation result (Proposition 3) provides the paper’s main conceptual contribution by reducing cross-domain allocation to matroid feasibility, bridging classical single-domain mechanism design and the multi-tier architecture that production deployments require. The theoretical value lies in the structural identification (that the problem has the right shape for these classical results) and in the architectural consequence (that encapsulation makes the classical results operationally deployable), rather than in the individual mechanism-design results themselves.

## REFERENCES

- [1] J. Edmonds, “Submodular functions, matroids, and certain polyhedra,” in _Combinatorial Optimization—Eureka, You Shrink!_ Berlin, Heidelberg: Springer-Verlag, 2003, pp. 11–26, originally published in _Combinatorial Structures and their Applications_ , Gordon and Breach, 1970.

- [2] S. Fujishige, _Submodular Functions and Optimization_ , 2nd ed. Elsevier, 2005, vol. 58.

- [3] A. S. Kelso and V. P. Crawford, “Job matching, coalition formation, and gross substitutes,” _Econometrica_ , vol. 50, no. 6, pp. 1483–1504, 1982.

- [4] F. Gul and E. Stacchetti, “Walrasian equilibrium with gross substitutes,” _Journal of Economic Theory_ , vol. 87, no. 1, pp. 95–124, 1999.

- [5] L. M. Ausubel and P. Milgrom, “The lovely but lonely Vickrey auction,” in _Combinatorial Auctions_ , P. Cramton, Y. Shoham, and R. Steinberg, Eds. MIT Press, 2006, pp. 17–40.

- [6] L. M. Ausubel, “An efficient ascending-bid auction for multiple objects,” _American Economic Review_ , vol. 94, no. 5, p. 1452–1475, December 2004.

- [7] G. Goel _et al._ , “Polyhedral clinching auctions and the adwords polytope,” _Journal of the ACM_ , vol. 62, no. 3, pp. 1–27, 2015.

- [8] S. Fujishige and Z. Yang, “A note on Kelso and Crawford’s gross substitutes condition,” _Mathematics of Operations Research_ , vol. 28, no. 3, pp. 463–469, 2003.

- [9] K. Murota, _Discrete Convex Analysis_ , ser. Monographs on Discrete Mathematics and Applications. SIAM, 2003.

- [10] H. Hu _et al._ , “Intelligent resource allocation for edge-cloud collaborative networks: A hybrid ddpg-d3qn approach,” _IEEE Transactions on Vehicular Technology_ , vol. 72, no. 8, pp. 10 696–10 709, 2023.

- [11] Y. Liu _et al._ , “Data orchestration service placement and resource allocation scheme for cloud-edge system,” _IEEE Transactions on Services Computing_ , 2026.

- [12] C. Tang _et al._ , “Collaborative service caching, task offloading, and resource allocation in caching-assisted mobile edge computing,” _IEEE Transactions on Services Computing_ , 2025.

- [13] S. Li _et al._ , “Tiered-pricing-based task offloading strategy in collaborative edge-cloud computing: A matching game approach,” _IEEE Internet of Things Journal_ , vol. 12, no. 11, pp. 15 114–15 129, 2025.

- [14] X. Xie _et al._ , “Coedge: A collaborative architecture for efficient task offloading among multiple edge service providers,” _IEEE Internet of Things Journal_ , 2025.

- [15] C. Shang _et al._ , “Joint computation offloading and service caching in mobile edge-cloud computing via deep reinforcement learning,” _IEEE Internet of Things Journal_ , vol. 11, no. 24, pp. 40 331–40 344, 2024.

- [16] H. Hantouti _et al._ , “Service function chaining in 5g & beyond networks: Challenges and open research issues,” 2022, arXiv preprint arXiv:2201.05455.

- [17] W. Fan _et al._ , “Drl-based service function chain edge-to-edge and edgeto-cloud joint offloading in edge-cloud network,” _IEEE Transactions on Network and Service Management_ , vol. 20, no. 4, pp. 4478–4493, 2023.

- [18] M. R. G. Oskoui and B. Sans`o, “Distributed dependency-aware task offloading and service caching in cloudlet-based edge computing networks,” _IEEE Transactions on Services Computing_ , 2026.

- [19] J. S. Park _et al._ , “Generative agents: Interactive simulacra of human behavior,” in _Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology_ , ser. UIST ’23. New York, NY, USA: Association for Computing Machinery, 2023.

- [20] S. Deng _et al._ , “Agentic services computing,” 2025, arXiv preprint arXiv:2509.24380.

- [21] B. Sedlak _et al._ , “Service orchestration in the computing continuum: Structural challenges and vision,” 2026, arXiv preprint arXiv:2602.15794.

- [22] N. Fornara, _Specifying and Monitoring Obligations in Open Multiagent Systems Using Semantic Web Technology_ . Berlin, Heidelberg: Springer Berlin Heidelberg, 2011, pp. 25–45.

- [23] H. Li and M. Singhal, “ Trust Management in Distributed Systems ,” _Computer_ , vol. 40, no. 02, pp. 45–53, Feb. 2007.

- [24] X. Wang _et al._ , “A survey on trustworthy edge intelligence: From security and reliability to transparency and sustainability,” _IEEE Communications Surveys & Tutorials_ , vol. 27, no. 3, pp. 1729–1757, 2025.

- [25] R. P. McAfee, “A dominant strategy double auction,” _Journal of Economic Theory_ , vol. 56, no. 2, pp. 434–450, 1992.

- [26] C. Weinhardt _et al._ , “Cloud computing – a classification, business models, and research directions,” _Business & Information Systems Engineering_ , vol. 1, no. 5, pp. 391–399, 2009.

- [27] U. Habiba _et al._ , “A repeated auction model for load-aware dynamic resource allocation in multi-access edge computing,” _IEEE Transactions on Mobile Computing_ , vol. 23, no. 7, pp. 7801–7817, 2023.

16

- [28] X. Zheng _et al._ , “Resource allocation and network pricing based on double auction in mobile edge computing,” _Journal of Cloud Computing_ , vol. 12, no. 1, p. 56, 2023.

- [29] B. Efron and R. J. Tibshirani, _An Introduction to the Bootstrap_ . Chapman & Hall/CRC, 1994.

- [30] W. H. Kruskal and W. A. Wallis, “Use of ranks in one-criterion variance analysis,” _Journal of the American Statistical Association_ , vol. 47, no. 260, pp. 583–621, 1952.

- [31] S. Holm, “A simple sequentially rejective multiple test procedure,” _Scandinavian Journal of Statistics_ , vol. 6, no. 2, pp. 65–70, 1979.

- [32] N. Cliff, “Dominance statistics: Ordinal analyses to answer ordinal questions,” _Psychological Bulletin_ , vol. 114, no. 3, pp. 494–509, 1993.

- [33] J. Romano _et al._ , “Appropriate statistics for ordinal level data: Should we really be using t-test and Cohen’s d for evaluating group differences on the NSSE and similar surveys?” _Annual Meeting of the Florida Association of Institutional Research_ , pp. 1–33, 2006.

- [34] J. O. Wobbrock _et al._ , “The aligned rank transform for nonparametric factorial analyses using only ANOVA procedures,” in _Proc. SIGCHI Conference on Human Factors in Computing Systems_ . ACM, 2011, pp. 143–146.

- [35] H. Derouiche _et al._ , “Agentic ai frameworks: Architectures, protocols, and design challenges,” 2025, arXiv preprint arXiv:2508.10146.

- [36] T. Meuser, L. Lov´en _et al._ , “Revisiting edge AI: Opportunities and challenges,” _IEEE Internet Computing_ , vol. 28, no. 4, pp. 49–59, 2024.

- [37] F. Bonomi _et al._ , “Fog computing and its role in the internet of things,” in _Proceedings of the First Edition of the MCC Workshop on Mobile Cloud Computing_ , ser. MCC ’12. New York, NY, USA: Association for Computing Machinery, 2012, p. 13–16.

- [38] Z. Zhou _et al._ , “Edge intelligence: Paving the last mile of artificial intelligence with edge computing,” _Proceedings of the IEEE_ , vol. 107, no. 8, pp. 1738–1762, 2019.

- [39] X. Foukas _et al._ , “Network slicing in 5G: Survey and challenges,” _IEEE Communications Magazine_ , vol. 55, no. 5, pp. 94–100, 2017.

- [40] L. Lov´en _et al._ , “Large language models in the 6g-enabled computing continuum: A white paper,” 6G Flagship, University of Oulu, Tech. Rep. 14, 2025, available at: https://www.6gflagship.com/publications/.

- [41] ——, “Semantic slicing across the distributed intelligent 6g wireless networks,” in _Proceedings of the IEEE International Conference on Sensing, Communication and Networking (SECON)_ , 2023, pp. 79–84.

17

TABLE IX

EXPERIMENT 4 ABLATION: NA¨IVE, HYBRID (EMA ONLY), AND HYBRID (FULL) ARCHITECTURE COMPARISON

|**Topology**<br>**Load**<br>**Architecture**|_N_<br>**Med. Lat. (ms)**<br>**Drop Rate**<br>**Welfare**<br>**Price Vol. (**_σ_**)**|
|---|---|
|SP<br>Medium<br>Na¨ıve<br>SP<br>Medium<br>EMA only<br>SP<br>Medium<br>Full hybrid<br>SP<br>Medium<br>Na¨ıve<br>SP<br>Medium<br>EMA only<br>SP<br>Medium<br>Full hybrid<br>SP<br>Medium<br>Na¨ıve<br>SP<br>Medium<br>EMA only<br>SP<br>Medium<br>Full hybrid<br>SP<br>Medium<br>Na¨ıve<br>SP<br>Medium<br>EMA only<br>SP<br>Medium<br>Full hybrid|20<br>138<br>0.40<br>9.2<br>0.000<br>20<br>138<br>0.40<br>9.2<br>0.096<br>20<br>137<br>0.39<br>9.3<br>0.096|
||40<br>140<br>0.42<br>17.4<br>0.000<br>40<br>140<br>0.42<br>17.4<br>0.096<br>40<br>138<br>0.41<br>17.9<br>0.096|
||60<br>139<br>0.67<br>14.8<br>0.000<br>60<br>139<br>0.67<br>14.8<br>0.096<br>60<br>138<br>0.67<br>15.1<br>0.096|
||80<br>149<br>0.95<br>2.9<br>0.198<br>80<br>149<br>0.95<br>3.0<br>0.097<br>80<br>139<br>0.95<br>3.0<br>0.096|
|SP<br>High<br>Na¨ıve<br>SP<br>High<br>EMA only<br>SP<br>High<br>Full hybrid<br>SP<br>High<br>Na¨ıve<br>SP<br>High<br>EMA only<br>SP<br>High<br>Full hybrid<br>SP<br>High<br>Na¨ıve<br>SP<br>High<br>EMA only<br>SP<br>High<br>Full hybrid<br>SP<br>High<br>Na¨ıve<br>SP<br>High<br>EMA only<br>SP<br>High<br>Full hybrid|20<br>141<br>0.42<br>12.9<br>0.000<br>20<br>141<br>0.42<br>12.9<br>0.096<br>20<br>139<br>0.41<br>13.4<br>0.096|
||40<br>141<br>0.68<br>14.4<br>0.000<br>40<br>141<br>0.68<br>14.4<br>0.096<br>40<br>139<br>0.67<br>14.9<br>0.096|
||60<br>197<br>1.00<br>0.3<br>0.337<br>60<br>315<br>0.99<br>0.4<br>0.097<br>60<br>181<br>0.99<br>0.4<br>0.096|
||80<br>635<br>1.00<br>0.0<br>0.286<br>80<br>699<br>1.00<br>0.0<br>0.097<br>80<br>674<br>1.00<br>0.0<br>0.097|
|Entangled<br>Medium<br>Na¨ıve<br>Entangled<br>Medium<br>EMA only<br>Entangled<br>Medium<br>Full hybrid<br>Entangled<br>Medium<br>Na¨ıve<br>Entangled<br>Medium<br>EMA only<br>Entangled<br>Medium<br>Full hybrid<br>Entangled<br>Medium<br>Na¨ıve<br>Entangled<br>Medium<br>EMA only<br>Entangled<br>Medium<br>Full hybrid<br>Entangled<br>Medium<br>Na¨ıve<br>Entangled<br>Medium<br>EMA only<br>Entangled<br>Medium<br>Full hybrid|20<br>145<br>0.46<br>8.0<br>0.000<br>20<br>145<br>0.46<br>8.0<br>0.096<br>20<br>144<br>0.45<br>8.2<br>0.096|
||40<br>149<br>0.63<br>10.8<br>0.287<br>40<br>150<br>0.63<br>10.7<br>0.262<br>40<br>146<br>0.61<br>11.4<br>0.096|
||60<br>152<br>0.93<br>3.1<br>0.301<br>60<br>156<br>0.93<br>3.0<br>0.097<br>60<br>155<br>0.93<br>2.9<br>0.154|
||80<br>439<br>1.00<br>0.0<br>0.274<br>80<br>453<br>1.00<br>0.0<br>0.097<br>80<br>473<br>1.00<br>0.0<br>0.097|
|Entangled<br>High<br>Na¨ıve<br>Entangled<br>High<br>EMA only<br>Entangled<br>High<br>Full hybrid<br>Entangled<br>High<br>Na¨ıve<br>Entangled<br>High<br>EMA only<br>Entangled<br>High<br>Full hybrid<br>Entangled<br>High<br>Na¨ıve<br>Entangled<br>High<br>EMA only<br>Entangled<br>High<br>Full hybrid<br>Entangled<br>High<br>Na¨ıve<br>Entangled<br>High<br>EMA only<br>Entangled<br>High<br>Full hybrid|20<br>151<br>0.53<br>10.1<br>0.066<br>20<br>151<br>0.53<br>10.1<br>0.141<br>20<br>147<br>0.50<br>10.9<br>0.096|
||40<br>157<br>0.93<br>3.0<br>0.307<br>40<br>164<br>0.93<br>3.0<br>0.165<br>40<br>162<br>0.93<br>3.0<br>0.097|
||60<br>683<br>1.00<br>0.0<br>0.270<br>60<br>651<br>1.00<br>0.0<br>0.097<br>60<br>684<br>1.00<br>0.0<br>0.097|
||80<br>688<br>1.00<br>0.0<br>0.346<br>80<br>620<br>1.00<br>0.0<br>0.097<br>80<br>684<br>1.00<br>0.0<br>0.097|



Values averaged over 10 seeds. EMA only: integrator with price smoothing but efficiency = 1 _._ 0; full hybrid: EMA plus efficiency factor (SP: 0 _._ 75, entangled: 0 _._ 85). EMA smoothing accounts for the majority of the price-volatility reduction; the efficiency factor primarily improves latency and welfare in the congested-but-not-saturated regime.

18

TABLE X

EXPERIMENT 5: ARCHITECTURE _×_ GOVERNANCE INTERACTION ( _N_ = 50, MEDIUM AND HIGH LOAD)

|**Topology**<br>**Load**|**Arch.**<br>**Gov.**<br>**Med. Lat. (ms)**<br>**Drop Rate**<br>**Welfare**<br>**Price Vol. (**_σ_**)**|
|---|---|
|Tree<br>Medium<br>Tree<br>Medium<br>Tree<br>Medium<br>Tree<br>Medium<br>Tree<br>High<br>Tree<br>High<br>Tree<br>High<br>Tree<br>High|Na¨ıve<br>None<br>138<br>0.40<br>23.0<br>0.000<br>Na¨ıve<br>Strict<br>137<br>0.73<br>10.6<br>0.770<br>Hybrid<br>None<br>137<br>0.39<br>23.4<br>0.096<br>Hybrid<br>Strict<br>136<br>0.72<br>10.9<br>0.208|
||Na¨ıve<br>None<br>142<br>0.49<br>28.6<br>0.000<br>Na¨ıve<br>Strict<br>138<br>0.67<br>18.5<br>1.152<br>Hybrid<br>None<br>139<br>0.47<br>30.0<br>0.096<br>Hybrid<br>Strict<br>137<br>0.67<br>19.1<br>0.498|
|SP<br>Medium<br>SP<br>Medium<br>SP<br>Medium<br>SP<br>Medium<br>SP<br>High<br>SP<br>High<br>SP<br>High<br>SP<br>High|Na¨ıve<br>None<br>140<br>0.53<br>17.4<br>0.000<br>Na¨ıve<br>Strict<br>138<br>0.63<br>13.9<br>0.775<br>Hybrid<br>None<br>138<br>0.52<br>18.0<br>0.096<br>Hybrid<br>Strict<br>137<br>0.62<br>14.5<br>0.195|
||Na¨ıve<br>None<br>146<br>0.90<br>5.7<br>0.112<br>Na¨ıve<br>Strict<br>140<br>0.97<br>1.7<br>0.407<br>Hybrid<br>None<br>140<br>0.90<br>5.9<br>0.096<br>Hybrid<br>Strict<br>139<br>0.97<br>1.9<br>0.202|
|Entangled<br>Medium<br>Entangled<br>Medium<br>Entangled<br>Medium<br>Entangled<br>Medium<br>Entangled<br>High<br>Entangled<br>High<br>Entangled<br>High<br>Entangled<br>High|Na¨ıve<br>None<br>149<br>0.77<br>8.4<br>0.373<br>Na¨ıve<br>Strict<br>145<br>0.81<br>7.1<br>1.315<br>Hybrid<br>None<br>146<br>0.76<br>8.6<br>0.096<br>Hybrid<br>Strict<br>144<br>0.79<br>7.7<br>0.388|
||Na¨ıve<br>None<br>404<br>1.00<br>0.1<br>0.273<br>Na¨ıve<br>Strict<br>199<br>1.00<br>0.1<br>0.455<br>Hybrid<br>None<br>444<br>1.00<br>0.1<br>0.097<br>Hybrid<br>Strict<br>168<br>1.00<br>0.2<br>0.313|



Values averaged over 10 seeds. Hybrid architecture reduces governance-induced price volatility by 57–82% across structured topologies (e.g., tree/high: na¨ıve/strict _σ_ = 1 _._ 15 vs. hybrid/strict _σ_ = 0 _._ 50).

19

TABLE XI

EXPERIMENT 6: MECHANISM ABLATION SUMMARY (NA¨IVE ARCHITECTURE, AVERAGED OVER 10 SEEDS)

|**Topology**|**Load**|**Random**|**EDF**|**Greedy EV**|**Market**|
|---|---|---|---|---|---|
|_Welfare (a.u.)_||||||
|Tree|Medium|22.1|22.1|23.0|23.0|
|Tree|High|24.4|24.3|28.6|28.6|
|SP|Medium|17.8|17.7|17.4|17.4|
|SP|High|2.4|2.5|5.7|5.7|
|Entangled|Medium|0.3|0.3|8.4|8.4|
|Entangled|High|0.0|0.0|0.1|0.1|
|_Drop rate (%)_||||||
|Tree|Medium|41.3|41.2|39.7|39.7|
|Tree|High|53.5|53.7|48.8|48.8|
|SP|Medium|50.0|50.3|53.4|53.4|
|SP|High|93.9|93.8|89.8|89.8|
|Entangled|Medium|98.9|98.8|76.9|76.7|
|Entangled|High|100|100|99.9|99.8|



## TABLE XII

THEORY-TO-EXPERIMENT MAPPING. EACH FORMAL RESULT IS PAIRED WITH ITS EMPIRICAL TEST AND KEY OBSERVABLES.

|**Result**|**Experiment**|**Observables**|
|---|---|---|
|Prop. 1 (Polymatroid)|Exps. 1–2 (_−_S)|_σp_, drop rate, scaling|
|Lemma 1 (GS valuations)|Exp. 6 (_−_M)|Welfare equivalence|
|Prop. 2 (DSIC mechanism)|Exp. 6 (_−_M)|Market _≈_value-greedy|
|Prop. 3 (Encapsulation)|Exp. 4 (_−_H)|_σp_ reduction, latency|



## TABLE XIII

COMPLETE ABLATION MATRIX

|**Ablation**|**Source**|**Isolates**|
|---|---|---|
|Full system (S+H+G+M)|Exp 5 (hybrid, strict)|Everything on|
|_−_M (remove market)|Exp 6 (greedy<br>ev vs. market)|Price coordination|
|_−_G (remove governance)|Exp 5 (no gov conditions)|Trust-gated capacity|
|_−_H (remove hybrid)|Exp 4 (na¨ıve conditions)|Integrator encapsulation|
|_−_Hef (remove eff. factor)|Exp 4 (EMA only)|Effciency sub-component|
|_−_S (break structure)|Exp 1/4 (entangled)|Structural discipline|
|_−_M_−_H (heuristic + na¨ıve)|Exp 6 (EDF, na¨ıve)|Scheduling-only baseline|
|_−_S_−_H_−_M (worst case)|Exp 6 (random, entangled)|Absolute foor|
