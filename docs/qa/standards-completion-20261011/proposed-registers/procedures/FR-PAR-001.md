## QA v1.3 — source-bound case design (proposed)

Story `FR-PAR-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PAR-001-001` / `TC-IMPRANA-FR-PAR-001-001` | `REV_14428e9659ef0c1e24d05ec91d90af3a23a94000e1e496c347591a070b9d9706` / `REV_c3758d98a011dfeb6bec9a976a10c541d8e16c5b8bdbc279f652e2265b157ef3` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PAR-001-002` / `TC-IMPRANA-FR-PAR-001-002` | `REV_a27e781246e40b24b9c5d2c872da13953fb000df282292c778c679411a1e0c41` / `REV_7b55cdbec0d31957118321416e26fb3d6104c28af5f4a245bccb7e2ad958f01a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PAR-001-003` / `TC-IMPRANA-FR-PAR-001-003` | `REV_118633bcf445a9da73cc7668d7fba730567f21bb6da605b845e60968f19a516c` / `REV_79917286b52c565d0ad3f2c41c588bf6a9e909ccf80eea717f67c62e2079cd4d` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PAR-001-001 — Only the registry-enabled programme exposes a registry workspace

Source persona: Programme Manager. Proposed fixture `FIX-FR-PAR-001-001` is not created. Verification duty `TASK-FR-PAR-001-03` (qualification); source `docs/backlog/backlog.csv` record 280, exact block `14428e9659ef0c1e24d05ec91d90af3a23a94000e1e496c347591a070b9d9706`.

**Original preconditions**

1. a Programme Manager creates an aggregate-only education programme
2. creates a registry-enabled participant programme

**Original actions**

1. they open each programme

**Exact source oracles — all required**

1. only the participant programme exposes the configured registry workspace

Legacy same-requirement reuse candidates: `TC-PAR-001-01`, `TC-PAR-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PAR-001-002 — Configure registry entities without national identifiers

Source persona: Programme Manager. Proposed fixture `FIX-FR-PAR-001-002` is not created. Verification duty `TASK-FR-PAR-001-03` (qualification); source `docs/backlog/backlog.csv` record 280, exact block `a27e781246e40b24b9c5d2c872da13953fb000df282292c778c679411a1e0c41`.

**Original preconditions**

1. a registry-enabled programme

**Original actions**

1. the Programme Manager selects entity types and necessary attributes

**Exact source oracles — all required**

1. the system issues a programme pseudonym
2. participants, households, groups, institutions, facilities and sites can be registered without mandatory national identifiers
3. entity types and relationships are explicit

Legacy same-requirement reuse candidates: `TC-PAR-001-01`, `TC-PAR-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PAR-001-003 — Reject switching to a registry without privacy review

Source persona: Programme Manager. Proposed fixture `FIX-FR-PAR-001-003` is not created. Verification duty `TASK-FR-PAR-001-03` (qualification); source `docs/backlog/backlog.csv` record 280, exact block `118633bcf445a9da73cc7668d7fba730567f21bb6da605b845e60968f19a516c`.

**Original preconditions**

1. an aggregate-only programme

**Original actions**

1. a switch to registry-enabled mode is attempted without privacy review and field configuration

**Exact source oracles — all required**

1. the switch is refused
2. no empty personal records are created

Legacy same-requirement reuse candidates: `TC-PAR-001-01`, `TC-PAR-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
