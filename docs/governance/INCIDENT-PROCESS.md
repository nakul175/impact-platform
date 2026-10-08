# Incident process

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: a named on-call route, a real-data deployment, or the first real incident.

Status: **agent-drafted 2026-10-08 as a frame over existing runbooks; not reviewed by a person; not rehearsed with people.** There is one staging server and one accountable owner; no incident has been run through this process.

Existing procedures are not repeated here: [Operational Runbooks v1.1](../current/Impact-Management-Operational-Runbooks-v1.1.md) (17 target runbooks, section 1 severity) and the live [SUPPORT-RUNBOOK](../current/SUPPORT-RUNBOOK.md) (sections 3, 4 and 5: first steps, escalation, ticket hygiene, section 4.11 suspected personal-data exposure). Alerts: [SLOS-AND-ALERTS](SLOS-AND-ALERTS.md).

## 1. Severity (from Runbooks section 1)

| Level | Examples |
|---|---|
| Sev 1 | Cross-tenant exposure; unauthorised restricted-data disclosure; corruption of official approval or calculation integrity; broad core outage |
| Sev 2 | Significant tenant disruption; a bounded security failure |
| Sev 3 | Contained degradation with a working workflow |

Response times per severity: TBD (owner: Nakul Jain).

## 2. Roles

Incident commander, platform on-call, security, privacy, domain owner, communications owner: defined in Runbooks section 1. Today every role maps to the owner; named deputies: TBD (owner: Nakul Jain). External notice deadlines (for example under DPDP Act 2023 or GDPR) are inputs to the organisation's own process; this repository sends no notice and states no deadline.

## 3. Flow

1. **Detect:** alert code, user report, or log review. Open a timestamped record straight away.
2. **Triage:** assign severity; record build and schema (`deploy-status.json`), affected tenant, safe correlation and operation identifiers, observed behaviour.
3. **Contain:** use the narrowest control that exists (suspend a tenant, revoke a grant, rotate a secret with `deploy/rotate-secrets.sh`, roll forward). Do not delete evidence; do not retry an uncertain external mutation blindly.
4. **Restore and verify:** follow the matching runbook; confirm with the status page and, for data, with the restore checks in [BACKUP-DR](BACKUP-DR.md).
5. **Communicate:** the communications owner decides who is told; the record never contains tokens, passwords or personal data (SUPPORT-RUNBOOK section 7).
6. **Review:** for Sev 1 and Sev 2, and any near miss that exposed a control gap, write a blameless review within an agreed time (target TBD) using [POSTMORTEM-TEMPLATE](POSTMORTEM-TEMPLATE.md); file it in `docs/postmortems/` (create on first use) and link follow-ups to the next-delivery list.

## 4. Where the record goes

`docs/postmortems/YYYY-MM-DD-<slug>.md`. Postmortem count to date: 0.
