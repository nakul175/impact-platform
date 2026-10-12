# Release 0.79.0 candidate — organisation agreement coverage

## Delivered

US-CM-09 / APL-431 records one current master-agreement and DPA bundle per organisation and makes that bundle a hard prerequisite for every new AI-solution deployment attestation. Each deployment pins the exact bundle revision, records partner terms as master-agreement flow-down and cannot request a separate contract or second DPA.

## Contract and persistence

`POST /v1/tenants/{tenant_id}/agreements` records authorised references, effective date and explicit flow-down confirmation. `GET /v1/tenants/{tenant_id}/agreements` returns the one current bundle and all covered deployments. Schema 71 preserves immutable bundle revisions, the current pointer and tenant-fenced deployment coverage. The existing deployment action records coverage atomically before its new plan revision commits.

## Limits

The platform records references and an authorised confirmation; it does not draft terms, validate signatures, provide legal advice or replace legal/privacy review. Historical deployments created before this candidate are not silently backfilled. A governed review must decide whether and how to attach them.

## Reproduction

This is a coding-only candidate. Formatting, lint, compilation, contract generation, JSON parsing and static release-review validation are source checks. Tests, CI, merge, staging, legal/privacy review and owner acceptance are deferred to combined qualification.

## Integration notes

Keep this story in a separate commit and ledger entry. Qualification must cover missing/expired/future bundles, tenant isolation, current-authority loss, bundle revision changes, exact retries, atomic deployment rollback and historical compatibility before merge or deployment.
