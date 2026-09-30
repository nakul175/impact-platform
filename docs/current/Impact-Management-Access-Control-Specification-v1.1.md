# Impact Management Access Control Specification

Version 1.1   27 September 2026

This specification defines how users, external partners, service identities, support staff and platform operators receive and exercise authority. The capability catalogue is generated from the API contract so every operation has an explicit policy entry. Role templates provide starting grant bundles. Authority comes from a current scoped grant and all contextual checks, not from a role label in the browser or identity-provider token.

## Release interpretation

Documentation edition 1.1 is reconciled with application build 0.12.0 on 27 September 2026. The document edition and application build use different version sequences. The original business requirements and their acceptance conditions remain authoritative. No requirement has been removed or weakened to match the current code.

Build 0.13.0 increment (28 September 2026): the current authority model gains reviewed renewal of unexpired delegated authority. Only the current owner proposes; only the pinned second administrator, a distinct natural person who currently holds delegated authority, consents; only a platform operator independent of both approves. Each step requires fresh configured assurance and rechecks readiness, tenant state, identity cutoffs, expected revisions and the pinned authority hash. Approval extends only the expiry of the pinned rows, adds no capability, never revives authority revoked before the proposal and fails on any revocation after it. Expired authority, administrator replacement and operator-initiated renewal remain pending. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.14.0 increment (29 September 2026): no capability, role template, purpose or assurance rule changed. The database side of the deny-by-default model is now qualified on native PostgreSQL under real login roles rather than one superuser session: impact_app_login, impact_identity_login and impact_platform_login each assume exactly their own privilege role (NOINHERIT, NOBYPASSRLS, one membership, provisioned by scripts/provision_logins.py outside the migration set), impact_app reads nothing without a transaction-local tenant and no control-plane table, impact_identity reaches identity tables only, impact_platform writes only its RESTRICTIVE object types and cannot re-date delegation ceilings or assignments, and the runtime guard (IMPACT_REQUIRE_UNPRIVILEGED_DB; always on in staging and production) refuses superuser, BYPASSRLS, owner-member or shared connections on readiness and on every transaction with a reason code only. Native races confirm that two independent approvals of one candidate admit exactly one decision and that a renewal approval and a pinned-grant revocation resolve in one order, never both (qualification/test_native_roles.py, test_native_concurrency.py). The Word copy is unchanged and will be regenerated at the next documentation edition.

The application is a development delivery. The requirement ledger records 74 PARTIAL and 233 PENDING requirements, with zero fully accepted. PARTIAL means a bounded implementation and some evidence exist, not that all acceptance conditions are satisfied. PENDING means the requirement has no accepted implementation coverage in the ledger; a read-only surface or reference example does not establish delivery.

Recorded qualification contains 325 application checks, 143 design-reference checks and 81 browser checks. One expired-offline-grant test is deselected and is not a pass. Local integration uses fresh in-memory PGlite PostgreSQL 17.5 with serialized transactions. Native PostgreSQL concurrency, live identity-provider assurance, disaster recovery, load qualification and production acceptance remain open.

The original BRD and FSD use R1, R2 and R3 requirement assignments. The later 16-stage delivery roadmap is an implementation sequence. Roadmap stage 1 and baseline R1 are different groupings; neither is complete. Requirement release assignments remain unchanged.

The sections explicitly marked current implementation describe this build. Retained target-design sections describe required future behavior unless the current implementation section states otherwise. Complete source, contracts, test evidence and original documents accompany this edition. Start at DOCUMENTATION-INDEX.md and TRACEABILITY.csv for exact locations and evidence boundaries.

## Current authority model

Identity authentication does not create tenant membership. Membership does not create a business grant. A role template does not grant authority until an explicit assignment is approved. Current access combines tenant state, principal and membership state, current authentication cutoff, scope, purpose, object restrictions and capability. Independent approval compares natural-person identities, including aliases.

Managed-tenant custody is separate from data access. An independent platform operator may approve activation, initial access or a recovery contact without receiving tenant membership. Initial administrative access is restricted to a fixed reviewed capability catalogue and bounded expiry. Business capabilities require subsequent normal review. The one-time bootstrap marker and revoked grants cannot be replayed into restored authority.

## Recovery and session boundaries

An owner nominates a distinct registered person with a verified account. The nominee verifies consent and an independent operator approves. All mutations require recent configured assurance. Current profile and authentication-cutoff checks are protected against the global account revocation path. Contact status and eligibility are distinct; account revocation, profile change, custody change or expiry can invalidate evidence without deleting its history.

A recovery contact receives no reset, custody, membership or data privilege. The owner becoming unavailable has no operator bypass in this build. Contact membership revocation is not automatically relationship revocation; a full departure process must explicitly account for both. Actual unavailable-owner recovery and factor replacement remain pending.

Own-session inventory, individual revocation and global session revocation are implemented locally. Production federation, provider logout, refresh-token revocation, shared-device safeguards and action-bound step-up remain unqualified. Native database role topology and distributed revocation propagation still require production-like tests.

## Retained requirements and target design

The following baseline sections retain their requirement IDs and intended behavior. Implementation status is governed by the current profile above and the accompanying traceability register. Planned components are not represented as deployed services.

## 1 Subjects and roles

| Template | Purpose | Restriction |
| --- | --- | --- |
| OWNER | Tenant custody, eligible owner transfer and bounded administration | Restricted data, review and privacy execution require their own grants. |
| TENANT_ADMIN | Identity, membership, grants and connection administration | Cannot exceed issuer authority or approve authored work. |
| MEL_ADMIN | Measurement setup, form publication, period close and report publication | Each sensitive action requires its distinct grant and prerequisites. |
| PROGRAMME_MANAGER | Programme lifecycle, work and assignments | Restricted participant fields and finance remain separately governed. |
| AUTHOR | Draft observations, evidence, reports and other permitted work | Cannot approve their own material. |
| REVIEWER | Approve, return, reject and verify eligible independent candidates | No implicit publication or period-close authority. |
| ENUMERATOR | Assigned forms, local capture, uploads and synchronisation | Assignment and device lease restrict records and fields. |
| DATA_STEWARD | Imports, mappings, datasets, quality and source correction | Exceptions and approval require independent authority. |
| ANALYST | Permitted datasets, dashboards, evaluation and AI-assisted drafts | Scope-safe derivation and separate export capability. |
| FINANCE | Funding, budgets, transactions, exchange rates and allocations | Does not obtain general participant identifiers. |
| PRIVACY | Verified cases, holds, purpose, disclosure and privacy execution | Plan approval, independence and per-store authority apply. |
| OPERATOR | Platform health, approved limits and service administration | Metadata only unless an independent scoped support grant exists. |
| SUPPORT | Request and exercise a specifically approved support session | Maximum 60 minutes; exact capability and object scope. |
| SERVICE | Explicit owner-bound integration and scheduled commands | No interactive human approval or broad inherited authority. |
| EXTERNAL | Eligible invitations and scoped shared information | Time-limited membership and disclosure conditions. |

A person may hold several tenant memberships and several role templates. Natural-person identity remains stable for independence checks. Two logins or two memberships belonging to the same person do not create an independent reviewer. Service identities have an accountable human owner and backup owner, a declared scope, credential expiry and an explicit permitted-command set.

Platform operators see service metadata by default. Tenant ownership permits custody and administration but does not automatically expose restricted participant identifiers, approve authored evidence, or execute privacy decisions. Support staff require a separately approved, purpose-bound, short-lived grant. AI has no authority-bearing role; its tool catalogue contains only permitted draft operations on behalf of the authenticated requester.

## 2 Policy evaluation order

Resolve and verify identity. Resolve the requested tenant and membership. Check tenant lifecycle, active membership and expiry. Require the exact capability for the operation and match the requested object, programme or assignment scope. Apply purpose and classification rules. Check fresh assurance where required, current subject and policy epochs, natural-person independence, current lifecycle and expected revision. Produce the audit obligation before committing an allowed effect.

All applicable checks must allow the action. Absence of an explicit grant denies it. A higher-level organisation relationship is not an implicit permission relationship. Scope inheritance is represented by versioned policy and explicit memberships; a missing scope is never interpreted as tenant-wide access. A custom role can combine capabilities only within the issuer's own grantable authority and the separation rules.

Invitation acceptance is the narrow pre-membership exception. The signed-in identity must match the tenant-bound, unexpired, unconsumed invitation; the inviter must still have authority. Consuming the token and creating or activating membership occur atomically. A successful token match does not grant capabilities beyond the invitation's approved scope.

The preparation evaluator takes trusted server-derived context. It must never be exposed as an endpoint that accepts caller assertions such as scope_match or membership_active. Those booleans are outputs of the implementation's resolvers and policy queries.

## 3 Grant structure and lifecycle

A grant contains tenant, subject, exact capability, scope version, start, expiry, issuer, authority source, purpose where required, independent approval reference where required and policy revision. Grant issuance checks that the issuer can grant that capability over that scope for that duration. Server-owned issuer fields cannot be assigned by a generic input.

Membership status is Invited, Active, Suspended, Expired or Revoked under the FSD lifecycle. External memberships default to a maximum 90-day review window. Invitation tokens expire after seven days, are stored as hashes, and are single use; resending revokes the earlier token. Revocation increments the subject or policy epoch, stops new online operations within 60 seconds of platform receipt, and invalidates positive cache entries within 30 seconds.

Service credentials expire within 90 days in the baseline. Rotation allows no more than 24 hours of overlap. Suspending a person cannot silently leave schedules operating under their departed session. Transfer eligible work to an explicitly owned service identity or pause it. The final eligible tenant owner cannot be revoked without completed custody transfer or the controlled recovery procedure.

## 4 Field classification and purpose

| Class | Typical content | Access treatment |
| --- | --- | --- |
| PUBLIC | Approved disclosed aggregates | Specific disclosure artifact and audience rules still apply |
| INTERNAL | Programme configuration and ordinary work | Current tenant membership and relevant scope |
| CONFIDENTIAL | Unpublished results, finance and evaluations | Explicit domain capability and declared scope |
| RESTRICTED | Direct identifiers and sensitive individual records | Explicit field permission, approved purpose, qualified device and current handling basis |

Classification is attached to fields and artifacts, not inferred from the screen they appear on. A permitted report does not make all its source observations readable. Derived outputs inherit relevant restrictions and undergo disclosure checks. A suppressed value is omitted from API fields, chart metadata, hover text, download payloads, logs and model context. Displaying an asterisk over a retained hidden value does not protect it.

Participant direct identifiers use the separate sensitive store and an authorised decryption path. Bulk export has its own capability, purpose, manifest and audit trail. Export scope is rechecked while producing and downloading the artifact. Public sharing is disabled by default; approved small-cell and complementary suppression rules apply to the cumulative disclosures, not just one table.

## 5 Separation of duties

The reviewer must be currently eligible and independent of all material authors of the exact candidate revision. Delegation preserves both real and effective actor and does not erase a conflict. Changing the candidate after review produces a new candidate and invalidates approval for the changed content. No bulk approval route may bypass per-candidate independence.

Period close requires complete obligations or reviewed exclusions, approved values, qualified evidence, fixed definitions and explicit close capability. Restatement requires reason and independent approval, and produces a new snapshot. Report publication requires approved report revision, authorised disclosure, audience and publication capability. A reviewer role alone does not automatically include period close or publication.

Support approval must come from a different eligible identity than the requester. The grant names exact capabilities, objects, purpose and expiry, capped at 60 minutes. Sensitive support actions use fresh assurance and an audit record. A general operator role cannot manufacture its own support approval. Privacy approval and execution preserve the authorised decision and store plan hash; changing the plan invalidates its approval.

## 6 Sessions and assurance

Ordinary application sessions expire after eight hours absolute or 30 minutes idle. Privileged sessions use a 15-minute idle bound. Sensitive actions require assurance within five minutes. Idle and absolute timeout are evaluated on the server; a browser timer is explanatory feedback. Federation logout, account suspension and recovered credentials revoke the relevant application sessions.

Recovery avoids account enumeration and cannot bypass enterprise federation policy or natural-person independence. A recovered administrator must re-establish strong authentication before issuing grants or transferring custody. A changed email address is verified before it receives pending sensitive notices. The release qualification checks session fixation, cross-site requests, token confusion and conflicting credentials.

## 7 Offline authority

An ordinary offline package lasts at most 24 hours; a restricted package at most eight hours on a qualified managed device. The signed manifest binds tenant, person, device key, assignment scope, form revisions, fields, policy epoch and expiry. A trusted server time anchor plus monotonic elapsed time controls local unlock. Clock rollback, reboot without trusted continuity or account switching locks sensitive content until renewal.

Online revocation cannot erase information already delivered to an offline device. The bounded lease and device controls define the residual exposure. Reconnection checks current membership, assignment, purpose and form compatibility before admitting writes. Expired or revoked authority produces a visible recovery route without falsely reporting that a local draft reached the server.

## 8 Access loss and derived artifacts

On loss of authority, stop active sensitive operations at their defined boundary, clear restricted client caches and invalidate job or report downloads. A queued task rechecks the requester and service authority before each consequential effect. Historical approval remains in the audit record while present access to its content can be restricted.

Mediated downloads reauthorise each request, range and bounded stream interval. Do not hand out a long-lived raw storage URL that bypasses revocation. Bytes already delivered outside the controlled system cannot be recalled; the sharing register records those disclosures and their handling obligations.

## 9 Verification and change control

The capability inventory covers every API operation. Its role matrix identifies allowed starting templates, assurance, independence, purpose and field filtering. Explicit positive fixtures accompany each role, with cross-tenant, cross-programme, expired, revoked, self-approval and purpose-denied negatives. Database tenant tests and application scope tests are separate gates.

Changes to templates or policy are versioned, previewed against affected memberships and artifacts, and audited. Sensitive authority changes cannot be bundled into an unexplained configuration import. The access simulation and certification features retain their FSD release assignments. A failed or unavailable policy resolver denies sensitive effects rather than relying on an unbounded cached allow.
