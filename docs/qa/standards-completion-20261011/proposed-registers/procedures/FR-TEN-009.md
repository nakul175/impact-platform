## QA v1.3 — source-bound case design (proposed)

Story `FR-TEN-009` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-TEN-009-001` / `TC-IMPRANA-FR-TEN-009-001` | `REV_c7e069efdcaa71ea3c4f95b59a55a753b2efbf138001d3958491335ccaaf929b` / `REV_39428a1299d966093060b1111b3fe4db02287e920bab62dbc0dc8f8a5b86a0ad` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-009-002` / `TC-IMPRANA-FR-TEN-009-002` | `REV_8e0468959ccd2200143a07de9f4f66c3c58bdd6d046911f51eef4b2e4579096c` / `REV_f28c6f3f6c8e4dee84e723b9fbec2bb83e925ac150835c383d5066052dde0be5` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-009-003` / `TC-IMPRANA-FR-TEN-009-003` | `REV_7c3945570fd8f3fdffd82c8025cf513a99cf68571344e1471cf2b5026c148855` / `REV_018b4c5bd0efe4f388f10b0fc6055dd407cd7729661bff38a3bd99dab005d592` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-009-004` / `TC-IMPRANA-FR-TEN-009-004` | `REV_24fd4d94d9ffc50fd4f5131b57db256a7b9e3f230582be2b05f25547945e834c` / `REV_cec8e46cce4cbdd9a4631e1005336b44436d097e743d0f2961845dbadf24daa6` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-009-005` / `TC-IMPRANA-FR-TEN-009-005` | `REV_2abb82ae9c22e7d1dcfd17b92a45118ded15b1a2d9c7f42a0f32a5d8902dc142` / `REV_a5fcb05c8f6dc8c1fadb6aee7c257e6eb63e7c77e1abd6daa8189f1f3abc7344` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-TEN-009-001 — Preview and publish a theme

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-009-001` is not created. Verification duty `TASK-FR-TEN-009-03` (qualification); source `docs/backlog/backlog.csv` record 363, exact block `c7e069efdcaa71ea3c4f95b59a55a753b2efbf138001d3958491335ccaaf929b`.

**Original preconditions**

1. approved logos, accessible colours, tenant name and report styles

**Original actions**

1. the Organisation Administrator previews and publishes the theme

**Exact source oracles — all required**

1. only presentation changes

Legacy same-requirement reuse candidates: `TC-TEN-009-01`, `TC-TEN-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-009-002 — Activate an external domain

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-009-002` is not created. Verification duty `TASK-FR-TEN-009-03` (qualification); source `docs/backlog/backlog.csv` record 363, exact block `8e0468959ccd2200143a07de9f4f66c3c58bdd6d046911f51eef4b2e4579096c`.

**Original preconditions**

1. an external domain has been added

**Original actions**

1. verified control and an active renewal or revocation owner are recorded

**Exact source oracles — all required**

1. the domain becomes active
2. until then it remains pending

Legacy same-requirement reuse candidates: `TC-TEN-009-01`, `TC-TEN-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-009-003 — Reject an inaccessible theme

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-009-003` is not created. Verification duty `TASK-FR-TEN-009-03` (qualification); source `docs/backlog/backlog.csv` record 363, exact block `7c3945570fd8f3fdffd82c8025cf513a99cf68571344e1471cf2b5026c148855`.

**Original preconditions**

1. reports are served with an accessible theme

**Original actions**

1. the Organisation Administrator attempts to publish a theme with a low contrast colour palette

**Exact source oracles — all required**

1. publication of the failing theme is blocked
2. the prior accessible theme continues to serve reports

Legacy same-requirement reuse candidates: `TC-TEN-009-01`, `TC-TEN-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-009-004 — Reject unsafe assets and branding that hides mandatory content

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-009-004` is not created. Verification duty `TASK-FR-TEN-009-03` (qualification); source `docs/backlog/backlog.csv` record 363, exact block `24fd4d94d9ffc50fd4f5131b57db256a7b9e3f230582be2b05f25547945e834c`.

**Original preconditions**

1. the Organisation Administrator is editing branding

**Original actions**

1. they upload an asset that fails file safety checks or configure branding that hides mandatory caveats, approval status or the actual organisation

**Exact source oracles — all required**

1. the asset or branding is rejected

Legacy same-requirement reuse candidates: `TC-TEN-009-01`, `TC-TEN-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-009-005 — Reject fallback when domain verification expires

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-009-005` is not created. Verification duty `TASK-FR-TEN-009-03` (qualification); source `docs/backlog/backlog.csv` record 363, exact block `2abb82ae9c22e7d1dcfd17b92a45118ded15b1a2d9c7f42a0f32a5d8902dc142`.

**Original preconditions**

1. an external domain whose verification has expired

**Original actions**

1. the domain is requested

**Exact source oracles — all required**

1. the domain is disabled
2. no fallback tenant is opened

Legacy same-requirement reuse candidates: `TC-TEN-009-01`, `TC-TEN-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
