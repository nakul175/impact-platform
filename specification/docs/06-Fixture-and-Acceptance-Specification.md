# Impact Management Fixture and Acceptance Specification

This specification defines reproducible synthetic data, identity prerequisites and acceptance evidence for implementing the platform. The assets include a concrete fixture manifest, database seed, role grants, development identity realm and executable preparation tests. They extend the earlier reference examples into a provisionable fixture contract while preserving the distinction between prepared data and a running application.

## 1 Fixture identity and boundaries

The fixture ID is impact-acceptance-20260925-v1. Tenant A represents a water programme and tenant B an unrelated education programme. IDs are deterministic and recorded in fixtures/api-fixture.json. The loader accepts only an empty impact_dev or impact_test database, requires an explicit enable flag, and refuses to remove existing data. These records are synthetic and must never be mixed with operational participant data.

| Fixture item | Count |
| --- | --- |
| Tenants | 2 |
| Actors | 10 |
| Domain and configuration records | 506 |
| Explicit fixture grants | 471 |
| Core API integration cases | 18 |
| Read-only smoke cases | 12 |
| Real database cases | 12 |

The seed is deliberately anchored to a fixed qualification clock. The baseline ordinary grants run from 1 September to 1 December 2026; the external member expires on 23 December 2026. Run tests using the fixed 25 September 2026 test clock or regenerate and version the entire fixture consistently. Do not silently extend an expired fixture in production code or bypass expiry checks to make a test pass.

## 2 Identity and authority fixtures

| Actor | Fixture templates | Purpose |
| --- | --- | --- |
| author | AUTHOR, PROGRAMME_MANAGER, REVIEWER | Tenant A scoped acceptance |
| admin | TENANT_ADMIN | Tenant A scoped acceptance |
| partner | EXTERNAL | Tenant A scoped acceptance |
| reviewer | REVIEWER, MEL_ADMIN | Tenant A scoped acceptance |
| revoked | AUTHOR | Suspended attribution |
| enumerator | ENUMERATOR | Tenant A scoped acceptance |
| owner | OWNER | Tenant A scoped acceptance |
| privacy | PRIVACY | Tenant A scoped acceptance |
| operator | OPERATOR | Tenant A scoped acceptance |
| other_tenant | AUTHOR | Tenant B isolation |

The author deliberately also has programme-manager and reviewer fixture grants. This isolates the self-approval check: a failure must arise from shared natural-person authorship, not merely a missing reviewer capability. The independent reviewer has a distinct natural identity. Role combinations are fixture setup and do not redefine the production templates.

The revoked user retains attribution but has no active membership. The other-tenant user belongs only to tenant B. External partners have bounded read scope and cannot list memberships. No token is stored in the archive. Token environment variable names are listed in the manifest; obtain their values through the test identity provider and keep them out of reports.

The development realm includes exact loopback callback and origin entries, code flow, PKCE and no direct password grant. Establish temporary local credentials administratively and issue short-lived tokens. Production provisioning uses the institution's configured identity process, not these synthetic accounts.

## 3 Core acceptance data

The water programme has an indicator definition, bound instance, reporting period, two observations, source lineage, an official calculation, evidence metadata, a form, an assignment, a workflow candidate, a snapshot, a report template and an internal report. The observations contribute 50 of 100 and 1 of 10. The official result contains numerator 51, denominator 110, stored percentage 46.363636363636 and displayed percentage 46.36.

The report binds its numeric occurrence to the result revision and the evidence revision. The candidate workflow records the author's natural identity so self-approval must fail. A separate mutable draft programme supports replay, stale revision and concurrent edit checks without changing the baseline programme. The connection fixture contains only a secret reference. Evidence metadata marked CLEAN is synthetic acceptance setup; no live file scanner has been exercised by loading that row.

The expired offline grant ended on 11 July 2026. Its sync request uses the correct form revision and typed answer structure, allowing the test to isolate lease expiry. The device public-key marker is deliberately invalid for cryptographic use. It cannot satisfy signature, attestation, device encryption or durable sync qualification. Mobile qualification provisions real test keys on controlled devices and records those separate results.

## 4 Golden corpus and boundaries

Retain the 20 FSD CAL examples and the 143-test calculation reference suite. Cover pooled percentages, unique counts with known versus unknown overlap, cumulative endings, lower-is-better targets, missingness, units, currency rates, contribution identity, decimal limits and display rounding. Additional production tests cover every relevant combination of grouping, filters, late correction and source exclusion.

The new preparation suite verifies closed schemas, all local references, protected server fields, typed answers, missing versus zero, recipient identity choice, decimal bounds, event sequencing, policy denial, assurance edges, self-approval, multipart sizes, replay and sealed-upload rejection. These tests run against specifications and small reference functions. They do not claim production code branch coverage.

## 5 Provisioning and reset

Apply the migrations to an empty disposable database using the migration runner. Set the explicit fixture-load flag and connection, then run fixtures/load.py. Import the development identity realm and set test credentials outside the archive. Configure the application to use the fixture clock, register the fixture ID in its runtime manifest, and enable mutation tests only in development, test or staging.

The fixture clock is an injected test dependency unavailable through public production APIs. The release build cannot accept a request header that changes policy time. Both the server and test harness must name the same fixture and environment. A mismatch blocks mutation tests before they write data.

Mutation tests restore the draft title by creating an audited correcting revision. They do not erase test history. A cleanup failure quarantines that fixture instance. To reset, provision a new disposable database through the environment operator; the packaged loader does not drop or truncate an existing database. Concurrent test jobs receive separate databases or tenant namespaces.

## 6 Application integration and smoke tests

The retained 18 integration tests cover unauthenticated requests, authorised reads, cross-tenant and hidden-object denial, revoked users, bounded lists, the pooled result, partner administration denial, safe secret metadata, self-approval, stale edits, state forgery, exact replay, competing edits and expired offline sync. They require the running API and actual fixture authority.

The retained 12 smoke tests check readiness, runtime identity and selected read paths and boundaries. They are intentionally read-only. A release candidate also executes the complete staging create-to-publication workflow defined in the Test Strategy. Read-only smoke alone does not prove that new data can be saved, reviewed, calculated and published.

The database suite adds 12 tests using the actual runtime role. It covers absent tenant context, tenant-limited reads, hidden objects, immutable revisions, audit deletion, TRUNCATE, direct partitions, private identifiers, cross-tenant references, wrong object kinds, permitted writes and context reset. These are run against PostgreSQL 17 after fixture provisioning.

## 7 Fault injection acceptance

Interrupt before and after domain commit, receipt return, part storage, part receipt, upload seal, job claim, outbox publication and external acknowledgement. Restart the worker or client and reconcile the same logical operation. No accepted source row may disappear, no uploaded part may be silently replaced and no external side effect may be inferred solely from a retry timeout.

Race revocation against approval and download, correction against close, and lease takeover against job completion. The stale actor or generation must fail its final predicate. For Android, force process death, power loss, full storage, account switching, clock rollback and lost monotonic continuity. Recovery must distinguish local data from confirmed server receipts.

## 8 Evidence format

Every run records build digest, contract version, migration checksums, policy baseline, fixture ID, environment, clock, start/end time, selected cases, actual results, failures, skips and evidence artifact hashes. Screenshots are supplementary for visual behaviour; server and database receipts establish durable effects. Remove credentials and minimise personal fields from all artifacts.

Report Passed, Failed, Blocked and Not run separately. A suite that executes zero tests because its server or tokens are missing is Blocked. A contract validation pass cannot substitute for browser, mobile, load, restore or independent security evidence. The package's current execution report records exactly which preparation checks ran.

## 9 Acceptance ownership

Domain owners confirm that fixtures represent the intended meaning. QA controls repeatability and independent expected outcomes. Security reviews negative identities and privilege tests. Privacy reviews synthetic-data handling and retention. The release owner verifies that evidence corresponds to the exact deployable build and current configuration. Completed documents enable this work; implementation acceptance requires its measured outcomes.
