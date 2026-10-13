## QA v1.3 — source-bound case design (proposed)

Story `FR-WFL-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-WFL-003-001` / `TC-IMPRANA-FR-WFL-003-001` | `REV_419c70fe585ad2a4cbc36d467b62ab40843073dd15163aa53d55e09d310d86c1` / `REV_e24ce936fda54d795a7b781d8412ab6cf8fa6ae9eb75d469a4b5157438ed707f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-003-002` / `TC-IMPRANA-FR-WFL-003-002` | `REV_ece8752c8648868efe40065a9ea1914d582ffdd2da3b7955460264806f68de99` / `REV_1e4c73de45dec4c75f961ea99faf1989b96f8fb0f5971c52b97279b7d4f4a1dd` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-003-003` / `TC-IMPRANA-FR-WFL-003-003` | `REV_d8327d907f3de7f289b75266a18d4db187a46bcde78c721a09aea622a7de8677` / `REV_e87fefd7607adbeff5bebe8644264b15cc5415391948019d1abdf32f93c50d38` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-003-004` / `TC-IMPRANA-FR-WFL-003-004` | `REV_020ccc1988b84cc399c8903a0d34a3c953df95f2c72127584f70f291cc21bab7` / `REV_a5dcbd0172e525b48961e6ecef9cdece3be90d350005fdc634a5f229d8a1cd1b` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-WFL-003-001 — Return work with actionable comments

Source persona: Reviewer. Proposed fixture `FIX-FR-WFL-003-001` is not created. Verification duty `TASK-FR-WFL-003-03` (interface); source `docs/backlog/backlog.csv` record 178, exact block `419c70fe585ad2a4cbc36d467b62ab40843073dd15163aa53d55e09d310d86c1`.

**Original preconditions**

1. a Reviewer reviewing a submission

**Original actions**

1. they return it with actionable comments tied to fields or issues

**Exact source oracles — all required**

1. the submission is returned to its author with those comments

Legacy same-requirement reuse candidates: `TC-WFL-003-01`, `TC-WFL-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-003-002 — Inspect two correction cycles

Source persona: Reviewer. Proposed fixture `FIX-FR-WFL-003-002` is not created. Verification duty `TASK-FR-WFL-003-03` (interface); source `docs/backlog/backlog.csv` record 178, exact block `ece8752c8648868efe40065a9ea1914d582ffdd2da3b7955460264806f68de99`.

**Original preconditions**

1. a submission that has gone through two correction cycles

**Original actions**

1. its history is inspected

**Exact source oracles — all required**

1. each cycle shows its distinct reasons, revisions, authors and decision times
2. each resubmission is a new candidate version compared to the returned one with a fresh decision sequence

Legacy same-requirement reuse candidates: `TC-WFL-003-01`, `TC-WFL-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-003-003 — Reject a return or rejection without required reasons

Source persona: Reviewer. Proposed fixture `FIX-FR-WFL-003-003` is not created. Verification duty `TASK-FR-WFL-003-03` (interface); source `docs/backlog/backlog.csv` record 178, exact block `d8327d907f3de7f289b75266a18d4db187a46bcde78c721a09aea622a7de8677`.

**Original preconditions**

1. a Reviewer deciding on a submission

**Original actions**

1. they return it without actionable comments or reject it without a policy permitted final disposition and reason

**Exact source oracles — all required**

1. the decision is refused

Legacy same-requirement reuse candidates: `TC-WFL-003-01`, `TC-WFL-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-003-004 — Reject reuse of previous approvals

Source persona: Reviewer. Proposed fixture `FIX-FR-WFL-003-004` is not created. Verification duty `TASK-FR-WFL-003-03` (interface); source `docs/backlog/backlog.csv` record 178, exact block `020ccc1988b84cc399c8903a0d34a3c953df95f2c72127584f70f291cc21bab7`.

**Original preconditions**

1. a resubmitted candidate whose earlier version had approvals

**Original actions**

1. the new candidate is decided

**Exact source oracles — all required**

1. the previous approvals remain historical
2. they do not satisfy the new candidate unless the workflow explicitly revalidates unchanged independent stages under a qualified rule

Legacy same-requirement reuse candidates: `TC-WFL-003-01`, `TC-WFL-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
