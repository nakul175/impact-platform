# Release 0.54 coding candidate: benefits in sector terms

US-VC-02 / APL-387 (frozen Gherkin SHA-256 `510db9c8f2eb6c0111ebf3336a757cd8cad5905ff8379e8464e694a287016159`) extends the complete value case with four required sector terms: staff hours, cost per beneficiary, data quality and reach.

Both baseline and trial source snapshots now require annual staff hours, a non-zero annual beneficiary count, data-quality percentage and annual reach. The server derives horizon-wide staff-hours saved and reach change, baseline and trial cost per beneficiary, and data-quality percentage-point change. Every metric is returned even when the change is negative; adverse results are not hidden.

Missing benefit inputs, zero beneficiary denominators and data-quality values above 100 are refused before a value case can be labelled complete. Values remain self-reported and do not become official MEL results or causal impact claims.

This is a coding-only candidate. Tests, CI, merge, staging deployment and owner acceptance are intentionally deferred to the combined qualification phase.
