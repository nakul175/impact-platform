## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-011` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-011-001` / `TC-IMPRANA-FR-SEC-011-001` | `REV_7c9e6a53178c77e97e35a43e7cfebfc1e97fe2b7fd8b0602a67ac86d32dd8191` / `REV_2c97ac56ba94a8747e01b8154f16639e41a13d0153c79835d509a1f95dc24184` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-011-002` / `TC-IMPRANA-FR-SEC-011-002` | `REV_56cabcc1f5e60677f084811fc00eab5372b9a9009e23a490906bb2c0a207fe4c` / `REV_b811fc32f77c600a53ba8b918d90107c49115ad43714690c3866f83347c66faa` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-011-003` / `TC-IMPRANA-FR-SEC-011-003` | `REV_119c5d65f4ef25e90acebac6f399b4d58540f31d244ca73382ce0d9b3c3470b6` / `REV_3ba7a429150e8bcbe979109031a192651d47f3d9528c5ef3da632657b78a50c4` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-011-004` / `TC-IMPRANA-FR-SEC-011-004` | `REV_f643584dc091ccb73b73b2794783e4fcabc3de44d95833c0bbb3f707ae0bd079` / `REV_fe77c47ae1469252ae2392c48b6a4a871d9c6692e40c34c8c8e089610be99ba2` | manual → MANUAL recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-011-001 — Detection raises a restricted incident

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-011-001` is not created. Verification duty `TASK-FR-SEC-011-03` (governance); source `docs/backlog/backlog.csv` record 155, exact block `7c9e6a53178c77e97e35a43e7cfebfc1e97fe2b7fd8b0602a67ac86d32dd8191`.

**Original preconditions**

1. detection rules for suspicious identity changes, bulk extraction, service misuse and failed controls

**Original actions**

1. a rule fires

**Exact source oracles — all required**

1. a restricted incident record is created
2. on call receives safe context and correlation references

Legacy same-requirement reuse candidates: `TC-SEC-011-01`, `TC-SEC-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-011-002 — Compromised service identity is handled

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-011-002` is not created. Verification duty `TASK-FR-SEC-011-03` (governance); source `docs/backlog/backlog.csv` record 155, exact block `56cabcc1f5e60677f084811fc00eab5372b9a9009e23a490906bb2c0a207fe4c`.

**Original preconditions**

1. a simulated compromised service identity

**Original actions**

1. detection triggers

**Exact source oracles — all required**

1. the identity is revoked
2. the incident identifies affected jobs and potential disclosures
3. general alerts contain no payloads

Legacy same-requirement reuse candidates: `TC-SEC-011-01`, `TC-SEC-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-011-003 — Incident handling is recorded

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-011-003` is not created. Verification duty `TASK-FR-SEC-011-03` (governance); source `docs/backlog/backlog.csv` record 155, exact block `119c5d65f4ef25e90acebac6f399b4d58540f31d244ca73382ce0d9b3c3470b6`.

**Original preconditions**

1. an open incident

**Original actions**

1. it is handled

**Exact source oracles — all required**

1. containment, affected tenants, evidence preservation, recovery and communications decisions are recorded

Legacy same-requirement reuse candidates: `TC-SEC-011-01`, `TC-SEC-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-011-004 — Reject invented deadlines and uncontrolled access

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-011-004` is not created. Verification duty `TASK-FR-SEC-011-03` (governance); source `docs/backlog/backlog.csv` record 155, exact block `f643584dc091ccb73b73b2794783e4fcabc3de44d95833c0bbb3f707ae0bd079`.

**Original preconditions**

1. an incident requiring notification or investigation

**Original actions**

1. notifications are sent or investigators access data

**Exact source oracles — all required**

1. notifications follow the approved legal and contractual policy, not an invented universal deadline
2. investigation access follows exceptional support controls

Legacy same-requirement reuse candidates: `TC-SEC-011-01`, `TC-SEC-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
