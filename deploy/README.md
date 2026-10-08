# deploy/: the staging server package

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: any change to `deploy/compose.yaml`, `deploy/update.sh`, a timer, or the server layout.

This directory turns one DigitalOcean droplet into the Impact Platform **staging** server. It is staging only: synthetic data, not production, not accepted (see [HANDOVER](../docs/HANDOVER.md)). The full narrative, click-paths and limits are in [DEPLOYMENT-GUIDE.md](../docs/current/DEPLOYMENT-GUIDE.md); this file is the map of the scripts. No credential appears here or may be added.

## Scope: which droplet

- The Impact staging droplet (Bangalore; address and host names are in DEPLOYMENT-GUIDE section 1) runs everything in this directory with Docker Compose, project name `impact`.
- Per the owner, the Saha apps (health, agriculture, education, and the other Products-project apps) run on a **separate, shared droplet**. That droplet does **not** run Impact, and nothing here deploys to it. Its hosting rule lives in the owner's Products project, not in this repository.

## How a change arrives

A timer on the server (`/usr/local/bin/impact-sync`, every 3 minutes) resets `/opt/impact/repo` to `origin/main` and runs `update.sh` as root. Nobody pushes to the server; there is no inbound SSH from outside. Therefore **a merge into `main` is a deployment** (AGENTS.md safety rules). Migrations are applied by the `migrate` job; fixtures are never loaded.

## Files

| File | Purpose |
|---|---|
| `compose.yaml` | Services: `postgres`, `migrate`, `operator-bootstrap`, `idp-admin`, `keycloak`, `api`, `mailsink`, `worker`, `executor` (asynchronous import commits, backend network only), `caddy`, `backup`, and the profile `drill` (`drill-db`, `drill-check`). Secrets come from `${...}` interpolation of the server's env files; the file holds none. |
| `Dockerfile`, `requirements.runtime.txt`, `hash_requirements.py` | Image build; Python packages installed with `pip --require-hashes` from the hash file generated from `requirements.lock`. |
| `update.sh`, `lib.sh` | Idempotent deployment: generate secrets once, derive host names, build the image per commit, provision logins, migrate, start services, import the realm if absent, create the owner account and first operator if absent, health-wait, write `deploy-status.json`. Never prints a secret. |
| `prepare_database.py` | Provisions the database logins (one role each, public connect revoked) and Keycloak's database. |
| `keycloak/realm-staging.json`, `keycloak_admin.py` | Realm import and admin-API helper (owner account, provisioner client). |
| `caddy/Caddyfile` | TLS (Let's Encrypt) and routing; only ports 80 and 443 are public. |
| `backup.sh` | Nightly verified backup set (both databases, roles, evidence volume). See [BACKUP-DR](../docs/governance/BACKUP-DR.md). |
| `restore-drill.sh`, `drill_restore.sh`, `restore_check.py` | Weekly drill into throwaway containers; writes `restore-drill.json`. |
| `ops-check.sh`, `ops_alerts.py`, `on-call.example.json` | Five-minute alert check, closed alert codes, optional webhook or e-mail delivery, on-call rota template. See [SLOS-AND-ALERTS](../docs/governance/SLOS-AND-ALERTS.md). |
| `readiness-exercise.sh` | Rehearses alert, delivery and clearance. |
| `rotate-secrets.sh` | Rotate or retire application secrets without printing a value. See [SECRETS-REGISTER](../docs/governance/SECRETS-REGISTER.md). |
| `first-admin.sh`, `add-user.sh`, `list-users.sh`, `reset-user.sh` | Owner console scripts, run in the DigitalOcean droplet console as root; they refuse to print passwords into a pipe. |
| `mail-check.sh`, `mail_check.py`, `mail_sink.py` | Test one SMTP provider; the loopback capture used while no provider is configured. |

## Server layout (default `IMPACT_HOME=/opt/impact`)

`repo/` (the checkout), `secrets.env` (0600, generated once), `config.env` (optional overrides), `compose.env`, `public/deploy-status.json` (served at `/deploy-status.json`, secrets scrubbed), `state/`, `ops/` (`ops-status.json`, `restore-drill.json`, alert state), `ca/`. Logs: `/var/log/impact-deploy.log`, `impact-ops.log`, `impact-restore-drill.log`.

## Configuration

Names are listed in [`docs/governance/env.example`](../docs/governance/env.example); the server-side overrides table is DEPLOYMENT-GUIDE section 8. Values live only on the server.

## Routine operations (in the droplet console, as root)

```
sudo /opt/impact/repo/deploy/update.sh                 # force a deployment run now
sudo /opt/impact/repo/deploy/ops-check.sh              # refresh alerts
sudo /opt/impact/repo/deploy/restore-drill.sh          # run the drill by hand
sudo /opt/impact/repo/deploy/rotate-secrets.sh status  # key ids and grace dates, no values
```

Check health from outside: `deploy-status.json` (`result`, `commit`, `schema_version`, `alerts`). Roll back by reverting on `main`; migrations are never undone (DEPLOYMENT-GUIDE section 7).

## Verified by

CI job `container-stack` (`.github/workflows/qualification.yml`) runs this package with fake host names and `CADDY_TLS_MODE=internal`. Docker images cannot be pulled from the development sandbox, so changes here are rehearsed only by that job. Whether the live server currently matches `main` has not been independently checked in this workspace: TBD (owner: Nakul Jain).
