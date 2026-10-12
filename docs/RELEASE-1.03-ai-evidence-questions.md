# Release 1.03 coding candidate — evidence-based questions

FR-AI-005 / APL-537 adds a reserved evidence-question workspace for Programme Managers. A request names an exact current programme revision, exact current period revision, the fixed selected-governed-results source mode and up to twenty exact `CalculatedResult` revisions. The service rechecks current caller authority and the programme/period binding before reading any result.

The bounded candidate does not perform arithmetic or invent prose claims. It extracts only supported stored result fields, attaches every material claim to the exact object, revision and JSON-pointer location, and exposes missing and contradictory evidence separately. An incomplete scope returns `CLARIFICATION_REQUIRED` without an official-number guess. Any missing, inaccessible or foreign-scope selector returns the same `ABSTAINED` response without confirming a protected resource or emitting a title, quotation or citation.

Migration 0087 adds `EVIDENCE_QUESTION` to the closed policy vocabulary. Current policy validation, runtime gate and policy UI keep it reserved-disabled, so activation requires a later reviewed application change and owner decision. No provider call, new arithmetic, merge, deployment or spend is introduced. Tests and CI remain deferred by owner request.
