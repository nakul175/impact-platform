# Release 1.38 coding candidate — expenditure ingestion

FR-FIN-003 / APL-650 imports exact-decimal expenditure with stable source transaction keys, posting/event dates, currency, category, funding allocation and explicit original, reversal or replacement semantics. File digests and unchanged transactions reconcile instead of duplicating spending.

Control totals must balance unless an explicit permitted exception is recorded. Changed transactions require correction semantics and retain the superseded revision.

Migration 0113 registers expenditure and variance records behind restrictive delivery-worker fences; the existing explicit finance capability remains required.

The story-specific disposable live HTTP journey in `qualification/test_expenditure_ingestion_live.py` now proves exact-decimal original, reversal and replacement revisions, immutable `supersedes_revision` links, file-digest reconciliation without duplicate transactions, and refusal of an unbalanced control total without an explicit exception. The focused journey passed locally on 16 October 2026. This is positive-journey and integral-refusal evidence only; CI, independent review, merge and deployment gates remain separate.
