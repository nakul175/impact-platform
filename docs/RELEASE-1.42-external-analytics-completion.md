# Release 1.42 — governed external analytics completion candidate

## Delivered

APL-620 / FR-ANA-010 now has a complete coding candidate for revocable, exact-revision BI extracts.
Creation validates current source authority and allowed fields, records the named destination and
reuse terms, and creates a real expiring `SERVICE` principal backed by two distinct active human
owners. The credential is returned to the caller, stored only as a digest on the connection, and
sealed for exact uncertain-operation replay.

Every refresh rechecks the human caller, service-principal state and expiry, exact current source
revision, read scope, effective field-category restrictions and readable indicator definition
before constructing a package. A revoked connection or changed authority yields no package. The
immutable extract manifest retains destination, terms, exact datasets and selected fields, package
digest, service identity and the explicit `TRACKED_NOT_REMOTELY_ERASED` state.

Safe list/read APIs omit credential material. The authored dashboard UI can create, refresh and
revoke a connection and inspect retained extract history after reload. It states that revocation
does not erase remote copies and provides no unrestricted database access.

## Persistence and security

Migration 0102 registers `ExternalAnalyticsConnection` and `ExternalAnalyticsExtract` and adds
restrictive delivery-worker fences. Dedicated policy operations govern create, read, list, refresh,
revoke and extract history. Revocation deactivates the service principal and advances its subject
epoch atomically with the connection revision.

## Limits

This is a local coding candidate: unmerged, undeployed and unaccepted. It returns a bounded package
through the authenticated API; it does not connect to or erase data in an external provider.
Existing tenants need their normal governed access-profile upgrade before using new operations.

## Integration notes

- Story: APL-620 / FR-ANA-010.
- Positive journey: `qualification/test_external_analytics_live.py` proves that a human author can
  bind an exact approved result revision and a bounded field set, refresh it into an immutable
  extract manifest, inspect that history, revoke the connection, and receive a policy refusal when
  the retired credential is presented again.
- Local evidence: focused live application run passed 1 test on 16 October 2026. This evidence does
  not claim CI, independent review, merge, staging deployment, acceptance, or remote erasure.
- Security-sensitive paths are recorded in `release-review-1.42.0.json`.
