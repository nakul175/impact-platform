# Release 1.28 coding candidate — reviewable anomaly assistance

FR-DQ-007 / APL-623 turns the existing robust median-absolute-deviation detector into an explicitly suggestion-only review flow. A run pins its method version and parameters, exact eligible observation revisions and source hashes, comparison window, owner and plain-language explanation. Only comparable present values inside the declared window enter the calculation.

Findings start as `SUGGESTED` and can be confirmed, dismissed with a required reason, or deferred. Dismissal remains distinct from a confirmed quality defect and retains only minimised review feedback. Runs and reviews state that source mutation and person-level fraud labels are false; no observation write occurs. Both commands use exact-payload idempotency receipts.

This release adds no migration or privilege change. Tests and CI remain deferred by owner request.
