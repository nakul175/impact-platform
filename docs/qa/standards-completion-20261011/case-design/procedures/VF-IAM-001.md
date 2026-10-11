## QA v1.3 — source-bound case design (proposed)

Story `VF-IAM-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-IAM-001-001` / `TC-IMPRANA-VF-IAM-001-001` | `REV_0ba9994e45ddfb289c3e382d4744adcb951e9229f8c68a2996a4bf91e1f30dcc` / `REV_ecc5bf9e64ceb7197b361b417213965cff38eaed9e83f1286477186c2bbfe654` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-IAM-001-002` / `TC-IMPRANA-VF-IAM-001-002` | `REV_66cfa165352ea566f547f73ec867631a90249b93ce62b2da65e999c3278bc688` / `REV_358f0f4cbff6c0685167427c6615de23d7ff542d3fd1234f2c2e390d58a9e26c` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-IAM-001-003` / `TC-IMPRANA-VF-IAM-001-003` | `REV_269af256504b95c48dbcabfdcdb08ee0624143845c0d60885ef6907a291226a3` / `REV_1f3bf69bb0654395d483ad0ca610e9abfcb5e3fd9cc67ebcd944de721de87d6a` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-IAM-001-004` / `TC-IMPRANA-VF-IAM-001-004` | `REV_69f4c6038a049b2b279248c3f1490c5aedee1308072c212585065649e6e1c4cb` / `REV_5b2a11b79ec5c853f6200daf51dc948c3dc50ad3a67345d864c350392ee54e92` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-IAM-001-001 — Revocation takes effect within 60 seconds across all channels

Source persona: Organisation Administrator. Proposed fixture `FIX-VF-IAM-001-001` is not created. Verification duty `TASK-VF-IAM-001-03` (qualification); source `docs/backlog/backlog.csv` record 90, exact block `0ba9994e45ddfb289c3e382d4744adcb951e9229f8c68a2996a4bf91e1f30dcc`.

**Original preconditions**

1. an online user, grant or service credential

**Original actions**

1. the Organisation Administrator suspends the user, removes the permission or revokes the credential

**Exact source oracles — all required**

1. access is blocked within 60 seconds across user interfaces, APIs, generated downloads, search and AI access

Legacy same-requirement reuse candidates: `TC-VF-IAM-001`, `TC-AT13`, `IT-005`, `SEC-002`, `SEC-016`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-IAM-001-002 — Directory-initiated revocation is measured from platform receipt

Source persona: Organisation Administrator. Proposed fixture `FIX-VF-IAM-001-002` is not created. Verification duty `TASK-VF-IAM-001-03` (qualification); source `docs/backlog/backlog.csv` record 90, exact block `66cfa165352ea566f547f73ec867631a90249b93ce62b2da65e999c3278bc688`.

**Original preconditions**

1. a revocation initiated from a directory

**Original actions**

1. the platform receives it

**Exact source oracles — all required**

1. the 60-second bound is measured from that receipt

Legacy same-requirement reuse candidates: `TC-VF-IAM-001`, `TC-AT13`, `IT-005`, `SEC-002`, `SEC-016`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-IAM-001-003 — Queued jobs reauthorise before sensitive actions

Source persona: Organisation Administrator. Proposed fixture `FIX-VF-IAM-001-003` is not created. Verification duty `TASK-VF-IAM-001-03` (qualification); source `docs/backlog/backlog.csv` record 90, exact block `269af256504b95c48dbcabfdcdb08ee0624143845c0d60885ef6907a291226a3`.

**Original preconditions**

1. a queued job pending a sensitive action for a revoked user or credential

**Original actions**

1. the job is about to execute

**Exact source oracles — all required**

1. it reauthorises and does not perform the action

Legacy same-requirement reuse candidates: `TC-VF-IAM-001`, `TC-AT13`, `IT-005`, `SEC-002`, `SEC-016`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-IAM-001-004 — Reject any protected access after 60 seconds

Source persona: Organisation Administrator. Proposed fixture `FIX-VF-IAM-001-004` is not created. Verification duty `TASK-VF-IAM-001-03` (qualification); source `docs/backlog/backlog.csv` record 90, exact block `69f4c6038a049b2b279248c3f1490c5aedee1308072c212585065649e6e1c4cb`.

**Original preconditions**

1. a revocation was received by the platform more than 60 seconds ago

**Original actions**

1. the revoked user or credential attempts protected access through any channel

**Exact source oracles — all required**

1. the access is refused
2. any successful protected access fails the gate, because 60 seconds is a maximum, not a percentile

Legacy same-requirement reuse candidates: `TC-VF-IAM-001`, `TC-AT13`, `IT-005`, `SEC-002`, `SEC-016`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
