## QA v1.3 — source-bound case design (proposed)

Story `FR-ACC-011` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ACC-011-001` / `TC-IMPRANA-FR-ACC-011-001` | `REV_e776fd3943ebbd56da7efbb398a4a7919f7b53db88a11f2479d1d7bd4e82d846` / `REV_ec803f3a8c9ae0678c4cb8c3b482182e23d9cd10ab73bdec80a04ccaccb60550` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-011-002` / `TC-IMPRANA-FR-ACC-011-002` | `REV_34f44a53fc0f8797838f965a30ed6d6540a9394eddff7c8613cbb6ba5671bac0` / `REV_532d119ff0ec15d89213f29ac7bd1e2c9f4176703856c50bb46941c626ac48cb` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-011-003` / `TC-IMPRANA-FR-ACC-011-003` | `REV_e65a4cdf1f68aaa10bdbd5b4fc4e6dea131a5cec3f2b6129d8cbb2a9e0db7ce4` / `REV_f232537a311a7462fb8049b4219398c3ec375de6f80575f69f44427e43adc7a5` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-011-004` / `TC-IMPRANA-FR-ACC-011-004` | `REV_a9f9bbfeb7f3721981d591b65043c87d26da98899b07676a6286db1621c27d24` / `REV_24c40e154bc260dcae5913d810f331876ca00b5ddc45c6f53ac7b6bc22bb53ed` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ACC-011-001 — Propagate a grant change

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-011-001` is not created. Verification duty `TASK-FR-ACC-011-03` (qualification); source `docs/backlog/backlog.csv` record 25, exact block `e776fd3943ebbd56da7efbb398a4a7919f7b53db88a11f2479d1d7bd4e82d846`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the Organisation Administrator changes a grant

**Exact source oracles — all required**

1. a revocation event covers active sessions, cached reads, queued jobs, generated artifacts and AI dependencies
2. new sensitive actions evaluate current policy immediately
3. online presentation converges within 60 seconds

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-011-01`, `TC-ACC-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-011-002 — Report previously downloaded copies

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-011-002` is not created. Verification duty `TASK-FR-ACC-011-03` (qualification); source `docs/backlog/backlog.csv` record 25, exact block `34f44a53fc0f8797838f965a30ed6d6540a9394eddff7c8613cbb6ba5671bac0`.

**Original preconditions**

1. copies were downloaded before the grant change

**Original actions**

1. the revocation is processed

**Exact source oracles — all required**

1. those copies are reported as external disclosures rather than remotely erased

Legacy same-requirement reuse candidates: `TC-ACC-011-01`, `TC-ACC-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-011-003 — Reject revoked source text in saved AI answers

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-011-003` is not created. Verification duty `TASK-FR-ACC-011-03` (qualification); source `docs/backlog/backlog.csv` record 25, exact block `e65a4cdf1f68aaa10bdbd5b4fc4e6dea131a5cec3f2b6129d8cbb2a9e0db7ce4`.

**Original preconditions**

1. an AI answer citing a source has been saved

**Original actions**

1. access to that source is removed and the conversation is reopened

**Exact source oracles — all required**

1. the revoked source text is not revealed, including through its summary

Legacy same-requirement reuse candidates: `TC-ACC-011-01`, `TC-ACC-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-011-004 — Reject stale presentation beyond the bound

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-011-004` is not created. Verification duty `TASK-FR-ACC-011-03` (qualification); source `docs/backlog/backlog.csv` record 25, exact block `a9f9bbfeb7f3721981d591b65043c87d26da98899b07676a6286db1621c27d24`.

**Original preconditions**

1. a grant has been removed

**Original actions**

1. more than 60 seconds have passed

**Exact source oracles — all required**

1. no online presentation under platform control still shows the revoked content

Legacy same-requirement reuse candidates: `TC-ACC-011-01`, `TC-ACC-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
