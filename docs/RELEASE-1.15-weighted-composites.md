# Release 1.15 coding candidate — governed weighted composites

FR-CAL-013 / APL-607 extends the closed formula catalogue with weighted composite indicators. A composite pins two to twenty exact approved indicator-definition revisions, a normalization range and proposed weight for each component, required-component flags, one closed missing-component policy and a written interpretation. Normalized weighted-mean weights must total exactly one.

Preview reports every component's normalized value, effective weight and contribution. It also reports a deterministic sensitivity value produced by increasing each present component's proposed weight by ten percent relative and renormalizing the present weights. Missing required components and the `BLOCK` policy return an incomplete result. Optional components may be omitted and the remaining weights renormalized only when the approved rule is `RENORMALIZE_OPTIONAL`.

The existing immutable FormulaDefinition revision and approval flow pins the complete composite configuration and exact source-definition revisions, so later weight changes create a new revision and old results remain reproducible. This release adds no migration or database privilege change. Tests and CI remain deferred by owner request; this coding candidate is unmerged and undeployed.
