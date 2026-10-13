# Release 1.22 coding candidate — governed table pivots

FR-ANA-005 / APL-613 adds pivot preview and execution for an exact currently readable calculated-result revision pinned by a private dashboard widget. The closed statistic vocabulary is distinct count, sum and mean, each checked against the source calculation method; incompatible requests are refused with a labelled supported alternative.

Cells retain their value state, suppression and additivity. Multiselect, distinct and nonadditive categories explicitly explain that category totals may exceed the distinct grand total. Grand totals come from the governed result or unrounded eligible values and are never summed from displayed cells.

Previews above 100 cells route to a tenant-bounded `DASHBOARD_PIVOT` job. Jobs are idempotently requested, capped at ten open jobs per tenant, cancellable before worker claim and completed by the worker from the authority-checked exact-revision manifest. Migration 0094 adds only the due-tenant directory; existing tenant-fenced job storage and worker privileges remain in force. Tests and CI remain deferred by owner request.
