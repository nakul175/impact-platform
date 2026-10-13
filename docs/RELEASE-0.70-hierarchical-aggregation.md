# Release 0.70 candidate — governed hierarchical aggregation

Coding-only candidate for **FR-CAL-006 / APL-580**.

Revisioned hierarchies declare every parent-child edge, contribution mode, combination rule and attribution scope. Draft writes reject cycles, disconnected nodes, mixed rules at one parent, implicit weights and weights that do not reconcile exactly to one. The evaluator supports up to 100 levels, pins a current approved hierarchy and exact readable calculated-result revisions, and stores an immutable result with maximum depth and complete source lineage.

`UNIQUE_UNION` deduplicates the same exact source revision reached through multiple branches when its value is consistent. `SUM` refuses any repeated source instead of double counting or silently halving it. `WEIGHTED` requires explicit, non-negative, exactly reconciled sibling weights. Exact operation retries return the recorded result only after current authority is rechecked.

Tests, CI, merge, staging deployment, acceptance and human certification remain pending under the owner's coding-first instruction.
