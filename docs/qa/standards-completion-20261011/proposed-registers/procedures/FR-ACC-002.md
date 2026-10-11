## QA v1.3 — source-bound case design (proposed)

Story `FR-ACC-002` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ACC-002-001` / `TC-IMPRANA-FR-ACC-002-001` | `REV_37da1ed4ce922ef7767ed63e364e3373b6acbc90188fcfdf6a703a8078ceb2cd` / `REV_f0eb82599f1d34f7dc23e679bad23e350efbfc205e0c212eaea261fc56eb0b2d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-002-002` / `TC-IMPRANA-FR-ACC-002-002` | `REV_05ed3d7056fcbf0bcb98aa4a603f238f4821db6b36e1a68034404b1019e9492f` / `REV_2fa4b854db75b03c571da60eb531e35e335f3df3238765d2bb45d6ad6cfcc9bf` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-002-003` / `TC-IMPRANA-FR-ACC-002-003` | `REV_7e2504575015d5734093e7c56bf61a592db4a2af636b5971ef7185e5ff06615c` / `REV_56dae4e4ead61cea339d63b2701a19b0b89ec27c1620e4dca093ee1da28ed724` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-002-004` / `TC-IMPRANA-FR-ACC-002-004` | `REV_452303d6a7de9ed5c6984aedeb8d52522ef1909046fd5a0ddb78a1a60deac0b1` / `REV_f797dad4377755288909e382f09d09bd70fce213d0b829b998f6ebf130641b37` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-002-005` / `TC-IMPRANA-FR-ACC-002-005` | `REV_7f0e2443931d232264266af8324be3a9262f9db58226f00966511c48a97e2ac5` / `REV_7174544a9768d64bdc843e54a8b0a8394ee8a17323199fa1df6fcfc8f6aaeae4` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ACC-002-001 — Define a fine grained grant

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-002-001` is not created. Verification duty `TASK-FR-ACC-002-03` (qualification); source `docs/backlog/backlog.csv` record 20, exact block `37da1ed4ce922ef7767ed63e364e3373b6acbc90188fcfdf6a703a8078ceb2cd`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the Organisation Administrator creates a grant

**Exact source oracles — all required**

1. they select action, project or partner scope, record condition and permitted field categories separately
2. sensitive view, download, approval and publication are granted independently from ordinary read

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-002-01`, `TC-ACC-002-02`, `IT-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-002-002 — Apply row and field policy first

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-002-002` is not created. Verification duty `TASK-FR-ACC-002-03` (qualification); source `docs/backlog/backlog.csv` record 20, exact block `05ed3d7056fcbf0bcb98aa4a603f238f4821db6b36e1a68034404b1019e9492f`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a member reads records

**Exact source oracles — all required**

1. row and field policy is applied before filters, sorting, aggregation or export

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-002-01`, `TC-ACC-002-02`, `IT-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-002-003 — Leave omitted hidden fields unchanged

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-002-003` is not created. Verification duty `TASK-FR-ACC-002-03` (qualification); source `docs/backlog/backlog.csv` record 20, exact block `7e2504575015d5734093e7c56bf61a592db4a2af636b5971ef7185e5ff06615c`.

**Original preconditions**

1. a field is hidden from a member

**Original actions**

1. they save an editable row without that field

**Exact source oracles — all required**

1. the omitted field is not cleared

Legacy same-requirement reuse candidates: `TC-ACC-002-01`, `TC-ACC-002-02`, `IT-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-002-004 — Reject actions outside a narrow grant

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-002-004` is not created. Verification duty `TASK-FR-ACC-002-03` (qualification); source `docs/backlog/backlog.csv` record 20, exact block `452303d6a7de9ed5c6984aedeb8d52522ef1909046fd5a0ddb78a1a60deac0b1`.

**Original preconditions**

1. a Reviewer is granted access to one candidate and its necessary evidence

**Original actions**

1. they attempt to edit the source or export the registry

**Exact source oracles — all required**

1. both attempts fail

Legacy same-requirement reuse candidates: `TC-ACC-002-01`, `TC-ACC-002-02`, `IT-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-002-005 — Reject writing a hidden field

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-002-005` is not created. Verification duty `TASK-FR-ACC-002-03` (qualification); source `docs/backlog/backlog.csv` record 20, exact block `7f0e2443931d232264266af8324be3a9262f9db58226f00966511c48a97e2ac5`.

**Original preconditions**

1. a row is editable but a field is hidden from the member

**Original actions**

1. they attempt to write the hidden field

**Exact source oracles — all required**

1. the write is denied

Legacy same-requirement reuse candidates: `TC-ACC-002-01`, `TC-ACC-002-02`, `IT-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
