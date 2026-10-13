# Diagnosis worker fence: bounded preparation

Status: source-inspected proposal only, not implemented, applied, tested or accepted. Active story remains US-DX-01a / APL-361; task APL-666 remains In Progress. Candidate inspected at 2e4dcaeff4ebfbcbd26bb8b093a4677fe95136c4. This record does not change frozen criteria or claim the broader persistence task complete.

## Actual dependency inventory

| Dependency | Existing source | Access needed |
| --- | --- | --- |
| Authority reminder scan | worker.py remind() joins membership_current to object_registry | SELECT Membership registry state |
| Reminder creation | worker.py remind() calls store.write("Notification") | INSERT Notification registry and revision |
| Reminder audit | worker.py remind() calls store.audit(), which calls write("AuditEvent") | INSERT AuditEvent registry/revision; shared store reads referenced revision identities and audit revision numbering |
| Frozen export rendering | worker.py export_model(), its revision() helper | SELECT Report, ReportTemplate, Snapshot, CalculatedResult, Target pinned revision payloads; refuse restricted/missing/wrong-kind content |
| Existing worker grant regression | qualification/test_worker.py kept/revoked grants and export-job grants | Existing table privileges must remain unchanged; RLS row restriction adds to tenant fencing |
| Current isolation gap | migrations0003/0024 retained grants;0025/0026 narrowed unrelated access | AIDiagnosis registry/revision has no worker-specific kind policy |

The export helper checks expected kinds after reading the revision. Its application check does not restrict a compromised worker's direct SQL read. Forced tenant RLS restricts tenants but does not isolate diagnosis kinds within a selected tenant. No executed exploit is claimed here.

## Prepared code and design review

[Draft SQL](diagnosis-worker-fence.DRAFT.sql) adds two RESTRICTIVE policies, scoped to impact_worker, excluding AIDiagnosis for both USING and WITH CHECK. It keeps every existing table grant and tenant policy intact. An allowlist for all worker-readable kinds would broaden this change and risk omitting historic duties; this draft narrows only the diagnosis exposure identified in the current story.

PostgreSQL restrictive policies combine with existing permissive policies by AND; a permissive policy added later cannot reopen diagnosis access for a worker-derived role. The actual provisioned runtime must be non-owner/NOBYPASSRLS and inherit the worker role; verify both the login and SET ROLE paths. A login that also inherits impact_app still has the restrictive worker policy; dual-role effects must be explicitly tested rather than assumed. The migration owner remains outside this policy; privacy definer behavior and tenant fencing require regression.

This is not a complete defence against every inference via inherited write privileges and foreign-key errors, or every other domain kind. It does not add malformed problem/order SQL constraints or protected evidence selectors. Those task gaps remain separate. It changes no official arithmetic, natural-person independence, API authority, immutable history or exact-operation semantics.

## Required actual qualification before promotion

1. Through real provisioned worker login and SET ROLE: select existing Draft/Completed/corrected diagnosis registry and revision by exact IDs and broad scans; expect no rows. Repeat in a foreign and unset tenant. Preserve exact app-visible revision/history payloads.
2. Worker INSERT diagnosis registry and new revision must fail with RLS refusal and leave counts unchanged. Use valid tenant/principal/FK identifiers so refusal is actually the policy, not malformed fixture data. Existing UPDATE/DELETE denial and immutable revision guard remain intact.
3. App read/manage operations and exact retries remain authorised by current capabilities. Platform/identity negative tests stay negative. Privacy/removal rules stay intact.
4. Actual reminder pass creates Notification and AuditEvent; recipient, deduplication and retry invariants pass. Worker table-grant kept/revoked tests pass unchanged.
5. Actual export jobs for existing supported formats and pinned chart targets still render; restricted/missing/wrong-kind pins remain refused. Native lease concurrency, cancellation and retry regression remains passing.
6. Populated44-to-next upgrade and real API restart/pg_dump restore preserve both policy definitions and exact diagnosis history/receipts. Restore uses replacement restricted runtime roles, not owner reads alone.
7. Full affected integration plus current-head required CI/container and human security review are still delivery gates. Structural checker success is not release acceptance.

## Authority and evidence review

The current window permits local coding and reversible preparation but explicitly excludes account or role changes. This draft is not registered or executed against any database. Do not apply a runtime permission change or promote to an active migration under this record alone; resolve the applicable authority at the concrete change boundary. Before promotion, claim the integration writer, inspect current migration count, assign the next contiguous filename, update schema/version/contracts/data dictionary and append a security impact entry. Never edit0044 or prior applied migrations.

Separate root-agent code review checked existing read/write/export duties against the narrow proposal. Separate evidence review confirms this is source inspection only: zero new runtime tests, no native role/concurrency/restore pass, no human signoff or release acceptance. Source hashes in the companion receipt bind this inspection. Original source errors from an initial lookup of a nonexistent report_exports.py were corrected by inspecting worker.py export_model(); no missing file is counted as inspected.
