## QA v1.3 — source-bound case design (proposed)

Story `FR-TEN-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-TEN-004-001` / `TC-IMPRANA-FR-TEN-004-001` | `REV_587b6d7ffb7d9af7aa2d964fe6421f04fc2a77ed660e467777f1ffc71b6a2555` / `REV_24978dd568587c781e916a28caf74c59fdf988110b3c74a37f3b0ef8cb087e7d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-004-002` / `TC-IMPRANA-FR-TEN-004-002` | `REV_517168aeaffd0078f0a912095b50177d3e9f517e63615fde041751bb17d631e4` / `REV_fb17e2d38a7f2785c0a4190e41958cde74380c794615f388ce3a867f85c38558` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-004-003` / `TC-IMPRANA-FR-TEN-004-003` | `REV_1c368ed3f3b651e2a3e66235fae5b4a3c82f39ef2f22fa054492fe6d13436f14` / `REV_2756045fdecdc3b75baddd0a15261715a0ec8496fcfc5c13912d354f16104516` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-004-004` / `TC-IMPRANA-FR-TEN-004-004` | `REV_c45079886937c38ba0f93462c8b0e4d0b2678f305850eb7e144c55266ba6d162` / `REV_b11b3043b07543ac896ae3e17ca8fd932ce65619705e6c7ad5b5aaa910aca564` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-TEN-004-001 — Preview and approve a configuration change

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-004-001` is not created. Verification duty `TASK-FR-TEN-004-03` (qualification); source `docs/backlog/backlog.csv` record 310, exact block `587b6d7ffb7d9af7aa2d964fe6421f04fc2a77ed660e467777f1ffc71b6a2555`.

**Original preconditions**

1. an Organisation Administrator proposes a label, code list, reporting calendar, time zone or unit change with an effective date

**Original actions**

1. they preview the change

**Exact source oracles — all required**

1. the preview lists dependent schedules and drafts
2. once approved the new version applies prospectively

Legacy same-requirement reuse candidates: `TC-TEN-004-01`, `TC-TEN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-004-002 — Historical objects keep their configuration version

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-004-002` is not created. Verification duty `TASK-FR-TEN-004-03` (qualification); source `docs/backlog/backlog.csv` record 310, exact block `517168aeaffd0078f0a912095b50177d3e9f517e63615fde041751bb17d631e4`.

**Original preconditions**

1. an output label has been renamed and the next fiscal year start changed

**Original actions**

1. a prior snapshot is opened

**Exact source oracles — all required**

1. its original labels and period membership remain reconstructable

Legacy same-requirement reuse candidates: `TC-TEN-004-01`, `TC-TEN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-004-003 — Reject a label edit that changes a stable code

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-004-003` is not created. Verification duty `TASK-FR-TEN-004-03` (qualification); source `docs/backlog/backlog.csv` record 310, exact block `1c368ed3f3b651e2a3e66235fae5b4a3c82f39ef2f22fa054492fe6d13436f14`.

**Original preconditions**

1. a code list entry with a stable code

**Original actions**

1. the Organisation Administrator edits its display label

**Exact source oracles — all required**

1. the stable code is not changed

Legacy same-requirement reuse candidates: `TC-TEN-004-01`, `TC-TEN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-004-004 — Reject an unsafe fiscal boundary change

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-004-004` is not created. Verification duty `TASK-FR-TEN-004-03` (qualification); source `docs/backlog/backlog.csv` record 310, exact block `c45079886937c38ba0f93462c8b0e4d0b2678f305850eb7e144c55266ba6d162`.

**Original preconditions**

1. an Organisation Administrator changes the fiscal year boundary

**Original actions**

1. they attempt to apply it without a new calendar and explicit regeneration of future obligations

**Exact source oracles — all required**

1. the change is rejected
2. a calendar that creates overlapping official periods is also rejected

Legacy same-requirement reuse candidates: `TC-TEN-004-01`, `TC-TEN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
