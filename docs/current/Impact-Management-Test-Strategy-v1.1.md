# Impact Management Platform
Test Strategy

Version 1.1 | 27 September 2026 | Qualification and execution plan

This document defines how to verify the Impact Management Platform against its FSD, HLD and LLD. It provides the execution model for the accompanying 825-case workbook and the executable reference, integration and smoke harnesses. It is intended for QA, engineering, security, SRE, mobile, data, AI evaluation and product acceptance leads.

Build 0.12.0 now has a runnable development implementation and recorded application and browser checks. Current execution is described in the implementation reconciliation below. Full product acceptance and production deployment remain pending.

## Contents

1 Coverage and traceability

2 Test levels and accountable roles

3 Environments and fixture contracts

4 Unit test design

5 Integration test design

6 Smoke testing

7 End to end and business acceptance

8 Security and privacy verification

9 Performance capacity and resilience

10 Accessibility localisation and device matrix

11 AI evaluation and change gates

12 Continuous integration and release pipeline

13 Defect evidence and release decision

14 Preparation record and next implementation work

## Release interpretation

Documentation edition 1.1 is reconciled with application build 0.12.0 on 27 September 2026. The document edition and application build use different version sequences. The original business requirements and their acceptance conditions remain authoritative. No requirement has been removed or weakened to match the current code.

Build 0.13.0 increment (28 September 2026): the regenerated counts are 353 application, 143 reference and 91 browser checks with zero failures, from make lint build test reference browser on 28 September 2026 (JUnit timestamp 2026-09-28T11:18:30-05:00; the offline case remains deselected). Authority renewal adds 28 application cases in qualification/test_authority_renewal.py and a ninth browser group of ten workflows in docs/evidence/renewal-browser-tests.json; EXECUTION-REGISTER.csv records them as APP-326 to APP-353 and WEB-082 to WEB-091. The 825-case baseline catalogue is unchanged. The Word copy and the test catalogue workbook are unchanged and will be regenerated at the next documentation edition.

The application is a development delivery. The requirement ledger records 74 PARTIAL and 233 PENDING requirements, with zero fully accepted. PARTIAL means a bounded implementation and some evidence exist, not that all acceptance conditions are satisfied. PENDING means the requirement has no accepted implementation coverage in the ledger; a read-only surface or reference example does not establish delivery.

Recorded qualification contains 325 application checks, 143 design-reference checks and 81 browser checks. One expired-offline-grant test is deselected and is not a pass. Local integration uses fresh in-memory PGlite PostgreSQL 17.5 with serialized transactions. Native PostgreSQL concurrency, live identity-provider assurance, disaster recovery, load qualification and production acceptance remain open.

The original BRD and FSD use R1, R2 and R3 requirement assignments. The later 16-stage delivery roadmap is an implementation sequence. Roadmap stage 1 and baseline R1 are different groupings; neither is complete. Requirement release assignments remain unchanged.

The sections explicitly marked current implementation describe this build. Retained target-design sections describe required future behavior unless the current implementation section states otherwise. Complete source, contracts, test evidence and original documents accompany this edition. Start at DOCUMENTATION-INDEX.md and TRACEABILITY.csv for exact locations and evidence boundaries.

## Current execution and test identity

The 825-case baseline catalogue is retained. It contains 540 functional cases, 37 nonfunctional cases, 30 journeys, 143 reference cases, 18 API integration cases, 12 smoke cases and 45 security or boundary cases. These design case IDs are not interchangeable with the names of the current automated tests. A green automated test establishes only its asserted behavior.

The revised catalogue adds current run records with exact test names and evidence paths, and requirement-level partial-coverage annotations. Broad baseline cases remain Not run until all their required variants and outcomes are executed and linked. Original integration and smoke cases that have an exact executable ID may be linked to the current run, while the offline test remains deselected. Reference passes remain labeled design-reference evidence.

## Reproduction and evidence

From the source root run make setup, then make lint build test reference browser. The test runner starts a fresh isolated synthetic fixture and produces application-tests.xml. Browser runs record the eight workflow groups in docs/evidence. The final recorded counts are 325 application, 143 reference and 81 browser checks, with zero failures in the saved runs. A documentation update does not claim a new application execution.

Current tests cover exact retry, stale revisions, natural-person independence, tenant isolation, forced RLS, unknown fields, revocation, rollback, pooled calculation, snapshot binding and reviewed publication. Recovery adds 29 application checks and nine browser workflows. Workspace regression deliberately delays the initial capabilities response until after navigation.

## Release acceptance still outstanding

Native PostgreSQL install and upgrade, concurrent approvals and revocations, distinct real service logins, live OIDC and MFA, real provider delivery, full accessibility, load and soak, backup restore, disaster recovery, external security assessment, device qualification and AI evaluation remain unqualified. Current fixtures contain synthetic identities and no production credentials. UAT approvers and dated organizational acceptance remain unassigned.

The qualification report is the current evidence authority; historical preparation reports remain unchanged under history. Release gates remain open until their complete criteria pass. The current register distinguishes partial implementation, test execution, requirement acceptance and production approval.

## Retained requirements and target design

The following baseline sections retain their requirement IDs and intended behavior. Implementation status is governed by the current profile above and the accompanying traceability register. Planned components are not represented as deployed services.

## 1 Coverage and traceability

The source baseline contains 270 functional requirements and 37 nonfunctional verification contracts, with 307 BRD mappings. The workbook preserves every parent, priority and release. It contains 540 functional cases, 37 NFR cases, 30 integrated acceptance journeys, 143 unit reference cases, 18 API integration cases, 12 smoke cases and 45 security/boundary cases. Separate scenario and traceability registers are navigation aids and are not counted as executed cases.

Each functional requirement has an intended-outcome case and a validation/recovery case. The detailed FSD acceptance fixture, behaviour and boundary contract are carried into the case. Where a contract contains several independent conditions, record each as a parameterised run variant with its own evidence; a single green status without the variant record cannot establish full coverage. The 30 AT journeys preserve cross-module outcomes that isolated feature tests can miss.

The common case record is ID, FSD/BRD reference, priority/release, scenario, preconditions/data, steps, expected outcome, execution status, evidence/run ID and defect/notes. Status is Not run, In progress, Pass, Fail, Blocked or Not applicable. Not applicable requires a recorded scope decision and cannot waive a control shared by a released feature. Requirement coverage is a traceability measure, not a mathematical proof that every possible failure has been tested.

## 2 Test levels and accountable roles

| Level | Primary owner | Purpose and boundary |
| --- | --- | --- |
| Static and contract checks | Engineering | Typed DTOs, schema compatibility, lint, dependency boundaries, secret scanning and migration review. |
| Unit and property tests | Domain engineers | Deterministic business rules, state guards, value states, policy composition and arithmetic with independent expected results. |
| Database integration | Backend and security engineers | Transactions, actual runtime privileges, RLS, constraints, numeric storage, locks and rollback under PostgreSQL. |
| API and worker integration | Engineering QA | Authenticated contracts, durable receipts, queue redelivery, external adapter boundaries and failure recovery. |
| Web and Android system tests | Product QA and mobile QA | Complete flows, offline authority, device lifecycle, errors, accessibility and localisation. |
| Security and privacy | Security and privacy leads | Abuse chains, isolation, inference, access revocation, deletion, holds and restore restrictions. |
| Load resilience and recovery | SRE and performance QA | End-to-end service targets, fairness, component failure, backup restore and regional recovery. |
| AI qualification | AI evaluation lead and domain reviewers | Grounding, citations, extraction, abstention, adversarial safety and released-language performance. |
| UAT and release decision | Product owner with independent control owners | Confirm operational usefulness, full acceptance journeys and documented residual decisions. |

Developers own fast failure feedback but do not replace independent approval for security, privacy or business acceptance. The test author and expected-result reviewer should be distinct for high-risk calculations and approval logic. Defect triage has an accountable domain owner and an explicit release disposition; moving a defect into a backlog does not waive a release gate.

## 3 Environments and fixture contracts

Use isolated development, CI integration, staging/qualification and production environments. Synthetic fixtures are mandatory by default. Anonymisation alone does not justify copying live participant records into test. Environment manifests pin code, schema, policy, calculation, connector, model/prompt/tool versions, device/browser profile, region and data seed digest. Tests record time zone, locale, network profile and random seed where relevant.

| Pack | Required data | Control |
| --- | --- | --- |
| FX01 Tenants and principals | A/B isolated tenant markers, author, reviewer, partner, privacy, admin, operator, revoked identity | Synthetic only; credentials from environment |
| FX02 Natural identity aliases | Author has two issuer/subject accounts mapped through verified identity reconciliation | Never join identities by matching email only |
| FX03 Golden mathematics | CAL01–CAL20 full corpus; raw decimals; compatible and incompatible definitions | Fixed independent expected values in FSD |
| FX04 Forms and devices | 200 questions,100 repeats,multilingual labels,25MB media,clock/reboot devices | Android profiles qualified separately |
| FX05 Imports and sources | 100k standard rows/30 fields,1M capacity,100MB files,keys,revisions,drift | Deterministic files and checksums |
| FX06 Governed publication | Draft/returned/approved candidates,locked snapshot,report,public cells 2/8/10 | Independent people and evidence manifests |
| FX07 Privacy and restore | Held item,executable deletion,old backup,index/cache/AI derivatives | Restricted synthetic markers |
| FX08 Capacity and resilience | 250 tenants,20 active,1000 users,100M total observations,20M largest tenant | Generated reproducible data; pinned region/config |
| FX09 AI qualification | At least200 representative cases/use case where feasible;20% adversarial/boundary | Held-out releases/languages; adjudicated human labels |
| FX10 API runner fixture | Dedicated mutable programme,expired bound grant,author-owned workflow,approved result | Replace every example ID; isolated staging; three mutation opt ins |

The current runner provisions deterministic synthetic identities, grants and records using the preserved fixture and explicit bootstrap adaptations. Generated tokens and credentials remain local. Native and live-provider qualification require their own authorized fixtures and environments.

API tests require IMPACT_BASE_URL and IMPACT_FIXTURE_FILE. Tokens are read from the environment names specified in the fixture. HTTPS is mandatory outside loopback. Mutation tests additionally require IMPACT_ALLOW_MUTATIONS=1, allow_mutations true in the fixture, and a runtime manifest naming a development/test/staging environment with matching fixture ID and mutation_tests_allowed true. Missing prerequisites return Blocked, not Pass. A configured but unsafe environment is an assertion failure.

## 4 Unit test design

Unit tests exercise pure rules without network, real time, database or vendor SDK. Inject clocks and IDs at ports rather than monkeypatching global behaviour. Use table-driven boundary cases for typed decimals, value states, target direction, date boundaries, coverage, policy precedence, stage quorum, lease expiry and row accounting. Use property tests where a property is stronger than a copied implementation, such as permutation invariance of compatible sums or preservation of import row totals.

The provided suite has 140 fixed JSON vectors and three canonicalisation tests. Expected values are written in the fixtures, not computed by the same function under test. Examples include 51/110 displaying 46.36%, known overlap 180 versus unknown overlap, cumulative end position 20, exact raw sum 1.005 displaying 1.01, zero denominator UNDEFINED, original/revised attainment 90%/112.5%, distinct reviewers, exact offline expiry and complementary suppression of 2/8/10.

The reference suite intentionally has a limited scope. It does not implement the full policy evaluator, cryptographic device lease, provider adapter, database or disclosure inference engine. Extend production tests to every CAL01–CAL20 variant, malformed and adversarial inputs, overflow boundaries, correction and access changes. Production arithmetic should also be compared against independently prepared high-precision calculations and known corpus outputs.

The proposed engineering gate is at least 90% branch coverage for critical calculation, authorisation, workflow and idempotency modules, plus explicit invariant and mutation-test evidence. This is a target, not an achieved metric. Coverage cannot substitute for a test that rejects self approval, prevents a tenant leak or detects rounding at the wrong stage. Avoid tests that merely assert the same constants or private implementation sequence as the code.

## 5 Integration test design

The 18 supplied API cases test unauthenticated and revoked access, tenant/path isolation, effective permissions, list limits, official result representation, delegated administration, safe missing-resource responses, credential exclusion, independent review, stale versions, forbidden state assignment, idempotent replay, concurrent edits and expired offline grants. They use standard-library HTTP clients, bounded bodies/timeouts and no automatic credential-bearing redirects.

Idempotency tests make a real unique title change, replay the identical command, compare the exact receipt, attempt changed intent under the same operation ID, and read the resulting head. A no-op update is insufficient to prove one intended effect. Concurrency tests race two distinct titles using the same expected revision and different operation IDs; exactly one wins and the other receives CONFLICT_VERSION. Both tests restore the original title through a new audited revision. A restoration failure fails the test and quarantines the fixture; history is never deleted to make the test look clean.

Database qualification additionally runs direct queries as the actual nonowner runtime role. Verify forced RLS, absent context, pool reset after rollback, composite foreign keys, object-kind checks, decimal limits, unique source identity and deferred revision/head constraints. Attempt owner/BYPASSRLS/TRUNCATE and direct partition access. Confirm that a failed command leaves no partial ordinary state and that a successful acknowledged command survives the qualified component failure model.

Worker integration delivers duplicate and reordered messages, kills a worker after commit before acknowledgement, expires its lease and resumes it after another worker obtains a new generation. Assert one intended effect, complete item receipts and rejection of stale writes. Fail the outbox dispatcher without losing committed intent. Provider tests distinguish known failure from unknown acceptance and reconcile using the upstream contract before retrying a non-idempotent effect.

Connector qualification requires vendor sandboxes or controlled stubs that model real identifiers, revisions, attachment behaviour, schema drift, rate limits and deletion semantics. A mock returning 200 for every call is insufficient. Secret rotation, scope expiry, owner departure and retry must be exercised. Real-provider contract tests are scheduled and version-pinned; missing provider access blocks that connector's release claim.

## 6 Smoke testing

The 12 readonly smoke checks cover readiness, build/schema manifest, effective tenant access, a permitted programme, official result metadata, evidence, report, form, unauthenticated denial, cross-tenant denial, bounded indicator list and revoked report denial. These are appropriate after deployment against a dedicated synthetic scope with least-privilege principals. They prove a narrow set of access and read paths, not full business completion.

Before production promotion, staging also runs a controlled vertical smoke journey: create a draft, submit complete evidence, independently approve, calculate the expected result, close a complete period, generate and approve a reconciled report, and publish to a controlled test audience. Verify receipts and audit lineage, then archive the synthetic scope. External email or publication destinations must be controlled test endpoints. This journey is specified here and in AT coverage; it is not falsely represented as implemented by the 12 readonly methods.

A failed smoke gate stops promotion or triggers the tested compatible rollback path. Do not repeatedly rerun until a transient pass hides the original failure. Capture correlation references and affected cohort, determine whether state was committed, then repair or reconcile. Production mutation probes require a separately approved synthetic scope and operational procedure; the supplied harness defaults to blocking such mutations.

## 7 End to end and business acceptance

Execute AT01–AT30 with actual users, scope and source fixtures in the release containing their dependencies. Cover programme setup through collection, correction, review, calculation, report generation and retrieval. Include cross-project and partner boundaries, owner departure, historical restatement, subscription restriction, regional recovery and tenant export. Preserve a complete run record of expected and observed results with safe evidence.

For every critical journey, vary user capacity, tenant, source mode, lifecycle, locale and error state. Read, export, approve, publish and direct-identifier rights are independent dimensions. Pairwise combinations help with ordinary configurations, but high-risk combinations such as revoked access during queued export or author alias plus delegated approval require explicit cases even if a pairwise matrix omits them.

UAT measures task completion after standard onboarding. At least 90% of representative users must complete the defined core tasks without facilitator intervention, with no observed critical data loss or disclosure error. Record where participants needed help and the exact failed task step. Do not score a task complete because the participant eventually succeeded after extensive coaching.

## 8 Security and privacy verification

The 45 boundary cases are concrete scenarios covering deny-by-default, online revocation across channels, restricted fields, purpose withdrawal, RLS, pool reuse, forged metadata, invitation races, final-owner custody, assurance, CSRF, unsafe text, outbound requests, files, streaming downloads, alias independence, approval races, snapshots, inference, imports, queues, offline time, AI, deletion, restore, audit and release gates.

Test with distinctive synthetic tenant markers in records, attachments, metadata, search, AI snippets and exports. Assert absence in unauthorised bodies, errors, counts, cached links and telemetry visible to the wrong audience. Timing differences require threat assessment; do not claim complete indistinguishability from matching status codes alone. Rate and enumeration controls must be evaluated in realistic attack sequences.

Privacy tests track every derivative store and external action. Execute deletion with a held item and one failing cleanup stage; expect partial status and restricted held content. Restore an older backup behind closed access, replay current deletion and grant state, then prove that search, AI, exports and original records cannot resurrect deleted values. Backup expiry and external-recipient acknowledgements are separate evidence items.

Map applicable ASVS 5.0 Level 2 controls, including Level 1, to tests and independent assessment. No unmitigated critical/high confidentiality, integrity or access finding may enter production. A verified effective mitigation must address the actual exploit path and have retest evidence; a policy document or planned patch is not sufficient protection.

## 9 Performance capacity and resilience

Use the FSD profile: 250 tenants, 20 active, 1000 concurrent users, largest active cohort 250, 100 million observations overall and 20 million for the largest tenant, 10000 projects and 200000 indicators. Generate deterministic compatible and restricted data with realistic distributions and attachment sizes. Report seeding duration and storage separately from measured user operations.

Run 200 operations per second baseline with a 400 operations-per-second burst lasting five minutes. Use 50% reads, 20% dashboards, 15% writes, 10% search and 5% approvals, with concurrent imports, calculation, rendering and AI work. Measure a 60-minute peak and eight-hour soak. Include cold/warm caches, narrow and broad permitted scopes, largest tenant and noisy-neighbour cases. Arrival rate is externally paced so a slowing server cannot make load disappear by slowing the test client.

Record p95/p99 per action and material cohort, error rate, timeout rate, queue depth, oldest job, CPU/memory, database waits, I/O, connection pressure and storage growth. User-to-usable completion includes internal queueing unless the parent explicitly excludes it. Partial dashboards and incomplete artifacts are not successful samples. The workbook carries every exact NFR target; do not replace them with one average response metric.

Import qualification includes 100000 rows with 30 fields within ten minutes at p95, followed by the bounded 1000-indicator recalculation within five further minutes. Export qualification includes 100000 rows or a 50-page/20-chart report within five minutes at p95, with acknowledgement within two seconds. Capacity boundaries include 199/200/201 questions, 99/100/101 repeats, exact file byte limits and one million-row asynchronous imports.

Resilience testing kills API, worker, database replica, queue consumer and provider connections around acknowledgement boundaries. Validate receipts rather than relying on UI messages. Monthly representative restores and quarterly regional disaster exercises must satisfy RPO <=15 minutes and RTO <=4 hours in allowed regions, including keys, files, configuration and governance replay. A downloaded backup archive is not a successful restore.

## 10 Accessibility localisation and device matrix

Automated accessibility checks run on all screen states, but manual keyboard and assistive-technology review cover complete processes. Include authentication, form repeats, validation summary, conflict comparison, independent review, chart alternatives, report generation and generated standard templates. Check focus order, focus restoration, live announcements, zoom/reflow, name/role/value, contrast and noncolour status indicators against WCAG 2.2 AA.

Qualify current and previous major Chrome, Edge, Firefox and Safari at release, with explicit OS and assistive-technology combinations. Pin the actual matrix in the release manifest rather than naming a permanently current version. Test core field screens at 360 pixels and common desktop widths. Complex tables may scroll horizontally if clearly labelled and keyboard usable.

Localisation fixtures include long translated labels, right-to-left text where released, non-Latin scripts, emoji, decimal comma, thousands separators, daylight-saving boundaries, source zones and exclusive period ends. Stored values and reporting membership must not change with display locale. Every blocking workflow, error and recovery string requires a released translation or an explicit supported-language restriction.

Android tests use qualified real device/OS profiles in addition to emulators. Cover reboot, app kill, storage pressure, clock rollback, account switch, device lock, lost trusted anchor, revoked reconnect, ordinary/restricted expiry and interrupted media sync. No sensitive offline qualification is claimed when the device cannot enforce the authority window.

## 11 AI evaluation and change gates

For each use case, maintain a versioned held-out set of at least 200 representative cases where feasible, with at least 20% boundary, unsupported or adversarial cases. Specialist smaller sets require explicit risk review. Label claims and citation locations independently, adjudicate disagreement and report released language/sector slices as well as aggregate results. Keep evaluation data outside prompt examples and tuning feedback used to select the candidate.

Evidence answers require at least 95% supported factual claims and 98% correct citation locations. Official numeric claims must exactly match authoritative tools. Extraction targets at least 95% field precision and 90% mandatory-field recall. Designated unanswerable cases require at least 95% correct abstention/clarification, while incorrect abstention on answerable cases stays at or below 10%. A critical unsupported consequential claim blocks the affected release regardless of averages.

Adversarial tests include indirect instructions in documents, malicious citations, cross-tenant references, tool-argument expansion, stale proposals, secrets and unsupported causal claims. The defined suite requires zero successful tenant disclosures, unauthorised tool actions or secret disclosures. This is an acceptance criterion for the tested corpus, not proof of zero real-world risk. Model, prompt, retrieval, tool or policy changes rerun qualification before controlled rollout and have a tested rollback/shutdown route.

## 12 Continuous integration and release pipeline

Pull requests run static checks, the relevant pure unit suite, contract validation and migration review. Integration CI provisions real PostgreSQL with production-like roles and isolated synthetic fixtures, then runs transaction, RLS, API and worker cases. A missing required dependency blocks the pipeline; silently skipping it must not produce a successful release gate. Test reports identify passed, failed, blocked and unrun counts separately.

Staging runs the full release-relevant regression, vertical smoke, security retests, accessibility matrix, connector contract tests and AI evaluations. Scheduled qualification runs capacity/soak, offline real-device cases, restore and disaster exercises. Use immutable artifact promotion: production receives the same image digest and configuration package that passed the gates, with environment-specific secrets supplied through approved references.

Flaky tests get an owner and root-cause investigation. A test protecting isolation, integrity or critical workflow cannot be quarantined to unblock release without equivalent verified coverage and a recorded control-owner decision. Reruns preserve the original failed evidence. Randomisation seeds, retries and injected faults are reported, so a passing run is reproducible.

## 13 Defect evidence and release decision

Severity describes impact; priority describes scheduling. Treat tenant leakage, unauthorised approval/publication, lost acknowledged data, official-number corruption and accessible deleted content as release-blocking integrity/confidentiality failures. A cosmetic layout issue can still become critical when it hides an approval caveat or makes a required accessibility workflow impossible.

A defect record includes requirement/case/variant, build and environment, minimal synthetic reproduction, expected/observed result, correlation references, affected scope, severity, owner, mitigation, fix and independent retest. Evidence avoids raw tokens, credentials and unnecessary participant payloads. Restrict security findings according to their sensitivity, while retaining enough information for accountable remediation.

Entry gates are reviewed requirements, versioned fixture/oracle, compatible environment, access/roles and observable correlation. Exit gates are all in-scope P0 and required control cases passing, no unexplained official reconciliation differences, no unmitigated critical/high confidentiality/integrity/access findings, all release-relevant NFR evidence complete, operational owners/runbooks ready and accepted residual decisions. Blocked required tests mean the release is not qualified.

## 14 Preparation record and next implementation work

The delivered package includes 825 designed cases, 30 screen wireframes, HLD, LLD, OpenAPI, data blueprint, fixed calculation/control fixtures and executable reference/API harnesses. The current run reports show 143 reference tests passed; integration planned 18 and executed zero; smoke planned 12 and executed zero. Both API suites are Blocked by missing implementation environment and fixture. Product_validated is false in all preparation reports.

The standalone prototype supports navigation, design-role/state review, local-save/sync simulation, independent candidate review, gated period close and report flow. JavaScript syntax and deterministic interaction logic can be checked without deploying a service. Browser layout, accessibility and real-device behaviour require their own qualified runs. The prototype is not a security implementation and never serves as evidence that server controls work.

Implementation teams should replace placeholders with a real isolated fixture, close nested API schemas, apply reviewed database migrations, implement adapters and then run the existing cases unchanged where their contract is still authoritative. Extend tests when implementation introduces new failure modes. Update traceability through a recorded baseline change rather than editing expected results solely to make a failing build pass.
