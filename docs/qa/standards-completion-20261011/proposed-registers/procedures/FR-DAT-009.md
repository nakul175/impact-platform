## QA v1.3 — source-bound case design (proposed)

Story `FR-DAT-009` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DAT-009-001` / `TC-IMPRANA-FR-DAT-009-001` | `REV_6a00079ac07b6d5903af08380332c3c7adf868853201ff3a0b64736f2e84cc46` / `REV_e0673d669a32c66368eb0a8b6e4575926509704435538e756326de6b382af584` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-009-002` / `TC-IMPRANA-FR-DAT-009-002` | `REV_7d51fb146bd5b2fa8c45d681ca85f46d10032bedbcd4d5b0113a3b3de7f73d60` / `REV_3ca0bdedfca51f5c2e5e82335b2779a24ddeee72dec99b03be22f9351fdb04df` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-009-003` / `TC-IMPRANA-FR-DAT-009-003` | `REV_8fe24c2363448c4411346d0403c3ba89158b2a804ae206691018f22ca2095275` / `REV_8a66c9fe148aae296d7c76b91247325ecde65d2fb22f246dea8b11fe5c8bcaab` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DAT-009-001 — Unit correction recalculates impacted indicators

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-009-001` is not created. Verification duty `TASK-FR-DAT-009-03` (qualification); source `docs/backlog/backlog.csv` record 72, exact block `6a00079ac07b6d5903af08380332c3c7adf868853201ff3a0b64736f2e84cc46`.

**Original preconditions**

1. an approved value recorded in kilograms

**Original actions**

1. an amendment correcting the unit to tonnes is approved

**Exact source oracles — all required**

1. a new revision is created and earlier values are retained where lawful
2. impacted indicators are recalculated under reviewed semantics
3. old reports remain frozen

Legacy same-requirement reuse candidates: `TC-DAT-009-01`, `TC-DAT-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_changes.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-009-002 — Bulk correction with itemised preview

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-009-002` is not created. Verification duty `TASK-FR-DAT-009-03` (qualification); source `docs/backlog/backlog.csv` record 72, exact block `7d51fb146bd5b2fa8c45d681ca85f46d10032bedbcd4d5b0113a3b3de7f73d60`.

**Original preconditions**

1. a bulk correction

**Original actions**

1. it is previewed and applied

**Exact source oracles — all required**

1. an itemised preview and outcome receipts are produced

Legacy same-requirement reuse candidates: `TC-DAT-009-01`, `TC-DAT-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_changes.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-009-003 — Reject editing calculated actuals

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-009-003` is not created. Verification duty `TASK-FR-DAT-009-03` (qualification); source `docs/backlog/backlog.csv` record 72, exact block `8fe24c2363448c4411346d0403c3ba89158b2a804ae206691018f22ca2095275`.

**Original preconditions**

1. a calculated actual

**Original actions**

1. a user tries to edit it through dataset correction

**Exact source oracles — all required**

1. the edit is refused
2. where deletion or minimisation policy applies, only a permitted change marker is kept instead of sensitive before and after values

Legacy same-requirement reuse candidates: `TC-DAT-009-01`, `TC-DAT-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_changes.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
