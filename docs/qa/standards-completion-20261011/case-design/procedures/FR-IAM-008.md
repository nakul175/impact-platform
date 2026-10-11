## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-008` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-008-001` / `TC-IMPRANA-FR-IAM-008-001` | `REV_0bb9c4b60042ec67be5dab605e5504ae5aac445e00c461377808d8a7d766fd58` / `REV_a3c57aa050f80db899909d1724d7cf7c448486a3d41e34614dcb4b181cbbccd4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-008-002` / `TC-IMPRANA-FR-IAM-008-002` | `REV_fc40780a6e9037869e8fabe14b92b8fe93cddb361b124e26eb6b221f64f1c0f3` / `REV_f96735583cb9a134b840a2a7b4b197843a8dbaed53836f22b2f7edeac6cf56fa` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-008-003` / `TC-IMPRANA-FR-IAM-008-003` | `REV_cb8f16017512349e0dd9e4b373c72f2a2c18aa294ee379fcd1596f813c4f2238` / `REV_a865da7cb3d013c42f561cba1e459ade5231410909971942eb91ad62926fac18` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-008-004` / `TC-IMPRANA-FR-IAM-008-004` | `REV_676d4de3bdc2cb343f60c5d9bf1898691bef17604d92e9ba5b1851b7e79ba30d` / `REV_4204161735f38816b749c37d08553ebd657a112b67229b4823c7ccc4b08add20` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-008-001 — Show upcoming expiry

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-008-001` is not created. Verification duty `TASK-FR-IAM-008-03` (qualification); source `docs/backlog/backlog.csv` record 87, exact block `0bb9c4b60042ec67be5dab605e5504ae5aac445e00c461377808d8a7d766fd58`.

**Original preconditions**

1. a membership with a scheduled expiry at an absolute instant

**Original actions**

1. the member or owner views the membership

**Exact source oracles — all required**

1. they see the upcoming expiry

Legacy same-requirement reuse candidates: `TC-IAM-008-01`, `TC-IAM-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-008-002 — Expire a membership in one tenant only

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-008-002` is not created. Verification duty `TASK-FR-IAM-008-03` (qualification); source `docs/backlog/backlog.csv` record 87, exact block `fc40780a6e9037869e8fabe14b92b8fe93cddb361b124e26eb6b221f64f1c0f3`.

**Original preconditions**

1. a Reviewer has memberships in tenants A and B

**Original actions**

1. their tenant A membership expires

**Exact source oracles — all required**

1. their approvals in tenant A fail
2. their authorised work in tenant B continues
3. their account is not deleted

Legacy same-requirement reuse candidates: `TC-IAM-008-01`, `TC-IAM-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-008-003 — Suspend a membership

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-008-003` is not created. Verification duty `TASK-FR-IAM-008-03` (qualification); source `docs/backlog/backlog.csv` record 87, exact block `cb8f16017512349e0dd9e4b373c72f2a2c18aa294ee379fcd1596f813c4f2238`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the Organisation Administrator suspends a membership

**Exact source oracles — all required**

1. online revocation starts immediately
2. pending work is identified
3. historical attribution is unchanged

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-008-01`, `TC-IAM-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-008-004 — Reject reactivation without review or revival of revoked items

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-008-004` is not created. Verification duty `TASK-FR-IAM-008-03` (qualification); source `docs/backlog/backlog.csv` record 87, exact block `676d4de3bdc2cb343f60c5d9bf1898691bef17604d92e9ba5b1851b7e79ba30d`.

**Original preconditions**

1. a suspended or expired membership

**Original actions**

1. the Organisation Administrator reactivates it

**Exact source oracles — all required**

1. a current grant review and a new expiry where relevant are required
2. revoked links, old service secrets and independently expired delegations are not revived

Legacy same-requirement reuse candidates: `TC-IAM-008-01`, `TC-IAM-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
