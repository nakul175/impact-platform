## QA v1.3 — source-bound case design (proposed)

Story `US-DP-03` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-DP-03-001` / `TC-IMPRANA-US-DP-03-001` | `REV_5b8ebdcfe837f7bab80f6b5cbf8776021864a3b632cba58358b55b76173e1e2b` / `REV_1b1f99f178eafe2b1770e39601857d919c4c5539e6d193597caaa1bb7edbbd3e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-DP-03-002` / `TC-IMPRANA-US-DP-03-002` | `REV_3d5b1a7f795de4b9810bc0ed5a89c66c602bd43870e16354e9728c8ca4490a19` / `REV_e25b1880f3c7f7067df113df5e61d2e86dafb075dc770835d0634c46c7599a9a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-DP-03-003` / `TC-IMPRANA-US-DP-03-003` | `REV_abc4576e67d4889334ae506d0a75c289634a0572be02a82eca121202edd1c9b3` / `REV_d4d8410b622d7f48cdc6434c7808ea939441a43235340aaad50fe536cfc25a79` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-DP-03-001 — Generate a deployment plan from a template

Source persona: Operations Head. Proposed fixture `FIX-US-DP-03-001` is not created. Verification duty `TASK-US-DP-03-03` (qualification); source `docs/backlog/backlog.csv` record 31, exact block `5b8ebdcfe837f7bab80f6b5cbf8776021864a3b632cba58358b55b76173e1e2b`.

**Original preconditions**

1. a solution to deploy

**Original actions**

1. the Operations Head generates a deployment plan

**Exact source oracles — all required**

1. the plan is created from a template with owners, milestones and acceptance criteria

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_adoption_plans.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-DP-03-002 — Track progress in the platform

Source persona: Operations Head. Proposed fixture `FIX-US-DP-03-002` is not created. Verification duty `TASK-US-DP-03-03` (qualification); source `docs/backlog/backlog.csv` record 31, exact block `3d5b1a7f795de4b9810bc0ed5a89c66c602bd43870e16354e9728c8ca4490a19`.

**Original preconditions**

1. a deployment plan

**Original actions**

1. an owner updates a milestone

**Exact source oracles — all required**

1. the progress is tracked in the platform

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_adoption_plans.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-DP-03-003 — Reject an unaccountable plan

Source persona: Operations Head. Proposed fixture `FIX-US-DP-03-003` is not created. Verification duty `TASK-US-DP-03-03` (qualification); source `docs/backlog/backlog.csv` record 31, exact block `abc4576e67d4889334ae506d0a75c289634a0572be02a82eca121202edd1c9b3`.

**Original preconditions**

1. a deployment plan

**Original actions**

1. a milestone has no owner or no acceptance criteria

**Exact source oracles — all required**

1. the plan is not accepted as complete

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_adoption_plans.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
