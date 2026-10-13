# Release 1.09 coding candidate — pooled ratios and explicit weighting

FR-CAL-003 / APL-402 makes the interpretation of ratio aggregation part of the frozen result contract. A pooled percentage sums every eligible approved numerator and denominator, divides the pooled quantities, then applies the percentage multiplier. The stored formula and lineage manifest disclose denominator weighting, required quantities and multiplier order; the result UI explains the same method.

An eligible component without either quantity is refused with `RATIO_QUANTITIES_REQUIRED`. A pooled denominator of zero remains `UNDEFINED` with `ZERO_DENOMINATOR`. The unweighted mean remains available only as a separately labelled statistic with equal contributor weighting, and is never substituted for the pooled percentage.

The existing deterministic Decimal arithmetic, immutable source revision pins and reproduction route are unchanged. No database migration is required. Tests and CI remain deferred by owner request; this coding candidate is unmerged and undeployed.
