## QA v1.3 — source-bound case design (proposed)

Story `FR-AI-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-AI-006-001` / `TC-IMPRANA-FR-AI-006-001` | `REV_a4ecfccf3e028d4e844dba9b104603a3bd15899587f246b0caff2a7cd29f5a07` / `REV_1f2d390a39d5ebdd8701a07fd007d4b8214f929db79307e4d56a7c731b96bebb` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-006-002` / `TC-IMPRANA-FR-AI-006-002` | `REV_17b0ac8ae3c4447b3da86521cc93fd1762a12296f4fce6aa6758beb38e1a63a0` / `REV_9545685f4e46a320f97481d3d84dc5afe35da27a680fd0fc19517d5f86c3eea2` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-006-003` / `TC-IMPRANA-FR-AI-006-003` | `REV_80a8515ff33c1691afa8682b86fe17cc5245b16bd5f4bb2465386f8081b0bc3b` / `REV_adcc177b9a070f748a681a3aec120db3e4a62ccce95713aba4ee7265ad5a08c5` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-006-004` / `TC-IMPRANA-FR-AI-006-004` | `REV_5588eba1919c2acdc7e28f7dc67d10ea219e7d6e3b5aa9aeba4e0962fc3cfc64` / `REV_6c64d6cca966b0e94ec1486634e7b9abb9a27ca364e9e0e8070e5a36dbcf024a` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-AI-006-001 — Numeric question runs as a typed analysis plan

Source persona: Analyst. Proposed fixture `FIX-FR-AI-006-001` is not created. Verification duty `TASK-FR-AI-006-03` (qualification); source `docs/backlog/backlog.csv` record 186, exact block `a4ecfccf3e028d4e844dba9b104603a3bd15899587f246b0caff2a7cd29f5a07`.

**Original preconditions**

1. an Analyst asks a numeric question

**Original actions**

1. it is processed

**Exact source oracles — all required**

1. it is translated into a plan with measure, compatible sources, filters, period, dimensions and permitted operation
2. an authorised deterministic tool executes the plan
3. the answer embeds the returned values and result references without model recomputation

Legacy same-requirement reuse candidates: `TC-AI-006-01`, `TC-AI-006-02`, `TC-AT26`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-006-002 — Pooled percentage uses the approved calculation

Source persona: Analyst. Proposed fixture `FIX-FR-AI-006-002` is not created. Verification duty `TASK-FR-AI-006-03` (qualification); source `docs/backlog/backlog.csv` record 186, exact block `17b0ac8ae3c4447b3da86521cc93fd1762a12296f4fce6aa6758beb38e1a63a0`.

**Original preconditions**

1. results of 50/100 and 1/10

**Original actions**

1. the Analyst asks for the pooled value

**Exact source oracles — all required**

1. the answer presents 46.36 percent with 51/110
2. it includes the approved calculation receipt

Legacy same-requirement reuse candidates: `TC-AI-006-01`, `TC-AI-006-02`, `TC-AT26`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-006-003 — Reject arbitrary queries

Source persona: Analyst. Proposed fixture `FIX-FR-AI-006-003` is not created. Verification duty `TASK-FR-AI-006-03` (qualification); source `docs/backlog/backlog.csv` record 186, exact block `80a8515ff33c1691afa8682b86fe17cc5245b16bd5f4bb2465386f8081b0bc3b`.

**Original preconditions**

1. a numeric question

**Original actions**

1. answering it would require arbitrary SQL, code execution or an unrestricted user supplied query

**Exact source oracles — all required**

1. the request is refused

Legacy same-requirement reuse candidates: `TC-AI-006-01`, `TC-AI-006-02`, `TC-AT26`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-006-004 — Reject mismatched figures

Source persona: Analyst. Proposed fixture `FIX-FR-AI-006-004` is not created. Verification duty `TASK-FR-AI-006-03` (qualification); source `docs/backlog/backlog.csv` record 186, exact block `5588eba1919c2acdc7e28f7dc67d10ea219e7d6e3b5aa9aeba4e0962fc3cfc64`.

**Original preconditions**

1. drafted numeric text that does not match the tool value

**Original actions**

1. the answer is about to be delivered

**Exact source oracles — all required**

1. delivery of the official claim is blocked

Legacy same-requirement reuse candidates: `TC-AI-006-01`, `TC-AI-006-02`, `TC-AT26`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
