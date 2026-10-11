## QA v1.3 — source-bound case design (proposed)

Story `FR-OFF-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OFF-005-001` / `TC-IMPRANA-FR-OFF-005-001` | `REV_e0df61495080c4ac0c4cca803722d8e171dc7193fd5e0e21807e3e4b71343a8c` / `REV_cde8682038700b09e69545d4e452d47d34ae9e6ac44c24874e57b8a6b537dd90` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-005-002` / `TC-IMPRANA-FR-OFF-005-002` | `REV_21ccd1b3e9a386c6ea2750a565210806c08c30ae96623cc102357f05f9d5fc22` / `REV_65fa79a0e7aa5c399d2f11b179e0a0471d881c663a3ec51820b8dc9efbfa37a9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-005-003` / `TC-IMPRANA-FR-OFF-005-003` | `REV_d58b81b2d96c33bc0425a55a0f228ae4bc4a3a342167bc9a9ae40e9a26834f6f` / `REV_25e057f46d3622567096e8c73c7ba516f814f3cd5f9548dbf40fa48116ab1131` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-005-004` / `TC-IMPRANA-FR-OFF-005-004` | `REV_896463841b249534f23258bf4cf245cd5cd15780c5664fde564fb731bcc08cd8` / `REV_f5fb3c756e9c09b8e771fa8e3e9bf050dfefde881de8ef4eca3c6fa568180db6` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OFF-005-001 — Offline unlock and expiry

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-OFF-005-001` is not created. Verification duty `TASK-FR-OFF-005-03` (qualification); source `docs/backlog/backlog.csv` record 275, exact block `e0df61495080c4ac0c4cca803722d8e171dc7193fd5e0e21807e3e4b71343a8c`.

**Original preconditions**

1. a collector with an offline grant

**Original actions**

1. they unlock the device offline and later the grant expires

**Exact source oracles — all required**

1. unlocking requires the qualified local authentication policy
2. after expiry further protected viewing or capture under that grant is prevented

Legacy same-requirement reuse candidates: `TC-OFF-005-01`, `TC-OFF-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-005-002 — Removal and wipe outcomes are reported

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-OFF-005-002` is not created. Verification duty `TASK-FR-OFF-005-03` (qualification); source `docs/backlog/backlog.csv` record 275, exact block `21ccd1b3e9a386c6ea2750a565210806c08c30ae96623cc102357f05f9d5fc22`.

**Original preconditions**

1. a package removal or remote wipe request

**Original actions**

1. its status is viewed

**Exact source oracles — all required**

1. it reports requested, confirmed or unknown

Legacy same-requirement reuse candidates: `TC-OFF-005-01`, `TC-OFF-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-005-003 — Reject a revoked collector after expiry

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-OFF-005-003` is not created. Verification duty `TASK-FR-OFF-005-03` (qualification); source `docs/backlog/backlog.csv` record 275, exact block `d58b81b2d96c33bc0425a55a0f228ae4bc4a3a342167bc9a9ae40e9a26834f6f`.

**Original preconditions**

1. a disconnected collector is revoked
2. time advances beyond the grant expiry

**Original actions**

1. the collector reconnects

**Exact source oracles — all required**

1. viewing is blocked locally
2. uploads are rejected or explicitly quarantined
3. quarantined uploads never become approved data automatically

Legacy same-requirement reuse candidates: `TC-OFF-005-01`, `TC-OFF-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-005-004 — Reject clock rollback

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-OFF-005-004` is not created. Verification duty `TASK-FR-OFF-005-03` (qualification); source `docs/backlog/backlog.csv` record 275, exact block `896463841b249534f23258bf4cf245cd5cd15780c5664fde564fb731bcc08cd8`.

**Original preconditions**

1. the device clock is rolled back

**Original actions**

1. the collector tries to continue offline work

**Exact source oracles — all required**

1. the verified authority window is not extended

Legacy same-requirement reuse candidates: `TC-OFF-005-01`, `TC-OFF-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
