## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-012` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-012-001` / `TC-IMPRANA-FR-IAM-012-001` | `REV_29ad17013eb7d874a069d5ea8c5f1527537495db43d415d76a846cd9e4b4a800` / `REV_65be814f2c33f22f9d94083a1088d381984b9d9adb6001e77b3f255cdc88208b` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-012-002` / `TC-IMPRANA-FR-IAM-012-002` | `REV_b0bfa8ef31d32348bf770147a1fe41faedb325f543653627899610a2db5371b0` / `REV_c3ccecf95f839a2d88228b0ac7d082054c3a621f519eabf7b85a54ca8baf4e05` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-012-003` / `TC-IMPRANA-FR-IAM-012-003` | `REV_a7597c5c564bb40f6914408288270b6c2762a3ff60b3016c9a504834e4857206` / `REV_c3c6efbf8541bd66891dd335e6b1917d60e0ad74a02ac1f6b67e175a5275d60d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-012-004` / `TC-IMPRANA-FR-IAM-012-004` | `REV_e4eecb849a2103fdb096e15dfc6f32f764fc6e3660aa1475b84dfccda6ea52f4` / `REV_a9b764f1f91425ca211d5a1ab0032430911bcf44b4b3568eb7e20fe5918bdfe6` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-012-001 — Create a service identity

Source persona: Integration Developer. Proposed fixture `FIX-FR-IAM-012-001` is not created. Verification duty `TASK-FR-IAM-012-03` (qualification); source `docs/backlog/backlog.csv` record 241, exact block `29ad17013eb7d874a069d5ea8c5f1527537495db43d415d76a846cd9e4b4a800`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. an Integration Developer creates a machine identity with purpose, allowed resources, operations and expiry

**Exact source oracles — all required**

1. the secret is shown once at issue
2. afterwards only a safe reference to it is shown

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-012-01`, `TC-IAM-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-012-002 — Rotate during a retried connector run

Source persona: Integration Developer. Proposed fixture `FIX-FR-IAM-012-002` is not created. Verification duty `TASK-FR-IAM-012-03` (qualification); source `docs/backlog/backlog.csv` record 241, exact block `b0bfa8ef31d32348bf770147a1fe41faedb325f543653627899610a2db5371b0`.

**Original preconditions**

1. a connector run is being retried

**Original actions**

1. the Integration Developer rotates the secret

**Exact source oracles — all required**

1. the previous credential remains valid only for the bounded overlap
2. one intended row effect is recorded
3. the expired secret fails on its next request

Legacy same-requirement reuse candidates: `TC-IAM-012-01`, `TC-IAM-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-012-003 — Flag on owner departure

Source persona: Integration Developer. Proposed fixture `FIX-FR-IAM-012-003` is not created. Verification duty `TASK-FR-IAM-012-03` (qualification); source `docs/backlog/backlog.csv` record 241, exact block `a7597c5c564bb40f6914408288270b6c2762a3ff60b3016c9a504834e4857206`.

**Original preconditions**

1. the owner of a service identity departs

**Original actions**

1. the departure is recorded

**Exact source oracles — all required**

1. the credential is flagged for reassignment or suspension

Legacy same-requirement reuse candidates: `TC-IAM-012-01`, `TC-IAM-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-012-004 — Reject human use and scope broadening

Source persona: Integration Developer. Proposed fixture `FIX-FR-IAM-012-004` is not created. Verification duty `TASK-FR-IAM-012-03` (qualification); source `docs/backlog/backlog.csv` record 241, exact block `e4eecb849a2103fdb096e15dfc6f32f764fc6e3660aa1475b84dfccda6ea52f4`.

**Original preconditions**

1. a service identity

**Original actions**

1. it is used for an ordinary login or a human approval, or to act beyond the scope of the owning integration

**Exact source oracles — all required**

1. the request is refused

Legacy same-requirement reuse candidates: `TC-IAM-012-01`, `TC-IAM-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
