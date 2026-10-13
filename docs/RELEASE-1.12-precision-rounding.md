# Release 1.12 coding candidate — explicit precision and workload boundary

FR-CAL-009 / APL-411 freezes the numeric contract with every new result and lineage manifest: inputs admit at most 12 fractional digits, intermediate Decimal arithmetic uses 100 significant digits, storage rounds half-up once to 12 places, and display rounds half-up from that stored raw decimal at the definition's requested places. The formula explicitly says `OUTPUT_ONLY`, so displayed component values cannot be reused as arithmetic inputs.

The qualified arithmetic workload is bounded at 10,000 approved present contributors. A larger eligible set fails before calculation or lineage writes with `CALCULATION_INPUT_LIMIT`, rather than overflowing a later manifest or silently truncating sources. Decimal overflow remains explicit as `NUMERIC_OVERFLOW`; identifiers remain strings.

No database migration is required. Tests and CI remain deferred by owner request; this coding candidate is unmerged and undeployed.
