**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

## **Financial Analysis: University of Oulu AI Service Economy**

University of Oulu, Faculty of ITEE, CSE Research Unit

|**Contents**||
|---|---|
|**1. Executive Summary**|**2**|
|**2. User Category Profles**|**3**|
|**3. Adoption Scenarios**|**4**|
|Conservative . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|4|
|Normal<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|5|
|Aggressive<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|5|
|Phase transition overlay (all scenarios) . . . . . . . . . . . . . . . . . . . . . . . . . . .|5|
|**4. Investment Requirements**|**6**|
|**5. Year-by-Year Financial Projections**|**7**|
|Value calculation methodology . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|7|
|Normal scenario . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|7|
|Conservative scenario . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|8|
|Aggressive scenario . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|8|
|**5b. Strategic Student Benefts (Not Quantifed in Core Projections)**|**9**|
|**6. Compute Cost Derivation**|**10**|
|Pricing tiers . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|10|
|Per-task token estimates (research-active staf, multi-call agentic usage)<br>. . . . . . .|10|
|Monthly per-user compute costs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|10|



Page 1 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

|**7. Comparison with Seat-Based Licensing**|**11**|
|---|---|
|Per-user cost comparison . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|11|
|Institutional cost comparison (Normal scenario, Y5)<br>. . . . . . . . . . . . . . . . . . .|11|
|**8. ROI Analysis**|**12**|
|Payback period . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|12|
|Phase 2 incremental ROI (Normal scenario) . . . . . . . . . . . . . . . . . . . . . . . .|12|
|5-year NPV (3% discount rate) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|12|
|Beneft-to-cost ratio (Y5)<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|13|
|**9. Sensitivity Analysis**|**13**|
|**10. Assumptions and Limitations**|**14**|
|**11. Conclusion**|**15**|



**Companion document to:** Use Case: The University of Oulu AI Service Economy **Classification:** Internal **Date:** March 2026

## **1. Executive Summary**

Deploying an AI service economy across the University of Oulu’s information systems can recover significant staff time currently spent on administrative navigation and data transfer, redirecting it toward research, teaching, and institutional support. Three adoption scenarios project 5-year outcomes:

|Metric|Conservative (Y5)|Normal (Y5)|Aggressive (Y5)|
|---|---|---|---|
|Active users|4,750|9,497|12,015|
|Active staf|1,550|2,297|2,415|
|Annual compute cost|EUR 276K|EUR 387K|EUR 407K|
|Annual net value recovered|EUR 2,661K|EUR 3,884K|EUR 4,062K|
|Annual investment|EUR 715K|EUR 715K|EUR 715K|
|BCR (Y5)|2.7:1|3.5:1|3.6:1|
|5-year cumulative net beneft|EUR 3.2M|EUR 7.8M|EUR 9.8M|
|5-year NPV (3%)|EUR 2.8M|EUR 6.9M|EUR 8.8M|



The financial case rests on the Phase 0 to Phase 1 transition (manual to agentic), where administrative overhead is reduced by an estimated 67% through a combination of navigational

Page 2 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

automation and AI-assisted judgment tasks. However, not all freed time converts to productive output at par: productivity conversion factors (0.50 to 0.70 depending on category) and an error/oversight deduction (15%) are applied to produce realistic net value estimates. The resulting values represent opportunity cost (time redirected to core functions), not cash savings.

Compute costs (EUR 4 to 20 per user per month, derived from first-principles token estimation) remain modest relative to recovered value. The Phase 1 to Phase 2 transition (agentic to exchange) reduces compute costs by approximately 45% through routing optimization and competitive pricing, and provides structural benefits (governance automation, shared specialized agents, capacity efficiency) that the financial model captures only partially.

Under the Normal scenario, the investment breaks even early in Year 2, with a Year 5 benefit-tocost ratio of 3.5:1 and a total five-year investment of approximately EUR 3.0M. The dominant parameters are the administrative time baseline, the internal hourly rate, and the time reduction factor. Compute and infrastructure costs have minimal impact on the outcome.

## **2.**

The University of Oulu population comprises four user categories with different system usage patterns, compute cost profiles, and productivity conversion characteristics.

||||||Phase 1|Phase 2||
|---|---|---|---|---|---|---|---|
|Category|Population|Phase|0|(h/mo)|(EUR/mo)|(EUR/mo)|Source|
|Research-|800|16|||20.00|11.00|Self-|
|active|||||||reported|
|staf|||||||(single|
||||||||user)|
|Administrative<br>1,200||20|||11.00|6.00|Estimate|
|staf||||||||
|Teaching-|500|12|||7.00|4.00|Estimate|
|focused||||||||
|staf||||||||
|Students|16,000|3|||1.50|0.85|Estimate|



**Internal hourly cost:** EUR 25/h (EUR 3,500/month average salary divided by 163 FTE monthly hours, multiplied by 1.26 employer cost factor, rounded).

**Time reduction factor:** 67% (blended). Approximately 60% of administrative hours consist of navigational and form-filling tasks (85% automatable); the remaining 40% are judgmentintensive tasks (40% automatable). The blended reduction is 0.60 x 0.85 + 0.40 x 0.40 = 0.67.

**Productivity conversion factors.** Not all freed time converts to productive output. Research staff, whose core function is research and teaching, convert freed administrative time well (0.70). Teaching staff convert to teaching preparation and some research (0.60). Administrative staff convert freed routine time to better support for research and teaching staff, amplifying institutional impact indirectly (0.50). Student time savings are excluded from financial projections entirely.

Page 3 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

**Error/oversight deduction:** 15% is deducted from gross value to account for human oversight of AI outputs on governance-critical tasks and error remediation costs.

**Research-active (800).** Professors, associate professors, postdocs, and doctoral researchers who manage funded projects, publish, teach, and interact with all institutional systems. The original 64 h/mo figure was self-reported by a single user and conflated substantive decision-making with automatable system-navigation overhead. The revised 16 h/mo baseline isolates the automatable administrative burden: navigating between systems, transferring data between forms, compiling reports from multiple sources, and similar overhead tasks. Research staff do mostly research and some teaching; administration is a side burden, not a core function. Phase 1 and Phase 2 compute costs are derived from per-task token estimates (see Section 6).

**Administrative (1,200).** HR, finance, procurement, student services, and IT support. Heavy SAP users (Tatu, SAP Travel, SAP CATS, SAP HR) and Office 365 users, but without research-specific tasks (no grant proposals as PI, no publication lifecycle management). Administrative overhead is estimated at 20 h/mo, reflecting the fact that system interaction is closer to their core job function. Freed time enables better support for research and teaching staff, amplifying institutional impact. Phase 1 cost is proportionally lower (EUR 11/mo) because fewer tasks require cloud frontier models.

Lecturers and university teachers. Heavy Moodle/Peppi/Patio users with some SAP interaction but minimal research-system usage. Overhead estimated at 12 h/mo, dominated by course management and assessment workflows. Freed time redirects primarily to teaching preparation and some research activity. Phase 1 cost: EUR 7/mo.

**Students (16,000).** Students interact primarily with Moodle, email/calendar, and course-specific tools. Administrative overhead is modest (3 h/mo). In Phase 1, most student tasks are handled by a local agent (near-zero cost); cloud compute is used only for project work. Student time value is excluded from the core financial projections (they are not salaried employees). However, student access to the platform creates strategic value that is discussed separately in Section 5b.

## **3. Adoption Scenarios**

All scenarios assume Phase 1 (agentic interface) deploys beginning in Year 1. Phase 2 (service economy) begins pilot deployment in Year 4, with meaningful adoption only in Year 5.

## **Conservative**

Cautious rollout. The platform deploys first within the research group that developed it, extending gradually to other research-active staff. Administrative and teaching staff adopt slowly. Students have access but limited uptake. Assumes institutional caution, long approval cycles, and limited IT support for onboarding.

|Category|Y1|Y2|Y3|Y4|Y5|
|---|---|---|---|---|---|
|Research (800)|10%|30%|50%|65%|80%|
|Administrative (1,200)|2%|10%|25%|40%|55%|



Page 4 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

|Category|Y1|Y2|Y3|Y4|Y5|
|---|---|---|---|---|---|
|Teaching (500)|2%|8%|20%|35%|50%|
|Students (16,000)|0%|1%|5%|10%|20%|



## **Normal**

Broader institutional initiative. The University of Oulu adopts the platform as a strategic IT project after the pilot phase. Dedicated onboarding support for each staff category. Student adoption follows naturally through course integration and project work.

|Category|Y1|Y2|Y3|Y4|Y5|
|---|---|---|---|---|---|
|Research (800)|20%|60%|85%|95%|99%|
|Administrative (1,200)|5%|25%|55%|80%|90%|
|Teaching (500)|5%|20%|45%|70%|85%|
|Students (16,000)|0%|5%|15%|30%|45%|



## **Aggressive**

Full institutional commitment. The platform is positioned as a core university service from Year 1. Student adoption is actively promoted through course integration, startup incubation programs, and innovation challenges. Assumes strong leadership support, dedicated IT resources, and organizational change management.

|Category|Y1|Y2|Y3|Y4|Y5|
|---|---|---|---|---|---|
|Research (800)|40%|80%|95%|99%|100%|
|Administrative (1,200)|10%|40%|70%|90%|95%|
|Teaching (500)|10%|35%|65%|85%|95%|
|Students (16,000)|1%|10%|25%|45%|60%|



## **Phase transition overlay (all scenarios)**

|Year|Phase|1|share|Phase|2|share|
|---|---|---|---|---|---|---|
|Y1|100%|||0%|||
|Y2|100%|||0%|||
|Y3|100%|||0%|||
|Y4|80%|||20%|||
|Y5|50%|||50%|||



Phase 2 pilot begins in Year 4; meaningful exchange adoption occurs only in Year 5. This is more conservative than many enterprise platform rollout assumptions and reflects the complexity of building a functioning multi-provider exchange with governance automation.

Page 5 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

## **4. Investment Requirements**

|Investment|Y1|Y2|Y3|Y4|Y5|Total|
|---|---|---|---|---|---|---|
|Thesis projects|100K|50K|—|—|—|150K|
|(M0-M5)|||||||
|Connector|—|125K|125K|125K|125K|500K|
|productionisation|||||||
|ConfdentialMind|600K|50K|75K|75K|100K|900K|
|capacity|||||||
|Phase 1 platform ops|42K|54K|54K|27K|—|177K|
|Exchange|—|—|100K|160K|140K|400K|
|development|||||||
|Exchange operations|—|—|—|250K|350K|600K|
|Organizational|100K|100K|100K|—|—|300K|
|change|||||||
|**Total**|**842K**|**379K**|**454K**|**637K**|**715K**|**3,027K**|



**Thesis projects (EUR 150K).** Six master’s thesis students at EUR 2,500/month base salary (× 1.26 overhead = EUR 3,150/month) for eight months each: 6 × 8 × EUR 3,150 = EUR 151K, rounded to EUR 150K. The thesis projects (M0-M5) build the agentic connectors for each institutional system. These projects are already part of the research program.

**Connector productionisation (EUR 500K).** After thesis completion, two software engineers maintain and harden the connectors for institutional use over four years, transitioning from research prototypes to production-grade software. At approximately EUR 63K/year per engineer (salary plus 1.26 overhead factor).

On-premises GPU infrastructure for privacy-sensitive workloads. The Year 1 cost (EUR 600K) reflects initial hardware acquisition: a single 8xB300 GPU node costs approximately EUR 550K, with remaining budget for networking, cooling, and installation. Years 2 through 5 cover incremental expansion and maintenance. Engineer salary costs (EUR 4,000 to 4,500/month base, multiplied by 1.26 overhead) are included in operational years.

**Phase 1 platform ops (EUR 177K).** Operational costs for the agentic interface layer during Years 1 through 4. Extended beyond the original two-year estimate to reflect realistic operational continuity requirements as Phase 2 ramps up.

**Exchange development (EUR 400K).** Research and engineering effort to build the exchange software. In a university context, a combination of PhD/postdoc research time and dedicated engineering. Development begins in Year 3, aligned with the delayed Phase 2 timeline.

**Exchange operations (EUR 600K, Y4-Y5).** The exchange coordination platform (compute, storage, messaging, monitoring). The exchange does not own GPUs; this covers the coordination infrastructure only. Operations begin with Phase 2 pilot in Year 4.

**Organizational change (EUR 300K).** Training, change management, help-desk support, onboarding programs, and transition support. Concentrated in Years 1 through 3 when most staff are first encountering the platform. This cost was absent from the original analysis and represents a significant real-world requirement for institutional AI adoption.

Page 6 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

**Note on GPU ownership.** Neither the agentic interface layer nor the exchange owns production GPUs beyond the ConfidentialMind cluster. Additional compute is provided by Campus IT (existing cluster) and research compute pools (existing departmental hardware). GPU utilization improves from 30-40% to 70-80% through dynamic allocation, representing a significant implicit saving not captured in this analysis.

## **5. Year-by-Year Financial Projections**

## **Value calculation methodology**

Annual net value per user is calculated as:

net_value = hours/mo x 0.67 (reduction) x EUR 25/h x conversion_factor x 12 months x 0.85 (oversight deduction)

Per-user annual net values: - **Research-active:** 16 x 0.67 x 25 x 0.70 x 12 x 0.85 = EUR 1,913/yr - **Administrative:** 20 x 0.67 x 25 x 0.50 x 12 x 0.85 = EUR 1,709/yr - **Teachingfocused:** 12 x 0.67 x 25 x 0.60 x 12 x 0.85 = EUR 1,230/yr - **Students:** excluded (not salaried employees)

For reference, the gross time freed (before conversion and oversight deductions) is approximately 2.8x larger than the net value figures. Gross figures represent an upper bound on the theoretical time savings; net figures represent the realistic institutional value recovered.

## **Normal scenario**

|Metric|Y1|Y2|Y3|Y4|Y5|
|---|---|---|---|---|---|
|Active staf|245|880|1,565|2,070|2,297|
|Active users|245|1,680|3,965|6,870|9,497|
|(incl. students)||||||
|Annual net value|440|1,555|2,706|3,525|3,884|
|recovered (EUR||||||
|K)||||||
|Annual compute|48|178|312|387|387|
|cost (EUR K)||||||
|Annual|842|379|454|637|715|
|investment (EUR||||||
|K)||||||
|**Annual net**|**-450**|**998**|**1,940**|**2,501**|**2,782**|
|**beneft (EUR K)**||||||
|**Cumulative net**|**-450**|**548**|**2,488**|**4,989**|**7,771**|
|**beneft (EUR K)**||||||



**Y1 detail:** 160 research + 60 admin + 25 teaching = 245 staff. Value: 160 x 1,913 + 60 x 1,709 + 25 x 1,230 = 306K + 103K + 31K = 440K. Compute: (160 x 20 + 60 x 11 + 25 x 7) x 12 = 48K.

Page 7 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

**Y2 detail:** 480 research + 300 admin + 100 teaching = 880 staff, plus 800 students = 1,680 users. Value: 480 x 1,913 + 300 x 1,709 + 100 x 1,230 = 919K + 513K + 123K = 1,555K. Compute: (480 x 20 + 300 x 11 + 100 x 7 + 800 x 1.50) x 12 = 178K.

**Y3 detail:** 680 research + 660 admin + 225 teaching = 1,565 staff, plus 2,400 students = 3,965 users. Value: 680 x 1,913 + 660 x 1,709 + 225 x 1,230 = 1,301K + 1,128K + 277K = 2,706K. Compute: (680 x 20 + 660 x 11 + 225 x 7 + 2,400 x 1.50) x 12 = 312K.

**Y4 detail:** 760 research + 960 admin + 350 teaching = 2,070 staff, plus 4,800 students = 6,870 users. Phase split 80/20. Value: 760 x 1,913 + 960 x 1,709 + 350 x 1,230 = 1,454K + 1,641K + 431K = 3,525K. Compute with phase blending: research 760 x (0.80 x 20 + 0.20 x 11) x 12 = 166K, admin 960 x (0.80 x 11 + 0.20 x 6) x 12 = 115K, teaching 350 x (0.80 x 7 + 0.20 x 4) x 12 = 27K, students 4,800 x (0.80 x 1.50 + 0.20 x 0.85) x 12 = 79K. Total compute = 387K.

**Y5 detail:** 792 research + 1,080 admin + 425 teaching = 2,297 staff, plus 7,200 students = 9,497 users. Phase split 50/50. Value: 792 x 1,913 + 1,080 x 1,709 + 425 x 1,230 = 1,515K + 1,846K + 523K = 3,884K. Compute: research 792 x (0.50 x 20 + 0.50 x 11) x 12 = 147K, admin 1,080 x (0.50 x 11 + 0.50 x 6) x 12 = 110K, teaching 425 x (0.50 x 7 + 0.50 x 4) x 12 = 28K, students 7,200 x (0.50 x 1.50 + 0.50 x 0.85) x 12 = 102K. Total compute = 387K.

## **Conservative scenario**

|Metric|Y1|Y2|Y3|Y4|Y5|
|---|---|---|---|---|---|
|Annual net value|206|713|1,401|2,031|2,661|
|recovered (EUR||||||
|K)||||||
|Annual compute|23|80|158|221|276|
|cost (EUR K)||||||
|Annual|842|379|454|637|715|
|investment (EUR||||||
|K)||||||
|**Annual net**|**-659**|**254**|**789**|**1,173**|**1,670**|
|**beneft (EUR K)**||||||
|**Cumulative net**|**-659**|**-405**|**384**|**1,557**|**3,227**|
|**beneft (EUR K)**||||||



## **Aggressive scenario**

|Metric|Y1|Y2|Y3|Y4|Y5|
|---|---|---|---|---|---|
|Annual net value|878|2,260|3,289|3,884|4,062|
|recovered (EUR||||||
|K)||||||
|Annual compute|100|260|393|431|407|
|cost (EUR K)||||||
|Annual|842|379|454|637|715|
|investment (EUR||||||
|K)||||||



Page 8 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

|Metric|Y1|Y2|Y3|Y4|Y5|
|---|---|---|---|---|---|
|**Annual net**|**-64**|**1,621**|**2,442**|**2,816**|**2,940**|
|**beneft (EUR K)**||||||
|**Cumulative net**|**-64**|**1,557**|**3,999**|**6,815**|**9,755**|
|**beneft (EUR K)**||||||



Note: In all scenarios, compute cost stabilises or decreases from Y4 onward as users transition from Phase 1 to Phase 2 pricing, even as the total number of users grows. The aggressive scenario’s higher user count is driven by student adoption, which adds compute cost but does not add to staff time value in the core projections. Strategic student benefits are discussed in Section 5b.

## **5b.**

Student time savings are excluded from the core financial projections because students are not salaried employees. However, providing students with access to the agentic platform creates three categories of strategic value that strengthen the institutional case beyond the staff-focused numbers above.

Students who learn to build, deploy, and orchestrate AI agents on real institutional systems gain directly transferable entrepreneurial skills. The platform provides a low-risk environment for prototyping AI-powered services (e.g., automated compliance checking, cross-system reporting tools, domain-specific assistants) that could form the basis for university spinoffs. At institutions with comparable innovation programs, student startup rates from AI-adjacent coursework are in the range of 2 to 5% of participants. For the University of Oulu, even a 1% rate among active student users (Normal Y5: 7,200 students) would yield approximately 70 startup attempts over the projection period. If 10 to 20% of these reach viable product stage, that represents 7 to 14 new ventures with potential for regional economic impact, licensing revenue, or strategic partnerships.

**Workforce readiness and recruitment.** Graduates with hands-on experience in agentic systems, governance-aware AI deployment, and service economy architectures are highly employable in a market where these skills are scarce. This positions the University of Oulu as a preferred recruitment pipeline for companies adopting enterprise AI, strengthening the university’s employer partnerships and industry collaboration.

**Educational quality.** Agentic tools reduce the administrative friction of coursework (enrollment, submission, assessment workflows), freeing student time for deeper engagement with course content. More importantly, courses can integrate the platform as a teaching tool: students learn AI governance, prompt engineering, and system integration by using (and building on) the same platform that runs the university’s own operations.

These benefits are not included in the BCR or NPV calculations. They represent upside that, while difficult to quantify precisely, could be significant for the university’s strategic positioning in AI education and regional innovation.

Page 9 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

## **6. Compute Cost Derivation**

Per-user compute costs are derived from first principles, estimating token consumption per task category and applying published API pricing.

## **Pricing tiers**

**Cloud frontier (Sonnet-tier).** Claude Sonnet 4 or equivalent: approximately USD 3/1M input tokens, USD 15/1M output tokens (approximately EUR 2.76/1M input, EUR 13.80/1M output at current exchange rates).

**On-premises** Marginal cost only, with hardware investment captured in the investment table: approximately EUR 0.05/1M tokens (covering electricity, cooling, and maintenance).

##

|Task|Input tokens|Output tokens|Routing|Cost per session|
|---|---|---|---|---|
|Grant proposal (1 session)|800K|50K|Cloud|EUR 2.90|
|Contract review|500K|30K|On-prem only|EUR 0.03|
|Teaching (mixed)|400K|25K|Cloud|EUR 1.24|
|Publication (mixed)|350K|20K|Cloud|EUR 1.05|
|Travel/reporting|100K|15K|On-prem|EUR 0.01|
|Period-end reporting (heavy)|1,200K|80K|Cloud|EUR 4.42|
|Dev discussions|150K|20K|On-prem|EUR 0.01|



Token estimates reflect multi-call agentic usage patterns, where a single task session involves multiple LLM calls for planning, retrieval, generation, and verification. On-premises routing is used for tasks involving sensitive personnel, financial, or contractual data.

## **Monthly per-user compute costs**

|Category|Phase|1|EUR/mo|Phase|2|EUR/mo|Derivation|
|---|---|---|---|---|---|---|---|
|Research-active|20|||11|||Derived from task|
||||||||profle above|
|Administrative|11|||6|||Proportional (fewer|
||||||||cloud tasks, more|
||||||||SAP/form|
||||||||automation)|
|Teaching-|7|||4|||Proportional|
|focused|||||||(primarily course|
||||||||management)|
|Students|1.50|||0.85|||Mostly local, some|
||||||||cloud for project|
||||||||work|



Page 10 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

**Phase 2 cost reduction.** Phase 2 reduces cloud compute costs by approximately 45%, comprising 35% from intelligent routing optimization (directing queries to the most cost-effective provider meeting quality requirements) and 10% from competitive pricing pressure among exchange providers. This is substantially less than a hypothetical maximum because not all tasks are cloud-routed and routing optimization has diminishing returns.

## **7. Comparison with Seat-Based Licensing**

As a reference, major cloud AI providers offer per-seat licensing models. Microsoft Copilot and comparable platforms currently price at approximately EUR 20/month per seat for standard use, with heavier tiers at EUR 100 to 200/month. These provide model access, interface, and basic integrations.

## **Per-user cost comparison**

|Category|Seat|license (typical)|Phase 1 (API)|Phase 2 (API)|Phase 2 vs. seat|
|---|---|---|---|---|---|
|Research-|EUR|100-200/mo|EUR 20/mo|EUR 11/mo|9-18x cheaper|
|active||||||
|AdministrativeEUR||20-100/mo|EUR 11/mo|EUR 6/mo|3-17x cheaper|
|Teaching-|EUR|20/mo|EUR 7/mo|EUR 4/mo|5x cheaper|
|focused||||||
|Students|EUR|20/mo|EUR 1.50/mo|EUR 0.85/mo|24x cheaper|



## **Institutional cost comparison (Normal scenario, Y5)**

|Model|Monthly cost|Annual cost|
|---|---|---|
|**Seat licensing**(all|EUR 190K|EUR 2,279K|
|active users at EUR|||
|20/mo minimum)|||
|**Seat licensing**|EUR 253K|EUR 3,040K|
|(tiered: research|||
|EUR 100, others|||
|EUR 20)|||
|**Phase 1**|EUR 47K|EUR 561K|
|**API-based**(100%|||
|Phase 1 pricing)|||
|**Phase 2**|EUR 28K|EUR 340K|
|**API-based**(100%|||
|Phase 2 pricing)|||



Notes: (1) Seat licensing applies to the 9,497 active users in the Normal Y5 scenario. (2) The API-based model costs are compute only; infrastructure investment (EUR 715K/year in Y5)

Page 11 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

must be added. Even so, Phase 2 total (EUR 340K compute + EUR 715K infrastructure = EUR 1,055K) is less than half of the minimum seat-licensing cost (EUR 2,279K). (3) The API-based model provides institutional governance (on-premises routing for sensitive data), dynamic cost optimization, and shared specialized agents that seat licensing does not offer. (4) For the 7,200 active students in Normal Y5, seat licensing at EUR 20/mo would cost EUR 1.73M/year; the API model serves the same students for approximately EUR 85K/year in Phase 2.

## **8. ROI Analysis**

## **Payback period**

Under the Normal scenario, the cumulative net benefit turns positive early in Year 2. Year 1 is an investment year (EUR -450K net), driven primarily by the EUR 842K infrastructure and organizational change investment. By the end of Year 2, the cumulative position is EUR +548K.

|Scenario|Cumulative break-even|
|---|---|
|Conservative|Mid-Year 3|
|Normal|Early Year 2|
|Aggressive|Early Year 2|



The break-even is realistic rather than instantaneous because (a) baseline hours are conservative, (b) productivity conversion factors reduce the effective value of freed time, (c) the oversight deduction accounts for AI error remediation, and (d) Year 1 investment is front-loaded with hardware acquisition (EUR 600K ConfidentialMind) and organizational change costs (EUR 100K).

## **Phase 2 incremental ROI (Normal scenario)**

|Metric|Y4-Y5 total|
|---|---|
|Phase 2 incremental investment (exchange dev + ops)|EUR 900K|
|Phase 2 compute savings vs. staying on Phase 1|~EUR 160K|
|Compute savings as share of investment|~18%|



Phase 2 does not pay for itself through compute savings alone. Its justification is structural: governance automation at scale, shared specialized agents that no department would build alone, GPU utilization improvement (30-40% to 70-80%), and audit/trust infrastructure for institutional accountability. The approximately 45% compute cost reduction from routing optimization and competitive pricing, while meaningful, is secondary to the governance and capability benefits.

## **5-year NPV (3% discount rate)**

Page 12 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

|Scenario|5-year NPV|
|---|---|
|Conservative|EUR 2.8M|
|Normal|EUR 6.9M|
|Aggressive|EUR 8.8M|



Normal scenario NPV breakdown: Y1 -437K + Y2 941K + Y3 1,775K + Y4 2,222K + Y5 2,400K = EUR 6,901K.

##

|Scenario|Y5 BCR|
|---|---|
|Conservative|2.7:1|
|Normal|3.5:1|
|Aggressive|3.6:1|



The Normal Y5 BCR of 3.5:1 (annual net value of EUR 3,884K divided by annual compute + investment of EUR 1,102K) represents a strong business case. While lower than the original analysis, it is more credible because it accounts for realistic productivity conversion, error overhead, and conservative baseline estimates.

## **9. Sensitivity Analysis**

Normal scenario, Year 5 annual net benefit as baseline (EUR 2,782K, unchanged by the thesis cost revision which affects only Y1-Y2):

|Parameter|Low value|High value|Low net (EUR K)|High net (EUR K)|
|---|---|---|---|---|
|Admin|10 h/mo|25 h/mo|1,740|4,320|
|baseline|||||
|hours|||||
|(research)|||||
|Internal|EUR 15/h|EUR 35/h|1,100|4,460|
|hourly rate|||||
|Time|50%|85%|1,830|3,465|
|reduction|||||
|factor|||||
|Productivity|-20%|+20% relative|2,000|3,560|
|conversion|relative||||
|Compute|+50%|-50%|2,589|2,976|
|cost|||||
|Infrastructure|+30%|-30%|2,567|2,997|
|cost|||||



Page 13 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

The analysis is most sensitive to the internal hourly rate and the administrative time baseline, and least sensitive to compute and infrastructure cost parameters. A 50% increase in per-user compute costs changes the annual net benefit by EUR 193K (7%), while a 67% change in the hourly rate shifts the result by EUR 1,680K (60%).

**Break-even analysis.** For the Normal Y5 investment to produce zero net benefit, the internal hourly rate would need to fall below approximately EUR 7/h, or the time reduction factor would need to fall below approximately 17%, or the productivity conversion factors would all need to fall below approximately 0.13. None of these is plausible in a university context.

## **10. Assumptions and Limitations**

1. **Time value is opportunity cost, not cash.** The EUR 25/h rate represents the university’s internal cost of staff time. Freeing administrative hours does not reduce payroll; it redirects time from administrative tasks to research, teaching, and institutional support. The financial projections should be interpreted as recovered institutional capacity, not as budget savings.

2. **Phase 0 time estimates are conservative and self-reported.** The 16 h/mo baseline for research-active staff is revised downward from an original 64 h/mo figure that was selfreported by a single user and conflated substantive decision-making with automatable system-navigation overhead. The revised figure isolates the automatable administrative burden. Actual time varies by individual, role, and discipline. The sensitivity analysis (Section 9) shows the impact of alternative baseline assumptions.

3. The 67% reduction blends two task types: navigational/form-filling tasks (approximately 60% of hours, 85% automatable) and judgment-intensive tasks (approximately 40% of hours, 40% automatable). Individual task categories may achieve higher or lower reductions.

4. **Productivity conversion factors are judgmental.** The conversion factors (0.50 to 0.70) represent estimates of how effectively freed administrative time translates into productive research, teaching, or institutional support output. These factors account for contextswitching costs, Parkinson’s law effects, and the reality that not all freed time is immediately productively deployed. The factors are novel to this analysis and should be validated empirically as the platform is deployed.

5. The 15% deduction for human oversight and error remediation on governance-critical tasks is applied uniformly across all categories. In practice, oversight requirements will vary by task type (higher for financial and contractual tasks, lower for scheduling and navigation). This deduction may underestimate overhead in early deployment (when trust is being established) and overestimate it in later years.

6. **Per-user costs for non-research categories are estimates.** Administrative staff, teaching staff, and student profiles are derived by proportional scaling from the research-active task profile. The analysis should be updated with measured data as Phase 1 deployment proceeds.

7. **Student time value is excluded from core projections.** Students are not salaried employees. Their benefit from the platform is strategic and educational, not financial in the salary-recovery sense. Student compute costs are included; student time savings are not. Section 5b discusses strategic student benefits (startups, workforce readiness, educational quality) that are not captured in the BCR or NPV.

Page 14 of 15

**==> picture [83 x 20] intentionally omitted <==**

**==> picture [131 x 20] intentionally omitted <==**

8. **Adoption percentages are projections.** Actual adoption depends on user experience quality, institutional change management, IT support capacity, and organizational culture. The three scenarios bracket a wide range of outcomes.

9. **Phase 2 cost reduction assumes a functional exchange.** The approximately 45% cost reduction from Phase 1 to Phase 2 depends on a functioning exchange with routing optimization and multiple competing providers. If the exchange is delayed or underperforms, users remain on Phase 1 costs. The reduction comprises 35% from routing optimization and 10% from competitive pricing pressure.

10. **Phase 2 timeline is delayed relative to typical projections.** Phase 2 pilot begins in Year 4, with meaningful adoption only in Year 5. This reflects the complexity of building governance automation, trust infrastructure, and a multi-provider marketplace in a university context.

11. **Infrastructure costs may shift.** GPU compute costs and cloud API pricing are declining. The per-token cost estimates use March 2026 pricing. Over the 5-year horizon, costs are likely to decrease, improving the financial case. Conversely, model capabilities (and thus token consumption per task) may increase.

12. **Organizational change costs are included but approximate.** The EUR 300K organizational change line item covers training, help-desk support, and transition management. Actual costs depend on institutional readiness and the degree of process redesign required.

13. **Compute cost derivation uses current model pricing.** The per-task token estimates assume Claude Sonnet 4-tier models. Future model generations may require different token volumes per task, and pricing structures may change (e.g., reasoning tokens, caching discounts, batch pricing).

14. **Exchange development cost is a rough estimate.** The EUR 400K assumes a universitybased research team. A commercial-grade exchange would cost significantly more.

15. **Seat-licensing comparison uses current (2026) pricing.** AI licensing models and prices are evolving rapidly. The comparison is indicative, not predictive.

## **11. Conclusion**

The financial case for deploying an AI service economy at the University of Oulu is positive under all three scenarios, with a Normal-scenario 5-year NPV of EUR 6.9M and a Year 5 benefitto-cost ratio of 3.5:1. These figures are substantially lower than the original analysis (which projected EUR 107M NPV and 46:1 BCR) because the revised model applies conservative baseline hours, realistic productivity conversion factors, an error/oversight deduction, a delayed Phase 2 timeline, and realistic investment costs (EUR 3.0M total over five years).

The revised figures are more credible and defensible. A 3.5:1 BCR still represents a strong institutional investment. The dominant value driver remains the Phase 0 to Phase 1 transition: replacing manual system navigation with agentic automation. Phase 2 adds structural benefits (governance, shared agents, capacity optimization) that are difficult to quantify fully but are strategically important for institutional AI maturity.

The analysis is most sensitive to the administrative time baseline and the internal hourly rate, and least sensitive to compute and infrastructure costs. Even under the Conservative scenario, the 5-year NPV is EUR 2.8M, confirming that the investment case is robust across a wide range of assumptions.

Page 15 of 15
