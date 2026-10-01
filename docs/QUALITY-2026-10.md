# Quality and hardening — October 2026

Branch `quality/2026-10-hardening` (based on `main` at ffbd931, build 0.20.0). No build or domain API
version change; no requirement status change. Steps 3 (narrowing `impact_worker`, migration 0025) and
4 (operator re-queue, platform API 1.5.0) follow on the stacked branch `quality/2026-10-worker-grants`
and are described in their own sections there.

## 1. Intermittent failure in `test_suspension_and_missing_recovery_contact_block_renewal`

Observed once on the CI native job (PostgreSQL 17.11, commit ffbd931, 1 Oct 2026 ~01:32 UTC): the
owner's `cancel` of a pending renewal after suspension answered 200 `Cancelled` where the test expected
403; a rerun of the same commit passed.

Root cause (test defect, product correct):

- Suspension (`tenant_lifecycle.py`, transition to Suspended/Closing) sets every tenant principal's
  `auth_not_before` to the suspension instant.
- `authority_renewal.py` deliberately exempts `cancel` and `reject` from `TENANT_NOT_ACTIVE`
  (RELEASE-0.13: "The owner can withdraw a pending proposal"). The only 403 the owner's cancel can get
  here is `REAUTHENTICATION_REQUIRED`, when the caller's `auth_time` is not later than the owner
  principal's `auth_not_before`.
- The suite reuses each actor's token for up to 60 s (`qualification/conftest.py`,
  `TOKEN_REUSE_SECONDS`), shared across tests. When the author's cached token turned 60 s old between
  the suspension and the cancel (in practice at the `propose` call right after the suspension), a new
  token was minted with an `auth_time` after the cutoff, and the owner legitimately withdrew the
  proposal. Whether it happened depended only on how long earlier tests had run, which is why a rerun
  passed. The UTC date change and the relative `review_expires_at`/`expires_at` play no part, the
  suspension is read under the tenant advisory lock in the same transaction as the cancel, and the
  earlier refused `approve` calls roll back and mutate nothing.
- Reproduced deterministically on PGlite by setting `TOKEN_REUSE_SECONDS = 0`: `assert 200 == 403`.

Fix: the test pins the owner's `auth_time` five seconds before the suspension and asserts
`REAUTHENTICATION_REQUIRED`; a new test
(`test_owner_who_authenticated_after_suspension_may_withdraw_a_pending_renewal`) records the
documented behaviour that an owner who authenticated after the suspension may withdraw.
`qualification/test_authority_renewal.py`: 29 passed on PGlite.

## 2. Single version source

- `VERSION.json` (repository root): `build`, `domain_api`, `platform_api`, `documentation_edition`.
- `apps/api/impact_api/version.py` reads it and exports `BUILD`, `DOMAIN_API`, `PLATFORM_API`,
  `DOCUMENTATION_EDITION` and `SCHEMA`. `SCHEMA` is never a literal: it is the number of files in
  `infrastructure/migrations` — the same rule `scripts/migrate.py` uses for `LATEST`.
- Readers: `main.py` (FastAPI version, `/health/ready` gate `version != SCHEMA`, runtime manifest
  `build_id`/`schema_version`/`api_version`), `worker.py` (heartbeat build), `tenant_contracts.py`
  (platform API), `scripts/build_contracts.py` (published domain API version of `openapi.json` and
  `access-policy.json`), `scripts/build_completion_ledger.py`, `scripts/package_source.py` (archive
  name), `tools/browser/tenant-check.mjs`, `qualification/test_worker.py` and `test_native_worker.py`.
  `deploy/Dockerfile` copies `VERSION.json` into the image.
- `qualification/test_version_unit.py` (added to `make unit`; also collected by `make test`) fails
  when: a key is missing or malformed; migration numbers are not contiguous from 0001 (so the count
  would differ from the highest applied version); `apps/web/package.json` or its lock differ from the
  build; the generated contracts carry a different domain or platform version (contracts not
  regenerated); a runtime module repeats the build literal or the readiness gate a number.
- The per-feature `*_contracts.py` `x-contract-version`/`VERSION` values record the API version that
  introduced each route and stay as they are; `build_contracts.py` overwrites the published version.
- Contracts regenerate byte-identical; the values are unchanged.

## 5. Small fixes

- `tenant_lifecycle.py`: owner-independence check is one `str(...) == str(...)` comparison (the
  UUID-to-str clause was always false).
- `tools/browser/prepare.mjs`: runs `$PYTHON` or `python3`.
- `scripts/idp.py`: docstring now says the foreign realm's author carries a subject derived from the
  author's.
- `.github/workflows/qualification.yml`: `actions/checkout@v6`, `setup-python@v6`, `setup-node@v6`,
  `setup-java@v5`, `cache@v5`, `upload-artifact@v6`; each tag's `action.yml` was read and declares
  `runs.using: node24` (`upload-artifact@v5` is still node20, so v6 is the first Node 24 major).
  Newer majors exist (checkout/setup-python/setup-node/upload-artifact v7, setup-java/cache v6); they
  were not adopted without reading their breaking changes.

## Tests run locally (PGlite, focused files only)

| Run | Result |
|---|---|
| `test_authority_renewal.py` | 29 passed |
| original test with `TOKEN_REUSE_SECONDS = 0` (reproduction, not committed) | 1 failed (200 == 403) |
| `test_worker.py` | 31 passed |
| `test_tenant_lifecycle.py` | 14 passed |
| `make unit` | 230 passed, 37 skipped |
| `make lint` | clean |

Full, browser, native and live-provider suites run in CI on push.

## Integration notes

Shared files touched by this branch: `Makefile` (unit target gains `qualification/test_version_unit.py`),
`deploy/Dockerfile` (one `COPY VERSION.json`), `apps/api/impact_api/main.py` (import plus three
version sites), `worker.py` (one import), `tenant_contracts.py` (one import and the info version),
`scripts/build_contracts.py`, `scripts/build_completion_ledger.py`, `scripts/package_source.py`,
`tools/browser/tenant-check.mjs`, `tools/browser/prepare.mjs`, `scripts/idp.py`,
`.github/workflows/qualification.yml`, `qualification/test_worker.py`, `test_native_worker.py`,
`test_authority_renewal.py`.

How the version source works for the other branches:

- A new migration `00NN_<topic>.sql` needs no version edit: readiness, the runtime manifest, the
  upgrade check and the restore drill all derive the schema from the file count. Keep numbering
  contiguous (the unit test enforces it) and still append the migration and its SHA-256 to
  `CURRENT-DATA-DICTIONARY.md`.
- The integrator bumps the build in `VERSION.json` and `apps/web/package.json` + `package-lock.json`
  (the unit test fails until all three agree), and the domain API in `VERSION.json` only, then runs
  `python scripts/build_contracts.py && python scripts/export_implemented_api.py` (the unit test fails
  if the contracts were not regenerated). Branches that resolved conflicts on the old literals in
  `main.py` (`version != 21`, `"impact-0.20.0"`, `"1.13.0"`) take this branch's lines.

Lines for the shared documents (the integrator applies them):

- CLAUDE.md §8 "Version literals to bump together": replace with "Build, domain API and platform API
  live in `VERSION.json` (plus `apps/web/package.json` and its lock for the build; checked by
  `qualification/test_version_unit.py`); the schema version is the migration count."
  §11 drop the tenant_lifecycle UUID/str and prepare.mjs `python` items and the scripts/idp.py
  docstring item; §1 "Evidence": one more authority-renewal test.
- IMPLEMENTATION.md: "Versions are read from `VERSION.json`; the readiness gate expects the number of
  migration files."
- QUALIFICATION.md: test counts move by +1 application test (`test_authority_renewal.py`) and +5 unit
  checks (`test_version_unit.py`); record the root cause of the renewal-cancel flake.
- CHANGELOG.md: "Quality: deterministic renewal-cancel test; single version source; Node 24 CI actions;
  small fixes (tenant_lifecycle comparison, prepare.mjs python3, idp.py docstring)."
- NEXT-DELIVERY.md / DELIVERY-PLAN open items: "a single version source" (v0.17) is delivered.
