## QA v1.3 — source-bound case design (proposed)

Story `VF-SUP-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-SUP-001-001` / `TC-IMPRANA-VF-SUP-001-001` | `REV_d2d4fbf6c67aa0a5fd0bcdb2b04f941bfcdc1ab236de609fa431877b9fe8dd1c` / `REV_bcbacb410363f9f5a15fa32a7e99a9f9fe0b0acc128247a266cdaddaf2b3540e` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-VF-SUP-001-002` / `TC-IMPRANA-VF-SUP-001-002` | `REV_d48a0ab92995f98703b2f182f40229caa7af95869df55df19267cd91cef5c732` / `REV_7bd8d874ee264c46d202546668e6f177c0a4d0f26709156f119b8c9006da28c2` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-VF-SUP-001-003` / `TC-IMPRANA-VF-SUP-001-003` | `REV_960c8010939aa0bd958dac74d84310e6dc3346dd648af57530474ad8bdb127d7` / `REV_985bad9c5ed17f06aa62471d3a4a2ba70ef1c5c6677395eeef1182bce74dab8b` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-VF-SUP-001-004` / `TC-IMPRANA-VF-SUP-001-004` | `REV_fe1a7c269ec1bbc71f5203c2b782d1596b33a73d725d420b8d1c0fc30af0de92` / `REV_58389e6bb0361089e68be5375e9d794c9cfd89c162d30fada4ec82a5f8ac7980` | manual → MANUAL recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-SUP-001-001 — Support terms are published for each service plan

Source persona: Executive Director. Proposed fixture `FIX-VF-SUP-001-001` is not created. Verification duty `TASK-VF-SUP-001-03` (qualification); source `docs/backlog/backlog.csv` record 120, exact block `d2d4fbf6c67aa0a5fd0bcdb2b04f941bfcdc1ab236de609fa431877b9fe8dd1c`.

**Original preconditions**

1. each service plan

**Original actions**

1. an Executive Director views its support terms

**Exact source oracles — all required**

1. normal support hours, response targets and escalation channels are published

Legacy same-requirement reuse candidates: `TC-VF-SUP-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-SUP-001-002 — Critical incidents have continuous on-call coverage

Source persona: Executive Director. Proposed fixture `FIX-VF-SUP-001-002` is not created. Verification duty `TASK-VF-SUP-001-03` (qualification); source `docs/backlog/backlog.csv` record 120, exact block `d48a0ab92995f98703b2f182f40229caa7af95869df55df19267cd91cef5c732`.

**Original preconditions**

1. a critical incident readiness exercise

**Original actions**

1. it is run

**Exact source oracles — all required**

1. continuous on-call ownership responds
2. the runbook and escalation route are verified

Legacy same-requirement reuse candidates: `TC-VF-SUP-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-SUP-001-003 — Every critical capability has an owner, runbook and tested recovery

Source persona: Executive Director. Proposed fixture `FIX-VF-SUP-001-003` is not created. Verification duty `TASK-VF-SUP-001-03` (qualification); source `docs/backlog/backlog.csv` record 120, exact block `960c8010939aa0bd958dac74d84310e6dc3346dd648af57530474ad8bdb127d7`.

**Original preconditions**

1. readiness exercises for critical incident, identity recovery, failed import, privacy deletion and report correction

**Original actions**

1. they are completed

**Exact source oracles — all required**

1. each critical capability has an accountable operational owner, a runbook and a rehearsed recovery path

Legacy same-requirement reuse candidates: `TC-VF-SUP-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-SUP-001-004 — Reject production exposure without readiness

Source persona: Executive Director. Proposed fixture `FIX-VF-SUP-001-004` is not created. Verification duty `TASK-VF-SUP-001-03` (qualification); source `docs/backlog/backlog.csv` record 120, exact block `fe1a7c269ec1bbc71f5203c2b782d1596b33a73d725d420b8d1c0fc30af0de92`.

**Original preconditions**

1. a critical capability without an accountable operational owner or a rehearsed recovery path

**Original actions**

1. it is proposed for production exposure

**Exact source oracles — all required**

1. the exposure is blocked

Legacy same-requirement reuse candidates: `TC-VF-SUP-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
