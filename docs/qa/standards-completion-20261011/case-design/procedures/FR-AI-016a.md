## QA v1.3 — source-bound case design (proposed)

Story `FR-AI-016a` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-AI-016a-001` / `TC-IMPRANA-FR-AI-016a-001` | `REV_e375dbd7371a14fd22c8b0751da0ccc06b12a2599185fc55c82ada845f74328f` / `REV_4bea744a11f6fb5aca39089668a1ca123b2efbcf944ccf4cbfe57ef99ecd5efc` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-016a-002` / `TC-IMPRANA-FR-AI-016a-002` | `REV_8e9ba86bb2cba14af10a73ed63c7835e7906b830826f078748ccbd254e4df319` / `REV_537e1f3bcfd7bb15e8a30db3355a864c7baed69b8ff0739b638236f590f5e9ec` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-016a-003` / `TC-IMPRANA-FR-AI-016a-003` | `REV_b15d3b3a675efe438dd665c66ca18c7284ee76b6e97d8ab4e07d1fc7b5ba9689` / `REV_a80997c171ca94bd0600ddf9719a3a3956b9f5810fabab2f02c2c46d5dcf9914` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-AI-016a-001 — Request reserves budget and runs as a job

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-016a-001` is not created. Verification duty `TASK-FR-AI-016a-06` (qualification); source `docs/backlog/backlog.csv` record 16, exact block `e375dbd7371a14fd22c8b0751da0ccc06b12a2599185fc55c82ada845f74328f`.

**Original preconditions**

1. an enabled use case with budget remaining

**Original actions**

1. a request is submitted

**Exact source oracles — all required**

1. the response is 202 with a job ID
2. the estimated units are reserved in the budget ledger
3. progress and a Cancel action are shown

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Synchronous advisory-attempt tests do not prove source 202 job identity, budget reservations, durable terminal settlement, cancellation or lease/recovery fencing.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-016a-002 — Budget exhausted during close

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-016a-002` is not created. Verification duty `TASK-FR-AI-016a-06` (qualification); source `docs/backlog/backlog.csv` record 16, exact block `8e9ba86bb2cba14af10a73ed63c7835e7906b830826f078748ccbd254e4df319`.

**Original preconditions**

1. the AI budget is exhausted

**Original actions**

1. the MEL Manager approves data, calculates results and generates a report

**Exact source oracles — all required**

1. each completes without AI

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Synchronous advisory-attempt tests do not prove source 202 job identity, budget reservations, durable terminal settlement, cancellation or lease/recovery fencing.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-016a-003 — Reject a request beyond the budget

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-016a-003` is not created. Verification duty `TASK-FR-AI-016a-06` (qualification); source `docs/backlog/backlog.csv` record 16, exact block `b15d3b3a675efe438dd665c66ca18c7284ee76b6e97d8ab4e07d1fc7b5ba9689`.

**Original preconditions**

1. the remaining budget is smaller than the estimate

**Original actions**

1. a request is submitted

**Exact source oracles — all required**

1. the response is 429 "AI_BUDGET_EXHAUSTED" and the user's input is kept

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Synchronous advisory-attempt tests do not prove source 202 job identity, budget reservations, durable terminal settlement, cancellation or lease/recovery fencing.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
