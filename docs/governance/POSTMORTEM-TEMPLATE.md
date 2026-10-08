# Postmortem template (blameless)

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: after the first postmortem, adjust to what was missing.

Copy to `docs/postmortems/YYYY-MM-DD-<slug>.md`. Describe systems and decisions, not people's faults. Never include tokens, passwords, secrets or personal data.

```
# <Title>
Date of incident: · Severity: · Author: · Reviewed by: · Status: draft | reviewed
Build and schema at the time:  (from deploy-status.json)

## Summary (3 sentences: what happened, who/what was affected, how it ended)

## Impact
- Tenants / users affected (counts, not names):
- Data affected (class, not content): confidentiality / integrity / availability
- Duration: detected at / contained at / restored at (UTC)

## Timeline (UTC)
| Time | Event | Source (alert, log, report) |

## Detection
How was it found? How long after it began? Which alert should have fired and did not?

## Cause
Immediate cause; contributing conditions; why existing controls did not stop it.

## What went well / what went badly / where we were lucky

## Decisions that were hard (and the information available then)

## Actions
| Action | Type (prevent / detect / mitigate) | Owner | Due | Linked item |

## Evidence kept
Paths to logs, status snapshots, correlation identifiers.

## Requirement and register impact
Ledger rows, threat-register entries, runbooks to update.
```
