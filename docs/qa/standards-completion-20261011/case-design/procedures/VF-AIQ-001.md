## QA v1.3 — source-bound case design (proposed)

Story `VF-AIQ-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-AIQ-001-001` / `TC-IMPRANA-VF-AIQ-001-001` | `REV_f247c1b218e7b03a6f3b2f686b55a518e1021472b38cc460679941cbedd40931` / `REV_37ff7cfa923ce9e70a3bb17a796ba6a426e1322f48369bdf31f02b17dd1adc7b` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-AIQ-001-002` / `TC-IMPRANA-VF-AIQ-001-002` | `REV_be74bc49df223428b418a2da6c2706dfc9e3ac6fd5be5d83bbe31cde0b8dc67c` / `REV_0193a24ad74cd74ac3193112893d8a7a8e2d3817cdf107a3232c8af18cce9dca` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-AIQ-001-003` / `TC-IMPRANA-VF-AIQ-001-003` | `REV_e3c7528ab7fc2b907d3bcfdcaa4403ccfc5163694246a20ed5a9b411a181456a` / `REV_be75a9d719589730ee88081a0b9d7e2a0cc82e49f3c193d6726b580ca2cf0bdf` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-AIQ-001-001 — Held-out set meets size and difficulty requirements

Source persona: Product Owner. Proposed fixture `FIX-VF-AIQ-001-001` is not created. Verification duty `TASK-VF-AIQ-001-03` (qualification); source `docs/backlog/backlog.csv` record 105, exact block `f247c1b218e7b03a6f3b2f686b55a518e1021472b38cc460679941cbedd40931`.

**Original preconditions**

1. an enabled AI use case

**Original actions**

1. its held-out evaluation set is reviewed

**Exact source oracles — all required**

1. it has at least 200 representative cases where feasible
2. at least 20 percent are boundary, unsupported or adversarial cases
3. it is separate from tuning

Legacy same-requirement reuse candidates: `TC-VF-AIQ-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_policy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AIQ-001-002 — Language and sector coverage is evidenced

Source persona: Product Owner. Proposed fixture `FIX-VF-AIQ-001-002` is not created. Verification duty `TASK-VF-AIQ-001-03` (qualification); source `docs/backlog/backlog.csv` record 105, exact block `be74bc49df223428b418a2da6c2706dfc9e3ac6fd5be5d83bbe31cde0b8dc67c`.

**Original preconditions**

1. a released language and sector

**Original actions**

1. evaluation coverage is reviewed

**Exact source oracles — all required**

1. explicit coverage evidence exists for it

Legacy same-requirement reuse candidates: `TC-VF-AIQ-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_policy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AIQ-001-003 — Reject unjustified small sets or paraphrase padding

Source persona: Product Owner. Proposed fixture `FIX-VF-AIQ-001-003` is not created. Verification duty `TASK-VF-AIQ-001-03` (qualification); source `docs/backlog/backlog.csv` record 105, exact block `e3c7528ab7fc2b907d3bcfdcaa4403ccfc5163694246a20ed5a9b411a181456a`.

**Original preconditions**

1. a specialist evaluation set below the required case count

**Original actions**

1. it has no documented justification, named risk decision and scope limitation

**Exact source oracles — all required**

1. the set is rejected
2. duplicated paraphrases are not counted as representative task coverage

Legacy same-requirement reuse candidates: `TC-VF-AIQ-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_policy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
