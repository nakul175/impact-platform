# 0.93 AI answer provenance and reuse authority

FR-AI-013 / APL-342 lets an advisory request name up to twenty exact source object/revision dependencies and their required read capability. The immutable advisory revision records the normalized dependency list and its creator-only permitted audience; a tenant-keyed relational link pins every exact source revision.

Every source is checked against current object authority and exact revision availability before reservation. Exact replay performs the same checks before returning the sealed answer. A removed, restricted, hidden, wrong-type or newly inaccessible source therefore withdraws the whole answer rather than trying to reconstruct unsafe redactions. The provider receives none of the dependency identifiers or source content, and copying the response body creates no server-side access or share grant.

This is a coding-only candidate. Source formatting, compilation and contract generation are not qualification. Tests, CI, independent review, merge, staging deployment and owner acceptance remain pending.
