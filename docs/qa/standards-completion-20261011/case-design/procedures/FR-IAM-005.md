## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-005-001` / `TC-IMPRANA-FR-IAM-005-001` | `REV_414f2d121f18235ffad9e2039843a6588574f665b40f81ded2946e7334bfcf3a` / `REV_2e4e7569dea6bb8a524d393edaa854b2534b319a9eca8001072ea082438242aa` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-005-002` / `TC-IMPRANA-FR-IAM-005-002` | `REV_61612119685b9260313c2d749d80afbf11701fd8e5ed23413a85086aa58b99d1` / `REV_b7e3c71d55ef33ec5ec956cd428c3b3de6f6e051ae33078105c636a6707e3866` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-005-003` / `TC-IMPRANA-FR-IAM-005-003` | `REV_2cee8b7dacea6179e18e44329c387f8f49ad0679b5771ade709746ef84fba837` / `REV_94337077eb5e812bf6cac8733e5f6a11b49b097efce43db2977d8bf825b60b91` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-005-004` / `TC-IMPRANA-FR-IAM-005-004` | `REV_9e1ba923bb08d64cddf5c285b7745988a4ac0f50813c8eef65cb39af24fd15aa` / `REV_fd3e7f3868c75cd22731b7b17d793e699fd77fa01c0c33a0054f372b3a97be78` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-005-001 — Provision from the directory

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-005-001` is not created. Verification duty `TASK-FR-IAM-005-03` (qualification); source `docs/backlog/backlog.csv` record 345, exact block `414f2d121f18235ffad9e2039843a6588574f665b40f81ded2946e7334bfcf3a`.

**Original preconditions**

1. a directory connection that declares authoritative attributes and groups

**Original actions**

1. a directory user is provisioned

**Exact source oracles — all required**

1. a pending or active membership is created only within the configured scope

Legacy same-requirement reuse candidates: `TC-IAM-005-01`, `TC-IAM-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-005-002 — Deactivate a user who owns a job

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-005-002` is not created. Verification duty `TASK-FR-IAM-005-03` (qualification); source `docs/backlog/backlog.csv` record 345, exact block `61612119685b9260313c2d749d80afbf11701fd8e5ed23413a85086aa58b99d1`.

**Original preconditions**

1. a directory user owns a job

**Original actions**

1. the user is deactivated in the directory

**Exact source oracles — all required**

1. derived access is removed, sessions are revoked and ownership reassignment tasks are opened
2. within the BRD revocation bound further access fails
3. the job is cancelled or explicitly reassigned

Legacy same-requirement reuse candidates: `TC-IAM-005-01`, `TC-IAM-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-005-003 — Reconcile directory and platform

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-005-003` is not created. Verification duty `TASK-FR-IAM-005-03` (qualification); source `docs/backlog/backlog.csv` record 345, exact block `2cee8b7dacea6179e18e44329c387f8f49ad0679b5771ade709746ef84fba837`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the Organisation Administrator views reconciliation

**Exact source oracles — all required**

1. differences between the directory and the platform are shown

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-005-01`, `TC-IAM-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-005-004 — Reject manual override of directory-controlled attributes

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-005-004` is not created. Verification duty `TASK-FR-IAM-005-03` (qualification); source `docs/backlog/backlog.csv` record 345, exact block `9e1ba923bb08d64cddf5c285b7745988a4ac0f50813c8eef65cb39af24fd15aa`.

**Original preconditions**

1. an attribute controlled by the directory

**Original actions**

1. an administrator manually overrides it without a recorded bounded exception

**Exact source oracles — all required**

1. the override is rejected
2. a manual grant may add only separately authorised scope and is removed if policy forbids local supplements

Legacy same-requirement reuse candidates: `TC-IAM-005-01`, `TC-IAM-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
