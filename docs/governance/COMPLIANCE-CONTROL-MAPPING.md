# Compliance control mapping

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: a new control, a framework chosen by the owner or a client, or legal review.

Status: **agent-drafted 2026-10-08; not reviewed by a person or counsel; no certification, attestation or legal compliance is claimed.** The platform is a development build with 0 of 307 requirements accepted. This is an index from framework themes to the control or document that bears on them, with an honest status, for use by whoever later performs a real assessment. Article and section references are indicative themes; verify against the legal texts: TBD (counsel).

Status words: **Partial** = a bounded subset exists with tests; **Documented** = a framework or draft exists, nothing implemented; **None** = not built; **Unknown** = depends on facts not in the repository.

| Theme (framework reference) | Platform control / document | Status |
|---|---|---|
| Lawfulness, purpose limitation, minimisation (GDPR Art. 5; DPDP Act 2023 s.4 to 7, notice and consent) | Tenant-controlled purposes; purpose-bound grants; [RECORD-OF-PROCESSING](RECORD-OF-PROCESSING.md). No consent-management or notice feature | Documented |
| Data protection by design (GDPR Art. 25) | Forced row-level security, deny-by-default, closed DTOs, separate read/export/approve capabilities ([Access-Control spec](../current/Impact-Management-Access-Control-Specification-v1.1.md)) | Partial |
| Records of processing (GDPR Art. 30) | [RECORD-OF-PROCESSING](RECORD-OF-PROCESSING.md) | Documented |
| Security safeguards (GDPR Art. 32; DPDP s.8(5)) | RLS, MFA assurance, sealed addresses, keyrings ([SECRETS-REGISTER](SECRETS-REGISTER.md)); not encrypted at rest by the application; no penetration test ([SECURE-DEV](SECURE-DEV-SUPPLY-CHAIN.md)) | Partial |
| Breach detection and notification (GDPR Art. 33 to 34; DPDP s.8(6)) | [INCIDENT-PROCESS](INCIDENT-PROCESS.md); audit and denial records; no notification workflow or deadlines | Documented |
| DPIA (GDPR Art. 35; DPDP s.10 for significant fiduciaries) | [DPIA](DPIA.md) | Documented |
| Processors and sub-processors (GDPR Art. 28; DPDP s.8(2)) | Sub-processor list in the record; contracts not in repo | Unknown |
| International transfers (GDPR Ch. V; DPDP s.16) | Region `do-blr1`; optional OpenAI call | Unknown |
| Access right (GDPR Art. 15; DPDP s.11) | Privacy-case ACCESS export for members ([DATA-SUBJECT-REQUESTS](DATA-SUBJECT-REQUESTS.md)) | Partial (members only) |
| Erasure and correction (GDPR Art. 16, 17; DPDP s.12; s.8(7)) | Privacy-case ERASURE with plan, holds, ledger; no correction workflow; backups not replayed ([BACKUP-DR](BACKUP-DR.md)) | Partial |
| Grievance redressal and nomination (DPDP s.13, 14) | Contact stated in SECURITY.md only; no grievance process | None |
| Retention and storage limitation (GDPR Art. 5(1)(e); DPDP s.8(7)) | Sweep and tenant policies ([RETENTION-SCHEDULE](RETENTION-SCHEDULE.md)); schedule not legally approved | Partial |
| Accountability, logging (GDPR Art. 5(2)) | Append-only audit, audit export with hash chain, denial auditing | Partial |
| Availability and resilience (GDPR Art. 32(1)(c)) | Backups and drill; no RPO/RTO met | Partial |
| Automated processing / AI transparency (GDPR Art. 22 themes) | AI advisory is a proposal for human review; [AI-MODEL-CARD](AI-MODEL-CARD.md) | Documented |
| Web accessibility (WCAG 2.2 AA) | Automated axe scan of 43 page states, no serious or critical violations; no manual or screen-reader audit ([ACCESSIBILITY-STATEMENT](../current/ACCESSIBILITY-STATEMENT.md)) | Partial |
| Application security verification (OWASP ASVS themes: authentication, session, access control, validation, cryptography, logging) | Session and CSRF controls, OIDC with PKCE, access-control tests; not assessed against ASVS | Partial, unassessed |
| Supply-chain (SBOM, dependency control) | [DEPENDENCY-INVENTORY](DEPENDENCY-INVENTORY.md) | Partial |
| ISO/IEC 27001, SOC 2 | No ISMS, no audit, no attestation | None |
| Licensing | [THIRD-PARTY-LICENCES](THIRD-PARTY-LICENCES.md); own licence undecided | Partial |

The repository's own requirement-to-evidence mapping is [TRACEABILITY.csv](../current/TRACEABILITY.csv) and the [completion ledger](../COMPLETION-LEDGER.md); release gates are in [RELEASE-ACCEPTANCE](../current/RELEASE-ACCEPTANCE.md).
