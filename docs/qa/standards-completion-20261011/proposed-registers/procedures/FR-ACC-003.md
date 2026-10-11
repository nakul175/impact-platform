## QA v1.3 — source-bound case design (proposed)

Story `FR-ACC-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ACC-003-001` / `TC-IMPRANA-FR-ACC-003-001` | `REV_31074da1d568bbef3bae19326ba1c549e9fd09b334d8d8a00e16bc3aad28f403` / `REV_72d2a89c1171b52a8ef1985d0ad2ee36a36ab312e9986357423dec29a8815f25` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-003-002` / `TC-IMPRANA-FR-ACC-003-002` | `REV_aeb28b1850c575afe0729abe2cbb9f903682282e881665d856c9cb828958c88a` / `REV_7d7339bc34bb6606b7b152066397bf0c75a56cabfd0469bd6d344fd7d1e69895` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-003-003` / `TC-IMPRANA-FR-ACC-003-003` | `REV_17aea8d29e2ef4d196e20133925645f29aa3032032fe1d744168d3027eef0083` / `REV_2ada37006407195864e696740803da387229ae56c9cbf44a5b33faf935ae3135` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-003-004` / `TC-IMPRANA-FR-ACC-003-004` | `REV_aac441b0dab41fd767d8f61e2e879f942c113c0d3a6f8d3ef3d21182bcafd0b0` / `REV_93000fa33c7cf32f0e0cc9bfd025c9fc331cc19f9c76e821753079e27686287f` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ACC-003-001 — Inspect effective access

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-003-001` is not created. Verification duty `TASK-FR-ACC-003-03` (qualification); source `docs/backlog/backlog.csv` record 21, exact block `31074da1d568bbef3bae19326ba1c549e9fd09b334d8d8a00e16bc3aad28f403`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the Organisation Administrator inspects effective access for a selected action and a subject within their administration scope

**Exact source oracles — all required**

1. each permitted grant path, restriction and missing assurance is shown

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-003-01`, `TC-ACC-003-02`, `IT-006`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Native tenant-fence tests do not establish own-access capability/grant-path explanations for every source path.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-003-002 — Explain a normal user's own access

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-003-002` is not created. Verification duty `TASK-FR-ACC-003-03` (qualification); source `docs/backlog/backlog.csv` record 21, exact block `aeb28b1850c575afe0729abe2cbb9f903682282e881665d856c9cb828958c88a`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a normal user inspects their own access

**Exact source oracles — all required**

1. they see explanations only about their own permitted context

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-003-01`, `TC-ACC-003-02`, `IT-006`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Native tenant-fence tests do not establish own-access capability/grant-path explanations for every source path.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-003-003 — Resolve conflicting roles

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-003-003` is not created. Verification duty `TASK-FR-ACC-003-03` (qualification); source `docs/backlog/backlog.csv` record 21, exact block `17aea8d29e2ef4d196e20133925645f29aa3032032fe1d744168d3027eef0083`.

**Original preconditions**

1. a person has both analyst and partner templates
2. a restriction applies to another partner's rows

**Original actions**

1. their access is inspected

**Exact source oracles — all required**

1. the restriction remains effective
2. the explanation identifies the scope rule safely

Legacy same-requirement reuse candidates: `TC-ACC-003-01`, `TC-ACC-003-02`, `IT-006`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Native tenant-fence tests do not establish own-access capability/grant-path explanations for every source path.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-003-004 — Reject leaking hidden information

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-003-004` is not created. Verification duty `TASK-FR-ACC-003-03` (qualification); source `docs/backlog/backlog.csv` record 21, exact block `aac441b0dab41fd767d8f61e2e879f942c113c0d3a6f8d3ef3d21182bcafd0b0`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a denial is explained or the Organisation Administrator attempts to simulate a subject outside their administration scope

**Exact source oracles — all required**

1. names of hidden projects and sensitive field values are not exposed
2. the out of scope simulation is refused

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-003-01`, `TC-ACC-003-02`, `IT-006`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Native tenant-fence tests do not establish own-access capability/grant-path explanations for every source path.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
