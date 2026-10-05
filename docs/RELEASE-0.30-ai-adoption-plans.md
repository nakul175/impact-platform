# Nonprofit AI adoption plans

Build 0.30 component proposal; schema +1 (0035), domain API +4 operations introduced in 1.21.0. No component version bump and no acceptance-ledger promotion. These are working tenant-shared product records, pending integrated qualification and release.

## Delivered

An organisation can save a draft AI adoption plan, reopen it in another session, and update its current revision. Each plan contains the organisation's assessment profile, a shortlist of up to four source-backed solution IDs, learning-step completion marks, procurement requirements and questions, and a pilot success measure and checklist. A plan may start with an empty shortlist.

Read access uses the existing `ai.enablement.read` capability. The separate `ai.enablement.manage` capability permits saves for TENANT_ADMIN, MEL_ADMIN and PROGRAMME_MANAGER. Other readers can view shared plans within their granted scope. Existing roles receive no new approval, purchasing or deployment power.

## Contract and persistence

The four implemented operations are `GET /v1/tenants/{tenant_id}/ai-enablement/plans`, `POST` on that path, and `GET`/`PUT` on `.../plans/{object_id}`. A create request is the closed object `{operation_id,data}`; an update adds `expected_revision`. `data` is exactly `{title,profile,solution_ids,learning_completed,procurement,pilot}`. The server rejects unknown fields, unknown solution or learning IDs, duplicate selections/actions, and unbounded notes. Learning keys are `path_id:index`, with zero-based indexes into the versioned catalogue steps.

Successful saves return the platform receipt, including object and revision IDs, operation and correlation IDs, `saved_at` and `business_state: Draft`. Reads return `{object_id,revision_id,business_state,data}`. The stored data adds server-owned `content_versions` for the assessment/learning catalogue and solution catalogue. Lists accept 1–100 items per page and use existing signed, tenant/principal/route/visibility-bound 15-minute cursors; no total count is exposed.

Migration 0035 only extends the existing object-registry kind constraint to `AIAdoptionPlan`, preserving every earlier kind. There is no new tenant table, role grant or parallel storage system. Plans use the existing forced-RLS registry, immutable object revisions and operation receipts. A save acquires the tenant write lock before resolving current authority, and commits its revision, current head, audit, outbox intent and receipt together. Updates compare the expected current revision and return `CONFLICT_VERSION` for stale drafts. The service refuses selectors naming another object kind.

Replay is keyed by tenant, current principal, command and operation ID. Its fingerprint covers the submitted command and selector, independent of changing catalogue content. Exact retries return the original receipt after current read and management access is rechecked; changed input returns `CONFLICT_OPERATION`. A subsequent catalogue update does not invalidate a successful original retry or rewrite the pinned data. Receipts follow the existing seven-day expiry; expired receipts are refused rather than silently saving again.

## Limits

Every plan stays Draft. Learning marks and completed pilot actions are self-reported organisational notes; they do not certify staff skills or prove pilot outcomes. Procurement notes and shortlists do not issue orders, spend money, award a contract, approve a supplier, disclose data or deploy a system. A saved plan does not feed official impact calculations. This component makes no external provider call and needs no API credits.

Plans are tenant-shared internal notes, not a place for beneficiary records, credentials or personal data. The user interface must state this boundary. A tenant may create at most 1,000 plans in this increment. There is no deletion, archival workflow, per-person private plan, approval workflow, attachment upload or automatic data-loss prevention. Pagination reads the current permitted records and is not a frozen snapshot.

Catalogue maintainers must preserve the meaning and order of existing `path_id:index` learning keys or provide an explicit migration strategy before changing them. Updates pin the current content versions; exact receipt replay preserves the originally saved versions. Existing tenants retain their delegation ceilings and need the separately governed widening path before a newly introduced capability can be delegated. Pending initial-access requests with an older profile hash must be re-proposed.

## Reproduction

Offline checks: `.venv/bin/python -m pytest qualification/test_ai_adoption_plans.py` — **29 passed**. Focused real API/database checks: `IMPACT_PORT=8146 .venv/bin/python scripts/run.py test --pytest-path qualification/test_ai_adoption_plans_live.py` — **5 passed, 1 skipped** on 5 October 2026. The skip is the native PostgreSQL login-role test. The final focused run applied all 35 migrations and used only synthetic fixture records. The fixture reviewer also holds MEL_ADMIN, so the read-only assertion narrows that synthetic management grant temporarily and restores it afterwards; role templates are unchanged.

Named live evidence includes `test_durable_adoption_plan_save_replay_revision_and_atomic_audit`, `test_adoption_plan_readonly_tenant_revoked_wrong_kind_and_closed_data`, `test_adoption_list_pagination_and_cursor_tenant_principal_binding`, `test_scoped_adoption_reads_filter_list_and_cursors_follow_current_visibility`, and `test_adoption_exact_replay_requires_current_management_authority`. Native-only `test_native_adoption_revisions_are_fenced_immutable_and_hidden_from_platform` checks the application tenant fence, forced RLS, revision immutability and the platform object-kind boundary. It has not been executed locally. Focused PGlite evidence does not qualify concurrency, native roles, hosted identity or the container deployment path.

Ruff lint and formatting checks pass for the four owned Python files. The first focused run exposed a test-fixture role assumption, corrected by testing the existing read/management boundary without changing access policy. The final focused run passed.

## Integration notes

Owned files: `apps/api/impact_api/ai_adoption_plans.py`, `ai_adoption_contracts.py`, `infrastructure/migrations/0035_ai_adoption_plans.sql`, `qualification/test_ai_adoption_plans.py`, `test_ai_adoption_plans_live.py` and this note. The integrator owns main routes, generator registration, implemented API export, fixture capability and access-profile regeneration, Makefile test registration, the UI and shared documents. The catalogue dependency is `ai_solutions_catalog.py`, exporting `SOLUTION_IDS` and `CONTENT_VERSION`.

The integrated records should state: durable shared adoption drafts are implemented; official approval, certification, supplier transactions and automated deployment remain outside this increment. Add the five passing live cases and 29 offline cases to the execution record using the final integrated evidence. Do not promote original requirements on this component's focused evidence alone. Record schema 35 and the new migration's SHA-256 in the current dictionary; the migration introduces no new table or grant. Run the integrated suite and all hosted gates before release.
