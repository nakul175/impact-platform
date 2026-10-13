# Release 0.69 candidate — governed population overlap

Coding-only candidate for **FR-CAL-004 / APL-578**.

An analyst first creates a revisioned population-matching scope declaring the entity type, population, project, time window and the only supported matching method: exact stable pseudonym. The normal independent workflow must approve the current scope revision before calculation.

The compute endpoint rechecks current authority for the exact approved scope and every exact approved observation revision. Identity-set inputs from that one project are unioned deterministically and the matched overlap is stored with an immutable result. Aggregate-only inputs produce gross reach and the literal overlap state `UNKNOWN`. Mixed identity and aggregate inputs also stay gross because exact external deduplication is absent. Cross-project input is refused, tenant isolation is inherited from forced RLS, pseudonyms must be opaque values, and no name or fuzzy matching path exists.

Tests, CI, merge, staging deployment, acceptance and human certification remain pending under the owner's coding-first instruction.
