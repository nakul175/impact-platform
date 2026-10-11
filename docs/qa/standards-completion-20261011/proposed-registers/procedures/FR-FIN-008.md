## QA v1.3 — source-bound case design (proposed)

Story `FR-FIN-008` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FIN-008-001` / `TC-IMPRANA-FR-FIN-008-001` | `REV_30fba5aceb922100b66bf6f6e71c78ae7c2d3e8e80dabffb0286e0ad9d21a226` / `REV_bc1c1f183ada17c905e3ad1bbdf40d7231a72721fdf5b0a62ddf36d8c243c4eb` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-008-002` / `TC-IMPRANA-FR-FIN-008-002` | `REV_1454dbca25ef4dfc6b9ab92d83a87ff62545fd5c8c098c4f6e250df81f321593` / `REV_8b911c8439c6b70727ae6ee22a4e6310f69415af5d6b7ec4debfaf40d39702c9` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-008-003` / `TC-IMPRANA-FR-FIN-008-003` | `REV_b3e193eb1884925c9c4fa64a6fa09314a159edd67b0d0f98ac3546c0ef0cec18` / `REV_cc4a64f436ad51c8de08276c20970c46e86bbd8aba76a6efe792612c9184d9c6` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-008-004` / `TC-IMPRANA-FR-FIN-008-004` | `REV_e662e98b96f43ca618fdb4c47356afcb89eacd9c637645f53eb730afe8b1ed55` / `REV_52aab0dec9bf920d0fa50af1687d648612dbdceb1783591ab25a2819b1a46057` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FIN-008-001 — Programme viewer sees the approved summary

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-008-001` is not created. Verification duty `TASK-FR-FIN-008-03` (qualification); source `docs/backlog/backlog.csv` record 232, exact block `30fba5aceb922100b66bf6f6e71c78ae7c2d3e8e80dabffb0286e0ad9d21a226`.

**Original preconditions**

1. a published budget total on a programme dashboard

**Original actions**

1. a programme viewer opens it

**Exact source oracles — all required**

1. the approved summary disclosure is visible
2. the audit record identifies the financial read without logging secret values

Legacy same-requirement reuse candidates: `TC-FIN-008-01`, `TC-FIN-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-008-002 — Reject retrieving restricted financial detail

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-008-002` is not created. Verification duty `TASK-FR-FIN-008-03` (qualification); source `docs/backlog/backlog.csv` record 232, exact block `1454dbca25ef4dfc6b9ab92d83a87ff62545fd5c8c098c4f6e250df81f321593`.

**Original preconditions**

1. a programme viewer who can see a published budget total

**Original actions**

1. they attempt to retrieve transaction rows or confidential clauses through drill down, API or export

**Exact source oracles — all required**

1. the request is refused

Legacy same-requirement reuse candidates: `TC-FIN-008-01`, `TC-FIN-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-008-003 — Reject self-approval of a budget revision

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-008-003` is not created. Verification duty `TASK-FR-FIN-008-03` (qualification); source `docs/backlog/backlog.csv` record 232, exact block `b3e193eb1884925c9c4fa64a6fa09314a159edd67b0d0f98ac3546c0ef0cec18`.

**Original preconditions**

1. a finance approver who authored a budget revision

**Original actions**

1. they attempt to approve it

**Exact source oracles — all required**

1. the approval is blocked

Legacy same-requirement reuse candidates: `TC-FIN-008-01`, `TC-FIN-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-008-004 — Reject ledger access through connection administration

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-008-004` is not created. Verification duty `TASK-FR-FIN-008-03` (qualification); source `docs/backlog/backlog.csv` record 232, exact block `e662e98b96f43ca618fdb4c47356afcb89eacd9c637645f53eb730afe8b1ed55`.

**Original preconditions**

1. a user with connection administration rights only

**Original actions**

1. they attempt to access ledger fields

**Exact source oracles — all required**

1. access to every ledger field is not granted

Legacy same-requirement reuse candidates: `TC-FIN-008-01`, `TC-FIN-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
