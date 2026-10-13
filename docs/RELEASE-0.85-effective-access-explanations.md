# Release 0.85 coding candidate — effective access explanations

FR-ACC-003 / APL-350 adds two read-only explanations. Any authorised member can inspect their own selected operation context. A tenant administrator with tenant-wide grants-read authority can simulate a current principal in that tenant. The server resolves the operation to its capability, evaluates current direct and group grant paths, scope membership and attached record conditions, and reports missing current-session assurance.

Outputs contain only path source, scope type/ID, whether a record condition applied, permitted category codes, decision and missing-assurance codes. They contain no project/resource names, record content or field values. A restriction is evaluated on every path; an unrelated role does not erase it. Unknown operations and out-of-tenant/inactive subjects are refused.

Explicit deny records beyond the implemented narrowing facets are not invented. Source checks only; tests, CI, merge, staging and acceptance are deferred.
