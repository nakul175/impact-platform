## QA v1.3 — source-bound case design (proposed)

Story `FR-DAT-003` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DAT-003-001` / `TC-IMPRANA-FR-DAT-003-001` | `REV_f9a1d48040b55597859c0bd57566774fe0eb3b7be34c6a11e6819657e6aa2618` / `REV_df6f1245ac0e7088063e946dbc5a535f06ad6456e442e641adfe879df95639b4` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-003-002` / `TC-IMPRANA-FR-DAT-003-002` | `REV_1d46480cd2eda25ef1d6a339a22181e599dbf4bf83b94173822e031968424762` / `REV_088ab5d225e7763ca4dfe4ec8ebe47fca9b42e54f6272fa3e6e4a58374506585` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-003-003` / `TC-IMPRANA-FR-DAT-003-003` | `REV_8262ade5f4206d6db37f0299d35decf67ddffd26afe1b6da61da7986bcf38d75` / `REV_1bc1393ff6b51939a39575521531047803f7e5f55d15c93a5047181a8388d0a6` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DAT-003-001 — Keyed reloads do not duplicate achievements

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-003-001` is not created. Verification duty `TASK-FR-DAT-003-03` (qualification); source `docs/backlog/backlog.csv` record 212, exact block `f9a1d48040b55597859c0bd57566774fe0eb3b7be34c6a11e6819657e6aa2618`.

**Original preconditions**

1. a keyed file

**Original actions**

1. it is loaded twice and then loaded a third time with one row revised

**Exact source oracles — all required**

1. the second run creates no new achievement
2. the third run creates one correction revision

Legacy same-requirement reuse candidates: `TC-DAT-003-01`, `TC-DAT-003-02`, `TC-AT23`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-003-002 — Preview and commit record every effect

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-003-002` is not created. Verification duty `TASK-FR-DAT-003-03` (qualification); source `docs/backlog/backlog.csv` record 212, exact block `1d46480cd2eda25ef1d6a339a22181e599dbf4bf83b94173822e031968424762`.

**Original preconditions**

1. an import mode, source namespace and stable key are selected

**Original actions**

1. the import is previewed and committed

**Exact source oracles — all required**

1. the preview computes inserts, revisions, unchanged duplicates and removals
2. commit records original and resulting revision references for every effect

Legacy same-requirement reuse candidates: `TC-DAT-003-01`, `TC-DAT-003-02`, `TC-AT23`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-003-003 — Reject unsafe append and implied deletion

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-003-003` is not created. Verification duty `TASK-FR-DAT-003-03` (qualification); source `docs/backlog/backlog.csv` record 212, exact block `8262ade5f4206d6db37f0299d35decf67ddffd26afe1b6da61da7986bcf38d75`.

**Original preconditions**

1. an append without reliable keys or a replacement without explicit scope

**Original actions**

1. it is previewed

**Exact source oracles — all required**

1. the append warns that deduplication cannot establish entity uniqueness
2. the replacement is refused until explicit scope and deletion impact are approved
3. records absent from a partial file are not deleted

Legacy same-requirement reuse candidates: `TC-DAT-003-01`, `TC-DAT-003-02`, `TC-AT23`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
