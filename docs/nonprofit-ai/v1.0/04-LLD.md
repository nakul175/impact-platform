# Nonprofit AI Enablement Platform Low Level Design

Edition 1.0  |  5 October 2026  |  Proposed baseline for owner review

## Authority and implementation boundary

This LLD follows [the FSD](02-FSD.md) and [the HLD](03-HLD.md), using review commit 36073f1, build 0.30.0, schema 35 and domain API 1.21.0 as the factual reference. Current contracts below are implemented locally. Proposed interfaces are design blueprints; they are not registered HTTP routes, capability grants, SQL tables or accepted features. The branch is not deployed. The data dictionary gives field level DD-NPA references; the test package specifies verification separately from execution evidence.

Use current contracts, store and route code as the executable source. Preserve closed request schemas, tenant fences, immutable revisions, independent decisions by natural person and atomic audit/outbox/receipt semantics. The original impact ledger remains unchanged. Future code must also regenerate implemented contracts and onboarding profiles and qualify real runtime roles.

## Current HTTP operations

Every path below begins with /v1/tenants/{tenant_id}/. Tenant and object path values are UUID selectors. Read role templates are TENANT_ADMIN, MEL_ADMIN, PROGRAMME_MANAGER, AUTHOR, REVIEWER, ANALYST and DATA_STEWARD; manager and advisory requester templates are TENANT_ADMIN, MEL_ADMIN and PROGRAMME_MANAGER. These templates are candidates for grants, not proof of current authority.

| Method and suffix | Operation and response |
|---|---|
| GET ai-enablement/catalog | get_ai_enablement_catalog; 200 AIEnablementCatalog |
| POST ai-enablement/assessment | assess_ai_enablement; 200 AIEnablementAssessment |
| GET ai-enablement/solutions | get_ai_solutions; 200 AISolutionsCatalog |
| POST ai-enablement/advisory | create_ai_advisory; 200 AIAdvisoryDraft |
| GET ai-enablement/plans | list_ai_adoption_plans; 200 AIAdoptionPlanList |
| POST ai-enablement/plans | create_ai_adoption_plan; 201 AIAdoptionPlanReceipt |
| GET ai-enablement/plans/{object_id} | get_ai_adoption_plan; 200 AIAdoptionPlan |
| PUT ai-enablement/plans/{object_id} | update_ai_adoption_plan; 200 AIAdoptionPlanReceipt |

Catalogue, assessment, solutions and plan reads require ai.enablement.read. Plan writes require ai.enablement.manage and a separate current read check. Advisory requires both ai.enablement.read and ai.advisory.request. These current policy rows have purpose_required false and no action specific fresh assurance requirement; existing identity/session checks still apply. Do not add an invented current MFA gate. Target approval and disclosure policies must explicitly determine their purpose and fresh assurance requirements.

References: FR-NPA-001, FR-NPA-002, FR-NPA-004, FR-NPA-006, FR-NPA-010, FR-NPA-025, FR-NPA-033 and FR-NPA-039.

## Current input schema and validation

Profile has exactly sector, team_size, goal, data_readiness, ai_experience and sensitive_data. sector is GENERAL, EDUCATION, HEALTH, LIVELIHOODS or ENVIRONMENT. team_size is an integer from 1 to 100000 and is not a boolean. goal is a raw string at most 1000 characters whose trimmed value is nonempty. data_readiness is NONE, BASIC or STRUCTURED. ai_experience is NONE, EXPERIMENTING or REGULAR. sensitive_data is boolean and does not authorise sensitive input.

Assessment request has only profile. Advisory request has only operation_id UUID, profile and consent with the constant true. Plan create has only operation_id UUID and data. Plan update adds expected_revision UUID. The plan data members are exactly title, profile, solution_ids, learning_completed, procurement and pilot. Server owned author, state, approval, content_versions and classification cannot be supplied.

| Plan member | Exact implemented constraint |
|---|---|
| title | Nonblank string, maximum 150 characters |
| solution_ids | Unique current known IDs, zero to four values |
| learning_completed | Unique known current lesson keys; semantic maximum twelve, schema array ceiling 100 |
| procurement.requirements | Required string, may be empty, maximum 2000 characters |
| procurement.data_boundary | Required string, may be empty, maximum 2000 characters |
| procurement.budget_notes | Required string, may be empty, maximum 500 characters |
| procurement.vendor_questions | Required string, may be empty, maximum 2000 characters |
| pilot.success_measure | Required string, may be empty, maximum 1000 characters |
| pilot.completed_actions | Unique known action subset, maximum five values |

The five action values are DEFINE_GOAL, SYNTHETIC_TRIAL, HUMAN_REVIEW, TRAIN_STAFF and REVIEW_OUTCOME. Current lesson keys are foundations:0 through foundations:3, pilot_design:0 through pilot_design:3 and procurement:0 through procurement:3. Current solution IDs are chatgpt_business, claude_team, microsoft_365_copilot, google_workspace_gemini, notebooklm, deepl, canva_magic_studio and microsoft_foundry. Empty selections are valid in saved plans. The standalone catalogue helper validate_solution_ids requires one to four items, but plan save does not use that helper; do not incorrectly require a shortlist in the plan DTO.

strict_body accepts application/json, bounds the streamed body to the application 256 KiB ceiling, refuses duplicate keys at any nesting depth, refuses nonfinite JSON constants and requires a top level object. Contract validation rejects unknown members. Service semantic validation additionally requires known IDs, nonblank values and exact types. Character counts are Python string lengths, not database byte capacities. Basic syntax and UUID validation precede opening a new plan transaction; complete plan semantic validation runs after authority and replay checks and before new writes.

References: FR-NPA-001, FR-NPA-005, FR-NPA-007, FR-NPA-013, FR-NPA-021, FR-NPA-037 and FR-NPA-038.

## Current response models

AIAdoptionPlan contains object_id UUID, revision_id UUID, business_state Draft and data. Stored data has the six writable data members plus content_versions containing catalog and solutions strings. At this baseline they are nonprofit-2026-10-05.2 and nonprofit-solutions-2026-10-05.1. Every new save stamps current versions; this is not a historical catalogue API. Earlier revisions retain their old strings.

AIAdoptionPlanReceipt contains operation_id, correlation_id, object_id, revision_id, business_state Draft and saved_at. These are server produced. A repeated identical save returns the original stored outcome, including original correlation_id and saved_at. The list contains items and next_cursor, which is nullable. It has no total_rows. The current plan has no approval, archive, delete or history browsing endpoint.

AIEnablementAssessment contains assessment. Assessment members are schema_version, content_version, method DETERMINISTIC_RULES, readiness with stage and reasons, recommendations, capacity_gaps, learning_path_ids, next_steps, human_approval_needs and limitations. Recommendations carry use_case_id, priority, status, reasons, capacity_gaps and human_approval_needs. Catalog and assessment response content currently use broad object schemas rather than a completely closed field schema; all write DTOs remain closed.

AISolutionsCatalog contains content_version, checked_on, explanation, solutions and comparison_criteria. Each solution has id, name, provider, category, use_case_ids, description, deployment, commercial_model, nonprofit_offer, api_available, source_urls, verification_notes and data_review_questions. Sources contain label and url. Compare criteria have stable id, label and prompt. Values are editorial source controlled data, not live offers, verified suppliers or vendor calls.

AIAdvisoryDraft contains status DRAFT, nonblank text of at most 12000 characters, original assessment, nonempty model string of at most 200 characters and disclaimer. Current model validation does not trim whitespace. Adapter accounting fields are not returned by orchestration or persisted in a tenant usage ledger. The disclaimer states that staff must verify claims and approve decisions and that the text cannot authorise spending, disclosure or official calculations.

References: FR-NPA-004, FR-NPA-005, FR-NPA-006, FR-NPA-010, FR-NPA-018, FR-NPA-027, FR-NPA-031, FR-NPA-035 and FR-NPA-038.

## Deterministic assessment algorithm

Validate the six profile members. Set global gaps for NONE data readiness, NONE AI experience, team size below five and reported sensitivity. FOUNDATION is the readiness stage when either data readiness or experience is NONE. Otherwise reported sensitivity yields REVIEW_REQUIRED; remaining profiles yield PILOT_CANDIDATE. Reasons explicitly identify the reported limitations. None of these stages verifies ability or authorises a pilot.

Tokenise goal into lowercase English words matching [a-z]+ and collect a set. Include a use case only if its sectors contain GENERAL or the submitted sector. Count matching goal_keywords. Add case gaps for an AI assisted example without experience and data readiness below the case requirement. Add applicable sensitivity and domain expert review needs. A NON_AI case is FOUNDATION_STEP; other cases are PREREQUISITES_REQUIRED when gaps exist, then REVIEW_REQUIRED for sensitive or high sensitivity examples, otherwise PILOT_CANDIDATE.

Sort by negative keyword match count, then count of unmet case prerequisites, then stable use case ID. Assign consecutive one based priority after sorting. Return foundations learning path only for no AI experience, followed by pilot_design and procurement. The method does not persist input or call a provider. Do not present this priority as supplier quality, competence, ROI or a numeric readiness score. Preserve rule/content version tests when changing English keyword matching or stage precedence.

References: FR-NPA-002, FR-NPA-003, FR-NPA-007, FR-NPA-035 and FR-NPA-036.

## Plan persistence and transaction algorithm

AIAdoptionPlan uses object_registry and object_revision only; there is no dedicated plan projection table. Migration 0035 extends the object type CHECK while preserving every existing kind. The shared writer creates UUID object and revision IDs, sets INTERNAL classification, current principal as owner and author, revision schema_version 1.2, payload hash, predecessor and revision number. The database schema number 35, revision schema 1.2 and catalogue schema 1.0 are different version domains.

The shared audit function appends an AuditEvent and object.changed outbox event plus an outbox_delivery tracking row. Plan save inserts an operation_receipt in the same transaction. Audit and event payloads identify the object and revision; they do not copy profile or generated text. Natural person authorship is recorded by the shared writer.

```text
save plan command
  verify command shape and UUID selectors
  fingerprint = hash_data([operation_name, object_id, submitted_body])
  begin tenant transaction with transaction local tenant context
    take tenant advisory lock with seed 0
    resolve current write context
    authorise create or update with hidden refusal
    separately authorise current plan read
    take submitted operation ID advisory lock with seed 1
    read receipt by tenant actor command and operation ID
    if receipt exists
      reject different fingerprint or expired receipt
      load original outcome object under current read scope
      recheck current action on original outcome object
      return original receipt
    if updating
      load current head for update
      reject expected revision mismatch or state other than Draft
    validate all data and known identifiers
    if creating count tenant plans and refuse count at least 1000
    stamp current catalogue version strings
    write head revision and natural person authorship
    append audit outbox event and delivery tracking row
    insert succeeded receipt with seven day expiry
  commit all components or roll back all
```

The fingerprint includes the submitted expected_revision where present and does not include the later stamped catalogue metadata. Thus a content refresh cannot change an old request fingerprint. Receipt lookup key includes actor and command as well as operation ID. Return after the transaction context commits; never infer external delivery from that receipt. A stale update is not automatically retried or rebased.

References: FR-NPA-006, FR-NPA-025, FR-NPA-027, FR-NPA-033, FR-NPA-037 and FR-NPA-039.

## Scope filtered reads and cursor algorithm

GET plan first validates the object selector, resolves current context, authorises get_ai_adoption_plan with hidden refusal and loads an available AIAdoptionPlan under ai.enablement.read. Listing defaults to 50 and permits an integer limit from one through 100. It filters object_registry joined to its exact head object_revision by tenant, kind, classification not RESTRICTED, revision restriction_state AVAILABLE and visible_sql for current read grants. It orders by object_id and reads limit plus one. Subsequent pages use object_id greater than the last returned UUID.

The cursor key is a one element list containing the last object UUID. The HMAC bound context includes tenant, principal, policy epoch, subject epoch, route and sorted current grants including grant object, capability, scope, expiry and purpose. The signed payload includes key, binding, expiry and key ID. TTL is 900 seconds and maximum token length 4096. Cookie keyring grace keys may verify an older cursor; retirement can invalidate it. Forged, expired, malformed or changed visibility cursor returns INVALID_CURSOR. On refusal start a fresh authorised listing; do not return hidden counts or fall back to an unscoped read.

References: FR-NPA-006, FR-NPA-025, FR-NPA-026 and FR-NPA-039.

## Advisory persistence and algorithm

Migration 0034 creates ai_advisory_request with primary key tenant_id and request_id, unique tenant_id and object_id, foreign keys to the tenant registry and principal, a 32 byte fingerprint and reserved_at. ai_advisory_result has the same tenant/request key and foreign key to the claim, completed_at and exactly one of sealed_output or failure_reason. The only persisted failure is AI_PROVIDER_UNAVAILABLE. Both tables force tenant_fence RLS and reject UPDATE or DELETE through insert only triggers. impact_app has SELECT and INSERT only. No new broad worker or platform read grant is added.

The submitted operation ID is canonicalised to request_id. The orchestration fingerprint is SHA256 of canonical JSON of the submitted body using sorted keys, compact separators and UTF8. The metadata object has a different server generated object_id, type AIAdvisoryRequest, lifecycle Recorded and payload containing original assessment content_version and status RESERVED. The raw profile is not copied into that metadata object. Advisory replay uses these request/result tables rather than operation_receipt; it is a specialised durable request ledger, not the seven day plan receipt mechanism.

```text
create advisory command
  require exact members operation_id profile and consent true
  validate profile and canonical UUID request ID
  calculate assessment and submitted body fingerprint
  begin tenant transaction
    take tenant lock then resolve current write authority
    require catalogue read and create advisory permission
    if tenant request ID exists
      require same principal and fingerprint
      if no result return in flight conflict
      if stored failure return unavailable without new call
      unseal and return the original draft or unreadable error
    require enabled provider configuration and sealing keys
    count all tenant reservations newer than database now minus 24 hours
    refuse count at least three
    write Recorded metadata object and append claim row
    append audit and outbox
  commit reservation
  call provider with only profile and assessment outside transaction
  validate bounded draft or sanitise failure class
  begin tenant transaction
    take tenant lock and recheck both current capabilities
    find original metadata object
    seal result bound to tenant and request or store failure reason
    insert exactly one result row
    append completed or failed audit and outbox
  commit outcome and return draft or bounded failure
```

Sealing derives a 32 byte key as HMAC SHA256 of the delivery secret with the label impact-ai-advisory-sealing-v1. Associated data is impact-ai-advisory-v1:{tenant}:{request}. The shared delivery keyring handles current and grace keys and AES GCM. If a required key is retired or ciphertext is altered, replay is AI_RESULT_UNREADABLE. Key lifecycle and retained outputs require an approved retention design; do not write unseal secrets into documentation or business payloads.

An authority change between claim and result can cause the second transaction to fail, leaving a reservation with no result. A process crash after external success but before durable outcome is also unresolved. Current code has no operator recovery endpoint and makes no automatic regeneration. Because the provider interface has no qualified external idempotency contract here, exactly once generation is not claimed.

References: FR-NPA-010, FR-NPA-023, FR-NPA-025, FR-NPA-026, FR-NPA-027, FR-NPA-029 and FR-NPA-039.

## Provider adapter contract

OpenAIAdvisory.generate(profile, assessment) uses server credential and configured model, currently default gpt-5-mini. It calls https://api.openai.com/v1/responses with fixed instructions, JSON organization_brief and assessment input, store false, max_output_tokens 2048 and reasoning effort low. A flag sent to a provider is not a claim about all provider contractual retention. HTTPX connect, read, write and pool phase or inactivity timeouts are configured to 45 seconds; this does not enforce a hard overall wall-clock deadline. A strict overall deadline remains a proposed control to qualify. Redirects are disabled and no tools or automatic retry are configured.

Only a completed, nonrefused response without incomplete_details or error is accepted. Gather assistant message output_text parts, join with newlines and strip. Refuse empty output, more than 12000 characters or text containing the credential. The adapter whitelists nonnegative integer input_tokens, output_tokens and total_tokens into an internal usage object; orchestration does not persist it. HTTP errors and malformed provider responses are sanitised rather than exposed or chained with secrets.

Current attempt quota is not a monetary budget. advisory_available reflects configuration and key availability rather than a live provider check. The selected project reported exhausted API credits; no successful live generation is evidenced. All target provider tests use fakes or synthetic fixtures until an explicitly authorised funded qualification is arranged. Do not make additional chargeable calls to prepare documents.

References: FR-NPA-010, FR-NPA-023, FR-NPA-026 and FR-NPA-029.

## Current error contract and safe client actions

The envelope has code, message, retryable, correlation_id and permitted_actions with optional field_errors and reason_code. Current global handling sets retryable true for status 503; this is not instruction to repeat a possibly completed external effect with a new ID. Prefer the operation specific safe action below.

| Code and status | Meaning and safe action |
|---|---|
| VALIDATION_FAILED 400 | Malformed object, duplicate key or invalid JSON; correct input |
| VALIDATION_FAILED 415 | Unsupported content type; submit application/json |
| VALIDATION_FAILED 422 | Contract or semantic validation, including AI_PROFILE_INVALID and AI_ADOPTION_PLAN_INVALID; retain edits and correct fields |
| LIMIT_EXCEEDED 413 | Streamed application request exceeds body ceiling; reduce input |
| AUTH_REQUIRED 401 | Identity or reauthentication unavailable; sign in again |
| RESOURCE_UNAVAILABLE 404 | Missing or hidden tenant/object/action; disclose no existence detail |
| POLICY_DENIED 403 | Action, purpose or scope denied where not hidden; review current access |
| CONFLICT_VERSION 409 | Expected plan revision stale or database conflict; retain edits and review current head |
| CONFLICT_OPERATION 409 | Changed payload under operation ID; reconcile original attempt |
| IDEMPOTENCY_EXPIRED 409 | Plan receipt past its seven day validity; verify outcome before any new operation |
| STATE_TRANSITION_DENIED 409 | Existing plan is not Draft; do not overwrite |
| INVALID_CURSOR 400 | Signature, TTL, shape or context changed; restart listing |
| LIMIT_EXCEEDED 429 | AI_ADOPTION_PLAN_LIMIT or AI_DAILY_LIMIT; inspect capacity or wait for quota window |
| SERVICE_UNAVAILABLE 503 | Bounded dependency failure; follow exact replay or investigation rules |

Advisory conflict reasons are AI_OPERATION_CHANGED for a different principal or fingerprint and AI_REQUEST_IN_FLIGHT for an unresolved claim. Advisory unavailable reasons are AI_NOT_CONFIGURED, AI_PROVIDER_UNAVAILABLE and AI_RESULT_UNREADABLE. Invalid consent is AI_CONSENT_REQUIRED and invalid advisory operation ID is AI_OPERATION_INVALID under VALIDATION_FAILED. A database unavailable class may be DATABASE_UNAVAILABLE. Do not fabricate a precise credit reason in the API: actual provider credit exhaustion is sanitised to unavailable and requires operational evidence.

References: FR-NPA-006, FR-NPA-010, FR-NPA-023, FR-NPA-025, FR-NPA-029, FR-NPA-037 and FR-NPA-039.

## Browser state and accessible recovery

Use separate state for current editable draft, captured pending save, saved snapshot and exact object/revision head. On save, freeze submitted body and operation ID. If response is ambiguous, keep the captured pending request and offer Retry previous save. Reuse that captured payload; newer edits stay separate. A success updates head and saved snapshot for the captured version and leaves changed current fields unsaved. A stale head clears the pending command and retains edits with a visible conflict message. Do not automatically overwrite or rebase.

A tenant or workspace epoch invalidates old responses and aborts outstanding requests. Ignore a completed response belonging to an earlier epoch. Opening a saved plan must not silently replace a draft edited while the load was pending. Discard uses the shared Dialog with keyboard and focus handling. Disabled AI must cause zero advisory POSTs; read only actors may view lessons and plans but cannot save or record completion. Comparison is limited to four and links only use HTTPS with noopener noreferrer.

Use labelled fields, grouped radios/checkboxes, visible focus, programmatic status and recoverable errors. Automated zero serious/critical findings are bounded evidence; manual contrast, screen reader, focus/error announcement, zoom and incomplete scan items remain qualification work. Languages and translation workflow await DEC-NPA-001.

References: FR-NPA-005, FR-NPA-006, FR-NPA-007, FR-NPA-028 and FR-NPA-029.

## Proposed logical entities and common command skeleton

The target entity vocabulary is LearningProgramme, Cohort, LearningAssignment, CompetencyAssessment, HumanAdvisoryCase, TaskTemplate, TaskRun, ProcurementRequest, SupplierQuote, CostLine, CostComparison, ProcurementDecision, SupplierSubmission, PublishedSupplierSnapshot, Engagement, DeliveryMilestone, ConnectorBinding, AdoptionOutcome, SupportCase and FeedbackRecord. These are not new SQL tables yet. [The data dictionary](08-DATA-DICTIONARY.md) labels proposed fields and policy dependencies. Purchase and PaymentAttempt remain conditional R3 placeholders.

Every target command should have closed operation_id, expected_revision when mutating existing work, and exact typed data. Tenant, author, state, reviewer, timestamps, grant epochs and content versions are server owned. Implement registry kind extensions in the next contiguous additive migration, currently 0036 if no other slice adds one first. Use tenant_id in every new primary/foreign key, ENABLE and FORCE RLS and narrow grants. Do not edit migrations 0001 through 0035.

```text
proposed governed decision
  validate closed command and syntax without persistence
  begin tenant transaction
    take tenant lock then resolve current authority
    require separate action and read capabilities and approved purpose
    take operation lock and check authorised exact replay
    load candidate and all referenced exact revisions under current scope
    refuse stale expected head or changed referenced evidence
    require permitted lifecycle transition
    require current assurance where approved policy says so
    resolve natural person and material author set
    refuse self approval or declared policy conflict
    append decision revision and immutable binding register
    append audit outbox and receipt in the same transaction
  commit before any external adapter call
```

This skeleton extends existing semantics; it cannot be registered until role mapping and reviewed delegation ceilings are designed. A new grant name is not enough to allow an existing tenant to use it. No target capability names or URL routes in this edition are claimed as current.

References: FR-NPA-008, FR-NPA-009, FR-NPA-011, FR-NPA-012, FR-NPA-014, FR-NPA-016, FR-NPA-017, FR-NPA-019, FR-NPA-022, FR-NPA-025, FR-NPA-027, FR-NPA-033 and FR-NPA-035.

## Proposed learning and advisory interfaces

Define LearningOperations.assign using programme_revision, cohort reference, eligible learner reference, rubric_revision, due_at and visibility policy. Verify each tenant reference and avoid learner count leakage. LearningOperations.submitAssessment accepts expected assignment revision and exact evidence revisions. LearningOperations.assess accepts expected submitted revision, rubric results, decision and remediation; assessor authority and independence follow DEC-NPA-008. Programme reordering cannot reinterpret historical lesson progress or rubric evidence.

Define HumanAdvice.openCase using bounded problem, allowed data boundary and desired outcome. HumanAdvice.assign pins adviser identity, declared conflict and exact scope. External adviser membership or case specific disclosure must be governed explicitly; no global read is implied. HumanAdvice.close pins final advice revision, acknowledged actions and closure evidence. Editing advice does not award procurement or authorise protected disclosure.

Define TaskWorkbench.reserveRun with published template_revision, exact permitted input references or bounded supplied data, consent and approved budget policy reference. Template input schema, provider destination, output checks and reviewer are immutable within a run. Model text is untrusted output and cannot supply tool calls with consequential authority. A review action pins DraftResult but cannot substitute for a separate disclosure or financial decision.

References: FR-NPA-008, FR-NPA-009, FR-NPA-011, FR-NPA-012, FR-NPA-026, FR-NPA-031, FR-NPA-035 and FR-NPA-038.

## Proposed procurement costing and supplier interfaces

Define Procurement.prepareRequest with source_plan_revision, exact brief fields, named recipients and disclosure policy reference. Procurement.reviewRequest pins candidate and audience; changing either requires a new review. Procurement.issueRequest commits an immutable issuance binding and delivery intent, then a bounded adapter works outside the transaction. Outcome records actual accepted delivery evidence or an unresolved/failed state. The draft never sends automatically.

Define Procurement.recordQuote with request_revision, responding supplier reference, offer_revision, currency, validity, inclusions, exclusions and exact evidence. Validation records provenance and does not infer vendor eligibility from the directory. Procurement.compareCosts pins exact quote revisions, period and assumptions. Each CostLine has category, quantity, unit, amount or explicit unknown, currency, period and source. Compute using Decimal with at least 50 digit intermediate precision; store amounts consistently with NUMERIC(38,12), transport decimal strings and round half up only at display. Do not sum unlike currencies. Missing required cost makes completeness INCOMPLETE and complete_total unavailable, not zero; currency conversion requires an approved sourced rule.

Define Procurement.submitDecision with comparison_revision, selected offer_revision, rationale, conflicts and policy_revision. Procurement.approveDecision checks all material natural person authors, current authority, assurance, exact still valid evidence and approved monetary thresholds. Immutable approval binds exact quotes and comparison. It creates no charge; Purchase is a conditional separate financial operation.

Define Marketplace.submitSupplier with attributable claims and bounded private evidence. Marketplace.reviewSupplier pins candidate, verification scope, sources, expiry, commercial relationships and allowed public fields. Marketplace.publishSupplier creates a separately reviewed minimised PublishedSupplierSnapshot. Global read never joins private submissions or exposes supplier contact/evidence by default. Withdraw or expiry leaves the previous published snapshot attributable and unavailable for a new decision, rather than overwriting its meaning. Placement policy awaits DEC-NPA-004.

References: FR-NPA-004, FR-NPA-005, FR-NPA-014, FR-NPA-015, FR-NPA-016, FR-NPA-017, FR-NPA-018, FR-NPA-020, FR-NPA-025 and FR-NPA-035.

## Proposed engagements connectors and usage ledger

Define Delivery.offerEngagement using exact scope/terms revisions, parties, milestones, evidence requirements and cancellation policy. Acceptance records proof from the addressed party and fixes agreed revisions. Delivery.submitMilestone pins deliverable and test evidence; Delivery.acceptMilestone requires an independent accepting natural person. Returned work creates a revision for remediation. A pending outbox message cannot prove acceptance or delivery.

Define Connectors.reviewBinding with provider, approved destination, minimal scope set, secret reference, data classes and synthetic trial evidence. Secret values stay in a server secret store and never in the registry payload, browser or audit. Connectors.activate requires current approved revision and trial checks. Pause or revoke prevents new claims and invalidates running work by a version or generation fence. Any already disclosed external bytes need a realistic exit process; revocation does not recall them.

Target UsageGovernance.reserve checks approved tenant budget policy and remaining allowance under the tenant lock before external work, records an immutable reservation and binds it to exact input/template/provider configuration. Calls remain outside the transaction. UsageGovernance.recordOutcome records bounded observed usage, provider evidence and deterministic cost assumptions; reconcile rather than erase reservations. A timeout without proven final outcome is OutcomeUnknown. Never release its funds and start a second call merely because a client retries. Proposed monetary budget period, rate source and overrun policy require DEC-NPA-011; the current three attempt quota remains its actual implementation.

References: FR-NPA-019, FR-NPA-021, FR-NPA-022, FR-NPA-023, FR-NPA-027, FR-NPA-029 and FR-NPA-035.

## Proposed outcomes support feedback and lifecycle

Define Outcomes.record with comparable task definition, baseline period, follow up period, observed staff time, human review and support effort, quality criteria and exact evidence. Use explicit units and incomplete states, not generated savings. Link official measures only through existing governed definition and snapshot revisions. The approved interpretation states uncertainty and never asserts causal proof from a checklist.

Define Support.openCase with minimal task reference, severity, bounded reason and authorised evidence. Support.triage identifies owner, approved response expectation and restricted participants. Incident pause names exact connector or pilot revision; resumption requires accountable review. Define Feedback.record as optional minimised usefulness or quality feedback with consent and sharing scope; it cannot silently retrain rules or a model on tenant records.

Define Portability.requestExport with separately permitted exact scope and versions, intended recipient, expiry and policy reference. A job prepares a versioned package outside the decision transaction and records a generation fenced immutable artifact. Download rechecks current export/disclosure scope and logs access. Include schema, catalogue versions, object/revision provenance and unknown content availability; exclude restricted or secret fields and hidden totals. Downloaded bytes cannot be recalled.

Retention design inventories ordinary revisions, sealed outputs, evidence, jobs, exports, cached/public snapshots and backups. Current advisory triggers prevent app removal and existing member privacy actions do not provide general AI text erasure. Any controlled removal or redaction needs a reviewed additive migration and narrow privacy role procedure with retained audit; never grant ordinary app DELETE as a shortcut. Restore must replay deletions and revocations before tenant access resumes. DEC-NPA-009 determines policy and holds; no retention durations are invented.

References: FR-NPA-024, FR-NPA-026, FR-NPA-030, FR-NPA-032, FR-NPA-034 and FR-NPA-035.

## Conditional finance and unresolved contracts

DEC-NPA-015 must settle operator responsibility, payment model, provider, approval, settlement, reconciliation, refund and dispute ownership before Purchase and PaymentAttempt schemas are implementable. The eventual design requires external idempotency tied to approved amount/currency/payee and exact authorising decision, verified event signatures and replay prevention, a deterministic reconciliation ledger and OutcomeUnknown investigation. No card or bank fields, accounting treatment, financial threshold, fee rate or actual provider integration is finalised here.

Unresolved design work also includes reviewed ceiling widening for active tenants, retained content snapshots, competency standard, marketplace operator, adviser case access, class retention, service levels, provider monetary budget and connector scopes. The decision register controls these choices. Every target interface needs exact field bounds and error codes in an approved slice before generating an implemented OpenAPI contract. Logical method names above organise design only and must not appear in the current route inventory.

References: FR-NPA-016, FR-NPA-018, FR-NPA-020, FR-NPA-022, FR-NPA-023, FR-NPA-030, FR-NPA-031 and FR-NPA-033.

## Requirement implementation index

The principal section below complements the references inside each design section. A current section may also identify a proposed gap; the index does not make a target interface implemented.

| Requirement | Principal design section |
|---|---|
| FR-NPA-001 | Current input schema and validation |
| FR-NPA-002 | Deterministic assessment algorithm |
| FR-NPA-003 | Deterministic assessment algorithm |
| FR-NPA-004 | Current response models |
| FR-NPA-005 | Current input schema and validation |
| FR-NPA-006 | Plan persistence and transaction algorithm |
| FR-NPA-007 | Browser state and accessible recovery |
| FR-NPA-008 | Proposed learning and advisory interfaces |
| FR-NPA-009 | Proposed learning and advisory interfaces |
| FR-NPA-010 | Advisory persistence and algorithm |
| FR-NPA-011 | Proposed learning and advisory interfaces |
| FR-NPA-012 | Proposed learning and advisory interfaces |
| FR-NPA-013 | Current input schema and validation |
| FR-NPA-014 | Proposed procurement costing and supplier interfaces |
| FR-NPA-015 | Proposed procurement costing and supplier interfaces |
| FR-NPA-016 | Proposed procurement costing and supplier interfaces |
| FR-NPA-017 | Proposed procurement costing and supplier interfaces |
| FR-NPA-018 | Proposed procurement costing and supplier interfaces |
| FR-NPA-019 | Proposed engagements connectors and usage ledger |
| FR-NPA-020 | Conditional finance and unresolved contracts |
| FR-NPA-021 | Proposed engagements connectors and usage ledger |
| FR-NPA-022 | Proposed engagements connectors and usage ledger |
| FR-NPA-023 | Provider adapter contract |
| FR-NPA-024 | Proposed outcomes support feedback and lifecycle |
| FR-NPA-025 | Scope filtered reads and cursor algorithm |
| FR-NPA-026 | Proposed outcomes support feedback and lifecycle |
| FR-NPA-027 | Plan persistence and transaction algorithm |
| FR-NPA-028 | Browser state and accessible recovery |
| FR-NPA-029 | Current error contract and safe client actions |
| FR-NPA-030 | Proposed outcomes support feedback and lifecycle |
| FR-NPA-031 | Current response models |
| FR-NPA-032 | Proposed outcomes support feedback and lifecycle |
| FR-NPA-033 | Proposed logical entities and common command skeleton |
| FR-NPA-034 | Proposed outcomes support feedback and lifecycle |
| FR-NPA-035 | Proposed logical entities and common command skeleton |
| FR-NPA-036 | Verification hooks and source evidence |
| FR-NPA-037 | Current input schema and validation |
| FR-NPA-038 | Current input schema and validation |
| FR-NPA-039 | Plan persistence and transaction algorithm |
| FR-NPA-040 | Verification hooks and source evidence |

## Verification hooks and source evidence

Current unit tests cover deterministic assessment, source catalogue, lesson isolation, plan validation and provider parsing. Current live application tests cover tenant scope, read/manage split, exact save replay, changed input conflict, stale head, validation, quota, sealed advisory replay and bounded failures. Browser evidence covers directory, assessment, comparison, lessons, save/reload, lost response replay, stale conflict, read only access and disabled generation with mobile and automated accessibility checks. Prior Mercy Corps arithmetic/calendar cases preserve pooled ratios, zero and period edge behaviour; no Django runtime is imported.

The exact local record is 1101 passing cases, seven unchanged Mac operations failures, 76 skipped and one deselected, and ten browser scenarios. Use docs/evidence/nonprofit-ai-adoption-local-suite.xml, nonprofit-ai-adoption-local-summary.json and ai-enablement-browser-tests.json. This does not establish native concurrent request behaviour or hosted identity/container qualification. Do not label specified target tests as run.

Before release qualify current and new claim/register tables under real unprivileged PostgreSQL roles, race duplicate requests and revocation against outcomes, test API restart, populated schema upgrade and restore, verify exact contract/profile generation and run all four hosted jobs on the candidate. Owner confirmation precedes merge and observed post deployment smoke follows it. No main merge, provider spending or external send is authorised by this documentation.

Implementation sources are ai_adoption_plans.py, ai_adoption_contracts.py, ai_enablement.py, ai_enablement_contracts.py, ai_enablement_catalog.py, ai_solutions_catalog.py, ai_learning_content.py, ai_advisory_provider.py, main.py, store.py and service.py under apps/api/impact_api, the two AI product React screens, migrations 0034/0035 and VERSION.json. Reference original impact security and arithmetic rules when extending the adapter or decision flows.

References: FR-NPA-028, FR-NPA-033, FR-NPA-036 and FR-NPA-040.
