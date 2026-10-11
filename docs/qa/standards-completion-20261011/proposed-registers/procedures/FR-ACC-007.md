## QA v1.3 — source-bound case design (proposed)

Story `FR-ACC-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ACC-007-001` / `TC-IMPRANA-FR-ACC-007-001` | `REV_c5ff1289a2adb54b3aeb93d72f91c3115e25ec29cf50527f56e4bcd6ad76aa81` / `REV_3f9aaba9fe9f67fffc02abcf6fd54435c78015863eb72911d6dd048fb6d4746f` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-007-002` / `TC-IMPRANA-FR-ACC-007-002` | `REV_8a0df190e563514cc14ec3a9e39e0c52ea6af598c3cee1214fe572de84df9e9b` / `REV_feac32bcb1dd8068e81622c133ae3d95b27080621570457df57b0a85d61a25eb` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-007-003` / `TC-IMPRANA-FR-ACC-007-003` | `REV_ca0557ce7797b948ef2018734e818785f4daccad2bc1a4d642b07d4d0c485fcd` / `REV_cbeef4d96dcfbf9363cd82f4467b82212c4b7b79f14c9d3c591b1a426a7d2e45` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-007-004` / `TC-IMPRANA-FR-ACC-007-004` | `REV_2219ee066470d460902be324e4ea825e3786b7e9c84eb29f3fb2b007807672ba` / `REV_8a4a11b9d0295bb71c47bb685f96a7a83a50fc38633f071e598a665549d83c2a` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ACC-007-001 — Preview an export

Source persona: Analyst. Proposed fixture `FIX-FR-ACC-007-001` is not created. Verification duty `TASK-FR-ACC-007-03` (qualification); source `docs/backlog/backlog.csv` record 188, exact block `c5ff1289a2adb54b3aeb93d72f91c3115e25ec29cf50527f56e4bcd6ad76aa81`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. an Analyst prepares an export

**Exact source oracles — all required**

1. the preview lists selected fields, filters, classification, row estimate and intended format

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-007-01`, `TC-ACC-007-02`, `TC-AT13`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-007-002 — Authorise at each stage

Source persona: Analyst. Proposed fixture `FIX-FR-ACC-007-002` is not created. Verification duty `TASK-FR-ACC-007-03` (qualification); source `docs/backlog/backlog.csv` record 188, exact block `8a0df190e563514cc14ec3a9e39e0c52ea6af598c3cee1214fe572de84df9e9b`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the export is requested, starts execution, generates sensitive output and is downloaded

**Exact source oracles — all required**

1. authorisation is checked at each of those points
2. the receipt identifies the export owner and expiry

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-007-01`, `TC-ACC-007-02`, `TC-AT13`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-007-003 — Reject download after revocation

Source persona: Analyst. Proposed fixture `FIX-FR-ACC-007-003` is not created. Verification duty `TASK-FR-ACC-007-03` (qualification); source `docs/backlog/backlog.csv` record 188, exact block `ca0557ce7797b948ef2018734e818785f4daccad2bc1a4d642b07d4d0c485fcd`.

**Original preconditions**

1. an export has been generated

**Original actions**

1. the requester is revoked before download
2. retrieval is attempted from the original URL

**Exact source oracles — all required**

1. no bytes are served after the revocation bound

**Separate existing supplemental plan oracle (unapproved)**

1. retrieval is attempted from the original URL

Legacy same-requirement reuse candidates: `TC-ACC-007-01`, `TC-ACC-007-02`, `TC-AT13`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-007-004 — Reject reliance on an old signature

Source persona: Analyst. Proposed fixture `FIX-FR-ACC-007-004` is not created. Verification duty `TASK-FR-ACC-007-03` (qualification); source `docs/backlog/backlog.csv` record 188, exact block `2219ee066470d460902be324e4ea825e3786b7e9c84eb29f3fb2b007807672ba`.

**Original preconditions**

1. a generated download link

**Original actions**

1. it is used after the policy grant has ended

**Exact source oracles — all required**

1. access is refused because downloads must be authenticated or bound to a current approved disclosure

Legacy same-requirement reuse candidates: `TC-ACC-007-01`, `TC-ACC-007-02`, `TC-AT13`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
