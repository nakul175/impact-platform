# Release 1.39 coding candidate — variance and forecast

FR-FIN-005 / APL-652 saves a variance view against an exact approved budget revision, actual cutoff and exact expenditure transaction revisions. Remaining budget uses the labelled positive-means-unspent convention; missing actual data produces no underspend value.

Forecast total, commitments, assumptions, author and method version remain separate from the actual series. Forecast overrun is reported separately and cannot imply programme impact success.

This release adds no migration or privilege change. Tests and CI remain deferred by owner request.
