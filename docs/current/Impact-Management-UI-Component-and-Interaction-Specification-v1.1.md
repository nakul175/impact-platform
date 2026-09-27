# Impact Management UI Component and Interaction Specification

Version 1.1   27 September 2026

This specification turns the 30 existing wireframe screens into implementation contracts for the web and Android clients. It defines reusable components, navigation, input behaviour, permission-aware states and recovery. The standalone wireframe HTML remains the visual reference; this document defines what its production interactions must do.

## Release interpretation

Documentation edition 1.1 is reconciled with application build 0.12.0 on 27 September 2026. The document edition and application build use different version sequences. The original business requirements and their acceptance conditions remain authoritative. No requirement has been removed or weakened to match the current code.

The application is a development delivery. The requirement ledger records 74 PARTIAL and 233 PENDING requirements, with zero fully accepted. PARTIAL means a bounded implementation and some evidence exist, not that all acceptance conditions are satisfied. PENDING means the requirement has no accepted implementation coverage in the ledger; a read-only surface or reference example does not establish delivery.

Recorded qualification contains 325 application checks, 143 design-reference checks and 81 browser checks. One expired-offline-grant test is deselected and is not a pass. Local integration uses fresh in-memory PGlite PostgreSQL 17.5 with serialized transactions. Native PostgreSQL concurrency, live identity-provider assurance, disaster recovery, load qualification and production acceptance remain open.

The original BRD and FSD use R1, R2 and R3 requirement assignments. The later 16-stage delivery roadmap is an implementation sequence. Roadmap stage 1 and baseline R1 are different groupings; neither is complete. Requirement release assignments remain unchanged.

The sections explicitly marked current implementation describe this build. Retained target-design sections describe required future behavior unless the current implementation section states otherwise. Complete source, contracts, test evidence and original documents accompany this edition. Start at DOCUMENTATION-INDEX.md and TRACEABILITY.csv for exact locations and evidence boundaries.

## Current interface coverage

The 30 baseline screens remain the intended product inventory. SCREEN-COVERAGE.csv maps each to current coverage and source files. The updated HTML prototype labels proposed screens and adds explicit current tenant lifecycle, initial-access, recovery-contact and account/workspace flows. A simulated prototype action is never evidence of backend authorization.

The compiled client includes sign-in, permitted workspace selection, programme and measurement setup, collection, review, calculation lineage, close and restatement, report and publication workflows, recalculation tasks, people and access administration, roles, groups, organisation units, personal preferences and sessions, plus managed-tenant control-plane panels.

## Current onboarding and recovery interaction

The Tenant lifecycle panel displays readiness and lifecycle state. Recovery contacts opens a private participant/operator inbox with masked identity evidence and history. The owner nominates a contact and expiry; the nominee sees the exact consent action; an independent operator approves. Pending replacements keep the old approved contact effective. The UI distinguishes stored state from current eligibility and shows verification, approval and expiry times. Development verification is visibly labeled synthetic.

Initial access is a separate panel. Owner proposal, nominee acceptance and operator provisioning must be visible as distinct steps. The tenant selector preserves the user's selection across asynchronous session refresh. Account custody and recovery-contact status do not imply programme permissions.

## Interaction regression and accessibility limits

Workspace settings now waits for capabilities before selecting its first permitted section and does not reset a valid selected tab. The browser regression holds the initial capability response until navigation completes. Destructive and approval actions use a reason and explicit confirmation. Exact retries retain operation identifiers and stale revision conflicts require review.

Browser qualification covers eight workflow groups with mobile layouts at 390 pixels and no uncaught page errors. This does not establish complete WCAG conformance, keyboard/screen-reader coverage, localization or the baseline 360-pixel requirement. Prototype screen states and final production interactions still require the specified acceptance matrix.

## Retained requirements and target design

The following baseline sections retain their requirement IDs and intended behavior. Implementation status is governed by the current profile above and the accompanying traceability register. Planned components are not represented as deployed services.

## 1 Interface structure

The application shell shows the current tenant, programme where applicable, user's work context and navigation permitted for that context. The tenant selector is an explicit change of authority scope. Switching tenant cancels old requests, clears restricted view state and reloads permissions. Browser Back cannot restore another tenant's cached private page after access loss.

Use the wireframe palette: white surfaces, dark navy text and restrained blue-grey separators. Status text accompanies colour and icons. Body text defaults to 16 CSS pixels, with readable density options for analytical tables. Layout spacing follows a 4-pixel base with 8, 16, 24 and 32-pixel gaps. Focus indicators remain visible against both light and dark surfaces.

Ordinary forms work at 360 pixels wide. Between 768 and 1199 pixels, secondary panels collapse into explicit drawers or tabs. At 1200 pixels and above, comparison and lineage panels may appear alongside the primary content. Wide analytical tables use labelled horizontal scrolling and fixed identifying columns. Text is not shrunk to force the table onto a phone.

## 2 Shared components

| Component | Contract | Acceptance |
| --- | --- | --- |
| Application shell | Tenant and scope, navigation, account menu | Current context is always visible; tenant switch clears old state. |
| Data table | Sort, cursor paging, row selection and bulk actions | Keyboard-accessible headers; hidden totals omitted; selected count is explicit. |
| Filter bar | Typed filter terms and saved views | No match differs from no data; changing scope resets incompatible filters. |
| Record header | Title, revision, owner, lifecycle and permitted actions | Status text is explicit; stale revisions cannot be silently acted upon. |
| Field control | Label, unit, requiredness, hint and error | Linked error summary; correct input type and no placeholder-only labels. |
| Decimal input | Canonical decimal string and locale display | No float coercion; missing and zero remain distinct. |
| Date and period selector | Source zone, reporting zone and interval | Exclusive end semantics; retain zone and reject ambiguous parsing. |
| Choice and repeat editor | Stable choice codes and row IDs | Accessible add/remove, bounded repeat count, row error summary. |
| File uploader | Progress, per-part receipt, manifest and scan state | Transfer completion is distinct from CLEAN; resume queries server receipts. |
| Save status | Local draft, pending server confirmation and receipt | Never show server success from a local write or lost response. |
| Version comparison | Base, candidate and current permitted fields | No hidden field leaks; changed candidate invalidates confirmation. |
| Review panel | Candidate, evidence, author conflict and decisions | Independent identity and current authority; reasons and audit receipt. |
| Result card | Value state, unit, approval, freshness and coverage | Suppression hides raw payload; chart has a data equivalent. |
| Lineage explorer | Included/excluded sources and rule version | Scope-safe traversal; clear contribution identity and exclusion reason. |
| Job progress | Stage, known denominator, outcomes and cancellation | No invented percent when total unknown; committed items remain visible. |
| Confirmation dialog | Exact scope, version, effect and recovery | Focus trap and return; pending action preserves operation identity. |
| Notification centre | Safe reference, event class, due date and read state | Current authority checked on open; no sensitive email content by default. |
| Error boundary | Safe message, correlation reference and recovery | Retain safe drafts; never show stack traces, raw queries or tokens. |
| AI proposal panel | Sources, exact diff, expiry and confirmation | Target/source changes invalidate proposal; only typed draft effects. |
| Offline lease indicator | Device authority, trusted expiry and last sync | Locked state is enforceable; stale identity or time trust is explicit. |
| Disclosure preview | Audience, purpose, cell suppression and expiry | Prior slices considered; approval version and download rights are fixed. |
| Accessible chart | Typed bindings, axes, legend, filters and table | Colour is supplementary; suppressed data absent from every representation. |

Every component exposes semantic name, role, state and validation message. Use native controls when they provide the needed interaction. Complex tables distinguish row selection, opening a record and bulk commands. Keyboard users can reach every action without dragging. Dialogs trap focus while open and restore it to the triggering control after close.

## 3 Common state contract

Loading means an operation is in progress and the current action cannot be duplicated accidentally. Empty means the authorised collection has no records. No filter match retains filters and explains how to clear them. Denied contains no private content. Stale identifies the changed source or configuration. Partial identifies incomplete coverage. Failure gives a safe recovery route and correlation reference.

Validation errors appear beside fields and in a focused summary linked to each field. A conflict compares only permitted fields and states which revision is current. A saved local draft is labelled Saved on this device; only a durable server receipt permits Saved to server. Submitted, Approved, Closed and Published are distinct business states and never inferred from a successful HTTP transport alone.

After a mutation, keep its operation ID and exact payload until the outcome is known. A timeout leads to receipt lookup and safe retry using the same logical operation. Editing the data creates a different operation. Buttons may prevent accidental double clicks, but the server's idempotency rules provide the actual duplicate-effect protection.

## 4 Screen contracts

The routes below are client route patterns. API paths and capability names are defined separately in the OpenAPI and access matrix. Each screen receives a server-computed view model containing visible fields, allowed actions, revision, state and scope label. Hidden buttons do not establish security.

### UI01 Sign in and recovery

Route: /sign-in. Primary actor: Member establishes identity.

Content: Identity method and recovery availability. Actions: Sign in, enterprise sign in, recover access.

Route to the configured identity provider and return through a verified callback; show safe feedback for unknown identities.

Do not enumerate accounts or bypass federation through recovery.

### UI02 Tenant switch and profile

Route: /tenants. Primary actor: Multi tenant member changes context.

Content: Current membership, tenant names, profile and sessions. Actions: Switch tenant, edit permitted profile, end session.

Reload scope and permitted navigation after a switch; clear the previous tenant view and requests.

Do not cache another tenant behind browser Back; identity changes require verification.

### UI03 My work

Route: /t/:tenant/work. Primary actor: Collector reviewer manager.

Content: Assigned tasks, due dates, review requests and job outcomes. Actions: Open task, filter, acknowledge eligible notice.

Open the exact object and revision context; distinguish overdue work from failed automation.

Only assigned or otherwise permitted work appears; notifications contain safe references.

### UI04 Tenant settings

Route: /t/:tenant/settings. Primary actor: Owner identity or policy admin.

Content: Versioned identity, region, retention and terminology settings. Actions: Preview change, save, promote configuration.

Show affected policy and work before applying; conflict on a changed configuration revision.

Prevent removal of final owner and activation without required policy settings.

### UI05 Members and grants

Route: /t/:tenant/access. Primary actor: Delegated identity admin.

Content: Members, role templates, scoped grants, expiry and effective access. Actions: Invite, change grant, suspend, revoke, transfer ownership.

Separate membership state from grants; show exact scope and expiry before sensitive commands.

Fresh assurance, issuer bounds and independent custody checks; no browser-assigned issuer.

### UI06 Programme registry

Route: /t/:tenant/programmes. Primary actor: Manager.

Content: Permitted programme registry and lifecycle. Actions: Create draft, filter, open, archive.

Preserve filters and cursor context; distinguish no records from no filter matches.

Creation is Draft; activation checks mandatory measurement and policy configuration.

### UI07 Programme workspace

Route: /t/:tenant/programmes/:id. Primary actor: Manager and partner.

Content: Programme overview, activities, risks, obligations and budget links. Actions: Edit draft, assign work, activate, archive.

Provide stable navigation between framework, indicators, work, results and reporting.

Material edits retain versions; archive previews unfinished obligations and schedules.

### UI08 Framework editor

Route: /t/:tenant/frameworks/:id. Primary actor: MEL administrator.

Content: Versioned nodes, relationships, completeness and comparison. Actions: Add node, link, reorder, compare, submit.

Offer graph and accessible tabular editing; validate cycles and missing definitions before review.

Published or reviewed meaning is preserved; a changed graph creates a new candidate.

### UI09 Indicator designer

Route: /t/:tenant/indicators/:id/design. Primary actor: MEL administrator.

Content: Unit, population, denominator, time meaning, source and targets. Actions: Edit, test calculation, compare, submit.

Make aggregation and comparability choices explicit; show sample inputs and expected result.

Block incompatible units, ambiguous denominators and invalid cumulative treatment.

### UI10 Indicator results

Route: /t/:tenant/indicators/:id/results. Primary actor: Reviewer or analyst.

Content: Periods, values, missingness, approval, coverage and lineage. Actions: Inspect contribution, compare periods, request correction.

Show official versus provisional, freshness and excluded contributions beside values.

No averaging displayed percentages; missing, zero and suppressed values remain distinct.

### UI11 Form designer

Route: /t/:tenant/forms/:id. Primary actor: Instrument owner.

Content: Fields, logic, repeats, language and compatibility. Actions: Add field, preview path, test, version, publish.

Validate bounded expressions and dependency cycles; test requiredness and hidden-field handling.

Published instrument immutable; destructive changes require a new version and compatibility handling.

### UI12 Field assignments

Route: /t/:tenant/assignments. Primary actor: Enumerator.

Content: Minimal assigned tasks, form version and offline lease. Actions: Download package, open task, request renewal.

Show last server check, package expiry and on-device availability; keep identities minimal.

Expired or unqualified device cannot unlock restricted content.

### UI13 Collection form

Route: /t/:tenant/collect/:assignment. Primary actor: Enumerator or respondent.

Content: Published questions, answers, repeats, media and save status. Actions: Save locally, validate, submit.

Label on-device save separately from server receipt; preserve repeat row identity and typed answers.

No false submission success; required media and current assignment checks apply.

### UI14 Sync and conflicts

Route: /t/:tenant/sync. Primary actor: Collector supervisor.

Content: Per-record local state, server receipts, parts and conflicts. Actions: Sync, resume, view permitted diff, resolve through correction.

Recover lost acknowledgements by receipt; show each failure without obscuring successful items.

Never overwrite conflicting server revision or expose another author private fields.

### UI15 Import workspace

Route: /t/:tenant/imports/:id. Primary actor: Data steward.

Content: Source digest, locale, mapping, duplicate rules and row outcomes. Actions: Upload, preview, map, confirm commit, cancel.

Use a staged flow; bind commit to current preview hash and show atomic versus partial treatment.

Controlled replacement names exact scope; row totals reconcile and cancellation preserves accepted rows.

### UI16 Dataset catalogue

Route: /t/:tenant/datasets. Primary actor: Steward analyst.

Content: Schema, owner, classification, refresh and lineage. Actions: Inspect, map, derive, export where permitted.

Show source version, stale data and transformation chain before choosing a dataset.

Exports require separate authority; schema views cannot leak restricted sample rows.

### UI17 Quality queue

Route: /t/:tenant/quality. Primary actor: Steward reviewer.

Content: Issues by severity, rule, affected revision and owner. Actions: Correct, revalidate, request exception, review exception.

Keep a correction separate from dismissal; show expiry and scope of approved exceptions.

Blocking issues stop affected approvals or close; exceptions require independent authority.

### UI18 Participant workspace

Route: /t/:tenant/participants/:id. Primary actor: Assigned programme staff.

Content: Pseudonym, permitted identifiers, events, relationships and purpose. Actions: Record event, update permitted fields, record handling, restrict.

Default to pseudonymous views; disclose direct identifiers only for an authorised purpose.

Keep encrypted identifiers separate; withdrawal does not silently rewrite aggregate arithmetic.

### UI19 Evidence repository

Route: /t/:tenant/evidence. Primary actor: Author analyst reviewer.

Content: Evidence versions, provenance, scan and verification. Actions: Upload, inspect, quote, verify, download.

Distinguish transfer, scan, provenance and review states; citations pin exact evidence revision.

Quarantined bytes unavailable; downloads and previews recheck present permission.

### UI20 Evaluation workspace

Route: /t/:tenant/evaluations/:id. Primary actor: Evaluator.

Content: Question, method, source extracts, findings and limitations. Actions: Code extract, compare findings, draft recommendation, submit.

Connect each finding to sources and method; preserve disagreement and management responses.

Causal statements require justified method and review; AI suggestions remain labelled drafts.

### UI21 Review queue

Route: /t/:tenant/reviews/:id. Primary actor: Independent reviewer.

Content: Exact candidate, changed fields, evidence and independence. Actions: Approve, return, reject, delegate within policy.

Pin the candidate and reveal current blockers; require reasons as specified and preserve receipts.

Self-approval and changed-candidate decisions fail at server even when a button was visible.

### UI22 Dashboard editor and viewer

Route: /t/:tenant/dashboards/:id. Primary actor: Analyst manager viewer.

Content: Typed widgets, scoped filters, target version and source mode. Actions: Filter, drill down, edit layout, save version.

Provide data alternatives to charts; show partial/stale status and official/provisional mode.

Hidden cells and metadata remain absent; filters never expand authority.

### UI23 Report workspace

Route: /t/:tenant/reports/:id. Primary actor: Report author and approver.

Content: Template, snapshot, narrative, citations and numeric bindings. Actions: Draft, reconcile, submit, export, publish, withdraw.

Bind official numbers to result revisions; preview audience and expiry before publication.

Approval, disclosure and publication capability are separate; partial render is never an official download.

### UI24 Period close

Route: /t/:tenant/periods/:id/close. Primary actor: MEL manager and reviewer.

Content: Expected obligations, blockers, exclusions and snapshot manifest. Actions: Refresh readiness, review exclusions, close, restate.

Show the exact version set and outstanding blockers; return a close job and durable outcome.

Late changes invalidate readiness; restatement requires independent approval and a new snapshot.

### UI25 Integration administration

Route: /t/:tenant/connections/:id. Primary actor: Connection owner.

Content: Scope, secret reference, qualification, schedule and checkpoints. Actions: Test, activate, pause, rotate, run, inspect retry.

Show credential expiry and upstream permission health without reading back secret values.

Service owner and backup are required; retry rechecks destination, credentials and scope.

### UI26 AI workspace

Route: /t/:tenant/ai. Primary actor: Author analyst reviewer.

Content: Use case, allowed sources, citations, budget and proposals. Actions: Ask, inspect evidence, preview diff, confirm draft, cancel.

Display exact sources and target revisions; stale or expired proposals require regeneration.

No autonomous approve, publish, grant or deletion; unsupported consequential claims block use.

### UI27 Privacy and disclosure

Route: /t/:tenant/privacy. Primary actor: Privacy officer.

Content: Cases, verified requester, authority, holds, disclosure and store outcomes. Actions: Review, approve plan, execute, verify outcomes, release hold through authority.

Show per-store progress and held actions; distinguish partial completion and effective restriction.

Plan changes invalidate approval; public disclosure checks cumulative inference and download rights.

### UI28 Service operations

Route: /operations. Primary actor: Platform operator.

Content: Service metadata, tenant limits, incidents and support sessions. Actions: Inspect health, change approved limits, request or end support.

Separate platform health from tenant content; show support scope, approver and countdown.

Operator role has no default business content access and cannot approve its own support grant.

### UI29 Migration and exit

Route: /t/:tenant/migration. Primary actor: Implementation lead owner.

Content: Mapping, dry run, reconciliation, cutover and exit manifest. Actions: Run trial, inspect semantic diff, confirm cutover, export, close.

Compare values, periods, approvals and lineage; preserve a rollback or repair path.

Exit cannot skip holds; migration never fabricates historic human approval.

### UI30 Budget workspace

Route: /t/:tenant/finance. Primary actor: Finance authorised user.

Content: Funding, budget versions, transactions, exchange rates and allocations. Actions: Import transactions, revise budget, apply rate, allocate, review.

Show source currency and reporting currency separately; reconcile allocation total and rounding residual.

No silent overwrite of expenditure; reversals link the original and finance authority remains separate.

## 5 Forms and validation

Show labels, units, requiredness and examples before input. Validate format locally for fast feedback and repeat authoritative validation on the server. Preserve safe entered values after an ordinary validation failure. Clear restricted values when permission is lost. A language or locale change must not reinterpret stored decimals, choice codes or reporting periods.

Expressions in the form designer are edited with field references and supported operators. Show dependency and cycle errors before publication. Preview representative paths, repeats, missingness and translations. A published form is immutable; changes produce a new version and an explicit compatibility decision. Enumerators cannot silently upgrade an in-progress draft to a different instrument.

## 6 Review publication and destructive actions

Review screens pin the candidate revision, changes, evidence and independence status. Approve, Return and Reject require a clear action label and the FSD reason rule. A changed candidate disables the old decision panel and reloads the comparison. The server supplies the reason for an unavailable action without revealing hidden authors or fields.

Publication preview names the exact report version, audience, expiry, download rights and disclosure result. Confirmation returns a job receipt and then a publication outcome. Privacy execution preview lists stores, hold results, authority, scope and plan digest. Generic confirmation text such as Are you sure is insufficient for these actions; the interface identifies the concrete effect and affected scope.

## 7 Accessibility and localisation

Target WCAG 2.2 AA for the supported web workflows. The product's touch target default is 44 by 44 CSS pixels where layout permits. Text contrast, visible focus, heading structure, labels, error association and keyboard order are part of the component acceptance tests. Charts provide an equivalent data table; graph editors provide a tabular relationship editor.

Announce meaningful asynchronous changes through live regions without repeatedly reading a progress counter. Focus moves to the first blocking error or result summary at an appropriate boundary. Provide reduced-motion support. Test at 200 percent zoom and with the declared screen readers; automatic scans alone do not establish workflow accessibility.

All labels, errors, confirmations and recovery text use message keys with interpolation rules. Numbers and dates use locale presentation while retaining canonical storage. Text expansion, right-to-left layout where supported, translated form revisions and fallback behaviour are verified before that language is enabled. Untranslated safety or permission messages block the affected language's release.

## 8 Client state and testing

Separate server state, editable form state, local offline drafts and transient presentation state. Cache keys include tenant, object revision and relevant permission context. Restrict persistence of sensitive web content; session tokens remain in secure cookies rather than local storage. Android storage follows the bounded package and key-custody specification.

Test every screen's relevant states, a complete keyboard workflow, narrow viewport, long translations and access loss during a pending operation. Verify official numeric bindings in both visible UI and exports. The wireframe's role selector is a design-review control; it is not carried into the production permission system.

## 9 Reference

Wireframe screen IDs UI01 to UI30 and FSD UX, IAM, ACC, OFF and domain requirements. WCAG 2.2: https://www.w3.org/TR/WCAG22/. The component and screen inventories are also supplied as machine-readable JSON for implementation traceability.
