# Nonprofit AI planning and practical capacity building

Build **0.31.0** review candidate · domain API **1.22.0** · platform API **1.9.0** unchanged · schema **35** unchanged · 5 October 2026.

This increment adds usable cost planning, self-reported pilot comparisons and guided task practice to the nonprofit adoption workspace. It also gives saved learning progress stable identifiers and bounds advisory response transfer. The candidate is on `release/0.31-nonprofit-ai-planning`; it is not merged or deployed. Starting development does not constitute business scope signoff or product acceptance. The original impact ledger stays **113 PARTIAL, 194 PENDING and 0 accepted out of 307**.

## Delivered

- **Stable learning progress.** Twelve lesson identifiers now describe their meaning rather than their position. The original twelve positional identifiers have fixed aliases. Old plans remain readable without changing their stored revision. New saves store canonical identifiers, reject duplicate completion through an alias plus its canonical key, and retain the original request fingerprint for exact retries. Reads report CURRENT, STALE or UNKNOWN catalogue/solutions compatibility and unavailable learning entries. The workspace retains unavailable entries until the user deliberately removes them from a new draft; it does not silently discard retired progress while saving. Historical guide text is not archived.
- **Compare supplied costs.** Staff enter one currency, a whole-month period and up to four offers, each with up to twenty lines. Setup, subscription, usage, integration, training, human review, support and exit costs are distinct categories. One-off lines count once; monthly lines count for the selected months. Exact decimal products are retained. A missing amount stays unknown even when its quantity is zero; an incomplete offer has no complete total, and any incomplete offer prevents a cheapest-offer indication for the comparison. Equal complete totals preserve all ties. These are supplied estimates, not verified supplier quotes, exchange conversion or procurement awards.
- **Evaluate a pilot.** Baseline and pilot inputs separately capture sample size, drafting minutes, review minutes and factual correction counts. The result normalizes total staff time per item and labels itself `SELF_REPORTED_DRAFT`. Percentage comparison is UNDEFINED when the samples are marked incomparable or baseline time is zero. Different sample sizes do not prove equivalent difficulty or quality. No causal benefit, ROI, accepted impact or official result is asserted.
- **Practise a useful task.** Four manual worksheets cover a community invitation, a fictional grant summary, invented meeting actions and fictional supplier questions. Each provides permitted/prohibited inputs, a synthetic example, a bounded prompt framework and human checks. The user writes the brief, draft and review notes; no model is called. Checked steps are self-recorded, not certification or independent approval. An unavailable saved template keeps all three texts and its raw self-check identifiers visible read-only. A manager must deliberately replace it (retaining text and resetting checks) or clear it before saving; read-only colleagues cannot resolve it. Saved practice editions show Current, Stale or Unknown, and historical guidance wording remains unavailable.
- **Save the source inputs.** Optional cost, pilot and task-practice inputs travel with the existing adoption plan. Calculation outputs remain temporary. Reopening a saved plan restores its original amounts, sample counts, notes and checked steps, allowing recalculation. An invalid nested input prevents the whole save. A read-only user can inspect stored inputs and request deterministic calculations but cannot persist edits.
- **Bound advisory transfer.** The server accepts at most 256 KiB of an uncompressed provider response and applies one 45-second cancellable request/body I/O deadline, rather than renewing a timeout for every chunk. Provider output remains plain text, limited to 12,000 characters, with the existing 2,048-output-token request limit, no redirects or automatic retry. OS DNS resolution and cleanup can outlive cancellation; this is not a hard end-to-end process wall-clock bound.

## Contract and persistence

Three domain operations extend the eight existing nonprofit operations; the domain inventory becomes **243 implemented operations**, with **44 platform operations** unchanged. All three require current `ai.enablement.read`; the two POST operations are deterministic read-like computations and do not write a record, issue a receipt, queue work or call a provider.

| Method | Tenant-relative path | Operation | Request / response |
|---|---|---|---|
| POST | `ai-enablement/cost-comparison` | `compare_ai_procurement_costs` | `AICostComparisonRequest` / `AICostComparisonResult` |
| POST | `ai-enablement/pilot-evaluation` | `evaluate_ai_pilot` | `AIPilotEvaluationRequest` / `AIPilotEvaluationResult` |
| GET | `ai-enablement/task-templates` | `get_ai_task_templates` | No body / `AITaskPracticeTemplates` |

The path prefix is `/v1/tenants/{tenant_id}/`. Closed schemas reject unknown nested fields, forged approval/version/result fields and duplicate JSON keys. Amounts remain strings; booleans are not accepted as integer sample sizes or months. Currency is a single three-letter uppercase input code, not proof of currency validity or conversion support.

The six existing required plan inputs remain valid without `planning`. When supplied, `planning` is a closed object with three keys: `cost_comparison`, `pilot_evaluation` and `task_practice`; each may be null or its validated source-input object. An older-client update that omits `planning` retains any existing source snapshots and their original practice edition; explicit null members clear them. There is one worksheet per plan, not a task-run history. The server stamps the current practice content version when a non-null practice worksheet is explicitly saved, while exact replay and legacy retention preserve the previous stamp. Saved-plan responses additionally expose `content_compatibility`; this interpretation never rewrites an old revision or claims a historical content snapshot.

No database migration, new capability, role bundle or delegation-ceiling widening is introduced. Existing `ai.enablement.manage` plus current read access controls plan saves. The existing tenant/operation locks, revision conflict checks and atomic head/revision/audit/outbox/receipt transaction remain in place. Exact replay checks current access before returning the original receipt; changing a nested source input under the same operation identifier conflicts. The 1,000-plan tenant limit, 15-minute signed cursor binding and seven-day receipt window remain unchanged.

## Limits and remaining target design

The [edition 1.0 design package](nonprofit-ai/v1.0/README.md) remains the proposed baseline at build 0.30.0. This implementation record extends it without silently changing its requirement statuses, Word documents or case execution records. [DEVELOPMENT-0.31.md](nonprofit-ai/v1.0/DEVELOPMENT-0.31.md) maps the bounded increment to requirements and supporting cases; no new requirement is accepted.

Still target work: operated supplier onboarding/verification and commercial neutrality; RFQ dispatch, live quotes and independently reviewed awards; human adviser bookings and service engagements; approved/generated workbench runs; competency assessment/certification and cohorts; governed pilot milestone acceptance, quality evidence and links to official measurements; connectors and deployments; monetary/token budgets and funded provider access; AI-specific retention/deletion and historical guide snapshots; purchasing/payments. Conditional Release 3 finance is not pulled forward by these planning calculations.

Provider use still requires separate advisory permission, explicit consent and server configuration. The existing three attempts per tenant in a rolling 24 hours includes failures; it is not a monetary spending ceiling. No paid provider request was needed for these features. The previously observed exhausted-credit condition is not represented as a new live provider check. There is no production-readiness, UAT, accessibility-conformance or security-assessment claim.

## Qualification record

Local application, API, new planning-browser and rebuilt baseline-adoption browser results are recorded in the [local evidence summary and source/evidence manifest](evidence/nonprofit-ai-planning-local-summary.json). This identifies the source before the increment commit rather than inventing a qualified commit identity. The full application run has **seven failures matching the unchanged Mac operations baseline**, so it is not a green qualification gate. Focused unit/reference, Python lint/format, scoped client formatting and the client build passed. Focused results are separate overlapping executions and must not be added to full-suite counts.

| Evidence layer | Recorded state | Meaning and limitation |
|---|---|---|
| Focused pure-unit checks | **469 passed, 1 skipped** across eleven files; [JUnit evidence](evidence/nonprofit-ai-planning-unit-tests.xml) | The skip is `test_ai_enablement.py::test_native_advisory_tables_force_rls_and_narrow_application_grants`, requiring native PostgreSQL; not a pass or final full-suite count |
| Preserved design-reference checks | **143 passed**, zero failures/errors; [evidence](evidence/nonprofit-ai-planning-reference-tests.json) | `product_validated:false`; preserved design assertions only |
| Synthetic planning-component browser checks | 16 passed, reported by `dev_planning_ui` | Component fixtures only; not the real API/database workspace |
| New API/database security tests | **49 passed, 0 failed, 0 skipped**, 1.52 seconds; [focused JUnit](evidence/nonprofit-ai-planning-focused-api.xml) | The full run included the prior 48 checks; this later overlapping run adds one real-API legacy-omission/null-clear/exact-retry/history regression absent from the full run |
| New planning workspace browser | **20 groups passed** in installed Chrome 154.0.8037.97 against real FastAPI/PGlite; [evidence](evidence/nonprofit-ai-planning-browser-tests.json) | Eight axe scans: zero violations and zero incomplete; zero uncaught JavaScript errors and zero advisory requests. Four historical-read projections are explicitly simulated; surrounding calculations and persistence are real |
| Baseline adoption browser regression | **10 groups passed**, zero failed/uncaught JavaScript errors; [final rebuilt evidence](evidence/nonprofit-ai-planning-adoption-regression.json) | The baseline report does not record a browser version; five axe scans have zero violations and one incomplete color-contrast finding in discard confirmation, retained for manual review |
| Full local application suite | **1,495 passed, 7 failed, 76 skipped, 1 deselected**, 177.98 seconds; [full JUnit](evidence/nonprofit-ai-planning-local-suite.xml) | All 48 planning-live checks in that run passed. Seven failure identities exactly match [the 0.30 Mac baseline](evidence/nonprofit-ai-adoption-local-suite.xml); no new failure identities. Not a green gate |
| Python lint and formatting | PASS: Ruff check and format across 198 files | Static source checks, not runtime or security qualification |
| Scoped client formatting | PASS: six touched web files | Does not claim a repository-wide Prettier run |
| TypeScript and Vite build | PASS | Existing chunk warning above 500 KiB remains; output `index-DQHgjmQq.js` / `index-Dv0WouL3.css` |
| Native PostgreSQL, live identity provider, deployment containers, hosted CI and UAT | NOT RUN for this candidate | Required qualification/approval gates remain outstanding |

The documentation's 108 `TC-NPA-*` cases remain `SPECIFIED_NOT_RUN`. Named automated checks can provide partial supporting evidence; they are not full execution of the written product cases. PGlite serializes local database transactions and supplies no native contention evidence. The seven unchanged failures are in `test_ops_unit.py`: backup-set manifest, same-day replacement, disk guard, Sunday hard-link/retention, JSON escaping, newest-set restore and damaged/failed restore. Comparison uses the named 0.30 Mac run, not the older Linux-green generic `application-tests.xml`. Those failures are retained and do not become passes because they predate this increment.

The integrator visually reviewed selected actual cost/practice desktop and mobile captures for legibility and layout, including [desktop supplied costs](evidence/nonprofit-ai-planning/cost-desktop.png) and [mobile task practice](evidence/nonprofit-ai-planning/practice-mobile.png). Automated axe scans and selected visual inspection do not establish complete accessibility conformance, assistive-technology coverage or UAT. The baseline discard dialog's incomplete `color-contrast` finding concerns `.ai-discard-copy`, whose background axe could not determine due to overlap; it remains a manual-review gap, not a pass or an accepted exception.

## Reproduction

From the repository root, after ordinary setup, use synthetic fixtures only and a free API port for each runner. The focused checks below are local and do not fund or call an AI provider. Recorded results above identify the executed scopes; `make lint` below is the broader reproducible gate, while only the scoped six-file Prettier result is claimed here.

```sh
.venv/bin/python -m pytest qualification/test_ai_enablement_catalog.py qualification/test_ai_solutions_catalog.py qualification/test_ai_learning_content.py qualification/test_ai_adoption_plans.py qualification/test_ai_planning_inputs.py qualification/test_ai_procurement_costs.py qualification/test_ai_pilot_outcomes.py qualification/test_ai_task_practice.py qualification/test_ai_advisory_provider.py qualification/test_ai_enablement.py qualification/test_version_unit.py --junitxml=docs/evidence/nonprofit-ai-planning-unit-tests.xml
.venv/bin/python specification/reference-v1/run_tests.py reference --report docs/evidence/nonprofit-ai-planning-reference-tests.json
IMPACT_PORT=8131 .venv/bin/python scripts/run.py test --pytest-path qualification/test_ai_planning_live.py
IMPACT_PORT=8132 .venv/bin/python scripts/run.py ai-planning-browser
IMPACT_PORT=8133 .venv/bin/python scripts/run.py ai-enablement-browser
make lint
make build
IMPACT_PORT=8134 make test
```

Local browser reproduction on macOS sets `IMPACT_BROWSER_EXECUTABLE` to the installed Chrome path; for example:

```sh
IMPACT_BROWSER_EXECUTABLE="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" IMPACT_PORT=8132 .venv/bin/python scripts/run.py ai-planning-browser
```

The repository's normal browser gate uses prepared Chromium on Linux. A focused application runner overwrites `docs/evidence/application-tests.xml`; preserve named final evidence and restore overwritten unrelated evidence before committing. Run full application suites one at a time. Native, live-identity and container qualification use the repository's separate documented gates and appropriately provisioned disposable infrastructure; none is inferred from these local commands.

## Integration notes

Ten named agent workstreams were assigned, with one root integrator. The runtime permits four active agents including the integrator, so the ten streams ran in parallel waves rather than ten simultaneous workers. The [development record](nonprofit-ai/v1.0/DEVELOPMENT-0.31.md) names every stream and its evidence boundary.

Primary code areas: `ai_learning_content.py`, `ai_adoption_plans.py`, `ai_procurement_costs.py`, `ai_pilot_outcomes.py`, `ai_task_practice.py`, `ai_planning_contracts.py`, `ai_advisory_provider.py`; web `AIPlanningTools.tsx`, `AITaskPractice.tsx`, `AIAdoptionWorkspace.tsx` and their styles; qualification and browser checks. The integrator owns versions, route/contract generators, runner entry points and final evidence. This stream owns the release/development records, implementation boundary, current documentation index, user guide and current API inventory. Generated `docs/API-INVENTORY.md` remains the integrator's separate output.

Risks that remain explicit: draft figures can be mistaken for accepted results; self-checks can be mistaken for competency; old guide text is unavailable; provider DNS/cleanup is not process-bounded; monetary budgets and AI data lifecycle are incomplete. No credentials, staging settings, migrations, independent-approval rules or official arithmetic are changed. Merge into auto-deploying `main` still requires all four hosted jobs green and explicit owner confirmation; paid CI and provider calls need their existing authorization.
