## QA v1.3 — source-bound case design (proposed)

Story `VF-PER-002` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-PER-002-001` / `TC-IMPRANA-VF-PER-002-001` | `REV_12eb9b2bb9b2a32d9db2567b46d4a43379e34b14a921b4e8afc27d8091cc3027` / `REV_4b4b83d551c36a90025f39c68552dcbcfbb04c8b5ff9dcf49f3ffca9dd6f2a88` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-002-002` / `TC-IMPRANA-VF-PER-002-002` | `REV_17bd260f3c78b3d472c2132123c863d67c26d1922d2d180ef4bcf4ddc9cd9c95` / `REV_955d31f93e619a199bea514291816454ff13f72ddbedfe3644ba803f5d221843` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-002-003` / `TC-IMPRANA-VF-PER-002-003` | `REV_afd19f6d3118a1425944145bbaa2b638fd8ddcaebe77ef781aa105e43f16e70b` / `REV_a26eed3745fcc7568856aeb666c7ee8090b24a5270139ef947c554cd522c03f9` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-PER-002-001 — Ten-widget dashboard meets response targets

Source persona: Analyst. Proposed fixture `FIX-VF-PER-002-001` is not created. Verification duty `TASK-VF-PER-002-02` (qualification); source `docs/backlog/backlog.csv` record 266, exact block `12eb9b2bb9b2a32d9db2567b46d4a43379e34b14a921b4e8afc27d8091cc3027`.

**Original preconditions**

1. a standard dashboard of up to ten widgets with approved bounded calculations
2. imports and report jobs are running

**Original actions**

1. initial opening, filter change and drill down are measured with cold and warm caches as separate populations

**Exact source oracles — all required**

1. the dashboard becomes usable at p95 within 5 seconds and p99 within 10 seconds
2. cached and uncached results are reported separately
3. data bindings, freshness and calculation status remain visible and correct

Legacy same-requirement reuse candidates: `TC-VF-PER-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-002-002 — Reject placeholders as usable completion

Source persona: Analyst. Proposed fixture `FIX-VF-PER-002-002` is not created. Verification duty `TASK-VF-PER-002-02` (qualification); source `docs/backlog/backlog.csv` record 266, exact block `17bd260f3c78b3d472c2132123c863d67c26d1922d2d180ef4bcf4ddc9cd9c95`.

**Original preconditions**

1. a widget showing a placeholder or partially loaded chart

**Original actions**

1. completion is timed

**Exact source oracles — all required**

1. it is not counted as usable completion
2. failed widgets are recorded rather than excluded from the samples

Legacy same-requirement reuse candidates: `TC-VF-PER-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-002-003 — Reject dashboards outside the bound

Source persona: Analyst. Proposed fixture `FIX-VF-PER-002-003` is not created. Verification duty `TASK-VF-PER-002-02` (qualification); source `docs/backlog/backlog.csv` record 266, exact block `afd19f6d3118a1425944145bbaa2b638fd8ddcaebe77ef781aa105e43f16e70b`.

**Original preconditions**

1. the measured results

**Original actions**

1. p95 exceeds 5 seconds or p99 exceeds 10 seconds

**Exact source oracles — all required**

1. the verification fails

Legacy same-requirement reuse candidates: `TC-VF-PER-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
