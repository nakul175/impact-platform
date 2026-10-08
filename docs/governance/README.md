# Governance documents: map of the 27 standard items

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: any document in the table is added, moved or retired, or the owner changes a decision in section 4.

The owner requires every application to carry the same 27 standard documents. This page maps each item to its **canonical** file in this repository, with an honest status. Baseline: `main` at build 0.36.0 (`2ab2153`, `VERSION.json`; schema 40). The repository is a development build, 0 of 307 requirements accepted, synthetic data only.

**Reviewer status:** every document marked NEW or EXTENDED was drafted by an agent on 2026-10-08. The security, privacy, compliance, AI and incident documents are **not reviewed by a person or counsel and claim no certification or legal compliance.** Unknown facts are written "TBD (owner: Nakul Jain)".

Status words: **PRESENT** (existed, mapped only), **EXTENDED** (existed, fixed or added to), **NEW** (created in this change), **STALE** (exists but out of date; flagged, not rewritten).

| # | Item | Canonical path | Status | Last reviewed |
|---|---|---|---|---|
| 1 | README | [README.md](../../README.md) | EXTENDED: status line now says build 0.36.0 (was v0.28.0); older 5 October paragraphs kept as history | 2026-10-08 |
| 2 | LICENSE, CODEOWNERS | [LICENSE](../../LICENSE) (placeholder: no licence granted), [docs/CODEOWNERS](../CODEOWNERS) | NEW (see section 5 for file locations) | 2026-10-08 |
| 3 | Contributing, PR template | [CONTRIBUTING.md](../../CONTRIBUTING.md), [.github/PULL_REQUEST_TEMPLATE.md](../../.github/PULL_REQUEST_TEMPLATE.md) | NEW (summarises [AGENTS.md](../../AGENTS.md)) | 2026-10-08 |
| 4 | Environment / config reference | [env.example](env.example) (names only, from `config.py`, `worker.py`, `deploy/compose.yaml`, `specification/contracts/deployment-inputs.json`) | NEW | 2026-10-08 |
| 5 | Changelog | [docs/current/CHANGELOG.md](../current/CHANGELOG.md) | PRESENT, STALE for builds 0.34 to 0.36 (entry added pointing to their release notes) | 2026-10-08 |
| 6 | Security policy | [SECURITY.md](../../SECURITY.md) (contact nakul.jain@aplyd.com) | NEW | 2026-10-08 |
| 7 | Architecture overview | [ARCHITECTURE-CURRENT.md](../current/ARCHITECTURE-CURRENT.md) (**STALE: describes build 0.18.0**), [HLD](../current/Impact-Management-HLD-v1.1.md), [LLD](../current/Impact-Management-LLD-v1.1.md); architecture as built is best read in [CLAUDE.md](../../CLAUDE.md) section 5 | PRESENT, STALE flagged | 2026-10-08 |
| 8 | Design docs / RFC process | [DESIGN-AND-DECISION-PROCESS.md](DESIGN-AND-DECISION-PROCESS.md) (indexes the existing practice, proposes a lightweight route) | NEW | 2026-10-08 |
| 9 | ADRs | [Architecture Decision Records v1.1](../current/Impact-Management-Architecture-Decision-Records-v1.1.md) (ADR01 to ADR22); AI extension: [13-ARCHITECTURE-DECISIONS](../nonprofit-ai/v1.0/13-ARCHITECTURE-DECISIONS.md) | PRESENT | 2026-10-08 |
| 10 | API contract | [packages/contracts/openapi-implemented.json](../../packages/contracts/openapi-implemented.json) (domain 1.25.0, 261 operations), [openapi-platform.json](../../packages/contracts/openapi-platform.json) (1.10.0, 52), [API-INVENTORY.md](../API-INVENTORY.md); `openapi.json` is the design contract, never generate clients from it | PRESENT | 2026-10-08 |
| 11 | Data dictionary, migrations | [CURRENT-DATA-DICTIONARY.md](../current/CURRENT-DATA-DICTIONARY.md), [infrastructure/migrations/](../../infrastructure/migrations) (0001 to 0040, frozen) | PRESENT | 2026-10-08 |
| 12 | Runbooks | [SUPPORT-RUNBOOK.md](../current/SUPPORT-RUNBOOK.md) (live), [OPERATIONS-GUIDE.md](../current/OPERATIONS-GUIDE.md), [Operational Runbooks v1.1](../current/Impact-Management-Operational-Runbooks-v1.1.md) (target procedures, no drill recorded) | PRESENT | 2026-10-08 |
| 13 | SLOs, alert catalogue | [SLOS-AND-ALERTS.md](SLOS-AND-ALERTS.md) (proposed targets, not measured) | NEW | 2026-10-08 |
| 14 | Incident process, postmortem template | [INCIDENT-PROCESS.md](INCIDENT-PROCESS.md), [POSTMORTEM-TEMPLATE.md](POSTMORTEM-TEMPLATE.md) | NEW | 2026-10-08 |
| 15 | Backup / DR with RPO, RTO, restore-test log | [BACKUP-DR.md](BACKUP-DR.md) (log has zero real-host entries) over [DEPLOYMENT-GUIDE](../current/DEPLOYMENT-GUIDE.md) section 6 | NEW | 2026-10-08 |
| 16 | Test strategy | [Test Strategy v1.1](../current/Impact-Management-Test-Strategy-v1.1.md), [QUALIFICATION.md](../QUALIFICATION.md), [Test Catalogue](../current/Impact-Management-Test-Catalogue-v1.1.xlsx) | PRESENT | 2026-10-08 |
| 17 | Release / deploy process | [DEPLOYMENT-GUIDE.md](../current/DEPLOYMENT-GUIDE.md), [deploy/README.md](../../deploy/README.md), [RELEASE-ACCEPTANCE.md](../current/RELEASE-ACCEPTANCE.md), CI in `.github/workflows/qualification.yml` | EXTENDED: deploy/README.md was absent | 2026-10-08 |
| 18 | User and admin guide | [USER-GUIDE.md](../current/USER-GUIDE.md), [ADMINISTRATOR-GUIDE.md](../current/ADMINISTRATOR-GUIDE.md) | PRESENT; both open with a "build 0.33 local candidate" banner and were last rewritten for 0.26 to 0.27: check against 0.36 before relying on them | 2026-10-08 |
| 19 | Third-party inventory / SBOM | [DEPENDENCY-INVENTORY.md](DEPENDENCY-INVENTORY.md), [sbom/](sbom/), [THIRD-PARTY-LICENCES.md](THIRD-PARTY-LICENCES.md) | NEW | 2026-10-08 |
| 20 | Threat model | [Security Threat Model v1.1](../current/Impact-Management-Security-Threat-Model-v1.1.md) (TH01 to TH32); AI extension: [09-SECURITY-AND-PRIVACY](../nonprofit-ai/v1.0/09-SECURITY-AND-PRIVACY.md) | PRESENT | 2026-10-08 |
| 21 | Access-control model | [Access Control Specification v1.1](../current/Impact-Management-Access-Control-Specification-v1.1.md), [packages/contracts/access-policy.json](../../packages/contracts/access-policy.json) | PRESENT | 2026-10-08 |
| 22 | Secrets / key register | [SECRETS-REGISTER.md](SECRETS-REGISTER.md) over [KEY-AND-ENCRYPTION-REGISTER.md](../current/KEY-AND-ENCRYPTION-REGISTER.md) | NEW | 2026-10-08 |
| 23 | Privacy: record of processing, DPIA, retention, data-subject requests | [RECORD-OF-PROCESSING](RECORD-OF-PROCESSING.md), [DPIA](DPIA.md), [RETENTION-SCHEDULE](RETENTION-SCHEDULE.md), [DATA-SUBJECT-REQUESTS](DATA-SUBJECT-REQUESTS.md); existing [DATA-GOVERNANCE](../current/DATA-GOVERNANCE.md) | NEW (frameworks only: GDPR Art. 30 and 35, DPDP Act 2023) | 2026-10-08 |
| 24 | Secure-dev / supply-chain evidence | [SECURE-DEV-SUPPLY-CHAIN.md](SECURE-DEV-SUPPLY-CHAIN.md) | NEW | 2026-10-08 |
| 25 | Accessibility statement | [ACCESSIBILITY-STATEMENT.md](../current/ACCESSIBILITY-STATEMENT.md), [QA-A11Y-2026-10](../QA-A11Y-2026-10.md) | PRESENT (build 0.25.0 scope) | 2026-10-08 |
| 26 | AI-feature docs | [AI-MODEL-CARD.md](AI-MODEL-CARD.md), [AI-EVALUATION-AND-LIMITS.md](AI-EVALUATION-AND-LIMITS.md); design set [docs/nonprofit-ai/v1.0/](../nonprofit-ai/v1.0/README.md) | NEW | 2026-10-08 |
| 27 | Compliance control mapping | [COMPLIANCE-CONTROL-MAPPING.md](COMPLIANCE-CONTROL-MAPPING.md) | NEW | 2026-10-08 |

## Which copy is canonical (duplicates)

| Location | What it is | Use |
|---|---|---|
| `docs/current/*.md` | Edition 1.1 reading copies of the ten specifications plus current guides and registers, reconciled to the implementation | **Canonical** for specifications and operations documents. The `.docx` beside each is the editable twin |
| `specification/docs/01-...10-*.md` | The original v1.0 engineering package (25 September 2026) | Preserved, read-only, never edit |
| `docs/history/v1.0/` | Original v1.0 Word and workbook files | Frozen history |
| `docs/RELEASE-*.md`, `docs/QUALIFICATION.md`, `docs/evidence/` | Per-increment records and recorded test evidence | Canonical for what a given build delivered and what was run |
| `docs/nonprofit-ai/v1.0/` | Separate 15-document baseline for the nonprofit AI extension | Canonical for that extension's requirements and design; marked proposed |

## 4. Open owner decisions raised by this bundle

1. **Repository licence:** none chosen. Proprietary placeholder in place. Choose a licence or keep it; confirm how it relates to the Apache-2.0 component in `third_party/` (needs counsel).
2. Named on-call route, response times, deputies, postmortem timing ([INCIDENT-PROCESS](INCIDENT-PROCESS.md)).
3. Off-server backup storage; first real-host restore test; agreed RPO and RTO ([BACKUP-DR](BACKUP-DR.md)).
4. Data controller and processor, sub-processor contracts, DPO or grievance officer, legal retention periods ([RECORD-OF-PROCESSING](RECORD-OF-PROCESSING.md)).
5. Whether to add scanners (dependency, secret, image) to CI, which costs CI minutes ([SECURE-DEV-SUPPLY-CHAIN](SECURE-DEV-SUPPLY-CHAIN.md)).
6. AI: funding a project key, evaluation set, provider terms ([AI-MODEL-CARD](AI-MODEL-CARD.md)).
7. Counsel review of every privacy, compliance and licence page.

## 5. File locations chosen to avoid starting CI

`.github/workflows/qualification.yml` ignores a pull request only when **every** changed file is `**.md` or under `docs/`. Files without a `.md` extension elsewhere would start the paid four-job run, and paid CI needs the owner's approval. Therefore: the licence is now the conventional `LICENSE` (moved with the shared-helpers code change), CODEOWNERS is `docs/CODEOWNERS` (a location GitHub reads), and the configuration reference is `docs/governance/env.example`. **Follow-up for the owner's go-ahead on CI:** move to `.github/CODEOWNERS` and root `.env.example`; that change will start CI.

## 6. Verified in this change

Relative links in the new files checked by script; no code, contract, migration, `VERSION.json` or test was changed; no heavy suite was run. The repository has no documentation-check script (`scripts/` contains none).
