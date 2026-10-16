# Release 1.42 — sampling methodology completion

## Delivered

APL-630 / FR-EVA-002 adds versioned sampling methodologies bound to an exact evaluation revision. Sampling frame, eligibility, assignment, strata, weights, nonresponse rules, analysis plan and expansion method remain together. Creation and every amendment enter independent review; amendments state whether they occurred before or after data inspection.

Reviewed sample exports reproduce the eligible denominator and keep sample count distinct from population estimates. Weighted output fails when any weight is missing or non-positive. Population estimates require both weighted output and a named supported expansion method. Nonresponse cannot exceed the sampled stratum.

## Contract and persistence

Dedicated create, list, read, amend, independent review, history and sample-export operations use evaluation capabilities and recheck current access to the bound evaluation. Mutations require the expected current revision and exact retries expire after seven days. Migrations 0106 and 0107 register the object kind, worker fences and exact generated access profile without activating it.

## Limits

This is a local coding candidate. CI, merge, staging deployment and owner acceptance remain separate gates.

## Reproduction

Run `IMPACT_PORT=8348 .venv/bin/python scripts/run.py test --pytest-path qualification/test_evaluation_methodology_live.py` for the disposable synthetic positive journey. Run `make lint`, `make unit`, TypeScript checking and the release security review for the broader candidate checks.

## Integration notes

The synthetic positive journey `test_methodology_is_independently_reviewed_and_exports_reproducible_sample_counts` proves exact evaluation binding, independent approval, immutable history and an explicit weighted export that keeps sample count separate from population estimate. No CI, merge, staging or acceptance claim is made.
