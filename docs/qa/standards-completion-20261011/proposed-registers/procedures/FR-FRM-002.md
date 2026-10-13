## QA v1.3 — source-bound case design (proposed)

Story `FR-FRM-002` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FRM-002-001` / `TC-IMPRANA-FR-FRM-002-001` | `REV_813539b46d6064ebaf4e7b47463dd6b1892592010c1f7f43328a6f4a9931f6d8` / `REV_1c85d12ba6758a63ba915421dcd290bf67261f2e87910b8ae5ccae57b4f9c848` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-002-002` / `TC-IMPRANA-FR-FRM-002-002` | `REV_b7f6457cf404a5d3021fb6c761caf14d8fa7e7bf6fd1801cdaf4957d0c9d6921` / `REV_eb6cb4693fde018951e56e880a58f02a577dea09b9afeb3ee1d3f46eb74b7897` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-002-003` / `TC-IMPRANA-FR-FRM-002-003` | `REV_bcc74a8e3644a6c367aefa05dc939ec822d32a09db160e424f53cb4856ded12c` / `REV_d732669ade92cd18fc8fbfca0a108d15734d186661207180248880028b498636` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-002-004` / `TC-IMPRANA-FR-FRM-002-004` | `REV_4d73855e949069137817ee22cb43250fb5a0fb9f6fa6a7205f99a34ba8ff8044` / `REV_9c9036eb387f5879970f0fb5c9737b625dce25a05fb0a2947346778f0b25449e` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FRM-002-001 — Newly irrelevant answers clear after confirmation

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-002-001` is not created. Verification duty `TASK-FR-FRM-002-03` (qualification); source `docs/backlog/backlog.csv` record 77, exact block `813539b46d6064ebaf4e7b47463dd6b1892592010c1f7f43328a6f4a9931f6d8`.

**Original preconditions**

1. a form whose pregnancy-dependent fields are relevant only when pregnancy is yes
2. those fields have been answered

**Original actions**

1. the pregnancy answer changes from yes to no

**Exact source oracles — all required**

1. downstream state is recalculated in dependency order
2. after a visible confirmation the dependent fields are cleared under the declared policy

Legacy same-requirement reuse candidates: `TC-FRM-002-01`, `TC-FRM-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-002-002 — Retained hidden values are excluded from calculations

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-002-002` is not created. Verification duty `TASK-FR-FRM-002-03` (qualification); source `docs/backlog/backlog.csv` record 77, exact block `b7f6457cf404a5d3021fb6c761caf14d8fa7e7bf6fd1801cdaf4957d0c9d6921`.

**Original preconditions**

1. the schema explicitly retains a hidden value

**Original actions**

1. calculations run

**Exact source oracles — all required**

1. the retained hidden value is excluded unless the approved schema says otherwise

Legacy same-requirement reuse candidates: `TC-FRM-002-01`, `TC-FRM-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-002-003 — Reject a tampered payload

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-002-003` is not created. Verification duty `TASK-FR-FRM-002-03` (qualification); source `docs/backlog/backlog.csv` record 77, exact block `bcc74a8e3644a6c367aefa05dc939ec822d32a09db160e424f53cb4856ded12c`.

**Original preconditions**

1. a client payload containing answers the relevance rules disallow, including a hidden required answer

**Original actions**

1. it is submitted

**Exact source oracles — all required**

1. the server checks the same versioned rules and rejects the payload

Legacy same-requirement reuse candidates: `TC-FRM-002-01`, `TC-FRM-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-002-004 — Reject cyclic or inaccessible rule references

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-002-004` is not created. Verification duty `TASK-FR-FRM-002-03` (qualification); source `docs/backlog/backlog.csv` record 77, exact block `4d73855e949069137817ee22cb43250fb5a0fb9f6fa6a7205f99a34ba8ff8044`.

**Original preconditions**

1. a relevance or required rule that creates a cycle or references an inaccessible field

**Original actions**

1. the rule is saved

**Exact source oracles — all required**

1. it is rejected

Legacy same-requirement reuse candidates: `TC-FRM-002-01`, `TC-FRM-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
