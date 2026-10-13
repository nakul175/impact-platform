## QA v1.3 — source-bound case design (proposed)

Story `FR-PRV-002` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRV-002-001` / `TC-IMPRANA-FR-PRV-002-001` | `REV_f0e29a970f7cfdc404b6d58adf90f48f79c1f413283706af960840a651c7cfff` / `REV_a672d66c6e624d8c7c85e700404e23b7ce87bad86260aa51461cfaba0264eb13` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-002-002` / `TC-IMPRANA-FR-PRV-002-002` | `REV_d5c98879aedf003c62508de31e5941e1a436a7a791fa6b1e6a71953410c36f27` / `REV_1260894816b1dc3fe421671a92f189e01605a388c24bd1b2f609ebc2fdc268a3` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-002-003` / `TC-IMPRANA-FR-PRV-002-003` | `REV_60753bd22895196f4361328bf0f46cce553447cd06efcea8b0ad21d10e657eeb` / `REV_ed443478ce6268f601324e578b1a7293d670c677fc7916894f9dccbebbc0ac51` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-002-004` / `TC-IMPRANA-FR-PRV-002-004` | `REV_34d5d4f5e2fbb2c0a937e80a54dbff405eb09ebfdf35a6fcc19e5a722d37c1c3` / `REV_d90c704a0e2915dc56d49392907e83ed6967375ed049dc7fb367f57c6122b8de` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRV-002-001 — Necessity and allowed uses are recorded

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-002-001` is not created. Verification duty `TASK-FR-PRV-002-03` (qualification); source `docs/backlog/backlog.csv` record 127, exact block `f0e29a970f7cfdc404b6d58adf90f48f79c1f413283706af960840a651c7cfff`.

**Original preconditions**

1. a programme being set up

**Original actions**

1. personal fields are defined

**Exact source oracles — all required**

1. the reason each is necessary and its allowed uses are recorded
2. optional fields remain optional in collection

Legacy same-requirement reuse candidates: `TC-PRV-002-01`, `TC-PRV-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `apps/api/impact_api/ai_policy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-002-002 — New use requires a purpose review

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-002-002` is not created. Verification duty `TASK-FR-PRV-002-03` (qualification); source `docs/backlog/backlog.csv` record 127, exact block `d5c98879aedf003c62508de31e5941e1a436a7a791fa6b1e6a71953410c36f27`.

**Original preconditions**

1. a proposed research, linkage or model improvement use

**Original actions**

1. it is requested

**Exact source oracles — all required**

1. a separate purpose review and data scope selection is created

Legacy same-requirement reuse candidates: `TC-PRV-002-01`, `TC-PRV-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `apps/api/impact_api/ai_policy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-002-003 — Reject transfer outside the purpose

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-002-003` is not created. Verification duty `TASK-FR-PRV-002-03` (qualification); source `docs/backlog/backlog.csv` record 127, exact block `60753bd22895196f4361328bf0f46cce553447cd06efcea8b0ad21d10e657eeb`.

**Original preconditions**

1. service delivery identities collected under a monitoring purpose

**Original actions**

1. someone attempts to send them for shared model training

**Exact source oracles — all required**

1. policy denies the transfer before transmission

Legacy same-requirement reuse candidates: `TC-PRV-002-01`, `TC-PRV-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `apps/api/impact_api/ai_policy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-002-004 — Reject purpose bypass

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-002-004` is not created. Verification duty `TASK-FR-PRV-002-03` (qualification); source `docs/backlog/backlog.csv` record 127, exact block `34d5d4f5e2fbb2c0a937e80a54dbff405eb09ebfdf35a6fcc19e5a722d37c1c3`.

**Original preconditions**

1. a rejected purpose

**Original actions**

1. someone copies the dataset, changes its label or relies on broad project permission

**Exact source oracles — all required**

1. the purpose is not enabled

Legacy same-requirement reuse candidates: `TC-PRV-002-01`, `TC-PRV-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `apps/api/impact_api/ai_policy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
