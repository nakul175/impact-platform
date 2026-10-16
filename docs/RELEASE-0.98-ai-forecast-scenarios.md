# 0.98 versioned forecast scenarios

FR-AI-017 / APL-718 adds planning-only forecast scenarios from exact, currently readable `OFFICIAL` calculated-result revisions. Inputs must be present and use one unit. The server records the exact revisions, horizon, fixed method, assumptions, validation history, uncertainty method and immutable projection points. One or two inputs produce an explicitly labelled `EXPLORATORY` artifact; three or more produce a `PROJECTION`.

Actual and projection series export separately. The export states that approved targets were not changed, and no forecast code writes target tables. Reusing a scenario ID with a changed request creates the next immutable version. A sufficient projection can only create a `PENDING` adoption review; exploratory output cannot enter that route and no review result automatically changes a target.

Current result authority and exact revision availability are rechecked on replay, read, export and adoption request.

The disposable positive journey in `qualification/test_ai_forecast_scenarios_live.py` passed on 16 October 2026. It created exact locked `OFFICIAL` revisions through the ordinary collection, calculation and period-close workflow; proved the one-input exploratory label and adoption refusal; proved a three-input projection, assumptions, validation and uncertainty metadata; exported actuals separately from projections without changing targets; created a pending adoption review; and proved a changed assumption creates version 2 while version 1 remains readable. CI, independent review, merge, staging deployment and owner acceptance remain pending.
