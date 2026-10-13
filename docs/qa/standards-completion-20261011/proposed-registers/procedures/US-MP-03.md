## QA v1.3 — source-bound case design (proposed)

Story `US-MP-03` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-MP-03-001` / `TC-IMPRANA-US-MP-03-001` | `REV_b30ed46623ead41d16f4f6a47c298c69ddeb434963450e40bd9d914a9187303e` / `REV_85a2f79e9ce90493d7f671b5a9ee3ac973ce635fc8a97207c1ea3fcc82583d08` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-MP-03-002` / `TC-IMPRANA-US-MP-03-002` | `REV_f5a83140c9ec30a4f45a0725251f26835af3bb412113cafcfdf4abf593ba87dc` / `REV_0ac38c23380bc18412c87de0c49781a6822445bd792c7729f3fcfe82d003c990` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-MP-03-003` / `TC-IMPRANA-US-MP-03-003` | `REV_c894589ce248726f1f20374ff568a2f737c50d1f2aa0b90f49778817b48f8803` / `REV_dd8d0522d95196554afab40637f1fd21d8ad5b3b84fc608e12fadb2fd2cd51fd` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-MP-03-001 — Opportunities ranked with scores

Source persona: Operations Head. Proposed fixture `FIX-US-MP-03-001` is not created. Verification duty `TASK-US-MP-03-03` (qualification); source `docs/backlog/backlog.csv` record 48, exact block `b30ed46623ead41d16f4f6a47c298c69ddeb434963450e40bd9d914a9187303e`.

**Original preconditions**

1. an organisation with mapped opportunities

**Original actions**

1. the Operations Head views the ranking

**Exact source oracles — all required**

1. the opportunities are listed in rank order
2. each shows its scores for impact, effort, cost and readiness

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_ranking.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-MP-03-002 — Adjust the ranking weights

Source persona: Operations Head. Proposed fixture `FIX-US-MP-03-002` is not created. Verification duty `TASK-US-MP-03-03` (qualification); source `docs/backlog/backlog.csv` record 48, exact block `f5a83140c9ec30a4f45a0725251f26835af3bb412113cafcfdf4abf593ba87dc`.

**Original preconditions**

1. the ranked list of opportunities

**Original actions**

1. the Operations Head changes the weights for impact, effort, cost and readiness

**Exact source oracles — all required**

1. the ranking is recalculated using the organisation's weights

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_ranking.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-MP-03-003 — Reject a ranking that ignores the organisation's weights

Source persona: Operations Head. Proposed fixture `FIX-US-MP-03-003` is not created. Verification duty `TASK-US-MP-03-03` (qualification); source `docs/backlog/backlog.csv` record 48, exact block `c894589ce248726f1f20374ff568a2f737c50d1f2aa0b90f49778817b48f8803`.

**Original preconditions**

1. the organisation has adjusted the weights

**Original actions**

1. the ranking is shown

**Exact source oracles — all required**

1. it does not use any weights other than the organisation's
2. no opportunity is ranked without its scores shown

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_ranking.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
