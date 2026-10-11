## QA v1.3 — source-bound case design (proposed)

Story `FR-UX-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-UX-004-001` / `TC-IMPRANA-FR-UX-004-001` | `REV_02bcf5db55931ccf6c7feda8fe42c267cfca95b48373733249db0d5d3462d58e` / `REV_ea8e467dbe2f6b23e8ba617af1ef70da20e1188b2f4eefb95de9427a6ae883c0` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-004-002` / `TC-IMPRANA-FR-UX-004-002` | `REV_07483dec5b14c52feb227418c8530cf88f0ea1ba0dc917a3d54a1feb87098350` / `REV_44f78df0fafa6f97293df7a620d52d5f6ca0556ca3fb28444948b7062d6902e9` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-004-003` / `TC-IMPRANA-FR-UX-004-003` | `REV_bd31370b738afd2f1e124f043b9b129979144cfa36e5773cd7250a821d3fb0c4` / `REV_98b63556ea1e247568745872a6a7ef86b3baaa60dea0fca478408f2dde715c68` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-004-004` / `TC-IMPRANA-FR-UX-004-004` | `REV_4b7f27ed1d6da9ff69e81c212bc46f834cbae96665be170680f55070d90d4459` / `REV_d714e3afe1cb1d400e92387a334a54c16a3a0ec8aa7fbe70db98ca442c252bd3` | manual → MANUAL recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-UX-004-001 — Complete core work with keyboard and screen reader

Source persona: Data Author. Proposed fixture `FIX-FR-UX-004-001` is not created. Verification duty `TASK-FR-UX-004-03` (qualification); source `docs/backlog/backlog.csv` record 171, exact block `02bcf5db55931ccf6c7feda8fe42c267cfca95b48373733249db0d5d3462d58e`.

**Original preconditions**

1. a Data Author using a keyboard and a qualified screen reader

**Original actions**

1. they complete collection, correction and approval
2. they encounter an invalid field and a stale revision conflict

**Exact source oracles — all required**

1. every step is completed with accessible labels, visible focus and understandable errors

**Separate existing supplemental plan oracle (unapproved)**

1. they encounter an invalid field and a stale revision conflict

Legacy same-requirement reuse candidates: `TC-UX-004-01`, `TC-UX-004-02`, `TC-AT30`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-004-002 — Alternatives for drag actions, charts and async changes

Source persona: Data Author. Proposed fixture `FIX-FR-UX-004-002` is not created. Verification duty `TASK-FR-UX-004-03` (qualification); source `docs/backlog/backlog.csv` record 171, exact block `07483dec5b14c52feb227418c8530cf88f0ea1ba0dc917a3d54a1feb87098350`.

**Original preconditions**

1. a drag action, a chart and an asynchronous state change

**Original actions**

1. they are used without a mouse or sight

**Exact source oracles — all required**

1. the drag action offers buttons or ordered lists
2. the chart offers a table
3. the state change is announced without unexpectedly moving focus

Legacy same-requirement reuse candidates: `TC-UX-004-01`, `TC-UX-004-02`, `TC-AT30`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-004-003 — Reject inaccessible authentication

Source persona: Data Author. Proposed fixture `FIX-FR-UX-004-003` is not created. Verification duty `TASK-FR-UX-004-03` (qualification); source `docs/backlog/backlog.csv` record 171, exact block `bd31370b738afd2f1e124f043b9b129979144cfa36e5773cd7250a821d3fb0c4`.

**Original preconditions**

1. a Data Author signing in

**Original actions**

1. authentication presents a challenge

**Exact source oracles — all required**

1. password managers are supported
2. an accessible alternative to the challenge is available

Legacy same-requirement reuse candidates: `TC-UX-004-01`, `TC-UX-004-02`, `TC-AT30`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-004-004 — Reject waiving conformance because of user content

Source persona: Data Author. Proposed fixture `FIX-FR-UX-004-004` is not created. Verification duty `TASK-FR-UX-004-03` (qualification); source `docs/backlog/backlog.csv` record 171, exact block `4b7f27ed1d6da9ff69e81c212bc46f834cbae96665be170680f55070d90d4459`.

**Original preconditions**

1. user-supplied content with accessibility limitations

**Original actions**

1. conformance is assessed

**Exact source oracles — all required**

1. the limitations are reported
2. product process conformance is not waived

Legacy same-requirement reuse candidates: `TC-UX-004-01`, `TC-UX-004-02`, `TC-AT30`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
