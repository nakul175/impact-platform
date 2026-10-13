## QA v1.3 — source-bound case design (proposed)

Story `VF-OBS-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-OBS-001-001` / `TC-IMPRANA-VF-OBS-001-001` | `REV_acf467032a2a90294a6d31159d11885937eeda62d8206c023241b19764552565` / `REV_f2a918f320eabfede3741ff1895abcec04299599ac33ce46c352fb6e4dd0109d` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-OBS-001-002` / `TC-IMPRANA-VF-OBS-001-002` | `REV_fe69dd24630efdf2f6315b05c7ca6c2ece0c7fc6433b4477e69b513b10589546` / `REV_2643de1d9dd2186c50cf9cc5a601dfa024fb26fdf45a4a1f0362d1e5aff9cfef` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-OBS-001-003` / `TC-IMPRANA-VF-OBS-001-003` | `REV_4486a81b7bc6cd72176d02a7e402bf18333789f7d1b9c27ad47d9401fde1cd64` / `REV_120d7e69ce346e257ea0e6d7b22e389b6f3c81682e867766756af5453f48d7c4` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-OBS-001-001 — Failure is traced with one correlation reference

Source persona: Platform Operator. Proposed fixture `FIX-VF-OBS-001-001` is not created. Verification duty `TASK-VF-OBS-001-03` (qualification); source `docs/backlog/backlog.csv` record 113, exact block `acf467032a2a90294a6d31159d11885937eeda62d8206c023241b19764552565`.

**Original preconditions**

1. failures injected at report receipt, calculation, rendering and delivery

**Original actions**

1. the Platform Operator traces a failure

**Exact source oracles — all required**

1. one safe correlation reference links the user action, background jobs and integration events across the authorised stages
2. logs support tenant-scoped diagnosis while keeping audit separate

Legacy same-requirement reuse candidates: `TC-VF-OBS-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-OBS-001-002 — Critical failure alert is raised within 5 minutes

Source persona: Platform Operator. Proposed fixture `FIX-VF-OBS-001-002` is not created. Verification duty `TASK-VF-OBS-001-03` (qualification); source `docs/backlog/backlog.csv` record 113, exact block `fe69dd24630efdf2f6315b05c7ca6c2ece0c7fc6433b4477e69b513b10589546`.

**Original preconditions**

1. a critical service failure meets its defined detection condition

**Original actions**

1. the alert is generated

**Exact source oracles — all required**

1. it is created within 5 minutes of the detection condition

Legacy same-requirement reuse candidates: `TC-VF-OBS-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-OBS-001-003 — Reject missing context, secrets or late alerts

Source persona: Platform Operator. Proposed fixture `FIX-VF-OBS-001-003` is not created. Verification duty `TASK-VF-OBS-001-03` (qualification); source `docs/backlog/backlog.csv` record 113, exact block `4486a81b7bc6cd72176d02a7e402bf18333789f7d1b9c27ad47d9401fde1cd64`.

**Original preconditions**

1. diagnostics and alerts from the injected failures

**Original actions**

1. they are inspected

**Exact source oracles — all required**

1. missing tenant context fails the gate
2. any secret payload in diagnostics fails the gate
3. a critical alert delayed beyond 5 minutes fails the gate

Legacy same-requirement reuse candidates: `TC-VF-OBS-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
