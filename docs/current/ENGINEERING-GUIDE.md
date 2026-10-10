# Impact Platform engineering guide

Owner: Nakul Jain · Written 9 October 2026 · Update trigger: any change to a make target, a CI workflow, the folder layout, a naming rule or a "do and don't" below.

This is the practical manual for anyone, human or AI, who takes over this repository without a chat history. It holds few facts that change (the build, counts, hosting state): those live in the status block at the top of [../HANDOVER.md](../HANDOVER.md) and are only linked here. It is written for a newcomer. For depth on the domain, the architecture and the database security model, open [ENGINEERING-BRIEF.md](ENGINEERING-BRIEF.md) at the section named in each link below.

How to read it: sections 1 and 2 get you running in an hour. Sections 3 to 6 are reference. Sections 7 and 8 are the commands and recipes you will use every week. Section 9 is the list of things not to do. Section 10 is how the repository stays clean.

Confidence tags: **verified** means the author ran the command or read the code on 9 October 2026; **unverified** means it comes from a document and was not checked.

## 0. The Products standard (identical in every Products repository)

This section is the same in all six repositories (saha-health, saha-education, saha-agriculture, aplyd-academy, impact-platform, sheet-happens-officer). The rest of this guide is specific to this repository. If the two ever disagree, this repository's own safety rules in AGENTS.md win.

### 0.1 Principles

1. **A human must be able to take over.** Anyone who can read English and knows the language of the repository should be productive on day one using only README.md, AGENTS.md, HANDOVER.md and this guide. If a fact is only in someone's head or a chat, it is missing; write it down.
2. **One place per fact.** Version, hosting state, test counts and open items are stated once, in the status block at the top of HANDOVER.md. Everything else links to it. Never copy a number into a second document.
3. **Small, reviewable, reversible.** One purpose per branch and pull request. Prefer deleting code to adding it. Nothing is merged without a green `verify` check and the owner's approval.
4. **Truth over polish.** Say what was and was not run. Never write "done", "passing" or "verified" for something that was not executed. Synthetic data is never described as real; a demo is never described as production.
5. **Server is the authority.** Permission, ownership and validation are decided on the server. The client only displays.
6. **Never destroy history.** Applied migrations, evidence, receipts and audit records are append-only. Corrections add a new record; they do not rewrite the old one.

### 0.2 Root of the repository

Exactly these markdown files may sit at the root: `README.md`, `AGENTS.md`, `CLAUDE.md`, `HANDOVER.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `LICENSE` (some repositories omit one or two). Every other document lives under `docs/`. `CLAUDE.md` is a short pointer to AGENTS.md and HANDOVER.md. `AGENTS.md` holds the rules, commands and safety limits. `HANDOVER.md` starts with the status block.

```
docs/
  DOCUMENTATION-INDEX.md   generated; lists every document; never edit by hand
  current/                 live documents (this guide, architecture, contracts)
  history/                 superseded documents and old receipts; read-only
  governance/              policy bundle where the repository has one
```

A document that replaces another moves the old one to `docs/history/` in the same pull request. A new document is added to the index in the same pull request (`pnpm run docs:index`; CI runs `docs:index:check`).

### 0.3 Naming

| Thing | Rule | Example |
|---|---|---|
| Source files and folders | `kebab-case`, lower case, no spaces, no version suffix | `reading-review.ts`, `lib/education/` |
| React components | file `kebab-case.tsx`, component `PascalCase` | `reading-review-panel.tsx` exports `ReadingReviewPanel` |
| Functions and variables | `camelCase`, verbs for functions, nouns for values | `loadStudent`, `studentCount` |
| Types, classes | `PascalCase` | `StudentRecord` |
| Constants | `UPPER_SNAKE_CASE` only for true constants | `MAX_UPLOAD_BYTES` |
| Python | `snake_case` modules and functions, `PascalCase` classes | `audit_export.py` |
| Database tables and columns | `snake_case`, plural table names, no abbreviations | `reading_checks.student_id` |
| Migrations | next number, then topic, never edited once applied | `0041_add_reading_review.sql` |
| API routes | nouns, plural, kebab-case; HTTP verb carries the action | `POST /api/reading-checks` |
| Environment variables | `UPPER_SNAKE_CASE`, one prefix per app; listed in README | `EDUCATION_DEMO_LOGIN` |
| Branches | `<type>/<topic>-<yyyy-mm-dd>` with type one of `feat fix docs chore refactor deploy release qa ops handover` | `fix/reading-nonce-2026-10-09` |
| Commits | `type: imperative sentence` (72 characters or fewer), body explains why | `fix: reject a replayed nonce` |
| Pull requests | title like a commit; body states what changed, what was run, what was not run | |
| Documents | `UPPER-CASE.md` for governance and handover files; `Title-Case.md` or `kebab-case.md` as the repository already does, never both in one folder | |
| Dates | ISO `2026-10-09` in file names; "9 October 2026" in prose; never `October2026` | |

Never put a version, date or "final" in a source file name (`index-v2.ts`, `new-api-final.ts`). Version control is the version.

### 0.4 Writing code

1. **Format is not a discussion.** Prettier (config in `.prettierrc.json`, print width 110, single quotes, trailing commas, semicolons) formats everything; `pnpm run format` fixes it, `pnpm run format:check` is a CI gate. Python uses ruff format. Never hand-align, never reformat a file you are not otherwise changing.
2. **Lines under 110 characters; functions under about 40 lines; files under about 400 lines.** If a file grows past that, split it by responsibility, not alphabetically.
3. **Types are real.** TypeScript is `strict`. No `any`; use `unknown` and narrow, or a named type. No `@ts-ignore`; if unavoidable use `@ts-expect-error` with a reason. Python functions that cross a module boundary carry annotations.
4. **One definition per helper.** Before writing `json()`, `sameOrigin()`, `sha256()`, `now()`, `uniqueFailure()` or similar, search the repository (`rg "function name"`); if it exists, import it. A second copy is a defect. Shared helpers live in one place named in section 3 of this guide.
5. **Imports go one way.** Pages and routes import from `lib/`; `lib/` never imports from `app/`. No import cycles. Use the `@/` alias, not `../../..`.
6. **Names say what a thing is.** No `data`, `info`, `tmp`, `util`, `helper`, `manager`, `handle2`. A boolean reads as a question: `isExpired`, `hasConsent`.
7. **Comments explain why, never what.** No commented-out code; delete it (git remembers). A `TODO` carries an owner and a date or does not exist.
8. **Errors are handled or raised, never swallowed.** No empty `catch`. A user-visible error is plain language and says what to do next. A server error never leaks stack traces, SQL or secrets.
9. **Validate at the boundary.** Every request body, query and header is parsed by a schema before use; unknown fields are rejected.
10. **Dependencies are a liability.** Add one only with a reason in the pull request; pin exact versions; prefer the standard library.
11. **Secrets, real personal data, databases, build output and logs never enter git.** Use synthetic fixtures. `.env*` files stay local.
12. **Tests prove behaviour.** A bug fix lands with the test that fails without it. A test names the behaviour (`rejects a replayed nonce`), not the function. Do not edit a test to make it pass; fix the code or explain why the test was wrong.
13. **Lint is a ratchet.** The committed baseline (`.lint-baseline.json`) may only go down. A pull request that raises it is red. Fix warnings in files you touch.

### 0.5 Every change, start to finish

1. Start from current `origin/main`: `git fetch origin main && git switch -c <type>/<topic>-<date> origin/main`.
2. Read the files you will touch and the tests beside them. Search for an existing helper before writing one.
3. Make the smallest change that does the job. Update the documents it affects in the same pull request.
4. Run the gate (section 6 of this guide). Run it again after the last edit.
5. Commit with a clear subject. Push. Open a **draft** pull request that states what was changed, what was run (with results) and what was not run.
6. Wait for CI. Fix every red check, or say plainly why it is unrelated.
7. A person (or a reviewing agent with the full diff) approves and merges. Agents do not merge on their own authority.
8. After a merge to `main`, check the status block in HANDOVER.md still tells the truth; update it if not.

### 0.6 Do and don't (all repositories)

Do:
- Search before writing. Reuse before adding.
- Keep a change to one purpose; split unrelated fixes.
- State what you did not test.
- Use synthetic data; mark demo behaviour as demo.
- Put new documents under `docs/` and in the index.
- Update HANDOVER.md's status block when hosting, version, gates or open items change.

Don't:
- Don't force-push `main`; don't push to `main` at all in repositories that deploy from it.
- Don't merge without a green `verify` and the owner's approval; don't deploy, change hosting, send messages to real people or spend money without being told to.
- Don't add a root-level document, a second status statement, or a count copied from elsewhere.
- Don't commit screenshots, logs, audio, zips, dumps, generated mirrors or test output. Evidence is kept as manifests and hashes; the files live outside git.
- Don't edit an applied migration, a retained evidence file, a receipt or anything under `docs/history/` (except to move a document there).
- Don't weaken a check, raise the lint baseline, add `eslint-disable` or `any` to get a green build.
- Don't retry an uncertain mutation (a payment, a message, a deploy) blindly; find out what happened first.
- Don't claim "production", "accepted", "verified" or "passing" for anything that was not run and observed.

### 0.7 Handing over (when your session ends)

Before you stop: everything is committed and pushed on a branch with a draft pull request; the status block in HANDOVER.md is current; "Open items" lists what is unfinished and why, with the exact next command or file; no uncommitted work remains in the checkout. The next person, human or agent, should be able to continue from HANDOVER.md alone.

### 0.8 Exceptions in this repository

Section 0 is written TypeScript-first. This repository is Python and Makefile first, with a React client in `apps/web`. Where the two differ, this table wins. Everything not listed here applies as written.

| Section 0 says | Here |
|---|---|
| "Section 3 of this guide" names the shared helpers; "section 6" is the gate | Section 3 is the map (helpers are in 3.3). The gate is section 7. |
| A green `verify` check | The small check is called **`checks`** (workflow `checks.yml`). The paid workflow `qualification.yml` has four more jobs. A merge needs `checks` and all four of those green, and the owner's say-so (section 7). |
| `pnpm run ...` scripts | `make` targets (`make setup`, `make lint`, `make unit`, `make test`). The web client uses **npm** (`apps/web/package-lock.json`). There is no pnpm. |
| Prettier at print width 110, single quotes, `.prettierrc.json` | Python is formatted by **`ruff format`** with line length **110** (`pyproject.toml`). `ruff check` selects only `E4, E7, E9, F`. The web client and `tools/browser/*.mjs` use **Prettier with its defaults** (no config file: 80 columns, double quotes). `make lint` runs all three. |
| `.lint-baseline.json` ratchet | There is no baseline file. `make lint` must pass with zero findings. Do not add `# noqa` or Prettier ignores to get green. |
| `kebab-case` source files | **Python modules, scripts and tests are `snake_case`** (`audit_export.py`, `test_audit_export.py`). **React components are `PascalCase.tsx`** (`Rounds.tsx`); non-component web modules are lower case (`operations.ts`, `a11y.ts`). Browser checks are `kebab-case.mjs` (`tools/browser/recovery-check.mjs`). |
| Plural table names | **Singular `snake_case` table names**: `object_revision`, `tenant_principal`, `import_unit_register`. Typed projections end in `_current` (`framework_current`). All live in the `impact` schema. Keep to this; do not rename. |
| API routes: the HTTP verb carries the action | Routes are plural kebab-case nouns under `/v1/tenants/{tenant_id}/`. A state change is `POST .../{object_id}/actions/<verb>` (for example `.../indicator-instances/{object_id}/actions/calculate`). Creating and patching use `POST` and `PATCH` on the noun. |
| Env vars listed in the README | `IMPACT_*` variables are listed in [../governance/env.example](../governance/env.example) (names only). The README does not list them. |
| Branch `<type>/<topic>-<date>` with the listed types | Recent branches follow it (`docs/claude-md-cut-2026-10-08`, `refactor/shared-helpers-2026-10-08`). [AGENTS.md](../../AGENTS.md) also lists older shapes (`release/<version>-<topic>`, `qa/<yyyy-mm>-<topic>`, `ux/<version>-<topic>`, `docs/<yyyy-mm>-<topic>`, `integration/<build>`). Use the section 0.3 shape for new branches; do not rename old ones. |
| `@/` import alias | None exists. Python imports are relative inside the package (`from .domain import DomainError`). Web files import with `./Name`. |
| Functions under about 40 lines, files under about 400 | Many existing files are far larger (`worker.py` 1,501 lines, `planning.py` 1,344, `main.py` 1,232). The limit applies to new code. Do not split an old file inside an unrelated change (section 10). |
| TypeScript has no `any` | `strict` is on, but `any` appears in existing code (for example `Record<string, any>`). New code uses a named type or `unknown`. |
| Python functions that cross a module boundary carry annotations | The code base is almost unannotated (about 30 return annotations in 105 modules). New public functions may carry them; do not add annotations to old code as a drive-by. |
| Validate with a schema at the boundary | Done with JSON Schema built from the generated contracts (`impact_api/contracts.py`, `jsonschema`). Every write schema is closed (no unknown fields). There is no pydantic model layer. |
| `HANDOVER.md` at the root | It is **`docs/HANDOVER.md`**. The root has `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md` (a pointer to `docs/current/CHANGELOG.md`) and `LICENSE` (a placeholder). |
| `docs/DOCUMENTATION-INDEX.md` is generated; `docs:index` and `docs:index:check` | **There is no generator and no index check.** Two index files exist and both are edited by hand: [../DOCUMENTATION-INDEX.md](../DOCUMENTATION-INDEX.md) (short entry page) and [DOCUMENTATION-INDEX.md](DOCUMENTATION-INDEX.md) (the real index, with tables). Add a new document to the second one in the same pull request. |
| The docs gate is `docs:check` | There is **no documentation check in CI**. The nearest gate is `qualification/test_version_unit.py` (inside `make unit`): it checks the version source, migration numbering and that the generated contracts match. Broken Markdown links are not checked by anything in the repository; check them yourself (section 7.4). |
| `docs/history/` for superseded documents | `docs/history/` exists but holds only `v1.0/` (the original editions). Superseded release notes and old checkpoints were **not** moved there; they sit in `docs/` with their original dates (section 10). Move a document you supersede to `docs/history/` as the standard says, and leave a link behind. |
| `docs/current/` holds live documents | True, but it also holds the edition 1.1 reading copies of the ten specifications (`Impact-Management-*-v1.1.md`, with `.docx` twins) and generated registers (`CURRENT-API-INVENTORY.md`, `TRACEABILITY.csv`). Treat the specifications as the target design, not the implementation (section 3.7). |
| Evidence is kept as manifests; files live outside git | This repository **tracks 1,829 files (about 100 MB) in `docs/evidence/`**. That is an existing deviation (section 10). Do not add more than the test runners write. |
| Dates in file names are ISO | Release notes are `RELEASE-0.N-<topic>.md` (build number, not a date); QA records are `QA-<topic>-2026-10.md`; handover files carry an ISO date (`CLAUDE-HANDOFF-2026-10-06.md`). |
| Commit subject `type: sentence` | Recent commits follow it (`docs:`, `refactor:`, `chore:`). Older ones do not (`Build 0.36.0: ...`, `CI: ...`). Use `type: imperative sentence`. |
| Node version | `engines` in `apps/web/package.json` is `>=22.12 <25`. `checks.yml` uses Node 22; `qualification.yml` uses Node 24. [../../README.md](../../README.md) says Node 24, AGENTS.md says 22.12+. Either works; Node 22.22 was used to write this guide. |
| Python version | `pyproject.toml` targets 3.12 and CI uses 3.12. The author ran everything below on Python 3.13.16 without trouble, but only 3.12 is tested. |

---

## 1. What this repository is

- A multi-tenant platform for monitoring, evaluation, learning and impact reporting. An organisation plans programmes, collects data, has every record approved by a *different person*, calculates results with fixed rules, locks reporting periods, and publishes frozen reports to named recipients.
- It also carries a "nonprofit AI enablement" area (planning tools, content, advice). It uses the same rules; it is not a separate application.
- Stack: Python 3.12 API (FastAPI) in `apps/api/impact_api`; PostgreSQL 16/17 with forced row-level security (migrations in `infrastructure/migrations`); React + Vite client in `apps/web`; a background worker and an import "executor" process; Keycloak for sign-in; Docker Compose on one staging server.
- It is a **development build**. No requirement is accepted. Data is synthetic. Never write "production-ready" or "accepted" about anything here.
- `main` **deploys itself** to the staging server every 3 minutes. That one fact shapes most rules below.
- The owner (Nakul Jain) is not an engineer. He decides scope and approves merges. Use plain words, put bad news first, and say how confident you are.
- The domain vocabulary (programme, indicator, observation, period, snapshot, revision, capability) is explained in [ENGINEERING-BRIEF.md](ENGINEERING-BRIEF.md) section 3. The glossary in section 11 below is a short version.
- Current build number, API versions, schema, the state of `main`, CI and staging: the status block at the top of [../HANDOVER.md](../HANDOVER.md). Do not copy those numbers anywhere else.
- Rules that must never be broken: [AGENTS.md](../../AGENTS.md) ("Rules that must never be broken", copied from brief section 4). Read them once, fully, before any change.

---

## 2. First hour for a newcomer

Everything here was run on 9 October 2026 on a 2-CPU Linux machine. Durations are from that run and will vary.

### 2.1 Prerequisites (2 minutes)

```
python3 --version   # 3.12 is the tested version
node --version      # 22.12 or newer
make --version
git --version
```

Not needed for the first hour: Java 21 (live Keycloak checks), PostgreSQL 16/17 (native gate), Linux x86_64 Chromium (browser checks), Docker (the deployment path; CI only).

### 2.2 Get the code and read four files (15 minutes)

```
git clone https://github.com/nakul175/impact-platform.git
cd impact-platform
git switch -c docs/my-first-change-2026-10-09 origin/main   # always branch; never work on main
```

Read, in this order: [AGENTS.md](../../AGENTS.md), the status block of [../HANDOVER.md](../HANDOVER.md), this guide's sections 3 and 9, and the "fragile spots" in [ENGINEERING-BRIEF.md](ENGINEERING-BRIEF.md) section 11 for the area you will touch.

### 2.3 Install (about 1 minute 15 seconds, needs internet)

```
make setup
```

It creates `.venv`, installs `requirements.lock`, runs `npm ci` for `apps/web` and `tools/dev-db`, and builds the web client. Expected end of output:

```
dist/assets/app-<hash>.js   483.66 kB │ gzip: 117.38 kB
✓ built in 554ms
```

(The sizes drift.) Nothing is installed outside the repository folder.

### 2.4 Check the toolchain (about 1.5 minutes)

```
make lint          # about 27 s. Ends with: All matched files use Prettier code style!
make unit          # about 1 minute. Ends with: N passed, M skipped  (no failures)
cd apps/web && npx tsc --noEmit && cd ..    # about 6 s. Prints nothing when clean
```

Since 9 October 2026 `make unit` no longer rewrites `docs/evidence/golden-reconciliation.json` (`qualification/test_golden.py` writes it only when the live API path ran). Other runners still write tracked evidence files, so run `git status` after any test run and restore them:

```
git checkout -- docs/evidence/ && git clean -f docs/evidence/
```

This is the same trap as a focused test run (section 7.3). Verified.

### 2.5 Start the application (ready in under 45 seconds; not timed more finely)

```
IMPACT_PORT=8123 make dev
```

Port 8000 is the default for every runner. Set `IMPACT_PORT` to anything free so you never collide with another run. Expected output, in order:

```
Applied 0001_roles.sql
...
Applied 0040_ai_plan_portability.sql
Loaded disposable acceptance fixture
Development configuration ready. Credentials: <repo>/.local/dev/passwords.json
Ready at http://127.0.0.1:8123
```

Open the address. Sign in with a fixture user from `.local/dev/passwords.json` (it holds `admin`, `author`, `reviewer`, `owner`, `partner`, `privacy`, `operator`, `enumerator`, `other_tenant`, `invitee` and `revoked`). The file is generated and git-ignored. The walkthrough "Try the complete workflow" in [../../README.md](../../README.md) shows what to click. `make dev` also starts one outbox worker (log `.local/dev/worker.log`). Stop it with Ctrl-C. Development data is kept in `.local/dev/database` (git-ignored). `scripts/run.py dev --ephemeral` uses throwaway memory storage instead.

### 2.6 Run one focused test file (about 1 minute)

```
IMPACT_PORT=8124 .venv/bin/python scripts/run.py test --pytest-path qualification/test_changes.py
```

It starts its own database and API on a random database port, runs the file, and prints `N passed in Ns` (16 passed in 25 s for this file). Then **restore the evidence it overwrote** (`docs/evidence/application-tests.xml`):

```
git checkout -- docs/evidence/ && git clean -f docs/evidence/
```

### 2.7 What the first hour does not cover

`make test` (the full suite, long), `make reference`, `make browser`, `make idp`, `make native`, `make perf`. They need more tools or time and are explained in section 7. Do not run the full suite for a small change; CI does that.

### 2.8 Make a trivial docs change to prove the loop

Edit a typo in a document under `docs/`, run the link check (section 7.4), `git commit`, `git push -u origin <branch>`, open a **draft** pull request. A docs-only pull request starts only the small `checks` job (section 7.2), so it costs nothing. Do not merge it yourself.

---

## 3. Map of the repository

### 3.1 Top level

| Path | What belongs here | What never goes here |
|---|---|---|
| `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `LICENSE` | The seven root documents. `CLAUDE.md` is a short pointer; `AGENTS.md` holds the rules; `CHANGELOG.md` points to `docs/current/CHANGELOG.md`. | A new root document. Status numbers. A second copy of the rules. |
| `Makefile` | Every command people run. | Logic longer than a few lines (put it in `scripts/`). |
| `VERSION.json` | The one source of the build, domain API and platform API versions. | Anything else. The schema version is *not* here: it is the count of migration files. |
| `pyproject.toml` | pytest settings (`pythonpath`, `testpaths`) and ruff (line length 110, target py312). | Dependencies. |
| `requirements.txt`, `requirements.lock` | Direct pins, and the full pinned set that `make setup` installs. | Unpinned versions. |
| `SHA256SUMS.json` | Not tracked since 9 October 2026 (listed in `.gitignore`). `make package` writes it next to the source archive. | Committing it. |
| `.editorconfig`, `.gitignore`, `.dockerignore` | Editor and ignore rules. `.gitignore` covers `.venv/`, `.local/`, `node_modules/`, `dist/`, `*.pem`, `*.key`, `*.log`, `.env`. | |
| `.github/workflows/` | `checks.yml` (cheap, always runs) and `qualification.yml` (paid, four jobs). `.github/PULL_REQUEST_TEMPLATE.md` is the PR form. | A third workflow without the owner's approval (it spends money). |
| `apps/` | `api/impact_api` (the service) and `web` (the client). | |
| `infrastructure/migrations/` | Numbered SQL migrations only. | Drafts, notes, anything not `NNNN_topic.sql`. |
| `packages/contracts/` | Generated OpenAPI and policy files (section 3.5). | Hand edits. |
| `qualification/` | The pytest suite and its helpers. | Application code. |
| `scripts/` | Runners and generators (section 3.6). | Library code the API imports. |
| `tools/` | `browser/` (Chromium checks and the training-video generator), `dev-db/` (the PGlite database server), `idp/` (the Keycloak test realm), `development-tracker/`, `documentation/`, `reuse/`. | Production code. |
| `deploy/` | The staging server package: `update.sh`, `compose.yaml`, Caddy, Keycloak realm, backups, restore drill, alert checks, owner console scripts. See [../../deploy/README.md](../../deploy/README.md). | Secrets, host-specific files. |
| `specification/` | The preserved original engineering package and the synthetic fixture (`specification/fixtures`). | Edits to the preserved documents. Fixture changes go through `scripts/redate_fixture.py` only. |
| `third_party/` | Vendored reference code (`mercycorps-toladata`) with its licence. | Our code. |
| `docs/` | All other documents (section 3.7). | |

### 3.2 The API package, by responsibility

`apps/api/impact_api` is one flat package of about 105 modules. There are no sub-packages; a name prefix tells you the area. The ten that matter most:

| Responsibility | Modules |
|---|---|
| Web entry, routes, error envelope | `main.py` (FastAPI app factory, explicit routes, the error JSON), `config.py` (settings from `IMPACT_*` variables), `version.py` (reads `VERSION.json` and counts migrations) |
| Identity and sessions | `auth.py` (tokens, cookie sessions, fresh-authentication time), `identity_profile.py`, `keyring.py` (rotatable keys), `platform_security.py` |
| Database access, tenant context, authorisation, revisions | `store.py` (`Store.transaction`, `authorize`, `write`, `Context`, audit, outbox), `domain.py` (`DomainError`, decimal and calculation rules) |
| Command dispatcher | `service.py` (`READ_ROUTES`, `WRITE_ROUTES`, `ACTIONS`, `Service.command`) |
| Domain areas (one per feature) | `planning.py`, `measurement.py`, `forms.py`, `imports.py`, `evidence.py`, `reporting.py`, `exports.py`, `export_render.py`, `dashboards.py`, `period_governance.py`, `changes.py`, `work.py`, `logframe.py`, `reference_data.py`, `privacy.py`, `retention.py`, `retention_policies.py`, `security_events.py`, `audit_export.py` |
| Administration and onboarding | `administration.py`, `workspace_administration.py`, `account.py`, `access_bootstrap.py`, `access_upgrade.py`, `authority_renewal.py`, `recovery_contacts.py` |
| Control plane (platform operators, tenants) | `tenant_lifecycle.py`, `operators.py`, `provider_accounts.py`, `provider_admin.py` |
| Background processes | `worker.py` (outbox delivery, export jobs, retention sweeps; its own clock logic), `application_executor.py` (queued import commits), `delivery.py`, `delivery_operations.py`, `mail_rate.py`, `worker_status.py` |
| Operations and status | `status.py`, `ops_metrics.py`, `object_store.py` |
| Nonprofit AI area | `ai_*.py` (catalogue, learning content, adoption plans, procurement costs, exports, advisory provider), `human_advice.py`, `content_safety.py` |
| Contract generators | `*_contracts.py`, one per area. Each has an `augment(spec, policy)` that adds that area's schemas, paths and policy rows (section 5.2). |

Rules of thumb: a feature's code is `<area>.py` and its contract is `<area>_contracts.py`. Shared plumbing is only in `store.py`, `domain.py`, `service.py`, `auth.py`, `config.py`, `clock.py`.

### 3.3 Shared helpers (search here before writing one)

| Helper | Where | Notes |
|---|---|---|
| `now()` | `impact_api/clock.py` | Timezone-aware UTC. Twelve modules do `from .clock import now` and keep the name `now`, so a test can replace `module.now` with `monkeypatch.setattr(module, "now", ...)`. Do not rename it and do not call `datetime.now(...)` in those modules. Other modules (`store.py`, `service.py`, `work.py`) still call `datetime.now(timezone.utc)` directly; move them one at a time, only with a reason. `worker.py` uses the database clock and does not use `clock.py`. |
| `DomainError(code, status, message, reason, fields)` and `unavailable()` | `domain.py` | The one way to refuse a request (section 5.7). |
| `decimal_value`, `stored`, `display`, `ratio` | `domain.py` | Decimal parsing, storage form and half-up display (section 5.5). |
| `authorize`, `write`, `Store.transaction`, `denied`, `hash_data` | `store.py` | Permission check, revision write, tenant-scoped transaction. |
| `validate(schema_name, data)` | `contracts.py` | JSON Schema validation against the generated contracts. |
| `closed`, `text_field`, `UUID`, `DATE` | `measurement_contracts.py` | Schema building blocks used by every `*_contracts.py`. |

Known duplicates that remain (do not add to them; consolidate only in a dedicated change): small `denied(reason)` / `deny(reason)` / `timestamp(value)` / `unavailable()` definitions appear in `access_bootstrap.py`, `operators.py`, `authority_renewal.py`, `recovery_contacts.py`, `human_advice.py`, `administration.py`, `workspace_administration.py`, `ai_advisory_provider.py`. They differ slightly in reason codes, so they are not interchangeable without reading each.

### 3.4 The web client (`apps/web/src`)

- `main.tsx` is the shell: the navigation list, the route switch, the `titles` map and the `areaCapabilities` gate that decides which screens a person sees.
- One file per area, `PascalCase.tsx` (`Planning.tsx`, `Forms.tsx`, `Rounds.tsx`, `ReportExports.tsx`, `TenantLifecycle.tsx`, ...). The AI area is `AI*.tsx` plus `*Model.ts` / `*Adapter.ts` files that hold logic testable without a browser.
- Shared pieces: `operations.ts` (pending-operation tracking), `a11y.ts`, `styles.css` plus `ai-*.css`. New colours use the `:root` tokens; new dialogs use `Dialog` (the accessibility check fails otherwise; brief section 11).
- Build: `npm run build --prefix apps/web` (`tsc --noEmit && vite build`). `apps/web/dist/` is ignored.
- The client only displays. It never decides permission (section 0.1, rule 5).

### 3.5 Contracts (`packages/contracts`) — generated, never hand-edited

| File | What it is |
|---|---|
| `openapi-implemented.json` | The domain API as implemented. Source of truth for what exists. |
| `openapi-platform.json` | The control-plane API. |
| `access-policy.json` | One policy row per operation: capability, role templates, purpose, fresh-assurance seconds, audit. |
| `event.schema.json` | Event schema. |
| `openapi.json` | The broad **design** contract. Never generate clients from it. |
| `openapi-baseline.json` | The earlier baseline. Leave alone. |

They are written by `python scripts/build_contracts.py && python scripts/export_implemented_api.py` (section 8.1). `qualification/test_version_unit.py` fails when they are stale.

### 3.6 Scripts

| Script | Use |
|---|---|
| `run.py` | The runner behind `make dev`, `make test` and every browser group: starts the database, migrates, loads the fixture, starts the API, runs the checks. Modes: `dev`, `check`, `test`, and the `*-browser` modes. Flags: `--native`, `--pytest-path`, `--idp keycloak`, `--pooler pgbouncer`, `--skip-upgrade-check`, `--skip-restart-check`, `--skip-restore-drill`, `--no-worker`. |
| `migrate.py` | The only migration runner. Verifies checksums, refuses a numbering gap. |
| `build_contracts.py`, `export_implemented_api.py`, `build_access_profile.py` | Generators (sections 3.5, 8.1, 8.3). |
| `bootstrap*.py`, `fixture_support.py`, `redate_fixture.py` | Fixture and first-run setup; `redate_fixture.py` moves the fixture expiry (section 7.6). |
| `provision_logins.py`, `idp.py`, `pooler.py` | Native-PostgreSQL logins, the pinned Keycloak, PgBouncer. |
| `restore_drill.py`, `native_upgrade_check.py` | Backup-and-restore and populated-upgrade checks (part of `make native`). |
| `rotate_secrets.py`, `staging_first_login.py`, `smoke.py`, `webhook_receiver.py` | Operations helpers. |
| `build_completion_ledger.py` | `make ledger`: regenerates `docs/COMPLETION-LEDGER.{json,md}`. |
| `package_source.py` | `make package`. |
| `perf.py`, `qualification/perf_harness.py` | `make perf`. |

### 3.7 Tests (`qualification/`)

- Runner: pytest. Config in `pyproject.toml`. `conftest.py` holds the `live` fixture (a signed-in HTTP client plus a database handle).
- File names: `test_<area>.py`. Suffixes tell you what it needs:
  - `test_<area>_unit.py` or a pure module test: no database. These are the files listed in `make unit`.
  - `test_<area>.py`: needs the live API on PGlite; skipped unless run through `scripts/run.py test`.
  - `test_<area>_live.py`: live API plus data it builds.
  - `test_native_*.py`: needs a real PostgreSQL (`make native`); skipped on PGlite.
  - `test_live_idp.py`: needs Keycloak (`make idp`).
  - `test_ai_plan_exports_upgrade.py`, `test_access_upgrade.py`: upgrade behaviour.
- Test functions have long snake_case names that state the behaviour: `test_correction_author_cannot_approve_and_rejection_preserves_source`.
- Helpers: `from test_live_application import cmd, expect`, and area helpers (`setup`, `create`, `action`, `submit`, `approve`, `observation`, `result` in `test_measurement.py`). Other directories: `golden/` (the golden corpus), `drafts/` (see section 10), `perf_*.py`, `process_environment.py`, `smtp_sink.py`.
- **A new pure unit file must be added to the `unit` target in the `Makefile`.** `make unit` lists files by name, so an unlisted file never runs in `checks.yml` (verified; the integrator checklist in [../handover/PARALLEL-WORK.md](../handover/PARALLEL-WORK.md) says the same).
- Browser checks live in `tools/browser/<area>-check.mjs`; a mode in `scripts/run.py` (`BROWSER_MODES`) and a line in the Makefile `browser` target register them.

### 3.8 Migrations (`infrastructure/migrations`)

- File name: `NNNN_snake_case_topic.sql`, four digits, regex `^\d{4}_[a-z0-9_]+\.sql$`, contiguous from 0001 (enforced by `test_version_unit.py` and `scripts/migrate.py`). The schema version is the number of files.
- **0001 to 0040 are frozen.** Never change a byte. The next file is `0041_<topic>.sql`.
- Shape: exactly one `BEGIN;`, then `SET LOCAL ROLE impact_owner;`, then the DDL, then exactly one `COMMIT;` (the runner strips the outer pair). Create any new role *before* `SET LOCAL ROLE`.
- Additive only. No destructive down migration exists.
- Every tenant table: `tenant_id` in the primary key and every foreign key, `ENABLE` and `FORCE ROW LEVEL SECURITY`, the `tenant_fence` policy, the narrowest grants (section 5.4).
- Each new migration's SQL and SHA-256 are appended to [CURRENT-DATA-DICTIONARY.md](CURRENT-DATA-DICTIONARY.md) in the same change; the upgrade check and restore drill derive the expected count from the files and fail if the register differs (brief section 8).

### 3.9 Documents (`docs/`)

| Place | Holds |
|---|---|
| `docs/HANDOVER.md` | The status block (the one place for build, APIs, schema, `main`, CI, staging) and the 3 October 2026 handover body, kept as written. |
| `docs/IMPLEMENTATION.md`, `QUALIFICATION.md`, `NEXT-DELIVERY.md`, `DELIVERY-PLAN.md`, `COMPLETION-LEDGER.{md,json}`, `API-INVENTORY.md` | Current behaviour and boundary, test counts, what is next, requirement status (ledger is generated by `make ledger`). |
| `docs/RELEASE-0.N*.md` (58 files), `QA-*-2026-10.md`, `RELEASE-OPS-2026-10.md` | One release note per build or slice; QA records. Dated records: read, never rewrite. |
| `docs/current/` | Current guides (this one, the brief, deployment, operations, user, administrator, support), registers (data dictionary, key register, inventories, CSV traceability) and the edition 1.1 specifications. |
| `docs/governance/` | The 27 standard governance documents mapped in [../governance/README.md](../governance/README.md), plus `env.example`, `sbom/`. Drafted by an agent, not reviewed by counsel. |
| `docs/handover/` | `BACKLOG.md` (ready-to-run slices), `PARALLEL-WORK.md` (builder and integrator rules), `MERCYCORPS-REUSE.md`. |
| `docs/nonprofit-ai/v1.0/` | The separate document baseline for the AI area (marked proposed). |
| `docs/development-tracker/`, `docs/verification/` | Tracker data and early verification manifests. |
| `docs/evidence/` | Test output and screenshots the runners write. 1,829 tracked files. Append-only in spirit; see section 10. |
| `docs/history/v1.0/` | The original Word and workbook editions. Frozen. |
| `docs/CODEOWNERS` | Review owners (placed in `docs/` so changing it starts no paid run). |

Every document that describes the product keeps "current implementation" and "retained target design" apart (rule 23).

---

## 4. Nomenclature for this repository

Section 0.3 gives the general rules. This section gives the names you will meet here, with real examples. (Where a name rule differs from section 0, see 0.8.)

### 4.1 Code

| Thing | Rule | Real example |
|---|---|---|
| Python module | `snake_case.py`; area name, no version | `period_governance.py` |
| Contract generator | `<area>_contracts.py` with `augment(spec, policy)` | `work_contracts.py` |
| Python class | `PascalCase` | `DomainError`, `Service`, `TenantLifecycle`, `Worker` |
| Python function | `snake_case` verb | `decimal_value`, `record`, `acknowledge` |
| Domain action (route + verb) | route is a plural kebab noun, verb is kebab | `work-items` + `recalculate`; `reports` + `cancel-export` |
| Operation id | actions: `action_<route_with_underscores>_<verb>`; creates `create_<route>`, patches `patch_<route>` (built by `service.operation(route, verb)`) | `action_work_items_recalculate` |
| Capability | dotted lower case; `<noun-plural>.read`, `<noun-plural>.draft.create`, `<noun-plural>.draft.edit`, and `<noun>.<verb>` for actions | `observations.read`, `observation.submit`, `workflow.approve`, `report.publish`, `indicator.calculate` |
| Role template | `UPPER_SNAKE` | `AUTHOR`, `REVIEWER`, `MEL_ADMIN`, `PROGRAMME_MANAGER`, `TENANT_ADMIN`, `DATA_STEWARD`, `EXTERNAL` |
| Error code | `UPPER_SNAKE`; `reason_code` is a more specific `UPPER_SNAKE` | `POLICY_DENIED` with reason `INDEPENDENCE_REQUIRED`; `CONFLICT_VERSION` |
| Object kind (registry type) | `PascalCase` singular | `Observation`, `IndicatorInstance`, `AuditEvent`, `ReportExport` |
| Version constants | only in `VERSION.json`; per-feature `x-contract-version` records the API version that introduced a route | `"x-contract-version": "1.8.0"` |
| Environment variable | `IMPACT_` prefix, `UPPER_SNAKE` | `IMPACT_PORT`, `IMPACT_FIXTURE_DSN`, `IMPACT_UPGRADE_BASELINE`, `IMPACT_CONFIG_FILE` |
| Test file / function | `test_<area>[_unit\|_live].py` / sentence-like snake_case | `test_changes.py::test_correction_author_cannot_approve_and_rejection_preserves_source` |
| Browser check / mode | `tools/browser/<area>-check.mjs` / `<area>-browser` | `recovery-check.mjs` / `recovery-browser` |
| React component | `PascalCase`, file `PascalCase.tsx` | `RoundsPanel` in `Rounds.tsx` |

### 4.2 Database

| Thing | Rule | Real example |
|---|---|---|
| Schema | everything in `impact` | `impact.object_revision` |
| Table | singular `snake_case` | `tenant_principal`, `report_package_binding`, `import_unit_register` |
| Current-state projection | `<kind>_current` | `framework_current`, `target_current` |
| Insert-only register | `<thing>_register`, or named for the event | `import_unit_register`, `form_publication`, `evidence_access` |
| Typed reference | a column plus a generated `<col>_kind` column that fixes the object type | `import_id` + `import_id_kind ... ('ImportJob')` |
| Policy | `tenant_fence` on every tenant table | `CREATE POLICY tenant_fence ON ...` |
| Roles | `impact_owner` (migrations only), `impact_app`, `impact_identity`, `impact_platform`, `impact_worker`, `impact_privacy`, `impact_sensitive`, `impact_observer` | |
| Migration | `NNNN_topic.sql` | `0031_theory_of_change.sql` |

### 4.3 Documents, branches, commits

| Thing | Rule | Real example |
|---|---|---|
| Release note | `docs/RELEASE-<build>[-<topic>].md`, with Delivered, Contract and persistence, Limits, Reproduction (and Integration notes for a parallel slice) | `RELEASE-0.36-procurement-preview.md` |
| QA record | `docs/QA-<topic>-2026-10.md` | `QA-A11Y-2026-10.md` |
| Dated handover | `docs/<NAME>-<yyyy-mm-dd>.md` | `CLAUDE-HANDOFF-2026-10-06.md` |
| Guides and registers | `UPPER-CASE.md` | `DEPLOYMENT-GUIDE.md`, `ENGINEERING-GUIDE.md` |
| Edition 1.1 specification | `Impact-Management-<Name>-v1.1.md` (+ `.docx`) | `Impact-Management-LLD-v1.1.md` |
| Branch | `<type>/<topic>-<yyyy-mm-dd>` (see 0.8) | `docs/engineering-guide-2026-10-09` |
| Commit | `type: imperative sentence`, body says why | `refactor: one now() for twelve modules` |
| Requirement ids | `FR-`, `BR-`, `VF-` prefixes, as in the BRD/FSD and ledger | `FR-CAL-003`, `VF-DIN-001` |

---

## 5. How to write code here

Every excerpt below is real code, trimmed. Find the full version with the `rg` command beside it.

### 5.1 A domain command (a state-changing action)

`rg -n "def acknowledge" apps/api/impact_api/work.py`

```python
def acknowledge(self, c, ctx, notification, _data):
    self.ensure_visible(ctx, notification)
    row = c.execute(
        "SELECT acknowledged_at FROM impact.notification_acknowledgement "
        "WHERE tenant_id=%s AND notification_id=%s",
        (ctx.tenant_id, notification["object_id"]),
    ).fetchone()
    at = row["acknowledged_at"] if row else datetime.now(timezone.utc)
    if not row:
        c.execute(
            "INSERT INTO impact.notification_acknowledgement VALUES(%s,%s,%s,%s)",
            (ctx.tenant_id, notification["object_id"], ctx.principal_id, at),
        )
    return {"operation_id": "", "object_id": str(notification["object_id"]), ... "business_state": "Acknowledged"}
```

What to copy from it:

- `c` is an open tenant transaction, `ctx` is the authorised caller. Both come from `Service.command`; your method does not open a transaction.
- Every query is parameterised (`%s`) and filters on `tenant_id`. Never build SQL with f-strings or `%` formatting.
- The method is idempotent: a second call does not create a second row.
- It returns a receipt-shaped dict. `Service.command` fills in `operation_id` and `correlation_id` afterwards.

Two registrations in `service.py` make the action reachable (`rg -n "^ACTIONS" -A4 apps/api/impact_api/service.py`, and `rg -n "acknowledge" apps/api/impact_api/service.py`):

```python
ACTIONS = {
    ...
    "notifications": {"acknowledge"},
}
...
            elif action == "acknowledge":                      # inside Service.command
                receipt = self.work.acknowledge(c, ctx, previous, body["data"])
```

`Service.command` builds the operation id, validates the body against the closed schema, takes the **tenant advisory lock first** (`pg_advisory_xact_lock(hashtextextended(tenant,0))`), builds `ctx`, calls `authorize(...)`, checks the stored receipt for the operation id (a retry returns the stored outcome; the same id with a different body is `CONFLICT_OPERATION`), checks `expected_revision` (`CONFLICT_VERSION`), runs your branch, then fills `operation_id` and `correlation_id` into the receipt, writes the audit event and stores the receipt for 7 days. Do not reorder those steps (rule 17). The branch chain in `Service.command` is long and ordered; add your branch next to the ones for similar actions.

### 5.2 A `*_contracts.py` `augment()` (schema, path and policy for the action)

`rg -n "action\(" -A6 apps/api/impact_api/work_contracts.py`

```python
def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"
    ...
    action(
        "notifications",              # route
        "acknowledge",                # verb
        "notifications.acknowledge",  # capability
        ["AUTHOR", "REVIEWER", "MEL_ADMIN", "PROGRAMME_MANAGER", "ANALYST", "EXTERNAL"],  # role templates
    )
```

The inner `action()` helper creates a closed request schema (`operation_id`, `expected_revision`, `data`), copies a path template, and appends a policy row:

```python
{"operation_id": op, "method": "POST", "path": ..., "capability": capability,
 "role_templates": roles, "purpose_required": False, "fresh_assurance_seconds": None, "audit": True}
```

Notes: register a new module in `scripts/build_contracts.py` (imports at the top, call it in the sequence), and keep `augment_reference(spec, policy)` **last**; an earlier order once lost the reference-data routes. A state-changing, sensitive action uses `fresh_assurance_seconds: 300` (rule 10).

### 5.3 A test

`rg -n "def test_correction_author_cannot_approve" -A12 qualification/test_changes.py`

```python
def test_correction_author_cannot_approve_and_rejection_preserves_source(live, setup):
    _, _, _, row = approved_observation(live, setup)
    proposal = propose(live, row, "Observation", {"value": "20"})
    workflow = submit(live, "measurement-changes", proposal)
    data = {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Review"}
    assert (
        action(live, "workflows", workflow, "approve", data, status=403)["reason_code"]
        == "INDEPENDENCE_REQUIRED"
    )
```

For any new action, write at least these cases (brief section 8, step 5): the allowed actor; another tenant gets 404; a revoked actor gets 401 or 404; the wrong role gets 403; self-approval gives `INDEPENDENCE_REQUIRED`; a stale revision gives 409; an exact retry returns the identical receipt; the same operation id with a changed payload conflicts. Then assert the database facts through `live.db()` (one revision, one audit row, one outbox row, one receipt). Never use `time.sleep` to wait; never rely on "the latest record by timestamp" (brief hazards list).

### 5.4 A migration

`cat infrastructure/migrations/0009_reporting_packages.sql` (trimmed):

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.report_package_binding(
  tenant_id uuid NOT NULL,
  report_id uuid NOT NULL,
  report_revision uuid NOT NULL,
  reconciliation_digest bytea NOT NULL CHECK(octet_length(reconciliation_digest)=32),
  approved_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,report_id,report_revision),
  FOREIGN KEY(tenant_id,report_id,report_revision)
    REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);
ALTER TABLE impact.report_package_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_package_binding FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.report_package_binding
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.report_package_binding TO impact_app;
COMMIT;
```

Checklist: `tenant_id` first in the key and in every foreign key; RLS enabled *and forced*; `tenant_fence`; grants to the narrowest role (`impact_app` SELECT/INSERT for an insert-only register; the worker and control plane get nothing unless they need it); a comment saying why. An additive payload column on a typed projection looks like `0031_theory_of_change.sql` (`ALTER TABLE impact.target_current ADD COLUMN ...`). If you add a new property to a registry kind's payload, you **must** add the matching `ALTER TABLE <kind>_current ADD COLUMN` or the first write fails with SQLSTATE 42703 and the API answers 503.

### 5.5 Decimals and "money"

- The platform computes indicator values, not currency. The only money-like code is the AI cost draft (`ai_procurement_costs.py`), which also uses `Decimal`. **No `float` is used for any calculated or stored amount** (the two `float(` calls in the API read an Excel date serial and a worker setting). Do not introduce one.
- In transport a number is a **decimal string** matching `^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$` (`domain.NUMBER`). Parse with `decimal_value`. Storage is `NUMERIC(38,12)`; `domain.stored` rounds half-up to 12 places inside a 60-digit context.
- Calculate at high precision (`PRECISION = 100` in `domain.py`). Round **once**, at display, half-up, 0 to 6 places (`domain.display`). A negative that rounds to zero shows as `0`, never `-0.00`.
- Never sum displayed values. A pooled percentage is `sum(numerators) / sum(denominators)`: 50/100 and 1/10 give 51/110 = 46.36, not 30. A zero denominator yields UNDEFINED, never 0. A zero "expected" count is "not applicable", never 100 %.
- Official numbers come only from approved, versioned, deterministic rules over approved source revisions. AI may propose; it never supplies official arithmetic (rule 5).
- Currencies: the cost drafts take a `currency` code as supplied and do no conversion. Do not add exchange-rate logic.

### 5.6 Tenant rules

- Every tenant table row carries `tenant_id`. Every query you write filters on it, even though row-level security would also stop a leak. RLS is the second fence, not the first.
- Open a tenant transaction only through `Store.transaction(tenant)`. It sets the runtime role, a statement timeout (8 s) and lock timeout (3 s), and `set_config('impact.tenant_id', ..., true)` (transaction-local). Never set it at session level and never reuse a connection of uncertain state (rule 13).
- Client-supplied ids are selectors, never proof. A missing and a hidden resource both return `RESOURCE_UNAVAILABLE` with status 404 (`domain.unavailable()`); a wrong-tenant id must look exactly like a missing one.
- Take the tenant advisory lock before any tenant write and before resolving authority. Do not take other locks in a different order (LLD lock order; brief section 11).
- No external call (mail, HTTP, object store) inside the transaction that commits head + revision + projection + audit + outbox + receipt. Outbox rows are intent, never proof of delivery (rule 16).
- The API never holds `impact_owner` or the migration DSN. `store.py` refuses superuser, BYPASSRLS and owner connections in staging and production. Do not weaken that guard.

### 5.7 Error envelope

Raise `DomainError`; do not build responses by hand. `main.py` turns it into:

```json
{"code": "POLICY_DENIED", "message": "The action is not permitted.", "retryable": false,
 "correlation_id": "<uuid>", "permitted_actions": [], "field_errors": [],
 "reason_code": "INDEPENDENCE_REQUIRED"}
```

```python
raise DomainError("POLICY_DENIED", 403, reason="INDEPENDENCE_REQUIRED")
raise DomainError("CONFLICT_VERSION", 409)
raise DomainError("VALIDATION_FAILED", message="Use a decimal string with at most 12 fractional places.")
```

- `code` is the class (`AUTH_REQUIRED`, `RESOURCE_UNAVAILABLE`, `POLICY_DENIED`, `CONFLICT_VERSION`, `CONFLICT_OPERATION`, `STATE_TRANSITION_DENIED`, `VALIDATION_FAILED`, `SERVICE_UNAVAILABLE`, ...). `reason_code` is the machine-readable detail tests assert on. Messages are plain language and say what to do next.
- `retryable` is true only for 503. Never auto-retry a semantic conflict, and never retry an uncertain mutation blindly: find out what happened first (rule 17).
- Never put a stack trace, SQL, a secret or a login name in a message.

### 5.8 Independence rules

- Approval needs a **different natural person** from every material author. Compare `natural_identity_id`, not the account, membership or alias (`administration.py` does this through `impact.member_natural_identity`). Second logins, groups and delegation never create independence.
- Editing as a reviewer makes you an author. A stale approval never authorises a newer revision.
- There is no synthetic, login-less, "system" or waiver approver, ever. A first organisation needs three different people by design. An earlier attempt to add a synthetic second approver was rejected as a security weakening.
- The refusal is always `denied("INDEPENDENCE_REQUIRED")` / `DomainError("POLICY_DENIED", 403, reason="INDEPENDENCE_REQUIRED")`.
- Do not write a test that weakens this rule to reach green. If a test needs two people, the fixture already has `author`, `reviewer`, `owner`, `admin`.

### 5.9 Web client habits

- Fetch through the `request` prop the shell passes to a panel; show errors with `explain(e)`; wrap dialogs in the shared `Dialog`.
- Add the new capability prefix to `areaCapabilities` in `main.tsx`, or the screen stays hidden for people who hold only that capability.
- Keep computation out of components. If a view needs logic that a browser-less check can test, put it in a `*Model.ts` file (the AI area does this).
- A screen change needs its browser group to pass (`scripts/run.py <group>-browser`), and a new colour must come from `:root` tokens.

---

## 6. How to find things

Install `rg` (ripgrep). The recipes assume the repository root. All were run on 9 October 2026.

| # | Question | Command |
|---|---|---|
| 1 | Where is an API route or operation defined? | `rg -n "action_work_items_recalculate" packages/contracts apps/api scripts` (policy + contract) then `rg -n "def recalculate" apps/api/impact_api` (code) |
| 2 | Which module owns an area? | `ls apps/api/impact_api \| rg planning` (module + `planning_contracts.py`) |
| 3 | Where is a capability granted to roles and to fixture users? | `rg -n "notifications.acknowledge" packages/contracts/access-policy.json scripts/bootstrap.py apps/api/impact_api/bootstrap_profile.json` |
| 4 | Who raises this error code or reason? | `rg -n "INDEPENDENCE_REQUIRED" apps/api/impact_api` |
| 5 | Which tests cover an error or behaviour? | `rg -n -l "INDEPENDENCE_REQUIRED" qualification` |
| 6 | Where is a table defined and later altered? | `rg -n "import_unit_register" infrastructure/migrations` (first hit is the CREATE) |
| 7 | Which tables have row-level security policies? | `rg -c "tenant_fence" infrastructure/migrations` |
| 8 | Which SQL grants a role access to a table? | `rg -n "GRANT .* impact\.report_package_binding" infrastructure/migrations` |
| 9 | What is the next migration number? | `ls infrastructure/migrations \| tail -1` (add one) |
| 10 | Where does a screen live and how is it routed? | `rg -n "rounds" apps/web/src/main.tsx` (nav entry, route switch) and `ls apps/web/src \| rg -i rounds` |
| 11 | Which screens hide behind a capability? | `rg -n "areaCapabilities" apps/web/src` |
| 12 | Is there already a helper for this? | `rg -n "^def (now\|denied\|deny\|timestamp\|unavailable\|digest)\b" apps/api/impact_api` (section 3.3) |
| 13 | Which environment variables exist? | `rg -o "IMPACT_[A-Z_]+" -N --no-filename apps scripts deploy \| sort -u` and [../governance/env.example](../governance/env.example) |
| 14 | Where is a make target defined, and what does it run? | `rg -n "^unit:\|^lint:\|^test:" Makefile` |
| 15 | Which browser groups exist? | `rg -n "BROWSER_MODES" -A30 scripts/run.py` |
| 16 | What does CI run, and when? | `rg -n "paths-ignore\|timeout-minutes\|run:" .github/workflows` |
| 17 | Where is a version stated? | `cat VERSION.json`; `rg -n "BUILD\|DOMAIN_API\|SCHEMA" apps/api/impact_api/version.py`; do not grep documents for it |
| 18 | Which release note introduced a feature? | `rg -n -l "import executor" docs/RELEASE-*.md` |
| 19 | Where is a requirement id explained and tracked? | `rg -n "FR-CAL-003" docs/COMPLETION-LEDGER.md docs/current/Impact-Management-Platform-FSD-v1.1.md` |
| 20 | What did a document say at the time versus now? | `git log --follow --oneline -- docs/HANDOVER.md`; then `git show <sha>:docs/HANDOVER.md` |
| 21 | Which files reference a document I want to move or rename? | `rg -n "ENGINEERING-BRIEF.md" --glob "*.md"` |
| 22 | Is a file tracked or ignored? | `git ls-files \| rg evidence \| head`; `git check-ignore -v .local` |
| 23 | Who calls a function? | `rg -n "work\.recalculate\(" apps/api/impact_api` (finds the call in `service.py`; the definition is `def recalculate` in `work.py`) |
| 24 | What does the fixture contain? | `ls specification/fixtures` (`api-fixture.json`, `records.json`, `seed.sql`) |
| 25 | How does a deployment step work? | `ls deploy`; read [../../deploy/README.md](../../deploy/README.md) first, then `deploy/update.sh` |

Rule of thumb: search in this order. (1) The generated policy and contract (what exists), (2) the module, (3) the tests, (4) the migration, (5) the release note. A statement in a document is a claim; the contract and the code are the facts.

---

## 7. Commands and gates

### 7.1 Make targets

All commands run from the repository root. `PY` is `.venv/bin/python`.

| Target | What it does | Needs | Proves | Does not prove |
|---|---|---|---|---|
| `make setup` | venv, `pip install -r requirements.lock`, `npm ci` (web and dev-db), web build | internet, Python, Node | the toolchain installs | anything about behaviour |
| `make build` | `npm run build --prefix apps/web` (`tsc --noEmit && vite build`) | `make setup` | the client type-checks and bundles | that screens work |
| `make dev` | one process tree: in-memory PGlite, migrations, fixture, API, one worker. Credentials in `.local/dev/passwords.json` | `make setup` | the app starts on the fixture | correctness |
| `make worker` | one more outbox worker beside a running `make dev` | `make dev` running | — | — |
| `make lint` | `ruff check` and `ruff format --check` on `apps/api scripts qualification deploy`; Prettier `--check` on `apps/web/src`, the HTML files, `vite.config.ts`, `tools/dev-db/server.mjs`, `tools/browser/*.mjs` | `make setup` | style and basic errors (E4, E7, E9, F) | logic, types of Python |
| `make unit` | pytest on a named list of database-free test files | `make setup` | pure logic, version source, migration numbering, generated contracts in step, golden corpus on the reference | any API, database or UI behaviour; **rewrites `docs/evidence/golden-reconciliation.json`** |
| `make test` | `scripts/run.py test`: fresh in-memory PGlite, API, the whole pytest suite | `make setup` | behaviour of the API against a fixture | concurrency, real PostgreSQL roles, restart, restore, upgrade (native-only tests are skipped); overwrites `docs/evidence/application-tests.xml` |
| `make reference` | the preserved design-reference assertions (`specification/reference-v1/run_tests.py`) | `make setup` | the independent reference still agrees | the live code |
| `make golden` | `test_golden.py` through `scripts/run.py` (writes `docs/evidence/golden-reconciliation.json`) | `make setup` | the golden corpus against reference, domain code and live API | — |
| `make browser` | Chromium checks of the real UI, 26 groups one after another | Linux x86_64, `npm ci --prefix tools/browser` | screens render and flows work; the accessibility group fails on any serious axe violation | other browsers, screen readers |
| `make idp` | the live Keycloak suite and its browser check | Java 21 | sign-in through a real provider | production identity setup |
| `make native` | the suite on a real PostgreSQL with provisioned login roles, API restart, backup-restore drill, populated upgrade | `IMPACT_FIXTURE_DSN` pointing at an empty disposable `impact_test*` database | role boundaries, concurrency, restart, restore, upgrade | multi-node behaviour |
| `make perf` | performance harness (`PERF_ARGS="--profile peak"` etc.) | like `native` | measured latency in that setup | production capacity |
| `make ledger` | regenerates `docs/COMPLETION-LEDGER.{json,md}` | — | — | that a requirement is accepted |
| `make package` | writes `SHA256SUMS.json` and a source archive | — | — | — |

Other commands: `.venv/bin/python scripts/run.py test --pytest-path qualification/test_<area>.py` (one file; set a unique `IMPACT_PORT`); `.venv/bin/python scripts/run.py <group>-browser` (one browser group); `cd apps/web && npx tsc --noEmit`.

### 7.2 CI: two workflows

| Workflow / job | Runs when | What | Cap |
|---|---|---|---|
| `checks.yml` / `checks` | every pull request, every push to `main`, manual. **No path filter.** | pip + npm install, `make lint`, `scripts/doc_index.py --check`, `make unit`, `scripts/release_review.py --check --base HEAD^1` (checkout `fetch-depth: 2`), `npx tsc --noEmit` (working dir `apps/web`). Node 22, Python 3.12. | 15 min |
| `qualification.yml` / `local-reference-and-browser` | push to `main`; pull request; manual. **Skipped when every changed file is `*.md` or under `docs/`** (`paths-ignore: "**.md", "docs/**"`) | `make setup`, `make lint test reference`, then `make browser` | 30 min |
| `qualification.yml` / `live-identity-provider` | same | a pinned Keycloak 26.7.4: `test_live_idp.py` and the identity-provider browser check | 20 min |
| `qualification.yml` / `native-postgresql-gate` | same | PostgreSQL 17.11: provisioned logins, the suite on them, restart check, restore drill, upgrade from schema 33 (`IMPACT_UPGRADE_BASELINE`), live provider on native logins, an advisory PgBouncer subset | 40 min |
| `qualification.yml` / `container-stack` | same | the whole deployment path in Docker: `deploy/update.sh`, HTTPS smoke, first sign-in, secret rotation, backup set, restore drill, alert exercise | 45 min |

Facts you need to act correctly:

- **The release security review gate (FR-SEC-001).** `checks` fails when the build in `VERSION.json` has no `docs/release-reviews/release-review-<build>.json` (create it with `.venv/bin/python scripts/release_review.py --init --prepared-by "<name>"`), and when the change set (the pull request: first parent of the test merge commit) touches `infrastructure/migrations/*`, a `*_contracts.py` module, `packages/contracts/access-policy.json` or `apps/api/impact_api/ai_*.py` without modifying that file with a new `impact_reviews` entry naming the path. A pull request that carries several builds (stacked stories, for example 0.37.0 to 0.39.0 at once) may name the path in a new entry of any review it adds; each added earlier review is checked on its own (schema, file name, threats, areas, no credentials), and the review of a build already superseded at the base is closed to new entries. It also fails when a test referenced by `docs/current/threat-register.json` is renamed or removed, so update the register in the same change. `make unit` runs the same check on the committed files. Run `.venv/bin/python scripts/release_review.py --check` locally before pushing.

- A pull request that touches any file that is not `*.md` and not under `docs/` (including `Makefile`, `.github/**`, `pyproject.toml`, `.editorconfig`, SQL, Python, TSX, shell) starts **all four paid jobs**. A newer push to the same pull request cancels the run in progress. GitHub evaluates path filters on the first 300 changed files only; a pull request larger than that may start the paid run anyway (this is why `checks.yml` has no filter).
- `docs/CODEOWNERS` sits under `docs/` on purpose, so changing it starts no paid run.
- Cost: the paid run uses GitHub Actions minutes (jobs run in parallel, 15 to 45 minutes each; the last recorded green `main` run took about 12, 3 and 15 minutes for the first three jobs). The money cost per run is **unverified**. The Actions spending limit has been exhausted three times (1 to 3 October 2026). If every job fails within seconds **with zero steps** and the annotation mentions payments or the spending limit, that is billing, not code: stop and tell the owner.
- Therefore: batch your work, run the local gate first, push once, and allow at most two fix pushes. Do not push "to see what CI says".
- `container-stack` is the only check of the deployment path and cannot run in a development sandbox. A change to `deploy/**` is not verified until that job is green.
- `native-postgresql-gate` is the only place the concurrency, role-boundary and restore tests run. A green `make test` does not stand in for it.
- The pooler subset is advisory (it does not fail the job).

### 7.3 What a local run overwrites

Several runners write tracked files in `docs/evidence/` (`application-tests.xml`, `golden-reconciliation.json`, `reference-tests.json`, browser JSON and PNG files, `native-qualification.json`). After any focused run, a `make unit`, or any browser group:

```
git status
git checkout -- docs/evidence/ && git clean -f docs/evidence/
```

Do this unless you are deliberately publishing a clean *full* run. Never keep a full-suite count after a focused run, and never commit evidence from a run you did not complete. Verified for `make unit` and a focused `scripts/run.py test`.

### 7.4 Link check for documents

Nothing in the repository checks Markdown links. Save this outside the repository (for example `/tmp/linkcheck.py`) and run it on the files you changed:

```python
#!/usr/bin/env python3
"""linkcheck.py <files...>: report relative markdown links whose target does not exist."""
import re, sys, os
bad = 0
for f in sys.argv[1:]:
    s = open(f, encoding="utf8", errors="replace").read()
    s = re.sub(r"```.*?```", "", s, flags=re.S)
    for m in re.finditer(r"\]\(([^)\s]+)\)", s):
        t = m.group(1)
        if re.match(r"(https?:|mailto:|#)", t):
            continue
        t = t.split("#")[0]
        if not t:
            continue
        p = os.path.normpath(os.path.join(os.path.dirname(f), t))
        if not os.path.exists(p):
            print(f, "->", t)
            bad += 1
print("broken:", bad)
```

```
python3 /tmp/linkcheck.py $(git diff --name-only origin/main -- '*.md')
```

It does not check `#anchors`.

### 7.5 The sequence that must be green before a pull request

For a **documentation-only** change (everything `*.md` or under `docs/`):

1. Link check (7.4) on every changed file.
2. `python -m pytest qualification/test_version_unit.py -q` (about 1 second; proves the version source, migration numbering and generated contracts still agree).
3. If you changed the status block, compare it with `cat VERSION.json`, `ls infrastructure/migrations | wc -l` and the real `main` commit.
4. `git status` shows only the files you meant to change; evidence restored (7.3).

For a **code** change, in this order, stopping at the first failure:

1. `make lint`
2. `make unit`
3. `cd apps/web && npx tsc --noEmit` (or `make build`) if you touched the client
4. Regenerate anything generated that your change affects (section 8): contracts, access profile, ledger.
5. The focused tests for your area: `IMPACT_PORT=<free port> .venv/bin/python scripts/run.py test --pytest-path qualification/test_<area>.py`
6. The browser group of any screen you touched: `.venv/bin/python scripts/run.py <group>-browser`
7. Restore evidence (7.3); `git status`; `git diff --stat` and read the diff.
8. Commit, push once, open a **draft** pull request. Wait for `checks` and the four jobs. Fix reds; if a red is unrelated, say why in the pull request.

Say in the pull request exactly which of these ran and which did not. "Not run: `make native`, `make browser`, `make idp`" is an acceptable sentence; leaving it out is not.

### 7.6 Fixture expiry (a deadline)

The synthetic fixture's grants expire on `2027-09-01T00:00:00Z` (`FIXTURE_EXPIRES_AT` in `scripts/fixture_support.py`, stamped in `specification/fixtures/api-fixture.json`). `scripts/run.py` refuses to start (preflight) when fewer than **90 days** remain, that is from **3 June 2027**, because the suites create authority that expires up to 60 days from "now". Fix: `python scripts/redate_fixture.py --expires <new instant>` (optionally `--membership-expires`), then rerun the full suites and commit the regenerated fixture files. Never edit the fixture by hand. Check the days left: `python3 -c "import datetime as d; print((d.datetime(2027,9,1)-d.datetime.now()).days)"`.

### 7.7 How staging is updated (read, do not touch)

A timer on the staging server runs every 3 minutes, resets its checkout to `origin/main` and runs `deploy/update.sh` (build, migrate, restart). Nobody pushes to the server and there is no inbound SSH from development sandboxes. See [../../deploy/README.md](../../deploy/README.md) and [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md). Whether staging currently runs the latest `main` is stated, with its date, in the status block of [../HANDOVER.md](../HANDOVER.md). Never run `deploy/*.sh` against a server without the owner's say-so.

---

## 8. Common tasks, step by step

Each task starts with: `git fetch origin main && git switch -c <type>/<topic>-<yyyy-mm-dd> origin/main`. Each ends with the gate in 7.5, a draft pull request, and no merge.

If you are one of several parallel builders, follow [../handover/PARALLEL-WORK.md](../handover/PARALLEL-WORK.md) too: no version bump, no edits to the shared documents (the integrator does them), a migration named with the placeholder number, one push plus at most two fix pushes.

### 8.1 Add a domain action (a button that changes state)

1. In `<area>_contracts.py`, inside `augment(spec, policy)`, add the request schema, the path with `x-capability`, and a policy row (5.2). The smallest template is `work_contracts.action()`.
2. If the module is new, import and call its `augment` in `scripts/build_contracts.py`. Keep `augment_reference` last.
3. Regenerate: `python scripts/build_contracts.py && python scripts/export_implemented_api.py`. This rewrites the files in `packages/contracts/` and `docs/API-INVENTORY.md`. Commit them.
4. In `service.py`: add the verb to `ACTIONS[route]` and a branch in `Service.command` that calls your method (5.1). A new object kind also needs a migration (8.2).
5. Implement the method in `<area>.py` (5.1). Raise `DomainError` for refusals (5.7). Use `authorize`/`write`; never skip the audit and receipt.
6. Give the fixture users the capability: `scripts/bootstrap.py` has a hard-coded capability list. Without it every live test gets 403. Then follow 8.3 for the profile.
7. Write the tests (5.3) in `qualification/test_<area>.py`.
8. Update the documents together (8.5).

### 8.2 Add a migration

1. Name it `infrastructure/migrations/0041_<topic>.sql` (the file count plus one; contiguous). Parallel builders use the placeholder number and the integrator renames in merge order, by renaming the file only.
2. Write it as in 5.4: one `BEGIN;`, `SET LOCAL ROLE impact_owner;`, additive DDL, one `COMMIT;`. Comment why. Tenant tables get the key, RLS, `FORCE`, `tenant_fence` and the narrowest grants.
3. If a payload property is new on a registry kind, add the `ALTER TABLE <kind>_current ADD COLUMN` in this migration.
4. Never edit 0001 to 0040. If one is wrong, add a new migration that corrects it.
5. Run `sha256sum infrastructure/migrations/0041_<topic>.sql`. In [CURRENT-DATA-DICTIONARY.md](CURRENT-DATA-DICTIONARY.md) add the row to the "Migration register" table and a section `## 0041_<topic>.sql` with the source path, the SHA-256 and the SQL (copy the form of the 0040 section). The upgrade check and restore drill derive the expected count from the files and fail if the register differs.
6. Update the places that state the schema number: the status block in [../HANDOVER.md](../HANDOVER.md), the status line in [../../AGENTS.md](../../AGENTS.md), the dictionary header paragraph. (Find them with `rg -n "0041" --glob "*.md" -l`: today `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `docs/HANDOVER.md`, `docs/current/ENGINEERING-BRIEF.md` and the dictionary mention it. Dated notes such as `docs/CLAUDE-HANDOFF-2026-10-06.md` keep their old wording.)
7. Add real-role negative tests for any new tenant table (see `qualification/test_native_roles.py` for the pattern; it is native-only).
8. `python -m pytest qualification/test_version_unit.py -q` must pass; it checks numbering and file-name shape.
9. Know the cost: a migration is a non-doc change, so the pull request starts the paid run, and when merged it runs on staging within 3 minutes. If the deployed schema changes, the owner decides whether to move `IMPACT_UPGRADE_BASELINE` in `qualification.yml` (currently `'33'`).

### 8.3 Add a capability

1. Add the policy row (8.1 step 1) with the capability name in the style of section 4.1.
2. Grant it to the role templates in the row's `role_templates`. Changing the bundle of an onboarding role means editing `scripts/build_access_profile.py`.
3. `python scripts/build_access_profile.py`. This rewrites `apps/api/impact_api/bootstrap_profile.json` and changes the profile hash. Consequence: pending initial-access requests pinned to the old hash must be proposed again, and tenants that already applied initial access keep the ceiling they were given. `qualification/test_usable_staging_unit.py` fails when the profile is stale. Tell the owner in the pull request.
4. Add the capability to the fixture grant list in `scripts/bootstrap.py`.
5. If a screen uses it, add the prefix to `areaCapabilities` in `apps/web/src/main.tsx`.
6. Regenerate the contracts (8.1 step 3).

### 8.4 Add a screen

1. Create `apps/web/src/<Name>.tsx` (PascalCase) exporting a panel component. Take `request`, `explain`, `Dialog`, `capabilities` as props the way `Rounds.tsx` does.
2. In `main.tsx`: import it, add the navigation entry (`["rounds", "Collection rounds", "▦"]` is the shape), add the route branch, add the title in `titles`, and add the capability prefix in `areaCapabilities`.
3. Put view logic that does not need a browser in `<Name>Model.ts` and test it with an `.mjs` model check in `tools/browser/`.
4. Add a browser check `tools/browser/<area>-check.mjs` (copy `recovery-check.mjs`), a mode in `BROWSER_MODES` in `scripts/run.py`, and a line in the Makefile `browser` target. Checks must read the build number from `apps/web/package.json`, never hard-code it, and must wait for loaded text.
5. Use `:root` colour tokens and the shared `Dialog`. Run `a11y-browser`.
6. `make lint` (Prettier), `npx tsc --noEmit`, the group, then the gate.

### 8.5 Change a document

1. Find the current home of the fact: `rg -n "<phrase>" --glob "*.md"`. Edit it *there*; do not add a second statement elsewhere.
2. A new document goes under `docs/` (never the root) and is added by hand to [DOCUMENTATION-INDEX.md](DOCUMENTATION-INDEX.md) in the same pull request. Give it an owner and a "last reviewed" line if it is a policy document.
3. A document you supersede moves to `docs/history/` in the same pull request, and the old path gets nothing (update inbound links with `rg -n "<old name>" --glob "*.md"`).
4. Keep the current/target split: describe what the code does, then, separately, what is only designed.
5. A code change that changes behaviour updates, together: its release note `docs/RELEASE-0.N-<topic>.md` (Delivered, Contract and persistence, Limits, Reproduction), `docs/IMPLEMENTATION.md`, `docs/QUALIFICATION.md` (real counts only), `docs/NEXT-DELIVERY.md`, `docs/current/CURRENT-API-INVENTORY.md`, `docs/current/CHANGELOG.md`, and the CSV registers (`SCREEN-COVERAGE.csv`, `EXECUTION-REGISTER.csv`, `TRACEABILITY.csv`). Evidence paths go in `scripts/build_completion_ledger.py`, then `make ledger`. Promote a requirement only with source and named passing tests. (Parallel builders leave all but the release note to the integrator.)
6. Do not edit anything under `docs/history/`, an older release note's findings, `docs/evidence/`, or the preserved `specification/` documents. Corrections append a new dated entry.
7. Run the docs-only gate (7.5).

### 8.6 Update the status block

When the build, API versions, schema, `main`, CI result, staging state or open items change:

1. Edit only the table at the top of [../HANDOVER.md](../HANDOVER.md). Verify each cell against its source: `cat VERSION.json`; `ls infrastructure/migrations | wc -l`; `gh api repos/nakul175/impact-platform/commits/main --jq .sha`; the latest CI run of `main`.
2. Write the verification date in the heading line. Say "not checked from this workspace" for anything you could not check (for example the live staging server).
3. The status line at the top of `AGENTS.md` and the dictionary header repeat a few of these values today (section 10). Update them in the same pull request until they are reduced to a link.
4. Do not copy the new numbers into any other document.

### 8.7 Bump a version

Versions live in `VERSION.json` (`build`, `domain_api`, `platform_api`) plus the web package.

1. Edit `VERSION.json`.
2. Set the same build in `apps/web/package.json` and in `apps/web/package-lock.json` (both `"version"` fields: top level and `packages[""]`). Edit both by hand and diff the lock to be sure only those two fields changed (unverified: whether `npm version` would also do it cleanly).
3. `python scripts/build_contracts.py && python scripts/export_implemented_api.py`.
4. `python -m pytest qualification/test_version_unit.py -q`.
5. Never write the version into runtime code, tests or scripts as a literal; `test_version_unit.py` fails if you do. Per-feature `x-contract-version` constants stay as they are.
6. The schema number is not bumped; it is the migration count.
7. Update the status block (8.6) and add the release note (8.5). A bump is normally the integrator's job, not a slice builder's.

---

## 9. Do and don't

### 9.1 Do

- **Branch from current `origin/main`, open a draft pull request.** Why: `main` deploys itself, and the draft keeps an unreviewed change from being merged by accident.
- **Read the rules that must never be broken** ([AGENTS.md](../../AGENTS.md)) before the first edit. Why: most are security invariants that tests alone do not catch.
- **Search before you write** (section 6, recipe 12). Why: the repository already carries duplicate helpers; a second copy is a defect.
- **Make one change per pull request**, and say what ran and what did not. Why: reviews are done by an owner who is not an engineer; small and honest is reviewable.
- **Write the failing test first for a bug fix**, and name the behaviour in the test name.
- **Restore `docs/evidence/` after local runs** (7.3). Why: otherwise unrelated rewrites land in your diff and hide the real change.
- **Fetch again before you push.** Why: the owner has also used Cursor's agent on this repository; a branch can receive commits from another tool while you work. Never push to someone else's branch.
- **Use only synthetic data** (`example.org`, `example.test`, the fixture identities).
- **Keep application authority on the server**, deny by default, and return the same 404 for missing and hidden resources.
- **Use `Decimal` and decimal strings** for every calculated value (5.5).
- **State confidence** ("high / medium / low, because ...") and put the uncomfortable fact first when you write to the owner.
- **Ask the owner before** anything that costs money (CI minutes, cloud resources, paid services, a new workflow) or cannot be undone (merging, deploying, deleting branches or data). Why: stated in AGENTS.md; the Actions budget has run out three times.
- **Update the status block** when you change something it states (8.6), and nowhere else.
- **Leave work in a state another person can continue:** committed, pushed, a draft pull request, "what is unfinished and the exact next command" written in the pull request.

### 9.2 Don't

- **Don't push to `main`, and don't merge** without `checks` and all four qualification jobs green *and* the owner's confirmation. Why: `main` goes to the staging server within 3 minutes, migrations included. Never force-push `main`.
- **Don't edit an applied migration (0001 to 0040), a retained evidence file, a receipt, anything under `docs/history/`, or `specification/` documents.** Why: checksums and audit history; corrections append.
- **Don't leave a gap in migration numbering.** Why: `scripts/migrate.py` and `test_version_unit.py` refuse to start, and then every runner is down.
- **Don't hand-edit generated files** (`packages/contracts/*`, `docs/API-INVENTORY.md`, `bootstrap_profile.json`, `docs/COMPLETION-LEDGER.*`). Regenerate them. Why: a hand edit is overwritten and the stale-check fails.
- **Don't add a version literal** (`"0.36.0"`) to code, tests, scripts or browser checks. Why: `test_version_unit.py` fails, and a hard-coded build once broke a browser run.
- **Don't weaken, skip or delete a test, an independence rule, a RLS policy or the lint to get green.** Don't add `# noqa`. Why: a green built on a weaker check is a false statement to the owner.
- **Don't add a synthetic, login-less, "system" or waiver approver.** It was tried and rejected as a security weakening.
- **Don't create accounts or set passwords, type credentials into anything, or act as a person.** Accounts come only from the governed flows and the owner's console scripts.
- **Don't commit** credentials, keys, tokens, `.local/`, `secrets.env`, generated passwords, participant data, `.env*`, databases, build output or logs.
- **Don't present PGlite results as concurrency evidence**, a PARTIAL requirement as accepted, a design section as implemented, or staging as production. Nothing here is production-ready.
- **Don't call an external service inside the commit transaction**, and don't treat an outbox row as proof of delivery.
- **Don't retry an uncertain mutation blindly.** Find out what happened (receipt, audit, outbox) first.
- **Don't build SQL with string formatting**, don't set `impact.tenant_id` at session level, don't connect as `impact_owner` or a superuser from the API.
- **Don't use a float** for a calculated value, and don't sum displayed (rounded) values.
- **Don't run two runners on port 8000.** Set `IMPACT_PORT`. Why: the second run times out or talks to the first run's API.
- **Don't pick "the latest" record by timestamp in a test.** Identify records by the id your step created. Why: the worker's skewed test clock leaves sweeps hours ahead; such tests pass alone and fail in suite order.
- **Don't retire a delivery secret without a grace window** (`rotate_secrets.py --expired`). Why: every intent sealed under it becomes undeliverable.
- **Don't run `deploy/*.sh` or touch a server** without the owner's say-so. Don't enable a real e-mail provider, paid AI or real recipients.
- **Don't add a root-level document, a second status statement, or a count copied from elsewhere.**
- **Don't split or reformat a file you are not otherwise changing**, and don't mix a refactor into a feature pull request. Why: it buries the real change.
- **Don't add a dependency** without a reason in the pull request; pin exact versions in `requirements.txt` and regenerate `requirements.lock` (the deployment image installs from a hash file derived from the lock).
- **Don't merge a draft that skipped the paid run by accident:** a PR that mixes `docs/` with one code file is not docs-only.

---

## 10. Keeping it clean

### 10.1 Rules

1. One purpose per branch. Prefer deleting to adding.
2. One place per fact: the status block for state; the contract and the code for behaviour; the release note for what a build delivered at the time.
3. New documents go under `docs/` and in the index. New root files are not allowed.
4. Generated files are regenerated, never edited. Evidence is appended, never rewritten.
5. A superseded document moves to `docs/history/` in the same pull request.
6. A dated record keeps its date and its limits. When a later fact contradicts it, add a dated correction pointing to the later fact; do not silently edit the old text.
7. `TODO` carries an owner and a date or does not exist. Commented-out code is deleted.
8. A helper exists once (section 3.3).

### 10.2 What CI enforces and what only people enforce

| Enforced by a machine | Enforced only by review |
|---|---|
| Python style and basic errors, Prettier formatting (`make lint`) | Naming rules in section 4 (nothing checks them, except migration file names and, through the policy, capability shape) |
| Version source in step with migrations, web package, generated contracts; no version literals (`test_version_unit.py`) | Documents placed under `docs/` and added to the index |
| Contiguous migration numbering | The status block telling the truth |
| All database, UI, role, restart, restore, upgrade and deployment behaviour (four paid jobs) | One purpose per pull request; no drive-by reformatting |
| Web type check (`tsc`) | No new evidence bulk; no stale banners; no copied numbers |
| Stale onboarding profile (`test_usable_staging_unit.py`) | Honest "what was not run" in the pull request |

Nothing enforces: Markdown links, document dates, the index, `docs/evidence/` growth, or whether a document is current. Those rely on this section and on the monthly check below.

### 10.3 Monthly 10-minute hygiene checklist

Run from a fresh `origin/main` checkout. Tick or write down each result; open one pull request for fixes, not one per item.

1. `git fetch --prune && git branch -r --merged origin/main` : list merged remote branches. Ask the owner before deleting any (deleting is irreversible).
2. `gh api 'repos/nakul175/impact-platform/pulls?state=open' --jq '.[] | [.number,.title,.updated_at] | @tsv'` : close or chase pull requests untouched for a month (ask the owner first).
3. `make lint && make unit`, then `git status`: both must pass and the tree must be clean after restoring evidence (7.3). If `git status` shows other changes, a runner is writing a tracked file; note it in section 10.4.
4. `ls *.md LICENSE` : exactly `README.md AGENTS.md CLAUDE.md CONTRIBUTING.md SECURITY.md CHANGELOG.md LICENSE`.
5. Status block vs reality: `cat VERSION.json`, `ls infrastructure/migrations | wc -l`, latest `main` commit and its CI result vs the table in `docs/HANDOVER.md`.
6. Fixture days left (7.6). Raise it with the owner at 150 days, because the runner stops at 90.
7. `git ls-files docs/evidence | wc -l` : record the number; it should not go up except for a deliberate clean full run.
8. Link check over every Markdown file (7.4): `python3 /tmp/linkcheck.py $(git ls-files '*.md')`.
9. Helper duplicates: `rg -n "^def (now|denied|deny|timestamp|unavailable)\b" apps/api/impact_api` : the list in 3.3 must not grow.
10. `git ls-files | rg -i "(^|/)\.env|\.pem$|\.key$|passwords|secrets\.env"` : must print nothing. Any hit is an incident for the owner, not a tidy-up. Then `git ls-files '*.log' '*.png' '*.zip' '*.mp4' '*.webm' | rg -v "^docs/(evidence|history|nonprofit-ai)/" | wc -l` : was 7 on 9 October 2026; it must not rise.
11. Dependency pins: `git log -1 --format=%cs -- requirements.lock apps/web/package-lock.json` : if older than 3 months, tell the owner (updating costs a paid run).
12. Write the date and the findings into the pull request or the status block's "open items".

### 10.4 Known leftover mess (honest list, 9 October 2026)

None of this should get worse. Fix items in dedicated, reviewed pull requests, not as a side effect.

- **Evidence bulk.** `docs/evidence/` tracks 1,829 files, about 100 MB, including 660 under `sprint-0.36` and many numbered attempt folders from builds 0.34 and 0.35. The standard says evidence should be manifests and hashes with the files outside git. An unmerged branch, `chore/dedupe-evidence-2026-10-09`, removes 525 byte-identical duplicates under `sprint-0.36` (its contents were not reviewed for this guide). A fuller plan needs an owner decision on where evidence lives.
- **Release notes without supersession marks.** 58 `RELEASE-*.md` files sit in `docs/`; none says whether a later build replaced it. `docs/HANDOVER.md` below its status block is the 3 October 2026 handover at build 0.27.0, kept as written; `docs/current/ARCHITECTURE-CURRENT.md` describes build 0.18.0; `docs/current/ENGINEERING-BRIEF.md` section 1 and parts of section 2 are written for 0.27.0. Read dates before trusting a number.
- **Two index files, edited by hand.** `docs/DOCUMENTATION-INDEX.md` is a short, partly stale entry page with long build paragraphs; `docs/current/DOCUMENTATION-INDEX.md` is the real one and carries stacked "checkpoint" paragraphs for superseded builds.
- **Flat `impact_api` package.** About 105 modules, no sub-packages, large files (`worker.py`, `planning.py`, `main.py`, `service.py`'s long `command` branch chain), function-local imports used to break cycles (for example `from .service import revision`), and the duplicate small helpers in 3.3. Only 12 modules use `clock.py`; the rest call `datetime.now(timezone.utc)` directly.
- **Statements that disagree with the tree** (found while writing this guide; all verified):
  - `README.md` says the first start "applies thirty-nine migrations" (it applies 40), asks for Node 24 (the small check uses 22), and still carries stacked build paragraphs from 0.18 to 0.27.
  - `AGENTS.md` says the browser run has "19 groups"; the Makefile lists 26.
  - `CONTRIBUTING.md` calls `CLAUDE.md` "the full engineering brief"; the brief moved to `docs/current/ENGINEERING-BRIEF.md` on 8 October 2026.
  - `infrastructure/migrations/0040_ai_plan_portability.sql` opens with the comment "Unregistered 0040 draft, outside repository; not project-applied". It is in the repository and applied. The file is frozen, so the comment stays; treat it as stale.
  - The governance map ([../governance/README.md](../governance/README.md)) flags `CHANGELOG`, `ARCHITECTURE-CURRENT`, `USER-GUIDE` and `ADMINISTRATOR-GUIDE` as stale.
- **Binary and log files in git.** 88 `.log`, 382 `.png` and 2 `.zip` files are tracked (almost all under `docs/evidence`, `docs/nonprofit-ai` and `docs/history`), against the standard's "no screenshots, logs, zips". Do not add more.
- **Tracked-file side effects.** `scripts/run.py test` and the browser runners still rewrite tracked evidence files (7.3); `make unit` no longer does. A runner that writes tracked files is a trap; the fix (write to an ignored path) is not made for the others.
- **`qualification/drafts/`** holds SQL and Python drafts (for example `0039_human_advice_anchor_availability.sql`) that are not migrations and not run. Do not copy from them as if they were applied.
- **Lint is lenient.** `ruff check` selects only `E4, E7, E9, F`; there is no import-order, naming, complexity or unused-argument rule, and Python is mostly unannotated.
- **`any` in the web client** (existing uses of `Record<string, any>`).
- **Unverified in this guide:** how long the full `make test`, `make browser` and `make native` take locally on a 2-CPU machine (CI timings are quoted in 7.2); the money cost of one paid run; whether staging currently runs the latest `main`; whether Dependabot or any other bot is configured on GitHub.

---

## 11. Glossary

| Term | Meaning here |
|---|---|
| Tenant | One organisation's workspace. Every tenant table row carries `tenant_id`. |
| Control plane | The platform-operator side: creating tenants, operators, accounts. Separate API (`openapi-platform.json`) and role (`impact_platform`). |
| Capability | A named permission such as `observation.submit`. Read, export, approve, publish and sensitive-field access are separate capabilities. |
| Role template | A bundle of capabilities (`AUTHOR`, `REVIEWER`, ...). |
| Grant, scope | A capability held by a member over a scope (the whole tenant, a programme, ...). Possibly with a purpose and an expiry. |
| Purpose-bound | A capability that works only when the caller states a purpose (audit export, privacy cases). |
| Fresh assurance | Sensitive actions need authentication within the previous 300 seconds (`auth_time`), not just a valid token. |
| Natural person | The real individual behind accounts. Independence is checked on this, not on logins. |
| Independence | The approver must be a different natural person from every material author. |
| Object, revision | An object is a head row (`object_registry`); each change is an immutable `object_revision`. Approved revisions never change. |
| Kind | The object type: `Observation`, `IndicatorInstance`, `Report`, ... |
| Projection (`*_current`) | A typed table holding the current state of a kind, upserted from the payload. |
| Operation id | A client-chosen UUID that makes a command idempotent. Same id and body returns the stored receipt; same id and a different body is a conflict. |
| Receipt | The stored outcome of a command (`operation_receipt`), kept 7 days. |
| Outbox | Rows recording "something should be delivered". Intent, never proof of delivery. Worked by the worker. |
| Programme, indicator, observation | A funded effort; a governed measure; one reported value with its source. |
| Collection plan, obligation | The expected sources for an indicator and period; each expected contributor is an obligation. |
| Period, snapshot, close | A reporting window; the frozen set of approved inputs at close; the independent decision that locks it and creates OFFICIAL results. |
| Provisional / official result | A calculation that can still change; the result pinned at period close. |
| Restatement | A governed correction of a closed period's included value. |
| Framework, target | The results framework (impact, outcome, output, activity nodes) and the targets set against indicators. |
| Report package, publication | A frozen, approved report; its controlled release to named recipients. Approval and publication are separate decisions. |
| Fixture | The synthetic dataset and identities in `specification/fixtures`, loaded by every runner. Expires 2027-09-01. |
| PGlite | An embedded PostgreSQL used for local runs and `make test`. Single connection at a time; not concurrency evidence. |
| Native | A real PostgreSQL 16/17 with provisioned login roles (`make native`, the CI native job). |
| Worker, executor | Background processes: outbox/export/retention work; queued import commits. |
| Ledger | `docs/COMPLETION-LEDGER.md`: status of every written requirement (PARTIAL, PENDING, accepted). |
| Slice, integrator | A bounded unit of parallel work on its own branch; the one person who merges slices, renumbers migrations and bumps versions. |
| Staging | The one test server that follows `main`. Synthetic data only. Not production. |

---

## 12. Where things stand and what is next

This guide deliberately holds no status. For the current build, API versions, schema, `main`, the latest CI result, the staging state and the open owner decisions, read the status block at the top of [../HANDOVER.md](../HANDOVER.md). For what is next, read [../NEXT-DELIVERY.md](../NEXT-DELIVERY.md), [../DELIVERY-PLAN.md](../DELIVERY-PLAN.md) and the ready-to-run slices in [../handover/BACKLOG.md](../handover/BACKLOG.md). For the state of every requirement, read [../COMPLETION-LEDGER.md](../COMPLETION-LEDGER.md).

When you hand over: everything committed and pushed on a branch with a draft pull request; the status block current; "what is unfinished and the exact next command" written down; no uncommitted work left in the checkout.
