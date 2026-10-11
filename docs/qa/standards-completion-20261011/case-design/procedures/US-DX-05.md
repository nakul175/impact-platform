## QA v1.3 — source-bound case design (proposed)

Story `US-DX-05` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-DX-05-001` / `TC-IMPRANA-US-DX-05-001` | `REV_ce7f443b8ca797b2e261301565cf5d080fb79f5369c08c0ce597156cc6a23adf` / `REV_a90b2f202bf91700f0d2cf986d5083207f3541d6a7431fd52e79736988bf7e39` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-DX-05-002` / `TC-IMPRANA-US-DX-05-002` | `REV_26cbdee5c7602ac8c0b0017bda19b8795147daf853b0021c5d3edc98379ddcc8` / `REV_b7492067ba37a5cf541523f99ac467ac0f8880347847da14c7072599c3829a76` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-DX-05-003` / `TC-IMPRANA-US-DX-05-003` | `REV_89269b6f55bba65e14f2f241d77c3d9112d6ef963a5d2cab5777f84471c79c8d` / `REV_ded3f2f03684ff7318ea2132e15d96426ede4b3e717f5dcc3c5c0d4cc4a7e9ef` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-DX-05-001 — Diagnosis appears in the advisor queue

Source persona: Imprana Advisor. Proposed fixture `FIX-US-DX-05-001` is not created. Verification duty `TASK-US-DX-05-03` (qualification); source `docs/backlog/backlog.csv` record 38, exact block `ce7f443b8ca797b2e261301565cf5d080fb79f5369c08c0ce597156cc6a23adf`.

**Original preconditions**

1. an organisation has a diagnosis ready for review

**Original actions**

1. the Imprana Advisor opens the advisor queue

**Exact source oracles — all required**

1. the diagnosis is listed for review

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_adoption_plans.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-DX-05-002 — Annotate and validate a diagnosis

Source persona: Imprana Advisor. Proposed fixture `FIX-US-DX-05-002` is not created. Verification duty `TASK-US-DX-05-03` (qualification); source `docs/backlog/backlog.csv` record 38, exact block `26cbdee5c7602ac8c0b0017bda19b8795147daf853b0021c5d3edc98379ddcc8`.

**Original preconditions**

1. an Imprana Advisor reviewing a diagnosis

**Original actions**

1. they add comments and mark the diagnosis validated

**Exact source oracles — all required**

1. the comments are visible to the organisation
2. the validated status is recorded

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_adoption_plans.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-DX-05-003 — Reject validation without advisor review

Source persona: Imprana Advisor. Proposed fixture `FIX-US-DX-05-003` is not created. Verification duty `TASK-US-DX-05-03` (qualification); source `docs/backlog/backlog.csv` record 38, exact block `89269b6f55bba65e14f2f241d77c3d9112d6ef963a5d2cab5777f84471c79c8d`.

**Original preconditions**

1. a diagnosis that has not been reviewed by an Imprana Advisor

**Original actions**

1. a member of the organisation tries to mark it validated

**Exact source oracles — all required**

1. the validated status is not recorded

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_adoption_plans.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
