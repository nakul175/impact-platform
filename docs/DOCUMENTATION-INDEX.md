# Impact Platform documentation

**Status:** the current build, API versions, schema and the verified state of `main`, CI and staging are stated once, at the top of [HANDOVER.md](HANDOVER.md); `VERSION.json` is the source for the version numbers. Every build has a release note in this directory (`RELEASE-0.N*.md`; the latest is [RELEASE-0.36-procurement-preview.md](RELEASE-0.36-procurement-preview.md)).

Start with the [current documentation index](current/DOCUMENTATION-INDEX.md); a newcomer should read the [engineering guide](current/ENGINEERING-GUIDE.md) first. Edition 1.1 is reconciled to application 0.12.0; builds 0.13.0 to 0.18.0 are recorded in [RELEASE-0.13.md](RELEASE-0.13.md), [RELEASE-0.14.md](RELEASE-0.14.md) (native PostgreSQL qualification), [RELEASE-0.15.md](RELEASE-0.15.md) (live identity provider), [RELEASE-0.16.md](RELEASE-0.16.md) (worker runtime, outbox dispatcher and email adapter: 405 PGlite and 437 native application checks, 16 + 16 live-provider checks, 143 reference, 93 browser and 2 live-provider browser checks; schema 18; platform API 1.4.0; ledger 76 PARTIAL, 231 PENDING, 0 accepted), and [RELEASE-0.18.md](RELEASE-0.18.md) (results framework and planning, built ahead of v0.17: 441 PGlite and 474 native application checks, 16 + 16 live-provider checks, 143 reference, 100 browser and 2 live-provider browser checks; schema 19; domain API 1.11.0; ledger 81 PARTIAL, 226 PENDING, 0 accepted) and the sequenced plan in [DELIVERY-PLAN.md](DELIVERY-PLAN.md); builds 0.19.0 to 0.36.0 have their own `RELEASE-0.N*.md` notes, listed in the [current documentation index](current/DOCUMENTATION-INDEX.md). Original editable documents and archives are retained in [history/v1.0](history/v1.0/).

The target requirements, implemented subsets and pending acceptance gates are explicitly distinguished. See [change record](current/CHANGELOG.md) and [verification](current/DOCUMENTATION-QA.md).

<!-- BEGIN GENERATED INDEX (scripts/doc_index.py; do not edit by hand) -->

## Every document (generated)

### docs (top level)

- [Implemented domain operations](API-INVENTORY.md)
- [Claude handover — 6 October 2026](CLAUDE-HANDOFF-2026-10-06.md)
- [Requirement completion ledger](COMPLETION-LEDGER.md)
- [Delivery plan from build 0.13.0](DELIVERY-PLAN.md)
- [Handover — Impact Platform and nonprofit AI enablement](HANDOVER.md)
- [Implementation boundary](IMPLEMENTATION.md)
- [Current roadmap and next delivery](NEXT-DELIVERY.md)
- [Accessibility conformance, bounded subset — October 2026](QA-A11Y-2026-10.md)
- [QA browser coverage — October 2026](QA-BROWSER-2026-10.md)
- [QA 2026-10 — qualified degradation behaviour](QA-DEGRADATION-2026-10.md)
- [QA 2026-10 — non-functional qualification: pooler, database restart, lock order, load profiles](QA-NONFUNCTIONAL-2026-10.md)
- [QA 2026-10 — performance measurement harness](QA-PERFORMANCE-2026-10.md)
- [QA 2026-10 — UAT pack, support runbook and Release 1 acceptance gaps](QA-UAT-2026-10.md)
- [Qualification record](QUALIFICATION.md)
- [Quality and hardening — October 2026](QUALITY-2026-10.md)
- [v0.10 — Tenant onboarding and lifecycle increment](RELEASE-0.10.md)
- [v0.11 — Reviewed initial tenant access](RELEASE-0.11.md)
- [v0.12 — Verified tenant recovery contacts](RELEASE-0.12.md)
- [v0.13 — Reviewed renewal of delegated authority](RELEASE-0.13.md)
- [v0.14 — Native PostgreSQL qualification](RELEASE-0.14.md)
- [v0.15 — Live identity provider](RELEASE-0.15.md)
- [v0.16 — Worker runtime, outbox dispatcher and email adapter](RELEASE-0.16.md)
- [v0.17 — Deployment package and first staging](RELEASE-0.17.md)
- [v0.18 — Results framework and planning](RELEASE-0.18.md)
- [v0.19 — Indicator and calculation completion](RELEASE-0.19.md)
- [Release 0.2.0 — access administration](RELEASE-0.2.md)
- [v0.20 — Web forms](RELEASE-0.20.md)
- [v0.21 — Import and data quality](RELEASE-0.21.md)
- [v0.22 — Object store and evidence attachments](RELEASE-0.22.md)
- [v0.23 — Report exports (PDF, XLSX, DOCX)](RELEASE-0.23.md)
- [v0.24 — Dashboards](RELEASE-0.24.md)
- [v0.25 part A — Key governance, secrets rotation and audit export](RELEASE-0.25a.md)
- [v0.25b — Privacy execution: data-subject requests and retention proof](RELEASE-0.25b.md)
- [v0.26a — Usable staging](RELEASE-0.26a.md)
- [v0.27 — Email readiness: qualified SMTP path, provider-ready configuration, owner decision pack](RELEASE-0.27-email.md)
- [v0.27 — Web forms, continued: language versions, collection rounds and assignments, correction of returned work](RELEASE-0.27-forms.md)
- [v0.27 (slice S1) — Plannable imports: acceptance gap A5](RELEASE-0.27-imports.md)
- [v0.27 — Operator lifecycle (slice S3 of the parallel build of 2 October 2026)](RELEASE-0.27-operators.md)
- [v0.27 (planning slice S7) — Theory of change, assumptions, target amendments and status thresholds](RELEASE-0.27-planning.md)
- [v0.27 — Charts in reports, dashboard drill-down and portfolio view](RELEASE-0.27-reports-dashboards.md)
- [v0.27 — Security and privacy: denial auditing, audit retention and export register, tenant retention policies, retention holds](RELEASE-0.27-security-privacy.md)
- [v0.27 — User-visible status and alert delivery](RELEASE-0.27-status-alerts.md)
- [v0.27 — Console dialogs, human labels, access gate and refreshed guides (UX slice S2)](RELEASE-0.27-ux.md)
- [v0.27 — Build 0.27.0: eleven parallel slices integrated (PRs #67–#77)](RELEASE-0.27.md)
- [Sunday backup qualification correction](RELEASE-0.28-ci-sunday.md)
- [v0.28 — Application executor and asynchronous import commits](RELEASE-0.28-import-executor.md)
- [v0.28 — Collection round and assignment screens](RELEASE-0.28-rounds-screen.md)
- [v0.29 — approved logframe spreadsheet exports from TolaData reuse](RELEASE-0.29-logframe-reuse.md)
- [Release 0.3.0 — manual measurement configuration](RELEASE-0.3.md)
- [Nonprofit AI adoption plans](RELEASE-0.30-ai-adoption-plans.md)
- [Nonprofit AI adoption tool](RELEASE-0.30-ai-adoption-tool.md)
- [Proposed 0.30 nonprofit AI catalogue and assessment](RELEASE-0.30-ai-catalog.md)
- [Nonprofit AI adoption tool — functional workspace](RELEASE-0.30-ai-product-ui.md)
- [Build 0.30 — nonprofit AI solution discovery](RELEASE-0.30-ai-solutions.md)
- [Proposed AI enablement workspace — build 0.30 slice](RELEASE-0.30-ai-workspace.md)
- [Nonprofit AI enablement foundation](RELEASE-0.30-nonprofit-ai-enablement.md)
- [0.30 Mercy Corps reporting regression scenarios](RELEASE-0.30-reuse-scenarios.md)
- [Nonprofit AI planning and practical capacity building](RELEASE-0.31-nonprofit-ai-planning.md)
- [Reviewed tenant access upgrades — development slice](RELEASE-0.32-access-upgrade.md)
- [Tola + AI sprint: access extension and saved guidance](RELEASE-0.32-tola-ai-sprint.md)
- [Internal member advice candidate for build 0.33](RELEASE-0.33-human-advice.md)
- [Build 0.33 slice — deliberate programme evidence for AI plans](RELEASE-0.33-impact-references.md)
- [Build 0.33 — programme evidence and internal AI advice](RELEASE-0.33-tola-ai-extension.md)
- [Build 0.34 saved AI plan copies](RELEASE-0.34-plan-portability.md)
- [Build 0.35 practical AI workspace](RELEASE-0.35-practical-ai-workspace.md)
- [Build 0.36 procurement preview and unsaved-brief protection](RELEASE-0.36-procurement-preview.md)
- [Release 0.4.0 — governed measurement changes](RELEASE-0.4.md)
- [Release 0.5.0 — programme-period close and restatement](RELEASE-0.5.md)
- [Release 0.6.0 — frozen internal reporting packages](RELEASE-0.6.md)
- [Release 0.7.0 — reviewed exclusions and recalculation work centre](RELEASE-0.7.md)
- [Release 0.8.0 — controlled report publication](RELEASE-0.8.md)
- [v0.9 — Release 1, tenant and identity administration increment](RELEASE-0.9.md)
- [Operations hardening (October 2026) — backups, restore drill, alerts, metrics, owner console](RELEASE-OPS-2026-10.md)
- [Tola + AI timed development handover](SPRINT-HANDOVER-2026-10-05.md)
- [Training video — how the platform works, end to end](TRAINING-VIDEO.md)

### agile

- [Persona to role map](agile/PERSONA-ROLE-MAP.md)
- [Imprana Commons working agreement](agile/WORKING-AGREEMENT.md)

### backlog

- [Imprana Commons backlog](backlog/README.md)

### current

- [Accessibility statement — Impact Platform web client](current/ACCESSIBILITY-STATEMENT.md)
- [Impact Platform administrator guide](current/ADMINISTRATOR-GUIDE.md)
- [Current Impact Platform architecture](current/ARCHITECTURE-CURRENT.md)
- [Documentation change record](current/CHANGELOG.md)
- [Current implemented API inventory](current/CURRENT-API-INVENTORY.md)
- [Current data dictionary and schema evolution](current/CURRENT-DATA-DICTIONARY.md)
- [Impact Platform data governance record](current/DATA-GOVERNANCE.md)
- [Deployment guide — staging server](current/DEPLOYMENT-GUIDE.md)
- [Impact Platform documentation index](current/DOCUMENTATION-INDEX.md)
- [Documentation verification record](current/DOCUMENTATION-QA.md)
- [Choosing an email provider — decision pack for the owner](current/EMAIL-PROVIDER-DECISION.md)
- [Impact Platform — working brief for engineering sessions](current/ENGINEERING-BRIEF.md)
- [Impact Platform engineering guide](current/ENGINEERING-GUIDE.md)
- [Impact Management API and Event Contracts](current/Impact-Management-API-and-Event-Contracts-v1.1.md)
- [Impact Management Access Control Specification](current/Impact-Management-Access-Control-Specification-v1.1.md)
- [Impact Management Architecture Decision Records](current/Impact-Management-Architecture-Decision-Records-v1.1.md)
- [Impact Management Database Migration Specification](current/Impact-Management-Database-Migration-Specification-v1.1.md)
- [Impact Management Development and CI Specification](current/Impact-Management-Development-and-CI-Specification-v1.1.md)
- [Impact Management Engineering Implementation Plan](current/Impact-Management-Engineering-Implementation-Plan-v1.1.md)
- [Impact Management Fixture and Acceptance Specification](current/Impact-Management-Fixture-and-Acceptance-Specification-v1.1.md)
- [Impact Management Platform](current/Impact-Management-HLD-v1.1.md)
- [Impact Management Platform](current/Impact-Management-LLD-v1.1.md)
- [Impact Management Operational Runbooks](current/Impact-Management-Operational-Runbooks-v1.1.md)
- [Impact Management Platform](current/Impact-Management-Platform-BRD-v1.1.md)
- [Impact Management Platform](current/Impact-Management-Platform-FSD-v1.1.md)
- [Impact Management Security Threat Model](current/Impact-Management-Security-Threat-Model-v1.1.md)
- [Impact Management Platform](current/Impact-Management-Test-Strategy-v1.1.md)
- [Impact Management UI Component and Interaction Specification](current/Impact-Management-UI-Component-and-Interaction-Specification-v1.1.md)
- [Key and encryption register](current/KEY-AND-ENCRYPTION-REGISTER.md)
- [Impact Platform operations guide](current/OPERATIONS-GUIDE.md)
- [Release 1 acceptance gaps](current/RELEASE-1-ACCEPTANCE-GAPS.md)
- [Impact Platform release acceptance record](current/RELEASE-ACCEPTANCE.md)
- [Support runbook — staging server](current/SUPPORT-RUNBOOK.md)
- [Release 1 user-acceptance test pack](current/UAT-PACK.md)
- [Impact Platform user guide](current/USER-GUIDE.md)

### development-tracker

- [Live Tola + AI development tracker](development-tracker/README.md)

### governance

- [AI features: evaluation and limits](governance/AI-EVALUATION-AND-LIMITS.md)
- [AI features: model card](governance/AI-MODEL-CARD.md)
- [Backup and disaster recovery](governance/BACKUP-DR.md)
- [Compliance control mapping](governance/COMPLIANCE-CONTROL-MAPPING.md)
- [Data-subject request procedure](governance/DATA-SUBJECT-REQUESTS.md)
- [Dependency inventory and SBOM](governance/DEPENDENCY-INVENTORY.md)
- [Design and decision process (design notes, RFCs, ADRs)](governance/DESIGN-AND-DECISION-PROCESS.md)
- [Data protection impact assessment (framework, pre-filled)](governance/DPIA.md)
- [Incident process](governance/INCIDENT-PROCESS.md)
- [Postmortem template (blameless)](governance/POSTMORTEM-TEMPLATE.md)
- [Governance documents: map of the 27 standard items](governance/README.md)
- [Record of processing activities (framework)](governance/RECORD-OF-PROCESSING.md)
- [Retention schedule](governance/RETENTION-SCHEDULE.md)
- [Secrets and key register (summary and index)](governance/SECRETS-REGISTER.md)
- [Secure development and supply-chain evidence](governance/SECURE-DEV-SUPPLY-CHAIN.md)
- [Service-level objectives and alert catalogue](governance/SLOS-AND-ALERTS.md)
- [Third-party licences](governance/THIRD-PARTY-LICENCES.md)

### handover

- [Backlog at handover (build 0.27.0, 3 October 2026)](handover/BACKLOG.md)
- [Mercy Corps TolaData reuse trial](handover/MERCYCORPS-REUSE.md)
- [Parallel work: several builders and one integrator](handover/PARALLEL-WORK.md)

### nonprofit-ai/v1.0

- [Nonprofit AI Enablement Platform Business Requirements](nonprofit-ai/v1.0/01-BRD.md)
- [Nonprofit AI Enablement Platform Functional Specification](nonprofit-ai/v1.0/02-FSD.md)
- [Nonprofit AI Enablement Platform High Level Design](nonprofit-ai/v1.0/03-HLD.md)
- [Nonprofit AI Enablement Platform Low Level Design](nonprofit-ai/v1.0/04-LLD.md)
- [Nonprofit AI Enablement Test Strategy](nonprofit-ai/v1.0/05-TEST-STRATEGY.md)
- [Nonprofit AI Enablement Test Scenarios and Cases](nonprofit-ai/v1.0/06-TEST-SCENARIOS-AND-CASES.md)
- [Nonprofit AI Enablement Wireframes and Journeys](nonprofit-ai/v1.0/07-WIREFRAMES-AND-JOURNEYS.md)
- [Nonprofit AI Enablement Data Dictionary](nonprofit-ai/v1.0/08-DATA-DICTIONARY.md)
- [Nonprofit AI Enablement Security and Privacy](nonprofit-ai/v1.0/09-SECURITY-AND-PRIVACY.md)
- [Nonprofit AI Enablement Operations and Release](nonprofit-ai/v1.0/10-OPERATIONS-AND-RELEASE.md)
- [Nonprofit AI Enablement Decisions and Risks](nonprofit-ai/v1.0/11-DECISIONS-AND-RISKS.md)
- [Nonprofit AI Enablement Delivery Backlog](nonprofit-ai/v1.0/12-DELIVERY-BACKLOG.md)
- [Nonprofit AI Enablement Architecture Decisions](nonprofit-ai/v1.0/13-ARCHITECTURE-DECISIONS.md)
- [Nonprofit AI Enablement Baseline and Glossary](nonprofit-ai/v1.0/14-BASELINE-AND-GLOSSARY.md)
- [Nonprofit AI Enablement Acceptance and Change Control](nonprofit-ai/v1.0/15-ACCEPTANCE-AND-CHANGE-CONTROL.md)
- [Development increment 0.31: nonprofit planning](nonprofit-ai/v1.0/DEVELOPMENT-0.31.md)
- [Development increment 0.32: access extension and saved guidance](nonprofit-ai/v1.0/DEVELOPMENT-0.32.md)
- [Development increment 0.33: governed evidence and internal advice](nonprofit-ai/v1.0/DEVELOPMENT-0.33.md)
- [Development increment 0.34 saved plan copies](nonprofit-ai/v1.0/DEVELOPMENT-0.34.md)
- [Development increment 0.35 practical AI workspace](nonprofit-ai/v1.0/DEVELOPMENT-0.35.md)
- [Build 0.36 development supplement](nonprofit-ai/v1.0/DEVELOPMENT-0.36.md)
- [Next bounded slice: internal saved-plan portability](nonprofit-ai/v1.0/PORTABILITY-IMPLEMENTATION-NOTE.md)
- [Nonprofit AI Enablement Documentation](nonprofit-ai/v1.0/README.md)

### nonprofit-ai/v1.0/drafts/0.34

- [Unregistered0.34 download draft: stop-point handoff](nonprofit-ai/v1.0/drafts/0.34/HANDOFF.md)
- [README-review](nonprofit-ai/v1.0/drafts/0.34/README-review.md)
- [UI-review](nonprofit-ai/v1.0/drafts/0.34/UI-review.md)
- [Prepared native qualification design — not executed](nonprofit-ai/v1.0/drafts/0.34/native-test-design.md)

### nonprofit-ai/v1.0/drafts/0.36

- [Preserved 0.36 proposals — controlled continuation](nonprofit-ai/v1.0/drafts/0.36/HANDOFF.md)
- [Review of the interrupted 0.36 producer drafts](nonprofit-ai/v1.0/drafts/0.36/PRODUCER-REVIEW-2026-10-06.md)

### nonprofit-ai/v1.0/drafts/0.36/deployment-verifier

- [Private 0.36 deployment verifier — prepared, not run](nonprofit-ai/v1.0/drafts/0.36/deployment-verifier/README.md)

### nonprofit-ai/v1.0/drafts/0.36/integration-package

- [Private 0.36 procurement preview integration package](nonprofit-ai/v1.0/drafts/0.36/integration-package/INTEGRATION-CHECKLIST.md)

### nonprofit-ai/v1.0/drafts/0.36/integration-package/review

- [Nonprofit AI Procurement Draft Preview — Proposed Development Supplement](nonprofit-ai/v1.0/drafts/0.36/integration-package/review/DEVELOPMENT-procurement-preview.proposed.md)

### nonprofit-ai/v1.0/drafts/0.36/model-and-design/docs/nonprofit-ai/v1.0

- [Nonprofit AI Procurement Draft Preview — Proposed Development Supplement](nonprofit-ai/v1.0/drafts/0.36/model-and-design/docs/nonprofit-ai/v1.0/DEVELOPMENT-procurement-preview.proposed.md)

### nonprofit-ai/v1.0/drafts/0.36/procurement-prototype

- [Private procurement preview proposal](nonprofit-ai/v1.0/drafts/0.36/procurement-prototype/INTEGRATION-PLAN.md)

### sprints

- [Sprint 1: governed AI and a trustworthy shortlist](sprints/SPRINT-01.md)

<!-- END GENERATED INDEX -->
