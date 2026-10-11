## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-006` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-006-001` / `TC-IMPRANA-FR-IAM-006-001` | `REV_7a2ccff5453eb24bab7b974e21e2ca1a3cfa246ecd0e6936271e18f16f01a661` / `REV_129d589d8e3fc9ca4dcaddc7626b1c9e22b39dd2053a2cd5277ac80293f83b09` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-006-002` / `TC-IMPRANA-FR-IAM-006-002` | `REV_17c0dea2e3b37c73cf16049556093887a83d877ee8f0d17c60fa61e94c2b22f8` / `REV_18fdd58c62f35cf8b8a1154f53f7c23d38f2cb9c2294b9e3d6a747b892a0d07a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-006-003` / `TC-IMPRANA-FR-IAM-006-003` | `REV_e0f6247cc50029b1185feb8fa5b8b768c150d65a09e59717155dde5fa73c5e9c` / `REV_d1a4abeeb872a841b19c6c7d9882edf08f7c6372a97385179be45ff590b60538` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-006-004` / `TC-IMPRANA-FR-IAM-006-004` | `REV_dcd324c67ba213c3a02ea1c4bf4d888dce22b204b44181b30ad72957eaa37056` / `REV_30d2300ff48603bd58d5198bec8df8e24eeac7a6a2c28405d8a0a7041c69b392` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-006-005` / `TC-IMPRANA-FR-IAM-006-005` | `REV_8a46eed1621abc4018f00af99e791b646ac2ef20bdcc594ecfc5e0d2d5850e58` / `REV_11a4e65a54864d229f1914a806d4b641682ba86671afa51af2be8ab7c6ce951d` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-006-001 — View sessions

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-006-001` is not created. Verification duty `TASK-FR-IAM-006-03` (qualification); source `docs/backlog/backlog.csv` record 86, exact block `7a2ccff5453eb24bab7b974e21e2ca1a3cfa246ecd0e6936271e18f16f01a661`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a Data Author views their sessions

**Exact source oracles — all required**

1. each shows a device label, approximate activity, creation and last use without unnecessary location detail

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-006-01`, `TC-IAM-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-006-002 — Revoke sessions

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-006-002` is not created. Verification duty `TASK-FR-IAM-006-03` (qualification); source `docs/backlog/backlog.csv` record 86, exact block `17c0dea2e3b37c73cf16049556093887a83d877ee8f0d17c60fa61e94c2b22f8`.

**Original preconditions**

1. a Data Author has verified their identity

**Original actions**

1. they revoke one session or all sessions

**Exact source oracles — all required**

1. the revoked sessions lose server authority even if a browser retains a stale screen image

Legacy same-requirement reuse candidates: `TC-IAM-006-01`, `TC-IAM-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-006-003 — Warn before expiry

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-006-003` is not created. Verification duty `TASK-FR-IAM-006-03` (qualification); source `docs/backlog/backlog.csv` record 86, exact block `e0f6247cc50029b1185feb8fa5b8b768c150d65a09e59717155dde5fa73c5e9c`.

**Original preconditions**

1. a session approaching idle or absolute expiry as defined in FD04

**Original actions**

1. the warning is shown

**Exact source oracles — all required**

1. permitted drafts are preserved before reauthentication

Legacy same-requirement reuse candidates: `TC-IAM-006-01`, `TC-IAM-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-006-004 — Reject use of a revoked session

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-006-004` is not created. Verification duty `TASK-FR-IAM-006-03` (qualification); source `docs/backlog/backlog.csv` record 86, exact block `dcd324c67ba213c3a02ea1c4bf4d888dce22b204b44181b30ad72957eaa37056`.

**Original preconditions**

1. a Data Author has two open sessions and revokes one

**Original actions**

1. the revoked session uses browser back navigation or a queued export

**Exact source oracles — all required**

1. neither returns protected data

Legacy same-requirement reuse candidates: `TC-IAM-006-01`, `TC-IAM-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-006-005 — Reject protected state after logout or on a shared device

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-006-005` is not created. Verification duty `TASK-FR-IAM-006-03` (qualification); source `docs/backlog/backlog.csv` record 86, exact block `8a46eed1621abc4018f00af99e791b646ac2ef20bdcc594ecfc5e0d2d5850e58`.

**Original preconditions**

1. a Data Author has logged out or is using shared device mode

**Original actions**

1. the browser is used to return to protected content

**Exact source oracles — all required**

1. sensitive in memory state and protected cached navigation have been cleared
2. no persistent unrestricted session is available

Legacy same-requirement reuse candidates: `TC-IAM-006-01`, `TC-IAM-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
