# Release 0.80.0 candidate — advisor-led option trials

## Delivered

US-AS-01 / APL-357 adds immutable advisor-led trial records for a catalogue-mapped opportunity and solution. A trial lasts from one to 28 days and uses either one currently permitted exact Evidence revision belonging to the organisation or the fixed synthetic sample.

## Contract and persistence

`POST /v1/tenants/{tenant_id}/ai-enablement/trials` requires the existing fresh advisor scoring authority and an active natural-person membership. `GET` lists trials for one opportunity while filtering own-data trials whose Evidence authority is no longer current. Schema 72 pins catalogue edition, dates, data mode/source, success criteria and advisor identities under forced tenant RLS. No update grant or extension action exists.

## Limits

This candidate governs the record and lifecycle for a human advisor-led trial; it does not call a solution provider, upload data, certify an advisor or claim an automated trial outcome. Evidence content is never fetched by the trial service. Sample data is synthetic. Results belong to the separate US-AS-03 story.

## Reproduction

Coding-only source checks may cover formatting, lint, compilation, contract generation, JSON parsing and static release review. Tests, CI, provider execution, merge, staging, privacy review and owner acceptance remain deferred.

## Integration notes

Keep the story in a separate commit and ledger entry. Combined qualification must cover the 28-day boundary, past starts, wrong catalogue mapping, service identities, revoked advisor/evidence authority, cross-tenant selectors, exact retries, list filtering and native RLS before merge or deployment.
