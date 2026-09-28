# Delivery plan from build 0.13.0

Prepared 28 September 2026 against documentation edition 1.1, build 0.13.0, schema 16, domain API 1.10.0 and control-plane API 1.3.0, and revised the same day by scope decision SD-01 (§7). Owner: product lead. This plan sequences the remaining work; it changes no requirement, no requirement release tag and no acceptance condition, and it declares nothing accepted. The requirement ledger stays the record of coverage: 74 PARTIAL, 233 PENDING, 0 accepted of 307.

Planning sources: [remaining work](NEXT-DELIVERY.md), the [engineering implementation plan](current/Impact-Management-Engineering-Implementation-Plan-v1.1.md) (work packages WP00–WP17, gates G01–G14), the [release acceptance record](current/RELEASE-ACCEPTANCE.md), the [completion ledger](COMPLETION-LEDGER.md) and the increment records `RELEASE-0.2.md` to `RELEASE-0.13.md`.

## 1. Planning rules

1. An increment is one reviewed slice with its own release note, migration(s) where needed, tests, browser check, evidence and documentation update, delivered through one pull request. The v0.10–v0.13 records are the template.
2. Every increment updates, in the same change: the requirement ledger groups, the implemented contracts and API inventory, the migration dictionary, the implementation profile, the user/administrator/operations guides, screen coverage, the execution and traceability registers, the qualification record, the next-delivery record and the change record. Migration bytes, requirement IDs, historical run dates and prior editions are preserved.
3. A requirement moves from PENDING to PARTIAL only with source and executed test evidence; it is never marked accepted by an increment. Acceptance follows the procedure in the release acceptance record with named approvers.
4. Effort is given as a size band, not a date: **S** (one increment of the v0.12/v0.13 kind: one new control-plane or domain workflow, one migration, 20–30 tests), **M** (two to three coupled workflows or a first infrastructure integration), **L** (a new subsystem such as a worker, an object store or a device client), **XL** (a module family). Measured calibration: the v0.13 increment (S) took 2 h 46 min of machine time end to end on 28 September 2026, including plan, build, two full gates, independent review and documentation. Calendar durations depend on review cadence and on the environments the owner provides; no date in this document is a commitment.
5. Infrastructure gates are delivered as increments of their own inside Release 1 (§2) rather than as a parallel track, because nothing is usable until they exist.
6. The BRD/FSD requirement release tags (R1/R2/R3) are the baseline's own grouping and are not changed by this plan. The delivery releases below are an implementation sequence chosen by scope decision SD-01.

## 2. Release 1 — Usable core (in progress)

**Definition of usable (SD-01).** One organisation can run its real monitoring, evaluation and learning cycle end to end on hosted infrastructure with real logins: design its results framework, define governed indicators, collect data through web forms and file imports, review it independently, calculate, close periods, export frozen reports as PDF and XLSX, see dashboards, and do all of this with the security, privacy, backup and monitoring basics a public-systems deployment cannot skip. Out of scope until Release 2 or 3: multi-tenant administration edge cases, offline and mobile collection, participant registries, the evaluation module, integrations, migration tooling, finance and AI.

Delivered so far: v0.2 access administration, v0.5 period close, v0.6 frozen reports, v0.7 work centre, v0.8 controlled publication, v0.9 workspace/account/ACR, v0.10 tenant lifecycle, v0.11 initial access, v0.12 recovery contacts, v0.13 reviewed renewal of delegated authority.

| Increment | Scope | Requirements touched | Size | Depends on |
|---|---|---|---|---|
| v0.14 | Native PostgreSQL qualification: separate app/identity/platform login roles provisioned by script and enforced by the runtime guard in native test; upgrade from schema 15 to 16 on a populated database; native-only concurrency tests (simultaneous approvals, revocation against renewal approval, simultaneous close); API restart persistence; backup and restore drill with measured timing; one migration runner; per-test signed fixture tokens; regenerated fixture before its 2026-12-01 expiry | FR-SEC-003, FR-OPS-005, VF-DIN-002, VF-DR-002, VF-DR-003 | M | none |
| v0.15 | Live identity provider: Keycloak realm from `specification/environment/keycloak-dev-realm.json` in CI; PKCE, state and nonce replay, ACR and TOTP MFA, disabled account, provider logout and refresh-token revocation, provider recovery; operation-identifier retention in the work centre and change requests; policy row and custom-role delegable-set cleanup | FR-IAM-006, FR-IAM-008, FR-IAM-011, VF-IAM-001 | M | v0.14 |
| v0.16 | Worker runtime and outbox dispatcher (generation-fenced leases, retries, dead-letter); email provider interface with a synthetic provider in test and SMTP in deployment; invitations and recovery-channel verification by email; in-app notices and expiry reminders; work cancellation | FR-IAM-001, FR-IAM-007, FR-TEN-001, FR-ACC-008 | L | v0.14 |
| v0.17 | Deployment package and operations: container images, compose and Helm charts, secrets from the environment or a secret store, TLS, structured logs with correlation identifiers, metrics, readiness and error-rate alerts, scheduled backups with the restore runbook, single version source, first staging deployment | FR-SEC-006, FR-OPS-005, VF-OBS-001, VF-DR-001, VF-AVL-001 | M | v0.14, v0.16, hosting decision (§7) |
| v0.18 | Results framework and planning: logframe/results hierarchy, indicator placement, targets and milestones, planning approval | FR-PLN P0 | M | none |
| v0.19 | Indicator and calculation completion: disaggregation, targets against actuals, remaining aggregation rules, golden corpus and reconciliation harness | FR-IND P0, FR-CAL P0, VF-DIN-001 | M | v0.18 |
| v0.20 | Web forms: form design and versioning, submission to observations with value states, validation, review integration | FR-FRM P0 (web) | L | v0.19 |
| v0.21 | Import and data quality: CSV/XLSX import with staging and quarantine, validation rules, duplicate and anomaly checks | FR-DAT P0, FR-DQ P0 | M | v0.16 |
| v0.22 | Object store and evidence attachments: private bucket, upload sessions, scanning hook, mediated downloads, attachments on observations and results | FR-EVD P0, FR-SEC-005 | L | v0.16 |
| v0.23 | Report exports: PDF, XLSX and DOCX rendering of frozen packages through the worker; delivery to named recipients | FR-RPT P0, VF-PER-005 | M | v0.16 |
| v0.24 | Dashboards: programme and indicator views from official snapshots, freshness indicator, coverage | FR-ANA P0, VF-PER-002, VF-PER-006 | M | v0.19 |
| v0.25 | Security and privacy P0: encryption and key governance, secrets rotation, data-subject export and deletion propagation, retention proof, audit export | FR-SEC-002, FR-SEC-006, FR-PRV P0, VF-PRV-001, VF-PRV-002, VF-AUD-001 | L | v0.17, v0.22 |
| v0.26 | Non-functional qualification and acceptance preparation: interactive response, scaling and workload isolation, availability and degradation, accessibility conformance, support readiness, UAT pack, penetration-test remediation | VF-PER-001, VF-CAP-002, VF-AVL-002, VF-UX-001, VF-SUP-001, VF-SEC-001 | L | all above |

Release 1 exit conditions: every P0 requirement in the definition above at PARTIAL with executed evidence or explicitly deferred by a recorded scope decision; gate G03 (database) executed natively with separate login roles; gate G04 (identity and access) executed against a live provider with MFA; a staging deployment operated with backups, monitoring and a restore drill; UAT with representative users and named approvers; the security assessment items that concern the delivered surface remediated. None of these is claimed today.

Decisions the owner must supply before the increments that need them: hosting provider and region (v0.17), identity provider deployment model (self-hosted Keycloak or a managed provider; v0.15 qualifies against Keycloak in CI either way), email provider (v0.16 uses a synthetic provider in test and needs real credentials only at staging).

## 3. Releases 2 and 3 (planned)

| Release | Scope | Families | Prerequisite capability | Size |
|---|---|---|---|---|
| 2 — Field and partners | Offline and Android collection with signed packages and device policy; participant registry with pseudonymisation and the sensitive-data role path; evaluation module; remaining evidence requirements; integrations, webhooks and connector runtime with credential rotation; migration tooling; tenant-administration completion (administrator replacement and expired-authority renewal, legacy tenant adoption, unavailable-owner recovery, lifecycle closure export/archive/deletion, access certification and shared-device mode, organisation reorganisation) | OFF, PAR, EVA, EVD, INT, MIG, remaining TEN/IAM/ACC | Release 1 in operation | XL + 3 L + 2 M |
| 3 — Intelligence | AI assistance with isolated workers, typed proposals and evaluation gates (G12); advanced analytics and reporting store; finance; remaining reporting and delivery; localisation and help completion | AI, ANA, FIN, remaining RPT, L10, UX | Release 2 | XL + L + 2 M |
| Production acceptance | Gates G01–G14 | all VF | everything above | — |

The former 16-stage sequence is retained in `NEXT-DELIVERY.md` history and in the engineering implementation plan for traceability; its stage numbers are no longer used for scheduling.

## 4. Former cross-cutting tracks, now scheduled

| Track | Status on 28 September 2026 | Delivered by |
|---|---|---|
| Native PostgreSQL qualification (G03) | The `native-postgresql-gate` CI job first passed on 28 September 2026 for build 0.13.0 (single fixture connection) | v0.14 |
| Live identity provider (G04) | Not started; realm export exists | v0.15 |
| Worker runtime and outbox dispatcher | Not started; `outbox_delivery` table exists | v0.16 |
| Object store and mediated downloads | Not started; upload-session tables exist | v0.22 |
| Observability and operations (G13, G10) | Readiness endpoint and correlation identifiers only | v0.17 |
| Security assessment (G11) | Not started | v0.25, v0.26 |
| Accessibility and browser matrix (G06) | Not started | v0.26 |

## 5. Quality backlog carried into the plan

Verified during the 28 September 2026 code and documentation review; each is an issue labelled `type:debt` and is scheduled into the nearest increment that touches the area.

| Item | Where | Planned in |
|---|---|---|
| Work centre and change-request submit mint a new operation ID per click, so retries there are not exact | `apps/web/src/WorkCenter.tsx`, `Changes.tsx` | v0.15 |
| Orphan baseline policy row `create_organisation_units`; custom roles treat every non-purpose policy capability, including unimplemented design operations, as delegable | `packages/contracts/access-policy.json`, `workspace_administration.py` | v0.15 |
| `IMPLEMENTATION.md` migration paragraph stops at 0012; FSD cites BRD v1.0 as its source | documentation | v0.14 documentation pass |
| Notice acknowledgement writes no revision although the implementation record says every command does | `work.py`, `IMPLEMENTATION.md` | v0.14 documentation pass (wording) |
| Version literals scattered across eight files | `main.py`, scripts, contracts, `package.json` | v0.17 (single version source) |
| Two migration runners with different BEGIN/COMMIT handling | `scripts/migrate.py`, `tools/dev-db/server.mjs` | v0.14 |
| Fixture bearer tokens are minted at suite start and fresh-assurance operations require authentication within 300 s; the full suite runs about 190 s | `scripts/run.py`, `qualification/` | v0.14 (per-test signed tokens) |
| Fixture identities, operators and qualification expire 2026-12-01 | `specification/fixtures/` | v0.14 (regenerated and versioned) |
| `Service.command` returns 503 rather than 404 for a route missing from the regenerated contract | `service.py` | v0.15 |
| Cookie sessions serialise a browser's parallel requests (`last_seen_at` under `FOR UPDATE`) | `auth.py` | v0.14 (native concurrency evidence decides the fix) |
| `make browser` failed once in two CI runs of the same commit (issue #24) | `tools/browser/`, CI | v0.14 if reproducible, otherwise v0.15 |

## 6. Operating model

- One product owner approves specifications and merges pull requests. Increments are built on a branch named `release/0.N-<topic>`, verified with `make lint build test reference browser` plus the native run where the increment touches persistence, reviewed by a reviewer who did not build the change, and merged only after the documentation listed in rule 2 is complete.
- GitHub milestones "Release 1 — Usable core", "Release 2 — Field and partners" and "Release 3 — Intelligence" hold one issue per increment in §2 and per family group in §3; the quality backlog in §5 is filed as issues labelled `type:debt`. Issues carry the requirement IDs they touch.
- Definition of done for an increment (from the engineering plan): positive, negative and recovery behaviours tested; closed versioned contract regenerated; tenant references, optimistic concurrency and immutable records preserved; server-side authorisation; UI states for loading, empty, denied, stale, partial and failure; clean local install; runbook entry; documentation and traceability updated together.
- Evidence is regenerated by the full gate on the release branch and committed with the increment; a focused run never replaces a full-suite count.
- Version literals (application, schema readiness, runtime manifest, control-plane API, package archive, web package, ledger build) are bumped together in every increment until the single version source in v0.17 lands.

## 7. Scope decision, risks and assumptions

**SD-01 (28 September 2026, product owner).** The delivery sequence is reorganised from the 16-stage family-by-family roadmap into three releases so that the first release is usable on its own by one organisation. Recorded consequences: (a) the BRD's baseline R1 tag covers 256 requirements including AI, offline, forms and migration, and is therefore not the same set as Release 1 here; the tags are unchanged and the ledger keeps reporting against them; (b) the tenant-administration edge cases previously planned as v0.14, v0.16, v0.17 and v0.20 move to Release 2 — a single organisation with a known owner does not need them to operate, and the v0.13 renewal path keeps its administrators' authority alive meanwhile; (c) the safeguards the BRD attaches to its R1 are split: the P0 security, privacy, backup and monitoring requirements stay in Release 1 (v0.14, v0.17, v0.25, v0.26); the rest follow their families. Nothing about acceptance changes: a release is accepted only by the procedure in the release acceptance record.

- All qualification to date runs on an embedded single-backend database. v0.14 is first because the native run may expose lock-ordering, serialisation or role-topology defects that change the shape of every later increment.
- The fixture identities, operator records and deployment qualification expire on 2026-12-01; v0.14 regenerates and versions them.
- No live identity provider, MFA, email or SMS has been exercised. v0.15 and v0.16 qualify against Keycloak and a synthetic email provider in CI; live provider evidence needs the owner's accounts.
- Hosting, identity-provider and email-provider decisions are the owner's and gate v0.15–v0.17; the code for those increments can be built and qualified in CI before the accounts exist, but nothing is usable by anyone until a staging deployment runs.
- Documentation edition 1.1 reconciles Word and workbook copies to build 0.12.0. Increments after it update the Markdown reading copies and registers; the Word and workbook editable copies are regenerated at the next documentation edition, and each release note says so.
