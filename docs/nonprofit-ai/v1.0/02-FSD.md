# Nonprofit AI Enablement Platform Functional Specification

Edition 1.0  |  5 October 2026  |  Proposed baseline for owner review

## Authority and reading order

This FSD derives from [the BRD](01-BRD.md) and the 40 functional requirements in requirements.json. The current reference is review commit 36073f1, build 0.30.0, schema 35 and domain API 1.21.0. The branch is not merged or deployed. R1, R2 and R3 below are the proposed nonprofit extension phases, separate from the original impact platform release groupings. This edition changes no original acceptance status and authorises no supplier contact, provider spending or financial action.

Each requirement states the current behaviour and the proposed increment. LOCAL_IMPLEMENTATION records bounded code and local evidence; PARTIAL_LOCAL records an incomplete subset; TARGET and CONDITIONAL_TARGET have no implementation claim. Business acceptance text is copied from the canonical registry and must be qualified through the separate test package. Future roles are logical responsibilities awaiting mapped capabilities and reviewed tenant ceilings, not grants already available to users.

## Actors and permissions

Current reader templates are TENANT_ADMIN, MEL_ADMIN, PROGRAMME_MANAGER, AUTHOR, REVIEWER, ANALYST and DATA_STEWARD. They can receive ai.enablement.read inside reviewed authority. Current managers are TENANT_ADMIN, MEL_ADMIN and PROGRAMME_MANAGER and also need read access. ai.advisory.request is separately scoped to these management templates. Authentication, role labels and ownership never substitute for current membership and grants. A grant ceiling is not expanded by changing a role template or generated profile.

Proposed responsibilities are learner, learning coordinator, competency assessor, adviser, buyer, procurement approver, supplier verifier, content publisher, connector administrator, support owner and financial operator. Map each responsibility to separate read, edit, review, disclose and export capabilities before implementing it. A supplier or external adviser receives only explicitly reviewed case or submission access. The control plane manages lifecycle and authority; it does not receive automatic tenant business reads.

## User journeys

A nonprofit team describes a goal, assesses readiness, reviews suitable AI or non AI examples, compares tools, practises with synthetic material, prepares a procurement brief, records pilot actions and saves a shared adoption draft. Consented AI advice is an optional separate action. The guide, directory, lessons and plan persistence continue without live AI. An unsaved change stays visible after error, conflict or an older save response.

The proposed operated journey adds coordinator assignments and competency evidence, human advisory cases, reviewed supplier publication, RFQs, validated quotes, deterministic cost comparison, independent procurement decisions, agreed engagements, accepted milestones and measured outcomes. Purchasing and payments are conditional R3 work. Draft preparation, comparison and booking do not imply financial commitment.

## Shared behaviour contract

All selectors are untrusted. Missing or inaccessible objects have the same RESOURCE_UNAVAILABLE response. Current authority is evaluated again on every read, mutation, replay, export and external disclosure. State changes pin exact expected revisions; approval checks natural person independence against all material authors. Server fields are not writable. Approved evidence is immutable and correction creates a new version.

Mutations use stable operation IDs. Plan saves commit registry head, revision, audit, outbox and receipt in one transaction under the tenant lock. External calls take place after a durable intent transaction and before a separate outcome transaction. An outbox intent is not proof of delivery. Official impact arithmetic remains in the existing deterministic calculation service and cannot be supplied by generated text.

The error envelope is code, message, retryable, correlation_id and permitted_actions with optional field_errors and reason_code. Recoverable UI errors retain input and identify the next safe action. An exact retry must reuse its submitted payload; it cannot silently submit edits made after the original attempt. Existing advisory failures are sanitised and replayed without a second generation. Detailed routes, DTOs and algorithms appear in the LLD.

## Functional requirements
### Organisation goals and readiness profiles

**FR-NPA-001**  Business source BR-NPA-001  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: An authorised plan manager enters a title and six profile fields. Readers may inspect a saved profile within their current scope.

Behaviour: Current: save a named organisation shared Draft with exact profile validation. A profile is self reported and can be changed through a new revision. Target: optionally attach reviewed readiness evidence with explicit author, reviewer and date; this is not present in schema 35.

Exceptions and recovery: Reject blank goal or title, unknown fields and invalid enumerations. Show field feedback without discarding the user input. Sensitive data selection triggers a review warning; it does not grant permission to send such data.

Acceptance reference: Authorised staff can save a named draft with sector, team size, goal, data readiness, experience and sensitive-data indicator; distinguish self-report from reviewed evidence.

### Transparent readiness assessment

**FR-NPA-002**  Business source BR-NPA-002  Proposed phase R1  Current state LOCAL_IMPLEMENTATION

Inputs and actors: A current reader submits a valid profile to assessment. Inputs are sector, team size, goal, data readiness, AI experience and sensitivity.

Behaviour: Current: deterministic stage and explanations are calculated without persistence or a provider call. Foundation takes precedence when either experience or data readiness is NONE; otherwise sensitivity requires review; remaining profiles are pilot candidates. Editing a profile clears its displayed assessment. Target: retain a versioned assessment alongside any reviewed profile evidence.

Exceptions and recovery: Invalid profile is refused. No numeric competence score, verified readiness, savings or ROI may be inferred. A provider outage must not change assessment results.

Acceptance reference: The same valid profile and rule version produce the same readiness stage, reasons, gaps and next steps; edits invalidate the prior assessment and no provider call is required.

### Use cases and pilot selection

**FR-NPA-003**  Business source BR-NPA-003  Proposed phase R1  Current state LOCAL_IMPLEMENTATION

Inputs and actors: A reader inspects editorial use cases returned by the assessment and chooses a bounded problem with its accountable owner.

Behaviour: Current: eligible general and sector examples are sorted by matching English goal keywords, then fewer unmet prerequisites, then stable use case ID. Each includes reasons, gaps and human approval needs. Non AI foundation steps remain eligible. Target: record the chosen use case, scope and testable acceptance criteria as a reviewed pilot decision.

Exceptions and recovery: No matching keyword is shown as a general example rather than a claim of fit. Medical, beneficiary eligibility, funding and official arithmetic decisions cannot be delegated to an AI recommendation.

Acceptance reference: Each suggested use case names applicability, prerequisites, acceptance checks and human decision needs; an unsuitable or non-AI alternative can be shown without promising savings.

### Evidence based tool discovery

**FR-NPA-004**  Business source BR-NPA-004  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: A reader searches the solution catalogue by name and category and follows attributed official sources.

Behaviour: Current: eight source backed editorial listings carry provider, purpose, deployment, commercial model, API availability, nonprofit offer notes, review date and uncertainty. Target: separate public reviewed supplier snapshots from private supplier submissions and show expiry or withdrawn status.

Exceptions and recovery: Unknown terms or eligibility remain unknown. A failed catalogue read has a recoverable message. Browsing or clicking a source never records a purchase or supplier endorsement.

Acceptance reference: Every published tool names its provider, purpose, sources, review date and uncertainty; browsing does not imply approval, a quote or eligibility.

### Comparable tools and offers

**FR-NPA-005**  Business source BR-NPA-005  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: A reader selects zero to four known solution IDs; a manager may retain that shortlist in a plan.

Behaviour: Current: comparison presents common catalogue attributes, distinguishes a user subscription from API access and shows source links and verification questions. Target: include exact written offer revisions and an incomplete total cost comparison with stated assumptions.

Exceptions and recovery: Reject a fifth selection or duplicate or unknown IDs. Do not add unsupported rankings or convert absent prices into zero. Narrow screen comparison remains readable and keyboard reachable.

Acceptance reference: Compare selected tools across common attributes, distinguish subscriptions from API access, and show missing costs or terms as unknown; do not manufacture a ranking.

### Shared adoption plans

**FR-NPA-006**  Business source BR-NPA-006  Proposed phase R1  Current state LOCAL_IMPLEMENTATION

Inputs and actors: A manager with both current read and management authority saves a closed plan create or update command; updates name the current expected revision.

Behaviour: Current: title, profile, shortlist, learning progress, procurement notes and pilot actions persist together in an immutable revision. List and reopen operate within current scope. Target: add reviewed delivery and other work as linked entities without changing the meaning of the original Draft.

Exceptions and recovery: Stale revision preserves unsaved edits and requires an explicit reload or reconciliation. A lost response offers retry with the identical operation ID and payload. The same ID with changed input conflicts; save success for an older input does not erase newer edits.

Acceptance reference: Saved plans reopen with their brief, shortlist, progress and notes; edits preserve earlier revisions, stale updates conflict, and current access governs every read and retry.

### Practical self paced learning

**FR-NPA-007**  Business source BR-NPA-007  Proposed phase R1  Current state LOCAL_IMPLEMENTATION

Inputs and actors: A reader opens one of twelve lessons; a manager records completed lesson keys in the plan. Each lesson includes explanation, synthetic exercise and a self check.

Behaviour: Current: three paths have four lessons each. Self check feedback is local; recorded completion is self reported. Target: connect the lesson to a governed programme and competency assessment without treating a checkbox as certification.

Exceptions and recovery: Unknown lesson keys are rejected. A tenant switch aborts requests and discards old results. Read only users can study but cannot modify organisation progress.

Acceptance reference: Lessons provide explanation, synthetic exercises and self-checks; self-recorded progress persists without being presented as competency certification.

### Competency evidence

**FR-NPA-008**  Business source BR-NPA-008  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a learning coordinator assigns a versioned task rubric to a learner; an authorised assessor reviews submitted evidence within the agreed scope.

Behaviour: Target only: CompetencyAssessment moves Assigned to Submitted, then Assessed or Remediation, and Closed when a recorded decision meets the rubric. Record rubric version, exact evidence revisions, assessor natural person, judgement and remediation. The owner must approve assessor independence and competency standard before delivery.

Exceptions and recovery: No self recorded completion can enter Assessed. Assessor editing creates authorship and cannot bypass the approved independence policy. Missing evidence, a stale candidate or changed rubric blocks decision. No certification claim exists today.

Acceptance reference: A proposed assessment records a task rubric, submitted evidence, assessor decision and remediation; a completion checkbox alone cannot establish competence.

### Learning programmes and cohorts

**FR-NPA-009**  Business source BR-NPA-009  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a coordinator defines LearningProgramme and Cohort, assigns a LearningAssignment and sets participants, due dates and visibility.

Behaviour: Target only: coordinator sees authorised participation; learners see their assigned work and expressly shared evidence. Programme versions pin lessons and rubrics. Removing a member ends future access without rewriting historical completion.

Exceptions and recovery: Reject cross organisation learners, invalid dates and duplicate live assignments. Participation lists and metrics must not reveal hidden learners or their evidence. No cohort management endpoint exists today.

Acceptance reference: An authorised coordinator can assign a learning programme and review participation within organisation scope; learners see their own work and agreed sharing boundaries.

### Consented AI advisory drafts

**FR-NPA-010**  Business source BR-NPA-010  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: A user needs current ai.enablement.read and ai.advisory.request authority and expressly consents to the submitted brief leaving the platform. Command contains operation_id, profile and consent true.

Behaviour: Current: reserve a tenant bounded request, call the provider outside the transaction and seal an unapproved DRAFT result. Only submitted profile and deterministic assessment are sent; no programme records are joined. Exact replay returns the original outcome after current access checks. Target: richer budget and reviewed task templates remain separately controlled.

Exceptions and recovery: Disabled configuration returns AI_NOT_CONFIGURED; three reserved attempts in a rolling 24 hours exhaust the current quota. Provider failure is stored and replayed without another call. A committed claim without outcome is in flight and needs investigation. Live generation is currently blocked by unfunded credits.

Acceptance reference: A separately permitted user explicitly consents to the submitted brief leaving the platform; the bounded draft remains unapproved, protected in storage and replayable without duplicate generation.

### Human advisory cases

**FR-NPA-011**  Business source BR-NPA-011  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a permitted requester opens HumanAdvisoryCase with problem, allowed data boundary and desired outcome. A named adviser accepts the scope and discloses conflicts.

Behaviour: Target only: Open, Assigned, AwaitingInput, AdviceDraft and Closed or Cancelled. Case membership and a reviewed disclosure determine which adviser sees which material. Closure records advice, actions and acceptance of closure; adviser access ends under the agreed policy.

Exceptions and recovery: An adviser is not automatically a tenant member with broad read rights. Conflict or missing consent blocks assignment or sharing. Advice cannot approve procurement, spending, protected disclosure or official results.

Acceptance reference: A case has a named adviser, agreed scope, disclosed conflict, restricted sharing, actions and recorded closure; advice alone cannot approve spending or disclose protected records.

### AI task workbench

**FR-NPA-012**  Business source BR-NPA-012  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a manager selects an approved TaskTemplate and supplies only allowed inputs; a reviewer checks the resulting TaskRun draft.

Behaviour: Target only: template versions specify purpose, input schema, forbidden data, provider configuration, checks and accountable reviewer. Output is labelled Draft and pinning records template and input versions. A separate authorised action is required to publish or act on it.

Exceptions and recovery: Unapproved templates, hidden inputs, absent consent or budget fail before generation. Prompt instructions inside input never broaden tool scopes. Output cannot invoke deployment, supplier messages or financial transfers.

Acceptance reference: Approved templates define inputs, purpose, output checks and review ownership; generated work is visibly a draft and cannot execute consequential actions without an authorised human decision.

### Procurement briefs

**FR-NPA-013**  Business source BR-NPA-013  Proposed phase R1  Current state LOCAL_IMPLEMENTATION

Inputs and actors: A plan manager writes requirements, data boundary, budget notes and vendor questions; a reader reviews the saved procurement brief.

Behaviour: Current: four bounded note fields persist in the Draft. No sending, quote collection or award occurs. Target: convert the agreed brief into a separate ProcurementRequest that pins the source plan revision and disclosure decision.

Exceptions and recovery: Over length or unknown fields are refused. Budget notes are assumptions, not available balance or approved expenditure. Draft save never sends an external message.

Acceptance reference: An editable brief records requirements, permitted data, budget assumptions and supplier questions, retaining unknowns and avoiding invented prices or commitments.

### Requests for offers and quotes

**FR-NPA-014**  Business source BR-NPA-014  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a buyer selects exact brief revision and named supplier recipients; an independent disclosure reviewer checks information to be released.

Behaviour: Target only: ProcurementRequest progresses Draft, Reviewed, Issued and Closed or Cancelled. SupplierQuote records exact responding party, currency, validity, inclusions, exclusions and evidence and progresses Received or Validated, Withdrawn or Expired. Issuance creates delivery intents only after the review; receipt evidence records actual delivery.

Exceptions and recovery: Changed brief or audience invalidates the review. Hidden recipients, unsafe attachments, expired offers and duplicate responses are flagged. External delivery failure is visible; an outbox row cannot prove the supplier received an RFQ.

Acceptance reference: An authorised buyer can issue a versioned brief to named recipients after disclosure review; responses record currency, validity, inclusions, exclusions and evidence without sending messages automatically from a draft.

### Total cost comparison

**FR-NPA-015**  Business source BR-NPA-015  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a buyer compares selected validated SupplierQuote revisions using an approved costing period, currency and explicit assumptions.

Behaviour: Target only: CostComparison separates setup, recurring subscription, usage, training, human review, support and exit amounts. Decimal strings and exact quote references are stored. Missing components produce INCOMPLETE totals; unlike currencies require an explicitly sourced exchange assumption.

Exceptions and recovery: Do not silently coerce missing costs to zero, sum unlike currencies or imply completeness. Changed quote revisions require recomputation. Calculations are deterministic and do not accept AI generated authoritative prices.

Acceptance reference: Comparison separates setup, recurring, usage, training, review, support and exit costs, states assumptions and dates, and excludes missing amounts from any asserted complete total.

### Independent procurement decisions

**FR-NPA-016**  Business source BR-NPA-016  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a requester submits ProcurementDecision referencing the exact comparison and offers; a separately permitted approver has current scoped authority and fresh assurance where policy requires it.

Behaviour: Target only: independent decision checks the approver is a different natural person from every material author, records declared conflicts and uses the owner approved thresholds and procurement policy. Approval pins all evidence revisions and never re points to a newer quote.

Exceptions and recovery: Self approval, aliases of the same person, stale evidence, conflict and expired authority are denied. A monetary threshold is not defined by this package. Approval does not itself charge money.

Acceptance reference: The requester cannot approve their own decision by the same natural person; the approver sees exact quote revisions, checks current authority and records the decision under the agreed procurement policy.

### Supplier onboarding and publication

**FR-NPA-017**  Business source BR-NPA-017  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a supplier submits SupplierSubmission through a constrained intake process; an independent verifier checks attributable evidence and intended publication.

Behaviour: Target only: Draft, Submitted, Returned, Approved. Publication creates PublishedSupplierSnapshot with approved visible fields, verification scope, sources and expiry. That snapshot is Published, Withdrawn or Expired; private documents stay inside their authorising tenant scope.

Exceptions and recovery: No unchecked submission appears publicly. Publication with wider fields or audience needs a new decision. Verification means only the specified evidence was checked, not blanket supplier certification.

Acceptance reference: Supplier submissions and supporting evidence remain private until independently reviewed; a published snapshot identifies verification scope, expiry and conflicts and does not imply blanket certification.

### Marketplace neutrality and conflicts

**FR-NPA-018**  Business source BR-NPA-018  Proposed phase R2  Current state PARTIAL_LOCAL

Inputs and actors: A buyer inspects the catalogue explanation; proposed marketplace participants also disclose commercial relationships, sponsored placement and adviser conflicts.

Behaviour: Current: the catalogue identifies editorial mappings and does not rank endorsed suppliers. Target: an owner approved placement and revenue policy governs displayed order and identifies paid placement visibly; comparison criteria remain attributable.

Exceptions and recovery: A missing conflict declaration or undisclosed placement blocks publication or assignment. The MSME revenue model cannot become policy by reuse. No affiliate or marketplace fee is currently implemented.

Acceptance reference: Display the basis for placement, comparison and any commercial relationship; separate an editorial mapping from a verified capability or paid placement; revenue policy requires owner approval.

### Bookings and service engagements

**FR-NPA-019**  Business source BR-NPA-019  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a requester and adviser or supplier agree Engagement scope, participants, terms, milestones and cancellation policy before work starts.

Behaviour: Target only: Draft, Offered, Accepted, InProgress, Submitted, AcceptedDelivery and Closed or Cancelled. External acceptance, meeting or delivery requires attributable evidence. Exact agreed revisions form the basis of milestone acceptance.

Exceptions and recovery: Changing scope or terms after acceptance creates a revised agreement. A booking intent cannot prove consent or delivery. Permission to book is distinct from permission to buy or pay.

Acceptance reference: A booking or engagement identifies parties, scope, terms, milestones and cancellation policy; external acceptance and delivery are recorded as evidence rather than inferred from an outbox intent.

### Purchasing and payments

**FR-NPA-020**  Business source BR-NPA-020  Proposed phase R3  Current state CONDITIONAL_TARGET

Inputs and actors: Conditional proposal: a buyer requests Purchase only after operator responsibility, financial policy and provider model are approved. A separate permitted person authorises payment.

Behaviour: R3 only: PaymentAttempt needs stable external idempotency, provider event verification, reconciliation, uncertainty handling, refund policy and final ledger evidence. The financial operator determines responsibilities before API or schema finalisation.

Exceptions and recovery: Do not trigger money from a draft, quote, booking or AI output. An unknown payment outcome is investigated rather than automatically retried with a new ID. No payment processing or ledger exists in build 0.30.0.

Acceptance reference: Enable purchasing only after the owner chooses operator responsibility, financial controls and payment model; idempotency, reconciliation, refunds and independent approval must be qualified before money moves.

### Pilot delivery and acceptance

**FR-NPA-021**  Business source BR-NPA-021  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: A manager records pilot success measure and five self reported actions. Proposed delivery owner submits DeliveryMilestone evidence for independent acceptance.

Behaviour: Current: plan checklist tracks define goal, synthetic trial, human review, staff training and outcome review. Target: milestones move Draft, InProgress, Submitted, Accepted or Returned and pin test results, deliverable revision and accepting natural person.

Exceptions and recovery: A checkbox is never independent acceptance. Stale evidence or acceptance by the deliverable author fails. Failure against a quality gate returns the milestone with remediation; official impact figures stay in the existing governed measurement workflow.

Acceptance reference: Record the scope, success measure and actions; target delivery adds versioned milestones and independent acceptance evidence; self-recorded pilot checklists remain visibly different from accepted delivery.

### Integration and deployment support

**FR-NPA-022**  Business source BR-NPA-022  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a connector administrator declares provider, minimal scopes, intended data flows and secret reference; an independent reviewer approves the exact ConnectorBinding.

Behaviour: Target only: synthetic trial precedes production connection. Server side secrets remain outside business payloads; connection and revocation states, last success, failure class and scope version are visible to permitted administrators.

Exceptions and recovery: Unreviewed scope or destination, missing authority, revoked credential and stale approval block a call. A connector cannot copy hidden tenant records, widen permissions or deploy from advice. No external integration is currently provided by the adoption tool.

Acceptance reference: Connections use reviewed scopes and server-side secrets, support revocation and failure visibility, and begin with synthetic trials; no integration can broaden data access or deploy from unapproved advice.

### Usage budgets and spending controls

**FR-NPA-023**  Business source BR-NPA-023  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: Current advisory requester consumes a tenant bounded attempt slot. Proposed budget administrator configures approved currency budget, period and provider limits.

Behaviour: Current: reserve at most three attempts across the tenant in a rolling 24 hours, including failures; bound request and output and prohibit automatic provider retries. Target: enforce reservation and reconciliation of monetary and token budgets before calls, with usage accounting and independent budget changes.

Exceptions and recovery: Quota refusal is AI_DAILY_LIMIT. Credits exhausted produces a provider unavailable result. Availability indicates configuration, not funded provider access. Three attempts are a count quota rather than a monetary spending ceiling.

Acceptance reference: Enforce configured tenant budgets before external generation, bound requests and timeouts, expose unavailable-credit conditions, and replay prior outcomes without automatically spending again.

### Adoption outcomes

**FR-NPA-024**  Business source BR-NPA-024  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a pilot owner records AdoptionOutcome baseline and follow up period using agreed task, staff time, quality checks, review effort and supporting evidence.

Behaviour: Target only: outcome calculations declare units, sample boundaries and assumptions. Governed impact indicators may be linked by exact definition and snapshot revision. A reviewer approves interpretation and avoids causal attribution beyond the evidence.

Exceptions and recovery: Missing baseline or incomparable tasks prevents an asserted gain. Exclude savings estimates that omit human review or support effort. AI narrative cannot create official arithmetic or causal proof.

Acceptance reference: Record a baseline and outcome with time period, review effort, quality criteria and evidence; link to governed impact measurements where appropriate, retaining deterministic official arithmetic.

### Organisation isolation and current access

**FR-NPA-025**  Business source BR-NPA-025  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: Every caller is authenticated and holds active membership plus exact current capability and scope. Operators have control plane rights only.

Behaviour: Current: tenant context and forced RLS fence plans and advisory records; visible reads and lists recheck scope; advisory needs both reader and requester access. Target: every future entity, export and supplier disclosure follows the same security model with no cross tenant joins.

Exceptions and recovery: Missing and hidden resources return RESOURCE_UNAVAILABLE without existence detail. Revoked identity, inactive tenant and membership fail closed. Role names and custody never establish business data authority by themselves.

Acceptance reference: Cross-organisation selectors do not reveal protected content; reads, writes, replay, exports and disclosures recheck current scoped authority, and a platform operator gains no automatic business-data access.

### Privacy and data lifecycle

**FR-NPA-026**  Business source BR-NPA-026  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: A user sees data boundary guidance and action specific consent; proposed privacy owner applies reviewed policy to each new store and disclosure.

Behaviour: Current: advisory requires consent true and sends only submitted profile plus assessment; advice output is sealed. Plan notes are ordinary organisation shared revisions, not private journals. Target: class inventory, retention, holds, erasure and export include new entities and backup replay restrictions.

Exceptions and recovery: Do not input beneficiary information or credentials in the initial pilot. The sensitive_data flag is a warning, not a redactor or automated data scanner. Existing advisory tables are insert only; a specific retention and privacy migration remains a design decision.

Acceptance reference: Show the allowed data boundary, obtain action-specific consent for disclosure, apply an approved retention policy and explain backup limitations; personal beneficiary data is excluded from the first pilot.

### Revision history and accountable actions

**FR-NPA-027**  Business source BR-NPA-027  Proposed phase R1  Current state LOCAL_IMPLEMENTATION

Inputs and actors: A manager submits operation ID and expected revision for a change; reviewers and auditors use governed evidence appropriate to their separate rights.

Behaviour: Current: plan writes commit registry head, immutable revision, audit, outbox and receipt atomically. Receipt binds operation, actor and submitted payload and expires after seven days. Target: expose authorised revision history and export without broadening read scope.

Exceptions and recovery: Database failure rolls back all plan components. A valid exact retry replays once; changed payload conflicts. No archive, deletion or revision history screen exists for adoption plans today.

Acceptance reference: Writes preserve immutable revisions and atomic audit, outbox and receipt records; identical retries replay an authorised original result and changed payloads conflict.

### Accessible and understandable experience

**FR-NPA-028**  Business source BR-NPA-028  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: Users operate critical journeys with keyboard, understandable labels and narrow screen layout; planned translations need agreed languages and stable content versions.

Behaviour: Current: shared dialogs, labelled controls, readable comparisons, mobile containment and automated scans support local workflows. Target: manual keyboard, screen reader, zoom, error announcement, language and representative user evaluation qualify critical paths.

Exceptions and recovery: Incomplete automated checks require manual follow up. Zero serious or critical violations is not full accessibility certification. Preserve input after errors and return focus from dialogs to the initiating control.

Acceptance reference: Critical journeys work by keyboard and on a narrow screen, with readable comparisons, clear labels and recoverable errors; automated findings and manual accessibility evidence are distinguished.

### Reliable operation during dependency failure

**FR-NPA-029**  Business source BR-NPA-029  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: Users continue guide, directory, lessons and saved planning when AI generation is disabled or unavailable. Operators investigate ambiguous external outcomes.

Behaviour: Current: provider dependent advice is separately available; failure is bounded and sanitised. Current claims without a result return in flight and cannot be safely regenerated automatically. Target: service notices and a controlled recovery workflow identify ownership and evidence.

Exceptions and recovery: Provider or credit failure must not fail open or corrupt official results. Database failure prevents a save and leaves a retryable or explicit failure message. Never label a delivery or generation intent as success.

Acceptance reference: Readiness, discovery, learning and saved drafts operate without AI generation; provider failure is explicit and bounded, ambiguous outcomes require safe retry or investigation, and no official data is corrupted.

### Ownership and portability

**FR-NPA-030**  Business source BR-NPA-030  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: an independently permitted exporter selects visible scope, versions and intended recipient; an owner can review agreed exit obligations.

Behaviour: Target only: an export package records tenant, scope, object and revision IDs, content versions, schema, generation time and restrictions; current authority is checked on request and download and audit records the disclosure.

Exceptions and recovery: Read does not imply export. Hidden fields are excluded without count leakage. Downloaded bytes cannot be recalled; expiry, recipient boundary and backup limitations must be explained before release.

Acceptance reference: A separately permitted export includes approved scope, versions and context and is audited; export rights and provider exit obligations are stated before engagement.

### Content maintenance and provenance

**FR-NPA-031**  Business source BR-NPA-031  Proposed phase R2  Current state PARTIAL_LOCAL

Inputs and actors: A content owner reviews dated sources and lesson meaning; proposed independent publisher approves a version for readers.

Behaviour: Current: catalogues carry versions and checked dates; save pins current version strings. Target: content registry retains previous published snapshots, review and expiry, source links and licence attribution and distinguishes unsupported or withdrawn claims.

Exceptions and recovery: A catalogue refresh cannot rewrite saved history. Pinning a version string alone does not archive the referenced content. Stale sources are flagged rather than filled with invented updates.

Acceptance reference: Published content carries stable identifiers, versions, sources and review dates; material changes require review, retain prior meaning and mark unavailable or stale offers without rewriting saved history.

### Support and incidents

**FR-NPA-032**  Business source BR-NPA-032  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a user opens SupportCase with minimised evidence and severity; an accountable support owner triages under an approved service policy.

Behaviour: Target only: restricted case membership, incident owner, response expectation, action log and resolution. Defined incidents can pause a connector or pilot; resumption records an authorised human decision.

Exceptions and recovery: Support staff receive no automatic tenant data access. Do not attach secrets, beneficiary records or unapproved output. Service levels and severity response times remain owner decisions.

Acceptance reference: A support case records severity, owner, response expectation and restricted evidence; defined incidents can pause a connector or pilot, and resumption needs an accountable decision.

### Governed release and onboarding

**FR-NPA-033**  Business source BR-NPA-033  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: Release owner reviews exact branch evidence and approved scope; organisation administrators assign permitted grants inside reviewed ceilings.

Behaviour: Current: additive migrations and generated contracts/profile preserve existing boundaries. Target release requires all four hosted jobs green and explicit owner merge approval. Pending initial access requests on an old profile hash need re proposal; applied ceilings remain unchanged.

Exceptions and recovery: No automatic capability widening, migration rewrite or main push. A profile hash change is not authority. Live provider configuration and credits are separately validated under a spending decision before rollout.

Acceptance reference: Release requires the four existing hosted jobs and owner confirmation; grants remain within reviewed ceilings, migrations are additive, and a deployment has an observable health result.

### Feedback and improvement

**FR-NPA-034**  Business source BR-NPA-034  Proposed phase R2  Current state TARGET

Inputs and actors: Proposed: a consenting user submits task feedback with a minimal task reference and optional reasons, within current scope.

Behaviour: Target only: FeedbackRecord separates usefulness, quality concern and unmet need; content owners review aggregated or explicitly shared evidence before changing a version. Optional feedback is not required to save a plan.

Exceptions and recovery: No silent training or recommendation updates from private organisation records. Avoid unnecessary personal data and disclose sharing. Feedback withdrawal or erasure follows the approved class policy.

Acceptance reference: Capture optional task-level feedback with consent and minimised data; changes to rules, content or recommendations are reviewed and versioned rather than silently learned from private records.

### Human control over consequential decisions

**FR-NPA-035**  Business source BR-NPA-035  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: All users see proposal status; independently authorised humans control consequential decisions, while official figures use governed deterministic rules.

Behaviour: Current: advisory text and plan/checklist remain unapproved. Target: explicit decision gates for disclosure, award, deployment and acceptance pin exact reviewed evidence and account for natural person authorship.

Exceptions and recovery: An AI output, readiness stage, learning checkbox or API success cannot impersonate a human approval. Automated beneficiary eligibility, clinical decisions and official impact arithmetic remain outside this product scope.

Acceptance reference: Generated text, scores and checklists remain proposals; sensitive disclosures, purchases, deployment, eligibility and official impact calculations require the appropriate independent human or deterministic controls.

### Reuse and interoperability

**FR-NPA-036**  Business source BR-NPA-036  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: Product engineers inspect reused components with provenance, licence compatibility, interfaces and invariant tests before inclusion.

Behaviour: Current: reuse existing tenant authority, revision, audit and outbox infrastructure; earlier Mercy Corps reuse supplies approved logframe export and twelve arithmetic/calendar regression scenarios. MSME contributes an adoption journey pattern. Target: extensions use adapters and reviewed contracts rather than copying unrelated factory or financial rules.

Exceptions and recovery: Reject reuse that weakens isolation, disclosure or independence or changes pooled arithmetic. A conceptual reuse claim is distinct from an imported module or verified licence review.

Acceptance reference: Reuse the governed platform and compatible Mercy Corps and MSME patterns with provenance and licence records; preserve tenant isolation, independent approval and official calculation semantics.

### Closed profile and draft validation

**FR-NPA-037**  Business source BR-NPA-001  Proposed phase R1  Current state LOCAL_IMPLEMENTATION

Inputs and actors: Every profile and save command is a closed JSON object and uses typed bounded inputs. Server owns authorship, business state, content versions and approval fields.

Behaviour: Current: unknown fields and duplicate JSON keys are rejected; profile requires exactly six fields; selected identifiers are unique and known. Plan contract allows at most 100 lesson keys structurally, but semantic validation permits only the twelve current keys. Target: all new command schemas remain closed and explicitly versioned.

Exceptions and recovery: Reject booleans for integer team size, whitespace only titles/goals, bad UUIDs, unsupported fields, excessive strings and forged server fields. Validation precedes new persistence and generation.

Acceptance reference: Reject unknown fields, duplicate JSON keys, invalid identifiers and limits before persistence; client input cannot set author, approval, state or content versions.

### Stable content versions and learning identifiers

**FR-NPA-038**  Business source BR-NPA-031  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: Content publisher maintains stable IDs and historical meaning; managers save progress using current known lesson keys.

Behaviour: Current: saves stamp catalogue and solution versions and use path ID plus positional index keys. Target: keep existing keys attached to their original lesson meaning, assign new stable keys for new lessons and retain versioned snapshots or an explicit migration.

Exceptions and recovery: Reordering steps must not change what foundations:0 or any stored key means. Do not imply the present version strings supply a historical catalogue reader. A material lesson change requires version and migration review.

Acceptance reference: Pin catalogue versions on saves and preserve stable lesson meanings; future content reordering must not reinterpret existing progress.

### Current authority on exact retries

**FR-NPA-039**  Business source BR-NPA-027  Proposed phase R1  Current state LOCAL_IMPLEMENTATION

Inputs and actors: A retrying principal submits the identical body and operation ID while still holding current tenant, membership, read and action authority.

Behaviour: Current: plan replay resolves authority before receipt lookup, loads the original object for current visibility and rechecks the action against it. Advisory replay checks reader plus requester authority and original principal and fingerprint. Target: all future external operations preserve this order and fail closed on changed grants.

Exceptions and recovery: Revoked or hidden original outcomes are not replayed. The same ID with changed payload returns conflict; an expired plan receipt is IDEMPOTENCY_EXPIRED. Auto retry must never switch IDs or retry semantic conflicts.

Acceptance reference: Recheck current tenant, membership, read and action capabilities before replay; changed payloads conflict and inaccessible prior outcomes remain hidden.

### Release evidence and operational smoke

**FR-NPA-040**  Business source BR-NPA-033  Proposed phase R1  Current state PARTIAL_LOCAL

Inputs and actors: Release reviewer records exact commit, build, migration checksums, environment and outcomes; operator performs approved deployment smoke after merge.

Behaviour: Current baseline evidence: 1101 local passes, seven unchanged Mac operations failures, 76 skips and one deselection, plus ten local browser scenarios. Target: native role and concurrency, live identity, Linux browser and container path evidence on the exact candidate, followed by owner approved merge and observed health.

Exceptions and recovery: Local tests and documentation do not promote formal acceptance. A test case catalogue is not an execution log. Treat failed or skipped gates explicitly and do not present a review branch as deployed.

Acceptance reference: Record exact commit, schema and check results; a documentation edition or local test run does not promote acceptance or establish a successful deployment.

## Proposed state models

These states are design proposals and require approved policy and capability mapping before coding. Existing AIAdoptionPlan records are Draft only; no proposed state may be accepted in the current write DTO.

CompetencyAssessment uses Assigned, Submitted, Assessed, Remediation and Closed. A rubric change requires a new assignment version. LearningProgramme, Cohort and LearningAssignment separately record organisation membership and visibility. HumanAdvisoryCase uses Open, Assigned, AwaitingInput, AdviceDraft, Closed and Cancelled. Closure does not authorise purchase or disclosure.

ProcurementRequest uses Draft, Reviewed, Issued, Closed and Cancelled. Review pins the exact brief and audience; changing either returns the work to a new Draft. SupplierQuote uses Received, Validated, Withdrawn and Expired, and is always tied to its exact responding party and offer revision. ProcurementDecision uses Draft, Submitted, Approved, Returned or Cancelled; approval pins offers and costing assumptions. An approved decision is immutable.

SupplierSubmission uses Draft, Submitted, Returned and Approved. PublishedSupplierSnapshot is a separate reviewed projection with Published, Withdrawn or Expired status and only approved public fields. Engagement uses Draft, Offered, Accepted, InProgress, Submitted, AcceptedDelivery, Closed and Cancelled. DeliveryMilestone uses Draft, InProgress, Submitted, Accepted and Returned. Changes after accepted terms or delivery create a new version and decision.

ConnectorBinding uses Draft, Reviewed, Trial, Active, Paused and Revoked. TaskTemplate uses Draft, Reviewed, Published and Withdrawn; each TaskRun uses Requested, Reserved, Running, DraftResult, Failed or OutcomeUnknown. These are target lifecycle concepts, not existing provider request states. SupportCase uses Open, Triaged, Investigating, Resolved and Closed with a separate incident pause decision. Purchase and PaymentAttempt states remain conditional on DEC-NPA-015 and cannot be finalised responsibly before choosing the financial model.

## Validation and nonfunctional behaviour

Current bounded profile, notes, selections, plan ceilings and cursor limits are specified exactly in the LLD and data dictionary. Proposed new fields require explicit maxima, enumerations and retention classes during slice design. Reject unknown or duplicate fields rather than silently ignoring them. Render untrusted text as text and do not execute instructions or active content from catalogue sources, supplier attachments or generated output.

Security, accessibility, privacy, availability and performance requirements apply across all functions. No response time, service level, concurrent user capacity, recovery objective, ROI target or procurement threshold is fabricated here. DEC-NPA-001, DEC-NPA-002, DEC-NPA-008, DEC-NPA-009, DEC-NPA-010 and DEC-NPA-011 determine the relevant scope and measurable targets before pilot or scale acceptance. The test package includes smoke, unit, integration, regression, security, accessibility, performance and UAT scenarios, distinguishing specified cases from executed evidence.

## Owner decisions and release acceptance

Resolve DEC-NPA-003 for permitted data and consent, DEC-NPA-004 through DEC-NPA-007 for marketplace, verification, advisory and procurement policy, DEC-NPA-012 for content ownership, DEC-NPA-013 for reviewed ceiling widening and DEC-NPA-014 for connectors. R3 requires DEC-NPA-015. Outcome and feedback interpretation depend on DEC-NPA-016. All decisions are open; this FSD does not close them.

Release requires exact candidate qualification in the existing four hosted jobs and explicit owner approval before merge. Automated accessibility scans include incomplete items needing manual follow up; they are not a full conformance assessment. The original impact ledger remains 113 PARTIAL, 194 PENDING and zero accepted among 307 requirements. This extension namespace is a proposed baseline for review, not a completion percentage.

## Related design and evidence

Read [the HLD](03-HLD.md) for boundaries, [the LLD](04-LLD.md) for implementation contracts and the separate test and UX packages for cases, screens and fields. Factual sources are apps/api/impact_api/ai_enablement_catalog.py, ai_solutions_catalog.py, ai_learning_content.py, ai_enablement.py, ai_adoption_plans.py, ai_advisory_provider.py, ai_enablement_contracts.py, ai_adoption_contracts.py, apps/web/src/AIEnablement.tsx, AIAdoptionWorkspace.tsx, migrations 0034 and 0035, VERSION.json and docs/RELEASE-0.30-ai-adoption-tool.md. Local evidence is in docs/evidence/nonprofit-ai-adoption-local-suite.xml, nonprofit-ai-adoption-local-summary.json and ai-enablement-browser-tests.json. Proposed behaviour has no execution evidence until implemented and qualified.
