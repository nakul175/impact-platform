# Nonprofit AI Enablement Platform Business Requirements

Edition 1.0   5 October 2026   Proposed business baseline

Prepared for the product owner and nonprofit pilot stakeholders. This document defines the business scope for extending the Impact Platform into an AI enablement service for nonprofits. It sets the basis for the functional specification, architecture, detailed design, wireframes and test coverage. Owner review is required before this proposed baseline becomes an agreed scope.

## Purpose and business problem

Nonprofit teams need help deciding where AI is useful, practising with it, comparing tools, procuring services and running accountable pilots. A catalogue alone does not resolve those tasks. The proposed service connects a team goal to assessment, learning, a solution shortlist, a procurement brief, human advice, delivery and evidence about the result.

The sponsor has requested reuse where appropriate from Mercy Corps TolaData and the sponsor's MSME platform. The business direction is an AI enablement platform for nonprofits covering use, capacity building, procurement, marketplace, comparison and advisory services. This is a sponsor direction; supplier partnerships, revenue terms, eligibility rules and purchase authority have not been decided.

## Document authority and interpretation

This is a new specification for the nonprofit AI extension. It does not replace the retained impact-management BRD, FSD, HLD or LLD or amend their 307-requirement acceptance ledger. Business identifiers use BR-NPA and derived functional identifiers use FR-NPA. A requirement described below is a proposed obligation, not proof of implementation or acceptance. Current product status and future target design are identified separately.

The document sequence is BRD to FSD to HLD to LLD. Tests and wireframes may be drafted in parallel against the same identified requirements. Downstream documents inherit open decisions rather than treating them as approvals. The requirements register is requirements.json and the package index is README.md.

## Product outcomes and success measures

The platform should help an organisation choose a bounded problem, understand the work and data needed, practise with representative synthetic examples, compare evidenced alternatives and record accountable delivery decisions. The result should be less avoidable work and better task quality, measured rather than assumed.

Before a pilot, record the current process, drafting and review time, corrections, accessibility needs and acceptance criteria. After the pilot, compare equivalent tasks and include human review and support effort. Also record staff participation, demonstrated competence where an assessment exists, procurement completeness, incidents and successful data export. Numeric improvement targets, a pilot cohort size and commercial targets remain owner decisions; this BRD promises no savings, ROI or adoption rate.

## People and responsibilities

The organisation sponsor defines the problem and owns the decision to adopt. An adoption lead maintains the shared plan. Staff practise and contribute within their granted scope. A data owner reviews permissible inputs and disclosure. A buyer prepares comparable requirements and offers. A different authorised natural person approves consequential procurement decisions under the organisation's policy.

A learning coordinator organises future cohorts and an assessor reviews task evidence. A human adviser works within an agreed scope and discloses conflicts. Suppliers supply attributable claims and offers. Catalogue curators review proposed public content. Platform operators run the service without overriding private organisation access. The product owner sets marketplace responsibilities, release scope and commercial policy. These are business roles; detailed capability assignments belong in the FSD.

## End to end journeys

For a first pilot, the organisation describes its goal, receives a transparent readiness assessment, selects a suitable task, practises through lessons, compares tools and saves a shortlist. The adoption lead prepares a procurement brief and a pilot success measure. The first local product can preserve these draft records; actual supplier responses, human advisory bookings and purchasing belong to later service journeys.

For operated procurement, the buyer shares an independently reviewed brief with named suppliers, captures written offers, compares costs and evidence, and seeks a separate approval. The engagement records agreed scope, milestones, delivery evidence and acceptance. A proposed financial transaction can occur only after the owner approves the marketplace and payment model and the controls are qualified.

For a sensitive or difficult task, the organisation opens a restricted advisory case, agrees the adviser and sharing boundary, receives advice and records its own decision. Generated advice or an adviser recommendation alone cannot approve a purchase, disclose data or determine official impact results.

## Scope and delivery sequence

R1 covers controlled adoption planning and a synthetic-data pilot: readiness, use cases, sourced discovery, comparison, practical learning, procurement drafts, saved plans, bounded advisory drafts and inherited governance. R2 proposes operated learning, competency evidence, human advice, supplier onboarding, requests for offers, governed engagements, integration support and outcome tracking. R3 is conditional on the owner's financial and accountability decisions and covers integrated purchasing, payments and scale.

These releases express dependency order and do not commit dates or budget. Pilot geography, languages, cohort, hosting service levels and commercial ownership require decisions before the affected implementation is approved. First-pilot working notes exclude beneficiary personal data and credentials. A future approved data use requires a policy and reviewed design specific to that use.

## Business requirements

### Organisation goals and readiness profiles

**BR-NPA-001**   Proposed phase R1

Teams need a shared account of their goal, people, data and constraints.

Business acceptance: Authorised staff can save a named draft with sector, team size, goal, data readiness, experience and sensitive-data indicator; distinguish self-report from reviewed evidence.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Transparent readiness assessment

**BR-NPA-002**   Proposed phase R1

Teams need to choose a realistic first step.

Business acceptance: The same valid profile and rule version produce the same readiness stage, reasons, gaps and next steps; edits invalidate the prior assessment and no provider call is required.

Current baseline status: local implementation. This status is supporting implementation context, not acceptance.

### Use cases and pilot selection

**BR-NPA-003**   Proposed phase R1

Teams need relevant tasks with explicit prerequisites and human responsibility.

Business acceptance: Each suggested use case names applicability, prerequisites, acceptance checks and human decision needs; an unsuitable or non-AI alternative can be shown without promising savings.

Current baseline status: local implementation. This status is supporting implementation context, not acceptance.

### Evidence based tool discovery

**BR-NPA-004**   Proposed phase R1

Teams need a reliable starting point for finding AI tools.

Business acceptance: Every published tool names its provider, purpose, sources, review date and uncertainty; browsing does not imply approval, a quote or eligibility.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Comparable tools and offers

**BR-NPA-005**   Proposed phase R1

Teams need to understand differences before choosing a solution.

Business acceptance: Compare selected tools across common attributes, distinguish subscriptions from API access, and show missing costs or terms as unknown; do not manufacture a ranking.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Shared adoption plans

**BR-NPA-006**   Proposed phase R1

Teams need continuity across assessment, learning, procurement and pilots.

Business acceptance: Saved plans reopen with their brief, shortlist, progress and notes; edits preserve earlier revisions, stale updates conflict, and current access governs every read and retry.

Current baseline status: local implementation. This status is supporting implementation context, not acceptance.

### Practical self paced learning

**BR-NPA-007**   Proposed phase R1

Staff need to practise safe and useful AI work.

Business acceptance: Lessons provide explanation, synthetic exercises and self-checks; self-recorded progress persists without being presented as competency certification.

Current baseline status: local implementation. This status is supporting implementation context, not acceptance.

### Competency evidence

**BR-NPA-008**   Proposed phase R2

Organisations need evidence that staff can perform the intended task.

Business acceptance: A proposed assessment records a task rubric, submitted evidence, assessor decision and remediation; a completion checkbox alone cannot establish competence.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Learning programmes and cohorts

**BR-NPA-009**   Proposed phase R2

Teams need coordinated capacity building rather than isolated lessons.

Business acceptance: An authorised coordinator can assign a learning programme and review participation within organisation scope; learners see their own work and agreed sharing boundaries.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Consented AI advisory drafts

**BR-NPA-010**   Proposed phase R1

Teams need tailored advice while retaining human accountability.

Business acceptance: A separately permitted user explicitly consents to the submitted brief leaving the platform; the bounded draft remains unapproved, protected in storage and replayable without duplicate generation.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Human advisory cases

**BR-NPA-011**   Proposed phase R2

Teams need access to accountable human support for difficult adoption decisions.

Business acceptance: A case has a named adviser, agreed scope, disclosed conflict, restricted sharing, actions and recorded closure; advice alone cannot approve spending or disclose protected records.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### AI task workbench

**BR-NPA-012**   Proposed phase R2

Teams need help applying AI to routine tasks using approved information.

Business acceptance: Approved templates define inputs, purpose, output checks and review ownership; generated work is visibly a draft and cannot execute consequential actions without an authorised human decision.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Procurement briefs

**BR-NPA-013**   Proposed phase R1

Buyers need a testable problem statement before approaching suppliers.

Business acceptance: An editable brief records requirements, permitted data, budget assumptions and supplier questions, retaining unknowns and avoiding invented prices or commitments.

Current baseline status: local implementation. This status is supporting implementation context, not acceptance.

### Requests for offers and quotes

**BR-NPA-014**   Proposed phase R2

Buyers need comparable written offers.

Business acceptance: An authorised buyer can issue a versioned brief to named recipients after disclosure review; responses record currency, validity, inclusions, exclusions and evidence without sending messages automatically from a draft.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Total cost comparison

**BR-NPA-015**   Proposed phase R2

Buyers need to compare the full cost of alternatives.

Business acceptance: Comparison separates setup, recurring, usage, training, review, support and exit costs, states assumptions and dates, and excludes missing amounts from any asserted complete total.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Independent procurement decisions

**BR-NPA-016**   Proposed phase R2

Purchases need accountable approval and conflict controls.

Business acceptance: The requester cannot approve their own decision by the same natural person; the approver sees exact quote revisions, checks current authority and records the decision under the agreed procurement policy.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Supplier onboarding and publication

**BR-NPA-017**   Proposed phase R2

The marketplace needs attributable listings and evidence.

Business acceptance: Supplier submissions and supporting evidence remain private until independently reviewed; a published snapshot identifies verification scope, expiry and conflicts and does not imply blanket certification.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Marketplace neutrality and conflicts

**BR-NPA-018**   Proposed phase R2

Buyers need to understand how listings and advice may be influenced.

Business acceptance: Display the basis for placement, comparison and any commercial relationship; separate an editorial mapping from a verified capability or paid placement; revenue policy requires owner approval.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Bookings and service engagements

**BR-NPA-019**   Proposed phase R2

Buyers and advisers need a clear record of agreed work.

Business acceptance: A booking or engagement identifies parties, scope, terms, milestones and cancellation policy; external acceptance and delivery are recorded as evidence rather than inferred from an outbox intent.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Purchasing and payments

**BR-NPA-020**   Proposed phase R3

Some organisations may need transactions through the platform.

Business acceptance: Enable purchasing only after the owner chooses operator responsibility, financial controls and payment model; idempotency, reconciliation, refunds and independent approval must be qualified before money moves.

Current baseline status: conditional target. This status is supporting implementation context, not acceptance.

### Pilot delivery and acceptance

**BR-NPA-021**   Proposed phase R1

Organisations need to move from a shortlist to a reviewed working pilot.

Business acceptance: Record the scope, success measure and actions; target delivery adds versioned milestones and independent acceptance evidence; self-recorded pilot checklists remain visibly different from accepted delivery.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Integration and deployment support

**BR-NPA-022**   Proposed phase R2

Teams need controlled connections to the tools they choose.

Business acceptance: Connections use reviewed scopes and server-side secrets, support revocation and failure visibility, and begin with synthetic trials; no integration can broaden data access or deploy from unapproved advice.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Usage budgets and spending controls

**BR-NPA-023**   Proposed phase R1

Organisations need to contain AI and service costs.

Business acceptance: Enforce configured tenant budgets before external generation, bound requests and timeouts, expose unavailable-credit conditions, and replay prior outcomes without automatically spending again.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Adoption outcomes

**BR-NPA-024**   Proposed phase R2

Teams need to know whether adoption improved their work.

Business acceptance: Record a baseline and outcome with time period, review effort, quality criteria and evidence; link to governed impact measurements where appropriate, retaining deterministic official arithmetic.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Organisation isolation and current access

**BR-NPA-025**   Proposed phase R1

Each organisation must control access to its own plans and cases.

Business acceptance: Cross-organisation selectors do not reveal protected content; reads, writes, replay, exports and disclosures recheck current scoped authority, and a platform operator gains no automatic business-data access.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Privacy and data lifecycle

**BR-NPA-026**   Proposed phase R1

Teams need explicit rules for information entered into AI or shared with suppliers.

Business acceptance: Show the allowed data boundary, obtain action-specific consent for disclosure, apply an approved retention policy and explain backup limitations; personal beneficiary data is excluded from the first pilot.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Revision history and accountable actions

**BR-NPA-027**   Proposed phase R1

Teams need a reliable history of who did what.

Business acceptance: Writes preserve immutable revisions and atomic audit, outbox and receipt records; identical retries replay an authorised original result and changed payloads conflict.

Current baseline status: local implementation. This status is supporting implementation context, not acceptance.

### Accessible and understandable experience

**BR-NPA-028**   Proposed phase R1

Small nonprofit teams need a usable interface across devices and abilities.

Business acceptance: Critical journeys work by keyboard and on a narrow screen, with readable comparisons, clear labels and recoverable errors; automated findings and manual accessibility evidence are distinguished.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Reliable operation during dependency failure

**BR-NPA-029**   Proposed phase R1

Basic planning must continue when an AI provider is unavailable.

Business acceptance: Readiness, discovery, learning and saved drafts operate without AI generation; provider failure is explicit and bounded, ambiguous outcomes require safe retry or investigation, and no official data is corrupted.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Ownership and portability

**BR-NPA-030**   Proposed phase R2

Organisations need to retain their working information and exit a service.

Business acceptance: A separately permitted export includes approved scope, versions and context and is audited; export rights and provider exit obligations are stated before engagement.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Content maintenance and provenance

**BR-NPA-031**   Proposed phase R2

Tool and learning content can become outdated.

Business acceptance: Published content carries stable identifiers, versions, sources and review dates; material changes require review, retain prior meaning and mark unavailable or stale offers without rewriting saved history.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Support and incidents

**BR-NPA-032**   Proposed phase R2

Users need a clear route for help and harmful-output or access incidents.

Business acceptance: A support case records severity, owner, response expectation and restricted evidence; defined incidents can pause a connector or pilot, and resumption needs an accountable decision.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Governed release and onboarding

**BR-NPA-033**   Proposed phase R1

New features must reach organisations without bypassing their authority or operational checks.

Business acceptance: Release requires the four existing hosted jobs and owner confirmation; grants remain within reviewed ceilings, migrations are additive, and a deployment has an observable health result.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Feedback and improvement

**BR-NPA-034**   Proposed phase R2

The product needs evidence about usefulness and unmet needs.

Business acceptance: Capture optional task-level feedback with consent and minimised data; changes to rules, content or recommendations are reviewed and versioned rather than silently learned from private records.

Current baseline status: target. This status is supporting implementation context, not acceptance.

### Human control over consequential decisions

**BR-NPA-035**   Proposed phase R1

AI enablement must preserve responsibility for people, money and official results.

Business acceptance: Generated text, scores and checklists remain proposals; sensitive disclosures, purchases, deployment, eligibility and official impact calculations require the appropriate independent human or deterministic controls.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

### Reuse and interoperability

**BR-NPA-036**   Proposed phase R1

Delivery should accelerate through compatible existing components.

Business acceptance: Reuse the governed platform and compatible Mercy Corps and MSME patterns with provenance and licence records; preserve tenant isolation, independent approval and official calculation semantics.

Current baseline status: partial local. This status is supporting implementation context, not acceptance.

## Current product and evidence

The review branch at commit 36073f1 contains build 0.30.0, schema 35 and domain API 1.21.0. It implements a readiness guide, an eight-product source-backed directory, comparison and shortlists, twelve lessons with self-checks, saved shared adoption plans, procurement notes and self-recorded pilot actions. AI advisory drafts have separate consent and capability checks, sealed replay and bounded requests. Live generation remains blocked by the selected provider project's exhausted credits. The branch is not deployed.

Local qualification recorded 1,101 passing tests, seven unchanged Mac-specific operations failures, 76 skipped cases and one deselected case. Ten local Chrome workflow checks passed, including bounded comparisons, save/reload, exact retry, stale conflicts, read-only access, mobile containment and automated accessibility scans. Two incomplete automated accessibility checks require manual investigation. These results support specific implemented behaviours and do not establish native concurrency, production readiness or formal acceptance. The four hosted release jobs and an owner-approved merge remain required.

Source-backed tool discovery is not a verified supplier registry. Self-recorded lesson and pilot progress is not competency evidence or independent acceptance. A procurement brief is not a quote, award or payment. These distinctions apply throughout the package.

## Business rules and constraints

Organisation isolation, current scoped authority, separate read/export/approve/disclose permissions, independent approval by natural person, immutable approved records and deterministic official arithmetic remain mandatory. AI proposes. A provider request must use only the approved action's inputs, with explicit consent and budget controls. Draft preparation never sends a supplier message or moves money.

Published claims require attributable sources and review dates. Unknown prices, terms, eligibility and measured benefits remain unknown until evidenced. Revenue and placement policy must be explicit and approved; the MSME fee model is not a nonprofit decision. Reuse must preserve licences and provenance. Content updates must not silently reinterpret saved versions or learning progress.

## Dependencies risks and open decisions

The existing platform supplies identity, tenant authority, revisions, audit, outbox, receipts and deterministic impact calculations. Provider credits and server configuration are dependencies for live generated drafts. Existing organisations require reviewed capability ceilings and grants; an updated profile cannot widen them automatically. Human services depend on named accountable people and an operating process, while financial services depend on a separately chosen financial model.

The decision register records open choices for the first cohort and geography, pilot tasks, data boundary, revenue and marketplace responsibility, supplier verification, adviser accountability, procurement policy, competency standard, retention and export policy, operational service levels and provider budget. No item is deemed approved by a document being written. Risks include misleading tool claims, excessive costs, unsafe disclosure, conflicts, overstated competency, biased comparisons, scope drift and inaccessible interfaces. The linked security and operations documents allocate controls and test evidence for these risks.

## Acceptance and change governance

Review this BRD with the product owner and representative organisation users. Resolve the affected open decisions, approve a defined phase and record the approving human and date. Derive detailed behaviours and test cases from the approved scope. Completion requires successful tests in the specified environment, traceable evidence, UAT sign-off and release controls; a populated test catalogue is not an executed test run.

Changes identify affected business and functional requirements, data, screens, tests and operational obligations. Update the version and decision history before implementation. Preserve earlier editions and the original impact requirements. Proposed requirements may be deferred through an owner decision; they must not be removed merely to make existing code appear complete.

## Evidence and related documents

The factual implementation baseline comes from VERSION.json, the implemented OpenAPI contract, migrations 0034 and 0035, the AI catalogue/adoption/provider modules, the product screens and docs/RELEASE-0.30-ai-adoption-tool.md. Test evidence is recorded in docs/evidence/nonprofit-ai-adoption-local-suite.xml, nonprofit-ai-adoption-local-summary.json and ai-enablement-browser-tests.json. Retained business and security invariants come from AGENTS.md, CLAUDE.md and the current impact-platform specifications. Vendor offers are supported only by the dated official sources in the catalogue; this BRD does not create or extend those offers.
