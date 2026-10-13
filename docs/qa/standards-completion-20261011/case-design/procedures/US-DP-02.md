## QA v1.3 — source-bound case design (proposed)

Story `US-DP-02` · 2 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-DP-02-001` / `TC-IMPRANA-US-DP-02-001` | `REV_0788111fe36819233b2aace3b757c127bdf77100a4ab311ac3bb28f3e7126631` / `REV_8da5bf99b059e9194218e70270b28bad4e0bfa2b6a95cc03c588e2cdd0e04283` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-DP-02-002` / `TC-IMPRANA-US-DP-02-002` | `REV_fa3d224bafca84fb9c45695a30dc92bdac14e80676945c81398a76ee754674df` / `REV_7b6e446a3db54e05dd3f6940d0aa17ed7ef31a256ae5d848997a4aa7fd6edb1f` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-DP-02-001 — Deployment plan names the workflow touchpoints

Source persona: Data Author. Proposed fixture `FIX-US-DP-02-001` is not created. Verification duty `TASK-US-DP-02-03` (qualification); source `docs/backlog/backlog.csv` record 30, exact block `0788111fe36819233b2aace3b757c127bdf77100a4ab311ac3bb28f3e7126631`.

**Original preconditions**

1. a deployment plan for a new solution

**Original actions**

1. the Data Author views it

**Exact source oracles — all required**

1. it names the touchpoints in the existing workflow where the solution is used

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_adoption_plans.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-DP-02-002 — Reject duplicate data entry

Source persona: Data Author. Proposed fixture `FIX-US-DP-02-002` is not created. Verification duty `TASK-US-DP-02-03` (qualification); source `docs/backlog/backlog.csv` record 30, exact block `fa3d224bafca84fb9c45695a30dc92bdac14e80676945c81398a76ee754674df`.

**Original preconditions**

1. a solution deployed inside the existing workflow

**Original actions**

1. a Data Author records data in the existing workflow

**Exact source oracles — all required**

1. they are not asked to enter the same data again in the new solution
2. a deployment plan that names no workflow touchpoints is not accepted

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_adoption_plans.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
