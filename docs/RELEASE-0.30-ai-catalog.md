# Proposed 0.30 nonprofit AI catalogue and assessment

## Delivered

A pure, versioned editorial catalogue covers the describe → assess → procure → pilot/deploy → operate journey. Eight examples cover data foundations, communications, document search, education, public health communications, livelihoods, environment and narratives around approved impact results. Three learning paths and seven procurement comparison criteria help teams plan capacity and ask providers comparable questions.

The assessment accepts exactly six self-reported profile fields and returns deterministic recommendations with explicit relevance reasons, unmet prerequisites, human approval needs and readiness limitations. English keyword matching orders examples, prerequisites break ties, and stable identifiers make the result reproducible. Sector examples are scoped; sensitive-data use needs data-owner review, and health communications need a qualified domain reviewer. AI does not generate official arithmetic or authorise spending, disclosure or deployment.

The MSME repository's five-stage journey and transparent-rule approach informed the structure. No manufacturing study material, benefit estimates, pricing or code was copied. All nonprofit content is editorial and needs practitioner validation. Catalogue `content_version` is `nonprofit-2026-10-05.1`; it must change whenever content or ranking semantics change.

## Contract and persistence

`catalog()` and `assess(profile)` are pure Python functions. They make no network calls and persist nothing. The schema version is `1.0`. The integrator owns authenticated routes, API contracts and UI wiring. Invalid values, missing fields and unknown fields raise `ValueError`; boundary types reject booleans masquerading as integers. Returned catalogue structures are isolated copies.

`marketplace_status` explicitly says `NOT_CONNECTED` with no vendor listings. Procurement content consists of questions and acceptance criteria, not endorsements, live quotes, legal advice or purchasing functions.

## Limits

Self-report is not verified capability or certification. No quantified readiness percentage, ROI, savings, vendor quality or cost estimates are fabricated. Matching is English keyword based and can miss meaning. There is no provider marketplace, procurement transaction, operational deployment, capacity certification or practitioner validation in this slice. No retained MEL requirement becomes accepted from these unit tests.

## Reproduction

`PYTHONPATH=apps/api .venv/bin/python -m pytest qualification/test_ai_enablement_catalog.py -q`

Focused result: **29 passed**, covering catalogue integrity, isolated copies, stable ranking, missing prerequisites, sensitive-data review, all four sector examples, health review, untrusted goal text, closed profile validation and boundary values. Focused lint passed for both Python files. This is pure-function evidence, not route authority or hosted qualification evidence.

## Integration notes

Files owned: `apps/api/impact_api/ai_enablement_catalog.py`, `qualification/test_ai_enablement_catalog.py`, this note. No schema migration, version bump, shared documentation, provider call, commit, push or paid CI in this slice. Add the test file to the pure unit target; expose catalogue and assessment only under existing tenant authority conventions. Render provenance and limitations visibly. Route validation should preserve the closed six-field profile. Catch `ValueError` as validation failure. Catalogue and assessment shapes were sent to the integrator and UI builder.
