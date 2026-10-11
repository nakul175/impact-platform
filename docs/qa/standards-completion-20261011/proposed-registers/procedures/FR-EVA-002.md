## QA v1.3 — source-bound case design (proposed)

Story `FR-EVA-002` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-EVA-002-001` / `TC-IMPRANA-FR-EVA-002-001` | `REV_ed603dd636613fbad0e1e498b9594f206439f605511b93abcafc20b5a2bd9a1f` / `REV_ab8b5e18842317ad02424df7f1de07041530fe5df97ba9dcfef7ccce61d1d01a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVA-002-002` / `TC-IMPRANA-FR-EVA-002-002` | `REV_bb6bff1e8448c24e880a518bddc7db8deca943fb23728ccc6bf75aa056d0f304` / `REV_3a414987ae2e144f5ae1527aec3d048beca00a9d273ab5f6b6e82404434adb50` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVA-002-003` / `TC-IMPRANA-FR-EVA-002-003` | `REV_2a9ccfb79fb2a80843779a96799fa9265b389a9df02a8997738ca5836f782337` / `REV_d16b777533bbec4c9c9dbe99e63e92f60504ada7c65c14bb2356cdbf3e353bdc` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVA-002-004` / `TC-IMPRANA-FR-EVA-002-004` | `REV_6b401869a662332b1247adf54a3ff575aaea765c6c79f80ed685ae98c7010fbb` / `REV_f019a7083e7e1eb8989f9a859931f200449a4d2771205d3f16ee20b7418bcaf8` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-EVA-002-001 — Export a stratified sample with methodology metadata

Source persona: Analyst. Proposed fixture `FIX-FR-EVA-002-001` is not created. Verification duty `TASK-FR-EVA-002-03` (qualification); source `docs/backlog/backlog.csv` record 332, exact block `ed603dd636613fbad0e1e498b9594f206439f605511b93abcafc20b5a2bd9a1f`.

**Original preconditions**

1. a stratified sample with weights and nonresponse metadata

**Original actions**

1. an Analyst exports it

**Exact source oracles — all required**

1. the declared eligible denominator can be reproduced

Legacy same-requirement reuse candidates: `TC-EVA-002-01`, `TC-EVA-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVA-002-002 — Amendments are reviewed and dated relative to data inspection

Source persona: Analyst. Proposed fixture `FIX-FR-EVA-002-002` is not created. Verification duty `TASK-FR-EVA-002-03` (qualification); source `docs/backlog/backlog.csv` record 332, exact block `bb6bff1e8448c24e880a518bddc7db8deca943fb23728ccc6bf75aa056d0f304`.

**Original preconditions**

1. a methodology record

**Original actions**

1. it is amended

**Exact source oracles — all required**

1. the amendment identifies when it occurred relative to data inspection
2. it requires review

Legacy same-requirement reuse candidates: `TC-EVA-002-01`, `TC-EVA-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVA-002-003 — Reject relabelling a sample count as a population

Source persona: Analyst. Proposed fixture `FIX-FR-EVA-002-003` is not created. Verification duty `TASK-FR-EVA-002-03` (qualification); source `docs/backlog/backlog.csv` record 332, exact block `2a9ccfb79fb2a80843779a96799fa9265b389a9df02a8997738ca5836f782337`.

**Original preconditions**

1. a sample count

**Original actions**

1. a population estimate is requested without an explicit valid expansion method

**Exact source oracles — all required**

1. the population estimate is refused
2. the sample count cannot be relabelled as all beneficiaries

Legacy same-requirement reuse candidates: `TC-EVA-002-01`, `TC-EVA-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVA-002-004 — Reject weighted output with missing weights

Source persona: Analyst. Proposed fixture `FIX-FR-EVA-002-004` is not created. Verification duty `TASK-FR-EVA-002-03` (qualification); source `docs/backlog/backlog.csv` record 332, exact block `6b401869a662332b1247adf54a3ff575aaea765c6c79f80ed685ae98c7010fbb`.

**Original preconditions**

1. a sample with missing weights

**Original actions**

1. weighted output is requested

**Exact source oracles — all required**

1. the weighted output is blocked
2. the weights are not silently defaulted to one

Legacy same-requirement reuse candidates: `TC-EVA-002-01`, `TC-EVA-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
