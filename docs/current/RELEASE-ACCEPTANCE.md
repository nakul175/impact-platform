# Impact Platform release acceptance record

Documentation edition 1.1 is reconciled to build 0.12.0 and schema 15; the counts below are updated to the build 0.14.0 runs of 28–29 September 2026 (schema 16, unchanged since 0.13.0). Release 1 remains in progress. The original R1/R2/R3 requirement assignments are distinct from the later delivery-stage roadmap. No full requirement or production gate is declared accepted by this update.

## Recorded development evidence

| Group | Executed and passed | Boundary |
| --- | ---: | --- |
| Application (PGlite) | 354 | Fresh in-memory PGlite, actual HTTP/SQL, 28 September 2026; 27 native-only tests skipped with a stated reason; one offline test deselected |
| Application (native PostgreSQL) | 379 | PostgreSQL 16.13, single node, API on three provisioned login roles, 29 September 2026; two restart phases executed separately (PASS); one offline test deselected. Restore drill and schema-15 upgrade check PASS; CI job on PostgreSQL 17.11 passed for commit c759e9e |
| Design reference | 143 | Reference implementation only; product_validated is false |
| Browser | 91 | Compiled client, nine workflow groups; no uncaught errors in saved runs |
| Complete requirements accepted | 0 | 76 partial and 231 pending across 307 |

Evidence files remain the original run reports, with their recorded timestamps. The documentation reconciliation does not claim a new application run. These counts overlap the exact 17 integration and 12 smoke cases shown in the test catalogue; do not add those 29 again to the application total.

## Gate record

| Gate | Current position | Evidence still required | Accountable role |
| --- | --- | --- | --- |
| G01 Requirements | Partial | Full release-assigned outcomes, recovery conditions and reviewed UAT | Product and QA |
| G02 Contracts | Partial | Complete released-scope DTO, compatibility and policy coverage | API lead |
| G03 Database | Partial native evidence (v0.14): provisioned login roles, 0015→0016 upgrade on a populated database, raced approvals/replays/close/renewal, API restart, CI-scale restore drill | Database restart persistence, connection pooler, lock order across objects, scale, migrations that rewrite populated tables | Database lead |
| G04 Identity and access | Partial | Live federation/MFA, actual recovery, provider revocation and departure inventory | Security lead |
| G05 Measurement | Partial | Full required measure types, golden corpus and reconciliation | Measurement lead |
| G06 Web | Partial | Full workflows, supported browser/device matrix and accessibility review | Frontend and QA |
| G07 Android | Pending | Device authority expiry, encryption, account isolation and durable sync | Mobile and QA |
| G08 Integration | Pending | Qualified providers, scopes, credential rotation, checkpoints and replay | Integration lead |
| G09 Performance | Pending | Peak/burst/soak and largest-tenant bounds with background work | Platform lead |
| G10 Recovery | Pending (a scripted restore drill exists and ran at CI scale; no backup regime) | Measured RPO/RTO on a deployed environment, deletion/grant state after restore and failure drills | Platform and privacy |
| G11 Security | Pending independent assessment | Remediated penetration test, dependency/SBOM and deployment control evidence | Security lead |
| G12 AI | Pending | Actual use-case evaluation, grounding, privacy, injection, confirmation and budget gates | AI and domain leads |
| G13 Operations | Pending | Named on-call, exercised alerts/runbooks, support custody and production limits | Operations owner |
| G14 Release | Partial packaging evidence | Immutable artifact/configuration/schema/policy/fixture/SBOM manifest and signed decision | Release manager |

Named assignees, reviewers, approval dates and accepted evidence references remain unassigned. A planned role is not a signoff. A gate can be excluded only by a recorded, authorized scope decision consistent with the unchanged requirements; a deselected test cannot waive a shared control.

## Acceptance procedure

1. Freeze the candidate build, configuration, schema, policy and fixture identities.
2. For each required baseline case, record all variants, actual results, environment, evidence and linked defects. Map exact automated test identities without inferring full-case coverage from a similarly named check.
3. Execute UAT with representative authorized users and independent control reviewers. Preserve the outcome and unresolved limitations.
4. Close or explicitly resolve defects under the baseline security and integrity rules. A general risk acceptance does not replace a required technical mitigation.
5. Complete operational and external-provider gates in the actual intended environment.
6. Record the release decision, approvers, date, scope, evidence manifest, rollback plan and remaining exclusions.

## Known limitations and issue handling

The current implementation profile and NEXT-DELIVERY.md remain the detailed backlog. High-impact open boundaries include the remainder of native database qualification (pooling, database restart, scale), live identity/MFA, real recovery, renewal of expired authority and administrator replacement, closure, external delivery, actual worker effects and the unimplemented product modules. Documentation annotations are not issue closure. New regressions need reproducible steps, expected/actual results, affected build, safe evidence, owner and verification outcome.
