# Release 0.4.0 — governed measurement changes

Build 0.4.0 · API 1.5.0 · additive migration 0007 · 26 September 2026.

## Delivered behavior

The Change requests workspace supports draft proposals, editing returned requests, submission and independent review for approved observations, approved collection plans and active indicator responsibilities. A proposal records the target kind, target identity, exact target revision, reason and a closed set of proposed fields. The approved original remains effective until approval commits. Rejection and return do not replace it.

Observation amendments support decimal values, numerator/denominator pairs, value state and source version through the API. The browser edits numeric fields and source version already present on the approved record. Source identity, indicator identity, event time and approval state cannot be supplied as changes. Calculated actuals remain read-only. A correction invalidates live freshness checks on previous results without rewriting those immutable result revisions. Automatic background recalculation is not implemented.

Plan amendments may change titles, labels and due dates or add obligations. Existing source pairs cannot be removed: governed exclusions and their evidence are a separate pending capability. The effective plan binding advances only after independent approval; previously calculated results keep the old plan pin and become stale. Removing assignment-only fields from the semantic configuration comparison lets approved responsibility changes coexist with the approved measurement plan; population, programme and definition changes still invalidate that pin.

Responsibility changes revalidate current membership, unexpired tenant capabilities and collector/reviewer natural-person independence. Neither proposal/target content authors nor the new assignment recipients can approve. Changing the reviewer updates pending observation review stages atomically while preserving the submitted candidate revision and attribution of existing decisions. Old workflow revisions can no longer be used to decide. The departure inventory, connectors, credentials, schedules, escalation and other task types remain pending.

## HLD and LLD delta

- `changes_contracts.py` adds five closed domain endpoints under `measurement-changes`: collection/item reads, create, patch and submit. Review uses the existing workflow decision endpoints. The implemented API export now contains 88 domain operations.
- `changes.py` validates target visibility, proposing authority, exact revision and lifecycle, then delegates measurement-specific checks. Proposals are a distinct `MeasurementChange` aggregate stored in the existing registry/revision model.
- `Service.submit` records proposal and target natural-person authors in the workflow independence set. `Service.review` applies an approved proposal in the same tenant-serialized transaction as the decision, audit, outbox and retry receipt.
- Migration 0007 preserves all preceding migration bytes. It adds the registry type and the append-only `measurement_change_effect` table with tenant/object/revision foreign keys. Forced row-level security protects the effect table. The application role has SELECT/INSERT but no UPDATE/DELETE there. Only the plan revision column receives UPDATE authority on the effective binding.
- Approval writes an immutable target revision, an effect linking the before/after revisions, and a target-change audit/outbox event. It retains proposal authors as content authors. A second request based on the old target revision fails atomically. Replaying the identical successful decision returns its receipt without adding another effect/event.
- `ReviewCandidate` has a typed optional current target so the reviewer can compare effective content with the proposed fields. Both target and proposal read permissions are enforced. Stale proposals can be returned or rejected; approval rechecks their exact target revision.
- `Changes.tsx` offers explicit measurement/plan/assignment forms. Resource loading is bounded at 1,000 entries and fails explicitly rather than silently omitting selectable data. The request form captures an expected revision; a stale returned draft must be edited and resubmitted against the refreshed target.

## Qualification and limits

Executed evidence is retained in `docs/evidence`. Application tests cover preservation until approval, independent authorship, conflicting corrections, plan binding changes, obligation-removal denial, cross-tenant and scoped denial, forced RLS, assignment recipient denial, pending-review reassignment, and idempotent application with one target event. Browser coverage includes correction submission, current-versus-proposed review, approval and mobile layout in addition to the existing measurement setup flow.

Latest executed results: **207 application tests passed**, one offline integration test deliberately deselected because offline sync is not implemented; **143 separate reference checks passed**; **34 Chromium scenarios passed** (8 core, 12 administration, 14 measurement/amendment). TypeScript/Vite build and Python/TypeScript formatting/lint passed. Reference checks exercise the preserved specification model and are not counted as application implementation tests.

Repeated regression runs exposed intermittent PGlite protocol failures and inconsistent reads. Inspection found a reused response buffer across asynchronous filesystem work and socket callbacks that were not serialized. The local development socket now serializes protocol packets and copies responses before awaiting filesystem synchronization. A mixed connection-handoff regression exercises administrative reads, tenant reads and cross-tenant denial. Native PostgreSQL operational and concurrency qualification remain separate open gates; the local transport workaround is not used in production.

One administration browser run still returned an internal PGlite error after that mitigation. The final complete application and administration browser runs passed, but that does not prove the embedded engine's intermittent failure mode is fully resolved. Treat native database qualification and repeatable harness stability as open release gates. No failed gate is counted as a passed test in the latest evidence files.

No official period-close snapshots, published report replacement or privacy restatement is introduced. Approved records with a non-open matching period are rejected for ordinary correction; that is a guard, not a completed period-close feature. The browser does not yet edit observation value states. Exclusion evidence, bulk changes, dry-run impact inventories, notifications and automatic recalculation remain open.

## Remaining product scope

`COMPLETION-LEDGER.json` retains every original requirement and acceptance criterion and records conservative implementation status. Database tables, reference models and design-only OpenAPI paths do not count as implemented features. The full product and production release gates remain incomplete.

Next implementation order: governed period-close preview/lock and restatement; frozen reporting packages and export; ingestion and quality workflows; reusable planning/frameworks; evidence, forms and offline collection; integration workers and scheduled operations; analytics, evaluations, finance and governed AI. Identity, privacy, security, observability, disaster recovery and accessibility qualification must advance with those modules. Hosting, live identity-provider credentials and managed services are external deployment inputs, not a reason to mark unfinished local coding complete.
