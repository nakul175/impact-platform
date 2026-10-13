## QA v1.3 — source-bound case design (proposed)

Story `FR-IND-012` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IND-012-001` / `TC-IMPRANA-FR-IND-012-001` | `REV_6e4962d62437dffd3d212db187dce9a3d687eabfe3c505388c033089223aaefc` / `REV_4d7a79069261b4abdb92ca8f325944142178afcaf13a270566d75d73b0ff67a9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-012-002` / `TC-IMPRANA-FR-IND-012-002` | `REV_eaba3688c4d75cdba66ec911827b213dc45968de3e363768c3be4b8e8d1da45f` / `REV_6d19ba1ec2d8d3317c397e11f5185976e2a9f915ea506b1940d03546098129f4` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-012-003` / `TC-IMPRANA-FR-IND-012-003` | `REV_ac91d777936f6ce53262bf6acb68ffda965e7bb87a846c223e25d45e675822bf` / `REV_819661e39ace97a38e7bb928b6881df2242043cd47671f414a28042950854295` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-012-004` / `TC-IMPRANA-FR-IND-012-004` | `REV_60809f6d0aaecc6bfbdb633ab28acb27e45c6e8cd65c24ae364a318a979ab91e` / `REV_9e35646e5bca29c29fca7f9fd15495cf9bcaa3493f3eb7d7a0240737afc9a78e` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IND-012-001 — Schedule creates assigned obligations

Source persona: Programme Manager. Proposed fixture `FIX-FR-IND-012-001` is not created. Verification duty `TASK-FR-IND-012-03` (qualification); source `docs/backlog/backlog.csv` record 100, exact block `6e4962d62437dffd3d212db187dce9a3d687eabfe3c505388c033089223aaefc`.

**Original preconditions**

1. an indicator schedule with an active date range

**Original actions**

1. it is instantiated

**Exact source oracles — all required**

1. obligations are created with a collector, independent reviewer, due time and escalation owner

Legacy same-requirement reuse candidates: `TC-IND-012-01`, `TC-IND-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms_rounds.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-012-002 — Preview an assignment change

Source persona: Programme Manager. Proposed fixture `FIX-FR-IND-012-002` is not created. Verification duty `TASK-FR-IND-012-03` (qualification); source `docs/backlog/backlog.csv` record 100, exact block `eaba3688c4d75cdba66ec911827b213dc45968de3e363768c3be4b8e8d1da45f`.

**Original preconditions**

1. a collector with open work and future obligations

**Original actions**

1. the Programme Manager changes the assignment

**Exact source oracles — all required**

1. the preview shows open work and future obligations separately

Legacy same-requirement reuse candidates: `TC-IND-012-01`, `TC-IND-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms_rounds.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-012-003 — Suspended collector creates reassignment work

Source persona: Programme Manager. Proposed fixture `FIX-FR-IND-012-003` is not created. Verification duty `TASK-FR-IND-012-03` (qualification); source `docs/backlog/backlog.csv` record 100, exact block `ac91d777936f6ce53262bf6acb68ffda965e7bb87a846c223e25d45e675822bf`.

**Original preconditions**

1. a collector suspended one day before due

**Original actions**

1. the Programme Manager views the obligation

**Exact source oracles — all required**

1. it shows as unassigned
2. they can appoint an eligible replacement

Legacy same-requirement reuse candidates: `TC-IND-012-01`, `TC-IND-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms_rounds.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-012-004 — Reject silent routing on departure

Source persona: Programme Manager. Proposed fixture `FIX-FR-IND-012-004` is not created. Verification duty `TASK-FR-IND-012-03` (qualification); source `docs/backlog/backlog.csv` record 100, exact block `60809f6d0aaecc6bfbdb633ab28acb27e45c6e8cd65c24ae364a318a979ab91e`.

**Original preconditions**

1. a collector whose account has been revoked

**Original actions**

1. their obligations come due

**Exact source oracles — all required**

1. no task is sent to the revoked account
2. no obligation is marked complete
3. historic owners remain attributed

Legacy same-requirement reuse candidates: `TC-IND-012-01`, `TC-IND-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms_rounds.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
