# 0.93 AI answer provenance and reuse authority

FR-AI-013 / APL-342 lets an advisory request name up to twenty exact source object/revision dependencies and their required read capability. The immutable advisory revision records the normalized dependency list and its creator-only permitted audience; a tenant-keyed relational link pins every exact source revision.

Every source is checked against current object authority and exact revision availability before reservation. Exact replay performs the same checks before returning the sealed answer. A removed, restricted, hidden, wrong-type or newly inaccessible source therefore withdraws the whole answer rather than trying to reconstruct unsafe redactions. The provider receives none of the dependency identifiers or source content, and copying the response body creates no server-side access or share grant.

The positive user journey is qualified on a disposable native PostgreSQL/API runtime by
`qualification/test_ai_answer_provenance_live.py` (1 passed). A synthetic advisory pins its exact
evidence object and revision in both the immutable request payload and relational dependency table,
records the creator-only audience, and replays without a second provider call. Governed revocation
of the source grant then withdraws the saved answer; a different principal cannot acquire reuse
rights by copying the request.

This evidence qualifies the positive-user-journey gate for APL-342. CI, independent review, merge,
staging deployment and owner acceptance remain pending.
