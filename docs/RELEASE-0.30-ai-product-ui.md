# Nonprofit AI adoption tool — functional workspace

Build 0.30 slice; no independent version bump, migration or requirement promotion. Root integration supplies the solution catalogue and revisioned adoption-plan API. This records implemented product code and local build checks, not a deployed product run.

## Delivered

- Search and category filters over the source-backed tool directory, with the source review date, direct published-source links, stated commercial models and nonprofit eligibility/offer uncertainty.
- A shortlist of up to four tools and a side-by-side comparison of provider, category, deployment, commercial model, nonprofit offer, API availability, source links and data questions. No supplier score or purchase action.
- Named, organisation-shared adoption plans containing the organisation brief, shortlist, completed learning steps, procurement draft, pilot success measure and five self-recorded pilot actions. Authorised staff can open existing plans. Only `ai.enablement.manage` holders can save, update or record completion.
- Practical learning lessons, synthetic exercises, local self-check feedback and self-recorded progress. Progress does not claim certification.
- An editable procurement brief populated deterministically from the organisation brief, selected tools and shared supplier questions. The user reviews requirements, data boundaries, budget/offer checks and supplier questions before use.
- A pilot tracker for defining the goal, trying synthetic material, human review, staff training and outcome review.
- Existing advisory consent, provider availability, separate advisory permission and stable retry guards are preserved. No protected programme or participant records are joined into the tool.

## Contract and persistence

The workspace reads `GET ai-enablement/solutions`, lists `GET ai-enablement/plans?limit=50` with signed-cursor continuation, and opens `GET ai-enablement/plans/{object_id}`. Create uses `POST ai-enablement/plans` with `{operation_id,data}`; update uses `PUT ai-enablement/plans/{object_id}` with `{operation_id,expected_revision,data}`. The save DTO is explicit and excludes server-owned `content_versions`.

New intents receive random operation IDs. Ambiguous network/transient failures retain the exact route/body for retry. Edits made after a save began remain in the view and remain unsaved when the earlier receipt returns. A stale `CONFLICT_VERSION` releases the retry intent, preserves local edits, and lets the user open the current saved revision without overwriting it. Switching or creating plans is blocked while an ambiguous save needs resolution. Tenant changes abort fetches and invalidate every pending response. An edit while an existing plan is opening prevents the delayed response from replacing that edit.

Drafts and selections are held in memory until an authorised user saves through the existing authenticated API. There is no browser-local persistence. Saved plans are draft records for authorised organisation staff, with an organisation-level data warning.

## Limits

The directory is a source-backed starting point, not a supplier marketplace transaction system. There are no bookings, orders, live prices, claims of nonprofit eligibility, verified supplier performance rankings, supplier registration or autonomous purchasing. Product terms may change after the displayed review date.

Lesson checks give local feedback. Completion and pilot progress are self-recorded rather than reviewed evidence or an approval. Plan updates use optimistic revision checks; there is no merge editor for concurrent edits. Opening another plan after unsaved edits requires the user to confirm discarding them in the application's shared, focus-contained Dialog; cancelling keeps the edits intact.

AI advisory generation still depends on separately enabled server configuration, explicit consent, current permission and provider credits. Readiness assessment, directory comparison, lessons, draft preparation and plan saves work without a model call.

## Reproduction

Local checks on the component: Prettier formatting, browser script syntax, TypeScript type-check and Vite production build pass. The existing large-bundle warning remains. No browser or database suite was run by this parallel builder.

`tools/browser/ai-enablement-check.mjs` now contains ten integrated scenarios: directory/source honesty; deterministic assessment and stale-result removal; search/category/max-four comparison; practical lesson/procurement/pilot interaction; lost-response exact save retry while preserving newer edits; reload restoring every plan area; stale-head protection; provider-disabled/no-request and desktop/mobile layout; automated accessibility of all four product sections and discard Dialog; and existing `other_tenant` read-only visibility. The root integrator runs these against the actual API. Optional `IMPACT_BROWSER_EXECUTABLE` selects an installed compatible Chromium browser; the default Linux qualification executable is unchanged. Desktop, comparison and mobile screenshots are viewport crops under `IMPACT_TEST_LOCAL`; failure screenshots retain the whole page. Results and detailed automated WCAG findings remain in `docs/evidence/ai-enablement-browser-tests.json`.

Visual QA after the first nine checks found that the global table action-column width collapsed the last comparison product. The fix is scoped to `.ai-comparison`: product headers use automatic widths and the table reserves 240 px per selected product. Browser checks now verify readable widths for one and four products on desktop and mobile, bounded heading/row heights and no page overflow. No global table rules changed. New colour values are named `--ai-*` tokens in `:root`, used only in the AI stylesheet.

## Integration notes

Files owned by this slice: `apps/web/src/AIEnablement.tsx`, new `apps/web/src/AIAdoptionWorkspace.tsx`, scoped `apps/web/src/ai-enablement.css`, `tools/browser/ai-enablement-check.mjs`, and this release note. No shared documents, contracts, access fixtures, versions or migrations were edited.

Recommended shared-document wording: nonprofit AI enablement now has a functional directory/comparison, self-paced lessons and revisioned shared adoption plan with procurement/pilot tracking; marketplace transactions remain future work. Browser evidence must be reported from the integrated run, with the configured browser name. No original requirement is proposed for acceptance or promotion by this slice.
