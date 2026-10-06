# Build 0.34 saved AI plan copies

5 October 2026 · Locally qualified checkpoint candidate · build 0.34.0 · domain API 1.25.0 · platform API 1.10.0 · schema 40.

A currently authorised manager can create a JSON copy of an exact saved adoption-plan revision and its actual archived guidance. The new copy permission is separate from plan reading and editing. Issuance saves the original bytes, an immutable audit event, an outbox intent and an operation receipt in one transaction. A retry returns those same bytes only after checking current authority and the fixed seven-day replay deadline. This increment remains part of the existing Tola/Impact Platform.

The additive database migration also corrects the private-advice receipt disclosure reproduced at checkpoint0.33. Focused registered-schema40 API/SQL checks, the historical independently reviewed access upgrade and current-source actual download browser checks pass. Full native regression passes2,045 tests, full PGlite passes1,980 and the exact Makefile unit set passes1,185. Both API restarts, backup restoration and populated33→40 upgrade pass. The four hosted CI jobs remain unrun. No main merge or deployment is recorded. The preceding local checkpoint is `861c2a807e774ec6bb53ef05c1ee25f853591085`; the last independently observed deployed commit is `69c2cca618ae8dcde8f981c48ece8a1e60f0ff70`, build0.29/schema33.

## Delivered behaviour

The saved-plan workspace exposes a deliberate download panel for an exact saved revision. Its acknowledgement describes the internal-use boundary and the fact that a downloaded local file cannot be recalled. The browser checks the returned UTF-8 byte count and SHA-256 before offering the file. It keeps the original response string rather than serialising the JSON again. Pending requests retain the same operation identifier, request, principal and revision for retry; a definitive expiry clears the pending copy and requires a fresh acknowledgement.

The copy contains the frozen public plan projection and the guidance actually archived with that revision. Guidance is explicitly COMPLETE, PARTIAL or UNAVAILABLE; current catalogue text does not replace a missing historical archive. Private programme references, internal advice cases and briefs, authentication proofs, provider secrets and unknown nested fields are excluded. Known stored values preserve their original meaning and decimal strings. Malformed known source data is refused rather than silently rewritten.

Current plan readability, current membership, separate export permission, exact historical revision availability and fresh authentication are checked before original issuance and replay. A prior receipt does not preserve authority after revocation. Selecting an older revision does not alter the current editable draft.

## Contract and persistence

The domain API adds one dedicated POST operation and now has261 implemented operations; the platform API retains52. The closed request accepts only `operation_id` and `data:{format:"JSON",restriction:"INTERNAL_SELF",acknowledged:true}`. Export records are excluded from generic entity/list/read routes. The bootstrap profile proposes `ai.enablement.export` only for TENANT_ADMIN, MEL_ADMIN and PROGRAMME_MANAGER. Generating the profile does not widen any existing tenant ceiling or grant; existing organisations use the independently reviewed extension and ordinary role-assignment flows.

Migration `0040_ai_plan_portability.sql` is frozen at SHA-256 `a4fa49f75b8734a4bb2ea3e9fa35572345714a74a8275381c1a0355756d00a89`. It adds tenant-qualified immutable issuance metadata and retained-byte tables, forced row security, narrow runtime privileges, permanent operation deduplication and deferred consistency checks across audit, projection, receipt and outbox pointers. All migrations0001–0039 remain byte-identical to the saved0.33 checkpoint. The [current dictionary](current/CURRENT-DATA-DICTIONARY.md) records all30 added columns, the exact SQL and its checksum.

Every issuer has100 permanent storage slots enforced beneath row security. Expired or currently hidden entries still consume slots, and the101st issuance is refused without disclosing a row count. Generation uses the observed database statement time; the runtime insertion guard refuses forged future or pre-transaction generation timestamps. The replay deadline is exactly168 hours after generation. Expiry closes byte replay and does not erase retained bytes or free capacity.

Both generic receipt-cleanup overloads now exclude private advice and plan-copy receipts while retaining ordinary expired-receipt cleanup. The actual worker and application controls remain separate. This correction does not establish an operated private retention/removal policy, and the advice requester-visible case cap is not a permanent storage quota.

## Qualification at this edition

| Executed scope | Observation | Evidence |
| --- | --- | --- |
| Registered migration on actual PostgreSQL runtime logins |21 focused groups pass, including ordinary APP/worker audit controls, both private cleanup exclusions, exact seals, tenant/type constraints, storage cap and generation-time bounds; all40 applied hashes match; captured runtime inputs unchanged | `evidence/sprint-0.34-portability-sql-native-qualification.json`, `evidence/sprint-0.34-portability-sql-native-applied-migrations.json` |
| Profile generation | Only the three manager-role export capabilities are added; this comparison is not a tenant upgrade | `evidence/sprint-0.34-profile-delta.json` |
| Integrated pure exporter checks |82 pass with no skips or failures; separate bounded scope | `evidence/sprint-0.34-ai-plan-export-unit-tests.xml`, `evidence/sprint-0.34-ai-plan-export-unit-source-proof.json` |
| Focused actual API/database checks |148 native pass with one explicit separate historical-setup skip; PGlite144 pass with five explicit skips, including four native-only cases. All40 registered hashes match | `evidence/sprint-0.34-ai-plan-export-native-focused-tests.xml`, `evidence/sprint-0.34-ai-plan-export-pglite-final-tests.xml` |
| Historical saved0.33 HTTP/native39→40 upgrade | Actual initial access, ordinary revocation, migration and independently reviewed extension on the same database pass. Only export is added after independent approval; revoked grants and old plan/archive bytes are preserved. Rejected fixture attempts are retained separately | `evidence/sprint-0.34-export-historical-redacted-summary.json`, `evidence/sprint-0.34-export-historical-redacted-source-chain.json` |
| Current-source actual download browser |15 groups pass, including four deliberate original-byte downloads;303 source fingerprints and served assets unchanged; three automated axe scans have zero violations/incomplete results. Six desktop/390/320 captures reviewed | `evidence/sprint-0.34-export-browser-tests.json`, `evidence/sprint-0.34-export-browser-proof/manifest.json` |
| Web typing and bundle | Strict TypeScript and production Vite build pass after fresh-assurance recovery correction; existing large-bundle advisory retained | `evidence/sprint-0.34-web-build-source-proof.json` |
| Full native regression, restart, restore and populated upgrade |2,045 pass,26 explicit skips and one deselection. Both restarts, backup restore of190 tables/108,188 rows and populated33→40 upgrade pass. All40 migration hashes match;356 source fingerprints unchanged | `evidence/sprint-0.34-full-native-source-proof.json`, `evidence/sprint-0.34-full-native-qualification.json`, `evidence/sprint-0.34-full-native-restore-drill.json` |
| Full local PGlite regression |1,980 pass,91 explicit skips and one deselection; no failures/errors and356 source fingerprints unchanged. This does not establish native role fencing | `evidence/sprint-0.34-full-local-tests.xml`, `evidence/sprint-0.34-full-local-source-proof.json` |
| Exact Makefile unit recipe |1,185 pass with62 explicit database-dependent skips; no failures/errors or source changes. First socket-restricted sandbox attempt is preserved separately | `evidence/sprint-0.34-unit-tests.xml`, `evidence/sprint-0.34-unit-summary.json`, `evidence/sprint-0.34-unit-initial-tests.xml` |
| Independent bounded release review | Both actual-worker cleanup overloads close the reproduced disclosure and retain unrelated cleanup behavior. No further implemented-flow blocker found in the reviewed export/advice/read/replay scope; operated retention/removal is still incomplete | `evidence/sprint-0.34-independent-release-review.json` |
| Hosted identity, container and four-job CI gate | NOT_RUN | Pending financial permission and final candidate |

The initial full native failure is preserved in `evidence/sprint-0.34-full-native-initial/manifest.json`. Its obsolete single-seed assertion was replaced by stronger canonical/current-profile checks, with the immutable0036 seed retained and hard-pinned;21 isolated assertion checks pass. No production migration or permission guard was changed for that correction. Ruff checks/formatting and web/browser Prettier checks pass. Broader existing browser workflows and hosted CI remain final-release gates.

Earlier unregistered scratch attempts and interface fixtures remain in the immutable [draft archive](nonprofit-ai/v1.0/drafts/0.34/HANDOFF.md). They are narrower evidence and do not establish final API or deployment behaviour. Counts overlap between scopes and are not summed as an acceptance total.

## Limits

This increment implements JSON copies for INTERNAL_SELF only. XLSX, re-import, provider exit services, external sharing, complete erasure and operated storage cleanup remain target work. An outbox row records intent and does not establish external delivery. No paid provider call, procurement award, supplier booking, adviser engagement or external message is introduced.

The original307 core requirements retain113 PARTIAL,194 PENDING and zero accepted. The40 nonprofit requirements and108 specified cases retain their reference baseline. Named implementation tests support bounded slices; they do not silently execute specified cases or provide nonprofit UAT, security assessment or manual assistive-technology acceptance.

## Reproduction and integration notes

The API implementation is `apps/api/impact_api/ai_plan_exports.py`; the closed contract and frozen public schema sit beside it. Pure and live checks are `qualification/test_ai_plan_exports_unit.py` and `qualification/test_ai_plan_exports_live.py`. The interface, byte-binding adapter and actual browser checker are `AIPlanPortability.tsx`, `AIPlanExportAdapter.ts` and `tools/browser/ai-plan-export-check.mjs`. `make unit` and `make browser` include the new checks.

The integration window starts19:17:34UTC on5October and ends03:17:34UTC /08:47:34IST on6October2026. Ten workstreams rotate through the four available concurrent agent slots. The owner has authorised main merge and the final demo; all four CI jobs must still pass on the exact candidate head. Separate permission is required before spending CI minutes. Main automatically deploys, so the final demo claim must be bound to the actual deployed commit, schema and healthy status.

No requirement status movement is proposed. Shared release, implementation, qualification, handover, API inventory and development documentation must reflect the final observed state. The [development appendage](nonprofit-ai/v1.0/DEVELOPMENT-0.34.md) maps the new behaviour to the preserved specification.
