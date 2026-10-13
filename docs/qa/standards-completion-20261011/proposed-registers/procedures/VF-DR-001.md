## QA v1.3 — source-bound case design (proposed)

Story `VF-DR-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-DR-001-001` / `TC-IMPRANA-VF-DR-001-001` | `REV_678bbd5c39ca10324a68230bd4724e093ee0abdab6681c1cb98b45ce5a6e648e` / `REV_7632c341bb1250c8ca3cd093477f9880b6b8778c7d2ed289e16beb1743cf7667` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DR-001-002` / `TC-IMPRANA-VF-DR-001-002` | `REV_c74efc0c0237ab4dcc271a6ac37ff08410295e4710018ac119b8dac9a1cac27d` / `REV_3af194c26024e81200e86d263fec69249cca6931a681c7c41fb08b45f6611743` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DR-001-003` / `TC-IMPRANA-VF-DR-001-003` | `REV_6cd7c7a831e81a85704c6a77b579d166b9f3cd727643c5cf775a56dadf9a60bc` / `REV_c86374560ad36ef6447891e52709e23b7b69f57ab55552f37c9a537e93bc662d` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DR-001-004` / `TC-IMPRANA-VF-DR-001-004` | `REV_de9890863125cab1931e58561fab8830cebb6539ca97ba826430aadc1f500822` / `REV_74ae696c9b8e0e6dc567cb75eadc6930e76dd70e9e12bf6876b421f9bc27bd32` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-DR-001-001 — Recovery meets recovery point and recovery time objectives

Source persona: Platform Operator. Proposed fixture `FIX-VF-DR-001-001` is not created. Verification duty `TASK-VF-DR-001-03` (qualification); source `docs/backlog/backlog.csv` record 117, exact block `678bbd5c39ca10324a68230bd4724e093ee0abdab6681c1cb98b45ce5a6e648e`.

**Original preconditions**

1. a simulated regional disaster has been declared for the standard qualified deployment

**Original actions**

1. the service is restored

**Exact source oracles — all required**

1. the recovery point is at most 15 minutes
2. service is recovered within 4 hours of incident declaration

Legacy same-requirement reuse candidates: `TC-VF-DR-001`, `TC-AT19`, `SEC-042`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DR-001-002 — Recovery stays in permitted regions and is complete

Source persona: Platform Operator. Proposed fixture `FIX-VF-DR-001-002` is not created. Verification duty `TASK-VF-DR-001-03` (qualification); source `docs/backlog/backlog.csv` record 117, exact block `c74efc0c0237ab4dcc271a6ac37ff08410295e4710018ac119b8dac9a1cac27d`.

**Original preconditions**

1. a restore is in progress

**Original actions**

1. recovery completes

**Exact source oracles — all required**

1. it has occurred only in a permitted region
2. files, configuration and governance state are restored
3. records and attachments are reconciled against the latest accepted receipts

Legacy same-requirement reuse candidates: `TC-VF-DR-001`, `TC-AT19`, `SEC-042`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DR-001-003 — Reject reopening with mismatched governance

Source persona: Platform Operator. Proposed fixture `FIX-VF-DR-001-003` is not created. Verification duty `TASK-VF-DR-001-03` (qualification); source `docs/backlog/backlog.csv` record 117, exact block `6cd7c7a831e81a85704c6a77b579d166b9f3cd727643c5cf775a56dadf9a60bc`.

**Original preconditions**

1. a restored environment with mismatched governance or missing deletion restrictions

**Original actions**

1. reopening is requested

**Exact source oracles — all required**

1. the service is not reopened

Legacy same-requirement reuse candidates: `TC-VF-DR-001`, `TC-AT19`, `SEC-042`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DR-001-004 — Reject a recovery report based only on backup timestamps

Source persona: Platform Operator. Proposed fixture `FIX-VF-DR-001-004` is not created. Verification duty `TASK-VF-DR-001-03` (qualification); source `docs/backlog/backlog.csv` record 117, exact block `de9890863125cab1931e58561fab8830cebb6539ca97ba826430aadc1f500822`.

**Original preconditions**

1. recovery is complete

**Original actions**

1. the recovery report is produced

**Exact source oracles — all required**

1. it states the actual lost interval and the affected accepted writes
2. a report showing only backup timestamps is rejected

Legacy same-requirement reuse candidates: `TC-VF-DR-001`, `TC-AT19`, `SEC-042`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
