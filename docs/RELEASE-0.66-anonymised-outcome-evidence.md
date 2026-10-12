# Release 0.66 candidate — anonymised outcome evidence

Coding-only candidate for **US-IM-05 / APL-572**, frozen in `docs/backlog/features/adoption-improve.feature` lines 90–110. Only an active organisation's latest explicit consent for an exact available outcome revision contributes. A withdrawal remains possible without reading a now-restricted outcome.

Schema 60 stores immutable tenant-fenced consent events, an owner-only fixed source set, safe platform-visible publications, and immutable approval/publish events. Each metric/unit/quarter cell reduces to one contribution per organisation. Values and organisation counts are withheld below five organisations and when comparison with an earlier publication could reveal a change involving fewer than five organisations. Shared artifacts never contain organisation identifiers, source-set fingerprints, notes, actors, or raw observations.

Domain API 1.57 adds the tenant consent command and platform operator list, prepare, independent approve, and publish commands. Prepare and both transitions use current operator authority; writes require fresh assurance, exact operation replay is durable, approval requires a different natural person, and transitions recheck consent and exact source revisions under lock.

Tests, CI, merge, deployment, product acceptance, and human certification remain pending under the owner's coding-first instruction.
