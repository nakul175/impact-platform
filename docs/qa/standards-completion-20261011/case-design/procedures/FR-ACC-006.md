## QA v1.3 — source-bound case design (proposed)

Story `FR-ACC-006` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ACC-006-001` / `TC-IMPRANA-FR-ACC-006-001` | `REV_e2aba4b277c7d76f32fbfe8ecf537f7c5935722c92f4db3bb58a15f22e0a7e6f` / `REV_ce8dad06df0e0367c5c150c70cfae18e86eb5b136fcadf7909fd50873992fa0f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-006-002` / `TC-IMPRANA-FR-ACC-006-002` | `REV_f2bbb5585f63fb03919abc55a053ea570ff2e04daf6e1f96853ac990a4f5f9b7` / `REV_33a3e7d352a186ae06157aecf2766eacd5db51c3f0ea8d524da0c2bc5823a747` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-006-003` / `TC-IMPRANA-FR-ACC-006-003` | `REV_a47144de659ab8fc95ae595378df4fd34f028f0315100dded54260c4cfa1c795` / `REV_d61b0b0474ab41c66c7bad27ec0efe1928aba79cbee0b2982ccb9221a7d29b7a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-006-004` / `TC-IMPRANA-FR-ACC-006-004` | `REV_5caafefd803e37756d91768d2c982038612b31dd3fb0aff43ad30ff1875124a7` / `REV_7543a10e7170fd85de1ec60ae536f56a64dfccea27417c28b7b00d3958b5ebce` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-006-005` / `TC-IMPRANA-FR-ACC-006-005` | `REV_42a5a67c3444e58ba59ecf80063571ed7d8257ffa3cd60d15a584dd281f1b8c0` / `REV_4610f3761ee67ea8e5107808aff0178a9ec3a8780b2593f71985101727f47f70` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ACC-006-001 — Create a share

Source persona: MEL Manager. Proposed fixture `FIX-FR-ACC-006-001` is not created. Verification duty `TASK-FR-ACC-006-03` (qualification); source `docs/backlog/backlog.csv` record 24, exact block `e2aba4b277c7d76f32fbfe8ecf537f7c5935722c92f4db3bb58a15f22e0a7e6f`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the MEL Manager shares an artifact

**Exact source oracles — all required**

1. they must specify the artifact version, audience, permitted actions, owner, reason and expiry
2. the preview uses the intended recipient's effective view
3. authenticated external access is the default

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-006-01`, `TC-ACC-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-006-002 — Limit public links

Source persona: MEL Manager. Proposed fixture `FIX-FR-ACC-006-002` is not created. Verification duty `TASK-FR-ACC-006-03` (qualification); source `docs/backlog/backlog.csv` record 24, exact block `f2bbb5585f63fb03919abc55a053ea570ff2e04daf6e1f96853ac990a4f5f9b7`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a public link is requested

**Exact source oracles — all required**

1. it is allowed only for approved public artifacts

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-006-01`, `TC-ACC-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-006-003 — Revalidate on classification change

Source persona: MEL Manager. Proposed fixture `FIX-FR-ACC-006-003` is not created. Verification duty `TASK-FR-ACC-006-03` (qualification); source `docs/backlog/backlog.csv` record 24, exact block `a47144de659ab8fc95ae595378df4fd34f028f0315100dded54260c4cfa1c795`.

**Original preconditions**

1. an artifact has existing disclosures

**Original actions**

1. its classification changes

**Exact source oracles — all required**

1. existing disclosures are revoked or revalidated

Legacy same-requirement reuse candidates: `TC-ACC-006-01`, `TC-ACC-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-006-004 — Reject access after revocation

Source persona: MEL Manager. Proposed fixture `FIX-FR-ACC-006-004` is not created. Verification duty `TASK-FR-ACC-006-03` (qualification); source `docs/backlog/backlog.csv` record 24, exact block `5caafefd803e37756d91768d2c982038612b31dd3fb0aff43ad30ff1875124a7`.

**Original preconditions**

1. a seven day report link has been issued

**Original actions**

1. the MEL Manager revokes it after one day

**Exact source oracles — all required**

1. old URLs and generated download references cease serving the artifact

Legacy same-requirement reuse candidates: `TC-ACC-006-01`, `TC-ACC-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-006-005 — Reject link possession as authorisation

Source persona: MEL Manager. Proposed fixture `FIX-FR-ACC-006-005` is not created. Verification duty `TASK-FR-ACC-006-03` (qualification); source `docs/backlog/backlog.csv` record 24, exact block `42a5a67c3444e58ba59ecf80063571ed7d8257ffa3cd60d15a584dd281f1b8c0`.

**Original preconditions**

1. a link to sensitive data or an expired link

**Original actions**

1. someone opens it

**Exact source oracles — all required**

1. link possession alone does not authorise the sensitive data
2. an expired link shows unavailable without an artifact preview

Legacy same-requirement reuse candidates: `TC-ACC-006-01`, `TC-ACC-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
