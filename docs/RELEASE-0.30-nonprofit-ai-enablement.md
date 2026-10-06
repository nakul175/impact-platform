# Nonprofit AI enablement foundation

Local proposed build 0.30.0; schema 35; domain API 1.21.0 (+8 operations); platform API 1.9.0 unchanged. Not merged or deployed. Original 307-requirement acceptance ledger unchanged.

## Delivered

An AI enablement workspace alongside the governed impact platform. Staff describe a goal and their team's data readiness and AI experience, receive a transparent rule-based assessment, explore eight editorial use-case examples and three learning paths, and use seven supplier/procurement criteria. Examples identify prerequisites, acceptance checks and human decision owners. They are editorial assumptions, not validated demand, vendor endorsements or promised savings.

Separately authorised staff can request an OpenAI advisory draft after explicit consent. Only the submitted brief and its assessment are sent; no platform records, participant data or credentials are retrieved for the prompt. Outputs remain proposals. They cannot alter official results, grant authority, award procurement or move money.

The journey adapts the sponsor's MSME repository concept: describe, diagnose, procure, deploy and run. Its manufacturing study, synthetic providers, fees and company records are not imported. Existing impact measurement provides a future way to track adoption outcomes; this increment does not automatically measure them.

Twelve Mercy Corps-inspired regression scenarios exercise existing arithmetic and calendar semantics. No upstream Django runtime is added. See RELEASE-0.30-reuse-scenarios.md for provenance and limits.

## Contract and persistence

- GET `ai-enablement/catalog` and POST `ai-enablement/assessment`: `ai.enablement.read`.
- POST `ai-enablement/advisory`: `ai.advisory.request` plus ordinary enablement read access; closed request with operation UUID, profile and consent.
- Migration 0034 introduces tenant-keyed, forced-RLS, insert-only request/result registers. Requests reserve their budget under the tenant advisory lock. Generated text and its assessment are AES-GCM sealed with a dedicated derivation/context of the delivery keyring. Briefs are not stored in clear text. Audit/outbox records cover reservations and completed/failed requests.
- Identical retries replay the sealed original after checking current access, including after editorial content changes. Changed payloads conflict; requests already in flight do not regenerate. Provider failures are closed and never automatically retried. An interrupted call or loss of authority can leave an in-flight claim requiring operator investigation; it never spends twice automatically.
- At most three reserved requests per tenant in any rolling 24-hour window, including failed attempts. Each provider response is bounded to 2048 generated tokens and 12000 returned characters, with a 45-second timeout, no redirects, no tools and no automatic retries.

## Configuration and reproduction

Advisory is disabled by default. The API uses `OPENAI_API_KEY`, `IMPACT_AI_ENABLED=1` and optionally `IMPACT_AI_MODEL` (default `gpt-5-mini`). Development alone can read the approved ignored `.env.local`; test/CI/staging do not read it. A delivery keyring is also required. The local key has not been installed on staging. Only the API container receives provider configuration.

New capabilities change the initial-access profile hash. Existing tenant ceilings require an independently reviewed widening before grants are possible; do not widen them automatically. Existing pending initial-access requests must be re-proposed with the current hash.

Live provider check on 5 October: key/model access returned HTTP 200, but generation returned HTTP 429 with `credit_balance_exhausted` / `insufficient_quota`. No live generation is qualified; the owner must fund the selected project in [OpenAI billing](https://platform.openai.com/settings/organization/billing). No further live generation calls were made after diagnosis.

Local qualification uses synthetic provider responses and a disposable database. The new `ai-enablement-browser` group covers readiness, capacity/procurement panels, unavailable advisory and mobile layout; it requires the Linux browser runner. Native login-role tests verify the new table fences and privileges. Full hosted qualification remains required before merge.

Responses uses `store:false` to disable response application-state storage; this does not itself establish zero data retention. See the [official Responses guide](https://developers.openai.com/api/docs/guides/migrate-to-responses) and [data controls](https://developers.openai.com/api/docs/guides/your-data). Do not include personal or beneficiary data in a brief. Retiring a delivery key can make cached drafts sealed under it unreadable; preserve applicable grace keys when replay is required.

## Original foundation limits, superseded where stated

The subsequent [working adoption-tool increment](RELEASE-0.30-ai-adoption-tool.md) delivers saved drafts, source-backed tool comparison, practical lessons/progress, procurement briefs and pilot checklists. The paragraph below records the initial foundation only; purchase/booking/payment integrations remain absent.

### Initial slice limits

There is no real supplier registry, live vendor comparison, quote collection, pooled purchase, payment, course enrolment, human advisory booking or deployment tracking yet. No real prices, certifications, ROI or supplier rankings are claimed. Readiness profiles are not saved as organisation records. The marketplace panel states these limits.

Next: independently reviewed organisation profiles and adoption decisions; evidenced provider/solution registry with comparable requirements and total-cost quotes; capacity programmes with practical competency evidence; governed procurement and delivery milestones; advisory cases with named human reviewers; adoption outcomes linked to the impact platform. Revenue policy, first pilot cohort and marketplace operator responsibilities remain owner decisions. Do not import the MSME fee model as a nonprofit decision.

## Integration notes

One new screen, three API operations, two capabilities, one additive migration and one browser group. New content, provider and persistence tests are synthetic. Existing arithmetic, identity, independence and official snapshots remain authoritative. No original requirement is promoted to accepted, and this foundation is not a production marketplace.

Local verification: **1,036 passed, 7 failed, 75 skipped, 1 deselected**. All seven failures match the unchanged Mac operations baseline; 72 new feature cases passed. Lint and web build passed. Hosted browser, identity, native PostgreSQL and container gates remain pending. Evidence: `docs/evidence/nonprofit-ai-local-suite.xml` and `docs/evidence/nonprofit-ai-local-summary.json`. Live generation remains blocked by OpenAI project credits (`credit_balance_exhausted`).
