## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-011` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-011-001` / `TC-IMPRANA-FR-CAL-011-001` | `REV_e1860dedb699bb04314a769e77d1723a023a79b63d501cfb0644c3cc3165c2c9` / `REV_6caa0e1e11070444151f291ecd07c05375a6191a5e2849d009c8cab9ee8e3007` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-011-002` / `TC-IMPRANA-FR-CAL-011-002` | `REV_0ae608f044baac234a6552667075475ad5aa47e9f4737eacf3061a7e562b1cdb` / `REV_a7063064e5b39943c6040445ea243d287f31c44ef3f5028111e058e4dc50573e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-011-003` / `TC-IMPRANA-FR-CAL-011-003` | `REV_6ec9849aca76fc1b75dc9399efc2c712de7fd7a28589fdb032ce50f257fbe2ce` / `REV_0dc50ece6f367d27fbeb2f6d82366dc23c6ba1aaa82d3c054c0946eb086f8456` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-011-001 — Correction updates live results but not published snapshots

Source persona: Data Steward. Proposed fixture `FIX-FR-CAL-011-001` is not created. Verification duty `TASK-FR-CAL-011-03` (qualification); source `docs/backlog/backlog.csv` record 61, exact block `e1860dedb699bb04314a769e77d1723a023a79b63d501cfb0644c3cc3165c2c9`.

**Original preconditions**

1. a ratio whose numerator comes from an imported value
2. a quarterly PDF report has been published from it

**Original actions**

1. a correction to that numerator is approved

**Exact source oracles — all required**

1. the affected definitions, result periods, dashboards and unpublished reports are identified
2. recalculation creates a new result version and the current ratio updates
3. the published quarterly PDF remains the original version until restated

Legacy same-requirement reuse candidates: `TC-CAL-011-01`, `TC-CAL-011-02`, `TC-AT07`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-011-002 — Retry creates one new result per input version

Source persona: Data Steward. Proposed fixture `FIX-FR-CAL-011-002` is not created. Verification duty `TASK-FR-CAL-011-03` (qualification); source `docs/backlog/backlog.csv` record 61, exact block `0ae608f044baac234a6552667075475ad5aa47e9f4737eacf3061a7e562b1cdb`.

**Original preconditions**

1. a recalculation is retried after an interruption

**Original actions**

1. it completes

**Exact source oracles — all required**

1. exactly one intended new result exists per input version

Legacy same-requirement reuse candidates: `TC-CAL-011-01`, `TC-CAL-011-02`, `TC-AT07`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-011-003 — Reject a mixed official snapshot after a failed run

Source persona: Data Steward. Proposed fixture `FIX-FR-CAL-011-003` is not created. Verification duty `TASK-FR-CAL-011-03` (qualification); source `docs/backlog/backlog.csv` record 61, exact block `6ec9849aca76fc1b75dc9399efc2c712de7fd7a28589fdb032ce50f257fbe2ce`.

**Original preconditions**

1. a downstream recalculation run fails

**Original actions**

1. affected results are viewed

**Exact source oracles — all required**

1. they show stale status
2. no partially recalculated mixed official snapshot is presented
3. the published report is not restated without a separate approved restatement

Legacy same-requirement reuse candidates: `TC-CAL-011-01`, `TC-CAL-011-02`, `TC-AT07`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
