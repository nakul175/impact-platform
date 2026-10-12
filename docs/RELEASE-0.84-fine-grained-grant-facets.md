# Release 0.84 coding candidate — fine-grained grant facets

FR-ACC-002 / APL-349 adds an attach-once narrowing facet to an existing active approved grant. The existing capability remains the action boundary and existing tenant/project/partner/object-set scope remains the outer row boundary. The facet adds an exact current-record allowlist and separate readable and writable field categories; writable categories must be a subset of readable categories. Records must exist in the tenant and, for scoped grants, remain inside the existing scope. Attaching the facet bumps tenant policy and subject epochs.

Shared direct-object scope checks and list visibility now apply the record allowlist before disclosure, filtering, sorting or aggregation. A shared `field_allowed` helper applies the same row condition before a server-owned category and distinguishes read from write. Omission semantics remain with each closed update command; the facet does not convert an omitted hidden field into a clear. Existing read, download, approval and publication capabilities remain separate.

This candidate does not claim every domain DTO has field-category metadata yet. Source checks only; tests, CI, merge, staging and acceptance are deferred.
