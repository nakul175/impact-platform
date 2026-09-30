# Impact Platform operations guide

Build 0.15.0 is qualified locally for bounded development workflows, at CI scale on native PostgreSQL with separately provisioned login roles, and against a live identity provider (a per-run development-mode Keycloak). This guide distinguishes commands that can be reproduced now from production procedures that require an actual environment, assigned owner and verified evidence.

## Reproduce the development environment

Prerequisites are Python 3.12, Node.js 24, npm and Make; the live identity-provider qualification also needs Java 21. Dependency installation requires network access. Run from the application source root:

```bash
make setup
make dev
```

The default origin is http://127.0.0.1:8000. Startup applies seventeen migrations through `scripts/migrate.py` (the only migration runner; the embedded PGlite server only serves the socket, on port 55432 unless `IMPACT_DEV_DB_PORT` moves it) and provisions synthetic development records. Local credentials, keys and data are under .local and are excluded from source archives. Stop the process tree normally with Ctrl+C. Do not expose development sign-in or the local database publicly.

The browser preparation path is Linux x86_64 specific. Development can run on the documented desktop prerequisites, but alternate browser platforms need their own setup and qualification. The local filesystem-backed database previously encountered consistency errors in this environment; final recorded test runs use fresh in-memory PGlite on an operating-system-chosen port. Production persistence is not qualified; the native PostgreSQL evidence below is single-node and ephemeral.

## Reproduce qualification

```bash
make lint build
make test
make reference
make browser
```

The full saved PGlite application run (29 September 2026) has 372 passing checks, 43 checks skipped with a stated reason (27 native-only and 16 live-provider) and one explicitly deselected offline case. Reference tests have 143 passing assertions. Nine browser groups have 91 passing workflows. The native run (29 September 2026, PostgreSQL 16.13) has 397 passing checks, 18 skipped (the 16 live-provider checks and the two restart phases, executed separately) and the same deselected case; its restart check, restore drill and 16→17 upgrade check are PASS. The live-provider suite has 16 passing checks on PGlite and 16 on the native login roles, and the live-provider browser check 2. Focused reproduction of the latest increment is `make idp` (see "Live identity provider" below). Focused test commands may replace the same JUnit output path; do not retain a full-suite count after replacing its report with a focused run.

The native runner is a separate gate:

```bash
IMPACT_FIXTURE_DSN=postgresql://postgres:<password>@127.0.0.1:5432/impact_test make native
```

It requires a superuser connection to an empty disposable `impact_test` or `impact_test_<suffix>` database. The fixture loader refuses existing data and non-fixture database names. Never point it at production. The runner refuses to start when the fixture expires within 90 days (`FIXTURE_EXPIRES_AT`, currently 2027-09-01). What it does, the variables it reads and the evidence it writes are in the next section; the recorded v0.14 evidence includes this run.

## Native PostgreSQL: provisioning logins, guard, restore drill

**Provision the login roles.** Migrations 0001 and 0013 create only NOLOGIN privilege roles; no migration carries a credential. The deployment administrator runs, once per cluster and database:

```bash
export IMPACT_ADMIN_DSN=postgresql://postgres:<password>@<host>:5432/<database>
export IMPACT_LOGIN_PASSWORD_APP=... IMPACT_LOGIN_PASSWORD_IDENTITY=... \
       IMPACT_LOGIN_PASSWORD_PLATFORM=... IMPACT_LOGIN_PASSWORD_MIGRATOR=...
.venv/bin/python scripts/provision_logins.py --revoke-public-connect
```

This creates or re-provisions `impact_app_login` → `impact_app`, `impact_identity_login` → `impact_identity`, `impact_platform_login` → `impact_platform` and `impact_migrator` → `impact_owner`, each `LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS NOREPLICATION`, each a member of exactly one privilege role (any other membership is revoked), each with CONNECT on the database; `impact_owner` receives CREATE on the database so that the migrator can create the schema. The privilege roles are created only when absent, so a fresh cluster can be provisioned before its first migration. The administrator connection must be a superuser or hold CREATEROLE, ownership of the database and ADMIN OPTION on all eight privilege roles; the script checks this before changing anything and, unless `--no-verify` is passed, connects as each login to confirm it can assume its own role and no other. Passwords are never printed. `--revoke-public-connect` removes PUBLIC's default CONNECT on the database; without it any login of the cluster can open the database, and the result reports `public_connect` either way. `--database` names another database than the administrator's.

**Run migrations as the migrator.** `IMPACT_MIGRATION_DSN=postgresql://impact_migrator:<password>@<host>:5432/<database> .venv/bin/python scripts/migrate.py [--until N] [--json]` applies the checksum-ledgered files as `impact_owner` (the session must be `impact_owner` or a member of it; a superuser runs the files as written). `--fixture` and `--fixture-if-empty` load the synthetic fixture and are refused unless `IMPACT_ALLOW_FIXTURE_LOAD=1` is set and the database is a fixture database name; `IMPACT_FIXTURE_DSN` is the superuser connection the fixture needs because every tenant table forces row-level security against its owner too. The API never holds the migration connection.

**Configure the API.** `IMPACT_APP_DSN`, `IMPACT_IDENTITY_DSN` and `IMPACT_PLATFORM_DSN` (or the same three fields in the configuration file) must name the three runtime logins. `IMPACT_REQUIRE_UNPRIVILEGED_DB=1` (`1/true/yes/on`; other spellings are a startup error; a configuration-file value must be a JSON boolean) makes `/health/ready` and every transaction verify that the three connections are distinct logins that are not superuser, BYPASSRLS or members of `impact_owner`; staging and production apply this regardless of the flag and therefore need a platform DSN. A verified topology is trusted for 60 seconds and then re-resolved; a refusal is never cached. Keep every privileged connection string, the login passwords and libpq `PG*` variables out of the API process environment, as `scripts/run.py` does.

**Readiness reason codes.** `/health/ready` answers 503 `SERVICE_UNAVAILABLE` with `reason_code` `PLATFORM_NOT_CONFIGURED` (a runtime connection string is missing — in staging and production, most often the platform DSN), `PRIVILEGED_RUNTIME_CONNECTION` (a connection is a superuser, BYPASSRLS or a member of `impact_owner`) or `SHARED_RUNTIME_LOGIN` (two of the three connections resolve to the same login), and a bare 503 when the schema version is not 16. The same reason codes refuse every request until the topology is corrected. The response never carries a login name; the server log does. Correct the DSNs or re-run the provisioning script; do not grant the runtime logins more privilege to make readiness pass.

**Restore drill runbook (as executed).** The drill exists as a script and has been executed against the disposable qualification database on 29 September 2026 (PostgreSQL 16.13) and in CI (17.11); it has not been executed against a deployed database because none exists.

```bash
export IMPACT_FIXTURE_DSN=postgresql://postgres:<password>@<host>:5432/<database>   # superuser; source database
export IMPACT_ADMIN_DSN=$IMPACT_FIXTURE_DSN                                       # creates and drops <database>_restored
export IMPACT_LOGIN_PASSWORD_APP=... IMPACT_LOGIN_PASSWORD_IDENTITY=... \
       IMPACT_LOGIN_PASSWORD_PLATFORM=... IMPACT_LOGIN_PASSWORD_MIGRATOR=...      # existing passwords; never generated or changed by the drill
export IMPACT_PG_BIN=/usr/lib/postgresql/17/bin                                   # only when the pg_dump on PATH is older than the server
.venv/bin/python scripts/restore_drill.py [--report docs/evidence/native-qualification.json]
```

The drill dumps the source with `pg_dump -Fc` (size and duration recorded; the superuser password travels through `PGPASSWORD` in the tool's environment, never on a command line), creates `<database>_restored`, restores it with `pg_restore --exit-on-error`, grants the four logins CONNECT and `impact_owner` CREATE on the copy and nothing else, runs `scripts/migrate.py` against the copy as `impact_migrator` (which must apply nothing and verify all sixteen ledgered checksums), and checks by direct query that the seeded OFFICIAL result 46.36 is present in its snapshot revision with its payload hash, that every table of the `impact` schema has the same row count as the source, that every table is owned by `impact_owner`, that RLS flags, policies, SECURITY DEFINER functions and grants are identical, and that `impact_app` reads nothing without a transaction-local tenant, exactly one tenant with one, and no control-plane table. It drops the copy and writes `docs/evidence/native-restore-drill.json` (`outcome`, `checks`, `credentials_altered: false`). Its limits: it is a CI-scale drill (the recorded dump is 3.4 MB), it needs a superuser and a server with room for a second copy of the database, it says nothing about backup scheduling, retention, off-site or immutable copies, protection against alteration or credential compromise, key recovery, attachments (none exist) or deletion/restriction replay before reopening, and it establishes no RPO or RTO. A backup regime is planned with the deployment package (v0.17); until it exists, no production restore capability may be claimed from this drill.

**Upgrade check and the full native sequence.** `IMPACT_ADMIN_DSN=... IMPACT_LOGIN_PASSWORD_*=... .venv/bin/python scripts/native_upgrade_check.py --report <json>` migrates a fresh disposable database to schema 16 as the migrator, loads the fixture, applies 0017 and verifies the seventeen checksums, the provider-logout columns, the replay table and the preserved tenant, revision and session counts; it exercises only 0016 → 0017, which adds nullable columns to a populated table and a new table. `make native` runs everything in order — provisioning with throwaway passwords unless `IMPACT_LOGIN_PASSWORD_*` are set, migration as the migrator, the suite on the runtime logins, the two-phase API restart check, the restore drill and the upgrade check — and writes `docs/evidence/native-application-tests.xml`, `native-qualification.json` and `native-restore-drill.json`; `--skip-restart-check`, `--skip-restore-drill` and `--skip-upgrade-check` are available through `scripts/run.py test --native`. `IMPACT_DEV_DB_PORT` concerns only the embedded PGlite server (`0` lets the operating system choose, as the test and browser modes do). The `native-postgresql-gate` job in `.github/workflows/qualification.yml` is the CI form of the same sequence against `postgres:17.11`.

## Live identity provider

Outside loopback development the platform signs people in only through the configured OpenID Connect provider. The configuration fields (configuration file or `IMPACT_<FIELD>` environment variables) are `issuer`, `client_id`, `audience` (the access-token audience accepted on bearer requests), `jwks_url`, `authorization_url`, `token_url`, `end_session_url` (the provider's RP-initiated logout endpoint; without it logout revokes only the platform session), `required_acr` (the assurance class that satisfies fresh-assurance operations; mandatory in staging and production), `provider_account_url` (optional HTTPS link shown with the session list) and `client_secret`. `client_secret` is for a confidential client only: supply it as `IMPACT_CLIENT_SECRET` from a secret store, at least 32 characters, never with `dev_auth`; the code exchange then uses HTTP Basic client authentication. A public client with S256 PKCE, as qualified, leaves it empty. `dev_auth` must be false. In staging and production every identity URL must be HTTPS; in development and test a plain-HTTP provider is accepted only on loopback.

Provider realm or tenant requirements, as the qualification realm `tools/idp/qualification-realm.json` sets them: authorization-code flow only (no direct grants), S256 PKCE required, redirect URI `<public origin>/auth/callback`, post-logout redirect URI `<public origin>/`, back-channel logout URL `<public origin>/auth/backchannel-logout` with the session identifier required (`sid` in the ID and logout tokens), refresh tokens disabled, an access-token audience matching `audience` and short access-token lifetimes (120 s in qualification), `auth_time` in the ID token, and an ACR mapping in which `required_acr` is reached only with the second factor (qualification: `urn:impact:acr:password` level 1, `urn:impact:acr:mfa` level 2 with TOTP). Each person's provider subject must match `provider_subject` of an `auth_identity` row with that issuer; provider roles and groups grant nothing on the platform.

Endpoints: `GET /auth/login` and `GET /auth/callback` run the sign-in; `POST /auth/logout` revokes the browser session and returns `logout_url` (the end-session URL with `client_id`, `post_logout_redirect_uri` and a sealed `id_token_hint`), which the web client visits; `POST /auth/backchannel-logout` receives the provider's signed logout token (form body, at most 16 KiB + 64 bytes; 404 when no live provider is configured) and revokes the platform sessions of that provider session, refusing replays with `LOGOUT_TOKEN_INVALID`. Replay records live in `impact.oidc_logout_token` and are purged in bounded batches once expired. The Host allow-list admits only the public origin's hostname (plus `testserver` in test), so the provider must call the back-channel URL by the public hostname, not an internal service name, or the call is refused before it reaches the handler.

Qualification: `make idp` (or `.venv/bin/python scripts/run.py test --idp keycloak` and `.venv/bin/python scripts/run.py idp-browser --idp keycloak`) downloads Keycloak 26.7.4 once into `.local/keycloak/` (override with `IMPACT_KEYCLOAK_CACHE`), verifies its SHA-256, starts it on a loopback port in development mode with an in-memory database, imports the realms, re-points the fixture identities to the realm issuer and runs `qualification/test_live_idp.py` and the Chromium check; with `--native` and `IMPACT_FIXTURE_DSN` (an empty disposable `impact_test_<suffix>`) the suite runs on the provisioned login roles. Generated credentials are written only to `.local/<run>/idp.json` (mode 0600). Evidence: `docs/evidence/idp-tests.xml`, `idp-native-tests.xml`, `idp-qualification.json`, `idp-browser-tests.json`. `.venv/bin/python scripts/idp.py serve` runs the same provider for manual exploration. This Keycloak is a qualification harness, never a production provider: the deployment model is an open owner decision, and recovery, enrolment completion, key rotation, provider outage and the confidential-client path have not been exercised.

## Health and diagnosis

| Signal | Meaning | Next check |
| --- | --- | --- |
| /health/live succeeds | API process responds | Check readiness before admitting workflows |
| /health/ready succeeds | Login topology (when unprivileged connections are required), configured database and schema readiness checks pass | Still run a permitted end-to-end workflow |
| /health/ready returns 503 with a topology reason code | A runtime connection is missing, privileged or shared (see the native section) | Correct the connection strings or re-provision the logins; never widen a runtime login's privilege |
| Build or schema differs | Artifact/configuration mismatch | Compare runtime manifest, migration checksums and intended release |
| Save outcome uncertain | Client lacks a known receipt | Reconcile operation receipt under current authority before replay |
| Authorization refused | Current authority or context is insufficient | Inspect tenant, membership, grant, scope, purpose and assurance |
| Sign-in returns 401 at `/auth/callback` | State consumed or not bound to this browser, nonce or PKCE mismatch, token exchange failed, provider `auth_time` older than 300 s, or unknown issuer/subject | Start a new sign-in; compare issuer, client and subject mapping; check the provider's event log |
| Back-channel logout returns 400 `LOGOUT_TOKEN_INVALID` or never arrives | Token unverifiable, stale, replayed or lacking `sid`; or the provider addressed the platform by a hostname the allow-list refuses | Check the provider's back-channel URL uses the public hostname and that clocks agree |
| Activation blocked | One or more readiness checks fail | Review actual eligibility and deployment/owner pins |

Preserve the safe error code and correlation identifier. Inspect the specific runner directory's service logs for the failing startup. Do not include secrets in exported diagnostics. Repeatedly deleting state to get a green startup is not evidence of upgrade or recovery correctness.

## Configuration and custody

The application configuration declares environment, application/identity/platform DSNs, public origin, issuer, audience, client ID, JWKS/authorization/token/end-session URLs, an optional client secret (`IMPACT_CLIENT_SECRET`), cookie and invitation secrets, required ACR and provider account-management URL. Development-only flags and fixture references must be absent from a production configuration. Use secret references in deployment records; do not store secret values in this document or Git.

Staging/production configuration rejects development identity, fixture mode, local serialization and non-HTTPS identity endpoints. Runtime database identities must not be superusers, BYPASSRLS or schema owners, must be three distinct logins, and must include a platform connection; readiness and every transaction verify this. Separate service-login provisioning is now scripted and qualified on single-node native PostgreSQL in CI and locally (see the native section); the owner's chosen identity provider, a connection pooler and the actual production topology remain to be qualified.

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

For compromised identities, current local session and account revocation tests establish denial under the implemented cutoff checks. Since v0.15 ending the person's sessions at the provider revokes the matching platform sessions through back-channel logout; no refresh token is issued, but an access token already issued remains valid on bearer requests until `exp` (keep access-token lifetimes short), and the identity cutoff (`auth_not_before`) remains the platform-side control. Distributed cache propagation and downstream cancellation require live qualification. For incorrect official results, preserve the approved snapshot, withdraw affected publication if authorized, and use governed correction and restatement.

For unavailable owners, there is no qualified bypass. Recovery contacts are consent evidence only. For database outage or data loss, the target operational runbooks define the required recovery behavior; the scripted restore drill above has been executed only against disposable qualification databases, no production backup exists and no production restore drill has been performed. Incident records must distinguish attempted steps from verified outcomes.
