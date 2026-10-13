## QA v1.3 — source-bound case design (proposed)

Story `FR-ANA-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ANA-006-001` / `TC-IMPRANA-FR-ANA-006-001` | `REV_11519d95daa7709cd8c7cd6da559938d7365ddb5c9191ad347b82495b0910890` / `REV_84985beae3b3fd418682f28bdb97a57aa6276ccc3f82d1cbfc0a7d96f3f01a46` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-006-002` / `TC-IMPRANA-FR-ANA-006-002` | `REV_3013bba3c52de5962818595412dd69488c0b88c77ae226970ccdee5006204274` / `REV_3fe754430ec1c3579a70c06bb04507bdbcd1d308be7e6c4f44f48528aa9b9f3e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-006-003` / `TC-IMPRANA-FR-ANA-006-003` | `REV_b490e82bb32563371f5ca8c6b477a7fff100b278c010e4a4f18ea0a9d98642c6` / `REV_a2039aedd02dabf57902c045434bd0b8e97efb4056c101d48be7c093360fe370` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-006-004` / `TC-IMPRANA-FR-ANA-006-004` | `REV_efd4c7b89f88a77bff5c3ec8edd423922a2545379821c8bd74ac80664ba3f278` / `REV_269f18ec1204cd7404544e527c184c915fa3fdc2d6b6b48bdfceb072cda551c1` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ANA-006-001 — Configure a map with an equivalent table

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-006-001` is not created. Verification duty `TASK-FR-ANA-006-03` (qualification); source `docs/backlog/backlog.csv` record 327, exact block `11519d95daa7709cd8c7cd6da559938d7365ddb5c9191ad347b82495b0910890`.

**Original preconditions**

1. the Analyst configures a map with a boundary version, authorised point or aggregate layer, period, legend and missingness treatment

**Original actions**

1. the map is displayed

**Exact source oracles — all required**

1. an equivalent sortable table is available

Legacy same-requirement reuse candidates: `TC-ANA-006-01`, `TC-ANA-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-006-002 — District view discloses no household coordinates

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-006-002` is not created. Verification duty `TASK-FR-ANA-006-03` (qualification); source `docs/backlog/backlog.csv` record 327, exact block `3013bba3c52de5962818595412dd69488c0b88c77ae226970ccdee5006204274`.

**Original preconditions**

1. only district aggregates are allowed for vulnerable participants

**Original actions**

1. the Analyst publishes a district view and the permitted payload is inspected

**Exact source oracles — all required**

1. no household coordinate is disclosed

Legacy same-requirement reuse candidates: `TC-ANA-006-01`, `TC-ANA-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-006-003 — Reject precise coordinates hidden in map outputs

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-006-003` is not created. Verification duty `TASK-FR-ANA-006-03` (qualification); source `docs/backlog/backlog.csv` record 327, exact block `b490e82bb32563371f5ca8c6b477a7fff100b278c010e4a4f18ea0a9d98642c6`.

**Original preconditions**

1. only district aggregates are allowed

**Original actions**

1. tooltips, downloads or map request payloads are inspected

**Exact source oracles — all required**

1. no precise coordinates are present

Legacy same-requirement reuse candidates: `TC-ANA-006-01`, `TC-ANA-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-006-004 — Reject a hidden boundary mismatch

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-006-004` is not created. Verification duty `TASK-FR-ANA-006-03` (qualification); source `docs/backlog/backlog.csv` record 327, exact block `efd4c7b89f88a77bff5c3ec8edd423922a2545379821c8bd74ac80664ba3f278`.

**Original preconditions**

1. the data and the selected boundary version do not match

**Original actions**

1. the map is displayed

**Exact source oracles — all required**

1. the boundary mismatch is visible

Legacy same-requirement reuse candidates: `TC-ANA-006-01`, `TC-ANA-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
