## QA v1.3 — source-bound case design (proposed)

Story `FR-AI-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-AI-001-001` / `TC-IMPRANA-FR-AI-001-001` | `REV_07b98caf49b671cd0d5a4b19e8930faa28c35b22bc4429a70140012b8861aff8` / `REV_f7063d9706ffa826b43d93acd0cf7ecb6f6804cbaae51d1666e54d7527632963` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-001-002` / `TC-IMPRANA-FR-AI-001-002` | `REV_519ed0f7cbd487a85d4f6fa6f3c006903236767d2669e54114746245d4cd11ce` / `REV_67e8dca1f2c385d6d4ed4337efe00170be5ac95e5553443967a83288f604a74e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-001-003` / `TC-IMPRANA-FR-AI-001-003` | `REV_838cf909324c0807839f96dbfc7c3cc4836194a3454ddb0f0f4fbd3a3a3313eb` / `REV_cb3d45c0ea9826b816ae61957da60d73f01c1772b17dbbef20297b0f5f3b962f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-001-004` / `TC-IMPRANA-FR-AI-001-004` | `REV_72694e8acfdece1d9db54bf3e41b872dd8faba82f489adc9d9a8eafe492a3e1a` / `REV_f994cd0299d27872e19b58929c9f8c65d455fe3264e67c4fb19c641dacfad8ae` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-AI-001-001 — Enable a named use case with its policy

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-AI-001-001` is not created. Verification duty `TASK-FR-AI-001-03` (qualification); source `docs/backlog/backlog.csv` record 8, exact block `07b98caf49b671cd0d5a4b19e8930faa28c35b22bc4429a70140012b8861aff8`.

**Original preconditions**

1. an Organisation Administrator configuring AI

**Original actions**

1. they enable a named use case with allowed data classes, destinations, language coverage, budget and required review

**Exact source oracles — all required**

1. only that use case is enabled
2. users see the active policy before making a request

Legacy same-requirement reuse candidates: `TC-AI-001-01`, `TC-AI-001-02`, `TC-AT28`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

**Inspected source assertion candidates — not verified binding**

- `qualification/test_ai_policy_unit.py::test_first_save_stores_version_1_with_exactly_that_use_case_and_audits` lines 455–471: Checks first policy save stores only the named use-case policy and audited revision. Gap: Source also requires users to see the active policy before request; this test alone does not prove that UI path.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-001-002 — Core workflows work with AI disabled

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-AI-001-002` is not created. Verification duty `TASK-FR-AI-001-03` (qualification); source `docs/backlog/backlog.csv` record 8, exact block `519ed0f7cbd487a85d4f6fa6f3c006903236767d2669e54114746245d4cd11ce`.

**Original preconditions**

1. AI is disabled for a tenant

**Original actions**

1. users complete programme setup, period close and report generation

**Exact source oracles — all required**

1. each completes using deterministic and manual workflows
2. no provider call is made

Legacy same-requirement reuse candidates: `TC-AI-001-01`, `TC-AI-001-02`, `TC-AT28`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_policy.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-001-003 — Reject transmission that fails policy

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-AI-001-003` is not created. Verification duty `TASK-FR-AI-001-03` (qualification); source `docs/backlog/backlog.csv` record 8, exact block `838cf909324c0807839f96dbfc7c3cc4836194a3454ddb0f0f4fbd3a3a3313eb`.

**Original preconditions**

1. a request for sensitive processing without an approved destination and purpose

**Original actions**

1. the request is submitted

**Exact source oracles — all required**

1. it is blocked before content leaves the authorised boundary

Legacy same-requirement reuse candidates: `TC-AI-001-01`, `TC-AI-001-02`, `TC-AT28`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

**Inspected source assertion candidates — not verified binding**

- `qualification/test_ai_policy_unit.py::test_gate_order_version_then_enablement_then_rules` lines 293–303: Checks policy gate refusal order for version, enablement and rules. Gap: Requires complete transmission-boundary/side-effect evidence; isolated unit gate is not proof that no provider received content.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-001-004 — Reject implicit enablement of tools

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-AI-001-004` is not created. Verification duty `TASK-FR-AI-001-03` (qualification); source `docs/backlog/backlog.csv` record 8, exact block `72694e8acfdece1d9db54bf3e41b872dd8faba82f489adc9d9a8eafe492a3e1a`.

**Original preconditions**

1. a chat interface has been enabled

**Original actions**

1. a user attempts to use a tool that was not separately enabled

**Exact source oracles — all required**

1. the tool is not available

Legacy same-requirement reuse candidates: `TC-AI-001-01`, `TC-AI-001-02`, `TC-AT28`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

**Inspected source assertion candidates — not verified binding**

- `qualification/test_ai_policy_unit.py::test_gate_names_every_unmet_rule_and_refuses_any_tool` lines 306–319: Checks named unmet policy rules and refusal of tools at the gate. Gap: Requires current chat/tool integration and authority path comparison, not merely gate-function presence.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
