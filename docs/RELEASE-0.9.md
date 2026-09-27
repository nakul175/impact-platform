# v0.9 — Release 1, tenant and identity administration increment

This build starts the first item in the agreed 16-release roadmap. It adds working administration flows to v0.8; it does **not** close roadmap Release 1 or declare the full product finished. Build: `impact-0.9.0`. Domain API: `1.10.0`. Schema: `12`. Implemented domain operations: `138` (23 added); five additional account routes are documented below.

## Delivered behaviour and boundaries

| Area | Delivered | Remaining within the larger requirement |
|---|---|---|
| Custom roles | Create, revise and retire custom templates; closed capability lists; explicit delegation ceiling; system-template protection; immutable role revisions | Authority provisioning UI, access certification, permission simulation and whole-assignment replacement |
| Governed groups | Flat membership and scoped role bindings; complete replacement proposals; independent approval/rejection; role and membership revision pins; current requester and reviewer delegation checks; immediate member removal and retirement | Directory synchronisation, bulk operations and richer group lifecycle UI; nesting is deliberately unsupported |
| Organisation units | Stable unique code, named unit, nullable parent, rename and immediate move; cross-tenant rejection; full-tree cycle/depth checks; immutable historical revisions | Future-effective reorganisation, obligation impact preview and inherited organisational access policies |
| Membership renewal | Independent request/approval/rejection; exact membership revision; bounded extension; fresh sign-in after approval; every old direct grant and materialised group entitlement removed | Proactive expiry jobs/notices, full departure inventory and streamlined reapproval of replacement access |
| Ownership | Owner-only nomination of an existing eligible administrator; seven-day expiry; successor acceptance; distinct natural identities; custody and tenant record changed atomically | Unavailable-owner recovery with independently verified contacts and operational custody provisioning |
| Sessions | Device labels, creation/activity/expiry times, active-session inventory, individual revocation and global revocation; global revocation rejects earlier bearer authentications too | Provider logout, refresh-token lifecycle, shared-device mode, idle draft warning and session export |
| Preferences | Optimistically versioned display name, English language setting, IANA time zone and reduced-motion preference | Other translations and consistent time-zone rendering across every older screen |
| Federation assurance | Validated `acr`/`amr` persistence; configured exact assurance-class check on fresh-assurance operations; production configuration requires an assurance class; fixed provider account-management link | Live provider qualification, authenticator enrolment, passkeys, last-factor/recovery safeguards, action-bound step-up challenges, SCIM and account provisioning |

### Access rules

Custom-role creation conveys no permission. Assignment continues through independently approved access requests or group proposals. A role revision or retirement never retroactively rewrites an approved assignment. Pending proposals are invalidated when their pinned role or membership changes. A retired template cannot be used for new assignments.

Group proposals replace the complete membership and binding snapshot. Approval must be performed by a different natural identity from the requester and every proposed member. It rechecks both administrators' current delegation ceilings, membership activity, scope type, expiry and pinned revisions. Derived access is read from the current group-entitlement projection on every request; removal or retirement cannot leave cached group access valid. Explicit direct grants are independent and remain separately governed. The group row, entitlement projection, revision history, audit/outbox event and receipt commit together under the tenant advisory lock.

Groups have at most 100 members, 10 bindings, 500 capability/scope pairs and 2,000 materialised entitlements in a proposal. A member has at most 500 current direct and derived grant rows when issuing new access. Each binding expires within 90 days and cannot outlive a member or the issuer's delegation authority. Administrative role bindings require tenant scope. The browser authors one binding per proposal and explicitly states that it replaces all prior bindings; the API supports ten.

Renewal supports active memberships, including those whose expiry has elapsed. It does not reactivate a suspended or revoked membership, and cannot renew the designated owner. Expiry must extend the existing date and be within 90 days. Approval invalidates old tenant authentication and removes all previous access, including unexpired access; the UI explains this before submission. A separate reviewed access request is required. Existing schedules are not automatically resumed.

Ownership is custody, not a new data-access role. The successor must already possess tenant-scoped ownership administration and operator-provisioned delegation. Both parties retain their separately approved grants after transfer. The runtime app role cannot directly update `tenant_custody`; the narrow SQL function accepts only a live nominated request, unchanged current owner, active pinned successor and different natural identity. Recovery of an unavailable owner is not implemented.

### Accounts and assurance

Every cookie session now uses the stricter 15-minute inactivity bound and eight-hour absolute lifetime. At most 50 active sessions may be created per identity. Session public IDs are independent UUIDs; inventory never exposes session hashes, cookies, raw user agents or tokens. Device labels are coarse, untrusted browser descriptions. Revocation requires authentication within five minutes and the configured assurance level. Origin/CSRF checks apply to cookie mutations. Account-level security events are append-only for the identity runtime role.

Global revocation updates an identity authentication cutoff and revokes all application cookie sessions in one transaction. A bearer authenticated before the cutoff is rejected even if its token has not expired. A new authentication can establish access again. This does not claim logout at an external identity provider or revocation of provider refresh tokens.

`IMPACT_REQUIRED_ACR` identifies the assurance class the configured provider contract defines as sufficient MFA. It is mandatory in staging/production. The application compares exact issuer-validated `acr` values; it does not infer MFA from token issuance or a user-supplied role. `amr` is type-checked and retained, not treated as a universal strength scale. Fresh-assurance commands require both the exact configured class and the existing authentication-age limit. Local synthetic identity is explicitly development-only and is not evidence of MFA.

`IMPACT_PROVIDER_ACCOUNT_URL`, when configured, must be a fixed HTTPS URL. It links to the provider's authenticator/recovery management. No enrolment or recovery completion is fabricated by the application. The [OpenID Connect Core specification](https://openid.net/specs/openid-connect-core-1_0.html) is the reference for `auth_time`, `acr`, `amr`, nonce and freshness semantics. Provider-side assurance policy and real callback/recovery qualification remain acceptance gates.

### API and data

New domain commands and closed list schemas are in `workspace_contracts.py`; the generated implemented inventory is `API-INVENTORY.md`. All administrative writes require reasons, current permission, fresh assurance, immutable expected revisions where applicable and seven-day exact-retry receipts. Administrative metadata is tenant-bound and paginated.

| Method | Account route | Contract |
|---|---|---|
| GET | `/auth/preferences` | Own display name, language, time zone, reduced motion and revision |
| PUT | `/auth/preferences` | Closed fields: `expected_revision` (UUID or null), `display_name`, `language` (`en`), `timezone`, `reduced_motion`; stale revisions return 409 |
| GET | `/auth/sessions` | Own active sessions, expiry policy and configured provider account URL |
| POST | `/auth/sessions/{session_id}/revoke` | Revoke own matching browser session; foreign/missing IDs return the same 404 |
| POST | `/auth/sessions/revoke-all` | Revoke all own application sessions and earlier bearer authentications |

These account operations use identity context and have no tenant selector. Preference edits do not change verified email, sign-in subject, natural-person identity or tenancy. Account mutations create identity-security events; they are separate from domain-command receipts. The session revocation routes accept no application data payload. Revoking an already revoked own session is harmless while the caller remains authenticated.

Migration `0012_workspace_administration.sql` extends allowed immutable object types, creates tenant-fenced group entitlements, enforces unique organisation codes, adds opaque session IDs and assurance snapshots, creates identity preferences/security state/events, and adds the constrained custody function. Migrations 0001–0011 and all preserved specification files remain unchanged. Migration 0012 can reject a database with duplicate existing organisation codes; review and resolve such legacy data through an authorised migration plan before production upgrade. No production upgrade was performed.

## Verification and known limits

See `QUALIFICATION.md` and the machine-readable evidence directory. New live scenarios cover closed reads, role ceilings/protection/history, unit cycles and parent clearing, group independence/current access/revision drift, renewal independence and non-resurrection, custody acceptance, preference isolation/stale writes, individual/global session revocation, CSRF, idle timeout and assurance-class enforcement. Browser checks cover the rendered role/unit/group/review/custody/preferences/session flows and responsive account layout.

Filesystem-backed PGlite intermittently returned EOF/page-consistency errors in this managed filesystem, including missing recent rows. Those runs were failures, not passing evidence. Final local qualification uses fresh in-memory PGlite PostgreSQL 17.5 and retains configuration/logs, not the database, after shutdown. Native PostgreSQL installation was unavailable in this execution environment; its persistence, migrations under real service roles, concurrency and recovery remain unqualified. Use `dev --ephemeral` for a disposable local demonstration. This workaround does not establish durable storage correctness.

Tenant onboarding, platform-operator provisioning, provider-owned recovery and the remaining Release 1 acceptance work are tracked in `NEXT-DELIVERY.md`. No site was deployed, no real person was invited and no external message was sent.
