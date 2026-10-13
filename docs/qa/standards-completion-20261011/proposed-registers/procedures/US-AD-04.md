## QA v1.3 — source-bound case design (proposed)

Story `US-AD-04` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-AD-04-001` / `TC-IMPRANA-US-AD-04-001` | `REV_da29d08e8c860dc13be698215f8da58024c7456b53146a7630d0f1dd108b2b80` / `REV_9f96ee0e42b5391cd09531998132e204ca72b3c0e16abeb1cbe3fd0ae15a8553` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-AD-04-002` / `TC-IMPRANA-US-AD-04-002` | `REV_d877af8e1643780fd71f0c027d27c86892f37146af9ad30ed3fae9e49536b93c` / `REV_e1add690579aa83e77b2936b0ace31aa05248289b9c8f01756a50afe7f67e9ac` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-AD-04-003` / `TC-IMPRANA-US-AD-04-003` | `REV_97d0b116f1166c90afb192d25f33bbffb136d9fb3504156278dd325c9f660705` / `REV_0ee5e40becfcb6c7bc1f1ad7fe927b08fc3cce82cd75dd755abab9dcbddf50b5` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-AD-04-001 — Configure nudge rules

Source persona: Programme Manager. Proposed fixture `FIX-US-AD-04-001` is not created. Verification duty `TASK-US-AD-04-03` (qualification); source `docs/backlog/backlog.csv` record 193, exact block `da29d08e8c860dc13be698215f8da58024c7456b53146a7630d0f1dd108b2b80`.

**Original preconditions**

1. a Programme Manager

**Original actions**

1. they configure a nudge rule for when usage drops

**Exact source oracles — all required**

1. the rule is saved

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-AD-04-002 — Colleague nudged when usage drops

Source persona: Programme Manager. Proposed fixture `FIX-US-AD-04-002` is not created. Verification duty `TASK-US-AD-04-03` (qualification); source `docs/backlog/backlog.csv` record 193, exact block `d877af8e1643780fd71f0c027d27c86892f37146af9ad30ed3fae9e49536b93c`.

**Original preconditions**

1. a nudge rule

**Original actions**

1. a colleague's usage drops and matches the rule

**Exact source oracles — all required**

1. the colleague receives a nudge

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-AD-04-003 — Reject nudging a user who opted out

Source persona: Programme Manager. Proposed fixture `FIX-US-AD-04-003` is not created. Verification duty `TASK-US-AD-04-03` (qualification); source `docs/backlog/backlog.csv` record 193, exact block `97d0b116f1166c90afb192d25f33bbffb136d9fb3504156278dd325c9f660705`.

**Original preconditions**

1. a colleague who has opted out of nudges

**Original actions**

1. their usage drops and matches a nudge rule

**Exact source oracles — all required**

1. they receive no nudge

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
