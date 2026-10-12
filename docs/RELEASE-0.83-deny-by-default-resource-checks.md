# Release 0.83 coding candidate — deny-by-default resource checks

FR-ACC-001 / APL-348 adds a closed, tenant-admin batch check that treats every supplied object ID as a selector. Each item is independently resolved through the shared current-authority loader against tenant, expected type, current availability and the requested capability. Only permitted selector IDs return; missing, hidden, restricted, wrong-type and cross-tenant selectors are omitted without names, counts or existence signals. Any non-hidden policy-resolution failure aborts the request rather than falling back to a cached role.

The existing shared `load` and `references` paths remain the enforcement boundary for domain reads and writes. This increment adds a bounded batch consumer of that boundary; it does not certify every historical route. Source checks only; tests, CI, merge, staging and acceptance are deferred.
