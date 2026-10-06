# Nonprofit AI Enablement Data Dictionary

Edition 1.0   5 October 2026   Proposed extension baseline

This is a logical and field dictionary for the nonprofit AI extension. Current facts are grounded in build 0.30.0 at commit 36073f1, schema 35. Proposed R2 and conditional R3 fields are design proposals, not SQL tables, migrations, deployed contracts or accepted requirements. The existing platform dictionary under docs/current remains authoritative for the complete database.

## How to use this dictionary

The machine-readable companion data-dictionary.csv gives one row per field, with DD-NPA identifiers, type, requiredness, nullability, constraints, editing authority, classification, retention, source and FR-NPA links. There are 362 field entries: 162 current local fields and 200 proposed or conditional fields.

Required means the member exists in the API or logical record. Nullable means an explicit null is allowed. A required string may still be empty where the current service permits it. Array element notation describes elements rather than independent columns. JSON paths are members of a payload, not new SQL columns. Proposed maximum lengths require approved closed contracts before implementation and do not alter current DTO limits.

CURRENT_LOCAL records an implemented source fact only. PROPOSED_R2 and CONDITIONAL_R3 identify logical target designs. Runtime classification INTERNAL is distinct from editorial LOW/MEDIUM/HIGH use-case sensitivity. Public editorial content still requires current tenant read access in the current API; there is no new unauthenticated public marketplace route.

## Current entities and storage

| Entity | Persistence and ownership | Access and constraints |
|---|---|---|
| AIEnablementProfile | Six required user-entered fields; assessment request is not independently persisted | Read capability for assessment; management capability for saved plan; no beneficiary information or credentials |
| AIEnablementAssessment | Inner assessment result in the response wrapper assessment; deterministic over submitted profile and versioned editorial rules | Self-report and English keyword matching; no verified competency or savings score |
| AIEnablementCatalog | Source-controlled use cases, lessons, criteria and journey | Tenant authorised read; schema 1.0; version nonprofit-2026-10-05.2 |
| AISolutionsCatalog | Source-controlled eight-product dated snapshot | Tenant authorised read; version nonprofit-solutions-2026-10-05.1; checked 5 October 2026 |
| AIAdoptionPlan | AIAdoptionPlan kind in existing registry and immutable revisions; no new projection table | Draft only; tenant scoped; at most 1000 plans; no archive, delete or approval screen |
| AIAdvisoryRequest | AIAdvisoryRequest registry metadata plus ai_advisory_request claim table in migration 0034 | Recorded metadata contains original content version and RESERVED status; raw submitted profile is not copied to metadata |
| AIAdvisoryResult | Insert-only ai_advisory_result table; sealed success output or sanitised failure | No UPDATE/DELETE app grant; tenant fence; current authority on replay |
| OperationReceipt | Existing operation_receipt, atomic with plan revision and audit/outbox | Plan replay window seven days; exact command fingerprint; no automatic semantic conflict retry |

AIAdoptionPlan is a shared organisation draft, not a private staff notebook. The shared writer stores classification INTERNAL and assigns owner and author from current identity; no caller chooses classification, lifecycle state, issuer, author, approval or content versions. All IDs in URLs are selectors rather than authority.

## Exact current plan contract

A create request has only operation_id and data. An update adds expected_revision. Data has exactly title, profile, solution_ids, learning_completed, procurement and pilot. Stored data adds content_versions with catalog and solutions. Duplicate JSON keys and unknown members are rejected by the closed contract path.

| Member | Current constraint |
|---|---|
| title | Nonblank, at most 150 characters |
| profile.sector | GENERAL, EDUCATION, HEALTH, LIVELIHOODS, ENVIRONMENT |
| profile.team_size | Integer 1 through 100000; boolean values rejected |
| profile.goal | Nonblank; at most 1000 characters in raw and trimmed validation |
| profile.data_readiness | NONE, BASIC, STRUCTURED |
| profile.ai_experience | NONE, EXPERIMENTING, REGULAR |
| profile.sensitive_data | Boolean; does not authorise sensitive data entry |
| solution_ids | Unique known catalogue IDs, zero through four items |
| learning_completed | Unique known lesson keys, zero through twelve current keys; contract array ceiling is 100 |
| procurement.requirements | Required string, may be empty, at most 2000 characters |
| procurement.data_boundary | Required string, may be empty, at most 2000 characters |
| procurement.budget_notes | Required string, may be empty, at most 500 characters; no committed budget |
| procurement.vendor_questions | Required string, may be empty, at most 2000 characters |
| pilot.success_measure | Required string, may be empty, at most 1000 characters |
| pilot.completed_actions | Unique subset of DEFINE_GOAL, SYNTHETIC_TRIAL, HUMAN_REVIEW, TRAIN_STAFF, REVIEW_OUTCOME; at most five |
| content_versions | Server owned, pinned on each new saved revision; excluded from write DTO |

The response carries object_id, revision_id, business_state Draft and stored data. The save receipt carries object_id, revision_id, business_state, saved_at, operation_id and correlation_id. The list returns items and nullable next_cursor, with default limit 50 and maximum 100. Cursors are HMAC signed, tenant/principal/route/current visibility bound and expire after fifteen minutes. No total_rows is returned.

## Version and learning key discipline

Current lesson keys are foundations:0 through foundations:3, pilot_design:0 through pilot_design:3 and procurement:0 through procurement:3. The index is part of the current identity scheme, so moving a lesson to a different index must not change the meaning of saved completion. A future explicit lesson UUID/version design needs a compatibility mapping, retained prior content and migration tests; it is proposed, not already delivered. DEC-NPA-012 must settle content ownership and stable identifiers before catalogue reordering.

Saved content_versions show which catalogue editions accompanied a save; they do not create a historical catalogue API or revision-history UI. Prior object revisions remain immutable. Reopening a plan against a changed current catalogue needs visible old/unavailable content handling in the target design. Current catalogues must preserve known keys to avoid reinterpretation.

## Advisory claim and result discipline

The advisory request has only operation_id, profile and consent true. It requires current ai.enablement.read and ai.advisory.request. The claim uses tenant_id plus request_id as its primary key, with server-generated object_id, current principal_id, a 32-byte submitted-body fingerprint and database reserved_at. A rolling twenty-four-hour window allows at most three tenant claims, including failed claims.

The claim transaction commits before any external generation call. The adapter receives only the submitted profile and deterministic assessment; it does not fetch protected programme records. The adapter configures forty-five-second HTTP phase and inactivity timeouts and requests at most 2048 output tokens with store false. This is not a strict overall wall-clock deadline; such a deadline requires a proposed control and qualification. That request flag is not an assertion about a provider's full contract or operational retention. The sealed success result contains DRAFT text, original assessment, model and disclaimer. Success text is nonblank and at most 12000 characters; model is nonempty and at most 200 characters; the current service does not reject an all-whitespace model string. Provider token usage is adapter-local accounting, not a persisted tenant usage ledger or funded budget control.

The result has sealed_output or failure_reason, exactly one nonnull. The only persisted failure reason is AI_PROVIDER_UNAVAILABLE. Sealing uses the delivery keyring and AES-GCM binding to tenant and request. Completed replay still checks current membership and both capabilities. A crash or authority change between claim and result can leave an in-flight request requiring investigation; an automatic repeat call would risk duplicate spending. The selected provider project currently has exhausted credits; no live generation success is documented.

## Keys relationships and atomic writes

Every tenant table has tenant_id in its primary key and foreign keys and FORCE ROW LEVEL SECURITY. The registry head points to an exact revision with a deferred composite foreign key. Object revisions carry predecessor_revision, schema_version 1.2 from the shared writer, payload_sha256, author_id, created_at, restriction_state and revision_number. The schema_version inside a revision is separate from database schema 35 and catalogue schema 1.0.

Plan saves take the tenant lock before resolving authority, then operation lock, current receipt/head checks, validation and revision/audit/outbox/receipt writes in one transaction. Stale expected_revision returns CONFLICT_VERSION; changed payload under an operation ID returns CONFLICT_OPERATION. Exact replay may return an older committed receipt but cannot overwrite a newer revision or bypass revoked read/write access. Operation receipt expiry does not delete the object revision.

Migration 0035 only extends the registry's kind check to AIAdoptionPlan. Migration 0034 creates the two advisory tables and adds AIAdvisoryRequest. Neither migration introduces RFQs, quotes, payments, supplier onboarding, cohort or human-adviser records.

## Proposed R2 entity groups

| Group | Logical entities | Decision dependency |
|---|---|---|
| Capacity | LearningProgramme, Cohort, LearningAssignment, CompetencyAssessment | DEC-NPA-008 rubric and assessors; DEC-NPA-012 stable content |
| Advice and application | HumanAdvisoryCase, TaskTemplate, TaskRun | DEC-NPA-003 data boundary; DEC-NPA-006 adviser accountability; DEC-NPA-011 budget |
| Procurement | ProcurementRequest, SupplierQuote, CostLine, CostComparison, ProcurementDecision | DEC-NPA-007 independence and procurement policy |
| Marketplace | SupplierSubmission, PublishedSupplierSnapshot | DEC-NPA-004 operator/revenue; DEC-NPA-005 verification scope; DEC-NPA-006 conflicts |
| Delivery and operation | Engagement, DeliveryMilestone, ConnectorBinding, AdoptionOutcome | DEC-NPA-010 service levels; DEC-NPA-014 connector scopes; DEC-NPA-016 outcome method |
| Support and feedback | SupportCase, FeedbackRecord | DEC-NPA-009 retention; DEC-NPA-010 incident handling; DEC-NPA-016 improvement governance |

All logical tenant records require server-owned tenant, object, revision and state metadata. An independent decision binds exact candidate revisions and the natural persons involved. PublishedSupplierSnapshot is a separately approved minimised publication DTO; it must never be a public query joining private supplier submissions. Proposed UUID references need tenant-inclusive keys and foreign keys if implemented. They are not unscoped cross-tenant references.

Cost amounts use decimal strings in transport and deterministic NUMERIC(38,12) semantics in storage. Missing amounts stay null and make a complete total unavailable. A cost line states category, currency, quantity, unit, period and source. Currency conversion is unavailable until an approved exchange-rate source and rule exist. Quotes retain validity and written inclusions/exclusions; a directory offer description is not a quote.

## Conditional R3 financial entities

Purchase and PaymentAttempt are logical placeholders only. DEC-NPA-004 and DEC-NPA-015 must determine operator responsibility, payment model, provider, settlement, reconciliation, refunds, dispute ownership and approval before contracts or migrations can be approved. No card data, bank account, payment token or actual financial amount appears in wireframe examples. An outbox intent never proves settlement.

## Privacy ownership retention and export

Free-text plans and generated drafts can contain organisational working notes and require minimised input. First-pilot rules exclude beneficiary personal data and credentials. A sensitive_data true flag records a concern; it does not permit uploads or disclosure. Proposed human advisory and learner evidence use CONFIDENTIAL_PROPOSED classifications pending exact privacy/capability policy, rather than pretending the current INTERNAL writer applies an already-approved higher classification.

The existing member privacy flow and fixed retention classes do not implement AI free-text removal, advisory result removal or supplier/learning deletion. Advisory tables explicitly reject app UPDATE/DELETE. This gap must be addressed through a reviewed append-only-aware privacy design rather than a blanket promise of erase/delete. No AI-specific retention duration is invented here. DEC-NPA-009 must cover legal holds, historical revisions, sealed outputs, evidence, backups and independent export authority. Current AI plan export and history browsing screens are absent.

A proposed export binds the approved exact scope and revisions, rechecks a separate export capability, logs the action, carries catalogue/schema versions and excludes secrets/restricted fields. Read permission alone cannot grant export or external disclosure. Retention and ownership requirements remain open release blockers for affected future scopes.

## Source references and review

Source modules: ai_adoption_contracts.py, ai_adoption_plans.py, ai_enablement_contracts.py, ai_enablement.py, ai_enablement_catalog.py, ai_learning_content.py, ai_solutions_catalog.py and ai_advisory_provider.py under apps/api/impact_api. Storage: migrations 0002, 0003, 0004, 0034 and 0035 plus store.py. Package requirements: requirements.json, 01-BRD.md and downstream FSD/HLD/LLD. Data ownership roles are proposed roles, not named assignees.

Review every CURRENT_LOCAL row against the pinned code, then review proposed fields against the FSD and decisions. Any implemented change needs closed DTO/schema validation, additive migration if needed, exact type/length tests, tenant/current-authority tests, immutable revision evidence and an updated dictionary. This documentation does not promote the original 307 impact requirements or prove execution of proposed tests.
