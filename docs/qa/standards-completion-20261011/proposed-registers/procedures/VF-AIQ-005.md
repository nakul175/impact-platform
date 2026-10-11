## QA v1.3 — source-bound case design (proposed)

Story `VF-AIQ-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-AIQ-005-001` / `TC-IMPRANA-VF-AIQ-005-001` | `REV_168ce480774b22ef076983957b79c95e1f8eb0c4b68cc844d46e20245115f082` / `REV_39997aaae6eb4d24052c772b1937029c7d3b6924b86d60f1884647d58adadc70` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-VF-AIQ-005-002` / `TC-IMPRANA-VF-AIQ-005-002` | `REV_04acaf78a2be7de397efdf3367bd6bb51226233ed400a13f9a8f2fbb0dc038c4` / `REV_6d624fb41a0099fa932cf2842c32803dec1c8a6cf5a877459163b17bd01e3de4` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-VF-AIQ-005-003` / `TC-IMPRANA-VF-AIQ-005-003` | `REV_10590c5c4e94080dbe2cac5019adf9834899b4ccda7ecb7969252d2cc5cdef93` / `REV_6d1244f72cd843a8eef81703c295fec25fb303e951eb8f99f5658bfed2d56740` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-VF-AIQ-005-004` / `TC-IMPRANA-VF-AIQ-005-004` | `REV_e5240f6c8bb670d88d3021eb2857727cff821b1d1b3213bbba2e5f3f3b58ded3` / `REV_29fb7a037ca2fa3ce483debfec2409313cb09ace1cce0ee3948bd4b5af3b1936` | manual → MANUAL recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-AIQ-005-001 — Degraded candidate is identified by versioned evaluation

Source persona: Platform Operator. Proposed fixture `FIX-VF-AIQ-005-001` is not created. Verification duty `TASK-VF-AIQ-005-03` (qualification); source `docs/backlog/backlog.csv` record 260, exact block `168ce480774b22ef076983957b79c95e1f8eb0c4b68cc844d46e20245115f082`.

**Original preconditions**

1. a deliberately degraded candidate configuration

**Original actions**

1. its versioned evaluation is compared to the approved version

**Exact source oracles — all required**

1. differences in quality, latency and cost are identified

Legacy same-requirement reuse candidates: `TC-VF-AIQ-005`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AIQ-005-002 — Controlled exposure can be stopped and rolled back

Source persona: Platform Operator. Proposed fixture `FIX-VF-AIQ-005-002` is not created. Verification duty `TASK-VF-AIQ-005-03` (qualification); source `docs/backlog/backlog.csv` record 260, exact block `04acaf78a2be7de397efdf3367bd6bb51226233ed400a13f9a8f2fbb0dc038c4`.

**Original preconditions**

1. a candidate configuration in controlled rollout

**Original actions**

1. the rollout is stopped and rolled back

**Exact source oracles — all required**

1. the approved version is restored
2. affected artifacts are identified

Legacy same-requirement reuse candidates: `TC-VF-AIQ-005`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AIQ-005-003 — Production quality is monitored

Source persona: Platform Operator. Proposed fixture `FIX-VF-AIQ-005-003` is not created. Verification duty `TASK-VF-AIQ-005-03` (qualification); source `docs/backlog/backlog.csv` record 260, exact block `10590c5c4e94080dbe2cac5019adf9834899b4ccda7ecb7969252d2cc5cdef93`.

**Original preconditions**

1. an AI configuration in production

**Original actions**

1. it is monitored

**Exact source oracles — all required**

1. failures, reviewer corrections, refusals, latency, cost and language-specific quality are tracked with minimised content retention

Legacy same-requirement reuse candidates: `TC-VF-AIQ-005`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AIQ-005-004 — Reject a rollback that reinstates a prohibited provider

Source persona: Platform Operator. Proposed fixture `FIX-VF-AIQ-005-004` is not created. Verification duty `TASK-VF-AIQ-005-03` (qualification); source `docs/backlog/backlog.csv` record 260, exact block `e5240f6c8bb670d88d3021eb2857727cff821b1d1b3213bbba2e5f3f3b58ded3`.

**Original preconditions**

1. a provider that is now prohibited by policy

**Original actions**

1. a rollback targets a configuration that used that provider

**Exact source oracles — all required**

1. the provider is not reinstated
2. only the approved policy-compatible destination and tool set is restored

Legacy same-requirement reuse candidates: `TC-VF-AIQ-005`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
