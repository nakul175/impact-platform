# Next bounded slice: internal saved-plan portability

5 October 2026 · Retained implementation design, now registered in local candidate0.34. Final API/browser/full/hosted qualification remains pending; see [current release](../../RELEASE-0.34-plan-portability.md).

The proposed first slice supports part of FR-NPA-030. A separately permitted current member deliberately downloads one exact saved AI adoption-plan revision for their own internal use. It is a draft planning record, not an approved procurement decision or official programme report. It does not deliver to an external recipient, import a package or establish provider exit acceptance. The original BRD/FSD/HLD/LLD and TC-NPA-059/060 remain unchanged and unrun.

## Contract and authority

Use a closed CSRF-protected POST selecting an exact plan/revision, bounded format, operation ID and acknowledgement of the internal-use restriction. `ai.enablement.export` is separate from read/manage, with current exact-revision read scope required at issuance and every replay. A capability hint controls the affordance; the server controls authority. Introduce the capability through a new immutable registered profile and the existing independently reviewed access extension, never by automatically widening an applied tenant's ceiling. Map the exporter responsibility explicitly to role/profile capabilities before implementation.

Resolve the intended recipient as the authenticated current tenant member and fix the restriction to `INTERNAL_SELF`. Accept no recipient email, contact or raw directory selector. Show that downloaded bytes cannot be recalled; an issuance/receipt expiry cannot prevent someone opening their saved local file.

## Exact package and exclusions

Build a closed allowlist from public plan data and its actually verified archived guidance. Include tenant context, exact object/revision, saved time, schema/renderer versions, actual guidance versions and COMPLETE/PARTIAL/UNAVAILABLE status. Never substitute current guide wording for missing history. Use constant declared components, without private linkage badges, omitted counts or hidden-field presence flags.

Exclude private impact selectors/pins/results, all human-advice cases/briefs/actions/participant proofs, provider outputs/configuration, credentials and unknown stored metadata. Do not serialize the raw stored plan payload. Canonical JSON is the lossless primary format; spreadsheet views can reuse pure existing renderer/formula-safety functions only with explicit typed-data limitations and no re-import claim. The existing formula guard recognises ASCII controls/space and BOM before =,+,-,@; it is not a general Unicode-whitespace normaliser. Keep bounded per-field rows and reject unrepresentable or overlong spreadsheet cells rather than relying on silent truncation. Existing Mercy Corps attribution must follow any reused styling; the approved-framework export service's business authority is not reusable for an AI draft.

## Persistence and recovery

Render a small bounded package synchronously. Retain an immutable tenant-qualified issuance record with original manifest generation time, exact schema/renderer, content digest, byte count, resolved internal recipient/restriction and correlation. Atomically record the audit and exact-operation receipt. An object/revision-only audit is insufficient to identify issued bytes. Either retain the actual issued bytes under narrow current-authorised access or guarantee exact original rendering across deployments; changed bytes cannot reuse the original receipt.

Retry an uncertain request with its original operation, format, revision and restriction. Recheck current export/read/membership/revision availability before returning issued bytes. A newer plan head does not switch the requested historical revision. Current authority refusal clears any preview or object URL. Use no-store/nosniff, a fixed safe filename and no public or presigned URL. Issuance audit proves authorised bytes were returned, not that the local filesystem saved them.

## Interface and meaningful checks

Show **Export this saved revision** for an opened saved plan with the export hint. Display its saved title, revision/time, draft status and actual archive availability. Historical choices come only from the existing current-authorised bounded revision history. Resolve unsaved edits and pending mutations before starting a new export; do not auto-save or alter links. Use a deliberate download action, keeping current editable draft and learning progress unchanged.

Qualification must cover read/manage without export, export without read, current grant/membership/revision restrictions before replay, tenant/principal/operation mismatch, exact historical edition and unavailable archives, private metadata exclusion, byte/hash equality on retry, atomic audit/receipt failure, size limits and safe filenames/headers. Add actual native role/immutability checks and browser download/recovery/mobile cases. Keep implementation tests separate from formal specified-case execution, hosted gates and nonprofit UAT.

## Reviewed first implementation boundary

Independent source review narrows the first format to JSON and maps the separate export capability to the existing TENANT_ADMIN, MEL_ADMIN and PROGRAMME_MANAGER responsibilities. A new immutable registered manifest fingerprint is required; its label alone is not its identity. Existing organisations and ordinary members gain no automatic permission. The reviewed access-extension and ordinary role-assignment decisions still apply.

The proposed endpoint is `POST /v1/tenants/{tenant_id}/ai-enablement/plans/{object_id}/revisions/{revision_id}/exports`. Its closed request contains the operation ID, format `JSON`, restriction `INTERNAL_SELF` and explicit acknowledgement. The response carries the exact original UTF-8 content string and an immutable manifest. The browser must verify the original bytes and digest rather than parse and reserialize the package. Each deliberate local download replays the original issuance through current authority before producing a fresh object URL.

Separate insert-only issuance and byte tables retain the exact bytes. The issuance ID can identify its own AuditEvent, with a typed foreign key to that exact audit revision and the exact plan revision. A deferred consistency guard seals the audit, register, bytes and receipt in one transaction. A permanent operation identity survives ordinary receipt cleanup; an expired issuance cannot silently generate a new artifact under its old operation. The seven-day server replay boundary does not stop someone opening their already downloaded file. Audit establishes preparation and commit, not successful network delivery or local filesystem saving.

Current privacy planning covers membership and named Evidence/ImportJob records; it does not inventory AI plans or exported copies. The first slice therefore requires a narrow guard refusing removal of a parent AI-plan payload while retained issued bytes exist. It does not add an unreviewed privacy selector, retention duration, child-erasure operation or backup-deletion claim. Those remain an explicit operated-policy and implementation boundary.

The design was initially preserved as an unregistered draft at checkpoint0.33. Local candidate0.34 now registers the dedicated endpoint, interface, frozen eleven-definition public-data schema and additive0040. Its21 focused registered native SQL groups pass. The immutable draft archive retains earlier attempts and their narrower observations. Unknown stored metadata and private programme/advice/proof fields remain excluded from the export allowlist at every nesting level. Current qualification, permanent100-slot storage, fixed168-hour replay and operated-policy limitations are recorded in the current release; this design note does not establish formal portability acceptance.
