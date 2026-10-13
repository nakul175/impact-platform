## QA v1.3 — source-bound case design (proposed)

Story `FR-EVD-004` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-EVD-004-001` / `TC-IMPRANA-FR-EVD-004-001` | `REV_305dbae6323d224df591e7db12ef6ed967d5a6c22912d609dbdb0eec0ac04062` / `REV_c9908c15e3ac896f16f9f3b54c4ab902bb4323d30cecfa065932bcd8ff60f18b` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-004-002` / `TC-IMPRANA-FR-EVD-004-002` | `REV_70feaf6db0aab9e9f072ebb183447919882ae8115a4bc0906ff2604ff58aa921` / `REV_11a9cc0529a27eaee7d5bf70cd2f9263917b87103bb2f439229b4486f68a714c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-004-003` / `TC-IMPRANA-FR-EVD-004-003` | `REV_273420a47401b2c0a4bab08b56621e9943d0bc5ad099384ed3af4ddf1573a66b` / `REV_61a5d7aefbe609f9c3042165162f7c18390cee247f68a68677e781af121ca529` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-EVD-004-001 — Annotate a document version

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-004-001` is not created. Verification duty `TASK-FR-EVD-004-03` (qualification); source `docs/backlog/backlog.csv` record 228, exact block `305dbae6323d224df591e7db12ef6ed967d5a6c22912d609dbdb0eec0ac04062`.

**Original preconditions**

1. a document version

**Original actions**

1. an Analyst adds an annotation

**Exact source oracles — all required**

1. it references that version and a stable page, section, timestamp or excerpt anchor
2. later comment edits retain the author and permitted history

Legacy same-requirement reuse candidates: `TC-EVD-004-01`, `TC-EVD-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-004-002 — Replace a report where pages shift

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-004-002` is not created. Verification duty `TASK-FR-EVD-004-03` (qualification); source `docs/backlog/backlog.csv` record 228, exact block `70feaf6db0aab9e9f072ebb183447919882ae8115a4bc0906ff2604ff58aa921`.

**Original preconditions**

1. a published citation to a page of a report

**Original actions**

1. the report is replaced by a new version in which pages shift

**Exact source oracles — all required**

1. the old published citation still resolves to the old page
2. migrating an annotation to the new version requires verified remapping with ambiguities flagged

Legacy same-requirement reuse candidates: `TC-EVD-004-01`, `TC-EVD-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-004-003 — Reject attaching an unmatched anchor to a similar passage

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-004-003` is not created. Verification duty `TASK-FR-EVD-004-03` (qualification); source `docs/backlog/backlog.csv` record 228, exact block `273420a47401b2c0a4bab08b56621e9943d0bc5ad099384ed3af4ddf1573a66b`.

**Original preconditions**

1. an annotation anchor that cannot be matched in the new version

**Original actions**

1. anchor migration runs

**Exact source oracles — all required**

1. the annotation is marked unresolved
2. it is not attached to a similar passage

Legacy same-requirement reuse candidates: `TC-EVD-004-01`, `TC-EVD-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
