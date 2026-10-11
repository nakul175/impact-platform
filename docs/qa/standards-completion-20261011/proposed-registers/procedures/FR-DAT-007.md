## QA v1.3 — source-bound case design (proposed)

Story `FR-DAT-007` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DAT-007-001` / `TC-IMPRANA-FR-DAT-007-001` | `REV_6e0431008bbeb12deddd97dc9c721be3dc687186831c75b81951d56b865cc555` / `REV_b4debbf5813acaa19cd484fc6d180896c7cb8a976770d445b33c0cd39fe57123` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-007-002` / `TC-IMPRANA-FR-DAT-007-002` | `REV_695b4d78fa8b021cf9d9479af634694be9e21d6ae29fe9d09195c35ee9ec0087` / `REV_c6c21d378792be2609f916291c96b01b8261acd5520eb389d72a983b16afaecc` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-007-003` / `TC-IMPRANA-FR-DAT-007-003` | `REV_45350400c8f2991d764fc2a800433d79085a40dfd7d431427807f3a986fd780d` / `REV_240b8ea9d5a9e716a732810464cfe2df4bb37fb965fe3d130d18e5030f3d9a42` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DAT-007-001 — Added optional field is ignored with notice

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-007-001` is not created. Verification duty `TASK-FR-DAT-007-03` (qualification); source `docs/backlog/backlog.csv` record 215, exact block `6e0431008bbeb12deddd97dc9c721be3dc687186831c75b81951d56b865cc555`.

**Original preconditions**

1. a recurring load with an added optional field

**Original actions**

1. it is compared with the approved source contract

**Exact source oracles — all required**

1. the field may be ignored and a notice is shown

Legacy same-requirement reuse candidates: `TC-DAT-007-01`, `TC-DAT-007-02`, `TC-AT23`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-007-002 — Type change pauses dependent processing

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-007-002` is not created. Verification duty `TASK-FR-DAT-007-03` (qualification); source `docs/backlog/backlog.csv` record 215, exact block `695b4d78fa8b021cf9d9479af634694be9e21d6ae29fe9d09195c35ee9ec0087`.

**Original preconditions**

1. a numerator column changes from decimal to free text

**Original actions**

1. the recurring load runs

**Exact source oracles — all required**

1. affected processing pauses for review
2. dependent result freshness becomes failed or stale until a reviewed mapping resolves it

Legacy same-requirement reuse candidates: `TC-DAT-007-01`, `TC-DAT-007-02`, `TC-AT23`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-007-003 — Reject silent coercion

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-007-003` is not created. Verification duty `TASK-FR-DAT-007-03` (qualification); source `docs/backlog/backlog.csv` record 215, exact block `45350400c8f2991d764fc2a800433d79085a40dfd7d431427807f3a986fd780d`.

**Original preconditions**

1. a load with missing required, renamed, type changed or unit changed fields

**Original actions**

1. it is processed

**Exact source oracles — all required**

1. incompatible text is not treated as zero
2. a new date locale is not silently inferred
3. unaffected validated data proceeds only when partial mode was approved

Legacy same-requirement reuse candidates: `TC-DAT-007-01`, `TC-DAT-007-02`, `TC-AT23`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
