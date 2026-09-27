# Impact Management Development and CI Specification

This specification establishes the repository, development dependencies, local services, configuration boundaries and delivery pipeline. The supplied environment assets provision development dependencies and define validation commands. Application services are the coding work described in the implementation plan. Production account identities, domains, permitted regions and secrets are explicit deployment inputs rather than invented values.

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
