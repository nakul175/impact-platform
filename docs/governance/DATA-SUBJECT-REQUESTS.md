# Data-subject request procedure

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: participants become data subjects, a change to the privacy-case operations, or counsel's review.

Status: **agent-drafted 2026-10-08 from [RELEASE-0.25b](../RELEASE-0.25b.md) and the code; not reviewed by a person or counsel; no compliance is claimed.** It describes how access and erasure requests are handled technically so that GDPR Articles 15 and 17 and the rights of a Data Principal under India's DPDP Act 2023 (access, correction, erasure, grievance redressal) can be served once a controller decides how. Correction and objection have no dedicated workflow. Response deadlines are a legal input: TBD (counsel).

Scope: **members of a tenant only.** No participant records exist in this build, so a request by a programme participant cannot be executed in the product.

## Steps (People & access, Data-subject requests; API `privacy-cases`)

1. **Receive and verify** outside the product: confirm who is asking and which tenant holds the data. Record the verification note in the case. The tenant's controller decides; the platform operator does not act without the tenant's instruction: TBD per contract.
2. **Intake** (PRIVACY or TENANT_ADMIN role holding a `DATA_SUBJECT_REQUEST` purpose-bound grant): create the case, type ACCESS or ERASURE, subject membership, reason, optional deadline.
3. **Plan:** the system produces a per-store plan and its SHA-256 (member profile, invitations, revision payloads, projections, outbox, object store). Items under a retention hold or shared evidence show as HELD.
4. **Independent approval** (fresh authentication within 300 s): an approver who is a different natural person from every author and from the subject confirms the plan hash. Erasure needs the member to be offboarded and not hold custody.
5. **Execute:** ACCESS builds a JSON export package (expires in 7 days, download logged). ERASURE runs in one transaction; failed object deletions are retried; a partial status is shown if any remain.
6. **Deliver or confirm** to the requester through the controller's own channel; the platform sends nothing itself. Close the case and keep the ledger.

## What is not erased, and why it is told to the requester

Pseudonymous principal and membership identifiers, audit events, the case record, and every official number, snapshot and report (altering them would change approved results). Data in backup sets taken before the erasure persists until they age out (up to 4 weeks) and in droplet backups; a restore does not replay erasures ([BACKUP-DR](BACKUP-DR.md)).

## Evidence

`privacy_store_action`, `deletion_ledger`, `retention_proof`, audit events, `privacy_export_access`. Browser check of the screen: none. Live server use: none recorded.
