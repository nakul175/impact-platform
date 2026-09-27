# Release 0.3.0 — manual measurement configuration

Build: 0.3.0 · API: 1.4.0 · database: migration 0006 · qualified locally: 25 September 2026.

## Delivered outcome

An author can configure a programme, define a measure, obtain independent approval, assign a collector and reviewer, specify expected sources for a period, obtain approval of that plan, activate the indicator, and move the programme through Draft → Ready → Active. The approved plan controls calculation eligibility and coverage. The browser supports this complete sequence.

This is the manual measurement implementation profile. Ready and Active do not certify the complete enterprise policy framework, privacy decisions, funding controls, framework completeness or production readiness. Those remain explicit release gates.

## Workflow and functional rules

1. Programme drafts capture code, title, programme type, start/end instants, reporting calendar and geography. Ownership comes from the authenticated creator. Dates must be ordered. The reference calendar and geography must be active.
2. Definition drafts capture code, name, population, inclusion/exclusion, method, unit and display precision. Supported configurations are MANUAL + FLOW, with COUNT/DECIMAL + SUM or RATIO/PERCENTAGE + POOLED_RATIO. Ratio definitions require numerator and denominator meanings. Unsupported configurations cannot be submitted.
3. A current active review policy produces a workflow tied to the exact candidate revision. A different natural person must approve. Returned definitions/plans can be edited and resubmitted. Approved definitions and plans cannot be patched. Definition replacement, retirement and approved-plan amendments are not implemented.
4. An indicator pins a current approved definition, programme, local applicability, collector and reviewer. Assignments do not grant access. Activation checks active memberships, unexpired exact tenant capabilities and distinct natural identities. It requires an approved collection plan.
5. A plan explicitly lists 1–500 obligations for one indicator and open period. Each has a label, namespace, source key and UTC due instant. The period must match the programme calendar and fit its dates. Due instants cannot precede the period start; later reporting deadlines are allowed. Keys must be unpadded and unique. Existing observations or other approved plans cannot reserve the same key for a different indicator/period.
6. Submission pins the indicator revision on the server. The draft input cannot supply this pin. Approval rechecks that the pinned indicator payload is unchanged. Activation checks the same pin; a lifecycle-only activation revision does not invalidate the plan.
7. One approved plan per indicator/period is enforced by a composite primary key and tenant-serialized command handling. Competing plans may be submitted, but only one can be approved. The losing transaction creates no decision, binding or successful receipt.
8. Programme readiness inspects all assigned indicators, current reference records and owner membership. At least one active indicator is required; each needs approved obligations and eligible independent assignments. Every check runs again on transition. Ready freezes ordinary programme edits; an audited Return to draft command requires a reason. Active editing, closing, archiving and reopening are not delivered.
9. Observation submission and calculation require an active programme and indicator. New configured indicators route observations to the assigned reviewer's membership, in addition to capability and natural-person independence checks. Departed or ineligible reviewers block submission; reassignment and escalation remain future work. Legacy synthetic indicators without assignments keep their existing independent-review behavior.

Collectors/reviewers are selected from a minimal directory containing display name, principal ID and eligibility flags. No email or identity-provider subject is exposed by that endpoint. Calendar/geography/period and workflow reference records can be selected, but their management UI is not delivered; the development fixture supplies them.

## Coverage semantics

The calculation snapshots the approved plan and all current, permitted observation revisions in the period. A source matches an obligation only when its indicator, event interval, namespace and source key match. The interval is start-inclusive and end-exclusive.

| Field | Meaning |
|---|---|
| expected_count | Number of obligations in the approved immutable plan |
| received_count | Planned sources with an observation record, including drafts and non-present values |
| valid_count | Received planned sources with PRESENT values that satisfy the implemented numeric rule |
| approved_count | Valid planned sources independently approved |
| pending_count | Valid planned sources not approved and not rejected, including drafts/returned records |
| missing_count | No observation, or an explicit MISSING / NOT_COLLECTED state |
| excluded_count | Planned records that are invalid, not applicable or rejected; they remain expected |
| unplanned_count | Observations whose namespace/key does not match an obligation |
| overdue_count | Unfulfilled obligations whose due instant is before the calculation cutoff |
| approval_percent | approved_count / expected_count × 100, two decimals, HALF_UP |
| complete | Every expected source is valid and approved |

The four mutually exclusive obligation outcomes are APPROVED, PENDING, MISSING and EXCLUDED. Received and valid are independent progress counts, not additional outcome partitions. An approved present zero is valid. A zero pooled denominator produces an undefined numeric result; collection completeness and numeric interpretability are separate.

FR-CAL-008's acceptance vector is executed: five expected, three approved, one pending and one missing yields 60.00% approval coverage. An extra unplanned approved observation cannot fill the gap and is excluded from the numeric result. NOT_APPLICABLE cannot silently reduce the denominator; governed eligibility exclusions are still pending.

Without an approved plan, the earlier provisional calculation behavior remains: expected_count=0 and COLLECTION_PLAN_REQUIRED. With a plan, numeric results include only eligible approved planned sources and carry PERIOD_CLOSE_REQUIRED. Even 100% collection completeness remains PROVISIONAL because governed closing, locking and official snapshots are not implemented.

Coverage is immutable at calculation time. Read-time freshness detects source revision changes or the arrival of an approved plan after an earlier calculation. Result and lineage records pin the plan revision; historical calculations are not rewritten when they become stale. The coverage panel displays counts, approval percentage and per-source status.

## HLD/LLD implementation delta

- The architecture remains a modular FastAPI application, React client and PostgreSQL store. No new service or background worker is introduced.
- measurement.py owns readiness, assignment qualification, collection-plan validation and pure coverage calculation. measurement_contracts.py generates additive schemas and policy mappings.
- CollectionPlan is a separate registry aggregate; it does not reuse operational Schedule or survey CollectionRound objects. Revision history, current heads, authorship, audit, idempotency and outbox semantics use the existing transactional store.
- Migration 0006 extends the registry kind constraint, adds component meanings to the indicator definition projection, creates collection_plan_binding with forced tenant RLS, and adds nullable result_binding.plan_revision. The binding references the approved plan revision and existing indicator/period projections. The app role has SELECT/INSERT, with no UPDATE/DELETE on plan bindings.
- Submission writes a server-controlled indicator_revision pin into the plan candidate. Draft contracts exclude that field. Immutable payload equality permits lifecycle-only indicator activation while refusing material configuration drift.
- The new read endpoints are programme readiness, typed review candidate and the minimal measurement-member directory. Calendar/geography and collection-plan list/detail endpoints follow existing authorization and pagination. Exact paths and capabilities are in API-INVENTORY.md.
- The implemented domain API grows from 67 to 83 operations. The broad design contract still contains future operations; clients should use openapi-implemented.json.
- All mutations retain tenant lock → current write authorization → idempotency → expected revision → business checks → atomic commit. Derived commands require a tenant capability grant because derived object-scope creation is not implemented. Scopes still apply to referenced records.
- Configuration.tsx contains the designer, bounded paginated selection loading, plan editor and readiness/coverage components. Sensitive authority continues to be enforced on the server.

## Non-functional implementation boundary

| Concern | Implemented / measured | Remaining qualification |
|---|---|---|
| Integrity | Immutable plan/revision pins, atomic approval binding, duplicate key checks, revision conflicts, rollback tests | Native concurrent approval/load tests |
| Isolation | Current grants, tenant-bound references, forced RLS; denied-path tests | Production login roles and threat review |
| Limits | 500 obligations/plan, 500 indicators/readiness evaluation, 500 records/type in setup UI, 1,000 principal candidates, 10,000 observations/calculation, 256 KiB request limit | Representative scale, response-time and throughput NFRs |
| Availability | Existing health checks, structured errors, transaction timeouts | HA, backups, DR, SLOs and worker recovery |
| Audit | Revisions, natural authors, decisions, audit/outbox and operation receipts | Dispatcher delivery, external audit export and retention administration |
| UX | Labelled forms, native dialogs, explicit blocked states, source tables and mobile layout | Full keyboard, screen-reader and WCAG audit |
| Security | Existing CSRF/session, capability, expiry and independence controls retained | Real IdP/MFA, privileged idle policy, key rotation and penetration testing |

The UI reports its setup cap rather than silently omitting options above 500. Legacy observation/report selectors remain bounded at 100 and need their own pagination improvements. The request-body cap may bind before the 500-obligation limit when many maximum-length strings are used.

## Upgrade and recovery

Run the normal local startup against an existing development database. Migrations 0001–0005 retain their original bytes. Migration 0006 is additive and applied once through the checksum-protected runner. No destructive reset is required. Existing results with null plan_revision remain readable; a later plan marks them stale.

Development bootstrap appends explicit new capability grants, component meanings to the synthetic definition, a matching indicator revision and a demonstration geography. Existing active managed role templates receive new immutable revisions when their capability bundle changes. Pending invitation/access requests pinned to an older template may need reissue; approved older grants are not silently replaced. This is fixture provisioning, not a production authority migration.

Back up a real database and qualify the upgrade before any production use. There is no down migration or production deployment in this delivery. For local recovery, restore a tested snapshot with its matching source version rather than editing applied migrations.

## Test scenarios and evidence

- 27 new unit/contract cases cover the five-source vector, present zero, exceptional values, unplanned observations, supported/unsupported definitions, input qualification and snapshot completeness.
- 21 new live API/SQL cases cover the complete flow, plan conflict rollback, draft/returned lifecycle, immutable approvals, current revision checks, stable retries, assignment suspension, protected server pins, source-key reservation and same/cross-tenant access.
- 11 new browser workflows exercise programme details, definition creation/approval, assignments, obligation editing/approval, activation/readiness, planned capture/review, visible coverage and mobile navigation.
- Existing 143 application checks, 143 separate reference checks and 20 prior browser workflows remain in the qualification runs. See QUALIFICATION.md for final totals and evidence.

## Next functional work

Requirement trace: this increment implements the manual subset of FR-IND-001/002 (definition and supported types), FR-IND-008 (draft review and approved immutability), FR-IND-010 (manual calculation), FR-IND-012 (assignments and explicit due obligations), FR-CAL-008 (coverage), and the Draft/Ready/Active portion of ST03. Full FR-IND-012 reassignment/escalation and complete ST03 policy readiness are not accepted as finished. The source FSD and preserved requirement catalogue remain authoritative.

Implement governed plan amendments and corrections, returned-observation editing in the UI, evidence upload/scanning, assignment reassignment and escalation, and governed period closing with immutable official snapshots. Continue native PostgreSQL and real IdP qualification before any deployment decision. Full privacy/policy readiness, targets, disaggregation, workflows, ingestion, offline capture, publication and operational execution remain open.
