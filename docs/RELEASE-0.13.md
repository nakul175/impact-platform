# v0.13 — Reviewed renewal of delegated authority

Build 0.13.0; schema 16; control-plane API 1.3.0. Roadmap Release 1 remains in progress. The original ledger remains 74 PARTIAL and 233 PENDING requirements, with none declared fully accepted.

## Delivered

The delegated authority created by reviewed initial access (v0.11) expires within 90 days. Until this build nothing could extend it, and the one-time bootstrap cannot run again for the same tenant. A managed tenant can now extend that authority before it expires through the same three-party review the platform already uses.

The current owner proposes an extension for the tenant: a new expiry later than the current one and at most 90 days ahead, and a reason. The proposal pins the exact current authority of the owner and of one second administrator: their delegation ceilings, the managed TENANT_ADMIN grants and role assignments those ceilings back, the second administrator's membership, and a hash of the whole set. The second administrator confirms the exact proposal. A platform operator who is a different natural person from both approves it. Every step requires authentication within the previous five minutes and the configured assurance, an Active tenant, and every readiness check, including an eligible recovery contact.

Approval extends only the pinned rows, in one transaction: the delegation ceilings, the pinned grants (as new revisions), the pinned administrative assignments and the second administrator's membership, which is never shortened. The owner's custody and membership are untouched, business-role grants are not extended and no capability is widened. The `grant_authority` and `member_role_assignment` changes are made by a database-owned applicator that re-verifies state, deadlines, operator status, independence, tenant state and the original bootstrap marker inside SQL; the HTTP roles cannot update those tables directly. The bootstrap marker is neither inserted, updated nor deleted.

Revocations are preserved. Anything revoked before the proposal is absent from the pinned set and stays absent. Anything revoked after the proposal changes the recomputed hash and the approval fails with `AUTHORITY_CHANGED`; nothing is extended and no receipt is written. A ceiling or grant removed through the ordinary administration path is never resurrected by a later proposal or by an exact retry.

The owner can withdraw a pending proposal and an operator can reject one. A pending proposal that has passed its review deadline must be withdrawn or rejected before a new one can be made. Readiness is enforced at the proposal, at consent and at approval; the authority read reports `renewable` and, when it is not, the reason (`AUTHORITY_UNAVAILABLE`, `SECOND_ADMIN_UNAVAILABLE`, `TENANT_NOT_ACTIVE`, `TENANT_NOT_READY`, `RENEWAL_PENDING`).

The Tenant lifecycle console gains an Authority renewal panel: the pinned authority of both administrators with expandable capability lists and expiries, the owner's proposal form with client-side bounds, participant and operator inboxes with only the actions each viewer may take, a history of applied, rejected and withdrawn proposals, plain-language reason strings, and a 390-pixel layout without horizontal overflow. Hidden buttons are not treated as security: the browser check bypasses the client gate and shows the server's denial.

## Contract and persistence

Seven new operations extend the separate control plane to 28 operations at API 1.3.0. The 138 domain operations and domain API 1.10.0 are unchanged.

| Method | Path | Purpose |
|---|---|---|
| GET | /v1/platform/authority-renewals | Owner, second-administrator or operator inbox; UUID cursor, 50 records per page |
| GET | /v1/platform/tenants/{tenant_id}/authority | Current pinned authority, hash, earliest expiry and renewable state; owner or operator |
| POST | /v1/platform/tenants/{tenant_id}/authority-renewal | Current owner proposes an extension |
| POST | /v1/platform/authority-renewals/{request_id}/actions/accept | Exact second administrator confirms |
| POST | /v1/platform/authority-renewals/{request_id}/actions/approve | Independent operator approves and applies |
| POST | /v1/platform/authority-renewals/{request_id}/actions/reject | Operator rejects a pending proposal |
| POST | /v1/platform/authority-renewals/{request_id}/actions/cancel | Current owner withdraws a pending proposal |

Proposals use the tenant revision and echo the authority hash from the authority read; actions use the exact proposal revision. Schemas reject unknown fields, invalid identifiers and out-of-bounds expiry. Shared tenant write locks serialise lifecycle, contact and renewal mutations. Reasons, real actor identity, pinned manifests, revisions and seven-day exact-retry receipts commit together in append-only platform events; reuse of an operation identifier with different content is refused.

Migration 0016 is additive and leaves migrations 0001–0015 and the original specifications unchanged. It adds `tenant_authority_renewal` (one pending proposal per tenant through a partial unique index), grants on it to the control-plane role only, and the SECURITY DEFINER function `apply_authority_renewal` with a fixed search path and no PUBLIC execution privilege. The control-plane role's write surface on existing tables is unchanged from migration 0014. SHA-256 of the migration file: `2c95596d9088fb2ec025266cffed824a787ec8df3d3dd4021fefe19cb09290cc`.

## Limits

Only authority that has not yet expired can be extended. Once either administrator's ceiling has lapsed, this flow is unavailable and the tenant needs the administrator-replacement and expired-authority workflow planned as v0.14. A tenant must have exactly one second holder of delegation authority besides the owner; tenants with none or several report `SECOND_ADMIN_UNAVAILABLE`. Legacy tenants created outside the control plane expose no authority view.

No expiry reminder, external notice, email, SMS, worker or operator-initiated renewal exists; the owner must notice the approaching expiry. Consent is registered-account, fresh-assurance confirmation, not a new external challenge. An unavailable owner cannot be bypassed. Business grants, custody, recovery contacts and memberships other than the second administrator's are outside this flow.

Tests run against fresh in-memory PGlite with serialised transactions and synthetic local identities. Native PostgreSQL scheduling, service-login topology, persistence, upgrades and live provider assurance remain release gates. No deployment occurred.

The specification Markdown reading copies carry a build 0.13.0 increment note; the Word and workbook editable copies and the interactive wireframes are unchanged and will be regenerated at the next documentation edition.

Focused reproduction: `.venv/bin/python scripts/run.py test --pytest-path qualification/test_authority_renewal.py` and `.venv/bin/python scripts/run.py renewal-browser`. Full reproduction: `make lint build test reference browser`. See QUALIFICATION.md for executed counts, NEXT-DELIVERY.md for remaining Release 1 work and DELIVERY-PLAN.md for the sequenced plan.
