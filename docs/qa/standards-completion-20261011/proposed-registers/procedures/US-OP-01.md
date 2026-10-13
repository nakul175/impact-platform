## QA v1.3 — source-bound case design (proposed)

Story `US-OP-01` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-OP-01-001` / `TC-IMPRANA-US-OP-01-001` | `REV_3b61a46c253b6106ac9c9f9ed68e5995e9dad4d1b943c9f6082a1ad5fdcfbb3a` / `REV_d800a718a443e09d0bf0c260ad58e154a0fc58b488070cd238bc00688e8f2e3a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-OP-01-002` / `TC-IMPRANA-US-OP-01-002` | `REV_072e72e3776662f48ed02e4e068c7ab11f359bb8f55b84a310ccbc44a0c99cf0` / `REV_aac6056e8e813040b8781566ea8e48abd33f829f07e868abcce7fc4dc99bdb24` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-OP-01-003` / `TC-IMPRANA-US-OP-01-003` | `REV_6e2cbace14f30a576140ee7f696815547b371003976279b6a6d93976cc34b214` / `REV_43abf178f422273bdd343550e07562250173259d38fbfcd371faecd4a00401d5` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-OP-01-001 — Case queue shows stage and next action

Source persona: Imprana Advisor. Proposed fixture `FIX-US-OP-01-001` is not created. Verification duty `TASK-US-OP-01-03` (qualification); source `docs/backlog/backlog.csv` record 122, exact block `3b61a46c253b6106ac9c9f9ed68e5995e9dad4d1b943c9f6082a1ad5fdcfbb3a`.

**Original preconditions**

1. an Imprana Advisor managing several organisations

**Original actions**

1. they open the case queue

**Exact source oracles — all required**

1. each organisation's stage and next action are shown

Original proposed anchors (file/artifact candidates only): `qualification/test_human_advice_live.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-OP-01-002 — Filter the queue

Source persona: Imprana Advisor. Proposed fixture `FIX-US-OP-01-002` is not created. Verification duty `TASK-US-OP-01-03` (qualification); source `docs/backlog/backlog.csv` record 122, exact block `072e72e3776662f48ed02e4e068c7ab11f359bb8f55b84a310ccbc44a0c99cf0`.

**Original preconditions**

1. the case queue

**Original actions**

1. the Imprana Advisor filters by stage, cohort or urgency

**Exact source oracles — all required**

1. only matching organisations are shown

Original proposed anchors (file/artifact candidates only): `qualification/test_human_advice_live.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-OP-01-003 — Reject non-matching results

Source persona: Imprana Advisor. Proposed fixture `FIX-US-OP-01-003` is not created. Verification duty `TASK-US-OP-01-03` (qualification); source `docs/backlog/backlog.csv` record 122, exact block `6e2cbace14f30a576140ee7f696815547b371003976279b6a6d93976cc34b214`.

**Original preconditions**

1. a filter applied to the case queue

**Original actions**

1. the queue is shown

**Exact source oracles — all required**

1. no organisation that does not match the filter is listed

Original proposed anchors (file/artifact candidates only): `qualification/test_human_advice_live.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
