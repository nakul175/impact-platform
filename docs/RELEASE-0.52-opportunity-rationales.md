# Release 0.52 coding candidate: explain every recommendation

US-MP-04 / APL-383 (frozen Gherkin SHA-256 `28b90856172a1b1a3ec1b095eb63a6b1ab53a9e6c313d19181b63447a4da750f`) adds a required plain-language rationale to every mapped opportunity. Each rationale carries closed links to the exact priority-problem ID and the diagnosis `description` and `affected_area` fields used by the deterministic match.

The server derives the rationale and links; it accepts no client-authored recommendation explanation. Empty problem inputs, missing match terms or missing links fail closed before a recommendation is returned. The completed-diagnosis view displays **Why recommended** and navigable links back to the relevant problem inputs.

The rationale describes the rule match only. It does not claim expected impact, prove suitability, endorse a provider, approve procurement or replace Executive Director judgment.

This is a coding-only candidate. Tests, CI, merge, staging deployment and owner acceptance are intentionally deferred to the combined qualification phase.
