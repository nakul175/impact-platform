# Impact Management Operational Runbooks

These runbooks define the actions, owners, verification and evidence required to operate the platform safely. Environment-specific resource IDs and escalation routes come from the deployment configuration. The operator uses declared service controls and least-privilege identities. A runbook is complete only when its recovery outcome is verified; an issued command or green process status alone is insufficient.

## 1 Incident ownership and severity

The incident commander coordinates containment and decisions. The platform on-call owns service restoration. Security owns suspected compromise and privileged access. Privacy owns personal-data handling and disclosure assessment. Domain owners verify calculations and business state. A communications owner records authorised notices; these documents do not send any notices.

Severity 1 includes cross-tenant exposure, unauthorised restricted-data disclosure, corruption of official approval or calculation integrity, or a broad core outage. Severity 2 includes significant tenant disruption or a bounded security failure. Severity 3 includes contained degradation with a functioning workflow. Page Severity 1 immediately through the configured route and begin a timestamped incident record. Applicable external notification deadlines are inputs to the organisation's incident policy.

## 2 Deployment and rollback

Trigger: a release candidate has satisfied the applicable gates. Owner: release manager with platform on-call. Verify artifact digests, migration checksums, supported client versions, policy baseline, backup freshness and rollback compatibility. Apply additive migrations with the migration identity. Deploy the same staged artifact to a limited canary and run smoke and critical workflow checks.

Observe per-tenant error rate, durable-save latency, approval correctness, official-value reconciliation, queue age and revocation propagation. An isolation or integrity failure stops rollout immediately. For a runtime regression with compatible data, return to the previous qualified artifact and configuration. For an incompatible migration, execute its forward repair or the rehearsed restore path. Verify both health and the previously failing user workflow, then record the final deployed manifest.

## 3 Database or core outage

Trigger: readiness failure, sustained core errors or failed commits. Owner: platform on-call. Confirm scope and distinguish database connectivity, pool exhaustion, storage exhaustion and slow-query saturation. Stop admitting new bulk work when it threatens ordinary requests. Preserve operation receipts and report uncertain writes as pending reconciliation.

Use the managed database's qualified failover procedure only within permitted regions. Reconnect with bounded retries and validate schema compatibility and session context reset. Reconcile in-progress operations by receipt before replay. Verify one safe read, one durable write, one independent approval and the pooled-result fixture in staging or the authorised production diagnostic scope. Do not erase receipts or requeue every task blindly.

## 4 Backup restore and disaster recovery

Trigger: irrecoverable storage failure or scheduled restore exercise. Owner: platform lead, privacy lead and security lead. Select an integrity-verified backup and record its recovery point. Restore into an isolated network with the API, workers, schedulers and deliveries closed. Recover keys through their separate custody procedure and verify the snapshot and blob manifests.

Replay the independently retained deletion ledger, current holds, identity revocations, grant changes and credential restrictions. Rebuild or invalidate search, dashboard, report and AI caches. Reconcile database revisions, source receipts, attachments and outbox outcomes. Test a deleted participant and revoked principal whose old records are in the backup. Only after isolation and restriction checks pass may traffic and workers reopen in controlled order.

The FSD targets are RPO at most 15 minutes and RTO at most four hours. Measure both from the actual incident or drill timeline. Perform monthly restore exercises and quarterly disaster recovery exercises in the allowed regions. Retain the backup identity, ledger cutoff, integrity results, resumed build and measured recovery outcome.

## 5 Suspected tenant data exposure

Trigger: a cross-tenant response, export, cache entry or search result. Owner: security incident commander. Disable the affected capability or path, revoke relevant sessions and prevent further artifact downloads. Preserve request, policy, job and audit references without spreading exposed content. Identify the affected tenants, objects, output channels and earliest possible exposure.

Reproduce the boundary failure in isolation, correct the underlying policy or query path and test every derived channel using the same data flow. Validate cached artifacts, background jobs, AI retrieval and exports. Reopen only the repaired scope after an independent boundary check. Record disclosures and organisational notification decisions through the configured process.

## 6 Compromised identity or credential

Trigger: suspicious login, leaked token, departed owner or unexpected service activity. Owner: identity on-call and security. Suspend the principal or credential, increment authority epochs and invalidate sessions. Identify scheduled jobs, integrations, pending reports and artifacts that used the identity. Pause or transfer work using an eligible accountable owner.

Rotate the credential through the approved secret path, revoke the old material and limit any required overlap to 24 hours. Verify that new requests, cached permissions and pending effects reject the old identity within the online revocation target. Restore work only after scope, ownership and provider access are rechecked. Never grant a broader emergency role merely to avoid a broken schedule.

## 7 Backlog or stalled worker

Trigger: queue age, expired lease or incomplete item progress exceeds its bound. Owner: worker on-call. Inspect job class, tenant, input revisions, generation, heartbeat and committed item outcomes. Distinguish a dead worker from a slow external provider and enforce per-tenant admission limits. Cancel or reclaim only through the job state machine.

A new worker increments the lease generation. The stale worker must fail its final update predicate. Reconcile source and consumer receipts before replay, and use stable external effect identity where applicable. Verify accepted, rejected, skipped and cancelled totals. Drain the failure queue selectively after fixing the cause; do not mark all jobs successful because the queue is empty.

## 8 Import or migration failure

Trigger: row errors, changed source, wrong totals or interrupted cutover. Owner: data steward and implementation lead. Stop further commit at the supported item boundary. Preserve raw source digest, mapping, preview, expected totals and outcome manifest. Identify which rows committed and whether the chosen atomic or partial mode behaved correctly.

Correct mappings in a new version and generate a fresh impact preview. Reuse permanent source identities so retries do not duplicate records. Controlled replacement requires exact scope and reviewed deletion treatment. For cutover, compare semantic totals, missingness, units, periods and approvals, not only row counts. Release the new source only after the reconciliation gates pass.

## 9 Incorrect official result or report

Trigger: a number, source contribution or report binding does not reconcile. Owner: measurement lead and reporting owner. Freeze publication or withdraw the affected version through the authorised workflow. Preserve the original snapshot and decision history. Trace definitions, sources, exclusions, aggregation, decimal precision and display bindings to isolate the error.

Correct the source or rule in a new version, rerun the golden and affected cohort examples, and obtain the required review. Restate the period when necessary and create a new report version. Record which recipients received the earlier artifact. Verify every numeric occurrence, table and narrative against the corrected authoritative result before republishing.

## 10 File scanner or upload failure

Trigger: scanner outage, digest mismatch, stuck assembly or storage pressure. Owner: evidence service on-call. Keep all unverified content quarantined. Inspect the sealed manifest, part receipts, lease generation and exact file digest. Reject changed bytes; a new source requires a new upload identity.

Resume a qualified scanner only after checking resource and egress limits. Expire abandoned sessions and remove temporary parts that no completed blob or hold references. Verify CLEAN status through the scanner result and byte identity rather than an operator toggle. Confirm that failed and infected files cannot be downloaded or linked into approved evidence.

## 11 Privacy case or deletion failure

Trigger: a store action fails or an executable case approaches its 24-hour deadline. Owner: privacy executor and privacy officer. Check requester verification, authority, plan digest, holds and store inventory. Apply effective restriction promptly where full physical removal is awaiting a bounded retry. Persist the deletion ledger independently before irreversible deletion.

Execute and reconcile every required store action, including revisions, current projections, blobs, search, caches, exports and device-key revocation. A successful database update cannot close a case with remaining blobs or cached identifiers. Retain minimised evidence of each outcome and hold decision. Verify through authorised lookup and restore testing that the content cannot reappear.

## 12 Lost or shared field device

Trigger: reported loss, unauthorised account use or failed device integrity. Owner: collection supervisor and security. Revoke the device and associated offline package, suspend new sync and initiate managed-device action where available. Record the last verified package, expiry and data classes. The residual exposure is bounded by the signed lease and actual device controls.

Provide a replacement assignment without treating unsynchronised local drafts as server records. Reconcile receipts for any submissions already accepted. Re-enrol a recovered device through fresh identity, key and security-profile checks; do not reuse a compromised key. Verify account-switch isolation and local deletion before reassigning a shared device.

## 13 AI provider failure or unsafe output

Trigger: provider outage, ungrounded consequential claim, prompt injection, privacy violation or budget anomaly. Owner: AI on-call and domain owner. Disable the affected use case or provider route. Preserve safe references to source versions, prompt/model configuration, proposal and confirmed command receipts. Do not switch to an unqualified region or retention policy to restore availability.

Reconcile reserved and consumed budget. Review whether an unsafe proposal was merely generated or was confirmed into a draft. Correct any affected draft through the ordinary versioned workflow. Run the use-case evaluation and attack corpus against the repaired configuration. Re-enable only when scope, citation, arithmetic and confirmation gates pass.

## 14 Connector and webhook failure

Trigger: expired credential, upstream permission change, repeated delivery failure or checkpoint mismatch. Owner: connection owner and integration on-call. Pause the connection and record the last durable checkpoint, source identity and delivery receipts. Verify current owner, scope and provider permissions before rotating a credential or resuming.

Replay from the committed checkpoint with source-version deduplication. For outgoing delivery, preserve the business event ID and use a new delivery attempt ID. Recheck destination and credential on every retry and stop after the bounded retry window. Reconcile acknowledged external effects before replaying an uncertain request. Verify a representative allowed record and a denied record before clearing degraded status.

## 15 Audit gap or privileged support incident

Trigger: missing checkpoint, digest mismatch, unexplained administrator effect or support expiry violation. Owner: security and platform leads. Freeze affected sensitive capabilities while preserving ordinary permitted reads where safe. Compare database audit, signed checkpoints, operation receipts and deployment logs. Treat truncation and missing batches as integrity failures even if remaining hashes verify.

Revoke the support session or privileged identity and establish the exact action scope. Repair through an authorised append-only correction record; never manufacture a historic decision or silently edit audit history. Verify checkpoint continuity and repeat the affected privileged workflow under an independent observer before reopening.

## 16 Capacity degradation and noisy tenants

Trigger: p95 or p99 breach, queue contention or an abusive tenant workload. Owner: platform on-call. Break down ordinary actions, tenants and background classes rather than averaging away the affected cohort. Enforce two active bulk jobs and two active AI jobs per tenant with 20 queued in each class. Reject excess work with visible retry guidance.

Throttle or pause the responsible background class, inspect query plans and storage behaviour, and scale only within tested limits. Preserve ordinary saves and approvals. Reproduce the workload in staging and verify the FSD peak, burst and soak profiles. Record the capacity change and the largest-tenant outcome before raising admission limits.

## 17 Closure evidence

Every incident closes with verified recovery, affected scope, root cause, corrective action, owner and a repeatable regression test. Attach the exact build and configuration manifest, relevant receipt or audit references and measured recovery time. Preserve organisational notification and retention decisions separately from broad operational logs. Update the runbook when the exercise reveals an inaccurate command, missing dependency or failed assumption.
