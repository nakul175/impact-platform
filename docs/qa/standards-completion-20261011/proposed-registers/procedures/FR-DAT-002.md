## QA v1.3 — source-bound case design (proposed)

Story `FR-DAT-002` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DAT-002-001` / `TC-IMPRANA-FR-DAT-002-001` | `REV_bf4607b453d8bc270bdab578d7f2179008c435ee5acc02d35d2785eaaf52fa17` / `REV_e7a27b7c9f22d15eee570a1d3a2fdfc9a827ca30b93b8771da855d394577f043` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-002-002` / `TC-IMPRANA-FR-DAT-002-002` | `REV_b1d9f3a64bbb8f4f766b772050284592cd4da78de3f3a2e933fba82d2ed1886d` / `REV_d63f82015a7734a8bfaedede1e75162c1655d45d476046cd92adffa7161403c9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-002-003` / `TC-IMPRANA-FR-DAT-002-003` | `REV_957de4785e14f4faedd0269f3f6fd04433fdbedf9261dc572c2733ee0f94fff3` / `REV_453b832a0e1d02d25a83a52cfbf9b55627e8860da1f71e60eaf72954a56c0084` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DAT-002-001 — Preview shows mapping issues

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-002-001` is not created. Verification duty `TASK-FR-DAT-002-03` (qualification); source `docs/backlog/backlog.csv` record 70, exact block `bf4607b453d8bc270bdab578d7f2179008c435ee5acc02d35d2785eaaf52fa17`.

**Original preconditions**

1. a mapping version

**Original actions**

1. the import is previewed

**Exact source oracles — all required**

1. unmatched required fields, dropped columns, conversion errors and sample outcomes are shown
2. AI suggestions remain unchecked proposals until individually accepted or edited

Legacy same-requirement reuse candidates: `TC-DAT-002-01`, `TC-DAT-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-002-002 — Reordered columns keep known bindings

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-002-002` is not created. Verification duty `TASK-FR-DAT-002-03` (qualification); source `docs/backlog/backlog.csv` record 70, exact block `b1d9f3a64bbb8f4f766b772050284592cd4da78de3f3a2e933fba82d2ed1886d`.

**Original preconditions**

1. a recurring source with an approved mapping

**Original actions**

1. its columns are reordered and one numeric field is renamed

**Exact source oracles — all required**

1. known bindings are preserved
2. the unknown mapping is paused instead of shifting values

Legacy same-requirement reuse candidates: `TC-DAT-002-01`, `TC-DAT-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-002-003 — Reject positional identity and stale previews

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-002-003` is not created. Verification duty `TASK-FR-DAT-002-03` (qualification); source `docs/backlog/backlog.csv` record 70, exact block `957de4785e14f4faedd0269f3f6fd04433fdbedf9261dc572c2733ee0f94fff3`.

**Original preconditions**

1. a source column is renamed or changes type

**Original actions**

1. the import runs

**Exact source oracles — all required**

1. reviewed remapping is required
2. column position alone is never used as stable identity
3. any existing preview expires when the source or mapping changes

Legacy same-requirement reuse candidates: `TC-DAT-002-01`, `TC-DAT-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
