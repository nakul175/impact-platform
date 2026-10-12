# Release 0.43 candidate — governed diagnosis collaboration

Status: **coding-only candidate; untested, unreviewed, unmerged and undeployed**.

## Delivered in code

US-DX-04 / APL-365 lets several staff contribute to one existing Draft diagnosis. A lead binds an
existing governed member invitation to explicit problem IDs, sections and one of three provisional
contribution roles. An accepted invitee can submit an immutable scoped proposal. The lead accepts
or rejects it against the exact diagnosis revision; acceptance creates a new revision of the same
diagnosis and never creates a split diagnosis. Completed diagnoses remain frozen.

Invitation delivery reuses the existing member-invitation outbox. The collaboration record reports
queued, delivered, failed, expired, revoked or accepted from existing durable evidence. It does not
claim that an email provider delivered a message without provider evidence.

## Security and persistence

- Build 0.43, domain API 1.34, derived schema 49.
- Migration 0049 adds forced-RLS, tenant-fenced, insert-only assignment, contribution and decision
  registers. It registers the generated future/bootstrap access profile without activating it for
  existing tenants.
- Contributors cannot edit diagnosis heads. Patch fields are checked against the immutable
  assignment, accepted membership and exact base revision. Leads re-authorise under the tenant lock.
- Operation receipts preserve exact retries; changed-payload reuse is refused.
- The browser exposes invitation assignment, proposal submission and lead decisions without storing
  collaboration data locally.

## Provisional product semantics

The role names and field mapping are implementation defaults pending owner confirmation:
`PROBLEM_OWNER` may propose descriptions/affected areas, `EVIDENCE_CONTRIBUTOR` evidence fields,
and `PRIORITISATION_CONTRIBUTOR` priority order. Existing member invitations remain the identity
onboarding boundary. These defaults are not accepted product semantics or human certification.

## Deferred qualification

Per the owner's coding-only batch instruction, no test, lint, type check, browser run, PostgreSQL
qualification, CI, merge or deployment was performed. Before combined qualification, confirm the
role taxonomy, exercise provider delivery and membership acceptance, test revocation/concurrency,
run migration upgrade/recovery and complete the required release and human gates.
