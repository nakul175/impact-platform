# Quality and hardening — October 2026

Two branches, both based on `main` at ffbd931 (build 0.20.0). No build or domain API version change;
no requirement status change.

- `quality/2026-10-hardening`: steps 1, 2 and 5. Merge first.
- `quality/2026-10-worker-grants` (stacked on the first): steps 3 and 4, migration
  `0025_worker_grants.sql` and platform API 1.5.0. **Merge only after 0022, 0023 and 0024**: on its
  own the migration directory has a gap (0021 then 0025), which the readiness gate, `migrate.LATEST`,
  the upgrade check and `test_version_unit.py` all refuse by design.

## 1. Intermittent failure in `test_suspension_and_missing_recovery_contact_block_renewal`

Observed once on the CI native job (PostgreSQL 17.11, commit ffbd931, 1 Oct 2026 ~01:32 UTC): the
owner's `cancel` of a pending renewal after suspension answered 200 `Cancelled` where the test expected
403; a rerun of the same commit passed.

Root cause (test defect, product correct):

- Suspension (`tenant_lifecycle.py`, transition to Suspended/Closing) sets every tenant principal's
  `auth_not_before` to the suspension instant.
- `authority_renewal.py` deliberately exempts `cancel` and `reject` from `TENANT_NOT_ACTIVE`
  (RELEASE-0.13: "The owner can withdraw a pending proposal"). The only 403 the owner's cancel can get
  here is `REAUTHENTICATION_REQUIRED`, when the caller's `auth_time` is not later than the owner
  principal's `auth_not_before`.
- The suite reuses each actor's token for up to 60 s (`qualification/conftest.py`,
  `TOKEN_REUSE_SECONDS`), shared across tests. When the author's cached token turned 60 s old between
  the suspension and the cancel (in practice at the `propose` call right after the suspension), a new
  token was minted with an `auth_time` after the cutoff, and the owner legitimately withdrew the
  proposal. Whether it happened depended only on how long earlier tests had run, which is why a rerun
  passed. The UTC date change and the relative `review_expires_at`/`expires_at` play no part, the
  suspension is read under the tenant advisory lock in the same transaction as the cancel, and the
  earlier refused `approve` calls roll back and mutate nothing.
- Reproduced deterministically on PGlite by setting `TOKEN_REUSE_SECONDS = 0`: `assert 200 == 403`.

Fix: the test pins the owner's `auth_time` five seconds before the suspension and asserts
`REAUTHENTICATION_REQUIRED`; a new test
(`test_owner_who_authenticated_after_suspension_may_withdraw_a_pending_renewal`) records the
documented behaviour that an owner who authenticated after the suspension may withdraw.
`qualification/test_authority_renewal.py`: 29 passed on PGlite.

## 2. Single version source

- `VERSION.json` (repository root): `build`, `domain_api`, `platform_api`, `documentation_edition`.
- `apps/api/impact_api/version.py` reads it and exports `BUILD`, `DOMAIN_API`, `PLATFORM_API`,
  `DOCUMENTATION_EDITION` and `SCHEMA`. `SCHEMA` is never a literal: it is the number of files in
  `infrastructure/migrations` — the same rule `scripts/migrate.py` uses for `LATEST`.
- Readers: `main.py` (FastAPI version, `/health/ready` gate `version != SCHEMA`, runtime manifest
  `build_id`/`schema_version`/`api_version`), `worker.py` (heartbeat build), `tenant_contracts.py`
  (platform API), `scripts/build_contracts.py` (published domain API version of `openapi.json` and
  `access-policy.json`), `scripts/build_completion_ledger.py`, `scripts/package_source.py` (archive
  name), `tools/browser/tenant-check.mjs`, `qualification/test_worker.py` and `test_native_worker.py`.
  `deploy/Dockerfile` copies `VERSION.json` into the image.
- `qualification/test_version_unit.py` (added to `make unit`; also collected by `make test`) fails
  when: a key is missing or malformed; migration numbers are not contiguous from 0001 (so the count
  would differ from the highest applied version); `apps/web/package.json` or its lock differ from the
  build; the generated contracts carry a different domain or platform version (contracts not
  regenerated); a runtime module repeats the build literal or the readiness gate a number.
- The per-feature `*_contracts.py` `x-contract-version`/`VERSION` values record the API version that
  introduced each route and stay as they are; `build_contracts.py` overwrites the published version.
- Contracts regenerate byte-identical; the values are unchanged.

## 5. Small fixes

- `tenant_lifecycle.py`: owner-independence check is one `str(...) == str(...)` comparison (the
  UUID-to-str clause was always false).
- `tools/browser/prepare.mjs`: runs `$PYTHON` or `python3`.
- `scripts/idp.py`: docstring now says the foreign realm's author carries a subject derived from the
  author's.
- `.github/workflows/qualification.yml`: `actions/checkout@v6`, `setup-python@v6`, `setup-node@v6`,
  `setup-java@v5`, `cache@v5`, `upload-artifact@v6`; each tag's `action.yml` was read and declares
  `runs.using: node24` (`upload-artifact@v5` is still node20, so v6 is the first Node 24 major).
  Newer majors exist (checkout/setup-python/setup-node/upload-artifact v7, setup-java/cache v6); they
  were not adopted without reading their breaking changes.

## 3. Narrowing `impact_worker` (migration 0025, part 1)

What the build 0.20.0 worker touches, read from `worker.py`, `store.write`/`store.audit` and
`delivery.enqueue` (every SQL statement), and the privileges it keeps:

| Table | Kept | Why |
|---|---|---|
| `object_registry` | SELECT, INSERT (UPDATE revoked) | reminder notices and their audit events are new objects; the reminder scan joins lifecycle |
| `object_revision` | SELECT, INSERT | revisions of those objects; `audit` reads the revision number |
| `notification_current` | SELECT, INSERT (UPDATE revoked) | reminder projection; IN_APP recipient recheck |
| `audit_event_current` | SELECT, INSERT | audit projection |
| `tenant_principal` | SELECT, INSERT (UPDATE revoked) | SERVICE principal `ON CONFLICT DO NOTHING`; recipient and administrator checks |
| `membership_current` | SELECT (INSERT, UPDATE revoked) | reminder recipients hold an active membership |
| `outbox_event` | SELECT, INSERT | intents and `object.changed` events of the notices |
| `outbox_delivery` | SELECT, INSERT, UPDATE | claims, fenced outcomes |
| `consumer_receipt` | SELECT, INSERT | `worker.in_app` |
| 0018 grants | unchanged | `notification_delivery`, `recovery_channel_challenge`, `member_invitation`, `grant_authority`, `worker_heartbeat`, `authority_reminder`, EXECUTE `worker_tenants` |

Revoked entirely (`REVOKE ALL`, one statement per table, 66 tables): `a_i_task_current`,
`allocation_rule_current`, `assignment_current`, `audit_batch_root`, `budget_line_current`,
`calculated_result_current`, `connection_current`, `dashboard_current`, `dataset_current`,
`decision_current`, `deletion_ledger`, `device_current`, `dimension_current`, `disclosure_current`,
`evaluation_current`, `evidence_current`, `exchange_rate_current`, `file_blob`,
`finance_transaction_current`, `form_current`, `form_field_current`, `framework_current`,
`funding_agreement_current`, `grant_current`, `handling_record_current`, `import_job_current`,
`indicator_definition_current`, `indicator_instance_current`, `lineage_edge`, `observation_current`,
`offline_grant`, `operation_receipt`, `organisation_unit_current`, `participant_current`,
`period_current`, `privacy_case_current`, `privacy_store_action`, `programme_current`,
`qualitative_extract_current`, `quality_issue_current`, `retention_hold`, `retention_policy_current`,
`review_decision`, `schedule_current`, `scope_definition`, `scope_member`, `service_event_current`,
`service_identity`, `snapshot_current`, `snapshot_member`, `source_key_registry`,
`source_revision_receipt`, `submission_current`, `subscription_current`, `support_request_current`,
`sync_receipt`, `target_current`, `tenant_current`, `tenant_root` (SELECT and the column
`UPDATE(policy_epoch)` of 0013; tenant discovery uses the definer `worker_tenants`),
`tenant_schedule_hold`, `upload_part`, `upload_session`, `webhook_delivery`, `work_item_current`,
`workflow_author`, `workflow_current`.

Deferred (not touched; follow-up after 0024 lands, which grants the worker explicit export-job
privileges): `job`, `job_item`, `report_current`, `report_template_current` (still SELECT, INSERT,
UPDATE from 0003). No other granted table name matches report/package/publication/artifact/job.

Why explicit per-table REVOKEs are safe beside 0022-0024: a REVOKE removes only what it names. The
0024 draft (read in its worktree, not yet pushed) grants the worker `job`, `job_item`,
`report_export`, `report_export_artifact`, `report_package_binding` and `object_revision`; none is
revoked here (`object_revision` keeps SELECT, INSERT). 0022 and 0023 grant the worker nothing.
Foreign-key checks run as the table owner and no row-level policy reads another table, so nothing
else is needed.

Tests: `test_worker.py::test_worker_role_holds_no_privilege_migration_0025_revoked` (parses every
REVOKE of 0025 and checks `has_table_privilege` for each privilege, the tenant_root column grants,
and that the used privileges remain), `test_worker_role_is_refused_on_revoked_tables` (SET ROLE
impact_worker refused on a sample, PGlite and native), and the native-only
`test_native_worker.py::test_native_worker_login_cannot_touch_tables_revoked_by_migration_0025`
(the provisioned `impact_worker_login`).

## 4. Operator re-queue of held or DEAD deliveries (platform API 1.5.0, migration 0025, part 2)

- `GET /v1/platform/deliveries[?tenant_id=]` (`list_delivery_attention`): operator only (others 404);
  dispatchable rows that are DEAD, or held by a suspension and PENDING/LEASED, at most 50, newest
  attempt first; tenant name and lifecycle state, channel, template, state, held, attempts, last
  error class, last attempt, `revision` (the lease generation) and `permitted_actions`. No address,
  reference, token or payload.
- `POST /v1/platform/tenants/{tenant_id}/deliveries/{event_id}/actions/{requeue|release}` with
  `{operation_id, expected_revision, data: {reason}}` (closed schema; `expected_revision` is the
  decimal lease generation): operator only (404), fresh assurance (403 `FRESH_MFA_REQUIRED`), reason
  required (422), the platform operation lock then the tenant advisory lock, exact replay returns the
  original receipt and a changed payload is `OPERATION_REUSE` (409), tenant must be Active (403
  `TENANT_NOT_ACTIVE`), unknown or non-dispatchable row 404, stale revision 409, wrong state 409
  (`DELIVERY_NOT_DEAD`, `DELIVERY_NOT_HELD`, `DELIVERY_NOT_PENDING`). `requeue`: DEAD to PENDING with
  a fresh attempt budget (attempts 0), released from any hold, due now. `release`: held PENDING to
  unheld, due now. Both advance the lease generation, so a stale worker outcome matches nothing.
  `platform_event` (`delivery-requeue` / `delivery-release`, with the previous state, attempts and
  error class) and `platform_receipt` commit in the same transaction.
- The control plane still cannot read or write the outbox: migration 0025 adds the SECURITY DEFINER
  functions `operator_delivery_attention(uuid,integer)` and
  `operator_requeue_delivery(uuid,text,bigint)`, EXECUTE to `impact_platform` only, reading through
  the owner-only policies of 0018 and updating under `tenant_fence`.
- The worker still rechecks every intent before sending: a re-queued invitation whose generation was
  superseded or expired becomes SUPERSEDED, never sent. FR-TEN-001 holds: nothing is replayed
  automatically; each row is a separate reviewed decision.
- UI: the tenant-lifecycle console's Workers area gains "Deliveries needing attention" (operators
  only) with per-row Re-queue / Release hold, a required reason, an operation identifier kept for
  retries of the same payload, and plain-language conflict messages. No browser check was added
  (browser suites are not run locally); `tenant-check.mjs` is the place for one.
- Tests: `qualification/test_delivery_requeue.py`, 4 tests: re-queue then worker delivery, replay and
  reuse, stale revision, wrong action; operator only, fresh assurance, closed body, unknown
  row/tenant/action; release of a held row then delivery; a Suspended tenant's row listed with no
  action and refused, then re-queued after reactivation.

## Tests run locally (PGlite, focused files only)

| Run | Result |
|---|---|
| `test_authority_renewal.py` | 29 passed |
| original test with `TOKEN_REUSE_SECONDS = 0` (reproduction, not committed) | 1 failed (200 == 403) |
| `test_worker.py` | 31 passed |
| `test_tenant_lifecycle.py` | 14 passed |
| `make unit` | 230 passed, 37 skipped (branch 1) |
| `make lint` | clean |

Branch 2 was run with temporary empty placeholder migrations 0022-0024 (not committed), on PGlite and
on a private native PostgreSQL 16.13 cluster with the provisioned login roles:

| Run | Result |
|---|---|
| `test_worker.py` (PGlite) | 33 passed |
| `test_delivery_requeue.py` (PGlite) | 4 passed |
| native `test_native_worker.py` | 9 passed |
| native `test_worker.py` | 32 passed, 1 skipped |
| native `test_native_roles.py` | 11 passed |
| native `test_native_concurrency.py` | 11 passed |
| native `test_delivery_requeue.py` | 4 passed |
| `make unit` without placeholders | 1 failed by design (`test_version_unit` contiguity: 0021 then 0025) |

Full, browser, native and live-provider suites run in CI on push.

## Integration notes

Shared files touched by this branch: `Makefile` (unit target gains `qualification/test_version_unit.py`),
`deploy/Dockerfile` (one `COPY VERSION.json`), `apps/api/impact_api/main.py` (import plus three
version sites), `worker.py` (one import), `tenant_contracts.py` (one import and the info version),
`scripts/build_contracts.py`, `scripts/build_completion_ledger.py`, `scripts/package_source.py`,
`tools/browser/tenant-check.mjs`, `tools/browser/prepare.mjs`, `scripts/idp.py`,
`.github/workflows/qualification.yml`, `qualification/test_worker.py`, `test_native_worker.py`,
`test_authority_renewal.py`.

How the version source works for the other branches:

- A new migration `00NN_<topic>.sql` needs no version edit: readiness, the runtime manifest, the
  upgrade check and the restore drill all derive the schema from the file count. Keep numbering
  contiguous (the unit test enforces it) and still append the migration and its SHA-256 to
  `CURRENT-DATA-DICTIONARY.md`.
- The integrator bumps the build in `VERSION.json` and `apps/web/package.json` + `package-lock.json`
  (the unit test fails until all three agree), and the domain API in `VERSION.json` only, then runs
  `python scripts/build_contracts.py && python scripts/export_implemented_api.py` (the unit test fails
  if the contracts were not regenerated). Branches that resolved conflicts on the old literals in
  `main.py` (`version != 21`, `"impact-0.20.0"`, `"1.13.0"`) take this branch's lines.

Branch 2 adds: `infrastructure/migrations/0025_worker_grants.sql`, the 0025 row and source in
`docs/current/CURRENT-DATA-DICTIONARY.md` (appended after 0021; place it after 0024 when combining),
`VERSION.json` (`platform_api` 1.5.0), `packages/contracts/openapi-platform.json` (regenerated),
`apps/api/impact_api/main.py` (two routes), `tenant_contracts.py` (one import and one call),
new `requeue_contracts.py`, `delivery_operations.py`, `qualification/test_delivery_requeue.py`,
`apps/web/src/Workers.tsx`, `qualification/test_worker.py`, `qualification/test_native_worker.py`.
Order: the 0022, 0023 and 0024 branches, then this one; rerun `make unit` (the contiguity check) and
the native job.

Lines for the shared documents (the integrator applies them):

- CLAUDE.md §8 "Version literals to bump together": replace with "Build, domain API and platform API
  live in `VERSION.json` (plus `apps/web/package.json` and its lock for the build; checked by
  `qualification/test_version_unit.py`); the schema version is the migration count."
  §11 drop the tenant_lifecycle UUID/str and prepare.mjs `python` items and the scripts/idp.py
  docstring item; §1 "Evidence": one more authority-renewal test.
- IMPLEMENTATION.md: "Versions are read from `VERSION.json`; the readiness gate expects the number of
  migration files."
- QUALIFICATION.md: test counts move by +1 application test (`test_authority_renewal.py`) and +5 unit
  checks (`test_version_unit.py`); record the root cause of the renewal-cancel flake.
- CHANGELOG.md: "Quality: deterministic renewal-cancel test; single version source; Node 24 CI actions;
  small fixes (tenant_lifecycle comparison, prepare.mjs python3, idp.py docstring)."
- NEXT-DELIVERY.md / DELIVERY-PLAN open items: "a single version source" (v0.17) is delivered;
  from v0.16 "narrowing `impact_worker`'s 0003 grants" is delivered except `job`, `job_item`,
  `report_current`, `report_template_current` (after 0024), and "an operator re-queue for held/DEAD
  rows" is delivered.
- CLAUDE.md §6: "0025 narrows `impact_worker` to the tables worker.py touches (job, job_item,
  report_current, report_template_current deferred) and adds the definer functions
  `operator_delivery_attention` and `operator_requeue_delivery` for `impact_platform`"; §5/§11 drop
  "no operator re-queue exists" and "`impact_worker` still holds migration 0003's ... grants";
  platform API 1.5.0 (34 operations, was 31) in §1, §2 and the header.
- CURRENT-API-INVENTORY.md: `GET /v1/platform/deliveries`, `POST
  /v1/platform/tenants/{tenant_id}/deliveries/{event_id}/actions/requeue|release`.
- IMPLEMENTATION.md / QUALIFICATION.md: the two sections above; +4 application tests
  (`test_delivery_requeue.py`), +2 in `test_worker.py`, +1 native-only in `test_native_worker.py`.
- CHANGELOG.md: "Worker privileges narrowed (0025); operator re-queue/release of held or DEAD
  deliveries; platform API 1.5.0."
- SCREEN-COVERAGE.csv: Workers panel gains "Deliveries needing attention" (no browser check yet).
- Threat model: TH10 (worker login boundary) narrower; TH31 unchanged.
