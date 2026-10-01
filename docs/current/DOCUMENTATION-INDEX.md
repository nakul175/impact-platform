# Impact Platform documentation index

Edition **1.1**, 27 September 2026. Reconciled to application **0.12.0**, domain API **1.10.0**, platform API **1.2.0** and schema **15**. Build **0.13.0** (28 September 2026; schema **16**, platform API **1.3.0**) is recorded in [RELEASE-0.13.md](../RELEASE-0.13.md) build **0.14.0** (28–29 September 2026; native PostgreSQL qualification; schema and both APIs unchanged) in [RELEASE-0.14.md](../RELEASE-0.14.md) build **0.15.0** (29 September 2026; live identity provider; schema **17**, both APIs unchanged) in [RELEASE-0.15.md](../RELEASE-0.15.md) and build **0.16.0** (29 September 2026; worker runtime, outbox dispatcher and email adapter; schema **18**, platform API **1.4.0**, domain API unchanged) in [RELEASE-0.16.md](../RELEASE-0.16.md) and build **0.18.0** (29 September 2026; results framework and planning, built ahead of v0.17; schema **19**, domain API **1.11.0**, platform API unchanged) in [RELEASE-0.18.md](../RELEASE-0.18.md); the Markdown reading copies, guides, registers and inventories below are updated to build 0.18.0, while the Word and workbook editable copies remain at edition 1.1. The sequenced plan for the remaining work is [DELIVERY-PLAN.md](../DELIVERY-PLAN.md).

This set describes the full target product and the current development implementation. Requirements and acceptance conditions are retained; current implementation profiles identify delivered subsets and limitations. The original editions are in [history/v1.0](../history/v1.0/).

## Start here

| Need | Document |
| --- | --- |
| Understand current behavior and limits | [Implementation record](../IMPLEMENTATION.md) and [current architecture](ARCHITECTURE-CURRENT.md) |
| Plan and sequence the remaining work | [Delivery plan](../DELIVERY-PLAN.md) and [remaining work](../NEXT-DELIVERY.md) |
| Use the implemented workflows | [User guide](USER-GUIDE.md) |
| Onboard and administer a tenant | [Administrator guide](ADMINISTRATOR-GUIDE.md) |
| Run and diagnose the development build | [Operations guide](OPERATIONS-GUIDE.md) |
| Deploy, check and back up the staging server | [Deployment guide](DEPLOYMENT-GUIDE.md) |
| Know which keys exist, what they protect and how they rotate | [Key and encryption register](KEY-AND-ENCRYPTION-REGISTER.md) (build 0.25.0) |
| Check what accessibility has and has not been verified | [Accessibility statement](ACCESSIBILITY-STATEMENT.md) and [QA accessibility record](../QA-A11Y-2026-10.md) (build 0.25.0) |
| Read the build 0.25.0 increment records | [v0.25 part A](../RELEASE-0.25a.md), [v0.25 part B](../RELEASE-0.25b.md), [operations hardening](../RELEASE-OPS-2026-10.md), [QA browser coverage](../QA-BROWSER-2026-10.md) |
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
| [Execution register](EXECUTION-REGISTER.csv) | 456 application case identities (405 executed on PGlite, 35 native-only cases executed on PostgreSQL 16.13 and 16 live identity-provider cases executed against Keycloak 26.7.4 on PGlite and on the native login roles, all on 29 September 2026) and 95 browser case identities (93 in nine groups and 2 live-provider checks); one reference-run row represents 143 assertions. |
| [API inventory](CURRENT-API-INVENTORY.md) | Exact 150 domain and 31 platform operations. Authentication (including `/auth/backchannel-logout` since 0.15.0) and health routes are outside the versioned contracts and listed in the implementation record. |
| [Data dictionary and migration ledger](CURRENT-DATA-DICTIONARY.md) | Exact SQL for all 18 migrations and their checksums; JSON payload contracts remain in source. |
| [Data governance](DATA-GOVERNANCE.md) | Data classes, implemented boundaries and unresolved policy decisions. |

## Status and acceptance

The ledger has **81 PARTIAL**, **226 PENDING** and **0 fully accepted** requirements (build 0.18.0, assessed 29 September 2026). The workbook records 29 exact integration/smoke passes, one blocked offline case, 176 cases with partial supporting coverage and 619 not run as full product cases. Those 29 passes already belong to the application checks (325 at edition 1.1; 441 on PGlite and 474 on native PostgreSQL at build 0.18.0); they are not additional executions.

The recorded runs used fresh in-memory PGlite and local identity/assurance, and since build 0.14.0 also single-node native PostgreSQL (16.13 locally, 17.11 in CI) with separately provisioned login roles, an API restart check, a CI-scale restore drill and a previous-schema upgrade check, since build 0.15.0 a live identity provider (a per-run development-mode Keycloak 26.7.4 with TOTP step-up and provider logout), and since build 0.16.0 a worker process on its own login delivering to a loopback SMTP sink and a synthetic sink, and since build 0.18.0 the results framework, targets and targets versus actuals (PGlite and native, plus a planning browser group). A connection pooler, database restart persistence, a backup regime, the owner's chosen identity provider, an email provider and other live providers, production operations, full UAT and formal approvals remain open. This edition adds no fabricated signoffs or test results. The baseline R1/R2/R3 requirement assignments are distinct from the later delivery-stage roadmap.

## Governance and maintenance

The functional baseline defines the required outcome; the implementation profile records what currently exists. If they differ, keep the gap visible and resolve it through development or an explicitly reviewed requirements change. The original source specification and prior release notes are preserved.

For each delivery, update the requirement ledger, implemented OpenAPI contracts, migration inventory, current implementation profile, user/admin workflow instructions, screen coverage, exact test evidence and release decision together. Preserve historical run dates, migration bytes and requirement IDs. A named reviewer and approval date must be supplied by the actual accountable person.

Required release records still to be completed include sponsor/UAT approval, named ownership/RACI, environment-specific data/privacy decisions, the remaining native database qualification (pooling, database restart, scale) and live identity qualification, performance/accessibility/security assessments, backup and incident drills on a deployed environment (the CI-scale restore drill is recorded but is not one), deployment/rollback evidence and the final release signoff. [Release acceptance](RELEASE-ACCEPTANCE.md) assigns role-level accountability and evidence expectations; it does not invent the missing results.

See [change record](CHANGELOG.md), [documentation verification](DOCUMENTATION-QA.md) and [open next-delivery work](../NEXT-DELIVERY.md).
