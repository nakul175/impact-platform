# Release 1.22 coding candidate — governed table pivots

FR-ANA-005 / APL-613 adds pivot preview and execution for an exact currently readable calculated-result revision pinned by a private dashboard widget. The closed statistic vocabulary is distinct count, sum and mean, each checked against the source calculation method; incompatible requests are refused with a labelled supported alternative.

Cells retain their value state, suppression and additivity. Multiselect, distinct and nonadditive categories explicitly explain that category totals may exceed the distinct grand total. Grand totals come from the governed result or unrounded eligible values and are never summed from displayed cells.

Previews above 100 cells route to a tenant-bounded `DASHBOARD_PIVOT` job. Jobs are idempotently requested, capped at ten open jobs per tenant, cancellable before worker claim and completed by the worker from the authority-checked exact-revision manifest. Migration 0094 adds only the due-tenant directory; existing tenant-fenced job storage and worker privileges remain in force.

## Positive journey evidence

The synthetic HTTP journey
`qualification/test_dashboard_pivots_live.py::test_analyst_previews_and_runs_a_source_based_dashboard_pivot_through_the_http_api`
passed on 16 October 2026. It creates and independently approves three observations, calculates their
exact result, saves a result-revision-bound dashboard through the API, then previews and executes the
regional pivot. Exact retry returns the durable outcome without another audit event or dashboard revision.
The observed regional cells are 12 and 3 while the governed source grand total is 15; the response
explicitly records that the grand total comes from eligible source semantics rather than displayed
cells.

The write-side execution and cancellation audit receipts now include their server timestamp, so both
can produce an audit/outbox event without weakening operation-receipt idempotency. Synchronous
execution is proven. Async execution/cancellation is implemented but is not exercised by this small
positive journey; CI, independent review, merge and deployment remain separate gates.

## Integration notes

- Story: APL-613 / FR-ANA-005.
- Positive preview and synchronous execution journey: locally passed; no acceptance, CI or deployment movement.
