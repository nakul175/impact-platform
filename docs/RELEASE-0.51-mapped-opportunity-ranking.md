# Release 0.51 coding candidate: rank exact mapped opportunities

US-MP-03 / APL-381 (frozen Gherkin SHA-256 `84faf53d5d8aa6ec73fc0b51b70e071a2003db2d8b55bf7f2ae02ec2b6260948`) connects the existing exact weighted-ranking engine to the exact completed diagnosis revision and pattern edition produced by US-MP-01. The new route ranks only unique opportunities in that complete map; an incomplete map is refused.

Every ranked item exposes impact, effort, cost and readiness plus its exact weighted total. The existing integer numerator and decimal display rules remain in force, ties use stable pattern IDs, incomplete editorial score sets remain explicitly unranked, and every response pins the diagnosis revision, pattern edition, score version, weights and weights revision.

Readiness is derived from the bounded organisation profile and applicable capacity gaps. Impact, effort and cost remain an editorial draft pending advisor review. The recorded owner decision keeps the Operations Head persona read-only: that persona can view rankings with the organisation's saved weights, while an existing authorized AI-enablement manager changes persistent weights. This is a disclosed deviation from the source wording that says the Operations Head changes them directly; no permission is silently widened.

This is a coding-only candidate. Tests, CI, merge, staging deployment and owner acceptance are intentionally deferred to the combined qualification phase.
