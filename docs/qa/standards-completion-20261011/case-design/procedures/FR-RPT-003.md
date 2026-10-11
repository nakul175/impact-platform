## QA v1.3 — source-bound case design (proposed)

Story `FR-RPT-003` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-RPT-003-001` / `TC-IMPRANA-FR-RPT-003-001` | `REV_6cecd4dc764a0afe05e4e3178ddbb31583a68733729f81da55abc24f407133cc` / `REV_cc778c515194a0b45724800706671a3150ee76909f7a2e5fc1ae6f2702a4a30a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-003-002` / `TC-IMPRANA-FR-RPT-003-002` | `REV_e519b1ddbfcfa58e5c34efa0885167e70f9061543f206d9d3cdb728b17f43ee7` / `REV_5c649ce2cd9e6efa41f34771d33fbb7a73467dae5fbd498aa5f90a585cd5d6ac` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-003-003` / `TC-IMPRANA-FR-RPT-003-003` | `REV_d2683f6ad1d95cc419a0ee95cc2d7c5642e907d335b0af5bda952d4c14c2a382` / `REV_8f5b9fb3dcbb530ab1830e527d0f41fe674abc5d8e37aab8936a5ffa0224938b` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-RPT-003-001 — Regenerate an old quarter after a live correction

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-003-001` is not created. Verification duty `TASK-FR-RPT-003-03` (qualification); source `docs/backlog/backlog.csv` record 139, exact block `6cecd4dc764a0afe05e4e3178ddbb31583a68733729f81da55abc24f407133cc`.

**Original preconditions**

1. a report for an old quarter was created from a locked snapshot
2. the live source data has since been corrected

**Original actions**

1. the MEL Manager regenerates the old quarter report

**Exact source oracles — all required**

1. its authorised numeric content stays unchanged
2. the later correction is a separate report version

Legacy same-requirement reuse candidates: `TC-RPT-003-01`, `TC-RPT-003-02`, `TC-AT07`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-003-002 — Regeneration uses the same versions

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-003-002` is not created. Verification duty `TASK-FR-RPT-003-03` (qualification); source `docs/backlog/backlog.csv` record 139, exact block `e519b1ddbfcfa58e5c34efa0885167e70f9061543f206d9d3cdb728b17f43ee7`.

**Original preconditions**

1. a report created from a locked snapshot

**Original actions**

1. the report is regenerated

**Exact source oracles — all required**

1. it uses the same definition, target, result, evidence and configuration versions
2. the rendering version is recorded separately from the content version

Legacy same-requirement reuse candidates: `TC-RPT-003-01`, `TC-RPT-003-02`, `TC-AT07`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-003-003 — Reject reconstructing lawfully deleted evidence

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-003-003` is not created. Verification duty `TASK-FR-RPT-003-03` (qualification); source `docs/backlog/backlog.csv` record 139, exact block `d2683f6ad1d95cc419a0ee95cc2d7c5642e907d335b0af5bda952d4c14c2a382`.

**Original preconditions**

1. evidence in a report has been lawfully deleted

**Original actions**

1. the report is regenerated or accessed

**Exact source oracles — all required**

1. the withheld evidence is disclosed as withheld or the artifact is withdrawn as required
2. the deleted content is not reconstructed to preserve visual identity
3. numeric history is retained only where lawful

Legacy same-requirement reuse candidates: `TC-RPT-003-01`, `TC-RPT-003-02`, `TC-AT07`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
