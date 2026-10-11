## QA v1.3 — source-bound case design (proposed)

Story `US-OP-02` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-OP-02-001` / `TC-IMPRANA-US-OP-02-001` | `REV_890be2cb0c5ee547c048da5d51c734c241a3d0c50aecb56ce88f989da52c195e` / `REV_877f75d76ff9052fd11d942f9586a6daa4a2141b3c442c7599875c13cb2f1bf4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-OP-02-002` / `TC-IMPRANA-US-OP-02-002` | `REV_3295d0bdd34fae2d0e56d295b846ab981518c6be0a7556b5989c3959c273df26` / `REV_c9c2f5f6e76822982255fa56f742f0ea5fba6d43d3e9158f6c8112f5e6f0b3c5` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-OP-02-003` / `TC-IMPRANA-US-OP-02-003` | `REV_91014a18742c27acb959466cdefaae6d7eddd71534b8ba0dcd2c800073b0bcdd` / `REV_4e863cd72779ff3e9ee5553eb0039560d8ea5f3aa0494e823d82c675b8ee0e3a` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-OP-02-001 — Log time per stage

Source persona: Imprana Advisor. Proposed fixture `FIX-US-OP-02-001` is not created. Verification duty `TASK-US-OP-02-03` (qualification); source `docs/backlog/backlog.csv` record 123, exact block `890be2cb0c5ee547c048da5d51c734c241a3d0c50aecb56ce88f989da52c195e`.

**Original preconditions**

1. an Imprana Advisor working with an organisation

**Original actions**

1. they log time

**Exact source oracles — all required**

1. the time is recorded against a stage

Original proposed anchors (file/artifact candidates only): `qualification/test_human_advice_live.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-OP-02-002 — Monthly report

Source persona: Imprana Advisor. Proposed fixture `FIX-US-OP-02-002` is not created. Verification duty `TASK-US-OP-02-03` (qualification); source `docs/backlog/backlog.csv` record 123, exact block `3295d0bdd34fae2d0e56d295b846ab981518c6be0a7556b5989c3959c273df26`.

**Original preconditions**

1. time logged during a month

**Original actions**

1. the monthly report is produced

**Exact source oracles — all required**

1. it shows the time spent per stage

Original proposed anchors (file/artifact candidates only): `qualification/test_human_advice_live.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-OP-02-003 — Reject time without a stage

Source persona: Imprana Advisor. Proposed fixture `FIX-US-OP-02-003` is not created. Verification duty `TASK-US-OP-02-03` (qualification); source `docs/backlog/backlog.csv` record 123, exact block `91014a18742c27acb959466cdefaae6d7eddd71534b8ba0dcd2c800073b0bcdd`.

**Original preconditions**

1. an Imprana Advisor logging time

**Original actions**

1. no stage is chosen

**Exact source oracles — all required**

1. the entry is refused

Original proposed anchors (file/artifact candidates only): `qualification/test_human_advice_live.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
