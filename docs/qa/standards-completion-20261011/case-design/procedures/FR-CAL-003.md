## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-003-001` / `TC-IMPRANA-FR-CAL-003-001` | `REV_b1e3e4e4c3b604915adb83c2592c5fd3ec54ecca5fb31d9ecbdd836bfba465cc` / `REV_43bb384dbefd79a967a52e7e3f893d0b3fd038ca97dfc4cf0929e7f7a55a8a13` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-003-002` / `TC-IMPRANA-FR-CAL-003-002` | `REV_1ee819def8704f814cd2031ab6f8741e694106feb65f7d9f4e021d8c13b91de8` / `REV_ee556435b419260341bbf082630e660f662f6f2c37a9edf2aee66c90f8013901` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-003-003` / `TC-IMPRANA-FR-CAL-003-003` | `REV_5936330567e4e85b11f260c6a1f575b6f03fd358466a2649f87a8bbdd779e872` / `REV_4514bb221c3df8e52712a5fc4bd835c1feb324ae0f7afc37b5c3b9d117553f92` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-003-004` / `TC-IMPRANA-FR-CAL-003-004` | `REV_35eb68fd39fad20ae7956801b331c96b526ef65b5702f7c882a5ed719ffccd8d` / `REV_73f5fa9d75f92ad4192f4de97a0e8fa735ea1066d485538f0a4710362c6ea891` | unit → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-003-001 — Pool two ratios

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-003-001` is not created. Verification duty `TASK-FR-CAL-003-03` (qualification); source `docs/backlog/backlog.csv` record 56, exact block `b1e3e4e4c3b604915adb83c2592c5fd3ec54ecca5fb31d9ecbdd836bfba465cc`.

**Original preconditions**

1. components of 50 of 100 and 1 of 10

**Original actions**

1. the Analyst pools them

**Exact source oracles — all required**

1. the result is 51 of 110
2. it displays 46.36 percent under two decimal rounding
3. the weighting basis is disclosed

Legacy same-requirement reuse candidates: `TC-CAL-003-01`, `TC-CAL-003-02`, `TC-AT01`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-003-002 — Unweighted mean is a separate statistic

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-003-002` is not created. Verification duty `TASK-FR-CAL-003-03` (qualification); source `docs/backlog/backlog.csv` record 56, exact block `1ee819def8704f814cd2031ab6f8741e694106feb65f7d9f4e021d8c13b91de8`.

**Original preconditions**

1. an explicitly requested unweighted mean

**Original actions**

1. it is calculated

**Exact source oracles — all required**

1. it is labelled as a different statistic from the pooled percentage

Legacy same-requirement reuse candidates: `TC-CAL-003-01`, `TC-CAL-003-02`, `TC-AT01`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-003-003 — Reject averaging percentages

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-003-003` is not created. Verification duty `TASK-FR-CAL-003-03` (qualification); source `docs/backlog/backlog.csv` record 56, exact block `5936330567e4e85b11f260c6a1f575b6f03fd358466a2649f87a8bbdd779e872`.

**Original preconditions**

1. components of 50 of 100 and 1 of 10

**Original actions**

1. a pooled percentage is produced

**Exact source oracles — all required**

1. it is never 30 percent
2. a component lacking the necessary quantities does not contribute as if its percentage were sufficient

Legacy same-requirement reuse candidates: `TC-CAL-003-01`, `TC-CAL-003-02`, `TC-AT01`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-003-004 — Reject a number for a zero denominator

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-003-004` is not created. Verification duty `TASK-FR-CAL-003-03` (qualification); source `docs/backlog/backlog.csv` record 56, exact block `35eb68fd39fad20ae7956801b331c96b526ef65b5702f7c882a5ed719ffccd8d`.

**Original preconditions**

1. a pooled denominator of zero

**Original actions**

1. the ratio is calculated

**Exact source oracles — all required**

1. the result is UNDEFINED

Legacy same-requirement reuse candidates: `TC-CAL-003-01`, `TC-CAL-003-02`, `TC-AT01`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
