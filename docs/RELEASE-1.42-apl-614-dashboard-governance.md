# Release 1.42 candidate — complete governed dashboard publication

## Delivered

- Copies a pinned dashboard configuration into a second workspace as a private draft. The destination receives no grant and every source binding remains unavailable until explicitly rebound to destination-owned approved material.
- Prepares immutable disclosure content and requires approval by a different natural person before public publication.
- Pins the exact approved disclosure revision in a public publication and serves only that frozen content through the controlled content route. No public read executes a private source query.
- Transfers publication ownership only under current dashboard authority and an exact publication revision.
- Persists suspension when expiry, source revision or source classification changes. Revalidation runs under the tenant lock against current authority and leaves the publication suspended until a separate exact-revision resume command.
- Binds every mutation to an operation identifier and payload fingerprint; exact retries return the original receipt and changed retries conflict.

## Contract and persistence

Migration0117 registers `DashboardDisclosureArtifact` and denies the worker access to its registry and immutable revisions. The domain contract adds closed requests for cross-workspace copy, disclosure preparation/review, owner transfer, revalidation and resume, plus a bounded frozen-content response.

Dashboard and publication history remains append-only. Cross-workspace copy requires the same authenticated natural identity to be an active, authorised member in both workspaces. It carries layout and binding kinds only; source object and revision selectors are replaced with opaque unavailable placeholders, and it does not carry source access or create grants.

## Limits

This is a local coding and qualification candidate. It does not claim CI, independent final review, merge, staging deployment or owner acceptance. Anonymous unauthenticated access is not added; controlled public content still requires the platform's authenticated route authority.

## Reproduction

Run `qualification/test_dashboard_governance_live.py` on a fresh disposable database. The test covers the funder-workspace copy, zero-grant/unavailable-binding result, exact retry conflict, public-without-disclosure refusal, natural-person self-review refusal, independent approval, frozen content retrieval, owner transfer, durable sensitivity suspension, revalidation and explicit resume.

## Integration notes

- Story: FR-ANA-008 / APL-614.
- Frozen source files and historical migrations remain unchanged.
- Migration0117 is additive and follows0116.
