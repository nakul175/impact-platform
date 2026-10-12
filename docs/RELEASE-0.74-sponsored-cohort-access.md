# Release 0.74 candidate — sponsored cohort access

Coding-only candidate for **US-CM-02 / APL-592**.

A sponsor with current subscription administration authority can save one named cohort with a positive exact-decimal budget, currency, fixed duration, exact terms version and unique active grantee tenants. Each grantee receives an invitation only. Nothing activates before a current administrator of that grantee tenant accepts the exact terms.

Acceptance is tenant-locked, exact-retry protected and append-only evidenced. It starts a bounded entitlement ending after the agreed duration and always records `no_charge=true`. Active sponsored-access reads omit invited and expired rows. Sponsorship creates no membership, grant, scope or data authority; `data_authority_granted` is fixed false.

Tests, CI, merge, staging deployment, acceptance and human certification remain pending under the owner's coding-first instruction.
