## QA v1.3 — source-bound case design (proposed)

Story `US-FP-03` · 2 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-FP-03-001` / `TC-IMPRANA-US-FP-03-001` | `REV_4653fea244fd4dfb26985175caba1720b22fccb03b431f4bd5f34859056f364e` / `REV_5bc1e82b54d5d7d9166f816af61115a34f0b17bb597fb1b7fb30cb7ee0929b10` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-FP-03-002` / `TC-IMPRANA-US-FP-03-002` | `REV_a1d6fc2d56b8d0510e9787768c2118ee032443dbc40eb7602dfe04fd1fbb97e6` / `REV_58cace31ccb0912705f7b95cd56584d5d9d3194af437144e267dc1473912ae73` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-FP-03-001 — Export a portfolio impact report

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-US-FP-03-001` is not created. Verification duty `TASK-US-FP-03-03` (qualification); source `docs/backlog/backlog.csv` record 82, exact block `4653fea244fd4dfb26985175caba1720b22fccb03b431f4bd5f34859056f364e`.

**Original preconditions**

1. a portfolio with shared grantee data

**Original actions**

1. the Funder Portfolio Manager exports the impact report

**Exact source oracles — all required**

1. the report includes its methodology and data sources

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-FP-03-002 — Reject a report without methodology or sources

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-US-FP-03-002` is not created. Verification duty `TASK-US-FP-03-03` (qualification); source `docs/backlog/backlog.csv` record 82, exact block `a1d6fc2d56b8d0510e9787768c2118ee032443dbc40eb7602dfe04fd1fbb97e6`.

**Original preconditions**

1. a portfolio impact report

**Original actions**

1. its methodology or data sources are missing

**Exact source oracles — all required**

1. the report is not accepted

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
