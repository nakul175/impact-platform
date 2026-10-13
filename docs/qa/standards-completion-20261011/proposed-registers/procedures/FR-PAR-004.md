## QA v1.3 — source-bound case design (proposed)

Story `FR-PAR-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PAR-004-001` / `TC-IMPRANA-FR-PAR-004-001` | `REV_8cb748a367605589dfd757297cdcc926c4df454c647a4d2c390fc0a725cfcb38` / `REV_23b5d633b31936dd86343241257d5689d381be68ede407632fae3ddeac29d4bd` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PAR-004-002` / `TC-IMPRANA-FR-PAR-004-002` | `REV_40f8171ce462de9ea4b9bc2514a124f79d420c98b5596fc9d7474d22238adb57` / `REV_16df1c482fe4b3eecf051b2e7d8743f5b5f97f2b3ea48faa539383175f75f1dd` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PAR-004-003` / `TC-IMPRANA-FR-PAR-004-003` | `REV_26623598f68d35aaab81b59eed5715cebd90ed9d5fa541f8b74c7a5e7fbba956` / `REV_c473966c6c13b0d29dfde4a06bbfd98dd2925a7b351a47f34ac493a1916c0ac5` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PAR-004-004` / `TC-IMPRANA-FR-PAR-004-004` | `REV_6949e54fad7daffb327ea1daee0d78e9e8d65ef3bc3817962f9645a7e06d41e5` / `REV_edb20caacf8e30155932e99a72ab1a93b71c0374b3b275626fb4169befc071c2` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PAR-004-001 — Count services and unique people

Source persona: MEL Manager. Proposed fixture `FIX-FR-PAR-004-001` is not created. Verification duty `TASK-FR-PAR-004-03` (qualification); source `docs/backlog/backlog.csv` record 283, exact block `8cb748a367605589dfd757297cdcc926c4df454c647a4d2c390fc0a725cfcb38`.

**Original preconditions**

1. three distinct visits recorded for one participant

**Original actions**

1. indicators are reported

**Exact source oracles — all required**

1. the service count is three
2. the approved unique person count is one

Legacy same-requirement reuse candidates: `TC-PAR-004-01`, `TC-PAR-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PAR-004-002 — Corrections create revisions

Source persona: MEL Manager. Proposed fixture `FIX-FR-PAR-004-002` is not created. Verification duty `TASK-FR-PAR-004-03` (qualification); source `docs/backlog/backlog.csv` record 283, exact block `40f8171ce462de9ea4b9bc2514a124f79d420c98b5596fc9d7474d22238adb57`.

**Original preconditions**

1. a recorded service event

**Original actions**

1. a Data Author corrects it

**Exact source oracles — all required**

1. a new revision of the event is created

Legacy same-requirement reuse candidates: `TC-PAR-004-01`, `TC-PAR-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PAR-004-003 — Reject duplicate ingestion of the same event

Source persona: MEL Manager. Proposed fixture `FIX-FR-PAR-004-003` is not created. Verification duty `TASK-FR-PAR-004-03` (qualification); source `docs/backlog/backlog.csv` record 283, exact block `26623598f68d35aaab81b59eed5715cebd90ed9d5fa541f8b74c7a5e7fbba956`.

**Original preconditions**

1. a service event that is already recorded

**Original actions**

1. the same event is ingested again

**Exact source oracles — all required**

1. no additional visit is added

Legacy same-requirement reuse candidates: `TC-PAR-004-01`, `TC-PAR-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PAR-004-004 — Reject silent removal on cancellation or reversal

Source persona: MEL Manager. Proposed fixture `FIX-FR-PAR-004-004` is not created. Verification duty `TASK-FR-PAR-004-03` (qualification); source `docs/backlog/backlog.csv` record 283, exact block `6949e54fad7daffb327ea1daee0d78e9e8d65ef3bc3817962f9645a7e06d41e5`.

**Original preconditions**

1. a recorded service event

**Original actions**

1. it is cancelled or reversed

**Exact source oracles — all required**

1. the cancellation or reversal is recorded explicitly
2. the original receipt is not removed

Legacy same-requirement reuse candidates: `TC-PAR-004-01`, `TC-PAR-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
