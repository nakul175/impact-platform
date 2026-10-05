# Nonprofit AI adoption tool

Build 0.30.0 in review, schema 35, domain API 1.21.0 (240 implemented operations), platform API 1.9.0 unchanged. This extends the foundation on the same review branch; it is not merged or deployed. The original 307-requirement acceptance ledger remains unchanged.

## Delivered product workflow

1. Describe the organisation's goal and assess readiness using transparent deterministic rules.
2. Search eight real AI products by name/category, inspect official source links and checked date, compare up to four products and retain a shortlist. The directory distinguishes subscription products from developer APIs and flags unknown costs or eligibility. It contains editorial use-case mappings rather than endorsed supplier rankings.
3. Work through twelve short lessons across foundations, pilot design and procurement. Each contains teaching material, a synthetic practice exercise and a knowledge self-check. Saved completion is self-recorded; it does not establish competency or award a certification.
4. Prepare an editable procurement brief: requirements, permitted data, budget assumptions and vendor questions. These are drafts, not quotes or approved purchases.
5. Set a pilot success measure and record five actions: define the goal, trial with synthetic material, human review, staff training and outcome review. A checked action does not constitute platform approval.
6. Save named organisation-shared adoption plans and reopen them after reload. The goal, shortlist, learning progress, procurement notes and pilot checklist persist together in immutable revisions.

OpenAI advisory remains a separate, consented action with the foundation's sealed replay and spending limits. The selected project currently reports exhausted API credits; no successful live generation is claimed. Every other step above operates without provider calls.

## Permissions and persistence

GET `ai-enablement/solutions`, GET `ai-enablement/plans` and GET `ai-enablement/plans/{object_id}` use `ai.enablement.read`. POST plans and PUT the selected plan require the separate `ai.enablement.manage` capability, limited to the existing tenant administrator, MEL administrator and programme manager templates. A manager also needs current read access. Existing tenant ceilings are never widened automatically.

Migration 0035 adds only the `AIAdoptionPlan` object kind. Drafts use the existing forced-RLS registry, append-only revision history, audit/outbox and operation receipts. Each save happens under the tenant and operation locks. Updates require the exact expected revision; an outdated save conflicts. Identical retries replay the original receipt only after current access checks; changed payloads under the same operation ID conflict. Client input cannot set state, author, content versions or an approval. Reads and pagination respect current tenant/scope, and cursors bind to principal, tenant, route and visibility. No total count is returned. Plans are bounded to 1,000 per tenant and four selected solutions per plan.

Plans are shared with organisation staff who hold the relevant read scope. Briefs are organisation working notes stored in ordinary platform revisions, not private journals. Do not enter beneficiary information or credentials. Catalogue versions are pinned on saves; preserve lesson keys when changing future content. Historical revisions cannot be edited, and no deletion/archiving screen is included in this increment.

## Reuse and limits

The describe–diagnose–procure–deploy–run journey and explicit milestones follow the user's MSME product direction. Its factory data, commercial fee model, supplier contracts and payment handling are not copied into nonprofit decisions. Earlier Mercy Corps reuse remains the approved-logframe export and twelve arithmetic/calendar regression scenarios; no upstream Django runtime is added.

This is a discovery, capacity and adoption-planning product. Supplier onboarding, live quotes, purchase transactions, payments, human advisory booking and automated production deployment remain future integrations. Tool listings are not supplier certifications. Source-backed features and offers still need confirmation for the actual plan, region, contract and intended use. The tool does not make legal, medical, funding or official impact decisions.

## Verification

Focused tests, full local qualification and browser evidence are recorded after integration below. Native PostgreSQL role/concurrency, live identity and deployment-container gates still require hosted qualification before an owner-approved merge. Local browser verification uses installed Chrome on macOS with synthetic accounts; it is separate from the required Linux CI run. No tests are weakened and no requirement is promoted to accepted.

## Integration notes

Five operations extend the prior foundation's three, one separate management capability and one additive registry migration. Root integrates contracts, route wiring, fixture/profile generation, test entry points and shared state documents. Source catalogue, adoption-plan and product-UI notes carry component evidence. New surfaces retain tenant isolation, official arithmetic, independent approval and current authority. No staging configuration or credentials are changed by this branch.

Final integrated local test run: **1,101 passed, 7 failed, 76 skipped, 1 deselected** in 164.29 seconds. All seven failures exactly match the unchanged Mac operations baseline; all 65 new adoption-product test cases passed. Lint and TypeScript/Vite build passed. Evidence: `docs/evidence/nonprofit-ai-adoption-local-suite.xml` and `docs/evidence/nonprofit-ai-adoption-local-summary.json`. Native role/concurrency and hosted identity/container gates remain pending; this is not a green release gate.

Final browser verification: **10 scenarios passed** in installed Chrome on macOS against a fresh synthetic local API/database. Covers search/filter, readable one/four-tool comparison on desktop/mobile, lessons and self-checks, procurement/pilot edits, durable save/reload, exact retry after a lost response, preservation of newer edits, stale-head conflict, read-only access and zero disabled-provider requests. Automated axe scans of all four sections and the shared discard dialog found no serious or critical WCAG-tagged issues; no exceptions. Visual inspection corrected a narrow comparison column and source-link touch targets. This does not replace the hosted Linux browser/native/identity/container release gates. Evidence: `docs/evidence/ai-enablement-browser-tests.json`.
