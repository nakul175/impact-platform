# Release 0.44 candidate — diagnosis advisor review

Status: **coding-only candidate; untested, unreviewed, unmerged and undeployed**.

US-DX-05 / APL-366 adds a named, same-tenant natural-person advisor assignment for an exact
Completed diagnosis revision. The assigned advisor sees an oldest-first queue, records a durable
review start, publishes organisation-visible comments and can validate only the still-current exact
revision. A later diagnosis revision retains the historical event but reports the validation as a
previous-revision result. Validation never edits the diagnosis and is not owner acceptance,
publication approval, official MEL approval or deployment acceptance.

Migration 0050 adds forced-RLS, tenant-fenced, insert-only review request and event registers. The
new `ai.diagnosis.review` capability is provisionally mapped to REVIEWER in the governed future
bootstrap profile; it is not activated for existing tenants by the migration. The requester must
select an active same-tenant membership already carrying that capability. Diagnosis authors and the
completer cannot review their own work. Requests and actions use exact operation receipts, current
authority and exact diagnosis revisions.

The browser exposes an organisation review request/status/comments panel and an assigned advisor
queue with start, comment and validate actions. All comments are public to authorised organisation
readers; this candidate introduces no private annotation channel.

Provisional semantics requiring product confirmation: REVIEWER represents the Imprana Advisor;
cross-tenant advisor custody is deferred; comments are optional for validation; reassignment and
cancellation are deferred; one new diagnosis revision requires a new request. Per the owner's batch
instruction, no tests, lint, type checking, database migration run, CI, merge or deployment occurred.
