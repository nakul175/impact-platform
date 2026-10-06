# Build 0.30 — nonprofit AI solution discovery

## Delivered

The product catalogue now has eight real solutions with provider names, comparable deployment and commercial-model descriptions, source links, a check date, explicit uncertainties and questions for data review. It covers ChatGPT Business, Claude Team, Microsoft 365 Copilot, Gemini for Google Workspace, Gemini Notebook (NotebookLM), DeepL, Canva Magic Studio and Microsoft Foundry (Azure AI Foundry). The stable IDs preserve references if a provider changes a display name.

The use-case associations are editorial pilot ideas linked to the existing nonprofit use-case library. They do not assert that a vendor meets an organisation's requirements, that a model is accurate, or that a purchase is approved. The comparison prompts require the same acceptance example, total-cost quote, exact plan's data terms, nonprofit eligibility, human review and exit checks.

## Contract and persistence

`ai_solutions_catalog.solutions_catalog()` returns an isolated JSON-safe snapshot with `content_version`, `checked_on`, `explanation`, `solutions` and `comparison_criteria`. Current content is `nonprofit-solutions-2026-10-05.1`, checked on 5 October 2026. Each solution has string comparison fields, existing `use_case_ids`, `source_urls` containing labelled official HTTPS links, `verification_notes` and `data_review_questions`.

`CONTENT_VERSION` and immutable `SOLUTION_IDS` support server validation and version pinning. `validate_solution_ids(value)` accepts an ordered list of one to four distinct known string IDs and returns a copy. It refuses empty, duplicate, unknown, whitespace-altered and non-string selectors. An optional empty selection must be handled explicitly by the caller before this helper.

Reading this catalogue makes no provider call and stores no organisation data. The integrator exposes it under the existing AI enablement read capability; this slice adds no access capability, tenant table or migration.

## Evidence and limits

The catalogue was compiled from official provider sources on 5 October 2026. It deliberately does not contain live or numeric purchase prices: the final price, tax, country-specific offer and the user's eligibility remain unverified. An advertised discount or grant is a starting point for application, not an entitlement granted by this platform.

Important distinctions are visible in the comparison data:

- [ChatGPT Business](https://help.openai.com/en/articles/8792828-chatgpt-business-overview) does not include API usage. The [nonprofit announcement](https://openai.com/index/introducing-openai-for-nonprofits/) has a February 2026 update that replaces its older discount figures.
- [Claude's nonprofit programme](https://www.anthropic.com/news/claude-for-nonprofits) describes Team and Enterprise offers; a Team offer is not treated as an API entitlement.
- [Microsoft's nonprofit offerings](https://learn.microsoft.com/en-us/industry/nonprofit/microsoft-for-nonprofits/nonprofit-offerings-products) state that Copilot requires Microsoft 365 licensing and that offers vary by region.
- [Google's nonprofit feature table](https://support.google.com/nonprofits/answer/16345471?hl=en) distinguishes Gemini app features from Gemini assistance inside Workspace apps. [Enterprise notebook APIs](https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks) do not establish an API entitlement for nonprofit Workspace accounts.
- [Gemini Notebook source citations](https://support.google.com/gemininotebook/answer/16179559?hl=en) support staff review; they are not an accuracy guarantee.
- [DeepL API documentation](https://support.deepl.com/hc/en-us/articles/9773914250012-About-DeepL-API) confirms an integration API. No nonprofit-specific benefit was verified in the reviewed sources.
- [Canva's nonprofit programme](https://www.canva.com/nonprofits/) and [Magic Studio announcement](https://www.canva.com/newsroom/news/magic-studio/) establish discovery information; unlimited AI use and Magic Studio API access are not assumed.
- [Microsoft Foundry documentation](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry) confirms a developer platform. An advertised Azure grant is not treated as coverage for every service or model.

There is no paid placement, vendor ranking, benchmark, supplier onboarding, purchase execution, quote request sent to vendors or automatic data-sharing integration. Selecting a shortlist is a planning action only. Provider pages can change; refresh and date the content before depending on an offer in procurement.

## Reproduction

Run `.venv/bin/python -m pytest -q qualification/test_ai_solutions_catalog.py` with `PYTHONPATH=apps/api`. The tests exercise JSON-safe versioning, official source structure, existing use-case references, uncertain entitlements, isolated snapshots and strict shortlist validation. They run without a database or vendor service request.

Focused result on this slice: 29 tests passed; Ruff lint and formatting passed. Integrated API, browser and native qualification remain the integrator's responsibility.

## Integration notes

Files owned by this slice are `apps/api/impact_api/ai_solutions_catalog.py`, `qualification/test_ai_solutions_catalog.py` and this note. Root integration owns the API contract, authorised route, browser UI, runner inclusion and shared documentation. Suggested product wording: “Compare real AI tools using dated provider sources, then save a shortlist for a reviewed pilot.” No existing requirement is proposed as accepted or moved by this slice alone. Native access and browser evidence belong to the integrated run.
