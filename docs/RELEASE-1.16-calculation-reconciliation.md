# Release 1.16 coding candidate — calculation reconciliation and explainability

FR-CAL-015 / APL-424 adds a result explanation view and a run-comparison endpoint. The explanation names the exact rule revision and lineage execution, formula and filters, included and excluded aggregate counts, adjustment labels, coverage and approval state. Excluded source identities and values are never returned.

Run comparison rechecks current authority for both results and every source needed for arithmetic. For compatible runs it constructs a deterministic bridge: first apply permitted new source revisions to the earlier inclusion set, then apply the later inclusion set. The two deltas are reported separately as `SOURCE` and `FILTER`. Rule, period, target, permission and disclosure changes are classified independently. A withheld source remains a withheld reference and prevents the response from claiming reconciliation.

When an amended report changes an existing numeric binding, independent approval now requires the earlier and later result revisions to reconcile completely. A missing, withheld, incompatible or unexplained amount returns `REPORT_DIFFERENCE_UNRECONCILED` before any approval decision is written. First-report approval has no prior numeric difference to reconcile.

The React result inspector presents the explanation aggregates and an accessible run selector and cause table. This release adds no migration or database privilege change. Tests and CI remain deferred by owner request; source checks only are recorded for this unmerged, undeployed coding candidate.
