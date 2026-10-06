# Nonprofit AI Enablement Test Strategy

Edition 1.0   5 October 2026   Proposed qualification strategy

This strategy derives from 01-BRD.md, requirements.json and 02-FSD.md. It defines how to qualify the nonprofit AI extension and preserve the existing Impact Platform controls. The companion catalogue contains 50 scenarios and 108 detailed cases covering all 40 functional requirements. This document prepares testing; it does not record a new product run or approve the business baseline.

## Baseline and evidence limits

The inspected review baseline is commit 36073f1, build 0.30.0, schema 35, domain API 1.21.0 and platform API 1.9.0. The branch is not merged or deployed. It provides a deterministic readiness guide, dated editorial directory, comparisons, twelve practical lessons, organisation-shared Draft adoption plans, procurement notes and pilot checklists. Advisory has separate consent and current capability checks, sealed results and bounded attempts. Supplier onboarding, RFQs, competency assessment, human advisory services, engagements, AI portability and payments are target work.

The existing local qualification records 1,101 passed, seven failed, 76 skipped and one deselected. All seven failures match the unchanged Mac operations baseline. Ten local Chrome browser scenarios passed. These counts describe the whole recorded suite and do not mean all 40 new FRs, all 36 BRs or the original 307 requirements passed acceptance. No product test was run to author this documentation. Existing product evidence is referenced for the exact assertions it contains. The separate offline wireframe checks validate the synthetic prototype only.

Required release evidence remains outstanding for this candidate: the hosted local-reference-and-browser, live-identity-provider, native-postgresql-gate and container-stack jobs, followed by owner merge confirmation. PGlite and database/service fakes do not prove native role isolation, parallel transaction safety, actual identity-provider behaviour or the container deployment path. Mock-provider passes do not prove live generation quality or provider eligibility. Live generation is blocked by exhausted provider credits; no further provider request is part of this documentation work.

Evidence sources are docs/evidence/nonprofit-ai-adoption-local-suite.xml, docs/evidence/nonprofit-ai-adoption-local-summary.json, docs/evidence/ai-enablement-browser-tests.json and docs/RELEASE-0.30-ai-adoption-tool.md. Always inspect the candidate SHA and environment before reusing a result. A documentation commit added after 36073f1 is not itself an executed product candidate.

## Traceability and record keeping

Each business requirement has a BR-NPA identifier; each derived functional requirement has an FR-NPA identifier. Scenarios use SC-NPA-001 through SC-NPA-050 and cases use TC-NPA-001 through TC-NPA-108. SC-NPA-001 through SC-NPA-040 correspond to the same-numbered FR. SC-NPA-041 through SC-NPA-050 cover cross-cutting smoke, security, validation, native concurrency, performance, recovery, original-platform regression, accessibility, user acceptance and AI output quality.

The stable design inventory is test-scenarios.csv and test-cases.csv. Semicolons delimit multiple IDs. Every case begins SPECIFIED_NOT_RUN. Its evidence_status describes related existing evidence independently: NONE, RELATED_LOCAL_EVIDENCE, PENDING_NATIVE_NOT_RUN or INCOMPLETE_REQUIRES_MANUAL_REVIEW. Related local evidence can support a subset of a case's assertions; it never substitutes for executing the full newly specified case or accepting its requirement.

For an execution, create a separate test-run record with run_id, timestamp, case_id, exact candidate SHA, build/schema/API versions, environment and database engine, fixtures/content versions, harness version, actual_result, outcome, evidence_paths, defect_ids, executor/reviewer and any blocking decision. Execution outcomes are NOT_STARTED, PASS, FAIL, BLOCKED and NOT_APPLICABLE, as defined in the acceptance and change-control procedure. BLOCKED needs an exact reason; NOT_APPLICABLE needs an approved scope decision. A skip does not satisfy a required gate. Preserve original evidence and record a new run rather than overwriting a prior successful or failed result with a focused test invocation.

Before approving a baseline or release, reconcile the requirements register, FSD state models, HLD trust boundaries, LLD transactions, wireframe journeys and data dictionary against the same identifiers. Every FR must have at least a normal case and a failure/negative case. Critical state transitions need current-authority, natural-person independence, stale-version and idempotency cases where applicable. A future capability or API route cannot be invented solely to execute a test.

## Test levels and boundaries

| Level | Purpose and assertions | Environment and evidence limit |
|---|---|---|
| Unit | Pure readiness rules, closed schema validation, known identifiers, content copies, arithmetic and bounded provider parsing. Assert exact outputs and non-mutation at meaningful boundaries. | Pure Python or HTTP mock transport. No real persistence, concurrency, identity provider or model-quality inference. |
| Service unit | Save/replay ordering, authority rechecks, failed attempts, operation conflicts, sealed-result binding and key rotation. | Explicit service/database fakes. These assert service logic and call ordering, not PostgreSQL privileges or locks under load. |
| Integration | Actual API/contract/service/database flow; revision, audit, outbox and receipt rows; closed-body rejection; scoped lists and exact replay. | Fresh PGlite may cover local flow. Repeat relevant tests on native PostgreSQL for transaction/role qualification. Provider transport remains a fake unless separately authorised. |
| Native database | FORCE RLS, real non-owner runtime logins, absent tenant context, prohibited mutations, immutable history, concurrent saves and receipt collisions. | Private native PostgreSQL with provisioned application/identity/platform roles and independent transactions. PGlite or superuser access is insufficient. |
| Identity and deployment integration | Current membership, session revocation, assurance, onboarding ceilings, worker delivery, migration upgrade and container path. | Existing live identity, native and container hosted gates. These are paid or operational actions needing the applicable owner authorisation before dispatch or deployment. |
| Browser | Real UI save/reload, stale conflicts, delayed responses, mobile comparison, honest status, readonly controls and zero disabled-provider requests. | Installed Chrome local results are distinct from the required hosted Linux browser result. Use request/response and visible-state evidence, not a standalone wireframe. |
| Smoke | Fast post-build and post-approved-deployment check of navigation, deterministic assessment, one saved Draft, reload, unavailable advisory and access denial. | Executes a small critical path. A smoke pass cannot replace the full integration, native, regression or acceptance gates. |
| Regression | Existing MEL calculation, review, periods, reporting, export/publication, privacy, onboarding, workers and reuse semantics. | Run appropriate original suites on the same candidate without weakening assertions, expected values or natural-person controls. |
| Security and privacy | Cross-tenant selectors, current capability/scope, cursor binding, server-owned fields, disclosure consent, secret leakage, injection and independent approval. | Positive and adversarial synthetic actors, real-role native negatives, browser payload observation and restricted audit evidence. Do not call a real service or send a real supplier message. |
| Accessibility | Keyboard, assistive technology, zoom, mobile reflow, focus, announcements, error recovery and automated scans. | Automated violations and incomplete findings are retained separately. Manual evidence is needed for incomplete checks and full critical journeys. |
| Performance and recovery | Latency/capacity measurement, timeout/pool/lock effects, restart, ambiguous outcomes, validated restore and populated upgrade. | Native disposable environment and a defined synthetic workload. Owner-approved service levels and capacity targets are required to assert pass/fail on timing. |
| User acceptance | Stakeholders judge comprehension, task fit, quality, procurement completeness, accountable delivery and actual business value. | Agreed synthetic pilot cohort, task/rubric and explicit owner decisions. Self-recorded progress and generated drafts cannot establish acceptance. |
| AI evaluation | Accuracy, unsupported assertions, embedded instruction handling, refusal, useful corrections, harm and review effort against a pinned corpus/rubric. | Mock outputs test mechanics only. Live quality evaluation waits for approved rubric, funded provider and explicit spending permission. No automated consequential actions. |

Layer codes in the case catalogue are UNIT, INTEGRATION, BROWSER, SMOKE, SECURITY, ACCESSIBILITY, PERFORMANCE, RECOVERY, REGRESSION and UAT. A SECURITY case may use unit, API, browser or native harnesses as its prerequisites specify; the code identifies the assurance objective rather than pretending that one harness proves every layer.

## Environments test data and isolation

Use the synthetic TD-NPA fixtures listed in 06-TEST-SCENARIOS-AND-CASES.md. Tenant A and tenant B, current and revoked actors, scoped read-only staff, programme managers and separate-natural-person decision makers must be distinguishable. Governed fixture creation supplies accounts; testers do not create passwords, impersonate a person or invent a loginless/system approver. A second login bound to the same natural person is an independence-negative fixture, never an independent approver.

Keep beneficiary, patient, bank, real staff and confidential supplier records out of tests and demonstrations. Use fabricated organisations, public-text tasks and example.test/example.org recipients. A sensitive-data flag can be true while the fixture contains no real sensitive data. Hostile prompt and HTML strings remain inert test data. A synthetic credential marker is safe to test redaction; real credentials must not be printed in requests, logs, screenshots, reports or committed fixtures.

Use fresh, disposable tenant data per run, distinct operation UUIDs per original intent and the same UUID/payload for an exact retry. Record created objects and clean up only through approved fixture disposal, never destructive actions on staging business data. Fault injection, key rotation and restore are restricted to disposable isolated environments. Bind all database and HTTP evidence to the same tenant, principal and request; do not use migration-owner credentials to claim an application-role result.

For provider mechanics, use an in-process counting fake or httpx mock transport with completed, refused, malformed, timeout, redirect and failure outputs. No network access, API key or live spending is necessary. Supplier dispatch, connector trials and payments use a local fake or isolated no-money sandbox after the corresponding target contracts exist. An outbox row is dispatch intent; a recorded external receipt or party acceptance must supply delivery evidence.

For actual local or hosted execution, follow repository AGENTS.md, CLAUDE.md and docs/QUALIFICATION.md. Use a unique test port and do not let concurrent runners overwrite shared evidence. The existing script entry points and test files are the source of executable commands; this proposed catalogue adds no new runner or hidden service. Do not alter applied migrations or depend on an unavailable future schema. Target feature cases remain BLOCKED until implementation and policy are approved.

## Entry criteria

For any meaningful product test, identify the exact candidate, relevant approved or proposed requirement revision, implemented contract/state model, synthetic fixture, deterministic expected result and isolated harness. The requirement may remain proposed during development, but that test cannot be presented as final business acceptance. Unknown decisions must be declared rather than silently filled in by a tester.

For R1 acceptance, resolve pilot cohort/languages, task and quality criteria, consent/data boundary, retention limitations, provider budget if generation is included, content ownership/stable learning IDs, service levels and onboarding ceiling changes. The actual decision identifiers are in the package decision register: DEC-NPA-001, 002, 003, 009, 010, 011, 012 and 013. Current source-backed listings do not resolve eligibility or commercial obligations. An attempt cap of three per rolling 24 hours is not a monetary/token budget ledger.

R2 cases additionally depend on the relevant marketplace/operator policy, supplier verification, adviser accountability, independent procurement, competency assessors, connector scopes and outcome/feedback governance: DEC-NPA-004 through 008, 014 and 016. Purchasing is conditional R3 and specifically blocked by DEC-NPA-015 and associated commercial/procurement decisions. Case rows state their narrower dependencies. Test data and smoke scripts cannot approve any of these choices.

For paid hosted qualification, provider evaluation or operational deployment, obtain the existing required owner authorisation before dispatch. Passing document validation or choosing to test does not approve expenditure, merge, production disclosure, vendor messages or money movement. Live generation currently has a funding block. Proceed with all free isolated tests that do not depend on that block when authorised by the implementation task.

## Prioritisation regression and automation

P0 cases protect isolation, independent decision making, privacy, irreversible action boundaries, current authority, atomic writes and critical availability. P1 covers core functional journeys, field bounds, comprehension, accessibility and measured capacity. A priority is a proposed triage order; it is not an accepted severity or agreed release waiver. Run the smallest meaningful checks while implementing a change and broaden only when the change or failure warrants it. Release qualification retains all four required hosted jobs.

Automate deterministic assertions at the narrowest useful layer: exact enum/length/identifier boundaries, independent catalogue copies, request counts, sealed binding, changed-intent conflicts and write-group counts. Use API integration for closed raw JSON, current scope and atomic persistence. Use real native roles and concurrent transaction barriers for RLS/lock/receipt claims. Use the actual browser for save uncertainty, stale-head user experience, mobile controls and tenant-switch response races. Reserve representative manual checks for screen readers, comprehension, quality rubrics and business outcomes. Avoid tests that merely mirror component implementation without asserting meaningful behaviour.

Regression scope is selected by dependency, not by a favourable overall percentage. Changes to permissions, schemas, shared revisions, receipts, locks, audit or outbox invoke original review, tenant lifecycle, identity, reporting/publication, privacy and worker suites. Content changes invoke stable-ID/version/replay, sector/ranking, provenance and honest-offer tests. Web changes invoke critical journey, conflict/retry, tenant switch and accessibility checks. Provider changes invoke bounded payload, consent, timeouts, redaction, disabled-zero-call, sealed replay, failed-attempt and uncertainty checks. Native migrations invoke real-role fences, immutable guards, populated upgrade and restore.

Mercy Corps-inspired arithmetic/calendar fixtures remain regression protection rather than imported authority. Preserve pooled percentages, empty versus zero, zero denominators, disaggregation, reporting-zone boundaries and approved-only export. MSME reuse contributes a journey and delivery pattern; it does not impose factory data, fees, payment model or procurement policy on nonprofits.

## Failure uncertainty and defect handling

A failed assertion is recorded with exact candidate, minimal synthetic reproduction, expected/actual result, affected requirements, environment, evidence and impact. Assign a named owner and severity through triage. A privacy/isolation or authority bypass, self-approval, corrupted official arithmetic, duplicated financial instruction or partial atomic write blocks the affected release path. Do not relax a natural-person rule, remove a negative test, add a waiver flag or label a dangerous failure a fixture limitation.

An environment failure must be reproducible and distinguished from a product failure. The seven Mac-specific baseline failures below remain failed outcomes; matching the unchanged baseline explains their context but does not make a full local suite green. Resolve or qualify them in the supported Linux/native/container environments before release. A blocked paid job with zero executed steps is an operational/billing block, not a passing product test.

| Recorded failing assertion in qualification/test_ops_unit.py | Recorded baseline context |
|---|---|
| test_backup_set_holds_databases_roles_objects_and_a_verified_manifest | Mac operations baseline; unchanged failure |
| test_a_second_set_the_same_day_replaces_the_first_only_when_complete | Mac operations baseline; unchanged failure |
| test_disk_guard_refuses_and_reports_without_touching_the_sets | Mac operations baseline; unchanged failure |
| test_sundays_set_is_kept_weekly_by_hard_link_and_retention_prunes_oldest | Mac operations baseline; unchanged failure |
| test_plain_strips_everything_that_would_need_json_escaping | Mac operations baseline; unchanged failure |
| test_drill_restores_the_newest_set_and_skips_the_bootstrap_superuser | Mac operations baseline; unchanged failure |
| test_drill_restore_reports_a_damaged_set_or_a_failed_restore | Mac operations baseline; unchanged failure |

A lost save response is an ambiguous outcome. Retry the identical original operation/payload and retain newer local edits separately. A stale head is a semantic conflict requiring explicit reconciliation, not an automatic retry. An advisory reservation without a safely persisted result remains in-flight/unknown and needs investigation; automatic regeneration could spend twice. Do not claim exactly-once external provider execution from local idempotency. A delivery intent or payment event is reconciled with the approved external evidence model, never assumed to be final acceptance.

Accessibility evidence currently contains zero recorded serious/critical WCAG-tagged violations and two incomplete automated checks: comparison aria-prohibited-attr and discard-dialog color-contrast. Both need manual investigation using actual rendered styles/semantics. No full conformance or manual pass is claimed. Keep incomplete checks, evidence and any fix separately visible.

## Exit criteria and release decision

A development slice can be reviewable when its implemented contracts, relevant functional/negative checks and documentation agree, and unresolved issues and target scope are explicit. That status does not mean production readiness, deployment success or owner acceptance. The original 307-requirement ledger remains 113 PARTIAL, 194 PENDING and zero accepted; this documentation does not amend it.

For a release, the exact candidate must have all four existing hosted jobs green, relevant security/native/identity/container checks executed rather than skipped, identified P0 failures resolved, approved migrations/capabilities and a truthful evidence manifest. Owner confirmation is required before merge. After authorised deployment, capture actual version/health and a bounded synthetic smoke result. Passing CI for one SHA does not permit a later changed candidate without applicable qualification.

Business acceptance additionally needs approved scope and policies, satisfied requirement-specific acceptance criteria, independent decision evidence where required, manual critical accessibility results and stakeholder UAT records. Timing and quality criteria wait for DEC-NPA-010 and DEC-NPA-002 respectively; no invented percentile threshold, accuracy score or ROI is a release criterion. Remaining lower-priority issues require a recorded owner decision with limits, rather than silent omission. Privacy/isolation and independence controls cannot be waived for convenience.

Report separate counts for specified, executed, passed, failed, blocked, not run and accepted requirements. Report native and local environments separately. Do not calculate product completion by dividing passing tests by total tests, or count a generated wireframe, document, completion checkbox or mock-provider response as an implemented and accepted feature.

## Review deliverables

The review package is this strategy, the scenario/case prose, both CSV inventories and cross-links to the FSD/HLD/LLD, wireframes, data dictionary, decision register and requirements register. A subsequent execution package contains the exact candidate manifest, test-run records, immutable evidence files, defects, accessibility/manual UAT observations and gate links. A sign-off records the approving people, scope, decisions and exact requirement/implementation revisions. Test design, executed evidence, business acceptance and release authorisation remain separate records.
