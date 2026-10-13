## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-002` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-002-001` / `TC-IMPRANA-FR-SEC-002-001` | `REV_8b0005a9e1344a3db2564cf1c7d8ba63e4294ce9b98e74545cbb9db27a42ba50` / `REV_2b0bfb8aac84120af9c799e6ec58ab978f8904f209549c282e359257fbe7b74c` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-002-002` / `TC-IMPRANA-FR-SEC-002-002` | `REV_17290fbe63f1328c110b16b091a6585c460cfba5ec53a831d2fe056304f114d4` / `REV_e69532f4d049dfc116a90b27f03ebd75c8169f113fca96ebdba374f214d96de0` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-002-003` / `TC-IMPRANA-FR-SEC-002-003` | `REV_9e1a3cfc4b1585d73cd7810e8d0f373f30d9bf2d63b5255cf6b29489250d1717` / `REV_ed8758f75249204804c3c8ea5e1b07d91aa60d7da7286af5cde767ce40ddb319` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-002-004` / `TC-IMPRANA-FR-SEC-002-004` | `REV_363846906313951dbb581964f940681f2231cf026d8ac3089d8e7a71aaccbdc2` / `REV_3a3d8456422540c0d767a307542416eaaf86a0eb6a7d58704054f48c10e36ee2` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-002-001 — Inventory covers every location

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-002-001` is not created. Verification duty `TASK-FR-SEC-002-03` (qualification); source `docs/backlog/backlog.csv` record 148, exact block `8b0005a9e1344a3db2564cf1c7d8ba63e4294ce9b98e74545cbb9db27a42ba50`.

**Original preconditions**

1. the security inventory

**Original actions**

1. it is reviewed

**Exact source oracles — all required**

1. it covers every permitted data location and transport, including temporary artifacts, backups and offline packages

Legacy same-requirement reuse candidates: `TC-SEC-002-01`, `TC-SEC-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-002-002 — Key status is visible without key material

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-002-002` is not created. Verification duty `TASK-FR-SEC-002-03` (qualification); source `docs/backlog/backlog.csv` record 148, exact block `17290fbe63f1328c110b16b091a6585c460cfba5ec53a831d2fe056304f114d4`.

**Original preconditions**

1. operational interfaces for keys

**Original actions**

1. the Platform Operator views a key

**Exact source oracles — all required**

1. its ownership, status, expiry and rotation evidence are shown
2. no key material is displayed

Legacy same-requirement reuse candidates: `TC-SEC-002-01`, `TC-SEC-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-002-003 — Key rotation preserves authorised access

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-002-003` is not created. Verification duty `TASK-FR-SEC-002-03` (qualification); source `docs/backlog/backlog.csv` record 148, exact block `9e1a3cfc4b1585d73cd7810e8d0f373f30d9bf2d63b5255cf6b29489250d1717`.

**Original preconditions**

1. a test data protection key

**Original actions**

1. it is rotated

**Exact source oracles — all required**

1. approved records and backups remain accessible only through authorised paths
2. no key values are exposed

Legacy same-requirement reuse candidates: `TC-SEC-002-01`, `TC-SEC-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-002-004 — Reject plaintext fallback on key loss

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-002-004` is not created. Verification duty `TASK-FR-SEC-002-03` (qualification); source `docs/backlog/backlog.csv` record 148, exact block `363846906313951dbb581964f940681f2231cf026d8ac3089d8e7a71aaccbdc2`.

**Original preconditions**

1. a required key is lost or revoked

**Original actions**

1. data protected by it is requested

**Exact source oracles — all required**

1. a controlled unavailable state is returned
2. no plaintext fallback is used

Legacy same-requirement reuse candidates: `TC-SEC-002-01`, `TC-SEC-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
