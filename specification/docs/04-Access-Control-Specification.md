# Impact Management Access Control Specification

This specification defines how users, external partners, service identities, support staff and platform operators receive and exercise authority. The capability catalogue is generated from the API contract so every operation has an explicit policy entry. Role templates provide starting grant bundles. Authority comes from a current scoped grant and all contextual checks, not from a role label in the browser or identity-provider token.

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
