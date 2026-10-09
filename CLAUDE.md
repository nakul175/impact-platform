# Impact Platform — entry point for Claude sessions

This file is short on purpose. The rules, commands and safety limits are in [AGENTS.md](AGENTS.md); the current build, API, schema, `main` and CI state is stated once, in the status block at the top of [docs/HANDOVER.md](docs/HANDOVER.md). The long engineering brief that used to be this file (domain vocabulary, architecture as built, database security, how to change things, verified fragile spots) is [docs/current/ENGINEERING-BRIEF.md](docs/current/ENGINEERING-BRIEF.md); other documents that cite "CLAUDE.md §N" mean that file.

## Read in this order

1. [AGENTS.md](AGENTS.md): rules that must never be broken, safety rules, commands, how to work with the owner.
2. [docs/HANDOVER.md](docs/HANDOVER.md): status block first; the body is the 3 October handover and says so.
3. [docs/current/ENGINEERING-BRIEF.md](docs/current/ENGINEERING-BRIEF.md): open the section you need, not the whole file (it is long). §3 vocabulary, §5 architecture, §6 data model and database security, §8 how to change things, §11 fragile spots.
4. [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md): what the current build does and does not do. [docs/NEXT-DELIVERY.md](docs/NEXT-DELIVERY.md): what is next.
5. [docs/DOCUMENTATION-INDEX.md](docs/DOCUMENTATION-INDEX.md): every other document.
6. [docs/current/ENGINEERING-GUIDE.md](docs/current/ENGINEERING-GUIDE.md): the practical manual (first hour, map, naming, do and don't).

## What this is

A multi-tenant monitoring, evaluation, learning and impact-reporting platform, built as a deliberately conservative development build: requirements are PARTIAL or PENDING, none is accepted, data is synthetic, and nothing is production-ready. Never write anything that says or implies otherwise. A PARTIAL requirement is a bounded, tested subset; PGlite evidence is never concurrency evidence; a target-design section is never "implemented".

## Hazards that have already cost time

Each item is explained in the engineering brief; this list is only the reminder.

- **`main` deploys itself.** The staging server pulls `main` every three minutes and runs migrations. Never push to `main`; never merge without all four CI jobs green and the owner's say-so.
- **Migrations 0001 to 0040 are frozen.** The next is `0041_<topic>.sql`, additive, contiguous, with `BEGIN;` / `SET LOCAL ROLE impact_owner;` / `COMMIT;`. A gap in the numbering makes every runner refuse to start. Append the SQL and its SHA-256 to `docs/current/CURRENT-DATA-DICTIONARY.md` in the same change.
- **Every tenant table** carries `tenant_id` in its primary key and every foreign key, gets `ENABLE` and `FORCE ROW LEVEL SECURITY` and the `tenant_fence` policy, and gets the narrowest grants. Add real-role negative tests.
- **Versions come from two places only:** `VERSION.json` (plus `apps/web/package.json` and its lock) and the migration count. After a bump run `python scripts/build_contracts.py && python scripts/export_implemented_api.py`. `qualification/test_version_unit.py` fails if a runtime module repeats a version literal or the contracts are stale.
- **A new capability** needs: its policy row via `augment()`, the fixture grant in `scripts/bootstrap.py`, `python scripts/build_access_profile.py`, and the prefix in `areaCapabilities` in `apps/web/src/main.tsx`, or the screen stays hidden for people who hold only that capability.
- **A new worker query** needs an explicit grant in a new migration; `impact_worker` was narrowed by 0025 and 0026 and gets `InsufficientPrivilege` otherwise (logged as a failed tenant pass, not a crash).
- **A new payload property** on a registry kind needs `ALTER TABLE <kind>_current ADD COLUMN` in a migration, or the first write fails with SQLSTATE 42703 and the API answers 503.
- **Periods:** more than one reporting calendar can contain the same date. Code that resolves "the period of an event" must consider every containing period, not the latest.
- **Tests that pick "the latest" record by timestamp are order-dependent** (the worker's skewed test clock leaves sweeps hours ahead). Identify records by the identity a step created. A builder's focused run is not a suite-order run.
- **A focused test run overwrites `docs/evidence/` files.** Restore them (`git checkout -- docs/evidence/ && git clean -f docs/evidence/`) unless you are publishing a clean full run, and never keep a full-suite count after a focused run.
- **Port 8000 is every runner's default API port.** Set `IMPACT_PORT` when anything else is running.
- **Browser checks:** wait for the loaded text, never read an element's text the moment it exists; the status banner polls every 60 s and a panel's own read can queue behind it on PGlite. Browser modes start no worker; checks run one iteration through `runWorkerOnce` inside `quietly()`.
- **Sealed values and keys:** retiring a delivery secret makes every intent sealed under it undeliverable. Rotate with a grace window, retire with `--expired`.
- **Identity and independence:** approval needs a different natural person from every material author; aliases, second logins, groups and delegation never create independence. No synthetic or waiver approver, ever.
- **The PGlite socket server frames protocol messages** (`tools/dev-db/server.mjs`); keep that framing if the PGlite packages are upgraded.

## Commands

The full list is in [AGENTS.md](AGENTS.md) ("Set up, run and test"). The ones used most:

```
make setup            # virtualenv + npm ci + web build
make dev              # http://127.0.0.1:8000, synthetic data, passwords in .local/dev/passwords.json
make lint             # ruff + ruff format --check + prettier --check
make unit             # pure tests, no database
IMPACT_PORT=8123 make test    # full suite on fresh in-memory PGlite
.venv/bin/python scripts/run.py test --pytest-path qualification/test_<area>.py   # one file
```

## Changing things

Summary in AGENTS.md; step-by-step in [the engineering brief §8](docs/current/ENGINEERING-BRIEF.md). Whatever you change, update the documents together (release note, `docs/IMPLEMENTATION.md`, `docs/QUALIFICATION.md`, `docs/NEXT-DELIVERY.md`, the changelog, the traceability files and the ledger) and promote no requirement without source and test evidence.

## Working with the owner

The owner is a non-engineer who decides product scope and approves merges. Plain language, short direct answers, uncomfortable facts first, explicit confidence. Confirm before merging, deploying or spending money (CI minutes, cloud resources, paid services). Details in AGENTS.md.
