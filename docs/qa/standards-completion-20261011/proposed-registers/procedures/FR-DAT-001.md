## QA v1.3 — source-bound case design (proposed)

Story `FR-DAT-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DAT-001-001` / `TC-IMPRANA-FR-DAT-001-001` | `REV_d37c9d64344ae710d650856029e8852eefb94c8777b120c2886494c34c9b6fe3` / `REV_f9c492f54249b60136ad13b7fba715a53fa82cb16fff287224810b0d88a77f1a` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-001-002` / `TC-IMPRANA-FR-DAT-001-002` | `REV_12ebde583d850a4145f469840cc50bac396004d008931f1a102585017fa1e3e5` / `REV_039e7f5595bf84c8e3e02aedb874a61c9005fb80328aab58223116a6ef37fd30` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-001-003` / `TC-IMPRANA-FR-DAT-001-003` | `REV_5353a28c7ae6ac7890a82f143e3fdaaf6edaefbb1c9b391b7c15830c1c769d99` / `REV_c8b889db7240c562d8741a2e6f8bbbf2b8346a8ec8b89210f81f7c30daedcb9d` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DAT-001-001 — Preview exact interpretation before commit

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-001-001` is not created. Verification duty `TASK-FR-DAT-001-03` (qualification); source `docs/backlog/backlog.csv` record 69, exact block `d37c9d64344ae710d650856029e8852eefb94c8777b120c2886494c34c9b6fe3`.

**Original preconditions**

1. a file containing 00123, a 20 digit ID, 03/04/2026 and a quoted comma

**Original actions**

1. the Data Steward previews the import with an explicit date pattern

**Exact source oracles — all required**

1. raw and interpreted values are shown side by side for each value
2. 00123 and the 20 digit ID are kept as text with all digits and leading zeros preserved
3. the quoted comma remains within one field

Legacy same-requirement reuse candidates: `TC-DAT-001-01`, `TC-DAT-001-02`, `TC-AT23`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-001-002 — Formulas follow the declared mode

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-001-002` is not created. Verification duty `TASK-FR-DAT-001-03` (qualification); source `docs/backlog/backlog.csv` record 69, exact block `12ebde583d850a4145f469840cc50bac396004d008931f1a102585017fa1e3e5`.

**Original preconditions**

1. a file containing formulas

**Original actions**

1. it is imported

**Exact source oracles — all required**

1. formulas are imported as permitted values or rejected according to the declared mode

Legacy same-requirement reuse candidates: `TC-DAT-001-01`, `TC-DAT-001-02`, `TC-AT23`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-001-003 — Reject ambiguous or unsafe input

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-001-003` is not created. Verification duty `TASK-FR-DAT-001-03` (qualification); source `docs/backlog/backlog.csv` record 69, exact block `5353a28c7ae6ac7890a82f143e3fdaaf6edaefbb1c9b391b7c15830c1c769d99`.

**Original preconditions**

1. a date such as 03/04/2026 with no explicit date pattern

**Original actions**

1. the import is previewed

**Exact source oracles — all required**

1. an explicit pattern is required before commit
2. mixed-type values produce row errors
3. file safety checks run before any parsing

Legacy same-requirement reuse candidates: `TC-DAT-001-01`, `TC-DAT-001-02`, `TC-AT23`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
