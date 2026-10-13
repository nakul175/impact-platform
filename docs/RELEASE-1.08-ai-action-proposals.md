# Release 1.08 coding candidate — inspectable action proposal and confirmation

FR-AI-010 / APL-541 adds a closed AI proposal route for one draft-only ordinary command: `CREATE_WORK_ITEM_DRAFT`. Generation pins the exact current Programme scope, exact current Evidence or CalculatedResult source revisions, tenant AI policy version, full before/after values and explicit consequences. The before value is null because the allowlist permits creation only. Generation validates the ordinary WorkItem payload and creates no domain side effect.

Confirmation is a separate request. The ordinary command dispatcher now supports optional internal pre/postcondition hooks while preserving every existing caller. Under the same tenant write lock and transaction, the proposal hook rechecks current proposal authority, current Programme and affected-source revisions, policy version, destination, language and safety state. The existing `create_work_items` command then rechecks its own current authority, validates the WorkItem again, writes its normal operation receipt and audit record, and atomically records the proposal confirmation.

The closed allowlist has no route for approved results, permission grants, publication, privacy deletion or independent decisions. A source, scope or policy change refuses confirmation without a domain write. The execution operation ID is generated once with the proposal, so an uncertain confirmation retry cannot duplicate the WorkItem.

Migration 0092 creates tenant-fenced, insert-only proposal, exact source-link and confirmation records. `ACTION_PROPOSAL` remains reserved-disabled until combined qualification activates it. Tests and CI remain deferred by owner request; this coding candidate is unmerged and undeployed.
