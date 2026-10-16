# Release 1.10 coding candidate — governed cumulative differences

FR-CAL-005 / APL-405 adds an explicit `CUMULATIVE_DIFFERENCE` method for cumulative count and decimal indicators. The approved definition must contain the starting cumulative value and a written basis. The result takes the latest approved position and subtracts that frozen baseline; it never adds monthly cumulative positions.

Approved positions are ordered by event time. Different values tied at the latest time return `UNDEFINED` with `TIED_LATEST_VALUES`. A decline between positions or below the approved baseline returns `UNDEFINED` with `CUMULATIVE_DECLINE`; reset inference is deliberately refused until a separately reviewed reset method exists. Formula and lineage documents retain the baseline and basis for reproduction, and the definition editor explains the behavior.

Each successful result also exposes the ordered cumulative positions and the exact increment from the approved baseline or preceding position. Reproduction recomputes and compares this increment series together with the stored result, while the immutable lineage manifest continues to pin every included source revision.

The existing flow sum, event count and latest stock behavior remains unchanged. Additive migration `0110_cumulative_difference_projection.sql` supplies the previously missing nullable baseline, basis and increment projections under the existing forced tenant fence. Qualification evidence is recorded by the story-specific live journey; merge, CI and deployment remain separate gates.
