# Impact Platform data governance record

This record describes the current implementation and the decisions required before real-data deployment. It does not assert compliance, a lawful basis, an approved retention schedule or a completed privacy assessment. The BRD/FSD privacy requirements remain unchanged.

## Current data flows

| Data | Current location and handling | Remaining decision or control |
| --- | --- | --- |
| Identity and verified-email evidence | Identity records, hashed/masked profile evidence and local sessions | Live provider lifecycle, account disablement, verified-channel change and recovery qualification |
| Tenant profile and recovery contacts | Privileged control-plane tables with event and receipt history | Actual recovery policy, external-channel verification and relationship-aware departure handling |
| Programme and measurement data | Tenant-fenced records with immutable revisions and explicit grants | Full data-classification and field-policy coverage across future modules |
| Source lineage and approvals | Pinned revisions and attributed independent decisions | Complete downstream derivative inventory and tamper-evidence assurance |
| Internal reports and publications | Frozen database-backed HTML/CSV and recipient-controlled access | Managed artifact storage, distribution, supersession and downloaded-copy handling |
| Audit and work notices | Reference-oriented audit/outbox events and principal-filtered in-app notices | Retention, monitoring, external delivery and operational ownership |
| Development data | Synthetic fixtures and local generated credentials | Never substitute real personal data without approved processing controls |

No external AI model calls, SMS/email dispatch or live ingestion provider is configured by this build. Those future data flows need separate approval before enablement.

## Required deployment decisions

Record the tenant's data controller and processors, processing purposes, permitted categories, collection justification, authorized recipients, hosting and transfer regions, retention and holds, deletion authority, support access and contractual obligations. Name accountable people rather than inferring them from role titles. Keep approved policy references and revision history; do not embed secrets or sensitive records in the documentation.

The target design covers retention, deletion ledgers, holds and restoring current restrictions before reopening a backup. Those workflows are not fully implemented or exercised. A configured retention number in tenant readiness is not proof of scheduled deletion or a legally approved schedule.

## Disclosure and recipient controls

Current controlled publication requires an approved package, independent disclosure review, declared purpose, expiry and named active recipients. Download permission is separate. Access is checked at retrieval and withdrawal blocks later controlled access. It does not erase copies recipients already downloaded. Anonymous publication and the target inference/suppression controls for public aggregates are not delivered.

## Evidence required before real data

The privacy owner must retain an approved processing inventory, data-flow review, applicable privacy assessment, provider and subprocessor review, access matrix, retention/hold policy, tested rights/deletion workflow, incident notification process and restore restrictions. Security supplies current identity, encryption/key-custody, least-privilege, testing and audit evidence. Legal determinations and organizational approvals remain unresolved; this documentation does not manufacture them.

## Change triggers

Reassess whenever a new data class, tenant region, external recipient, provider, AI use case, bulk export, offline device, retention period or support-access pattern is introduced. Map the change to requirements, interface/schema changes, tests and the release gate before enabling the affected capability.
