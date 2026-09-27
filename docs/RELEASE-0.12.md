# v0.12 — Verified tenant recovery contacts

Build 0.12.0; schema 15; control-plane API 1.2.0. Roadmap Release 1 remains in progress. The original ledger remains 74 PARTIAL and 233 PENDING requirements, with none declared fully accepted.

## Delivered

A managed tenant has one primary recovery contact. The current owner nominates an existing registered person with a verified account, specifies a reason and chooses an expiry within 90 days. The nominated person confirms the exact nomination through an authenticated inbox with fresh configured assurance. A platform operator independent of both owner and contact approves it. The contact receives no membership, grant, reset capability or custody authority.

The nomination pins the tenant revision, current owner and membership revision, nominee identity and verified-email hash, expiry and current contact revision. Verification must occur within the seven-day nomination window; approval must follow within 24 hours of verification and before either expiry. Each mutation requires authentication within five minutes and the configured MFA assurance. Identity, profile and cutoff checks are locked against the existing account revocation path before mutation or receipt replay.

Approval makes the contact eligible for tenant readiness. Eligibility is recomputed from the current owner/custody, nominee issuer, verified-email hash, authentication cutoff and expiry. A subsequent channel change, contact account-wide revocation, owner change or expiry invalidates eligibility without rewriting historical approval evidence. The UI distinguishes the stored Active state from current readiness eligibility.

Activation and reactivation now require an eligible contact as well as all earlier readiness checks. The deployment recovery-evidence reference remains a separate requirement. Existing active tenants are not automatically suspended when contact evidence becomes invalid. Owners with fresh authentication can replace or renew contact evidence while a tenant is Suspended, then an independent operator can reactivate it. Initial administrative-access approval also retains the complete readiness check.

Replacement is an owner nomination pinned to the current contact revision. The existing contact remains effective while a replacement is pending. Nominee verification and independent approval atomically mark the old record Replaced and activate the new record. An injected failure after replacement restores the old record, revision and evidence, and creates no receipt. Renewal uses the same flow with the same identity and new proof; it cannot silently extend old verification.

The owner can withdraw a pending nomination, the nominee can decline, and an operator can reject. Owner, nominee or operator can revoke an Active contact immediately. Revocation blocks future activation/reactivation when no eligible contact remains. Exact retries return the original receipt without resurrecting revoked or replaced records. Changes to the current contact invalidate pending replacement approvals.

The interface includes private participant/operator inboxes, nomination and confirmation forms, masked contact details, verification and review times, approval attribution, expiry, history and mobile layout. A previous contact can inspect their own historical record without seeing the replacement person's nomination.

Workspace settings now initializes its selected section when permissions arrive after the page opens, while retaining a valid user selection. A browser regression check deliberately holds the permissions response until after navigation.

## Contract and persistence

Eight new operations extend the separate control plane to 21 operations. The 138 domain operations and domain API version 1.10.0 are unchanged.

| Method | Path | Purpose |
|---|---|---|
| GET | /v1/platform/recovery-contacts | Current owner, nominee or operator inbox; UUID cursor, 50 records per page |
| POST | /v1/platform/tenants/{tenant_id}/recovery-contacts | Owner nominates or renews a contact |
| POST | /v1/platform/recovery-contacts/{contact_id}/actions/verify | Exact nominee verifies and accepts |
| POST | /v1/platform/recovery-contacts/{contact_id}/actions/approve | Independent operator approves |
| POST | /v1/platform/recovery-contacts/{contact_id}/actions/reject | Operator rejects a pending nomination |
| POST | /v1/platform/recovery-contacts/{contact_id}/actions/cancel | Current owner withdraws a pending nomination |
| POST | /v1/platform/recovery-contacts/{contact_id}/actions/decline | Nominee declines a pending nomination |
| POST | /v1/platform/recovery-contacts/{contact_id}/actions/revoke | Owner, nominee or operator revokes an Active contact |

Tenant responses now include `recovery_contact` status and the `recovery_contact_verified` readiness check. Client contracts must be updated with API 1.2.0. Nomination uses the current tenant revision and nullable `expected_contact_revision`; actions use the exact contact revision. Schemas reject unknown fields and invalid identifiers/expiry. Shared tenant write locks serialize lifecycle and contact mutations. Reasons, real actor identity, masked evidence, revisions and seven-day exact-retry receipts commit together in append-only platform events.

Migration 0015 is additive and leaves migrations 0001–0014 and the original specifications unchanged. A unique index permits one Active and one pending contact per tenant. Only the control-plane role can access the contact table; app and identity roles cannot read it. A narrow SECURITY DEFINER function obtains identity/profile/cutoff locks, uses a fixed search path and is not executable by PUBLIC. No extra business-object visibility or identity mutation permission is granted.

## Limits

Verification method is **REGISTERED_IDENTITY_MFA**: an existing verified account plus fresh configured authentication and explicit tenant-specific consent. It is not a new mailbox or phone challenge and does not prove a person can receive new external messages. Local development verification is synthetic and labelled as such. No real email/SMS was sent; no live identity provider or MFA enrolment was configured or qualified.

This is contact evidence management, not an account recovery or unavailable-owner bypass. Recovery codes, factor replacement, independent recovery quorum, unavailable-owner evidence adjudication, custody reset, security-notice delivery, external contacts and verified message delivery remain pending. Tenant membership revocation does not automatically revoke the separately nominated recovery-contact relationship; account-wide authentication cutoff invalidates its existing proof. Full departure inventory remains open.

Only one primary contact is implemented. A pending expired nomination must be withdrawn, declined or rejected before another is created. No expiry reminder worker or external notice dispatcher is present. A current owner can maintain contacts, but an unavailable owner cannot be bypassed by an operator. Existing managed tenants without contact evidence keep current business access but must enrol a contact before later reactivation or initial-access approval. Legacy unmanaged tenants still require reviewed adoption.

Tests run against fresh in-memory PGlite with serialized transactions. Native PostgreSQL concurrent scheduling, service-login topology, persistence, upgrades, backup/restore and live provider delivery remain release gates. No production deployment or real account recovery occurred.

Focused reproduction: `.venv/bin/python scripts/run.py test --pytest-path qualification/test_recovery_contacts.py` and `.venv/bin/python scripts/run.py recovery-browser`. Full reproduction: `make lint build test reference browser`. See QUALIFICATION.md for executed counts and NEXT-DELIVERY.md for remaining Release 1 work.
