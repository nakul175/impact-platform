## QA v1.3 — source-bound case design (proposed)

Story `FR-ACC-009` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ACC-009-001` / `TC-IMPRANA-FR-ACC-009-001` | `REV_2a75b79ee0266e2527a6de3328459ae814120749ab217ebe2f9889eb07a9a7d1` / `REV_be84b3a098862e9be09b03c4cf20ff481910ed425f82cc445c1fb7c6f80d1346` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-009-002` / `TC-IMPRANA-FR-ACC-009-002` | `REV_c36f153f709bc9df0bc10f32c7c344c4ee6d0a1b89ed5a349274493d42ed196d` / `REV_600fdd4d1e036b1e60bccc6c5c726cb9751c866bb153421bfbcaa36f71192417` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-009-003` / `TC-IMPRANA-FR-ACC-009-003` | `REV_1c8d0a9aad0369d0567a87456976068a2e352395b185fa254e15cab1abced97f` / `REV_ff369b26d7cdc3748b78032b49a8fdc123635544628e0f5b72ab57aa76589762` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-009-004` / `TC-IMPRANA-FR-ACC-009-004` | `REV_ad36ecb9d0f6a7294300326cbedc8989d514d2e50a8e56323e5e80662ecf119d` / `REV_c1aae5a2cef355b32083fffefee0b7966bc8fdf072b6d7aa5aae3daab87979c3` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ACC-009-001 — Configure and test disclosure rules

Source persona: Privacy Officer. Proposed fixture `FIX-FR-ACC-009-001` is not created. Verification duty `TASK-FR-ACC-009-03` (qualification); source `docs/backlog/backlog.csv` record 190, exact block `2a75b79ee0266e2527a6de3328459ae814120749ab217ebe2f9889eb07a9a7d1`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the Privacy Officer selects a minimum cell threshold, complementary suppression and allowed fixed slices

**Exact source oracles — all required**

1. the preview tests totals, cross tables and filter combinations for reconstruction
2. the default threshold of five is applied as a minimum rule

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-009-01`, `TC-ACC-009-02`, `TC-AT16`, `SEC-021`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-009-002 — Return the same suppressed output everywhere

Source persona: Privacy Officer. Proposed fixture `FIX-FR-ACC-009-002` is not created. Verification duty `TASK-FR-ACC-009-03` (qualification); source `docs/backlog/backlog.csv` record 190, exact block `c36f153f709bc9df0bc10f32c7c344c4ee6d0a1b89ed5a349274493d42ed196d`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the aggregate is retrieved through public APIs or downloads

**Exact source oracles — all required**

1. the same suppressed representation is returned without hidden raw values

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-009-01`, `TC-ACC-009-02`, `TC-AT16`, `SEC-021`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-009-003 — Reject reconstruction by differencing

Source persona: Privacy Officer. Proposed fixture `FIX-FR-ACC-009-003` is not created. Verification duty `TASK-FR-ACC-009-03` (qualification); source `docs/backlog/backlog.csv` record 190, exact block `1c8d0a9aad0369d0567a87456976068a2e352395b185fa254e15cab1abced97f`.

**Original preconditions**

1. groups of two and eight with a total of ten

**Original actions**

1. the aggregate is published

**Exact source oracles — all required**

1. the eight and ten combination is not exposed if it reveals the suppressed two

Legacy same-requirement reuse candidates: `TC-ACC-009-01`, `TC-ACC-009-02`, `TC-AT16`, `SEC-021`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-009-004 — Reject slices that cannot be bounded

Source persona: Privacy Officer. Proposed fixture `FIX-FR-ACC-009-004` is not created. Verification duty `TASK-FR-ACC-009-03` (qualification); source `docs/backlog/backlog.csv` record 190, exact block `ad36ecb9d0f6a7294300326cbedc8989d514d2e50a8e56323e5e80662ecf119d`.

**Original preconditions**

1. complementary suppression or differencing cannot be bounded for a slice

**Original actions**

1. publication is attempted

**Exact source oracles — all required**

1. the affected slice is withheld or only a reviewed fixed artifact is exposed

Legacy same-requirement reuse candidates: `TC-ACC-009-01`, `TC-ACC-009-02`, `TC-AT16`, `SEC-021`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
