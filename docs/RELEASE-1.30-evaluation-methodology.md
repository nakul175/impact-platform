# Release 1.30 coding candidate — reproducible sampling methodology

FR-EVA-002 / APL-630 adds evaluation-bound, versioned methodology records covering sampling frame, eligibility, assignment, strata, weights, nonresponse and analysis plan. Stratum eligible and sampled counts reproduce the declared denominator; invalid or duplicate strata are refused.

Amendments record whether they occurred before or after data inspection and become review-pending before use. Sample export is available only from a reviewed revision. Missing weights block weighted output instead of defaulting to one, and population estimates require an explicit supported expansion method. Every count is labelled as a sample rather than all beneficiaries.

This release adds no migration or privilege change. Tests and CI remain deferred by owner request.
