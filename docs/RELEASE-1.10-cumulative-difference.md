# Release 1.10 coding candidate — governed cumulative differences

FR-CAL-005 / APL-405 adds an explicit `CUMULATIVE_DIFFERENCE` method for cumulative count and decimal indicators. The approved definition must contain the starting cumulative value and a written basis. The result takes the latest approved position and subtracts that frozen baseline; it never adds monthly cumulative positions.

Approved positions are ordered by event time. Different values tied at the latest time return `UNDEFINED` with `TIED_LATEST_VALUES`. A decline between positions or below the approved baseline returns `UNDEFINED` with `CUMULATIVE_DECLINE`; reset inference is deliberately refused until a separately reviewed reset method exists. Formula and lineage documents retain the baseline and basis for reproduction, and the definition editor explains the behavior.

The existing flow sum, event count and latest stock behavior remains unchanged. No database migration is required. Tests and CI remain deferred by owner request; this coding candidate is unmerged and undeployed.
