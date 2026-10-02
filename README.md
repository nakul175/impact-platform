# Impact Platform · v0.25.0

Documentation edition **1.1** is available in the [master documentation index](docs/current/DOCUMENTATION-INDEX.md): BRD, FSD, HLD, LLD, wireframes, test cases/scenarios, engineering specifications and handover guides. Original editions are preserved in `docs/history/v1.0`. This documentation update does not declare product or production acceptance.


A working development delivery of the Impact Management platform described in the saved implementation package. It includes a React interface, FastAPI service, PostgreSQL migrations, explicit permissions, immutable revisions, independent review, provisional and official calculations, programme-period close/restatement, snapshot-bound reporting, and named-recipient controlled publication.

This release is a development build. It does not implement the complete enterprise product. The exact boundary and remaining work are documented in [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md).

Build 0.25.0 delivers v0.25 security and privacy P0 in two bounded parts — key governance (rotatable application secrets with key ids and grace windows, `scripts/rotate_secrets.py` and `deploy/rotate-secrets.sh`, a key and encryption register) with a purpose-required, sealed audit export; and privacy execution (purpose-bound data-subject requests for members with an independently approved per-store plan, an access export package and erasure propagation, plus a retention sweep with proof; migration 0027) — together with operations hardening on the staging server (verified nightly backup sets including the evidence files, a weekly restore drill, alerts on the status page, operator metrics, owner console scripts) and two QA passes (browser checks for imports, evidence, exports and re-queue; an automated accessibility scan with keyboard checks). Domain API 1.15.0 (197 operations), control plane 1.6.0 (35 operations), schema 27; ledger 103 PARTIAL, 204 PENDING, 0 accepted. See [docs/RELEASE-0.25a.md](docs/RELEASE-0.25a.md), [docs/RELEASE-0.25b.md](docs/RELEASE-0.25b.md), [docs/RELEASE-OPS-2026-10.md](docs/RELEASE-OPS-2026-10.md), [docs/QA-BROWSER-2026-10.md](docs/QA-BROWSER-2026-10.md) and [docs/QA-A11Y-2026-10.md](docs/QA-A11Y-2026-10.md).

Build 0.24.0 integrated v0.21 import and data quality (CSV/XLSX import batches with header-name mapping, a staged preview that quarantines or flags every row, duplicate and warning-only anomaly checks, and an atomic or partial commit into the observation review; migration 0022), v0.22 object store and evidence attachments (a private content-addressed store, checked and scanned whole-file uploads — the bundled scanner is a test scanner, not anti-malware — evidence revisions, citations of exact revisions and mediated, audited downloads; migration 0023), v0.23 report exports (PDF, XLSX and DOCX renderings of frozen packages by the worker, pinned by a reviewed disclosure; migration 0024) and v0.24 dashboards (official and provisional values kept apart, coverage and a stated stale rule; no migration), with the October 2026 quality work (single version source in `VERSION.json`, narrowed worker privileges in migrations 0025–0026, an operator re-queue of held or DEAD deliveries). Domain API 1.14.0 (186 operations), control plane 1.5.0 (34 operations), schema 26; ledger 94 PARTIAL, 213 PENDING, 0 accepted. See [docs/RELEASE-0.21.md](docs/RELEASE-0.21.md), [0.22](docs/RELEASE-0.22.md), [0.23](docs/RELEASE-0.23.md), [0.24](docs/RELEASE-0.24.md) and [docs/QUALITY-2026-10.md](docs/QUALITY-2026-10.md).

Version 0.20 adds web forms: a form version carries its fields, answer rules and indicator bindings, is independently reviewed and published into an insert-only register; responses are validated on the server against the exact published version (one bounded relevance rule per field; hidden answers refused), saved as server drafts and submitted into one observation per bound indicator with explicit value states, inside the existing observation review; a response on a superseded version is quarantined unchanged (migration 0021; domain API 1.13.0, 160 operations; see [docs/RELEASE-0.20.md](docs/RELEASE-0.20.md)). Version 0.19 completes the P0 calculation methods, disaggregation and a golden corpus (migration 0020; [docs/RELEASE-0.19.md](docs/RELEASE-0.19.md)).

Version 0.18 adds the results framework and planning: a governed framework per programme with typed impact, outcome, output and activity nodes, stable node identities, owners and indicator placement, structural validation, a completeness review whose warnings can be excepted with a reason and review date, independent review into immutable baselines with a supersession chain; targets, baselines and milestones per indicator and period with explicit value states, approved the same way; a paged targets-versus-actuals view that shows an official actual only from the programme's own locked snapshot; and a period close that pins targets and the governing framework revision (migration 0019; domain API 1.11.0). It was built ahead of v0.17, whose staging step waits on the hosting decision. Version 0.16 adds a worker process and outbox dispatcher on its own database login: delivery intents written in the business transaction (no link, code or clear address stored), generation-fenced leases on database time, retries with backoff and a dead-letter state, exactly-once in-app notices, an SMTP adapter (loopback only outside staging and production) and a synthetic mail sink, invitation email, nominee confirmation of a recovery contact's registered email address by single-use code, delegated-authority expiry reminders, cancellation of queued jobs, and an operator Workers panel (migration 0018; control-plane API 1.4.0). No email provider is deployed and no real email has been sent. Version 0.15 runs the platform against a live identity provider: a pinned Keycloak 26.7.4 started per run, the real authorization-code flow with PKCE, state and nonce, step-up from password to TOTP with fresh assurance measured from the provider's `auth_time`, RP-initiated logout with a sealed ID-token hint, verified back-channel logout with a replay register (migration 0017), and bearer validation through the provider's keys; it also fixes exact retries in the work centre and change requests (#18), limits custom roles to implemented capabilities (#19) and answers 404 for a route missing from the contract (#22). Version 0.14 qualified the platform on native PostgreSQL with separately provisioned login roles; version 0.13 added reviewed renewal of unexpired delegated authority. All prior capabilities remain included. Release 1 remains incomplete: the identity provider the owner will choose, refresh tokens (none are issued), provider recovery, the email provider and outbound-mail operations (bounces, SPF/DKIM, sending limits), a deployment with backups and monitoring, renewal of expired authority, administrator replacement and full closure remain open, and the native, worker and live-provider evidence is single-node and CI-scale. See [0.18 release details](docs/RELEASE-0.18.md), [0.16 release details](docs/RELEASE-0.16.md), [0.15 release details](docs/RELEASE-0.15.md), [remaining work](docs/NEXT-DELIVERY.md), the [sequenced delivery plan](docs/DELIVERY-PLAN.md) and the [307-requirement ledger](docs/COMPLETION-LEDGER.md) (81 PARTIAL, 226 PENDING, 0 accepted).

## Start locally

Prerequisites: Python 3.12, Node.js 24, npm, and Make on Linux or macOS; Java 21 for the live identity-provider checks (`make idp`). The automated browser setup is Linux x86_64 only. Dependency installation requires internet access.

```bash
cd impact-platform
make setup
make dev
```

Open **http://127.0.0.1:8000**. The first startup applies twenty-seven migrations, loads synthetic records, generates local passwords and starts one outbox worker (`--worker-id dev-worker`, log `.local/dev/worker.log`); `make worker` attaches another to a running `make dev`, and `.venv/bin/python scripts/run.py dev --no-worker` starts without one. The development worker never sends real email: messages go to the synthetic sink `.local/dev/synthetic-mail.jsonl`. Find the `author`, `reviewer`, `partner`, `admin`, `owner` and `invitee` passwords in `.local/dev/passwords.json`; they are generated on your machine and are not included in this source archive. Stop with Ctrl+C. Running `make dev` again preserves the development database, passwords and signing secrets. Existing databases receive the additive migrations; they are not reset.

The managed execution filesystem produced intermittent EOF/page-consistency errors with filesystem-backed PGlite. The test runners therefore use disposable memory storage. For a disposable local demonstration use `.venv/bin/python scripts/run.py dev --ephemeral`; records in that mode disappear on shutdown. Native PostgreSQL is a separate gate (`make native`, below); persistence across a database restart, a connection pooler and any load profile remain open.

For this increment, sign in as `admin` and open **Workspace settings**. Custom roles do not grant access on creation; use **People & access → Access requests** or submit a group proposal. Sign in separately as `owner` to review a proposal independently. **My account** shows preferences and active sessions. Ownership nomination must originate from the current owner and be accepted by the nominated administrator.

For tenant onboarding, open **Tenant lifecycle** as `admin`. Request a tenant using the `author` identity UUID from `specification/fixtures/api-fixture.json`, the local deployment profile and privacy reference `local-development-privacy`. Sign in separately as `author` to accept ownership. Open **Recovery contacts**, nominate the `partner` identity UUID and choose an expiry within 90 days. Sign in as `partner` to verify the nomination and, optionally, choose **Email me a verification code**, read the eight-digit code from `.local/dev/synthetic-mail.jsonl` and enter it (this confirmation is evidence only and changes nothing a contact may do); then sign in as `admin` to approve it independently. Finally, sign in as `owner` to activate the tenant. These local identities and verification are synthetic. Contacts receive no tenant access. Activation grants no business access; continue with the initial-access flow below.

For initial access, open **Tenant lifecycle → Initial access** as `author`, propose access for the new tenant, nominate the `reviewer` identity UUID, choose an expiry within 90 days and select **PROGRAMME MANAGER** for later delegation. Sign in separately as `reviewer` to accept, then as `admin` to approve independently. The owner and second administrator receive administration access only. Return to the workspace and select the new tenant. As `reviewer`, use **People & access → Members → Reviewer → Request role change** to request PROGRAMME_MANAGER within the reviewed expiry. As `author`, approve it under **Access requests**. Refresh the reviewer workspace; **Portfolio** now permits creating the first programme draft. The protected owner remains the independent administrator. To extend that authority before it expires, sign in as `author`, open **Tenant lifecycle → Authority renewal**, choose a later expiry within 90 days and propose; sign in as `reviewer` to confirm, then as `owner` (an operator independent of both) to approve. Authority that has already expired cannot be renewed in this build. Complete new-tenant measurement/reference setup remains pending.

Keep the local process running while using the application. `make dev` starts both the database and API in the same process tree. This also works in environments that isolate network namespaces between shell commands. Only one local runner can use the default ports 8000 and 55432 at a time; `IMPACT_DEV_DB_PORT` moves the development database port (`0` lets the operating system choose, which is what `make test` and the browser checks do so that parallel runners never collide).

The embedded PGlite database is for local development and qualification. Production requires separately operated native PostgreSQL, a qualified identity provider, and the release gates listed below.

## Try the complete workflow

1. Sign in as `author`. Open **Portfolio** and create a programme.
2. Open **Measurement** and add an observation for the seeded indicator. Use a unique source key, event date **2026-08-15**, value **80**, numerator **8**, and denominator **10**.
3. Open the new observation, choose **Submit for review**, and select the review template.
4. In **Review queue**, attempt to approve it as `author`. The server rejects self approval even though this fixture actor has a reviewer grant.
5. Sign out and sign in as `reviewer`. Approve the submitted observation.
6. Open **Results**, calculate the indicator for **2026-Q3**, and inspect the new result. On a fresh fixture, it displays **49.17** from pooled components **59 / 120**. It is explicitly **PROVISIONAL** because expected coverage is not configured.
7. Add another observation in that period, then refresh the results. The previous result is marked stale; its immutable calculation revision remains intact.

The seeded **OFFICIAL 46.36** result is synthetic baseline data, not an official calculation produced by this implementation. Fixture grants, delegation ceilings, operator records and the deployment qualification expire on **2027-09-01** (fixture version 2026-09-28; the instant is `FIXTURE_EXPIRES_AT` in `scripts/fixture_support.py`). Before that date, regenerate the fixture with `scripts/redate_fixture.py --expires <instant>`, which re-hashes every changed revision payload, and rerun the full suites; `scripts/run.py` refuses to start within 90 days of expiry, because the suites create authority that expires up to 60 days out and must stay inside the fixture ceilings. Do not disable expiry checks.

## Configure your own measurement workflow

1. As `author`, create a programme with type, dates covering 2026-Q3, the seeded reporting calendar and demonstration geography.
2. Open **Measurement setup → Definitions**. Create a COUNT measure with population, criteria, method and unit; submit for independent review. As `reviewer`, approve it in **Review queue**.
3. As `author`, open **Indicators**. Select your programme and approved definition, describe local applicability, and assign `Author` as collector and `Reviewer` as independent reviewer.
4. Open **Collection plans**. Select the indicator and 2026-Q3. Add one obligation per expected contributor, using unique period-specific source keys and UTC due dates. Submit; sign in as `reviewer` and approve the plan.
5. As `author`, activate the indicator. In **Portfolio**, inspect the programme, review its readiness checks, choose **Mark ready**, then reopen it and choose **Activate programme**.
6. Capture observations using the exact planned namespace and keys. Submit and approve independently. Calculate a result and inspect its coverage counts and missing-source table.

Approved revisions are immutable; amendments create a new revision after independent approval. Calculations begin as provisional results and become separate OFFICIAL revisions only through a successful programme-period close.

## Close a period and freeze a report

1. Complete and independently approve every collection-plan obligation, then calculate a current provisional result.
2. Open **Period close**, choose the active programme and period, provide a reason and select the independent review policy. The generated candidate lists every pinned input and blocker.
3. As `reviewer`, approve the close. If any source, plan or result changed after preview, approval fails and a fresh preview is required. Success creates OFFICIAL result revisions and a locked snapshot.
4. To correct a closed value, use **Request restatement**, name the exact included source and a window of no more than seven days, then obtain independent approval. Submit the governed correction, recalculate and close again. The new snapshot supersedes rather than overwrites the old one.
5. Open **Reports**, choose an approved template, locked snapshot and official snapshot result, then save and submit the draft. Numeric claims in narrative use declared placeholders such as `{{total_reached}}`; bare numeric claims are blocked. After independent approval, **Open approved export** renders the frozen internal HTML package and **Download CSV** exports the same pinned values.

See [docs/RELEASE-0.5.md](docs/RELEASE-0.5.md), [docs/RELEASE-0.6.md](docs/RELEASE-0.6.md) and [docs/RELEASE-0.8.md](docs/RELEASE-0.8.md) for exact semantics and limits.

## Publish to named recipients

1. As `author`, open an approved report and choose **Request controlled publication**. Select an active workspace recipient, a declared purpose, a UTC expiry no more than 90 days away, and whether CSV download is allowed.
2. Submit the disclosure under the independent publication-review template. The requester cannot approve their own request.
3. Sign in as `reviewer`, approve the exact disclosure in **Review queue**, then return to **Reports** and publish it. Current recipient eligibility, exact report revision and expiry are rechecked at publication time.
4. Sign in as the named recipient. Open the controlled HTML publication and, when allowed, download its exact CSV artifact. Each successful view/download is recorded separately.
5. As the publisher, withdraw the publication with a reason. Subsequent recipient requests receive the ordinary unavailable response; the frozen artifacts and access history remain intact.

This release intentionally has no anonymous/public link, external-contact delivery, schedule, PDF/DOCX/XLSX, signature or recall of already downloaded bytes. Recipients must already be active members of the workspace. See [docs/RELEASE-0.8.md](docs/RELEASE-0.8.md).

## Review an exception and recover stale calculations

1. As `author`, calculate a provisional result for an active indicator and open **Change requests**.
2. Create a collection-plan change, mark one obligation **Excepted**, record its reason and effective UTC time, and submit it for the configured independent review. At least one required obligation must remain.
3. As `reviewer`, inspect and approve the exact proposed plan revision. The historical expected count remains visible, while required completion excludes the reviewed exception.
4. As `author`, open **My work**. The plan change has marked affected provisional results stale and created one personal recalculation task plus a safe in-app notice.
5. Choose **Acknowledge** on the notice. The task remains open. Choose **Recalculate** on the task; a new result and lineage revision are created, the old result stays immutable and stale, and the task completes.

Recalculation is currently synchronous and user-triggered. The notice is delivered in-app by the worker (exactly once; `make dev` runs one); no email, SMS or push is sent for notices, and locked snapshots or frozen report packages are changed only through the separate restatement process. See [docs/RELEASE-0.7.md](docs/RELEASE-0.7.md) for exact security, transaction and scope limits.

## Try user administration

1. Sign in as `admin`; **People & access** opens automatically. Inspect members, grants, fixed role templates and scopes.
2. Open **Invitations**. Invite `invitee@example.test` with role **AUTHOR**, scope **All workspace records**, the default expiry and a reason. Copy the generated link. The invitation also records an email intent; in development the worker writes that message to the synthetic sink `.local/dev/synthetic-mail.jsonl`, never to a real mailbox.
3. Open the link in a separate private browser session, sign in as `invitee`, and accept it. That synthetic account has a provisioned identity but no membership before acceptance. A forwarded link does not work for another account.
4. As `admin`, open the new member and request the **REVIEWER** role. This adds access; it does not replace existing grants. The requesting administrator cannot approve it.
5. In another session, sign in as `owner`, open **Access requests** and approve the precise request. Both administrators' current delegation limits are checked by the server.
6. As `admin`, suspend the invited member. New tenant requests fail. Reactivate the member; their earlier session still cannot access the workspace until they sign in again. Permanent revocation cannot be undone through reactivation or another invitation.
7. Inspect the owner: ordinary suspension, revocation and owner-grant removal are prohibited. Reviewed ownership transfer is available under Workspace settings → Ownership: the current owner nominates and the exact nominee accepts. Unavailable-owner recovery remains unimplemented.

Administrative writes require authentication within the previous five minutes. Sign out and sign in again if prompted. Only a trusted, already-provisioned identity with a verified matching email can accept an invitation; the invitation is not an account-creation or email-verification service. Local email verification and delivery are explicitly synthetic. See [docs/RELEASE-0.2.md](docs/RELEASE-0.2.md) for rules, architecture, tests and limitations.

## Verify

```bash
make lint
make unit
make test
make reference
make browser
make idp
make worker        # with make dev running: one more outbox worker
IMPACT_FIXTURE_DSN=postgresql://postgres:<password>@127.0.0.1:5432/impact_test make native
IMPACT_FIXTURE_DSN=postgresql://postgres:<password>@127.0.0.1:5432/impact_test_idp .venv/bin/python scripts/run.py test --native --idp keycloak
```

`make test` creates a fresh, isolated in-memory fixture on an operating-system-chosen port and runs unit, live integration, and smoke tests; the native-only and live-provider tests skip there with a stated reason. It does not reset your development workspace. `make browser` installs the Linux browser dependencies and exercises the actual rendered UI. `make native` needs a superuser connection to an empty disposable `impact_test` or `impact_test_<suffix>` database: it provisions the five login roles (`scripts/provision_logins.py`), migrates as `impact_migrator`, runs the whole suite against the API on the app, identity and platform logins with `IMPACT_REQUIRE_UNPRIVILEGED_DB=1` (the native worker tests start worker processes on `impact_worker_login`), restarts the API between the two phases of the persistence check, runs the backup and restore drill on that database and the upgrade check from the previous schema on a fresh one, and writes `docs/evidence/native-application-tests.xml`, `native-qualification.json` and `native-restore-drill.json`. Test configuration and logs stay under `.local/test-*` for diagnosis; disposable database contents are not retained. `make idp` downloads Keycloak 26.7.4 once into `.local/keycloak/` and verifies its SHA-256, starts it on a loopback port in development mode with an in-memory database and a qualification realm, runs `qualification/test_live_idp.py` through `scripts/run.py test --idp keycloak` and the Chromium sign-in/sign-out check through `scripts/run.py idp-browser --idp keycloak`, and writes `docs/evidence/idp-tests.xml`, `idp-qualification.json` and `idp-browser-tests.json`; `--native --idp keycloak` runs the same suite on the provisioned login roles (`idp-native-tests.xml`). Generated provider credentials stay in a 0600 file under `.local/`. These directories are excluded from packages.

Evidence for build 0.25.0 is in [docs/evidence](docs/evidence), from 1 October 2026: the PGlite gate (822 passed, 58 skipped — 42 native-only and 16 live-provider — 1 deselected), 143 reference assertions and the native run on PostgreSQL 16.13 (861 passed, 19 skipped — the 16 live-provider tests, the 2 restart phases run separately and 1 PGlite-only case — 1 deselected; restart, restore and 26→27 upgrade checks PASS). The seventeen browser groups (140 checks, including `import-browser`, `evidence-browser`, `export-browser`, `requeue-browser` and the accessibility scan `a11y-browser`) and their screenshots were re-run for build 0.25.0. The live identity-provider files (16 + 16 + 2 browser checks) are from build 0.20.0 (30 September 2026); for builds 0.24.0 and 0.25.0 the live identity provider and the container stack (with the rotation, backup-set, restore-drill and alert steps) run in CI (`.github/workflows/qualification.yml`; `native-postgresql-gate` uses PostgreSQL 17.11). None of these runs establishes throughput, behaviour behind a connection pooler, persistence across a database restart or operational readiness.

## Structure

| Path | Purpose |
|---|---|
| `apps/api/impact_api` | Authentication, policy checks, validation, transaction services and calculations |
| `apps/web` | React / TypeScript web interface |
| `infrastructure/migrations` | Original migrations plus additive application, access, measurement, amendment, period-governance, reporting and controlled-publication migrations |
| `packages/contracts` | Preserved baseline, additive contract, and explicit implemented API subset |
| `qualification` | Implementation tests, including live security and workflow checks |
| `specification` | Preserved engineering package, fixtures, reference models and source requirements |
| `tools/dev-db` | Local PostgreSQL-compatible PGlite process |
| `tools/browser` | Real-browser qualification and screenshots |
| `tools/idp` | Keycloak qualification realm for the live identity-provider checks |
| `apps/api/impact_api/worker.py` | Outbox worker (`python -m impact_api.worker`; `make worker`) |
| `scripts` | Setup support, runners, the single migration runner, login provisioning, restore drill, upgrade check, the Keycloak runner (`idp.py`), fixture redating, contract export and packaging |
| `docs` | Implementation boundary, qualification results and next delivery tasks |

## Continue development

Read [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md), [docs/API-INVENTORY.md](docs/API-INVENTORY.md), [docs/QUALIFICATION.md](docs/QUALIFICATION.md), and [docs/NEXT-DELIVERY.md](docs/NEXT-DELIVERY.md). The original requirement and architecture documents remain under `specification/docs`.

Changes to API contracts should update `scripts/build_contracts.py` and the relevant additive contract module; regenerate the contract, then run `scripts/export_implemented_api.py`. The implemented subset contains 197 domain operations and 35 control-plane operations, plus the documented authentication/support routes. Preserve baseline files and the bytes of migrations already applied outside disposable development databases. `make package` produces `Impact-Platform-Source-v<build>.zip` (the build from `VERSION.json`, v0.25.0 here) with a SHA-256 manifest and verifies every archived file. Dependencies, generated passwords, keys, databases and logs are excluded.
