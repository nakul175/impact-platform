# Impact Platform administrator guide

**Build 0.33 local candidate — internal advice permissions:** the new saved-plan advice workflow uses existing AI read/manage authority. Only an owner or tenant administrator with current tenant-wide directory authority and current plan AI authority can load eligible-colleague names. Ordinary AI management does not grant directory access. The chosen requester/adviser must remain distinct currently authorised natural people, and membership does not establish certification or availability. Private brief sharing needs the requester’s explicit assignment and consent; terminal cases immediately end adviser access. The workflow creates no external engagement, message, supplier booking or purchase. [Candidate record](../RELEASE-0.33-tola-ai-extension.md). Native/application/browser gates remain in progress.

**Build 0.32 review update — extend organisation access:** in **Tenant lifecycle**, select **Extend organisation access**. The owner chooses the organisation, reviews the exact added capabilities and target role templates and proposes with a reason. The named second administrator inspects the proposal and accepts; a current independent operator then reviews and approves or rejects with a reason. Confirm the organisation and proposal shown on the decision form. The owner may withdraw a pending request. Approval adds only the registered profile's new capability delta and preserves existing expiries and prior revocations. It does not renew authority; use the separate renewal flow. Material changes require a fresh proposal. [Release and limits](../RELEASE-0.32-tola-ai-sprint.md). Local review candidate only.

This guide describes build 0.26.0, refreshed for the v0.27 usability work (`docs/RELEASE-0.27-ux.md`) and, at the build 0.27.0 integration, for operator renewal and deactivation; the other 0.27.0 additions (retention policies and holds, the Access denied list, collection rounds, alerts and the service-notice banner) are described in `docs/RELEASE-0.27.md` and its slice notes. It is for the people who look after a workspace (the owner and the administrators under People & access and Workspace settings) and for platform operators (the Tenant lifecycle console). Each section names the release note that holds the full description and the exact limits; where they disagree, the release note is right. The operations guide (`docs/current/OPERATIONS-GUIDE.md`) and the deployment guide (`docs/current/DEPLOYMENT-GUIDE.md`) cover the server, secrets, backups and alerts; the support runbook (`docs/current/SUPPORT-RUNBOOK.md`) covers incidents.

Four authorities are kept apart on purpose, and no screen merges them: **custody** (owning the organisation's workspace), **tenant control** (the operators' console), **access administration** (who may do what) and **programme-data permissions** (reading or changing data). Holding one never implies another. Every administrative change records who did it, their reason, the exact revision they changed and an operation receipt, and every review that needs a different person compares natural persons, not accounts.

## Bring a new organisation onto the platform

*Release notes: `docs/RELEASE-0.26a.md` (operators, sign-ins, reference data, `initial-access-v2`), `docs/RELEASE-0.12.md` (recovery contacts), `docs/RELEASE-0.13.md` (authority renewal); the owner's click path is `docs/current/DEPLOYMENT-GUIDE.md` §4.1.*

The first organisation needs three people: the operator who requests it, the person who will own it, and a second operator who activates it and approves its access reviews. The platform refuses to let one person play two of these roles.

| Step | Who | Where | What it does |
| --- | --- | --- | --- |
| 1 | Operator | Tenant lifecycle → Platform operators | **Nominate an operator** by e-mail, then **Create a sign-in for someone** for that address. Hand over the one-time password yourself; it is shown once and never stored. |
| 2 | Nominee | Sign in, Tenant lifecycle | Set a password and authenticator on first sign-in, then **Accept** the nomination. The nominating operator cannot accept for them. |
| 3 | Operator | Platform operators | Create sign-ins for the future owner and for the second administrator (two different people). Each signs in once. |
| 4 | Operator | **Request tenant** | Operating name, owner (chosen by name from the people who have signed in), qualified deployment, reporting time zone, retention days, privacy policy reference, reason. The form opens in a dialog; the request creates a record and nothing else. |
| 5 | Owner | The card of the request | **Accept ownership.** This creates the custody membership. It opens no data: the owner now sees **Your administrator access is being set up** in the workspace. |
| 6 | Owner | Recovery contacts | **Nominate** a registered person as recovery contact (expiry within 90 days). The contact **verifies** the nomination with a fresh sign-in and may confirm their e-mail address with a code; an operator who is not the owner **approves** within 24 hours of the verification. |
| 7 | Independent operator | The card | **Activate tenant.** Refused for the requesting operator and for the owner. |
| 8 | Owner | Initial access | **Propose initial access**, naming the second administrator. The proposal pins the onboarding profile `initial-access-v2`. |
| 9 | Second administrator | Initial access | **Accept administrator role.** Consent only; still no access. |
| 10 | Independent operator | Initial access | **Approve initial access.** The reviewed package is applied once: the owner and the second administrator receive their administration capabilities and delegation ceilings, with an expiry. |
| 11 | Owner | People & access → Reference data | **Set up the standard reference data**, or create a calendar, review template, report template and geography by hand. Programmes cannot be activated without a calendar and a geography. |
| 12 | Administrators | People & access | Invite members and grant them roles (below). |

Tenants onboarded before build 0.26.0 keep the older `initial-access-v1` ceiling of 75 capabilities until a separately reviewed extension is applied. The local 0.32 candidate provides that extension through **Extend organisation access**, with owner proposal, named second-administrator consent and independent operator approval. Existing ceilings are not widened automatically. A v1 initial-access proposal still pending when the platform is updated is refused (`ACCESS_PROFILE_CHANGED`): cancel it and propose again.

## Operators' console (Tenant lifecycle)

*Release notes: `docs/RELEASE-0.26a.md`, `docs/RELEASE-0.16.md` (workers), `docs/QUALITY-2026-10.md` (re-queue), `docs/RELEASE-0.27-ux.md` (dialogs).*

Everyone can open the console; it shows each person only the requests addressed to them. A platform operator sees every organisation, the operators, the registered people, the workers and the deliveries.

- **Tenant cards** show state, region, time zone, retention, the owner's identity reference, the work still outstanding (unfinished jobs, schedules, undelivered notices, retention holds) and the readiness checks. The actions on a card (**Accept ownership**, **Activate**, **Suspend**, **Reactivate**, **Begin closure**) open a dialog next to the card that names the action and the organisation, asks for a reason, and returns focus to the card when closed. Every one of them needs a sign-in within the last five minutes.
- **Suspend** stops access and holds background deliveries; **Reactivate** rechecks readiness, needs an operator independent of the requester and the owner, and does not resend what was held. **Begin closure** cannot be reversed in this build and deletes nothing; a Closing record is not an archived or deleted one.
- **Platform operators**: nominate, cancel a nomination, create or reissue a sign-in, see who has signed in and their identity references. Since build 0.27.0 (`docs/RELEASE-0.27-operators.md`) another active operator renews an operator's role before it expires (**Renew operator role**: a later end date, at most 365 days ahead, and a reason) or ends it at once (**Deactivate**, with a reason); nobody can renew or deactivate themself, the last active operator cannot be deactivated, an expired or deactivated operator is re-established only by a new nomination, and the panel lists every operator change. A departing operator is deactivated by a colleague; nominations they made can no longer be accepted.
- **Workers**: heartbeats of the background workers (build, state, failures); a worker whose heartbeat is older than a minute while running is shown stale.
- **Deliveries needing attention**: notices and e-mails that failed permanently or are held by a suspension. **Re-queue** or **Release hold** one at a time, with a reason, for an Active organisation only; nothing is resent automatically.
- **Recovery contacts**, **Initial access** and **Authority renewal** are separate pages with the same card-and-form pattern.

## Keep the administrators' authority alive

*Release note: `docs/RELEASE-0.13.md`.*

The authority applied at initial access expires. **Authority renewal** shows the owner's and the second administrator's delegated authority as it stands and whether a renewal can be proposed now. The owner proposes an expiry up to 90 days ahead; the second administrator confirms the exact proposal; an operator who is neither of them approves within seven days. Approval extends only what was pinned: nothing is widened and business grants are not extended. Authority that has already expired cannot be renewed in this build, and an administrator cannot yet be replaced; both are Release 2 work.

Administrators of delegated authority receive a notice in My work 14 and 3 days before it expires.

## Invite people and grant access

*Release notes: `docs/IMPLEMENTATION.md` (access administration), `docs/RELEASE-0.16.md` (emailed invitations), `docs/RELEASE-0.26a.md` (sign-ins and purpose-bound grants).*

1. In **People & access**, **Invite member**: a person's e-mail address with an expiry. The invitation is single use and bound to the intended verified identity; reissuing it invalidates the earlier one. Where e-mail delivery is configured the worker e-mails the link; the e-mail itself grants nothing. On staging the workspace owner can then **Create a sign-in for this person**, and hands over the one-time password in person.
2. The person opens the link, signs in and joins. They now have a membership and no permission: they see **Your access is being set up** until a grant is approved.
3. **Request role change** for a member: a fixed template (AUTHOR, REVIEWER, MEL_ADMIN, PROGRAMME_MANAGER, DATA_STEWARD, ENUMERATOR, ANALYST, EXTERNAL and so on) or a custom role, a scope (the whole workspace or a named scope), an expiry within 90 days and a reason. A different administrator chooses **Approve request** or **Reject request**. A request beyond your own delegation ceiling is refused: you cannot delegate what you do not hold.
4. **Purpose-bound access** is requested and approved the same way for the seven capabilities that only exist for a stated purpose: the audit export and the six data-subject-request capabilities. They are never part of a role.
5. **Suspend** a member to stop their access and hold their work; **Reactivate** needs their fresh sign-in and resumes nothing automatically; **Revoke** removes their grants and is not undone by reactivation. The owner's own custody membership cannot be removed here.

Every one of these needs your sign-in within the last five minutes. The requester, the member and any author of the request cannot approve it, however many accounts they hold.

## Roles, groups and organisation units

*Release note: `docs/IMPLEMENTATION.md`; the delegable set is `contracts.DELEGABLE_CAPABILITIES`.*

In **Workspace settings** you create, revise and retire custom roles within your delegation ceiling; the fifteen system templates cannot be edited. A custom role may carry only the 117 capabilities of implemented, purpose-less operations; a design-only capability is refused even if your ceiling names it. Groups bind reviewed memberships to roles, and removing a member from a group removes the derived access at once. Organisation units can be created, renamed and reparented; a cycle is refused. Custody can be transferred to a nominated successor who accepts it; the transfer carries no business permission.

## Reference data

*Release note: `docs/RELEASE-0.26a.md`.*

Under **People & access → Reference data** (capability `reference-data.manage`, owner and tenant administrator): **Set up the standard reference data** once per workspace (a quarterly calendar for this and next year, the review template "Standard independent review", the report template "Standard results report", the geography "Organisation-wide"); or create a **reporting calendar** (monthly, quarterly or yearly, 1–5 years, extendable to 20), a **review template** (the only shape this build executes: one independent approval), a **report template** (1–20 sections) and **geographies** by hand. Each is an ordinary governed command with a reason and an audit record. The development fixture's calendar cannot be extended.

## Export the audit trail

*Release note: `docs/RELEASE-0.25a.md`.*

**Audit export** under People & access (capability `audit.export`, held for a purpose: security review, incident investigation, regulatory request or internal audit) exports the audit events of a window as JSON lines with a hash chain and a seal, page by page, with a manifest you download beside it. State the purpose and a reason; the export itself is audited. The seal can be verified only while the key that made it is current or in its grace period, so verify soon after exporting.

## Handle a data-subject request

*Release note: `docs/RELEASE-0.25b.md`.*

Subjects are members of the workspace; participants do not exist in this build. Under **People & access → Data-subject requests**, with purpose-bound privacy capabilities:

1. **Open a case**: access or erasure, the member, the reason, how the request was verified, an optional deadline. An erasure case may name the member's evidence files and finished import batches.
2. Read the **plan**: every store the case will touch and what happens there (redact, delete, supersede), including items held back by a retention hold or shared content.
3. A different person **approves** the exact plan. Erasure also requires that the member is no longer active and does not hold custody: offboard first.
4. **Execute.** An access case produces an export package to download within seven days; an erasure case runs at once, records every store action in the deletion ledger and reports anything held back or failed (failed object deletions are retried). Approved observations, results, snapshots and reports are never altered: official numbers stay as they were.

Erased values remain in backup sets taken before the erasure until those age out, and a restore does not replay erasures; the retention schedule is fixed for every workspace and cannot yet be set per tenant.

## Suspend or close an organisation

*Release notes: `docs/IMPLEMENTATION.md`, `docs/RELEASE-0.16.md`.*

Review the card's impact figures before suspending. Suspension cancels queued jobs, marks running ones for cancellation and pauses schedules; notices queued before it are never sent, not even after reactivation. Reactivation rechecks readiness and needs independent review. Closing is a preserved state: governed export, archival and deletion are not implemented, and a Closing organisation must not be described as deleted.

## Record an administrative incident

Record the organisation, actor, operation and correlation identifiers, the revisions before and after, the reason, the current state, what was observed and where the evidence is. Never paste credentials, one-time passwords or personal data into an issue. Alert codes, first steps and escalation are in `docs/current/SUPPORT-RUNBOOK.md`.
