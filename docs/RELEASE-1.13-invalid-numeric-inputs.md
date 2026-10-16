# Release 1.13 coding candidate — governed invalid numeric inputs

FR-CAL-010 / APL-415 gives invalid numeric inputs distinct, stable outcomes. Negative participant or event counts fail with `NEGATIVE_COUNT`; negative ratio components fail with `NEGATIVE_RATIO_QUANTITY`; a percentage numerator above its denominator fails with `PERCENTAGE_OUT_OF_RANGE`. None is clipped, converted to zero or displayed as a successful result. A zero denominator continues to return `UNDEFINED` with `ZERO_DENOMINATOR`.

Negative values for a decimal measure are accepted only when its reviewed definition sets `allows_negative_adjustments` and supplies a written basis. The result and lineage formula freeze both fields, while other measurement types cannot enable the rule. The definition editor exposes this choice only for decimal measures and explains its boundary.

No database migration is required.

The story-specific disposable live HTTP journey in `qualification/test_invalid_numeric_inputs_live.py` now proves that a reviewed negative decimal adjustment contributes to the exact result and freezes its approval basis, a zero denominator persists as `UNDEFINED` with `ZERO_DENOMINATOR`, and invalid count and ratio submissions retain the stable `NEGATIVE_COUNT`, `NEGATIVE_RATIO_QUANTITY` and `PERCENTAGE_OUT_OF_RANGE` reasons without clipping or conversion to zero. The focused journey passed locally on 16 October 2026. This is positive-journey and integral-refusal evidence only; CI, independent review, merge and deployment gates remain separate.
