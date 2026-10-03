# Handover — Impact Platform at build 0.27.0

**Date:** 3 October 2026. **Prepared for:** whoever continues the engineering (human or AI agent — GPT/Codex, Claude or another) and for the owner. Start with [AGENTS.md](../AGENTS.md); the full engineering brief is [CLAUDE.md](../CLAUDE.md) (model-agnostic despite its name). This document holds no password, token, secret or personal contact detail, and must never hold one.

## 1. In plain words

The platform lets an organisation plan its programmes, collect data (by hand, web forms or spreadsheet import, with evidence files), have every record approved by a different person, calculate results, lock reporting periods and publish frozen reports to named people. It runs on one test ("staging") server. It is **not** production-ready: none of the 307 written requirements is accepted, and the first organisation has not yet used it for real work. Build 0.27.0 combines eleven pieces of work done in parallel on 2–3 October 2026. It is waiting for its automated checks (CI) and for the owner's go-ahead to merge; merging puts it on the staging server within about three minutes.

Confidence: high on what is written here about the code and the tests (checked on the integrated tree on 3 October); medium on the live server's state (the development sandbox cannot reach it — see §3).

## 2. Versions and status

| Item | Value |
|---|---|
| Build | **0.27.0** on branch `integration/0.27`, in the integration pull request to `main` titled "Build 0.27.0: integrate #67–#77 and GPT handover docs" (not merged) |
| `main` | build 0.26.0 at 0025767 (25a8dca plus #78, a CI-workflow-only change merged on 3 October 2026) until that pull request is merged |
| Schema | 32 migrations (0029–0032 new in this build; staging runs 28) |
| Domain API | 1.17.0, 230 implemented operations (`packages/contracts/openapi-implemented.json`) |
| Platform (control-plane) API | 1.8.0, 44 operations (`openapi-platform.json`); plus the support route `GET /v1/status` |
| Requirement ledger | **113 PARTIAL, 194 PENDING, 0 accepted** of 307 (`docs/COMPLETION-LEDGER.md`; was 106/201 at 0.26.0) |
| Release | Release 1 "Usable core" in progress (scope decision SD-01); Releases 2 and 3 planned |
| Fixture expiry | synthetic fixture grants expire 2027-09-01; `scripts/run.py` refuses to start within 90 days of it — regenerate with `scripts/redate_fixture.py` before 3 June 2027 |

What 0.27.0 adds, in one line each (details: [RELEASE-0.27.md](RELEASE-0.27.md)): imports that a collection plan can name in advance, so a planned import no longer blocks period close (acceptance gap A5 closed); theory of change, assumptions, target amendments after close and on-track/at-risk bands; forms in several languages, collection rounds and assignments (no screen yet), correction of returned work; charts in frozen reports, dashboard drill-down and a portfolio view; a record of refused access, retention policies and holds; operators renewing and deactivating each other; a service-notice banner and alerts delivered to a webhook or e-mail; a tested secure e-mail path ready for a provider; database pooler, restart and load evidence; clearer console screens and a waiting page instead of permission errors; a generated training video.

## 3. `main` versus the staging server

- **Staging**: https://168-144-78-191.sslip.io — one DigitalOcean droplet in Bangalore (2 vCPU, 4 GB) running everything with Docker Compose: the API and web client, the worker, PostgreSQL 17, Keycloak 26.7.4 (sign-in at `auth.168-144-78-191.sslip.io`, realm `impact`), Caddy with Let's Encrypt, a local mail capture (no e-mail provider), nightly verified backup sets, a weekly restore drill and a five-minute alert check.
- **How it updates**: a timer on the server pulls `main` every 3 minutes and runs `deploy/update.sh` (builds the image on the server, applies migrations, restarts services). Nobody pushes to the server and there is no inbound SSH from development sandboxes; the owner reaches the server only through the DigitalOcean web console (droplet → Access → Launch Droplet Console) and the console scripts in [DEPLOYMENT-GUIDE.md](current/DEPLOYMENT-GUIDE.md) §4.
- **Status page**: https://168-144-78-191.sslip.io/deploy-status.json (`result`, deployed `commit`, `schema_version`, `alerts`, `operations`; secrets redacted).
- **Live state, read on 3 October 2026 at about 02:05 UTC** (the status page fetched over the web; the development sandbox has no other route to the server): `result` ok, `commit` 0025767 (`main`: build 0.26.0 plus the CI-only #78), `schema_version` 28, last deployment finished 00:41 UTC; the nightly backup succeeded (two daily sets); **one warning, `RESTORE_DRILL_STALE`** — the weekly restore drill has never recorded a result on this server (`operations.restore_drill.outcome` is null; its timer runs on Sundays at about 23:15 UTC). The owner can run it now from the DigitalOcean console with `sudo /opt/impact/repo/deploy/restore-drill.sh` (DEPLOYMENT-GUIDE.md §6.2; SUPPORT-RUNBOOK.md §4.6). After the merge of build 0.27.0, `commit` should show the merge commit and `schema_version` 32.
- **On merge of build 0.27.0** the server applies migrations 0029–0032 (rehearsed on a populated schema-28 database, not on the staging data). Initial-access requests proposed but not applied fail with `ACCESS_PROFILE_CHANGED` and must be proposed again; an organisation that already applied initial access cannot grant the 16 capabilities this build added until a reviewed ceiling widening exists. Nothing else needs a manual step; new optional settings are listed in RELEASE-0.27.md "Owner-facing notes".

## 4. CI

- One workflow, [`.github/workflows/qualification.yml`](../.github/workflows/qualification.yml), four jobs: `local-reference-and-browser` (lint, the PGlite suite, the reference suite, all browser groups), `live-identity-provider` (a real Keycloak), `native-postgresql-gate` (native PostgreSQL 17 on provisioned logins, restore drill, upgrade from schema 28, live provider on native logins, and an advisory pooled subset) and `container-stack` (the whole deployment path in Docker: `update.sh`, smoke, first sign-in, secret rotation, backup set, restore drill, alert exercise). **`container-stack` is the only check of the deployment path; it cannot run in a development sandbox.** Since #78 (merged into `main` on 3 October 2026) a push runs the workflow only on `main`; any other branch is qualified by its pull request, once per push, and a newer push cancels the run in progress; a change that touches only `**.md` or `docs/**` starts nothing; the jobs are capped at 30, 20, 40 and 45 minutes; `workflow_dispatch` runs the full suite on any branch.
- The GitHub Actions spending limit has been exhausted three times (1–3 October 2026). When it is, every job fails within seconds **with zero steps** and the annotation "The job was not started because recent account payments have failed or your spending limit needs to be increased" — that is billing, not code: raise the budget, then re-run the jobs from the pull request's Checks tab.
- At handover: Actions refused every job from about 00:30 to 00:46 UTC on 3 October 2026 — the checks of `main` at 0025767 (#78), of #79 and of the imports branch head bd1f43f failed that way and have not been re-run — and ran again from about 00:46 UTC: #69 and #77 passed all four jobs on their updated heads (which merged `main`), and #74's final head (fde4411) passed all four at 01:59 UTC. The integration pull request's own result is on its Checks tab; it is the first CI run of the integrated build. If a job there failed within seconds with zero steps, it is billing again.
- Before the integration, four component pull requests (#68, #69, #74, #77) had no CI on their final heads; #69, #74 and #77 have since passed on their updated heads, and #68's final head (with #79) and `main` at 0025767 (#78) have had no CI run at all. The integration's local runs (§9) and the integration pull request's CI are the verification of the combination.

## 5. Open pull requests

After this integration the only open pull request that matters is the integration pull request from `integration/0.27` ("Build 0.27.0: integrate #67–#77 and GPT handover docs"). The eleven component pull requests #67–#77 stay open until it is merged **with a merge commit** (not squash, not rebase): GitHub then marks them merged. Do not close them by hand.

## 6. Owner decisions still open

| Decision | Why it matters | Where it is prepared |
|---|---|---|
| **E-mail provider** (and a sending subdomain the owner controls) | No invitation, recovery code or alert e-mail reaches anyone until one is configured; switching on is a configuration step since 0.27.0 | [EMAIL-PROVIDER-DECISION.md](current/EMAIL-PROVIDER-DECISION.md) — Postmark first, Amazon SES (Mumbai) if one AWS bill is wanted, Brevo as the free fallback |
| **Off-server backup storage** | Backups live on the same droplet as the data; losing the droplet leaves only DigitalOcean's own daily droplet backups | DEPLOYMENT-GUIDE.md §6 |
| **GitHub Actions budget** | The limit ran out three times on 1–3 October 2026 (most recently about 00:30–00:46 UTC on 3 October); while it is out nothing can be verified in CI and nothing should be merged; since #78 a pull request runs the four jobs once per push and documentation-only changes skip CI | §4 above; PARALLEL-WORK.md |
| **Google integration project** (Google Cloud project and OAuth client) | Needed before any Google Sheets/Drive import or export | BACKLOG.md slice 11 |
| **Map tile provider** (or an offline base map) | Needed before maps; has content-security-policy and privacy consequences | BACKLOG.md slice 12 |
| **Budget tracking pulled forward from Release 3?** | Finance is Release 3 under SD-01; a bounded planned-versus-actual subset is specified | BACKLOG.md slice 4 |
| Named on-call people, hours and response targets | The rota file and the readiness exercise exist; the names do not | SUPPORT-RUNBOOK.md, `deploy/on-call.example.json` |
| Alert destination | Alerts reach a person only when `ALERT_WEBHOOK_URL` or `ALERT_EMAIL_TO` is set in `config.env` | DEPLOYMENT-GUIDE.md §6.4 |

## 7. Known issues and fragile spots (top items)

Full list: CLAUDE.md §11. The ones most likely to bite next:

1. **Applied tenants' ceilings cannot be widened.** Organisations that applied initial access before a build that adds capabilities (v1 tenants; v2 tenants before 0.27.0) cannot grant the new capabilities. Designed, not built (RELEASE-0.27-operators.md).
2. **No real e-mail, no paging.** E-mail goes to a capture on the server; alerts reach the status page, the banner and (if configured) a webhook — nobody is paged.
3. **Single-server backups**, no off-server copy; no recovery-point or recovery-time target is met; a restore does not replay privacy erasures.
4. **Synchronous imports**: a 500-row commit holds the organisation's write lock for about 14 s; the asynchronous design is recorded in RELEASE-0.27-imports.md.
5. **Order-dependent and timing-sensitive tests**: run the full suite in its own (alphabetical) order before trusting a slice; identify records a test created by identity, never by "the newest". Builders' focused runs are not suite-order runs.
6. **Profile hash changes** whenever a capability is added: pending initial-access requests must be re-proposed after such a deployment.
7. **Behind a connection pooler** (not deployed) an outage would be reported only after the pooler's wait timeout; configure `query_wait_timeout` and `server_login_retry` to a few seconds if one is ever deployed.
8. **UI selectors**: a change from a form to a dialog breaks browser checks and the training-video generator alike; grep `tools/browser/`.
9. **Port 8000** is every runner's default; set `IMPACT_PORT` when anything else runs. The development machine has 2 CPUs and 7 GB: run full suites one at a time.
10. **Fixed at this integration** (keep the regression tests): a late value could enter a locked period when a tenant had two reporting calendars (`test_import.py::test_a_locked_period_refuses_late_values_when_another_calendar_overlaps_it`; #79 fixed the same defect on the imports branch more narrowly — the integration keeps the broader check and #79's test in `test_period_governance.py`); two security/privacy tests picked the wrong sweep in suite order (`test_retention.sweep_created_since()`, #74's own fix, adopted at integration); a browser check matched three "Reason" fields after the retention panels were added; `status-browser` read the on-call line before it had loaded (it now waits for the placeholder to go — PGlite serves one connection, so any check that reads a panel's text must wait for the loaded state, not for the element).

## 8. Setting up the first organisation on staging

By design three different people are needed: the deployment owner (the first platform operator), a colleague who becomes the second platform operator, and a colleague who will own the organisation. No setting removes that; it is what makes every approval independent. The click-path, all in the web application since build 0.26.0, is [DEPLOYMENT-GUIDE.md §4.1](current/DEPLOYMENT-GUIDE.md): nominate the second operator and create their sign-in; create the future owner's sign-in; each signs in once (own password and authenticator app); request the organisation naming its owner; the owner accepts and nominates a recovery contact; the second operator approves the contact and activates the organisation; the owner proposes initial access with a second administrator, who accepts, and the second operator approves; then **People & access → Reference data → Set up the standard reference data**. One-time passwords are shown once to the person who created the sign-in and must be handed over in person or by phone.

A narrated walkthrough of exactly this path and of one measurement cycle can be generated from the real UI with `tools/browser/training-video.mjs` and `tools/browser/narrate.py` ([TRAINING-VIDEO.md](TRAINING-VIDEO.md)); the video itself is not stored in the repository.

## 9. Quality evidence summary (build 0.27.0, local, final tree)

| Suite | Result |
|---|---|
| `make lint` | clean |
| `make unit` | 379 passed, 59 skipped |
| PGlite gate (`make test`) | 952 passed, 73 skipped (56 native-only, 17 live-provider), 0 failed, 1 deselected |
| Native PostgreSQL 16.13 on the provisioned logins (`make native`) | 1,000 passed, 25 skipped, 0 failed, 1 deselected; API restart, backup/restore drill and upgrade from schema 28 to 32: PASS |
| Native through PgBouncer with a database stop and start (focused) | 21 passed |
| Reference (design) suite | 143 passed |
| Browser (`make browser`, Chromium), re-run on the final tree after #74's last two commits | 153 checks in 19 groups passed (one check's waiting race fixed in `status-check.mjs`) |
| Training-video generator | generated end to end (not kept) |

Not run locally: the live identity-provider suite (17 tests) and the container stack — both run in CI. Recorded counts and their meaning: [QUALIFICATION.md](QUALIFICATION.md). Nothing above is load, availability or security-assessment evidence beyond what each line says.

## 10. Prioritised next steps

1. **Get the integration pull request green** in CI (all four jobs), then ask the owner to merge it with a merge commit; watch `deploy-status.json` until `result` is `ok` with schema 32 (§3). Independently of the merge, ask the owner to run the restore drill once by hand (`sudo /opt/impact/repo/deploy/restore-drill.sh` in the DigitalOcean console) to clear `RESTORE_DRILL_STALE` and prove the backups restore on the server.
2. **Hosted user acceptance on staging** with [UAT-PACK.md](current/UAT-PACK.md) (22 scenarios), after the first organisation is set up (§8). Record results in the sign-off sheet.
3. **Owner decisions** in §6, starting with the e-mail provider and off-server backup storage.
4. **Release 1 remainder without an owner decision** ([NEXT-DELIVERY.md](NEXT-DELIVERY.md)): the reviewed ceiling widening for applied tenants; screens for collection rounds and assignments; browser checks for the Access denied, Retention policies and Retention holds panels; Keycloak signing-key rotation in the live-provider suite; the asynchronous import executor; the quantified standard workload on the staging droplet; a crash restart and per-tenant fairness; penetration testing.
5. **Product backlog beyond Release 1**: the twelve ready-to-run slices in [handover/BACKLOG.md](handover/BACKLOG.md) (KoboToolbox connector, saved views and governed exports, workplans, indicator library, Unicode PDF, discussions, offline web forms, UI localisation, …), run as parallel slices with one integrator per [handover/PARALLEL-WORK.md](handover/PARALLEL-WORK.md) — four or five builders at a time, one push each.

## 11. Access and secrets (where they are, never what they are)

- **Repository**: GitHub `nakul175/impact-platform`; `main` is the deployed branch.
- **Server secrets**: generated once on the droplet into `/opt/impact/secrets.env` (mode 0600, never printed, never in the repository); rotated with `deploy/rotate-secrets.sh` (DEPLOYMENT-GUIDE.md §10). Optional settings go in `/opt/impact/config.env`.
- **Sign-in accounts**: Keycloak on the server; created only through the platform's governed flows or the owner's console scripts; one-time passwords are never stored or logged.
- **Development**: every local password, key and database is generated under `.local/` on the developer's machine and excluded from the repository and from packages.

## 12. Who has worked on this repository, and with what

Builds up to 0.27.0 were written by AI coding agents (Anthropic's Claude, through Claude Code) under the owner's direction: several builders in parallel and one integrator per build, following [handover/PARALLEL-WORK.md](handover/PARALLEL-WORK.md). **The owner has also used Cursor's agent on this repository**: #78 (the CI workflow change on `main`), #79 (the period-lock fix on the imports branch) and #74's last three commits on 3 October 2026 are by "Cursor Agent". Nothing in the repository depends on either tool: `AGENTS.md`, `CLAUDE.md` (the model-agnostic engineering brief, despite its name) and the documents they link are the whole working contract. Expect a component branch to receive commits from another tool while you integrate it: fetch every branch again just before you push (PARALLEL-WORK.md, integrator step 9).
