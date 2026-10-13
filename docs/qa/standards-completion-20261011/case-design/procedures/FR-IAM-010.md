## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-010` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-010-001` / `TC-IMPRANA-FR-IAM-010-001` | `REV_23527e36257fc02060646e2062bb8267f33066b12daeadbb804c2e6cb142d8fb` / `REV_1e1c009450dabd043b4cd85208b01b99576084626a14e26173cd47afd45276eb` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-010-002` / `TC-IMPRANA-FR-IAM-010-002` | `REV_97d6c9f30ebd4ea1581fb5d71dc3cef447c3dd7681bf8e06a139be20eed06be7` / `REV_dfdb8a630edee28a520b3bfd75c92fb8398a3a4742ac85c58c380ff30087f863` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-010-003` / `TC-IMPRANA-FR-IAM-010-003` | `REV_a0fe375694b9be125174abc3fa05671477b543679cdb9cf0d8cce5fae24d6e0f` / `REV_d5c060d906652d6970b731dfabfaaf132b8d744b5ef5fe11779f67c253ef79da` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-010-004` / `TC-IMPRANA-FR-IAM-010-004` | `REV_09051f5c924ec929b2807bc0ac760e56ea863eb9025f4b09a65614d3dc005e34` / `REV_1aa7a2cb3d82c938c7326167350e8906005bb33a37e81f11cb3dd16fa53ef8f7` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-010-005` / `TC-IMPRANA-FR-IAM-010-005` | `REV_24d1abdd76208d56ac89c1ac952dee8b82b34475f5aa8a1722f5f3473db7fe01` / `REV_94d2aac12c2cc61e47555318c260834014d86fd0956a52d765ad6dda38a1ebd4` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-010-001 — Maintain groups and inspect effective permissions

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-010-001` is not created. Verification duty `TASK-FR-IAM-010-03` (qualification); source `docs/backlog/backlog.csv` record 240, exact block `23527e36257fc02060646e2062bb8267f33066b12daeadbb804c2e6cb142d8fb`.

**Original preconditions**

1. a group editor maintains members and scoped grants with effective dates and ownership

**Original actions**

1. effective permissions are inspected for a member

**Exact source oracles — all required**

1. all valid grant paths are expanded

Legacy same-requirement reuse candidates: `TC-IAM-010-01`, `TC-IAM-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-010-002 — Remove a member from a group

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-010-002` is not created. Verification duty `TASK-FR-IAM-010-03` (qualification); source `docs/backlog/backlog.csv` record 240, exact block `97d6c9f30ebd4ea1581fb5d71dc3cef447c3dd7681bf8e06a139be20eed06be7`.

**Original preconditions**

1. an Analyst is a member of a reporting group

**Original actions**

1. they are removed from the group

**Exact source oracles — all required**

1. their existing report links, AI citations and scheduled exports are denied within the defined bound

Legacy same-requirement reuse candidates: `TC-IAM-010-01`, `TC-IAM-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-010-003 — Delete a group

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-010-003` is not created. Verification duty `TASK-FR-IAM-010-03` (qualification); source `docs/backlog/backlog.csv` record 240, exact block `a0fe375694b9be125174abc3fa05671477b543679cdb9cf0d8cce5fae24d6e0f`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a group is deleted

**Exact source oracles — all required**

1. its future grants are retired
2. its audit history is retained

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-010-01`, `TC-IAM-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-010-004 — Reject group permissions overriding restrictive policy

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-010-004` is not created. Verification duty `TASK-FR-IAM-010-03` (qualification); source `docs/backlog/backlog.csv` record 240, exact block `09051f5c924ec929b2807bc0ac760e56ea863eb9025f4b09a65614d3dc005e34`.

**Original preconditions**

1. an explicit restrictive policy applies to a member

**Original actions**

1. a group grants a conflicting permission

**Exact source oracles — all required**

1. the restrictive policy still applies

Legacy same-requirement reuse candidates: `TC-IAM-010-01`, `TC-IAM-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-010-005 — Reject unqualified nested groups

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-010-005` is not created. Verification duty `TASK-FR-IAM-010-03` (qualification); source `docs/backlog/backlog.csv` record 240, exact block `24d1abdd76208d56ac89c1ac952dee8b82b34475f5aa8a1722f5f3473db7fe01`.

**Original preconditions**

1. cycle detection, visible ancestry and identical revocation behaviour have not been qualified for nested groups

**Original actions**

1. an administrator attempts to nest one group inside another

**Exact source oracles — all required**

1. nesting is not available and groups remain flat

Legacy same-requirement reuse candidates: `TC-IAM-010-01`, `TC-IAM-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
