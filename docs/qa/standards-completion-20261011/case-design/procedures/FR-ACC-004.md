## QA v1.3 — source-bound case design (proposed)

Story `FR-ACC-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ACC-004-001` / `TC-IMPRANA-FR-ACC-004-001` | `REV_2c1cefb9d6a07346736ab22a63ecc7b341e4aae6ebf96eeba3245570b1a45cd5` / `REV_36b0cadc6f7e6c2c3aea947caf34914d691339a8116d8e405fdd3783951763a4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-004-002` / `TC-IMPRANA-FR-ACC-004-002` | `REV_dc94b9fae490a22c82ab48c726904af438f028c98dd4da5f4a76a1d57291b240` / `REV_5834ad4f74001d28a162fc4ec44298292be98bbe1da1f3c0220e343314c940b3` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-004-003` / `TC-IMPRANA-FR-ACC-004-003` | `REV_a210e8a11f53d94629a38566ed8c8cee431d34178e505244005d29e9cb8bc3a2` / `REV_f8680fd3c9276d278f54ff5914a8d59816979975191f7b468979d7fcdccdda1f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-004-004` / `TC-IMPRANA-FR-ACC-004-004` | `REV_f87231631a14a17c6c9a071bd9fc754af140115b93ef4d0e957ff361eb11260d` / `REV_3eaa6b61e4ce941e22faf55c27bf348e08d8b31a8db1d30464b0a78ba2be1511` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ACC-004-001 — Accept an independent approval

Source persona: MEL Manager. Proposed fixture `FIX-FR-ACC-004-001` is not created. Verification duty `TASK-FR-ACC-004-03` (qualification); source `docs/backlog/backlog.csv` record 22, exact block `2c1cefb9d6a07346736ab22a63ecc7b341e4aae6ebf96eeba3245570b1a45cd5`.

**Original preconditions**

1. a candidate's author set, verified identity aliases, delegated authorisation and current reviewer assignment have been calculated

**Original actions**

1. a Reviewer who is not a material author approves it

**Exact source oracles — all required**

1. the approval is accepted

Legacy same-requirement reuse candidates: `TC-ACC-004-01`, `TC-ACC-004-02`, `TC-AT12`, `SEC-017`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-004-002 — Invalidate decisions when the candidate is edited

Source persona: MEL Manager. Proposed fixture `FIX-FR-ACC-004-002` is not created. Verification duty `TASK-FR-ACC-004-03` (qualification); source `docs/backlog/backlog.csv` record 22, exact block `dc94b9fae490a22c82ab48c726904af438f028c98dd4da5f4a76a1d57291b240`.

**Original preconditions**

1. a candidate has existing decisions

**Original actions**

1. the candidate is edited

**Exact source oracles — all required**

1. it returns to draft
2. the old candidate decisions are invalidated

Legacy same-requirement reuse candidates: `TC-ACC-004-01`, `TC-ACC-004-02`, `TC-AT12`, `SEC-017`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-004-003 — Reject self approval through a second group

Source persona: MEL Manager. Proposed fixture `FIX-FR-ACC-004-003` is not created. Verification duty `TASK-FR-ACC-004-03` (qualification); source `docs/backlog/backlog.csv` record 22, exact block `a210e8a11f53d94629a38566ed8c8cee431d34178e505244005d29e9cb8bc3a2`.

**Original preconditions**

1. the author of a candidate becomes a Reviewer through a second group

**Original actions**

1. they attempt to approve the candidate

**Exact source oracles — all required**

1. the approval is rejected
2. a different eligible person is still required

Legacy same-requirement reuse candidates: `TC-ACC-004-01`, `TC-ACC-004-02`, `TC-AT12`, `SEC-017`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-004-004 — Reject other routes to false independence

Source persona: MEL Manager. Proposed fixture `FIX-FR-ACC-004-004` is not created. Verification duty `TASK-FR-ACC-004-03` (qualification); source `docs/backlog/backlog.csv` record 22, exact block `f87231631a14a17c6c9a071bd9fc754af140115b93ef4d0e957ff361eb11260d`.

**Original preconditions**

1. the approver overlaps the material authors through a role switch, group change, delegated task, service identity or verified alias

**Original actions**

1. approval is attempted

**Exact source oracles — all required**

1. it is not counted as independent
2. an emergency exception requires a separately approved policy and cannot silently count self approval as independent

Legacy same-requirement reuse candidates: `TC-ACC-004-01`, `TC-ACC-004-02`, `TC-AT12`, `SEC-017`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
