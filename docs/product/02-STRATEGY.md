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
