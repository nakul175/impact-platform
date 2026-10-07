# Secrets and key register (summary and index)

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: a new secret family or credential, a change to `scripts/rotate_secrets.py`, `deploy/compose.yaml` env names, or a real-data deployment.

**Names, holders and rotation steps only; no value appears here or may be added.** The detailed technical register (what each key protects, kid format, encrypted-at-rest inventory, limits) is [KEY-AND-ENCRYPTION-REGISTER](../current/KEY-AND-ENCRYPTION-REGISTER.md) and is canonical; this page adds owner and review columns and covers credentials that register leaves out. Variable names: [`env.example`](env.example).

Holder on the staging server: `/opt/impact/secrets.env` and `compose.env` (root, mode 0600, generated once by `deploy/update.sh`, never printed). Accountable owner for every row: Nakul Jain unless stated.

| Secret | Name(s) | Used by | Rotation | Last rotated |
|---|---|---|---|---|
| Cookie secret (CSRF, cursors, sealed logout hint, audit-export seal) | `IMPACT_COOKIE_SECRET`, `_PREVIOUS` | API | `deploy/rotate-secrets.sh rotate --family cookie`; grace 1 day by default; then `retire --family cookie --expired` | TBD (owner: Nakul Jain); none recorded in this repo |
| Invitation signing secret | `IMPACT_INVITATION_SECRET`, `_PREVIOUS` | API, worker | `--family invitation`; grace 8 days | TBD |
| Delivery secret (sealed recipient addresses, recovery codes) | `IMPACT_DELIVERY_SECRET`, `_PREVIOUS` | API, worker | `--family delivery`; grace 8 days. Retiring early makes queued sealed rows `DEAD RECIPIENT_UNREADABLE` | TBD |
| Provisioner client secret (Keycloak `impact-provisioner`) | `IMPACT_PROVISIONER_SECRET` -> `IMPACT_PROVIDER_ADMIN_CLIENT_SECRET` | API | `--family provisioner`; no grace (script rewrites file, re-aligns Keycloak, recreates API) | TBD |
| Development signing key | `IMPACT_DEV_PUBLIC_KEY`, `IMPACT_DEV_SIGNING_KEYS` | local runs only, never a server | `scripts/rotate_secrets.py ... --family signing`; grace 1 day | n/a |
| Database login passwords | `IMPACT_LOGIN_PASSWORD_{APP,IDENTITY,PLATFORM,WORKER,EXECUTOR,MIGRATOR}`, `POSTGRES_PASSWORD`, `KEYCLOAK_DB_PASSWORD` | API, worker, executor, migrate, Keycloak | **Not covered by the script.** Edit `secrets.env`; next `update.sh` re-provisions logins with a brief restart, no grace | TBD |
| Keycloak admin / owner temporary password | `KEYCLOAK_ADMIN_PASSWORD`; owner one-time password | operators | Manual; owner reset with `deploy/first-admin.sh --reset` or `deploy/reset-user.sh` | TBD |
| SMTP credential | `SMTP_PASSWORD` (`IMPACT_SMTP_PASSWORD`) | worker | By the e-mail provider; none configured (loopback capture) | n/a |
| Alert webhook signing secret | `ALERT_WEBHOOK_SECRET` | ops check | Manual; unset on staging at handover | n/a |
| AI provider key | `OPENAI_API_KEY` / `IMPACT_AI_API_KEY` | API (advisory only) | Provider console; AI is off by default and no funded key is recorded ([AI-MODEL-CARD](AI-MODEL-CARD.md)) | n/a |
| Identity-provider token-signing keys | Keycloak realm `impact` | Keycloak | In Keycloak (add a higher-priority `rsa-generated` provider, keep the old one until tokens expire, disable). Untested here | TBD |
| TLS certificates | Caddy | Caddy | Automatic (Let's Encrypt) | automatic |
| GitHub deploy read key | on the droplet | `impact-sync` | Manual in GitHub; not described in this repo | TBD |
| KMS / platform encryption key | `IMPACT_KMS_KEY_REFERENCE` (release input) | none | No application-level platform key or KMS exists | n/a |

Rotation evidence to keep: output of `deploy/rotate-secrets.sh status` (key ids and grace dates only) and the register files `secrets.env.keys.json` (server) or `.local/<run>/keyring-register.json` (local). They are not backed up off the server. The CI job `container-stack` rehearses rotate and retire for every family and checks that no value is printed.

Gaps: no scheduled rotation or expiry alert; no compromise drill beyond that CI step; no secret scanning in CI (see [SECURE-DEV-SUPPLY-CHAIN](SECURE-DEV-SUPPLY-CHAIN.md)); a rotation calendar and a "last rotated" record per row: TBD (owner: Nakul Jain). Disk and backup encryption at rest depend on the hosting provider and are unverified.
