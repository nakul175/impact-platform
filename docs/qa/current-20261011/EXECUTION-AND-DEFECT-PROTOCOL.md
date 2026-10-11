# Imprana Commons execution and defect protocol — current planning edition

Protocol ID: `PROTOCOL-IMPRANA-QA-20261011-01` · Version: `1` · Date: 11 October 2026 · Status: **PROPOSED / RECORD ADOPTION NOT CONFIGURED**.

Documentation input: `c1bcae29718bcae0fac51000d69734a536061fba`. Application input: `8a1e405f0086033dfb25ad834689a08bfe9f1eea` (source build 0.39.0; domain API 1.28.0; platform API 1.11.0; schema 43). These are source pins, not a selected deployable candidate or a live-server observation. This protocol creates no run, defect closure, accepted exclusion, severity decision, appointed owner or release approval.

Use it with the [release test plan](RELEASE-TEST-PLAN.md), [QA audit](../APLYD-v1.3-AUDIT-20261011.md), [reconciliation plan](../APLYD-v1.3-RECONCILIATION-20261011.md) and [working agreement](../../agile/WORKING-AGREEMENT.md). Its reference is the owner's unchanged APLYD QA v1.3 package, SHA-256 `26c64346226f660f6a648e5cebcaf2ee893750e1fb8fe50b13821aae631b5e5a`, especially `standards/register-schema.json`, the run/defect/test-report templates and source-pinning/evidence/repetition/reporting/readiness workflows. [Exact package requirements and source citations](../audit-v13-20261011/package-audit/QA-V13-REQUIREMENTS-MATRIX.json) are retained in the audit.

## 1. Separate design, execution and decisions

| Dimension | Package values / interpretation |
| --- | --- |
| Applicability | `YES`, `NO`, `UNKNOWN`; `NO` requires a real reviewed rationale for the complete scope; unresolved applicability cannot disappear from the source inventory |
| Execution result | `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, `SKIPPED`, `NOT_APPLICABLE`; PASS means the actual declared assertions/thresholds completed successfully |
| Freshness | `CURRENT`, `STALE`, `UNASSESSED`; this is separate from execution, so a historical PASS can be STALE |
| Run purpose | `QUALIFICATION` or `DIAGNOSTIC`; diagnostic success cannot replace selected qualification evidence |
| Quality | `UNASSESSED`, `MEETS_GATES`, `DOES_NOT_MEET_GATES`; a mechanical record check is only one subordinate gate |
| Approval | `PENDING`, `APPROVED`, `REJECTED`; identify the actual authority and authentic decision record |
| Readiness | `NOT_READY`, `READY`, `WITH_EXCEPTION`; readiness alone grants no deployment permission |
| Delivery | `NOT_ESTABLISHED`, `IN_PROGRESS`, `DEPLOYED`, `ROLLED_BACK`; bind the actual environment/commit/artifact |
| Learning | `NOT_STARTED`, `IN_PROGRESS`, `COMPLETE`; report observed outcome separately from predicted value |

No execution row means derived NOT_RUN; designing a case is not an attempt. Infrastructure unavailable before an assertion can be qualified is BLOCKED, not PASS. A skipped required assertion remains unmet. Preserve original labels such as `Not run`, `Local pass`, `Partial` or `Pending CI` in history; any future normalized migration needs an explicit reviewed interpretation, not a retroactive upgrade.

## 2. Freeze the complete source and candidate

The scope record must name `scope_id`, `build_sha`, `artifact_digest`, `environment`, `config_version`, `data_version`, timezone-bearing `assessment_time` and the controlled `evidence_root`. Bind `criteria_source_ref`, `criteria_source_sha256`, `expected_ac_count`, `expected_ac_ids_sha256` and `criteria_source_review_ref` from the independent canonical PM export. The source snapshot carries `source_id`, `source_version`, `scope_id`, `review_ref` and each criterion's `ac_id`, `ac_version`, `applicability`.

Preserve the existing source IDs/Gherkin and documented aliases; do not assign default versions because a legacy row lacks one. Include all YES/NO/UNKNOWN criteria in the export and complete count. The canonical identity digest is SHA-256 over UTF-8 JSON of lexicographically sorted `[ac_id, ac_version]` pairs, with `ensure_ascii=False`, separators `(',', ':')` and no final newline. Exact file-byte hashing is a different pin and remains required. Count/hash consistency does not establish source completeness or owner approval.

The source population currently has 1,328 original scenarios; that fact does not automatically select all of them for a new bounded run. An actual approved scope export must establish its own complete population independently of case mappings. Do not silently narrow RG-R1's 172-story release scope, omit an unmapped/UNKNOWN criterion or inflate the count with supplemental assertions. Changing source identity/version/applicability needs a new reviewed source version and pins; relevant old results become stale.

For every candidate, record actual Git head and clean/dirty tree information, built artifact digest, configuration/feature-policy revision, schema/migration ledger, fixture/data/model/prompt/corpus versions where relevant, tool/runtime versions and environment provenance. A Git SHA does not by itself identify an uncommitted build artifact. No deployment, provider or real-data identity is inferred from the pinned application source.

## 3. Eight proposed normalized records

These are the **exact field sets** of the referenced package schema, for a reviewed future adoption. They are not newly installed registers or fake populated rows. Do not add multivalued identities, execution results to links-only traceability or comments disguised as CSV records. Keep richer narratives and specialist protocols in linked versioned artifacts.

| Record | Exact schema fields | Purpose and preservation rule |
| --- | --- | --- |
| `ac-register.csv` | `ac_id`, `ac_version`, `scope_id`, `source_ref`, `applicability`, `applicability_rationale`, `review_ref`, `risk_tier` | Full source criterion inventory independent of tests; unknown applicability remains visible |
| `case-register.csv` | `case_id`, `case_version`, `scope_id`, `mode`, `procedure_ref`, `automation_locator`, `marker` | Versioned designed procedure and honest AUTO/MANUAL binding; no execution claim |
| `traceability.csv` | `mapping_id`, `vision_id`, `strategy_id`, `roadmap_id`, `release_goal_id`, `release_id`, `epic_id`, `story_id`, `ac_id`, `ac_version`, `task_id`, `risk_id`, `case_id`, `case_version`, `required` | Stable links only; preserve story/release/epic identity and existing task prerequisites |
| `run-register.csv` | `run_id`, `case_id`, `case_version`, `ac_id`, `ac_version`, `scope_id`, `build_sha`, `artifact_digest`, `environment`, `config_version`, `data_version`, `tool_versions`, `start_time`, `end_time`, `executor`, `purpose`, `protocol_ref`, `result`, `freshness`, `expected`, `observed`, `evidence_ref`, `parent_attempt`, `defect_id`, `rationale`, `review_ref` | Immutable actual attempt/group record with candidate and evidence; later results receive new IDs |
| `coverage-selection.csv` | `mapping_id`, `run_id` | Explicit candidate decision snapshot selecting the qualification run for each required mapping; preserve preceding snapshots |
| `defect-register.csv` | `event_id`, `defect_id`, `previous_event_id`, `severity`, `priority`, `status`, `case_id`, `run_id`, `build_sha`, `owner`, `details_ref`, `fix_pr`, `retest_run`, `close_evidence`, `severity_change_rationale`, `severity_review_ref` | Append-only defect events and linked same-case retest; no overwrite of original failure/severity |
| `risk-register.csv` | `risk_id`, `scope_id`, `failure_mode`, `impact`, `likelihood`, `inherent_tier`, `rationale_source`, `controls`, `required_cases`, `evidence_refs`, `residual_risk`, `owner`, `reviewer`, `decision`, `expiry` | Source-backed risk/control cases and actual residual decision; unassigned/unconfirmed remains unresolved |
| `exception-register.csv` | `exception_id`, `scope_id`, `gate_id`, `unmet_condition`, `eligibility`, `risk`, `controls_evidence`, `owner`, `authority`, `approval_ref`, `expiry`, `status` | Actual eligible bounded decision, never a PASS conversion or automatic waiver |

Case identity is `(case_id, case_version)`; criterion identity is `(ac_id, ac_version)`. Preserve both and link the exact source revision. A shared executable can satisfy more than one mapping only where its actual assertions and immutable run bindings support each criterion; do not turn one observed assertion into blanket coverage. The complete original 779 task dependencies remain intact.

A future compatibility record must map every migrated legacy field, identity, result, severity scale and evidence limitation to its source hash, reviewer and disposition. Keep original CSV/Markdown/Word/Excel rows and IDs unchanged. Missing artifact/configuration/data/version/review fields remain unknown; do not backfill them as if observed. Original catalogue cases and newer PM scenarios are separate populations. No fictional package example run belongs in a product register.

Serialize register integration. Concurrent authors use disjoint proposed record IDs and per-author change files/branches; one integrator validates and appends reviewed records. Do not share a writable CSV between agents or resolve duplicate IDs/predecessors by overwriting an event. Preserve earlier register and coverage-selection snapshots.

## 4. Before an actual run

1. Select the actual case/version and criterion binding, purpose, candidate and scope under the release plan. Confirm meaningful positive/rejection assertions and authoritative side-effect checks. Specify expected values/invariants and any numeric/statistical thresholds with their source and review, before observing results.
2. Name the actual executor and independently available reviewer; confirm accepted manual procedure where the source permits it. Automation needs a reviewed existing code locator and actual marker/version binding. A string marker only demonstrates presence, not assertion quality or successful execution. Do not create a fabricated AUTO locator or label planned automation MANUAL to obtain a structural pass.
3. Declare repetition protocol: group identity, purpose, attempt count, seeds/sampling, warmup, aggregation, slice obligations, critical stop conditions and completion rule. Capture fixture/actor/current permission/policy identity, redaction/access/retention and resource/time bounds.
4. Confirm authority for data, provider, environment, installation/network and any costs. Synthetic controlled responses may exercise deterministic provider branches; they do not evaluate live model quality or authorise paid calls. Use existing governed fixture identities and distinct natural people for independence; never create credentials or a synthetic second approver as a shortcut.
5. Use an owned isolated checkout/environment. Reserve a unique port and disposable native database where needed. Snapshot current authoritative evidence and record actual input pins; do not use another chat's working candidate or shared database.
6. Verify the selected entry point and its output destinations before execution. [Makefile](../../../Makefile), [scripts/run.py](../../../scripts/run.py) and workflow source are the command authority. Default runners overwrite fixed files under `docs/evidence/` and may merge reports. Choose an isolation/archive procedure that retains every first failure and rerun before another invocation. Existing runner exclusions or skipped phases must be reported.

No action above is recorded as completed by publishing this protocol. A case procedure cannot be selected as QUALIFICATION while its required source, environment, oracle or permissions remain unresolved.

## 5. Run evidence and immutable attempts

For each completed actual attempt/group, capture the following in its run evidence narrative, linked by the normalized row:

| Evidence group | Required actual content |
| --- | --- |
| Identity | Run/group ID; parent failure/diagnostic relation; exact case and AC versions; story/task/risk/source links; purpose and protocol version |
| Candidate | Build SHA and tree state; deployable artifact hash; schema/migration state; environment/configuration/data versions; provider/model/prompt/corpus or justified source-backed not-applicable boundary |
| Execution | Actual command/manual steps and selected files/modes; tools/OS/database/browser/assistive technology; executor; start/end/timezone; resource bounds; every assertion and actual code/error/skip outcome |
| Oracle and observation | Predeclared expected result/threshold; observed result; numerator/denominator and slices where relevant; current-authority/absence/persistence evidence; uncertainty and limitations |
| Artifacts | Redacted raw logs, JUnit/JSON/trace/DB-state/screenshot/manual observations; exact artifact hashes and access/retention; command exit status is insufficient alone |
| Decision | Execution result and freshness separately; linked defects; selection eligibility; actual reviewer/evidence record or unresolved review field |

Never invent timestamps, executors, observations, checks, approvals or null-equivalent “not applicable” values to fill a schema. Preserve failed/incomplete evidence even when a tool crashes. An actual blocked/skipped attempt may have its own row and explanation; it cannot be selected as passing release evidence. Runs with no meaningful assertions cannot establish PASS.

Treat evidence as append-only: a correction is a new record/version linked to the original and a clear reason. Preserve original redacted raw captures, first red result, fixed candidate and every retest. Retention/privacy handling is an actual approved policy; this protocol grants no right to erase history or retain personal data indefinitely. Store synthetic evidence and bounded identifiers, never credentials, sealed plaintext or real participant information.

Future evidence references should use an approved portable confined store, for example an explicitly adopted `repo:docs/qa/evidence` root. The checker supports its declared repository/relative resolution but does not install that store. Verify path/symlink containment and access for the actual capture. HTTP/record links and fragments are pointers, not authenticated fetched assertions; archive appropriate reviewed content/hash where policy allows. An absolute-root override, if genuinely approved, must not become arbitrary absolute evidence references.

## 6. Repetitions, flakes and freshness

Ordinary deterministic gates require successful meaningful assertions. A flaky required behavior is a defect/evidence gap; majority voting cannot make it pass. Predeclare AI/statistical repetitions only with a risk-justified sample/distribution rule and required slices. The package's “4 of 5” is an example, not an Imprana default. Report every sample, count, uncertainty interval and critical invariant failure; no pooled score hides a failed privacy, tenant, independence or arithmetic case.

A run row represents the completed declared qualification group for its exact case/AC binding, with full per-attempt evidence linked. PASS is unavailable until that group finishes and meets its rule. Unplanned extra attempts are DIAGNOSTIC, retain parent links and cannot replace the original selected result. New insight may justify a new reviewed protocol version and qualification group; never rewrite the failed group. A changed fixed build receives a new qualification attempt and linked retest.

Freshness is a reviewed relation to the candidate snapshot, not simply the latest timestamp. Match scope, build/artifact, environment/configuration/data, case/criterion/protocol versions and relevant policy/model/corpus changes. Record dependencies and rationale when a change invalidates evidence. A run from another candidate stays historical; an affected change makes it STALE until actual requalification. UNASSESSED cannot count as CURRENT. No arbitrary age window or undocumented “no impact” exemption is introduced here.

Version coverage selection separately from runs. For each required mapping, select only an eligible completed QUALIFICATION run for the exact case/AC versions and current candidate pins. Missing selection remains derived NOT_RUN; selected failure cannot be replaced by a later diagnostic green. Preserve historical selections and their failed results alongside the new decision snapshot.

## 7. Defect events, severity and retest

Every observed material failure gets a concrete defect narrative: original failed behavior/expected vs actual, release/story/criterion/task/case/run links, candidate/configuration/data identity, reproduction steps/frequency/denominator, impact/blast radius, redacted evidence, workaround, actual owner/status, hypothesis-labelled cause, fix PR/build and required retest/regression scope. Use new immutable event IDs with `previous_event_id`; one initial root, no fork/cycle, and the same defect/case identity throughout the chain.

| Package severity | Source guide | Explicit legacy compatibility where that scale is used |
| --- | --- | --- |
| D4 | Severe harm, critical outage or disclosure | S1 → D4 |
| D3 | Major function impaired | S2 → D3 |
| D2 | Recoverable material issue | S3 → D2 |
| D1 | Minor issue | S4 → D1 |

This is a proposed documented mapping, not a recategorization of historical defects. Retain the original scale/value and review a real migration before adoption. Priority is a separate urgency/exposure/dependency decision. Do not lower severity merely because a fix, deadline or passing unrelated test is available.

A severity decrease requires a new event with nonempty `severity_change_rationale` and `severity_review_ref`, an actual independent authorised review, and preserved prior event/case. A locally typed person/path does not prove authority. The code author or agent cannot self-certify a review to clear a gate.

Closure requires a current PASS **QUALIFICATION retest of the same failed case ID** on the closed event's fixed build, with relevant case/AC versions. Release closure additionally matches the actual selected scope/artifact/environment/configuration/data. Keep the original failure and actual fix/retest relation; unrelated green evidence is insufficient. If the criterion or procedure changes, preserve the old defect and record separately reviewed requirement/case-version change and applicability/invalidation; do not silently rename the failing case away.

The package's strict release-record gate rejects any unresolved D3/D4 defect leaf event. Its exception records do not auto-waive that condition. Lower-severity findings still need actual impact/priority/regression disposition; reducing a label is not a substitute for closure or an eligible independent release decision.

Declare regression scope from the failed invariant and affected dependencies: related positive/refusal/retry/stale/current-authority paths, tenant/role boundaries, persisted state, browser recovery and native races/restart where affected. An isolated focused retest does not establish the full release gate. Reopen through a new event when the same defect recurs, the fix/regression fails or relevant evidence becomes invalid. Closure authority and product acceptance remain actual human decisions.

## 8. Exceptions and incident boundaries

An exception needs the exact scope/gate/unmet condition, eligible policy, impact/exposure, compensating-control evidence, responsible owner, actual approving authority/reference, expiry and retest/reopen trigger. Record it separately; retain the failed/missing/stale test outcome. WITH_EXCEPTION is a qualified decision, not PASS. The package checker does not automatically waive any failed strict-release condition.

Exceptions cannot waive tenant isolation, current authority, natural-person independence, immutable approved history/audit, deterministic official arithmetic or mandatory privacy/rights/legal baseline. A quota or commercial credit is not data permission; AI budget failure cannot gate the independent manual MEL path. Missing financial, provider, real-data, merge or deployment permission is not a QA exception. No new waiver, approver identity or emergency bypass is introduced here.

For active suspected disclosure/corruption/unsafe paid calls, stop the dependent run, retain bounded evidence and contain within existing authority. Link defect/incident/run and use an authorised internal escalation route. Do not send external messages, delete protected evidence, alter user roles or create credentials on this document's authority. Recovery must preserve history and recheck current access rather than resurrecting revoked rights or deleted data by assumption.

## 9. Test report and honest arithmetic

Use the package report structure with actual scope/build/artifact/environment/window first. Report required mappings and unique selected runs separately from historical run rows and designed cases. Show PASS, FAIL, BLOCKED, NOT_RUN, SKIPPED and NOT_APPLICABLE counts, then freshness counts separately. Report first failures/repeats/flakes, high/critical coverage, approved exclusions, open defect severities, exception expiry, domain slices/uncertainty and unresolved decision owners. No report is populated by this edition.

| Measure | Numerator / denominator and qualification rule |
| --- | --- |
| Planned AC coverage | Criteria with at least one required mapping / complete source population whose applicability is YES or UNKNOWN; reviewed NO records alone are excluded |
| Validated AC coverage | YES criteria for which every required mapping has selected current PASS QUALIFICATION evidence matching the candidate / complete YES-or-UNKNOWN source population |
| Required-case completion | Selected required mappings with current executed PASS or FAIL / all required mappings whose criterion is YES or UNKNOWN; blocked/not-run/skipped/unassessed/stale evidence cannot masquerade as completed qualification |
| Selected executed pass rate | Selected mapping PASS / (selected mapping PASS + FAIL), as printed by the checker; freshness is counted separately, so this ratio alone cannot imply current evidence or readiness |
| Unique executions/history | Count distinct selected run IDs and historical qualification/diagnostic rows separately. A shared executable mapped to two criteria contributes two mapping obligations; actual physical group/attempt counts need their own evidence and cannot be inferred from the mapping count |

UNKNOWN applicability stays visible and blocks a release-record decision; it cannot be counted as an approved exclusion. For planning, report the unresolved population explicitly and avoid a favourable percentage derived only from known mapped rows. A zero or unknown denominator is undefined/null, never 100%. Preserve the package checker's definition/output when normalized adoption exists; do not implement a competing tally that drops missing or stale evidence. Designed case counts, code/test function counts and accepted story counts are different measures.

The executive decision separates quality, approval, readiness, delivery and learning. A screenshot, command exit 0 or “all tests pass” phrase cannot replace candidate identity, actual selected assertions and unrun/blocked limitations. Evidence must remain available to authorised reviewers through its decision and approved retention window.

## 10. Checker and repository-control limits

The unchanged package's supported-runtime checker regressions passed 57/57 against package fixtures, as recorded in the [supported receipt](../audit-v13-20261011/package-audit/CHECKER-SUPPORTED-RUN-RECEIPT.json). Those fictional demonstrations and structural/release failures are not Imprana product runs. The [crosswalk review](../audit-v13-20261011/package-audit/CROSSWALK-REVIEW.json) is a documentation consistency review, not production acceptance.

On a future reviewed installation, the offline structural checker can validate exact schema/identity/reference consistency and report planned/selected coverage; strict release mode additionally rejects unmet selected-current evidence, unresolved applicability and open D3/D4 defect leaf events. Neither mode discovers criteria omitted from the canonical source, authenticates approval/owner identity, proves history against Git, validates digest truth/statistics/assertion adequacy, executes product tests, verifies specialist/legal accessibility judgments, enforces real permissions or configures trusted branch checks. Source/pins changed together can still be self-consistent and wrong.

Do not advertise `docs/qa/checker/qa_lint.py` as installed or add a runnable CI command pointing to a nonexistent adopted path. Installing registers/checker, actual case/version markers, workflow/always-run aggregator and source-control protection requires separately reviewed adoption changes. `docs/CODEOWNERS` already exists; live required/fresh code-owner review, named trusted checks and bypass/source-protection enforcement remain NOT_VERIFIED. No enforcement configuration is changed by this protocol.

The existing four qualification jobs plus `checks` retain their repository policy. Before any merge, bind every required genuine run to the exact head/integration artifact and current authority. Missing/skipped/neutral/cancelled/timed-out/unavailable results are not successful execution. Documentation-only four-job filtering and the small job's non-aggregator behavior remain visible. Paid CI/provider/cloud actions and `main` auto-deployment need their actual authority; this protocol supplies none.

## 11. Current disposition and next record gate

The preserved 0.39 review remains **G11 Not passed**, **G12 Not run**, 14 open critical threats, 13 open other threats and two BLOCK chains. The [release review](../../release-reviews/release-review-0.39.0.json) and [threat register](../../current/threat-register.json) remain unchanged; confirmations and independent assessment/model evaluation are not supplied here. A new product run, defect event or approval is not inferred from this documentation work.

The next bounded adoption needs an actual owner-selected scope, a complete independently reviewed criterion snapshot, honest case-to-code/manual bindings, a reviewed legacy compatibility bridge, candidate/environment/protocol authority and immutable evidence capture. Only then can actual affected tests create qualified run records. Preserve all earlier editions, source Gherkin, estimates, workflow states, regression minima, failures/retries and confirmed history. Documentation alignment alone cannot clear readiness.
