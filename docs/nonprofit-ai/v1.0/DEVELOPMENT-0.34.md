# Development increment 0.34 saved plan copies

5 October2026 · Integrated candidate · build0.34.0 · domain1.25.0 · platform1.10.0 · schema40.

This appendage extends the preserved BRD, FSD, HLD, LLD, wireframes, dictionary and test design for the same Tola/Impact Platform. It records a bounded plan-copy implementation and the correction of the cleanup privacy residual observed at checkpoint0.33. The original edition1.0 documents,40-requirement baseline and108 specified-case statuses remain unchanged. The [release record](../../RELEASE-0.34-plan-portability.md) owns current qualification and limits.

## Support map

| Proposed requirement | Bounded implementation | Sources | Remaining scope |
| --- | --- | --- | --- |
| FR-NPA-030 | Exact-revision JSON copy with saved meaning, actual archive provenance, separate export authority and fixed replay period | `ai_plan_exports.py`, `ai_plan_export_contracts.py`, `ai_plan_public_export_schema_v1.json`, new pure/live/browser checks | Wider portability formats, re-import, service exit terms, provider arrangements and formal TC-NPA-059 execution |
| FR-NPA-025, FR-NPA-037 | Current read/export authority, current membership, fresh assurance and exact retained-revision availability before issuance/replay | Dedicated endpoint, existing authoriser and migration0040 guards | Formal TC-NPA-060 execution, comprehensive access certification and hosted security assessment |
| FR-NPA-027, FR-NPA-039 | One immutable audit issuance, retained bytes, receipt and outbox intent committed together; original-byte retry and permanent deduplication | Exporter transaction, deferred SQL seals and atomicity/replay tests | Complete operated retention/removal, external delivery and formal acceptance |
| FR-NPA-028, FR-NPA-040 | Deliberate saved-plan download, acknowledgement, uncertain-response retry, expired-copy recovery and byte-integrity checking | `AIPlanPortability.tsx`, `AIPlanExportAdapter.ts`, actual browser checker | Manual accessibility, same-identity session-generation reset and nonprofit UAT |

These relationships do not move acceptance states. TC-NPA-059/060 remain SPECIFIED_NOT_RUN until their complete approved scenarios are formally executed; similar named implementation tests are separate evidence.

## Added data and UI dictionary

| Record or screen | Meaning and boundary |
| --- | --- |
| `ai_plan_export_issuance` |27 immutable tenant-qualified metadata columns binding exact plan/audit revisions, issuer/membership, operation/fingerprint, versions, archive provenance, byte hash/count and fixed replay dates. Permanent100-slot allocation includes retained hidden/expired records. |
| `ai_plan_export_bytes` | Three-column immutable tenant/issuance/UTF-8-byte store. Current-authorised replay ends after168hours; expiry is not deletion. |
| Copy manifest | Closed13-field plan/revision/title/time/version/filename/media-type/hash/size/replay/guidance summary. No hidden component counts or private presence badges. |
| Copy receipt | Closed nine-field issuance/audit/operation/correlation/time/hash/size/replay result. It is a pointer to the original retained artifact and does not grant authority. |
| Public plan document | Frozen recursive allowlist of stored public plan fields and actual archived guidance. No private advice, programme pins, authentication proofs or unknown nested metadata. |
| Saved-plan copy panel | Deliberate JSON download from a selected saved revision; separate export hint; current identity/revision reset; original-operation retry; expiry clears pending state and requires a fresh acknowledgement. |

The [current database dictionary](../../current/CURRENT-DATA-DICTIONARY.md) owns exact columns and registered SQL. The [implementation note](PORTABILITY-IMPLEMENTATION-NOTE.md) retains the design rationale. An exported local file cannot be recalled by the platform; narrower server replay does not revoke a previously downloaded file.

## Privacy correction and qualification

Registered0040 excludes private advice and copy receipts from both generic cleanup definers. Its21 focused native groups use the actual runtime logins and record all40 applied hashes. Ordinary APP plan/audit and worker first-audit controls, unrelated receipt cleanup, cross-tenant/type constraints, immutable projection seals, permanent capacity and database-time guards are included. Earlier failed ordinary-audit controls remain preserved. This scope does not establish final API/browser behaviour or comprehensive privacy acceptance.

Focused API qualification passes148 native checks and144 PGlite checks, with their explicit skips retained. The actual saved0.33 HTTP/native39→40 independently reviewed upgrade passes, and the latest-source actual download browser passes15 groups with four original-byte downloads. Full native2,045/PGlite1,980/unit1,185 scopes pass, with their explicit skips retained; both restarts, restore and populated33→40 upgrade pass. Hosted CI remains unrun. Exact reports and their bounded meanings belong in the release record; counts overlap and are not summed. Private-advice retention and complete plan removal remain unresolved operated-service work, despite the corrected generic-cleanup disclosure.

## Integration and release

The new capability appears only in three proposed manager roles. A generated profile does not widen deployed tenant ceilings or resurrect revoked grants. Historical upgrade qualification must use the prior actual HTTP bootstrap, independently reviewed profile extension and ordinary role assignment on the same upgraded database.

The new owner-authorised window ends03:17:34UTC /08:47:34IST on6October2026. Merge and automatic deployment require four green CI jobs on the exact candidate. The live demo must be verified against the resulting commit/schema/health. Original307 core requirement states remain113 PARTIAL /194 PENDING /zero accepted; no whole-platform completion percentage is inferred from this increment.
