# Release 0.2.0 — access administration

Date: 25 September 2026. Status: implemented and locally qualified development release. This advances WP01 and UI05; neither the entire work package nor the enterprise platform is complete.

## Delivered workflows

| Workflow | Server-enforced result |
|---|---|
| Member directory | Current workspace only, masked email, current membership revision/state, explanatory role labels and permitted exact grants |
| Invite | Existing role template, explicit scope, maximum seven-day link, maximum 90-day external membership, reason and current delegation checks |
| Reissue | New token generation invalidates the old link; current issuer/role/scope/expiry checked again |
| Revoke invitation | Link disabled without deleting the historical invitation revision |
| Accept | Provisioned, signed-in identity must match the trusted verified email, tenant, configured issuer and unconsumed/unexpired link; current inviter authority is checked |
| Request access | Exact target membership revision, role-template revision, scope and expiry retained for independent review |
| Approve / reject | Approver must be a different natural person from requester and recipient; approval rechecks both administrators' authority and target revision |
| Scope creation | Immutable set of existing, non-restricted tenant records; no implicit inclusion of related or future objects |
| Revoke grant | One exact current grant becomes revoked; other grants can still authorize the same capability |
| Suspend | New tenant access denied; old authentication fenced; pending invitations revoked, queued jobs cancelled and active owned schedules paused |
| Reactivate | Suspended, unexpired membership becomes active; earlier sessions/tokens remain fenced until fresh sign-in; stopped work is not resumed |
| Offboard | Membership and active grants revoked; attribution/history retained; ordinary reactivation and re-invitation cannot recover it |
| Protect owner | Designated custodian cannot be suspended, revoked, assigned ordinary role changes or have their grants revoked through these routes |

The UI has Members, Invitations, Access requests, Scopes and Role templates tabs; reason-bearing confirmation forms; read-only invitation-link display; pagination; and a join screen. An unauthorized session response clears the client workspace and returns to sign-in. Tab changes discard prior-section data so stale members cannot briefly appear as access requests. Mobile tables have labelled, keyboard-accessible scrolling and a fixed identifying column.

## Access model and constraints

- Authority comes from current explicit grants. JWT roles and visible controls do not authorize commands.
- Administration currently requires tenant-wide grants. Fine-grained delegated administration is not silently treated as tenant-wide authority.
- A separate operator-provisioned `grant_authority` ceiling bounds every capability, scope and expiry that an administrator can delegate. Receiving the TENANT_ADMIN use-role does not manufacture new delegation authority.
- Six fixed templates are supplied: AUTHOR, REVIEWER, PROGRAMME_MANAGER, ANALYST, EXTERNAL and TENANT_ADMIN. They bundle implemented capabilities, not the full future product catalogue. Template editing is not implemented.
- Invitations cannot directly assign an administrative template. Elevated/additional roles require independent access approval.
- Role approval is additive, not replacement. It does not revoke previous or overlapping grants. Exact grants are authoritative; role labels explain their origin and can indicate partial revocation.
- Membership expiry bounds role grants. External-access renewal is pending. An invitation cannot reactivate a suspended or revoked principal.
- Sensitive commands require trusted authentication within five minutes. A recently issued JWT without `auth_time` cannot satisfy that requirement. This is not qualified MFA.
- The owner rule protects one designated custodian. Multi-owner succession, transfer and controlled recovery remain pending. Fixture expiry is still enforced.
- Closed schemas reject server-owned field injection. Existing-object actions require the expected revision. Administrative writes are POST-only; generic PATCH routes cannot create access objects.

## Invitation identity and tokens

An invitation is an access offer, not a login account. The identity must already exist in the trusted identity directory. Production email verification must come from the configured identity provider. The local `invitee@example.test` profile is deliberately synthetic.

The supported email format is bounded ASCII. Local and domain parts are lowercased, without provider-specific dot stripping or plus-tag rewriting. This canonicalization is a declared product policy; providers with different mailbox-equivalence rules require review. The database stores a SHA-256 email identifier and a masked presentation, not the invitation's plaintext email. Hashing does not make predictable addresses anonymous or resistant to dictionary recovery.

The link contains the tenant and an opaque invitation-ID/generation/HMAC token in the browser URL fragment. Only the token hash and public generation are stored. Raw tokens are absent from audit payloads and stored receipts. The creator's response regenerates the URL; exact retry uses the original operation and generation. A forwarded link is insufficient without the matching verified identity. Acceptance consumes the invitation and creates membership/grants atomically.

The issuer's current authority is checked at acceptance, not merely at creation. Reissue changes the token generation/hash. Consumed, revoked, expired, wrong-tenant and wrong-identity links fail closed. Exact retry can recover its own accepted receipt while current authorization and expiry checks still pass; a different operation cannot consume the token again.

No email is sent. Open a production invitation after sign-in; continuation through a real provider redirect has not been qualified. Signing-key rotation is not automated: changing the key alone does not invalidate stored token hashes, and receipt-link regeneration needs the original key. Revoke/reissue pending invitations under a controlled rotation procedure.

## Components and transactions

| Component | Responsibility |
|---|---|
| `administration_contracts.py` | Five list DTOs, twelve command schemas, exact capabilities and fresh-authentication mappings |
| `administration.py` | Delegation subset checks, invitations, lifecycle, custody guards, independent decisions, paging and command receipts |
| `auth.py` / `identity_profile.py` | Trusted verified-email snapshot, sessions, bounded normalization and masked identity presentation |
| `store.py` | Current membership/grant resolution, authentication cutoff, RLS transactions and immutable revisions |
| `service.py` | Existing measurement workflows and shared tenant-lock/cursor helpers |
| `Administration.tsx` | Administration tabs, details, exact-grant actions, confirmations and invitation acceptance |
| `bootstrap_administration.py` | Explicit synthetic identity, role, custody, grant and ceiling provisioning; not a production provisioning API |

Command processing: closed validation → tenant advisory lock → current identity/membership/authority → recent authentication and tenant scope → exact retry lookup → expected revision → lifecycle/delegation/independence checks → changes, audit, outbox, reason and receipt → commit. Acceptance uses the narrow pre-membership branch and resolves current inviter authority before issuing access.

The tenant lock precedes current write authorization. A command waiting behind offboarding re-evaluates current authority. Writes in one tenant are serialized; this favors a clear safety boundary over throughput. Native PostgreSQL scheduling and enterprise concurrency remain unqualified.

Suspension/revocation records an authentication cutoff that reactivation does not erase. Existing cookies may still identify the person globally or in another tenant, but cannot regain this tenant with older authentication. Issuing a fresh token from an older login is insufficient. Already-delivered bytes cannot be recalled.

Running jobs receive a cancellation marker. There is no worker execution loop yet, so tests establish the marker, queued cancellation and schedule pause—not interruption of external side effects. Draft/retired schedules are not promoted to paused active work.

## Database and contract changes

Migration `0005_access_administration.sql` is additive. Migrations 0001–0004 remain unchanged.

| Data | Purpose / privilege |
|---|---|
| `tenant_principal.auth_not_before` | Fence pre-suspension authentication |
| `identity_profile` and session profile fields | Protected global verified identity snapshot; separate identity database role |
| `member_profile` | Tenant-local display name and masked email; forced RLS |
| Invitation generation, role revision, membership expiry and accepted membership | Bind the exact offer; one pending offer per tenant/email hash |
| `tenant_custody` | Designated owner; ordinary app role read-only |
| `grant_authority` | Explicit capability/scope/expiry ceilings; ordinary app role read-only |
| `member_role_assignment` | Immutable assignment metadata and issued grant identifiers |
| `admin_reason` | Nonblank reason tied to the administrative revision |
| `member_natural_identity` | Narrow tenant-bound independence lookup; fixed search path and no PUBLIC execution |

API version is 1.3.0, build is 0.2.0 and readiness schema version is 5. The implemented subset contains 67 domain operations, including 17 added here. The broad design contract includes future endpoints; generate application clients from `openapi-implemented.json`. See `API-INVENTORY.md` for exact paths.

Invitation inputs now require role, scope, link expiry, membership expiry, external status and reason. Consumers of the old design-only shape must update. Arbitrary membership/grant writes remain unavailable.

## Qualification and traceability

The execution record is in `QUALIFICATION.md`. New coverage includes 30 pure unit/contract checks, 34 live administration/security checks and 12 browser workflows. The earlier 79 application checks and eight browser workflows remain in the regression suite.

| Source baseline | This increment | Still open |
|---|---|---|
| WP01 / Access Control §1–3 | Explicit ceilings, verified invitation binding, lifecycle and scoped access approval | Tenant onboarding, operator provisioning, custom roles and renewal |
| Access Control §3 / UI05 | Custody safeguard, exact grants and reasoned actions | Owner transfer and controlled recovery |
| Access Control §5 | Natural-person independence and exact target/template revisions | Full access certification and other governed workflows |
| Access Control §6 | Recent authentication; issuance time cannot impersonate authentication time | Real IdP/MFA, privileged idle limit, federation logout and recovery |
| Access Control §8 | New requests fenced; queued work stopped; running cancellation marked | Worker/download enforcement and provider/device lifecycle |
| UI01 / UI02 / UI05 | Join screen, scoped workspace, access tabs, dialogs, stale-section cleanup and mobile scrolling | Complete navigation, profile/session management and accessibility certification |

Unit checks cover canonicalization, invalid addresses, token tenant/generation binding, separate signing-key use, closed schemas, capability mapping and production key guards. Live checks cover forwarded/replayed/expired/reissued/revoked links; cross-tenant and object scopes; changed/expired authority; natural-person independence; target revision conflicts; owner safeguards; session fencing; PATCH denial; bootstrap restart safety; pending-work cancellation; and policy-bound cursors. Browser tests use separate administrator, invited-member and owner sessions with the real API.

## Non-deliveries

No public deployment or paid infrastructure was created. No real accounts were invited or emailed. Native PostgreSQL CI is configured but not executed here. Live SSO/MFA, email delivery, SCIM, tenant creation, owner transfer, recovery, expiry renewal, custom-role editing, delegation-ceiling management, outbox workers, notifications, automated rotation and production hardening remain pending.

Ingestion, advanced indicator/form designers, collection obligations, attachments, official publication, report rendering/disclosure/export, offline/mobile sync and broad NFR acceptance remain separate increments. Use `NEXT-DELIVERY.md` for the next work package.
