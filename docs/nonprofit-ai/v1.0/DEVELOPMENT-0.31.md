# Development increment 0.31: nonprofit planning

5 October 2026 · Build 0.31.0 review candidate · domain API 1.22.0 · platform API 1.9.0 · schema 35.

This is the implementation and qualification appendage to the **proposed edition 1.0** BRD → FSD → HLD → LLD baseline. Those documents, their editable copies, requirement registry, traceability/data CSVs and 108 specified case statuses retain their original build-0.30.0 reference point. The user authorized development; no design signoff, requirement acceptance, spending commitment or deployment is recorded. The complete increment and reproduction commands are in the [release note](../../RELEASE-0.31-nonprofit-ai-planning.md).

## Current increment and retained target

The integrated source adds deterministic cost estimates, sample-aware pilot time comparisons, manual practice worksheets and stable lesson identifiers. It extends ordinary saved adoption drafts with optional source inputs and content compatibility information. Advisory request/body transfer is bounded more strongly. These subsets are locally built and tested; their exact evidence and remaining qualification limits are recorded below.

The operated marketplace, adviser/procurement decisions, competency assessment, governed service delivery, connectors, monetary budgets, AI-specific retention and conditional payments remain target design. The original 307 impact requirements retain 113 PARTIAL, 194 PENDING and zero accepted. None of the nonprofit requirements below is promoted to accepted, and no target case is marked passed by resemblance to an automated check.

## Ten development streams

Each stream has an isolated code/document responsibility. Four active runtime slots include the root integrator; the ten streams ran in parallel waves. This is a ten-agent work allocation, not a claim that ten agents executed simultaneously.

| Stream | Agent | Implemented responsibility | Qualification state at this record |
|---|---|---|---|
| 1 | `dev_learning` | Stable semantic lesson keys, fixed legacy aliases, read-time content compatibility and version warnings | Complete within local scope; focused/unit and local browser support recorded |
| 2 | `dev_costing` | Exact supplied whole-cost calculations with incomplete totals and preserved ties | Complete within local scope; unit, API and real local-browser support recorded |
| 3 | `dev_outcomes` | Source-preserving sample/time comparison including human review; explicit undefined/draft states | Complete within local scope; unit, API and real local-browser support recorded |
| 4 | `dev_practice` | Four versioned manual worksheets, input boundaries, preserved unavailable drafts and edition warnings | Complete within local scope; unit/API support and explicitly simulated compatibility browser projections |
| 5 | `dev_planning_ui` | Cost and pilot input/calculation components and interaction recovery | Complete within local scope; 16 component checks plus separate real local-workspace coverage |
| 6 | `dev_workspace` | Parent workspace, saved source-input roundtrip, stable progress and practice section | Complete within local scope; real save/reopen, retry, conflict and read-only browser support |
| 7 | `dev_provider` | Cancellable request/body I/O deadline and 256 KiB uncompressed response cap | Complete within mock-I/O scope; no paid/live provider or hard process-wide deadline claim |
| 8 | `dev_security_tests` | API/database negative cases, current authority, closed input and atomic saved drafts | Complete within local scope; 49 focused API passes, including one added after the full run |
| 9 | `dev_browser` | Real local API/database workspace browser smoke/regression and accessibility scans | Complete within local scope; twenty new groups and ten rebuilt baseline groups passed, with the incomplete baseline contrast check retained |
| 10 | `dev_release_docs` | Release/development record, implementation boundary, user guide and API/index documentation | Complete source-grounded local implementation/evidence record; no acceptance or deployment |
| Integration | Root | Versions, generated contracts, wiring, runners, combined review and final qualification | Local integration complete with seven unchanged Mac failures; hosted/native/UAT gates outstanding |

## Requirement and specified-case support

The following is a **partial implementation support map**, not a case-execution or acceptance register. `TC-NPA-*` identifiers reference the unchanged [specified case catalogue](06-TEST-SCENARIOS-AND-CASES.md). New automated tests are named separately so that future formal execution can use them as supporting evidence without inventing case outcomes.

| Requirements | Added supporting implementation | Related specified cases | Named automated sources | Remaining requirement scope |
|---|---|---|---|---|
| FR-NPA-006, FR-NPA-027, FR-NPA-039 | Save original planning inputs together, retain immutable revisions, exact retry and current authority | TC-NPA-011, TC-NPA-012, TC-NPA-077, TC-NPA-078, TC-NPA-097 | `test_ai_planning_inputs.py`; `test_ai_planning_live.py::test_planning_snapshot_save_reload_exact_retry_changed_input_and_stale_edit_are_atomic`; `test_ai_planning_live.py::test_read_only_actor_can_compute_and_practise_but_cannot_save_or_update_inputs` | Formal full-case execution, native contention and crash/recovery evidence |
| FR-NPA-007, FR-NPA-038 | Preserve lesson meaning through fixed aliases; expose stale/unknown guide compatibility without rewriting old revisions | TC-NPA-013, TC-NPA-014, TC-NPA-075, TC-NPA-076 | `test_ai_learning_content.py`; `test_ai_planning_inputs.py::test_reading_an_old_plan_does_not_backfill_inputs_or_mutate_its_revision` | Human accessibility/learning validation; historical content archive remains absent |
| FR-NPA-012, FR-NPA-035 | Four manual task worksheets, safe input boundaries and recorded self-checks | TC-NPA-023, TC-NPA-024, TC-NPA-069, TC-NPA-070 | `test_ai_task_practice.py`; `test_ai_planning_live.py::test_task_templates_api_returns_four_versioned_manual_exercises_without_execution_or_approval` | Approved template governance, generated runs and independent review ownership; a manual worksheet does not execute TC-NPA-023 |
| FR-NPA-013, FR-NPA-015 | Supplied source amounts, separate cost categories, exact totals, unknown amounts and one currency | TC-NPA-025, TC-NPA-026, TC-NPA-029, TC-NPA-030 | `test_ai_procurement_costs.py`; `test_ai_planning_live.py::test_cost_api_preserves_unknown_exit_cost_even_with_zero_quantity_and_does_not_pick_a_winner`; `test_ai_planning_live.py::test_cost_api_uses_exact_decimal_products_and_preserves_equal_total_ties` | Quote provenance/dates, operated RFQs, supplier verification, award approval and commercial policy |
| FR-NPA-021, FR-NPA-024 | Draft baseline/pilot sample counts and review effort, explicit comparability and source retention | TC-NPA-041, TC-NPA-042, TC-NPA-047, TC-NPA-048 | `test_ai_pilot_outcomes.py`; `test_ai_planning_live.py::test_pilot_api_retains_source_counts_and_marks_comparability_without_official_outcomes` | Measurement periods, verified quality/evidence, independent milestone acceptance and official measurement links |
| FR-NPA-025, FR-NPA-037, FR-NPA-039 | Current tenant/read authority on deterministic tools; closed nested source inputs; no client approval/result/version fields | TC-NPA-049, TC-NPA-050, TC-NPA-073, TC-NPA-074, TC-NPA-077, TC-NPA-078, TC-NPA-089 | `test_ai_planning_live.py::test_planning_tools_recheck_current_read_authority_for_every_request`; `test_ai_planning_live.py::test_invalid_saved_planning_inputs_leave_no_head_revision_audit_outbox_or_receipt` | Native role/concurrency gates, independent security assessment and full-case execution |
| FR-NPA-010, FR-NPA-023, FR-NPA-029 | Uncompressed response-byte ceiling and one cancellable request/body I/O deadline; deterministic tools avoid provider calls | TC-NPA-045, TC-NPA-046, TC-NPA-057, TC-NPA-058, TC-NPA-095 | `test_ai_advisory_provider.py`; `test_ai_planning_live.py::test_authorized_planning_never_inspects_or_calls_an_enabled_provider` | Funded/live provider evaluation, money/token budgets, process-wide hard deadline and crash/inflight recovery |
| FR-NPA-028, FR-NPA-040 | Integrated screens, local browser evidence and reproducible smoke sequence | TC-NPA-081, TC-NPA-083, TC-NPA-097, TC-NPA-104, TC-NPA-106 | `tools/browser/ai-planning-check.mjs`; `tools/browser/ai-enablement-check.mjs` | Twenty new groups and ten baseline groups passed; one incomplete contrast check, manual assistive-technology review, hosted gates and UAT remain outstanding |

TC-NPA-046 (monetary/token budget), TC-NPA-042 (independent pilot acceptance), TC-NPA-091/092 (native races), TC-NPA-098/099 (crash/restore) and operated R2/R3 cases are not fulfilled by this increment. Related implementation does not remove an open decision in [11-DECISIONS-AND-RISKS.md](11-DECISIONS-AND-RISKS.md).

## Source-input and data model appendage

These fields extend the local implementation; the edition-1.0 dictionary remains its original reference rather than being relabelled current in place. No SQL table or migration is added.

| Object / field | Type and limits | Ownership / persistence |
|---|---|---|
| `AIAdoptionPlanData.planning` | Optional closed object; when present all three nullable source keys are required | Client source inputs, validated and stored in the existing immutable plan payload |
| `.cost_comparison` | Currency `[A-Z]{3}`; integer months 1–60; 1–4 offers; 1–20 lines per offer | Original decimal strings retained; computed totals are not stored |
| Cost amount / quantity | Nonnegative ordinary decimal string; up to 26 integer and 12 fractional digits; amount may be null | Null is unknown, including at zero quantity; no client computed result accepted |
| Cost offer/line identifiers | Known-shape slug, max 64 characters; unique within their respective collection | Client identifiers only, never authority or verified supplier identity |
| `.pilot_evaluation` | Task label max 150; notes max 1,000; boolean comparability; baseline and pilot each have sample size 1–10,000 and correction count 0–1,000,000 | Self-reported source counts and decimal minute strings stored unchanged |
| `.task_practice` | Known template ID; brief/draft/review notes each max 2,500; up to 10 distinct known checked steps | One manual worksheet, not approval/certification or generated output |
| `data.content_versions.practice` | Server-owned current editorial practice version when a worksheet is explicitly supplied | Exact replay and older-client omission preserve the original stamp with any retained worksheet |
| `content_compatibility` | Current guide versions, CURRENT/STALE/UNKNOWN status, canonical completion, legacy/unavailable keys, `historical_snapshots_available:false` | Computed on read; not an archived guide or a revision rewrite |
| Cost result | Exact nonnegative subtotal/complete-total strings; nullable complete total; missing line IDs and tied minimum IDs | Temporary deterministic response; absent costs exclude a complete claim |
| Pilot result | `SELF_REPORTED_DRAFT`, source inputs, per-item measures rounded once to at most six decimals, DEFINED/UNDEFINED improvement | Temporary deterministic response; zero baseline and incomparable samples remain undefined |

All fields remain organisation working notes visible under plan read scope. Use invented or permitted non-sensitive material; do not enter beneficiary data, credentials or private case files. The existing plan privacy/retention gaps remain open. Advisory sends only the submitted organisation brief and deterministic assessment; it does not join these saved cost/pilot/practice fields or platform records into a provider request.

Backward-compatible updates preserve optional source snapshots when an older client omits the whole `planning` object. A client that supplies it explicitly can clear members with null. This distinction prevents silent source-input loss; it does not reinterpret old revisions or restamp retained practice content as current.

The workspace also keeps retired learning entries in the editable draft rather than filtering them away. A user must review and explicitly remove unavailable progress before a new save; the original revision is retained.

Practice compatibility follows the same preservation principle. If a saved template is unavailable, its exact brief, draft, review notes and raw checked-step identifiers remain visible read-only. A manager can deliberately choose a current replacement, retain all three texts and reset checks, or explicitly clear the worksheet; read-only colleagues cannot replace or clear it. The parent save guard refuses unresolved unavailable practice. Current/Stale/Unknown practice-edition labels distinguish saved metadata from the current guide; no historical wording archive is claimed.

## Evidence and release gates

The [local evidence summary and manifest](../../evidence/nonprofit-ai-planning-local-summary.json) ties the recorded runs to source/evidence hashes before the increment commit. It does not present a later commit as already qualified.

Final focused support: **469 passed and one skipped across eleven files**, recorded in [nonprofit-ai-planning-unit-tests.xml](../../evidence/nonprofit-ai-planning-unit-tests.xml). The skipped identity is `test_ai_enablement.py::test_native_advisory_tables_force_rls_and_narrow_application_grants`, which requires native PostgreSQL. The preserved [reference suite](../../evidence/nonprofit-ai-planning-reference-tests.json) records **143 passes**, with `product_validated:false`. Ruff check and format across 198 files, scoped Prettier across six touched web files, and TypeScript/Vite build passed. The existing bundle warning above 500 KiB remains. Sixteen synthetic planning-component checks are separately reported support.

The [full local application run](../../evidence/nonprofit-ai-planning-local-suite.xml) records **1,495 passed, seven failed, 76 skipped and one deselected** in 177.98 seconds, including all 48 then-existing planning-live checks passed. The seven operations-test failure identities exactly match the named [0.30 Mac baseline](../../evidence/nonprofit-ai-adoption-local-suite.xml); no new failure identities were observed. This remains a failed overall gate. The older generic `application-tests.xml` is a different Linux-green baseline and is not the comparison source.

The later [focused API run](../../evidence/nonprofit-ai-planning-focused-api.xml) records **49 passed, zero failed/skipped** in 1.52 seconds. It includes `test_older_six_field_update_preserves_planning_and_explicit_nulls_clear_only_the_new_revision`, added after the full run, covering real API legacy omission, explicit clearing, exact retries and retained revision history. The 49 overlaps the earlier 48; it is not 49 extra application passes.

The [new planning-browser record](../../evidence/nonprofit-ai-planning-browser-tests.json) reports **twenty groups passed**, eight axe scans with zero violations/incomplete, zero uncaught JavaScript errors and zero advisory requests, using Chrome 154.0.8037.97 on macOS with real FastAPI/PGlite. Four historical-read projections are explicitly simulated; their surrounding calculations and saved-plan operations are real. Selected actual desktop/mobile cost and practice captures were visually reviewed for legibility/layout.

The [final rebuilt baseline-adoption regression](../../evidence/nonprofit-ai-planning-adoption-regression.json) separately records **ten groups passed**, zero failed/uncaught JavaScript errors and five axe scans with zero violations. Its browser version is unrecorded and is not inferred from the new planning report. One incomplete `color-contrast` finding on `.ai-discard-copy` in discard confirmation is retained: axe could not determine its background due to overlap. It requires manual review and is not accepted as an exception. These browser records do not establish complete accessibility conformance or nonprofit UAT.

Focused unit/reference/component results are distinct executions, not additional cases to add to the full application count. No sum of these runs is an execution count for the 108 specified product cases.

Local PGlite execution is not native concurrency evidence; mocked provider I/O is not a successful live model call; synthetic component fixtures are not a real tenant workspace run. The seven known Mac operations baseline failures are retained. Native PostgreSQL, live identity provider, deployment-container/hosted jobs and nonprofit UAT have not qualified this candidate. No requirement or product case is accepted by this record.

Before a merge, the repository requires green `local-reference-and-browser`, `live-identity-provider`, `native-postgresql-gate` and `container-stack`, followed by explicit owner confirmation. `main` deploys automatically. The first development request does not supply paid-CI/provider, merge or deployment authorization.

## Next development dependencies

Continue with stable content maintenance and explicit historical snapshots; money/token budget enforcement and funded advisory evaluation; task-template/run approval and retention policy; then operated supplier, adviser and procurement workflows after their owner decisions. Introduce each tenant data entity with an additive migration and forced RLS, current capability enforcement, natural-person independence, immutable reviewed decisions and matching evidence. Do not widen previously applied tenant ceilings automatically.
