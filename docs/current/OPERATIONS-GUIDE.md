# Impact Platform operations guide

Build 0.13.0 is qualified locally for bounded development workflows. This guide distinguishes commands that can be reproduced now from production procedures that require an actual environment, assigned owner and verified evidence.

## Reproduce the development environment

Prerequisites are Python 3.12, Node.js 24, npm and Make. Dependency installation requires network access. Run from the application source root:

```bash
make setup
make dev
```

The default origin is http://127.0.0.1:8000. Startup applies sixteen migrations and provisions synthetic development records. Local credentials, keys and data are under .local and are excluded from source archives. Stop the process tree normally with Ctrl+C. Do not expose development sign-in or the local database publicly.

The browser preparation path is Linux x86_64 specific. Development can run on the documented desktop prerequisites, but alternate browser platforms need their own setup and qualification. The local filesystem-backed database previously encountered consistency errors in this environment; final recorded test runs use fresh in-memory PGlite. Production persistence is not qualified.

## Reproduce qualification

```bash
make lint build
make test
make reference
make browser
```

The full saved application run has 353 passing checks and one explicitly deselected offline case. Reference tests have 143 passing assertions. Nine browser groups have 91 passing workflows. Focused reproduction of the latest increment: `.venv/bin/python scripts/run.py test --pytest-path qualification/test_authority_renewal.py` and `.venv/bin/python scripts/run.py renewal-browser`. Focused test commands may replace the same JUnit output path; do not retain a full-suite count after replacing its report with a focused run.

The native runner is a separate gate:

```bash
.venv/bin/python scripts/run.py test --native
```

It requires an explicitly configured IMPACT_FIXTURE_DSN for a fresh disposable impact_test database. The fixture loader refuses existing data and nonfixture database names. Never point it at production. The recorded v0.12 evidence does not include a native run.

## Health and diagnosis

| Signal | Meaning | Next check |
| --- | --- | --- |
| /health/live succeeds | API process responds | Check readiness before admitting workflows |
| /health/ready succeeds | Configured database and schema readiness checks pass | Still run a permitted end-to-end workflow |
| Build or schema differs | Artifact/configuration mismatch | Compare runtime manifest, migration checksums and intended release |
| Save outcome uncertain | Client lacks a known receipt | Reconcile operation receipt under current authority before replay |
| Authorization refused | Current authority or context is insufficient | Inspect tenant, membership, grant, scope, purpose and assurance |
| Activation blocked | One or more readiness checks fail | Review actual eligibility and deployment/owner pins |

Preserve the safe error code and correlation identifier. Inspect the specific runner directory's service logs for the failing startup. Do not include secrets in exported diagnostics. Repeatedly deleting state to get a green startup is not evidence of upgrade or recovery correctness.

## Configuration and custody

The application configuration declares environment, application/identity/platform DSNs, public origin, issuer, audience, client ID, JWKS/authorization/token URLs, cookie and invitation secrets, required ACR and provider account-management URL. Development-only flags and fixture references must be absent from a production configuration. Use secret references in deployment records; do not store secret values in this document or Git.

Staging/production configuration rejects development identity, fixture mode, local serialization and non-HTTPS identity endpoints. Runtime database identities must not be superusers, BYPASSRLS or schema owners. Separate service-login provisioning, real provider assurance and the actual production topology remain to be qualified.

## Release procedure requiring completion

1. Identify the immutable application artifact, source revision, schema, policy and client contract versions.
2. Resolve each gate in RELEASE-ACCEPTANCE.md with a named accountable reviewer and evidence.
3. Rehearse installation and upgrade on native PostgreSQL using the intended service roles. Preserve recorded migration checksums.
4. Verify backup integrity, restoration, current deletion/grant restrictions and measured RPO/RTO in approved regions.
5. Stage the exact artifact, run smoke and the critical business journey, and check identity, access and recipient isolation.
6. Record a rollout boundary, monitorable signals, stop conditions and a tested rollback or forward-repair path.
7. Obtain the organization's release decision. A documentation update or successful local build is not that decision.

Infrastructure identifiers, production regions, accounts, domains, secrets custody, on-call routes, monitoring thresholds and release approvers are unresolved inputs. No live environment or provider purchase is implied by this guide.

## Recovery and incident limits

For compromised identities, current local session and account revocation tests establish denial under the implemented cutoff checks. Provider refresh-token revocation, distributed cache propagation and downstream cancellation require live qualification. For incorrect official results, preserve the approved snapshot, withdraw affected publication if authorized, and use governed correction and restatement.

For unavailable owners, there is no qualified bypass. Recovery contacts are consent evidence only. For database outage or data loss, the target operational runbooks define the required recovery behavior, but no production restore drill has been performed. Incident records must distinguish attempted steps from verified outcomes.
