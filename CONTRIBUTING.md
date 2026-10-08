# Contributing

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: a change to AGENTS.md rules, CI triggers or the branch model.

The binding rules are in [AGENTS.md](AGENTS.md) (short) and [CLAUDE.md](CLAUDE.md) (the full engineering brief, model-agnostic). This file only points to them and states the minimum.

## Ground rules

1. **`main` deploys itself.** The staging server pulls `main` every 3 minutes and applies migrations. Never push to `main`. Work on a branch (`release/…`, `qa/…`, `ux/…`, `docs/<yyyy-mm>-<topic>`), open a **draft** pull request, and do not merge without all four CI jobs green and the owner's confirmation.
2. **Cost and irreversibility need the owner.** CI minutes, cloud spend, merges, deployments and deletions are the owner's call.
3. **Synthetic data only.** Never commit credentials, keys, `.local/`, `secrets.env` or real personal data.
4. **Migrations 0001 to 0040 are frozen**; the next is 0041, additive, with forced row-level security on every tenant table.
5. **Do not weaken tests, independence rules or deny-by-default** to get a green result.
6. Keep "current implementation" and "target design" separate in every document; move a requirement's status only with named passing tests.

## Set up and check

`make setup`, `make dev`, `make lint`, `make unit`, `make test` (see AGENTS.md "Set up, run and test" for ports, native PostgreSQL and browser groups). Documentation-only changes (under `docs/` or any `*.md`) start no CI.

## Design changes

Anything that changes behaviour, a contract, a data model or a security property goes through the design-note and decision-record route in [docs/governance/README.md](docs/governance/README.md) (row 8 and 9) before code.

## Pull requests

Use the template in `.github/PULL_REQUEST_TEMPLATE.md`. List the exact checks you ran and the ones you did not.

## Reporting a security problem

Do not use issues. See [SECURITY.md](SECURITY.md).
