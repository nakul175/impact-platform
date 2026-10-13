## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-015` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-015-001` / `TC-IMPRANA-FR-SEC-015-001` | `REV_51fc05c1ee498665b4eaf01caef85f3345e74b7fbb82456db757e754c912e98a` / `REV_57f082105f8e06cd3bde4327fd3cc854c358bf31570febf46b653523a8504bcd` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-015-002` / `TC-IMPRANA-FR-SEC-015-002` | `REV_3110d98424d21f6b980e09c54482ec48d10abd45182da7935d61c5da85024626` / `REV_461872e77d02c0abbe5162ac6b35015fcbff3c8afd18399fb896ffa2a1a038c8` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-015-003` / `TC-IMPRANA-FR-SEC-015-003` | `REV_f0ee83159670cc9599fde8d49b8b3210a3ab222911a8c0ad088f96cf1c5f305f` / `REV_01c812faf67fbb8fc43c1f7c2503874fbbd7e3a37a6ab3bdc243fd789206e6b1` | manual → MANUAL recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-015-001 — Variant profile is defined

Source persona: Executive Director. Proposed fixture `FIX-FR-SEC-015-001` is not created. Verification duty `TASK-FR-SEC-015-02` (qualification); source `docs/backlog/backlog.csv` record 371, exact block `51fc05c1ee498665b4eaf01caef85f3345e74b7fbb82456db757e754c912e98a`.

**Original preconditions**

1. an enterprise deployment variant

**Original actions**

1. it is offered

**Exact source oracles — all required**

1. it has a named capability profile, region and recovery constraints, responsibilities, upgrade process, key custody and exit process
2. product screens show supported and unsupported features for that profile

Legacy same-requirement reuse candidates: `TC-SEC-015-01`, `TC-SEC-015-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-015-002 — Customer key loss behaves as documented

Source persona: Executive Director. Proposed fixture `FIX-FR-SEC-015-002` is not created. Verification duty `TASK-FR-SEC-015-02` (qualification); source `docs/backlog/backlog.csv` record 371, exact block `3110d98424d21f6b980e09c54482ec48d10abd45182da7935d61c5da85024626`.

**Original preconditions**

1. a qualified dedicated profile with a customer controlled key

**Original actions**

1. the key is lost

**Exact source oracles — all required**

1. the documented unavailable and recovery behaviour occurs
2. data is not silently moved elsewhere

Legacy same-requirement reuse candidates: `TC-SEC-015-01`, `TC-SEC-015-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-015-003 — Reject unqualified variants

Source persona: Executive Director. Proposed fixture `FIX-FR-SEC-015-003` is not created. Verification duty `TASK-FR-SEC-015-02` (qualification); source `docs/backlog/backlog.csv` record 371, exact block `f0ee83159670cc9599fde8d49b8b3210a3ab222911a8c0ad088f96cf1c5f305f`.

**Original preconditions**

1. a dedicated deployment or customer controlled key option

**Original actions**

1. it is selected through a commercial checkbox without passing equivalent functional, isolation and recovery gates

**Exact source oracles — all required**

1. it is not made available

Legacy same-requirement reuse candidates: `TC-SEC-015-01`, `TC-SEC-015-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
