## QA v1.3 — source-bound case design (proposed)

Story `VF-DR-002` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-DR-002-001` / `TC-IMPRANA-VF-DR-002-001` | `REV_dcb0403773e70980a66996b84023781b338cc822275141bf19ea1e333d836290` / `REV_cefbdbf359a8bb7593b55a27897348dfdba04001950f6291109b48005c406f7b` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DR-002-002` / `TC-IMPRANA-VF-DR-002-002` | `REV_1dbe4d317301d160f82489a34aaab340a756eeda2fd1464d2292f6b79bc1bd6e` / `REV_5c2d7c86239c8599b24e3b6adaaffcfe7bc7eb691b24191bad67856bc004812b` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DR-002-003` / `TC-IMPRANA-VF-DR-002-003` | `REV_d49bd6c680aa6dfb34f722d1c2aa81f1e4136107f0a5266db6ec37c39dde07bf` / `REV_614a5ca5757c61e6a9f82483513264148c7e5a13ac246073414fbbb3f3f4546d` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-DR-002-001 — Server acknowledgement survives an ordinary single component failure

Source persona: Data Author. Proposed fixture `FIX-VF-DR-002-001` is not created. Verification duty `TASK-VF-DR-002-03` (qualification); source `docs/backlog/backlog.csv` record 118, exact block `dcb0403773e70980a66996b84023781b338cc822275141bf19ea1e333d836290`.

**Original preconditions**

1. a Data Author saves a record and receives a server receipt

**Original actions**

1. a qualified individual component is interrupted during or around the write

**Exact source oracles — all required**

1. the recovered record, its child relationships and files match the receipt

Legacy same-requirement reuse candidates: `TC-VF-DR-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DR-002-002 — Offline local saves are clearly distinct

Source persona: Data Author. Proposed fixture `FIX-VF-DR-002-002` is not created. Verification duty `TASK-VF-DR-002-03` (qualification); source `docs/backlog/backlog.csv` record 118, exact block `1dbe4d317301d160f82489a34aaab340a756eeda2fd1464d2292f6b79bc1bd6e`.

**Original preconditions**

1. a Data Author saves a record while offline

**Original actions**

1. the save completes locally

**Exact source oracles — all required**

1. it is clearly shown as a local save, distinct from a server acknowledgement

Legacy same-requirement reuse candidates: `TC-VF-DR-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DR-002-003 — Reject silent loss of an acknowledged save

Source persona: Data Author. Proposed fixture `FIX-VF-DR-002-003` is not created. Verification duty `TASK-VF-DR-002-03` (qualification); source `docs/backlog/backlog.csv` record 118, exact block `d49bd6c680aa6dfb34f722d1c2aa81f1e4136107f0a5266db6ec37c39dde07bf`.

**Original preconditions**

1. a successful server receipt for a saved record

**Original actions**

1. an ordinary qualified single component failure occurs

**Exact source oracles — all required**

1. the record does not silently disappear
2. any uncertain client outcome is reconciled by operation identity

Legacy same-requirement reuse candidates: `TC-VF-DR-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
