# Handover — Impact Platform and nonprofit AI enablement

**Local qualification observation — 16 October 2026:** The 56-story cohort has verified bounded local positive, authorization/refusal and error/recovery evidence for **49/56** stories on clean source `645466ff032cbcd7e9927a646f44c75318fef24a`: 2,648 passed, zero failures, 229 skipped and one deselected. Seven reserved-disabled AI use cases remain external-runtime blocked; substituted component tests are excluded from these counts. Additive migration0118 registers the generated WorkItem draft profile without applying existing-tenant authority;0001–0117 unchanged. [Qualification scope and evidence](RELEASE-1.42-three-gate-qualification.md). Root remained sole integration writer with read-only independent code/evidence review. No remote CI, main merge, staging observation/deployment or human/owner acceptance was performed in this continuation; the remote observations below are historical.

**Current observations — 12 October 2026, 07:07 UTC:** Imprana Commons only, sole active APL-361/US-DX-01a. Public draft [PR96](https://github.com/nakul175/impact-platform/pull/96) at `d2368091a29a296b86da399f7e7d01f4bd6e073a`, build0.40.0/unreleased, domain1.31/platform1.11/schema47. Checks, browser/reference, live identity provider and container-stack pass on that head. [Native qualification38212778560](https://github.com/nakul175/impact-platform/actions/runs/38212778560) fails the worker batch precondition:2694passed/1failed/29skipped. The three diagnosis clone restore failures from the preceding head are resolved. The bounded dispatch-only scenario followup has a separate actual9-case native PASS and source pins; fresh exact-head hosted qualification remains required after publication. [Raw bounded evidence](evidence/candidate-0.40/native-dispatch-preparation-20261012/run-7/RUN-RECEIPT.json).

Owner explicitly authorized public code/documentation/synthetic evidence export and existing-limit CI, with no budget increase. Publication is complete; no main merge or staging deployment. Last read-only staging observation (12October, approximately04:29UTC) remains `8a1e405f0086033dfb25ad834689a08bfe9f1eea`, schema43 and healthy services. Populated43→47 container promotion, independent human review/release dispositions and operator maintenance gates are held; no acceptance/signoff invented. Delivered/deployed count remains **0/50**. [Current engineering handover](engineering/delivery-system-20261011/HANDOVER.md).

<details><summary>Preserved 11 October observation (superseded)</summary>

**Current observations — 11 October 2026, 17:34 UTC:** Imprana Commons only. Local `feat/imprana-diagnosis-20261011` at tested application head `79b2316` is build 0.40.0 (unreleased), domain API 1.31.0, platform API 1.11.0, registered schema 47. Full native regression: 2,626 passed / 28 skipped / zero failures; separate actual database outage, 18 provider tests and 10 browser groups / 318 assertions pass. A bounded deployment writer-quiescence patch is being qualified separately and has not run on containers or staging. Sole active story US-DX-01a; delivered/deployed toward the new target: **0/50**. [Exact qualification receipt](evidence/candidate-0.40/registered-head-full-20261011/FULL-NATIVE-RECEIPT.json) and [current engineering handover](engineering/delivery-system-20261011/HANDOVER.md).

Read-only GitHub/main observation: `git ls-remote` returned `8a1e405f0086033dfb25ad834689a08bfe9f1eea` (PR #94); its committed version is 0.39.0 / domain 1.28.0 / platform 1.11.0 and 43 migration files. The local candidate descends from that commit. Actual current main CI and live staging commit/health were not verified in this continuation. The public repository has no diagnosis feature branch or PR yet. No remote publication, merge, deployment or new spending performed; export, paid CI, human release and maintenance gates remain.

</details>

**Complete native backlog refinement — 10 October 2026:** Nakul approved the remaining task/story expansion. All 1,553 unique native project issues are saved and fully read-back verified: 54 epics, 368 stories and 1,131 tasks, with 779 prerequisite edges and proposed plans for all 1,328 original scenarios. [Full verification](product/refinement/readback-verification.json) passes with zero failures; original criteria, 24 task cores, source statuses and estimates are preserved. Twelve planning/import guard tests pass. [Complete refinement](product/10-COMPLETE-BACKLOG-REFINEMENT.md) and [Linear continuation](product/07-LINEAR-IMPORT-STATUS.md) contain real IDs, immutable baseline/partial evidence and the resolved three-duplicate incident. Only the optional additional overview document awaits separate upload approval; its source is preserved in Git. This completes planning integration, without feature implementation or acceptance claims.

**Initial product planning import — 10 October 2026 (preserved baseline):** Nakul authorised the vision → strategy → roadmap → release goals → epics → stories → criteria → technical tasks structure and Linear integration. Eleven product documents, five milestones and the original 446 native issues were saved and verified: 54 epics, 368 stories and 24 tasks/36 dependencies. The expansion above adds 1,107 tasks and exact additive sections without replacing that baseline. Start at [docs/product/README.md](product/README.md). Four Sprint 1 stories remain In Review pending owner acceptance; Sprint 2 is proposed. This planning handover does not replace the engineering status evidence below.

**Historical status — verified 8 October 2026 (preserved; current observations above supersede these repository version/main values):**

| Item | Value |
|---|---|
| Build | **0.36.0** (`VERSION.json`). A development build: 0 of 307 requirements accepted, synthetic data only, not production-ready |
| Domain API | 1.25.0, 261 implemented operations (`packages/contracts/openapi-implemented.json`) |
| Platform (control-plane) API | 1.10.0, 52 operations (`packages/contracts/openapi-platform.json`) |
| Schema | 40, the number of files in `infrastructure/migrations/`; 0001–0040 are frozen; the next migration is 0041 |
| `main` | `5eb9b3b` (PR #86, documentation only, 8 October 2026) on `2ab2153` (PR #85, build 0.36.0, merged 6 October 2026 at 18:56 UTC) |
| CI | all four jobs of the `main` push run for `2ab2153` succeeded on 6 October 2026 ([run 37515232963](https://github.com/nakul175/impact-platform/actions/runs/37515232963)) |
| Staging | `main` deploys itself (§3); whether the server currently runs `2ab2153` has not been checked from a development workspace |
| Latest records | [RELEASE-0.36-procurement-preview.md](RELEASE-0.36-procurement-preview.md) (what 0.36.0 adds and its local evidence) and [CLAUDE-HANDOFF-2026-10-06.md](CLAUDE-HANDOFF-2026-10-06.md) (the 6 October continuation notes, preserved drafts and limits) |

When any of these change, change this table and `VERSION.json`; the other documents point here instead of repeating the figures.

**Earlier checkpoints (superseded; their counts and evidence stay in the linked notes):** 0.35, 6 October 2026, local head `be65086` on `integration/0.32-tola-ai-sprint` ([RELEASE-0.35-practical-ai-workspace.md](RELEASE-0.35-practical-ai-workspace.md)); 0.34, 5 October, migration 0040 closed the private-advice cleanup disclosure found at 0.33 ([RELEASE-0.34-plan-portability.md](RELEASE-0.34-plan-portability.md)); 0.33, 5 October, programme evidence and internal member advice ([RELEASE-0.33-tola-ai-extension.md](RELEASE-0.33-tola-ai-extension.md), [SPRINT-HANDOVER-2026-10-05.md](SPRINT-HANDOVER-2026-10-05.md)); 0.32, 5 October, reviewed access extensions, saved guidance history and Mac operations portability ([RELEASE-0.32-tola-ai-sprint.md](RELEASE-0.32-tola-ai-sprint.md)); 0.31 and 0.30, 5 October, nonprofit AI planning and the adoption workspace ([RELEASE-0.31-nonprofit-ai-planning.md](RELEASE-0.31-nonprofit-ai-planning.md), [RELEASE-0.30-ai-adoption-tool.md](RELEASE-0.30-ai-adoption-tool.md)); 0.29, merged in #84 as `69c2cca` and deployed to staging on 5 October at 04:16 UTC with healthy services and no alerts ([RELEASE-0.29-logframe-reuse.md](RELEASE-0.29-logframe-reuse.md)); 0.28, #81 (`e6c23b4`: application executor and queued imports, migration 0033) and #82 (`6712970`: collection-round and assignment screens) merged on 4 October with four green jobs each ([RELEASE-0.28-import-executor.md](RELEASE-0.28-import-executor.md), [RELEASE-0.28-rounds-screen.md](RELEASE-0.28-rounds-screen.md), [RELEASE-0.28-ci-sunday.md](RELEASE-0.28-ci-sunday.md)).

The body below is the handover written on 3 October 2026 at build 0.27.0 and is kept as written: §2, §3, §4 and §9 describe that build, and the live-server facts in §3 are the last ones observed.

**Date:** 3 October 2026. **Prepared for:** whoever continues the engineering (human or AI agent — GPT/Codex, Claude or another) and for the owner. Start with [AGENTS.md](../AGENTS.md); the full engineering brief is [ENGINEERING-BRIEF.md](current/ENGINEERING-BRIEF.md) (model-agnostic despite its name). This document holds no password, token, secret or personal contact detail, and must never hold one.

## 1. In plain words

The platform lets an organisation plan its programmes, collect data (by hand, web forms or spreadsheet import, with evidence files), have every record approved by a different person, calculate results, lock reporting periods and publish frozen reports to named people. It runs on one test ("staging") server. It is **not** production-ready: none of the 307 written requirements is accepted, and the first organisation has not yet used it for real work. Build 0.27.0 combines eleven pieces of work done in parallel on 2–3 October 2026. Pull request #80 passed all four CI jobs and was merged on 3 October; it deployed to staging at 02:35 UTC.

Confidence: high on what is written here about the code and the tests (checked on the integrated tree on 3 October); medium on the live server's state (the development sandbox cannot reach it — see §3).

## 2. Versions and status

| Item | Value |
|---|---|
| Build | **0.27.0**, merged in #80 at `c6ac17a` and deployed to staging |
| `main` | `c6ac17a3d4af9025b69a1daccdb12f48e0bb8c3f` (#80 merge) |
| Schema | 32 migrations (0029–0032 new in this build; staging runs 32) |
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
- **Live state, checked on 3 October 2026 at 03:55 UTC**: `result` ok, commit `c6ac17a` deployed at 02:35 UTC, `schema_version` 32, all services up. The sole alert is `RESTORE_DRILL_STALE`; the weekly timer runs Sunday at about 23:15 UTC. This report came from the owner after a live check; it has not been independently rechecked in this development workspace. Use a cache-busting query string when fetching `deploy-status.json`.
- **After the 0.27.0 deployment**, initial-access requests proposed but not applied must be proposed again (`ACCESS_PROFILE_CHANGED`); an organisation that already applied initial access cannot grant the 16 capabilities this build added until a reviewed ceiling widening exists. New optional settings are listed in RELEASE-0.27.md "Owner-facing notes".

## 4. CI

- One workflow, [`.github/workflows/qualification.yml`](../.github/workflows/qualification.yml), four jobs: `local-reference-and-browser` (lint, the PGlite suite, the reference suite, all browser groups), `live-identity-provider` (a real Keycloak), `native-postgresql-gate` (native PostgreSQL 17 on provisioned logins, restore drill, upgrade from schema 28, live provider on native logins, and an advisory pooled subset) and `container-stack` (the whole deployment path in Docker: `update.sh`, smoke, first sign-in, secret rotation, backup set, restore drill, alert exercise). **`container-stack` is the only check of the deployment path; it cannot run in a development sandbox.** Since #78 (merged into `main` on 3 October 2026) a push runs the workflow only on `main`; any other branch is qualified by its pull request, once per push, and a newer push cancels the run in progress; a change that touches only `**.md` or `docs/**` starts nothing; the jobs are capped at 30, 20, 40 and 45 minutes; `workflow_dispatch` runs the full suite on any branch.
- The GitHub Actions spending limit has been exhausted three times (1–3 October 2026). When it is, every job fails within seconds **with zero steps** and the annotation "The job was not started because recent account payments have failed or your spending limit needs to be increased" — that is billing, not code: raise the budget, then re-run the jobs from the pull request's Checks tab.
- At handover: Actions refused every job from about 00:30 to 00:46 UTC on 3 October 2026. The integration pull request #80 subsequently passed all four jobs on its final head `ff9ba7f`; it was merged as `c6ac17a`. If future jobs fail within seconds with zero steps, check the spending limit before retrying.
- Before the integration, four component pull requests (#68, #69, #74, #77) had no CI on their final heads; #69, #74 and #77 have since passed on their updated heads, and #68's final head (with #79) and `main` at 0025767 (#78) have had no CI run at all. The integration's local runs (§9) and the integration pull request's CI are the verification of the combination.

## 5. Open pull requests

Pull requests #67–#82 are merged. #82 merged as `6712970` after four green PR jobs. The subsequent `main` run exposed a date-dependent backup unit test on Sunday; the separate fix is described in [RELEASE-0.28-ci-sunday.md](RELEASE-0.28-ci-sunday.md). Staging deployment health remains unverified from this workspace.

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

Full list: ENGINEERING-BRIEF.md §11. The ones most likely to bite next:

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

1. **Confirm the live executor and fix the Sunday backup test.** The executor and collection-round screen have merged; the Sunday-dependent test fix is in [RELEASE-0.28-ci-sunday.md](RELEASE-0.28-ci-sunday.md). Kobo follows only after staging reports `ok`, the current commit, schema 33 and a healthy executor. `main` auto-deploys after merge; never merge another PR without four green CI jobs and the owner's explicit confirmation. The weekly restore-drill timer should clear `RESTORE_DRILL_STALE` after its Sunday run; verify the result then.
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
