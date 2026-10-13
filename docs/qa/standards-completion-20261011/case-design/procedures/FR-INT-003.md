## QA v1.3 — source-bound case design (proposed)

Story `FR-INT-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-INT-003-001` / `TC-IMPRANA-FR-INT-003-001` | `REV_c7ac70593aca76c271cfe9d28953ee5b0a3f4bcc81f491bb30c7e794dd5f58ec` / `REV_0a9a509d30a6a684cedc04c6daad46ac670429d7a8447947ce97b793c3320330` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-003-002` / `TC-IMPRANA-FR-INT-003-002` | `REV_e2b5927529d664c7f192c7cd33f5e7fe635904ac4348cc8697eb40c94063d8cc` / `REV_15a8c84788e6c6b6ef427bbe2a38349e5dce1427ae6c2327dfe4e1993fd263c8` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-003-003` / `TC-IMPRANA-FR-INT-003-003` | `REV_602a54a88bc43eddaa4d0ee3bcb3369c87aba08fde67f2f5d5e5762abc33165b` / `REV_9172f67c79940e60d3d9c6cab92ac21ed8ba6f4009b09329fc646b80940f83e9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-003-004` / `TC-IMPRANA-FR-INT-003-004` | `REV_493f27251d3661e55632c23ca630f44a1c69dc2db8523bdecfffa6cd640b6a7d` / `REV_10d13a876a0614585cf9c86ecf7a4d63a733958640a98a0c686b3e8e7263be41` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-INT-003-001 — Resume an interrupted run

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-003-001` is not created. Verification duty `TASK-FR-INT-003-03` (qualification); source `docs/backlog/backlog.csv` record 103, exact block `c7ac70593aca76c271cfe9d28953ee5b0a3f4bcc81f491bb30c7e794dd5f58ec`.

**Original preconditions**

1. a run of 100 records is interrupted after 60

**Original actions**

1. the run resumes

**Exact source oracles — all required**

1. the first 60 records are recognised
2. exactly 40 remaining intended effects occur

Legacy same-requirement reuse candidates: `TC-INT-003-01`, `TC-INT-003-02`, `SEC-027`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-003-002 — Transient failures follow the default retry schedule

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-003-002` is not created. Verification duty `TASK-FR-INT-003-03` (qualification); source `docs/backlog/backlog.csv` record 103, exact block `e2b5927529d664c7f192c7cd33f5e7fe635904ac4348cc8697eb40c94063d8cc`.

**Original preconditions**

1. a run encounters a transient failure

**Original actions**

1. retries are attempted

**Exact source oracles — all required**

1. they follow the default schedule of one, five, fifteen and sixty minutes
2. the item then goes to manual review

Legacy same-requirement reuse candidates: `TC-INT-003-01`, `TC-INT-003-02`, `SEC-027`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-003-003 — Permanent failures pause and poison items are quarantined

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-003-003` is not created. Verification duty `TASK-FR-INT-003-03` (qualification); source `docs/backlog/backlog.csv` record 103, exact block `602a54a88bc43eddaa4d0ee3bcb3369c87aba08fde67f2f5d5e5762abc33165b`.

**Original preconditions**

1. a run encounters a poison item or a permanent schema or policy failure

**Original actions**

1. the run processes it

**Exact source oracles — all required**

1. a poison item is quarantined while permitted partial processing continues and reconciles outcomes
2. a permanent schema or policy failure pauses the run

Legacy same-requirement reuse candidates: `TC-INT-003-01`, `TC-INT-003-02`, `SEC-027`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-003-004 — Reject advancing the checkpoint past unapplied items

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-003-004` is not created. Verification duty `TASK-FR-INT-003-03` (qualification); source `docs/backlog/backlog.csv` record 103, exact block `493f27251d3661e55632c23ca630f44a1c69dc2db8523bdecfffa6cd640b6a7d`.

**Original preconditions**

1. required items in a run have not been applied

**Original actions**

1. the run attempts to commit its checkpoint

**Exact source oracles — all required**

1. the checkpoint is not advanced past those items unless a recoverable exception manifest exists

Legacy same-requirement reuse candidates: `TC-INT-003-01`, `TC-INT-003-02`, `SEC-027`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
