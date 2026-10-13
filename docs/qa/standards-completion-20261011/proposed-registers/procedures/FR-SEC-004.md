## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-004-001` / `TC-IMPRANA-FR-SEC-004-001` | `REV_ae4a57b2a2c559413bfc2d7e653dedee932b5acabb5bba768f9a31063a17fa84` / `REV_7e139334e8a01a9effdbbe6a95e22eff4b195a40b4b8468ffe96ed5365a25a90` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-004-002` / `TC-IMPRANA-FR-SEC-004-002` | `REV_8b6ab298fa7565b918f216d381ab3776faee0f51b99c5bf1640dff846df217b5` / `REV_05c1e31a42fdc98350bb9140d73cd4d130c23e72666f41449282d40e10b797f5` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-004-003` / `TC-IMPRANA-FR-SEC-004-003` | `REV_30845f0e64738985056be4356a5e13222c6c3ed0e7e1e3e7844bcd741d31a3ab` / `REV_4ff6ebd91554be96dbcc846d42875db257e29396f264e20bcb318facd1f23eac` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-004-004` / `TC-IMPRANA-FR-SEC-004-004` | `REV_af9b9623a74bad2e9f7ff4dba7b8d4d8c41894bbf8d8cd57570557891e377032` / `REV_80a5b43cb7199ed00712879e3d303e391b400e4ef7688d46229539f6f6380c75` | manual → MANUAL recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-004-001 — Hostile inputs are handled at the boundary

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-004-001` is not created. Verification duty `TASK-FR-SEC-004-02` (qualification); source `docs/backlog/backlog.csv` record 150, exact block `ae4a57b2a2c559413bfc2d7e653dedee932b5acabb5bba768f9a31063a17fa84`.

**Original preconditions**

1. script-like text, a cross tenant object reference and an internal network URL

**Original actions**

1. each is submitted

**Exact source oracles — all required**

1. each is safely rendered or rejected at the relevant boundary

Legacy same-requirement reuse candidates: `TC-SEC-004-01`, `TC-SEC-004-02`, `SEC-012`, `SEC-013`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-004-002 — Shared authorisation and error contracts

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-004-002` is not created. Verification duty `TASK-FR-SEC-004-02` (qualification); source `docs/backlog/backlog.csv` record 150, exact block `8b6ab298fa7565b918f216d381ab3776faee0f51b99c5bf1640dff846df217b5`.

**Original preconditions**

1. public and authenticated surfaces

**Original actions**

1. a request is processed

**Exact source oracles — all required**

1. both use the same domain authorisation and safe error contracts
2. authenticated mutations are protected and outbound destinations are verified

Legacy same-requirement reuse candidates: `TC-SEC-004-01`, `TC-SEC-004-02`, `SEC-012`, `SEC-013`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-004-003 — Verification maps to ASVS

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-004-003` is not created. Verification duty `TASK-FR-SEC-004-02` (qualification); source `docs/backlog/backlog.csv` record 150, exact block `30845f0e64738985056be4356a5e13222c6c3ed0e7e1e3e7844bcd741d31a3ab`.

**Original preconditions**

1. security verification for a release

**Original actions**

1. it is reviewed

**Exact source oracles — all required**

1. applicable ASVS 5.0 controls through Level 2, including Level 1, are mapped
2. tests cover uploads, rich text, links, filtering, exports and API references

Legacy same-requirement reuse candidates: `TC-SEC-004-01`, `TC-SEC-004-02`, `SEC-012`, `SEC-013`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-004-004 — Reject assertions in place of evidence

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-004-004` is not created. Verification duty `TASK-FR-SEC-004-02` (qualification); source `docs/backlog/backlog.csv` record 150, exact block `af9b9623a74bad2e9f7ff4dba7b8d4d8c41894bbf8d8cd57570557891e377032`.

**Original preconditions**

1. a release that asserts broad immunity without passing test evidence and independent review

**Original actions**

1. it is assessed

**Exact source oracles — all required**

1. the assertion is not accepted as security verification

Legacy same-requirement reuse candidates: `TC-SEC-004-01`, `TC-SEC-004-02`, `SEC-012`, `SEC-013`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
