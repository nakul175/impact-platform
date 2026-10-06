# AGENTS.md — Impact Platform

**Current local candidate, 6 October 2026:** Build 0.35.0 integrates guided manual practice, canonical saved-plan preparation review, entered-cost category clarity and an isolated fictional public walkthrough. Domain 1.25.0 (261 operations), platform 1.10.0 (52) and schema 40 are unchanged. The corrected candidate has passing strict build/lint; native 2,102 pass/26 skip/1 deselected, PGlite 2,037/91/1 and unit 1,242/62; both native restarts, populated 33→40 upgrade and a restore of 190 tables/108,188 rows (71,506,951 bytes) passed. Reference 143 is design-only. Final 26 browser modes passed 281 groups with zero failures/skips; four pure prerequisites passed 66 groups. All 423 browser sources, eight built/served files and 40 migration hashes remained unchanged; 965 historical files were restored. Earlier failed runs remain preserved. Automated accessibility found zero violation classes; the broad audit retains 50 manual-review incomplete entries. No requirements are accepted by these overlapping local results. Two current UI limitations—fresh profile-only brief replacement and misleading Unknown/Stale archive wording—have reviewed private 0.36 fixes pending integration and fresh qualification. Save this local checkpoint before that next increment. Four exact-head hosted CI jobs, merge and deployment remain pending; the owner has authorised main merge after those jobs pass, and separate CI-spending approval is pending. Last verified deployment remains build 0.29/schema 33 at `69c2cca618ae8dcde8f981c48ece8a1e60f0ff70`. See [current release](docs/RELEASE-0.35-practical-ai-workspace.md) and [handover](docs/HANDOVER.md). Earlier dated facts retain their historical scope; migrations 0001–0040 remain frozen.

Entry point for any engineering agent (GPT/Codex, Claude or another) and for human engineers. Read it completely before changing anything. It is short on purpose; the full brief and the current state are linked below.

## What this is

The Impact Platform is a multi-tenant monitoring, evaluation, learning and impact-reporting web application for organisations that run development programmes: programme set-up and governed indicator definitions, results frameworks and targets, data collection by web forms and CSV/XLSX import with evidence files, independent review of every record by a different person, deterministic calculations, locked reporting periods, frozen report packages exported as PDF/XLSX/DOCX and controlled publication to named recipients. Python/FastAPI API, PostgreSQL with forced row-level security, a React web client, a background worker, Keycloak for sign-in, deployed with Docker Compose on one staging server. Build **0.27.0** (schema 32, domain API 1.17.0, platform API 1.8.0) is a development build: 0 of 307 requirements are accepted, Release 1 ("Usable core") is in progress, and nothing may be described as production-ready.

## Read in this order

1. **`AGENTS.md`** (this file): rules, commands, safety, how to work with the owner.
2. **[`docs/HANDOVER.md`](docs/HANDOVER.md)**: the state at handover (3 October 2026) — versions, what is on `main` versus live on staging, CI, open owner decisions, known issues, next steps.
3. **[`CLAUDE.md`](CLAUDE.md)**: despite its file name, the **full, model-agnostic engineering brief** — status, where to look, domain vocabulary, the rules below with their context, architecture as built, data model and database security, commands, how to change things, the security model, what is next and the verified fragile spots. It is binding and nothing in it is specific to one assistant.
4. **[`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md)**: what the current build does and does not do, area by area.

Then as needed: [`docs/RELEASE-0.27.md`](docs/RELEASE-0.27.md) (latest build and its slice notes), [`docs/handover/BACKLOG.md`](docs/handover/BACKLOG.md) (TolaData parity map and ready-to-run slices), [`docs/handover/PARALLEL-WORK.md`](docs/handover/PARALLEL-WORK.md) (builder rules and integrator checklist), [`docs/current/DOCUMENTATION-INDEX.md`](docs/current/DOCUMENTATION-INDEX.md) (every document), [`docs/current/DEPLOYMENT-GUIDE.md`](docs/current/DEPLOYMENT-GUIDE.md) (the staging server).

## Rules that must never be broken

Copied verbatim from CLAUDE.md §4 (which is the source; keep the two identical).

<!-- BEGIN CLAUDE.md §4 (verbatim) -->

Business rules (FSD; RULE01–26):
1. Deny by default; client-supplied IDs are selectors, never proof; missing and hidden resources both return `RESOURCE_UNAVAILABLE` 404.
2. Read, export, approve, publish and sensitive-field access are separate capabilities; export is not implied by read; custody never implies data access.
3. No self-approval; independence is by natural person; editing as a reviewer makes you an author; a stale approval never authorises a newer revision.
4. Approved records are immutable; material change is a new revision; audit is append-only.
5. Official numbers come only from approved, versioned, deterministic rules over approved source revisions. AI (when it exists) proposes; it never supplies official arithmetic.
6. Decimal arithmetic (strings in transport, NUMERIC(38,12) in storage, ≥50-digit intermediates); round half-up once at display (0–6 places); never sum displayed values; pooled percentage = Σnumerators/Σdenominators (50/100 + 1/10 → 51/110 = 46.36, never 30); zero denominator → UNDEFINED, never 0.
7. Coverage denominators come from the period's obligation snapshot, not current membership; zero expected is "not applicable", not 100 %.
8. Close requires every mandatory obligation approved, no blockers, unchanged sources since preview, and an independent decision; late data stays outside the snapshot.
9. Report approval and publication are separate decisions; a wider audience is a new disclosure.
10. Sensitive actions need authentication within the previous 300 seconds plus the configured assurance (ACR); token issuance time does not count, only `auth_time`.
11. Synthetic fixtures only; never commit credentials, keys, `.local/`, participant data or real personal data.

Engineering invariants (HLD/LLD/MIG; verified in code):
12. Every tenant table carries `tenant_id` in its primary key and every foreign key; every new tenant table gets `ENABLE` + `FORCE ROW LEVEL SECURITY` and the `tenant_fence` policy.
13. `set_config('impact.tenant_id', …, true)` is transaction-local and set before any tenant-table access; never session-level; never reuse a connection of uncertain state.
14. Runtime roles (`impact_app`, `impact_identity`, `impact_platform`, …) are NOLOGIN-derived, non-owner, NOBYPASSRLS; the API never holds the migration DSN or `impact_owner`; `store.py` refuses superuser/BYPASSRLS/owner connections in staging and production. Keep that guard.
15. `object_revision` is insert-only (privacy removal through `impact_privacy` under the `revision_removal_guard` trigger is the sole exception). Projections listed as insert-only in migration 0003 stay that way. `operation_receipt` is insert-once.
16. Head + revision + projection + audit event + outbox event + receipt commit in one transaction. No external call inside that transaction. An outbox or `platform_event` row is intent, never proof of delivery.
17. Take the tenant advisory lock (`pg_advisory_xact_lock(hashtextextended(tenant_id,0))`) before any tenant write, before resolving authority; respect the LLD lock order; never auto-retry semantic conflicts.
18. Snapshot members, `official_result_snapshot`, `report_package_binding` and publication artifacts are never re-pointed; corrections create new versions.
19. Server-owned fields (issuer, approver, author, scan state, epochs) never come from request bodies; every write DTO is closed (`additionalProperties:false`); unknown fields and duplicate JSON keys are rejected.
20. `impact_platform` stays inside the RESTRICTIVE object-type lists of migrations 0013/0014; app and identity roles can never create custody, delegation ceilings or recovery evidence (only `accept_custody`, `apply_initial_authority` and the control plane can).
21. Cursors are HMAC-signed, bound to tenant/principal/route/visibility, 15-minute TTL; no `total_rows`.
22. Migrations are additive, ordered, checksum-ledgered; never change a byte of 0001–0040; next is 0041 (contiguous numbering); no destructive down migration.
23. Keep the "current implementation" versus "retained target design" split in every document you touch; a documentation edition is not a product run.

<!-- END CLAUDE.md §4 -->

## Safety rules for agents

- **`main` deploys itself.** The staging server pulls `main` every 3 minutes and runs `deploy/update.sh` (migrations included). Never push to `main` and never merge a pull request without **all four CI jobs green** (`local-reference-and-browser`, `live-identity-provider`, `native-postgresql-gate`, `container-stack`) **and the owner's confirmation**. `container-stack` is the only check of the deployment path and cannot run in a development sandbox. If every job fails instantly with zero steps, the GitHub Actions spending limit is exhausted: that is billing, not code — stop and tell the owner. CI runs on pushes to `main` and once per push to a pull request (a newer push cancels the run in progress); documentation-only changes start nothing; every push therefore costs a full run.
- **Secrets and personal data.** Never commit credentials, keys, tokens, `.local/`, `secrets.env`, generated passwords, participant data or real personal data. Test and demo data are synthetic only (`example.org`, `example.test`, the fixture identities).
- **Accounts.** Never create or set a user's password, never type credentials into anything and never act as a person. Sign-in accounts are created only by the platform's governed flows (a platform operator in Tenant lifecycle, or the owner's console scripts on the server), with one-time passwords handed over by people.
- **Independence is never relaxed.** No self-approval shortcuts, no synthetic, login-less or "system" second approver, no waiver flag, no test that weakens a natural-person rule. A previous attempt to add a synthetic second approver was rejected as a security weakening. A first organisation needs three different people by design.
- **Tests.** Never weaken, skip or delete a test to get green; fix the cause. Never present PGlite evidence as concurrency evidence, a PARTIAL requirement as accepted, or a design section as implemented.
- **Money and irreversible actions.** Ask the owner before anything that costs money (CI minutes, cloud resources, paid services) or cannot be undone (merging, deploying, deleting branches or data).

## Working with the owner

The owner is a non-engineer who decides product scope and approves merges. Use plain language without jargon, short direct answers, the uncomfortable facts first, and state your confidence explicitly ("high / medium / low confidence", and why). Confirm before merges, deployments or spending money. When something cannot be done, say so and offer the nearest safe alternative. Owner decisions that are still open are listed in `docs/HANDOVER.md`. The owner has also used Cursor's agent on this repository, so a branch may receive commits from another tool while you work on it: fetch again before you merge or push, and never push to someone else's branch.

## Set up, run and test

Prerequisites: Linux or macOS, Python 3.12, Node.js 22.12+ (24 in CI), Make; Java 21 for the live identity-provider checks; Linux x86_64 for the browser checks; a private PostgreSQL 16 or 17 cluster created with `initdb -E UTF8` for the native gate.

```
make setup            # virtualenv + npm ci + web build
make dev              # http://127.0.0.1:8000 with synthetic data; passwords in .local/dev/passwords.json; starts one worker
make lint             # ruff + ruff format --check + prettier --check
make unit             # pure tests, no database
IMPACT_PORT=8123 make test     # full suite on fresh in-memory PGlite; writes docs/evidence/application-tests.xml
make reference        # preserved design-reference assertions
make browser          # Chromium checks of the real UI (19 groups); one group: .venv/bin/python scripts/run.py tenant-browser
make idp              # live Keycloak suite (Java 21)
IMPACT_FIXTURE_DSN=postgresql://postgres:<pw>@127.0.0.1:<port>/impact_test_<x> IMPACT_UPGRADE_BASELINE=33 make native
                      # full suite on provisioned login roles + API restart + restore drill + populated upgrade from deployed schema 33
.venv/bin/python scripts/run.py test --pytest-path qualification/test_<area>.py   # one file (use a unique IMPACT_PORT)
make ledger           # regenerate docs/COMPLETION-LEDGER.{json,md} from scripts/build_completion_ledger.py
python scripts/build_contracts.py && python scripts/export_implemented_api.py    # after any contract change
python scripts/build_access_profile.py                                             # after any capability change
```

A focused run overwrites files in `docs/evidence/`; restore them before committing (`git checkout -- docs/evidence/ && git clean -f docs/evidence/`) unless you are publishing a clean full run. Port 8000 is every runner's default: set `IMPACT_PORT` when anything else runs. Full details, flags and recorded counts: CLAUDE.md §7 and `docs/QUALIFICATION.md`.

## Changing things (summary of CLAUDE.md §8)

- **Domain action:** add schemas, path and policy row in the feature's `*_contracts.py` `augment()` (register new modules in `scripts/build_contracts.py`, keeping `augment_reference` last); regenerate the contracts; register the action in `service.py` and implement it; give fixture actors the capability in `scripts/bootstrap.py`; regenerate the onboarding profile; add the capability prefix to `areaCapabilities` in `apps/web/src/main.tsx` if a screen uses it; tests for the positive case, another tenant (404), revoked (401/404), wrong role (403), self-approval (`INDEPENDENCE_REQUIRED`), stale revision (409), exact retry and changed payload under the same operation ID.
- **Tenant-admin command:** a tuple in `COMMANDS` of `administration_contracts.py` / `workspace_contracts.py` (OWNER/TENANT_ADMIN and 300 s assurance are generated) and a dispatch branch.
- **Control-plane operation:** closed schemas and paths in a `*_contracts.py` wired into `tenant_contracts.openapi()`, a class on `TenantLifecycle`, explicit routes in `main.py`, tables granted to `impact_platform` only, platform event and receipt in one transaction.
- **Migration:** next is `infrastructure/migrations/0041_<topic>.sql` — additive, `BEGIN;`/`SET LOCAL ROLE impact_owner;`/`COMMIT;`, `tenant_id` in every key, forced RLS with `tenant_fence`, narrowest grants, never edit an applied migration; append the SQL and SHA-256 to `docs/current/CURRENT-DATA-DICTIONARY.md`; add real-role RLS negative tests.
- **Versions:** only in `VERSION.json` plus `apps/web/package.json` and its lock (the schema is the migration count); regenerate the contracts after a bump.
- **Documents together:** a release note per increment (`docs/RELEASE-0.N.md` or `RELEASE-0.N-<topic>.md`, with Delivered, Contract and persistence, Limits, Reproduction and, on a parallel slice, **Integration notes**), then the shared documents listed in CLAUDE.md §8 step 6; promote a requirement in the ledger only with named passing tests.

## Repository map

| Path | Contents |
|---|---|
| `apps/api/impact_api/` | FastAPI service: `main.py` routes, `auth.py` identity, `store.py` tenant context, RLS, authorisation, revisions, audit and outbox, `service.py` domain dispatcher, one module per area (`planning.py`, `forms.py`, `imports.py`, `evidence.py`, `reporting.py`, `exports.py`, `dashboards.py`, `privacy.py`, `retention_policies.py`, `security_events.py`, `status.py`, …), the control plane (`tenant_lifecycle.py`, `operators.py`, …), `worker.py` (separate worker process) and `*_contracts.py` contract generators |
| `apps/web/src/` | React client: `main.tsx` (shell, navigation, `areaCapabilities` gate) and one file per area |
| `infrastructure/migrations/` | 40 checksum-ledgered SQL migrations (never edit an applied one) |
| `packages/contracts/` | Generated contracts: `openapi-implemented.json` (the implemented domain API), `openapi-platform.json` (control plane), `access-policy.json`; `openapi.json` is the broad design contract |
| `qualification/` | The test suite (PGlite and native PostgreSQL), unit tests, performance harness |
| `scripts/` | Runner (`run.py`), migration runner, login provisioning, contract and profile generators, restore drill, upgrade check, ledger builder, secret rotation, Keycloak runner, pooler |
| `tools/browser/` | Chromium checks of the real UI and the training-video generator; `tools/dev-db/` the PGlite server; `tools/idp/` the Keycloak qualification realm |
| `deploy/` | Staging server: `update.sh`, Docker Compose, backups, restore drill, alert checks, owner console scripts |
| `docs/` | Release notes, implementation and qualification records, roadmap, handover; `docs/current/` the current specifications, guides, data dictionary and registers; `docs/evidence/` recorded test evidence |
| `specification/` | The preserved original engineering package and synthetic fixtures (never edit) |

## Commits, branches and pull requests

- Branches: `release/<version>-<topic>`, `qa/<yyyy-mm>-<topic>`, `ux/<version>-<topic>`, `docs/<yyyy-mm>-<topic>`, `integration/<build>`. Branch from the current `main`.
- Integrations use real merge commits (`git merge --no-ff`) so the component pull requests show as merged; one integration pull request per build.
- Every increment has a release note with an **Integration notes** section (proposed requirement movements with exact test names, lines for the shared documents, files touched, risks).
- Parallel builders follow `docs/handover/PARALLEL-WORK.md`: no version bumps, no shared-document edits, migration placeholder supplied by the integrator (next registered0041), focused tests only, one push plus at most two fix pushes, never merge.
- Commit messages: a short imperative summary line, a body explaining why, and any attribution lines your tooling requires.

## Where the current state lives

`docs/HANDOVER.md` (state at handover and next steps), `docs/RELEASE-0.27.md` (latest build), `docs/QUALIFICATION.md` (test counts), `docs/COMPLETION-LEDGER.md` (requirement status), `docs/NEXT-DELIVERY.md` and `docs/DELIVERY-PLAN.md` (roadmap), `docs/handover/BACKLOG.md` (ready-to-run slices). Update `docs/HANDOVER.md` when you hand over again.
