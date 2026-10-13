## QA v1.3 — source-bound case design (proposed)

Story `FR-WFL-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-WFL-006-001` / `TC-IMPRANA-FR-WFL-006-001` | `REV_b509c8763f37814612d8cb67852dac365ca4b99ca150da210b2447a223167643` / `REV_e569257e96c3536017ea09feb658ba42a5c3f65d23e3175cf2272f1fbe871de7` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-006-002` / `TC-IMPRANA-FR-WFL-006-002` | `REV_b4d501bbfa9660d5f230689b4936b268c1629700831f6b1492b7c41ee89c1c1e` / `REV_fffb75cad57f7b4526f75ce2af831ea3c2f6c561851c55b21b4bc60d0816d582` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-006-003` / `TC-IMPRANA-FR-WFL-006-003` | `REV_56ce18a3d1278a2f93c0dcd294ed2bac0c4afa08356470dd66f226294ade4386` / `REV_69c4663affee51e335b874306e6d42cca06c285d31caa45112ada7cd18c91f0d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-006-004` / `TC-IMPRANA-FR-WFL-006-004` | `REV_0f9d9fd43cfd4117dc1f2bc5187b30ea00846254cc1b44a94777267c2692ea20` / `REV_62ff9461871e8875f713d61b1915088bfd7e7788602b8f803d005d50979eba53` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-WFL-006-001 — Use the consolidated work centre

Source persona: Data Author. Proposed fixture `FIX-FR-WFL-006-001` is not created. Verification duty `TASK-FR-WFL-006-03` (qualification); source `docs/backlog/backlog.csv` record 320, exact block `b509c8763f37814612d8cb67852dac365ca4b99ca150da210b2447a223167643`.

**Original preconditions**

1. a Data Author with assignments, returned work, due obligations and security notices

**Original actions**

1. they open the work centre

**Exact source oracles — all required**

1. all of these items are consolidated in one place
2. they can choose permitted channels and digests
3. deadlines and escalations follow FD12
4. every notification has an event identity and per recipient delivery status

Legacy same-requirement reuse candidates: `TC-WFL-006-01`, `TC-WFL-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-006-002 — Retry an overdue reminder after a provider timeout

Source persona: Data Author. Proposed fixture `FIX-FR-WFL-006-002` is not created. Verification duty `TASK-FR-WFL-006-03` (qualification); source `docs/backlog/backlog.csv` record 320, exact block `b4d501bbfa9660d5f230689b4936b268c1629700831f6b1492b7c41ee89c1c1e`.

**Original preconditions**

1. an overdue reminder whose delivery timed out at the provider

**Original actions**

1. the reminder is retried

**Exact source oracles — all required**

1. one logical notice remains with traceable delivery attempts
2. no duplicate task is created

Legacy same-requirement reuse candidates: `TC-WFL-006-01`, `TC-WFL-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-006-003 — Reject muting mandatory security notices

Source persona: Data Author. Proposed fixture `FIX-FR-WFL-006-003` is not created. Verification duty `TASK-FR-WFL-006-03` (qualification); source `docs/backlog/backlog.csv` record 320, exact block `56ce18a3d1278a2f93c0dcd294ed2bac0c4afa08356470dd66f226294ade4386`.

**Original preconditions**

1. a mandatory security notice

**Original actions**

1. a Data Author tries to mute it

**Exact source oracles — all required**

1. muting is refused

Legacy same-requirement reuse candidates: `TC-WFL-006-01`, `TC-WFL-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-006-004 — Reject revealing content after failed delivery

Source persona: Data Author. Proposed fixture `FIX-FR-WFL-006-004` is not created. Verification duty `TASK-FR-WFL-006-03` (qualification); source `docs/backlog/backlog.csv` record 320, exact block `0f9d9fd43cfd4117dc1f2bc5187b30ea00846254cc1b44a94777267c2692ea20`.

**Original preconditions**

1. a notification whose delivery failed

**Original actions**

1. contact remediation is flagged

**Exact source oracles — all required**

1. the content is not revealed to unverified alternative contacts

Legacy same-requirement reuse candidates: `TC-WFL-006-01`, `TC-WFL-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
