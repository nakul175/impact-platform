# Service-level objectives and alert catalogue

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: a change to `deploy/ops_alerts.py` alert codes, to the FSD non-functional targets, or the first measurement on the staging server.

**The targets below are proposed targets taken from the functional specification, not measured service levels. No SLO is met, monitored or reported against on the staging server.** The staging server is a single droplet for synthetic data; nobody is paged.

## 1. Proposed objectives

| Objective | Proposed target (source) | Measured evidence | Status |
|---|---|---|---|
| Interactive response: reads, 100-row lists, saves, approvals | p95 <= 2 s, p99 <= 5 s (FSD VF-PER-001, NFR-PER-001) | One run on a shared 2-CPU sandbox, not the server: [2026-10-01](../evidence/performance-2026-10-01.md) (read, list, save within bounds) and [peak profile 2026-10-02](../evidence/performance-2026-10-02-peak.md) (approval p95 2,119.6 ms: NOT MET) | Not met under peak in the sandbox; not measured on staging |
| Dashboard response | p95 <= 5 s, p99 <= 10 s (VF-PER-002) | Warm dashboard within bound in the same runs; cold reads recorded as NOT MEASURED | Partial, sandbox only |
| Report export | render <= 300 s (VF-PER-005) | Rendered in 142.8 ms p95 for a small package; verdict NOT MEASURED in the file | Not measured |
| Data freshness | calculation to dashboard <= 60 s (VF-PER-006) | MET in the 2026-10-01 sandbox run | Sandbox only |
| Core availability | >= 99.9 percent monthly, per critical journey and tenant cohort (VF-AVL-001) | None. No synthetic-journey monitor exists | Not measured |
| Recovery point / time | RPO <= 15 min, RTO <= 4 h (FSD/HLD target) | Not met: nightly sets give up to 24 h of loss ([BACKUP-DR](BACKUP-DR.md)) | Not met |
| Dependency degradation | Fail closed with reason codes (VF-AVL-002) | [QA-DEGRADATION-2026-10](../QA-DEGRADATION-2026-10.md): PARTIAL | Partial |

Requirement state for all of these is PENDING or PARTIAL in the [completion ledger](../COMPLETION-LEDGER.md). Error budgets, burn-rate alerts and a monthly SLO report do not exist: TBD (owner: Nakul Jain).

## 2. Alert catalogue (what exists)

Source of truth: `deploy/ops_alerts.py` and [SUPPORT-RUNBOOK](../current/SUPPORT-RUNBOOK.md) section 2. The check runs every 5 minutes (`impact-ops-check.timer`), writes `deploy-status.json` and `ops-status.json`, shows a service-notice banner to signed-in users, and delivers NEW, CLEARED and REMINDER transitions to a signed webhook and/or e-mail only if `ALERT_WEBHOOK_URL` or `ALERT_EMAIL_TO` is set. At handover none was set on staging (CLAUDE.md section 11, "Operations").

| Code | Severity | Means | First step |
|---|---|---|---|
| `BACKUP_MISSING` | critical | No verified backup set | Take one (runbook 4.5) |
| `BACKUP_STALE` | critical | Newest set older than 26 h | Take one; read backup log |
| `BACKUP_FAILED` | critical | Last attempt failed | Runbook 4.5 |
| `BACKUP_REFUSED_DISK_LOW` | critical | Less free space than twice the newest set (floor 1 GB) | Runbook 4.4 |
| `DISK_LOW` | warning below 10 % or 2 GB free; critical below 5 % or 1 GB | Disk filling | Runbook 4.4 |
| `CONTAINER_UNHEALTHY` | critical | A service is absent, stopped or unhealthy | Runbook 4.2 |
| `WORKER_STALE` | critical | No worker heartbeat within 120 s | Runbook 4.2 |
| `DELIVERIES_DEAD` | warning | Notices or e-mails failed for good | Runbook 4.3 |
| `QUEUE_BACKLOG` | warning | More than 200 unsent deliveries or unfinished jobs | Check `WORKER_STALE` first |
| `SCHEMA_MISMATCH` | critical | Database and build disagree | Roll forward (DEPLOYMENT-GUIDE section 7) |
| `OPS_SUMMARY_UNAVAILABLE` | warning | API's operations summary unreadable | Check the `api` container |
| `RESTORE_DRILL_FAILED` | critical | Last drill failed | Runbook 4.6 |
| `RESTORE_DRILL_STALE` | warning | No drill in 8 days | Run it by hand |

## 3. Known gaps

- No paging, acknowledgement or escalation tooling; no metric history (request counters are per process, in memory; `GET /v1/platform/metrics`, operators only).
- `QUEUE_BACKLOG` and DEAD counts cover at most 200 custody tenants (DEAD capped at 50). The alert's worker window (120 s) differs from the Workers panel (60 s).
- Named on-call people: none. `IMPACT_ONCALL_ROUTE` is an unsupplied release input ([`env.example`](env.example)); the template is `deploy/on-call.example.json`.
- The readiness exercise (`deploy/readiness-exercise.sh`) rehearses alert, delivery and clearance in CI, not with a person on call.
