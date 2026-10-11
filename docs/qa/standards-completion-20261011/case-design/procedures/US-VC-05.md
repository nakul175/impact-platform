## QA v1.3 — source-bound case design (proposed)

Story `US-VC-05` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-VC-05-001` / `TC-IMPRANA-US-VC-05-001` | `REV_32762d2bc686637d5ee7ee9b51a19550b116930df20b6e8e38fb2c669ae1367f` / `REV_2a708451d5bb76c2012241ff436df5fee001fe5fa98282bc776c108c6f8cbd55` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-VC-05-002` / `TC-IMPRANA-US-VC-05-002` | `REV_4eedbe2d76e6f3065f13600e034a772b5cbda64ea50341b535c84657262ab7f8` / `REV_181b926a5391ff259d445e82424bd5665001de162c9bb09f73c44857a4de5d3a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-VC-05-003` / `TC-IMPRANA-US-VC-05-003` | `REV_baf1eb3ff2fd09232bcc25b045f3c4a79c23190a345756cd4deffc87c5dad778` / `REV_7e09d9453b01d596192117a406289891b3fd791224f9e9e5355169118be38483` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-VC-05-001 — Lock the approved value case

Source persona: Executive Director. Proposed fixture `FIX-US-VC-05-001` is not created. Verification duty `TASK-US-VC-05-03` (qualification); source `docs/backlog/backlog.csv` record 53, exact block `32762d2bc686637d5ee7ee9b51a19550b116930df20b6e8e38fb2c669ae1367f`.

**Original preconditions**

1. an approved value case

**Original actions**

1. the Executive Director locks it

**Exact source oracles — all required**

1. the locked version records the date and the approver

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_procurement_costs.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-VC-05-002 — Changes create a new version

Source persona: Executive Director. Proposed fixture `FIX-US-VC-05-002` is not created. Verification duty `TASK-US-VC-05-03` (qualification); source `docs/backlog/backlog.csv` record 53, exact block `4eedbe2d76e6f3065f13600e034a772b5cbda64ea50341b535c84657262ab7f8`.

**Original preconditions**

1. a locked value case

**Original actions**

1. someone changes it

**Exact source oracles — all required**

1. a new version is created
2. the locked version stays unchanged

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_procurement_costs.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-VC-05-003 — Reject overwriting the locked version

Source persona: Executive Director. Proposed fixture `FIX-US-VC-05-003` is not created. Verification duty `TASK-US-VC-05-03` (qualification); source `docs/backlog/backlog.csv` record 53, exact block `baf1eb3ff2fd09232bcc25b045f3c4a79c23190a345756cd4deffc87c5dad778`.

**Original preconditions**

1. a locked value case

**Original actions**

1. an edit is saved

**Exact source oracles — all required**

1. the locked version is not overwritten
2. later ROI is still measured against the locked version

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_procurement_costs.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
