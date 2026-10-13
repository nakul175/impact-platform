## QA v1.3 — source-bound case design (proposed)

Story `FR-AI-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-AI-007-001` / `TC-IMPRANA-FR-AI-007-001` | `REV_432dde72d0b5d51d95a93719f2652f859debe40d01c58f43a4ed379f32b793cc` / `REV_da79260415e305afe6c8005e230bd3a8985c01fff17f17e922f5cf11bd54be07` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-007-002` / `TC-IMPRANA-FR-AI-007-002` | `REV_27c11101b150a073800ac215d2d7012523d20c6ea4a7865a182fcb7c9881821b` / `REV_8ea4d231722d9ffd4a461d4e7acf9b581fd81c674caf849ee63fb3da459c4257` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-007-003` / `TC-IMPRANA-FR-AI-007-003` | `REV_fb689859047f11710067cd846465f8fda5d7c6311d88459dc97145272f308884` / `REV_240e1e20b2bb3a448d54cf5291a6a65cce7da32c16aad11392a3ffe3c21d485e` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-007-004` / `TC-IMPRANA-FR-AI-007-004` | `REV_806d90a9425df34cb8e1c662ddbf1e6674147a23ec1a3e47cd1fe8451029089a` / `REV_80c8e1ea7576f6322632a15be117507a85a6cec2ef6dedbd69670187589f3afa` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-AI-007-001 — Draft binds snapshot and template

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-007-001` is not created. Verification duty `TASK-FR-AI-007-03` (qualification); source `docs/backlog/backlog.csv` record 9, exact block `432dde72d0b5d51d95a93719f2652f859debe40d01c58f43a4ed379f32b793cc`.

**Original preconditions**

1. an approved snapshot and report template

**Original actions**

1. the MEL Manager requests a draft

**Exact source oracles — all required**

1. proposed sections include evidence references and metric bindings
2. every official number matches its bound result

Legacy same-requirement reuse candidates: `TC-AI-007-01`, `TC-AI-007-02`, `TC-AT10`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_reporting.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-007-002 — Missing evidence stays visible

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-007-002` is not created. Verification duty `TASK-FR-AI-007-03` (qualification); source `docs/backlog/backlog.csv` record 9, exact block `27c11101b150a073800ac215d2d7012523d20c6ea4a7865a182fcb7c9881821b`.

**Original preconditions**

1. an incomplete snapshot

**Original actions**

1. a draft is generated

**Exact source oracles — all required**

1. missing sections appear as evidence gaps

Legacy same-requirement reuse candidates: `TC-AI-007-01`, `TC-AI-007-02`, `TC-AT10`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_reporting.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-007-003 — Review tracks AI origin

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-007-003` is not created. Verification duty `TASK-FR-AI-007-03` (qualification); source `docs/backlog/backlog.csv` record 9, exact block `fb689859047f11710067cd846465f8fda5d7c6311d88459dc97145272f308884`.

**Original preconditions**

1. a draft under review

**Original actions**

1. reviewers correct it and finalise wording

**Exact source oracles — all required**

1. AI origin, corrections and final human wording are tracked

Legacy same-requirement reuse candidates: `TC-AI-007-01`, `TC-AI-007-02`, `TC-AT10`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_reporting.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-007-004 — Reject invented results and overwritten edits

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-007-004` is not created. Verification duty `TASK-FR-AI-007-03` (qualification); source `docs/backlog/backlog.csv` record 9, exact block `806d90a9425df34cb8e1c662ddbf1e6674147a23ec1a3e47cd1fe8451029089a`.

**Original preconditions**

1. a draft with accepted human edits

**Original actions**

1. the assistant regenerates it or attempts to create a new official snapshot, invent a result or remove a mandatory caveat

**Exact source oracles — all required**

1. the snapshot, result and caveat changes are refused
2. accepted human edits are not overwritten without an explicit reviewed diff

Legacy same-requirement reuse candidates: `TC-AI-007-01`, `TC-AI-007-02`, `TC-AT10`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_reporting.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
