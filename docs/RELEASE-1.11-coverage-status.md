# Release 1.11 coding candidate — explicit calculation coverage status

FR-CAL-008 / APL-408 makes coverage interpretation explicit on every newly calculated result. Results backed by an approved obligation snapshot are labelled `COMPLETE` only when every required obligation has an approved valid value; otherwise they are `PARTIAL` and carry a `PARTIAL_COVERAGE` limitation. Results without an approved collection plan are `NOT_CONFIGURED` rather than appearing complete.

The existing coverage record continues to distinguish expected, received, valid, approved, pending, missing, excluded, excepted, overdue and unplanned contributions. Arithmetic still uses only approved eligible values; absent values never become zero. The UI presents the status and reason beside the counts.

No database migration is required. Tests and CI remain deferred by owner request; this coding candidate is unmerged and undeployed.
