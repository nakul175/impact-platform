## QA v1.3 — source-bound case design (proposed)

Story `FR-RPT-011` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-RPT-011-001` / `TC-IMPRANA-FR-RPT-011-001` | `REV_5b700f8f7946f72a47b341080f7e8a3a339920697a3a63704b52b12d87537741` / `REV_9112ab367c430fae4bc2940f660eb3cf7b365d4287def16065e743e0deab4f8d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-011-002` / `TC-IMPRANA-FR-RPT-011-002` | `REV_ecc60f6c844b1aa5cc9030be0c782342e38c8ffed4aa071ebbf37e88deef60d7` / `REV_a75c925fcea48bd04e6d911180119af1de88d677167442e7d636d441ad06905f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-011-003` / `TC-IMPRANA-FR-RPT-011-003` | `REV_227136ac9fbcce8d00616af9678c724a35e6c2bac4ebc9992cb2a26b0d3896b9` / `REV_51227487cfdd659c49c07cae6fbea52fb786eab2ae4e09c2cc785cd1e4198991` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-011-004` / `TC-IMPRANA-FR-RPT-011-004` | `REV_d3793c48c6e3a3046bd1e5760252ed1da6fe9bcabcf9e633eb4737409a0d8cb9` / `REV_cb857232d3794985ba66d30d5cd045e01e400f03c10f062c93a441ace7758080` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-011-005` / `TC-IMPRANA-FR-RPT-011-005` | `REV_4beda30de7aaa64a23223d74b9c8fecc96cc5de385ee20c9a88927de3791876c` / `REV_99eb0c7159f273fb84fa47e7019538053422a767b28a34349891a96ad923a8ad` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-RPT-011-001 — Validation lists payload issues

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-011-001` is not created. Verification duty `TASK-FR-RPT-011-03` (qualification); source `docs/backlog/backlog.csv` record 357, exact block `5b700f8f7946f72a47b341080f7e8a3a339920697a3a63704b52b12d87537741`.

**Original preconditions**

1. a publication workspace with a specifically qualified IATI standard profile, organisation identity and mapping

**Original actions**

1. the MEL Manager validates a representative payload containing an invalid code

**Exact source oracles — all required**

1. mandatory fields, code list errors and disclosure issues are listed

Legacy same-requirement reuse candidates: `TC-RPT-011-01`, `TC-RPT-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-011-002 — Approved version reconciles to the external acknowledgement

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-011-002` is not created. Verification duty `TASK-FR-RPT-011-03` (qualification); source `docs/backlog/backlog.csv` record 357, exact block `ecc60f6c844b1aa5cc9030be0c782342e38c8ffed4aa071ebbf37e88deef60d7`.

**Original preconditions**

1. the MEL Manager has fixed the invalid code and approved the exact payload version

**Original actions**

1. the payload is exported or published directly and the external acknowledgement is received

**Exact source oracles — all required**

1. the payload version and external acknowledgement are recorded
2. the acknowledgement reconciles to the internal publication record

Legacy same-requirement reuse candidates: `TC-RPT-011-01`, `TC-RPT-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-011-003 — Reject unspecified schema versions

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-011-003` is not created. Verification duty `TASK-FR-RPT-011-03` (qualification); source `docs/backlog/backlog.csv` record 357, exact block `227136ac9fbcce8d00616af9678c724a35e6c2bac4ebc9992cb2a26b0d3896b9`.

**Original preconditions**

1. a schema version that has not been specifically qualified

**Original actions**

1. publication against it is attempted

**Exact source oracles — all required**

1. support for that schema version is not claimed

Legacy same-requirement reuse candidates: `TC-RPT-011-01`, `TC-RPT-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-011-004 — Reject treating an external rejection as delivered

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-011-004` is not created. Verification duty `TASK-FR-RPT-011-03` (qualification); source `docs/backlog/backlog.csv` record 357, exact block `d3793c48c6e3a3046bd1e5760252ed1da6fe9bcabcf9e633eb4737409a0d8cb9`.

**Original preconditions**

1. a payload has been published

**Original actions**

1. the external recipient rejects it

**Exact source oracles — all required**

1. the delivery is left as failed or correction required

Legacy same-requirement reuse candidates: `TC-RPT-011-01`, `TC-RPT-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-011-005 — Reject claims of erasing third party copies

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-011-005` is not created. Verification duty `TASK-FR-RPT-011-03` (qualification); source `docs/backlog/backlog.csv` record 357, exact block `4beda30de7aaa64a23223d74b9c8fecc96cc5de385ee20c9a88927de3791876c`.

**Original preconditions**

1. a published payload must be removed

**Original actions**

1. removal follows the qualified route

**Exact source oracles — all required**

1. the system does not claim that third party copies were erased

Legacy same-requirement reuse candidates: `TC-RPT-011-01`, `TC-RPT-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
