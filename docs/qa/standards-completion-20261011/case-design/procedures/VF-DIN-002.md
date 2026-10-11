## QA v1.3 — source-bound case design (proposed)

Story `VF-DIN-002` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-DIN-002-001` / `TC-IMPRANA-VF-DIN-002-001` | `REV_4c98c0fba89fb811b1bdd57cbcd74bcb3dd4707bf1dc223f8909de6f1d5eb725` / `REV_576226fe2d34caf0d2d53327605abc646b2d6e0c9610119a75c591143140346d` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DIN-002-002` / `TC-IMPRANA-VF-DIN-002-002` | `REV_64801fcd450525b199299b5297a5059820c04ef425e6d614427fd4fb5ab7deb2` / `REV_ee5f6316f4b5c9b07459e2e66fcc660f992b33c82d1954da61ba6349e7513027` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DIN-002-003` / `TC-IMPRANA-VF-DIN-002-003` | `REV_61a2327ce25fb26a748dc35f0babeec58021fb9c2146985989b8bedd0f6d0cca` / `REV_f51dffb43324158a3aa2bd3dbe9b9de12d675956f9886f61e602445f87f1223c` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DIN-002-004` / `TC-IMPRANA-VF-DIN-002-004` | `REV_4e27988569f830b93c01dc576762bc070a941d60673bcd70b8893809220efdc6` / `REV_9d3e38497a784b57c9161fe8cdc0afdfa7e42daa71cbfbecbbad13dfc329900d` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-DIN-002-001 — Concurrent edits do not silently overwrite each other

Source persona: Data Author. Proposed fixture `FIX-VF-DIN-002-001` is not created. Verification duty `TASK-VF-DIN-002-03` (qualification); source `docs/backlog/backlog.csv` record 112, exact block `4c98c0fba89fb811b1bdd57cbcd74bcb3dd4707bf1dc223f8909de6f1d5eb725`.

**Original preconditions**

1. two Data Authors edit the same record at the same time

**Original actions**

1. both save

**Exact source oracles — all required**

1. one save completes with recorded effects
2. the stale save is rejected explicitly rather than silently overwriting the other

Legacy same-requirement reuse candidates: `TC-VF-DIN-002`, `IT-017`, `SEC-018`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_concurrency.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DIN-002-002 — Repeated commands and interrupted jobs do not duplicate results

Source persona: Data Author. Proposed fixture `FIX-VF-DIN-002-002` is not created. Verification duty `TASK-VF-DIN-002-03` (qualification); source `docs/backlog/backlog.csv` record 112, exact block `64801fcd450525b199299b5297a5059820c04ef425e6d614427fd4fb5ab7deb2`.

**Original preconditions**

1. an import command is repeated or a bulk job is interrupted

**Original actions**

1. processing finishes

**Exact source oracles — all required**

1. no achievement is duplicated
2. the operation either completes with recorded effects or returns an explicit recoverable partial outcome with complete per-item receipts

Legacy same-requirement reuse candidates: `TC-VF-DIN-002`, `IT-017`, `SEC-018`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_concurrency.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DIN-002-003 — Approvals apply only to the reviewed version

Source persona: Data Author. Proposed fixture `FIX-VF-DIN-002-003` is not created. Verification duty `TASK-VF-DIN-002-03` (qualification); source `docs/backlog/backlog.csv` record 112, exact block `61a2327ce25fb26a748dc35f0babeec58021fb9c2146985989b8bedd0f6d0cca`.

**Original preconditions**

1. a Reviewer approved an earlier version of a record
2. a new candidate version has since been submitted

**Original actions**

1. approval is applied

**Exact source oracles — all required**

1. the earlier decision is not used to approve the new candidate

Legacy same-requirement reuse candidates: `TC-VF-DIN-002`, `IT-017`, `SEC-018`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_concurrency.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DIN-002-004 — Reject silent overwrite, duplicate result or stale approval

Source persona: Data Author. Proposed fixture `FIX-VF-DIN-002-004` is not created. Verification duty `TASK-VF-DIN-002-03` (qualification); source `docs/backlog/backlog.csv` record 112, exact block `4e27988569f830b93c01dc576762bc070a941d60673bcd70b8893809220efdc6`.

**Original preconditions**

1. racing edits, racing approvals, repeated imports and interrupted bulk jobs

**Original actions**

1. outcomes are verified

**Exact source oracles — all required**

1. any silent last-write overwrite fails
2. any duplicate intended result fails
3. any approval of a new candidate using an old decision fails

Legacy same-requirement reuse candidates: `TC-VF-DIN-002`, `IT-017`, `SEC-018`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_concurrency.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
