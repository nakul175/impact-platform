# Release 0.49 coding candidate: source-backed opportunity mapping

US-MP-01 / APL-376 (frozen Gherkin SHA-256 `c36936aedf7f418f8fddb2089019766001200e7ab3ba2c716a6d82d1d5a59f21`) adds a read-only map from an exact completed diagnosis revision to a pinned pattern-library edition. Each matched opportunity carries at least one stable, public, source-backed real-world example and an explicit match basis. The server never accepts client-authored pattern or example claims.

The mapper is deterministic and fail-closed. It labels the result `INCOMPLETE` when any priority problem has no verified library match; it does not add a generic fallback to manufacture coverage. A malformed library refuses the request. Exact historical diagnosis revisions remain addressable through `revision_id`, subject to the diagnosis's existing tenant, authority and evidence checks.

The completed-diagnosis view can request and display the map, its edition, completeness, unmapped count, match basis and linked examples. Examples are context only: they do not assert suitability, predicted results, endorsement, procurement approval or deployment authority.

Pinned public example sources were checked on 12 October 2026: UNICEF's U-Report COVID-19 chatbot, the World Bank's Edo learning pilot, and WFP's Enterprise Deduplication and emergency imagery accounts. Their claims remain attributed to those publishers.

This is a coding-only candidate. Tests, CI, merge, staging deployment and owner acceptance are intentionally deferred to the combined qualification phase.
