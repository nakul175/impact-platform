# Delivery plan from build 0.13.0

Prepared 28 September 2026 against documentation edition 1.1, build 0.13.0, schema 16, domain API 1.10.0 and control-plane API 1.3.0. Owner: product lead. This plan sequences the remaining work; it does not change any requirement, release assignment or acceptance condition, and it declares nothing accepted. The requirement ledger stays the record of coverage: 74 PARTIAL, 233 PENDING, 0 accepted of 307.

Planning sources: [remaining work](NEXT-DELIVERY.md), the [engineering implementation plan](current/Impact-Management-Engineering-Implementation-Plan-v1.1.md) (work packages WP00–WP17, gates G01–G14), the [release acceptance record](current/RELEASE-ACCEPTANCE.md), the [completion ledger](COMPLETION-LEDGER.md) and the increment records `RELEASE-0.2.md` to `RELEASE-0.13.md`.

## 1. Planning rules

1. An increment is one reviewed slice with its own release note, migration(s), tests, browser check, evidence and documentation update, delivered through one pull request. The v0.10–v0.13 records are the template.
2. Every increment updates, in the same change: the requirement ledger groups, the implemented contracts and API inventory, the migration dictionary, the implementation profile, the user/administrator/operations guides, screen coverage, the execution and traceability registers, the qualification record, the next-delivery record and the change record. Migration bytes, requirement IDs, historical run dates and prior editions are preserved.
3. A requirement moves from PENDING to PARTIAL only with source and executed test evidence; it is never marked accepted by an increment. Acceptance follows the procedure in the release acceptance record with named approvers.
4. Effort is given as a size band, not a date: **S** (one increment of the v0.12/v0.13 kind: one new control-plane or domain workflow, one migration, 20–30 tests), **M** (two to three coupled workflows or a first infrastructure integration), **L** (a new subsystem such as a worker, an object store or a device client), **XL** (a module family). Calendar durations depend on the team the owner assembles and must be calibrated on the first two increments delivered under this plan; no date in this document is a commitment.
5. Infrastructure gates are tracked separately from feature increments. A feature increment may deliver a bounded local implementation of a capability whose gate is still open, provided the release note says so.

## 2. Release 1 — tenant and user administration (in progress)

Delivered so far: v0.2 access administration, v0.5 period close, v0.6 frozen reports, v0.7 work centre, v0.8 controlled publication, v0.9 workspace/account/ACR, v0.10 tenant lifecycle, v0.11 initial access, v0.12 recovery contacts, v0.13 reviewed renewal of delegated authority.

| Increment | Scope | Requirements touched | Size | Depends on |
|---|---|---|---|---|
| v0.13 (done) | Owner-proposed, second-administrator-consented, operator-approved extension of unexpired delegated authority; readiness rechecked at proposal, consent and approval; revocations preserved; bootstrap marker untouched | FR-TEN-001, FR-IAM-008, FR-IAM-009 | S | v0.11, v0.12 |
| v0.14 | Administrator replacement and additional authority recipients: replace a revoked, expired or unavailable second administrator; add a further reviewed holder; renewal of authority that has already expired through the same three-party review | FR-TEN-001, FR-IAM-009, FR-IAM-014 | S | v0.13 |
| v0.15 | External recovery-channel verification and external invitations: a provider adapter interface with a local synthetic provider, verified-channel evidence on contacts and invitations, delivery attempts recorded as intent; live provider qualification stays a gate | FR-IAM-001, FR-IAM-007, FR-TEN-001 | M | v0.12, outbox dispatcher (§4) |
| v0.16 | Legacy tenant adoption: reviewed migration of fixture-created and unmanaged tenants into the control plane with custody, contact and authority evidence | FR-TEN-001, FR-TEN-010 | S | v0.13 |
| v0.17 | Unavailable-owner recovery: independently verified contact evidence, two separate approvers, audited fail-closed custody transition, no operator bypass | FR-TEN-010, FR-IAM-007 | M | v0.12, v0.14, v0.15 |
| v0.18 | Lifecycle completion: real worker cancellation, source-credential rechecks, support and exit access, closure export/archive/deletion | FR-TEN-001, FR-ACC-008, FR-PRG-008, FR-PRV-005 | L | worker runtime (§4) |
| v0.19 | Account and access acceptance: expiry notices and jobs, provider logout and refresh-token revocation, shared-device mode, idle-draft timeout warning, access certification, complete departure inventory, key rotation procedure | FR-IAM-006, FR-IAM-008, FR-IAM-011, FR-IAM-014, FR-SEC-006 | M | v0.15, live identity provider (§4) |
| v0.20 | Organisation reorganisation acceptance: future-effective moves, affected-obligation preview, historical context, documented scope semantics | FR-TEN-002, FR-ACC-011 | S | none |

Release 1 exit conditions (from the release acceptance record): every R1 requirement in the TEN, IAM and ACC families at PARTIAL with evidence or explicitly deferred by a recorded scope decision; gate G03 (database) executed natively with separate login roles; gate G04 (identity and access) executed against a live provider with MFA; UAT with representative users and named approvers; the security assessment items that concern identity and tenancy remediated. None of these is claimed today.

## 3. Releases 2–16 (planned)

The roadmap order is retained. Each row names the requirement families, the platform capability that must exist first, and the size of the family as a whole.

| Release | Scope | Families | Prerequisite capability | Size |
|---|---|---|---|---|
| 2 | Security and privacy foundations | SEC, PRV, remaining ACC | secrets management, encrypted managed artifact storage, penetration test, SBOM | L |
| 3 | Programme planning | PLN, remaining PRG | none beyond Release 1 | M |
| 4 | Advanced measurement | remaining IND, CAL | golden corpus and reconciliation harness | L |
| 5 | Forms | FRM | file/media storage with scanning (object store, §4) | L |
| 6 | Ingestion | DAT, DQ | worker runtime, object store, quarantine | L |
| 7 | Offline | OFF | Android client, signed offline packages, device policy | XL |
| 8 | Evidence and evaluation | EVD, EVA | object store, search | L |
| 9 | Participant and finance | PAR, FIN | pseudonymisation and the sensitive-data role path | L |
| 10 | Analytics | ANA | reporting store and freshness index | M |
| 11 | Automation and integrations | INT | connector runtime, webhooks, credential rotation | L |
| 12 | Reporting | remaining RPT | document rendering (PDF/DOCX/XLSX), delivery provider | M |
| 13 | AI | AI | isolated AI workers, typed proposals, evaluation gates (G12) | XL |
| 14 | Product administration, migration, localisation, help, gaps | OPS, MIG, UX, remaining L10 | none | M |
| 15 | Full qualification | all VF non-functional requirements | performance, recovery and accessibility environments | L |
| 16 | Production acceptance | gates G01–G14 | everything above | — |

Earlier builds already contain bounded implementations in later-release areas (calculation, close, reporting, publication, work centre). Their original acceptance criteria remain open and are tracked in the ledger, not re-planned here.

## 4. Cross-cutting engineering tracks

These are gates and shared capabilities. Each has an owner role in the release acceptance record and none is complete.

| Track | First deliverable | Unblocks |
|---|---|---|
| Native PostgreSQL qualification (G03) | The `native-postgresql-gate` CI job first passed on 28 September 2026 for build 0.13.0 (single fixture connection). Next: separate app/identity/platform login roles, persistence across restarts, upgrade from an earlier schema, and concurrent approval/revocation under native scheduling, each recorded as evidence | every claim about concurrency; Release 1 exit |
| Live identity provider (G04) | Keycloak realm from `specification/environment/keycloak-dev-realm.json`; PKCE, nonce, ACR, disabled-account and logout tests; MFA enrolment policy | v0.19, Release 1 exit |
| Worker runtime and outbox dispatcher | One worker process consuming `outbox_delivery` with generation-fenced leases, retries and dead-lettering; first consumer: in-app notices and cancellation | v0.15, v0.18, Releases 5–6, 11 |
| Object store and mediated downloads | Private bucket, upload sessions (tables exist), quarantine and scanning, authorising stream service | Releases 5–8, 12 |
| Observability and operations (G13) | Structured logs with correlation IDs shipped, readiness and error-rate alerts, exercised runbooks, backup and restore drill with measured RPO/RTO (G10) | Release 1 exit, Release 16 |
| Security assessment (G11) | Dependency and SBOM review, penetration test on the Release 1 surface, remediation record | Release 2, Release 16 |
| Accessibility and browser matrix (G06) | WCAG 2.2 AA review of the delivered screens, keyboard and screen-reader pass, supported browser list | Release 14 |

## 5. Quality backlog carried into the plan

Verified during the 28 September 2026 code and documentation review; each becomes an issue and is scheduled into the nearest increment that touches the area.

| Item | Where | Planned in |
|---|---|---|
| Work centre and change-request submit mint a new operation ID per click, so retries there are not exact | `apps/web/src/WorkCenter.tsx`, `Changes.tsx` | v0.14 |
| Orphan baseline policy row `create_organisation_units`; custom roles treat every non-purpose policy capability, including unimplemented design operations, as delegable | `packages/contracts/access-policy.json`, `workspace_administration.py` | v0.14 |
| `IMPLEMENTATION.md` migration paragraph stops at 0012; FSD cites BRD v1.0 as its source | documentation | v0.14 documentation pass |
| Notice acknowledgement writes no revision although the implementation record says every command does | `work.py`, `IMPLEMENTATION.md` | v0.14 documentation pass (wording) |
| Version literals scattered across eight files | `main.py`, scripts, contracts, `package.json` | v0.15 (single version source) |
| Two migration runners with different BEGIN/COMMIT handling | `scripts/migrate.py`, `tools/dev-db/server.mjs` | G03 track |
| Fixture bearer tokens are minted at suite start and fresh-assurance operations require authentication within 300 s; the full suite now runs about 190 s, leaving little headroom before assurance-gated tests fail for timing reasons | `scripts/run.py`, `qualification/` | v0.14 (per-test signed tokens or a longer dev window with a documented reason) |
| `Service.command` returns 503 rather than 404 for a route missing from the regenerated contract | `service.py` | v0.15 |
| Cookie sessions serialise a browser's parallel requests (`last_seen_at` under `FOR UPDATE`) | `auth.py` | G03 track |

## 6. Operating model

- One product owner approves specifications and merges pull requests. Increments are built on a branch named `release/0.N-<topic>`, verified with `make lint build test reference browser`, reviewed by a reviewer who did not build the change, and merged only after the documentation listed in rule 2 is complete.
- The GitHub milestone "Release 1 — tenant and user administration" holds one issue per increment in §2 and per track in §4; the quality backlog in §5 is filed as issues labelled `type:debt`. Issues carry the requirement IDs they touch.
- Definition of done for an increment (from the engineering plan): positive, negative and recovery behaviours tested; closed versioned contract regenerated; tenant references, optimistic concurrency and immutable records preserved; server-side authorisation; UI states for loading, empty, denied, stale, partial and failure; clean local install; runbook entry; documentation and traceability updated together.
- Evidence is regenerated by the full gate on the release branch and committed with the increment; a focused run never replaces a full-suite count.
- Version literals (application, schema readiness, runtime manifest, control-plane API, package archive, web package, ledger build) are bumped together in every increment until the single version source in v0.15 lands.

## 7. Risks and assumptions

- All qualification to date runs on an embedded single-backend database. The first native PostgreSQL run may expose lock-ordering, serialisation or role-topology defects that change the shape of later increments; the G03 track is therefore scheduled before v0.18, which introduces the first worker.
- The fixture identities, operator records and deployment qualification expire on 2026-12-01. The fixture must be regenerated and versioned before then or every live test will fail for reasons unrelated to code.
- No live identity provider, MFA, email or SMS has been exercised. Increments v0.15, v0.17 and v0.19 deliver local adapters only until the G04 track lands.
- Release ordering assumes Release 1 is finished before Release 2 begins, as the roadmap states. If the owner chooses to interleave (for example to start Release 3 planning features earlier), the ledger and this plan must record that decision.
- Documentation edition 1.1 reconciles Word and workbook copies to build 0.12.0. Increments after it update the Markdown reading copies and registers; the Word and workbook editable copies are regenerated at the next documentation edition, and each release note says so.
