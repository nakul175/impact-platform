## QA v1.3 — source-bound case design (proposed)

Story `FR-PRV-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRV-001-001` / `TC-IMPRANA-FR-PRV-001-001` | `REV_25029ba8f3f1712b5ed982904f107f45c0fe79240b8362eda518d565e2dfb6a8` / `REV_4eccce1375dacebb39029dfa70bdc09e07e130f83e5942c6ed5903cb04eb3912` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-001-002` / `TC-IMPRANA-FR-PRV-001-002` | `REV_3b19b0831cc3107a1c2c173f47a9832b7d21bde0e063df5efd71520e3eda421f` / `REV_f4fa31977cfdfb2cb395fa6192ea75b465984ac4f559278d25a8ba74708b0ff6` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-001-003` / `TC-IMPRANA-FR-PRV-001-003` | `REV_e4bf905d2785805204854dfee244969a2d46b032b7fc65b6e334e0a06d577112` / `REV_ef0fe3f45560e511b36d4767d910a03c52dd7b47ce6c60fb794faf229719e4bc` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-001-004` / `TC-IMPRANA-FR-PRV-001-004` | `REV_68894b469ec5594ae7a77523026cc5a1775e23f917f0b8f69321517db3d3637b` / `REV_3956868c97e38b2dc5833c29570c03dcee774ed48320b889578213ed48878f48` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRV-001-001 — New fields are classified

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-001-001` is not created. Verification duty `TASK-FR-PRV-001-03` (qualification); source `docs/backlog/backlog.csv` record 126, exact block `25029ba8f3f1712b5ed982904f107f45c0fe79240b8362eda518d565e2dfb6a8`.

**Original preconditions**

1. a new data field or source

**Original actions**

1. it is added

**Exact source oracles — all required**

1. it receives classification, purpose, owner and retention
2. it inherits the stricter source classification by default

Legacy same-requirement reuse candidates: `TC-PRV-001-01`, `TC-PRV-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `apps/api/impact_api/ai_policy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-001-002 — Reclassification is reviewed

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-001-002` is not created. Verification duty `TASK-FR-PRV-001-03` (qualification); source `docs/backlog/backlog.csv` record 126, exact block `3b19b0831cc3107a1c2c173f47a9832b7d21bde0e063df5efd71520e3eda421f`.

**Original preconditions**

1. a request to reclassify a field

**Original actions**

1. it is submitted

**Exact source oracles — all required**

1. it requires review
2. it shows the affected forms, exports, indexes and AI policies

Legacy same-requirement reuse candidates: `TC-PRV-001-01`, `TC-PRV-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `apps/api/impact_api/ai_policy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-001-003 — Restricted field stays out of ordinary channels

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-001-003` is not created. Verification duty `TASK-FR-PRV-001-03` (qualification); source `docs/backlog/backlog.csv` record 126, exact block `e4bf905d2785805204854dfee244969a2d46b032b7fc65b6e334e0a06d577112`.

**Original preconditions**

1. a restricted participant field

**Original actions**

1. its values are collected

**Exact source oracles — all required**

1. they are absent from ordinary logs, analyst views, exports and unapproved model inputs

Legacy same-requirement reuse candidates: `TC-PRV-001-01`, `TC-PRV-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `apps/api/impact_api/ai_policy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-001-004 — Reject downgrades and unclassified collection

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-001-004` is not created. Verification duty `TASK-FR-PRV-001-03` (qualification); source `docs/backlog/backlog.csv` record 126, exact block `68894b469ec5594ae7a77523026cc5a1775e23f917f0b8f69321517db3d3637b`.

**Original preconditions**

1. derived data or an unclassified sensitive field

**Original actions**

1. derived data attempts to downgrade its own classification or production collection starts

**Exact source oracles — all required**

1. the downgrade is refused
2. unclassified sensitive production collection is blocked
3. credentials are handled as secrets, not as ordinary content

Legacy same-requirement reuse candidates: `TC-PRV-001-01`, `TC-PRV-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `apps/api/impact_api/ai_policy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
