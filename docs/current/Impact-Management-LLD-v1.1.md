# Impact Management Platform
Low Level Design

Version 1.1 | 27 September 2026 | Proposed engineering baseline

This document specifies the implementation structure, transaction rules, data contracts and failure handling for the Impact Management Platform. It is intended for engineers building the API, database, workers, web client and Android client, and for reviewers checking that the implementation preserves the FSD. The executable reference suite illustrates deterministic rules; it is not a production implementation or proof of deployed security.

The FSD is authoritative for behaviour and release assignment. The HLD chooses the component boundaries and reference infrastructure. This LLD makes those choices concrete. The engineering archive contains openapi.json, entity-catalogue.json, postgresql-blueprint.sql, fixtures, tests and supporting operational contracts. The database file is a design blueprint that has not been applied to a PostgreSQL instance. Nested API structures marked as open objects require closed, generated DTO schemas before the implementation contract is frozen.

## Contents

1 Repository and module structure

2 Request context and transaction pipeline

3 Canonical types and limits

4 Storage model and physical conventions

5 Entity and invariant catalogue

6 Keys indexes and query paths

7 Identity sessions invitations and custody

8 Policy evaluation and revocation

9 HTTP and error contracts

10 Lifecycle implementation

11 Idempotency canonicalisation and audit atomicity

12 Review and period close algorithms

13 Deterministic calculation algorithms

14 Ingestion row processing and replacement

15 Form grammar and submission validation

16 Offline persistence and sync protocol

17 Evidence evaluation and analytical finance

18 Dashboards reports and disclosure

19 AI orchestration and confirmation

20 Jobs leases notifications and webhooks

21 Audit privacy and restore mechanics

22 Web interactions and accessibility

23 Security implementation controls

24 Release migrations and operations

25 Testing and implementation completion

26 Supporting entity invariants

27 References

## Release interpretation

Documentation edition 1.1 is reconciled with application build 0.12.0 on 27 September 2026. The document edition and application build use different version sequences. The original business requirements and their acceptance conditions remain authoritative. No requirement has been removed or weakened to match the current code.

The application is a development delivery. The requirement ledger records 74 PARTIAL and 233 PENDING requirements, with zero fully accepted. PARTIAL means a bounded implementation and some evidence exist, not that all acceptance conditions are satisfied. PENDING means the requirement has no accepted implementation coverage in the ledger; a read-only surface or reference example does not establish delivery.

Recorded qualification contains 325 application checks, 143 design-reference checks and 81 browser checks. One expired-offline-grant test is deselected and is not a pass. Local integration uses fresh in-memory PGlite PostgreSQL 17.5 with serialized transactions. Native PostgreSQL concurrency, live identity-provider assurance, disaster recovery, load qualification and production acceptance remain open.

The original BRD and FSD use R1, R2 and R3 requirement assignments. The later 16-stage delivery roadmap is an implementation sequence. Roadmap stage 1 and baseline R1 are different groupings; neither is complete. Requirement release assignments remain unchanged.

The sections explicitly marked current implementation describe this build. Retained target-design sections describe required future behavior unless the current implementation section states otherwise. Complete source, contracts, test evidence and original documents accompany this edition. Start at DOCUMENTATION-INDEX.md and TRACEABILITY.csv for exact locations and evidence boundaries.

## Current code and persistence map

The application lives in apps/api/impact_api and apps/web/src. Python modules expose explicit commands rather than generic workflow-state patches. SQL migrations 0001 through 0015 are applied in order and checksum-checked. Source paths, implemented API operations and database definitions are indexed in CURRENT-API-INVENTORY.md, CURRENT-DATA-DICTIONARY.md and TRACEABILITY.csv.

store.py owns transaction-local tenant and role context, scopes, immutable revision storage and receipts. administration.py and workspace_contracts.py enforce reviewed grants, groups and roles. measurement.py and service.py implement configuration and domain commands; period_governance.py reconciles close and restatement; reporting.py freezes reports and publications; work.py creates invalidations and resolves recalculation tasks. main.py wires transport and the runtime manifest.

## Recovery contact transaction

tenant_recovery_contact stores contact and revision identifiers, tenant and owner pins, nominee identity and masked verified-email evidence, replacement pins, authentication and verification times, approval attribution, contact and review expiry, reason and state. Partial unique indexes allow one Active and one pending Nominated or Verified record per tenant. The platform role can select, insert and update; application and identity roles cannot read the table, and runtime deletion is not granted.

Nomination requires the current owner, fresh assurance, an existing verified account for a different natural person and bounded expiry. The mutation takes the tenant lock, rechecks current authority and authentication cutoff, validates the tenant and replacement revisions, then commits the row, event and seven-day operation receipt. Exact replay rechecks current authority before returning the original result.

Verify is restricted to the exact nominee. Approve requires an operator independent of both owner and nominee, current pins, a verification no older than 24 hours, and both unexpired deadlines. The identity-lock function takes ordered share locks with a fixed search path and no PUBLIC execution. Global account revocation takes a conflicting lock. Approval marks an old Active row Replaced and a verified new row Active in one transaction. An injected failure proves rollback of both state changes and evidence.

Eligibility is derived at read time from current custody, nominee verified identity and channel hash, nominee authentication cutoff and expiry. Stored Active is not equivalent to eligible. Current owners may repair expired proof while a tenant is Suspended. Contact management grants no principal, membership, business permission or recovery power.

## Current limits and client behavior

Domain operation receipts last seven days. Cursors for ordinary domain lists are signed, scoped and expire after 15 minutes. The control-plane directory uses its separately specified UUID cursor with 50-row pages. Request bodies are bounded to 256 KiB and calculation input sets to 10000. The configuration UI follows pages up to its explicit 500-record cap; older selectors still have smaller limits.

The React settings page initializes the first permitted section after capabilities arrive, while preserving a valid user selection. Tenant switching cancels stale data loads. Forms retain an operation identifier for an exact retry and use expected revisions; changed command content requires a new operation identifier. Server checks remain authoritative regardless of visible buttons.

The remaining low-level designs below specify required future capabilities, not completed implementations. The open nested-schema and multipart gaps from the original edition are governed by the accompanying revised API and migration specifications; current implemented schemas are closed.

## Retained requirements and target design

The following baseline sections retain their requirement IDs and intended behavior. Implementation status is governed by the current profile above and the accompanying traceability register. Planned components are not represented as deployed services.

## 1 Repository and module structure

Use a single repository initially with applications web, api, workers and android; packages domain, contracts, policies and testkit; and infrastructure, migrations and qualification directories. A domain module contains entities, value objects, commands, queries, policies, repositories and events. Transport DTOs stay outside domain entities. The composition root constructs dependencies; domain code imports no HTTP framework, cloud SDK or model provider.

| Component | Owned function | Package |
| --- | --- | --- |
| C01 Identity | IAM · identity broker and sessions | core.identity |
| C02 Tenant and access | TEN ACC SEC · membership, policy, support | core.access |
| C03 Planning | PLN PRG · programme, framework, work and risks | core.planning |
| C04 Measurement | IND CAL · definitions, periods, targets, deterministic results | core.measurement |
| C05 Collection | FRM OFF PAR · forms, assignments, participants, sync | core.collection |
| C06 Data and quality | DAT DQ MIG · ingestion, lineage, quality and migration | core.data |
| C07 Evidence and evaluation | EVD EVA · files, verification, qualitative findings | core.evidence |
| C08 Workflow | WFL · decisions, close, collaboration and notifications | core.workflow |
| C09 Reporting | ANA RPT · dashboards, snapshots, reports and delivery | core.reporting |
| C10 Finance | FIN · analytical funding, budgets, rates, allocations | core.finance |
| C11 Integrations | INT · source adapters, checkpoints and external delivery | workers.connectors |
| C12 AI | AI · scoped retrieval, typed proposals and evaluation | workers.ai |
| C13 Privacy | PRV · purpose, retention, holds and deletion | core.privacy |
| C14 Operations | OPS · entitlements, jobs, diagnostics, custody and exit | core.operations |
| C15 Web | UX · accessible browser application | web |
| C16 Android | OFF UX · qualified local collection and synchronisation | field.android |

Ports include IdentityResolver, PolicyEvaluator, RevisionRepository, TransactionManager, AuditWriter, OutboxWriter, BlobStore, Clock, IdGenerator, CalculationRunner, ConnectorAdapter and ModelGateway. Production adapters implement these ports; deterministic tests replace only the boundary being isolated. Database integration tests use real PostgreSQL and the actual runtime role. SQLite or an in-memory repository cannot establish row-level security, locking or numeric behaviour.

Module boundaries are enforced by import checks and repository ownership tests. Shared code contains value types and contracts, not an unowned collection of business rules. Configuration supplies policies, labels and limits through versioned records. Avoid tenant-specific branches in source code for ordinary configuration requirements.

## 2 Request context and transaction pipeline

RequestContext contains authenticated identity ID, verified natural-person identity where required, effective actor, tenant ID, membership ID, capability request, scope references, purpose, assurance time, session or service credential ID, subject epoch, policy epoch, request timestamp and correlation ID. It contains no raw password, token or unfiltered model conversation. The server derives the actor fields. An offline payload may name an original author only as a claim validated against the signed device grant and assignment.

The command handler follows this order: resolve identity and tenant; validate the closed DTO and request size; evaluate coarse access; start a transaction; set transaction-local tenant context; acquire locks in the prescribed order; verify fresh authority and operation identity; load the current object heads; check expected revisions; validate domain and lifecycle rules; write revisions and projections; append audit and outbox records; persist the receipt; commit; then return the receipt. If an identical completed operation exists, return that receipt before rejecting its now-old expected revision, after rechecking present access to the outcome.

The lock order is tenant policy row, subject epoch row, operation receipt, affected object heads in UUID order, then workflow or job state. A handler must not reverse that order in a nested module call. Retry deadlock or serialization failures at most three times with bounded jitter under the same logical operation ID. Do not automatically retry a semantic version conflict, rejected approval or non-idempotent external effect.

Runtime connections use a nonowner NOBYPASSRLS role. Each transaction executes parameterised SET LOCAL context before touching tenant tables. Missing context denies tenant access. Pool release resets or discards any connection with uncertain state. The platform never exposes arbitrary SQL to users; a mutable database session setting is not an independent security boundary against a party allowed to issue unrestricted SQL.

## 3 Canonical types and limits

Object, revision, event, operation and job IDs are opaque UUIDs. Times use timezone-aware RFC3339 in UTC, with relevant source and reporting zone retained separately. Intervals include start and exclude end. Stable source IDs, national reference strings and codes remain text; leading zeros must survive import and export. Human labels can use a separate search-normalised representation without altering stored stable codes.

Input decimals are strings matching a sign, up to 26 integral digits and at most 12 fractional digits. Reject binary floats, exponent notation, NaN, infinity, overprecision and overflow. Store NUMERIC(38,12). Use at least 50 digits of intermediate precision, with a 60-digit local context in the reference implementation. Apply explicit storage quantisation only at the documented result boundary and display half-up rounding at zero to six places. Never sum already displayed values to derive an official total.

Text limits count Unicode scalar values: codes 64, titles 200, ordinary descriptions 2000, comments 5000 and designated narratives 20000. Reject unpaired surrogates and invalid encodings; do not measure UTF16 code units or byte length as character length. Transport byte limits apply separately. Rich text is sanitised with a qualified allowlist. Export protection against spreadsheet formulas preserves original source text in documented safe encoding.

ValueState is PRESENT, MISSING, NOT_COLLECTED, NOT_APPLICABLE, INVALID or UNDEFINED. PRESENT requires a valid numeric value, including zero. Every other numeric state requires no value and a suitable reason where specified. Approval, freshness, completeness and suppression are separate fields. An unauthorised disclosure response must omit the suppressed raw value entirely, including metadata or hidden chart payloads.

## 4 Storage model and physical conventions

tenant_root identifies the tenant and its region/lifecycle policy. auth_identity is a restricted global identity table keyed by issuer and provider subject; it does not contain unrestricted tenant content. object_registry uses the composite primary key tenant_id and object_id. object_revision uses tenant_id, object_id and revision_id, with a unique tenant/revision pair for immutable references. Deferred constraints allow registry head and first revision to be inserted in one transaction.

The current domain table contains typed frequently queried fields and the current revision reference. Immutable payloads are canonical JSON with schema version and digest. A projection update and registry head change occur in one transaction. All tenant-owned tables and direct observation partitions enable and force RLS. The runtime has no direct partition privileges, ownership, CREATE or TRUNCATE permission. Migration and privacy executor roles are separate from the runtime and audited.

Use composite foreign keys for tenant-owned relationships. Classify every UUID field as a global identity reference, tenant object reference or immutable revision reference; they are not interchangeable. A programme reference must point to a programme, not simply any valid registry UUID. Typed repositories enforce the object kind and lifecycle; production migrations add concrete foreign keys and checks for the resolved storage layout. The supplied blueprint highlights fields still requiring that migration classification and must not be treated as a ready production migration.

Observation data is proposed to use 32 hash partitions by tenant ID. This spreads indexes without assuming each tenant needs a physical table. Retention and performance qualification must consider tenant skew, vacuum, index maintenance and partition pruning. Change this partition count only through a measured migration plan. Immutable revisions may dominate storage and require separate retention and indexing decisions.

## 5 Entity and invariant catalogue

The first 37 entities implement D01–D37 exactly. Common envelope fields are object ID, tenant ID, revision ID, schema version, lifecycle, classification, owner, policy/retention reference, creation actor/time and update actor/time. DTOs split editable draft data from server-owned metadata. The following table gives the governing fields and invariants; the machine-readable catalogue and OpenAPI provide the proposed route and typed storage mapping.

| Record | Required data | Invariant |
| --- | --- | --- |
| D01 Tenant | Legal or operating name, owner membership, reporting zone, hosting policy, privacy policy, lifecycle | Activation requires retention, region, identity recovery and administrator readiness |
| D02 Membership | Identity, tenant, status, authority source, joined or invited time | Expiry mandatory for external roles; suspended identity retains attribution |
| D03 Grant | Subject, capability, scope, issuer, start, expiry policy | Sensitive purpose and independent approval where policy requires; no wildcard by omission |
| D04 Organisation unit | Code, name, parent or root, owner | Reporting hierarchy and access scope are separate; cycles prohibited |
| D05 Programme | Code, title, programme type, start, end, owner, reporting calendar, geography reference | End is not before start; activation requires measurement completeness |
| D06 Framework version | Programme, version, nodes, relationships, owner, status | Each node has stable ID, type, title and definition; structural cycles rejected where hierarchy applies |
| D07 Indicator definition | Code, name, measurement type, unit, population, inclusion, exclusion, method, source mode, time semantic, owner | Ratios need numerator and denominator meanings; aggregation needs combination rule and comparability contract |
| D08 Indicator instance | Definition version, programme, local applicability, collector, reviewer, reporting schedule | Local overrides explicit; parent version remains immutable |
| D09 Target | Indicator version, period or date, target kind, value state, direction, approval status | Range has low and high; baseline and target units match; original and revised are separate |
| D10 Dimension version | Code, label, categories, exclusivity, exhaustiveness, effective date | Unknown and declined codes distinct; category crosswalks reference both versions |
| D11 Reporting period | Calendar version, code, start instant, exclusive end, reporting zone, status | No unintended overlap within one series; custom overlapping analyses do not duplicate official membership |
| D12 Observation | Source business key, indicator or dataset binding, event time, collection time, value state, source version, approval state | Numeric value required only when present; numerator and denominator retained where applicable |
| D13 Calculated result | Indicator version, period, dimensions, rule version, input snapshot, run ID, result state, coverage | Read only numeric result; lineage includes included and excluded source identities |
| D14 Form version | Code, fields, logic, language versions, owner, lifecycle | Field IDs immutable within lineage; published form locked; destructive change creates version |
| D15 Form field | Stable code, type, label, classification, required or relevance rule | Choices use code list; bounds typed; repeat child has parent definition; no circular calculation |
| D16 Collection assignment | Round, form version, assignee, site or eligible subject scope, due time, status | Replacement and reassignment preserve original task identity and history |
| D17 Submission | Submission ID, form version, assignment if required, respondent scope, answers, device author, event time | Revision and server receipt separate; required media completeness explicit |
| D18 Participant | Programme pseudonym, entity type, purpose, active status | Direct identifiers optional and separately restricted; aggregate-only programmes omit registry entirely |
| D19 Relationship or service event | Related entity IDs, relationship or event code, effective or event date, source | Household membership has start and optional end; one event identity prevents repeated attendance imports |
| D20 Consent or handling record | Subject, notice version, purpose, handling basis, language, recorded time, recorder, scope | Consent only where applicable; withdrawal scope and effective time explicit |
| D21 Dataset version | Name, purpose, owner, source, schema version, classification, retention, refresh contract | Raw receipt immutable; derived dataset records transformation and parent versions |
| D22 Import job | Source identity, mapping version, mode, key policy, submitter, operation ID, state | Row outcome counts reconcile; controlled replacement requires impact preview |
| D23 Quality issue | Rule version, affected object and revision, severity, owner, status, detected time | Exception needs authority, reason, scope and expiry; dismissal is not correction |
| D24 Evidence version | File or external reference, source, owner, date, type, integrity reference, classification, verification state | Scan status, provenance and publication consent are separate fields |
| D25 Workflow instance | Object and version, workflow version, stages, candidate reviewers, status | Decisions immutable; current authority and independence checked at each stage |
| D26 Decision | Actor, capacity, candidate version, action, time, reason, evidence references | No decision fabricated for imported historic records; delegated actor recorded |
| D27 Snapshot | Scope, period, definition set, target set, approved result set, evidence set, policy context, lock time | Immutable manifest; deletion restrictions can withhold content without rewriting original arithmetic |
| D28 Report version | Template version, snapshot, language, audience class, sections, owner, status | Official numeric fields bind to result references; approved version immutable |
| D29 Disclosure | Artifact version, recipients or public audience, purpose, policy review, expiry, owner | Public cells and privacy transformations fixed at approval; download rights explicit |
| D30 Funding or budget line | Agreement, project, category, period, amount, currency, version, owner | Rate reference for conversion; actual expenditure has independent source transaction key |
| D31 Connection | Type, authorised object scope, owner, credential reference, mapping, schedule, state | Secret value not readable after entry; credential expiry and upstream permission health visible |
| D32 AI task and proposal | Use case, requester, tenant, permitted sources, configuration version, state, budget context | Applied proposal has exact diff, source revisions, confirming actor and domain command receipts |
| D33 Privacy case | Verified requester reference, request type, affected scope, handling authority, deadline, case status | Identity verification evidence restricted; holds and external actions tracked separately |
| D34 Audit event | Tenant, real actor, effective actor if delegated, action, object reference, outcome, time, correlation | No secrets or unnecessary payload; restricted read events record category rather than values |
| D35 Evaluation and finding | Questions, programme baseline, methods, study period, evaluator, evidence, limitations | Causal claim requires reviewed methodology; contradictory evidence references retained |
| D36 Retention and hold | Data class, purpose, trigger, duration, expiry action, policy owner | Hold has authority, reason, covered objects, review date and release decision |
| D37 Subscription and entitlement | Plan reference, commercial status, effective dates, authorised limits, billing contact | Independent of data permissions and tenant deletion state |

Membership status and joined time, grant issuer, observation approval state, evidence scan/verification results, handling recorder/time and subscription commercial status are server-owned output fields. Generic create or patch payloads reject them as unknown fields. An invitation, approved grant request, workflow decision, scanner result or commercial administration command changes them through its own policy and state machine. Merely setting readOnly in a shared schema is insufficient; the input schema must exclude the property.

Participant direct identifiers are stored behind a separate field policy and encryption boundary. Decision actors and audit references preserve attribution after membership suspension. AI proposals record both confirming actor and ordinary command receipts. Derived artifacts carry source restrictions; a separately approved public artifact has its own audience policy and transformed content.

## 6 Keys indexes and query paths

The permanent source key is tenant, namespace and stable source key. A source revision receipt additionally includes source revision and content digest. Identical source identity and identical revision content are duplicates; same revision identity with changed content is a conflict requiring investigation. A new source revision creates a new destination revision. File row number is provenance only and cannot be the durable identity across files.

Primary query indexes start with tenant_id. Add programme/status/updated_at/object_id for registries; indicator/event_at/object_id for observations; scope and due time for work; workflow/stage/state for review; job class/state for admission; and pending outbox occurrence time for dispatch. Use JSON indexes only for reviewed stable query patterns, not an index on every arbitrary custom field. Inspect execution plans on the largest tenant and restricted scopes.

List requests default to 50 and cap at 100 rows. Use deterministic keyset pagination with object ID as a tie breaker. A signed opaque cursor binds tenant, subject or effective scope digest, policy epoch, query hash, sort, snapshot/live traversal mode, last key and expiry. Reject changed-context reuse. Counts, facets and suggestions operate over the same eligible set; a hidden row cannot alter a visible count or continuation hint in an information-revealing manner.

Read-model cache keys contain tenant, object or query, source revision set, mode, locale and policy context. Caches never substitute for current access checks. Large previews cap at 1000 rows and larger retrieval becomes an export job. Expensive count queries may be omitted rather than returning an unauthorised or misleading estimate.

## 7 Identity sessions invitations and custody

OIDC login uses code flow with PKCE, state and nonce, validated issuer/audience, exact redirect URI and trusted discovery configuration. Tokens are not accepted solely because their signature validates; tenant binding, subject mapping and required assurance must also hold. Cookie sessions store a random opaque identifier, with a server-side hash and absolute/idle expiry. No browser local storage contains reusable access or refresh tokens.

Invitation creation checks that the inviter can delegate every requested capability and scope and that external membership expiry satisfies policy. Store a token hash, intended verified identity constraints, tenant, inviter, role template, scopes, expiry and state. Acceptance is authenticated but can occur before active membership exists. Lock the invitation, check intended identity, validity and current inviter authority, consume once, create one membership and record the receipt atomically. Resend revokes prior tokens before issuing a new one.

Ownership transfer uses a successor nomination, successor acceptance, fresh assurance and distinct approval or verified recovery case. Lock tenant custody and involved memberships, compare expected current owner, recheck successor eligibility and then append a custody event. Ordinary suspension or revocation of the final eligible owner is rejected unless an approved closure path permits it. Custody transfer does not grant participant identity access automatically.

Service identities have named owners, backup owners, scopes, purposes, credential references and expiry. Offboarding enumerates owned jobs, schedules, connections, drafts and review tasks. Every dependency becomes reassigned, cancelled or explicitly held. A job cannot continue forever under a departed human session or silently adopt an unrestricted operator credential.

## 8 Policy evaluation and revocation

PolicyEvaluator returns allowed, safe reason code, permitted field set, eligible row predicate, obligations, policy epoch and subject epoch. Its order is tenant lifecycle, identity/membership lifecycle, explicit deny, capability, scope, classification, purpose, expiry, assurance, separation of duties and entitlement. Unknown scope or policy denies sensitive work. Positive cache TTL is at most 30 seconds; sensitive execution takes a fresh decision within its transaction or side-effect boundary.

Administrative permission simulation uses the same evaluator with an explicit hypothetical change set and produces an impact preview. Simulation does not persist grants. Positive role inheritance never erases a stricter tenant policy. An exception carries allowed relaxations, scope, reason, owner, independent approval and expiry; it cannot waive tenant isolation, valid arithmetic or independent approval.

Revocation increments subject/policy epochs and creates an outbox invalidation event in the same transaction. Consumers invalidate sessions, query caches, search handles, AI contexts and generated artifact handles. During propagation, reads recheck at the maximum permitted TTL; sensitive actions check immediately before effect. Download streams set bounded write deadlines and recheck at short chunks or time intervals so a slow client cannot extend access beyond 60 seconds. Qualify this end to end, including reverse-proxy buffering and ranges.

## 9 HTTP and error contracts

All business routes are tenant-bound beneath /v1/tenants/{tenant_id}. GET returns a bounded resource envelope or collection. POST to an ordinary resource creates a draft only where allowed. PATCH accepts expected_revision and only editable draft fields. State changes use explicit actions paths. Asynchronous commands return HTTP 202 and JobReceipt; completion is discovered through the job and final domain receipt. No DELETE route directly purges a governed object; privacy and lifecycle commands own deletion.

Every mutation has an operation_id. Commands changing existing state also carry expected_revision or an explicit equivalent candidate/custody comparison. Resource envelopes contain object_id, tenant_id, revision_id, lifecycle_state and typed data. Receipt contains operation_id, object_id, revision_id, business_state, saved_at and correlation_id, with job reference when applicable. Client input actor, scan state, approval status and audit time are never authoritative.

| Semantic code | HTTP treatment | Required behaviour |
| --- | --- | --- |
| AUTH_REQUIRED | 401 | Authenticate without returning protected content. |
| ASSURANCE_REQUIRED | 403 | Step up for the pending sensitive intent before any effect. |
| RESOURCE_UNAVAILABLE | 404 | Missing and inaccessible protected objects share safe response shape and message. |
| POLICY_DENIED | 403 | Known context but action disallowed; self approval adds INDEPENDENCE_REQUIRED reason_code. |
| VALIDATION_FAILED | 422 | Field errors and retained draft; no ordinary partial save. |
| CONFLICT_VERSION | 409 | Reload or review permitted differences; never overwrite silently. |
| CONFLICT_OPERATION | 409 | Same operation ID has different intent; require a new reviewed command. |
| STATE_TRANSITION_DENIED | 409 | State does not admit the requested action; show only permitted recovery. |
| EVIDENCE_REQUIRED | 422 | Mandatory evidence incomplete or unverified; approval remains blocked. |
| INCOMPATIBLE_MEASURE | 422 | Unit, period, population or definition contract is incompatible. |
| UNDEFINED_RESULT | 200 typed calculation result | No numeric zero, infinity or generic server error; include reason such as ZERO_DENOMINATOR. |
| LIMIT_EXCEEDED | 429 or 422 for fixed capacity validation | Explain admission delay or fixed input bound; Retry-After only where retry is meaningful. |
| DEPENDENCY_UNAVAILABLE | 503 | Preserve input and show controlled degraded route; no unapproved fallback. |
| QUARANTINED | 423 for blocked content access | File remains inaccessible through ordinary preview and evidence approval. |
| EXPIRED_GRANT | 410 | Offline package or temporary authority expired; renewal cannot silently accept stale authority. |

Errors contain code, safe message, retryable, correlation_id and permitted_actions, with optional field_errors and reason_code. Reverse proxies and authentication middleware must preserve this contract for application errors. Limit diagnostic bodies and never echo tokens or unsafe payloads. The API test harness disables redirects to avoid forwarding credentials and bounds response size and timeout.

## 10 Lifecycle implementation

Each state machine has an explicit transition table, guard evaluator and effect handler. Transport methods do not directly set state. State names remain case-sensitive in persisted contracts. Current permitted actions are computed from both state and policy. Material changes create a new candidate rather than editing an approved revision.

| Model | Transitions | Guards |
| --- | --- | --- |
| ST01 Tenant | Requested to Provisioning to Active; Active to Suspended or Closing; Suspended to Active or Closing; Closing to Archived to Deleted | Activation policies complete; suspension pauses writes and schedules; closure export and hold checks; deletion irreversible and audited |
| ST02 Membership | Invited to Active; Invited to Expired or Revoked; Active to Suspended Expired or Revoked; Suspended to Active | Identity verified; new activation rechecks grants and expiry; revoked membership needs a fresh approved invitation rather than token reuse |
| ST03 Programme | Draft to Ready to Active to Closing to Archived; Archived to Active through approved reopen | Ready has measurement and policy completeness; closing checks outstanding work; reopening does not unlock old periods automatically |
| ST04 Governed definition | Draft to InReview; InReview to Approved Returned or Rejected; Returned to new Draft revision; Approved to Superseded or Retired | Review binds candidate; material edits create draft child; approved version immutable |
| ST05 Form | Draft to Test to InReview to Published; Published to Superseded or Retired | No test data in production; version compatibility policy required; retired version cannot create new assignments |
| ST06 Submission | LocalDraft to UploadPending to Received; Received to Validating; Validating to Valid Quarantined or Invalid; Valid to InReview; InReview to Approved Returned or Rejected | Required media and authoritative checks complete; approved correction is a new revision; old approval never transfers |
| ST07 Import | Draft to Previewed to Queued to Running to Completed CompletedWithIssues Failed or Cancelled | Confirmation binds source and mapping; every row has outcome; completed import does not imply data approval |
| ST08 Quality issue | Open to Assigned to InResolution to Revalidation to Resolved; eligible warning to Excepted | Revalidation proves fix; exception has authority and expiry; recurrence reopens or creates linked issue |
| ST09 Workflow | Pending to Active; Active to Approved Returned Rejected Cancelled or Blocked | All required stages/quorum complete; no stale decisions; absent reviewers cause blocked reassignment, not auto approval |
| ST10 Reporting period | Open to Closing to Locked; Closing to Open on failure; Locked to RestatementPending to new Locked version | Preview reconciliation; new lock has new snapshot; original remains identifiable |
| ST11 Report | Draft to InReview to Approved to Published; Published to Withdrawn or Superseded | Approval and publication separate; audience and snapshot fixed; corrections create a new draft version |
| ST12 Connection | Draft to Testing to Active; Active to Paused Failed Expired or Revoked; Failed or Paused to Testing | Secrets tested against bounded scope; revoked credentials never silently restored; resume uses checkpoint and current mapping |
| ST13 AI task | Queued to Running to DraftReady or Failed; DraftReady to Reviewed or Discarded; proposal Reviewed to Applied Rejected Stale or Expired | Write confirmation separate from generation; no domain approval generated; source or policy change makes proposal stale |
| ST14 Privacy case | Received to Verification to Assessment to Approved Rejected or OnHold; Approved to Executing to Completed or PartiallyCompleted | Verification minimal; stores individually accounted; partial cannot imply full deletion; hold release resumes remaining actions |
| ST15 Evidence | Received to Quarantined or Safe; Safe to Unverified Verified or Disputed; eligible version to Restricted Archived or Deleted | Safety scan differs from authenticity; disputed mandatory evidence blocks qualified publication |
| ST16 Subscription | Trial to Active or Expired; Active to Overdue Suspended or Closing; Overdue to Active or Suspended | Commercial changes never directly erase records or remove security; tenant lifecycle separately authorised |
| ST17 Support elevation | Requested to Approved or Rejected; Approved to Active to Ended Expired or Revoked | Distinct approver, scope and duration; denied operations remain denied during support |
| ST18 Participant | Active to Restricted Withdrawn Inactive or Archived; permitted corrected state by reviewed change | Withdrawal scope explicit; death or loss to follow up is an observation code, not automatic deletion |

ST15 evidence safety and authenticity are orthogonal substates. A clean scan does not verify a source, and verified source provenance does not make malicious bytes safe. ST14 privacy may finish PartiallyCompleted with explicit stores or holds outstanding. ST10 restatement creates a new locked snapshot and leaves the old arithmetic unchanged. ST02 revoked membership requires a fresh approved invitation; a consumed old token is never reactivated.

## 11 Idempotency canonicalisation and audit atomicity

Canonical intent is calculated after DTO validation and typed normalisation. Sort object keys, preserve array order, normalise decimals according to their declared field type, preserve case-sensitive codes, normalise timestamps to their semantic instant where appropriate and reject nonfinite values. Do not remove meaningful defaults, null states, ordering or revision references to force two different commands to look identical. The reference canonical_hash illustrates JSON ordering only; the production typed canonicaliser must implement the field rules.

The unique operation key is tenant_id, actor_id, command_type and operation_id. Acquire or insert the receipt under a unique constraint. A concurrent duplicate waits for the original transaction or receives an explicit processing state. Completed identical intent returns the recorded safe result; changed hash fails. A retry from a different actor cannot inherit another actor's command authority. Expired interactive receipts do not remove permanent source and submission identity records.

Revision, projection, audit, receipt and outbox write commit together. Audit failure aborts a governed command where audit is mandatory. Do not write a success audit after returning a success response in a best-effort background task. Denied attempts may use a separate minimised audit transaction, without logging hidden data. External calls occur outside the core transaction through a durable job, and their outcome is reconciled with the provider's supported idempotency or receipt mechanism.

## 12 Review and period close algorithms

For a decision, load the workflow and immutable candidate, lock current review state, verify candidate equality and current authority, map actor to verified natural identity, compare against all contributing authors, validate delegation and stage eligibility, and check mandatory evidence. Insert an immutable decision under a unique stage/person/candidate key. Count distinct eligible decisions; a repeat click or alternate membership cannot increase quorum. Apply transition and receipt in the same transaction.

Returning a candidate terminates or invalidates pending approvals for that candidate according to workflow policy. The next revision starts a new decision set. Reviewer expiry or departure pauses affected stages for controlled reassignment. Delegation is bounded by the delegator's current authority and records both actors. There is no automatic timeout approval.

ClosePeriod first creates a readiness manifest from obligations, quality, evidence, definitions and targets. Confirmation locks the period and verifies all manifest revisions. If anything changed, return CONFLICT_VERSION and rebuild readiness. If gates fail, keep the period open with actionable missing work. If valid, generate immutable snapshot members and their digest, mark locked and emit an event. Recalculation after an approved correction produces new live results; restatement requires an independent new close/report process.

## 13 Deterministic calculation algorithms

Calculation input is an immutable manifest containing candidate definition/rule versions, approved source revisions, period/calendar version, dimensions, comparability contract, target context and policy scope. Sort by stable contribution identity for reproducibility. Validate acyclic dependencies and deduplicate identical source contribution identities before additive aggregation. Conflicting values under one immutable source identity fail; they are not averaged or chosen arbitrarily.

The engine evaluates value states before arithmetic. MISSING and NOT_COLLECTED retain expected obligations; approved NOT_APPLICABLE eligibility removes its obligation from the denominator. Zero expected obligations yields coverage NOT_APPLICABLE, not 100%. UNDEFINED results retain reason and lineage. Coverage, approval context and freshness do not become numeric values.

Pooled ratio sums eligible numerators and denominators before division. A zero denominator yields UNDEFINED with no value. Percentage and rate multipliers are explicit in the rule; proportions enforce nonnegative components and meaningful numerator bounds. A count sums compatible disjoint contributions. Unique counts require authorised matchable identity sets. An unknown overlap may provide gross reach but cannot claim an exact unique total.

Cumulative results select the eligible end position; increments need a verified start. Higher-target attainment uses the declared positive target and remains uncapped. Lower-target attainment uses direction and signed deviation. Range attainment compares against inclusive bounds. Weighted scores require compatible normalisation, equal component/weight cardinality, nonnegative weights and exact sum one. Median uses pooled compatible raw values. All display and currency conversions retain their rule versions.

CalculatedResult includes mode, value_state, stored value, numerator/denominator where relevant, displayed_value, display_decimals, rounding_rule, unit, run_id, lineage_manifest_id, coverage, freshness, reason_code and limitations. A result version is published atomically with its complete lineage; partial failed computation cannot expose a mix of old and new widgets as current. Snapshot reports use their pinned result revisions regardless of live refresh.

## 14 Ingestion row processing and replacement

Create upload session, stream into quarantine, verify size and digest, scan, then parse with bounded memory. CSV parsing declares delimiter, quoting, encoding and decimal/date locale. XLSX parsing uses the selected sheet and excludes macros or active evaluation. Formulas are source values under an explicit ingestion policy, not arbitrary code to execute. Archive extraction requires a separate bounded qualified profile.

Preview produces source digest, mapping revision, schema comparison, sampled rows, expected totals, duplicate/key rules, atomic/partial mode and replacement impact. Commit validates that preview is unexpired and every bound input is unchanged. Controlled replacement enumerates exact scope and deletion treatment; absence from an append source never means deletion. One million rows use an asynchronous staged path with bounded batches.

For each row, derive permanent source identity, validate scope and typed fields, resolve referenced versions, apply deterministic transformations and quality rules, compare source revision receipt, then create or revise the destination in its atomic item transaction. Store one outcome and provenance location. Crash after row commit but before worker acknowledgement is resolved by the durable row/source receipt. Cancellation accounts for parsed unprocessed rows and never erases committed items.

## 15 Form grammar and submission validation

Expressions permit typed literals and field references; arithmetic +, -, *, /; comparison; and/or/not; exists; code-list membership; bounded date difference; min/max; and conditional selection. A proposed grammar is expression = conditional or logical; logical = comparison joined by and/or; comparison = arithmetic optionally followed by a comparison operator and arithmetic; arithmetic = bounded terms; term = literal, field reference, permitted function or parenthesised expression. Precedence is explicit and parsed into an AST, never evaluated through Python eval, JavaScript eval, SQL or network access.

Proposed qualification bounds are 8192 Unicode characters, 256 AST nodes, depth 16, 32 arguments per function and 10000 visited nodes per submission. These are design limits that must be measured against the FSD 200-question and 100-repeat capacity, and changed through review if needed. Acyclic dependency ordering is validated at publication. Repeat references declare local repeat versus aggregate context and cannot accidentally read a different household member.

Date difference specifies elapsed duration or calendar-date semantics. Age calculation declares treatment of incomplete dates. Unit-incompatible comparisons fail at publication or server validation. Hidden values follow the published CLEAR or RETAIN_RESTRICTED rule consistently on device, API, import and export. A retained hidden value remains classified and cannot leak because the field is visually absent.

Submission input binds stable submission ID, form/translation version, assignment, event/capture times and zone, answers, attachment manifest and offline grant when used. Server receipt time and uploader identity are generated by the server. A received record is validated but still awaits review. Corrections require base revision and produce a new revision; published form changes cannot silently reinterpret older submitted answers.

## 16 Offline persistence and sync protocol

Local tables store packages, grants, assignments, drafts, answer revisions, media chunks, sync attempts and receipts, each bound to tenant and signed-in identity. Encryption keys never appear in sync payloads or diagnostics. A device account switch locks the previous account's database and media keys. Qualified device policy controls backup, screen lock, root/integrity response, Keystore use and local deletion. Root detection alone is not sufficient assurance.

The package manifest is signed by the platform and binds device key, subject, scope, form versions, permitted fields, policy epoch, issued time and expiry. Verify signature and trusted time anchor before unlocking. Compare monotonic elapsed time with the remaining lease; wall-clock adjustment cannot extend it. Lost trusted continuity locks sensitive data. Local save uses a database transaction and a visible device-only receipt; server receipt is never inferred from a spinner disappearing.

Sync first reauthenticates, renews current authority where allowed and checks assignment/form compatibility. Transfer media with stable content identity and inspect receipts. Submit the stable submission identity with exact payload hash. Lost responses are queried by receipt before resending. A changed payload under the same immutable submission revision produces conflict, while a correction has a new revision and expected base. Server conflict payloads expose only permitted differences.

The API archive uses a bounded whole-object upload PUT as the initial media contract. A fully resumable multipart implementation needs chunk identity, offset, content digest, final manifest and cleanup qualification before it claims support for weak-link field media. This is an explicit implementation item, not an assertion that the prototype demonstrates durable mobile sync. AT21 requires interruption at every commit and acknowledgement boundary on actual devices.

## 17 Evidence evaluation and analytical finance

File metadata contains blob identity, digest, byte length, actual type, quarantine state, scan version, source provenance, classification, authenticity verification and publication handling. Upload ownership and tenant are checked on every operation. Finalisation verifies complete bytes before requesting scan. A scan failure never creates a usable evidence link. External evidence URLs are fetched only through qualified outbound policy, including redirects, DNS and private-network restrictions.

Qualitative extracts reference evidence revision, source span, codebook version, assigned code and interpretation author. A changed source yields a new extract revision. Conflicting findings preserve their evidence and limitations. Evaluation records bind question, programme baseline, method, period, evaluator and permissible causal interpretation. AI suggestions cannot promote a descriptive trend into reviewed causal evidence.

FundingAgreement records ceiling, dates, currency and restrictions. FinanceTransaction uses a stable external key, posting and event dates, amount, category and optional reversal reference. ExchangeRate is dated, versioned and positive, with explicit reporting-currency units per source-currency unit. AllocationRule weights sum exactly to one; residual rounding follows stable recipient order and a recorded adjustment. Reconcile allocated totals to the source, and keep paid amounts separate from budgets and commitments.

## 18 Dashboards reports and disclosure

DashboardDefinition stores widgets and their typed result bindings, approved/provisional mode, filters and display configuration. Filter execution is scoped server-side. Ten widgets is the standard performance qualification profile; unsupported combinations have visible asynchronous or limit behaviour. Geographic views aggregate through reviewed geography and disclosure rules. Hover cards and downloaded chart data must not reveal suppressed values.

ReportTemplate contains versioned sections, language, mandatory caveats and numeric bindings. Report generation reads the pinned snapshot and builds a reconciliation manifest mapping every numeric occurrence to an authoritative result and display rule. A failure leaves no downloadable partial official artifact. The artifact digest, template, language, fonts and renderer version are recorded for reproducibility. Accessibility verification includes standard generated templates.

Disclosure review evaluates purpose, audience, recipient eligibility, expiry, classification and the cumulative information revealed by prior released slices. The reference public_cells function demonstrates conservative withholding of a single additive row only; it is not a complete inference-control engine. Production review must handle totals, repeated queries, overlapping slices, geography and linkage risk. Sensitive report downloads are mediated and reauthorised; publication notices carry safe references rather than unprotected attachments.

## 19 AI orchestration and confirmation

AITask records tenant, use case, requester, scope, permitted source revisions, model/prompt/retrieval/tool configuration, budget reservation and state. Admission reserves budget atomically before accepting provider work. Cancellation stops new provider/tool calls where controllable and reconciles already accepted provider usage. A provider failure is recorded without switching to a destination with different retention or region policy.

Retrieval uses only eligible source revisions. Tool output is typed and rechecked even if the model asks for a broader scope. Evidence questions return supported claims with source spans and limitations. Official numbers are formatted from CalculationResult, not parsed back out of prose. Consequential unsupported claims block publication or use-case release according to the evaluation contract.

AIProposal includes target object, expected revision, exact diff, source manifest, policy epoch, proposal digest and expiry at most 30 minutes or material change. ConfirmProposal is an ordinary authenticated command that reloads sources and target, verifies digest and current scope, then applies only the allowed draft fields. No generic SQL, shell or unrestricted HTTP tool is exposed to the model. Approval, publication, grant and deletion capabilities remain absent from its tool catalogue.

## 20 Jobs leases notifications and webhooks

Job states are Requested, Validating, Queued, Running, Cancelling and terminal Succeeded, SucceededWithIssues, Failed or Cancelled. Job contains requester, service identity, scope, input versions, admission class, lease generation, heartbeat, attempt count, cancellation boundary and output manifest. Progress percentage requires a known denominator; otherwise expose named stage and completed count.

Workers claim jobs with a bounded lease and increment generation. Every result update includes the generation predicate. Outbox dispatch may publish the same event more than once. Consumer receipts key tenant, consumer and event ID; domain constraints are still necessary because different events can represent the same source business identity. Retries use exponential backoff with jitter and a bounded failure queue; exact connector schedules follow the FSD qualification profile.

Notifications deduplicate by event, recipient, channel and notice class. Security notices are not suppressed by digest preference. Recheck current recipient and scope before delivery; a changed email address does not redirect a pending sensitive notice without verification. Digests default to 09:00 recipient zone, reminders three days before and at due time, escalation after two business days under the programme calendar.

Webhook business event_id remains stable across attempts; delivery_id and attempt identify transport. Sign the exact body with a qualified integrity scheme and enforce timestamp/replay policy. A retry checks current destination scope and credential. Reordering is handled through resource revision semantics. An external consumer outage cannot roll back a valid internal approval.

## 21 Audit privacy and restore mechanics

AuditEvent records tenant, real and effective actor, action_type, specification_ref, object/revision reference, outcome, occurrence time, correlation ID and minimum required context. Approval adds candidate/workflow/evidence references. Export adds purpose and manifest. AI adds proposal and ordinary command receipts. Privacy adds minimised store outcomes. Secret values and unnecessary personal fields never enter logs or audit by convenience.

Append-only privileges prevent ordinary runtime updates to revisions, decisions and audit. Ordered audit batches link digests and publish signed checkpoints to independently protected storage. Verification detects mutation, gaps, reordering and truncation relative to a retained checkpoint. A lawful payload removal records an authorised privacy event without selectively erasing accountability. Cryptographic hashes are still reviewed for their own retention and potential identifying value.

Privacy execution creates one action per store and object/version scope, checks holds and writes an independently durable deletion ledger entry. Active removal or effective restriction must complete within 24 hours once executable. A hold has authority, reason, covered scope, review date and release decision. A failure leaves the case PartiallyCompleted and schedules bounded retry; aggregate completion is derived from all required store outcomes, not the first successful deletion.

Restore begins in a closed network and application state. Verify backup integrity, recover keys, apply the current deletion ledger, current identity/grant restrictions and retained holds, rebuild or invalidate search/AI caches, reconcile attachments and snapshots, run isolation and receipt checks, then admit traffic. Do not start workers before governance replay. The restore test must include a deleted participant and revoked principal whose old state still exists in the backup.

## 22 Web interactions and accessibility

Each screen uses an explicit view model containing object context, revision, permitted actions, fields, source mode and visible status. The server remains authoritative; hidden buttons are not a permission control. UI01–UI30 are demonstrated in the standalone HTML prototype. Its role selector is a design-review control and intentionally does not implement production authorisation.

Handle loading, empty scope, no filter match, partial, stale, validation failure, access loss, version conflict, offline local save and job failure as distinct states. Preserve entered values when safe; do not retain restricted content after access loss. On error, move focus to a summary linked to fields. On dialog close, restore focus; announce asynchronous state changes. Tables have headers, charts have nonvisual data equivalents and colour is not the sole indication of status.

Ordinary field screens work at a 360-pixel viewport; wide analytical tables can use labelled horizontal scroll. Keyboard alternatives exist for hierarchy editing and drag interactions. Released translation strings cover validation, confirmation and recovery, not only labels. Formatting locale never changes stored decimals, event instants or period assignment. Browser and assistive-technology matrices are pinned at release and include complete workflows.

## 23 Security implementation controls

Use parameterised database access, strict DTO parsing, bounded deserialisation, dependency pinning, security headers, CSP, CSRF protection, authenticated object checks and safe error rendering. Public forms have bounded capability and rate policies; anonymous collection does not grant participant discovery. Credentials are stored as secret references and never appear in ordinary configuration exports or logs.

Outbound fetch policy validates scheme, host allowlist, resolved addresses, redirect destinations and connection behaviour, including IPv6 and DNS rebinding. Block internal metadata and private ranges unless a specifically approved private integration path exists. Do not forward an original destination's credentials through arbitrary redirects. Upload parsing uses resource limits and isolated workers; file previews never execute active content.

CI produces dependency and container findings, secret scans and an SBOM. Independent assessment tests chained abuse across roles, files, exports, AI and support. No unresolved critical or high access/confidentiality/integrity finding enters production without an effective verified mitigation. A passing average or feature priority cannot override that gate.

## 24 Release migrations and operations

Every deploy records image digest, build ID, API schema version, database migration version, policy baseline, UI/client versions, calculation version and model/prompt/retrieval/tool versions. Backward-compatible additions precede clients that use them. Backfills are tenant-scoped and resumable with their own progress receipts. Delete old fields or constraints only after the rollback and client-support window closes.

Readiness proves the instance can serve its assigned core dependencies and compatible schema. Liveness detects process failure without restarting on every external model or email outage. Degraded AI or connector status is visible separately. Queue depth, lease age, oldest task, per-tenant latency, revocation propagation, calculation freshness, audit gaps and privacy deadlines are operational signals with explicit owners and runbooks.

Rollback restores compatible code and configuration. Irreversible data transformations need a forward repair plan or rehearsed restore; database down migrations are not automatically safe. A canary observes critical journeys, official reconciliation, isolation and error rates before wider rollout. Scope-specific feature shutdown can disable AI or a connector without disabling healthy manual collection and reporting.

## 25 Testing and implementation completion

The reference suite contains 143 runnable tests and has passed in the preparation environment. It covers selected deterministic contracts and fixed boundary vectors; it has no production branch-coverage claim. The 18 API integration and 12 readonly smoke tests require an actual implementation and provisioned fixture. Their recorded status is Blocked because those prerequisites were not supplied. The 825-case catalogue describes the broader functional, journey, security and NFR work.

Completion requires closed nested DTOs; applied and reversible qualified migrations; real-role RLS tests; connector/provider qualification; Android expiry/sync qualification; complete golden-corpus variants; browser/accessibility evidence; load/soak and recovery reports; and independent security/AI evaluation. The archived SQL and OpenAPI are useful starting contracts, not a substitute for those gates. Any change in FSD meaning must update source traceability and receive a recorded baseline decision.

## 26 Supporting entity invariants

| Supporting record | Owner | Invariant |
| --- | --- | --- |
| Funding agreement | C10 | Version ceiling, dates, currency and donor restrictions. Activation requires authority and eligibility checks. |
| Finance transaction | C10 | Unique source identity; correcting reversal links original; never silently overwrite imported expenditure. |
| Exchange rate | C10 | Positive rate with source and reporting currency direction, effective time and immutable version. |
| Allocation rule | C10 | Nonnegative weights sum one; preserve source total; residual follows stable reviewed order. |
| Work item | C03 | Activity, milestone, risk and action types have explicit owners, dates and acyclic dependencies. |
| Dashboard definition | C09 | Widgets bind typed result versions/modes, permitted filters and visible freshness. |
| Report template | C09 | Numeric bindings separate from narrative; language and mandatory caveats are versioned. |
| Notification | C08 | Event/recipient/channel/class deduplication; minimal safe reference; current recipient authority. |
| Schedule | C14 | Owner, service identity, scope, timezone, cadence and missed-run policy. No departed-session execution. |
| Qualitative extract | C07 | Immutable evidence revision, source span, codebook version and authored interpretation. |
| Device registration | C16 | Device key, qualified security profile, attestation reference and revocation lifecycle. |
| Support request | C14 | Exact scope/capabilities/expiry, requester and distinct approver; maximum 60-minute grant. |
| Webhook delivery | C11 | Stable event ID, separate delivery attempt identity, integrity proof and reconciled external outcome. |

Nested arrays and objects are bounded by entity-specific schemas: framework nodes have stable IDs/types/titles and scoped edges; form fields and answers use published field types; workflow stages identify mandatory reviewers/quorum; report sections distinguish narrative from numeric result bindings; scopes contain reviewed explicit members or versioned predicates; import mappings name typed transforms and keys; schedules bind owner/service identity and timezone; AI sources bind immutable revision IDs and spans. additionalProperties false must be applied at every executable write DTO, not only the outer envelope.

The blueprint deliberately separates design from deployment. Environment role/grant SQL, append-only triggers or privilege arrangements, classified UUID foreign keys, encrypted identifier storage, signed cursor code, full nested DTOs, exact connector schemas and multipart sync are implementation tasks with named verification gates. They must not be silently assumed complete because a design file parses as JSON or SQL text.

## 27 References

| Ref | Contract | Source |
| --- | --- | --- |
| S01 | Functional baseline | Impact Management Platform FSD v1.0, 24 September 2026. Source digest is recorded in the companion HLD and archive README. |
| S02 | PostgreSQL row security | https://www.postgresql.org/docs/17/ddl-rowsecurity.html |
| S03 | Transactional outbox | https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html |
| S04 | Queue redelivery | https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html |
| S05 | OIDC identity layer | https://www.keycloak.org/securing-apps/oidc-layers |
| S06 | Android key custody | https://developer.android.com/privacy-and-security/keystore |
| S07 | OpenAPI format | https://spec.openapis.org/oas/v3.1.1.html |
| S08 | Worker boundary | https://fastapi.tiangolo.com/tutorial/background-tasks/ |
