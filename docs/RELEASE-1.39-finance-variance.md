# Release 1.39 coding candidate — variance and forecast

FR-FIN-005 / APL-652 saves a variance view against an exact approved budget revision, actual cutoff and exact expenditure transaction revisions. Remaining budget uses the labelled positive-means-unspent convention; missing actual data produces no underspend value.

Forecast total, commitments, assumptions, author and method version remain separate from the actual series. Forecast overrun is reported separately and cannot imply programme impact success.

Migration 0113 registers expenditure and variance records behind restrictive delivery-worker fences; the existing explicit finance capabilities remain required.

The story-specific disposable live HTTP journey in `qualification/test_finance_variance_live.py` now proves an exact approved budget and expenditure revision produce `40.00` currently unspent and a separate `10.00` forecast overrun, with the sign convention, assumptions and method version preserved and forecasts excluded from actuals. A second journey proves missing actual data stores neither an actual total nor apparent underspend. Both focused journeys passed locally on 16 October 2026. This is positive-journey and integral-missingness evidence only; CI, independent review, merge and deployment gates remain separate.
