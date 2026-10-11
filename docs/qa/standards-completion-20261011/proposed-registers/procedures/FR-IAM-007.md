## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-007-001` / `TC-IMPRANA-FR-IAM-007-001` | `REV_2ad9e264ede714781d37cde4ca8218cb28ae1ce4bda61bf607d50053e23bab93` / `REV_60b3238a43863b2a2766a6d250d41f25a10734a4fa3f297105353cc987c8cb92` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-007-002` / `TC-IMPRANA-FR-IAM-007-002` | `REV_c44bf358bd941781ba2b61c06598535241a26d4dff8220d7050c1ffa56ab2679` / `REV_e5c8816b8d0f35c4e5f874394d7a2ffd1f817c3b255e0d2fa97ec04ef91a69ff` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-007-003` / `TC-IMPRANA-FR-IAM-007-003` | `REV_279c00774d5a1e85651d91068786cf3677b53bab49ce578aa200001d79257bfd` / `REV_489eb607c8bce7bbbaf68fca2259750af280c9ba43b6ac9c70c4d2ac927b5e57` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-007-004` / `TC-IMPRANA-FR-IAM-007-004` | `REV_3fedcb18c6dce7eded113e06ec5cb95238f85064709c124a53afa3c89076b8c7` / `REV_b2bf6b19527e7b2475f23a8afbc8f630fbf55f419bc1000a253186d830e929ac` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-007-001 — Change identity after step up

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-007-001` is not created. Verification duty `TASK-FR-IAM-007-03` (qualification); source `docs/backlog/backlog.csv` record 239, exact block `2ad9e264ede714781d37cde4ca8218cb28ae1ce4bda61bf607d50053e23bab93`.

**Original preconditions**

1. a Data Author has completed a recent step up

**Original actions**

1. they change their identity contact and verify the new channel

**Exact source oracles — all required**

1. the change is applied
2. both permitted old and new contacts are notified without disclosing secrets

Legacy same-requirement reuse candidates: `TC-IAM-007-01`, `TC-IAM-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-007-002 — Recover a lost factor

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-007-002` is not created. Verification duty `TASK-FR-IAM-007-03` (qualification); source `docs/backlog/backlog.csv` record 239, exact block `c44bf358bd941781ba2b61c06598535241a26d4dff8220d7050c1ffa56ab2679`.

**Original preconditions**

1. a Data Author has lost a factor

**Original actions**

1. they verify enrolled recovery evidence

**Exact source oracles — all required**

1. one recovery code is consumed
2. a security notice is triggered

Legacy same-requirement reuse candidates: `TC-IAM-007-01`, `TC-IAM-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-007-003 — Reject identity change from a stolen session

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-007-003` is not created. Verification duty `TASK-FR-IAM-007-03` (qualification); source `docs/backlog/backlog.csv` record 239, exact block `279c00774d5a1e85651d91068786cf3677b53bab49ce578aa200001d79257bfd`.

**Original preconditions**

1. an attacker holds a stolen ordinary session

**Original actions**

1. they attempt to replace the recovery email

**Exact source oracles — all required**

1. the change is blocked until stronger verification succeeds

Legacy same-requirement reuse candidates: `TC-IAM-007-01`, `TC-IAM-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-007-004 — Reject support resets based on conversation alone

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-007-004` is not created. Verification duty `TASK-FR-IAM-007-03` (qualification); source `docs/backlog/backlog.csv` record 239, exact block `3fedcb18c6dce7eded113e06ec5cb95238f85064709c124a53afa3c89076b8c7`.

**Original preconditions**

1. a Support Agent receives an identity reset request

**Original actions**

1. the only evidence is a conversation or knowledge questions

**Exact source oracles — all required**

1. the Support Agent cannot reset the identity
2. a disputed change enters a restricted recovery case where existing broad privileges are not restored until verification completes

Legacy same-requirement reuse candidates: `TC-IAM-007-01`, `TC-IAM-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
