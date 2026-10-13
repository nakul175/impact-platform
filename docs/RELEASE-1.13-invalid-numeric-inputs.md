# Release 1.13 coding candidate — governed invalid numeric inputs

FR-CAL-010 / APL-415 gives invalid numeric inputs distinct, stable outcomes. Negative participant or event counts fail with `NEGATIVE_COUNT`; negative ratio components fail with `NEGATIVE_RATIO_QUANTITY`; a percentage numerator above its denominator fails with `PERCENTAGE_OUT_OF_RANGE`. None is clipped, converted to zero or displayed as a successful result. A zero denominator continues to return `UNDEFINED` with `ZERO_DENOMINATOR`.

Negative values for a decimal measure are accepted only when its reviewed definition sets `allows_negative_adjustments` and supplies a written basis. The result and lineage formula freeze both fields, while other measurement types cannot enable the rule. The definition editor exposes this choice only for decimal measures and explains its boundary.

No database migration is required. Tests and CI remain deferred by owner request; this coding candidate is unmerged and undeployed.
