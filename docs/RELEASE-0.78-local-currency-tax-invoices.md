# Release 0.78.0 candidate — local-currency tax invoices

## Delivered

US-CM-08 / APL-608 adds a tenant billing-market profile and explicit invoice issuance. India is the launch market with INR and GST. An invoice cannot issue unless its currency matches an active configured market, contains positive line value and carries the market's positive tax snapshot.

## Contract and persistence

`POST /v1/tenants/{tenant_id}/billing-profile` selects an already governed active market. `POST /v1/tenants/{tenant_id}/commercial-invoices/{invoice_id}/actions/issue` calculates exact subtotal, tax and total under the tenant lock and pins the tax snapshot. `GET /v1/tenants/{tenant_id}/commercial-invoices/{invoice_id}` exposes that issued snapshot. Schema 70 adds the market catalogue, forced-RLS tenant profile and issued-invoice fields; earlier migrations remain byte-exact.

## Limits

Only India/INR/GST is registered at launch. A later market requires an additive governed catalogue change and matching local-price inputs; this candidate does not invent exchange rates. It does not generate a PDF, file a tax return, collect payment or provide tax/legal advice. Product, finance and tax review remain required.

## Reproduction

This is a coding-only candidate. Contract generation, source formatting, static lint and JSON parsing may be used as source-integrity checks. Tests, CI, merge, staging, owner acceptance and tax review are intentionally deferred to the combined qualification phase.

## Integration notes

Commit this story separately and retain its ledger state as `COMPLETE_CANDIDATE / NOT_RUN_BY_OWNER_REQUEST / NOT_MERGED / NOT_DEPLOYED`. Before release, run migration upgrade and native RLS/race/replay checks, affected API tests, the full four-job candidate CI set, independent finance/tax review and owner merge/deployment gates.
