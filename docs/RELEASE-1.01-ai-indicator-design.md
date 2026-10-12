# Release 1.01 coding candidate — governed indicator design assistance

FR-AI-003 / APL-533 adds a reserved indicator-design use case. It reads an exact current approved `IndicatorDefinition` revision and exact current programme revision, then proposes the governed definition fields with explicit denominator, proxy, population and evidence-method warnings. The response contains no model confidence and cannot approve an indicator or create a standard mapping.

An authorised MEL administrator can select proposal fields into an ordinary `IndicatorDefinition` draft. The write rechecks both source revisions, the policy in force and the safety shutdown, uses the existing draft schema, and records an ordinary audited revision plus replay-safe operation receipt. Incomplete drafts remain drafts: the existing `definition_ready` and method oracle refuses submission or approval until required fields, ratio component meanings and a supported manual calculation method are present.

Migration 0085 adds `INDICATOR_DESIGN` to the closed policy vocabulary while retaining the existing reserved-use constraint. It therefore cannot be enabled by a tenant in this candidate; activation requires a later reviewed migration and owner decision. No provider call, standard mapping, approval, merge, deployment or spend is introduced. Tests and CI remain deferred by owner request.
