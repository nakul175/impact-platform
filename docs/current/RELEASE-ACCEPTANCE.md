# Impact Platform release acceptance record

Documentation edition 1.1 is reconciled to build 0.12.0 and schema 15; the counts below are updated to the build 0.25.0 runs of 1 October 2026 (schema 27; domain API 1.15.0; control-plane API 1.6.0), with the QA 2026-10 degradation, performance and UAT slices merged onto build 0.25.0 without a version change (their full-suite figures are the CI run of the integration pull request, not recorded here). Release 1 remains in progress. The original R1/R2/R3 requirement assignments are distinct from the later delivery-stage roadmap. No full requirement or production gate is declared accepted by this update.

## Recorded development evidence

| Group | Executed and passed | Boundary |
| --- | ---: | --- |
| Application (PGlite) | 822 | Fresh in-memory PGlite, actual HTTP/SQL, build 0.25.0, 1 October 2026; 42 native-only and 16 live-provider tests skipped with a stated reason; one offline test deselected (QUALIFICATION.md) |
| Application (native PostgreSQL) | 861 | PostgreSQL 16.13, single node, API on three provisioned login roles and worker processes on a fourth, build 0.25.0, 1 October 2026; 16 live-provider tests skipped (run separately), two restart phases executed separately, one PGlite-only case; API restart, restore drill and 26→27 upgrade PASS |
| QA 2026-10 degradation | 5 PGlite + 6 native | Merged onto build 0.25.0 (QA-DEGRADATION-2026-10.md); a TCP proxy and a stub provider stand in for real outages; included in the CI run of the integration head |
| QA 2026-10 performance | one sandbox run | One native run on 2 shared vCPUs (QA-PERFORMANCE-2026-10.md, `evidence/performance-2026-10-01.json`); measurement, not a capacity statement |
| Live identity provider | 16 + 16 | Keycloak 26.7.4 per run, development mode, in-memory provider database; on PGlite and on the native login roles (recorded at build 0.20.0; later builds in CI on their integration pull requests) |
| Live identity-provider browser | 2 | Chromium sign-in with TOTP and sign-out through the provider |
| Design reference | 143 | Reference implementation only; product_validated is false |
| Browser | 140 | Compiled client, seventeen workflow groups including the axe-core accessibility scan of 43 page states (build 0.25.0); no uncaught errors in saved runs |
| Complete requirements accepted | 0 | 106 partial and 201 pending across 307 |

Evidence files remain the original run reports, with their recorded timestamps. The documentation reconciliation does not claim a new application run. These counts overlap the exact 17 integration and 12 smoke cases shown in the test catalogue; do not add those 29 again to the application total.

## Gate record

| Gate | Current position | Evidence still required | Accountable role |
| --- | --- | --- | --- |
| G01 Requirements | Partial | Full release-assigned outcomes, recovery conditions and reviewed UAT | Product and QA |
| G02 Contracts | Partial | Complete released-scope DTO, compatibility and policy coverage | API lead |
| G03 Database | Partial native evidence (v0.14, v0.15): provisioned login roles, upgrade of a populated database (0015→0016, then 0016→0017, then 0017→0018 altering a populated outbox table, then 0018→0019 altering populated framework and target projections), a worker login and two worker processes contending for leases (v0.16), raced approvals/replays/close/renewal, API restart, CI-scale restore drill | Database restart persistence, connection pooler, lock order across objects, scale, migrations that rewrite populated tables | Database lead |
| G04 Identity and access | Partial; executed against a live provider (v0.15): authorization code with PKCE and nonce, TOTP step-up, fresh assurance by provider `auth_time`, RP-initiated and back-channel logout, JWKS bearer validation, on a per-run development-mode Keycloak | The owner's chosen provider and deployment model, MFA enrolment and recovery, key rotation, provider outage, bearer-token lifetime after logout (no revocation before `exp`), acceptance of the no-refresh-token substitution, departure inventory | Security lead |
| G05 Measurement | Partial (v0.18 adds results framework, targets and targets versus actuals) | Full required measure types, golden corpus and reconciliation | Measurement lead |
| G06 Web | Partial (build 0.25.0: automated accessibility scan and keyboard-only flows in Chromium only) | Full workflows, supported browser/device matrix and accessibility review | Frontend and QA |
| G07 Android | Pending | Device authority expiry, encryption, account isolation and durable sync | Mobile and QA |
| G08 Integration | Pending | Qualified providers, scopes, credential rotation, checkpoints and replay | Integration lead |
| G09 Performance | Pending (QA 2026-10: a measurement harness, `make perf`, and one sandbox run; VF-PER-001 and VF-PER-006 PARTIAL; the synchronous 500-row import commit takes about 14 s) | Peak/burst/soak and largest-tenant bounds with background work | Platform lead |
| G10 Recovery | Pending (since build 0.25.0 verified nightly backup sets and a weekly restore drill on the staging server; no off-server copy; no RPO/RTO met) | Measured RPO/RTO on a deployed environment, deletion/grant state after restore and failure drills | Platform and privacy |
| G11 Security | Pending independent assessment | Remediated penetration test, dependency/SBOM and deployment control evidence | Security lead |
| G12 AI | Pending | Actual use-case evaluation, grounding, privacy, injection, confirmation and budget gates | AI and domain leads |
| G13 Operations | Pending (since build 0.25.0 a five-minute alert check into the status page, operator metrics and owner console scripts; QA 2026-10 adds the [support runbook](SUPPORT-RUNBOOK.md); alerts reach no person; no named on-call) | Named on-call, exercised alerts/runbooks, support custody, production limits, the chosen email provider with bounce handling, SPF/DKIM and sending limits | Operations owner |
| G14 Release | Partial packaging evidence | Immutable artifact/configuration/schema/policy/fixture/SBOM manifest and signed decision | Release manager |

Named assignees, reviewers, approval dates and accepted evidence references remain unassigned. A planned role is not a signoff. A gate can be excluded only by a recorded, authorized scope decision consistent with the unchanged requirements; a deselected test cannot waive a shared control.

## Acceptance procedure

1. Freeze the candidate build, configuration, schema, policy and fixture identities.
2. For each required baseline case, record all variants, actual results, environment, evidence and linked defects. Map exact automated test identities without inferring full-case coverage from a similarly named check.
3. Execute UAT with representative authorized users and independent control reviewers, using [`UAT-PACK.md`](UAT-PACK.md). Preserve the outcome and unresolved limitations.
4. Close or explicitly resolve defects under the baseline security and integrity rules. A general risk acceptance does not replace a required technical mitigation.
5. Complete operational and external-provider gates in the actual intended environment.
6. Record the release decision, approvers, date, scope, evidence manifest, rollback plan and remaining exclusions.

## Known limitations and issue handling

The current implementation profile and NEXT-DELIVERY.md remain the detailed backlog. High-impact open boundaries include the remainder of native database qualification (pooling, database restart, scale), the chosen identity provider with MFA enrolment and recovery, real recovery, renewal of expired authority and administrator replacement, closure, external delivery through a real email provider (the v0.16 worker has delivered only to a loopback SMTP sink and a synthetic sink), worker-executed job classes and the unimplemented product modules. What blocks Release 1 acceptance at build 0.25.0 — including the hosted-UAT blockers A1–A4 — is listed in [RELEASE-1-ACCEPTANCE-GAPS.md](RELEASE-1-ACCEPTANCE-GAPS.md). Documentation annotations are not issue closure. New regressions need reproducible steps, expected/actual results, affected build, safe evidence, owner and verification outcome.
