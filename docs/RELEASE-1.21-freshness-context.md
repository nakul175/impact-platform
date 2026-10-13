# Release 1.21 coding candidate — freshness and approval context

FR-ANA-004 / APL-437 labels every programme result card as snapshot, live approved, provisional or unavailable. Its material context names the last valid source data time, approval cutoff, calculation time, coverage, stale reasons and dashboard fetch time. Fetch success is explicitly separate from the source and calculation freshness basis and cannot clear a stale state.

The print/save view retains these labels and timestamps with every card, including provisional and stale markers. No new freshness threshold is invented. This release adds no migration or privilege change. Tests and CI remain deferred by owner request.
