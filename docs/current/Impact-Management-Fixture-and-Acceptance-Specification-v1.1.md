# Impact Management Fixture and Acceptance Specification

Version 1.1   27 September 2026

This specification defines reproducible synthetic data, identity prerequisites and acceptance evidence for implementing the platform. The assets include a concrete fixture manifest, database seed, role grants, development identity realm and executable preparation tests. They extend the earlier reference examples into a provisionable fixture contract while preserving the distinction between prepared data and a running application.

## Release interpretation

Documentation edition 1.1 is reconciled with application build 0.12.0 on 27 September 2026. The document edition and application build use different version sequences. The original business requirements and their acceptance conditions remain authoritative. No requirement has been removed or weakened to match the current code.

Build 0.13.0 increment (28 September 2026): the runner now applies sixteen migrations. The regenerated full application run has 353 passing tests and one deselected offline test; the reference report has 143 passing design assertions; nine browser groups contain 91 passing workflows without uncaught page errors. Renewal qualification (qualification/test_authority_renewal.py, 28 cases; tools/browser/renewal-check.mjs, ten workflows) covers owner-only proposal, second-administrator eligibility and alias independence, expiry bounds, removed and revoked ceilings, drifted pins, expired review windows, operator independence, exact retry, one live request per tenant, suspension and missing recovery evidence, runtime-role privilege boundaries and rollback after an injected failure. Edition 1.1 figures elsewhere describe build 0.12.0. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.14.0 increment (29 September 2026): the synthetic fixture was regenerated on 28 September 2026 with scripts/redate_fixture.py: every fixture grant, delegation ceiling, role assignment, platform operator and deployment qualification now expires at 2027-09-01T00:00:00Z (FIXTURE_EXPIRES_AT in scripts/fixture_support.py; ordinary grants still start on 1 September 2026, and the one external membership now also ends on 2027-09-01), 472 revision payloads were re-hashed after all 507 existing hashes were verified, records.json was rewritten, api-fixture.json carries fixture_version 2026-09-28 and fixture_expires_at, and fixture_id is unchanged; the earlier 1 December and 23 December 2026 instants stated in §1 describe the edition-1.1 fixture. scripts/run.py refuses to start within 90 days of the expiry or when the stamp and the constant disagree, and the qualification suite mints one signed token per actor on demand instead of at suite start. Fixture targets include impact_test_<suffix> for parallel native databases. Regenerated counts: 354 passed / 27 native-only skipped / 1 deselected on PGlite; 379 passed / 2 restart phases run separately / 1 deselected on native PostgreSQL 16.13 (qualification/test_native_roles.py 11, test_native_sessions.py 3, test_native_concurrency.py 11, test_native_restart.py 2); 143 reference assertions; 91 browser workflows. Edition 1.1 figures elsewhere describe build 0.12.0. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.15.0 increment (29 September 2026): the fixture is unchanged (fixture_version 2026-09-28, expiry 2027-09-01). For live identity-provider runs the bootstrap re-points the auth_identity rows whose subjects exist in the Keycloak qualification realm from the fixture issuer to the realm issuer; identity identifiers, natural persons, memberships and grants are untouched. The realm (tools/idp/qualification-realm.json) is derived from specification/environment/keycloak-dev-realm.json with the same users, subjects and enabled flags; admin, owner and reviewer hold a TOTP credential, the author holds provider roles the platform must ignore, and passwords and TOTP secrets are generated per run into a 0600 file and never recorded. Regenerated counts: 372 passed / 43 skipped / 1 deselected on PGlite; 397 passed / 18 skipped / 1 deselected on native PostgreSQL 16.13; 16 + 16 live-provider tests; 143 reference; 91 + 2 browser workflows. Edition 1.1 figures elsewhere describe build 0.12.0. The Word copy is unchanged and will be regenerated at the next documentation edition.

The application is a development delivery. The requirement ledger records 74 PARTIAL and 233 PENDING requirements, with zero fully accepted. PARTIAL means a bounded implementation and some evidence exist, not that all acceptance conditions are satisfied. PENDING means the requirement has no accepted implementation coverage in the ledger; a read-only surface or reference example does not establish delivery.

Recorded qualification contains 325 application checks, 143 design-reference checks and 81 browser checks. One expired-offline-grant test is deselected and is not a pass. Local integration uses fresh in-memory PGlite PostgreSQL 17.5 with serialized transactions. Native PostgreSQL concurrency, live identity-provider assurance, disaster recovery, load qualification and production acceptance remain open.

The original BRD and FSD use R1, R2 and R3 requirement assignments. The later 16-stage delivery roadmap is an implementation sequence. Roadmap stage 1 and baseline R1 are different groupings; neither is complete. Requirement release assignments remain unchanged.

The sections explicitly marked current implementation describe this build. Retained target-design sections describe required future behavior unless the current implementation section states otherwise. Complete source, contracts, test evidence and original documents accompany this edition. Start at DOCUMENTATION-INDEX.md and TRACEABILITY.csv for exact locations and evidence boundaries.

## Current fixture and execution contract

The preserved specification fixture is the source of stable synthetic identities and records. scripts/bootstrap.py adapts it with explicit additional revisions, system roles, grants, managed-tenant operator qualification and local sign-in configuration. This is a development fixture, not a real identity-provider deployment or production data migration.

The runner starts a fresh isolated in-memory PGlite instance for qualification, applies all seventeen migrations and creates the application. Current tests use the actual HTTP service, SQL roles, RLS, immutable revisions and transaction rollback. Browser checks use the compiled client. Credentials, private keys, local databases and tokens are excluded from release archives.

## Recorded acceptance evidence

The saved full application run has 325 passing tests and one deselected offline test. The reference report has 143 passing design assertions. Eight browser groups contain 81 passing workflows without uncaught page errors. Recovery-specific qualification covers wrong actors, alias independence, schema closure, time limits, current identity cutoffs, stale revisions, exact retry, atomic replacement, revocation and repair while Suspended.

An injected failure proves recovery-contact replacement leaves the old contact and events unchanged with no receipt. Initial-access fault injection proves no membership, grants, authority, applied marker or receipt survives an aborted provision. These checks establish local transactional behavior; they do not qualify native concurrent schedules or downstream worker effects.

## Acceptance remains separate

The 825 baseline cases retain their original expected outcomes. Current automated run names and evidence are recorded separately and mapped conservatively. Any multi-condition case needs all variants before a full pass. Organizational UAT, live providers, real devices, native persistence and upgrades, load, accessibility, restore drills and independent security remain open. Named acceptance owners and signatures are not supplied by automated execution.

## Retained requirements and target design

The following baseline sections retain their requirement IDs and intended behavior. Implementation status is governed by the current profile above and the accompanying traceability register. Planned components are not represented as deployed services.

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
