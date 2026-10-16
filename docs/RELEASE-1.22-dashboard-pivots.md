# Release 1.22 coding candidate — governed table pivots

FR-ANA-005 / APL-613 adds pivot preview and execution for an exact currently readable calculated-result revision pinned by a private dashboard widget. The closed statistic vocabulary is distinct count, sum and mean, each checked against the source calculation method; incompatible requests are refused with a labelled supported alternative.

Cells retain their value state, suppression and additivity. Multiselect, distinct and nonadditive categories explicitly explain that category totals may exceed the distinct grand total. Grand totals come from the governed result or unrounded eligible values and are never summed from displayed cells.

Previews above 100 cells route to a tenant-bounded `DASHBOARD_PIVOT` job. Jobs are idempotently requested, capped at ten open jobs per tenant, cancellable before worker claim and completed by the worker from the authority-checked exact-revision manifest. Migration 0094 adds only the due-tenant directory; existing tenant-fenced job storage and worker privileges remain in force.

## Positive journey evidence

The synthetic HTTP journey
`qualification/test_dashboard_pivots_live.py::test_analyst_previews_a_source_based_dashboard_pivot_through_the_http_api`
passed on 16 October 2026. It creates and independently approves three observations, calculates their
exact result, saves a result-revision-bound dashboard through the API, and previews the regional pivot.
The observed regional cells are 12 and 3 while the governed source grand total is 15; the response
explicitly records that the grand total comes from eligible source semantics rather than displayed
cells.

The same run found a separate blocker in the write-side `run-pivot` action: its audit receipt omits
`saved_at`, so the action currently returns 503 before it can persist its idempotency receipt. The
positive preview is proven; synchronous execution, async execution/cancellation, CI, independent
review, merge and deployment are not proven by this evidence.

## Integration notes

- Story: APL-613 / FR-ANA-005.
- Positive preview journey: locally passed; no acceptance, CI or deployment movement.
