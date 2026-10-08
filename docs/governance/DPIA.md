# Data protection impact assessment (framework, pre-filled)

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: before the first real-data tenant, any AI enablement, a new data class, or a material change in hosting.

Status: **agent-drafted 2026-10-08, not reviewed by a person or counsel; no certification is claimed; no legal conclusion about necessity, proportionality or lawful basis is made.** Structure follows the elements of GDPR Article 35(7) as a checklist, and is offered as groundwork for any assessment a Data Fiduciary may need under India's DPDP Act 2023. A DPIA is only meaningful for a specific processing; this one is pre-filled for the platform in general and **must be completed per deployment**. Risk ratings below are the drafter's, unreviewed.

## 1. Description of processing
See [RECORD-OF-PROCESSING](RECORD-OF-PROCESSING.md). Context: organisations enter programme data, possibly about vulnerable populations in low- and middle-income countries; the platform is a development build with 0 of 307 requirements accepted, no penetration test, and a single-server staging environment.

## 2. Necessity and proportionality
TBD (owner: Nakul Jain; counsel): purposes per tenant, data minimisation by form design, retention per tenant. Built-in supports: separate read/export/approve capabilities, field and scope limits, purpose-bound grants, time-limited authority.

## 3. Risks and existing controls

| # | Risk to individuals | Existing control (source) | Residual gap | Draft rating |
|---|---|---|---|---|
| 1 | Cross-tenant disclosure | Tenant in every key, forced RLS, non-owner runtime roles, 404 for hidden resources ([CLAUDE.md](../../CLAUDE.md) sections 4 and 6) | No penetration test; native tests single-node | High until tested |
| 2 | Unauthorised access by privileged staff | No self-approval, natural-person independence, custody does not imply data access, denial auditing | Operator account creation asserts the natural-person link (CLAUDE.md section 11) | Medium |
| 3 | Disclosure through backups | Verified sets, checksums | Sets and evidence files not encrypted by the application; erased data persists in older sets; no off-server or immutable copy | High |
| 4 | Disclosure through reports or exports | Separate export capability, independent disclosure review, named recipients, access log | Downloaded copies cannot be recalled; no anonymous publication controls | Medium |
| 5 | Incomplete erasure | Privacy cases with per-store plan, ledger, holds | Members only; restore does not replay erasures; audit and identifiers retained | High |
| 6 | Re-identification through small aggregates | None built | Suppression/inference controls "not delivered" ([DATA-GOVERNANCE](../current/DATA-GOVERNANCE.md)) | High |
| 7 | AI processing of personal data | AI off by default; brief is user-supplied; no tools; `store:false`; human review ([AI-MODEL-CARD](AI-MODEL-CARD.md)) | Self-reported sensitive-data flag is not a detector; provider retention not established | Medium if enabled |
| 8 | Weak recovery or loss of availability | Alerts, nightly sets | No RPO/RTO met ([BACKUP-DR](BACKUP-DR.md)) | Medium |
| 9 | Malicious uploads | Declaration and byte checks, quarantine, EICAR-level scanner | No real anti-malware engine | Medium |

## 4. Consultation and approval
Data subjects or representatives consulted: none. Reviewer, counsel, and DPO/grievance officer: TBD. Approval signature and date: TBD. Re-assessment trigger: see header.
