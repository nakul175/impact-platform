## QA v1.3 — source-bound case design (proposed)

Story `FR-AI-012` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-AI-012-001` / `TC-IMPRANA-FR-AI-012-001` | `REV_a428a14a50ebdb82f4275cbe077a7492b243ced602c083095d72496864cfd4ed` / `REV_b6f23ba0026a7b60abe788a9bf860290aea83da14022f2f4bb94fd4989046df1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-012-002` / `TC-IMPRANA-FR-AI-012-002` | `REV_eb0c215e08793f6a1d7998b7a5f4600a35abe048ecf6ab799fb1264a5f3d6d44` / `REV_424efe856249fa89d08092f6bfab53c69186ed44cb69e2371986a58b9b425a60` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-012-003` / `TC-IMPRANA-FR-AI-012-003` | `REV_ade7a8078e377b51c99e506cce47483f8fa9dc4eadc47f80db79506add28fca9` / `REV_e875a89e4415cecf835ef42a899ce714b421d30b1e762e0892006e91630244be` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-012-004` / `TC-IMPRANA-FR-AI-012-004` | `REV_f403679a12d9a5631f8e1a8aac2a4385d86f090070feb543cb46c2c2b5adfdfb` / `REV_a903f36474811307a944b6beec9b28ed30a6c8189baa0d0637573568854683ca` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-AI-012-001 — Policy is evaluated before transmission

Source persona: Privacy Officer. Proposed fixture `FIX-FR-AI-012-001` is not created. Verification duty `TASK-FR-AI-012-03` (qualification); source `docs/backlog/backlog.csv` record 11, exact block `a428a14a50ebdb82f4275cbe077a7492b243ced602c083095d72496864cfd4ed`.

**Original preconditions**

1. an AI request containing tenant content

**Original actions**

1. it is about to be transmitted

**Exact source oracles — all required**

1. tenant, use case, purpose, classification, region, provider retention and minimisation policy are evaluated
2. prohibited fields are redacted or excluded
3. the approved destination version is recorded

Legacy same-requirement reuse candidates: `TC-AI-012-01`, `TC-AI-012-02`, `TC-AT24`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `apps/api/impact_api/privacy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-012-002 — Primary provider offline for restricted data

Source persona: Privacy Officer. Proposed fixture `FIX-FR-AI-012-002` is not created. Verification duty `TASK-FR-AI-012-03` (qualification); source `docs/backlog/backlog.csv` record 11, exact block `eb0c215e08793f6a1d7998b7a5f4600a35abe048ecf6ab799fb1264a5f3d6d44`.

**Original preconditions**

1. restricted data and the primary provider forced offline

**Original actions**

1. an AI request is made

**Exact source oracles — all required**

1. no unapproved fallback provider receives the content
2. the manual workflow remains usable

Legacy same-requirement reuse candidates: `TC-AI-012-01`, `TC-AI-012-02`, `TC-AT24`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `apps/api/impact_api/privacy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-012-003 — Reject training reuse without opt in

Source persona: Privacy Officer. Proposed fixture `FIX-FR-AI-012-003` is not created. Verification duty `TASK-FR-AI-012-03` (qualification); source `docs/backlog/backlog.csv` record 11, exact block `ade7a8078e377b51c99e506cce47483f8fa9dc4eadc47f80db79506add28fca9`.

**Original preconditions**

1. a tenant that has not explicitly opted in

**Original actions**

1. its content is processed by AI

**Exact source oracles — all required**

1. it is not reused for training
2. no implicit opt in is applied

Legacy same-requirement reuse candidates: `TC-AI-012-01`, `TC-AI-012-02`, `TC-AT24`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `apps/api/impact_api/privacy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-012-004 — Reject retention and reuse outside schedule

Source persona: Privacy Officer. Proposed fixture `FIX-FR-AI-012-004` is not created. Verification duty `TASK-FR-AI-012-03` (qualification); source `docs/backlog/backlog.csv` record 11, exact block `f403679a12d9a5631f8e1a8aac2a4385d86f090070feb543cb46c2c2b5adfdfb`.

**Original preconditions**

1. prompts, answers and diagnostics

**Original actions**

1. their retention schedule ends or evaluation datasets are assembled

**Exact source oracles — all required**

1. they are not kept beyond their schedule
2. private content is not automatically copied into broad model evaluation datasets

Legacy same-requirement reuse candidates: `TC-AI-012-01`, `TC-AI-012-02`, `TC-AT24`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `apps/api/impact_api/privacy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
