## QA v1.3 — source-bound case design (proposed)

Story `FR-PRV-003` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRV-003-001` / `TC-IMPRANA-FR-PRV-003-001` | `REV_2281f60b4cc9fa0b7a4cf2b3010a768a0e8fdc89f4e0f63d76a1ed14b6fce8d4` / `REV_1bca442d024b4369e1dc529faceb92667788b5078a890e512c1710611ba5230a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-003-002` / `TC-IMPRANA-FR-PRV-003-002` | `REV_9dca49b03ce94f17af87145acdb139753710dee138305640be0dee4d7af087c1` / `REV_c5a6548d1bcdabaf97ebaa7c76e6b5d727969e0d6fbad24a513e9f140dc44e86` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-003-003` / `TC-IMPRANA-FR-PRV-003-003` | `REV_a8ec2d99c9b28a843dbc53b3225a8963d0476d69c540784d75d5987480909eb0` / `REV_2bd8f1bf856dc55adf5feb998b13d10e9953ddda56ab6d6f76590d1e924c1eb1` | manual → MANUAL recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRV-003-001 — Transfer is checked against permitted destinations

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-003-001` is not created. Verification duty `TASK-FR-PRV-003-04` (qualification); source `docs/backlog/backlog.csv` record 128, exact block `2281f60b4cc9fa0b7a4cf2b3010a768a0e8fdc89f4e0f63d76a1ed14b6fce8d4`.

**Original preconditions**

1. a tenant policy listing permitted regions and destinations for primary data, recovery, support and models

**Original actions**

1. processing requests a transfer to a destination

**Exact source oracles — all required**

1. destination eligibility is checked before the transfer proceeds

Legacy same-requirement reuse candidates: `TC-PRV-003-01`, `TC-PRV-003-02`, `TC-AT19`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-003-002 — Adding a destination requires approval and an impact notice

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-003-002` is not created. Verification duty `TASK-FR-PRV-003-04` (qualification); source `docs/backlog/backlog.csv` record 128, exact block `9dca49b03ce94f17af87145acdb139753710dee138305640be0dee4d7af087c1`.

**Original preconditions**

1. a Privacy Officer proposes a new destination for the tenant policy

**Original actions**

1. the destination is submitted

**Exact source oracles — all required**

1. it is not permitted until the applicable approval is recorded
2. an impact notice is issued

Legacy same-requirement reuse candidates: `TC-PRV-003-01`, `TC-PRV-003-02`, `TC-AT19`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-003-003 — Reject recovery in a prohibited region

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-003-003` is not created. Verification duty `TASK-FR-PRV-003-04` (qualification); source `docs/backlog/backlog.csv` record 128, exact block `a8ec2d99c9b28a843dbc53b3225a8963d0476d69c540784d75d5987480909eb0`.

**Original preconditions**

1. the primary region has failed

**Original actions**

1. recovery is requested in a region the tenant policy prohibits

**Exact source oracles — all required**

1. recovery is blocked because failover cannot override residency
2. the incident records the approved alternative or a continued controlled outage with the restriction communicated
3. no data is moved silently

Legacy same-requirement reuse candidates: `TC-PRV-003-01`, `TC-PRV-003-02`, `TC-AT19`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
