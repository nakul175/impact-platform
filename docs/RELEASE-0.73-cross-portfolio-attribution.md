# Release 0.73 candidate — governed cross-portfolio attribution

Coding-only candidate for **FR-CAL-014 / APL-589**.

Revisioned portfolio allocation views store view-only portfolio memberships plus exact result-revision shares, basis and remainder policy. A project may appear in multiple named portfolios, while the organisation count is the set of currently permitted underlying programme/project IDs. Hidden projects are never inferred or counted.

Allocation rows must belong to a declared membership and the exact result lineage must resolve to that project. Duplicate allocation rows and additive shares above one are refused. An explicitly nonadditive view may exceed one only with a visible label and a not-applicable remainder policy; every response fixes `causal_ownership` to false. Additive views disclose the unallocated result remainder under their named policy rather than silently dropping it. Preview requires the current independently approved view revision, filters hidden projects and their allocations before counting, and exposes an allocation only while its exact result, lineage and indicator remain readable.

Tests, CI, merge, staging deployment, acceptance and human certification remain pending under the owner's coding-first instruction.
