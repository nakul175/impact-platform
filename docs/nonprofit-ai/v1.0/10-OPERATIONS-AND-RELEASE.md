# Nonprofit AI Enablement Operations and Release

Edition 1.0 · 5 October 2026 · Proposed operating extension

## Operating baseline

The review baseline is commit 36073f1, build 0.30.0, schema 35 and domain API 1.21.0. This documentation task does not merge or deploy it. Existing deployment scripts, backup and restore procedures and control-plane restrictions remain authoritative. Service levels, support hours, recovery objectives and retention are owner decisions under DEC-NPA-009 and 010; no new numeric target is assumed.

The directory, readiness assessment, practical learning and shared draft plans can operate without a live AI generation provider. The advisory feature is disabled by default. Local provider credentials remain outside version control; the selected provider project reported exhausted credits. There is no working live-generation acceptance result and no staging credential installation is claimed.

## Roles and readiness

Before a pilot appoint an organisation sponsor, adoption lead, data owner, support owner and release owner. Assign distinct people for consequential review where independence applies. Review the allowed synthetic tasks and quality criteria, language and accessibility needs, contact route, data boundary and provider budget. Record approved scope and unresolved dependencies in the decision register.

Existing tenants need reviewed capabilities within their approved ceilings. Updating the initial-access profile does not automatically grant access. Pending requests based on an earlier hash may need reproposal; an already applied ceiling needs a governed widening process. Do not edit grants directly to make a demonstration work.

## Configuration and monitoring

Use the existing secrets/configuration channel, separate runtime and migration database roles and the repository's deployment guide. Never put a key in a browser bundle, document or evidence file. Enable provider generation only after approved funding, model access, deployment configuration and a bounded synthetic end-to-end check. A disabled provider must leave core planning functional.

Proposed dashboards should report safe aggregate request counts, attempt-limit denials, failed and in-flight claims, provider duration and availability, plan write conflicts, delivery backlog age and service health. Do not include goals, prompts or generated text in logs. Current code does not provide a monetary budget dashboard or persisted token accounting; those require additional implementation.

Separate transport acceptance, intent recorded, externally acknowledged, reconciled and business-approved states in future services. A worker success must not imply supplier acceptance or independent delivery approval. Aggregate monitoring must not broaden private organisation access.

## Failure and recovery playbook

| Condition | Operator action | Verification before resuming |
|---|---|---|
| Advisory disabled or unconfigured | Leave deterministic guide available; show availability and configuration reason safely. | No generation request is sent by the disabled UI; authorised planning/save still works. |
| Provider unavailable or credits exhausted | Stop repeated live checks; report the safe failure; resolve funding through the owner. | Approved funded synthetic call, timeout/failure handling and replay checks; no leaked raw response. |
| Ambiguous advisory outcome or in-flight claim | Investigate using tenant/request/correlation IDs and approved access. Do not automatically generate again under a fresh ID. | Establish whether a result exists and whether any external call completed. Proposed recovery procedure must prevent repeat spending. |
| Lost plan save response | Retry the same operation ID and unchanged payload under current authority. Keep newer local edits unsaved until the first result is resolved. | Original authorised receipt replays; changed payload conflicts; no additional revision. |
| Stale shared plan revision | Preserve the user's working copy; fetch current authorised revision and let the user reconcile. | New save is explicit and based on the selected current revision; no silent overwrite. |
| Access revoked or tenant suspended | Deny the next operation and replay; clear stale client state during tenant change. | Reauthorisation uses current membership, capabilities and lifecycle state. |
| Database or migration failure | Follow the existing deployment recovery guide; retain the previous artifact and logs without secrets. Do not run a destructive down migration. | Migration ledger and checksums, role/RLS smoke, schema-aware application health, backup/restore evidence where required. |
| Target supplier delivery or payment ambiguity | Pause dispatch/financial action, retain intent and reconcile external acknowledgement through the approved adapter. | Proven external idempotency and reconciled outcome. R3 financial operation remains disabled until its model is approved. |

## Release gates

Before a release proposal, confirm the exact commit, contract/build/schema versions, additive migration checksums, changed capability profile and affected tests. Record local failures and skipped checks honestly. Documentation-only work does not execute or substitute for runtime qualification.

The existing four hosted jobs are mandatory for merging: local-reference-and-browser, live-identity-provider, native-postgresql-gate and container-stack. Obtain the owner's approval before paid CI use. Every required job must pass for the reviewed commit and the owner must confirm the merge. Main deploys itself, so merging is a deployment decision. Earlier approval of another release does not approve this release.

After an approved deployment, check health/build/schema, identity login, reviewed tenant access, directory/readiness, plan create/reload/retry, revoked access and provider-disabled behavior. If generation is explicitly funded/enabled, use one agreed synthetic smoke case and inspect its bounded, draft-labelled result and safe replay. Do not use real beneficiary records to demonstrate it.

## Pilot acceptance and handover

Run the specified UAT journeys with representative organisation users against the approved scope. Record task context, observed outcomes, defects and the named human decision. Self-recorded learning progress and pilot checklists cannot substitute for assessed competence or accepted delivery. Link approved evidence to the traceability matrix rather than changing status because a document exists.

The handover package includes approved scope and decisions, configuration ownership, escalation contacts, outstanding defects, executed evidence, restoration/recovery procedures and restrictions on unsupported services. Refresh catalogue review dates through a controlled content change. Keep financial and integration services disabled where their policy or qualification is incomplete.

## Change and rollback approach

Retain immutable prior revisions and approved snapshots. An application rollback must be compatible with the already applied additive schema; never remove migrations or rewrite ledger checksums. Corrections and new approvals are new revisions. If unsafe functionality must be stopped, use a reviewed feature/configuration control and verify core workflows and data visibility remain intact. Do not claim rollback removes disclosed external data or erases backups.
