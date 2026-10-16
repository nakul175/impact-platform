# Release 1.09 coding candidate — pooled ratios and explicit weighting

FR-CAL-003 / APL-402 makes the interpretation of ratio aggregation part of the frozen result contract. A pooled percentage sums every eligible approved numerator and denominator, divides the pooled quantities, then applies the percentage multiplier. The stored formula and lineage manifest disclose denominator weighting, required quantities and multiplier order; the result UI explains the same method.

An eligible component without either quantity is refused with `RATIO_QUANTITIES_REQUIRED`. A pooled denominator of zero remains `UNDEFINED` with `ZERO_DENOMINATOR`. The unweighted mean remains available only as a separately labelled statistic with equal contributor weighting, and is never substituted for the pooled percentage.

The existing deterministic Decimal arithmetic, immutable source revision pins and reproduction route are unchanged. No database migration is required.

## Positive journey evidence

The disposable synthetic HTTP journey
`qualification/test_pooled_ratios_live.py::test_analyst_calculates_denominator_weighted_ratio_from_approved_components`
creates and independently approves the 50/100 and 1/10 observations, calculates 51/110, stores
46.363636363636 and displays 46.36. Its formula identifies denominator weighting and multiplication
after pooling, and the reproduction endpoint recomputes an exact match from the two pinned source
revisions. The journey explicitly refuses the incorrect 30.00 interpretation by assertion.

CI, independent final review, merge, staging deployment and owner acceptance remain separate gates.
