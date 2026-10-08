# Retention schedule

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: any change to `apps/api/impact_api/retention.py`, a tenant retention policy feature, or a legal retention requirement being identified.

Status: **the technical schedule below is read from code; it is not a legally approved schedule** (DATA-GOVERNANCE says so). Agent-drafted summary 2026-10-08; not reviewed by a person or counsel; no compliance is claimed. Canonical code: `apps/api/impact_api/retention.py`; behaviour: [RELEASE-0.25b](../RELEASE-0.25b.md), [RELEASE-0.27-security-privacy](../RELEASE-0.27-security-privacy.md).

## Enforced by the worker's retention sweep (daily per tenant)

| Data class | Rule | Action | Tenant policy range |
|---|---|---|---|
| `OPERATION_RECEIPT` | 7 days after the command (idempotency window) | Delete | 7 to 90 days (lengthen only) |
| `UPLOAD_SESSION` | Open past 24 hours | Expire (bytes of an expired OPEN upload remain in the object store) | Fixed |
| `PRIVACY_EXPORT_PACKAGE` | 7 days after production; download log stays | Delete | 1 to 30 days |
| `OUTBOX_RECIPIENT` | 30 days after the delivery reached a final state | Redact the sealed address | 7 to 365 days |
| `SECURITY_EVENT` (access denials) | Audit window, default 2,555 days (7 years), floor 365 days | Delete beyond window | 365 to 3,650 days |

A tenant policy needs independent approval and is applied from the insert-only `retention_policy_binding`. Each sweep writes an insert-only `retention_proof` row per class.

## Kept without a deletion rule

AuditEvent records (never deleted); object revisions of observations, results, snapshots, reports and publications (immutable; payload removal only through an approved privacy case); `report_export_artifact` rows (never purged); principal and membership identifiers (pseudonymous keys needed for audit and independence). Evidence files: no automatic expiry. A **retention hold** pins one object against erasure until released by a different person.

## Backups and AI

Backup sets: 7 daily and 4 weekly, then removed; they hold data the live system has erased until they age out ([BACKUP-DR](BACKUP-DR.md)). Droplet backups: interval set by the DigitalOcean plan. AI advisory results: no schedule defined; TBD (owner: Nakul Jain). Provider-side retention for the AI call is not established (`store:false` only disables response storage by the API).

## Not decided

Legal or contractual minimum and maximum periods per data class and jurisdiction; tenant-level schedules for programme and evidence data; deletion on tenant closure; reminders for holds: all TBD (owner: Nakul Jain; counsel).
