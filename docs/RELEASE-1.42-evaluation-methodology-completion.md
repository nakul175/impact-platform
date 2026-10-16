# Release 1.42 — sampling methodology completion

## Delivered

APL-630 / FR-EVA-002 adds versioned sampling methodologies bound to an exact evaluation revision. Sampling frame, eligibility, assignment, strata, weights, nonresponse rules, analysis plan and expansion method remain together. Creation and every amendment enter independent review; amendments state whether they occurred before or after data inspection.

Reviewed sample exports reproduce the eligible denominator and keep sample count distinct from population estimates. Weighted output fails when any weight is missing or non-positive. Population estimates require both weighted output and a named supported expansion method. Nonresponse cannot exceed the sampled stratum.

## Contract and persistence

Dedicated create, list, read, amend, independent review, history and sample-export operations use evaluation capabilities and recheck current access to the bound evaluation. Mutations require the expected current revision and exact retries expire after seven days. Migrations 0106 and 0107 register the object kind, worker fences and exact generated access profile without activating it.

## Limits

This is a local coding candidate. CI, merge, staging deployment and owner acceptance remain separate gates.

## Reproduction

Run `make lint`, `make unit`, TypeScript checking and the release security review.

## Integration notes

FR-EVA-002 may move to coding-complete after exact-commit review. No acceptance claim is made.
