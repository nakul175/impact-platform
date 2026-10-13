# Imprana Commons release test plan — current planning edition

Plan ID: `PLAN-IMPRANA-QA-20261011-01` · Version: `1` · Date: 11 October 2026 · Status: **PROPOSED / CANDIDATE NOT SELECTED**.

This is a source-bound plan for the next qualification work. It records no new product execution, approved scope, named executor, sprint commitment, financial permission, production acceptance or deployment authority. The accountable product owner remains Nakul Jain; quality, engineering, security/privacy, accessibility and operations assignments require actual acceptance by those people. A document author is not an appointed reviewer or approver.

## 1. Source and candidate boundary

| Item | Bound source or unresolved field |
| --- | --- |
| Documentation input | `c1bcae29718bcae0fac51000d69734a536061fba`; the QA audit and current product refinement carried by that commit |
| Application input | `8a1e405f0086033dfb25ad834689a08bfe9f1eea`; source build 0.39.0, domain API 1.28.0, platform API 1.11.0, schema 43 |
| Preserved planning baseline | `eb194fdbb6fc8247db8429fc23120aa0fe659ed8`; original criteria, estimates, allocations, workflow states and dependencies remain authoritative |
| QA reference | Owner-supplied `APLYD-Software-Testing-QA-v1.3.zip`, SHA-256 `26c64346226f660f6a648e5cebcaf2ee893750e1fb8fe50b13821aae631b5e5a` |
| Candidate scope/build/artifact | **Not selected.** A later decision must name the actual scope ID, complete criteria source, source head and deployable artifact digest |
| Environment/configuration/data | **Not selected.** Synthetic data only within current authority; record exact environment, configuration and fixture revisions before execution |
| Qualification dates, repetitions and spend | **Not committed.** Declare the case protocols and available authority before a run; this plan grants no paid CI/provider/cloud permission |
| Delivery state | **Not established by this edition.** Source pins do not prove current hosted commit, schema, health or incident resolution |

These source pins are inputs, not an assertion that an application built from them has passed this plan. Inspect the actual candidate before engineering. Older instruction files contain historical build/migration literals; the source version and migration ledger determine the actual candidate. Keep every applied migration immutable and derive the next contiguous migration from the current checkout, rather than reusing an old number.

The plan uses the package's `templates/release-test-plan.md`, `templates/run-evidence.md`, `templates/defect.md`, `templates/test-report.md`, normalized register schema and source/evidence/repetition/readiness workflows. The [54-requirement inventory](../audit-v13-20261011/package-audit/QA-V13-REQUIREMENTS-MATRIX.json) preserves their exact reference paths, line ranges and hashes. The package has not been installed as a live repository QA gate. Its fictional examples and checker regression results are separate from product evidence.

Read the [audit](../APLYD-v1.3-AUDIT-20261011.md), [reconciliation plan](../APLYD-v1.3-RECONCILIATION-20261011.md), [current product entry point](../../product/framework-v4-20261011/START-HERE.md), [working agreement](../../agile/WORKING-AGREEMENT.md), [AGENTS.md](../../../AGENTS.md) and [CLAUDE.md](../../../CLAUDE.md) with this plan. The companion [execution and defect protocol](EXECUTION-AND-DEFECT-PROTOCOL.md) defines the records and decisions required to use it.

## 2. Release outcome and proposed next slice

The existing [RG-R1 goal](../../product/04-RELEASE-GOALS.md) covers **172 active R1 Pilot stories**. Its outcome hypothesis is that a nonprofit can carry a priority problem through diagnosis, trial and adoption, compare outcomes to a defensible baseline, and complete governed MEL work. Identity, tenancy, collection, independent review, official calculations, privacy, reporting and operations remain within the assigned release scope. The [refined release contracts](../../product/framework-v4-20261011/04-RELEASE-GOALS.md) retain that population. A first bounded story or walkthrough does not replace the release denominator or accept the remaining stories.

The current product hierarchy contains 54 epics, 368 active stories, 1,328 original acceptance scenarios, 1,131 tasks and 779 task prerequisites. The 370 backlog rows include two historical split parents. The original 825-case catalogue, 108 nonprofit AI specified cases and 1,328 product scenarios are distinct populations; do not add them together or use one as the other's denominator. Four earlier stories remain In Review pending actual acceptance; this plan changes no state.

The [existing Sprint 2 proposal](../../product/06-NEXT-SPRINT-REFINEMENT.md) and its [current refinement](../../product/framework-v4-20261011/06-NEXT-SPRINT-REFINEMENT.md) propose the following 26-point slice. It is a refinement sequence, not an approved sprint or chosen release scope.

| Existing story | Existing proposal and dependency | Planned correctness/absence oracles |
| --- | --- | --- |
| `US-DX-01a` — prioritised problem diagnosis | 5 points; structured problem model, completion/correction rules, evidence types and capability scopes must be settled first; tasks `TASK-US-DX-01a-01`–`06` | Stable problem IDs and exact ordered evidence survive reopen/restart; incomplete completion and duplicate/stale ordering refuse atomically; hidden and missing evidence both return `404 RESOURCE_UNAVAILABLE` without a title leak; AI-off creates no provider transmission |
| `US-DX-03` — locked problem baseline | 8 points; depends on agreed problem IDs/revision semantics from `US-DX-01a`; tasks `TASK-US-DX-03-01`–`06` | The four source-defined measures have explicit units, period, denominator and evidence; missing differs from zero; exact decimals and server-owned lock actor/date persist; locked observations remain immutable; stale source and competing locks cannot create an invalid or second lock |
| `FR-AI-016a` — bounded jobs/reservation/cancellation | 8 points; depends on actual policy readiness and a settled budget-unit/window/upper-bound/uncertain-acceptance contract; `FR-AI-001` review/acceptance is unresolved; tasks `TASK-FR-AI-016a-01`–`06` | Permitted bounded `ADVISORY_DRAFT` creates one stable job/reservation/receipt atomically; exact retry is authority-aware and changed payload conflicts; native races cannot overspend or settle twice; cancellation stops the next controllable call and accounts for accepted/uncertain work; stale lease holders cannot publish or settle; AI-off/exhaustion leaves core MEL available |
| `US-CM-05` — visible authoritative AI usage | 5 points; depends on `FR-AI-016a`'s authoritative journal/settlement; read scope, personal-data display and alert basis remain design decisions | Consistent limit/consumed/reserved/available units with window/as-of basis; uncertainty never becomes zero; the source's 80%/100% alerts retain their proposed exposure interpretation until reviewed; threshold/window/recipient effects are idempotent; delivery rechecks current authority; zero limit/unavailable data produces no fabricated percentage |

The two dependency chains are diagnosis → baseline and bounded jobs/accounting → usage. Recommend refining one coherent existing story at a time, starting with the structured-diagnosis design if its actual Ready conditions can be met. The owner still selects the first scope and confirms consequential decisions; this recommendation does not mark that story Ready or assign its implementation.

Keep the original source Gherkin exact. Use the [scenario/task matrix](../../product/framework-v4-20261011/task-author/acceptance-task-matrix.proposed.json), [task contracts](../../product/framework-v4-20261011/task-author/task-contracts.proposed.json) and [criterion alias map](../../product/framework-v4-20261011/bundle-review/CRITERION-ALIAS-MAP.json) to preserve identities and duties. The 37 source scenarios with missing phases, seven supplemental assertion groups and 13 stories with proposed qualification duties remain visible clarifications. Supplemental assertions are not additional accepted source criteria.

Scope selection must identify every included story/criterion, inherited control, relevant prerequisite and justified exclusion. A narrowed qualification scope needs its own ID and a stated relation to RG-R1; no narrower release acceptance is inferred. Real cohort, data permissions, provider/region, budget, languages, editorial scores/disclosures, success thresholds and operational support remain unresolved decisions.

## 3. Entry conditions and complete coverage population

Before any QUALIFICATION group:

1. Record the approved bounded scope or explicitly label the work DIAGNOSTIC; confirm story design/Ready decisions and prerequisite evidence without promoting source workflow states.
2. Export the complete in-scope PM criterion population **independently of tests and QA rows**. Retain original scenario text, identity, alias and source version; record `YES`, `NO` or `UNKNOWN` applicability. Include unresolved items. Every `NO` needs scope-covering rationale and a real review. Unresolved mandatory applicability prevents readiness.
3. Review source completeness/applicability independently; bind exact source-byte SHA-256, complete count and the package's canonical sorted AC ID/version SHA-256 in a scope snapshot. No default AC version or agent checksum can stand in for a source-owner review. Source/pin/control protection must be independently verified before relying on the package for a real release decision.
4. Design actual case versions and reviewed links from vision/strategy/roadmap/release/epic/story/criterion/task/risk to those cases. Resolve the expected oracle, prohibited effects, automation locator or accepted manual procedure. New story tests are planned until their actual files/assertions exist; do not invent runnable markers or substitute manual labels to satisfy a checker.
5. Pin the candidate and immutable artifact, environment/configuration, synthetic fixture/data version, runtime/tools, actors/current scopes and protocol/repetitions. Establish environment isolation, evidence access/redaction/retention and actual executor/reviewer availability.
6. Confirm relevant spending, data, network, provider and release authority. A design or synthetic-provider test does not authorise a paid model call, hosted CI dispatch, real personal or participant data, new resources, merge or deployment.

The adopted normalized registers and canonical scope export are not yet configured. This edition specifies their contract; it does not create executed rows or select an evidence snapshot. Historical rows lacking candidate/artifact/configuration/data identity retain those limitations rather than receiving inferred values.

## 4. Risk-based test portfolio

Every selected original scenario needs its positive and rejection assertions plus the affected platform controls. Check authoritative revisions, receipts, audit/outbox state and provider-attempt records when proving absence. A UI refusal alone cannot prove that no forbidden write or transmission happened. A bounded refusal audit explicitly required by the source remains permitted.

| Domain | Planned evidence and decision boundary |
| --- | --- |
| Static/unit/contract | Existing lint/types/build; source-bound DTO and Decimal rules; closed inputs/duplicate JSON keys; state-machine transitions and exact oracles. Unit/component evidence alone cannot validate real tenancy, concurrency, identity or provider behavior |
| API/integration/SQL | Real HTTP paths and authoritative persisted state; transaction rollback; stale revision, exact retry/changed payload, hidden/missing identity symmetry, denied side effects. Preserve existing regression minima and all task dependencies |
| Native database/current authority | PostgreSQL 16/17 with provisioned runtime login roles, forced RLS and narrow grants; cross-tenant direct SQL and API denial, revoked capability, natural-person self-approval refusal, simultaneous mutations/leases/cancellation/settlement. Migration-owner/superuser fixture setup is distinct from runtime evidence |
| Browser/E2E | Real selected UI journey and persisted outcomes, keyboard flow, validation recovery, stale/lost-response/reload and tenant-switch cases. Adapter/model checks are separate component evidence; synthetic screenshots do not prove authorization or full outcome |
| Security/privacy | Relevant `FR-SEC-001/003`, `FR-PRV-001` and G11 impact/threat/chain review; field purpose/owner/classification/retention, bounded logs and sealed inputs/outputs; no unauthorized recipient/provider disclosure. Actual independent assessment and residual confirmations remain required |
| Accessibility | Relevant `VF-UX-001`; source-bound WCAG 2.2 AA assertions, automated findings plus named manual keyboard and assistive-technology procedures on the exact process/browser. Automated scan success does not replace manual evidence |
| Recovery/reliability | Relevant `VF-DIN-002`, `VF-AUD-001`, `VF-DR-003`; pending-operation restart, immutable history, restore and populated upgrade; deny after revoked/expired authority during retries. A local drill is bounded evidence, not full monthly/disaster-recovery acceptance |
| Performance | Representative workload, data/cohort sizes, concurrency, hardware/tools, warmup/duration and distribution metrics; preserve original source thresholds. The selected workload and actual threshold owner are not supplied by this plan; shortened smoke runs cannot claim peak/soak capacity |
| AI policy/budget/fallback | Synthetic controllable provider for deterministic failures/ambiguous acceptance; pre-call current-policy gate, maximum reservation, lease fence, one settlement, sealed data, no retry of possibly accepted paid work. `VF-AVL-002` verifies independently healthy manual/MEL paths with AI off/failing/exhausted. `EXTRACTION`, `REPORT_DRAFT`, `CHAT` and tools stay disabled unless their own contracts change |
| AI quality/specialist evaluation | Where generated advice is selected: reviewed held-out corpus, model/prompt/policy versions, grounded/correct/private/injection-safe outcomes, required persona/language/risk slices, budget bounds and human adjudication. No live-model evaluation or statistically justified sample/target is established here; G12 remains Not run |
| UAT/exploratory | An actual authorised representative can complete the agreed task and explain the result; independent review and official-number boundaries remain intact. Version scenario procedures, exploratory charters, observations and defects; no research, saving, ROI or causal effect is inferred from synthetic success |
| Operations/deployment | Exact artifact/configuration, migration ledger, backup/restore, smoke/health, alerts/support and rollback/compensation. Actual host, cohort, window and operator authority must be established separately; deployment is not part of this documentation step |

Measure contracts in the [story recommendations](../../product/framework-v4-20261011/epic-story-author/STORY-MEASURE-CONTRACTS.json) remain proposed experiments. Predeclare comparable tasks/control, sample/denominator, observation period, uncertainty, slices and falsifier before learning. Correctness invariants can be exact; benefit baselines and new numerical targets remain unknown. The source's existing thresholds are retained, not accepted or recalibrated by this edition.

## 5. Ordered execution guidance — not executed

Use an owned, isolated qualification checkout and synthetic disposable resources. Pin the input and evidence state before a run. Existing runners write fixed `docs/evidence/` destinations; capture each complete attempt into a distinct controlled evidence directory before another run, preserving first failures and redacted raw logs. Never run in another agent's checkout, overwrite authoritative history or discard a failed output as “restore cleanup.” Inspect actual runner exclusions/skips and record their effect on required cases.

The following are existing entry points, not a claim that they ran for this edition. Angle-bracket values are unresolved run configuration, not literal runnable commands. Dependencies must already be authorised and available; installation/fetching, resource provision and paid CI are separate actions.

| Order | Existing command/entry point | What the actual report must distinguish |
| --- | --- | --- |
| 1 — input/static checks | `make lint`; `python3 scripts/doc_index.py --check`; `make unit`; `make build`; `npx tsc --noEmit` from `apps/web` | Exact selected targets, failures/errors/skips, source head/tools and outputs. `make unit` cannot certify DB-dependent behavior; skipped assertions are not passes |
| 2 — security change consistency | `.venv/bin/python scripts/release_review.py --check --base <actual-change-base>` | Actual change base and required append-only impact-review entries. CI uses `HEAD^1` for its checkout semantics; do not assume that is the correct local story baseline. Consistency success does not pass G11 or confirm residual risk |
| 3 — affected existing tests | `IMPACT_PORT=<isolated_port> .venv/bin/python scripts/run.py test --pytest-path qualification/test_ai_policy_live.py` is an existing focused entry point | Select only where that existing test is relevant; record actual new story case bindings when implemented. Focused PGlite output is not a full suite or native proof |
| 4 — local API/regression | `IMPACT_PORT=<isolated_port> make test`; `make golden`; `make reference` | PGlite/API evidence, actual golden reconciliation and preserved design-reference assertions remain distinct. Neither PGlite nor reference-only output proves native races/RLS roles or deployed behavior |
| 5 — native/restart/restore/upgrade | `IMPACT_PORT=<isolated_port> make native`, with authorised private PostgreSQL fixture DSN/tooling | Provisioning vs runtime roles, full suite, restart phases, restore drill and populated-upgrade results. Pin the actual populated baseline and target schema; the workflow's historical baseline 33 is not a fresh deployed-schema fact |
| 6 — real browser and identity | `make browser`; `make idp` | Actual UI modes vs adapter/model checks; live Keycloak/PGlite vs native identity runs. These commands install browser dependencies or fetch pinned identity tooling when absent; they require their own authorised environment. Record manual accessibility separately |
| 7 — representative workload/specialists | `make perf` with reviewed `PERF_ARGS`; existing scoped accessibility/UAT/security/recovery procedures | Actual profile and bounds, all failures and limitations. Native fixture authority and workload/data permission are prerequisites; no default peak/soak or specialist pass is assumed |
| 8 — hosted candidate qualification | Existing workflows below, only after current financial authority and review | Exact tested head/integration head and artifacts; all required jobs actually executed. Missing, skipped, neutral, cancelled, timed-out or unavailable is not a current pass |
| 9 — authorised rollout validation | Existing `scripts/smoke.py` against the separately approved URL/CA and deployment runbook | Exact live commit/build/schema/artifact/configuration and health, plus declared rollback/compensation tests. Smoke is basic health, not every acceptance criterion; no host check is executed by this plan |

A focused `--native --pytest-path` or live-IDP run does not include the full native restart/restore/upgrade sequence. Skipping a stage must remain visible; the selected required gate still needs its evidence. The existing runner's test-selection exclusions and repository warnings are retained, not silently reinterpreted as full coverage.

### Existing hosted gate portfolio

| Workflow/job | Declared source behavior | Required evidence before any release promotion |
| --- | --- | --- |
| `checks` / `checks` | Every PR and main push; 15-minute timeout; lint, doc index, unit, release-review consistency and web types | Genuine successful steps on the exact candidate; this small job is not a child-result completion aggregator |
| `Application qualification` / `local-reference-and-browser` | 30-minute timeout; setup, local API/reference/lint and browser | Actual local artifacts and logs; no model-adapter result substituted for real UI |
| `Application qualification` / `live-identity-provider` | 20-minute timeout; pinned Keycloak/live identity API and browser | Real identity result and configuration, separate from synthetic fixture authentication |
| `Application qualification` / `native-postgresql-gate` | 40-minute timeout; provisioned runtime roles, native suite/restart, restore, populated upgrade and native live-IDP evidence | All applicable native stages and artifact identity, with fixture/runtime separation |
| `Application qualification` / `container-stack` | 45-minute timeout; Linux deployment/container path and smoke | Actual deployment-path output; local development checks cannot substitute |

Sources are [checks.yml](../../../.github/workflows/checks.yml) and [qualification.yml](../../../.github/workflows/qualification.yml). The four-job workflow filters documentation-only changes; the small workflow does not. A documentation push therefore does not provide four-job qualification. Newer candidate pushes may cancel older PR runs. A current green interface alone cannot establish execution or trusted reporting. No QA record gate, always-run aggregator, merge-queue trigger or branch/ruleset change is installed here.

## 6. Thresholds and stop rules

For deterministic required cases, the planned oracle is the complete required assertion set: correct authorised outcome and no prohibited effects. No majority vote, quarantining, test deletion, narrowed source denominator or weaker expectation rescues a critical failure. Predeclare statistical AI repetition/aggregation separately; record all samples and slice results. Missing meaningful assertions is a blocked evidence gate, not an automated pass.

Stop the affected run and preserve evidence when tenant data/secret disclosure, unauthorized action, self-approval, immutable-history mutation, official-arithmetic corruption, duplicate paid call/settlement or unsafe resource use is observed or plausibly continuing. Contain only within actual authority; record a linked defect/incident and notify the accountable internal owner through an authorised route. This document authorises no external messages, data deletion or new credentials. An infrastructure/tooling failure is BLOCKED for the dependent evidence, not a product PASS.

Stop dependent external work when financial/data/provider/host authority is absent. Zero-step hosted CI failures attributed to exhausted spending require the owner's spending decision; changing code or retrying indefinitely cannot fix billing. Retests need a declared fixed candidate or a preserved diagnostic purpose, not “rerun until green.”

## 7. Current unresolved gates

The preserved [0.39 release review](../../release-reviews/release-review-0.39.0.json) records `passed: false`, **G11 Not passed**, **G12 Not run**, **14 open critical threats**, **13 open other threats**, and **two BLOCK chains**. Critical IDs are TH04, TH05, TH06, TH09, TH11, TH13, TH17, TH21, TH25, TH26, TH27, TH28, TH29 and TH34. CH01 document injection to export and CH02 support escalation remain BLOCK. See the [threat register](../../current/threat-register.json). No live-model grounding/correctness/privacy/injection/budget qualification or independent security assessment is supplied by this plan; impact/residual confirmations remain actual human gates.

`docs/CODEOWNERS` exists. Target-branch required/fresh code-owner review, trusted required checks, bypass rules and independent source/pin protection remain **NOT_VERIFIED**. File presence and checker consistency cannot authenticate live enforcement. Existing release evidence remains scoped to its exact build; [QUALIFICATION.md](../../QUALIFICATION.md) and the [legacy acceptance record](../../current/RELEASE-ACCEPTANCE.md) must not be reported as current execution for this plan.

Quality is UNASSESSED for a future selected candidate; approval is PENDING; readiness is NOT_READY for a release decision; delivery is NOT_ESTABLISHED by this edition; learning is NOT_STARTED for its proposed experiments. These are separate dimensions, not revisions to historical records.

## 8. Exit, review and rollout handoff

For the bounded story: its declared original scenarios and affected control cases need current real evidence; all omissions/limitations must be visible; code and evidence need separate actual reviews; the product owner must accept the delivered scope under the working agreement. Completion of one story does not clear the full RG-R1 or G11/G12 population.

For a release candidate: freeze the full selected source/artifact/configuration/data snapshot, verify complete mappings and current qualification selections, close blocking defects through same-case retests, complete applicable specialist reviews, resolve nonwaivable/source-protection gates, and record actual residual/exception/owner decisions. The test report shows exact scoped numerator/denominator and all missing/blocked/stale outcomes. Quality evidence, approval, readiness and deployment permission remain separate.

Before any authorised rollout, name the actual cohort/operator, exposure and observation window, permitted data/provider use, alert/support responsibility, stop signals and rollback/restore/compensation procedure. Verify current deployed commit/schema/health/demo only after promotion. Code rollback cannot be assumed to undo migrations, privacy effects or provider actions. No rollout selection, merge or deployment is approved here.

The next documentation adoption step is a reviewed complete criterion export and case/register compatibility bridge for the owner-selected bounded scope. Actual execution follows only after source/candidate/environment/protocol and permissions are concrete. Preserve the original evidence and all later attempts as history.
