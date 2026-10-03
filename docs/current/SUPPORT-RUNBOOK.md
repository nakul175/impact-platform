# Support runbook — staging server

Build 0.27.0, prepared 1 October 2026 and updated 3 October 2026. This runbook says who does what when something goes wrong on the staging server (https://168-144-78-191.sslip.io), how to check health, and the first steps for the incidents seen so far or designed for. It is the support-readiness record behind VF-SUP-001, which stays **PENDING**: an on-call rota format and a scripted readiness exercise exist since build 0.27.0, but no named people, published support hours, response targets or rehearsal on the real server exist yet (§8). Technical detail lives in the [deployment guide](DEPLOYMENT-GUIDE.md) (server, backups, alerts, rotation), the [operations guide](OPERATIONS-GUIDE.md) (configuration, worker, delivery inspection) and the [key and encryption register](KEY-AND-ENCRYPTION-REGISTER.md).

Staging holds synthetic or test data only. Nothing here makes it a production service.

## 1. Who does what

| Role | Person today | Does | Never does |
|---|---|---|---|
| **Server owner** | The deployment owner (first platform operator; `IMPACT_OWNER_EMAIL`) | Everything in the droplet console as root: account resets, restore drill, secret rotation, manual restore, reading server logs; merges fixes to `main` | Shares a one-time password, secret or console session in writing |
| **Platform operator** | Today the same person; a second operator is nominated and accepts in the web application (since build 0.26.0); another operator renews or deactivates one (since build 0.27.0) | Tenant lifecycle, recovery-contact approval, Workers panel, re-queue or release of deliveries, `GET /v1/platform/metrics` | Reads tenant data: operator status grants no data access |
| **Tenant owner / tenant administrator** | Named per tenant at onboarding | Members, invitations, access requests, suspension and revocation inside their tenant; audit export (where granted) | Reset sign-in accounts (only the server owner can) |
| **Engineer on call** | **Not assigned** — once named, in `/opt/impact/ops/on-call.json` (copy `deploy/on-call.example.json`); operators read it in Tenant lifecycle → Workers and in the service-notice details | Diagnoses failed deployments, application errors (correlation IDs), alert codes that need code or database work | — |
| **Privacy contact** | **Not assigned** | Data-subject requests, suspected personal-data exposure | — |

The accountable people for the empty rows, their contact routes and their hours are owner decisions (§8). Until they are named, the server owner is the only escalation point.

## 2. Checking health

1. Open **https://168-144-78-191.sslip.io/deploy-status.json** (if HTTPS fails, the same file is served at `http://168-144-78-191.sslip.io/deploy-status.json`). Healthy means `"result": "ok"` and `"alerts": []`. `operations` shows the figures behind the alerts: newest backup set and its age, last restore drill (outcome, set, duration), free disk, containers, worker heartbeats, DEAD deliveries and waiting jobs. `log_tail` is the end of the last deployment run with stored secrets replaced by `[redacted]`.
2. Alerts are recalculated every 5 minutes by `impact-ops-check.timer` (`deploy/ops-check.sh`), after each deployment and after each drill. Since build 0.27.0 they are also delivered (NEW, CLEARED, a reminder every 6 hours) to the webhook and e-mail address set in `config.env` (`ALERT_WEBHOOK_URL`, `ALERT_WEBHOOK_SECRET`, `ALERT_EMAIL_TO`); the delivery state is `/opt/impact/ops/alert-state.json`. Without those settings nothing is sent: someone has to look. Every signed-in user sees a service-notice banner for worker, storage, e-mail and upgrade problems. A `checked_at` that stops moving means the check itself is not running (see `/var/log/impact-ops.log`).
3. From any computer with the repository: `.venv/bin/python scripts/smoke.py https://168-144-78-191.sslip.io` checks TLS, the HTTP→HTTPS redirect, `/health/ready`, security headers, sign-in redirection with PKCE and the MFA class, the realm and the status file, and prints the alert codes.
4. Platform operators can read the same figures plus request counts and latency at `GET /v1/platform/metrics` (operators only; everyone else gets "not found"). Counters reset when the API restarts.
5. Force a check now (console): `sudo /opt/impact/repo/deploy/ops-check.sh`.

### Alert codes

The closed set evaluated by `deploy/ops_alerts.py`:

| Code | Severity | Means | First step |
|---|---|---|---|
| `BACKUP_MISSING` | critical | No verified backup set exists yet | Take one now (§4.5) |
| `BACKUP_STALE` | critical | Newest verified set older than 26 hours | Take one now; read the backup log (§4.5) |
| `BACKUP_FAILED` | critical | Last backup attempt failed (the failing step is in the message) | §4.5 |
| `BACKUP_REFUSED_DISK_LOW` | critical | Last attempt refused: less free space than twice the newest set (floor 1 GB) | §4.4 |
| `DISK_LOW` | warning below 10 % or 2 GB free; critical below 5 % or 1 GB | `/` or Docker's data directory is filling | §4.4 |
| `CONTAINER_UNHEALTHY` | critical | One of postgres, keycloak, api, worker, mailsink, caddy, backup is absent, stopped or unhealthy | §4.2 |
| `WORKER_STALE` | critical | No running worker has reported within its window (120 s) | §4.2 |
| `DELIVERIES_DEAD` | warning | Some in-app notices or e-mails failed for good | §4.3 |
| `QUEUE_BACKLOG` | warning | More than 200 unsent deliveries or unfinished jobs | Check `WORKER_STALE` first; then the deployment log tail |
| `SCHEMA_MISMATCH` | critical | Database schema differs from the one the build expects | Usually a rollback past a migration: roll forward (deployment guide §7) |
| `OPS_SUMMARY_UNAVAILABLE` | warning | The API's operations summary could not be read | Check `CONTAINER_UNHEALTHY` for `api`; then §4.2 |
| `RESTORE_DRILL_FAILED` | critical | Last restore drill failed | §4.6 |
| `RESTORE_DRILL_STALE` | warning | No restore drill in the last 8 days | Run it by hand (§4.6) |

`QUEUE_BACKLOG` and DEAD counts cover tenants under control-plane custody only (at most 200; DEAD capped at 50).

## 3. Before you start any incident

- Write down: time (UTC), who reported it, what they were doing, the tenant's operating name (not the content of their data), and the **correlation ID** from the error message. The correlation ID is the key to every log line; it contains nothing personal.
- Note the deployed `commit` from the status page.
- Work in the DigitalOcean browser console (droplet → **Access → Launch Droplet Console**); there is no SSH from outside. Set a shorthand for Compose commands used below:

```
cd /opt/impact/repo/deploy
C="sudo docker compose -p impact -f compose.yaml --env-file /opt/impact/compose.env"
```

## 4. Common incidents and first steps

### 4.1 A user cannot sign in

| Symptom | First step |
|---|---|
| Forgot password, or locked after five wrong passwords | `sudo /opt/impact/repo/deploy/reset-user.sh name@example.org` — a new one-time password in a box (terminal only; pipes are refused), the lockout lifted. Hand the password over by phone or in person. |
| Lost the phone with the authenticator app | `sudo /opt/impact/repo/deploy/reset-user.sh name@example.org --totp` — they set up a new app at the next sign-in |
| The server owner's own account | `sudo /opt/impact/repo/deploy/first-admin.sh --reset` (or `--reset-totp`) |
| "Who has an account, who is locked?" | `sudo /opt/impact/repo/deploy/list-users.sh` |
| Signs in but sees no workspace or a missing action | Not a sign-in problem: membership, grant, scope, purpose or tenant state. The tenant administrator checks **People & access**; fresh sign-in is required for sensitive actions after five minutes |
| No account yet | `sudo /opt/impact/repo/deploy/add-user.sh name@example.org "First" "Last"`; they sign in once before they can be named in onboarding or invited |

Every add and reset is logged (who, when, never the password) in `/opt/impact/state/admin-actions.log`. Before resetting, confirm the requester's identity through a channel you already trust; there is no self-service recovery and "Forgot password" is off (no e-mail provider).

### 4.2 Worker stale or a container unhealthy

1. The deployment timer runs every 3 minutes and normally restores a stopped service; wait one cycle and reload the status page.
2. Still failing: `$C ps` to see states, `$C logs --tail 100 worker` (or `api`, `keycloak`, …). Logs carry error classes and correlation IDs, not secrets.
3. `sudo /opt/impact/repo/deploy/update.sh` re-runs the deployment by hand (idempotent; holds the deployment lock).
4. Operators can confirm worker heartbeats in **Tenant lifecycle → Workers** (the panel calls a worker stale after 60 s; the alert waits 120 s).

### 4.3 DEAD deliveries

Deliveries are in-app notices and e-mail intents. On staging, e-mail goes to the on-server capture (`mailsink`), never to a mailbox.

1. As a platform operator open **Tenant lifecycle → Workers → Deliveries needing attention**. Each row shows tenant, channel, template, state, attempts and last error class — never an address, link or code.
2. Choose **Re-queue** (DEAD → pending with a fresh attempt budget) or **Release hold** (a row held by a suspension), with a reason. Requires a sign-in within the last five minutes and an Active tenant. Each action is recorded as a platform event.
3. Do not re-queue blindly: `RECIPIENT_UNREADABLE` after a delivery-secret retirement will fail again (issue a new invitation instead, §4.7); an invitation that was reissued, revoked or expired is superseded by the worker, never sent.
4. Nothing is re-sent automatically after a suspension ends (by design).

### 4.4 Disk filling

1. `df -h /` in the console; the status page shows the same figures.
2. `sudo docker image prune -a` removes unused images (running ones are kept; the deployment keeps the last three).
3. Do not delete backup sets by hand; retention (7 daily, 4 weekly) prunes them. If the disk is genuinely too small, resize the droplet in the DigitalOcean panel (a cost decision for the owner).

### 4.5 Failed or stale backup

1. Read the reason: `operations.backup` on the status page, then `$C logs --tail 200 backup`.
2. Take a set now: `$C exec backup /bin/bash /opt/backup/backup.sh --now`; list sets with `$C exec backup ls -l /backups/daily /backups/weekly`.
3. A failed attempt leaves earlier sets untouched. If attempts keep failing, the last good set and DigitalOcean's droplet backup are the only copies; tell the owner the recovery point is growing.

### 4.6 Restore drill failed or stale

1. Run it by hand: `sudo /opt/impact/repo/deploy/restore-drill.sh` (or name a set: `… restore-drill.sh weekly/20261004`).
2. Read `/var/log/impact-restore-drill.log` and `operations.restore_drill` (error class, set, duration). The drill uses throwaway containers that cannot see the live database; a failed drill does not touch live data.
3. A drill that fails on a damaged set means that set must not be used for a restore; try the previous set and tell the owner.
4. Restoring live data is a separate, deliberate procedure (deployment guide §6.5): stop `api` and `worker`, restore into a side database, check, swap, unpack the evidence tar, run `update.sh`. After restoring a set older than a data-subject erasure, that erasure must be executed again by hand — no tool replays it.

### 4.7 Secret rotation and its grace window

Scheduled, or immediately after a suspected leak:

```
sudo /opt/impact/repo/deploy/rotate-secrets.sh status
sudo /opt/impact/repo/deploy/rotate-secrets.sh rotate --family all --reason "scheduled rotation" --dry-run
sudo /opt/impact/repo/deploy/rotate-secrets.sh rotate --family all --reason "scheduled rotation"
```

The old value stays in **grace**: the cookie secret 1 day, the invitation and delivery secrets 8 days by default (`--grace-days N`). Sessions, open tabs, invitation e-mails and recovery codes made before the rotation keep working during grace. After the window: `sudo /opt/impact/repo/deploy/rotate-secrets.sh retire --family all --expired --reason "grace ended"`. After a suspected compromise retire at once with `--all-previous`, accepting that queued e-mails sealed with the retired delivery secret become `DEAD RECIPIENT_UNREADABLE` and old invitation links stop working (issue new invitations). Output names key ids only; the API (and the worker for invitation/delivery) is recreated, a few seconds of unavailability. Not covered by the script: Keycloak token-signing keys, database passwords, TLS (deployment guide §10).

### 4.8a A member reports being refused, or a privacy case shows HELD

Since build 0.27.0 refusals are recorded. An owner or tenant administrator opens **People & access → Access denied** (or `GET /v1/tenants/{tenant}/access-denials`) and finds the member's row: `POLICY_DENIED` (missing capability: request a role or grant), `RESOURCE_UNAVAILABLE` (the record is hidden from them or does not exist), `PURPOSE_REQUIRED` (a purpose-bound capability without its purpose), `FRESH_AUTHENTICATION_REQUIRED` or `MFA_ASSURANCE_REQUIRED` (sign out and in again). A `DENIAL_LIMIT` row means more than 50 different refusals in five minutes from one person: treat it as a scan — check the member's session and grants. A data-subject request that shows an item as HELD is blocked by a retention hold: list them under **People & access → Retention holds**; releasing one needs a person other than the one who placed it.

### 4.8b Readiness exercise

`sudo /opt/impact/repo/deploy/readiness-exercise.sh` (console, root) stops the worker for one check, confirms that `WORKER_STALE` and `CONTAINER_UNHEALTHY` are raised and delivered, restarts it, confirms they clear, and simulates a full disk on a scratch copy; the record is `/opt/impact/ops/readiness-exercise.json`. Queued deliveries wait while the worker is stopped and are sent when it is back.

### 4.8 A user reports wrong or missing numbers

Do not edit anything in the database. Ask for the programme, indicator, period and the correlation ID; check whether the value is PROVISIONAL or OFFICIAL and whether it is marked stale. Corrections go through the product's own flows (return or amendment before close, restatement after close). Report a suspected calculation defect to the engineer with the IDs.

### 4.9 Suspected personal-data exposure or security incident

Staging must hold no real personal data. If some appears, or access looks wrong: record time and correlation IDs, tell the owner at once, consider suspending the affected membership (tenant administrator) and rotating secrets (§4.7). There is no incident-response procedure, detection tooling or notification process beyond this (FR-SEC-011 PENDING).

## 5. Escalation

1. Tester or user → tenant administrator (access questions) or the server owner (sign-in, outage, alerts).
2. Server owner → engineer (code, database, deployment failures), with the correlation ID, commit and status-page excerpt. Fixes reach the server only by merge to `main` (pulled within 3 minutes); there is no hot-patching.
3. Engineer → product owner for anything that needs a decision (data loss, rollback past a migration, scope).

No response times are promised for staging. Named on-call coverage and published hours are required before production (§8).

## 6. Logs and where they are

| Log | Where | Kept |
|---|---|---|
| Deployment runs | `/var/log/impact-deploy.log` | weekly rotation, 8 kept |
| Alert check | `/var/log/impact-ops.log` | weekly, 8 kept |
| Restore drill | `/var/log/impact-restore-drill.log` | weekly, 8 kept |
| Account adds and resets | `/opt/impact/state/admin-actions.log` | monthly, 24 kept |
| Containers | `$C logs <service>` | 10 MB × 5 per container |
| Captured e-mail | `mail` volume, `/var/lib/impact/mail/captured.jsonl` | not rotated |

## 7. Never copy into a ticket, chat or e-mail

- Passwords and one-time passwords (including the boxes printed by `first-admin.sh`, `add-user.sh`, `reset-user.sh`), authenticator QR codes or 6-digit codes.
- Anything from `/opt/impact/secrets.env`, `compose.env` or the Keycloak administration console; database connection strings.
- Invitation links (they carry a single-use token), recovery-contact verification codes, and the content of captured mail (`captured.jsonl` holds both).
- Session cookies, bearer or ID tokens, CSRF tokens, signed list cursors, browser "copy as cURL" output.
- Personal data of any member or subject, evidence files, import file content, data-subject export packages, audit-export pages, database dumps or backup files.
- Screenshots that show any of the above.

Safe to include: correlation IDs, tenant operating name, object IDs, revision numbers, error codes and reason codes, alert codes, commit hash, timestamps, the status page with its redacted `log_tail`.

## 8. What support readiness still lacks (VF-SUP-001)

VF-SUP-001 asks for continuous on-call coverage for critical incidents, published support hours, response targets and escalation channels per service plan, an operational owner, runbook and tested recovery path for every critical capability, and rehearsed readiness exercises for critical incident, identity recovery, failed import, privacy deletion and report correction. Today:

- **Exists:** this runbook; the status page with closed alert codes; console scripts for account reset, restore drill and rotation, exercised in CI (`container-stack`); a weekly on-server restore drill; operator re-queue; since build 0.27.0 an on-call rota format shown to operators, alert delivery to a webhook or e-mail (when configured), a service-notice banner for users, the access-denied record, and a scripted readiness exercise (worker stop → alert delivered → restart → cleared) run by CI.
- **Missing:** named owners for the roles in §1; on-call coverage; support hours and response targets; paging and acknowledgement; a rehearsal on the real server; identity recovery beyond a console reset by the server owner; the other readiness exercises (identity recovery, failed import, privacy deletion, report correction), recorded with outcomes.

Proposed status: VF-SUP-001 stays PENDING.
