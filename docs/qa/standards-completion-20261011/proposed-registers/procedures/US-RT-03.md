## QA v1.3 — source-bound case design (proposed)

Story `US-RT-03` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-RT-03-001` / `TC-IMPRANA-US-RT-03-001` | `REV_72edb4289c96021cc04a626c97c10ad3e6e754663cb52cf208d6269591acb04e` / `REV_ec18478af566bf18bbed5b20ca039335af9df18f4e4080a1b538231647ae943d` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-US-RT-03-002` / `TC-IMPRANA-US-RT-03-002` | `REV_2bc3591f16e0bad35e52283dfeafb8900582ff3e59a7724c88c935f81ca9cfb0` / `REV_6e52bb0e2b8b9699206b1b0b8e634ba6af9752c109a9747737bdb68fb184ed23` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-US-RT-03-003` / `TC-IMPRANA-US-RT-03-003` | `REV_044bf333abe1afc40ba0832bb8e0faf978ddd71c2fa7ed4f0c9612062b971f9f` / `REV_a7b790626832bdf0ceff50da4d6c308888b3a76dace44cfaa0139da996be236b` | manual → MANUAL recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-RT-03-001 — Archive evidence and agent logs out of main

Source persona: Platform Operator. Proposed fixture `FIX-US-RT-03-001` is not created. Verification duty `TASK-US-RT-03-03` (qualification); source `docs/backlog/backlog.csv` record 6, exact block `72edb4289c96021cc04a626c97c10ad3e6e754663cb52cf208d6269591acb04e`.

**Original preconditions**

1. the tag on the last Impact Platform commit

**Original actions**

1. the archive change is merged to main

**Exact source oracles — all required**

1. docs/evidence and dated agent logs are no longer in main
2. they are still available at the tag

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-RT-03-002 — Keep governance templates and current guides

Source persona: Platform Operator. Proposed fixture `FIX-US-RT-03-002` is not created. Verification duty `TASK-US-RT-03-03` (qualification); source `docs/backlog/backlog.csv` record 6, exact block `2bc3591f16e0bad35e52283dfeafb8900582ff3e59a7724c88c935f81ca9cfb0`.

**Original preconditions**

1. the archive change has been merged

**Original actions**

1. the Platform Operator browses main

**Exact source oracles — all required**

1. governance templates and current guides are still present

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-RT-03-003 — Reject lost evidence or removed current material

Source persona: Platform Operator. Proposed fixture `FIX-US-RT-03-003` is not created. Verification duty `TASK-US-RT-03-03` (qualification); source `docs/backlog/backlog.csv` record 6, exact block `044bf333abe1afc40ba0832bb8e0faf978ddd71c2fa7ed4f0c9612062b971f9f`.

**Original preconditions**

1. the archive change

**Original actions**

1. evidence or agent logs are missing from the tag, or governance templates or current guides are removed from main

**Exact source oracles — all required**

1. the change is rejected

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
