# Proposed AI enablement workspace — build 0.30 slice

## Delivered

A tenant workspace presents the nonprofit AI adoption journey, an editable organisation-level brief, deterministic readiness assessment, candidate pilots, capacity-building paths and supplier comparison questions. A separately authorised action requests an AI advisory draft. Sensitive records are excluded from the brief instructions. Results are explicitly drafts for human review and cannot become official impact arithmetic.

The workspace presents marketplace preparation honestly: no supplier registration, verified listings, prices, ranking or transactions are implemented. Catalogue use cases are editorial examples, not validated customer demand. Profile edits clear earlier results; changing tenant prevents an earlier request response from appearing in the next workspace. The layout uses ordinary headings, labelled form controls, native validation, status announcements and responsive cards.

## Contract and persistence

`AIEnablementPanel` accepts `base`, `request`, `explain`, and `capabilities`, matching the existing tenant shell. `base` is the tenant URL with its trailing slash. It uses:

- `GET ai-enablement/catalog` for the versioned editorial guide.
- `POST ai-enablement/assessment` with `{profile}`; response `{assessment}`.
- `POST ai-enablement/advisory` with `{profile}`; response `{status:'DRAFT',text,assessment,model,disclaimer}`. The advisory body also carries a fresh `operation_id` and explicit `consent:true`. A failed request retains its exact serialized body for a safe retry; a successful request or edited brief starts a new intent.

`ai.enablement.read` permits the workspace and readiness action; `ai.advisory.request` separately reveals the advisory action. The server remains the authority for both capabilities. Advisory generation explicitly tells the user that their organisation brief reaches the configured provider and may incur usage charges. No browser key or provider call exists.

There is no browser persistence or claim that the brief is saved. Advisory drafts are cached encrypted by the server for safe retries and are explicitly not approved or official records. An unchecked consent control requires the user to agree to sending their brief to OpenAI before requesting a draft. The catalogue `advisory_available` flag disables generation and explains unavailable provider configuration. The component reads only the AI guide, never participant data, reports or indicators. Advisory text renders as plain text, with no HTML injection or executable Markdown.

## Limits

This is a development proposal, not production-readiness or accepted-requirement evidence. No live AI request or provider spending was performed for the UI slice. The frontend does not provide training certification, procurement approval, purchase execution, vendor verification or marketplace transactions. Current API constraints and configuration determine whether an advisory request succeeds; refusal and provider errors remain visible.

## Reproduction

The TypeScript check and web build passed locally on 5 October 2026. Prettier passed for the two new frontend files. The existing large-bundle warning remains. A new four-check `tools/browser/ai-enablement-check.mjs` group exercises guide loading, deterministic assessment and stale-result clearing, learning and procurement guidance with advisory disabled and no advisory POST, and 390 px layout. The browser actor is the existing author; the separate read/advisory permission boundary is covered by API qualification rather than widening any role. Browser execution is pending root wiring and hosted Linux qualification; no live provider is called.

## Integration notes

Owned files: `apps/web/src/AIEnablement.tsx`, `apps/web/src/ai-enablement.css`, `tools/browser/ai-enablement-check.mjs`, and this release note. Import `AIEnablementPanel` into the tenant shell and include `ai.enablement.read` in the new area's capability gate. This slice does not change versions, contracts, shared documents or the requirement ledger.

Stable browser selectors: section `AI enablement workspace`; buttons `Assess readiness` and `Request AI advisory draft`; labels `Sector`, `Team size`, `Data readiness`, `AI experience`, and `AI goal`; headings `AI advisory draft`, `Build team capacity`, `Procurement and comparison`, and `Marketplace preparation`. Advisory and readiness state should be tested with synthetic data and a stubbed provider, never a paid live call.

Suggested shared-document wording: “Build 0.30 proposes a nonprofit AI enablement workspace with organisation briefs, deterministic readiness, editorial learning and procurement guidance, and separately authorised AI draft advice. Marketplace transactions and verified vendors remain unavailable.” No requirement movement is proposed by this UI-only slice.
