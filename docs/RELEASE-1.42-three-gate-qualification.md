# Release 1.42 — local journey, refusal and recovery qualification

## Delivered

The 56-story review cohort now has an explicit candidate test-node map in
`docs/acceptance/RELEASE-1.42-THREE-GATE-TEST-MAP.json`. It identifies bounded
positive, refusal and recovery journeys for 49 stories. Seven AI use cases remain
reserved-disabled: APL-533, APL-535, APL-537, APL-538, APL-597, APL-601 and APL-541.
Passing components behind a substituted test policy cannot qualify their external
user journeys.

New dashboard journeys cover lower-is-better overachievement with target labels,
stale source detection across repeated fetches followed by recalculation and a
locked snapshot, and exact-version qualified portfolio rankings. Recovery probes
exercise invalid selectors, corrected numeric submissions, closed request
refusals, exact retries, restored source authority, renewed presentation leases,
and manual calculation while an AI configuration remains contained.

Daily advisory-budget tests receive a new disposable workspace instead of
deleting or backdating request history or changing the limit. The cross-workspace
dashboard test revokes its temporary membership after the journey, preserving
later tests' cross-tenant preconditions.

## Contract and persistence

Component qualification exposed invalid row-update locks on immutable AI
suggestions, detection tasks, findings and action proposals. The code now reads
them under the existing tenant advisory lock and uniqueness constraints. No
UPDATE privilege is added. Action proposals and proactive findings obtain
classification from the currently authorized registry entry; immutable revisions
do not contain that field.

The existing closed WorkItem draft contract is now registered in the ordinary
command dispatcher; its implemented API export and generated onboarding access
profile are synchronized. Live tests exercise creation, authority refusals and
exact retries without duplicate writes.

No migration, DTO, policy activation, provider request, production identity or
spending change is introduced. IR-1.42-22 records the product repair; its human
confirmation remains empty.

## Evidence and limits

Raw local results, including failures, are retained under
`docs/evidence/candidate-1.42/three-gates-20261016/`. Evidence must bind the tested
source and explicit test nodes. A suite count does not establish every one of the
cohort's 209 scenarios or 364 assertions, native concurrency, browser behavior,
hosted CI, independent approval, staging or product-owner acceptance.

The earlier full run reported 2,628 passed, 9 failed and 229 skipped. After fixture
isolation, the next run reported 2,637 passed, 3 failed and 229 skipped; those three
failures were the newly introduced component tests before their immutable-read
repair. Subsequent focused runs and the final combined result are recorded in the
receipt, rather than treating those failed full runs as passes.

## Integration notes

- Cohort: the exact 56 IDs in the frozen acceptance manifest.
- Sources, acceptance criteria, old migrations and historical receipts are unchanged.
- Reserved activation requires an explicit decision and qualification of the actual runtime.
- Local test evidence does not supply independent human or owner acceptance.
