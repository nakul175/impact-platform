## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-007-001` / `TC-IMPRANA-FR-CAL-007-001` | `REV_c2315dcafde4e9814d1cd5fca95186d280dfe1d1722534eda8966c9c95fc8c1a` / `REV_16085a7162606bf884c661ee887001c1212f69b31ea6106bd221a7ab3b506074` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-007-002` / `TC-IMPRANA-FR-CAL-007-002` | `REV_bf51713ce62e4c1f83c839cba84bfd722f4ff1159363b8733bbbb1cddd01900f` / `REV_0573d5efac9ba6e3fdeee0613327fccd1288f5992bb89c769330c0f4d7a3b701` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-007-003` / `TC-IMPRANA-FR-CAL-007-003` | `REV_2670060cca7638cefdad270cce0e0c79be678ff849215c5e29cdf384bdbb27b8` / `REV_43842ba89c20c98a92c9fae10e8f5fe01997d9d723db508fbf21cf9ac3b99e1d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-007-004` / `TC-IMPRANA-FR-CAL-007-004` | `REV_4c2c12bd660a0f6e89996837c519b1fc1e4077936f79e12cca501883f6cd6aeb` / `REV_b50abe88648a9cd01505fefb101a4e1b1d352afc599469d332e49da2bbcb2e5f` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-007-001 — Record a crosswalk

Source persona: Data Steward. Proposed fixture `FIX-FR-CAL-007-001` is not created. Verification duty `TASK-FR-CAL-007-03` (qualification); source `docs/backlog/backlog.csv` record 201, exact block `c2315dcafde4e9814d1cd5fca95186d280dfe1d1722534eda8966c9c95fc8c1a`.

**Original preconditions**

1. source and target dimension versions

**Original actions**

1. the Data Steward creates a crosswalk

**Exact source oracles — all required**

1. it records source and target versions, mapping type and information loss
2. exact mapping, many to one pooling and approved proportional allocation are distinct

Legacy same-requirement reuse candidates: `TC-CAL-007-01`, `TC-CAL-007-02`, `TC-AT08`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-007-002 — Preview shows gaps

Source persona: Data Steward. Proposed fixture `FIX-FR-CAL-007-002` is not created. Verification duty `TASK-FR-CAL-007-03` (qualification); source `docs/backlog/backlog.csv` record 201, exact block `bf51713ce62e4c1f83c839cba84bfd722f4ff1159363b8733bbbb1cddd01900f`.

**Original preconditions**

1. a crosswalk

**Original actions**

1. the Data Steward previews it

**Exact source oracles — all required**

1. unmapped and suppressed contributions are reported

Legacy same-requirement reuse candidates: `TC-CAL-007-01`, `TC-CAL-007-02`, `TC-AT08`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-007-003 — Reject splitting a broad band without data

Source persona: Data Steward. Proposed fixture `FIX-FR-CAL-007-003` is not created. Verification duty `TASK-FR-CAL-007-03` (qualification); source `docs/backlog/backlog.csv` record 201, exact block `2670060cca7638cefdad270cce0e0c79be678ff849215c5e29cdf384bdbb27b8`.

**Original preconditions**

1. one aggregate for ages 0 to 17

**Original actions**

1. a user attempts to convert it into 0 to 14

**Exact source oracles — all required**

1. exact transformation is blocked
2. the unresolved coverage remains visible

Legacy same-requirement reuse candidates: `TC-CAL-007-01`, `TC-CAL-007-02`, `TC-AT08`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-007-004 — Reject silently remapping unknown

Source persona: Data Steward. Proposed fixture `FIX-FR-CAL-007-004` is not created. Verification duty `TASK-FR-CAL-007-03` (qualification); source `docs/backlog/backlog.csv` record 201, exact block `4c2c12bd660a0f6e89996837c519b1fc1e4077936f79e12cca501883f6cd6aeb`.

**Original preconditions**

1. values coded unknown

**Original actions**

1. a crosswalk is applied

**Exact source oracles — all required**

1. unknown is not silently mapped to another category

Legacy same-requirement reuse candidates: `TC-CAL-007-01`, `TC-CAL-007-02`, `TC-AT08`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
