## QA v1.3 — source-bound case design (proposed)

Story `FR-PLN-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PLN-001-001` / `TC-IMPRANA-FR-PLN-001-001` | `REV_30af53338ca4b00aaafc4dba08819fbe43880dfb204eb840d3d8f80538b26992` / `REV_05fe0b7aca428be053754a0238bfd73f3269c198c33e9aedcc6ba6910e3f6751` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PLN-001-002` / `TC-IMPRANA-FR-PLN-001-002` | `REV_dcca4b77d818f1111f8bf52c2548c4920d1403b75f238dcdd70f3057c08bd2a5` / `REV_a5064f6d92de06dacee9d27ec074ce033f71ceba019de70a537d89a9899a0577` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PLN-001-003` / `TC-IMPRANA-FR-PLN-001-003` | `REV_ba223f5c8cce6fa7278ad951a141b7b9bf6dcead8f8c091e9fb6f74c8909ccf7` / `REV_eb460fed05cc1b57973e3409a9c0d15af794b55100b6722e022761ee3a115410` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PLN-001-004` / `TC-IMPRANA-FR-PLN-001-004` | `REV_0716777b97fde52c873bdc96ddf777dfc14ab99fe74e99edb75b00381d38e3fc` / `REV_c4466e0dd5fc5f0745c50aaa5b47f2a0be60c8d8e5024406ee1233cc59f87621` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PLN-001-001 — Create framework nodes in either view

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-001-001` is not created. Verification duty `TASK-FR-PLN-001-03` (qualification); source `docs/backlog/backlog.csv` record 143, exact block `30af53338ca4b00aaafc4dba08819fbe43880dfb204eb840d3d8f80538b26992`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the MEL Manager creates typed framework nodes in the table or relationship view

**Exact source oracles — all required**

1. both views edit the same stable node identities and version
2. activities may be linked to output nodes
3. relationship links are kept distinct from numeric aggregation links

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-PLN-001-01`, `TC-PLN-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PLN-001-002 — Rename a node in one view

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-001-002` is not created. Verification duty `TASK-FR-PLN-001-03` (qualification); source `docs/backlog/backlog.csv` record 143, exact block `dcca4b77d818f1111f8bf52c2548c4920d1403b75f238dcdd70f3057c08bd2a5`.

**Original preconditions**

1. an output with indicator bindings in a draft

**Original actions**

1. the MEL Manager renames the output in the table

**Exact source oracles — all required**

1. the graph and indicator bindings update within the same draft
2. no duplicate node is created

Legacy same-requirement reuse candidates: `TC-PLN-001-01`, `TC-PLN-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PLN-001-003 — Validate nodes before review

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-001-003` is not created. Verification duty `TASK-FR-PLN-001-03` (qualification); source `docs/backlog/backlog.csv` record 143, exact block `ba223f5c8cce6fa7278ad951a141b7b9bf6dcead8f8c091e9fb6f74c8909ccf7`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the MEL Manager submits the draft for review

**Exact source oracles — all required**

1. each node is validated for title, description, owner and intended result level

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-PLN-001-01`, `TC-PLN-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PLN-001-004 — Reject invalid structural changes

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-001-004` is not created. Verification duty `TASK-FR-PLN-001-03` (qualification); source `docs/backlog/backlog.csv` record 143, exact block `0716777b97fde52c873bdc96ddf777dfc14ab99fe74e99edb75b00381d38e3fc`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the MEL Manager creates a containment cycle, leaves an orphaned parent reference or deletes a referenced approved node

**Exact source oracles — all required**

1. the change is rejected

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-PLN-001-01`, `TC-PLN-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
