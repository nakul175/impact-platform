# Impact Management Development and CI Specification

Version 1.1   27 September 2026

This specification establishes the repository, development dependencies, local services, configuration boundaries and delivery pipeline. The supplied environment assets provision development dependencies and define validation commands. Application services are the coding work described in the implementation plan. Production account identities, domains, permitted regions and secrets are explicit deployment inputs rather than invented values.

## Release interpretation

Documentation edition 1.1 is reconciled with application build 0.12.0 on 27 September 2026. The document edition and application build use different version sequences. The original business requirements and their acceptance conditions remain authoritative. No requirement has been removed or weakened to match the current code.

Build 0.13.0 increment (28 September 2026): reviewed renewal of unexpired delegated authority is implemented and recorded in RELEASE-0.13.md, IMPLEMENTATION.md and QUALIFICATION.md; make browser now also runs the authority-renewal group (tools/browser/renewal-check.mjs), and the full reproduction remains make lint build test reference browser, regenerated on 28 September 2026 (353 application, 143 design-reference and 91 browser checks). Edition 1.1 figures elsewhere in this document describe build 0.12.0. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.14.0 increment (29 September 2026): the native-postgresql-gate job of .github/workflows/qualification.yml now generates masked throwaway passwords, provisions the four login roles as the postgres superuser (scripts/provision_logins.py), runs scripts/run.py test --native on those logins followed by the API restart check, installs postgresql-client-17 from the PGDG repository after verifying the signing key's fingerprint, runs the backup and restore drill with IMPACT_PG_BIN and the populated schema-15 upgrade check, and uploads native-application-tests.xml, native-qualification.json and native-restore-drill.json; it passed on PostgreSQL 17.11 for commit c759e9e (run 36482067070, job 109129869783). The browser job of that run failed in measurement-check.mjs on a frontend race fixed by commit 4e00dd0 (issue #24); CI for the final commit is recorded in the pull request. Locally, make native is the native gate, scripts/migrate.py is the single migration runner for PGlite and native, the PGlite server only serves the socket on IMPACT_DEV_DB_PORT (an operating-system-chosen port in test and browser modes), and the recorded full reproduction remains make lint build test reference browser: 354 passed / 27 native-only skipped / 1 deselected on 28 September 2026, 143 reference and 91 browser checks on 29 September 2026. Edition 1.1 figures elsewhere in this document describe build 0.12.0. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.15.0 increment (29 September 2026): the new CI job live-identity-provider (Temurin 21, cached and SHA-256-verified Keycloak 26.7.4) runs scripts/run.py test --idp keycloak on PGlite and the idp-browser check and uploads idp-tests.xml, idp-qualification.json and idp-browser-tests.json; the native-postgresql-gate job adds a step running the live suite on its provisioned login roles in a separate empty database. Locally, make idp runs both live modes (Java 21 required), and --native --idp keycloak runs the live suite on native login roles. All three jobs passed for commit 715c36a (run 36639725698). Recorded counts on 29 September 2026: 372 passed / 43 skipped / 1 deselected on PGlite; 397 passed / 18 skipped / 1 deselected on PostgreSQL 16.13; 16 + 16 live-provider tests; 143 reference; 91 browser and 2 live-provider browser checks. Edition 1.1 figures elsewhere in this document describe build 0.12.0. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.16.0 increment (29 September 2026): make worker starts one more outbox worker for a running make dev (which starts one itself; --no-worker omits it); scripts/provision_logins.py provisions a fifth login, impact_worker_login, with IMPACT_LOGIN_PASSWORD_WORKER, which the native-postgresql-gate CI job now generates with the other four; the native suite hands the worker login's DSN only to the test process, where qualification/test_native_worker.py starts worker subprocesses; the browser checks run one worker iteration against the run's own worker.json and read the synthetic sink; qualification/smtp_sink.py is a plain loopback SMTP server for tests. Recorded counts on 29 September 2026: 405 passed / 51 skipped / 1 deselected on PGlite; 437 passed / 19 skipped / 1 deselected on native PostgreSQL 16.13; 16 + 16 live-provider tests; 143 reference; 93 browser and 2 live-provider browser checks. CI for build 0.16.0 is recorded in the pull request. Edition 1.1 figures elsewhere in this document describe build 0.12.0. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.18.0 increment (29 September 2026): scripts/run.py planning-browser runs the new planning browser check (tools/browser/planning-check.mjs, seven checks) and is part of make browser, so the CI local-reference-and-browser job runs it. make unit adds qualification/test_planning_unit.py (120 unit checks). The PGlite gate counts 441 passed / 52 skipped / 1 deselected and the native run 474 passed / 19 skipped / 1 deselected.

The application is a development delivery. The requirement ledger records 74 PARTIAL and 233 PENDING requirements, with zero fully accepted. PARTIAL means a bounded implementation and some evidence exist, not that all acceptance conditions are satisfied. PENDING means the requirement has no accepted implementation coverage in the ledger; a read-only surface or reference example does not establish delivery.

Recorded qualification contains 325 application checks, 143 design-reference checks and 81 browser checks. One expired-offline-grant test is deselected and is not a pass. Local integration uses fresh in-memory PGlite PostgreSQL 17.5 with serialized transactions. Native PostgreSQL concurrency, live identity-provider assurance, disaster recovery, load qualification and production acceptance remain open.

The original BRD and FSD use R1, R2 and R3 requirement assignments. The later 16-stage delivery roadmap is an implementation sequence. Roadmap stage 1 and baseline R1 are different groupings; neither is complete. Requirement release assignments remain unchanged.

The sections explicitly marked current implementation describe this build. Retained target-design sections describe required future behavior unless the current implementation section states otherwise. Complete source, contracts, test evidence and original documents accompany this edition. Start at DOCUMENTATION-INDEX.md and TRACEABILITY.csv for exact locations and evidence boundaries.

## Current developer workflow

The runnable source root contains apps/api, apps/web, packages/contracts, infrastructure/migrations, qualification and tools/browser. Python 3.12, Node 24, npm and Make are the documented prerequisites. make setup creates the virtual environment, installs pinned dependencies and builds the web client. make dev starts the local synthetic fixture and exposes the application on loopback. Generated credentials are local outputs and must never be committed.

make lint build verifies formatting, Python lint, TypeScript and the client build. make test runs current application tests with one explicitly deselected offline case. make reference runs the preserved design-reference suite. make browser runs core, access administration, measurement, reporting, workspace, tenant lifecycle, initial access and recovery browser groups. The browser installer is Linux x86_64 only; other environments require a qualified browser setup.

## CI and runtime separation

.github/workflows/qualification.yml defines local qualification and a native PostgreSQL gate. The saved results do not include a native run. Native qualification requires an explicitly authorized disposable impact_test database and IMPACT_FIXTURE_DSN. The fixture loader refuses nonfixture database names and existing data; it is not a production migration mechanism.

Configuration for staging or production rejects development identity, fixture flags, local serialization and non-HTTPS identity endpoints. Runtime connections reject superuser, BYPASSRLS and schema-owner membership. These guards do not establish a ready production deployment. Image provenance, SBOM review, deployment automation, secrets, regional resources, backups, service identities, monitoring and live provider qualification remain required work.

## Documentation and evidence maintenance

Use the current master index and traceability export. Preserve baseline documents and historical release notes. Update executable contracts and the schema dictionary whenever routes or SQL change. Link a test run to its build, fixture, schema, environment and evidence. Do not overwrite the complete-suite report with a focused run and retain the old total as if it were current.

## Retained requirements and target design

The following baseline sections retain their requirement IDs and intended behavior. Implementation status is governed by the current profile above and the accompanying traceability register. Planned components are not represented as deployed services.

## 1 Repository and ownership

Use applications web, api, workers and android; packages domain, contracts, policies and testkit; and infrastructure, migrations, qualification and runbooks directories. Domain packages contain entities, value types, commands, policies and repository ports. Adapters contain HTTP, PostgreSQL, object storage, queue, identity and model-provider code. Domain code must not import a web framework or provider SDK.

Each package has an owning engineering role and prohibited import directions. Shared code is limited to canonical types, contract machinery and established cross-cutting concerns. Tenant configuration belongs in versioned records. A tenant-specific code branch requires an explicit exception decision and maintenance owner.

## 2 Dependency baseline

| Dependency | Version | Use |
| --- | --- | --- |
| Python runtime | 3.12.14 | API, workers and validation preparation |
| Node runtime | 24.19.0 | Frontend tooling and artifact preparation |
| fastapi | 0.141.1 | Pinned in requirements.lock |
| uvicorn | 0.53.0 | Pinned in requirements.lock |
| pydantic | 2.13.5 | Pinned in requirements.lock |
| psycopg | 3.3.6 | Pinned in requirements.lock |
| jsonschema | 4.26.0 | Pinned in requirements.lock |
| pglast | 8.4 | Pinned in requirements.lock |
| react | 19.3.0 | Pinned in package-lock.json |
| react-dom | 19.3.0 | Pinned in package-lock.json |
| typescript | 7.0.2 | Pinned in package-lock.json |
| vite | 8.3.1 | Pinned in package-lock.json |
| PostgreSQL | 17.11 | Development image; production digest required |
| Keycloak | 26.7.4 | Development image; production digest required |

The Python lock contains exact versions and distribution hashes resolved for Python 3.12. Install with a tool that enforces those hashes. The frontend package and lock record exact package versions and integrity values. Dependency resolution is distinct from application compatibility and security qualification: run the implementation and scan the resulting build before release.

Use Python 3.12.14 and Node 24.19.0 as the preparation environment baseline. Patch upgrades require lock regeneration, contract tests and affected integration checks. The Android implementation begins with JDK 17, Gradle 8.11.1, Android Gradle Plugin 8.10.1, Kotlin 2.1.20, compile SDK 36 and minimum SDK 26 as a compatibility baseline. Pin the actual SDK, Gradle wrapper checksum and dependency verification metadata in the Android repository before its first qualified build. Device support is determined by expiry, encryption and workflow qualification, not API level alone.

Local infrastructure uses PostgreSQL 17.11 and Keycloak 26.7.4. The compose configuration binds ports only to loopback and requires generated development passwords. Production images require verified immutable digests and current advisory checks. The local Keycloak start-dev profile and development realm are restricted to isolated test environments.

## 3 Local setup sequence

Install the declared Python and Node runtimes and Docker Compose. Create generated local development secrets in an untracked environment file. Start environment/compose.yaml. Apply the checksummed database migrations using a bootstrap connection authorised to create roles. Create an application login mapped only to impact_app and separate identities for worker, identity, sensitive and privacy access.

Load fixtures only into an empty database named impact_dev or impact_test with IMPACT_ALLOW_FIXTURE_LOAD set to 1. The loader never clears an existing database. Import the development identity realm, establish local test credentials through the identity administrator, and issue short-lived tokens through the normal code-and-PKCE path. The packaged realm contains no passwords and enables no password grant.

Run the static validation command from the assets root, then the database checks with the actual PostgreSQL connection. Start the implemented API and web services using their repository commands once they exist. Point the API suites at the provisioned application and fixture manifest. A fixture in a JSON file alone does not prove that the running service contains the records or grants.

## 4 Configuration contract

| Input | Meaning | Owner |
| --- | --- | --- |
| IMPACT_REGION | Actual deployment region | Platform lead |
| IMPACT_ALLOWED_REGIONS | Permitted region allowlist approved for the data | Privacy and platform |
| IMPACT_PUBLIC_ORIGIN | Actual HTTPS web origin | Platform lead |
| IMPACT_OIDC_ISSUER | Configured identity issuer and audience contract | Identity lead |
| IMPACT_RUNTIME_SECRET_REFERENCE | Runtime database credential secret reference | Platform lead |
| IMPACT_PRIVACY_SECRET_REFERENCE | Separate privacy executor credential reference | Privacy engineering |
| IMPACT_KMS_KEY_REFERENCE | Governed encryption key identity | Security lead |
| IMPACT_ONCALL_ROUTE | Actual incident routing and accountable rota | Operations owner |
| IMPACT_RELEASE_EVIDENCE_FILE | Qualified release evidence manifest path | QA lead |
| IMPACT_POSTGRES_IMAGE | Verified immutable database image digest | Platform lead |
| IMPACT_IDP_IMAGE | Verified immutable identity image digest | Identity lead |
| IMPACT_MIGRATION_DSN | Privileged deployment connection supplied securely | Database lead |
| IMPACT_FIXTURE_DSN | Disposable fixture database connection | QA lead |
| IMPACT_TEST_DSN | Disposable runtime-role qualification connection | QA lead |
| IMPACT_BASE_URL | Running application API origin | QA lead |
| IMPACT_FIXTURE_FILE | Provisioned manifest path | QA lead |
| IMPACT_MODEL_DESTINATIONS | Qualified provider models, regions, retention and egress | AI and privacy leads |

Store secret values in the environment's secret manager and grant each service identity only its required paths. Configuration contains secret references rather than secret values. Production startup checks required fields and refuses placeholder domains, undefined permitted regions, wildcard redirects and development identity settings. Secret and model-provider destinations cannot change through ordinary tenant branding or terminology configuration.

Web origins, API audiences and callback URIs are explicit. Validate issuer, signature, audience, expiry and authorised client. The server derives tenant context from the requested route and verified membership, never from an unverified header. Database migrations and fixtures use separate credentials from application requests.

## 5 Build pipeline

The pull-request stage performs format and lint checks, import-boundary checks, closed-schema validation, generated type consistency, deterministic unit tests, security scanning and change-specific database tests. Reject source secrets and unpinned release dependencies. Produce machine-readable results tied to the commit and tool versions.

The integration stage starts disposable PostgreSQL and identity services, applies migrations, loads synthetic fixtures and executes runtime-role database and application tests. Test actual query, locking and RLS behaviour. Do not replace PostgreSQL with an in-memory database for those checks. Browser and Android workflows run in their declared matrices with failure artifacts that exclude credentials and unnecessary personal content.

The build stage produces immutable API, worker and web artifacts, the Android package, generated clients, SBOM and provenance. Reuse the same artifact digest through staging and production. Separate configuration promotion from binary changes. A deployment manifest records code, schema, policy, calculation, form compatibility and model/prompt/retrieval versions.

## 6 CI commands and outcomes

| Command from assets root | Purpose | Prerequisite |
| --- | --- | --- |
| bash environment/ci.sh static | Schema, policy, upload and retained calculation reference checks | Locked Python dependencies |
| bash environment/ci.sh database | Migrations, guarded seed and real runtime-role tests | Empty disposable PostgreSQL 17 database and explicit fixture flag |
| bash environment/ci.sh application | Existing integration and smoke suites against the application | Deployed API, fixture manifest and scoped tokens |
| bash environment/ci.sh release | Run all package stages and check release evidence inputs | Complete environment and release evidence |

Exit 0 means the invoked stage passed. Exit 1 means a failed assertion or rejected configuration. Exit 3 means a required environment or fixture is unavailable. A skipped application suite cannot satisfy a release gate. The package's release-input checker verifies the presence of evidence records; the release owner still verifies their provenance and applicability to the exact build.

## 7 Environment separation

Development and test use synthetic records and separate identities, secrets, buckets, queues and database instances. Staging uses production-shaped security controls, retention and deployment topology while maintaining a distinct account or equivalent administrative boundary. Production data is not copied into fixtures or model prompts for convenience.

Network policy permits only declared inbound services and required outbound providers. Production databases and queues are private. The object store separates quarantined, clean, report and export paths, with access mediated through services. Provider availability, region, retention and training terms are validated before a connector or AI destination is enabled.

## 8 Rollout and observability

Readiness checks core dependencies and compatible schema. Liveness checks process health without cycling the application for an unrelated email or model-provider outage. Publish separate degraded statuses for optional integrations. Traces carry correlation and operation IDs; metrics identify tenant cohort without exposing raw participant identifiers or uncontrolled high-cardinality labels.

Deploy a canary, execute smoke checks and watch per-tenant errors, official-value reconciliation, queue age, revocation propagation and latency. Expand only after the observation interval and gates in the runbook. Rollback uses the previous compatible artifact and configuration. A data migration requiring repair must use its explicit forward repair or rehearsed restore procedure.

## 9 Technical references

Keycloak container operation: https://www.keycloak.org/server/containers. Keycloak 26.7.4 release: https://www.keycloak.org/2026/09/keycloak-2674-released. PostgreSQL maintained versions: https://www.postgresql.org/. Android Gradle Plugin 8.10 compatibility: https://developer.android.com/build/releases/past-releases/agp-8-10-0-release-notes. Dependency locks in this package are reproducibility records, not a certification that future application code is secure.
