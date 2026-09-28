# Impact Platform administrator guide

This guide describes build 0.13.0. Custody, tenant control, access administration and programme-data permissions are separate authorities. All sensitive changes retain the real actor, reason, expected revision and operation receipt. Local synthetic verification does not establish a production identity or recovery process.

## Managed tenant onboarding

| Step | Actor | Action | Result and boundary |
| --- | --- | --- | --- |
| 1 | Qualified platform operator | Request tenant with profile, nominated owner and deployment qualification reference | Requested record only; no business access |
| 2 | Exact nominated owner | Review and accept custody | Owner acceptance; no implicit programme grant |
| 3 | Current owner | Nominate a distinct registered recovery contact and bounded expiry | Pending contact; no authority granted |
| 4 | Exact nominee | Verify the nomination with fresh configured assurance | Verified consent to the pinned proposal |
| 5 | Independent operator | Approve the verified contact | Eligible contact if all current checks still pass |
| 6 | Independent operator | Review full readiness and activate | Active tenant; still no automatic business grants |
| 7 | Owner | Propose initial administrative package | Fixed capability and expiry ceilings pinned |
| 8 | Distinct nominated administrator | Accept the exact package | Consent only; no access until provision |
| 9 | Independent operator | Provision reviewed initial access | Bounded administration; one-time applied marker |
| 10 | Authorized administrator and independent reviewer | Request and approve business grants | Explicit scoped business access |

The initial requester cannot independently activate their own tenant request. Operator independence also compares natural-person identities. Current recovery readiness is required for initial-access approval. Authority expiry does not authorize rerunning bootstrap; reviewed renewal/extension remains future work.

## Maintain recovery contacts

Open Tenant lifecycle, then Recovery contacts. The inbox is restricted to current participants and operators. Inspect both stored state and current readiness eligibility. An Active record can be ineligible because of expiry, owner change, verified-channel change or account authentication revocation.

Nomination chooses an existing registered person with verified email evidence, a reason and an expiry no more than 90 days away. The pending window is at most seven days. The nominee must verify the exact proposal, and an independent operator must approve within 24 hours of that verification and before the relevant expiries. Each mutation requires authentication within five minutes and the configured assurance class.

To replace or renew a contact, the owner creates a proposal pinned to the current contact revision. The existing contact remains effective until the replacement is approved. Approval atomically replaces the old record. Decline, withdrawal or rejection leaves the old approved contact untouched. Renewal with the same identity still requires new proof and independent approval.

The owner may cancel pending nominations, the nominee may decline, and an operator may reject. An owner, nominee or operator may revoke an Active contact. Revocation removes future readiness but does not automatically suspend the tenant. Expired pending proposals must be withdrawn, declined or rejected before a new proposal can be created.

A freshly authenticated current owner can repair contact evidence while the tenant is Suspended. An unavailable owner cannot be bypassed by an operator. Contact records confer no reset, custody, membership or grant rights. Account-wide revocation invalidates contact proof; tenant-membership revocation alone does not automatically revoke this separate relationship.

## Renew delegated authority

Open Tenant lifecycle, then Authority renewal. The panel shows the delegated authority of the owner and the second administrator as it currently stands: the exact capability ceilings, the grants and assignments they back, and their expiry. It states whether a renewal can be proposed now and, if not, why (no applied initial access, no second holder, tenant not Active, readiness not met, or a proposal already pending).

Only the current owner proposes. Choose an expiry later than the current one and no more than 90 days ahead, give a reason, and confirm. The proposal pins the exact current authority; anything revoked before the proposal is not included. The second administrator confirms the exact proposal from their inbox. A platform operator who is a different natural person from both approves it within seven days. Every step requires authentication within the previous five minutes and the configured assurance.

Approval extends only the pinned ceilings, grants, assignments and the second administrator's membership. Nothing is widened, business grants are not extended, and a grant revoked after the proposal makes approval fail; withdraw and propose again. Authority that has already expired cannot be renewed in this build; that case, and replacing an administrator, are planned as v0.14.

## Manage members and grants

Inspect the intended verified identity, scope, capabilities, purpose and expiry before issuing a membership invitation or access request. Invitations are single use, intended-identity bound and time limited. Reissue invalidates the earlier invitation. Development links are not evidence of external delivery.

Role changes and renewal require independent review of the exact proposal. The requester, recipient and material author cannot create independence by switching accounts. Template changes do not silently rewrite previously approved assignments. Renewal removes old grants and requires fresh tenant authentication rather than preserving stale authority.

Suspension stops current access and holds owned work. Reactivation requires fresh sign-in and does not replay queued writes or resume schedules. Revocation removes grants and is not reversible through reactivation. Review departure-related sources, schedules, tasks, credentials and recovery-contact relationships separately; the full departure inventory is not yet complete.

## Roles groups and organisation

Workspace settings supports custom role creation, revision and retirement within the actor's delegation ceiling. System templates cannot be edited. Groups require reviewed membership and role bindings; removal immediately removes derived access. Nested groups and full certification are not qualified.

Organisation units support creation, rename and immediate reparenting. Stable codes remain fixed. Cycles and cross-tenant parents are rejected. Future-effective moves and full impact previews remain pending. Custody transfer requires the nominated eligible successor to accept; it never supplies new business permissions.

## Tenant suspension and closure

Review the impact preview before suspension. Queued jobs are cancelled, running jobs are marked for cancellation, and active owned schedules are paused. These database effects have local evidence; actual downstream worker interruption is not implemented.

Reactivation rechecks readiness and requires independent review and fresh authentication. Closing is a preserved lifecycle state, not proof of export, archival or deletion. Governed exit, support access, source-credential rechecks and completed closure remain open. Do not describe a Closing record as deleted.

## Administrative incident record

Record the tenant, actor, operation and correlation identifiers, source and resulting revisions, reason, current state, observed outcome and evidence reference. Never paste credentials or sensitive participant content into an issue. Escalation routes and production security responsibilities must be assigned by the operating organization before deployment.
