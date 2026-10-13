## QA v1.3 — source-bound case design (proposed)

Story `FR-DAT-004` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DAT-004-001` / `TC-IMPRANA-FR-DAT-004-001` | `REV_4d46fbfd5bfad5aa0169b517e6a0dced39b1479f76ff056ca706dbc81328f7ea` / `REV_b3d2042ca9d4d8ee83ea919b2bbb9b5389cd6c1da1c21c2657180056cf6a14a4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-004-002` / `TC-IMPRANA-FR-DAT-004-002` | `REV_5e5b5da50752ff1c5e0592cad1e2cc2596aecc3afd2979d18264702f290df4ba` / `REV_75f24928da1b705baf3d4500ab450dfd7e3ed6df5ed98610869964538874dfb9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-004-003` / `TC-IMPRANA-FR-DAT-004-003` | `REV_35f36ceb513ccfc8a09a2617b96e89979c84789fae1c7a15cc68e92b8606099e` / `REV_9df317ecd226977d4b75c053c217d1d6c6d79cc41d22af75d5177ce4670d6dbf` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DAT-004-001 — Partial mode reconciles all rows

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-004-001` is not created. Verification duty `TASK-FR-DAT-004-03` (qualification); source `docs/backlog/backlog.csv` record 71, exact block `4d46fbfd5bfad5aa0169b517e6a0dced39b1479f76ff056ca706dbc81328f7ea`.

**Original preconditions**

1. 100 rows with 90 valid, five duplicates and five invalid
2. partial mode was selected before execution

**Original actions**

1. the import runs

**Exact source oracles — all required**

1. eligible rows are committed and the exact manifest is returned
2. all 100 outcomes reconcile as accepted insert, accepted update, unchanged duplicate, rejected, quarantined or unprocessed
3. only the five corrected rows are retried

Legacy same-requirement reuse candidates: `TC-DAT-004-01`, `TC-DAT-004-02`, `SEC-024`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-004-002 — Atomic mode commits nothing on a blocking failure

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-004-002` is not created. Verification duty `TASK-FR-DAT-004-03` (qualification); source `docs/backlog/backlog.csv` record 71, exact block `5e5b5da50752ff1c5e0592cad1e2cc2596aecc3afd2979d18264702f290df4ba`.

**Original preconditions**

1. atomic mode was selected before execution

**Original actions**

1. any blocking row fails

**Exact source oracles — all required**

1. no rows are committed

Legacy same-requirement reuse candidates: `TC-DAT-004-01`, `TC-DAT-004-02`, `SEC-024`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-004-003 — Reject altered raw input or false rollback claims

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-004-003` is not created. Verification duty `TASK-FR-DAT-004-03` (qualification); source `docs/backlog/backlog.csv` record 71, exact block `35f36ceb513ccfc8a09a2617b96e89979c84789fae1c7a15cc68e92b8606099e`.

**Original preconditions**

1. an import with rejected rows that is later cancelled

**Original actions**

1. the results are reviewed

**Exact source oracles — all required**

1. rejected rows carry safe field errors and the raw input remains unchanged
2. the cancelled job identifies committed rows and never claims full rollback
3. an import cannot execute until its mode is selected

Legacy same-requirement reuse candidates: `TC-DAT-004-01`, `TC-DAT-004-02`, `SEC-024`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
