# Current implemented API inventory

**Active local candidate 0.33 (5 October 2026):** domain API 1.24.0 has 260 implemented operations, platform 1.10.0 has 52; schema 39. Two dedicated plan impact-reference operations and thirteen closed internal-member-advice operations reuse existing AI enablement capabilities. The eligible-member directory selector requires separate current directory authority. HumanAdviceCase has no generic entity/export routes. The registered bootstrap profile hash is unchanged. [Generated inventory](../API-INVENTORY.md), [candidate record](../RELEASE-0.33-tola-ai-extension.md). Focused and combined qualification is in progress; no deployment or acceptance.

**Current local review candidate 0.32 (5 October 2026):** domain API 1.23.0 has 245 implemented operations; platform API 1.10.0 has 52; schema 37. Added domain reads: `list_ai_adoption_revisions` and `get_ai_adoption_guidance`, both under current scoped `ai.enablement.read`. Eight control-plane access-upgrade operations cover the global inbox, tenant directory/preview/proposal and accept/approve/reject/cancel decisions. The existing generated onboarding profile hash is unchanged. Current generated tables are in [API inventory](../API-INVENTORY.md); exact contracts and evidence are in [release record](../RELEASE-0.32-tola-ai-sprint.md). No deployment or acceptance.

**Current review candidate, 5 October 2026:** build 0.31.0, domain API 1.22.0 (**243 operations**), platform API 1.9.0 (**44 operations**), schema 35 unchanged. Three deterministic planning reads use the existing `ai.enablement.read` capability; no new role bundle, ceiling or migration. Local implementation and evidence are recorded; seven unchanged Mac failures keep the overall application gate failed, and hosted/native qualification remains outstanding. No deployment or requirement acceptance is recorded. [Release record](../RELEASE-0.31-nonprofit-ai-planning.md) and [development/support map](../nonprofit-ai/v1.0/DEVELOPMENT-0.31.md). The tables below are generated from the current implemented contracts; earlier version notes are historical, and their deployment statements are not fresh checks.

## Nonprofit planning contract changes in 0.31

| Method | Tenant-relative path | Operation | Behavior |
|---|---|---|---|
| POST | `ai-enablement/cost-comparison` | `compare_ai_procurement_costs` | Supplied decimal source amounts only; incomplete costs remain unknown; no record or procurement approval |
| POST | `ai-enablement/pilot-evaluation` | `evaluate_ai_pilot` | Self-reported baseline/pilot time including review and sample normalization; no official impact |
| GET | `ai-enablement/task-templates` | `get_ai_task_templates` | Four versioned manual practice worksheets; no model execution or certification |

All three return 200 and recheck current tenant/read authority. Closed request DTOs reject unknown nested fields and duplicate JSON keys. The two computations have no operation ID because they do not persist, issue a receipt or queue an external effect. Saving their optional original source inputs uses the existing POST/PUT plan routes, `ai.enablement.manage` plus current read authority, expected revision and exact-operation receipt rules. The original six required plan fields remain valid; an older client update omitting `planning` preserves any existing snapshots and their practice edition. Explicit null members clear the optional source inputs. Read responses add `content_compatibility`, including CURRENT/STALE/UNKNOWN guide status, stable/legacy/unavailable learning IDs and `historical_snapshots_available:false`. None of this response metadata is client-owned approval or archived guidance.

## Historical version notes

Build 0.30.0 review update: save named AI adoption drafts, search and compare eight source-backed tools, record practical learning progress, draft procurement questions and track a pilot checklist. Schema 35/domain API 1.21.0, 240 implemented operations. Not merged or deployed; live advisory needs funded API credits. See `RELEASE-0.30-ai-adoption-tool.md`.

**Proposed local 0.30.0 (5 October 2026):** nonprofit AI enablement, with readiness/capacity/procurement guidance and separately authorised advisory drafts. Three domain operations (1.20.0), schema 34. Not merged or deployed. See [release note](../RELEASE-0.30-nonprofit-ai-enablement.md). Marketplace transactions remain unavailable.

Proposed local build 0.29.0: domain API 1.19.0, 232 operations. Added `GET frameworks/{object_id}/logframe.csv` and `.xlsx`, with required `revision_id` query UUID and separate `framework.export` capability. Both recheck approved-register membership, current programme/framework/indicator visibility and audit successful generation. No platform API/schema change or staging deployment. See [release note](../RELEASE-0.29-logframe-reuse.md).

Proposed 0.28.0 PR 1: domain API 1.18.0, still 230 operations. `action_imports_commit` above 50 staged rows returns Queued and a job ID; reads show `data.processing` with Queued/Running/Committed/Failed and closed error class. The internal commit request is omitted. Platform API 1.9.0 (still 44 operations) extends `list_workers` with `kind`, `succeeded` and `failed`, and nullable delivery counters for application executors. Current staging remains 0.27.0.

Build 0.27.0 (integration of PRs #67–#77, [RELEASE-0.27.md](../RELEASE-0.27.md)). The domain contract moves from 1.16.0 (207 operations) to **1.17.0 with 23 added operations, 230 in all** — the last 23 rows of the domain table: web forms continued (#73, [RELEASE-0.27-forms.md](../RELEASE-0.27-forms.md)): `list|create|get|patch_collection_rounds` (`collection-rounds.read`, `.draft.create`, `.draft.edit`; MEL_ADMIN, PROGRAMME_MANAGER), `list|create|get|patch_assignments` (`assignments.*`; a member without `assignments.draft.create` at TENANT scope lists only the assignments they hold), `action_assignments_reassign` (`assignment.reassign`, PROGRAMME_MANAGER; history in the revision chain), `action_submissions_correct` (`submission.correct`, AUTHOR and ENUMERATOR, with the bound capabilities of submit), `get_form_completeness` (`forms.read`) and `get_round_coverage` (`collection-rounds.read`); reports and dashboards (#71): `indicator_dashboard_sources` (`GET …/indicator-instances/{object_id}/dashboard-sources?period_id&limit&cursor`, `dashboards.read`) and `indicator_definition_portfolio` (`GET …/indicator-definitions/{object_id}/portfolio?period_id&limit&cursor`, `dashboards.read`), and `ReportSection.charts` on report create/patch; security and privacy (#74): `list_access_denials` (`access-denials.read`, OWNER and TENANT_ADMIN), `list|get|create|patch_retention_policies` (OWNER, TENANT_ADMIN, PRIVACY), `action_retention_policies_approve` (`retention-policy.approve`, TENANT_ADMIN and PRIVACY, 300 s, a natural person other than every author), `list|create_retention_holds` (`retention-holds.read`, `retention.hold`, 300 s) and `action_retention_holds_release` (`retention.release`, 300 s, a person other than the placer); `create_audit_export` answers format `impact-audit-export-v2` (DENIED lines, `occurrences`, manifest `denial_count`) and `list_retention_schedule` gains `source` and `policy_id` per class. Imports (#68): the staged preview's values gain `source_key` and `planned`, `counts` gains `unplanned` and the preview gains `plan_check` (no operation change). `GET /v1/tenants/{tenant_id}/me/access` adds `custody` (#77). `access-policy.json` has 351 policy rows and 235 capabilities; the 230 implemented operations use 133 non-purpose capabilities, all delegable; 56 policy rows require fresh assurance and 19 are purpose-required. The control-plane contract moves from 1.7.0 (42 operations) to **1.8.0 with two operations, 44 in all** (#72): `renew_platform_operator` and `deactivate_platform_operator` (`POST /v1/platform/operators/{identity_id}/actions/renew|deactivate`; identity-authorised: another active operator of another natural person; fresh assurance; `expected_revision` is the operator's `revision_id`), and `list_platform_operators` returns `revision_id`, `state`, `updated_at` and `changes`. New support route outside both contracts (#76): `GET /v1/status` — any signed-in identity (anonymous 401); `{generated_at, state: OK|DEGRADED, poll_seconds, notices[]}` from a closed catalogue, plus `detail` (sources, counts, server alerts, on-call rota) for platform operators only. Errors (#76): the contract's `Error.code` enum now admits `SERVICE_UNAVAILABLE`, the code every 503 has carried since v0.1 (`DEPENDENCY_UNAVAILABLE` is kept as the design alias), and each 503 description names the reason codes (`DATABASE_UNAVAILABLE`, `IDENTITY_PROVIDER_UNAVAILABLE`, `OBJECT_STORE_FULL`, `OBJECT_STORE_UNAVAILABLE`, `OBJECT_MISSING`, `PLATFORM_NOT_CONFIGURED`); the wire is unchanged.

Build 0.26.0 (v0.26a usable staging, [RELEASE-0.26a.md](../RELEASE-0.26a.md)). The domain contract moves from 1.15.0 (197 operations) to 1.16.0 with 10 added tenant-administration operations, 207 in all — the last ten rows of the domain table: reviewed purpose-bound grants (`list_purpose_grants` with `access-requests.read`; `request_purpose_grant` with `grant.request`; `approve_purpose_grant` and `reject_purpose_grant` with `grant.approve`, natural-person independence from requester and member) and reference data (`create_reporting_calendar`, `extend_reporting_calendar`, `create_workflow_template`, `create_report_template`, `create_geography`, `apply_reference_defaults`, all with the new capability `reference-data.manage`); every command is OWNER and TENANT_ADMIN, fresh assurance 300 s, reason required, audited, closed bodies (`RequestPurposeGrant`, `CreateReportingCalendar`, … generated in `administration_contracts.py` / `reference_contracts.py`), response `AdministrationReceipt`. The design-only `create_report_templates` row (capability `report-templates.draft.create`) is gone: its path now carries the implemented `create_report_template`. `access-policy.json` has 337 policy rows and 226 capabilities; the 207 implemented operations use 117 non-purpose capabilities, all delegable; 53 policy rows require fresh assurance and 19 are purpose-required. The control-plane contract moves from 1.6.0 (35 operations) to 1.7.0 with seven operations, 42 in all: `list_platform_operators`, `nominate_platform_operator`, `operator_nomination_accept|decline|cancel`, `create_provider_account` and `reissue_provider_account` (identity-authorised: operator, nominee, or tenant owner for an invited address; fresh assurance on every command; the account receipt's `temporary_password` is set only in the live response). Build 0.25.0 (integration of v0.25 parts A and B, the October 2026 operations hardening and the QA passes). The domain contract moved from 1.14.0 (186 operations) to 1.15.0 with 11 added operations, 197 in all — the rows after `indicator_dashboard_series` in the domain table: the audit export (v0.25 part A: `create_audit_export`, `POST /v1/tenants/{tenant_id}/audit-exports`, capability `audit.export` for OWNER and TENANT_ADMIN, purpose-required (SECURITY_REVIEW, INCIDENT_INVESTIGATION, REGULATORY_REQUEST, INTERNAL_AUDIT), fresh assurance 300 s, body `AuditExportRequest`, response `AuditExport` with JSON Lines content, manifest, seal and signed `next_cursor`) and the privacy routes (v0.25 part B: `list_privacy_cases`, `create_privacy_cases`, `get_privacy_cases`, `patch_privacy_cases`, `get_privacy_case_plan`, `action_privacy_cases_approve`, `action_privacy_cases_execute`, `read_privacy_case_export`, all purpose-bound to `DATA_SUBJECT_REQUEST` — `data.purpose` on commands, `?purpose=` on reads — with capabilities `privacy-cases.read`, `privacy-cases.draft.create`, `privacy-cases.draft.edit`, `privacy.approve`, `privacy.execute` and `privacy.export`; and `list_retention_schedule` and `list_retention_proofs`, capability `retention.read` for PRIVACY and TENANT_ADMIN). `/me/access` lists purpose-bound grants separately as `purpose_capabilities`. Every added operation carries `x-contract-version` 1.15.0. `access-policy.json` has 328 policy rows and 226 capabilities; the 197 implemented operations use 116 non-purpose capabilities, all delegable in custom roles; 44 operations require fresh assurance and 19 are purpose-required. The control-plane contract moves from 1.5.0 (34 operations) to 1.6.0 with one operator-only read, 35 in all: `platform_metrics` (`GET /v1/platform/metrics`: request counts by route family and status class with a latency histogram, worker freshness, DEAD and held deliveries, unsent deliveries and unfinished jobs, tenants by state, object-store space and the last operations status; others 404, anonymous 401; no path, tenant data or identity). Build 0.24.0 (integration of v0.21–v0.24 and the October 2026 quality work): the domain contract moved from 1.13.0 (160 operations) to 1.14.0 with 26 added operations, 186 in all — the rows after `action_submissions_submit` in the domain table: import batches (v0.21: `list_imports`, `get_imports`, `create_imports`, `patch_imports`, `action_imports_preview`, `action_imports_commit` — which also needs `observation.submit` at TENANT scope, declared as `additional_capabilities` — and `action_imports_cancel`); uploads and evidence (v0.22: `create_upload`, `get_uploads`, `put_upload_content` — the only route whose body is not JSON, `application/octet-stream` up to 25,000,000 bytes and never more than the declared size — `complete_upload`, `create_evidence`, `patch_evidence`, `action_evidence_attach`, `read_evidence_content` (mediated, audited download) and the citation reads `list_observation_evidence` and `list_calculated_result_evidence`); report exports (v0.23: `action_reports_export`, `action_reports_cancel_export`, `list_report_exports`, `download_report_export` and the recipient downloads `download_controlled_publication_pdf|xlsx|docx`); dashboards (v0.24: `programme_dashboard`, query `period_id` required, and `indicator_dashboard_series`, both `dashboards.read`, signed cursors, `limit` 1–100). Every added operation carries `x-contract-version` 1.14.0. `access-policy.json` has 323 policy rows and 223 capabilities (`imports.draft.create` and `imports.draft.edit` among the additions); the 186 implemented operations use 115 non-purpose capabilities, all delegable in custom roles (100 before); 42 operations require fresh assurance and 16 are purpose-required, as before. The control-plane contract moves from 1.4.0 (31 operations) to 1.5.0 with three operator-only operations, 34 in all: `list_delivery_attention` (`GET /v1/platform/deliveries`: DEAD or suspension-held dispatchable rows, at most 50, no address, reference, token or payload) and `delivery_requeue` / `delivery_release` (`POST /v1/platform/tenants/{tenant_id}/deliveries/{event_id}/actions/requeue|release`, fresh assurance, reason required, `expected_revision` the lease generation, Active tenants only). Domain and control-plane operations are distinct. Authentication (`/auth/*`) and health (`/health/*`) routes are outside the versioned contracts, as before; they are listed in ../IMPLEMENTATION.md ("Supplementary implemented routes"). The worker's `delivery.requested` outbox events are internal delivery intents and are not part of `event.schema.json`; report-export jobs are rows in `impact.job`, not events. A route or method absent from the contract answers `RESOURCE_UNAVAILABLE` 404. No broad-design operation is implied by this inventory. Earlier builds: 0.20.0 added ten operations (forms and submissions; 1.13.0, 160), 0.18.0 twelve (frameworks, completeness, targets, targets versus actuals), 0.16.0 three control-plane operations (channel request and confirm, `list_workers`).

Error reason codes added by the QA 2026-10 degradation slice merged onto build 0.25.0 (no contract version change; `reason_code` is a free string of at most 64 characters in the error envelope, so no schema changed): dependency failures answer `503 SERVICE_UNAVAILABLE`, `retryable: true`, with `reason_code` `DATABASE_UNAVAILABLE` (connection refused, lost or shut down; `/health/ready` answers the same), `IDENTITY_PROVIDER_UNAVAILABLE` (key set unreachable after the 60-second cache, or the token endpoint unreachable or answering 5xx at `/auth/callback`), `OBJECT_STORE_FULL` (ENOSPC/EDQUOT on upload) or `OBJECT_STORE_UNAVAILABLE` (any other store `OSError` on upload or download); `OBJECT_MISSING` (503, missing object on download) is unchanged. Known mismatch at the time: the contract's error `code` enum and the 503 response descriptions named `DEPENDENCY_UNAVAILABLE`, while the implementation answers `SERVICE_UNAVAILABLE`, as it has since v0.1; build 0.27.0 documents `SERVICE_UNAVAILABLE` in the contract (above) without changing the wire.

## Domain API

| Method | Path | Operation |
| --- | --- | --- |
| GET | `/v1/tenants/{tenant_id}/memberships` | list_memberships |
| GET | `/v1/tenants/{tenant_id}/memberships/{object_id}` | get_memberships |
| GET | `/v1/tenants/{tenant_id}/grants` | list_grants |
| GET | `/v1/tenants/{tenant_id}/grants/{object_id}` | get_grants |
| GET | `/v1/tenants/{tenant_id}/organisation-units` | list_organisation_units |
| POST | `/v1/tenants/{tenant_id}/organisation-units` | create_organisation_unit |
| GET | `/v1/tenants/{tenant_id}/programmes` | list_programmes |
| POST | `/v1/tenants/{tenant_id}/programmes` | create_programmes |
| GET | `/v1/tenants/{tenant_id}/programmes/{object_id}` | get_programmes |
| PATCH | `/v1/tenants/{tenant_id}/programmes/{object_id}` | patch_programmes |
| GET | `/v1/tenants/{tenant_id}/frameworks` | list_frameworks |
| POST | `/v1/tenants/{tenant_id}/frameworks` | create_frameworks |
| GET | `/v1/tenants/{tenant_id}/frameworks/{object_id}` | get_frameworks |
| PATCH | `/v1/tenants/{tenant_id}/frameworks/{object_id}` | patch_frameworks |
| GET | `/v1/tenants/{tenant_id}/indicator-definitions` | list_indicator_definitions |
| POST | `/v1/tenants/{tenant_id}/indicator-definitions` | create_indicator_definitions |
| GET | `/v1/tenants/{tenant_id}/indicator-definitions/{object_id}` | get_indicator_definitions |
| PATCH | `/v1/tenants/{tenant_id}/indicator-definitions/{object_id}` | patch_indicator_definitions |
| GET | `/v1/tenants/{tenant_id}/indicator-instances` | list_indicator_instances |
| POST | `/v1/tenants/{tenant_id}/indicator-instances` | create_indicator_instances |
| GET | `/v1/tenants/{tenant_id}/indicator-instances/{object_id}` | get_indicator_instances |
| PATCH | `/v1/tenants/{tenant_id}/indicator-instances/{object_id}` | patch_indicator_instances |
| GET | `/v1/tenants/{tenant_id}/targets` | list_targets |
| POST | `/v1/tenants/{tenant_id}/targets` | create_targets |
| GET | `/v1/tenants/{tenant_id}/targets/{object_id}` | get_targets |
| PATCH | `/v1/tenants/{tenant_id}/targets/{object_id}` | patch_targets |
| GET | `/v1/tenants/{tenant_id}/periods` | list_periods |
| GET | `/v1/tenants/{tenant_id}/periods/{object_id}` | get_periods |
| GET | `/v1/tenants/{tenant_id}/observations` | list_observations |
| POST | `/v1/tenants/{tenant_id}/observations` | create_observations |
| GET | `/v1/tenants/{tenant_id}/observations/{object_id}` | get_observations |
| PATCH | `/v1/tenants/{tenant_id}/observations/{object_id}` | patch_observations |
| GET | `/v1/tenants/{tenant_id}/calculated-results` | list_calculated_results |
| GET | `/v1/tenants/{tenant_id}/calculated-results/{object_id}` | get_calculated_results |
| GET | `/v1/tenants/{tenant_id}/forms` | list_forms |
| POST | `/v1/tenants/{tenant_id}/forms` | create_forms |
| GET | `/v1/tenants/{tenant_id}/forms/{object_id}` | get_forms |
| PATCH | `/v1/tenants/{tenant_id}/forms/{object_id}` | patch_forms |
| GET | `/v1/tenants/{tenant_id}/assignments` | list_assignments |
| POST | `/v1/tenants/{tenant_id}/assignments` | create_assignments |
| GET | `/v1/tenants/{tenant_id}/assignments/{object_id}` | get_assignments |
| PATCH | `/v1/tenants/{tenant_id}/assignments/{object_id}` | patch_assignments |
| GET | `/v1/tenants/{tenant_id}/submissions` | list_submissions |
| POST | `/v1/tenants/{tenant_id}/submissions` | create_submissions |
| GET | `/v1/tenants/{tenant_id}/submissions/{object_id}` | get_submissions |
| PATCH | `/v1/tenants/{tenant_id}/submissions/{object_id}` | patch_submissions |
| GET | `/v1/tenants/{tenant_id}/imports` | list_imports |
| POST | `/v1/tenants/{tenant_id}/imports` | create_imports |
| GET | `/v1/tenants/{tenant_id}/imports/{object_id}` | get_imports |
| PATCH | `/v1/tenants/{tenant_id}/imports/{object_id}` | patch_imports |
| GET | `/v1/tenants/{tenant_id}/evidence` | list_evidence |
| POST | `/v1/tenants/{tenant_id}/evidence` | create_evidence |
| GET | `/v1/tenants/{tenant_id}/evidence/{object_id}` | get_evidence |
| PATCH | `/v1/tenants/{tenant_id}/evidence/{object_id}` | patch_evidence |
| GET | `/v1/tenants/{tenant_id}/workflows` | list_workflows |
| GET | `/v1/tenants/{tenant_id}/workflows/{object_id}` | get_workflows |
| GET | `/v1/tenants/{tenant_id}/decisions` | list_decisions |
| GET | `/v1/tenants/{tenant_id}/decisions/{object_id}` | get_decisions |
| GET | `/v1/tenants/{tenant_id}/snapshots` | list_snapshots |
| GET | `/v1/tenants/{tenant_id}/snapshots/{object_id}` | get_snapshots |
| GET | `/v1/tenants/{tenant_id}/reports` | list_reports |
| POST | `/v1/tenants/{tenant_id}/reports` | create_reports |
| GET | `/v1/tenants/{tenant_id}/reports/{object_id}` | get_reports |
| PATCH | `/v1/tenants/{tenant_id}/reports/{object_id}` | patch_reports |
| GET | `/v1/tenants/{tenant_id}/disclosures` | list_disclosures |
| GET | `/v1/tenants/{tenant_id}/disclosures/{object_id}` | get_disclosures |
| GET | `/v1/tenants/{tenant_id}/connections` | list_connections |
| GET | `/v1/tenants/{tenant_id}/connections/{object_id}` | get_connections |
| GET | `/v1/tenants/{tenant_id}/privacy-cases` | list_privacy_cases |
| POST | `/v1/tenants/{tenant_id}/privacy-cases` | create_privacy_cases |
| GET | `/v1/tenants/{tenant_id}/privacy-cases/{object_id}` | get_privacy_cases |
| PATCH | `/v1/tenants/{tenant_id}/privacy-cases/{object_id}` | patch_privacy_cases |
| GET | `/v1/tenants/{tenant_id}/audit-events` | list_audit_events |
| GET | `/v1/tenants/{tenant_id}/audit-events/{object_id}` | get_audit_events |
| GET | `/v1/tenants/{tenant_id}/retention-policies` | list_retention_policies |
| POST | `/v1/tenants/{tenant_id}/retention-policies` | create_retention_policies |
| GET | `/v1/tenants/{tenant_id}/retention-policies/{object_id}` | get_retention_policies |
| PATCH | `/v1/tenants/{tenant_id}/retention-policies/{object_id}` | patch_retention_policies |
| GET | `/v1/tenants/{tenant_id}/work-items` | list_work_items |
| GET | `/v1/tenants/{tenant_id}/work-items/{object_id}` | get_work_items |
| GET | `/v1/tenants/{tenant_id}/report-templates` | list_report_templates |
| POST | `/v1/tenants/{tenant_id}/report-templates` | create_report_template |
| GET | `/v1/tenants/{tenant_id}/report-templates/{object_id}` | get_report_templates |
| GET | `/v1/tenants/{tenant_id}/notifications` | list_notifications |
| GET | `/v1/tenants/{tenant_id}/notifications/{object_id}` | get_notifications |
| POST | `/v1/tenants/{tenant_id}/programmes/{object_id}/actions/activate` | action_programmes_activate |
| POST | `/v1/tenants/{tenant_id}/frameworks/{object_id}/actions/submit` | action_frameworks_submit |
| POST | `/v1/tenants/{tenant_id}/indicator-definitions/{object_id}/actions/submit` | action_indicator_definitions_submit |
| POST | `/v1/tenants/{tenant_id}/targets/{object_id}/actions/submit` | action_targets_submit |
| POST | `/v1/tenants/{tenant_id}/forms/{object_id}/actions/publish` | action_forms_publish |
| POST | `/v1/tenants/{tenant_id}/assignments/{object_id}/actions/reassign` | action_assignments_reassign |
| POST | `/v1/tenants/{tenant_id}/submissions/{object_id}/actions/submit` | action_submissions_submit |
| POST | `/v1/tenants/{tenant_id}/imports/{object_id}/actions/preview` | action_imports_preview |
| POST | `/v1/tenants/{tenant_id}/imports/{object_id}/actions/commit` | action_imports_commit |
| POST | `/v1/tenants/{tenant_id}/imports/{object_id}/actions/cancel` | action_imports_cancel |
| POST | `/v1/tenants/{tenant_id}/workflows/{object_id}/actions/approve` | action_workflows_approve |
| POST | `/v1/tenants/{tenant_id}/workflows/{object_id}/actions/return` | action_workflows_return |
| POST | `/v1/tenants/{tenant_id}/workflows/{object_id}/actions/reject` | action_workflows_reject |
| POST | `/v1/tenants/{tenant_id}/periods/{object_id}/actions/close` | action_periods_close |
| POST | `/v1/tenants/{tenant_id}/periods/{object_id}/actions/restate` | action_periods_restate |
| POST | `/v1/tenants/{tenant_id}/reports/{object_id}/actions/submit` | action_reports_submit |
| POST | `/v1/tenants/{tenant_id}/reports/{object_id}/actions/publish` | action_reports_publish |
| POST | `/v1/tenants/{tenant_id}/reports/{object_id}/actions/withdraw` | action_reports_withdraw |
| POST | `/v1/tenants/{tenant_id}/privacy-cases/{object_id}/actions/approve` | action_privacy_cases_approve |
| POST | `/v1/tenants/{tenant_id}/privacy-cases/{object_id}/actions/execute` | action_privacy_cases_execute |
| POST | `/v1/tenants/{tenant_id}/memberships/{object_id}/actions/suspend` | action_memberships_suspend |
| POST | `/v1/tenants/{tenant_id}/memberships/{object_id}/actions/revoke` | action_memberships_revoke |
| POST | `/v1/tenants/{tenant_id}/grants/{object_id}/actions/revoke` | action_grants_revoke |
| POST | `/v1/tenants/{tenant_id}/member-invitations` | invite_member |
| GET | `/v1/tenants/{tenant_id}/member-invitations` | list_member_invitations |
| POST | `/v1/tenants/{tenant_id}/invitation-acceptances` | accept_invitation |
| POST | `/v1/tenants/{tenant_id}/disclosure-requests` | request_disclosure |
| GET | `/v1/tenants/{tenant_id}/uploads/{object_id}` | get_uploads |
| POST | `/v1/tenants/{tenant_id}/uploads` | create_upload |
| PUT | `/v1/tenants/{tenant_id}/uploads/{object_id}/content` | put_upload_content |
| POST | `/v1/tenants/{tenant_id}/uploads/{object_id}/actions/complete` | complete_upload |
| GET | `/v1/tenants/{tenant_id}/evidence/{object_id}/content` | read_evidence_content |
| POST | `/v1/tenants/{tenant_id}/observations/{object_id}/actions/submit` | action_observations_submit |
| POST | `/v1/tenants/{tenant_id}/indicator-instances/{object_id}/actions/calculate` | action_indicator_instances_calculate |
| GET | `/v1/tenants/{tenant_id}/workflow-templates` | list_workflow_templates |
| POST | `/v1/tenants/{tenant_id}/workflow-templates` | create_workflow_template |
| GET | `/v1/tenants/{tenant_id}/workflow-templates/{object_id}` | get_workflow_templates |
| GET | `/v1/tenants/{tenant_id}/lineage-manifests` | list_lineage_manifests |
| GET | `/v1/tenants/{tenant_id}/lineage-manifests/{object_id}` | get_lineage_manifests |
| POST | `/v1/tenants/{tenant_id}/member-invitations/{object_id}/actions/resend` | resend_invitation |
| POST | `/v1/tenants/{tenant_id}/member-invitations/{object_id}/actions/revoke` | revoke_invitation |
| POST | `/v1/tenants/{tenant_id}/memberships/{object_id}/actions/reactivate` | reactivate_membership |
| POST | `/v1/tenants/{tenant_id}/access-scopes` | create_access_scope |
| GET | `/v1/tenants/{tenant_id}/access-scopes` | list_access_scopes |
| POST | `/v1/tenants/{tenant_id}/access-requests` | request_access_change |
| GET | `/v1/tenants/{tenant_id}/access-requests` | list_access_requests |
| POST | `/v1/tenants/{tenant_id}/access-requests/{object_id}/actions/approve` | approve_access_change |
| POST | `/v1/tenants/{tenant_id}/access-requests/{object_id}/actions/reject` | reject_access_change |
| POST | `/v1/tenants/{tenant_id}/purpose-grants` | request_purpose_grant |
| GET | `/v1/tenants/{tenant_id}/purpose-grants` | list_purpose_grants |
| POST | `/v1/tenants/{tenant_id}/purpose-grants/{object_id}/actions/approve` | approve_purpose_grant |
| POST | `/v1/tenants/{tenant_id}/purpose-grants/{object_id}/actions/reject` | reject_purpose_grant |
| POST | `/v1/tenants/{tenant_id}/role-templates` | create_role_template |
| GET | `/v1/tenants/{tenant_id}/role-templates` | list_role_templates |
| POST | `/v1/tenants/{tenant_id}/role-templates/{object_id}/actions/revise` | revise_role_template |
| POST | `/v1/tenants/{tenant_id}/role-templates/{object_id}/actions/retire` | retire_role_template |
| POST | `/v1/tenants/{tenant_id}/access-groups` | create_access_group |
| GET | `/v1/tenants/{tenant_id}/access-groups` | list_access_groups |
| POST | `/v1/tenants/{tenant_id}/access-groups/{object_id}/actions/remove-member` | remove_group_member |
| POST | `/v1/tenants/{tenant_id}/access-groups/{object_id}/actions/retire` | retire_access_group |
| POST | `/v1/tenants/{tenant_id}/group-change-requests` | request_group_change |
| GET | `/v1/tenants/{tenant_id}/group-change-requests` | list_group_change_requests |
| POST | `/v1/tenants/{tenant_id}/organisation-units/{object_id}/actions/reparent` | reparent_organisation_unit |
| POST | `/v1/tenants/{tenant_id}/organisation-units/{object_id}/actions/rename` | rename_organisation_unit |
| POST | `/v1/tenants/{tenant_id}/renewal-requests` | request_membership_renewal |
| GET | `/v1/tenants/{tenant_id}/renewal-requests` | list_renewal_requests |
| POST | `/v1/tenants/{tenant_id}/ownership-transfers` | nominate_owner |
| GET | `/v1/tenants/{tenant_id}/ownership-transfers` | list_ownership_transfers |
| POST | `/v1/tenants/{tenant_id}/ownership-transfers/{object_id}/actions/accept` | accept_ownership |
| POST | `/v1/tenants/{tenant_id}/ownership-transfers/{object_id}/actions/cancel` | cancel_ownership |
| POST | `/v1/tenants/{tenant_id}/group-change-requests/{object_id}/actions/approve` | approve_group_change_requests |
| POST | `/v1/tenants/{tenant_id}/group-change-requests/{object_id}/actions/reject` | reject_group_change_requests |
| POST | `/v1/tenants/{tenant_id}/renewal-requests/{object_id}/actions/approve` | approve_renewal_requests |
| POST | `/v1/tenants/{tenant_id}/renewal-requests/{object_id}/actions/reject` | reject_renewal_requests |
| GET | `/v1/tenants/{tenant_id}/membership-directory` | list_membership_directory |
| GET | `/v1/tenants/{tenant_id}/collection-plans` | list_collection_plans |
| POST | `/v1/tenants/{tenant_id}/collection-plans` | create_collection_plans |
| GET | `/v1/tenants/{tenant_id}/collection-plans/{object_id}` | get_collection_plans |
| PATCH | `/v1/tenants/{tenant_id}/collection-plans/{object_id}` | patch_collection_plans |
| GET | `/v1/tenants/{tenant_id}/reporting-calendars` | list_reporting_calendars |
| POST | `/v1/tenants/{tenant_id}/reporting-calendars` | create_reporting_calendar |
| GET | `/v1/tenants/{tenant_id}/reporting-calendars/{object_id}` | get_reporting_calendars |
| GET | `/v1/tenants/{tenant_id}/geographies` | list_geographies |
| POST | `/v1/tenants/{tenant_id}/geographies` | create_geography |
| GET | `/v1/tenants/{tenant_id}/geographies/{object_id}` | get_geographies |
| POST | `/v1/tenants/{tenant_id}/collection-plans/{object_id}/actions/submit` | action_collection_plans_submit |
| POST | `/v1/tenants/{tenant_id}/indicator-instances/{object_id}/actions/activate` | action_indicator_instances_activate |
| POST | `/v1/tenants/{tenant_id}/programmes/{object_id}/actions/ready` | action_programmes_ready |
| POST | `/v1/tenants/{tenant_id}/programmes/{object_id}/actions/revise` | action_programmes_revise |
| GET | `/v1/tenants/{tenant_id}/programmes/{object_id}/readiness` | programme_readiness |
| GET | `/v1/tenants/{tenant_id}/workflows/{object_id}/candidate` | workflow_candidate |
| GET | `/v1/tenants/{tenant_id}/measurement-members` | measurement_members |
| GET | `/v1/tenants/{tenant_id}/measurement-changes` | list_measurement_changes |
| POST | `/v1/tenants/{tenant_id}/measurement-changes` | create_measurement_changes |
| GET | `/v1/tenants/{tenant_id}/measurement-changes/{object_id}` | get_measurement_changes |
| PATCH | `/v1/tenants/{tenant_id}/measurement-changes/{object_id}` | patch_measurement_changes |
| POST | `/v1/tenants/{tenant_id}/measurement-changes/{object_id}/actions/submit` | action_measurement_changes_submit |
| GET | `/v1/tenants/{tenant_id}/period-closes` | list_period_closes |
| GET | `/v1/tenants/{tenant_id}/period-closes/{object_id}` | get_period_closes |
| GET | `/v1/tenants/{tenant_id}/restatement-requests` | list_restatement_requests |
| GET | `/v1/tenants/{tenant_id}/restatement-requests/{object_id}` | get_restatement_requests |
| GET | `/v1/tenants/{tenant_id}/reports/{object_id}/export` | export_report_package |
| POST | `/v1/tenants/{tenant_id}/notifications/{object_id}/actions/acknowledge` | action_notifications_acknowledge |
| POST | `/v1/tenants/{tenant_id}/work-items/{object_id}/actions/recalculate` | action_work_items_recalculate |
| GET | `/v1/tenants/{tenant_id}/reports/{object_id}/export.csv` | export_report_package_csv |
| GET | `/v1/tenants/{tenant_id}/publications/{object_id}/view` | view_controlled_publication |
| GET | `/v1/tenants/{tenant_id}/publications/{object_id}/download.csv` | download_controlled_publication_csv |
| GET | `/v1/tenants/{tenant_id}/publication-recipients` | list_publication_recipients |
| GET | `/v1/tenants/{tenant_id}/frameworks/{object_id}/logframe.csv` | export_framework_csv |
| GET | `/v1/tenants/{tenant_id}/frameworks/{object_id}/logframe.xlsx` | export_framework_xlsx |
| GET | `/v1/tenants/{tenant_id}/frameworks/{object_id}/completeness` | framework_completeness |
| GET | `/v1/tenants/{tenant_id}/programmes/{object_id}/targets-vs-actuals` | programme_targets_vs_actuals |
| POST | `/v1/tenants/{tenant_id}/submissions/{object_id}/actions/correct` | action_submissions_correct |
| GET | `/v1/tenants/{tenant_id}/collection-rounds` | list_collection_rounds |
| POST | `/v1/tenants/{tenant_id}/collection-rounds` | create_collection_rounds |
| GET | `/v1/tenants/{tenant_id}/collection-rounds/{object_id}` | get_collection_rounds |
| PATCH | `/v1/tenants/{tenant_id}/collection-rounds/{object_id}` | patch_collection_rounds |
| POST | `/v1/tenants/{tenant_id}/forms/{object_id}/actions/submit` | action_forms_submit |
| GET | `/v1/tenants/{tenant_id}/forms/{object_id}/published` | get_form_published |
| GET | `/v1/tenants/{tenant_id}/forms/{object_id}/completeness` | get_form_completeness |
| GET | `/v1/tenants/{tenant_id}/collection-rounds/{object_id}/coverage` | get_round_coverage |
| POST | `/v1/tenants/{tenant_id}/evidence/{object_id}/actions/attach` | action_evidence_attach |
| GET | `/v1/tenants/{tenant_id}/observations/{object_id}/evidence` | list_observation_evidence |
| GET | `/v1/tenants/{tenant_id}/calculated-results/{object_id}/evidence` | list_calculated_result_evidence |
| POST | `/v1/tenants/{tenant_id}/reports/{object_id}/actions/export` | action_reports_export |
| POST | `/v1/tenants/{tenant_id}/reports/{object_id}/actions/cancel-export` | action_reports_cancel_export |
| GET | `/v1/tenants/{tenant_id}/reports/{object_id}/exports` | list_report_exports |
| GET | `/v1/tenants/{tenant_id}/reports/{object_id}/exports/{job_id}/download` | download_report_export |
| GET | `/v1/tenants/{tenant_id}/publications/{object_id}/download.pdf` | download_controlled_publication_pdf |
| GET | `/v1/tenants/{tenant_id}/publications/{object_id}/download.xlsx` | download_controlled_publication_xlsx |
| GET | `/v1/tenants/{tenant_id}/publications/{object_id}/download.docx` | download_controlled_publication_docx |
| GET | `/v1/tenants/{tenant_id}/programmes/{object_id}/dashboard` | programme_dashboard |
| GET | `/v1/tenants/{tenant_id}/indicator-instances/{object_id}/dashboard-series` | indicator_dashboard_series |
| GET | `/v1/tenants/{tenant_id}/indicator-instances/{object_id}/dashboard-sources` | indicator_dashboard_sources |
| GET | `/v1/tenants/{tenant_id}/indicator-definitions/{object_id}/portfolio` | indicator_definition_portfolio |
| POST | `/v1/tenants/{tenant_id}/audit-exports` | create_audit_export |
| GET | `/v1/tenants/{tenant_id}/privacy-cases/{object_id}/plan` | get_privacy_case_plan |
| GET | `/v1/tenants/{tenant_id}/privacy-cases/{object_id}/export` | read_privacy_case_export |
| GET | `/v1/tenants/{tenant_id}/retention-schedule` | list_retention_schedule |
| GET | `/v1/tenants/{tenant_id}/retention-proofs` | list_retention_proofs |
| POST | `/v1/tenants/{tenant_id}/retention-policies/{object_id}/actions/approve` | action_retention_policies_approve |
| GET | `/v1/tenants/{tenant_id}/retention-holds` | list_retention_holds |
| POST | `/v1/tenants/{tenant_id}/retention-holds` | create_retention_holds |
| POST | `/v1/tenants/{tenant_id}/retention-holds/{object_id}/actions/release` | action_retention_holds_release |
| GET | `/v1/tenants/{tenant_id}/access-denials` | list_access_denials |
| GET | `/v1/tenants/{tenant_id}/ai-enablement/catalog` | get_ai_enablement_catalog |
| POST | `/v1/tenants/{tenant_id}/ai-enablement/assessment` | assess_ai_enablement |
| GET | `/v1/tenants/{tenant_id}/ai-enablement/solutions` | get_ai_solutions |
| POST | `/v1/tenants/{tenant_id}/ai-enablement/advisory` | create_ai_advisory |
| POST | `/v1/tenants/{tenant_id}/ai-enablement/cost-comparison` | compare_ai_procurement_costs |
| POST | `/v1/tenants/{tenant_id}/ai-enablement/pilot-evaluation` | evaluate_ai_pilot |
| GET | `/v1/tenants/{tenant_id}/ai-enablement/task-templates` | get_ai_task_templates |
| GET | `/v1/tenants/{tenant_id}/ai-enablement/plans` | list_ai_adoption_plans |
| POST | `/v1/tenants/{tenant_id}/ai-enablement/plans` | create_ai_adoption_plan |
| GET | `/v1/tenants/{tenant_id}/ai-enablement/plans/{object_id}` | get_ai_adoption_plan |
| PUT | `/v1/tenants/{tenant_id}/ai-enablement/plans/{object_id}` | update_ai_adoption_plan |
| GET | `/v1/tenants/{tenant_id}/ai-enablement/plans/{object_id}/revisions/{revision_id}/guidance` | get_ai_adoption_guidance |
| GET | `/v1/tenants/{tenant_id}/ai-enablement/plans/{object_id}/revisions` | list_ai_adoption_revisions |
| POST | `/v1/tenants/{tenant_id}/reporting-calendars/{object_id}/actions/extend` | extend_reporting_calendar |
| POST | `/v1/tenants/{tenant_id}/reference-defaults` | apply_reference_defaults |


## Privileged control plane

| Method | Path | Operation |
| --- | --- | --- |
| GET | `/v1/platform/tenants` | list_tenant_lifecycle |
| POST | `/v1/platform/tenants` | request_tenant |
| POST | `/v1/platform/tenants/{tenant_id}/actions/accept-owner` | tenant_accept_owner |
| POST | `/v1/platform/tenants/{tenant_id}/actions/activate` | tenant_activate |
| POST | `/v1/platform/tenants/{tenant_id}/actions/begin-closure` | tenant_begin_closure |
| POST | `/v1/platform/tenants/{tenant_id}/actions/reactivate` | tenant_reactivate |
| POST | `/v1/platform/tenants/{tenant_id}/actions/suspend` | tenant_suspend |
| GET | `/v1/platform/access-bootstraps` | list_initial_access |
| POST | `/v1/platform/tenants/{tenant_id}/access-bootstrap` | request_initial_access |
| POST | `/v1/platform/access-bootstraps/{request_id}/actions/accept` | initial_access_accept |
| POST | `/v1/platform/access-bootstraps/{request_id}/actions/approve` | initial_access_approve |
| POST | `/v1/platform/access-bootstraps/{request_id}/actions/cancel` | initial_access_cancel |
| POST | `/v1/platform/access-bootstraps/{request_id}/actions/reject` | initial_access_reject |
| GET | `/v1/platform/recovery-contacts` | list_recovery_contacts |
| POST | `/v1/platform/tenants/{tenant_id}/recovery-contacts` | nominate_recovery_contact |
| POST | `/v1/platform/recovery-contacts/{contact_id}/actions/approve` | recovery_contact_approve |
| POST | `/v1/platform/recovery-contacts/{contact_id}/actions/cancel` | recovery_contact_cancel |
| POST | `/v1/platform/recovery-contacts/{contact_id}/actions/channel-confirm` | recovery_contact_channel_confirm |
| POST | `/v1/platform/recovery-contacts/{contact_id}/actions/channel-request` | recovery_contact_channel_request |
| POST | `/v1/platform/recovery-contacts/{contact_id}/actions/decline` | recovery_contact_decline |
| POST | `/v1/platform/recovery-contacts/{contact_id}/actions/reject` | recovery_contact_reject |
| POST | `/v1/platform/recovery-contacts/{contact_id}/actions/revoke` | recovery_contact_revoke |
| POST | `/v1/platform/recovery-contacts/{contact_id}/actions/verify` | recovery_contact_verify |
| GET | `/v1/platform/authority-renewals` | list_authority_renewals |
| GET | `/v1/platform/tenants/{tenant_id}/authority` | get_delegated_authority |
| POST | `/v1/platform/tenants/{tenant_id}/authority-renewal` | request_authority_renewal |
| POST | `/v1/platform/authority-renewals/{request_id}/actions/accept` | authority_renewal_accept |
| POST | `/v1/platform/authority-renewals/{request_id}/actions/approve` | authority_renewal_approve |
| POST | `/v1/platform/authority-renewals/{request_id}/actions/cancel` | authority_renewal_cancel |
| POST | `/v1/platform/authority-renewals/{request_id}/actions/reject` | authority_renewal_reject |
| GET | `/v1/platform/access-upgrades` | list_access_upgrade_inbox |
| GET | `/v1/platform/tenants/{tenant_id}/access-upgrades` | list_access_upgrades |
| GET | `/v1/platform/tenants/{tenant_id}/access-upgrade-preview` | get_access_upgrade_preview |
| POST | `/v1/platform/tenants/{tenant_id}/access-upgrade` | request_access_upgrade |
| POST | `/v1/platform/tenants/{tenant_id}/access-upgrades/{request_id}/actions/accept` | access_upgrade_accept |
| POST | `/v1/platform/tenants/{tenant_id}/access-upgrades/{request_id}/actions/approve` | access_upgrade_approve |
| POST | `/v1/platform/tenants/{tenant_id}/access-upgrades/{request_id}/actions/cancel` | access_upgrade_cancel |
| POST | `/v1/platform/tenants/{tenant_id}/access-upgrades/{request_id}/actions/reject` | access_upgrade_reject |
| GET | `/v1/platform/workers` | list_workers |
| GET | `/v1/platform/deliveries` | list_delivery_attention |
| POST | `/v1/platform/tenants/{tenant_id}/deliveries/{event_id}/actions/release` | delivery_release |
| POST | `/v1/platform/tenants/{tenant_id}/deliveries/{event_id}/actions/requeue` | delivery_requeue |
| GET | `/v1/platform/metrics` | platform_metrics |
| GET | `/v1/platform/operators` | list_platform_operators |
| POST | `/v1/platform/operators/{identity_id}/actions/deactivate` | deactivate_platform_operator |
| POST | `/v1/platform/operators/{identity_id}/actions/renew` | renew_platform_operator |
| POST | `/v1/platform/operator-nominations` | nominate_platform_operator |
| POST | `/v1/platform/operator-nominations/{nomination_id}/actions/accept` | operator_nomination_accept |
| POST | `/v1/platform/operator-nominations/{nomination_id}/actions/cancel` | operator_nomination_cancel |
| POST | `/v1/platform/operator-nominations/{nomination_id}/actions/decline` | operator_nomination_decline |
| POST | `/v1/platform/accounts` | create_provider_account |
| POST | `/v1/platform/accounts/{account_id}/actions/reissue` | reissue_provider_account |
