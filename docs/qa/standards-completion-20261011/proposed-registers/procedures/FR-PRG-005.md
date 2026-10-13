## QA v1.3 — source-bound case design (proposed)

Story `FR-PRG-005` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRG-005-001` / `TC-IMPRANA-FR-PRG-005-001` | `REV_6157f3231fec5554f2bdbc7ddbadd819b5725625f0d9c9620c23e44ebb5fa6e0` / `REV_f1893b1ff312cebc25288583724b941d0afcd74b916d1898bdfd9b8a0c995419` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-005-002` / `TC-IMPRANA-FR-PRG-005-002` | `REV_eaeac3cd20c977e48f0513d0685e78aca6a0092da3a1d68d2f05344f6c738eb8` / `REV_8df79c01f19d3ee4181dedd4b4153a84505ec11c3ca36ee51d4a13c8184ac542` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-005-003` / `TC-IMPRANA-FR-PRG-005-003` | `REV_ac02fe71905f0238b2d9343bd7da82a275d9851f8270203094007b8af29cc771` / `REV_97ec58d810dd43aef019b41c84740243fb03006f4addee3d7b21356b313db56c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-005-004` / `TC-IMPRANA-FR-PRG-005-004` | `REV_62cfe9589d7dc8f4c25d23963d2c8d4f3d4def4b323f87deb3da538fc29bc7e3` / `REV_8d6b98bcf094c65f8d5b4f1cbb709c57b0cbcb61c746a17a7812ff1d79909f27` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-005-005` / `TC-IMPRANA-FR-PRG-005-005` | `REV_8d3751c472536a4e108f11ada71c1d21911de3175e115e3b48653065fb29f343` / `REV_f1b4d740722756093f3e503c0cce3524282b414220938fa42ebc88fa9712a9e3` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRG-005-001 — Bind data to a boundary version

Source persona: Data Steward. Proposed fixture `FIX-FR-PRG-005-001` is not created. Verification duty `TASK-FR-PRG-005-03` (qualification); source `docs/backlog/backlog.csv` record 294, exact block `6157f3231fec5554f2bdbc7ddbadd819b5725625f0d9c9620c23e44ebb5fa6e0`.

**Original preconditions**

1. a Data Steward in the geography editor

**Original actions**

1. they import or select a versioned hierarchy with optional permitted coordinates

**Exact source oracles — all required**

1. project and observation bindings record boundary version and effective date

Legacy same-requirement reuse candidates: `TC-PRG-005-01`, `TC-PRG-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-005-002 — Report on the old boundary after a split

Source persona: Data Steward. Proposed fixture `FIX-FR-PRG-005-002` is not created. Verification duty `TASK-FR-PRG-005-03` (qualification); source `docs/backlog/backlog.csv` record 294, exact block `eaeac3cd20c977e48f0513d0685e78aca6a0092da3a1d68d2f05344f6c738eb8`.

**Original preconditions**

1. a district that is split into two new districts

**Original actions**

1. a report on the old boundary is reproduced

**Exact source oracles — all required**

1. it uses the old boundary codes
2. future data uses the new codes

Legacy same-requirement reuse candidates: `TC-PRG-005-01`, `TC-PRG-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-005-003 — Maps follow the viewer's disclosure level

Source persona: Data Steward. Proposed fixture `FIX-FR-PRG-005-003` is not created. Verification duty `TASK-FR-PRG-005-03` (qualification); source `docs/backlog/backlog.csv` record 294, exact block `ac02fe71905f0238b2d9343bd7da82a275d9851f8270203094007b8af29cc771`.

**Original preconditions**

1. a viewer without exact coordinate permission

**Original actions**

1. they view a map

**Exact source oracles — all required**

1. locations are shown at the disclosure level allowed for them
2. generalisation uses a documented mapping

Legacy same-requirement reuse candidates: `TC-PRG-005-01`, `TC-PRG-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-005-004 — Reject rewriting old observation codes

Source persona: Data Steward. Proposed fixture `FIX-FR-PRG-005-004` is not created. Verification duty `TASK-FR-PRG-005-03` (qualification); source `docs/backlog/backlog.csv` record 294, exact block `62cfe9589d7dc8f4c25d23963d2c8d4f3d4def4b323f87deb3da538fc29bc7e3`.

**Original preconditions**

1. observations coded to an old boundary

**Original actions**

1. the boundaries change

**Exact source oracles — all required**

1. the old observation codes are not rewritten

Legacy same-requirement reuse candidates: `TC-PRG-005-01`, `TC-PRG-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-005-005 — Reject exposing or faking exact locations

Source persona: Data Steward. Proposed fixture `FIX-FR-PRG-005-005` is not created. Verification duty `TASK-FR-PRG-005-03` (qualification); source `docs/backlog/backlog.csv` record 294, exact block `8d3751c472536a4e108f11ada71c1d21911de3175e115e3b48653065fb29f343`.

**Original preconditions**

1. a viewer without separate exact coordinate permission

**Original actions**

1. they view locations

**Exact source oracles — all required**

1. exact coordinates are not shown
2. arbitrary jitter is not presented as an exact location

Legacy same-requirement reuse candidates: `TC-PRG-005-01`, `TC-PRG-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
