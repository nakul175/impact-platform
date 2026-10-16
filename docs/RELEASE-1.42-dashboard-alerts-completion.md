# Release 1.42 — governed dashboard alert completion candidate

## Delivered

APL-618 / FR-ANA-009 now has a complete coding candidate. An alert rule pins its measure,
condition, coverage, freshness, calendar cadence, recipients and cooldown. The first evaluation is
refused before its due instant; a due reporting period is retained on every outcome. Missing,
stale and threshold conditions remain separate, and absent values never enter threshold arithmetic.
Repeated evaluation of the same period during cooldown revisions one incident and increments its
occurrence count.

Rules and incidents are durable, tenant-fenced resources. Their read and list APIs use current
`dashboards.read` scope, signed visibility-bound cursors and hidden-resource semantics. Evaluation
revalidates the current measure, period, result binding and active recipients, and an incident pins
the exact calculated-result revision. The authored-dashboard screen can configure a rule, restore
it after reload, select a readable result or an absent result, and inspect incident history.

## Contract and persistence

- `0101_dashboard_alert_kinds.sql` additively registers `DashboardAlertRule` and
  `DashboardAlertIncident` and adds restrictive delivery-worker fences.
- The domain contract adds rule list/read, incident list and period-bound evaluation responses.
- Cadence state is revisioned with the rule (`next_evaluation_at`, `last_evaluated_at`,
  `last_period_id`). Monthly advancement uses calendar months rather than fixed seconds.

## Limits

This is a local coding candidate. It is not merged, deployed or accepted. Evaluation is initiated
by an authorised application caller when the rule is due; no background alert scheduler is claimed.
Operational delivery of notifications remains a later story. Existing tenants require the normal
governed access-profile upgrade before newly registered operations can be used.

## Reproduction

The synthetic positive journey
`qualification/test_dashboard_alerts_live.py::test_author_creates_due_rule_and_receives_a_durable_missingness_incident`
passed on 16 October 2026. It creates the rule through the HTTP API, reads it back, evaluates a due
period with an absent result, and verifies the durable recipient-bound missingness incident. The
focused pure classification and calendar-cadence checks remain in
`qualification/test_dashboard_alerts_unit.py`. Browser, native PostgreSQL and four-job CI evidence
remain separate qualification gates and must not be inferred from this local journey.

## Integration notes

- Story: APL-618 / FR-ANA-009.
- Positive user journey: locally passed; no acceptance, CI or deployment movement.
- Security-sensitive paths are recorded in `release-review-1.42.0.json`.
