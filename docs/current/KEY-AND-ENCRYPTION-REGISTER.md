# Key and encryption register

Current implementation as of the v0.25 part A slice (branch `release/0.25a-keys-audit`, 1 October 2026). This register states what this build encrypts, signs or hashes, with which key, who holds that key, how it is rotated, and — as plainly — what is **not** encrypted by the application. It describes the code and the staging deployment package; it is not a target design and it is not an acceptance of FR-SEC-002 or FR-SEC-006. No key value appears in this document, in Git or in any output of the tools named here.

## 1. Application secrets (keyrings)

Each family has one current secret and an ordered list of grace secrets (`<family>_secret_previous`). New values are always made with the current secret; values made before a rotation keep working while their secret is in grace and stop working when it is removed (retired). Implementation: `apps/api/impact_api/keyring.py`. A key id (kid) is the first 12 hex characters of SHA-256(`impact-key-id-v1:<family>:<secret>`); it identifies a secret without revealing it.

| Family | Configuration (API / worker) | Protects | Kid carried in | Default grace | Holders |
|---|---|---|---|---|---|
| cookie | `cookie_secret`, `cookie_secret_previous` (`IMPACT_COOKIE_SECRET[_PREVIOUS]`) — API only | CSRF tokens (`<kid>.<HMAC-SHA256>` of the session); signed list cursors (15 min; kid inside the signed payload); provider logout hints (AES-256-GCM, key = HMAC(secret, session cookie); header `0x4B` + 6-byte kid); the audit-export seal (HMAC under HMAC(secret, `impact-audit-export-seal-v1`)) | token prefix, cursor payload, sealed header, manifest `seal.key_id` | 1 day (sessions last at most 8 h) | API process; `/opt/impact/secrets.env` (0600, root) |
| invitation | `invitation_secret`, `invitation_secret_previous` — API and worker | Invitation link tokens (HMAC-SHA256 over tenant, invitation, generation). Only `SHA-256(token)` is stored; acceptance looks the token up by that hash and needs no secret. | none (the worker and a receipt replay find the secret whose token matches the stored hash) | 8 days (invitations ≤ 7 days) | API, worker, `secrets.env` |
| delivery | `delivery_secret`, `delivery_secret_previous` — API and worker | Sealed delivery recipients in `outbox_delivery.recipient_sealed` (AES-256-GCM, key = HMAC(secret, `impact-delivery-recipient-v1`), bound to tenant/template/reference; header `0x4B` + kid); recovery-channel codes (HMAC) and their stored keyed hash | sealed header; codes: none (the secret whose code matches the stored hash is used) | 8 days (a resend reuses the first intent's sealed address) | API, worker, `secrets.env` |
| signing (development only) | `dev_public_key` (current) + `dev_signing_keys` (JSON key set of grace public keys) | RS256 fixture/development bearer tokens; the token header `kid` is `rs-` + 16 hex of SHA-256 over the DER public key | JWT header `kid` | 1 day | `.local/<run>/private.pem` (0600) — never on a server |

Values written before this build carry no kid (bare-hex CSRF tokens, cursors without `kid`, sealed values without the header). They are verified or unsealed by trying each non-retired secret; the HMAC comparison and the AES-GCM tag make every wrong secret fail closed. A token without a `kid` header is verified only with the current development key.

Validation at start-up (`Settings.load`, `WorkerSettings.validate`): every secret at least 48 characters, a grace secret never equal to its family's current one, no secret shared between families (the API refuses to start with `ValueError`, the worker exits with `INVALID_KEYRING`). Every secret, grace secret and connection string is excluded from `repr` of both settings classes.

## 2. Keys the application does not hold

| Key | Held by | Rotation |
|---|---|---|
| Identity-provider token-signing keys (RS256) | Keycloak realm `impact` on the staging server | In Keycloak (Realm settings → Keys → Providers: add a new `rsa-generated` provider with a higher priority, keep the old one active for verification until issued tokens have expired — access tokens live 120 s in the qualification realm — then disable it). The API fetches the realm JWKS by `kid` (`PyJWKClient`, no key cache, 60 s lifespan), so no API change or restart is needed. Not exercised by any test in this build. |
| Provider client secret | Not used: the staging client is public with S256 PKCE (`IMPACT_CLIENT_SECRET` empty). | — |
| Database login passwords (`IMPACT_LOGIN_PASSWORD_*`, `POSTGRES_PASSWORD`, `KEYCLOAK_DB_PASSWORD`) | `secrets.env`; applied by `deploy/prepare_database.py` on each deployment | Not covered by `rotate_secrets.py`. Changing one in `secrets.env` is applied on the next `update.sh` run (logins are re-provisioned), with a brief restart and no grace period. |
| TLS certificates | Caddy (Let's Encrypt, automatic renewal) | Automatic. |
| Keycloak administrator password, owner temporary password | `secrets.env` | Manual; not part of this register's procedure. |

## 3. What is encrypted at rest, and what is not

Encrypted or hashed by the application (application-level, key in section 1):

- delivery recipient addresses in the outbox (AES-256-GCM);
- the provider ID token kept for RP-initiated logout (`web_session.provider_logout_hint`, AES-256-GCM under a key derived from the session cookie, which is never stored);
- session cookies, invitation tokens, recovery codes, OIDC state and browser binding values are stored only as SHA-256 or keyed hashes; verified email addresses only as a SHA-256 hash and a mask.

**Not encrypted by the application** — protection relies on the disk, the host and the provider:

- the PostgreSQL data files (all domain data: observations, results, reports, audit events, identity rows, receipts) on the droplet's volume;
- the evidence object store (`objects` volume, `/var/lib/impact/objects`): uploaded files are stored as plain bytes, content-addressed;
- the nightly `pg_dump` files in the `backups` volume and DigitalOcean's droplet backups;
- the captured-mail file of the loopback mail sink (`mail` volume);
- container logs (10 MB × 5 per container; the application logs error classes and identifiers, not secret values);
- `/opt/impact/secrets.env` and `compose.env` themselves (plain text, mode 0600, root only).

Whether the hosting provider encrypts the droplet disk and its backups at rest is a property of the provider, to be confirmed from its documentation; this build has not verified it, holds no key for it and cannot rotate it. There is no application-level encryption of database columns other than those listed above, no envelope encryption, no KMS or HSM, and no encryption of the object store or dumps with a key the platform controls. A person with root on the droplet, or with a copy of a dump or of the objects volume, can read the data; the secrets in `secrets.env` additionally let them forge CSRF tokens and cursors and read sealed recipients.

## 4. Rotation procedure (summary)

Staging: `sudo /opt/impact/repo/deploy/rotate-secrets.sh rotate --family cookie|invitation|delivery|all [--grace-days N] [--reason TEXT] [--dry-run]`, later `retire --family F --expired` (or `--kid K` / `--all-previous`). Local runs: `.venv/bin/python scripts/rotate_secrets.py --config-dir .local/dev rotate --family all` (including `signing`), then restart `make dev`. Both print key ids and grace dates only and keep a register of kids and events beside the secrets (`secrets.env.keys.json`, `.local/<run>/keyring-register.json`). Details: `docs/current/DEPLOYMENT-GUIDE.md` §10 and `docs/current/OPERATIONS-GUIDE.md` "Key rotation".

Effects of retiring a key before its grace has run out: open browser tabs get `403 CSRF_REQUIRED` on their next change until reloaded (sessions themselves survive); outstanding list cursors answer `400 INVALID_CURSOR`; logout from a session made before the rotation goes to the provider without an ID-token hint; queued invitation emails become `DEAD SIGNING_KEY_MISMATCH`, outbox intents sealed under the retired delivery key become `DEAD RECIPIENT_UNREADABLE` (a resend of such an invitation then fails the same way: issue a new invitation); a recovery-channel code issued before the rotation no longer confirms. An invitation link already delivered keeps working (acceptance needs no secret).

## 5. Limits

- Sealed outbox rows are not re-encrypted under the new delivery key on rotation (the API role cannot update `outbox_delivery`); they remain readable only during grace.
- The kids are derived, not registered: there is no database record of keys, owners or expiry inside the product, and no operator screen. The register files beside `secrets.env` are the evidence; they are not backed up off the server.
- No automatic or scheduled rotation, no expiry alerting, no key-compromise drill beyond the CI rotation step, no FIPS-validated module claim (Python `cryptography` with OpenSSL).
- Rotating the cookie secret changes the audit-export seal key: a manifest sealed earlier verifies (`verify_seal`) only while that key is in grace; the content digest and hash chain stay verifiable by anyone.
- Identity-provider key rotation, database password rotation and certificate rotation are outside the application keyrings and untested here.
