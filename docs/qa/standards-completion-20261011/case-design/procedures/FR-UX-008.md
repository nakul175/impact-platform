## QA v1.3 — source-bound case design (proposed)

Story `FR-UX-008` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-UX-008-001` / `TC-IMPRANA-FR-UX-008-001` | `REV_2402d1d0e707a83f1bb46204b4809e9bd20c279b5ce670ed85ade957d7d0147e` / `REV_8285a707281b547fe6e220356ea57f6c008449e0a4b1ddac009e15cc79b0dc62` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-008-002` / `TC-IMPRANA-FR-UX-008-002` | `REV_3d6ba33a066f7094aef67ac6b366c447acfc9f61520e57d493f8f742664bff65` / `REV_7cdf9445d9c35305a9bc65514e9be4fecdb151a5198a0508a7d9ae93b3fb0289` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-008-003` / `TC-IMPRANA-FR-UX-008-003` | `REV_37ce6065fcdef750e52a8b670e0729e64f08c5ca52edbd2e6d57b5e2750bfb05` / `REV_32bbe46b23d82fcc4e8d55764e7e50a88df862060faf2fb45489518ed2144c75` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-008-004` / `TC-IMPRANA-FR-UX-008-004` | `REV_3dce037c39429688296bfe6b18a3a66a2002141a603dadf02709d1604a5f3af9` / `REV_bc1fc5aebb50f3c5d91fa798c149a242e2442fc3b19c3fdc3339476efc3ac9f4` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-UX-008-001 — Resolve a pending approval without help from an administrator

Source persona: Data Author. Proposed fixture `FIX-FR-UX-008-001` is not created. Verification duty `TASK-FR-UX-008-03` (qualification); source `docs/backlog/backlog.csv` record 315, exact block `2402d1d0e707a83f1bb46204b4809e9bd20c279b5ce670ed85ade957d7d0147e`.

**Original preconditions**

1. an indicator assigned to the Data Author with approval pending

**Original actions**

1. they search for it

**Exact source oracles — all required**

1. they find it, identify why approval is pending and reach the required evidence task without administrator intervention

Legacy same-requirement reuse candidates: `TC-UX-008-01`, `TC-UX-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-008-002 — Notification leads to the exact issue

Source persona: Data Author. Proposed fixture `FIX-FR-UX-008-002` is not created. Verification duty `TASK-FR-UX-008-03` (qualification); source `docs/backlog/backlog.csv` record 315, exact block `3d6ba33a066f7094aef67ac6b366c447acfc9f61520e57d493f8f742664bff65`.

**Original preconditions**

1. a safe task notification

**Original actions**

1. the Data Author follows it

**Exact source oracles — all required**

1. they reach the exact permitted object and issue
2. help examples use synthetic data without revealing implementation secrets

Legacy same-requirement reuse candidates: `TC-UX-008-01`, `TC-UX-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-008-003 — Reject results beyond current permissions

Source persona: Data Author. Proposed fixture `FIX-FR-UX-008-003` is not created. Verification duty `TASK-FR-UX-008-03` (qualification); source `docs/backlog/backlog.csv` record 315, exact block `37ce6065fcdef750e52a8b670e0729e64f08c5ca52edbd2e6d57b5e2750bfb05`.

**Original preconditions**

1. an item the Data Author is no longer permitted to see

**Original actions**

1. they use search, recent work or saved views

**Exact source oracles — all required**

1. the item does not appear

Legacy same-requirement reuse candidates: `TC-UX-008-01`, `TC-UX-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-008-004 — Reject silent rebinding of a saved view

Source persona: Data Author. Proposed fixture `FIX-FR-UX-008-004` is not created. Verification duty `TASK-FR-UX-008-03` (qualification); source `docs/backlog/backlog.csv` record 315, exact block `3dce037c39429688296bfe6b18a3a66a2002141a603dadf02709d1604a5f3af9`.

**Original preconditions**

1. a saved view bound to a retired definition

**Original actions**

1. it is opened

**Exact source oracles — all required**

1. a reviewed rebinding is prompted
2. its meaning is not silently changed

Legacy same-requirement reuse candidates: `TC-UX-008-01`, `TC-UX-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
