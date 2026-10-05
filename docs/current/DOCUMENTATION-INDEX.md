# Impact Platform documentation index

Current additions: [executor and queued imports](../RELEASE-0.28-import-executor.md) merged in #81 as `e6c23b4` with four green CI jobs; staging health unverified. [Collection-round and assignment screens](../RELEASE-0.28-rounds-screen.md) are proposed and unmerged. The target-design documents and their historical editions remain separate from these current implementation records.

Edition **1.1**, 27 September 2026. Reconciled to application **0.12.0**, domain API **1.10.0**, platform API **1.2.0** and schema **15**. Build **0.13.0** (28 September 2026; schema **16**, platform API **1.3.0**) is recorded in [RELEASE-0.13.md](../RELEASE-0.13.md) build **0.14.0** (28–29 September 2026; native PostgreSQL qualification; schema and both APIs unchanged) in [RELEASE-0.14.md](../RELEASE-0.14.md) build **0.15.0** (29 September 2026; live identity provider; schema **17**, both APIs unchanged) in [RELEASE-0.15.md](../RELEASE-0.15.md) and build **0.16.0** (29 September 2026; worker runtime, outbox dispatcher and email adapter; schema **18**, platform API **1.4.0**, domain API unchanged) in [RELEASE-0.16.md](../RELEASE-0.16.md) and build **0.18.0** (29 September 2026; results framework and planning, built ahead of v0.17; schema **19**, domain API **1.11.0**, platform API unchanged) in [RELEASE-0.18.md](../RELEASE-0.18.md); the Markdown reading copies, guides, registers and inventories below are updated to build 0.18.0, while the Word and workbook editable copies remain at edition 1.1. Since then the registers, inventories, guides and records listed below have been updated with each build; at build **0.27.0** (3 October 2026; schema **32**, domain API **1.17.0**, platform API **1.8.0**; [RELEASE-0.27.md](../RELEASE-0.27.md)) they describe that build, and the Word and workbook copies still remain at edition 1.1. The sequenced plan for the remaining work is [DELIVERY-PLAN.md](../DELIVERY-PLAN.md).

This set describes the full target product and the current development implementation. Requirements and acceptance conditions are retained; current implementation profiles identify delivered subsets and limitations. The original editions are in [history/v1.0](../history/v1.0/).

## Start here

| Need | Document |
| --- | --- |
| Continue the engineering (a person or an AI agent) | [AGENTS.md](../../AGENTS.md) (rules, commands, conventions, safety), then the [handover](../HANDOVER.md) (state on 3 October 2026: versions, `main` versus staging, CI, owner decisions, known issues, next steps) and the full engineering brief [CLAUDE.md](../../CLAUDE.md) (model-agnostic despite its name) |
| Plan the next slices and run them in parallel | [Backlog](../handover/BACKLOG.md) (ready-to-run slices, reconciliation of the earlier backlog, TolaData comparison) and [parallel work](../handover/PARALLEL-WORK.md) (builder rules, integrator checklist, lessons) |
| Read the build 0.27.0 records | [Integration record](../RELEASE-0.27.md) and the slice notes: [imports](../RELEASE-0.27-imports.md), [planning](../RELEASE-0.27-planning.md), [forms](../RELEASE-0.27-forms.md), [reports and dashboards](../RELEASE-0.27-reports-dashboards.md), [security and privacy](../RELEASE-0.27-security-privacy.md), [operator lifecycle](../RELEASE-0.27-operators.md), [status and alerts](../RELEASE-0.27-status-alerts.md), [e-mail readiness](../RELEASE-0.27-email.md), [console and guides](../RELEASE-0.27-ux.md), [non-functional QA](../QA-NONFUNCTIONAL-2026-10.md) and the [training-video generator](../TRAINING-VIDEO.md) |
| Choose the e-mail provider | [E-mail provider decision pack](EMAIL-PROVIDER-DECISION.md) (Postmark, Amazon SES in Mumbai, Brevo; what the owner must supply) |
| Understand current behavior and limits | [Implementation record](../IMPLEMENTATION.md) and [current architecture](ARCHITECTURE-CURRENT.md) |
| Plan and sequence the remaining work | [Delivery plan](../DELIVERY-PLAN.md) and [remaining work](../NEXT-DELIVERY.md) |
| Use the implemented workflows | [User guide](USER-GUIDE.md) |
| Onboard and administer a tenant | [Administrator guide](ADMINISTRATOR-GUIDE.md) |
| Run and diagnose the development build | [Operations guide](OPERATIONS-GUIDE.md) |
| Deploy, check and back up the staging server | [Deployment guide](DEPLOYMENT-GUIDE.md) |
| Know which keys exist, what they protect and how they rotate | [Key and encryption register](KEY-AND-ENCRYPTION-REGISTER.md) (build 0.25.0) |
| Check what accessibility has and has not been verified | [Accessibility statement](ACCESSIBILITY-STATEMENT.md) and [QA accessibility record](../QA-A11Y-2026-10.md) (build 0.25.0) |
| Read the build 0.26.0 increment record | [v0.26a usable staging](../RELEASE-0.26a.md) (reference data, `initial-access-v2`, purpose-bound grants, operator onboarding; owner click-path in [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) §4.1) |
| Read the build 0.25.0 increment records | [v0.25 part A](../RELEASE-0.25a.md), [v0.25 part B](../RELEASE-0.25b.md), [operations hardening](../RELEASE-OPS-2026-10.md), [QA browser coverage](../QA-BROWSER-2026-10.md) |
| Run Release 1 user acceptance | [UAT pack](UAT-PACK.md) — Release 1 user-acceptance pack (staging and local tracks, 22 scenarios, sign-off sheet) |
| Support the staging service | [Support runbook](SUPPORT-RUNBOOK.md) — support roles, health checks, alert codes, incident first steps, escalation, ticket hygiene |
| See what blocks Release 1 acceptance | [Release 1 acceptance gaps](RELEASE-1-ACCEPTANCE-GAPS.md) — what blocks Release 1 acceptance (assessed at build 0.25.0; A1–A4 resolved in build 0.26.0, A5 in build 0.27.0) |
| Read the QA 2026-10 records merged onto build 0.25.0 | [degradation](../QA-DEGRADATION-2026-10.md), [performance harness](../QA-PERFORMANCE-2026-10.md) (evidence `../evidence/performance-2026-10-01.json`), [UAT pack, runbook and gaps](../QA-UAT-2026-10.md) |
| Assess release readiness | [Release acceptance record](RELEASE-ACCEPTANCE.md) and [qualification evidence](../QUALIFICATION.md) |
| Review exact requirement coverage | [Traceability CSV](TRACEABILITY.csv) and [completion ledger](../COMPLETION-LEDGER.md) |

## Specifications and designs

Each Word document has a Markdown reading copy for GitHub. The editable Word file preserves the original detailed baseline and adds a build-specific implementation profile.

| Document | Read on GitHub | Editable file |
| --- | --- | --- |
| API and Event Contracts | [Markdown](Impact-Management-API-and-Event-Contracts-v1.1.md) | [Word](Impact-Management-API-and-Event-Contracts-v1.1.docx) |
| Access Control Specification | [Markdown](Impact-Management-Access-Control-Specification-v1.1.md) | [Word](Impact-Management-Access-Control-Specification-v1.1.docx) |
| Architecture Decision Records | [Markdown](Impact-Management-Architecture-Decision-Records-v1.1.md) | [Word](Impact-Management-Architecture-Decision-Records-v1.1.docx) |
| Database Migration Specification | [Markdown](Impact-Management-Database-Migration-Specification-v1.1.md) | [Word](Impact-Management-Database-Migration-Specification-v1.1.docx) |
| Development and CI Specification | [Markdown](Impact-Management-Development-and-CI-Specification-v1.1.md) | [Word](Impact-Management-Development-and-CI-Specification-v1.1.docx) |
| Engineering Implementation Plan | [Markdown](Impact-Management-Engineering-Implementation-Plan-v1.1.md) | [Word](Impact-Management-Engineering-Implementation-Plan-v1.1.docx) |
| Fixture and Acceptance Specification | [Markdown](Impact-Management-Fixture-and-Acceptance-Specification-v1.1.md) | [Word](Impact-Management-Fixture-and-Acceptance-Specification-v1.1.docx) |
| HLD | [Markdown](Impact-Management-HLD-v1.1.md) | [Word](Impact-Management-HLD-v1.1.docx) |
| LLD | [Markdown](Impact-Management-LLD-v1.1.md) | [Word](Impact-Management-LLD-v1.1.docx) |
| Operational Runbooks | [Markdown](Impact-Management-Operational-Runbooks-v1.1.md) | [Word](Impact-Management-Operational-Runbooks-v1.1.docx) |
| BRD | [Markdown](Impact-Management-Platform-BRD-v1.1.md) | [Word](Impact-Management-Platform-BRD-v1.1.docx) |
| FSD | [Markdown](Impact-Management-Platform-FSD-v1.1.md) | [Word](Impact-Management-Platform-FSD-v1.1.docx) |
| Security Threat Model | [Markdown](Impact-Management-Security-Threat-Model-v1.1.md) | [Word](Impact-Management-Security-Threat-Model-v1.1.docx) |
| Test Strategy | [Markdown](Impact-Management-Test-Strategy-v1.1.md) | [Word](Impact-Management-Test-Strategy-v1.1.docx) |
| UI Component and Interaction Specification | [Markdown](Impact-Management-UI-Component-and-Interaction-Specification-v1.1.md) | [Word](Impact-Management-UI-Component-and-Interaction-Specification-v1.1.docx) |

## Interactive and structured records

| Artifact | Coverage |
| --- | --- |
| [Wireframes](Impact-Management-Wireframes-v1.1.html) | 30 original target screens and 4 current workflow additions; synthetic interaction only. Download and open locally; GitHub displays source. |
| [Screen coverage](SCREEN-COVERAGE.csv) | Every screen (34 baseline and UI35 authority renewal) mapped to current support and limits. |
| [Test catalogue](Impact-Management-Test-Catalogue-v1.1.xlsx) | All 825 baseline cases, scenarios, fixtures and 307 requirement links, with current execution evidence. |
| [Implementation register](Impact-Management-Implementation-Register-v1.1.xlsx) | Requirements, foundations, packages, contracts, roles, threats, screens, release gates and deployment inputs. |
| [Execution register](EXECUTION-REGISTER.csv) | Build 0.27.0: 1,024 application case identities (952 executed on PGlite, 49 native-only cases executed on PostgreSQL 16.13, the 2 restart phases, 5 cases executed only in the focused run through PgBouncer with a database stop and start, and 16 live identity-provider cases recorded on 30 September 2026) and 155 browser case identities (153 in nineteen groups and 2 live-provider checks); one reference-run row represents 143 assertions. |
| [API inventory](CURRENT-API-INVENTORY.md) | Exact 230 domain and 44 platform operations (build 0.27.0). Authentication (including `/auth/backchannel-logout` since 0.15.0), health and status (`GET /v1/status` since 0.27.0) routes are outside the versioned contracts and listed in the implementation record. |
| [Data dictionary and migration ledger](CURRENT-DATA-DICTIONARY.md) | Exact SQL for all 32 migrations and their checksums; JSON payload contracts remain in source. |
| [Data governance](DATA-GOVERNANCE.md) | Data classes, implemented boundaries and unresolved policy decisions. |

## Status and acceptance

The ledger currently has **113 PARTIAL**, **194 PENDING** and **0 fully accepted** requirements (build 0.27.0, 3 October 2026; `make ledger` regenerates it; it was 106 PARTIAL and 201 PENDING at builds 0.25.0 and 0.26.0). The rest of this paragraph is the build 0.18.0 record: the ledger then had **81 PARTIAL**, **226 PENDING** and **0 fully accepted** requirements (assessed 29 September 2026). The workbook records 29 exact integration/smoke passes, one blocked offline case, 176 cases with partial supporting coverage and 619 not run as full product cases. Those 29 passes already belong to the application checks (325 at edition 1.1; 441 on PGlite and 474 on native PostgreSQL at build 0.18.0); they are not additional executions.

The recorded runs used fresh in-memory PGlite and local identity/assurance, and since build 0.14.0 also single-node native PostgreSQL (16.13 locally, 17.11 in CI) with separately provisioned login roles, an API restart check, a CI-scale restore drill and a previous-schema upgrade check, since build 0.15.0 a live identity provider (a per-run development-mode Keycloak 26.7.4 with TOTP step-up and provider logout), and since build 0.16.0 a worker process on its own login delivering to a loopback SMTP sink and a synthetic sink, and since build 0.18.0 the results framework, targets and targets versus actuals (PGlite and native, plus a planning browser group), and since build 0.27.0 a focused native run through PgBouncer with a clean database stop and start and smoke-scale load profiles. A deployed connection pooler, persistence across a database crash, an off-server backup regime, the owner's chosen identity provider, an email provider and other live providers, production operations, full UAT and formal approvals remain open. This edition adds no fabricated signoffs or test results. The baseline R1/R2/R3 requirement assignments are distinct from the later delivery-stage roadmap.

## Governance and maintenance

The functional baseline defines the required outcome; the implementation profile records what currently exists. If they differ, keep the gap visible and resolve it through development or an explicitly reviewed requirements change. The original source specification and prior release notes are preserved.

For each delivery, update the requirement ledger, implemented OpenAPI contracts, migration inventory, current implementation profile, user/admin workflow instructions, screen coverage, exact test evidence and release decision together. Preserve historical run dates, migration bytes and requirement IDs. A named reviewer and approval date must be supplied by the actual accountable person.

Required release records still to be completed include sponsor/UAT approval, named ownership/RACI, environment-specific data/privacy decisions, the remaining native database qualification (a deployed pooler, crash restart, scale) and live identity qualification, performance/accessibility/security assessments, backup and incident drills on a deployed environment (the CI-scale restore drill is recorded but is not one), deployment/rollback evidence and the final release signoff. [Release acceptance](RELEASE-ACCEPTANCE.md) assigns role-level accountability and evidence expectations; it does not invent the missing results.

See [change record](CHANGELOG.md), [documentation verification](DOCUMENTATION-QA.md) and [open next-delivery work](../NEXT-DELIVERY.md).

## Nonprofit AI enablement proposal

- [0.30 integrated release note](../RELEASE-0.30-nonprofit-ai-enablement.md): current implemented foundation, exact limits and future product slices.
- [Catalogue](../RELEASE-0.30-ai-catalog.md), [workspace](../RELEASE-0.30-ai-workspace.md), and [Mercy Corps scenarios](../RELEASE-0.30-reuse-scenarios.md): component provenance and validation.

- [Nonprofit AI adoption tool](../RELEASE-0.30-ai-adoption-tool.md): delivered product workflow and verification.
- [Source-backed solutions](../RELEASE-0.30-ai-solutions.md): official product evidence and comparison limits.
- [Durable adoption plans](../RELEASE-0.30-ai-adoption-plans.md): draft persistence and permission boundaries.
- [Product screens](../RELEASE-0.30-ai-product-ui.md): browse, compare, learning, procurement and pilot flow.
