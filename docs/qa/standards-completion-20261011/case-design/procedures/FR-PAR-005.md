## QA v1.3 — source-bound case design (proposed)

Story `FR-PAR-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PAR-005-001` / `TC-IMPRANA-FR-PAR-005-001` | `REV_4f3aab9f4c7190e27d41cb616b0172c57895cee8b33aca01cd3e047da1a493bb` / `REV_e1d1c2a87f62ce1a1153a669a18cf6c5c5c73a6f282aa95688daa5b7bb278c72` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PAR-005-002` / `TC-IMPRANA-FR-PAR-005-002` | `REV_9e7a9e50201ee69ce5748969c7445d90c608cbf204d88e1c324a007dbfe02c2d` / `REV_2e73599f0e1afa352b0429e59c058400e2f9346e1cf948e88b4e866c22231f3f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PAR-005-003` / `TC-IMPRANA-FR-PAR-005-003` | `REV_8da660da546519d0d16a897994a7dcdac4ca709a88cfe16ddd585bceb8e4c228` / `REV_d93ecab7769b91f17c34042d08101d0ceded3c9c7d7cac4105adba1e12fe33d4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PAR-005-004` / `TC-IMPRANA-FR-PAR-005-004` | `REV_4f7516fbdf8ea618fa5732a8b8aa70fb5062bdb22ad257b31604126d3911cfc3` / `REV_b4bfd9db6ec798c13dc3f7426d8b22acca296eaa7a3d871df20c6a2f49d476b2` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PAR-005-001 — Move a person between households

Source persona: Data Steward. Proposed fixture `FIX-FR-PAR-005-001` is not created. Verification duty `TASK-FR-PAR-005-03` (qualification); source `docs/backlog/backlog.csv` record 351, exact block `4f3aab9f4c7190e27d41cb616b0172c57895cee8b33aca01cd3e047da1a493bb`.

**Original preconditions**

1. a person who is a member of household A

**Original actions**

1. they move to household B on 1 June

**Exact source oracles — all required**

1. the membership in household A is closed and a membership in household B is opened after overlap validation
2. May observations retain household A
3. July observations resolve to household B

Legacy same-requirement reuse candidates: `TC-PAR-005-01`, `TC-PAR-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PAR-005-002 — Record a membership and pin it to surveys

Source persona: Data Steward. Proposed fixture `FIX-FR-PAR-005-002` is not created. Verification duty `TASK-FR-PAR-005-03` (qualification); source `docs/backlog/backlog.csv` record 351, exact block `9e7a9e50201ee69ce5748969c7445d90c608cbf204d88e1c324a007dbfe02c2d`.

**Original preconditions**

1. a household or group

**Original actions**

1. a membership is recorded

**Exact source oracles — all required**

1. it records the entity pair, role, effective start and optional end
2. survey submissions pin the relevant relationship version

Legacy same-requirement reuse candidates: `TC-PAR-005-01`, `TC-PAR-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PAR-005-003 — Reject retrospective application of current membership

Source persona: Data Steward. Proposed fixture `FIX-FR-PAR-005-003` is not created. Verification duty `TASK-FR-PAR-005-03` (qualification); source `docs/backlog/backlog.csv` record 351, exact block `8da660da546519d0d16a897994a7dcdac4ca709a88cfe16ddd585bceb8e4c228`.

**Original preconditions**

1. historic surveys pinned to an earlier membership

**Original actions**

1. the person's current membership changes

**Exact source oracles — all required**

1. the historic surveys are not updated to the current membership

Legacy same-requirement reuse candidates: `TC-PAR-005-01`, `TC-PAR-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PAR-005-004 — Reject guardian details bypassing their own controls

Source persona: Data Steward. Proposed fixture `FIX-FR-PAR-005-004` is not created. Verification duty `TASK-FR-PAR-005-03` (qualification); source `docs/backlog/backlog.csv` record 351, exact block `4f7516fbdf8ea618fa5732a8b8aa70fb5062bdb22ad257b31604126d3911cfc3`.

**Original preconditions**

1. a user permitted to view household membership
2. not permitted under the guardian field's separate sensitivity and purpose controls

**Original actions**

1. they view the membership

**Exact source oracles — all required**

1. the guardian field is not shown to them

Legacy same-requirement reuse candidates: `TC-PAR-005-01`, `TC-PAR-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
