# Nonprofit AI Procurement Draft Preview — Proposed Development Supplement

Private next-release proposal, 6 October 2026. Not registered, deployed or accepted. The frozen 0.35 candidate, its sources and its broad qualification remain separate. The product patch is `b3455058a0b61d3ceff6a73f0927ba0c26afc2b978749ef2f02283b361cb841e`; its model is `1718d6fec60ba23d3aa6fafe35f49eb0ffc24b47138c60ae90d1b18cf1ffbe09`. Integrate only after the integrator saves the qualified 0.35 checkpoint and reviews the final proposal.

## Functional boundary and traceability

This proposal changes the existing local procurement-fill interaction to preview and deliberate replacement. A manager reviews the same four existing strings before changing requirements, data boundary, budget notes and supplier questions. Preview and cancellation leave the draft and saved plan unchanged. Applying replaces all four procurement fields together in the local draft, preserving other plan fields. The user still chooses the existing Save action; the server independently authorises it.

| Existing requirement | Bounded contribution                                                                                                                                                          | Existing design reference                                                                                          | Verification boundary                                                                                                                                  |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| FR-NPA-013           | Preview the current deterministic procurement copy; explicit replacement of four existing note fields; ordinary plan save remains separate                                    | `02-FSD.md#procurement-briefs`, `04-LLD.md#current-input-schema-and-validation` and WF-NPA-006 in `07-WIREFRAMES-AND-JOURNEYS.md` | Literal four-string and preservation checks; proposed actual save/reopen/cancel tests; no request issuance, supplier quote, award or approval          |
| FR-NPA-039           | Refuse a stale confirmation after exact context/head/profile/catalog/shortlist/draft or observed authority/pending-state changes; retain normal current-authority save/replay | `02-FSD.md#current-authority-on-exact-retries`, existing authority/replay sections of `04-LLD.md`                  | Pure invalidation checks establish client-model behavior; actual current-management refusal and exact ambiguous-save replay must run after integration |
| FR-NPA-028           | Named preview, understandable replacement warning, explicit cancel, keyboard actions and bounded mobile layout                                                                | `02-FSD.md#accessible-and-understandable-experience`, existing WF-NPA-006 journey                                  | Private prototype scans and proposed actual 1440/390/320 checks; automated results do not replace manual assistive-technology or user evaluation       |

These links supplement the existing FSD/HLD/LLD and wireframe baseline. They do not change the 40 nonprofit requirements, 108 baseline cases or 307 core requirement acceptance. The proposed next-release designation does not establish an accepted requirement or an operated procurement service.

## FSD supplement

The current manager sees **Prepare a procurement draft** and **Preview draft from brief and shortlist**. The action requires a nonblank goal, valid bounded current procurement values, the current management hint and no pending saved-plan/evidence/advice/export action. It prepares no provider output. A preview names the loaded catalogue and tool-directory editions and shows the existing four strings.

If any procurement field contains text, including whitespace, the preview explicitly says that applying replaces all four fields and keeps other plan fields. **Replace these four draft fields** applies only while the confirmation still matches the exact current source. **Keep my procurement fields unchanged** discards the confirmation. Neither action creates a receipt, sends anything, approves a purchase or saves automatically.

The confirmation becomes unusable after observed actor/context/session-label changes, a different object or revision, a transition between new and saved work, any full profile or plan edit, current catalogue/criterion or selected-row changes, shortlist order/unavailable IDs, any procurement edit, management loss, pending actions or unavailable canonical context. Observed edit then undo and hint/pending loss then return still require a new preview. The exposed session label is a client context key; it is not proof that two server sessions are unique.

Save continues to use the existing closed request and operation ID. A cached positive hint cannot grant server management authority. If the server refuses the current request or exact retry, ordinary recovery preserves local work and does not silently create a replacement operation.

## HLD supplement

Reuse the existing product workspace and AIAdoptionPlan read/save boundary. `AIProcurementPreviewModel.ts` contains a pure four-field text builder and exact-source confirmation checks. `AIProcurementPreview.tsx` renders the preparation/confirmation state and invokes the existing local edit callback after rechecking the latest source. A narrow Workspace hunk replaces the direct fill button and passes the current source and existing pending-action state; no backend, capability, profile, database, schema, provider, account or deployment resource is introduced.

The proposed parent binds the full selected public directory rows and full serialized plan/profile, rather than only the interpolated names. It preserves the existing full-plan draft-generation counter. The child increments its own irreversible interaction generation on observed input changes, hides a mismatch during render, clears retained confirmation in an effect, and rechecks the latest source at Apply. The parent separately refuses Apply while its current busy reference or pending operation is set. These are client recovery guards; current object-specific authority remains the API's responsibility.

Root-owned Workspace changes must be integrated as a narrow hunk against the then-current parent. Never replace the parent with the earlier whole-file prototype, which can predate other review/starter changes. No change is needed to the public fictional walkthrough, original source-backed tool catalogue or saved-plan public DTO.

## LLD supplement

`ProcurementDraft` remains exactly `requirements`, `data_boundary`, `budget_notes`, `vendor_questions`. Existing JavaScript input limits are 2000/2000/500/2000 UTF-16 code units. The server's existing closed payload validation remains authoritative; this proposal does not redefine its character rules.

`prepareProcurementText(source)` preserves the current fill text verbatim. Requirements contain the profile goal, team size and selected public names in order, falling back to **a supplier to be selected**. The sensitive-data flag selects the exact existing boundary copy. Budget text remains the same qualitative request for total cost and direct supplier eligibility confirmation. Questions preserve current procurement-criterion order followed by each selected tool's data-review-question order. Requirements and questions retain the existing `.slice(0, 2000)` behavior, including a split surrogate at a constructed boundary; this is a compatibility constraint, not a Unicode-quality or server-acceptance claim.

`previewProcurement(source)` returns an exact source binding, a copied four-field `before`, a deterministic `proposed`, and `hasExistingWork`; unusable input returns null. `currentProcurementPreview(source, preview)` recomputes and compares binding/before/proposed. `applyProcurementPreview(source, preview)` returns exactly four fields only for a still-current confirmation. The component rereads its latest source; the parent merges `{ ...previous, procurement: value }` through the existing edit helper. No server-generated fields are constructed or inserted into the draft.

The binding includes tenant-route base, principal selector, exposed session identity label, nullable object/revision, full profile, loaded public catalogue, tool-directory edition, ordered stored shortlist IDs, selected public rows, exact four current fields, full serialized plan/profile, parent generation, interaction generation, current management hint and mutation lock. Binding strings are local comparisons, not cryptographic authentication, signatures or immutable evidence.

## Transient data dictionary

| Transient member               | Source and purpose                                                            | Lifetime and disclosure boundary                                                                         |
| ------------------------------ | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `preview.binding`              | Exact current source comparison string                                        | Component memory only; never a server receipt, provider input, browser-storage record or authority proof |
| `preview.before`               | Copied exact four current draft fields                                        | Used to invalidate replacement after own-work changes; cancellation preserves the original fields        |
| `preview.proposed`             | Existing deterministic four-string output                                     | Preview-only until deliberate Apply; then ordinary local draft until separate Save                       |
| `preview.hasExistingWork`      | Any current field has nonzero string length                                   | Local replacement-warning state; not a hidden-record count                                               |
| `planGeneration`               | Existing irreversible parent draft-change counter                             | Invalidates observed edit/undo; not a persisted revision or audit record                                 |
| `interactionGeneration`        | Child counter on observed source transitions                                  | Invalidates observed hint/pending loss and return; not a database identity                               |
| `selectedSourceKey`, `planKey` | Full current public selected rows and closed local plan/profile serialization | Local stale-source guards; no added participant/advice/export presence fields                            |

The existing server plan dictionary and migration ledger remain unchanged. Preview state has no local/session storage, cookie, new telemetry or new retention policy. Ordinary plan save continues to retain only the existing closed fields under the current archive/authority behavior.

## Wireframe supplement

Within existing WF-NPA-006, retain the four labelled editable note fields and ordinary Save action. Before the fields show:

```text
Prepare a procurement draft
[Preview draft from brief and shortlist]

Procurement draft preview — changed no field and saved nothing
Your procurement fields already contain work.
Applying this preview replaces all four fields; other plan fields are kept.

Pilot requirements: existing prepared text
Data boundary: existing selected boundary text
Budget and nonprofit offer checks: existing request-for-cost text
Questions for suppliers: existing catalogue questions
Current catalogue and tool-directory editions

[Replace these four draft fields] [Keep my procurement fields unchanged]
```

Read-only users see no preparation/replacement controls. Pending state explains waiting; a blank goal refuses preview. Keyboard focus, preview/cancel behavior, readable narrow-screen content and incomplete automated findings require the proposed actual browser checks after the integrated build. The sketch introduces no quote, decision, disclosure, supplier-contact or financial screen.

## Test proposal and proof boundaries

The proposed repo-style checker directly imports the actual TS model with Node type stripping and generates current public inputs through local `catalog()` and `solutions_catalog()` using the existing Python environment, with bytecode writes disabled. It uses independent literal expected four strings rather than executing a duplicated fill implementation. Catalogue editions, ordered criterion IDs, selected actual tool names and all generator/model/checker bytes are bound in its named report.

Its 35 private pure groups port the 28 original model boundaries and add current-generator controls, each exact input-limit boundary, full/split surrogate and newline compatibility, whitespace replacement disclosure and unchanged-source proof. Successful control previews precede invalidation assertions. Synthetic overlong directory wording is explicitly a helper boundary fixture, not an actual published tool or server-valid selection. The parent-merge example verifies the narrow returned object; it cannot prove React callback wiring, server authorization or persistence.

Add only one always-on pure prerequisite to the existing Makefile browser recipe. The proposed registration paths are `apps/web/src/AIProcurementPreviewModel.ts`, `tools/browser/ai-procurement-preview-model-check.mjs`, and a separate named `sprint-0.36-procurement-preview-model-tests.json`; the integrator chooses final release naming. Run against the local generators, not a stale copied fixture. Current editions changing must prompt deliberate expectation review, never silently regenerate expected output to match the implementation.

Content owns the separate proposed actual browser adaptation. It preserves all ten original groups and fifty original assertion calls, adds exact preview/cancel/apply preservation, normal save/reopen, current-authority refusal, same-valued new revision, ambiguous exact replay, edit/undo and keyboard/mobile checks. Its actual API/browser/database execution is **NOT_RUN** until integration and a coordinated fresh qualification lease. Private 28 original pure /12 synthetic composed UI /two prototype axe scopes remain historical proposal proof. New pure groups are not added to original acceptance totals and do not establish procurement, UAT, hosted or full security acceptance.

## Integration and remaining decisions

After the clean 0.35 checkpoint, review the exact model/component and narrow parent hunk; copy the reviewed new modules, add the proposed always-on model prerequisite, regenerate the current build and run the strict pure plus content-owned actual browser checks. Verify the original app and public walkthrough still use their existing handlers and static graph. Then perform the integrator's complete source-bound release checks and save a distinct checkpoint.

No new owner business decision is needed for this bounded client replacement. ProcurementRequest issuance, independent decisions, supplier certification/eligibility, financial thresholds, paid provider calls and operated retention remain outside this proposal and retain their existing unresolved target status.
