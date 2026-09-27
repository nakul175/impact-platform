# Impact Management implementation package

Version 1.0 — 25 September 2026

This package completes the ten implementation documents identified after the FSD, HLD, LLD, wireframes and test strategy. It contains specifications and executable preparation assets for the enterprise impact management platform. The application services and clients remain the engineering work described in the implementation plan.

## Start here

Read the Engineering Implementation Plan, then use the Implementation Register to assign the foundation tasks and work packages. Start WP00 and WP01 before the first end-to-end measurement workflow. Preserve the FSD release assignments; an early demonstration is not completion of R1.

The accompanying Word documents are in `documents/` at the archive root. The editable workbook is in `register/`. This README and the executable assets are in `assets/`. Equivalent Markdown document sources are in `assets/docs/`.

| Document | Implementation purpose |
|---|---|
| Engineering Implementation Plan | 18 work packages, dependencies, foundation tasks, ownership, acceptance and release gates |
| API and Event Contracts | HTTP semantics, typed DTOs, events, idempotency, errors and resumable upload protocol |
| Database Migration Specification | Physical tables, references, RLS, database roles, migration execution and qualification |
| Access Control Specification | 15 role templates, exact capabilities, scoped grants, sessions, independence and revocation |
| Development and CI Specification | Repository boundaries, pinned dependencies, local infrastructure, configuration and CI stages |
| Fixture and Acceptance Specification | Deterministic synthetic records, identity setup, acceptance examples and execution evidence |
| Security Threat Model | Trust boundaries, 32 threats, controls, owners and verification requirements |
| UI Component and Interaction Specification | 22 shared components, 30 screens, state handling, accessibility and recovery |
| Architecture Decision Records | 18 implementation decisions, tradeoffs and required verification |
| Operational Runbooks | Deployment, incidents, restoration, tenant exposure, identity, imports, calculations, privacy and capacity |

The workbook contains Overview, Requirements, Foundations, Work packages, API operations, Role templates, Threats, UI screens, Release gates and Deployment inputs. Yellow cells are editable. A requirement counts as Complete only when its status is Done and both an assignee and evidence reference exist. A release gate counts as Qualified only with Pass and an evidence reference. These formulas check recorded fields; the accountable owner must still assess the evidence.

## Authority and compatibility

The source FSD has 270 functional requirements and 37 nonfunctional contracts. The backlog retains all 307 exactly once, with their source release, priority, intended behaviour, recovery and acceptance condition. Functional releases contain 220 R1, 44 R2 and 6 R3 requirements. Including the nonfunctional contracts, the workbook totals are 256 R1, 45 R2 and 6 R3 requirements.

The authoritative source FSD is `Impact-Management-Platform-FSD-v1.0.docx`, SHA256 `1dccf4fbe6361c5530aef5239a880d87bf440eb5a548d31a8c32ad559b10e66a`. Its structured content is retained in `contracts/fsd-requirements.json`. The prior HLD, LLD, wireframe HTML, test strategy and test workbook remain the design baseline delivered separately.

The new OpenAPI document has API version **1.1.0** and uses OpenAPI 3.1.1. It supersedes the earlier Engineering Assets v1.0 API and SQL blueprints where specified in these documents. Generic workflow PATCH is removed; explicit domain commands control workflow lifecycle. The earlier calculation reference suite remains applicable. Its runner now resolves a report path against the caller's working directory before entering its own directory.

## Machine-readable inventory

| Path, relative to `assets/` | Contents |
|---|---|
| `implementation-backlog.json` | 307 requirement tasks, 18 packages and 10 foundation tasks |
| `contracts/openapi.json` | 162 paths, 235 operations and 453 named schemas |
| `contracts/access-policy.json` | Exact route-to-capability mapping; 183 capabilities and 15 role templates |
| `contracts/event.schema.json` and `event-catalogue.json` | Closed event envelope and 24 event types |
| `contracts/entity-catalogue.json` | Domain API entity inventory |
| `contracts/ui-components.json` and `ui-screens.json` | 22 components and 30 screen contracts |
| `contracts/threat-register.json` | 32 threat records |
| `contracts/release-gates.json` and `deployment-inputs.json` | 14 release gates and 17 environment inputs with accountable roles |
| `database/migrations/` | Three ordered PostgreSQL 17 migrations |
| `database/catalogue.json` and `reference-map.json` | 113 tenant tables including 32 partitions, 49 current projections and 101 classified scalar domain UUID fields |
| `fixtures/` | Two tenants, ten actors, 506 records, 471 explicit grants, SQL seed and guarded loader |
| `environment/` | Python and frontend dependency locks, local Compose configuration, identity realm and CI commands |
| `tests/` | 38 preparation tests and 12 live database tests |
| `reference-v1/` | Retained 143 calculation/reference tests, 18 API integration tests, 12 smoke tests and source test catalogue |
| `reports/` | Actual execution results, specification validation and document/workbook QA summaries |

The policy reference function consumes trusted context already derived by a server. It is not a public permission API. Role templates do not independently grant authority. The application must implement current identity, scope, purpose, assurance, separation and lifecycle resolution.

## Reproduce preparation checks

Run these commands from `assets/` in an isolated development checkout using Python 3.12.14. The preparation environment also used Node 24.19.0. The dependency locks record resolved packages and hashes; they do not qualify a future application build.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r environment/requirements.lock
bash environment/ci.sh static
```

The static stage runs the 38 new contract/control tests and 143 retained reference tests. The new tests include schema validation, reference resolution, rejection of server-owned input fields, numeric and answer boundaries, event constraints, SQL syntax, policy coverage, fixture references and isolated upload/control behaviour. SQL parsing does not apply a migration or prove an RLS policy.

To resolve the frontend dependencies, run `npm ci --ignore-scripts` in `environment/frontend/`. There is no web application entry point in this package. The actual web client, API, worker and Android application are the implementation deliverables.

## Database and identity setup

Use the Development and CI Specification for the complete sequence. Supply generated development passwords through environment configuration, then start `environment/compose.yaml`. The supplied PostgreSQL and Keycloak ports bind to loopback. The realm contains synthetic accounts with no packaged passwords and uses authorization code with PKCE. Set temporary test credentials administratively outside the archive.

Provision separate actual database login identities for the declared nonlogin roles. The migration identity needs schema/role bootstrap authority. The application must never use that identity or own its tables.

The relevant environment variables are:

| Variable | Purpose |
|---|---|
| `IMPACT_DEV_DB_PASSWORD`, `IMPACT_DEV_IDP_PASSWORD` | Generated secrets for isolated local services |
| `IMPACT_MIGRATION_DSN` | Privileged migration connection supplied securely |
| `IMPACT_FIXTURE_DSN` | Connection to an empty disposable development/test database |
| `IMPACT_ALLOW_FIXTURE_LOAD=1` | Explicitly enable the guarded fixture load |
| `IMPACT_TEST_DSN` | Qualification connection able to enter the actual `impact_app` role |

```bash
python database/migrate.py
python fixtures/load.py
python tests/run_database.py
```

The seed loader accepts only an empty database named `impact_dev` or `impact_test`. It does not reset existing records. The combined `bash environment/ci.sh database` command performs the same three steps and therefore expects a fresh disposable database. For subsequent checks of an already seeded database, run `python tests/run_database.py` directly. Migration reruns validate retained checksums; fixture reruns intentionally refuse existing data.

The fixed fixture ID is `impact-acceptance-20260925-v1`, with qualification clock 25 September 2026. The implementation's injected test clock must agree with the fixture. Expired fixture grants must not be made to pass by bypassing production expiry enforcement. Device key material is a deliberately noncryptographic test marker and cannot qualify mobile signatures or device security.

## Application integration and smoke execution

Provision the implemented API and the actual fixture before running these suites. Set `IMPACT_BASE_URL`, an absolute `IMPACT_FIXTURE_FILE` path to the provisioned manifest, and the actor token environment variables named in that manifest. Obtain short-lived tokens through the configured identity flow. Do not place tokens in the archive, workbook or reports.

```bash
python reference-v1/run_tests.py integration --report reports/integration.json
python reference-v1/run_tests.py smoke --report reports/smoke.json
```

`bash environment/ci.sh application` runs both and stops if a stage fails or is blocked. Mutation tests require the isolated fixture and its explicit test-environment controls. The smoke suite is read-only; release acceptance also requires the full create-to-publication workflow in the existing test strategy.

Exit 0 means the invoked stage passed; exit 1 means a failed assertion or rejected configuration; exit 3 means a required environment or fixture is unavailable. A blocked or skipped stage cannot qualify a release. `environment/check_release_inputs.py` checks required configuration and evidence entries; it does not prove their authenticity or replace the release owner's review.

## Evidence delivered with this package

| Check | Recorded outcome | Limit |
|---|---|---|
| New preparation tests | 38 passed | Specifications and isolated reference controls |
| Retained calculation/reference tests | 143 passed | Deterministic reference logic |
| OpenAPI validation | Passed using `openapi-spec-validator` 0.9.0 | Document structure and schema validity |
| SQL parsing | Three migrations and fixture seed parsed | PostgreSQL did not execute the scripts |
| Database suite | Blocked; 0 of 12 executed | No PostgreSQL 17 execution service available |
| API integration | Blocked; 0 of 18 executed | No running application or issued actor tokens |
| Smoke | Blocked; 0 of 12 executed | No running application or issued actor tokens |
| Word documents | Ten documents rendered; all 59 pages inspected; automated accessibility audit reported no issues | Document QA, not application accessibility |
| Implementation register | Ten tabs inspected; zero formula errors; completion/evidence recalculation checked | Recorded progress fields, not implementation evidence |

The 181 passing tests are preparation/reference tests. Browser workflows, Android devices, runtime migration behaviour, concurrency, provider integrations, load tests, restore drills and independent application security assessment remain execution work against the implemented system. No production readiness, compliance certification or organisational signoff is asserted.

Named assignees, deployment accounts, approved regions, DNS, secret references and on-call routes must be supplied by the actual engineering organisation. The documents define their contracts and owners without inventing these values. They do not prevent starting the foundation and domain implementation work.

`manifest-sha256.json` at the archive root records the bytes of every packaged file except itself. Preserve the manifest with the delivered version and regenerate it whenever the package changes.
