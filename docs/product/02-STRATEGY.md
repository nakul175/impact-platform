# Imprana Commons strategy

Owner: Nakul Jain · Prepared 10 October 2026 · Status: proposed product planning baseline; product scope approval pending.

## Strategic choice

Build on the existing MEL and reporting core to support the complete adoption journey in [the vision](01-VISION.md). The proposed starting approach is a supported, bounded pilot: prove that an organisation can define a problem, select a suitable intervention, deliver it safely and compare the outcome with a recorded baseline. Broader self-service, cohort operations and partner services follow the evidence from that pilot.

This is a proposal, not an approved cohort, market segment, delivery date or funded commitment. Existing implementation evidence remains in [IMPLEMENTATION](../IMPLEMENTATION.md) and [Sprint 1 review](../sprints/SPRINT-01-REVIEW.md); the following objectives describe intended outcomes.

## Objectives and priorities

| ID | Proposed objective | First proof to seek | Backlog anchors |
| --- | --- | --- | --- |
| STR-01 | Establish a trusted operating foundation | Trace a change from story and threat review to independent review, acceptance evidence and release decision; qualify tenant isolation and recovery | FR-SEC-008, FR-SEC-010, FR-TEN-001, FR-ACC-001, FR-PRV-001, VF-DR-001 |
| STR-02 | Help an organisation choose the right problem and intervention | Preserve problem evidence and baseline, explain the opportunity ranking, compare disclosed options and record a trial | US-DX-01a, US-DX-02, US-DX-03, US-MP-01, US-MP-02, US-MP-03, US-DC-01, US-DC-04, US-AS-01 |
| STR-03 | Turn a chosen intervention into adoption with measured value | Link an approved value case to deployment, training, observed use and equivalent outcome measures | US-VC-01, US-VC-05, US-DP-02, US-DP-03, US-AD-01, US-AD-02, US-IM-01, US-IM-03 |
| STR-04 | Make official MEL results and reporting dependable | Trace an official result through approved data, rules and locked snapshots to the authorised report and recipient | FR-IND-001, FR-CAL-001, FR-DAT-001, FR-FRM-001, FR-WFL-001, FR-RPT-003, FR-RPT-007 |
| STR-05 | Grow an accountable service and ecosystem | Prove grantee-controlled cohort reporting, clear entitlements and partner accountability before expanding commercial services | US-FP-01, US-FP-02, US-FP-04, US-CM-02, US-CM-03, US-PT-01, US-PT-03, US-PT-06 |

An anchor is an example, not an exhaustive scope list or a new release assignment. The source backlog retains each story's release, priority and criteria. Security, privacy, accessibility, operations and the non-functional requirements constrain every objective.

## Epic alignment for traceability

The proposed primary alignment below covers all 54 source epic/areas. A whole epic may serve several objectives; refinement should record the specific story's objective rather than inherit a misleading commercial or AI label. For example, FR-AI-016a and US-CM-05 serve STR-01 and STR-03 because they keep adoption within usage limits. This alignment does not change releases or permissions.

| Primary objective | Source epic/areas |
| --- | --- |
| STR-01 | Access control; Identity and accounts; Migration and exit; NFR audit; NFR availability; NFR capacity; NFR compatibility; NFR cost; NFR data integrity; NFR localisation; NFR maintainability; NFR observability; NFR performance; NFR portability; NFR recovery; NFR support; Non-functional; Operators; Platform; Privacy; Security; Service operations; Tenancy and organisation; Transition; User experience; Workflow and review |
| STR-02 | Adoption: Diagnose; Adoption: Map; Adoption: Discover; Adoption: Assess |
| STR-03 | Adoption: Value case; Adoption: Deploy; Adoption: Adopt; Adoption: Improve |
| STR-04 | Calculations; Dashboards and analysis; Data import and management; Data quality; Evaluation; Evidence; Finance; Forms and collection; Indicators; Integrations and connectors; Offline collection; Participants; Programmes; Reporting; Results planning |
| STR-05 | Commercial and billing; Funder portfolio; Partners |
| STR-01, with STR-02/03/04 as secondary objectives | AI capabilities; NFR AI quality |

## Proposed first learning slice

Use a representative synthetic case to exercise structured problem capture (US-DX-01a), readiness and baseline (US-DX-02/03), opportunity mapping and ranking (US-MP-01/02/03), disclosed discovery (US-DC-01/02/03/04), a trial (US-AS-01/03), value case (US-VC-01/05), deployment (US-DP-02/03), staff adoption (US-AD-01/02) and measured follow-up (US-IM-01/03). Exercise the inherited collection, review, calculation and reporting path alongside it.

This is a proposed walkthrough for refinement, not a committed sprint or a reduction of the 172 active R1 Pilot stories. Dependencies must be verified against current evidence. For example, conversational intake US-DX-01b follows structured capture and AI policy/job controls; FR-AI-016a precedes usage and alerts US-CM-05. Sprint 1 code merged in [PR #94](https://github.com/nakul175/impact-platform/pull/94); product-owner acceptance remains unrecorded. The committed [Sprint 1 review](../sprints/SPRINT-01-REVIEW.md) contains older pre-merge wording; future changes retain the current [AGENTS](../../AGENTS.md) review, CI and owner gates. No AI destination is approved, so generated drafts cannot be assumed available for the pilot.

## Trade-offs

| Proposed choice | Why | Cost or condition |
| --- | --- | --- |
| Reuse one platform for MEL and AI enablement | Carries permissions, programme context and evidence through the journey | Shared controls and acceptance dependencies cannot be bypassed to ship an AI feature |
| Start with supported trials and advisor-reviewed fit | Helps learn where users need help and where tools work | Named advisors, their authority, conflicts and operating capacity must be decided |
| Prefer deterministic assessment and process alternatives when adequate | Makes reasons repeatable and avoids unnecessary provider use | Generated assistance is added only where its quality and permitted data boundary are demonstrated |
| Keep the first planning and trial work synthetic | Allows workflow learning while privacy and production gates remain open | Real organisation or participant data requires separately approved use and qualified controls |
| Refine stories near implementation | Keeps acceptance and technical tasks grounded in current evidence | A broad release bucket does not justify promising every story in the next sprint |
| Publish commercial disclosures with recommendations | Lets organisations judge conflicts | Revenue incentives cannot silently change ranking or claim verified supplier status |

## Non-goals for the proposed first pilot

The first pilot does not introduce autonomous purchases, autonomous approvals, official arithmetic produced by AI, beneficiary personal data, guaranteed savings or causal impact claims. Payments, a full accounting/payroll product, a partner marketplace with verified suppliers, broad offline/mobile support and unrestricted cross-organisation analysis are outside this proposed first slice. Their existing backlog stories retain their current buckets and can be reconsidered through an explicit owner decision.

## Draft business model to validate

The proposed model combines organisation access with optional supported adoption services. Direct organisation subscriptions and funder-sponsored cohort access are alternatives to test; entitlement combinations, local-currency invoicing, fixed-fee packages and partner revenue-share accounting remain R2 stories. Partner outcome access and wider ecosystem services remain later dependencies.

For the pilot, record who receives value, who would pay, support effort, total delivery cost, retention needs and willingness to continue. Use those observations to choose commercial terms. A master agreement and DPA are backlog work, not established legal terms. Prices, sponsor commitments, commissions, margins, purchase authority and revenue targets are not approved. Sponsorship ending must preserve the organisation's data as required by US-CM-04; a funder or partner receives only authorised disclosure.

## Decisions and feedback

Nakul Jain must confirm the first target segment and cohort, the walkthrough scope, languages and geography, success thresholds, advisor responsibilities and commercial responsibility. Provider/region and data-retention decisions, named operations/support coverage and external services must be resolved before affected use. The [release goals](04-RELEASE-GOALS.md) place these decisions at their gates. At each review, compare results and limitations with the baseline, then record whether to continue, change or stop. A document, sprint estimate or Linear status change alone cannot approve scope or accept a story.


<!-- imprana:bundle-v4.2:documentation:20261011 -->

Application source 8a1e405f0086033dfb25ad834689a08bfe9f1eea; planning source eb194fdbb6fc8247db8429fc23120aa0fe659ed8; build 0.39.0, domain API 1.28.0, platform API 1.11.0, schema 43. These are source pins, not a fresh deployed-runtime assertion.

This edition applies the attached Product Management Agent Bundle v4.2 / standard 3.0-generic to Imprana Commons. It adds source-bound product reasoning and executable evidence plans. Original requirements, Gherkin, estimates, priorities, workflow states, release allocations, historical decisions and human edits remain authoritative. Recommendations below are not user research, a test execution, Ready/Done, an approved sprint, financial authority or production acceptance. The current request authorises documentation refinement and Linear publication.

Use the eight-tier chain: vision → strategy → roadmap → release goal → epic → user story → acceptance criterion and technical task. Criteria and tasks are sibling children of their story. Existing native epics can span releases; retain each story's real release and primary epic. A checker-only release anchor is explicitly a proposed adapter convention, never a native reparenting or scope change.

## Refined strategic choices and learning — 11 October 2026

| Objective | Choice and opportunity cost | Evidence of progress | Stop/change signal |
| --- | --- | --- | --- |
| STR-01 Trusted operating foundation | Prioritise current authority, isolation, immutable evidence, security/release qualification and recovery ahead of broader assistants or enterprise promises | Exact candidate qualification, source-bound refusal/replay/restore evidence, independent reviews and disposition | A current-authority/privacy/history defect blocks the affected commitment; a checklist or feature flag cannot waive it |
| STR-02 Appropriate problem and intervention | Capture structured diagnosis and baseline before conversational intake; compare process changes, manual and deterministic options with AI | A reviewed problem revision, evidence links, comparable options and a disclosed recommendation carried into the next stage | An undisclosed sponsorship, unsupported fit/confidence claim or untraceable recommendation requires correction |
| STR-03 Adoption and measured value | Fund capacity building, safe trials, support and follow-up alongside tool selection; distinguish forecast from realised value | M-01/M-03 with defined denominators, baseline, follow-up, non-response and operating cost | Attendance/logins alone or missing comparable follow-up cannot support an adoption/value claim |
| STR-04 Dependable official impact evidence | Keep MEL definitions, source lineage, deterministic arithmetic and independently approved reporting as the shared platform foundation | M-02/M-04/M-05 plus original arithmetic, lock, revision, import and reporting scenarios | Any AI proposal treated as an official figure, silent source loss or later mutation of approved history blocks release |
| STR-05 Accountable service ecosystem | Start with a curated and disclosed advisory/service path; earn multi-partner scale through observed need and operating evidence | Capability/price/sponsorship provenance, scoped engagement handoffs, complaint/exit and entitlement evidence | Unapproved financial commitment, inaccessible exit, or commercial influence hidden from comparison blocks the affected decision |

The business model remains a planning hypothesis: organisation access plus optional advisory/capacity-building services and disclosed sponsorship. Proposed commercial measures are qualified demand, retained task completion, support minutes per eligible organisation, delivery cost and successful governed exit; no revenue, margin, conversion rate, price or market-size observation is fabricated. Procurement comparison must include suitability, total operating cost, data/region/exit constraints, capability limitations and commercial influence. A supplier plan does not itself create a DPA or approve a destination.

**Recommended sequence:** resolve Foundation evidence and Sprint 1 acceptance; qualify structured diagnosis and saved baselines; enable bounded AI job policy/budget/evaluation only where genuinely needed; connect trial, value case, deployment and adoption; then qualify cohort/grantee/partner scale. The existing proposed Sprint 2 set is unchanged (US-DX-01a 5, US-DX-03 8, FR-AI-016a 8, US-CM-05 5; 26 points, not committed). Do not schedule usage alerts ahead of the job/budget boundary they depend on, or conversational intake ahead of its structured record and policy controls.

For each investment, record the problem, affected population, alternative, source evidence, strongest counter-hypothesis, consequential risk, proposed experiment and continue/change/stop rule. Reuse existing code only after the exact affected contract is inspected and qualified; a route or screen already present does not establish acceptance of its full source story.

Seven AI assurance groups apply when the slice touches AI: intended use and accountable owners; permitted data/provenance and destinations; model/prompt/tool/version records; scoped evaluation including adverse cases; human authority and refusal/fallback; security/privacy/abuse controls; and operational monitoring, budget, incident/recovery/exit. Scope exclusions need evidence and review. Unknown provider/language/region/data approval is a dependency, not a green control. Existing source NFR/AI thresholds remain exact.
