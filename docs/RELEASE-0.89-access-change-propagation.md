# 0.89 access-change propagation

FR-ACC-011 / APL-354 records every tenant policy-epoch change and adds online presentation leases bound to the current principal, current policy epoch and immutable derivative sources. Leases last at most sixty seconds; validation fails closed after expiry, an access change or loss of any source permission.

The positive user journey is qualified on a disposable native PostgreSQL/API runtime by
`qualification/test_access_change_propagation_live.py` (2 passed), alongside the permission-safe
derivative regression suite (2 passed). The journey proves a valid sixty-second online lease,
immediate invalidation after an unrelated governed policy-epoch change while its source remains
readable, and fail-closed derivative and presentation reads after the exact source permission is
revoked. The qualification also repaired the lease's principal binding to use the authenticated
context's canonical `principal_id`.

This evidence qualifies the positive-user-journey gate for APL-354. CI, independent review, merge,
staging deployment and owner acceptance remain pending.
