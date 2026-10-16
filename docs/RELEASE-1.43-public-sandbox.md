# Disposable public workspace demonstration

## Delivered

A separate `/sandbox.html` entry, linked from the shared workspace's sign-in page, opens without an account. Twenty fictional sections cover portfolio, measurement setup and observations, planning, dashboards, forms, rounds, import plans, evidence notes, change requests, period previews, work, review candidates, result notes, report drafts, evaluation, finance, AI practice, access proposals and workspace setting drafts.

Each section has an invented example, search, bounded local draft creation and editing, a local history, and clearly labelled simulated submission/review transitions. Editing a simulated reviewed item returns it to draft. Reset requires an explicit discard action. Every tab starts independently; refreshing discards changes. There is no browser storage, cookie, authenticated identity, domain request, external provider or shared database connection in this entry.

## Contract and persistence

The only new server route serves bundled static HTML, without resolving an identity or opening a database transaction. Its CSP denies network connections, form submissions, frames, images and external scripts. React renders invented and entered text as text. All state lives in component memory; the model bounds a section to 50 drafts and title/notes to 120/2,000 characters. Shared application authentication, tenant authorization, CSRF, natural-person independence, history and migrations are unchanged. No new domain API operation or migration is registered. Release candidate build is 1.43.1; domain/platform API versions remain unchanged.

## Limits

This is a standalone interface simulation, not the authenticated application running anonymously. The sections use generic draft interactions, not the full domain-specific workflows, uploads, actual imports, charts, official calculations, grants, AI generation, export bytes or real approval/publication. Simulated reviews are not human decisions. It does not establish acceptance of any of the 56 reviewed stories or add a story to the delivery count. Only invented text belongs in this disposable public page.

## Reproduction and verification

- `node --test tools/browser/public-sandbox-model.test.mjs`: actual model tests for isolation, review invalidation, validation, bounded drafts and reset.
- `.venv/bin/python -m pytest qualification/test_public_sandbox_unit.py qualification/test_version_unit.py`: executes the model and validates release versions.
- `.venv/bin/python scripts/run.py public-sandbox-browser`: actual anonymous browser checks of all sections, create/edit/search/review/reset, escaped text, reload and same-context tab isolation, no cookies/storage/API requests, existing anonymous API refusals, landing entry and mobile layout.
- `npm run build --prefix apps/web`: TypeScript and bundled multi-entry web build.

The initial browser run failed to locate the populated notes field through its implicit nested label. Inputs now use explicit IDs and labels; no assertion was removed. The provisional build number 1.43.0 collided with an existing historical contract version in the runtime-version guard; the candidate uses 1.43.1 without editing that contract or weakening its test. Failed preparation receipts remain outside Git alongside the successful source-bound evidence. Final local evidence: 4 actual model cases; 8 focused Python checks; full unit suite 1,543 passed and62skipped; 7 actual anonymous browser groups passed with stable source hashes and zero page errors. [Raw browser receipt](evidence/candidate-1.43/public-sandbox-browser.json) and [separate source/evidence self-review](evidence/candidate-1.43/SOURCE-EVIDENCE-REVIEW.json). The first restricted unit run had15failures/2errors because local sockets were forbidden; the approved loopback-enabled run passed. Hosted CI and deployment must be recorded separately after they occur.

## Integration notes

The new browser group is part of `make browser`; the actual model test is part of `make unit`. The checks workflow now installs its existing Node 22 runtime before unit tests, including documentation-only runs, because those tests execute the TypeScript model with built-in type stripping. No fixture, source criteria, applied migration or historical receipt changes. The release security review remains unconfirmed and not passed; CI consistency is not human security signoff. After publication verify the exact tested tree on staging, check the public route and existing anonymous API refusals, and label all results as demonstration checks.
