# Imprana Commons release goals

Owner: Nakul Jain · Prepared 10 October 2026 · Status: proposed product planning baseline; product scope approval pending.

These goals use the existing five backlog buckets. All new pilot choices, business-model choices and exit targets below are proposals. Preparing this planning structure and Linear integration does not approve product scope, a provider, real-data use, spend or a release. See the [roadmap](03-ROADMAP.md) for sequencing and the [strategy](02-STRATEGY.md) for objective IDs.

## Common evidence rule

Every active story in a release needs a traceable epic/area, user outcome, refined acceptance and rejection criteria, dependencies and technical tasks. Release acceptance requires the [Definition of Done](../agile/WORKING-AGREEMENT.md), named evidence for every included story, applicable production gates and the owner's recorded decision. If an early slice excludes existing release stories, Nakul Jain must explicitly approve and record that scope change; a slice is not acceptance of the whole bucket.

For each review, record the candidate and environment, intended scope, actual checks and results, unresolved defects and limitations, reviewers, owner decision and supporting evidence. Named human approval remains required for future changes. Shared controls cannot be waived through a feature flag, an AI review or a general risk statement. Implementation and acceptance records are in [HANDOVER](../HANDOVER.md), [IMPLEMENTATION](../IMPLEMENTATION.md), the [completion ledger](../COMPLETION-LEDGER.md) and the retained [Sprint 1 review](../sprints/SPRINT-01-REVIEW.md); the [strategy](02-STRATEGY.md) clarifies the review's older pre-merge wording. This document records proposed goals.

## RG-FOUNDATION — establish the product and delivery foundation

**Outcome:** the team can develop Imprana Commons under clear ownership, a coherent backlog and independently reviewed engineering controls. Supports STR-01. Scope: six active stories in Security and Transition.

**Scope anchors:** US-RT-01 licence, US-RT-02 rename/rebrand, US-RT-03 archive policy/evidence transition, US-RT-05 one backlog, FR-SEC-008 secure engineering lifecycle and FR-SEC-010 independent security review. The source stories retain their original wording; adopting Linear requires a recorded tooling decision wherever that wording names GitHub as the backlog.

**Proposed exit evidence:** licence decision and document are recorded; transition preserves repository and evidence traceability; the backlog has every active ID exactly once and retains both split-parent relationships; release records connect changed stories to reviewed code, threats and evidence; branch controls require the intended checks and human review; the independent security review has a named reviewer, agreed scope and recorded findings/disposition. Commissioning a review is not a passing security assessment.

**Owner decisions:** licence terms and authority, transition/archive approach, GitHub/Linear division of responsibility, reviewer and spending. These external actions are not performed by writing this plan. Nakul Jain owns scope decisions; legal/licensing, engineering and security work need named accountable people before execution.

## RG-R1 — demonstrate a governed pilot journey

**Outcome:** a pilot organisation can take a priority problem through diagnosis, a trial and adoption, then compare the result with its approved baseline while producing trustworthy MEL evidence. Supports STR-01–05. Scope: 172 active R1 Pilot stories; a narrower first walkthrough is proposed in [the strategy](02-STRATEGY.md).

**Scope anchors:** structured diagnosis and collaborative review (US-DX-01a, US-DX-02/03/04/05); transparent opportunity mapping (US-MP-01/02/03/04); vetted, disclosed discovery and trial (US-DC-01/02/03/04, US-AS-01/03); value case and baseline (US-VC-01/02/03/05); owned deployment (US-DP-02/03); training/champions and follow-up (US-AD-01/02, US-IM-01/02/03). Inherited identity, tenancy, collection, review, calculations, privacy, reporting and operations stories remain required. AI use requires policy and budget controls including FR-AI-001 and FR-AI-016a/016b. Usage limits are visible through US-CM-05.

**Proposed exit evidence:** a representative synthetic journey preserves the problem evidence, baseline, explained recommendation, trial result, approved value case, deployment ownership and outcome comparison. Every selected option shows its evidence and disclosure; incomplete scores or missing costs remain explicit. A different authorised natural person reviews consequential decisions. Official results reconcile to approved source revisions and deterministic rules through locked snapshots and frozen reports. AI-off and budget-exhausted cases still complete core MEL work. Tenant boundary, stale changes, revoked access, forbidden disclosures and self-approval rejection cases pass. All included stories meet the common evidence rule and applicable gates in the intended environment.

Measure baseline and follow-up total work/review time, corrections, training evidence, actual use, support effort and incidents. Report equivalent tasks and observation periods; label forecast and realised value separately. No saving, ROI, cohort size or adoption threshold is approved here.

**Dependencies and owner decisions:** Foundation; accepted structured problem and baseline work; AI policy/jobs before conversational intake; reviewed listings and advisor responsibility; provider/region, destination, permitted data and retention before generated work; email, off-server recovery, alerts and named support before operated use. Nakul Jain must choose the first cohort, problems, languages, geography, scope and success thresholds, and confirm editorial scores/disclosures and threat residual decisions. Current use remains synthetic; any real-data pilot requires a separate approved boundary and qualified controls. Assign named product, MEL, adoption/advisor, engineering, security/privacy and operations owners before the gate review.

## RG-R2 — repeat adoption safely at scale

**Outcome:** organisations and funder-sponsored cohorts can repeat the journey with reliable support, controlled sharing and accountable partners. Supports STR-01, STR-03, STR-04 and STR-05. Scope: 139 active R2 Scale stories.

**Scope anchors:** option comparison and scenario analysis (US-AS-02, US-VC-04); reusable deployment and local-language adoption (US-DP-04, US-AD-03/04); improvement evidence (US-IM-04/05); sponsored/direct entitlements and service invoicing (US-CM-02/03/06/07/08); grantee-controlled portfolio views (US-FP-02/04); partner onboarding, integration, referrals and review (US-PT-01/02/03/06). Wider offline collection, migration, participant, integration, calculation and operational stories retain their assigned scope.

**Proposed exit evidence:** representative multi-organisation and cohort cases demonstrate that no tenant is exposed without authority, grantees control each funder disclosure and ending sponsorship preserves data. Entitlement changes, invoices and any partner share reconcile to approved terms and retain an audit trail. Partner listings/referrals show consent and disclosures; review/delisting preserves historical evidence. Included offline, integration and migration stories pass their conflict, expiry, replay, export and failure cases. Measure peak/soak workload, recovery and support effort in the intended environment against owner-approved limits before claiming capacity.

**Dependencies and owner decisions:** accepted R1 controls and recorded lessons; sponsor and partner terms; qualified connectors and data handling; commercial responsibility and local-currency/tax treatment; expanded data boundary, languages, target workload and support/service levels. Nakul Jain sets these choices and names cohort, commercial, partner, privacy and operations owners. No invoice, legal term or throughput commitment is approved by this goal.

## RG-R3 — extend an accountable ecosystem

**Outcome:** add advanced capabilities where accepted evidence and commercial responsibility justify them, including authorised partner outcome feedback. Supports STR-01, STR-03, STR-04 and STR-05. Scope: 45 active R3 Ecosystem stories.

**Scope anchors:** US-PT-04 partner deployment outcomes; advanced AI/analysis and evaluation; richer evidence, measurement, finance, reporting and operations as assigned in the source backlog. This bucket does not authorise autonomous purchasing, official AI arithmetic or unrestricted cross-organisation access.

**Proposed exit evidence:** each included capability has an approved problem/value case, named operating responsibility and passing acceptance/rejection evidence. Partner outcome reads demonstrate disclosure authority and revocation. Financial and advanced-analysis outputs expose their assumptions, sources and limitations, preserve official-number rules and meet the approved security/privacy boundary. Ongoing service cost and support evidence are available for the owner's continuation decision.

**Dependencies and owner decisions:** accepted earlier platform and sharing controls, comparable outcome evidence, AI evaluation and specific permitted data uses. Nakul Jain must decide financial/marketplace responsibilities, which advanced capabilities justify investment and who owns partner and financial operations. No new payment model, spending or ROI is approved here.

## RG-LATER — retain optional scope for evidence-led decisions

**Outcome:** preserve future choices without making a delivery promise. Supports STR-01, STR-03 and STR-04. Scope: six active Could stories: FR-AI-017, FR-EVA-005, FR-EVA-008, FR-FIN-007, FR-PLN-008 and FR-SEC-015.

**Proposed entry and exit evidence:** before an individual story moves into delivery, record its unmet problem, user, value hypothesis, data/control implications, dependencies, acceptance/rejection checks, accountable owner and capacity/cost decision. An executed story then meets the common evidence rule. Remaining deferred stories do not block acceptance of another bucket unless their controls are a dependency of its approved scope.

**Owner decisions:** Nakul Jain chooses whether, when and into which release each optional story moves. This goal sets no deadline or spend. The bucket remains deferred until that decision is recorded.
