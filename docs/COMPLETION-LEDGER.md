# Requirement completion ledger

PARTIAL means tested behavior exists for a bounded subset; PENDING does not imply that a scaffold or design contract is an implementation. No enterprise acceptance is inferred from passing subset tests.

Scope: 270 functional requirements and 37 non-functional qualification requirements. Status: {'PARTIAL': 81, 'PENDING': 226}. Enterprise completion: **false**.

| Requirement | Title | Status | Evidence |
|---|---|---|---|
| FR-TEN-001 | Tenant lifecycle | PARTIAL | [tenant_lifecycle.py](../apps/api/impact_api/tenant_lifecycle.py), [test_tenant_lifecycle.py](../qualification/test_tenant_lifecycle.py), [tenant-check.mjs](../tools/browser/tenant-check.mjs), [RELEASE-0.10.md](../docs/RELEASE-0.10.md), [access_bootstrap.py](../apps/api/impact_api/access_bootstrap.py), [test_access_bootstrap.py](../qualification/test_access_bootstrap.py), [bootstrap-check.mjs](../tools/browser/bootstrap-check.mjs), [RELEASE-0.11.md](../docs/RELEASE-0.11.md), [recovery_contacts.py](../apps/api/impact_api/recovery_contacts.py), [test_recovery_contacts.py](../qualification/test_recovery_contacts.py), [recovery-check.mjs](../tools/browser/recovery-check.mjs), [RELEASE-0.12.md](../docs/RELEASE-0.12.md), [authority_renewal.py](../apps/api/impact_api/authority_renewal.py), [test_authority_renewal.py](../qualification/test_authority_renewal.py), [renewal-check.mjs](../tools/browser/renewal-check.mjs), [RELEASE-0.13.md](../docs/RELEASE-0.13.md), [test_native_concurrency.py](../qualification/test_native_concurrency.py), [worker.py](../apps/api/impact_api/worker.py), [test_worker.py](../qualification/test_worker.py), [test_native_worker.py](../qualification/test_native_worker.py), [RELEASE-0.16.md](../docs/RELEASE-0.16.md) |
| FR-TEN-002 | Organisation structures | PARTIAL | [workspace_administration.py](../apps/api/impact_api/workspace_administration.py), [account.py](../apps/api/impact_api/account.py), [test_workspace_administration.py](../qualification/test_workspace_administration.py), [workspace-check.mjs](../tools/browser/workspace-check.mjs), [RELEASE-0.9.md](../docs/RELEASE-0.9.md), [authority_renewal.py](../apps/api/impact_api/authority_renewal.py), [test_authority_renewal.py](../qualification/test_authority_renewal.py), [renewal-check.mjs](../tools/browser/renewal-check.mjs), [RELEASE-0.13.md](../docs/RELEASE-0.13.md) |
| FR-TEN-003 | Multiple memberships | PARTIAL | [administration.py](../apps/api/impact_api/administration.py), [test_administration.py](../qualification/test_administration.py), [RELEASE-0.2.md](../docs/RELEASE-0.2.md) |
| FR-TEN-004 | Configuration and terminology | PENDING | Pending |
| FR-TEN-005 | Custom fields and templates | PENDING | Pending |
| FR-TEN-006 | Partner and consortium boundaries | PENDING | Pending |
| FR-TEN-007 | Policy inheritance and exceptions | PENDING | Pending |
| FR-TEN-008 | Configuration promotion | PENDING | Pending |
| FR-TEN-009 | Branding and external identity | PENDING | Pending |
| FR-TEN-010 | Ownership continuity | PARTIAL | [workspace_administration.py](../apps/api/impact_api/workspace_administration.py), [account.py](../apps/api/impact_api/account.py), [test_workspace_administration.py](../qualification/test_workspace_administration.py), [workspace-check.mjs](../tools/browser/workspace-check.mjs), [RELEASE-0.9.md](../docs/RELEASE-0.9.md), [authority_renewal.py](../apps/api/impact_api/authority_renewal.py), [test_authority_renewal.py](../qualification/test_authority_renewal.py), [renewal-check.mjs](../tools/browser/renewal-check.mjs), [RELEASE-0.13.md](../docs/RELEASE-0.13.md) |
| FR-IAM-001 | Invitations and onboarding | PARTIAL | [administration.py](../apps/api/impact_api/administration.py), [test_administration.py](../qualification/test_administration.py), [RELEASE-0.2.md](../docs/RELEASE-0.2.md), [delivery.py](../apps/api/impact_api/delivery.py), [worker.py](../apps/api/impact_api/worker.py), [test_worker.py](../qualification/test_worker.py), [RELEASE-0.16.md](../docs/RELEASE-0.16.md) |
| FR-IAM-002 | Enterprise federation | PARTIAL | [administration.py](../apps/api/impact_api/administration.py), [test_administration.py](../qualification/test_administration.py), [RELEASE-0.2.md](../docs/RELEASE-0.2.md), [auth.py](../apps/api/impact_api/auth.py), [idp.py](../scripts/idp.py), [qualification-realm.json](../tools/idp/qualification-realm.json), [test_live_idp.py](../qualification/test_live_idp.py), [idp-tests.xml](../docs/evidence/idp-tests.xml), [idp-native-tests.xml](../docs/evidence/idp-native-tests.xml), [idp-qualification.json](../docs/evidence/idp-qualification.json), [RELEASE-0.15.md](../docs/RELEASE-0.15.md) |
| FR-IAM-003 | Multifactor and passkeys | PARTIAL | [workspace_administration.py](../apps/api/impact_api/workspace_administration.py), [account.py](../apps/api/impact_api/account.py), [test_workspace_administration.py](../qualification/test_workspace_administration.py), [workspace-check.mjs](../tools/browser/workspace-check.mjs), [RELEASE-0.9.md](../docs/RELEASE-0.9.md), [authority_renewal.py](../apps/api/impact_api/authority_renewal.py), [test_authority_renewal.py](../qualification/test_authority_renewal.py), [renewal-check.mjs](../tools/browser/renewal-check.mjs), [RELEASE-0.13.md](../docs/RELEASE-0.13.md), [auth.py](../apps/api/impact_api/auth.py), [idp.py](../scripts/idp.py), [qualification-realm.json](../tools/idp/qualification-realm.json), [test_live_idp.py](../qualification/test_live_idp.py), [idp-tests.xml](../docs/evidence/idp-tests.xml), [idp-native-tests.xml](../docs/evidence/idp-native-tests.xml), [idp-qualification.json](../docs/evidence/idp-qualification.json), [RELEASE-0.15.md](../docs/RELEASE-0.15.md), [idp-check.mjs](../tools/browser/idp-check.mjs), [idp-browser-tests.json](../docs/evidence/idp-browser-tests.json) |
| FR-IAM-004 | Local account security | PENDING | Pending |
| FR-IAM-005 | Provisioning and deprovisioning | PENDING | Pending |
| FR-IAM-006 | Session control | PARTIAL | [workspace_administration.py](../apps/api/impact_api/workspace_administration.py), [account.py](../apps/api/impact_api/account.py), [test_workspace_administration.py](../qualification/test_workspace_administration.py), [workspace-check.mjs](../tools/browser/workspace-check.mjs), [RELEASE-0.9.md](../docs/RELEASE-0.9.md), [authority_renewal.py](../apps/api/impact_api/authority_renewal.py), [test_authority_renewal.py](../qualification/test_authority_renewal.py), [renewal-check.mjs](../tools/browser/renewal-check.mjs), [RELEASE-0.13.md](../docs/RELEASE-0.13.md), [auth.py](../apps/api/impact_api/auth.py), [idp.py](../scripts/idp.py), [qualification-realm.json](../tools/idp/qualification-realm.json), [test_live_idp.py](../qualification/test_live_idp.py), [idp-tests.xml](../docs/evidence/idp-tests.xml), [idp-native-tests.xml](../docs/evidence/idp-native-tests.xml), [idp-qualification.json](../docs/evidence/idp-qualification.json), [RELEASE-0.15.md](../docs/RELEASE-0.15.md), [test_backchannel_logout.py](../qualification/test_backchannel_logout.py), [idp-check.mjs](../tools/browser/idp-check.mjs), [idp-browser-tests.json](../docs/evidence/idp-browser-tests.json) |
| FR-IAM-007 | Recovery and identity changes | PENDING | Pending |
| FR-IAM-008 | Membership status and expiry | PARTIAL | [workspace_administration.py](../apps/api/impact_api/workspace_administration.py), [account.py](../apps/api/impact_api/account.py), [test_workspace_administration.py](../qualification/test_workspace_administration.py), [workspace-check.mjs](../tools/browser/workspace-check.mjs), [RELEASE-0.9.md](../docs/RELEASE-0.9.md), [authority_renewal.py](../apps/api/impact_api/authority_renewal.py), [test_authority_renewal.py](../qualification/test_authority_renewal.py), [renewal-check.mjs](../tools/browser/renewal-check.mjs), [RELEASE-0.13.md](../docs/RELEASE-0.13.md) |
| FR-IAM-009 | Delegated user administration | PARTIAL | [administration.py](../apps/api/impact_api/administration.py), [test_administration.py](../qualification/test_administration.py), [RELEASE-0.2.md](../docs/RELEASE-0.2.md), [authority_renewal.py](../apps/api/impact_api/authority_renewal.py), [test_authority_renewal.py](../qualification/test_authority_renewal.py), [renewal-check.mjs](../tools/browser/renewal-check.mjs), [RELEASE-0.13.md](../docs/RELEASE-0.13.md), [contracts.py](../apps/api/impact_api/contracts.py), [workspace_administration.py](../apps/api/impact_api/workspace_administration.py), [test_workspace_administration.py](../qualification/test_workspace_administration.py), [RELEASE-0.15.md](../docs/RELEASE-0.15.md) |
| FR-IAM-010 | Group management | PARTIAL | [workspace_administration.py](../apps/api/impact_api/workspace_administration.py), [account.py](../apps/api/impact_api/account.py), [test_workspace_administration.py](../qualification/test_workspace_administration.py), [workspace-check.mjs](../tools/browser/workspace-check.mjs), [RELEASE-0.9.md](../docs/RELEASE-0.9.md), [authority_renewal.py](../apps/api/impact_api/authority_renewal.py), [test_authority_renewal.py](../qualification/test_authority_renewal.py), [renewal-check.mjs](../tools/browser/renewal-check.mjs), [RELEASE-0.13.md](../docs/RELEASE-0.13.md) |
| FR-IAM-011 | Access certification | PENDING | Pending |
| FR-IAM-012 | Service identities | PENDING | Pending |
| FR-IAM-013 | User profile and preferences | PARTIAL | [workspace_administration.py](../apps/api/impact_api/workspace_administration.py), [account.py](../apps/api/impact_api/account.py), [test_workspace_administration.py](../qualification/test_workspace_administration.py), [workspace-check.mjs](../tools/browser/workspace-check.mjs), [RELEASE-0.9.md](../docs/RELEASE-0.9.md), [authority_renewal.py](../apps/api/impact_api/authority_renewal.py), [test_authority_renewal.py](../qualification/test_authority_renewal.py), [renewal-check.mjs](../tools/browser/renewal-check.mjs), [RELEASE-0.13.md](../docs/RELEASE-0.13.md) |
| FR-IAM-014 | Departure and work reassignment | PARTIAL | [administration.py](../apps/api/impact_api/administration.py), [test_administration.py](../qualification/test_administration.py), [RELEASE-0.2.md](../docs/RELEASE-0.2.md) |
| FR-ACC-001 | Deny by default | PARTIAL | [store.py](../apps/api/impact_api/store.py), [auth.py](../apps/api/impact_api/auth.py), [test_live_application.py](../qualification/test_live_application.py) |
| FR-ACC-002 | Fine grained scope | PARTIAL | [workspace_administration.py](../apps/api/impact_api/workspace_administration.py), [account.py](../apps/api/impact_api/account.py), [test_workspace_administration.py](../qualification/test_workspace_administration.py), [workspace-check.mjs](../tools/browser/workspace-check.mjs), [RELEASE-0.9.md](../docs/RELEASE-0.9.md), [authority_renewal.py](../apps/api/impact_api/authority_renewal.py), [test_authority_renewal.py](../qualification/test_authority_renewal.py), [renewal-check.mjs](../tools/browser/renewal-check.mjs), [RELEASE-0.13.md](../docs/RELEASE-0.13.md) |
| FR-ACC-003 | Effective permissions | PARTIAL | [administration.py](../apps/api/impact_api/administration.py), [test_administration.py](../qualification/test_administration.py), [RELEASE-0.2.md](../docs/RELEASE-0.2.md) |
| FR-ACC-004 | Separation of duties | PARTIAL | [store.py](../apps/api/impact_api/store.py), [auth.py](../apps/api/impact_api/auth.py), [test_live_application.py](../qualification/test_live_application.py) |
| FR-ACC-005 | Permission safe derivation | PARTIAL | [store.py](../apps/api/impact_api/store.py), [auth.py](../apps/api/impact_api/auth.py), [test_live_application.py](../qualification/test_live_application.py) |
| FR-ACC-006 | External access lifecycle | PARTIAL | [administration.py](../apps/api/impact_api/administration.py), [test_administration.py](../qualification/test_administration.py), [RELEASE-0.2.md](../docs/RELEASE-0.2.md) |
| FR-ACC-007 | Export and bulk access | PENDING | Pending |
| FR-ACC-008 | Privileged support access | PENDING | Pending |
| FR-ACC-009 | Privacy preserving aggregates | PENDING | Pending |
| FR-ACC-010 | Partner limited collaboration | PENDING | Pending |
| FR-ACC-011 | Access changes and existing artifacts | PARTIAL | [store.py](../apps/api/impact_api/store.py), [auth.py](../apps/api/impact_api/auth.py), [test_live_application.py](../qualification/test_live_application.py) |
| FR-ACC-012 | Administrative review and simulation | PARTIAL | [administration.py](../apps/api/impact_api/administration.py), [test_administration.py](../qualification/test_administration.py), [RELEASE-0.2.md](../docs/RELEASE-0.2.md) |
| FR-PLN-001 | Results hierarchy | PARTIAL | [planning.py](../apps/api/impact_api/planning.py), [planning_contracts.py](../apps/api/impact_api/planning_contracts.py), [test_planning.py](../qualification/test_planning.py), [test_planning_unit.py](../qualification/test_planning_unit.py), [Planning.tsx](../apps/web/src/Planning.tsx), [planning-check.mjs](../tools/browser/planning-check.mjs), [native-application-tests.xml](../docs/evidence/native-application-tests.xml), [planning-browser-tests.json](../docs/evidence/planning-browser-tests.json), [application-tests.xml](../docs/evidence/application-tests.xml), [RELEASE-0.18.md](../docs/RELEASE-0.18.md) |
| FR-PLN-002 | Theory of change relationships | PENDING | Pending |
| FR-PLN-003 | Framework baselines | PARTIAL | [planning.py](../apps/api/impact_api/planning.py), [planning_contracts.py](../apps/api/impact_api/planning_contracts.py), [test_planning.py](../qualification/test_planning.py), [test_planning_unit.py](../qualification/test_planning_unit.py), [period_governance.py](../apps/api/impact_api/period_governance.py), [native-application-tests.xml](../docs/evidence/native-application-tests.xml), [application-tests.xml](../docs/evidence/application-tests.xml), [RELEASE-0.18.md](../docs/RELEASE-0.18.md) |
| FR-PLN-004 | Reusable libraries | PENDING | Pending |
| FR-PLN-005 | Standard mappings | PENDING | Pending |
| FR-PLN-006 | Measurement plan | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-PLN-007 | Assumptions and context | PENDING | Pending |
| FR-PLN-008 | Planning scenarios | PENDING | Pending |
| FR-PLN-009 | Document assisted setup | PENDING | Pending |
| FR-PLN-010 | Framework completeness review | PARTIAL | [planning.py](../apps/api/impact_api/planning.py), [planning_contracts.py](../apps/api/impact_api/planning_contracts.py), [test_planning.py](../qualification/test_planning.py), [test_planning_unit.py](../qualification/test_planning_unit.py), [planning-check.mjs](../tools/browser/planning-check.mjs), [planning-browser-tests.json](../docs/evidence/planning-browser-tests.json), [application-tests.xml](../docs/evidence/application-tests.xml), [RELEASE-0.18.md](../docs/RELEASE-0.18.md) |
| FR-PRG-001 | Programme and project registry | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-PRG-002 | Activities and milestones | PENDING | Pending |
| FR-PRG-003 | Workplans and calendars | PENDING | Pending |
| FR-PRG-004 | Risks issues and dependencies | PENDING | Pending |
| FR-PRG-005 | Geography and sites | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-PRG-006 | Partner responsibilities | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-PRG-007 | Programme change control | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-PRG-008 | Closure and archival | PENDING | Pending |
| FR-PRG-009 | Cross project dependencies | PENDING | Pending |
| FR-PRG-010 | Bulk administration | PENDING | Pending |
| FR-IND-001 | Complete indicator definition | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-IND-002 | Supported measurement types | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-IND-003 | Baselines and targets | PARTIAL | [planning.py](../apps/api/impact_api/planning.py), [planning_contracts.py](../apps/api/impact_api/planning_contracts.py), [test_planning.py](../qualification/test_planning.py), [test_planning_unit.py](../qualification/test_planning_unit.py), [Planning.tsx](../apps/web/src/Planning.tsx), [planning-check.mjs](../tools/browser/planning-check.mjs), [planning-browser-tests.json](../docs/evidence/planning-browser-tests.json), [application-tests.xml](../docs/evidence/application-tests.xml), [RELEASE-0.18.md](../docs/RELEASE-0.18.md) |
| FR-IND-004 | Target amendments | PENDING | Pending |
| FR-IND-005 | Reporting periods | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-IND-006 | Disaggregation dimensions | PENDING | Pending |
| FR-IND-007 | Missing and exceptional values | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-IND-008 | Definition versioning | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-IND-009 | Indicator library reuse | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-IND-010 | Manual and calculated results | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-IND-011 | Evidence requirements | PENDING | Pending |
| FR-IND-012 | Responsibility and collection schedule | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-IND-013 | Status and thresholds | PENDING | Pending |
| FR-IND-014 | Retirement and replacement | PENDING | Pending |
| FR-IND-015 | Reference sheets and dictionary export | PENDING | Pending |
| FR-CAL-001 | Deterministic calculation | PARTIAL | [domain.py](../apps/api/impact_api/domain.py), [service.py](../apps/api/impact_api/service.py), [test_measurement.py](../qualification/test_measurement.py) |
| FR-CAL-002 | Type and unit compatibility | PARTIAL | [domain.py](../apps/api/impact_api/domain.py), [service.py](../apps/api/impact_api/service.py), [test_measurement.py](../qualification/test_measurement.py) |
| FR-CAL-003 | Ratios rates and percentages | PARTIAL | [domain.py](../apps/api/impact_api/domain.py), [service.py](../apps/api/impact_api/service.py), [test_measurement.py](../qualification/test_measurement.py) |
| FR-CAL-004 | Population overlap | PENDING | Pending |
| FR-CAL-005 | Time aggregation semantics | PARTIAL | [domain.py](../apps/api/impact_api/domain.py), [service.py](../apps/api/impact_api/service.py), [test_measurement.py](../qualification/test_measurement.py) |
| FR-CAL-006 | Hierarchical aggregation | PENDING | Pending |
| FR-CAL-007 | Dimension alignment | PENDING | Pending |
| FR-CAL-008 | Missingness and coverage | PARTIAL | [domain.py](../apps/api/impact_api/domain.py), [service.py](../apps/api/impact_api/service.py), [test_measurement.py](../qualification/test_measurement.py) |
| FR-CAL-009 | Precision and rounding | PARTIAL | [domain.py](../apps/api/impact_api/domain.py), [service.py](../apps/api/impact_api/service.py), [test_measurement.py](../qualification/test_measurement.py) |
| FR-CAL-010 | Zero denominators and invalid inputs | PARTIAL | [domain.py](../apps/api/impact_api/domain.py), [service.py](../apps/api/impact_api/service.py), [test_measurement.py](../qualification/test_measurement.py) |
| FR-CAL-011 | Corrections and recalculation | PARTIAL | [work.py](../apps/api/impact_api/work.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-CAL-012 | Formula authoring and validation | PENDING | Pending |
| FR-CAL-013 | Weighted and composite indicators | PENDING | Pending |
| FR-CAL-014 | Cross portfolio attribution | PENDING | Pending |
| FR-CAL-015 | Reconciliation and explainability | PARTIAL | [domain.py](../apps/api/impact_api/domain.py), [service.py](../apps/api/impact_api/service.py), [test_measurement.py](../qualification/test_measurement.py) |
| FR-CAL-016 | Statistical interpretation | PENDING | Pending |
| FR-FRM-001 | Form builder | PENDING | Pending |
| FR-FRM-002 | Conditional logic and validation | PENDING | Pending |
| FR-FRM-003 | Form lifecycle and compatibility | PENDING | Pending |
| FR-FRM-004 | Multilingual instruments | PENDING | Pending |
| FR-FRM-005 | Collection rounds and assignments | PENDING | Pending |
| FR-FRM-006 | Save resume and correction | PENDING | Pending |
| FR-FRM-007 | Media and location evidence | PENDING | Pending |
| FR-FRM-008 | Respondent and public forms | PENDING | Pending |
| FR-FRM-009 | Longitudinal and repeat visits | PENDING | Pending |
| FR-FRM-010 | Instrument testing and reuse | PENDING | Pending |
| FR-OFF-001 | Offline task packages | PENDING | Pending |
| FR-OFF-002 | Durable local capture | PENDING | Pending |
| FR-OFF-003 | Idempotent synchronisation | PENDING | Pending |
| FR-OFF-004 | Conflict handling | PENDING | Pending |
| FR-OFF-005 | Device protection and expiry | PENDING | Pending |
| FR-OFF-006 | Shared device operation | PENDING | Pending |
| FR-OFF-007 | Sync and quality supervisor view | PENDING | Pending |
| FR-OFF-008 | Constrained connectivity | PENDING | Pending |
| FR-DAT-001 | File ingestion | PENDING | Pending |
| FR-DAT-002 | Mapping and preview | PENDING | Pending |
| FR-DAT-003 | Import mode and identity | PENDING | Pending |
| FR-DAT-004 | Validation and quarantine | PENDING | Pending |
| FR-DAT-005 | Immutable raw source | PENDING | Pending |
| FR-DAT-006 | Governed transformations | PENDING | Pending |
| FR-DAT-007 | Schema drift | PENDING | Pending |
| FR-DAT-008 | Data catalogue and lineage | PARTIAL | [domain.py](../apps/api/impact_api/domain.py), [service.py](../apps/api/impact_api/service.py), [test_measurement.py](../qualification/test_measurement.py) |
| FR-DAT-009 | Data editing and amendments | PARTIAL | [work.py](../apps/api/impact_api/work.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-DAT-010 | Refresh scheduling and freshness | PENDING | Pending |
| FR-DAT-011 | Data exports and portability | PENDING | Pending |
| FR-DAT-012 | Data retention and dependency review | PENDING | Pending |
| FR-DQ-001 | Quality rule catalogue | PENDING | Pending |
| FR-DQ-002 | Blocking and warning behaviour | PENDING | Pending |
| FR-DQ-003 | Duplicate detection | PENDING | Pending |
| FR-DQ-004 | Reconciliation checks | PENDING | Pending |
| FR-DQ-005 | Quality issue workflow | PENDING | Pending |
| FR-DQ-006 | Completeness and timeliness | PARTIAL | [measurement.py](../apps/api/impact_api/measurement.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-DQ-007 | Anomaly assistance | PENDING | Pending |
| FR-DQ-008 | Quality disclosure | PENDING | Pending |
| FR-PAR-001 | Optional registries | PENDING | Pending |
| FR-PAR-002 | Purpose limited identity | PENDING | Pending |
| FR-PAR-003 | Notice consent and lawful handling | PENDING | Pending |
| FR-PAR-004 | Service and participation events | PENDING | Pending |
| FR-PAR-005 | Household and group membership | PENDING | Pending |
| FR-PAR-006 | Cohorts and follow up | PENDING | Pending |
| FR-PAR-007 | Safeguarding and vulnerable people | PENDING | Pending |
| FR-PAR-008 | Participant requests and corrections | PENDING | Pending |
| FR-EVD-001 | Evidence repository | PENDING | Pending |
| FR-EVD-002 | Evidence verification and provenance | PENDING | Pending |
| FR-EVD-003 | Search and knowledge retrieval | PENDING | Pending |
| FR-EVD-004 | Document versioning and annotations | PENDING | Pending |
| FR-EVD-005 | Qualitative coding | PENDING | Pending |
| FR-EVD-006 | Transcription and translation | PENDING | Pending |
| FR-EVD-007 | Quotations and disclosure | PENDING | Pending |
| FR-EVD-008 | Findings and triangulation | PENDING | Pending |
| FR-EVA-001 | Evaluation registry | PENDING | Pending |
| FR-EVA-002 | Sampling and methodological metadata | PENDING | Pending |
| FR-EVA-003 | Analysis packages | PENDING | Pending |
| FR-EVA-004 | Causal claims and uncertainty | PENDING | Pending |
| FR-EVA-005 | Outcome harvesting and contribution | PENDING | Pending |
| FR-EVA-006 | Learning agenda | PENDING | Pending |
| FR-EVA-007 | Management responses and actions | PENDING | Pending |
| FR-EVA-008 | Institutional learning library | PENDING | Pending |
| FR-WFL-001 | Configurable approvals | PARTIAL | [work.py](../apps/api/impact_api/work.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-WFL-002 | Reviewer independence and authority | PARTIAL | [work.py](../apps/api/impact_api/work.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-WFL-003 | Return reject and resubmit | PARTIAL | [work.py](../apps/api/impact_api/work.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-WFL-004 | Delegation escalation and absence | PARTIAL | [work.py](../apps/api/impact_api/work.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-WFL-005 | Comments mentions and discussions | PENDING | Pending |
| FR-WFL-006 | Task and notification centre | PARTIAL | [work.py](../apps/api/impact_api/work.py), [WorkCenter.tsx](../apps/web/src/WorkCenter.tsx), [RELEASE-0.7.md](../docs/RELEASE-0.7.md), [worker.py](../apps/api/impact_api/worker.py), [test_worker.py](../qualification/test_worker.py), [RELEASE-0.16.md](../docs/RELEASE-0.16.md) |
| FR-WFL-007 | Period close and lock | PARTIAL | [period_governance.py](../apps/api/impact_api/period_governance.py), [test_period_governance.py](../qualification/test_period_governance.py), [RELEASE-0.5.md](../docs/RELEASE-0.5.md) |
| FR-WFL-008 | Reopen and restate | PARTIAL | [period_governance.py](../apps/api/impact_api/period_governance.py), [test_period_governance.py](../qualification/test_period_governance.py), [RELEASE-0.5.md](../docs/RELEASE-0.5.md) |
| FR-WFL-009 | Automation rules | PENDING | Pending |
| FR-WFL-010 | Decisions and signoff | PARTIAL | [work.py](../apps/api/impact_api/work.py), [test_work_center.py](../qualification/test_work_center.py), [RELEASE-0.7.md](../docs/RELEASE-0.7.md) |
| FR-ANA-001 | Dashboard authoring | PENDING | Pending |
| FR-ANA-002 | Filters and drill down | PENDING | Pending |
| FR-ANA-003 | Actual target and baseline views | PARTIAL | [planning.py](../apps/api/impact_api/planning.py), [planning_contracts.py](../apps/api/impact_api/planning_contracts.py), [test_planning.py](../qualification/test_planning.py), [test_planning_unit.py](../qualification/test_planning_unit.py), [Planning.tsx](../apps/web/src/Planning.tsx), [planning-check.mjs](../tools/browser/planning-check.mjs), [planning-browser-tests.json](../docs/evidence/planning-browser-tests.json), [application-tests.xml](../docs/evidence/application-tests.xml), [RELEASE-0.18.md](../docs/RELEASE-0.18.md) |
| FR-ANA-004 | Freshness and approval context | PARTIAL | [domain.py](../apps/api/impact_api/domain.py), [service.py](../apps/api/impact_api/service.py), [test_measurement.py](../qualification/test_measurement.py) |
| FR-ANA-005 | Table analysis and pivots | PENDING | Pending |
| FR-ANA-006 | Geographic analysis | PENDING | Pending |
| FR-ANA-007 | Portfolio comparison | PENDING | Pending |
| FR-ANA-008 | Dashboard governance | PENDING | Pending |
| FR-ANA-009 | Alerts and thresholds | PENDING | Pending |
| FR-ANA-010 | External analytics access | PENDING | Pending |
| FR-RPT-001 | Report template library | PENDING | Pending |
| FR-RPT-002 | Reporting obligations | PENDING | Pending |
| FR-RPT-003 | Frozen reporting packages | PARTIAL | [reporting.py](../apps/api/impact_api/reporting.py), [test_reporting.py](../qualification/test_reporting.py), [test_publication.py](../qualification/test_publication.py), [RELEASE-0.6.md](../docs/RELEASE-0.6.md), [RELEASE-0.8.md](../docs/RELEASE-0.8.md) |
| FR-RPT-004 | Narrative authoring and review | PARTIAL | [main.tsx](../apps/web/src/main.tsx), [reporting-check.mjs](../tools/browser/reporting-check.mjs), [IMPLEMENTATION.md](../docs/IMPLEMENTATION.md) |
| FR-RPT-005 | Accessible export formats | PARTIAL | [reporting.py](../apps/api/impact_api/reporting.py), [test_reporting.py](../qualification/test_reporting.py), [test_publication.py](../qualification/test_publication.py), [RELEASE-0.6.md](../docs/RELEASE-0.6.md), [RELEASE-0.8.md](../docs/RELEASE-0.8.md) |
| FR-RPT-006 | Presentation and donor format output | PENDING | Pending |
| FR-RPT-007 | Publication control | PARTIAL | [reporting.py](../apps/api/impact_api/reporting.py), [test_reporting.py](../qualification/test_reporting.py), [test_publication.py](../qualification/test_publication.py), [RELEASE-0.6.md](../docs/RELEASE-0.6.md), [RELEASE-0.8.md](../docs/RELEASE-0.8.md) |
| FR-RPT-008 | Distribution and scheduled delivery | PENDING | Pending |
| FR-RPT-009 | Amend withdraw and supersede | PARTIAL | [reporting.py](../apps/api/impact_api/reporting.py), [test_reporting.py](../qualification/test_reporting.py), [test_publication.py](../qualification/test_publication.py), [RELEASE-0.6.md](../docs/RELEASE-0.6.md), [RELEASE-0.8.md](../docs/RELEASE-0.8.md) |
| FR-RPT-010 | Reporting reconciliation | PARTIAL | [reporting.py](../apps/api/impact_api/reporting.py), [test_reporting.py](../qualification/test_reporting.py), [test_publication.py](../qualification/test_publication.py), [RELEASE-0.6.md](../docs/RELEASE-0.6.md), [RELEASE-0.8.md](../docs/RELEASE-0.8.md) |
| FR-RPT-011 | Transparency publication | PENDING | Pending |
| FR-RPT-012 | Report evidence package | PENDING | Pending |
| FR-FIN-001 | Funding and grant context | PENDING | Pending |
| FR-FIN-002 | Budget planning | PENDING | Pending |
| FR-FIN-003 | Expenditure ingestion | PENDING | Pending |
| FR-FIN-004 | Currency treatment | PENDING | Pending |
| FR-FIN-005 | Variance and forecast | PENDING | Pending |
| FR-FIN-006 | Shared costs and allocations | PENDING | Pending |
| FR-FIN-007 | Cost effectiveness | PENDING | Pending |
| FR-FIN-008 | Finance permissions and audit | PENDING | Pending |
| FR-INT-001 | Connector qualification | PENDING | Pending |
| FR-INT-002 | Connection lifecycle | PENDING | Pending |
| FR-INT-003 | Reliable job execution | PENDING | Pending |
| FR-INT-004 | API completeness and consistency | PARTIAL | [store.py](../apps/api/impact_api/store.py), [auth.py](../apps/api/impact_api/auth.py), [test_live_application.py](../qualification/test_live_application.py) |
| FR-INT-005 | API version and compatibility | PARTIAL | [store.py](../apps/api/impact_api/store.py), [auth.py](../apps/api/impact_api/auth.py), [test_live_application.py](../qualification/test_live_application.py) |
| FR-INT-006 | Webhook delivery | PENDING | Pending |
| FR-INT-007 | Limits and tenant fairness | PENDING | Pending |
| FR-INT-008 | Import export standards | PENDING | Pending |
| FR-INT-009 | Integration diagnostics | PENDING | Pending |
| FR-INT-010 | Development and testing access | PENDING | Pending |
| FR-AI-001 | Explicit enablement and policy | PENDING | Pending |
| FR-AI-002 | Proposal and logframe extraction | PENDING | Pending |
| FR-AI-003 | Indicator design assistance | PENDING | Pending |
| FR-AI-004 | Import and cleaning assistance | PENDING | Pending |
| FR-AI-005 | Evidence based questions | PENDING | Pending |
| FR-AI-006 | Governed numerical analysis | PENDING | Pending |
| FR-AI-007 | Report drafting | PENDING | Pending |
| FR-AI-008 | Qualitative assistance | PENDING | Pending |
| FR-AI-009 | Proactive findings | PENDING | Pending |
| FR-AI-010 | Action proposal and approval | PENDING | Pending |
| FR-AI-011 | Input and tool isolation | PENDING | Pending |
| FR-AI-012 | Model data handling | PENDING | Pending |
| FR-AI-013 | Source access and conversation history | PENDING | Pending |
| FR-AI-014 | Traceability and reproducibility | PENDING | Pending |
| FR-AI-015 | Evaluation and release gates | PENDING | Pending |
| FR-AI-016 | Cost latency and fallback | PENDING | Pending |
| FR-AI-017 | Forecasts and scenario assistance | PENDING | Pending |
| FR-AI-018 | Safety feedback and shutdown | PENDING | Pending |
| FR-SEC-001 | Security threat assessment | PENDING | Pending |
| FR-SEC-002 | Encryption and key governance | PENDING | Pending |
| FR-SEC-003 | Tenant isolation verification | PARTIAL | [store.py](../apps/api/impact_api/store.py), [auth.py](../apps/api/impact_api/auth.py), [test_live_application.py](../qualification/test_live_application.py), [provision_logins.py](../scripts/provision_logins.py), [test_native_roles.py](../qualification/test_native_roles.py), [restore_drill.py](../scripts/restore_drill.py), [native-application-tests.xml](../docs/evidence/native-application-tests.xml), [native-qualification.json](../docs/evidence/native-qualification.json), [RELEASE-0.14.md](../docs/RELEASE-0.14.md) |
| FR-SEC-004 | Application and API protection | PARTIAL | [store.py](../apps/api/impact_api/store.py), [auth.py](../apps/api/impact_api/auth.py), [test_live_application.py](../qualification/test_live_application.py) |
| FR-SEC-005 | File and content safety | PENDING | Pending |
| FR-SEC-006 | Secrets management | PENDING | Pending |
| FR-SEC-007 | Tamper evident audit | PARTIAL | [store.py](../apps/api/impact_api/store.py), [auth.py](../apps/api/impact_api/auth.py), [test_live_application.py](../qualification/test_live_application.py) |
| FR-SEC-008 | Secure engineering lifecycle | PENDING | Pending |
| FR-SEC-009 | Vulnerability management | PENDING | Pending |
| FR-SEC-010 | Independent assurance | PENDING | Pending |
| FR-SEC-011 | Detection and incident response | PENDING | Pending |
| FR-SEC-012 | Environment separation | PARTIAL | [store.py](../apps/api/impact_api/store.py), [auth.py](../apps/api/impact_api/auth.py), [test_live_application.py](../qualification/test_live_application.py) |
| FR-SEC-013 | Privileged operations | PENDING | Pending |
| FR-SEC-014 | Resilience to abusive traffic | PENDING | Pending |
| FR-SEC-015 | Enterprise assurance options | PENDING | Pending |
| FR-PRV-001 | Data inventory and classification | PENDING | Pending |
| FR-PRV-002 | Minimisation and purpose controls | PENDING | Pending |
| FR-PRV-003 | Hosting and transfer policy | PENDING | Pending |
| FR-PRV-004 | Retention schedules | PENDING | Pending |
| FR-PRV-005 | Deletion restriction and holds | PENDING | Pending |
| FR-PRV-006 | Backup deletion handling | PENDING | Pending |
| FR-PRV-007 | Data subject request handling | PENDING | Pending |
| FR-PRV-008 | Sharing register and agreements | PENDING | Pending |
| FR-PRV-009 | Privacy review and country policy | PENDING | Pending |
| FR-PRV-010 | Telemetry and analytics privacy | PENDING | Pending |
| FR-OPS-001 | Service administration console | PENDING | Pending |
| FR-OPS-002 | Entitlements and limits | PENDING | Pending |
| FR-OPS-003 | Subscription administration | PENDING | Pending |
| FR-OPS-004 | Support case management | PENDING | Pending |
| FR-OPS-005 | Monitoring and service visibility | PARTIAL | [main.tsx](../apps/web/src/main.tsx), [reporting-check.mjs](../tools/browser/reporting-check.mjs), [IMPLEMENTATION.md](../docs/IMPLEMENTATION.md), [main.py](../apps/api/impact_api/main.py), [store.py](../apps/api/impact_api/store.py), [test_native_roles.py](../qualification/test_native_roles.py), [test_native_restart.py](../qualification/test_native_restart.py), [native-qualification.json](../docs/evidence/native-qualification.json), [RELEASE-0.14.md](../docs/RELEASE-0.14.md) |
| FR-OPS-006 | Backup and recovery operations | PENDING | Pending |
| FR-OPS-007 | Safe release and rollback | PENDING | Pending |
| FR-OPS-008 | Capacity and cost management | PENDING | Pending |
| FR-OPS-009 | Operational automation | PENDING | Pending |
| FR-OPS-010 | Trust and assurance information | PENDING | Pending |
| FR-MIG-001 | Source discovery and mapping | PENDING | Pending |
| FR-MIG-002 | Trial migrations | PENDING | Pending |
| FR-MIG-003 | Semantic reconciliation | PENDING | Pending |
| FR-MIG-004 | Historical provenance | PENDING | Pending |
| FR-MIG-005 | Cutover and rollback | PENDING | Pending |
| FR-MIG-006 | User enablement | PENDING | Pending |
| FR-MIG-007 | Full tenant export | PENDING | Pending |
| FR-MIG-008 | Closure and deletion evidence | PENDING | Pending |
| FR-UX-001 | Role relevant workspaces | PARTIAL | [main.tsx](../apps/web/src/main.tsx), [reporting-check.mjs](../tools/browser/reporting-check.mjs), [IMPLEMENTATION.md](../docs/IMPLEMENTATION.md) |
| FR-UX-002 | Progressive configuration | PARTIAL | [main.tsx](../apps/web/src/main.tsx), [reporting-check.mjs](../tools/browser/reporting-check.mjs), [IMPLEMENTATION.md](../docs/IMPLEMENTATION.md) |
| FR-UX-003 | Error recovery and work preservation | PARTIAL | [main.tsx](../apps/web/src/main.tsx), [reporting-check.mjs](../tools/browser/reporting-check.mjs), [IMPLEMENTATION.md](../docs/IMPLEMENTATION.md) |
| FR-UX-004 | Accessible interaction | PARTIAL | [main.tsx](../apps/web/src/main.tsx), [reporting-check.mjs](../tools/browser/reporting-check.mjs), [IMPLEMENTATION.md](../docs/IMPLEMENTATION.md) |
| FR-UX-005 | Responsive operation | PARTIAL | [main.tsx](../apps/web/src/main.tsx), [reporting-check.mjs](../tools/browser/reporting-check.mjs), [IMPLEMENTATION.md](../docs/IMPLEMENTATION.md) |
| FR-UX-006 | Language and locale | PENDING | Pending |
| FR-UX-007 | Expanded localisation | PENDING | Pending |
| FR-UX-008 | Discoverability and help | PENDING | Pending |
| FR-UX-009 | Status and trust cues | PARTIAL | [main.tsx](../apps/web/src/main.tsx), [reporting-check.mjs](../tools/browser/reporting-check.mjs), [IMPLEMENTATION.md](../docs/IMPLEMENTATION.md) |
| FR-UX-010 | Usability evidence | PENDING | Pending |
| VF-PER-001 | Interactive response | PENDING | Pending |
| VF-PER-002 | Dashboard response | PENDING | Pending |
| VF-PER-003 | Search response | PENDING | Pending |
| VF-PER-004 | Import and recalculation throughput | PENDING | Pending |
| VF-PER-005 | Export and report generation | PENDING | Pending |
| VF-PER-006 | Data freshness | PENDING | Pending |
| VF-PER-007 | AI responsiveness | PENDING | Pending |
| VF-CAP-001 | Supported object limits | PENDING | Pending |
| VF-CAP-002 | Scaling and workload isolation | PENDING | Pending |
| VF-AVL-001 | Core availability | PENDING | Pending |
| VF-AVL-002 | Dependency degradation | PENDING | Pending |
| VF-DR-001 | Disaster recovery | PENDING | Pending |
| VF-DR-002 | Ordinary failure durability | PENDING | Pending |
| VF-DR-003 | Recovery testing and backups | PARTIAL | [restore_drill.py](../scripts/restore_drill.py), [native-restore-drill.json](../docs/evidence/native-restore-drill.json), [native-qualification.json](../docs/evidence/native-qualification.json), [RELEASE-0.14.md](../docs/RELEASE-0.14.md), [OPERATIONS-GUIDE.md](../docs/current/OPERATIONS-GUIDE.md) |
| VF-DIN-001 | Calculation correctness | PENDING | Pending |
| VF-DIN-002 | Concurrent change integrity | PARTIAL | [test_native_concurrency.py](../qualification/test_native_concurrency.py), [service.py](../apps/api/impact_api/service.py), [store.py](../apps/api/impact_api/store.py), [native-application-tests.xml](../docs/evidence/native-application-tests.xml), [native-qualification.json](../docs/evidence/native-qualification.json), [RELEASE-0.14.md](../docs/RELEASE-0.14.md) |
| VF-IAM-001 | Revocation time | PENDING | Pending |
| VF-OFF-001 | Offline authority window | PENDING | Pending |
| VF-SEC-001 | Release security threshold | PENDING | Pending |
| VF-SEC-002 | Incident and remediation timing | PENDING | Pending |
| VF-AUD-001 | Audit coverage and retention | PENDING | Pending |
| VF-PRV-001 | Deletion propagation | PENDING | Pending |
| VF-PRV-002 | Retention defaults and proof | PENDING | Pending |
| VF-AIQ-001 | Evaluation set quality | PENDING | Pending |
| VF-AIQ-002 | Evidence and numeric accuracy | PENDING | Pending |
| VF-AIQ-003 | Extraction and abstention | PENDING | Pending |
| VF-AIQ-004 | Leakage and action safety | PENDING | Pending |
| VF-AIQ-005 | Change monitoring and rollback | PENDING | Pending |
| VF-UX-001 | Accessibility conformance | PENDING | Pending |
| VF-UX-002 | Usability qualification | PENDING | Pending |
| VF-CMP-001 | Browser and device support | PENDING | Pending |
| VF-L10-001 | Localisation integrity | PENDING | Pending |
| VF-MNT-001 | Maintainable contracts | PENDING | Pending |
| VF-OBS-001 | Operational diagnosability | PENDING | Pending |
| VF-PRT-001 | Portability and exit quality | PENDING | Pending |
| VF-ECO-001 | Cost transparency and sustainability | PENDING | Pending |
| VF-SUP-001 | Support and service readiness | PENDING | Pending |
