## QA v1.3 — source-bound case design (proposed)

Story `FR-PAR-002` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PAR-002-001` / `TC-IMPRANA-FR-PAR-002-001` | `REV_35464babf69c5367af9d5b69d1e4359e58d1d5a69262f6c9c4717ad4fea65483` / `REV_12797ebaf7a8341c6c33467c7c4f1aae9e0dca481b4bbb74ca5d3377a6645744` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PAR-002-002` / `TC-IMPRANA-FR-PAR-002-002` | `REV_1ceaec576a7b3c48c3fdb33738efebbf06433ffc4183105bfb143c08e5d84fc6` / `REV_936fb1dc071b9f5e5d7daf1822abebc3ce06e707bdc39d1f57581442a1478bb9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PAR-002-003` / `TC-IMPRANA-FR-PAR-002-003` | `REV_b68c43847c00d1037bc3094520ccb47a6b9ce4beacf1e431ce08f8e3fee7e175` / `REV_a644e42f850b2ebfc806ed7b933d4e51408e07d54bc6c2a0fa78be5ff2f4eae1` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PAR-002-001 — Analyst joins visits by pseudonym without seeing identity

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PAR-002-001` is not created. Verification duty `TASK-FR-PAR-002-03` (qualification); source `docs/backlog/backlog.csv` record 281, exact block `35464babf69c5367af9d5b69d1e4359e58d1d5a69262f6c9c4717ad4fea65483`.

**Original preconditions**

1. an Analyst without direct identity capability

**Original actions**

1. they join two visits for one participant using the programme pseudonym

**Exact source oracles — all required**

1. the join succeeds
2. they cannot resolve the person's name
3. they cannot resolve the person's participation in another programme

Legacy same-requirement reuse candidates: `TC-PAR-002-01`, `TC-PAR-002-02`, `TC-AT02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PAR-002-002 — Reject cross-project linkage without separate approval

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PAR-002-002` is not created. Verification duty `TASK-FR-PAR-002-03` (qualification); source `docs/backlog/backlog.csv` record 281, exact block `1ceaec576a7b3c48c3fdb33738efebbf06433ffc4183105bfb143c08e5d84fc6`.

**Original preconditions**

1. participant records in two projects

**Original actions**

1. a user attempts to link them without a separately approved purpose, a matching contract and authority to both scopes

**Exact source oracles — all required**

1. the linkage is refused

Legacy same-requirement reuse candidates: `TC-PAR-002-01`, `TC-PAR-002-02`, `TC-AT02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PAR-002-003 — Reject using a pseudonym as a universal identifier

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PAR-002-003` is not created. Verification duty `TASK-FR-PAR-002-03` (qualification); source `docs/backlog/backlog.csv` record 281, exact block `b68c43847c00d1037bc3094520ccb47a6b9ce4beacf1e431ce08f8e3fee7e175`.

**Original preconditions**

1. a pseudonym scoped to one approved programme

**Original actions**

1. it is used to identify the person outside that programme or matching agreement

**Exact source oracles — all required**

1. it does not resolve to the person

Legacy same-requirement reuse candidates: `TC-PAR-002-01`, `TC-PAR-002-02`, `TC-AT02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
