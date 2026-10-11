## QA v1.3 — source-bound case design (proposed)

Story `VF-OFF-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-OFF-001-001` / `TC-IMPRANA-VF-OFF-001-001` | `REV_efa70c6fcef2a59bb279e74a42ef34cc8fc79ccf1ffe729af323114eb4e943c5` / `REV_2eb2b6aff0ef272ce5e97c55ea004d4408d4f2e64a77341d73184219aa371710` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-OFF-001-002` / `TC-IMPRANA-VF-OFF-001-002` | `REV_05c8b21173f4e2e2b1e1c5323556c80805b162cc6398d239efe07c86607f915c` / `REV_3aa65565330c1ca74beca239eb48c871989903e269a9de621d185ee5777113c6` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-OFF-001-003` / `TC-IMPRANA-VF-OFF-001-003` | `REV_0eb50cb71e34b99e4c784386fd8c2d6b339045915c5a1a91d493d3e8685b3455` / `REV_f7e77cc2e1115e3f65ac32e3688e3554285240ff0188ba3404e3bce8d696605d` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-OFF-001-004` / `TC-IMPRANA-VF-OFF-001-004` | `REV_7d9a217a7bc67a9614b5b5bc218c916563ffc370077ba6886d9e02bcd5fe8121` / `REV_698b6c6fd3807e2db1da0726b5ffd81c8ce859a247704b02d379754236392abd` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-OFF-001-001 — Default offline package expires within 24 hours

Source persona: Privacy Officer. Proposed fixture `FIX-VF-OFF-001-001` is not created. Verification duty `TASK-VF-OFF-001-02` (qualification); source `docs/backlog/backlog.csv` record 279, exact block `efa70c6fcef2a59bb279e74a42ef34cc8fc79ccf1ffe729af323114eb4e943c5`.

**Original preconditions**

1. a default offline package on a device

**Original actions**

1. 24 hours pass without renewed authorisation

**Exact source oracles — all required**

1. the package expires
2. expiry holds across restart, clock rollback, account switching, prolonged disconnection and revoked reconnect

Legacy same-requirement reuse candidates: `TC-VF-OFF-001`, `UT-106`, `UT-107`, `UT-108`, `UT-109`, `UT-110`, `UT-111`, `IT-018`, `SEC-029`, `SEC-030`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-OFF-001-002 — Restricted participant package expires within 8 hours by default

Source persona: Privacy Officer. Proposed fixture `FIX-VF-OFF-001-002` is not created. Verification duty `TASK-VF-OFF-001-02` (qualification); source `docs/backlog/backlog.csv` record 279, exact block `05c8b21173f4e2e2b1e1c5323556c80805b162cc6398d239efe07c86607f915c`.

**Original preconditions**

1. a restricted participant package on a device with approved device controls

**Original actions**

1. 8 hours pass without renewed authorisation

**Exact source oracles — all required**

1. the package expires

Legacy same-requirement reuse candidates: `TC-VF-OFF-001`, `UT-106`, `UT-107`, `UT-108`, `UT-109`, `UT-110`, `UT-111`, `IT-018`, `SEC-029`, `SEC-030`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-OFF-001-003 — Longer windows need a recorded risk exception

Source persona: Privacy Officer. Proposed fixture `FIX-VF-OFF-001-003` is not created. Verification duty `TASK-VF-OFF-001-02` (qualification); source `docs/backlog/backlog.csv` record 279, exact block `0eb50cb71e34b99e4c784386fd8c2d6b339045915c5a1a91d493d3e8685b3455`.

**Original preconditions**

1. a low sensitivity package

**Original actions**

1. a window longer than the default is configured

**Exact source oracles — all required**

1. a recorded risk exception is required
2. sensitive data may be prohibited from offline use entirely

Legacy same-requirement reuse candidates: `TC-VF-OFF-001`, `UT-106`, `UT-107`, `UT-108`, `UT-109`, `UT-110`, `UT-111`, `IT-018`, `SEC-029`, `SEC-030`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-OFF-001-004 — Reject sensitive offline use on a device that cannot enforce the window

Source persona: Privacy Officer. Proposed fixture `FIX-VF-OFF-001-004` is not created. Verification duty `TASK-VF-OFF-001-02` (qualification); source `docs/backlog/backlog.csv` record 279, exact block `7d9a217a7bc67a9614b5b5bc218c916563ffc370077ba6886d9e02bcd5fe8121`.

**Original preconditions**

1. a device that cannot reliably enforce the authority window

**Original actions**

1. sensitive offline use is assessed for that device

**Exact source oracles — all required**

1. sensitive offline use is not qualified
2. remote wipe is recorded as best effort only

Legacy same-requirement reuse candidates: `TC-VF-OFF-001`, `UT-106`, `UT-107`, `UT-108`, `UT-109`, `UT-110`, `UT-111`, `IT-018`, `SEC-029`, `SEC-030`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
