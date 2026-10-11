## QA v1.3 — source-bound case design (proposed)

Story `US-IM-03` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-IM-03-001` / `TC-IMPRANA-US-IM-03-001` | `REV_155231fa3c7a53efe5ed14f24060afcb12f6882ecde517a0c4fa675843514ef2` / `REV_aa758ef8da16844ae15819fa63f8d72dd1a2b01994eaa298fdfb310d682393f6` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-IM-03-002` / `TC-IMPRANA-US-IM-03-002` | `REV_791ab98e5c3dc8885c954b8b94ed8fb811b58b9eaa649aa0244b8374cf8179be` / `REV_1bf9889447f7b9f339b350477f9ffed168d3aeca0fd6c4b0f593d9be52799513` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-IM-03-003` / `TC-IMPRANA-US-IM-03-003` | `REV_c93a1ad999105e9149ee99d96ffc33e392d00043bcaf59d899ef5660ce7fe77f` / `REV_771e54783ebb9a3cff30e0f58c6c19aea27a8abf84848905add96d38deb4e16f` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-IM-03-001 — Run a quarterly value review from a template

Source persona: Imprana Advisor. Proposed fixture `FIX-US-IM-03-001` is not created. Verification duty `TASK-US-IM-03-03` (qualification); source `docs/backlog/backlog.csv` record 45, exact block `155231fa3c7a53efe5ed14f24060afcb12f6882ecde517a0c4fa675843514ef2`.

**Original preconditions**

1. an organisation due its quarterly value review

**Original actions**

1. the Imprana Advisor starts the review

**Exact source oracles — all required**

1. the review template is used

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_pilot_outcomes.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-IM-03-002 — Actions logged and tracked

Source persona: Imprana Advisor. Proposed fixture `FIX-US-IM-03-002` is not created. Verification duty `TASK-US-IM-03-03` (qualification); source `docs/backlog/backlog.csv` record 45, exact block `791ab98e5c3dc8885c954b8b94ed8fb811b58b9eaa649aa0244b8374cf8179be`.

**Original preconditions**

1. a value review in progress

**Original actions**

1. the Imprana Advisor records an action

**Exact source oracles — all required**

1. the action is logged
2. its progress is tracked

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_pilot_outcomes.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-IM-03-003 — Reject untracked actions

Source persona: Imprana Advisor. Proposed fixture `FIX-US-IM-03-003` is not created. Verification duty `TASK-US-IM-03-03` (qualification); source `docs/backlog/backlog.csv` record 45, exact block `c93a1ad999105e9149ee99d96ffc33e392d00043bcaf59d899ef5660ce7fe77f`.

**Original preconditions**

1. a completed value review

**Original actions**

1. an action agreed in the review is not logged

**Exact source oracles — all required**

1. the review is not accepted as complete

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_pilot_outcomes.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
