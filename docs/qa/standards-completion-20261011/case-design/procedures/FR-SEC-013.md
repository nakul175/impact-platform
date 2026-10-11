## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-013` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-013-001` / `TC-IMPRANA-FR-SEC-013-001` | `REV_8b366b0e160ba146c1389a465f4e1294fa75a55ffbdf8caf5f348b89aa43aea2` / `REV_3b14307bc29923f3e95ca8392608a79cbc225e8b7eb0ca00e23a985cf9994b4f` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-013-002` / `TC-IMPRANA-FR-SEC-013-002` | `REV_e34e6727e48edab6a9700f40eee667728eb9cc61a24ee762a9cb7fa809ce9423` / `REV_e1b5531c33fcab58d214a54c0da1ad8968ce8802b1d060384f027d9a1c1f5760` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-013-003` / `TC-IMPRANA-FR-SEC-013-003` | `REV_8c945ec74bc42f8934af46c95122a3ed17d5ae7ede61b322f757b24e6f98f4a8` / `REV_5d113ba4f788c08a21106438fe964774326e5f7ec1d21685a3c960fecd7ed697` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-013-004` / `TC-IMPRANA-FR-SEC-013-004` | `REV_37d01c93a5e1f3cf77a36c5b9b3269072ae0e5e32aff8ff959435b4c87640f36` / `REV_892764c533491e4ef12eac75a22f407eaa515a43d10c43d088d01ec2fe7c8713` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-013-001 — Request scoped elevation

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-013-001` is not created. Verification duty `TASK-FR-SEC-013-03` (qualification); source `docs/backlog/backlog.csv` record 157, exact block `8b366b0e160ba146c1389a465f4e1294fa75a55ffbdf8caf5f348b89aa43aea2`.

**Original preconditions**

1. a Platform Operator with a named incident or maintenance task

**Original actions**

1. they request elevation

**Exact source oracles — all required**

1. the request states the exact capability scope and duration
2. a distinct reviewer approves where required

Legacy same-requirement reuse candidates: `TC-SEC-013-01`, `TC-SEC-013-02`, `TC-AT17`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-013-002 — Emergency activation is reviewed afterwards

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-013-002` is not created. Verification duty `TASK-FR-SEC-013-03` (qualification); source `docs/backlog/backlog.csv` record 157, exact block `e34e6727e48edab6a9700f40eee667728eb9cc61a24ee762a9cb7fa809ce9423`.

**Original preconditions**

1. an emergency elevation

**Original actions**

1. it is activated

**Exact source oracles — all required**

1. a mandatory retrospective review is created

Legacy same-requirement reuse candidates: `TC-SEC-013-01`, `TC-SEC-013-02`, `TC-AT17`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-013-003 — Sessions keep the real actor and expire

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-013-003` is not created. Verification duty `TASK-FR-SEC-013-03` (qualification); source `docs/backlog/backlog.csv` record 157, exact block `8c945ec74bc42f8934af46c95122a3ed17d5ae7ede61b322f757b24e6f98f4a8`.

**Original preconditions**

1. an elevated session

**Original actions**

1. it is used

**Exact source oracles — all required**

1. the real actor is retained
2. the session expires automatically

Legacy same-requirement reuse candidates: `TC-SEC-013-01`, `TC-SEC-013-02`, `TC-AT17`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-013-004 — Reject actions after expiry

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-013-004` is not created. Verification duty `TASK-FR-SEC-013-03` (qualification); source `docs/backlog/backlog.csv` record 157, exact block `37d01c93a5e1f3cf77a36c5b9b3269072ae0e5e32aff8ff959435b4c87640f36`.

**Original preconditions**

1. an operator elevated for recovery diagnostics whose grant has expired

**Original actions**

1. they attempt further reads or a queued sensitive operation runs

**Exact source oracles — all required**

1. all are denied
2. no expired job credential can continue a privileged operation

Legacy same-requirement reuse candidates: `TC-SEC-013-01`, `TC-SEC-013-02`, `TC-AT17`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
