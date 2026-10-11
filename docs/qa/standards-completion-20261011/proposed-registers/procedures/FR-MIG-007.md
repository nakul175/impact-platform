## QA v1.3 — source-bound case design (proposed)

Story `FR-MIG-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-MIG-007-001` / `TC-IMPRANA-FR-MIG-007-001` | `REV_9604d7c1bdb7508517afb70aeaf6cf4e7e3ee4a3e0d3170075d9301862ff6dee` / `REV_69d5fc848be1d7f0e4aee5a956427f56f7ddd9d06edf08e7fd08f783c0b84e77` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-007-002` / `TC-IMPRANA-FR-MIG-007-002` | `REV_c5f4b5787ad835f8cafe7e64f145f1ae8268c6d7b8e82b0419243c693cc84deb` / `REV_048d6825f673b27fa506e09277f352d8acf7268c47782ec668924cae4da68554` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-007-003` / `TC-IMPRANA-FR-MIG-007-003` | `REV_ff7df2d1795f7476d5c50f3c3e263f04628640c001eab408a43eeeea5f19e7ff` / `REV_773720bfb28b65051f41607582646e6655062d619387b070d1e83c7768c9f231` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-007-004` / `TC-IMPRANA-FR-MIG-007-004` | `REV_d97958c62d8311a2951a6967ef3a80109a6dcdc5108c3117fcf24815967d26d2` / `REV_bfd857a503d0322705a10d71cf821c31b4e6625393e21dcf612ef169daaf7fa1` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-MIG-007-001 — Reconstruct relationships outside the application

Source persona: Executive Director. Proposed fixture `FIX-FR-MIG-007-001` is not created. Verification duty `TASK-FR-MIG-007-03` (qualification); source `docs/backlog/backlog.csv` record 104, exact block `9604d7c1bdb7508517afb70aeaf6cf4e7e3ee4a3e0d3170075d9301862ff6dee`.

**Original preconditions**

1. a full tenant export package

**Original actions**

1. it is used outside the application

**Exact source oracles — all required**

1. programme-to-indicator-to-result-to-report relationships can be reconstructed
2. sample file integrity is verified

Legacy same-requirement reuse candidates: `TC-MIG-007-01`, `TC-MIG-007-02`, `TC-AT20`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_report_exports.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-007-002 — Manifest describes the export

Source persona: Executive Director. Proposed fixture `FIX-FR-MIG-007-002` is not created. Verification duty `TASK-FR-MIG-007-03` (qualification); source `docs/backlog/backlog.csv` record 104, exact block `c5f4b5787ad835f8cafe7e64f145f1ae8268c6d7b8e82b0419243c693cc84deb`.

**Original preconditions**

1. a completed tenant export

**Original actions**

1. the manifest is inspected

**Exact source oracles — all required**

1. it records counts, integrity references, exclusions and restoration instructions independent of internal infrastructure

Legacy same-requirement reuse candidates: `TC-MIG-007-01`, `TC-MIG-007-02`, `TC-AT20`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_report_exports.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-007-003 — Reject silent omission of secrets

Source persona: Executive Director. Proposed fixture `FIX-FR-MIG-007-003` is not created. Verification duty `TASK-FR-MIG-007-03` (qualification); source `docs/backlog/backlog.csv` record 104, exact block `ff7df2d1795f7476d5c50f3c3e263f04628640c001eab408a43eeeea5f19e7ff`.

**Original preconditions**

1. configuration containing secret values

**Original actions**

1. the export is built

**Exact source oracles — all required**

1. secret values are excluded
2. they are listed in the manifest as requiring reconfiguration

Legacy same-requirement reuse candidates: `TC-MIG-007-01`, `TC-MIG-007-02`, `TC-AT20`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_report_exports.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-007-004 — Reject bypassing sensitive content policy on exit

Source persona: Executive Director. Proposed fixture `FIX-FR-MIG-007-004` is not created. Verification duty `TASK-FR-MIG-007-03` (qualification); source `docs/backlog/backlog.csv` record 104, exact block `d97958c62d8311a2951a6967ef3a80109a6dcdc5108c3117fcf24815967d26d2`.

**Original preconditions**

1. an owner initiates exit

**Original actions**

1. the export reaches sensitive content

**Exact source oracles — all required**

1. access to that content remains policy governed

Legacy same-requirement reuse candidates: `TC-MIG-007-01`, `TC-MIG-007-02`, `TC-AT20`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_report_exports.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
