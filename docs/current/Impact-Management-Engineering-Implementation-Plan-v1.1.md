# Impact Management Engineering Implementation Plan

Version 1.1   27 September 2026

This plan converts the functional design baseline into engineering work packages, dependencies, acceptance evidence and release gates. The product is the enterprise impact management platform described in the FSD dated 24 September 2026. Delivery starts with identity, tenant isolation and one durable measurement workflow. Every existing functional and nonfunctional requirement remains in the implementation register.

Original engineering baseline: edition 1.0, dated 25 September 2026. Current documentation edition: 1.1. Accountable roles are specified below; named staffing, commercial commitments and production deployment approval remain organisational assignments.

## Release interpretation

Documentation edition 1.1 is reconciled with application build 0.12.0 on 27 September 2026. The document edition and application build use different version sequences. The original business requirements and their acceptance conditions remain authoritative. No requirement has been removed or weakened to match the current code.

Build 0.13.0 increment (28 September 2026): the executable source has progressed through build 0.13.0, adding reviewed renewal of unexpired delegated authority (owner proposal, second-administrator consent, independent operator approval, readiness rechecked at each step, revocations preserved, bootstrap marker untouched). The next coding dependency becomes administrator replacement and renewal of already-expired authority through the same three-party review (v0.14), sequenced in DELIVERY-PLAN.md; external channel verification, legacy tenant adoption and unavailable-owner recovery follow. The ledger remains 74 PARTIAL and 233 PENDING. The Word copy and the implementation register workbook are unchanged and will be regenerated at the next documentation edition.

Build 0.14.0 increment (29 September 2026): the executable source has progressed through build 0.14.0, native PostgreSQL qualification (provisioned login roles, runtime guard, one migration runner, API restart persistence, CI-scale restore drill, populated schema-15 upgrade, native concurrency and login-role tests, regenerated fixture expiring 2027-09-01, per-actor signed tokens), which supplies part of gate G03. Scope decision SD-01 of 28 September 2026 (DELIVERY-PLAN.md §7) superseded the sequencing stated in the previous note: administrator replacement and renewal of expired authority move to Release 2, and the next coding slice is v0.15, the live identity provider. The ledger is 76 PARTIAL and 231 PENDING (VF-DIN-002 and VF-DR-003 PARTIAL on bounded native evidence; VF-DR-002 PENDING). The Word copy and the implementation register workbook are unchanged and will be regenerated at the next documentation edition.

Build 0.15.0 increment (29 September 2026): the executable source has progressed through build 0.15.0, live identity provider, which executes part of gate G04 against a per-run development-mode Keycloak 26.7.4 (authorization code with PKCE and nonce, TOTP step-up, fresh assurance by provider auth_time, RP-initiated and back-channel logout, JWKS bearer validation) and closes backlog items #18, #19 and #22. G04 against the owner's chosen provider, MFA enrolment, recovery and key rotation remain open. The ledger stays at 76 PARTIAL and 231 PENDING. The next coding slice is v0.16 (worker, outbox dispatcher and email adapter), in progress. The Word copy and the implementation register workbook are unchanged and will be regenerated at the next documentation edition.

Build 0.16.0 increment (29 September 2026): the executable source has progressed through build 0.16.0, worker runtime, outbox dispatcher and email adapter: a separate worker on its own login with generation-fenced leases, retries and dead-letter handling, exactly-once in-app delivery, an SMTP adapter and a synthetic sink, invitation email, recovery-channel verification, expiry reminders, cancellation of queued jobs and an operator heartbeat view. The email provider, bounce handling, SPF/DKIM, sending limits, worker-executed job classes and narrowing of the worker role remain open. The ledger stays at 76 PARTIAL and 231 PENDING. The next slice is v0.17 (deployment package), whose staging step waits on the hosting decision; v0.18 (results framework and planning) has been built ahead of it on its own stacked branch. The Word copy and the implementation register workbook are unchanged and will be regenerated at the next documentation edition.

The application is a development delivery. The requirement ledger records 74 PARTIAL and 233 PENDING requirements, with zero fully accepted. PARTIAL means a bounded implementation and some evidence exist, not that all acceptance conditions are satisfied. PENDING means the requirement has no accepted implementation coverage in the ledger; a read-only surface or reference example does not establish delivery.

Recorded qualification contains 325 application checks, 143 design-reference checks and 81 browser checks. One expired-offline-grant test is deselected and is not a pass. Local integration uses fresh in-memory PGlite PostgreSQL 17.5 with serialized transactions. Native PostgreSQL concurrency, live identity-provider assurance, disaster recovery, load qualification and production acceptance remain open.

The original BRD and FSD use R1, R2 and R3 requirement assignments. The later 16-stage delivery roadmap is an implementation sequence. Roadmap stage 1 and baseline R1 are different groupings; neither is complete. Requirement release assignments remain unchanged.

The sections explicitly marked current implementation describe this build. Retained target-design sections describe required future behavior unless the current implementation section states otherwise. Complete source, contracts, test evidence and original documents accompany this edition. Start at DOCUMENTATION-INDEX.md and TRACEABILITY.csv for exact locations and evidence boundaries.

## Updated delivery position

The executable source has progressed through build 0.12.0. Delivered increments include explicit access administration, measurement configuration and amendments, close and restatement, frozen reporting, invalidation work, controlled publication, workspace and account administration, managed-tenant lifecycle, reviewed initial access and recovery-contact evidence management. These increments do not constitute acceptance of the full baseline R1 scope.

The current ledger is 74 PARTIAL and 233 PENDING across all 307 requirements. Every original requirement, priority, acceptance condition and baseline release assignment is retained in the updated implementation register. Role owners remain proposed accountabilities; named assignees and organizational approvals are not invented.

## Next dependency and completion gates

The next coding dependency is reviewed delegation-authority renewal and extension with current authority, recovery readiness, capability and scope ceilings, expiry and independent review. It must not reset revocations or the one-time initial-access marker. Further onboarding work includes external channel verification, legacy tenant adoption and unavailable-owner recovery. Lifecycle completion still requires actual worker effects, source-credential checks, governed support and exit, export, archive and deletion.

The baseline gates G01 through G14 remain unqualified. Current evidence supports subsets of requirements, contracts, identity, measurement and web gates; native concurrency, mobile, live integrations, performance, recovery, independent security, AI and operations still require their specified environments and results. The release acceptance guide records the evidence that each owner must supply.

## Change maintenance

Every code increment must update the current documentation profile, API inventory, schema dictionary, screen coverage, requirement assessments and test evidence mapping. Preserve stable IDs and earlier document editions in history. A requirement is complete only when the full baseline acceptance and recovery behavior is met and the authorized reviewer records acceptance.

## Retained requirements and target design

The following baseline sections retain their requirement IDs and intended behavior. Implementation status is governed by the current profile above and the accompanying traceability register. Planned components are not represented as deployed services.

## 1 Baseline and authority

The FSD controls required behaviour, priorities and release assignment. The HLD controls component boundaries and reference infrastructure. The LLD controls transaction semantics, state transitions and domain invariants. This implementation package closes the specific contract gaps listed below. It does not change a requirement's release merely because a work package is scheduled earlier or later.

The source FSD contains 270 functional requirements: 220 in R1, 44 in R2 and six in R3. Its 37 nonfunctional contracts are retained independently. The register contains one implementation row for each of these 307 requirements, preserving the source acceptance condition and recovery rule. An R1 release requires all R1 obligations and its applicable nonfunctional gates; an early demonstrator is not an R1 release.

| Existing design item | Completing specification | Result |
| --- | --- | --- |
| LLD 5 and 9 open nested DTOs | API and Event Contracts and contracts/openapi.json | Typed nested objects, bounded arrays and explicit dynamic maps |
| LLD 4 and 6 reference classification | Database Migration Specification and three SQL migrations | Scalar UUID fields classified and constrained; tenant and object type relationships explicit |
| LLD 16 media transfer | API and Event Contracts section 5 | Numbered parts, replay, sealing, digest verification, expiry and recovery defined |
| LLD 25 example fixture IDs | Fixture and Acceptance Specification and fixtures/seed.sql | Deterministic identities, grants and records with a guarded loader |
| Implementation order | This plan and Implementation Register | Work packages, dependencies, role ownership and requirement acceptance |

The new API contract has version 1.1.0. It supersedes the API and SQL blueprints inside Engineering Assets v1.0. The original calculation reference and its tests remain applicable. Generic workflow PATCH is removed: domain submission commands create workflow candidates, and explicit decision commands control their lifecycle.

## 2 Delivery structure

The unit of delivery is a tested user workflow with UI, domain logic, persistence, policy, audit and recovery. A work package groups related requirements; it is not a permission to bypass dependencies or defer security. Repository and policy foundations run before domain features. Security, privacy and accessibility reviews occur within each package and are consolidated at release.

| Package | Owned modules and outcome | Dependencies |
| --- | --- | --- |
| WP00 Repository and development foundations | Build a clean checkout with deterministic dependencies, contract validation, local services and CI. | None |
| WP01 Tenant identity and access | TEN, IAM, ACC. Establish tenant lifecycle, owner custody, identity federation, invitations, sessions, scoped grants and revocation. | WP00 |
| WP02 Programme planning | PLN, PRG. Implement programme, framework, activities, risks and reporting obligations with versioned configuration. | WP01 |
| WP03 Indicators and calculations | IND, CAL. Implement definitions, targets, comparability, provenance, deterministic decimal calculations and golden examples. | WP02 |
| WP04 Forms and participants | FRM, PAR. Implement typed instruments, safe expression grammar, assignments, purpose-bound participants and consent handling. | WP03 |
| WP05 Ingestion and quality | DAT, DQ. Implement immutable source receipts, previews, mappings, row reconciliation, replacement and quality workflows. | WP02 |
| WP06 Evidence and evaluation | EVD, EVA. Implement quarantined files, versioned citations, codebooks, qualitative extracts and evaluated findings. | WP01 |
| WP07 Review and period close | WFL. Implement immutable candidates, natural-person independence, decisions, close readiness and restatement. | WP03, WP06 |
| WP08 Dashboards reports and disclosure | ANA, RPT. Implement scoped analysis, snapshot bindings, reconciled report generation and controlled publication. | WP05, WP07 |
| WP09 Android offline collection | OFF. Implement device custody, signed packages, bounded leases, local durability, resumable media and replay-safe sync. | WP04 |
| WP10 Analytical finance | FIN. Implement source transactions, budget versions, exchange rates, allocations and financial reconciliation. | WP02 |
| WP11 External integrations | INT. Implement service-owned connections, checkpointed imports, credential rotation and webhook delivery. | WP05 |
| WP12 AI assistance | AI. Implement scoped retrieval, typed proposals, exact-diff confirmation, budgets and use-case evaluation. | WP08, WP13 |
| WP13 Privacy execution | PRV. Implement purpose and disclosure policy, cases, holds, deletion manifests, store outcomes and restore replay. | WP01, WP06 |
| WP14 Security and operations | SEC, OPS. Implement security controls, observability, limits, release controls, audited support and recovery. | WP00 |
| WP15 User experience and accessibility | UX. Implement shared components and all UI states, localisation, keyboard navigation and accessibility verification. | WP01 |
| WP16 Migration and exit | MIG. Implement semantic mapping, trial imports, cutover, exports, exit custody and closure reconciliation. | WP08, WP13 |
| WP17 Cross platform qualification | Execute all NFR profiles, independent assessment, restore drills and release evidence reconciliation. | WP08, WP09, WP10, WP11, WP12, WP13, WP14, WP15, WP16 |

Dependencies indicate the minimum contracts a package consumes. For example, Android collection depends on the published form contract, but mobile interface work can begin against fixtures once that contract is stable. AI consumes reviewed calculations, evidence and privacy policy, so its consequential workflows follow those foundations. Security engineering participates from WP00 even though operational qualification continues through WP17.

## 3 First implementation sequence

Create the repository, dependency locks, contract validation and disposable database environment. Apply migrations, create separate database login identities for the declared roles, and verify that the application cannot read another tenant or alter immutable history. Implement the request context, current-policy evaluation, version checks, operation receipts, audit and transactional outbox before writing domain handlers.

Implement sign-in, invitation acceptance, tenant selection, membership suspension and scoped grants. Then implement a programme, an indicator definition, two observations, an independent review, the pooled calculation and an internal report. The visible result must be 51 divided by 110 multiplied by 100, displayed as 46.36, with source lineage. A saved response must correspond to a committed revision. A repeated operation must return its original receipt.

The first workflow must also demonstrate denied cross-tenant access, forbidden self-approval, stale-edit rejection, source correction and report freshness. This establishes the application pattern for later modules. It is an internal engineering milestone; it does not replace the remaining R1 features.

| Task | Deliverable | Acceptance |
| --- | --- | --- |
| F01 | Repository and ownership | Folders, module import boundaries, owners and lint commands present. |
| F02 | Closed contract generation | All DTO references resolve and invalid examples are rejected. |
| F03 | Database bootstrap | Fresh database applies every migration and exact rerun preserves checksums. |
| F04 | Role and scope evaluator | Deny, expiry, scope, separation and revocation fixtures pass. |
| F05 | Identity development realm | Public browser client enforces code with PKCE; redirects are exact. |
| F06 | First durable transaction | Revision, audit, outbox and receipt commit or roll back together. |
| F07 | Seed and repeatable checks | Isolated fixture loads and both tenant boundaries are tested. |
| F08 | First vertical workflow | Author captures observations; separate reviewer approves; pooled result and report show 46.36. |
| F09 | Deployment inputs | Real environment supplies permitted regions, DNS, issuer, secret references and on-call routing. |
| F10 | Release evidence manifest | Code, schema, policy, mobile, test and SBOM versions are linked to a build. |

## 4 Work item requirements

Each implementation item names its FSD ID, release, priority, owning role, package dependencies, intended behaviour, invalid or recovery behaviour, acceptance condition and test reference. The spreadsheet adds editable assignee, status and evidence fields. Status begins at Not started. A reference test pass does not change a product requirement to Done.

Split a large item into API, domain, persistence, UI and qualification subtasks while retaining the parent requirement. Track a change that affects several modules as one parent with explicit dependent subtasks. Do not duplicate source requirements under several packages and count them as separate coverage.

Ready means the consumed DTOs, permissions, state transition, data retention treatment and acceptance fixture are specified. In progress means code is being implemented. In review means the implementation and evidence are available for review. Done requires merged implementation, passing required tests and the acceptance evidence link. Blocked requires a concrete unmet prerequisite and owner. Deferred requires a recorded scope decision and cannot silently remove an R1 obligation.

## 5 Engineering ownership

The product lead controls interpretation of the FSD and acceptance of scope changes. The technical lead controls module interfaces and design consistency. Domain leads implement package behaviour. The platform lead owns environments, deployment and recovery. Security and privacy leads review access, data handling and abuse cases. QA owns independent test selection, fixture integrity and release evidence. The delivery owner resolves staffing and sequencing dependencies.

No individual must impersonate a second reviewer to satisfy separation of duties. A small team may hold several engineering roles, but production approval and sensitive business decisions still require the distinct identities specified by policy. Role titles in the documents are responsibilities, not a fabricated staffing roster.

## 6 Definition of done

A change satisfies its declared positive, negative and recovery behaviours. Its public contract is closed and versioned; generated client types match the server. Database writes preserve tenant references, optimistic concurrency, lineage and immutable records. Access is evaluated on the server and denied data is absent from responses, logs, exports and model context.

The change has useful tests at its failure boundaries. UI work covers loading, empty, denied, stale, validation, conflict, offline and failure states where applicable. Sensitive effects have current authority checks. Changes to a long job define cancellation, retries, leases and reconciliation. Migration changes have a clean install and upgrade check on PostgreSQL 17. Operational changes have usable telemetry and a runbook entry.

Documentation, policy fixtures, API examples and requirement traceability are updated together. A screenshot or successful build alone does not prove an approval, durable save, tenant boundary or offline receipt. Attach evidence from the relevant running component.

## 7 Release gates

| Gate | Release criterion | Owner |
| --- | --- | --- |
| G01 Requirements | All release-assigned requirements meet source acceptance and recovery behaviours. | Product and QA |
| G02 Contracts | Closed schemas, generated types, compatibility and policy coverage pass. | API lead |
| G03 Database | Fresh install, upgrade, checksums, real-role isolation and concurrent transactions pass. | Database lead |
| G04 Identity and access | Federation, recovery, grant issuance, revocation, purpose and independence pass. | Security lead |
| G05 Measurement | Golden corpus, source lineage and official report reconciliation pass. | Measurement lead |
| G06 Web | Complete workflows, browser matrix, keyboard, screen reader and responsive checks pass. | Frontend and QA |
| G07 Android | Qualified device matrix proves expiry, encryption, account isolation and durable sync. | Mobile and QA |
| G08 Integration | Provider scope, checkpoint, credential rotation, retry and replay tests pass. | Integration lead |
| G09 Performance | FSD peak, burst, soak and largest-tenant bounds pass with background work. | Platform lead |
| G10 Recovery | RPO and RTO measured; deletion and identity restrictions survive restore. | Platform and privacy |
| G11 Security | Independent assessment has no unresolved critical/high access or integrity failure without verified mitigation. | Security lead |
| G12 AI | Released use cases pass grounding, correctness, privacy, injection, confirmation and budget evaluation. | AI and domain leads |
| G13 Operations | Alerts, on-call route, runbooks, limits and support custody exercised. | Operations owner |
| G14 Release | Artifact, schema, policy, fixture, SBOM and evidence manifest match the release candidate. | Release manager |

A gate may be marked Not applicable only when the release scope excludes the feature and the owning role records the reason. An R1 requirement cannot become Not applicable through a test runner flag. A failed confidentiality, tenant isolation, approval integrity or official calculation gate prevents production release. Security exceptions require a specific effective mitigation and verification, consistent with the FSD; a general risk acceptance does not satisfy the technical gate.

## 8 Estimates and change control

The plan deliberately contains dependency order rather than invented calendar dates. Once named engineers and capacity are assigned, estimate the work packages using the closed contracts and acceptance cases. Reestimate when a connector, deployment jurisdiction, mobile device policy or supported language materially changes the work. Keep product scope, engineering effort and external qualification waiting time distinct.

Record changes with a decision ID, affected requirements, contract or data compatibility impact, tests, rollout and rollback treatment. Additive optional fields may be compatible; a changed calculation meaning, permission default, required field, enum interpretation or offline protocol requires explicit version handling. Feature flags do not permit incompatible stored data or weakened security.

## 9 Handoff and coding entry

The coding handoff consists of these ten specifications, the implementation register and the assets archive. Begin WP00 and WP01 using the supplied contracts and fixtures. PostgreSQL execution, running application tests, browser qualification, Android device tests and production exercises remain evidence produced during implementation. Their absence is shown in the validation report and does not change the completed specification into a claim of an implemented system.

## 10 Source records

Impact Management Platform FSD v1.0, HLD v1.0, LLD v1.0, Test Strategy v1.0 and Test Catalogue v1.0. The source FSD SHA256 is 1dccf4fbe6361c5530aef5239a880d87bf440eb5a548d31a8c32ad559b10e66a. The assets manifest records the exact bytes delivered in this package.
