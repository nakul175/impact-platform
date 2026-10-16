# Release 1.42 — reviewable anomaly assistance completion candidate

## Delivered

APL-623 / FR-DQ-007 now has a complete coding candidate for suggestion-only anomaly review. A run records its exact eligible observation revisions, source hashes, comparison window, reviewed robust-MAD method and explanation. A raised finding records severity, owner and its source revision without editing the observation or creating a person-level fraud label.

Data Stewards can list and inspect retained runs and current finding reviews, then confirm, dismiss with a bounded reason code, or defer. Every read and review rechecks current source-object and field authority. A review verifies the retained source hash, permits only valid state transitions and writes a new finding revision. Dismissed feedback stays distinct from a confirmed quality defect and records the named minimisation policy and exact fields intended for later evaluated method changes. The immutable revision store retains earlier review evidence; this candidate does not claim an unsupported purge schedule.

## Persistence and interface

Migration 0103 registers `AnomalyRun` and `AnomalyFinding` with restrictive delivery-worker fences. Dedicated access-policy operations cover create, list, read and review. The import workspace includes the version-pinned run form, review queue and explicit source-mutation and person-label limits.

## Verification and limits

Focused pure checks cover the deterministic outlier boundary, dedicated policy operations and worker
fences. The synthetic positive journey
`qualification/test_anomaly_assistance_live.py::test_analyst_runs_anomaly_assistance_and_confirms_a_reviewable_finding`
passed on 16 October 2026: six independently approved aggregate observations produce one reviewable
spike, a human confirms it through the HTTP API, and the exact source revision and value remain
unchanged. This remains a local candidate: unmerged, not independently accepted, and undeployed. No
model is retrained automatically, person-linked observations are refused, raw values are not persisted
in run context, and no review decision changes underlying observations.

## Integration notes

- Story: APL-623 / FR-DQ-007.
- Positive user journey: locally passed; no acceptance, CI or deployment movement.
- Security-sensitive paths are recorded in `release-review-1.42.0.json`.
