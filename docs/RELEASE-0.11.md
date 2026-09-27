# v0.11 — Reviewed initial tenant access

Build 0.11.0; schema 14; control-plane API 1.1.0. Roadmap Release 1 remains in progress. The 307-requirement ledger remains 74 PARTIAL and 233 PENDING, with none declared fully accepted.

## Delivered

A tenant activated through v0.10 can now become operational without fixture grants or automatic owner authority. The current owner proposes a bounded access package. A second registered, verified person accepts the exact package. An expiring, explicitly provisioned platform operator independent of both people approves it. Natural-identity independence applies even when accounts differ.

The proposal pins the onboarding revision, owner membership revision, fixed capability profile, selected role bundles, reason and expiry. The review expires after at most seven days; authority expires after at most 90 days. Every mutation requires configured fresh authentication assurance. Acceptance and approval recheck tenant Active state, deployment qualification, current custody/membership, profile hash, verified identities, authentication cutoffs, expiry and the absence of earlier grants or authority.

Approval atomically creates the second administrator membership, a tenant-wide scope, immutable starter role templates, 23 TENANT_ADMIN grants per administrator, role assignments, delegation ceilings, policy/subject epoch updates, append-only platform evidence and a retry receipt. A database-owned marker prevents another initial provision for the tenant. The HTTP roles cannot delete/reset that marker or directly insert arbitrary grant_authority rows. Injected failure after provisioning rolls the whole transaction back.

The owner selects from AUTHOR, REVIEWER, PROGRAMME_MANAGER, ANALYST and EXTERNAL for **later delegation**. TENANT_ADMIN is also an explicit delegation ceiling. The fixed profile contains only bounded supported non-purpose capabilities; it is not recomputed from future operation registries. Profile changes invalidate pending reviews. The UI displays exact capability lists and expiry before consent and approval.

No business-role grants are created by initial provision. The second administrator can request PROGRAMME_MANAGER, the owner can independently approve it within both delegation ceilings, and the second administrator can create the first programme draft. Initial administrators and the operator cannot read business records without a business grant. Operators retain configuration-only SQL visibility; programme and observation payloads remain outside their role.

The console includes nominated-person and operator inboxes, owner proposals, acceptance, approval, rejection and withdrawal. Refreshing the session after leaving the console preserves a valid user-selected workspace instead of resetting it asynchronously. Capability reads discard aborted responses.

## Contract and transactions

Six new operations are documented separately from the 138 domain operations:

| Method | Path | Purpose |
|---|---|---|
| GET | /v1/platform/access-bootstraps | Participant/operator inbox, fixed profile and UUID cursor; 50 per page |
| POST | /v1/platform/tenants/{tenant_id}/access-bootstrap | Current owner proposes |
| POST | /v1/platform/access-bootstraps/{request_id}/actions/accept | Nominated administrator consents |
| POST | /v1/platform/access-bootstraps/{request_id}/actions/approve | Independent operator provisions |
| POST | /v1/platform/access-bootstraps/{request_id}/actions/reject | Operator rejects a pending proposal |
| POST | /v1/platform/access-bootstraps/{request_id}/actions/cancel | Current owner withdraws a pending proposal |

Closed schemas reject extra fields, unknown/duplicate roles, invalid identifiers, stale profile hashes and out-of-bounds expiry. Requests use the shared tenant write lock and optimistic revisions. Seven-day exact retries return the original result after current caller authority checks; altered or expired operation reuse fails. A replay never recreates revoked grants. No tokens or invitation links are recorded. Cookie requests retain Origin/CSRF checks.

Migration 0014 adds the review and applied-marker tables, narrow configuration projection permissions and a constrained SECURITY DEFINER authority applicator with a fixed search path and no PUBLIC execution permission. It preserves migrations 0001–0013 and the original specifications unchanged. Apply through the checksum-verified migration runner; no operator or deployment authority is inferred from tenant roles.

## Limits and next work

This flow applies only to managed new tenants with no prior grant history or delegation authority. Existing membership recovery, legacy tenant adoption, authority renewal/extension, additional authority recipients and replacing an unavailable administrator require further reviewed workflows. Administrative role assignment alone does not give a third person delegation authority. Once both initial ceilings expire, the app cannot renew them. The protected owner cannot receive ordinary role changes; the demonstrated business workflow uses the second administrator.

The second administrator must already have a registered verified identity and uses an authenticated inbox. No external invitation, email, self-registration or live identity-provider delivery was performed. Both initial grants and the second membership expire; owner custody persists independently. The EXTERNAL starter role label does not turn the nominated administrator into an external member.

First programme creation is demonstrated. Complete new-tenant geography/calendar/workflow-template provisioning and a full measurement-to-publication workflow from an empty tenant are not claimed. Recovery-contact verification, production provider assurance, unavailable-owner recovery, exit/deletion, live workers and operational qualification remain open.

Tests use fresh in-memory PGlite with serialized transactions and synthetic local identities. Native PostgreSQL multi-login isolation, persistence, upgrades, concurrent approval/revocation, backup/restore and live OIDC/MFA are not qualified here. No deployment or real message was sent.

See QUALIFICATION.md for final counts and evidence. Focused reproduction: `.venv/bin/python scripts/run.py test --pytest-path qualification/test_access_bootstrap.py` and `.venv/bin/python scripts/run.py bootstrap-browser`. Full reproduction: `make lint build test reference browser`.
