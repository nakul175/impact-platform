# Diagnosis promotion: bounded writer quiescence

US-DX-01a remains the sole active story. This is local deployment preparation, not a deployment receipt or human release decision.

The existing deployment script ran migrations while the previous API, worker and executor could still write. Migration 0047 takes DDL locks before per-tenant locks; application writes take the tenant lock first. Controlled writer quiescence is required to avoid that inversion during promotion.

The proposed script now builds the matching image before interruption, waits for PostgreSQL, then stops only API, worker and executor with a 120-second grace period. It records their previous image/container identifiers privately, checks clean exit codes 0 or 143 without OOM, and re-enumerates to refuse replacement or surviving writers. An existing administrator connection performs a read-only probe: no other application-database client connections and no prepared transactions may remain. Fresh schema absence is recorded as 0; otherwise the actual ledger maximum is recorded. Failure refuses migration and retains stopped writers.

The credential-free checkpoint is atomically written with mode 0600 to `state/writer-quiescence.json`, before migration starts and again on ordinary failure. Public status reports the phase, original schema, migration-start flag and checkpoint existence; container/image checkpoint details stay private. Short legacy checkpoint log lines are redacted from public status as well. Neither the checkpoint nor a migration command failure proves that earlier additive migrations did not commit.

The probe closes before migration begins. It does **not** prevent an external operator/client reconnecting afterward. An accountable operator must keep every external writer disconnected throughout the maintenance window; this is not a database-wide authenticated writer fence. Existing account/bootstrap behavior is unchanged and requires its existing authority. Do not run bootstrap against production identities under this local coding authorization.

## Actual local qualification

The first helper-unit run caught the empty-array failure under macOS Bash 3.2 with `set -u`; its raw failure is preserved. The shell loop was corrected. Subsequent actual Bash/fake-command tests exercise stop/probe ordering, failure refusal, normal/unexpected exit codes, fresh deployment, service isolation, replacement writers, invalid probe output, and durable private/public status behavior. Python fake-connection tests cover read-only transactions, administrator visibility, session/prepared counts and exception redaction. These qualify orchestration logic, not Docker shutdown or in-flight production work.

A separate actual owned PostgreSQL 17.10 run verifies fresh schema 0, registered schema 47, refusal while another real client remains, refusal for a real prepared synthetic transaction, and zero counts after cleanup. The cluster was stopped; no runtime login/account or production data was created. This proves the probe against native PostgreSQL, not the Compose/container path.

## Promotion and failure gates

Before promotion: reviewed exact candidate; all four hosted jobs plus `checks`; spending and export authority; actual release/current-authority/privacy dispositions and independent human gates; controlled maintenance window with accountable operator; backup and current matching schema/checksum/image observations. The container gate must verify graceful in-flight worker/executor handling, disappearance of connections, failure/refusal and matching-image recovery.

On failure keep the failed checkpoint. Never restart the old image automatically, downgrade a migration, remove volumes, restore an older database to discard writes, or manufacture command retries. An operator may use the previous matching image only after separately proving that the complete original schema/checksum state is unchanged. If an additive migration committed, use a compatible forward fix and preserve immutable history. Reopen traffic only after matching API/worker/executor health and bounded synthetic smoke checks pass. Deployed delivery remains 0/50 until the actual gates and live verification pass.
