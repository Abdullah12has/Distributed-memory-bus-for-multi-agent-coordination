**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

## **Use Case: The University of Oulu AI Service Economy**

University of Oulu, Faculty of ITEE, CSE Research Unit

## **Contents**

|**1. **|**The Institutional Landscape**|**2**|
|---|---|---|
||Three phases of maturity<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|3|
|**2. **|**Prof. Koskela’s Infrastructure**|**4**|
||Phase 0 (today) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|4|
||Phase 1 (agentic interface)<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|4|
||Phase 2 (service economy) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|4|
|**3. **|**A Week at the University**|**5**|
||3.1 Monday Morning Triage . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|5|
||3.2 Grant Proposal Preparation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|5|
||3.3 Contract Review and Budget Verifcation . . . . . . . . . . . . . . . . . . . . . . .|6|
||3.4 Teaching Workfow . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|7|
||3.5 Publication Lifecycle . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|7|
||3.6 Travel and Hourly Reporting<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|8|
||3.7 Period-End Project Reporting. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|8|
||3.8 Development Discussions. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|9|
|**4. **|**The Monthly Ledger**|**10**|
|**5. **|**The Ecosystem Behind the Scenes**|**11**|
||5.1 Integrator Taxonomy (Phase 2) . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|11|
||5.2 How the Exchange Works (Phase 2) . . . . . . . . . . . . . . . . . . . . . . . . . .|12|
||5.3 Trust and Quality . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|12|
|**6. **|**Why This Requires a Neutral Exchange**|**12**|



Page 1 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

|**7. **|**From the University to the Addressable Market**||**13**|
|---|---|---|---|
|**8. **|**Implementation Roadmap**||**13**|
||Phase 0 ￿<br>Phase 1: Agentic interfaces (current research program)|. . . . . . . . . .|13|
||Phase 1 ￿<br>Phase 2: Service economy (exchange implementation) .|. . . . . . . . . .|13|



## **How institutional information systems evolve from manual web interfaces to a coordinated AI service economy**

## Internal **Date:** March 2026

This document follows a representative research group leader through a working week, showing the same tasks at three levels of maturity. In Phase 0 (today), every system is accessed manually through separate web interfaces. In Phase 1 (agentic interface), AI agents handle individual systems with fixed routing rules. In Phase 2 (service economy), a neutral exchange coordinates agents across all systems, optimizing cost and enforcing governance automatically. The Phase 0 to Phase 1 transition delivers the transformative improvement in time: hours of manual work collapse to minutes of agent-assisted review. The Phase 1 to Phase 2 transition delivers the transformative improvement in cost: dynamic market coordination reduces agentic compute costs by roughly 45% versus fixed-routing operation, while enabling shared specialized agents and governance infrastructure that no individual department could justify building alone.

## **1. The Institutional Landscape**

The University of Oulu operates a patchwork of information systems, each with its own web interface, data model, and access control:

|System|Function|Interface complexity|
|---|---|---|
|Publication DB|Research output|Moderate|
||tracking||
|Contract DB|Research contracts,|High|
||grants, funding;||
||license compliance||
||and export-restriction||
||tracking||
|Moodle|Learning|Moderate|
||management, course||
||materials||
|Patio|University intranet,|Moderate|
||service information,||
||proposal budgeting||
||tools||



Page 2 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

|System|Function|Interface complexity|
|---|---|---|
|Peppi|Course participation|Moderate|
||and outcomes||
||tracking||
|CRM|Stakeholder relations,|Moderate|
||alumni, industry||
||partners||
|Ofce 365 /|Email, calendars,|Moderate|
|Teams|document repository;||
||some groups also use||
||Slack or Discord||
|Tatu|Funded-project|High|
||budgets:||
||month-by-month FTE||
||allocation, salary||
||projections,||
||budget-to-grant||
||alignment (SAP)||
|SAP Travel|Travel proposals and|High|
||expense claims (SAP)||
|SAP CATS|Hourly reporting by|High|
||project code (SAP)||



The SAP family (Tatu, SAP Travel, SAP CATS) is especially demanding: multi-step forms, nonintuitive navigation, rigid data entry rules, and no cross-system search. Tatu requires monthby-month maintenance of FTE allocations and salary projections for every funded project, with budget predictions checked against the grant agreement. A single travel claim requires collecting and scanning receipts, gathering travel documents, writing justifications for each expense item, navigating expense categories, looking up country-specific per diem rules, identifying the correct cost centers, validating project codes, and checking budget ceilings across separate interfaces. A straightforward domestic trip takes 1 to 2 hours; an international conference claim with multiple expense types, foreign-currency receipts, and split project funding can easily consume half a working day. Routine hourly reporting in SAP CATS consumes 15 to 30 minutes per week.

## **Three phases of maturity**

**Phase 0 — Manual (today).** Every system is accessed through its own web interface. Crosssystem tasks require the user to switch between browser tabs, manually copy data, and mentally integrate information. Complex tasks (grant proposals, contract reviews, year-end reports) take hours or days.

**Phase 1 — Agentic interface.** AI agents connect to individual systems through API connectors and handle queries, retrieval, and synthesis. Routing is fixed: governance-sensitive systems use the on-premises platform (ConfidentialMind), everything else defaults to the cloud platform (MS Copilot/Azure) at retail pricing. There is no marketplace to optimize cost, balance load, or enable competition between providers. No shared compute pools, no specialized agent services across departments. The current research program (thesis projects M0 through M5) operates primarily in this phase, building the agentic connectors and evaluation harness

Page 3 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

## that Phase 2 will coordinate.

**Phase 2 — Service economy.** A neutral exchange coordinates agents across all systems. Routing is dynamic: a market mechanism allocates tasks to the cheapest capable tier while enforcing governance constraints automatically. Specialized institutional agents, research compute pools, and cloud providers compete on the exchange. Cost-optimized, governancecompliant, and scalable. The software architecture for this phase comprises its own internal progression from basic posted-price exchange through ascending auction mechanisms to full governance and adversarial resilience infrastructure.

## **2. Prof. Koskela’s Infrastructure**

Prof. Marja Koskela is a research group leader and associate professor at the University of Oulu. She leads a team of 8 researchers, teaches two courses per year, manages 4 active research contracts (including EU-funded projects), and serves on the faculty research committee.

## **Phase 0 (today)**

Prof. Koskela accesses each system through its web interface: a browser with multiple tabs open to Office 365 (Outlook, Teams, calendar), Patio, Moodle, Peppi, the Publication DB, the Contract DB, Tatu, SAP Travel, and SAP CATS. Cross-system tasks require manual data lookup and re-entry. She estimates spending 8 to 12 hours per week on administrative tasks that are primarily navigation and data transfer rather than substantive decision-making.

## **Phase 1 (agentic interface)**

Three infrastructure tiers become available:

**Laptop agent.** Runs a lightweight local model (Phi-4 Mini, 3.8B parameters) for scheduling, email triage, message drafting, and simple lookups. Marginal inference cost: zero.

**On-premises platform** Runs on the university’s GPU cluster, managed by Campus IT. Hosts a capable 70 to 80 billion parameter model with RAG connectors to institutional databases. Handles contract analysis, document synthesis, cross-system queries, and governance-enforced data access. Inference cost: approximately EUR 0.10 to 0.20 per GPU-hour (internal allocation).

**Cloud platform (MS Copilot / Azure).** Frontier model access via the university’s Microsoft institutional license. Handles complex reasoning tasks: cross-domain synthesis, proposal writing, long-horizon planning. Cost: institutional SLA pricing.

Routing is fixed by IT policy: governance-sensitive data (contracts, financials, student records) goes to ConfidentialMind; everything else defaults to Azure/Copilot at retail API pricing. No competition between providers, no shared compute pools across departments, no dynamic optimization.

## **Phase 2 (service economy)**

The same three tiers, plus:

Page 4 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

- **Research compute pools:** Faculty groups pooling idle departmental GPUs into the marketplace.

- **Specialized institutional agents:** Purpose-built agents (contract review including exportrestriction checks, publication tracking, evidence generation, SAP travel/reporting automation, SAP HR form automation) available as services on the exchange.

- **Dynamic routing:** A neutral exchange matches each task to the cheapest capable provider, enforcing governance constraints as hard routing rules and optimizing cost for everything else.

## **3. A Week at the University**

## **3.1 Monday Morning Triage**

Prof. Koskela starts her week by reviewing her Office 365 calendar and email, triaging messages, and checking Patio for committee deadlines, faculty meeting agendas, and policy updates.

**Phase 0.** She opens Outlook, the Office 365 calendar, and Patio in three browser tabs. She manually scans each, mentally prioritizes, and writes a to-do list in a notebook or text file. This takes 15 to 20 minutes each morning, roughly 6 hours per month.

**Phase 1.** Her laptop agent (Phi-4 Mini, local) synthesizes the Office 365 calendar, triages emails by priority, and pulls cached Patio announcements into a ranked task list. Ready in under two seconds. Zero compute cost.

**Phase 2.** Identical to Phase 1 for this task. The exchange adds no value to a purely local operation. This is by design: the platform earns nothing on simple tasks, but honest local routing builds user trust and ensures the exchange handles only tasks where market coordination matters.

## **3.2 Grant Proposal Preparation**

Prof. Koskela is preparing a Horizon Europe proposal. She needs FTE allocations and salary projections for the proposed team (Tatu), year-by-year budget scenarios from Patio’s budgeting tools (testing staffing mixes of postdocs and doctoral students, calculating salary costs, overheads, and equipment over the project duration), partner collaboration history and capabilities (CRM), and the group’s recent publication track record (Publication DB). These must be synthesized into a coherent proposal narrative.

**Phase 0.** She opens Tatu to extract current salary levels and FTE availability for the proposed team members. She downloads Patio’s budgeting Excel sheets and tests year-by-year staffing scenarios, projecting salary costs, overheads, and equipment over the proposal’s duration. She switches to CRM to look up past collaborations with the proposed partners, copying relevant details into a document. She then searches the Publication DB for the group’s recent papers in the proposal domain. Assembling the data takes 2 to 3 hours; writing the narrative takes another 2 to 3 hours. A single proposal preparation session consumes half a working day.

**Phase 1.** The ConfidentialMind agent retrieves FTE allocations and salary projections from Tatu, budget scenario templates from Patio, partner histories from CRM, and publication records

Page 5 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

from the Publication DB through API connectors. The data retrieval completes in seconds. For the synthesis step, the agent sends the assembled briefing to Azure (the fixed routing rule routes all non-governance synthesis to cloud at retail pricing). Total time: 10 to 15 minutes of review and refinement. Compute cost: approximately EUR 3.50 (EUR 0.30 on-premises retrieval + EUR 3.20 cloud synthesis at retail API pricing with no competitive alternatives).

**Phase 2.** The exchange optimizes the allocation. The on-premises integrator encapsulates the three-system retrieval into a single slice. Multiple cloud providers compete on price for the synthesis step. If on-premises has idle capacity, the exchange routes synthesis locally at a fraction of cloud cost. If a research compute pool has spare GPUs, it undercuts both. Cost: approximately EUR 1.40. Savings over Phase 1: 60%.

## **Service-dependency DAG (Phase 2):**

Tatu FTE/salary query ─────┐ Patio budget scenarios ─────┤ CRM partner query ──────────┼──►Data fusion ──►Proposal synthesis Publication DB query ───────┘ (on-prem) (cloud frontier)

##

A new industry research contract arrives. Prof. Koskela needs to cross-reference proposed terms with existing contracts (Contract DB), verify budget allocations and overhead rates (Tatu), check actual effort logged against planned effort on related projects (SAP CATS), verify exportrestriction compliance for named researchers and any restricted technology or software licenses, and produce a structured review with flagged issues.

**Phase 0.** She opens the Contract DB and searches for similar contracts with this partner, reading through previous agreements to find comparable clauses. She switches to Tatu to check the proposed overhead rate against the institutional standard and verifies the budget ceiling for the relevant cost category. She opens SAP CATS to check whether the researchers proposed for the new contract are already over-committed on existing projects. She also checks whether any named researchers on the contract are subject to export restrictions and whether the proposed work involves restricted technology or software licenses with compliance requirements, cross-referencing against HR records and the Contract DB’s license registry. Each system requires separate login, navigation, and manual data extraction. She manually compiles the findings into a review memo. This process takes 2 to 4 hours, depending on the complexity of the contract and the number of cross-references needed.

**Phase 1.** The contract review agent (running on ConfidentialMind) performs all four operations automatically: retrieves similar contracts and precedent clauses, verifies budget rates in Tatu, cross-references effort in SAP CATS, checks export-restriction status for named personnel and license compliance requirements, and generates a structured review. The entire task stays onpremises (governance-critical). The full review completes in under three minutes. Cost: EUR 0.80 internal compute (the central on-premises cluster is shared across all departments with static allocation; during peak demand, queuing adds latency and cost).

**Phase 2.** The exchange adds dynamic capacity management. When the central cluster is busy, a research compute pool provides overflow GPU slices at lower cost. The governance interface enforces data-locality constraints throughout. An audit trail records every document accessed. Cost: approximately EUR 0.40. Savings over Phase 1: 50%.

Page 6 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

##

Prof. Koskela updates her course. She needs to revise Moodle course materials, pull relevant content from Patio for a guest lecture, generate assessment rubrics, and check Peppi for last semester’s participation and outcomes data to identify where students struggled.

**Phase 0.** She logs into Moodle and navigates the course structure, manually updating slides and adding new readings. She searches Patio for relevant internal resources, copying links and summaries. She writes assessment rubrics from scratch or adapts previous ones manually. She logs into Peppi and exports last semester’s outcomes data, then analyses it in a spreadsheet to identify low-performing topics. Updating a course for the next teaching period takes 4 to 6 hours spread over several days.

**Phase 1.** The task is executed on both platforms for comparison. On Copilot: the agent pulls Moodle content through Microsoft 365 connectors, generates rubrics using frontier reasoning, and produces outputs with Office formatting. On ConfidentialMind: the on-premises agent retrieves Moodle materials and Patio content directly, generates equivalent rubrics, and provides full audit trails. Peppi student data stays on-premises (GDPR). In routine use (outside comparison mode), the fixed routing defaults non-sensitive tasks to Copilot at cloud pricing. Time: 30 minutes to 1 hour of review. Cost: EUR 0.80 per session (Copilot retail pricing for rubric generation and content assembly).

**Phase 2.** The exchange automatically routes each sub-task to the optimal platform: rubric generation (non-sensitive) goes to whichever provider is cheapest at the moment (on-prem if idle, cloud if not); Peppi data access (GDPR-protected) goes exclusively to on-premises; Patio content retrieval is routed by availability. Competition between providers drives prices down. Cost: approximately EUR 0.25. Savings over Phase 1: 69%.

## **3.5 Publication Lifecycle**

Prof. Koskela’s group has a paper ready for submission. She needs to track co-author affiliations (Publication DB), cross-reference funder mandates (Contract DB: is open access required? are there embargo periods?), verify compliance (acknowledgments match contract terms, data availability statement is correct), check export-restriction status for international co-authors, compile an evidence bundle, and update the Publication DB.

**Phase 0.** She opens the Publication DB to check co-author affiliations and previous submissions. She switches to the Contract DB to identify which contracts fund this work and reads the relevant clauses on open access, embargo periods, and acknowledgment requirements. She manually verifies that the paper’s acknowledgment section lists the correct grant numbers and that the data availability statement matches contract terms. She updates the Publication DB with the new submission record. For projects involving international collaborators, she must also verify export-restriction compliance before submission. Cross-referencing two systems and verifying compliance takes 1 to 2 hours, with a meaningful risk of human error (a missed open-access mandate can result in funder penalties; an overlooked export restriction can have legal consequences).

**Phase 1.** The ConfidentialMind agent retrieves publication metadata and contract terms, identifies compliance requirements including export-restriction checks for international co-authors, and generates a structured checklist. However, evidence bundle generation (compiling formal compliance proofs) requires specialized capability. Without an exchange to discover and access shared services, each group must either build its own evidence tooling or use the cloud for compliance checking. The publication agent sends the compliance verification task to Azure.

Page 7 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

Time: 5 minutes of review. Cost: EUR 1.50 (EUR 0.20 on-premises retrieval + EUR 1.30 cloud compliance checking at retail pricing).

**Phase 2.** A specialized evidence-as-a-service agent (running on a research compute pool) is discoverable through the exchange. It compiles formal proof packages at a fraction of cloud cost. The exchange handles service discovery, quality verification, and settlement. If the usual evidence agent is busy, the exchange routes to an alternative provider. Cost: approximately EUR 0.38. Savings over Phase 1: 75%.

## **3.6 Travel and Hourly Reporting**

Prof. Koskela returns from a conference. She needs to file a travel expense claim (SAP Travel) and log conference hours against the correct project codes (SAP CATS).

**Phase 0.** She starts by collecting receipts (paper and digital), scanning or photographing each one, gathering conference programs and hotel and flight confirmations, and writing a justification for each expense item. She then opens SAP Travel and begins the multi-step form: trip details, per diem calculation (looking up the correct daily rate for the destination country, adjusting for trip duration and provided meals), expense classification (accommodation, transport, meals, registration, incidentals), receipt attachment, and project code assignment. For a conference funded by an EU project, she must split costs across the correct work packages and verify that travel is within the contract’s approved travel budget. She then opens SAP CATS and logs the conference days against the correct project code, checking the hours against approved allocations. A straightforward domestic trip takes 1 to 2 hours; an international conference claim with foreign-currency receipts, multiple expense types, and split project funding can consume half a working day. Across the department, hundreds of claims per year represent one of the largest administrative burdens.

**Phase 1.** The on-premises agent processes scanned receipts (OCR and classification), matches them against the itinerary, and generates submissions. However, it uses a general-purpose model without specialized knowledge of per diem rules, expense categories, or project code structures. Some cross-referencing still requires manual verification. Time: 10 to 15 minutes of review (down from hours, but not fully automated). Cost: EUR 0.15 internal compute (more processing needed due to lack of specialization).

**Phase 2.** A specialized SAP travel/reporting agent, available on the exchange, handles the cross-referencing logic with full knowledge of the university’s per diem rules, expense categories, and project codes. Fully automated, requiring only a quick confirmation. The exchange provides discovery, quality tracking, and fallback routing. Cost: approximately EUR 0.05. Savings over Phase 1: 67%.

## **3.7 Period-End Project Reporting**

Most funded projects require periodic reports. Reporting complexity varies significantly by funder: Horizon Europe (HE) and ERDF (European Regional Development Fund) reports are very time-consuming, requiring detailed financial documentation, activity evidence, and milestone verification; Business Finland (BF) reports fall in the middle; Research Council of Finland (RCF) and internal funding reports are comparatively lightweight. Prof. Koskela manages 4 active projects across different funders. For each report she must aggregate publications (Publication DB), contract status and milestones (Contract DB), budget utilization and FTE allocations (Tatu), effort allocation (SAP CATS), travel expenses (SAP Travel), and sometimes course outcomes (Moodle and Peppi), partner activity (CRM), and institutional context (Patio). University-

Page 8 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

level year-end budgeting is handled at the research unit lead and dean level; Prof. Koskela’s responsibility is to ensure her Tatu project entries are accurate and up to date.

**Phase 0.** For each project, she opens the relevant systems, exports or copies data, and compiles it into a Word document or spreadsheet. A single HE or ERDF project report requires pulling publication metrics from the Publication DB, reading through the active agreement in the Contract DB for milestone status, extracting budget utilization and month-by-month FTE actuals from Tatu, exporting effort data from SAP CATS, collecting travel totals from SAP Travel, and sometimes gathering course outcomes from Moodle/Peppi or partner activity from CRM. Synthesizing these into a coherent narrative with cross-cutting analysis takes several additional hours of writing. A single HE/ERDF project report consumes 1 to 2 full working days. An RCF or internal funding report takes 2 to 4 hours. Business Finland falls between these extremes. Across 4 active projects, the annual reporting burden averages roughly 5 hours per month when amortized.

**Phase 1.** The on-premises agent queries each system sequentially for each project (no multiagent orchestration without an exchange to coordinate). Per-system data retrieval works but is slower and less parallelized. For complex funders (HE/ERDF), the synthesis step sends a large data package to Azure at retail pricing (no competition, no load optimization). For lighter funders (RCF, internal), the on-premises agent handles the full report locally. Time: 1 to 2 hours of review and refinement across all projects. Cost: EUR 8 to 10 (EUR 1.50 on-premises sequential processing + EUR 6.50 to 8.50 cloud synthesis at retail pricing).

**Phase 2.** The exchange orchestrates multi-agent composition across all four integrator types simultaneously. Eight specialized agents query systems in parallel on-premises. Campus IT provides the backbone; research compute pools contribute overflow GPU capacity. Specialized agents pre-process each data stream efficiently, reducing the cloud synthesis payload by 80%. The cloud provider delivers frontier narrative synthesis on a compact, well-structured input. Funder-specific routing means the exchange allocates frontier compute only where the reporting complexity justifies it: HE/ERDF reports get full multi-agent composition with cloud synthesis, while RCF and internal reports route entirely on-premises. The full service economy in action.

## **Service-dependency DAG (Phase 2):**

Publication DB agent ──┐ Contract DB agent ─────┤ Tatu budget agent ─────┤ SAP CATS effort agent ─┼──►Orchestrator ──►Narrative synthesis SAP Travel agent ──────┤ (on-prem) (cloud frontier) Moodle/Peppi agent ────┤ CRM agent ─────────────┤ Patio agent ───────────┘

Cost: approximately EUR 2.15. Savings over Phase 1: 76%.

## **3.8 Development Discussions**

Each spring, line managers conduct individual development discussions with every team member. Research unit leads hold them for line managers, and the dean for research unit leads. The discussions themselves are substantive, but much of the time burden comes from filling in the mandatory SAP HR forms: self-assessments, competence evaluations, goal-setting templates, and follow-up documentation for each person.

Page 9 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

**Phase 0.** Prof. Koskela schedules and conducts development discussions with each of her 8 team members over a two-week period. For each discussion, she prepares by reviewing the previous year’s form entries in SAP, writing her own assessment notes, and pre-filling parts of the current year’s form. After each discussion, she finalizes the SAP form with agreed goals, competence ratings, and development actions. The SAP HR forms are multi-step, with rigid field structures and no pre-population from prior years. Preparing, conducting, and documenting 8 discussions takes roughly 16 to 20 hours total, of which at least half is SAP form navigation and data entry rather than the discussions themselves. Amortized over 12 months: approximately 1.5 hours per month.

**Phase 1.** The on-premises agent (ConfidentialMind) pre-populates each form from prior-year data, drafts assessment summaries based on project outputs and SAP CATS effort records, and generates goal suggestions aligned with the group’s research strategy. Prof. Koskela reviews and adjusts each draft before the discussion. After the meeting, she confirms or edits the agreed outcomes, and the agent finalizes the SAP submission. Preparation and documentation time drops from roughly 10 hours to roughly 2 hours across all 8 discussions. The discussions themselves remain the same duration. Total time: roughly 8 to 10 hours per year (discussions unchanged, SAP overhead reduced by 80%). Cost: EUR 0.60 per year internal compute (all data is HR-confidential, stays on-premises). Amortized: approximately EUR 0.05 per month.

**Phase 2.** A specialized SAP HR agent on the exchange handles form generation with full knowledge of the university’s competence framework, goal taxonomies, and prior-year patterns. The exchange routes entirely on-premises (HR data governance). If the central cluster is busy during the spring peak, research compute pools provide overflow capacity. Cost: approximately EUR 0.25 per year (EUR 0.02 per month amortized). Savings over Phase 1: 58%.

## **4. The Monthly Ledger**

Aggregating Prof. Koskela’s typical monthly usage across all three phases:

||||Phase 1|||
|---|---|---|---|---|---|
|||Phase 0|(agentic,|Phase 2||
|Category|Sessions/Mo|(manual)|fxed)|(exchange)|Phase 1￿2|
|Daily triage|22 days|~3 h/mo|EUR 0 (local)|EUR 0 (local)|—|
|Grant/proposal|3 sessions|~3 h/mo|~EUR 8.70|~EUR 4.79|-45%|
|work||||||
|Contract|2 sessions|~1.5 h/mo|~EUR 0.06|~EUR 0.03|-50%|
|reviews||||||
|Teaching|4 sessions|~4 h/mo|~EUR 4.96|~EUR 2.73|-45%|
|workfows||||||
|Publication|2 sessions|~1 h/mo|~EUR 2.10|~EUR 1.16|-45%|
|lifecycle||||||
|Travel/hourly|3 claims|~1.5 h/mo|~EUR 0.03|~EUR 0.02|-33%|
|reporting||||||



Page 10 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

||||Phase 1|||
|---|---|---|---|---|---|
|||Phase 0|(agentic,|Phase 2||
|Category|Sessions/Mo|(manual)|fxed)|(exchange)|Phase 1￿2|
|Period-end|0.33|~1.5 h/mo|~EUR 1.46|~EUR 0.80|-45%|
|project|sessions|||||
|reporting||||||
|Development|8 annual|~0.5 h/mo|~EUR 0.01|~EUR 0.01|—|
|discussions||||||
|**Total**||**~16 h/mo**|**~EUR 17**|**~EUR 10**|**-45%**|



**Phase 0 to Phase 1** delivers the transformative improvement in **time** . Approximately 16 hours per month of manual administrative work (navigating web interfaces, copying data between systems, compiling reports) drops to minutes of agent-assisted review. At even a modest internal hourly rate, the recovered productive time dwarfs any compute cost.

**Phase 1 to Phase 2** delivers the transformative improvement in **cost** . Fixed routing in Phase 1 defaults non-governance tasks to cloud at retail API pricing, with no competition between providers, no shared compute pools, and no specialized agents available as shared services. The exchange in Phase 2 introduces provider competition (driving prices toward marginal cost), research compute pools (providing cheap overflow capacity from idle departmental GPUs), specialized institutional agents (amortizing domain expertise across all users), and dynamic routing (sending tasks to the cheapest capable tier in real time). The result: approximately 45% cost reduction per user.

At institutional scale (200 active users), Phase 1 costs approximately EUR 3,400 per month; Phase 2 reduces this to approximately EUR 1,900. The annual saving of approximately EUR 18,000 is significant, but the deeper value is structural: the exchange prevents capacity bottlenecks, enforces governance uniformly without manual IT policy management, enables shared specialized agents that no single department would build alone, and provides the audit and trust infrastructure needed for institutional accountability.

## **5. The Ecosystem Behind the Scenes**

## **5.1 Integrator Taxonomy (Phase 2)**

Four integrator types supply the institutional marketplace.

**Campus IT / Data Centre.** Central IT manages the on-premises GPU cluster hosting ConfidentialMind, maintains connectors to institutional databases, and enforces data governance policies. Today, campus GPU infrastructure runs at 30 to 40% utilization under static allocation. The exchange pushes utilization to 70 to 80% by dynamically allocating idle capacity. Business model: internal cost recovery.

**Research compute pools.** Faculty groups pool idle departmental GPUs. A research group’s ML training cluster sits idle between training runs; during those hours, the GPUs enter the marketplace as inference capacity, earning the group internal compute credits. Business model: shared cost recovery.

Page 11 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

**Specialized institutional agents.** Purpose-built agents for specific workflows: contract review (including export-restriction checks), publication tracking, evidence generation, SAP travel/reporting automation, and SAP HR form automation (development discussions). These package domainspecific institutional knowledge into services with defined quality commitments. In Phase 1, these agents exist but are accessed directly. In Phase 2, the exchange provides discovery, quality tracking, and settlement. Business model: service subscription within the marketplace.

**Cloud platform providers.** Microsoft Azure with institutional SLA, offering frontier model access with guaranteed throughput, latency commitments, and GDPR-compliant region selection.

## **5.2 How the Exchange Works (Phase 2)**

1. The agent submits a task description, capability requirements, governance tags, and budget.

2. The routing module checks governance constraints: tasks tagged as institutional-confidential are routed only to on-premises integrators, narrowing the candidate set.

3. The exchange broadcasts current prices across matching slices.

4. The routing module evaluates price, latency, quality, and trust scores, then places a bid.

5. Prices adjust until supply meets demand. The agent receives an allocation at the clearing price.

6. The task executes. The integrator’s quality score is updated based on the outcome.

The ascending price broadcast ensures transparency: any manipulation by the exchange operator would produce a detectable inconsistency. This is a lightweight commitment device that makes the exchange credible without heavy overhead.

## **5.3 Trust and Quality**

Integrators are certified before listing on the exchange. Dynamic trust scores (visible to agents) reflect SLA compliance, uptime, and audit outcomes. Trust is slow to rebuild and fast to lose. In a university context, a single data governance violation has severe regulatory consequences (GDPR fines, institutional reputation damage), so the trust mechanism provides strong deterrence.

## **6. Why This Requires a Neutral Exchange**

If Microsoft ran the exchange, it would route tasks to Azure even when on-premises would be cheaper and more governance-appropriate. If Campus IT ran it, it would favour on-premises even when cloud frontier would deliver superior quality for non-sensitive tasks. A neutral exchange earns per-unit fees on volume. Its revenue is maximized by making the best routing decision regardless of provider. This neutrality is not a design preference but a structural constraint: any entity with an ownership stake in the allocated resources has a structural incentive to manipulate routing.

Page 12 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

## **7. From the University to the Addressable Market**

The university is one institution. The addressable market is every regulated organization with multiple information systems and governance requirements: higher education (Moodle/Canvas, SAP/Oracle), healthcare (patient records, clinical systems, billing), government (citizen records, case management), and regulated enterprise (banking, insurance, pharmaceuticals). The coordination problem is identical: agents need to query across systems under governance constraints. The university testbed provides a controlled, real-world environment to develop and validate the architecture.

## **8. Implementation Roadmap**

## **Phase 0 ￿ Phase 1: Agentic interfaces (current research program)**

The thesis projects build the agentic interface layer:

- **M0 (Mohammad Abaeiani):** Publication DB agent on ConfidentialMind. Retrieval, crossreferencing, and reporting.

- **M1 (Faisal Khan):** Contract DB agent on ConfidentialMind. Access-scoped retrieval, audit logging, policy-as-code. Vignettes 3.3 and 3.5.

- **M2 (Vu Truong):** Platform comparison harness (Copilot vs ConfidentialMind) on Moodle/Patio. Produces the evaluation methodology. Vignette 3.4.

- **M3:** Evidence-as-a-service agent on Patio. Machine-checkable compliance proofs. Vignette 3.5.

- **M4:** Governance toolkit on CRM. Autonomy tiers, escalation paths, accountability.

- **M5:** Multi-agent orchestration on ERP/SAP (Tatu, SAP Travel, SAP CATS, SAP HR). ServiceDAG representation of institutional workflows. Vignettes 3.2, 3.6, 3.7, 3.8.

Phase 1 delivers immediate value: the manual overhead drops from ~16 hours per month to minutes of review. Routing is fixed by IT policy, but agentic access to each system is functional.

## **Phase 1 ￿ Phase 2: Service economy (exchange implementation)**

Phase 2 builds the marketplace infrastructure in four internal stages (corresponding to the software architecture’s Phase 0 through Phase 3):

**Stage 2a — Integrator stack and posted prices.** Campus IT becomes the first integrator. Slice templates define on-premises compute and inference services. A basic exchange with posted prices (no auction) handles discovery and allocation. The contract review agent and publication agent are the first specialized institutional agents listed.

**Stage 2b — Exchange launch with ascending auction.** The matching engine goes live with ascending clinching on polymatroid feasibility regions. The cloud provider joins as the second integrator type. Settlement and audit-trail services provide accountability. The evaluation harness (from M2) benchmarks exchange-mediated versus fixed routing.

Page 13 of 14

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

**Stage 2c — Governance and supply growth.** Certification authority and cross-market auditor come online. Research compute pools join as the third integrator type. Cooperative tools enable departmental GPU pooling. The full four-integrator ecosystem emerges.

**Stage 2d — Full institutional service economy.** Adversarial resilience (coalition detection, adaptive penalties, dynamic credibility). All institutional systems participate as service nodes. Prof. Koskela’s entire week runs seamlessly on the platform.

The university information systems exist today. The agentic platforms exist today (ConfidentialMind, MS Copilot/Azure). The governance frameworks exist today (GDPR, institutional data policies). Phase 1 is under construction. Phase 2 is the target architecture. The progression is incremental: each stage is production-complete for the institutional scale it serves, and the credibility built at each stage compounds into the next.

Page 14 of 14
