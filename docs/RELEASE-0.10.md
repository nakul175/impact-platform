# v0.10 — Tenant onboarding and lifecycle increment

Build 0.10.0; schema 13. This advances roadmap Release 1 but does not complete it.

## Delivered

- Separate control-plane connection and NOLOGIN/NOBYPASSRLS role, impact_platform. Operators are explicitly provisioned, expire and can be revoked. Tenant ownership and JWT roles do not imply operator authority.
- An operator requests a tenant for an existing registered, verified identity. Profile pins: name, IANA reporting zone, retention duration, privacy reference, region and exact deployment-qualification revision.
- Nominated owner accepts the displayed configuration through an authenticated inbox within seven days. Another identity cannot accept a forwarded UUID. Acceptance atomically creates principal, membership, custody, tenant and policy revisions.
- An operator independent of requester and owner at the natural-identity level activates the tenant. Server checks qualification expiry/revision, environment, issuer/ACR, privacy reference, region, retention bound, recovery-evidence reference and active owner membership.
- Ownership creates zero grants. Operator provenance principals have no memberships. Control-plane SQL cannot read programme/observation payloads. Initial administrative/delegation access remains an explicit provisioning requirement.
- Suspension and beginning closure fence ordinary access, invalidate earlier tenant authentications, cancel queued jobs, mark running jobs Cancelling, advance leases, hold unsent outbox/webhook delivery and hold active schedules. Accepted data and revisions remain intact. Reactivation rechecks readiness without resuming held work.
- Impact counts before confirmation; reasons and real actor identity in append-only platform events; optimistic revisions, seven-day exact retries and tenant write locks. Authority is checked before replay. Custody transfers synchronise owner metadata and invalidate old control-plane revisions.
- Responsive console, owner inbox, confirmation forms and seven closed-schema API operations.

## Limits

FR-TEN-001 remains PARTIAL. Lifecycle applies only to tenants created through this control plane. Adopting existing tenants needs a reviewed migration. Owner requests use existing identity UUIDs and an inbox, not email delivery or self-registration. Request amendment, reissue and cancellation remain pending.

Deployment qualification is an evidence registry writable only by deployment administration. The app checks references and pins; it does not execute provider, contact or recovery qualification. Local evidence is synthetic and constrained to the matching development/test environment. Production SSO/MFA, tenant-specific verified recovery contacts and disaster recovery remain unqualified.

New owners have no automatic data or administrative grants. Reviewed bootstrap authority provisioning is still needed before business workflows can run. Existing explicit access administration works in previously provisioned tenants.

Closing is a terminal fence in this increment, not completed closure. It does not export, archive, delete data, release holds or bypass an exit workflow. Support/exit access, owner-requested closure, unavailable-owner recovery and final deletion remain pending. No destructive deletion operation is exposed.

No live worker exists. Cancellation and holds are verified database state, not downstream interruption. Future dispatchers must recheck tenant Active state, lease generation, cancellation and holds before side effects. Previously admitted reads/delivered bytes cannot be retroactively revoked.

## API and reproduction

packages/contracts/openapi-platform.json documents seven operations separately from 138 existing domain operations (domain API 1.10). Control-plane authority is not a tenant capability.

- GET /v1/platform/tenants: nominated/current managed custody or operator directory; UUID cursor, 50/page, max 100 qualification choices.
- POST /v1/platform/tenants: request.
- POST /v1/platform/tenants/{tenant_id}/actions/{action}: accept-owner, activate, suspend, reactivate, begin-closure.

Mutations require authentication within five minutes, configured assurance and cookie Origin/CSRF. Receipts last seven days; payload changes/expired reuse fail. No raw credentials or tokens are recorded.

Run make test reference browser lint build. Focused: .venv/bin/python scripts/run.py test --pytest-path qualification/test_tenant_lifecycle.py; .venv/bin/python scripts/run.py tenant-browser.

## Deployment setup — not performed here

Apply migration 0013 using the checksum-verified runner. It removes app/worker INSERT and unrestricted UPDATE on tenant_root; policy-epoch updates remain. Provision a separate runtime login with only impact_platform membership and set IMPACT_PLATFORM_DSN. Do not grant app, identity or owner memberships. Staging/production refuse privileged or RLS-bypassing connections.

Through authorised deployment administration, provision expiring platform_operator entries for two independent people and register genuine deployment_qualification evidence: environment, region, issuer, ACR, privacy/recovery references, retention maximum, expiry and a new revision UUID on every change. HTTP cannot edit these records. Never copy synthetic local qualification into production.

No live deployment, external invitation or production mutation occurred. See QUALIFICATION.md and NEXT-DELIVERY.md.

Regression fixes: reload change-request resources when capabilities arrive; do not override a user-selected navigation route when initial access resolves.
