# Nonprofit AI Enablement Baseline and Glossary

Edition 1.0 · 5 October 2026

## Frozen product context

This specification edition uses review commit 36073f1 on release/0.30-nonprofit-ai-enablement, build 0.30.0, domain API 1.21.0, platform API 1.9.0 and schema 35. The schema count is derived from migration files. The broad original design contract is not the same as the implemented API contract. The branch is not merged or deployed by this documentation task.

The original impact platform has 307 requirements: 270 functional and 37 non-functional, with 113 PARTIAL, 194 PENDING and zero accepted. Its retained BRD/FSD/HLD/LLD editions, specification directory and completion ledger remain intact. This nonprofit AI extension introduces 36 BR-NPA business requirements and 40 FR-NPA functional requirements. It does not renumber or promote the original requirements.

Current AI adoption features include deterministic readiness, eight editorial use cases, eight source-backed product entries, three learning paths with twelve practical lessons, comparison up to four tools, tenant-shared draft plans, procurement notes and self-recorded pilot actions. Advisory draft infrastructure has explicit consent, bounded requests and sealed replay; live generation is blocked by exhausted provider credits. Human adviser operations, supplier onboarding, RFQs, quote awards, transactions, competency certification, integrations and outcome evidence are proposed.

## Evidence register

| Source | What it supports | Limitation |
|---|---|---|
| VERSION.json and implemented OpenAPI | Review build/API versions and implemented routes | Does not prove deployment or acceptance |
| Migrations 0034 and 0035 | Tenant advisory claim/result persistence and AIAdoptionPlan kind | Does not prove native concurrency or all target entities |
| ai_enablement_catalog.py and ai_learning_content.py | Deterministic rules, use cases, lessons and content versions | Maintained editorial content, not assessed competency |
| ai_solutions_catalog.py | Eight dated source-backed product descriptions | Not verified supplier inventory, quotes or guaranteed offers |
| ai_adoption_plans.py and workspace screens | Closed draft persistence, current authority, revisions and UI journeys | No plan-specific export, deletion or history UI |
| ai_enablement.py and ai_advisory_provider.py | Consent, attempt claim, provider boundary, bounded adapter and sealed replay | No money budget ledger, no working funded live-generation evidence |
| docs/evidence/nonprofit-ai-adoption-local-suite.xml and summary | 1,101 passed, seven known unchanged Mac-specific failures, 76 skipped, one deselected | Local in-memory evidence; does not replace native roles/concurrency, identity or container gates |
| docs/evidence/ai-enablement-browser-tests.json | Ten local Chrome workflows, mobile checks and automated scans | Two incomplete accessibility checks require investigation; not manual accessibility sign-off |
| docs/RELEASE-0.30-ai-adoption-tool.md | Current delivered slice and stated limits | Release note alone is not product qualification |
| AGENTS.md and CLAUDE.md | Existing governed engineering/business invariants | Opening version numbers reflect an older handover; use frozen code/release baseline above |

Counts describe the recorded product evidence, not tests executed during documentation authoring. Proposed test cases are marked separately and need execution against the approved implementation.

## Reuse provenance

Mercy Corps source inspection is pinned to upstream commit 7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d. The reuse trial, licence assessment and source links are in docs/handover/MERCYCORPS-REUSE.md. The governed logframe export adaptation and licence/notice handling are documented in docs/RELEASE-0.29-logframe-reuse.md. Independent arithmetic/calendar scenario adaptations are recorded in the later reuse release notes. Earlier trial statements remain historical; they do not describe all later release actions.

The inspected upstream uses Django/MobX and provides domain layouts and scenarios rather than a compatible tenant-governed runtime. No current commercial TolaData capability may be inferred solely from that older source. The nonprofit design reuses compatible journey patterns from the local MSME repository, not its manufacturing data, pricing or commercial policy. New literal reuse needs source and licence records; pattern inspiration is labelled as such.

## Glossary

| Term | Meaning in this package |
|---|---|
| BRD | Business Requirements Document: problem, intended outcomes, people, scope and business acceptance |
| FSD | Functional Specification Document: user/system behavior, inputs, decisions, states and errors |
| HLD | High Level Design: components, trust boundaries, major data flows and deployment responsibilities |
| LLD | Low Level Design: contracts, fields, algorithms, persistence, transitions and failure handling |
| Adoption plan | Tenant-shared working draft connecting profile, shortlist, learning, procurement and pilot notes |
| Readiness assessment | Deterministic versioned guidance from self-reported inputs, not certification or eligibility |
| Editorial catalogue | Sourced product descriptions curated as a starting point for discovery |
| Supplier verification | Proposed independently reviewed evidence with defined scope and expiry |
| Self completion | A user's recorded learning or pilot action, without independent competence/delivery acceptance |
| Competency evidence | Proposed task submission reviewed against a pinned rubric by an authorised assessor |
| RFQ | Request for quotation or offer: a versioned brief deliberately disclosed to named recipients |
| Total cost | Comparable dated cost categories and assumptions; missing inputs prevent a complete asserted total |
| Independent approval | Decision by a different natural person with current authority, bound to exact revisions |
| Official result | Governed deterministic impact calculation over approved source revisions |
| Operation receipt | Durable replay binding for one submitted operation; current access still applies |
| Outbox intent | Committed instruction for external work, not evidence that it was delivered or accepted |
| Sealed advisory result | Authenticated encrypted draft bound to its tenant and request |
| Capability ceiling | Reviewed upper boundary on what an organisation can grant; a new profile does not widen it |
| R1 R2 R3 | Proposed dependency phases, not promised release dates |
| Local implementation | Behavior exists on the review branch; no formal acceptance is implied |
| Target | Proposed behavior still requiring policy decisions, implementation and qualification |
| UAT | User acceptance testing by representative users against the approved scope |

## Package ownership

The product owner reviews business scope. Functional, technical, QA, UX, security and operating role owners review their dependent artefacts. Record named appointments and approvals through the decision/change process. Keep the requirements registry and traceability matrix aligned with every version; review changes to code against current facts before updating the baseline.
