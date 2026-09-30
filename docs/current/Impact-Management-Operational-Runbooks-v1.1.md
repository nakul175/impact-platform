# Impact Management Operational Runbooks

Version 1.1   27 September 2026

These runbooks define the actions, owners, verification and evidence required to operate the platform safely. Environment-specific resource IDs and escalation routes come from the deployment configuration. The operator uses declared service controls and least-privilege identities. A runbook is complete only when its recovery outcome is verified; an issued command or green process status alone is insufficient.

## Release interpretation

Documentation edition 1.1 is reconciled with application build 0.12.0 on 27 September 2026. The document edition and application build use different version sequences. The original business requirements and their acceptance conditions remain authoritative. No requirement has been removed or weakened to match the current code.

Build 0.13.0 increment (28 September 2026): startup applies sixteen migrations and /health/ready requires schema 16. The Tenant lifecycle panel gains Authority renewal: when delegated administrative authority approaches expiry, the current owner proposes a bounded extension, the second administrator consents and an independent operator approves; expired authority cannot be renewed, and an expired pending proposal must be withdrawn or rejected before a new one. Focused reproduction: .venv/bin/python scripts/run.py test --pytest-path qualification/test_authority_renewal.py and .venv/bin/python scripts/run.py renewal-browser. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.14.0 increment (29 September 2026): three operator procedures now exist as scripts and are described in OPERATIONS-GUIDE.md ("Native PostgreSQL: provisioning logins, guard, restore drill"): provisioning the four login roles with scripts/provision_logins.py (IMPACT_ADMIN_DSN, IMPACT_LOGIN_PASSWORD_APP/IDENTITY/PLATFORM/MIGRATOR, --revoke-public-connect), running migrations as impact_migrator with scripts/migrate.py, and the backup and restore drill scripts/restore_drill.py (pg_dump -Fc, pg_restore into <database>_restored, migrator checksum pass, golden value, row counts, ownership, RLS, grants and fences verified, copy dropped; IMPACT_PG_BIN when the client must be newer than the server). /health/ready answers 503 with reason code PRIVILEGED_RUNTIME_CONNECTION, SHARED_RUNTIME_LOGIN or PLATFORM_NOT_CONFIGURED when the runtime login topology is wrong; correct the connection strings rather than widening a login. The drill has been executed only against disposable qualification databases (CI scale, 3.4 MB); no production backup, restore, RPO or RTO exists, and the backup, DR and incident procedures of this document remain target design. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.15.0 increment (29 September 2026): OPERATIONS-GUIDE.md gains a "Live identity provider" section: the configuration fields (issuer, client_id, audience, jwks_url, authorization_url, token_url, end_session_url, required_acr, provider_account_url, client_secret supplied as IMPACT_CLIENT_SECRET for a confidential client only), the realm requirements (S256 PKCE, callback, post-logout and back-channel URLs on the public origin, sid required, refresh tokens off, short access tokens, an ACR map reaching required_acr only with the second factor), the logout and back-channel endpoints, and the Host allow-list rule that the provider must call the public hostname. For a compromised account, ending its provider sessions now revokes the matching platform sessions through back-channel logout, but already issued bearer access tokens stay valid until exp. No production provider, recovery, key rotation or provider-outage procedure has been exercised. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.16.0 increment (29 September 2026): OPERATIONS-GUIDE.md gains a "Worker and email delivery" section: running workers (make dev, make worker, --once, graceful SIGTERM), the impact_worker_login login, the worker's own configuration and IMPACT_<FIELD> variables, the invitation and delivery secrets it shares with the API and what rotating them does to queued rows, the SMTP adapter and its error classes, the heartbeat and the operators' Workers panel, and dead-letter inspection by query (there is no re-queue API; repeat the business action instead, and never edit outbox_delivery by hand). Readiness requires schema 18. No email provider, bounce handling, metrics or alerting exists, and rows held by a suspension are never sent. The Word copy is unchanged and will be regenerated at the next documentation edition.

The application is a development delivery. The requirement ledger records 74 PARTIAL and 233 PENDING requirements, with zero fully accepted. PARTIAL means a bounded implementation and some evidence exist, not that all acceptance conditions are satisfied. PENDING means the requirement has no accepted implementation coverage in the ledger; a read-only surface or reference example does not establish delivery.

Recorded qualification contains 325 application checks, 143 design-reference checks and 81 browser checks. One expired-offline-grant test is deselected and is not a pass. Local integration uses fresh in-memory PGlite PostgreSQL 17.5 with serialized transactions. Native PostgreSQL concurrency, live identity-provider assurance, disaster recovery, load qualification and production acceptance remain open.

The original BRD and FSD use R1, R2 and R3 requirement assignments. The later 16-stage delivery roadmap is an implementation sequence. Roadmap stage 1 and baseline R1 are different groupings; neither is complete. Requirement release assignments remain unchanged.

The sections explicitly marked current implementation describe this build. Retained target-design sections describe required future behavior unless the current implementation section states otherwise. Complete source, contracts, test evidence and original documents accompany this edition. Start at DOCUMENTATION-INDEX.md and TRACEABILITY.csv for exact locations and evidence boundaries.

## Current operational scope

The runnable environment is local development with synthetic data. The reference operational runbooks below remain production requirements and have not been exercised against a production deployment. Do not execute managed failover, key rotation, external notification or disaster recovery steps against nonexistent or unapproved resources.

## Local start and diagnosis

From a fresh source checkout, run make setup and make dev. Confirm /health/live and /health/ready, which checks schema 18, then sign in using the generated local account credentials. If startup fails, inspect the specific runner directory under .local, check dependency and migration errors, and preserve the failure evidence. Do not commit that directory because it contains credentials, keys and data.

For an uncertain write, preserve the operation identifier and reconcile its receipt under current authority. Retry the identical command; do not invent a new operation identifier until the outcome is known. A stale revision requires reloading and reviewing the change. For denied access, check current workspace, membership, grant, scope, purpose, tenant state and recent configured assurance. Do not expand privileges merely to clear an error.

## Tenant readiness and recovery-contact repair

An activation or reactivation refusal may be caused by missing or invalid recovery-contact evidence. Inspect the current eligibility reason and pinned owner/identity/expiry information. The current owner can nominate a new or renewed registered contact, including while Suspended. The nominee provides fresh consent and an independent operator reviews the exact nomination. Recheck full tenant readiness before reactivation. Existing work is not automatically replayed or resumed.

If a nominee account is revoked, the old proof is invalid. A new sign-in does not rewrite the original proof; a reviewed renewal is required. If the current owner is unavailable, stop at the unsupported recovery boundary. The platform has no qualified operator bypass, factor reset or custody reset. Preserve records and escalate through the separately approved organizational process once defined.

## Release and incident records

Record build, schema, configuration, affected tenant and safe correlation/operation identifiers, observed behavior, containment, result and reviewer. Never include bearer tokens, local passwords or private participant data in a ticket. Current run evidence is in docs/evidence; production on-call contacts, severity response times, provider procedures, actual backup locations, RPO/RTO drill outcomes and release approvers remain to be assigned and qualified.

The current deployment is not production approved. Follow RELEASE-ACCEPTANCE.md and OPERATIONS-GUIDE.md for the exact unfulfilled gates and environment inputs. Historical runbooks remain useful target procedures, not evidence that a drill occurred.

## Retained requirements and target design

The following baseline sections retain their requirement IDs and intended behavior. Implementation status is governed by the current profile above and the accompanying traceability register. Planned components are not represented as deployed services.

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
