# Release 1.38 coding candidate — expenditure ingestion

FR-FIN-003 / APL-650 imports exact-decimal expenditure with stable source transaction keys, posting/event dates, currency, category, funding allocation and explicit original, reversal or replacement semantics. File digests and unchanged transactions reconcile instead of duplicating spending.

Control totals must balance unless an explicit permitted exception is recorded. Changed transactions require correction semantics and retain the superseded revision.

This release adds no migration or privilege change. Tests and CI remain deferred by owner request.
