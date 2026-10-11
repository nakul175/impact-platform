## QA v1.3 — source-bound case design (proposed)

Story `FR-ACC-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ACC-001-001` / `TC-IMPRANA-FR-ACC-001-001` | `REV_ee0284aca0ba1089c94c143fc7018d45fe1b30954fafa01128aa362d66df80ed` / `REV_eb41d6ae2ddefb19d23f6600086bd47ae72ac80bed1484a76ff477ab0aff2360` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-001-002` / `TC-IMPRANA-FR-ACC-001-002` | `REV_9dd3ba243027ab65a3914290a1f24e964d6b77a5408baaee5d68d8a121946c86` / `REV_63e1b5a0c3f4c8e9270eb02435b4097ff681e50246dd6593f0efba6b62c43e21` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-001-003` / `TC-IMPRANA-FR-ACC-001-003` | `REV_1b353b63b08ee384cf7de481e209e2a06049ffc6df9ddabc96bc6214326f38d6` / `REV_17327e1aba28292206bd9eadef9d9703222caefb3b921168e86a1a765057fc28` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-001-004` / `TC-IMPRANA-FR-ACC-001-004` | `REV_b8c4ddb75a2109e3aa383d63e58881aef47a81b7c070ed48e47c72f706ff6e13` / `REV_69bdab7e032303756d36716fc947ef911ff70296e82a8980d6afc94a5dd70f12` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ACC-001-001 — Authorise every resource and reference

Source persona: Platform Operator. Proposed fixture `FIX-FR-ACC-001-001` is not created. Verification duty `TASK-FR-ACC-001-03` (qualification); source `docs/backlog/backlog.csv` record 19, exact block `ee0284aca0ba1089c94c143fc7018d45fe1b30954fafa01128aa362d66df80ed`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a request reads or writes a resource

**Exact source oracles — all required**

1. the resource and each related reference are authorised before access
2. a client supplied tenant or object ID is treated only as a selector

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-001-01`, `TC-ACC-001-02`, `TC-AT11`, `SEC-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-001-002 — Check batch items individually

Source persona: Platform Operator. Proposed fixture `FIX-FR-ACC-001-002` is not created. Verification duty `TASK-FR-ACC-001-03` (qualification); source `docs/backlog/backlog.csv` record 19, exact block `9dd3ba243027ab65a3914290a1f24e964d6b77a5408baaee5d68d8a121946c86`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a batch request is submitted

**Exact source oracles — all required**

1. each item is checked
2. only permitted item outcomes are exposed

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-001-01`, `TC-ACC-001-02`, `TC-AT11`, `SEC-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-001-003 — Reject a cross tenant reference

Source persona: Platform Operator. Proposed fixture `FIX-FR-ACC-001-003` is not created. Verification duty `TASK-FR-ACC-001-03` (qualification); source `docs/backlog/backlog.csv` record 19, exact block `1b353b63b08ee384cf7de481e209e2a06049ffc6df9ddabc96bc6214326f38d6`.

**Original preconditions**

1. a valid form submission

**Original actions**

1. the participant ID is replaced with one from another tenant

**Exact source oracles — all required**

1. the reference is rejected
2. no cross tenant relationship is recorded

Legacy same-requirement reuse candidates: `TC-ACC-001-01`, `TC-ACC-001-02`, `TC-AT11`, `SEC-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-001-004 — Reject leaky responses and failing open

Source persona: Platform Operator. Proposed fixture `FIX-FR-ACC-001-004` is not created. Verification duty `TASK-FR-ACC-001-03` (qualification); source `docs/backlog/backlog.csv` record 19, exact block `b8c4ddb75a2109e3aa383d63e58881aef47a81b7c070ed48e47c72f706ff6e13`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a protected unknown ID is requested or policy cannot be resolved

**Exact source oracles — all required**

1. RESOURCE_UNAVAILABLE is returned without record names or counts
2. the action is denied rather than using a cached broad role

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-001-01`, `TC-ACC-001-02`, `TC-AT11`, `SEC-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
