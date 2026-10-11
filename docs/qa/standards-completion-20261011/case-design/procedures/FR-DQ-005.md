## QA v1.3 — source-bound case design (proposed)

Story `FR-DQ-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DQ-005-001` / `TC-IMPRANA-FR-DQ-005-001` | `REV_f6b874b8f9306e74118eaa2bd0a6742f97e0c825134c282498761b05a08e95e9` / `REV_4974f255462274a0d2bb3990eaa63fa0c74d8bfb0cd6f1905cb961ffd3eb21cd` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-005-002` / `TC-IMPRANA-FR-DQ-005-002` | `REV_d85eb07ad8cd6c2b60282baa979292c49875c7f36635baa1d6cda46a781b51e7` / `REV_63d158e4a54f7050a88c8e5fba38b2e0bffe308d528c9821ce0d2aa6d8de23ac` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-005-003` / `TC-IMPRANA-FR-DQ-005-003` | `REV_b64772bae4d054da88161d5241ccc96c24eba4d71d35c439e3bd8d361202e5fa` / `REV_4b9cc9af92c3337925038137edbad90ddef38fb640240f611c3110aff54a2b53` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-005-004` / `TC-IMPRANA-FR-DQ-005-004` | `REV_5f60d20ff60652e7c887ab834741bd33b34ef6d9298310f07ded8f1a05bf4773` / `REV_d62a9f19053e144e6a38db28a47e6db66fd1f3988a2944f0082614a6b1386b85` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DQ-005-001 — Trace a malformed date from import rejection to accepted revision

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-005-001` is not created. Verification duty `TASK-FR-DQ-005-03` (qualification); source `docs/backlog/backlog.csv` record 223, exact block `f6b874b8f9306e74118eaa2bd0a6742f97e0c825134c282498761b05a08e95e9`.

**Original preconditions**

1. an imported record is rejected for a malformed date
2. a quality issue binds the failing revision, rule, severity, owner and due time

**Original actions**

1. a correction opens a linked revision
2. revalidation confirms the new outcome

**Exact source oracles — all required**

1. closure records its evidence
2. the reporting delay and final accepted revision remain traceable

**Separate existing supplemental plan oracle (unapproved)**

1. revalidation confirms the new outcome

Legacy same-requirement reuse candidates: `TC-DQ-005-01`, `TC-DQ-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-005-002 — Unresolved material issue stays attached to dependent results

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-005-002` is not created. Verification duty `TASK-FR-DQ-005-03` (qualification); source `docs/backlog/backlog.csv` record 223, exact block `d85eb07ad8cd6c2b60282baa979292c49875c7f36635baa1d6cda46a781b51e7`.

**Original preconditions**

1. an unresolved material quality issue

**Original actions**

1. a dependent result is viewed

**Exact source oracles — all required**

1. the issue remains attached to that result

Legacy same-requirement reuse candidates: `TC-DQ-005-01`, `TC-DQ-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-005-003 — Recurrence links to prior history

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-005-003` is not created. Verification duty `TASK-FR-DQ-005-03` (qualification); source `docs/backlog/backlog.csv` record 223, exact block `b64772bae4d054da88161d5241ccc96c24eba4d71d35c439e3bd8d361202e5fa`.

**Original preconditions**

1. a quality issue that was previously fixed

**Original actions**

1. the issue recurs

**Exact source oracles — all required**

1. the new recurrence links to the prior history
2. the earlier fix is not erased

Legacy same-requirement reuse candidates: `TC-DQ-005-01`, `TC-DQ-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-005-004 — Reject closing an issue by changing owner or resolving a comment

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-005-004` is not created. Verification duty `TASK-FR-DQ-005-03` (qualification); source `docs/backlog/backlog.csv` record 223, exact block `5f60d20ff60652e7c887ab834741bd33b34ef6d9298310f07ded8f1a05bf4773`.

**Original preconditions**

1. an open quality issue

**Original actions**

1. its owner is changed or a comment on it is marked resolved

**Exact source oracles — all required**

1. the issue remains open

Legacy same-requirement reuse candidates: `TC-DQ-005-01`, `TC-DQ-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
