# 0.89 access-change propagation

FR-ACC-011 / APL-354 records every tenant policy-epoch change and adds online presentation leases bound to the current principal, current policy epoch and immutable derivative sources. Leases last at most sixty seconds; validation fails closed after expiry, an access change or loss of any source permission.

This is a coding candidate only. Qualification, independent review, merge and deployment remain pending.
