# Release 1.12 coding candidate — explicit precision and workload boundary

FR-CAL-009 / APL-411 freezes the numeric contract with every new result and lineage manifest: inputs admit at most 12 fractional digits, intermediate Decimal arithmetic uses 100 significant digits, storage rounds half-up once to 12 places, and display rounds half-up from that stored raw decimal at the definition's requested places. The formula explicitly says `OUTPUT_ONLY`, so displayed component values cannot be reused as arithmetic inputs.

The qualified arithmetic workload is bounded at 10,000 approved present contributors. A larger eligible set fails before calculation or lineage writes with `CALCULATION_INPUT_LIMIT`, rather than overflowing a later manifest or silently truncating sources. Decimal overflow remains explicit as `NUMERIC_OVERFLOW`; identifiers remain strings.

No database migration is required.

## Positive journey evidence

The synthetic HTTP journey
`qualification/test_precision_rounding_live.py::test_three_exact_inputs_round_only_after_the_unrounded_sum_is_stored`
passed on 16 October 2026. It creates three independently approved exact inputs of `0.335`, calculates
through the API, and reads back the durable result. The stored raw total is `1.005`, the display is
`1.01`, and the frozen formula records 100-digit calculation precision, 12-digit input/storage scale,
`HALF_UP`, and `OUTPUT_ONLY`. The result also retains its exact lineage-manifest reference.

The independent golden/reference/domain/live reconciliation suite passed all 118 checks, including
the `CAL09-display-precision` live vector. CI, independent review, merge, deployment, export-specific
qualification and product acceptance remain separate gates.

## Integration notes

- Story: APL-411 / FR-CAL-009.
- Positive user journey: locally passed; no CI, acceptance or deployment movement.
