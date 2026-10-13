## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-002` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-002-001` / `TC-IMPRANA-FR-IAM-002-001` | `REV_43ad1fc1f5c6f7272d5f35c4a391213426be6f59b3baa2dfd84aac37fb320df0` / `REV_98e257538f8233fa1e9e6c1156a566cfc4edf9774646a0b534ebbd36f41e0676` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-002-002` / `TC-IMPRANA-FR-IAM-002-002` | `REV_c11ee4c16788daccf5c0ca8771b6c1aa5a197619f3f58ccdf4fb78af3ffca339` / `REV_6a1d178ad63fd6ac52b1a18941387aa53bbc6b0bed780f9f891aa8dd00155677` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-002-003` / `TC-IMPRANA-FR-IAM-002-003` | `REV_9e03e9e387ec437978f67df22a3331ec98dd8ddb65fbb1c0c033f6a947613beb` / `REV_4f93ed9d0be65a33bed7e44e9b897218ae2e438e26f036fcaa115e5dc0d1e312` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-002-004` / `TC-IMPRANA-FR-IAM-002-004` | `REV_3398e6a22525a1e51c9904913fe22205304040474b0d9a47b09170bbebf7d7d8` / `REV_bd33c89e00ebabb72a75db8a6d139ecfb11585aa3f195b78787b31cbd959e318` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-002-001 — Configure and test federation before enforcing it

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-002-001` is not created. Verification duty `TASK-FR-IAM-002-03` (qualification); source `docs/backlog/backlog.csv` record 84, exact block `43ad1fc1f5c6f7272d5f35c4a391213426be6f59b3baa2dfd84aac37fb320df0`.

**Original preconditions**

1. an Organisation Administrator configures provider metadata, tenant binding and subject mapping

**Original actions**

1. they test sign in with designated accounts

**Exact source oracles — all required**

1. federation can be enforced
2. login binds the issuer and stable subject to the intended tenant membership

Legacy same-requirement reuse candidates: `TC-IAM-002-01`, `TC-IAM-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-002-002 — Rotate the provider certificate

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-002-002` is not created. Verification duty `TASK-FR-IAM-002-03` (qualification); source `docs/backlog/backlog.csv` record 84, exact block `c11ee4c16788daccf5c0ca8771b6c1aa5a197619f3f58ccdf4fb78af3ffca339`.

**Original preconditions**

1. federation is enforced and the certificate expiry is shown

**Original actions**

1. the Organisation Administrator performs a tested overlapping certificate rotation

**Exact source oracles — all required**

1. sign in continues under the new certificate

Legacy same-requirement reuse candidates: `TC-IAM-002-01`, `TC-IAM-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-002-003 — Reject email-only linking and invalid assertions

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-002-003` is not created. Verification duty `TASK-FR-IAM-002-03` (qualification); source `docs/backlog/backlog.csv` record 84, exact block `9e03e9e387ec437978f67df22a3331ec98dd8ddb65fbb1c0c033f6a947613beb`.

**Original preconditions**

1. two different federation identities share a matching email

**Original actions**

1. either signs in

**Exact source oracles — all required**

1. the matching email alone never joins the identities
2. an invalid assertion, wrong audience or missing assurance fails safely

Legacy same-requirement reuse candidates: `TC-IAM-002-01`, `TC-IAM-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-002-004 — Reject local password bypass

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-002-004` is not created. Verification duty `TASK-FR-IAM-002-03` (qualification); source `docs/backlog/backlog.csv` record 84, exact block `3398e6a22525a1e51c9904913fe22205304040474b0d9a47b09170bbebf7d7d8`.

**Original preconditions**

1. federation is enforced, the old certificate has expired and the provider is interrupted

**Original actions**

1. a member attempts to sign in with an ordinary local password

**Exact source oracles — all required**

1. the sign in is refused
2. only separately enrolled, restricted and audited emergency local recovery remains available

Legacy same-requirement reuse candidates: `TC-IAM-002-01`, `TC-IAM-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
