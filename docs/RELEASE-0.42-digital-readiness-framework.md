# Release 0.42 candidate — explained digital-readiness assessment

Status: **coding-only candidate; untested, unreviewed, unmerged and undeployed**.

## Delivered in code

US-DX-02 / APL-363 extends the existing bounded organisation brief with a deterministic,
server-owned digital maturity and data-readiness result. The candidate returns exactly five ordered
dimension scores: data foundation, people and skills, governance and safety, workflow fit, and
delivery capacity. Every score includes its 1–5 scale, named level, explanation, rule ID and the
exact submitted fields used by that rule. The browser renders the full result and limitations.

The client submits only the existing six bounded self-report inputs. It cannot submit or overwrite a
score or explanation. The server refuses an internally incomplete framework rather than returning
an unexplained or out-of-range result. Existing recommendations and capacity gaps remain compatible.

## Framework boundary

The pinned edition is `IMPRANA_DIGITAL_READINESS` / `2026-10-v1-editorial-draft`. It is an internal
editorial draft, not an externally recognised standard, certification, advisor approval or official
impact result. It produces no aggregate because no cross-dimension weights are approved. It is not
persisted and does not feed opportunity ranking. Owner review of the edition, dimensions, scale and
score ownership remains a product gate before the story can satisfy the source phrase “standard
framework”.

## Contract and persistence

- Domain API candidate 1.33; build 0.42.
- The assessment response is now closed around the existing result and the five explained scores.
- No new capability, table or migration. Schema remains 48 and all migrations stay byte-exact.
- OpenAPI, implemented API and access-policy artifacts were regenerated.

## Limits

No test, lint, type check, browser run, native PostgreSQL qualification, independent review, CI,
merge or deployment was performed at the owner's request to defer qualification until the combined
story train. No Linear status, source criterion or acceptance state changed.

## Integration notes

This candidate is stacked on US-DX-03 commit `a46b58d7c303dc6d91f81fed40caa3535b07eeda`.
Before merge, confirm the provisional framework semantics, add meaningful unit/API/browser cases,
run the complete required CI matrix and complete the declared human and release gates.
