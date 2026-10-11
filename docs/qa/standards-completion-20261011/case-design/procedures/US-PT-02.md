## QA v1.3 — source-bound case design (proposed)

Story `US-PT-02` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-PT-02-001` / `TC-IMPRANA-US-PT-02-001` | `REV_689d73c0e12f47ff78cfeb0d50fdc67f61fa2a4895ede7ad3a990910896d15ff` / `REV_40aa4c586d493aa5db7c74e190792b83f7b280ea97a3ba5f3bde40def5db3cc0` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-PT-02-002` / `TC-IMPRANA-US-PT-02-002` | `REV_51adf73ab793e5f48dd87429842ff6f9dfdfc0d88bcff525c3d97d06ee9c4b72` / `REV_0bd089933079a133b08b664ba017ccbc133808f9ce63dbcbf2c1dc5afa719e9e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-PT-02-003` / `TC-IMPRANA-US-PT-02-003` | `REV_6f3c9635c8b22a6aadc0e5ac44f4aade0248a0a443f81eaf4dc6ea9ac8044bcd` / `REV_c330f4f1e4a77501719383134cbc76b6df5744ff190c3f075f4e38ab5e950acb` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-PT-02-001 — Read and write through the shared data model

Source persona: Solution Partner Manager. Proposed fixture `FIX-US-PT-02-001` is not created. Verification duty `TASK-US-PT-02-03` (qualification); source `docs/backlog/backlog.csv` record 287, exact block `689d73c0e12f47ff78cfeb0d50fdc67f61fa2a4895ede7ad3a990910896d15ff`.

**Original preconditions**

1. a Solution Partner Manager's integration built against the Imprana Commons APIs

**Original actions**

1. it reads and writes data

**Exact source oracles — all required**

1. the data is read from and written to the shared data model

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-PT-02-002 — Test sandbox

Source persona: Solution Partner Manager. Proposed fixture `FIX-US-PT-02-002` is not created. Verification duty `TASK-US-PT-02-03` (qualification); source `docs/backlog/backlog.csv` record 287, exact block `51adf73ab793e5f48dd87429842ff6f9dfdfc0d88bcff525c3d97d06ee9c4b72`.

**Original preconditions**

1. a Solution Partner Manager building an integration

**Original actions**

1. they use the test sandbox

**Exact source oracles — all required**

1. they can test reads and writes without touching any organisation's live data

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-PT-02-003 — Reject per-client integration

Source persona: Solution Partner Manager. Proposed fixture `FIX-US-PT-02-003` is not created. Verification duty `TASK-US-PT-02-03` (qualification); source `docs/backlog/backlog.csv` record 287, exact block `6f3c9635c8b22a6aadc0e5ac44f4aade0248a0a443f81eaf4dc6ea9ac8044bcd`.

**Original preconditions**

1. an integration built once against the Imprana Commons APIs

**Original actions**

1. another organisation deploys the solution

**Exact source oracles — all required**

1. no client-specific integration is required

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
