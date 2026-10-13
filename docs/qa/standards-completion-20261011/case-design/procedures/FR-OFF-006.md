## QA v1.3 — source-bound case design (proposed)

Story `FR-OFF-006` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OFF-006-001` / `TC-IMPRANA-FR-OFF-006-001` | `REV_8d0f64d40c09146285062b0008b6c58b498ac64d884895255c88901425bdee23` / `REV_65a8f0cc110031efd23b150c457d97dc01f5f2ba9782bf3adede5c4de0f4ab9d` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-006-002` / `TC-IMPRANA-FR-OFF-006-002` | `REV_04ce61bf4e5aa1ef40205625c7781f702a8a04cf9792ffcbca6e22a36c35057b` / `REV_6931ef79f4dd0fed7225cb0400ce9f1996f588975efc02d6f938633874919c97` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-006-003` / `TC-IMPRANA-FR-OFF-006-003` | `REV_54b6c2786e5b752aff4b32895f1349c353033dd063ab8d49059a6cf373378103` / `REV_a2b0486e6b3b553e55fc5f3d4415d13b98a93f15d335cf347c5fcd4fa4f74bb1` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OFF-006-001 — Switching accounts protects the previous workspace

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-006-001` is not created. Verification duty `TASK-FR-OFF-006-03` (qualification); source `docs/backlog/backlog.csv` record 276, exact block `8d0f64d40c09146285062b0008b6c58b498ac64d884895255c88901425bdee23`.

**Original preconditions**

1. collector A leaves two unsynchronised forms on a shared device

**Original actions**

1. collector B signs in

**Exact source oracles — all required**

1. A's workspace is closed and its unsynchronised count is shown without content
2. B sees neither the answers nor participant names
3. A's authorship remains unchanged

Legacy same-requirement reuse candidates: `TC-OFF-006-01`, `TC-OFF-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-006-002 — Handover requires eligible actors

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-006-002` is not created. Verification duty `TASK-FR-OFF-006-03` (qualification); source `docs/backlog/backlog.csv` record 276, exact block `04ce61bf4e5aa1ef40205625c7781f702a8a04cf9792ffcbca6e22a36c35057b`.

**Original preconditions**

1. pending work needs to be handed over

**Original actions**

1. the handover is performed

**Exact source oracles — all required**

1. both eligible actors are online or a separately qualified secure supervisor procedure is used

Legacy same-requirement reuse candidates: `TC-OFF-006-01`, `TC-OFF-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-006-003 — Reject authorship transfer or silent deletion

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-006-003` is not created. Verification duty `TASK-FR-OFF-006-03` (qualification); source `docs/backlog/backlog.csv` record 276, exact block `54b6c2786e5b752aff4b32895f1349c353033dd063ab8d49059a6cf373378103`.

**Original preconditions**

1. collector A has pending work on the device

**Original actions**

1. collector B continues on the device or A logs out

**Exact source oracles — all required**

1. author identity is never transferred to B
2. pending work may be locked for later recovery
3. it is deleted only after an explicit loss warning and permitted confirmation

Legacy same-requirement reuse candidates: `TC-OFF-006-01`, `TC-OFF-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
