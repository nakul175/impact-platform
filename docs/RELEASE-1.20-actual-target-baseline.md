# Release 1.20 coding candidate — actual, target and baseline comparison

FR-ANA-003 / APL-435 makes the existing governed programme comparison explicit. Target and baseline blocks identify the exact approved revision, original/revised/baseline label, applicable period, direction and time semantic. Comparison output declares its deviation, attainment and baseline-change formulas rather than leaving interpretation to the client.

Lower-is-better attainment uses `target / actual × 100`; target ten and actual eight is `ACHIEVED` with deviation `-2` and uncapped attainment `125.00%`. Higher-is-better keeps `actual / target × 100`. Percentage change from a zero or negative baseline remains `Undefined` with a reason and never produces an infinite value. An actual/target time-semantic mismatch without an approved conversion returns `NOT_COMPUTABLE` and `INCOMPATIBLE_TIME_SEMANTIC` instead of a comparison.

The dashboard UI shows the target edition, applicable period, time semantic, formulas, signed deviation, uncapped scale and baseline-change state. This release adds no migration or database privilege change. Tests and CI remain deferred by owner request; source checks only are recorded for this unmerged, undeployed coding candidate.
