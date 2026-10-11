## QA v1.3 — source-bound case design (proposed)

Story `US-AD-01` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-AD-01-001` / `TC-IMPRANA-US-AD-01-001` | `REV_605c3386be520a8849f35181e5e261b13bd346d710c51238205fa3f0c1178337` / `REV_a431a594a1c6b362bbdbd58c2ba298176c65c168d2bfdc89ed1ab84bd7231252` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-AD-01-002` / `TC-IMPRANA-US-AD-01-002` | `REV_a1f21e326a6e9b908f397581ca725583ab1a1b69afd349a01b7e9c3b1c75221e` / `REV_4c7fd2ccef97b40b9acc518fd9f55a4fc0db4c2580b414cdaa53b0f2ed628bdc` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-AD-01-003` / `TC-IMPRANA-US-AD-01-003` | `REV_34ddbba5023391bd2cac056f7ffb1cbd3f704d29c31d8f1a18906e6695c36f0b` / `REV_2d1cd7e33917758ec2818574259f559a7ccbcd4d8ce9c282a87d24f56fedea8d` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-AD-01-001 — Training modules for the user's role

Source persona: Data Author. Proposed fixture `FIX-US-AD-01-001` is not created. Verification duty `TASK-US-AD-01-03` (qualification); source `docs/backlog/backlog.csv` record 26, exact block `605c3386be520a8849f35181e5e261b13bd346d710c51238205fa3f0c1178337`.

**Original preconditions**

1. a deployed solution with training modules per role

**Original actions**

1. a Data Author opens the training

**Exact source oracles — all required**

1. they see the modules for their role

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_learning_content.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-AD-01-002 — Completion tracked

Source persona: Data Author. Proposed fixture `FIX-US-AD-01-002` is not created. Verification duty `TASK-US-AD-01-03` (qualification); source `docs/backlog/backlog.csv` record 26, exact block `a1f21e326a6e9b908f397581ca725583ab1a1b69afd349a01b7e9c3b1c75221e`.

**Original preconditions**

1. a Data Author taking a training module

**Original actions**

1. they finish it

**Exact source oracles — all required**

1. their completion is recorded

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_learning_content.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-AD-01-003 — Reject training for other roles

Source persona: Data Author. Proposed fixture `FIX-US-AD-01-003` is not created. Verification duty `TASK-US-AD-01-03` (qualification); source `docs/backlog/backlog.csv` record 26, exact block `34ddbba5023391bd2cac056f7ffb1cbd3f704d29c31d8f1a18906e6695c36f0b`.

**Original preconditions**

1. a Data Author

**Original actions**

1. they open the training for a deployed solution

**Exact source oracles — all required**

1. they are not required to complete modules for other roles

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_learning_content.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
