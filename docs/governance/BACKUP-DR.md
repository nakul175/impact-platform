# Backup and disaster recovery

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: off-server backup chosen, first real-host restore test, a change to `deploy/backup.sh` or `restore-drill.sh`, or an agreed RPO/RTO.

Canonical detail: [DEPLOYMENT-GUIDE sections 6 and 7](../current/DEPLOYMENT-GUIDE.md), [RELEASE-OPS-2026-10](../RELEASE-OPS-2026-10.md), [SUPPORT-RUNBOOK 4.5 and 4.6](../current/SUPPORT-RUNBOOK.md), [Runbooks section 4](../current/Impact-Management-Operational-Runbooks-v1.1.md). This page states the objectives and the honest evidence position.

## 1. What exists

| Item | Fact (source) |
|---|---|
| Nightly verified set | `impact.dump`, `keycloak.dump`, role definitions without passwords, `objects.tar` (evidence volume), checksums, manifest; verified after writing; 7 daily and 4 weekly kept; refused when free disk is below twice the newest set (`deploy/backup.sh`) |
| Weekly restore drill | Sunday about 23:15 UTC, `impact-restore-drill.timer`; restores the newest set into throwaway containers and checks object digests, blob rows, migration checksums, ownership, forced row-level security, and the app role seeing no rows without a tenant; result in `ops/restore-drill.json` and `deploy-status.json` |
| Droplet backups | DigitalOcean daily/weekly droplet backups (an add-on priced in DEPLOYMENT-GUIDE section 1); the only off-server copy |
| Off-server copy of the sets | **None.** Owner decision open ([RELEASE-1-ACCEPTANCE-GAPS](../current/RELEASE-1-ACCEPTANCE-GAPS.md)) |
| Encryption of backup sets | Not encrypted by the application ([KEY-AND-ENCRYPTION-REGISTER](../current/KEY-AND-ENCRYPTION-REGISTER.md) section 3) |

## 2. RPO and RTO

| Scenario | Target (specification) | What the set-up delivers today |
|---|---|---|
| Data damaged, server intact | RPO <= 15 min, RTO <= 4 h (FSD / Runbooks section 4) | RPO up to 24 h (last nightly set), longer if nightly runs failed unnoticed; **RTO not measured on the server.** DEPLOYMENT-GUIDE 6.3 still contains the literal text `RESTORE_TIME_PLACEHOLDER` where a measured time belongs |
| Droplet lost | same | RPO up to the droplet-backup interval; the nightly sets are lost with the droplet; RTO unmeasured |

**No RPO or RTO has been agreed or met.** Requirement VF-DR-001 is PENDING ([RELEASE-ACCEPTANCE](../current/RELEASE-ACCEPTANCE.md) G10). Deletions and revocations are not replayed after a restore (FR-PRV-006, TH27): erased data returns with an old set until it ages out.

## 3. Restore-test log (real host)

A real-host restore test is a restore of an actual staging backup set, performed on the server, with a dated record. Entries:

| Date (UTC) | Set restored | Where | Duration | Result | Record |
|---|---|---|---|---|---|
| *(none)* | | | | | |

Zero entries. The repository holds no dated record of a restore on the staging server. The weekly timer is configured to produce `restore-drill.json` on the server; HANDOVER recorded `RESTORE_DRILL_STALE` as the only alert on 3 October 2026, i.e. no drill result had yet been shown. Owner: add rows from `/opt/impact/ops/restore-drill.json` once a drill has actually run.

### Not real-host restores (listed so they are not mistaken for one)

CI-scale and local-database drills by `scripts/restore_drill.py`, on disposable databases in a development environment (PostgreSQL 17.11), recorded in `docs/evidence/`: `native-restore-drill.json` (2026-10-05T11:21Z, PASS) and `sprint-0.32` to `sprint-0.35` `*-restore-drill.json` (2026-10-05, PASS; one initial 0.33 attempt recorded FAIL). They verify that `pg_dump`/`pg_restore` round-trip data, row-level security, grants and the golden 46.36 result at small size. They do not test the server's backup sets, the evidence volume, the droplet, elapsed recovery time on that hardware, or a person performing recovery. Performance files under `docs/evidence/performance-*` are load measurements, not restore evidence.

## 4. Actions to close the gap

1. Choose off-server storage (owner decision) and copy sets there.
2. Run `deploy/restore-drill.sh` on the server, record the duration, add a row above, replace the placeholder text in DEPLOYMENT-GUIDE 6.3.
3. Agree RPO/RTO with the owner; decide whether nightly granularity can ever meet 15 minutes (it cannot; continuous archiving is not built).
4. Add deletion/revocation replay before any restore is reopened (TH27).
