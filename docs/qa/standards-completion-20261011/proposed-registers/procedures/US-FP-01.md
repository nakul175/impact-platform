## QA v1.3 — source-bound case design (proposed)

Story `US-FP-01` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-FP-01-001` / `TC-IMPRANA-US-FP-01-001` | `REV_971fd18521dfdd740f306e8a50737c3e2a00531e2dcd060f935e42696504f4c8` / `REV_8d94c94ab92a0662226539736c0a999f7b6b437e582067a79526a68b2bd13b87` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-FP-01-002` / `TC-IMPRANA-US-FP-01-002` | `REV_bdbae9adf403f2ce3305ddbec6c92eb3a1304fbcc17ded17f4ccea4b7ca58149` / `REV_e4e29c46a918df63346f67f2c796aa912363f279194a3f079011323c657f9f3f` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-FP-01-003` / `TC-IMPRANA-US-FP-01-003` | `REV_bd37ae2a145d9c38201518464347d07d6953054170bdb7c0033269f28b703400` / `REV_7ca3d7be3fad7b6ef0142119264805389345f0443832f060841488004a30b777` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-FP-01-001 — Bulk invite grantees to a cohort

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-US-FP-01-001` is not created. Verification duty `TASK-US-FP-01-03` (qualification); source `docs/backlog/backlog.csv` record 81, exact block `971fd18521dfdd740f306e8a50737c3e2a00531e2dcd060f935e42696504f4c8`.

**Original preconditions**

1. a Funder Portfolio Manager with a list of grantee organisations

**Original actions**

1. they invite them to a cohort in one bulk action

**Exact source oracles — all required**

1. each organisation receives an invitation

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-FP-01-002 — Cohort status view

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-US-FP-01-002` is not created. Verification duty `TASK-US-FP-01-03` (qualification); source `docs/backlog/backlog.csv` record 81, exact block `bdbae9adf403f2ce3305ddbec6c92eb3a1304fbcc17ded17f4ccea4b7ca58149`.

**Original preconditions**

1. a cohort with invited grantees

**Original actions**

1. the Funder Portfolio Manager opens the cohort status view

**Exact source oracles — all required**

1. the status of each grantee in the cohort is shown

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-FP-01-003 — Reject organisations outside the cohort

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-US-FP-01-003` is not created. Verification duty `TASK-US-FP-01-03` (qualification); source `docs/backlog/backlog.csv` record 81, exact block `bd37ae2a145d9c38201518464347d07d6953054170bdb7c0033269f28b703400`.

**Original preconditions**

1. an organisation not enrolled in the Funder Portfolio Manager's cohort

**Original actions**

1. they open the cohort status view

**Exact source oracles — all required**

1. that organisation is not shown

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
