# Release 1.11 coding candidate — explicit calculation coverage status

FR-CAL-008 / APL-408 makes coverage interpretation explicit on every newly calculated result. Results backed by an approved obligation snapshot are labelled `COMPLETE` only when every required obligation has an approved valid value; otherwise they are `PARTIAL` and carry a `PARTIAL_COVERAGE` limitation. Results without an approved collection plan are `NOT_CONFIGURED` rather than appearing complete.

The existing coverage record continues to distinguish expected, received, valid, approved, pending, missing, excluded, excepted, overdue and unplanned contributions. Arithmetic still uses only approved eligible values; absent values never become zero. The UI presents the status and reason beside the counts.

No database migration is required.

## Positive journey evidence

The synthetic HTTP journey
`qualification/test_coverage_status_live.py::test_calculation_keeps_approved_pending_and_missing_coverage_explicit`
passed on 16 October 2026. It creates an approved five-obligation collection plan, records three
independently approved values and one pending value, leaves one obligation missing, and calculates
the result through the API. The durable result pins its plan revision, uses only the three approved
values, reports 60.00% approval, retains distinct approved/pending/missing counts of 3/1/1, and carries
both `PARTIAL` coverage state and the `PARTIAL_COVERAGE` limitation.

The broader `qualification/test_measurement.py` disposable suite also passed 21 tests in the same
qualification cycle. CI, independent review, merge, deployment and product acceptance remain
separate gates.

## Integration notes

- Story: APL-408 / FR-CAL-008.
- Positive user journey: locally passed; no CI, acceptance or deployment movement.
