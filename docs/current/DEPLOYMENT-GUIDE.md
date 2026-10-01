# Deployment guide — staging server

Build 0.17 deployment package (v0.17). This guide explains, in plain language, what runs on the staging server, how a change reaches it, how to check it from outside, how the owner signs in for the first time, how backups work and what is not yet in place. The technical reference for each component is in `deploy/` and in the [operations guide](OPERATIONS-GUIDE.md).

Status: **staging only**. Nothing here makes the platform ready for real personal data or production use, and no release is accepted by deploying it.

## 1. What runs where

One DigitalOcean droplet in Bangalore (Ubuntu 24.04, 2 vCPU, 4 GB memory, 2 GB swap, public IPv4 168.144.78.191) runs everything with Docker Compose (`deploy/compose.yaml`, project name `impact`):

| Service | What it is | Reachable from |
|---|---|---|
| `caddy` | Web entry point. Obtains and renews free TLS certificates from Let's Encrypt, redirects HTTP to HTTPS, forwards requests. The only service with open ports (80 and 443). | The internet |
| `api` | The Impact Platform application (API plus the web client), running as `staging` on three separate database logins with no special privileges. | Caddy only |
| `worker` | Delivers in-app notices and email intents. | Nothing (it calls out only) |
| `mailsink` | Captures the worker's email on the server instead of sending it (there is no email provider yet). | The worker only |
| `keycloak` | The sign-in service (Keycloak 26.7.4, production mode, its own database). Passwords and authenticator apps live here. | Caddy (sign-in pages); its administration console is **not** published |
| `postgres` | PostgreSQL 17: the application database `impact` and Keycloak's database `keycloak`. | Other services only, on a network with no route out |
| `backup` | Nightly backup sets: both databases, the database roles and the evidence files, checked after writing (section 6). | Nothing |
| `drill-db`, `drill-check` | Exist only while the weekly restore drill runs (section 6), then are removed. They see the backups read-only and nothing of the live database. | Nothing |

Addresses (no domain was bought; sslip.io turns the IP address in the name into the address itself):

- Application: **https://168-144-78-191.sslip.io/**
- Sign-in service: **https://auth.168-144-78-191.sslip.io/** (realm `impact`)
- Deployment status: **https://168-144-78-191.sslip.io/deploy-status.json**

The names are derived from the droplet's public IP (DigitalOcean metadata). To use a real domain later, point its DNS at the droplet and put `IMPACT_APP_HOST=` and, if wanted, `IMPACT_AUTH_HOST=` in `/opt/impact/config.env` (section 8); the next deployment re-aligns the sign-in client to the new address.

Cost: **US$31.20 per month** — the US$24 droplet plus US$7.20 for DigitalOcean's daily backups. Let's Encrypt, sslip.io and all software used are free.

## 2. How a change reaches the server

The server pulls; nobody pushes to it and there is no SSH access from outside.

1. A change is merged into `main` on GitHub.
2. Every 3 minutes a timer on the server runs `/usr/local/bin/impact-sync`, which fetches the repository with a read-only key into `/opt/impact/repo`, resets it to `origin/main` when `main` has changed, and runs `deploy/update.sh` as root, logging to `/var/log/impact-deploy.log`.
3. `deploy/update.sh` then, every time and without harm when repeated:
   - stops the temporary first-boot key service that held port 80;
   - creates `/opt/impact/secrets.env` on the first run only (random database, Keycloak and application secrets, mode 0600; values are never printed or logged);
   - works out the host names and writes the Compose environment file;
   - builds the application image once per commit (`impact-platform:<first 12 characters of the commit>`), on the server — no image registry is used;
   - starts PostgreSQL, provisions the five database logins (each limited to one role, public connect revoked) and Keycloak's own login and database, and applies the database migrations — never test fixtures;
   - starts Caddy and every other service, waits for Keycloak, imports the sign-in realm if it does not exist yet (an existing realm and its users are never overwritten; only the web client's addresses are re-aligned), creates the owner's sign-in account if it does not exist, and makes that account the first platform operator (section 4);
   - waits for every service to be healthy, removes old images (keeping the last three) and writes the status file.

A typical deployment takes a few minutes; the first one takes longer (image build, certificates, Keycloak's first start). A commit that is already deployed and healthy is left alone (the run only refreshes the status file).

## 3. Checking a deployment from outside

Open **https://168-144-78-191.sslip.io/deploy-status.json**. It shows:

- `result` — `ok` or `failed`; `step` — the last step reached (on failure, where it stopped);
- `commit` — the deployed commit, with start and finish times;
- `services` — each container's state and health;
- `schema_version`, `first_operator` (`created`, `already-bootstrapped` or `refused`);
- `alerts` — problems the server's own check found in the last 5 minutes (section 6.4); an empty list means none;
- `operations` — the figures behind the alerts: newest backup and its age, last restore drill, free disk space, containers, workers, failed deliveries and waiting jobs;
- `log_tail` — the last 40 lines of the run, with every stored secret value replaced by `[redacted]`.

If the HTTPS address does not open at all (for example because the certificate could not be obtained), the same file is also served over plain HTTP at http://168-144-78-191.sslip.io/deploy-status.json; everything else on plain HTTP redirects to HTTPS. It never contains a password or secret. For a fuller check from any computer with the repository:

```
.venv/bin/python scripts/smoke.py https://168-144-78-191.sslip.io
```

This verifies the certificate, the HTTP→HTTPS redirect, `/health/ready` (database logins and schema), the security headers, the web client, that development sign-in is off, that `/auth/login` sends the browser to the realm with S256 PKCE and the MFA assurance class, the realm's discovery document and login page, that Keycloak's administration console is not published, and the status file. It prints a JSON report and exits 1 if anything fails.

## 4. First administrator (the owner)

The deployment creates one sign-in account, for **nakul.jain@aplyd.com**, with a random one-time password, and registers it as the first **platform operator** (the person who can request tenants, activate them after review and see the Workers panel). The one-time password is stored only on the server; it is never shown on a web page or in a log. There is no email provider yet, so "Forgot password" is switched off; the DigitalOcean console is the recovery path.

Steps for the owner, once `deploy-status.json` shows `"result": "ok"`:

1. Sign in to the DigitalOcean control panel, open the droplet, choose **Access → Launch Droplet Console** (the browser console; it signs you in as root, no key needed).
2. Type: `sudo /opt/impact/repo/deploy/first-admin.sh` and press Enter.
3. It prints a box with the application address, the username (your email address) and the one-time password. Keep the console open.
4. On your own computer open **https://168-144-78-191.sslip.io/**, choose **Sign in**, enter the email address and the one-time password.
5. Keycloak asks you to set up an authenticator app: scan the QR code with Google Authenticator, Microsoft Authenticator or a similar app and type the 6-digit code. It then asks for a new password (at least 6 characters on this test server, not your email address).
6. You are returned to the platform, signed in with two-factor assurance, and you see **Tenant lifecycle** as the platform operator. Close the console.

Running `first-admin.sh` again after step 5 shows nothing (the one-time password is no longer valid). If you forget your password: `sudo /opt/impact/repo/deploy/first-admin.sh --reset` issues a new one-time password; if you lose the authenticator app: `--reset-totp` (also removes the enrolled app, so you enrol again). Five wrong passwords in a row lock the account for a while (brute-force protection), increasing up to 15 minutes.

What the owner cannot do alone — by design. The platform's rules require different people for the steps of creating a working tenant (organisation workspace):

- a platform operator **requests** a tenant and names its **owner**, who must be a different person;
- the named owner **accepts** custody;
- the owner nominates a **recovery contact**, who consents, and a platform operator who is neither requester nor owner approves it;
- a platform operator who is **neither the requester nor the owner activates** the tenant.

So a first tenant needs at least three people (for example: you as requesting operator, a colleague as tenant owner, and a second operator to activate and approve), plus a recovery contact. The deployment makes only you an operator. To give others a sign-in, run in the console, once per person:

```
sudo /opt/impact/repo/deploy/add-user.sh colleague@example.org "First" "Last"
```

It creates their sign-in account with a one-time password (shown once in the console, not stored; hand it over yourself) and registers them as a platform identity with no authority. They must sign in once (setting their password and authenticator) before they can be named as a tenant owner, because the platform learns their verified email address at sign-in.

**Everyday tasks for the owner.** All of them are typed into the DigitalOcean browser console (droplet → **Access → Launch Droplet Console**), one line each, then Enter. Nothing here needs a password of your own; the console already runs as the server's administrator. A one-time password is shown only on your screen: it is never written to a log, a file or the status page, so copy it before you close the console and give it to the person yourself.

| You want to… | Type this | What you see |
|---|---|---|
| See who has a sign-in | `sudo /opt/impact/repo/deploy/list-users.sh` | A list: e-mail, name, and whether each person has signed in yet, set up an authenticator app, or is locked out |
| Give someone a sign-in | `sudo /opt/impact/repo/deploy/add-user.sh name@example.org "First" "Last"` | Their one-time password, in a box |
| Help someone who forgot their password (or is locked out after wrong passwords) | `sudo /opt/impact/repo/deploy/reset-user.sh name@example.org` | A new one-time password, in a box; the lock is lifted |
| Help someone who lost their phone with the authenticator app | `sudo /opt/impact/repo/deploy/reset-user.sh name@example.org --totp` | As above; they set up the app again at their next sign-in |
| Your own password or app | `sudo /opt/impact/repo/deploy/first-admin.sh --reset` (or `--reset-totp`) | Your address, username and a new one-time password, in a box |
| Check the server is healthy | open https://168-144-78-191.sslip.io/deploy-status.json in a browser | `"result": "ok"` and `"alerts": []` when all is well (section 6.4) |

Every add and reset is recorded (who, when, never the password) in `/opt/impact/state/admin-actions.log`. A **second platform operator** cannot be created by the scripts (the first-operator bootstrap refuses once any operator exists, and there is no operator-management screen yet); adding one is a deliberate database change by the owner and is not automated in this build.

The tenant request form in **Tenant lifecycle** offers the server's deployment qualification: region `do-blr1`, privacy reference `staging-privacy-notice-v1` (a placeholder until a real privacy notice exists), retention up to 3,650 days, valid for one year. The operator authority and the qualification both expire after 365 days and must then be renewed by a deliberate database change; nothing renews them automatically.

## 5. Email

No email provider has been chosen. The worker speaks SMTP to a small capture service on the same server (`mailsink`), which writes each message to `/var/lib/impact/mail/captured.jsonl` in the `mail` volume and sends nothing. Invitations and recovery-contact codes therefore do not reach anyone by email; in-app notices work. To see captured mail: `sudo docker compose -p impact -f /opt/impact/repo/deploy/compose.yaml --env-file /opt/impact/compose.env exec mailsink tail /var/lib/impact/mail/captured.jsonl`.

When a provider is chosen, add to `/opt/impact/config.env`: `SMTP_HOST=`, `SMTP_PORT=` (587), `SMTP_USERNAME=`, `SMTP_PASSWORD=`, `SMTP_FROM=`; the next deployment points the worker at it (STARTTLS with certificate verification is enforced for any non-local host). The worker container then also needs a route out; that change, bounce handling, SPF/DKIM and sending limits are part of choosing the provider and have not been tested.

## 6. Backups, restore drill, recovery objectives and alerts

### 6.1 What is backed up, and where

Two layers:

- **Nightly backup sets on the server** by the `backup` service, at 21:00 UTC (02:30 IST; `BACKUP_HOUR_UTC` in `config.env` moves it). One set is everything a restore needs:
  - `impact.dump` and `keycloak.dump` — the application database and the sign-in service's database (`pg_dump -Fc`);
  - `globals.sql` — the database roles and their memberships (without passwords), which a restore onto a fresh database server needs before the dumps;
  - `objects.tar` — every evidence file in the `objects` volume, taken *after* the dumps, so every file the database refers to is in it;
  - `SHA256SUMS` and `manifest.json` — size and SHA-256 of each file, schema version, deployed commit, number of evidence files.

  A set is built in a hidden folder and checked before it counts: each dump is read back (`pg_restore --list`), the tar is read to its end and every checksum is compared. Only then is it renamed into `/backups/daily/YYYYMMDD/`. Sunday's set is also kept as `/backups/weekly/YYYYMMDD/` (hard links: no second copy on disk). The last 7 daily and 4 weekly sets are kept. A failed attempt leaves the earlier sets untouched. **Disk guard:** an attempt is refused, and an alert raised, when the backup disk has less free space than twice the newest set (never less than 1 GB; `BACKUP_MIN_FREE_MB` in `config.env` changes the floor). One set is also taken when the service starts on a server that has none for today.
- **DigitalOcean droplet backups** of the whole server (enabled by the owner; kept by DigitalOcean off the server, daily or weekly as chosen in the control panel, and taken at a time DigitalOcean picks). This is the **only copy that survives the loss of the droplet**.

Each attempt writes `/opt/impact/ops/backup-status.json` (result, reason, sizes, free space, the last successful set); its figures appear in `deploy-status.json` under `operations.backup`.

List sets, take one now (for example before a risky change):

```
cd /opt/impact/repo/deploy
C="sudo docker compose -p impact -f compose.yaml --env-file /opt/impact/compose.env"
$C exec backup ls -l /backups/daily /backups/weekly
$C exec backup /bin/bash /opt/backup/backup.sh --now
```

### 6.2 The weekly restore drill

Every Sunday at about 23:15 UTC, a timer on the server (`impact-restore-drill.timer`, installed by the deployment) runs `deploy/restore-drill.sh`. It starts a **throwaway** PostgreSQL in its own container, on its own network, which can read the backup sets but cannot see the live database at all; restores the newest set into it (checksums, roles, both dumps); and then checks, from the application image (`deploy/restore_check.py`): every evidence file in the tar still hashes to its name; every evidence record in the restored database has its file, with the recorded hash and size; the migration runner, as the restricted migration login, finds every recorded migration checksum equal to this build's files and reaches this build's schema; every table is owned by `impact_owner`; every table that forces row-level security has its policies; the application role sees no rows without a tenant; the sign-in database holds the `impact` realm. The containers and their data are deleted afterwards. To run it by hand: `sudo /opt/impact/repo/deploy/restore-drill.sh` (or name a set: `… restore-drill.sh weekly/20261004`).

The result is kept in `/opt/impact/ops/restore-drill.json` and shown in `deploy-status.json` under `operations.restore_drill`: outcome, the set restored, how old that set was, and how long the whole drill took.

### 6.3 Recovery point and recovery time — honestly

| Situation | What is restored | Data lost (recovery point) | Time to restore (recovery time) |
|---|---|---|---|
| Data damaged or deleted by mistake; server intact | The newest nightly set (section 6.5) | Everything since the last nightly set: **up to 24 hours**, longer if nightly runs had been failing unnoticed (the `BACKUP_FAILED` / `BACKUP_STALE` alerts exist to keep that window short) | The drill measures the database part on this server: **RESTORE_TIME_PLACEHOLDER** for the current, small databases (see `operations.restore_drill.duration_seconds`; it grows with the data). Add the swap-in and redeploy (minutes) and the time for someone to notice and act. |
| The droplet is lost or unusable | DigitalOcean's last droplet backup (control panel → Backups → Restore) | Everything since that droplet backup: **up to the interval of those backups** (a day if daily, a week if weekly, plus however late DigitalOcean takes them). The nightly sets are lost with the droplet. | DigitalOcean's restore time (not measured here) plus a deployment run. |

No objective has been agreed; these are what the current set-up can deliver, measured only at today's small size. **Off-server copies of the nightly sets** (so that losing the droplet costs at most a day) need a storage provider outside the droplet, for example a DigitalOcean Spaces bucket (a paid add-on). That is an owner decision and has not been taken; nothing in this package sends data off the server.

### 6.4 Alerts on the status page

Every 5 minutes a timer (`impact-ops-check.timer`) runs `deploy/ops-check.sh`, which looks at the backups, the last drill, free disk space, the containers and, inside the application, the workers' heartbeats, failed (DEAD) deliveries and waiting jobs. It writes what it finds into `deploy-status.json` as `alerts` (and `/opt/impact/ops/ops-status.json`). Nothing is sent anywhere — there is no paid monitoring service — so **someone has to look**: open the status page now and then; an empty `alerts` list means nothing was found.

| Alert | Means | What to do |
|---|---|---|
| `BACKUP_MISSING`, `BACKUP_STALE`, `BACKUP_FAILED` | No good backup set in the last 26 hours, or the last attempt failed | Take one now (6.1); if it fails again, look at `$C logs backup` |
| `BACKUP_REFUSED_DISK_LOW`, `DISK_LOW` | The disk is nearly full | Remove old images (`sudo docker image prune -a` keeps running ones) or resize the droplet |
| `CONTAINER_UNHEALTHY` | A part of the stack is stopped or unhealthy | Usually fixed by the next deployment run within 3 minutes; else `sudo /opt/impact/repo/deploy/update.sh` |
| `WORKER_STALE` | No delivery worker is running | As above |
| `DELIVERIES_DEAD` | Some in-app notices or e-mails failed for good | A platform operator re-queues them in **Tenant lifecycle → Workers** |
| `QUEUE_BACKLOG`, `SCHEMA_MISMATCH`, `OPS_SUMMARY_UNAVAILABLE` | Work is piling up, the database and the application disagree, or the application could not be asked | Look at the deployment log tail on the status page |
| `RESTORE_DRILL_FAILED`, `RESTORE_DRILL_STALE` | The weekly drill failed, or has not run for 8 days | Run it by hand (6.2) and read `/var/log/impact-restore-drill.log` |

Platform operators can read the same figures, plus request counts and response times of the running application, at `GET /v1/platform/metrics` (operators only; everyone else gets "not found"). It holds counts only — no tenant names, identifiers or personal data.

Logs: every container keeps at most 5 files of 10 MB; the server's own logs (`/var/log/impact-deploy.log`, `impact-ops.log`, `impact-restore-drill.log`) rotate weekly (8 kept, compressed, sooner above 20 MB), and `admin-actions.log` monthly (2 years kept).

### 6.5 Restoring live data from a set (by hand)

This replaces the live data; stop the application first, and run the drill on the set first if it is older than a week:

```
cd /opt/impact/repo/deploy
C="sudo docker compose -p impact -f compose.yaml --env-file /opt/impact/compose.env"
S=daily/YYYYMMDD
$C stop api worker
$C exec backup bash -c "cd /backups/$S && sha256sum --check SHA256SUMS && dropdb --if-exists impact_restore && createdb impact_restore && pg_restore --exit-on-error -d impact_restore impact.dump"
# check impact_restore, then swap it in:
$C exec backup psql -d postgres -c 'ALTER DATABASE impact RENAME TO impact_old' -c 'ALTER DATABASE impact_restore RENAME TO impact'
# evidence files: unpack the set's tar over the volume (files are named by their hash, so nothing is overwritten with other content)
$C run --rm --no-deps -u 0 --entrypoint tar -v impact_backups:/backups:ro api -xf /backups/$S/objects.tar -C /var/lib/impact/objects
sudo /opt/impact/repo/deploy/update.sh    # re-grants the logins on the restored database and restarts everything
```

On a brand-new database server, apply `globals.sql` (`psql -d postgres -f globals.sql`) before the dumps, then let `update.sh` set the passwords. The sign-in database is restored the same way from `keycloak.dump`. CI (`container-stack`) takes a set on every run, restores it, runs the restore drill and the alert check on its own stack; a restore of the live server's data has not been needed or rehearsed beyond the weekly drill.

## 7. Rolling back

Revert the change on `main` (for example with GitHub's **Revert** button on the merged pull request). Within about 3 minutes the server resets to the new `main` and redeploys; the image of a recent commit is still on the server and is rebuilt otherwise. Database migrations are never undone: a rollback past a migration keeps the newer schema, and the older application refuses to report ready if the schema number differs (`/health/ready` 503), which shows in the status file. If that happens, roll forward with a fix instead.

## 8. Configuration overrides

`/opt/impact/config.env` (optional, root only, `KEY=value` lines) is read on every deployment:

| Key | Default | Meaning |
|---|---|---|
| `IMPACT_APP_HOST` | `<ip with dashes>.sslip.io` | Application host name |
| `IMPACT_AUTH_HOST` | `auth.<app host>` | Sign-in host name |
| `IMPACT_OWNER_EMAIL`, `IMPACT_OWNER_FIRST_NAME`, `IMPACT_OWNER_LAST_NAME` | nakul.jain@aplyd.com, Nakul, Jain | The first operator's sign-in account |
| `ACME_EMAIL` | the owner's email | Contact address for Let's Encrypt |
| `CADDY_TLS_MODE` | `acme` | `internal` uses Caddy's own certificate authority (CI only) |
| `IMPACT_REGION`, `IMPACT_PRIVACY_REFERENCE`, `IMPACT_RECOVERY_REFERENCE` | `do-blr1`, `staging-privacy-notice-v1`, droplet backups | The deployment qualification the bootstrap records (only when it creates one) |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM` | loopback capture | Email provider (section 5) |
| `BACKUP_HOUR_UTC` | 21 | Hour of the nightly dump |

Server files: `/opt/impact/secrets.env` (generated secrets, never edit casually: changing a database password is applied on the next run; rotate the cookie, invitation and delivery secrets only with `deploy/rotate-secrets.sh` (section 10), which keeps the old value in grace — editing them by hand invalidates outstanding CSRF tokens, cursors, invitation emails and codes at once), `/opt/impact/secrets.env.keys.json` (key ids and rotation events, no values), `/opt/impact/compose.env` (generated each run), `/opt/impact/status.json`, `/opt/impact/state/` (last successful commit, run log, admin actions), `/opt/impact/ca/` (CI only).

## 9. Known limits

- **One server.** Database, sign-in service and application share one 4 GB droplet; a failure of the droplet stops everything. No load test has been run; the sizing is a guess for a handful of users.
- **Backups:** the nightly sets (databases, roles, evidence files) sit on the same server; DigitalOcean's droplet backups are the only off-server copy, so losing the droplet loses everything since the last droplet backup (up to a day or a week, by the plan chosen) (section 6.3). Off-server copies of the nightly sets need an owner decision on a storage provider. The weekly restore drill runs on the same server into throwaway containers; a restore onto a different server has not been rehearsed.
- **No email** (section 5), so invitation and recovery-contact emails are captured, not delivered; "Forgot password" is off.
- **sslip.io host names** depend on a free third-party DNS service; if it is unavailable, the site cannot be reached by name. Let's Encrypt rate limits apply to the shared sslip.io domain.
- **Staging only**: synthetic or test data only, no real personal data (repository rule 11), no penetration test. Alerts are written to the status page only (section 6.4): nobody is paged or e-mailed, metrics are kept in memory by the running application and reset when it restarts, there is no history or dashboard, and logs stay on the server (10 MB × 5 per container; host logs rotated).
- **Sign-in:** self-hosted Keycloak on the same server; no refresh tokens are issued (as qualified in v0.15; for the owner to accept); key rotation, provider outage and account recovery beyond the console reset have not been exercised. The Keycloak administration console is reachable only from inside the server.
- **Operators:** only the first operator is created automatically; a second operator, operator renewal and qualification renewal are manual database changes.
- The image base versions (`python:3.12-slim-bookworm`, `node:24-bookworm-slim`, `postgres:17`, `caddy:2`) follow their tags and are refreshed at each build; Keycloak is pinned to 26.7.4; Python packages are pinned by SHA-256.

## 10. Rotating the application secrets

The API's cookie secret (CSRF tokens, list cursors, sealed logout hints, the audit-export seal), the invitation signing secret and the delivery secret (sealed recipient addresses, recovery codes) are versioned keyrings: one current secret plus grace secrets in `IMPACT_<FAMILY>_SECRET_PREVIOUS`. A rotation makes a new current secret and keeps the old one in grace, so sessions, open tabs, invitation emails and codes issued before it keep working; retiring the old secret later ends that. What each secret protects, what is and is not encrypted, and the effect of retiring early: `docs/current/KEY-AND-ENCRYPTION-REGISTER.md`.

Run in the droplet console as root (no value is ever printed; the output names key ids):

```
sudo /opt/impact/repo/deploy/rotate-secrets.sh status
sudo /opt/impact/repo/deploy/rotate-secrets.sh rotate --family all --reason "scheduled rotation" --dry-run
sudo /opt/impact/repo/deploy/rotate-secrets.sh rotate --family all --reason "scheduled rotation"
# after the grace window (cookie 1 day, invitation and delivery 8 days by default; --grace-days N):
sudo /opt/impact/repo/deploy/rotate-secrets.sh retire --family all --expired --reason "grace ended"
```

`--family` is `cookie`, `invitation`, `delivery` or `all`; `retire` takes `--expired` (only keys whose recorded grace has ended), `--kid <kid>` or `--all-previous` (immediately; use after a suspected compromise, accepting the effects listed in the register). The script holds the deployment lock (an automatic update cannot interleave), rewrites `/opt/impact/secrets.env` and `/opt/impact/compose.env` atomically (mode 0600), appends the event to `/opt/impact/secrets.env.keys.json`, then recreates the `api` container (and the `worker` when the invitation or delivery family changed) and waits for them to be healthy. A recreate is a few seconds of unavailability on this single server; no session is lost. If a container does not come back, the previous secret is still in grace: fix the cause and run `deploy/update.sh`, or retire nothing until it is healthy.

The CI job `container-stack` rotates every family, runs the smoke check, retires every grace key, runs the smoke check again and verifies that no secret value appeared in any output.

Not covered: the identity provider's token-signing keys (rotate them in Keycloak: add a new `rsa-generated` key provider with a higher priority, keep the old one active until issued tokens expire, then disable it — the API verifies bearer tokens by `kid` through the realm JWKS without a restart; not yet exercised), database login passwords (edit `secrets.env` and run `update.sh`; no grace) and TLS certificates (Caddy renews them).

