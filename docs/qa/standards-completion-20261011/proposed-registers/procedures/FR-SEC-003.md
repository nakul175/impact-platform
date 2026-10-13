## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-003` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-003-001` / `TC-IMPRANA-FR-SEC-003-001` | `REV_fddb1984673fead328007f1114067333efa7ff9add2af879081d53f1e6398e97` / `REV_fe4392fb60234a14d5ed5d98eae549b74d626f8af9ca6f2b045c57635eb0a6dc` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-003-002` / `TC-IMPRANA-FR-SEC-003-002` | `REV_46e9b0e3e285d0cd2277e3ea20fa07ff093f8264325dcd6c2afa199f064f3f2a` / `REV_036aea7128a7d8e06873111d519d7feffec01d3d8c1d5d8974547a2ff63c55c3` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-003-003` / `TC-IMPRANA-FR-SEC-003-003` | `REV_b6f0b8d6a5cdf5690c87e534078a359db35d92d79bba7f236c60ba749898a9cb` / `REV_9638b3457ba64547b763430a2ac1dd32a6df5fbdc66c9a16593f053e67927c12` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-003-001 — Isolation fixtures run for tenancy changes

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-003-001` is not created. Verification duty `TASK-FR-SEC-003-02` (qualification); source `docs/backlog/backlog.csv` record 149, exact block `fddb1984673fead328007f1114067333efa7ff9add2af879081d53f1e6398e97`.

**Original preconditions**

1. a release affecting tenancy

**Original actions**

1. release checks run

**Exact source oracles — all required**

1. isolation fixtures cover records, attachments, async jobs, caches, search, AI and support
2. each fixture uses distinct synthetic tenant markers and principals with differing roles

Legacy same-requirement reuse candidates: `TC-SEC-003-01`, `TC-SEC-003-02`, `IT-003`, `IT-004`, `SEC-005`, `SEC-006`, `SEC-007`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

**Inspected source assertion candidates — not verified binding**

- `specification/reference-v1/tests/test_integration.py::test_IT_003` lines 8–8: Bounded tenant-route refusal assertion: tenant B programme request returns 404 RESOURCE_UNAVAILABLE. Gap: Preserved executable-reference case IT-003; no new execution or assertion-equivalence approval. This narrow API route assertion cannot satisfy all source channels (exports/search/cache/AI/support/async/database) by itself.
- `specification/reference-v1/tests/test_integration.py::test_IT_004` lines 9–9: Bounded cross-tenant object-under-route refusal assertion: B object under A context returns 404 RESOURCE_UNAVAILABLE. Gap: Reference source only; retain complete scenario-specific channels and then-outcomes as unmet until separately bound.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-003-002 — Cross tenant access attempts return nothing

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-003-002` is not created. Verification duty `TASK-FR-SEC-003-02` (qualification); source `docs/backlog/backlog.csv` record 149, exact block `46e9b0e3e285d0cd2277e3ea20fa07ff093f8264325dcd6c2afa199f064f3f2a`.

**Original preconditions**

1. another tenant's artifact carrying a synthetic marker

**Original actions**

1. a user guesses its reference, requests it through a background job and asks AI for its contents

**Exact source oracles — all required**

1. no path returns the synthetic marker

Legacy same-requirement reuse candidates: `TC-SEC-003-01`, `TC-SEC-003-02`, `IT-003`, `IT-004`, `SEC-005`, `SEC-006`, `SEC-007`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

**Inspected source assertion candidates — not verified binding**

- `specification/reference-v1/tests/test_integration.py::test_IT_003` lines 8–8: Bounded tenant-route refusal assertion: tenant B programme request returns 404 RESOURCE_UNAVAILABLE. Gap: Preserved executable-reference case IT-003; no new execution or assertion-equivalence approval. This narrow API route assertion cannot satisfy all source channels (exports/search/cache/AI/support/async/database) by itself.
- `specification/reference-v1/tests/test_integration.py::test_IT_004` lines 9–9: Bounded cross-tenant object-under-route refusal assertion: B object under A context returns 404 RESOURCE_UNAVAILABLE. Gap: Reference source only; retain complete scenario-specific channels and then-outcomes as unmet until separately bound.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-003-003 — Reject release on isolation failure

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-003-003` is not created. Verification duty `TASK-FR-SEC-003-02` (qualification); source `docs/backlog/backlog.csv` record 149, exact block `b6f0b8d6a5cdf5690c87e534078a359db35d92d79bba7f236c60ba749898a9cb`.

**Original preconditions**

1. an isolation fixture that exposes another tenant's data

**Original actions**

1. the release is evaluated

**Exact source oracles — all required**

1. the finding records the specific exposed path
2. the affected release is blocked even if ordinary workflows succeed
3. shared infrastructure or reused cache entries do not imply shared authorisation

Legacy same-requirement reuse candidates: `TC-SEC-003-01`, `TC-SEC-003-02`, `IT-003`, `IT-004`, `SEC-005`, `SEC-006`, `SEC-007`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

**Inspected source assertion candidates — not verified binding**

- `specification/reference-v1/tests/test_integration.py::test_IT_003` lines 8–8: Bounded tenant-route refusal assertion: tenant B programme request returns 404 RESOURCE_UNAVAILABLE. Gap: Preserved executable-reference case IT-003; no new execution or assertion-equivalence approval. This narrow API route assertion cannot satisfy all source channels (exports/search/cache/AI/support/async/database) by itself.
- `specification/reference-v1/tests/test_integration.py::test_IT_004` lines 9–9: Bounded cross-tenant object-under-route refusal assertion: B object under A context returns 404 RESOURCE_UNAVAILABLE. Gap: Reference source only; retain complete scenario-specific channels and then-outcomes as unmet until separately bound.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
