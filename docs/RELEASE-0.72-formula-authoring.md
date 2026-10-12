# Release 0.72 candidate — typed formula authoring and preview

Coding-only candidate for **FR-CAL-012 / APL-586**.

Formula definitions store a closed JSON AST rather than executable text. The only nodes are decimal literals, exact approved indicator-definition references, approved category filters and calls from the bounded catalogue: add, subtract, scalar multiply, divide, count, sum, minimum, maximum, ratio and eligible distinct count. The contract has no script, SQL, URL, network, filesystem or dynamic-query node.

Draft validation rechecks current read authority for every exact approved reference, rejects a direct circular target reference, validates filter categories and propagates units through every node. Preview requires the exact referenced sample set and returns deterministic Decimal output with explicit `PRESENT`, `MISSING` or `UNDEFINED` state; zero denominator remains undefined. Ordinary independent workflow review governs formula approval.

Tests, CI, merge, staging deployment, acceptance and human certification remain pending under the owner's coding-first instruction.
