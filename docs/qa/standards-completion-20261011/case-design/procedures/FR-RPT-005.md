## QA v1.3 — source-bound case design (proposed)

Story `FR-RPT-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-RPT-005-001` / `TC-IMPRANA-FR-RPT-005-001` | `REV_7a0032db3fa0ecb064c2da58a716fccb4c183d3a0795cf90ac7faae6a98a889e` / `REV_3f7c4bab01cc6923847c66533d0b98820376df622af0488cdd722a9a343bf697` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-005-002` / `TC-IMPRANA-FR-RPT-005-002` | `REV_649759d6edd055bbf0aa932faeb9fa1126ff8c9328d0b66521fcf8437f2d6aee` / `REV_b4fb0be6cf48333f10a30f0fb5319ecbb4330b23eb9bef194f83f26c23ae9245` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-005-003` / `TC-IMPRANA-FR-RPT-005-003` | `REV_3eaed4477b7f7f8160f5764a14fa4445a97253f13aa1f35efa94bb92006d34d5` / `REV_2cdbe510be3203fa2ab764735eed6221f7848e2c185a506d51d829c11bb063d7` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-005-004` / `TC-IMPRANA-FR-RPT-005-004` | `REV_540d2e57f3f9ce1e38a85b8d571d4817ac4bcbaef42b7cca1ea3b8d1fe43e3ea` / `REV_e0af3ed8b8cc71035f9ea845a1a3d41f2d574eb9b9a23894ed2212f8f52cd5e1` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-RPT-005-001 — Export a large report faithfully

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-005-001` is not created. Verification duty `TASK-FR-RPT-005-03` (qualification); source `docs/backlog/backlog.csv` record 300, exact block `7a0032db3fa0ecb064c2da58a716fccb4c183d3a0795cf90ac7faae6a98a889e`.

**Original preconditions**

1. an approved 50-page report with twenty charts

**Original actions**

1. the MEL Manager exports it

**Exact source oracles — all required**

1. no values are clipped
2. no caveats are missing
3. all values agree exactly with the snapshot
4. the artifact receipt identifies the report version, format and access expiry

Legacy same-requirement reuse candidates: `TC-RPT-005-01`, `TC-RPT-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-005-002 — Export job validates content and structure

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-005-002` is not created. Verification duty `TASK-FR-RPT-005-03` (qualification); source `docs/backlog/backlog.csv` record 300, exact block `649759d6edd055bbf0aa932faeb9fa1126ff8c9328d0b66521fcf8437f2d6aee`.

**Original preconditions**

1. a report export in DOCX or PDF or a table export in XLSX or CSV

**Original actions**

1. the export job runs

**Exact source oracles — all required**

1. it validates snapshot, fonts, page breaks, headings, tables, figures, units, caveats and filter context
2. accessible standard templates preserve headings and table structure

Legacy same-requirement reuse candidates: `TC-RPT-005-01`, `TC-RPT-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-005-003 — Reject marking a failed rendering as published

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-005-003` is not created. Verification duty `TASK-FR-RPT-005-03` (qualification); source `docs/backlog/backlog.csv` record 300, exact block `3eaed4477b7f7f8160f5764a14fa4445a97253f13aa1f35efa94bb92006d34d5`.

**Original preconditions**

1. an export job encounters a rendering failure

**Original actions**

1. the job ends

**Exact source oracles — all required**

1. publication is not marked successful

Legacy same-requirement reuse candidates: `TC-RPT-005-01`, `TC-RPT-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-005-004 — Reject unremediated conformance claims

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-005-004` is not created. Verification duty `TASK-FR-RPT-005-03` (qualification); source `docs/backlog/backlog.csv` record 300, exact block `540d2e57f3f9ce1e38a85b8d571d4817ac4bcbaef42b7cca1ea3b8d1fe43e3ea`.

**Original preconditions**

1. a report containing user supplied inaccessible content

**Original actions**

1. it is exported

**Exact source oracles — all required**

1. the inaccessible content is flagged
2. the artifact is not claimed conformant until it is remediated

Legacy same-requirement reuse candidates: `TC-RPT-005-01`, `TC-RPT-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
