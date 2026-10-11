## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-009` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-009-001` / `TC-IMPRANA-FR-IAM-009-001` | `REV_b3f2c006bd703c044cebca0da8792c8319d376e5d0a3dd407845749c0d82a91f` / `REV_b1be1023f6563407a25e0b2b39d5ae005022b32c47cfb45a6f49753cf8808a21` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-009-002` / `TC-IMPRANA-FR-IAM-009-002` | `REV_0137143c38f602a970a6b2b3157212ae965a187c25f5ac89811cd05b50db271f` / `REV_52e9dd2d5a1fa0bc0c14fc9f0e09009b912ab2c39cf2e1609529f6c71f3ba6e4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-009-003` / `TC-IMPRANA-FR-IAM-009-003` | `REV_2f425eda2a878dacf6fc1a3a659cd77df0b7c640ebcc132e557a0800ae8fdfc4` / `REV_e4d367c336050e95964220430c2274535e47d42315349539a06d215b73b310c5` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-009-004` / `TC-IMPRANA-FR-IAM-009-004` | `REV_9911ca60e0672a15b75e15fbca81cb586079a8a82039a55876ddbc2ee464d6d8` / `REV_6ecc79088ee0872c5b1f57f6e7ab8ca7a572fe320bd50ba3671938ad74882566` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-009-001 — Invite or modify members within the delegation envelope

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-009-001` is not created. Verification duty `TASK-FR-IAM-009-03` (qualification); source `docs/backlog/backlog.csv` record 88, exact block `b3f2c006bd703c044cebca0da8792c8319d376e5d0a3dd407845749c0d82a91f`.

**Original preconditions**

1. a delegated administrator with a delegation envelope

**Original actions**

1. they invite or modify a member within that envelope

**Exact source oracles — all required**

1. the grant preview shows the effective capability difference
2. any sensitive expansion is flagged for independent approval

Legacy same-requirement reuse candidates: `TC-IAM-009-01`, `TC-IAM-009-02`, `IT-010`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-009-002 — Recheck authority at approval

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-009-002` is not created. Verification duty `TASK-FR-IAM-009-03` (qualification); source `docs/backlog/backlog.csv` record 88, exact block `0137143c38f602a970a6b2b3157212ae965a187c25f5ac89811cd05b50db271f`.

**Original preconditions**

1. a flagged grant awaiting independent approval

**Original actions**

1. it is approved

**Exact source oracles — all required**

1. the issuer's current delegation authority is rechecked before the grant applies

Legacy same-requirement reuse candidates: `TC-IAM-009-01`, `TC-IAM-009-02`, `IT-010`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-009-003 — Reject indirect escalation through a group

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-009-003` is not created. Verification duty `TASK-FR-IAM-009-03` (qualification); source `docs/backlog/backlog.csv` record 88, exact block `2f425eda2a878dacf6fc1a3a659cd77df0b7c640ebcc132e557a0800ae8fdfc4`.

**Original preconditions**

1. a project administrator

**Original actions**

1. they create a group and attempt to add tenant administration through it

**Exact source oracles — all required**

1. the indirect escalation fails

Legacy same-requirement reuse candidates: `TC-IAM-009-01`, `TC-IAM-009-02`, `IT-010`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-009-004 — Reject delegating non-delegable rights and self elevation

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-009-004` is not created. Verification duty `TASK-FR-IAM-009-03` (qualification); source `docs/backlog/backlog.csv` record 88, exact block `9911ca60e0672a15b75e15fbca81cb586079a8a82039a55876ddbc2ee464d6d8`.

**Original preconditions**

1. an administrator holds a right that is not delegable

**Original actions**

1. they attempt to delegate it, elevate themselves, grant a role through a new group or expand scope through an import

**Exact source oracles — all required**

1. identical checks apply and the action is refused

Legacy same-requirement reuse candidates: `TC-IAM-009-01`, `TC-IAM-009-02`, `IT-010`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
